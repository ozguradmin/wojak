"""Sahne tipleri (1920x1080, hepsi easing'li animasyon) ve sahne üstü katmanlar.

Tipler: wojak, foto, manset, harita, sayac, bolum_karti, metin, zaman_cizelgesi (takma ad: liste); 2. tur:
bolunmus, izgara, pano (bilgi.py), marka, bitis (kanal.py). Koyu bilgi sahnelerinin zemini: zemin.py.
Üst katmanlar (her sahnede): isim etiketi (lower third), vurgu kelimesi, lastik damga, köşe göstergesi (ust.py).
Filigran render.py'de, geçişten sonra eklenir (her karede sabit; sahne `filigran: false` ile kapatır).

Her sahnenin varsayılan zamanlaması (ülkelerin yanma sırası, noktaların belirmesi, etiketin yazılması...)
bu dosyanın başındaki *_zamanlari() fonksiyonlarındadır: çizici, otomatik efektler (ses.py) ve hareket
denetimi (vuruslar) aynı zamanları kullanır.
"""

from __future__ import annotations

import math
import wave
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps

from .. import facing
from . import cizim as C
from . import easing as E
from . import zemin as Z
from .spec import Olay, Sahne, Video
from .ust import Damga, KoseGostergesi, damga_olaylari, kose_olaylari
from .zaman import balon_olaylari


# ================================================================ zamanlama varsayılanları

def olaylar(sahne: Sahne, tip: str) -> list[Olay]:
    return sorted((o for o in sahne.olaylar if o.tip == tip), key=lambda o: o.zaman)


def basla_zamani(sahne: Sahne, varsayilan: float) -> float:
    b = olaylar(sahne, "basla")
    return b[0].zaman if b else varsayilan


def karakter_zamanlari(sahne: Sahne) -> dict[str, dict]:
    """id -> {giris: t|None, cikis: t|None, yuz: [(t, gorsel)]}"""
    out = {}
    for i, c in enumerate(sahne.p.get("karakterler", []) + sahne.p.get("konuk", [])):
        g = c.get("giris", True)
        giris = None if g is False else (float(g) if isinstance(g, (int, float)) and g is not True else 0.05 + 0.22 * i)
        out[c["id"]] = {"giris": giris, "cikis": None, "yuz": [], "sik": [], "buyu": [], "agiz": []}
    for o in sahne.olaylar:
        k = o.p.get("karakter")
        if k not in out:
            continue
        if o.tip == "giris":
            out[k]["giris"] = o.zaman
        elif o.tip == "cikis":
            out[k]["cikis"] = o.zaman
        elif o.tip == "yuz":
            out[k]["yuz"].append((o.zaman, Path(o.p["gorsel"])))
            if o.p.get("sik", True) is not False:   # 8. tur: sik: false = sıkışmasız geçiş (kapı kanadı ara kareleri)
                out[k]["sik"].append(o.zaman)
            if o.p.get("buyu"):   # 9. tur: yeni görsel eski boyundan büyüyerek oturur (doz şişesi)
                out[k]["buyu"].append(o.zaman)
        elif o.tip == "balon" and o.p.get("agiz"):
            # 9. tur (animasyon hakemi S10): balon açıkken hecelerde açık ağızlı yüz (balon repliklerinde oyunculuk yoktu)
            sure = min(float(o.p.get("sure") or 2.5), 1.6)
            ag = o.p["agiz"]
            out[k]["agiz"].append((o.zaman, o.zaman + sure, [Path(a) for a in (ag if isinstance(ag, list) else [ag])]))
    for v in out.values():
        v["yuz"].sort(key=lambda x: x[0])
    return out


def foto_zamanlari(sahne: Sahne) -> dict:
    inis = 0.12
    et = olaylar(sahne, "etiket")
    etiket = et[0].zaman if et else 0.95
    metin = str(sahne.p.get("etiket") or "")
    return {"inis": inis, "oturma": inis + 0.62, "etiket": etiket, "harf_hizi": DaktiloEtiket.HIZ,
            "etiket_metni": metin, "etiket_bitis": etiket + len(metin) / DaktiloEtiket.HIZ}


def etiket_zamani(sahne: Sahne, varsayilan: float) -> float | None:
    """wojak/manset/foto sahnelerindeki daktilo etiketinin başlama anı (etiket yoksa None)."""
    if not sahne.p.get("etiket"):
        return None
    et = olaylar(sahne, "etiket")
    return et[0].zaman if et else varsayilan


def manset_zamanlari(sahne: Sahne) -> list[float]:
    n = len(sahne.p.get("kutular") or [])
    ts = [0.8 + 1.1 * i for i in range(n)]
    for o in olaylar(sahne, "vurgula"):
        k = int(o.p["kutu"]) - 1
        if 0 <= k < n:
            ts[k] = o.zaman
    return ts


def harita_zamanlari(sahne: Sahne) -> tuple[list[tuple[str, float]], tuple[str, float] | None]:
    p = sahne.p
    kodlar = [str(k) for k in (p.get("ulkeler") or [])]
    dur = sahne.sure_hesap or 6.0
    bas = basla_zamani(sahne, 0.5)
    n = max(1, len(kodlar))
    aralik = float(p["aralik"]) if p.get("aralik") is not None else min(0.45, max(0.12, dur * 0.45 / n))
    ts = {k: bas + i * aralik for i, k in enumerate(kodlar)}
    vurgu = p.get("vurgu")
    vk = None
    if vurgu:
        vk = str(vurgu["kod"] if isinstance(vurgu, dict) else vurgu)
    vt = (bas + n * aralik + 0.6) if kodlar else bas
    for o in olaylar(sahne, "ulke"):
        k = str(o.p["kod"])
        if k == vk:
            vt = o.zaman
        elif k in ts:
            ts[k] = o.zaman
    return [(k, ts[k]) for k in kodlar], ((vk, vt) if vk else None)


def rota_zamanlari(sahne: Sahne) -> list[tuple[float, float, dict]]:
    """Harita rotaları: [(başlangıç, çizim süresi, olay p)] (7. tur)."""
    return [(o.zaman, float(o.p.get("sure", 1.2)), o.p) for o in olaylar(sahne, "rota")]


SAYAC_TUT = 0.6       # sn (10. tur): sayım bitince değer en az bu kadar okunur kalır, sonra yeni değer (sahne `tut`)
SAYAC_EN_AZ = 0.6     # sn: tutma payı için kısaltılan sayımın en kısa hâli
SAYAC_EN_AZ_TUT = 0.3  # sn: kısaltma yetmezse sonraki değer en az bu kadar tutulsun diye ertelenir
SAYAC_GECIS = 0.26    # sn (10. tur): bir anda gelen değer (sure: 0) tekerlek gibi yuvarlanarak gelir
SAYAC_GECIS_K = 1.3   # yuvarlanmanın out_back taşması; yeni değer pencereye 0,435 * SAYAC_GECIS'te oturur (vuruş)


def sayac_bolumleri(sahne: Sahne) -> list[dict]:
    """Sayacın sayım bölümleri: [{t0, t1, a, b, yil, etiket, renk, onek, sonek, varis}]. İlki sahnenin
    `deger`/`yil`'ından (`deger: [60, 0]` azalan), sonrakiler `deger` olaylarından (bir önceki değerden yenisine).

    10. tur (animasyon hakemi M2): her değer, sonraki değişimden önce yerleşir ve en az `tut` (0,6 sn) okunur kalır.
    Eskiden "1.267 doktor" sayımı (vars. 2,2 sn) bitmeden 20.000 olayı geliyordu: sayı hiç okunmuyordu. Sayım
    gerekirse kısaltılır (en az 0,6 sn), o da yetmezse sonraki değer ertelenir; `kisaldi` / `ertelendi` anahtarları
    `kontrol` uyarısına gider. Sayım süresi `sure_say` ya da `basla` olayının `sure`'ü; son sayım da sahne bitmeden
    `tut` kadar önce biter."""
    p = sahne.p
    bas = basla_zamani(sahne, 0.35)
    bo = olaylar(sahne, "basla")
    sure_b = bo[0].p.get("sure") if bo else None
    tut = float(p.get("tut", SAYAC_TUT))
    pal = Z.KAGIT if p.get("zemin") == "kagit" else Z.KOYU
    renk0 = Z.renk(p.get("renk"), pal.metin)
    if p.get("yil"):
        a, b = p["yil"]
        sure = float(sure_b if sure_b is not None else p.get("sure_say", max(1.0, 0.42 * abs(int(b) - int(a)))))
        return [{"t0": bas, "t1": bas + sure, "a": int(a), "b": int(b), "yil": True, "etiket": p.get("etiket"),
                 "renk": renk0, "onek": "", "sonek": str(p.get("sonek", "")), "varis": bas + sure}]
    d = p["deger"]
    liste = isinstance(d, list)
    a, b = (float(d[0]), float(d[1])) if liste else (0.0, float(d))
    sure = float(sure_b if sure_b is not None else p.get("sure_say", 2.2))
    out = [{"t0": bas, "t1": bas + sure, "a": a, "b": b, "yil": False, "etiket": p.get("etiket"), "renk": renk0,
            "onek": str(p.get("onek", "")), "sonek": str(p.get("sonek", "" if liste else "+")),
            "log": p.get("olcek") == "log", "onek_once": None}]
    for o in olaylar(sahne, "deger"):
        q, onc = o.p, out[-1]
        t0 = max(o.zaman, onc["t0"] + 0.05)
        out.append({"t0": t0, "t1": t0 + float(q.get("sure", 1.2)), "a": onc["b"], "b": float(q["deger"]),
                    "yil": False, "etiket": q.get("etiket", onc["etiket"]),
                    "renk": Z.renk(q.get("renk"), onc["renk"]) if q.get("renk") is not None else onc["renk"],
                    "onek": str(q.get("onek", "")), "sonek": str(q.get("sonek", "")), "onek_once": onc["onek"]})
    # 10. tur: yerleşip okunmadan yeni değere geçilmez (sayım kısalır; yetmezse sonraki değer ertelenir)
    for onc, b in zip(out, out[1:]):
        if onc["t1"] - onc["t0"] < 1e-3:
            continue
        son = b["t0"] - tut
        if onc["t1"] > son + 1e-6:
            yeni = max(onc["t0"] + min(SAYAC_EN_AZ, onc["t1"] - onc["t0"]), son)
            onc["kisaldi"] = round(onc["t1"] - yeni, 3)
            onc["t1"] = yeni
            ek = onc["t1"] + min(tut, SAYAC_EN_AZ_TUT) - b["t0"]
            if ek > 1e-6:
                b["t0"] += ek
                b["t1"] += ek
                b["ertelendi"] = round(ek, 3)
    dur = sahne.sure_hesap or 0.0
    sonb = out[-1]
    if dur > 0 and sonb["t1"] - sonb["t0"] >= 1e-3 and sonb["t1"] > dur - tut + 1e-6:
        yeni = max(sonb["t0"] + min(SAYAC_EN_AZ, sonb["t1"] - sonb["t0"]), dur - tut)
        if yeni < sonb["t1"] - 1e-6:
            sonb["kisaldi"] = round(sonb["t1"] - yeni, 3)
            sonb["t1"] = yeni
    # 8. tur: tekerlekli sayaçta basamak sayısı sabit: art arda sayan bölümler (1.267 -> 20.000) en büyük değerin
    # basamak sayısını baştan ayırır; bir anda gelen değer (sure: 0) kendi basamak sayısıyla yeniden yerleşir
    zincir = [b for b in out if not b["yil"] and b["t1"] - b["t0"] >= 1e-3]
    D = max([len(str(int(round(max(abs(b["a"]), abs(b["b"])))))) for b in zincir] or [1])
    for i, b in enumerate(out):
        ani = b["t1"] - b["t0"] < 1e-3
        b["basamak"] = len(str(int(round(abs(b["b"]))))) if ani else D
        b["ani"] = ani
        # vuruş anı: sayım bitişi; bir anda gelen değerde yuvarlanan yeni sayının pencereye oturduğu an
        b["varis"] = b["t0"] + 0.435 * SAYAC_GECIS if (ani and i > 0) else b["t1"]
    return out


def sayac_zamanlari(sahne: Sahne) -> tuple[float, float]:
    """İlk sayımın başı ve son sayımın sonu."""
    b = sayac_bolumleri(sahne)
    return b[0]["t0"], b[-1]["t1"]


def zc_zamanlari(sahne: Sahne) -> list[float]:
    n = len(sahne.p["noktalar"])
    dur = sahne.sure_hesap or 6.0
    bas = basla_zamani(sahne, 0.75)
    ara = max(0.45, min(2.2, (dur - bas - 1.0) / max(n, 1)))
    ts = [bas + i * ara for i in range(n)]
    for o in olaylar(sahne, "nokta"):
        k = int(o.p["indeks"]) - 1
        if 0 <= k < n:
            ts[k] = o.zaman
    return ts


DAKTILO_HIZI = 13.0   # metin sahnesi daktilo modu: harf / sn


def metin_zamanlari(sahne: Sahne) -> dict:
    """kelimeler: her kelimenin belirme anı; daktilo: (başlangıç, harf/sn) ya da None; ceviri: çeviri anı."""
    metin = str(sahne.p.get("metin", ""))
    kel = metin.split()
    bas = basla_zamani(sahne, 0.3)
    daktilo = sahne.p.get("yazim") == "daktilo"
    if daktilo and sahne.gecis != "kesme" and sahne.gecis_kare:
        # 9. tur (animasyon S1): daktilo geçiş bitince başlar (imleç ve ilk harfler sönen önceki karenin üstündeydi)
        bas = max(bas, (sahne.gecis_kare + 1) / 30.0)
    if daktilo:   # kelime anı = o kelimenin ilk harfinin yazıldığı an
        kt, i = [], 0
        for k in kel:
            kt.append(bas + i / DAKTILO_HIZI)
            i += len(k) + 1
        son = bas + len(" ".join(kel)) / DAKTILO_HIZI
    else:
        kt = [bas + 0.14 * i for i in range(len(kel))]
        son = kt[-1] if kt else bas
    cev = olaylar(sahne, "ceviri")
    ct = cev[0].zaman if cev else (float(sahne.p["ceviri_t"]) if sahne.p.get("ceviri_t") is not None
                                  else son + 0.7)
    return {"kelimeler": kt, "ceviri": ct, "daktilo": (bas, DAKTILO_HIZI) if daktilo else None, "metin": metin}


def vuruslar(sahne: Sahne) -> list[float]:
    """Sahnede ekrana yeni bir şey geldiği anlar (hareket denetimi için, sahne içi sn)."""
    t = [0.0]
    for o in sahne.olaylar:
        t.append(o.zaman)
    tip = sahne.tip
    if tip == "wojak":
        for v in karakter_zamanlari(sahne).values():
            t += [x for x in (v["giris"], v["cikis"]) if x is not None] + [y for y, _ in v["yuz"]]
        t += [o.zaman for o in balon_olaylari(sahne)]
        e = etiket_zamani(sahne, 0.6)
        t += [e] if e is not None else []
    elif tip == "foto":
        z = foto_zamanlari(sahne)
        t += [z["oturma"]] + ([z["etiket"]] if z["etiket_metni"] else [])
    elif tip == "manset":
        t += manset_zamanlari(sahne)
        e = etiket_zamani(sahne, 0.7)
        t += [e] if e is not None else []
    elif tip == "harita":
        u, v = harita_zamanlari(sahne)
        t += [x for _, x in u] + ([v[1]] if v else [])
        t += [a + b for a, b, _ in rota_zamanlari(sahne)]
    elif tip == "sayac":
        for b in sayac_bolumleri(sahne):
            t += [b["t0"], b["t1"]]
    elif tip == "zaman_cizelgesi":
        t += zc_zamanlari(sahne)
    elif tip == "metin":
        z = metin_zamanlari(sahne)
        t += z["kelimeler"][:1] + ([z["ceviri"]] if sahne.p.get("ceviri") else [])
    elif tip == "bolum_karti":
        t += [0.4]
    elif tip in ("bolunmus", "izgara", "pano"):
        from . import bilgi
        t += bilgi.vuruslar(sahne)
    elif tip in ("marka", "bitis"):
        from . import kanal
        t += kanal.vuruslar(sahne)
    elif tip == "kapanis":
        from . import kapanis
        t += kapanis.vuruslar(sahne)
    if tip != "wojak" and sahne.p.get("konuk"):
        for v in karakter_zamanlari(sahne).values():
            t += [x for x in (v["giris"], v["cikis"]) if x is not None] + [y for y, _ in v["yuz"]]
    return sorted(x for x in t if 0 <= x <= max(sahne.sure_hesap, 0.01))


# ================================================================ bağlam ve temel

class Baglam:
    def __init__(self, video: Video, W: int = 1920, H: int = 1080, fps: int = 30):
        self.v, self.W, self.H, self.fps = video, W, H, fps
        self.S = W / 1920


class Cizici:
    bindirme = False   # True: önceki sahnenin son karesi üstüne çizilir (render.py dondur() ile verir)

    def __init__(self, sahne: Sahne, c: Baglam):
        self.sahne, self.c, self.p = sahne, c, sahne.p
        self.W, self.H, self.S = c.W, c.H, c.S
        self.dur = max(sahne.sure_hesap, 1 / c.fps)
        self.hazirla()
        self.katman = UstKatman(sahne, c, self)

    def hazirla(self):
        pass

    def sabit_engeller(self) -> list[tuple]:
        """11. tur: sahnenin kendi çizdiği, üst katmanların (isim etiketi) örtmemesi gereken sabit kutular (ekran
        pikseli; ör. fotoğrafın lisans/atıf satırı)."""
        return []

    def ciz(self, t: float) -> Image.Image:
        raise NotImplementedError

    def dondur(self, onceki: Image.Image) -> None:
        """Bindirme sahneleri için önceki sahnenin son karesi (filigransız)."""

    def kare(self, t: float) -> Image.Image:
        im = self.ciz(t)
        self.katman.uygula(im, t)
        return sarsinti_uygula(im, self.sarsintilar, t, self.S) if self.sarsintilar else im

    @property
    def sarsintilar(self) -> list:
        if not hasattr(self, "_sars"):
            self._sars = [(o.zaman, float(o.p.get("guc", 7.0)), float(o.p.get("sure", 0.1)))
                          for o in olaylar(self.sahne, "sarsinti")]
        return self._sars

    def px(self, v: float) -> float:
        return v * self.S


def sarsinti_uygula(im: Image.Image, sarsintilar: list, t: float, S: float) -> Image.Image:
    """8. tur (animasyon hakemi S4): kapı çarpmasında 2-3 karelik kamera sarsıntısı. Bütün kare (yazılar dahil)
    sönümlü, yön değiştiren bir ötelemeyle kayar; kenar boşluğu kalmasın diye kare o kadar büyütülür. Filigran
    render'da sonra eklenir (sarsılmaz)."""
    dx = dy = 0.0
    for t0, guc, sure in sarsintilar:
        u = (t - t0) / max(sure, 1e-3)
        if 0 <= u <= 1.0:
            k = guc * S * (1 - u) ** 1.5
            dx += k * math.cos(1.0 + 9.0 * u)
            dy += k * math.sin(2.3 + 11.0 * u)
    if abs(dx) < 0.3 and abs(dy) < 0.3:
        return im
    W, H = im.size
    m = abs(dx) + abs(dy) + 2
    zz = 1 + 2 * m / min(W, H)
    return C.kamera(im, W, H, zz, (0.5 - dx / (W * zz), 0.5 - dy / (H * zz)))


# ================================================================ üst katmanlar

def kesmeyle_biter(sahne: Sahne, v: Video | None) -> str | None:
    """Sahneden sonra ne geliyor: 'kesme' | 'donuk' (sonraki sahne bu sahnenin son karesini dondurup üstüne çizer:
    bindirme kart/imza/kapanış) | None (çapraz geçiş ya da itme: bu sahne geçiş boyunca çizilmeye devam eder)."""
    if v is None:
        return "kesme"
    ss = v.sahneler
    i = sahne.no
    if not (0 <= i < len(ss) and ss[i] is sahne) or i + 1 >= len(ss):
        return "kesme"
    n = ss[i + 1]
    if n.p.get("bindirme") and n.tip in ("bolum_karti", "marka", "bitis", "kapanis"):
        return "donuk"
    return "kesme" if n.gecis == "kesme" else None


def kesmede_yarim_kalmasin(t0: float, sure: float, cikis: float, dur: float, kesme) -> float:
    """7. tur: çıkış animasyonu (söndürme / kayarak çıkma) sahne sonunda yarıda kalmasın (talidomit-turkiye: 8 vurgu
    kelimesi kesmede %18-95 saydam kesiliyordu). Kesmede öğe kesmeye dek tam görünür kalır; donmuş kare bindirmesinde
    (bölüm kartı) çıkışını kesmeden önce bitirir: donan karede yarı saydam yazı kartın başlığıyla yarışmasın (en az
    0,6 sn görünmüşse; yoksa tam görünür kalır)."""
    if kesme and t0 + sure < dur < t0 + sure + cikis:
        if kesme == "donuk" and dur - cikis - 0.04 - t0 >= 0.6:
            return dur - cikis - 0.04 - t0
        return dur - t0 + 1.0
    if kesme == "donuk" and t0 + sure >= dur and dur - cikis - 0.04 - t0 >= 0.6:
        return dur - cikis - 0.04 - t0      # kesmeyi aşan öğe de donmadan önce söner
    return sure


class UstKatman:
    """Her sahnede: konuk karakterler, köşe göstergesi, isim etiketleri, vurgu kelimeleri, damgalar.

    10. tur (animasyon hakemi M1/S5): isim etiketi yerini kendisi seçer (`_isim_yeri`): kutusu her karakterin alfa
    kutusundan en az `yerlesim.BOSLUK` (40 px), öteki üst katmanlardan 20 px uzak; önce istenen kenarda, sonra
    karakterin yanındaki boşlukta ya da boş tarafta, sığmazsa unvanı/adı iki satıra kırarak, sonra küçülterek.
    `kutular(t)` / `yuz_kutulari(t)`: `kontrol`ün çakışma denetimi için o anki üst katman ve yüz kutuları."""

    ISIM_GIRIS = 0.5
    ISIM_CIKIS = 0.38

    def __init__(self, sahne: Sahne, c: Baglam, cizici=None):
        self.c = c
        S = c.S
        dur = max(sahne.sure_hesap, 1e-3)
        kesme = kesmeyle_biter(sahne, getattr(c, "v", None))
        self.bulanik = bool((getattr(c.v, "hareket", None) or {}).get("bulaniklik", False))
        # konuk: wojak dışı sahnede köşeden/kenardan giren tepki karakteri (kamerasız, ekran koordinatında; yazı
        # katmanlarının ALTINDA çizilir)
        self.konuklar = []
        if sahne.tip != "wojak" and sahne.p.get("konuk"):
            zam = karakter_zamanlari(sahne)
            for i, cs in enumerate(sahne.p["konuk"]):
                self.konuklar.append(Karakter(cs, zam[cs["id"]], c, i + 3))
        # yerleşim için karakterler: (id, Karakter, kamera fonksiyonu ya da None)
        self.kars = []
        if cizici is not None and getattr(cizici, "karakterler", None) and hasattr(cizici, "kam"):
            for k in cizici.karakterler:
                self.kars.append((k, (lambda t, k=k: cizici.kam_derin(cizici.kam(t), 0.8 * k.derinlik)
                                      if k.derinlik else cizici.kam(t))))
        self.kars += [(k, None) for k in self.konuklar]
        self.kar_id = {}
        for cs, (k, _) in zip(list(sahne.p.get("karakterler", []) if sahne.tip == "wojak" else [])
                              + list(sahne.p.get("konuk", []) if sahne.tip != "wojak" else []), self.kars):
            self.kar_id[cs["id"]] = k
        e_ = getattr(cizici, "etiket", None)
        self.etiket_ref = e_ if isinstance(e_, DaktiloEtiket) else None   # wojak/foto/manset daktilo etiketi
        self._bb: dict = {}
        self.vurgular = []
        for o in olaylar(sahne, "kelime"):
            spr = C.yazi(str(o.p["metin"]), C.FONT_DIALOG, 92 * S, C.BEYAZ, stroke=7 * S, max_w=1500 * S,
                         max_lines=2, align="center", golge=(0, 5 * S, 9 * S, 0.55))
            sure = kesmede_yarim_kalmasin(o.zaman, float(o.p.get("sure", 2.3)), 0.3, dur, kesme)
            self.vurgular.append((o.zaman, sure, spr, str(o.p.get("konum", "alt")), str(o.p["metin"])))
        self.damgalar = [Damga(o, c, i) for i, o in enumerate(damga_olaylari(sahne))]
        for d in self.damgalar:
            if d.sure is not None:
                d.sure = kesmede_yarim_kalmasin(d.t0, d.sure, 0.25, dur, kesme)
        ko = kose_olaylari(sahne)
        self.kose = KoseGostergesi(sahne, c, ko) if (sahne.kose is not None or ko) else None
        # 11. tur (animasyon hakemi S4): Kelsey'nin isim etiketi fotoğrafın atıf satırını ("kamu malı") örtüyordu:
        # sahnenin sabit kutuları da engel
        self.sabit = list(cizici.sabit_engeller()) if cizici is not None and hasattr(cizici, "sabit_engeller") else []
        self.isimler = []
        for o in olaylar(sahne, "isim"):
            konum = str(o.p.get("konum", "sol"))
            hedef = None
            if o.p.get("karakter") is not None:   # adı verilen karakterin tarafına (sığmazsa yanına / boş tarafa)
                for c_ in sahne.p.get("karakterler", []) + sahne.p.get("konuk", []):
                    if c_["id"] == str(o.p["karakter"]):
                        cx = float(c_["x"]) if c_.get("x") is not None else {"sol": 0.25, "sag": 0.75, "orta": 0.5}[c_["taraf"]]
                        konum = "sag" if cx > 0.5 else "sol"
                hedef = self.kar_id.get(str(o.p["karakter"]))
            sure = kesmede_yarim_kalmasin(o.zaman, float(o.p.get("sure", 4.2)), self.ISIM_CIKIS, dur, kesme)
            self.isimler.append(self._isim_yeri(str(o.p["ad"]), o.p.get("unvan"), o.zaman, sure, konum, hedef))

    # ---------------------------------------------------------------- isim etiketi

    def _isim(self, ad: str, unvan: str | None, olcek: float = 1.0) -> Image.Image:
        S = self.c.S * olcek
        a = C.yazi(ad, C.FONT_BOLD, 46 * S, C.BEYAZ)
        u = C.yazi(unvan, C.FONT_BOLD, 31 * S, (214, 216, 222)) if unvan else None   # 6. tur (N6): 27 telefonda küçüktü
        padx, pady, bar = 30 * S, 18 * S, 10 * S
        w = int(max(a.width, u.width if u else 0) + 2 * padx + bar)
        h = int(a.height + (u.height + 10 * S if u else 0) + 2 * pady)
        panel = C.yuvarlak_kutu(w, h, 6 * S, (10, 12, 16, 228))
        ImageDraw.Draw(panel).rectangle((0, 0, int(bar) - 1, h), fill=C.SARI + (255,))
        panel.alpha_composite(a, (int(bar + padx), int(pady)))
        if u:
            panel.alpha_composite(u, (int(bar + padx), int(pady + a.height + 10 * S)))
        spr, _, _ = C.golgeli(panel, 12 * S, 0.45, 0, 6 * S)
        return spr

    def _isim_varyantlari(self, ad: str, unvan: str | None):
        """Sırayla: olduğu gibi; en geniş satır iki satıra; ikisi de iki satıra; aynıları %86 boyda."""
        from . import yerlesim as Y
        yield ad, unvan, 1.0
        f_a, f_u = C.font(C.FONT_BOLD, 46), C.font(C.FONT_BOLD, 31)
        sa, su = Y.ikiye_bol(ad), Y.ikiye_bol(unvan)
        aday = []
        if unvan and f_u.getlength(unvan) >= f_a.getlength(ad):
            aday += [(ad, su)] if su else []
        elif sa:
            aday += [(sa, unvan)]
        if sa and su:
            aday.append((sa, su))
        for a_, u_ in aday:
            yield a_, u_, 1.0
        for a_, u_ in [(ad, unvan)] + aday:
            yield a_, u_, 0.86

    def _kutu_ici(self, spr: Image.Image) -> tuple:
        """Sprite'ın görünen (gölgesiz) kutusu, sprite pikseli."""
        k = id(spr)
        if k not in self._bb:
            self._bb[k] = (spr.getchannel("A").point(lambda v: 255 if v > 160 else 0).getbbox()
                           or (0, 0, spr.width, spr.height), spr)
        return self._bb[k][0]

    def _isim_yeri(self, ad: str, unvan, t0: float, sure: float, konum: str, hedef) -> dict:
        """10. tur: isim etiketinin yeri. Etiketin durduğu süre boyunca (0,25 sn arayla) karakterlerin alfa kutuları
        ve öteki üst katmanlar engel; aday konumlar: istenen kenar, öbür kenar, her engelin hemen solu/sağı. İlk
        engelsiz varyant (olduğu gibi > kırık > küçük) ve en yakın konum seçilir; yoksa en az çakışan (ihlal > 0,
        kontrol uyarır)."""
        from . import yerlesim as Y
        S, W, H = self.c.S, self.c.W, self.c.H
        bos, bos2 = Y.BOSLUK * S, Y.BOSLUK_UST * S
        t_a, t_b = t0 + min(self.ISIM_GIRIS, sure), t0 + sure
        ts = [t_a + j * 0.25 for j in range(int((t_b - t_a) / 0.25) + 1)] or [t_a]
        engel, yuzler = [], []
        for t in ts:
            r, yz = [], []
            for k, kf in self.kars:
                kb = k.ekran_kutulari(t, kf(t) if kf else None)
                if kb:   # canlı karakter 40 px; dekor/nesne (canli: false) yalnız 8 px
                    r.append((kb[0], bos if not k.sabit else Y.BOSLUK_NESNE * S, k))
                    if k.yuzlu:
                        yz.append(kb[1])
            r += [(Y.kutu_icin(p_), bos2, None) for _, p_ in self.kutular(t)]   # önceki isimler dahil
            r += [(b_, bos2, None) for b_ in self.sabit]
            engel.append(r)
            yuzler.append(yz)
        en_iyi = None
        for j, (a_, u_, olc) in enumerate(self._isim_varyantlari(ad, unvan)):
            spr = self._isim(a_, u_, olc)
            pb = self._kutu_ici(spr)
            y = H - 92 * S - spr.height
            py0, py1 = y + pb[1], y + pb[3]
            sol_d, sag_d = 64 * S, W - 64 * S - spr.width
            xs = {sol_d, sag_d}
            for r in engel:
                for kb, pay, _ in r:
                    if kb[3] > py0 - pay and kb[1] < py1 + pay:
                        xs.add(kb[0] - pay - pb[2] - 1)
                        xs.add(kb[2] + pay - pb[0] + 1)
            x_min, x_max = 32 * S - pb[0], W - 32 * S - pb[2]
            tercih = sol_d if konum == "sol" else sag_d
            for x in xs:
                x = min(max(x, x_min), x_max)
                p0, p1 = x + pb[0], x + pb[2]
                ihlal = yuz_ihlal = 0.0
                for r, yz in zip(engel, yuzler):
                    ihlal = max(ihlal, sum(Y.kutu_kesisim((p0 - pay, py0 - pay, p1 + pay, py1 + pay), kb)
                                           for kb, pay, _ in r))
                    # sığmazsa yüz hiç örtülmesin (en az çakışan yer gövdede, göğüste olsun)
                    yuz_ihlal = max(yuz_ihlal, sum(Y.kutu_kesisim((p0 - bos2, py0 - bos2, p1 + bos2, py1 + bos2), yb)
                                                   for yb in yz))
                if abs(x - tercih) < 1:
                    poz = 0.0
                elif hedef is not None and any(k is hedef and (abs(p1 + bos - kb[0]) < 3 or abs(p0 - bos - kb[2]) < 3)
                                               for r in engel for kb, _, k in r):
                    poz = 1.0
                elif abs(x - (sag_d if konum == "sol" else sol_d)) < 1:
                    poz = 3.0
                else:
                    poz = 4.0 + 2.0 * abs((p0 + p1) / 2 - (tercih + (pb[0] + pb[2]) / 2)) / W
                anahtar = (ihlal > 0, round(yuz_ihlal / (400 * S * S)), round(ihlal / (4000 * S * S)), 10 * j + poz)
                if en_iyi is None or anahtar < en_iyi[0]:
                    en_iyi = (anahtar, spr, x, olc, u_ != unvan or a_ != ad)
            if en_iyi[0][0] is False:
                break   # bu varyantta engelsiz yer var: sonrakiler (kırık/küçük) daha kötü
        (cakisma, yuz_c, _, _), spr, x, olc, kirik = en_iyi
        pb = self._kutu_ici(spr)
        kenar = abs(x - 64 * S) < 1 or abs(x - (W - 64 * S - spr.width)) < 1
        return {"t0": t0, "sure": sure, "spr": spr, "x": x, "sol": (x + (pb[0] + pb[2]) / 2) < W / 2,
                "kenar": kenar, "ihlal": 1.0 if cakisma else 0.0, "yuz": yuz_c > 0, "ad": ad,
                "olcek": olc, "kirik": kirik}

    def _isim_xy(self, it: dict, u: float) -> tuple[float, float, float]:
        """Etiketin u (girişten beri sn) anındaki sol üstü ve opaklığı. Kenardaki etiket kenardan kayarak girer
        (eski davranış); boşluğa yerleşen etiket kısa kayma + belirme ile (kenardan gelirken karakterin üstünden
        geçmesin)."""
        S, W, H = self.c.S, self.c.W, self.c.H
        spr, x_dur, sure = it["spr"], it["x"], it["sure"]
        y = H - 92 * S - spr.height
        if it["kenar"]:
            git = (spr.width + x_dur + 20 * S) if it["sol"] else -(W - x_dur + 20 * S)
            x = x_dur - (1 - E.out_cubic(u / self.ISIM_GIRIS)) * git - E.in_cubic((u - sure) / self.ISIM_CIKIS) * git
            return x, y, 1.0
        yon = -1.0 if it["sol"] else 1.0
        e, c_ = E.out_cubic(u / 0.42), E.in_cubic((u - sure) / 0.32)
        x = x_dur + yon * (1 - e) * 90 * S + yon * c_ * 60 * S
        return x, y, min(1.0, max(0.0, u) / 0.25) * (1 - c_)

    # ---------------------------------------------------------------- geometri (yerleşim + kontrol)

    def kutular(self, t: float, isim: bool = True) -> list[tuple[str, list]]:
        """t anında görünen üst katmanların çokgenleri (ekran pikseli): [(ad, 4 köşe)]. Yarı saydamdan (< 0,3)
        silik olanlar ve inmekte olan damga sayılmaz."""
        from . import yerlesim as Y
        S, W, H = self.c.S, self.c.W, self.c.H
        out = []
        if isim:
            for it in getattr(self, "isimler", []):
                u = t - it["t0"]
                if u < 0 or u > it["sure"] + 0.4:
                    continue
                x, y, a = self._isim_xy(it, u)
                if a < 0.3:
                    continue
                pb = self._kutu_ici(it["spr"])
                out.append((f"isim '{it['ad']}'", Y.dikdortgen(x + pb[0], y + pb[1], x + pb[2], y + pb[3])))
        for t0, sure, spr, konum, metin in self.vurgular:
            u = t - t0
            if u < 0.08 or u > sure + 0.3 * 0.7:
                continue
            s = 0.6 + 0.4 * E.out_back(u / 0.26, 1.6)
            cy = {"ust": 0.17, "orta": 0.5, "alt": 0.80}.get(konum, 0.80) * H
            pb = self._kutu_ici(spr)
            x0, y0 = W / 2 - spr.width / 2 * s, cy - spr.height / 2 * s
            out.append((f"kelime '{metin}'", Y.dikdortgen(x0 + pb[0] * s, y0 + pb[1] * s, x0 + pb[2] * s,
                                                         y0 + pb[3] * s)))
        for d in self.damgalar:
            u = t - d.t0
            if u < d.INIS or (d.sure is not None and u > d.sure + 0.25 * 0.7):
                continue
            out.append((f"damga '{d.metin}'", Y.donuk_dikdortgen(d.x, d.y, d.spr.width, d.spr.height, d.aci)))
        e = self.etiket_ref
        if e is not None and e.metin and e.t0 <= t and (e.bitis is None or t <= e.bitis + 0.2):
            spr = e._spr(len(e.metin), False)
            out.append((f"etiket '{e.metin}'", Y.dikdortgen(70 * S, H - 120 * S - spr.height, 70 * S + spr.width,
                                                           H - 120 * S)))
        if self.kose is not None and t >= self.kose.goster_t + 0.3:
            out.append(("köşe göstergesi", Y.dikdortgen(*self.kose.kutu(t))))
        return out

    def yuz_kutulari(self, t: float) -> list[tuple[str, tuple]]:
        out = []
        for k, kf in self.kars:
            if not k.yuzlu:   # dekor/nesne (canli: false ya da chars/ dışı görsel): damga belgeye bilerek basılır
                continue
            kb = k.ekran_kutulari(t, kf(t) if kf else None)
            if kb:
                out.append((k.ad, kb[1]))
        return out

    def uygula(self, im: Image.Image, t: float) -> None:
        S, W, H = self.c.S, self.c.W, self.c.H
        for k in self.konuklar:
            k.ciz(im, t)
        if self.kose is not None:
            self.kose.ciz(im, t)
        for it in self.isimler:
            u = t - it["t0"]
            if u < 0 or u > it["sure"] + 0.4:
                continue
            spr = it["spr"]
            x, y, a = self._isim_xy(it, u)
            dx = x - self._isim_xy(it, u - 1 / self.c.fps)[0]
            if self.bulanik and abs(dx) > 10 * S:   # hızlı kayan etiket: hareket bulanıklığı (keskin etiketin altında)
                spr2, ox, oy = C.hareket_izi(spr, dx, 0.0, en_cok=C.IZ_EN_COK * S)
                C.bindir(im, spr2, x + ox, y + oy, a)
            else:
                C.bindir_alt(im, spr, x, y, a)
        for t0, sure, spr, konum, _ in self.vurgular:
            u = t - t0
            if u < 0 or u > sure + 0.3:
                continue
            s = 0.6 + 0.4 * E.out_back(u / 0.26, 1.6)
            a = min(1.0, u / 0.08) * (1 - E.lineer((u - sure) / 0.3))
            cy = {"ust": 0.17, "orta": 0.5, "alt": 0.80}.get(konum, 0.80) * H
            if s != 1.0:
                spr2, x0, y0 = C.afin(spr, W / 2, cy, s, s)
                C.bindir(im, spr2, x0, y0, a)
            else:
                C.bindir(im, spr, W / 2 - spr.width / 2, cy - spr.height / 2, a)
        for d in self.damgalar:
            d.ciz(im, t)


# ================================================================ daktilo etiketi (yer / tarih / kaynak)

class DaktiloEtiket:
    """Sol altta, harf harf yazılan yer-tarih etiketi (koyu kutu, sarı çizgi, yanıp sönen imleç)."""
    HIZ = 20.0   # harf / sn

    def __init__(self, metin, c: Baglam, ol: list, varsayilan: float, kalis: float | None = 3.5):
        self.metin = str(metin) if metin else ""
        self.c = c
        self.t0 = ol[0].zaman if ol else varsayilan
        # yazı bittikten sonra kalma süresi (None: sahne sonuna kadar)
        self.bitis = None if kalis is None else self.t0 + len(self.metin) / self.HIZ + kalis
        self.f = C.font(C.FONT_MONO, 34 * c.S)
        self._cache: dict[int, Image.Image] = {}

    def _spr(self, n: int, imlec: bool) -> Image.Image:
        key = n * 2 + int(imlec)
        if key in self._cache:
            return self._cache[key]
        S, f = self.c.S, self.f
        asc, desc = f.getmetrics()
        padx, pady = 22 * S, 13 * S
        w, h = int(f.getlength(self.metin) + 2 * padx + 26 * S), int(asc + desc + 2 * pady)
        lay = C.yuvarlak_kutu(w, h, 4 * S, (8, 9, 12, 205))
        d = ImageDraw.Draw(lay)
        d.rectangle((0, 0, int(6 * S), h), fill=C.SARI + (255,))
        d.text((padx + 6 * S, pady), self.metin[:n], font=f, fill=(240, 238, 230, 255))
        if imlec:
            x = padx + 6 * S + f.getlength(self.metin[:n]) + 3 * S
            d.rectangle((x, pady + 4 * S, x + 15 * S, pady + asc + desc - 6 * S), fill=(240, 238, 230, 255))
        self._cache[key] = lay
        return lay

    def ciz(self, im: Image.Image, t: float) -> None:
        if not self.metin or t < self.t0 - 0.15 or (self.bitis is not None and t > self.bitis + 0.3):
            return
        S, H = self.c.S, self.c.H
        u = t - self.t0
        n = max(0, min(len(self.metin), int(u * self.HIZ) + 1)) if u >= 0 else 0
        imlec = (n < len(self.metin)) or (int(t * 2.2) % 2 == 0)
        spr = self._spr(n, imlec)
        a = E.out_cubic((u + 0.15) / 0.2)
        if self.bitis is not None and t > self.bitis:
            a *= 1 - E.in_cubic((t - self.bitis) / 0.3)
        C.bindir(im, spr, 70 * S - (1 - a) * 30 * S, H - 120 * S - spr.height, a)


# ---------------------------------------------------------------- konuşma zarfı (talk bounce)

@lru_cache(maxsize=256)
def _hece_anlari(yol: str, mtime: float) -> tuple[tuple[float, float], ...]:
    """Satır sesindeki hece başları: ((sn, ağırlık 0..1), ...). 10 ms RMS; 40 ms'de > 6 dB yükselen ve en yüksek
    seviyenin 25 dB altından güçlü an, aralarında en az 0,14 sn."""
    with wave.open(yol, "rb") as w:
        sr, ch = w.getframerate(), w.getnchannels()
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    if ch > 1:
        x = x.reshape(-1, ch).mean(axis=1)
    h = max(1, int(sr * 0.01))
    n = len(x) // h
    if n < 6:
        return ()
    r = np.sqrt((x[: n * h].reshape(n, h) ** 2).mean(axis=1) + 1e-10)
    db = np.convolve(20 * np.log10(r), np.ones(3) / 3, "same")
    mx = float(db.max())
    out: list[tuple[float, float]] = []
    son = -100
    for i in range(4, n):
        if db[i] - db[i - 4] > 6 and db[i] > mx - 25 and i - son >= 14:
            out.append((i / 100, float(np.clip((db[i] - (mx - 25)) / 25, 0.35, 1.0))))
            son = i
    return tuple(out)


def hece_anlari(wav) -> tuple[tuple[float, float], ...] | None:
    if wav is None or not Path(wav).exists():
        return None
    p = Path(wav)
    return _hece_anlari(str(p), p.stat().st_mtime)


def yapay_heceler(sure: float, tohum: int = 0) -> tuple[tuple[float, float], ...]:
    """Ses yoksa (tahmini süre ya da yalnız görsel balon): ~3,8/sn düzensiz hece ritmi."""
    rng = np.random.default_rng(1000 + tohum)
    out, t = [], 0.03
    while t < sure - 0.1:
        out.append((t, float(rng.uniform(0.5, 1.0))))
        t += float(rng.uniform(0.18, 0.36))
    return tuple(out)


class Konusma:
    """Bir karakterin konuşma aralıkları ve hece vuruşları; deger(t) -> 0..1 sekme."""

    def __init__(self):
        self.araliklar: list[tuple[float, float, tuple]] = []   # (t0, t1, heceler (göreli sn, ağırlık))

    def ekle(self, t0: float, t1: float, heceler) -> None:
        self.araliklar.append((t0, t1, heceler))
        self.araliklar.sort(key=lambda a: a[0])

    def deger(self, t: float) -> float:
        v = 0.0
        for t0, t1, hc in self.araliklar:
            if t < t0 - 0.05 or t > t1 + 0.3:
                continue
            u = t - t0
            for th, w in hc:
                d = u - th + 0.02
                if -0.01 < d < 0.24:
                    v = max(v, w * E.tumsek(d / 0.24))
        return v

    def birlesik(self, bosluk: float = 1.0) -> list[tuple[float, float]]:
        """Kamera itmesi için birleştirilmiş konuşma aralıkları (aradaki boşluk < bosluk sn ise tek aralık)."""
        out: list[list[float]] = []
        for t0, t1, _ in self.araliklar:
            if out and t0 - out[-1][1] < bosluk:
                out[-1][1] = max(out[-1][1], t1)
            else:
                out.append([t0, t1])
        return [(a, b) for a, b in out]


# ================================================================ wojak

class Kam:
    """Sahne kamerası: sahne koordinatı (0..1, arka plan = sahne) -> ekran pikseli. Karakterler, balonlar ve
    arka plan aynı kamerayla hareket eder (itme ve kaydırma hepsine birden uygulanır)."""

    def __init__(self, zoom: float, cx: float, cy: float, W: int, H: int):
        hx, hy = 0.5 / zoom, 0.5 / zoom
        self.z = zoom
        self.cx = min(max(cx, hx), 1 - hx)
        self.cy = min(max(cy, hy), 1 - hy)
        self.W, self.H = W, H

    def nokta(self, x: float, y: float) -> tuple[float, float]:
        """Sahne pikseli (zoom 1'deki ekran pikseli) -> ekran pikseli."""
        return ((x / self.W - self.cx) * self.z + 0.5) * self.W, ((y / self.H - self.cy) * self.z + 0.5) * self.H


@lru_cache(maxsize=8)
def yay_egrisi(k: float = 1.1, frekans: float = 1.8, sonum: float = 0.36, giris: float = 0.75,
               uzunluk: float = 2.6, n: int = 1600) -> tuple[np.ndarray, np.ndarray]:
    """İkincil hareketin şekli (7. tur): out_back girişinin normalize ivmesine (e''(u)) sönümlü yay tepkisi.
    (u ekseni, tepki) döner; en büyük |tepki| = 1. Yandan girişte gövdenin eğilmesi (kayarak duran gövdenin üstü
    öne gider, sonra geri yaylanıp oturur), alttan/üstten girişte esneme-basılma bu eğriden okunur.
    frekans Hz, giris sn (u = t / giris)."""
    us = np.linspace(0.0, uzunluk, n)
    du = float(us[1] - us[0])
    w = 2 * math.pi * frekans * giris
    th = v = 0.0
    out = np.zeros(n)
    for i, u in enumerate(us):
        acc = 6 * (k + 1) * (u - 1) + 2 * k if u < 1 else 0.0
        a = acc - w * w * th - 2 * sonum * w * v
        v += a * du
        th += v * du
        out[i] = th
    return us, out / (np.abs(out).max() + 1e-12)


def _tohum01(*parca) -> list[float]:
    """Karaktere özgü kararlı sözde rastgele sayılar (0..1): ad + görsel adından."""
    import zlib
    h = zlib.crc32("|".join(str(x) for x in parca).encode())
    rng = np.random.default_rng(h)
    return [float(x) for x in rng.random(8)]


class Karakter:
    GIRIS = 0.75
    CIKIS = 0.45
    POP = 0.45          # yon: pop -> yerinde büyüyerek belirme süresi
    EGIM = 2.6          # ikincil hareket: yandan girişte en büyük eğilme (derece)
    ESNEME = 0.055      # alttan/üstten girişte en büyük esneme (oran)
    CIKIS_EGIM = 2.2    # çıkışta hızlanırken geriye eğilme (derece)
    BULANIK_ESIK = 10.0  # px/kare: bunun üstündeki hızda hareket bulanıklığı (8. tur: 7 -> 10; yavaşta iz yok)

    def __init__(self, spec: dict, zam: dict, c: Baglam, sira: int, konusma: Konusma | None = None):
        S, W, H = c.S, c.W, c.H
        self.c = c
        self.ad = f"{spec.get('id')} ({Path(str(spec['gorsel'])).stem})"   # 10. tur: denetim mesajları
        hk = getattr(c.v, "hareket", None) or {}
        self.bulanik = bool(hk.get("bulaniklik", False))
        self.ikincil = bool(hk.get("ikincil", False))
        self.canli = bool(hk.get("canli", False)) and spec.get("canli", True) is not False
        self.sabit = spec.get("canli", True) is False      # canli: false -> nefes/salınım yok (dekor, kapı, şişe)
        # 10. tur (yerleşim denetimi): yüzü olan karakter mi (chars/ ya da kit görseli, canlı); belge/kapı/telefon değil
        self.yuzlu = not self.sabit and bool({"chars", "kit"} & set(Path(str(spec["gorsel"])).parts))
        yollar = [Path(spec["gorsel"])] + [p for _, p in zam["yuz"]]
        n_yuz = len(yollar)
        agiz = zam.get("agiz", [])
        for _, _, ps in agiz:
            yollar += list(ps)
        ims = [C.yukle(p).convert("RGBA") for p in yollar]
        if len({im.size for im in ims}) == 1:
            ims = C.kirp_alfa(ims)
        else:
            ims = [C.kirp_alfa([im])[0] for im in ims]
        taraf = spec.get("taraf", "sol")
        cxn = float(spec["x"]) if spec.get("x") is not None else {"sol": 0.25, "sag": 0.75, "orta": 0.5}[taraf]
        self.taraf = taraf if spec.get("x") is None else ("sol" if cxn < 0.42 else "sag" if cxn > 0.58 else "orta")
        bak = spec.get("bakis")
        faces, bilinen = facing.resolve(yollar[0], bak)
        flip = faces != "front" and facing.needs_flip(faces, cxn)
        if flip:
            ims = [ImageOps.mirror(im) for im in ims]
        # derinlik: 0 = ön plan, 1 = en arka (küçük, ufka yakın, hafif soluk ve yumuşak)
        self.derinlik = d = float(spec.get("derinlik", 0.0) or 0.0)
        boy = float(spec.get("boy", 0.66)) * (1 - 0.30 * d)
        th = boy * H
        self.ims = []
        for im in ims:
            w = max(1, round(im.width * th / im.height))
            im = im.resize((w, round(th)), Image.LANCZOS)
            if d > 0:
                im = _derinlik_uygula(im, d, S)
            self.ims.append(im)
        self.w, self.h = self.ims[0].size
        self.cx = cxn * W
        # taban kadrajın altında kalır (kit görselleri göğüsten kesik): arkadaki karakteri küçüklüğü, sisi ve
        # önce çizilmesi uzağa iter; yükseltmek kesik kenarı gösterirdi
        self.alt = float(spec.get("alt", 0.0))
        self.taban = H + self.alt * H + 0.04 * self.h
        self.giris, self.cikis = zam["giris"], zam["cikis"]
        self.yuz_t = [t for t, _ in zam["yuz"]]
        self.sik_t = list(zam.get("sik", self.yuz_t))
        # 9. tur: açık ağız görselleri (balon) yüz listesinin sonunda; (t0, t1, [görsel indeksleri]); 11. tur: iki
        # görsel = [yarık, açık]
        self.agiz = []
        j = n_yuz
        for a, b, ps in agiz:
            self.agiz.append((a, b, list(range(j, j + len(ps)))))
            j += len(ps)
        # 9. tur: büyüyerek gelen yüz: (an, eski/yeni görünür boy oranı)
        self.buyu = []
        for tb in zam.get("buyu", []):
            j = sum(1 for ts in self.yuz_t if ts <= tb)
            if 1 <= j < n_yuz:
                h0, h1 = (self._gorunen_boy(self.ims[j - 1]), self._gorunen_boy(self.ims[j]))
                if h1 > 0:
                    self.buyu.append((tb, min(1.0, h0 / h1)))
        self.konusma = konusma or Konusma()
        self.faz = 1.7 * sira
        r = _tohum01(spec.get("id"), Path(spec["gorsel"]).name, sira)
        # canlı boşta hareket: karakter başına nefes/salınım ritmi ve küçük baş eğimi (hepsi aynı anda nefes almasın)
        self.f_nefes = 0.3 * (0.84 + 0.32 * r[0]) if self.canli else 0.3
        self.f_salin = 0.21 * (0.82 + 0.36 * r[1]) if self.canli else 0.21
        self.a_salin = 3.0 * (0.75 + 0.5 * r[2]) if self.canli else 3.0
        self.egim_a = 0.42 * (0.7 + 0.6 * r[3]) if self.canli else 0.0
        self.f_egim = 0.085 * (0.8 + 0.5 * r[4])
        self.faz2 = 6.283 * r[5]
        # baş: üst %18'lik bandın yatay merkezi
        a = np.asarray(self.ims[0].getchannel("A"))
        band = a[: max(2, int(self.h * 0.18))] > 60
        xs = np.where(band.any(axis=0))[0]
        self.bas_x = self.cx - self.w / 2 + (xs.mean() if len(xs) else self.w / 2)
        ys = np.where((a > 60).any(axis=1))[0]
        self.ust_y = self.taban - self.h + (ys[0] if len(ys) else 0)
        self.ic_yon = 1 if self.cx < W / 2 else -1   # kadrajın ortasına doğru
        self.yon = spec.get("yon")   # giriş/çıkış yönü (sol | sag | alt | ust | pop); yoksa tarafına göre
        # pop'ta pivot: yerdeki (göğüsten kesik) karakter tabandan, havadaki nesne ortasından büyür
        self.pop_orta = self.alt < -0.05
        self._onbellek: dict = {}
        self._pm: dict = {}
        # 8. tur (animasyon hakemi S3): havada duran nesne (zarf, numune kutusu, yumurta tablası) zemine "basmıyordu":
        # golge: true -> sağ alta düşen yumuşak gölge (fotoğraf baskısıyla aynı dil: masaya konmuş çıkartma)
        self.golge = None
        if spec.get("golge"):
            gl = []
            for im in self.ims:
                g, gx, gy = C.golge_katmani(im, 12 * S, 0.58)
                gl.append((C.alt_piksel_hazirla(g), gx, gy, g.convert("RGBa")))
            self.golge = {"ims": gl, "dx": 13 * S, "dy": 22 * S}

    AGIZ_ADIM = 4 / 30   # 11. tur (animasyon S6): ağız her durumda en az 4 kare kalır (saniyede en çok 7,5 değişim)

    def _agiz_seviye(self, t: float, a_: float, n: int) -> int:
        """Balon ağzının durumu: 0 kapalı (yüzün kendisi), 1 yarık, 2 açık (tek görselde 0/1). 11. tur (animasyon
        hakemi S6): ağız her hecede ince sırıtışla geniş hilal arasında gidip geliyordu (telefonda yanıp sönen
        sırıtış). Şimdi zaman `AGIZ_ADIM` adımlarına bölünür, her adımda konuşma değerinin adım içindeki en yükseği
        okunur; iki görselde kapalıdan açığa (ya da tersi) atlanmaz, arada yarık adımı olur."""
        q = self.AGIZ_ADIM

        def sev(k: int) -> int:
            if k < 0:
                return 0
            t0 = a_ + k * q
            v = max(self.konusma.deger(t0 + i * q / 4) for i in range(4))
            if n == 1:
                return 1 if v > 0.3 else 0
            return 2 if v > 0.55 else 1 if v > 0.2 else 0

        k = math.floor((t - a_) / q + 1e-6)
        s, p = sev(k), sev(k - 1)
        if n == 2 and abs(s - p) == 2:
            s = 1
        return s

    @staticmethod
    def _gorunen_boy(im: Image.Image) -> float:
        bb = im.getchannel("A").point(lambda v: 255 if v > 40 else 0).getbbox()
        return float(bb[3] - bb[1]) if bb else 0.0

    def odak(self) -> tuple[float, float]:
        """Kamera itmesinin hedefi (sahne 0..1): başın biraz altı."""
        return self.bas_x / self.c.W, (self.ust_y + 0.22 * self.h) / self.c.H

    def _mesafe(self) -> tuple[float, float]:
        W, H = self.c.W, self.c.H
        if self.yon == "pop":
            return 0.0, 0.0
        if self.yon == "alt":   # alttan yükselir (köşedeki konuk)
            return 0.0, self.h * 1.06 + 40 * self.c.S
        if self.yon == "ust":   # üstten düşer
            return 0.0, -(self.taban + 40 * self.c.S)
        if self.yon == "sol":
            return -(self.cx + self.w / 2 + 40 * self.c.S), 0.0
        if self.yon == "sag":
            return W - self.cx + self.w / 2 + 40 * self.c.S, 0.0
        if self.taraf == "sol":
            return -(self.cx + self.w / 2 + 40 * self.c.S), 0.0
        if self.taraf == "sag":
            return W - self.cx + self.w / 2 + 40 * self.c.S, 0.0
        return 0.0, H * 0.75

    def gorunur(self, t: float) -> bool:
        if self.giris is not None and t < self.giris:
            return False
        if self.cikis is not None and t > self.cikis + self.CIKIS:
            return False
        return True

    def _yer(self, t: float) -> tuple[float, float]:
        """Giriş/çıkış ötelemesi (dx, dy), sahne pikseli."""
        mx, my = self._mesafe()
        dx = dy = 0.0
        if self.giris is not None and self.yon != "pop":
            e = E.out_back((t - self.giris) / self.GIRIS, 1.1)
            dx += (1 - e) * mx
            dy += (1 - e) * my
        if self.cikis is not None and t > self.cikis:
            if self.yon == "pop":
                mx, my = (self._mesafe_kenar())
            e = E.in_cubic((t - self.cikis) / self.CIKIS)
            dx += e * mx
            dy += e * my
        return dx, dy

    def _mesafe_kenar(self) -> tuple[float, float]:
        """pop girişli karakterin çıkışı: en yakın kenardan."""
        W = self.c.W
        if self.cx < W / 2:
            return -(self.cx + self.w / 2 + 40 * self.c.S), 0.0
        return W - self.cx + self.w / 2 + 40 * self.c.S, 0.0

    def poz(self, t: float) -> dict:
        """t anındaki duruş: taban ortası (x, y; sahne pikseli), ölçek (sx, sy), eğim (derece), yüz, opaklık,
        pivot ('taban' | 'orta')."""
        S = self.c.S
        dx, dy = self._yer(t)
        mx, my = self._mesafe()
        vi = sum(1 for ts in self.yuz_t if t >= ts)
        nefes = 1 + 0.01 * math.sin(2 * math.pi * self.f_nefes * t + self.faz) if not self.sabit else 1.0
        sx = sy = nefes
        for tb, oran in self.buyu:   # 9. tur: eski boydan out_back ile büyüyerek oturur (tek karede sıçrama yok)
            if 0 <= t - tb < 0.3:
                k_ = oran + (1 - oran) * E.out_back((t - tb) / 0.3, 1.6)
                sx *= k_
                sy *= k_
        for a_, b_, vj in self.agiz:   # 9. tur: balon açıkken hece vuruşlarında ağız açık
            if a_ <= t <= b_:
                sv = self._agiz_seviye(t, a_, len(vj))
                if sv:
                    vi = vj[sv - 1] if len(vj) == 2 else vj[0]
                break
        aci = 0.0
        alfa = 1.0
        pivot = "taban"
        for ts in self.sik_t:
            b = E.tumsek((t - ts + 0.13) / 0.26)
            if b:
                sy *= 1 - 0.075 * b
                sx *= 1 + 0.05 * b
        if self.giris is not None:
            u = (t - self.giris) / self.GIRIS
            if self.yon == "pop":
                q = (t - self.giris) / self.POP
                k = max(0.0, E.out_back(q, 1.7))
                sx *= k
                sy *= k
                alfa = min(1.0, max(0.0, q) / 0.3)
                pivot = "orta" if self.pop_orta else "taban"
            elif self.ikincil and 0 <= u < 2.6:
                us, yay = yay_egrisi(1.1, 1.8, 0.36, self.GIRIS)
                y_ = float(np.interp(u, us, yay))
                if abs(mx) > 1:    # yandan: soldan giren (mx < 0, sağa gider) frenlenirken üstü sağa (aci < 0)
                    aci += self.EGIM * y_ * (1 if mx < 0 else -1)
                elif abs(my) > 1:  # alttan: yukarı giderken frenlenince esner; üstten: aşağı inerken basılır
                    es = self.ESNEME * y_ * (-1 if my > 0 else 1)
                    sy *= 1 + es
                    sx *= 1 - 0.5 * es
        if self.cikis is not None and t > self.cikis and self.ikincil:
            u = (t - self.cikis) / self.CIKIS
            cmx, _ = self._mesafe_kenar() if self.yon == "pop" else (mx, my)
            if abs(cmx) > 1:   # hızlanarak çıkarken üstü geride kalır
                aci += self.CIKIS_EGIM * E.out_cubic(min(1.0, u / 0.6)) * (1 if cmx > 0 else -1)
        # konuşma: hece başlarında küçük sekme + dikey esneme (sesle eş zamanlı)
        k = self.konusma.deger(t)
        if k:
            dy -= 9 * S * k * (1 - 0.3 * self.derinlik)
            sy *= 1 + 0.016 * k
            sx *= 1 - 0.005 * k
        if not self.sabit:
            dy += self.a_salin * S * math.sin(2 * math.pi * self.f_salin * t + self.faz * 0.6)
            if self.egim_a:
                aci += self.egim_a * math.sin(2 * math.pi * self.f_egim * t + self.faz2)
        return {"x": self.cx + dx, "y": self.taban + dy, "sx": sx, "sy": sy, "aci": aci, "vi": vi, "alfa": alfa,
                "pivot": pivot}

    def ekran_kutulari(self, t: float, kam: Kam | None = None) -> tuple[tuple, tuple] | None:
        """10. tur (yerleşim): t anında (alfa kutusu, yüz kutusu), ekran pikseli; görünmüyorsa None. ciz() ile aynı
        poz ve kamera (eğim yok sayılır: en çok ~3°)."""
        if not self.gorunur(t):
            return None
        p = self.poz(t)
        if p["sx"] <= 0.01 or p["alfa"] < 0.5:
            return None
        vi = p["vi"]
        if not hasattr(self, "_kutu"):
            self._kutu = {}
        if vi not in self._kutu:
            from . import yerlesim as Y
            ab = Y.alfa_kutusu(self.ims[vi])
            self._kutu[vi] = (ab, Y.yuz_kutusu(self.ims[vi]) or ab)
        ab, yb = self._kutu[vi]
        if ab is None:
            return None
        z = kam.z if kam is not None else 1.0
        x, y = kam.nokta(p["x"], p["y"]) if kam is not None else (p["x"], p["y"])
        w0, h0 = self.ims[vi].size
        sx, sy = p["sx"] * z, p["sy"] * z
        ust = (y - h0 * z / 2 - h0 * sy / 2) if p["pivot"] == "orta" else (y - h0 * sy)
        sol = x - w0 * sx / 2

        def ekran(bb):
            return (sol + bb[0] * sx, ust + bb[1] * sy, sol + bb[2] * sx, ust + bb[3] * sy)
        return ekran(ab), ekran(yb)

    def ciz(self, im: Image.Image, t: float, kam: Kam | None = None) -> None:
        if not self.gorunur(t):
            return
        p = self.poz(t)
        if p["sx"] <= 0.01 or p["alfa"] <= 0.003:
            return
        vi = p["vi"]
        z = 1.0
        x, y = p["x"], p["y"]
        if kam is not None:
            z = kam.z
            x, y = kam.nokta(x, y)
        w0, h0 = self.ims[vi].size
        sx, sy = p["sx"] * z, p["sy"] * z
        orta = p["pivot"] == "orta"
        if self.golge is not None:
            gsrc, gx, gy, gpm = self.golge["ims"][vi]
            gdx, gdy = self.golge["dx"] * z, self.golge["dy"] * z
            if abs(p["aci"]) < 0.01:
                ust_g = (y - h0 * z / 2 - h0 * sy / 2) if orta else (y - h0 * sy)
                g_spr, gx0, gy0 = C.alt_piksel(gsrc, x - w0 * sx / 2 - gx * sx + gdx, ust_g - gy * sy + gdy, sx, sy)
            elif orta:
                g_spr, gx0, gy0 = C.afin_pm(gpm, x + gdx, y - h0 * z / 2 + gdy, sx, sy, p["aci"], gx + w0 / 2, gy + h0 / 2)
            else:
                g_spr, gx0, gy0 = C.afin_pm(gpm, x + gdx, y + gdy, sx, sy, p["aci"], gx + w0 / 2, gy + h0)
            C.bindir(im, g_spr, gx0, gy0, p["alfa"])
        if abs(p["aci"]) < 0.01:
            # alt piksel yerleştirme: ölçek (nefes, sıkışma, kamera) ve konum tek bir örneklemeyle, kesirli olarak
            # uygulanır (C.alt_piksel). Eskiden sprite 0.001 adımla ölçeklenip tam piksele yuvarlanıyordu: arka plan
            # kamerayla alt pikselde kayarken büyük karakter 3-10 karede bir ~1 px sıçrıyordu (yavaş itmede titreme).
            # Önceden çarpılmış alfa (RGBa) ile örneklenir: saydam kenarda koyu saçak olmaz.
            src = self._onbellek.get(vi)
            if src is None:
                src = self._onbellek[vi] = C.alt_piksel_hazirla(self.ims[vi])
            ust = (y - h0 * z / 2 - h0 * sy / 2) if orta else (y - h0 * sy)
            spr, x0, y0 = C.alt_piksel(src, x - w0 * sx / 2, ust, sx, sy)
        else:
            # eğimli: tabandan (ya da ortadan) döndürme, önceden çarpılmış alfa ile
            pm = self._pm.get(vi)
            if pm is None:
                pm = self._pm[vi] = self.ims[vi].convert("RGBa")
            if orta:
                spr, x0, y0 = C.afin_pm(pm, x, y - h0 * z / 2, sx, sy, p["aci"], w0 / 2, h0 / 2)
            else:
                spr, x0, y0 = C.afin_pm(pm, x, y, sx, sy, p["aci"], w0 / 2, h0)
        if self.bulanik:
            dt = 1.0 / max(self.c.fps, 1)
            if self.gorunur(t - dt):
                dx0, dy0 = self._yer(t - dt)
                dx1, dy1 = self._yer(t)
                vx, vy = (dx1 - dx0) * z, (dy1 - dy0) * z
                if math.hypot(vx, vy) > self.BULANIK_ESIK * self.c.S:
                    # 8. tur: iz keskin ve tam opak karakterin ALTINDA, en çok 40 px (yüz bulanıp 'hayalet' olmaz)
                    spr, ox, oy_ = C.hareket_izi(spr, vx, vy, en_cok=C.IZ_EN_COK * self.c.S)
                    x0, y0 = x0 + ox, y0 + oy_
        C.bindir(im, spr, x0, y0, p["alfa"])


def _derinlik_uygula(im: Image.Image, d: float, S: float) -> Image.Image:
    """Arka plandaki karakter: hafif soluk (havada kaybolur), az doygun, çok hafif yumuşak."""
    rgb = im.convert("RGB")
    rgb = C.ayarla(rgb, bulanik=1.1 * d * S, doygunluk=1 - 0.25 * d)
    sis = Image.new("RGB", rgb.size, (120, 124, 132))
    rgb = Image.blend(rgb, sis, 0.16 * d)
    out = rgb.convert("RGBA")
    a = im.getchannel("A")
    if d * S > 0.3:
        a = a.filter(ImageFilter.GaussianBlur(0.6 * d * S))
    out.putalpha(a)
    return out


class Balon:
    """Konuşma balonu: yuvarlak, kuyruğu konuşana dönük, açılırken 'pop'."""

    def __init__(self, metin: str, k: Karakter, t0: float, sure: float, c: Baglam):
        S, W = c.S, c.W
        self.t0, self.sure, self.c = t0, sure, c
        yz = C.yazi(metin, C.FONT_DIALOG, 46 * S, (0, 0, 0), max_w=560 * S, max_lines=3, align="center",
                    satir=1.1)
        padx, pady = 36 * S, 24 * S
        bw, bh = int(yz.width + 2 * padx), int(yz.height + 2 * pady)
        kuyruk = 46 * S
        sw = 4.5 * S
        # uç (dünya koordinatı): konuşanın başının üstü, biraz içeri
        ux = k.bas_x + k.ic_yon * 0.10 * k.w
        uy = k.ust_y - 8 * S
        # balon dikdörtgeni: kuyruk tabanı balonun dış tarafına yakın
        rx0 = ux - (0.25 * bw if k.ic_yon > 0 else 0.75 * bw)
        rx0 = min(max(rx0, 40 * S), W - 40 * S - bw)
        ry0 = uy - kuyruk - bh
        if ry0 < 30 * S:
            ry0 = 30 * S
            uy = ry0 + bh + kuyruk
        # sprite (kenar payı = kontur)
        pad = int(sw * 2) + 2
        ss = 3
        SW_, SH_ = int(bw + 2 * pad), int(bh + kuyruk + 2 * pad)
        lay = Image.new("RGBA", (SW_ * ss, SH_ * ss), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        r = min(bh / 2, 38 * S)
        tbx = min(max(ux - rx0, r + 22 * S), bw - r - 22 * S)   # kuyruk tabanı (dikdörtgen içi x)
        tipx = ux - rx0
        tri = [(pad + tbx - 20 * S, pad + bh - 2 * S), (pad + tbx + 20 * S, pad + bh - 2 * S), (pad + tipx, pad + bh + kuyruk)]
        sc = lambda pts: [(x * ss, y * ss) for x, y in pts]
        siyah, beyaz = (0, 0, 0, 255), (255, 255, 255, 255)
        d.rounded_rectangle(((pad - sw) * ss, (pad - sw) * ss, (pad + bw + sw) * ss, (pad + bh + sw) * ss),
                            radius=int((r + sw) * ss), fill=siyah)
        d.polygon(sc(tri), fill=siyah, outline=siyah, width=int(sw * 2 * ss))
        d.rounded_rectangle((pad * ss, pad * ss, (pad + bw) * ss, (pad + bh) * ss), radius=int(r * ss), fill=beyaz)
        d.polygon(sc(tri), fill=beyaz)
        lay = lay.resize((SW_, SH_), Image.LANCZOS)
        lay.alpha_composite(yz, (int(pad + padx), int(pad + pady)))
        self.spr = lay
        self.ax, self.ay = pad + tipx, pad + bh + kuyruk     # sprite içindeki uç
        self.ux, self.uy = rx0 + tipx, ry0 + bh + kuyruk    # sahnedeki uç
        self.sol_pay = self.ax                               # ucun soluna/sağına taşan genişlik (kırpma için)
        self.sag_pay = self.spr.width - self.ax

    def ciz(self, im: Image.Image, t: float, kam: Kam | None = None) -> None:
        u = t - self.t0
        if u < 0 or u > self.sure + 0.16:
            return
        s = 0.3 + 0.7 * E.out_back(u / 0.24, 1.7)
        a = min(1.0, u / 0.06)
        if u > self.sure:
            q = (u - self.sure) / 0.16
            s *= 1 - 0.25 * q
            a *= 1 - q
        ux, uy, z = self.ux, self.uy, 1.0
        if kam is not None:
            ux, uy = kam.nokta(ux, uy)
            z = kam.z
            # kamera itmesinde balon kadrajdan taşmasın
            W, S = self.c.W, self.c.S
            ux = min(max(ux, 30 * S + self.sol_pay * z), W - 30 * S - self.sag_pay * z)
            uy = max(uy, 24 * S + self.ay * z)
        s *= z
        if abs(s - 1) < 1e-3:
            C.bindir_alt(im, self.spr, ux - self.ax, uy - self.ay, a)
        else:
            spr, x0, y0 = C.afin(self.spr, ux, uy, s, s, 0, self.ax, self.ay)
            C.bindir(im, spr, x0, y0, a)


class WojakCizici(Cizici):
    def hazirla(self):
        p, S, W, H = self.p, self.S, self.W, self.H
        kam = p.get("kamera") or {}
        z = kam.get("zoom", [1.0, 1.07])
        z = [1.0, float(z)] if isinstance(z, (int, float)) else [float(z[0]), float(z[1])]
        m = kam.get("merkez", [[0.5, 0.5], [0.5, 0.46]])
        m = [m, m] if isinstance(m[0], (int, float)) else m
        self.z, self.m = z, [tuple(map(float, m[0])), tuple(map(float, m[1]))]
        self.etiket = DaktiloEtiket(self.p.get("etiket"), self.c, olaylar(self.sahne, "etiket"), 0.6)
        zam = karakter_zamanlari(self.sahne)
        bal = balon_olaylari(self.sahne)
        konusmalar = konusma_araliklari(self.sahne)
        self.karakterler = []
        kmap = {}
        for i, cs in enumerate(p.get("karakterler", [])):
            k = Karakter(cs, zam[cs["id"]], self.c, i, konusmalar.get(cs["id"]))
            self.karakterler.append(k)
            kmap[cs["id"]] = k
        self.cizim_sirasi = sorted(self.karakterler, key=lambda k: -k.derinlik)   # arkadakiler önce
        # konuşana doğru hafif kamera itmesi (it: zoom artışı; odak: merkezin konuşana kayma oranı)
        konusan_var = any(k.konusma.araliklar for k in self.karakterler)
        self.it = float(kam.get("it", 0.05 if konusan_var else 0.0))
        self.odak_g = float(kam.get("odak", 0.4))
        self.itmeler = []
        for k in self.karakterler:
            fx, fy = k.odak()
            for a, b in k.konusma.birlesik():
                self.itmeler.append((a, b, fx, fy))
        # 9. tur: `it` olayı: kamera vurgu itmesi (zoom x(1+guc), sure sn; x/y verilirse merkez oraya kayar); kalıcı
        self.vurgu_it = [(o.zaman, float(o.p.get("guc", 0.08)), max(0.05, float(o.p.get("sure", 0.5))),
                          o.p.get("x"), o.p.get("y")) for o in olaylar(self.sahne, "it")]
        ek = 1.0
        for _, g_, _, _, _ in self.vurgu_it:
            ek *= 1 + max(0.0, g_)
        zm = max(z) * (1 + self.it) * ek + 0.01
        bg = C.yukle(p["arka"]).convert("RGB")
        if p.get("kirp"):   # [x0, y0, x1, y1] (0..1): fotoğrafın istenmeyen kenarını at
            k_ = [float(v) for v in p["kirp"]]
            bg = bg.crop((round(k_[0] * bg.width), round(k_[1] * bg.height), round(k_[2] * bg.width),
                          round(k_[3] * bg.height)))
        bg = C.kapla(bg, round(W * zm), round(H * zm), tuple(p.get("odak", (0.5, 0.5))))
        self.bg = C.ayarla(bg, bulanik=float(p.get("bulanik", 1.6)) * S, karart=float(p.get("karart", 0.12)),
                           doygunluk=float(p.get("doygunluk", 0.85)))
        # kaynağa bir kez (her karede maske bindirmek pahalı); `vinyet` (6. tur): düz zeminde bilinçli yakın çekim
        C.vinyet_uygula(self.bg, float(p.get("vinyet", 0.42)))
        self.balonlar = []
        for i, o in enumerate(bal):
            sure = float(o.p.get("sure") or 2.5)
            sonraki = [x.zaman for x in bal[i + 1:] if x.p["karakter"] == o.p["karakter"]]
            if sonraki:
                sure = min(sure, sonraki[0] - o.zaman - 0.05)
            self.balonlar.append(Balon(str(o.p["metin"]), kmap[o.p["karakter"]], o.zaman, sure, self.c))
        # 7. tur: paralaks (arka plan kamerayı daha az izler: itmede karakterler arka plandan çok büyür, derinlik
        # hissi) ve arka plan dokusu (gren + toz; karakterler net kalır). Video `hareket` ayarı, sahne üstüne yazar.
        hk = getattr(self.c.v, "hareket", None) or {}
        self.paralaks = float(kam.get("paralaks", hk.get("paralaks", 0.0)) or 0.0)
        dk = p.get("doku") if p.get("doku") is not None else hk.get("doku", False)
        self.doku = dk if isinstance(dk, dict) else ({"gren": 0.035, "toz": 18} if dk else None)
        self.toz = Z.Toz(int(self.doku["toz"]), self.c.S, tohum=self.sahne.no) if self.doku else None

    def itme(self, t: float) -> tuple[float, tuple[float, float] | None]:
        """(itme miktarı 0..1, konuşanın odak noktası) — konuşma aralıklarının yumuşak pencereleri."""
        top, fx, fy = 0.0, 0.0, 0.0
        for a, b, x, y in self.itmeler:
            w = E.in_out_sine((t - a + 0.4) / 1.3) * (1 - E.in_out_sine((t - b - 0.1) / 1.5))
            if w > 0:
                top += w
                fx += w * x
                fy += w * y
        if top <= 1e-6:
            return 0.0, None
        return min(1.0, top), (fx / top, fy / top)

    def kam(self, t: float) -> Kam:
        u = E.in_out_sine(t / self.dur)
        z = E.karistir(self.z[0], self.z[1], u)
        mx, my = E.karistir(self.m[0][0], self.m[1][0], u), E.karistir(self.m[0][1], self.m[1][1], u)
        if self.it > 0:
            q, f = self.itme(t)
            if f is not None:
                z *= 1 + self.it * q
                mx += (f[0] - mx) * self.odak_g * q
                my += (f[1] - my) * self.odak_g * q
        for t0, g_, su, x_, y_ in self.vurgu_it:
            q = E.out_cubic((t - t0) / su) if t > t0 else 0.0
            if q > 0:
                z *= 1 + g_ * q
                if x_ is not None:
                    mx += (float(x_) - mx) * q
                if y_ is not None:
                    my += (float(y_) - my) * q
        return Kam(z, mx, my, self.W, self.H)

    def kam_derin(self, k: Kam, d: float) -> Kam:
        """Paralaks: d (0 = ön plan, 1 = arka plan düzlemi) derinliğindeki katmanın kamerası."""
        f = 1 - self.paralaks * d
        if f >= 0.999:
            return k
        return Kam(1 + (k.z - 1) * f, 0.5 + (k.cx - 0.5) * f, 0.5 + (k.cy - 0.5) * f, self.W, self.H)

    def ciz(self, t):
        k = self.kam(t)
        kb = self.kam_derin(k, 1.0)
        im = C.kamera(self.bg, self.W, self.H, kb.z, (kb.cx, kb.cy))
        if self.doku:
            if self.doku.get("gren"):
                C.gren_uygula(im, t, float(self.doku["gren"]))
            if self.toz is not None:
                self.toz.ciz(im, t)
        for kr in self.cizim_sirasi:
            kr.ciz(im, t, self.kam_derin(k, 0.8 * kr.derinlik) if kr.derinlik else k)
        for b in self.balonlar:
            b.ciz(im, t, k)
        self.etiket.ciz(im, t)
        return im


def konusma_araliklari(sahne: Sahne) -> dict[str, Konusma]:
    """Karakter -> konuşma (satır sesiyle eş zamanlı hece vuruşları; açık balon olayları için yapay ritim)."""
    out: dict[str, Konusma] = {}
    for i, st in enumerate(sahne.satirlar):
        k = st.konusan or st.balon
        if not k:
            continue
        hc = hece_anlari(st.wav) if not st.tahmini else None
        if hc is None:
            hc = yapay_heceler(st.sure or 0.0, i)
        out.setdefault(k, Konusma()).ekle(st.t0, st.t1, hc)
    for j, o in enumerate(sorted((o for o in sahne.olaylar if o.tip == "balon"), key=lambda o: o.zaman)):
        sure = min(float(o.p.get("sure") or 2.5), 1.6)
        out.setdefault(str(o.p["karakter"]), Konusma()).ekle(o.zaman, o.zaman + sure, yapay_heceler(sure, 50 + j))
    return out


# ================================================================ foto

class FotoCizici(Cizici):
    def hazirla(self):
        p, S, W, H = self.p, self.S, self.W, self.H
        foto = C.yukle(p["gorsel"]).convert("RGB")
        arka = C.yukle(p["arka"]).convert("RGB") if p.get("arka") else foto
        self.arka = C.ayarla(C.kapla(arka, round(W * 1.1), round(H * 1.1)), bulanik=26 * S, karart=0.62,
                             doygunluk=0.55)
        boy = float(p.get("boy", 0.72))
        kenar = max(12 * S, min(28 * S, 0.026 * min(W * 0.78, H * boy)))
        ph = C.sigdir(foto, W * 0.78 - 2 * kenar, H * boy - 2 * kenar)
        b = int(round(kenar))
        pr = Image.new("RGBA", (ph.width + 2 * b, ph.height + 2 * b), (247, 245, 238, 255))
        pr.paste(ph, (b, b))
        ImageDraw.Draw(pr).rectangle((0, 0, pr.width - 1, pr.height - 1), outline=(214, 210, 200, 255),
                                     width=max(1, int(S)))
        self.spr, ox, oy = C.golgeli(pr, 22 * S, 0.62, 9 * S, 16 * S)
        self.ax, self.ay = ox + pr.width / 2, oy + pr.height / 2
        # 7. tur: gölge ayrı katman: baskı havadayken (iniş) gölge daha uzak, yumuşak ve soluk; oturunca sıkılaşır
        hk = getattr(self.c.v, "hareket", None) or {}
        self.bulanik = bool(hk.get("bulaniklik", False))
        self.canli_golge = bool(hk.get("ikincil", False))
        if self.canli_golge:
            self.baski = pr
            self.golgeler = []
            for h in (0.0, 0.33, 0.66, 1.0):
                g, gx, gy = C.golge_katmani(pr, (22 + 26 * h) * S, 0.62 * (1 - 0.4 * h))
                self.golgeler.append((h, g, gx, gy))
        self.egim = float(p.get("egim", -2.2))
        self.giris = str(p.get("giris", "alt"))
        z = p.get("zoom", 1.05)
        self.zoom = float(z[1] if isinstance(z, list) else z)
        self.z = foto_zamanlari(self.sahne)
        self.etiket = DaktiloEtiket(p.get("etiket"), self.c, olaylar(self.sahne, "etiket"), self.z["etiket"], None)
        self.atif = C.yazi(str(p["atif"]), C.FONT_BOLD, 19 * S, (230, 230, 230)) if p.get("atif") else None
        # x: baskının yatay merkezi (0..1; konuk karakter için yer açmak: ör. 0.4 + konuk sağda). Ortada değilse
        # atıf ekran köşesine değil baskının altına, sağ kenarına hizalı yazılır (köşedeki konuğa binmesin)
        self.x = float(p.get("x", 0.5))
        self.pr_w, self.pr_h = pr.width, pr.height

    def _atif_yeri(self) -> tuple[float, float] | None:
        if self.atif is None:
            return None
        W, H, S = self.W, self.H, self.S
        if abs(self.x - 0.5) < 1e-3:
            return W - 70 * S - self.atif.width, H - 82 * S - self.atif.height
        # 8. tur: baskının SON (yakınlaşmış, eğik) alt kenarına göre: zoom > 1,04'te baskı atıfın üstüne büyüyordu
        th = math.radians(abs(self.egim))
        yari_h = (self.pr_h * math.cos(th) + self.pr_w * math.sin(th)) / 2 * self.zoom
        yari_w = (self.pr_w * math.cos(th) + self.pr_h * math.sin(th)) / 2 * self.zoom
        return W * self.x + yari_w - self.atif.width, min(H * 0.455 + yari_h + 12 * S, H - 40 * S - self.atif.height)

    def sabit_engeller(self) -> list[tuple]:
        yer = self._atif_yeri()
        if yer is None:
            return []
        return [(yer[0], yer[1], yer[0] + self.atif.width, yer[1] + self.atif.height)]

    def _poz(self, t):
        W, H = self.W, self.H
        u = (t - self.z["inis"]) / 0.72
        e = E.out_back(u, 1.0)
        cx, cy = W * self.x, H * 0.455
        yon = {"alt": (0, 1), "ust": (0, -1), "sag": (1, 0), "sol": (-1, 0)}.get(self.giris, (0, 1))
        cx += (1 - e) * yon[0] * W * 0.9
        cy += (1 - e) * yon[1] * H * 0.95
        aci = self.egim + (1 - E.out_cubic(u)) * (7.0 if yon[0] >= 0 else -7.0)
        kalk = 1 - E.out_cubic(u)                         # 1: havada, 0: masaya oturdu
        s = (1.0 + 0.07 * kalk) * (1 + (self.zoom - 1) * E.in_out_sine(t / self.dur))
        return u, cx, cy, aci, s, kalk

    def ciz(self, t):
        W, H, S = self.W, self.H, self.S
        im = C.kamera(self.arka, W, H, 1.0 + 0.06 * E.in_out_sine(t / self.dur), (0.5, 0.5))
        u, cx, cy, aci, s, kalk = self._poz(t)
        if u > 0 and self.canli_golge:
            # gölge: yükseklikle uzaklaşır (sağ alta), büyür, yumuşar, solar
            h = min(1.0, max(0.0, kalk * 1.6))
            hh, g, gx, gy = min(self.golgeler, key=lambda q: abs(q[0] - h))
            ox, oy = (9 + 34 * h) * S, (16 + 48 * h) * S
            gs = s * (1 + 0.03 * h)
            spr, x0, y0 = C.afin(g, cx + ox, cy + oy, gs, gs, aci, gx + self.baski.width / 2, gy + self.baski.height / 2)
            C.bindir(im, spr, x0, y0)
            spr, x0, y0 = C.afin(self.baski, cx, cy, s, s, aci)
            if self.bulanik:
                _, px, py, _, _, _ = self._poz(t - 1 / self.c.fps)
                if math.hypot(cx - px, cy - py) > 10 * S:
                    spr, ox_, oy_ = C.hareket_izi(spr, cx - px, cy - py, en_cok=C.IZ_EN_COK * S)
                    x0, y0 = x0 + ox_, y0 + oy_
            C.bindir(im, spr, x0, y0)
        elif u > 0:
            spr, x0, y0 = C.afin(self.spr, cx, cy, s, s, aci, self.ax, self.ay)
            if self.bulanik:
                _, px, py, _, _, _ = self._poz(t - 1 / self.c.fps)
                if math.hypot(cx - px, cy - py) > 10 * S:
                    spr, ox_, oy_ = C.hareket_izi(spr, cx - px, cy - py, en_cok=C.IZ_EN_COK * S)
                    x0, y0 = x0 + ox_, y0 + oy_
            C.bindir(im, spr, x0, y0)
        self.etiket.ciz(im, t)
        if self.atif is not None:
            ax, ay = self._atif_yeri()
            C.bindir(im, self.atif, ax, ay, 0.65)
        return im


# ================================================================ manşet / belge

class MansetCizici(Cizici):
    def hazirla(self):
        p, S, W, H = self.p, self.S, self.W, self.H
        doc = C.yukle(p["gorsel"]).convert("RGB")
        z = p.get("zoom", 1.18)
        self.zson = float(z[1] if isinstance(z, list) else z)
        zm = max(self.zson, 1.0) + 0.02
        BW, BH = round(W * zm), round(H * zm)
        arka = C.yukle(p["arka"]).convert("RGB") if p.get("arka") else doc
        page = C.ayarla(C.kapla(arka, BW, BH), bulanik=30 * S, karart=0.78, doygunluk=0.4)
        boy = float(p.get("boy", 0.80))
        d = C.sigdir(doc, BW * 0.84, BH * boy)
        dl = d.convert("RGBA")
        spr, ox, oy = C.golgeli(dl, 26 * S, 0.7, 0, 14 * S)
        x0, y0 = (BW - d.width) // 2, (BH - d.height) // 2
        C.bindir(page, spr, x0 - ox, y0 - oy)
        C.vinyet_uygula(page, 0.3)
        self.page = page
        self.etiket = DaktiloEtiket(p.get("etiket"), self.c, olaylar(self.sahne, "etiket"), 0.7)
        self.BW, self.BH = BW, BH
        renk = tuple(p.get("renk", (255, 221, 40)))
        self.renk = np.array(renk, np.float32) / 255.0
        self.kutular = []
        for k in p.get("kutular") or []:
            k = [float(v) for v in k]
            if max(k) <= 1.0:
                bx = [k[0] * d.width, k[1] * d.height, k[2] * d.width, k[3] * d.height]
            else:
                r = d.width / doc.width
                bx = [v * r for v in k]
            padx, pady = 6 * S, 0.12 * (bx[3] - bx[1])
            bx = [x0 + bx[0] - padx, y0 + bx[1] - pady, x0 + bx[2] + padx, y0 + bx[3] + pady]
            bx = [int(round(v)) for v in bx]
            self.kutular.append((bx, self._kalem_maske(bx[2] - bx[0], bx[3] - bx[1], len(self.kutular))))
        self.ts = manset_zamanlari(self.sahne)
        # 7. tur: vurgu stili kutu başına (vurgula olayının `stil`/`renk`i): kalem (fosforlu, vars.) | daire (elle
        # çizilmiş kırmızı çember) | alt_cizgi (elle çizilmiş dalgalı alt çizgi)
        self.stiller = {}
        for o in olaylar(self.sahne, "vurgula"):
            k = int(o.p["kutu"]) - 1
            st = str(o.p.get("stil", "kalem"))
            self.stiller[k] = (st, tuple(Z.renk(o.p.get("renk"), (206, 30, 36))) if st != "kalem" else None)
        # kamera: sırayla her kutunun merkezine doğru kayar (kalem nereden geçiyorsa oraya)
        self.hedefler = [((b[0] + b[2]) / 2 / BW, (b[1] + b[3]) / 2 / BH) for b, _ in self.kutular]

    def _kalem_maske(self, w: int, h: int, seed: int) -> np.ndarray:
        """Fosforlu kalem izi: uçları yuvarlak, kenarları hafif düzensiz, içi hafif dokulu (0..1)."""
        rng = np.random.default_rng(100 + seed)
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        ust = 0.06 * h + rng.normal(0, 0.015 * h, w).cumsum() * 0.05
        alt = 0.94 * h + rng.normal(0, 0.015 * h, w).cumsum() * 0.05
        m = ((yy >= ust[None, :]) & (yy <= alt[None, :])).astype(np.float32)
        r = h / 2
        for cx in (r, w - r):  # yuvarlak uçlar
            dx = np.abs(xx - cx)
            out = (dx > 0) & (((xx < r) & (cx == r)) | ((xx > w - r) & (cx == w - r)))
            m[out & (((xx - cx) ** 2 + (yy - r) ** 2) > r * r)] = 0
        doku = 0.86 + 0.1 * rng.random((1, w)).astype(np.float32).repeat(h, 0)
        return np.clip(m * doku, 0, 1)

    def _el_cizimi(self, pg: Image.Image, bx, stil: str, renk, pr: float, tohum: int) -> None:
        """Elle çizilmiş işaret (7. tur): çember kutunun çevresinde ~380° döner (uçları üst üste biner, hafif
        eğik, yarıçapı dalgalı), alt çizgi kutunun altında hafif dalgalı ve sonunda yukarı kıvrık. Kalınlık
        uçlarda incelir (kalem basıncı). 2x örneklemeyle çizilip küçültülür."""
        S = self.S
        rng = np.random.default_rng(300 + tohum)
        x0, y0, x1, y1 = bx
        cx, cy, rx, ry = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2, (y1 - y0) / 2
        if stil == "daire":
            # geniş kutuda (belge satırı) elips komşu satırları üstü çizilmiş gibi keser: süperelips, kutuya yakın
            # (dikeyde satır aralığında kalır); kare kutuda düz elips
            rx, ry = rx + 16 * S, ry + 5 * S
            us_ = 2 + min(4.0, (rx / max(ry, 1)) / 3)
            f1, f2 = rng.uniform(0, 6.28, 2)
            n = 200
            th0 = math.radians(-160)
            tam = math.radians(385)
            egim = math.radians(rng.uniform(-1.2, 1.2))
            pts = []
            for i in range(n + 1):
                u = i / n
                th = th0 + tam * u
                c_, s_ = math.cos(th), math.sin(th)
                r_ = 1 + 0.02 * math.sin(2 * th + f1) + 0.012 * math.sin(3 * th + f2) + 0.03 * u
                px = rx * r_ * math.copysign(abs(c_) ** (2 / us_), c_)
                py = ry * r_ * math.copysign(abs(s_) ** (2 / us_), s_)
                pts.append((cx + px * math.cos(egim) - py * math.sin(egim), cy + px * math.sin(egim) + py * math.cos(egim)))
        else:
            n = 60
            yb = y1 + 3 * S
            f1 = rng.uniform(0, 6.28)
            pts = [(x0 - 10 * S + (x1 - x0 + 20 * S) * i / n,
                    yb + 3 * S * math.sin(6.28 * 1.3 * i / n + f1) - 2 * S * i / n) for i in range(n + 1)]
            pts += [(pts[-1][0] + 10 * S, pts[-1][1] - 9 * S)]
        k = max(2, int(round(len(pts) * pr)))
        yol = pts[:k]
        xs, ys = [p_[0] for p_ in pts], [p_[1] for p_ in pts]
        pad = 20 * S
        L, T = min(xs) - pad, min(ys) - pad
        w, h = int(max(xs) - L + pad) + 1, int(max(ys) - T + pad) + 1
        ss = 2
        lay = Image.new("RGBA", (w * ss, h * ss), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        kal = 7 * S * ss
        for i, ((xa, ya), (xb, yb)) in enumerate(zip(yol, yol[1:])):
            u = i / max(1, len(pts) - 2)
            bas = 0.55 + 0.45 * min(1.0, u / 0.08, (1 - u) / 0.1 if u < 1 else 0)
            d.line([((xa - L) * ss, (ya - T) * ss), ((xb - L) * ss, (yb - T) * ss)], fill=tuple(renk) + (235,),
                   width=max(1, int(kal * bas)), joint="curve")
        lay = lay.resize((w, h), Image.LANCZOS)
        C.bindir(pg, lay, L, T)

    def ciz(self, t):
        pg = self.page.copy()
        for i, ((bx, mask), t0) in enumerate(zip(self.kutular, self.ts)):
            st = self.stiller.get(i, ("kalem", None))
            if st[0] != "kalem":
                pr = E.in_out_sine((t - t0) / 0.7)
                if pr > 0:
                    self._el_cizimi(pg, bx, st[0], st[1], pr, i)
                continue
            pr = E.in_out_cubic((t - t0) / 0.6)
            if pr <= 0:
                continue
            w = bx[2] - bx[0]
            n = max(1, int(round(w * pr)))
            reg = (bx[0], bx[1], bx[0] + n, bx[3])
            a = np.asarray(pg.crop(reg), np.float32) / 255.0
            mk = mask[:, :n, None] * 0.82
            out = a * (1 - mk * (1 - self.renk[None, None, :]))
            pg.paste(Image.fromarray((out * 255).astype(np.uint8), "RGB"), reg[:2])
        u = E.in_out_sine(t / self.dur)
        m = (0.5, 0.5)
        for (hx, hy), t0 in zip(self.hedefler, self.ts):
            k = E.in_out_sine((t - t0 + 0.5) / 1.4)
            if k > 0:   # yalnız dikeyde izle: yatayda kaydırmak satırın öbür ucunu kadraj dışında bırakıyor
                m = (0.5, E.karistir(m[1], E.karistir(0.5, hy, 0.8), k))
        im = C.kamera(pg, self.W, self.H, 1.0 + (self.zson - 1.0) * u, m)
        self.etiket.ciz(im, t)
        return im


# ================================================================ harita

class HaritaCizici(Cizici):
    def hazirla(self):
        from .harita import BOLGELER, HaritaCizer
        p, S, W, H = self.p, self.S, self.W, self.H
        bolge = p.get("bolge", "avrupa")
        if isinstance(bolge, str) and bolge not in BOLGELER:
            raise ValueError(f"{self.sahne.yer}: bölge '{bolge}' yok ({', '.join(BOLGELER)}) ya da sözlük ver")
        r = p.get("cozunurluk") or ("110m" if bolge == "dunya" else "50m")
        z = p.get("zoom", [1.0, 1.06])
        self.z = [1.0, float(z)] if isinstance(z, (int, float)) else [float(z[0]), float(z[1])]
        zm = max(self.z) + 0.01
        BW, BH = round(W * zm), round(H * zm)
        self.BW, self.BH = BW, BH
        hc = HaritaCizer(bolge, BW, BH, r)
        self.taban = hc.taban()
        C.vinyet_uygula(self.taban, 0.38)
        renk = tuple(p.get("renk", (205, 62, 52)))
        self.renk = renk
        self.parlak = tuple(min(255, int(v * 1.35 + 40)) for v in renk)
        zam, vz = harita_zamanlari(self.sahne)
        etk = p.get("etiketler", False)
        self.ulkeler = []
        for kod, t0 in zam:
            mk = hc.maske(kod)
            if mk is None:
                continue
            mask, bbox = mk
            glow = self._parilti(mask, bbox, 14 * S)
            lab = None
            if etk is True or (isinstance(etk, list) and kod in [str(x) for x in etk]):
                pt = hc.etiket_noktasi(kod)
                if pt:
                    lab = (pt, C.yazi(hc.ulkeler[kod].ad_tr, C.FONT_BOLD, 25 * S, C.BEYAZ, stroke=3 * S,
                                      stroke_fill=(10, 12, 16)))
            self.ulkeler.append((kod, t0, mask, bbox, glow, lab))
        self.vurgu = None
        mrk = (0.5, 0.5)
        if vz:
            v = p["vurgu"] if isinstance(p["vurgu"], dict) else {"kod": vz[0]}
            mk = hc.maske(vz[0])
            if mk:
                mask, bbox = mk
                vr = tuple(v.get("renk", C.YESIL))
                halka = self._halka(mask, bbox, 5 * S)
                pt = hc.etiket_noktasi(vz[0]) or ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)
                ad = C.buyuk(str(v.get("ad", hc.ulkeler[vz[0]].ad_tr)))
                kutu = self._cagri(ad, v.get("etiket"), vr)
                self.vurgu = (vz[1], mask, bbox, vr, halka, pt, kutu)
                mrk = (E.karistir(0.5, pt[0] / BW, 0.35), E.karistir(0.5, pt[1] / BH, 0.35))
        self.merkez = mrk
        # 7. tur: rotalar (a'dan b'ye çizilerek uzanan yay; uçta parlayan nokta, varışta halka)
        self.rotalar = []
        for i, (t0, sure, q) in enumerate(rota_zamanlari(self.sahne)):
            a_, b_ = self._rota_noktasi(hc, q["a"]), self._rota_noktasi(hc, q["b"])
            if a_ is None or b_ is None:
                raise ValueError(f"{self.sahne.yer}: rota noktası bulunamadı ({q['a']} -> {q['b']})")
            kavis = float(q.get("kavis", 0.22))
            (x0, y0), (x1, y1) = a_, b_
            L = math.hypot(x1 - x0, y1 - y0)
            nx, ny = (-(y1 - y0) / max(L, 1e-6), (x1 - x0) / max(L, 1e-6))
            if ny > 0:   # yay yukarı doğru kabarsın
                nx, ny = -nx, -ny
            cx_, cy_ = (x0 + x1) / 2 + nx * kavis * L, (y0 + y1) / 2 + ny * kavis * L
            us = np.linspace(0, 1, 120)
            pts = np.stack([(1 - us) ** 2 * x0 + 2 * (1 - us) * us * cx_ + us ** 2 * x1,
                            (1 - us) ** 2 * y0 + 2 * (1 - us) * us * cy_ + us ** 2 * y1], axis=1)
            uz = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(pts, axis=0).T))])
            renk = tuple(Z.renk(q.get("renk"), C.SARI))
            et = None
            if q.get("etiket"):
                et = C.yazi(str(q["etiket"]), C.FONT_BOLD, 28 * S, C.BEYAZ, stroke=3 * S, stroke_fill=(10, 12, 16))
            self.rotalar.append({"t0": t0, "sure": sure, "pts": pts, "uz": uz, "renk": renk,
                                 "kesik": bool(q.get("kesik", False)), "et": et, "i": i})
        self.baslik = None
        if p.get("baslik"):
            self.baslik = C.yazi(str(p["baslik"]), C.FONT_DIALOG, 54 * S, C.BEYAZ, max_w=1100 * S, max_lines=2,
                                 golge=(0, 3 * S, 6 * S, 0.6))
        self.aciklama = None
        if p.get("aciklama"):
            # 4. tur: 26 -> 34 pt (izlenme hakemi: telefonda ~14 px, okunmuyordu; olgu çekincesi taşıyor)
            yz = C.yazi(str(p["aciklama"]), C.FONT_BOLD, 34 * S, (232, 234, 238))
            sq = int(28 * S)
            w, h = int(sq + 14 * S + yz.width + 36 * S), int(max(sq, yz.height) + 24 * S)
            lay = C.yuvarlak_kutu(w, h, 5 * S, (8, 10, 14, 200))
            ImageDraw.Draw(lay).rectangle((int(18 * S), (h - sq) // 2, int(18 * S) + sq, (h - sq) // 2 + sq),
                                          fill=renk + (255,))
            lay.alpha_composite(yz, (int(18 * S + sq + 14 * S), (h - yz.height) // 2))
            self.aciklama = lay

    @staticmethod
    def _rota_noktasi(hc, v):
        """ISO3 kodu (ülkenin etiket noktası) ya da [boylam, enlem] -> taban pikseli."""
        if isinstance(v, (list, tuple)) and len(v) == 2:
            px, py, _ = hc.proj(np.array([float(v[0])]), np.array([float(v[1])]))
            return float(px[0]), float(py[0])
        k = str(v)
        if k not in hc.ulkeler:
            return None
        pt = hc.etiket_noktasi(k)
        if pt is None:
            mk = hc.maske(k)
            if mk is None:
                return None
            bb = mk[1]
            pt = ((bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2)
        return pt

    def _rota_ciz(self, base: Image.Image, r: dict, t: float) -> None:
        """Rotayı tabana çiz (kamera öncesi; kamera örneklemesi kenarı yumuşatır). İlerleme in_out_cubic, kesik
        çizgi seçeneği, uçta parlayan nokta, varışta genişleyen halka."""
        S = self.S
        q = E.in_out_cubic((t - r["t0"]) / r["sure"])
        if q <= 0:
            return
        pts, uz = r["pts"], r["uz"]
        hedef = q * uz[-1]
        n = int(np.searchsorted(uz, hedef))
        yol = [tuple(p_) for p_ in pts[:max(1, n)]]
        if n < len(pts):
            k = max(1, n)
            f = (hedef - uz[k - 1]) / max(uz[k] - uz[k - 1], 1e-6) if k < len(uz) else 1.0
            yol.append(tuple(pts[k - 1] + (pts[min(k, len(pts) - 1)] - pts[k - 1]) * min(1.0, f)))
        xs, ys = [p_[0] for p_ in yol], [p_[1] for p_ in yol]
        pad = 40 * S
        L, T = min(xs) - pad, min(ys) - pad
        w, h = int(max(xs) - L + pad) + 1, int(max(ys) - T + pad) + 1
        ss = 2
        lay = Image.new("RGBA", (w * ss, h * ss), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        yy = [((x - L) * ss, (y - T) * ss) for x, y in yol]
        kal = max(2, int(6 * S * ss))
        if len(yy) > 1:
            d.line([(x + 3 * S * ss, y + 4 * S * ss) for x, y in yy], fill=(8, 10, 14, 120), width=kal + 2 * ss,
                   joint="curve")
            if r["kesik"]:
                ac = True
                adim = 22 * S * ss
                birikim = 0.0
                for (xa, ya), (xb, yb) in zip(yy, yy[1:]):
                    birikim += math.hypot(xb - xa, yb - ya)
                    if ac:
                        d.line([(xa, ya), (xb, yb)], fill=r["renk"] + (255,), width=kal)
                    if birikim >= adim * (0.62 if ac else 0.38):
                        ac, birikim = not ac, 0.0
            else:
                d.line(yy, fill=r["renk"] + (255,), width=kal, joint="curve")
        # başlangıç noktası
        x0, y0 = yy[0]
        rr = 7 * S * ss
        d.ellipse((x0 - rr, y0 - rr, x0 + rr, y0 + rr), fill=r["renk"] + (255,), outline=(10, 12, 16, 255),
                  width=max(1, int(2 * S * ss)))
        lay = lay.resize((w, h), Image.LANCZOS)
        C.bindir(base, lay, L, T)
        xe, ye = yol[-1]
        if q < 1:   # uçta parlayan nokta
            gl = Z._yumusak_nokta(max(2, int(16 * S)))
            self._renk_bas(base, (255, 250, 220), (xe - gl.width / 2, ye - gl.height / 2), gl, 0.9)
            r2 = 6 * S
            ImageDraw.Draw(base).ellipse((xe - r2, ye - r2, xe + r2, ye + r2), fill=(255, 255, 255))
        else:       # varış: genişleyen halka + kalıcı nokta
            u = (t - r["t0"] - r["sure"]) / 0.7
            if u < 1:
                rh = (8 + 46 * E.out_cubic(u)) * S
                lay2 = Image.new("RGBA", (int(2 * rh + 10), int(2 * rh + 10)), (0, 0, 0, 0))
                ImageDraw.Draw(lay2).ellipse((5, 5, 5 + 2 * rh, 5 + 2 * rh), outline=r["renk"] + (255,),
                                             width=max(1, int(5 * S * (1 - u) + 1)))
                C.bindir(base, lay2, xe - rh - 5, ye - rh - 5, 1 - u)
            r3 = 9 * S
            ImageDraw.Draw(base).ellipse((xe - r3, ye - r3, xe + r3, ye + r3), fill=r["renk"], outline=(10, 12, 16),
                                         width=max(1, int(2 * S)))

    def _parilti(self, mask, bbox, r):
        pad = int(r * 3)
        m = Image.new("L", (mask.width + 2 * pad, mask.height + 2 * pad), 0)
        m.paste(mask, (pad, pad))
        return m.filter(ImageFilter.GaussianBlur(r)), (bbox[0] - pad, bbox[1] - pad)

    def _halka(self, mask, bbox, kal):
        pad = int(kal * 4)
        m = Image.new("L", (mask.width + 2 * pad, mask.height + 2 * pad), 0)
        m.paste(mask, (pad, pad))
        # MaxFilter(1) Pillow'u çökertiyor (küçük ön izleme boyutunda kal < 1): en az 3
        big = m.filter(ImageFilter.MaxFilter(max(3, int(round(kal)) * 2 + 1))).filter(ImageFilter.GaussianBlur(kal * 0.6))
        halka = ImageChops.subtract(big, m)
        return halka, (bbox[0] - pad, bbox[1] - pad)

    def _cagri(self, ad: str, etiket, renk) -> Image.Image:
        S = self.S
        a = C.yazi(ad, C.FONT_BOLD, 34 * S, (10, 14, 12), aralik=0.06)
        b = C.yazi(str(etiket), C.FONT_DIALOG, 36 * S, (10, 14, 12)) if etiket else None
        padx, pady = 22 * S, 14 * S
        w = int(max(a.width, b.width if b else 0) + 2 * padx)
        h = int(a.height + (b.height + 6 * S if b else 0) + 2 * pady)
        lay = C.yuvarlak_kutu(w, h, 8 * S, tuple(renk) + (250,))
        lay.alpha_composite(a, (int(padx), int(pady)))
        if b:
            lay.alpha_composite(b, (int(padx), int(pady + a.height + 6 * S)))
        spr, _, _ = C.golgeli(lay, 14 * S, 0.55, 0, 6 * S)
        return spr

    @staticmethod
    def _renk_bas(dst, renk, xy, mask, a):
        if a <= 0.003:
            return
        m = mask if a >= 0.997 else mask.point(C._alfa_lut(int(a * 255)))
        x, y = int(xy[0]), int(xy[1])
        l, t_ = max(0, -x), max(0, -y)
        r, b = min(m.width, dst.width - x), min(m.height, dst.height - y)
        if r <= l or b <= t_:
            return
        if (l, t_, r, b) != (0, 0, m.width, m.height):
            m = m.crop((l, t_, r, b))
        dst.paste(tuple(renk), (x + l, y + t_, x + r, y + b), m)

    def _nokta(self, pt, zoom, merkez):
        sw, sh = self.BW, self.BH
        ww, wh = sw / zoom, sh / zoom
        cx = min(max(merkez[0] * sw, ww / 2), sw - ww / 2)
        cy = min(max(merkez[1] * sh, wh / 2), sh - wh / 2)
        return (pt[0] - (cx - ww / 2)) * self.W / ww, (pt[1] - (cy - wh / 2)) * self.H / wh

    def ciz(self, t):
        S, W, H = self.S, self.W, self.H
        # animasyonu bitmiş ülkeler bir kez tabana işlenir (zaman sırasıyla çizildiğinde her karede tekrar yok)
        if not hasattr(self, "_statik") or t < self._statik_t:
            self._statik, self._statik_t, self._bitti = self.taban.copy(), 0.0, set()
        for kod, t0, mask, bbox, glow, lab in self.ulkeler:
            if kod not in self._bitti and t - t0 > 1.05:
                self._renk_bas(self._statik, self.renk, bbox[:2], mask, 1.0)
                self._bitti.add(kod)
        self._statik_t = t
        base = self._statik.copy()
        for kod, t0, mask, bbox, glow, lab in self.ulkeler:
            u = t - t0
            if u < 0 or kod in self._bitti:
                continue
            a = E.out_cubic(u / 0.35)
            k = E.out_cubic(u / 0.7)
            renk = tuple(int(E.karistir(pa, ra, k)) for pa, ra in zip(self.parlak, self.renk))
            self._renk_bas(base, renk, bbox[:2], mask, a)
            if u < 1.0:
                gm, gxy = glow
                self._renk_bas(base, self.parlak, gxy, gm, 0.55 * (1 - E.out_cubic(u / 1.0)))
        for r in self.rotalar:
            self._rota_ciz(base, r, t)
        if self.vurgu:
            t0, mask, bbox, vr, (halka, hxy), pt, kutu = self.vurgu
            u = t - t0
            if u >= 0:
                self._renk_bas(base, vr, bbox[:2], mask, E.out_cubic(u / 0.4))
                nab = 0.55 + 0.45 * math.sin(2 * math.pi * 1.1 * u) if u > 0.4 else E.out_cubic(u / 0.4)
                self._renk_bas(base, (235, 255, 240), hxy, halka, nab)
        uz = E.in_out_sine(t / self.dur)
        zoom = E.karistir(self.z[0], self.z[1], uz)
        im = C.kamera(base, W, H, zoom, self.merkez)
        for kod, t0, mask, bbox, glow, lab in self.ulkeler:
            if lab and t >= t0 + 0.1:
                (px, py), spr = lab
                x, y = self._nokta((px, py), zoom, self.merkez)
                a = E.out_cubic((t - t0 - 0.1) / 0.3)
                C.bindir_alt(im, spr, x - spr.width / 2, y - spr.height / 2 + (1 - a) * 8 * S, a)
        for r in self.rotalar:
            if r["et"] is not None and t >= r["t0"] + r["sure"]:
                a = E.out_cubic((t - r["t0"] - r["sure"]) / 0.3)
                x, y = self._nokta(tuple(r["pts"][-1]), zoom, self.merkez)
                C.bindir_alt(im, r["et"], x + 14 * S, y - r["et"].height - 10 * S + (1 - a) * 8 * S, a)
        if self.vurgu:
            t0, mask, bbox, vr, _, pt, kutu = self.vurgu
            u = t - t0 - 0.25
            if u >= 0:
                x, y = self._nokta(pt, zoom, self.merkez)
                a = E.out_cubic(u / 0.3)
                bx = min(x + 110 * S, W - kutu.width - 40 * S)
                by = max(y - 150 * S, 140 * S)
                lu = E.out_cubic(u / 0.25)
                # 7. tur: çizgi + nokta kenarı yumuşatılmış katman, alt pikselde (kamerayla kayarken basamaklanmasın)
                cz, lx, ly = C.cizgi_katmani(x, y, x + (bx + 12 * S - x) * lu, y + (by - y) * lu, max(1.0, 4 * S),
                                             (245, 255, 248), nokta=8 * S)
                C.bindir_alt(im, cz, lx, ly)
                s = 0.7 + 0.3 * E.out_back((u - 0.12) / 0.3, 1.5)
                if u > 0.12:
                    spr, x0, y0 = C.afin(kutu, bx, by, s, s, 0, 0, kutu.height * 0.5)
                    C.bindir(im, spr, x0, y0, a)
        a = E.out_cubic(t / 0.5)
        if self.baslik is not None:
            C.bindir(im, self.baslik, 80 * S, 64 * S - (1 - a) * 12 * S, a)
            ImageDraw.Draw(im).rectangle((80 * S, 64 * S + self.baslik.height + 12 * S,
                                          80 * S + 140 * S * E.out_cubic((t - 0.15) / 0.5),
                                          64 * S + self.baslik.height + 18 * S), fill=C.SARI)
        if self.aciklama is not None:
            C.bindir(im, self.aciklama, 80 * S, H - 110 * S - self.aciklama.height, a)
        return im


# ================================================================ sayaç

class SayacCizici(Cizici):
    """Büyük sayaç: artan (out_cubic) ya da azalan (doğrusal, 60 -> 0) sayım, yıl odometresi; `deger` olaylarıyla
    yeni değerlere sayar (etiket ve renk değişebilir: 1.267 doktor -> 20.000 hasta -> en az 17)."""

    def hazirla(self):
        p, S = self.p, self.S
        self.zemin = Z.Zemin(self.c, p)
        self.pal = self.zemin.palet
        self.yil = p.get("yil")
        self.bolumler = sayac_bolumleri(self.sahne)
        self.t0, self.t1 = self.bolumler[0]["t0"], self.bolumler[-1]["t1"]
        self.f = C.font(C.FONT_CARD, (300 if self.yil else 270) * S)
        self.hucre = max(self.f.getlength(str(d)) for d in range(10))
        tops, bots = zip(*[(self.f.getbbox(str(d))[1], self.f.getbbox(str(d))[3]) for d in range(10)])
        m = 0.07 * self.f.size
        self.bant = (min(tops) - m, max(bots) + m)          # rakamların görünür bandı (odometre penceresi)
        self.yuk = self.bant[1] - self.bant[0]
        self._rk: dict = {}
        self._et: dict = {}
        self.ust = C.yazi(C.buyuk(str(p["ust"])), C.FONT_BOLD, 32 * S, self.pal.ikincil, aralik=0.22) \
            if p.get("ust") else None
        self.yuvarla = bool((getattr(self.c.v, "hareket", None) or {}).get("bulaniklik", False))

    def _etiket(self, metin):
        if not metin:
            return None
        if metin not in self._et:
            self._et[metin] = C.yazi(str(metin), C.FONT_DIALOG, 76 * self.S, self.pal.vurgu, max_w=1400 * self.S,
                                     max_lines=2, align="center", golge=self.pal.golge_t(self.S, 4, 8))
        return self._et[metin]

    def _w(self, ch: str) -> float:
        return self.hucre if ch.isdigit() else self.f.getlength(ch)

    def _rakam(self, ch: str, renk) -> Image.Image:
        """Tek karakter, rakam bandına kırpılmış (rakamlar sabit genişlikte hücrede ortalı)."""
        key = (ch, renk)
        if key not in self._rk:
            w = int(math.ceil(self._w(ch))) + 2
            lay = Image.new("RGBA", (w, int(math.ceil(self.yuk))), (0, 0, 0, 0))
            ImageDraw.Draw(lay).text(((w - self.f.getlength(ch)) / 2, -self.bant[0]), ch, font=self.f,
                                     fill=tuple(renk) + (255,))
            self._rk[key] = lay
        return self._rk[key]

    # 10. tur (animasyon hakemi S1): tekerleğin izi keskin rakamın ALTINDA (karakterlerin hareket izi gibi). Eskiden
    # bütün hücre dikeyde 0,26-0,38 hücre kutu bulanıktı ve hızı tekerleğin kendi hareketinden değil sayının
    # hızından (hiz / 10^k) alıyordu: duran 6, 8, 9 bulanıp "0" okunuyordu ("≈6.318" -> "≈0.310", "292,9 M" ->
    # "202,0 M", "38" -> "30": sayı geriye gidiyor gibiydi).
    IZ_SEVIYE = (0.06, 0.12, 0.2, 0.3, 0.42, 0.56, 0.75, 1.0)   # iz uzunluğu (hücre)
    IZ_OPAK = 0.38           # izin opaklığı (keskin rakam her zaman tam opak ve okunur)
    HIZLI = 0.5              # birim/kare: birler tekerleği bundan hızlıysa sayaç "sayısal" (her kare round(v))

    def _serit(self, renk, seviye: float, bos: bool = False) -> np.ndarray:
        """0-9-0 rakam şeridi (11 hücre, dikey), dikeyde `seviye` hücre boyu kutu bulanık; önceden çarpılmış alfa.
        bos (8. tur): 0 hücresi boş (öndeki basamak: sayı o basamağa ulaşınca boştan 1'e döner); 10. tur: boş
        şeritte bulanıklık üstten 9'u sarmalamaz (boş tekerlekte "9" hayaleti olmasın)."""
        key = ("serit", tuple(renk), seviye, bos)
        if key in self._rk:
            return self._rk[key]
        hucreler = [np.asarray(self._rakam(str(d % 10), renk).convert("RGBa"), np.float32) for d in range(10)]
        if bos:
            hucreler[0] = np.zeros_like(hucreler[0])
        h = hucreler[0].shape[0]
        a = np.concatenate(hucreler, axis=0)            # döngüsel 10 hücre
        n = int(round(seviye * h))
        if n >= 2:
            ust = a[-(n // 2 + 1):]
            pad = np.concatenate([np.zeros_like(ust) if bos else ust, a, a[:n - n // 2]], axis=0)
            c = np.cumsum(pad, axis=0)
            a = (c[n:n + 10 * h] - c[:10 * h]) / n
        a = np.concatenate([a, a[:h]], axis=0)          # 11. hücre (sarma için)
        self._rk[key] = a
        return a

    def _teker(self, renk, konum: float, iz: float, bos: bool = False) -> Image.Image:
        """Sayaç tekerleği: konum (0..10, kesirli: yuvarlanma), iz (hücre: dönüşün hareket izi) -> hücre katmanı.
        Keskin şerit üstte, bulanık kopya `IZ_OPAK` ile altında: rakam her karede okunur kalır.
        bos: öndeki boş basamak (0 yerine boşluk)."""
        a = self._serit(renk, 0.0, bos)
        h = a.shape[0] // 11
        y0 = min(10 * h, int(round((konum % 10) * h)))
        parca = a[y0:y0 + h]
        if iz > 0.03:
            sev = min(self.IZ_SEVIYE, key=lambda x: abs(x - iz))
            b_ = self._serit(renk, sev, bos)[y0:y0 + h]
            if "profil" not in self._rk:   # iz pencerenin üst/alt kenarında söner (silindir; kutu gibi durmasın)
                yy = (np.arange(h, dtype=np.float32) + 0.5) / h
                self._rk["profil"] = (np.minimum(1.0, np.minimum(yy, 1 - yy) / 0.22) ** 1.5)[:, None, None]
            parca = parca + self.IZ_OPAK * b_ * self._rk["profil"] * (1.0 - parca[..., 3:4] / 255.0)
        return Image.fromarray(np.clip(parca + 0.5, 0, 255).astype(np.uint8), "RGBa").convert("RGBA")

    @staticmethod
    def _konumlar(av: float, D: int) -> list[float]:
        """Mekanik kilometre sayacı (yavaş sayım), en alttaki tekerlekten: birler v mod 10; her üst tekerlek
        floor(v / 10^k) mod 10 + YALNIZ alttaki tekerlek 9'dan 0'a dönerken (görünen konumu 9..10) yumuşatılmış
        (in_out_sine) kesir. Konumlar v ile tekdüze: hiçbir tekerlek geri dönmez."""
        pos = [av % 10.0]
        for k in range(1, D):
            c = min(1.0, max(0.0, pos[-1] % 10.0 - 9.0)) if pos[-1] < 10.0 else 0.0
            taban = math.floor(av / 10 ** k + 1e-9) % 10
            pos.append(taban + E.in_out_sine(c))
        return pos

    def _yuvarlanan(self, v: float, hiz: float, b: dict, v_once: float | None = None) -> list:
        """7. tur: sayım tekerlekli sayaç gibi akar. Dönen (soldan sağa): tekerlek (konum 0..10, iz hücre, boş mu)
        ve binlik ayracı (".", opaklık).

        10. tur (animasyon hakemi S1, "sayı geriye okunuyor"):
        - hızlı sayımda (birler > `HIZLI` birim/kare) bütün tekerlekler round(v)'nin rakamlarını gösterir (sayısal
          sayaç); kendi ortalama hızı yarım hücre/kareyi aşan tekerleğin altında dönüş izi. Her kare doğru bir tam
          sayı: alt basamak keskin, üst basamaklar onunla aynı karede ilerler (yarım dönmüş üst basamağın yanında
          duran 9 "39 -> 30" gibi okunuyordu);
        - yavaşta mekanik kilometre sayacı (`_konumlar`): üst tekerlek yalnız alttaki 9'dan 0'a dönerken, yumuşak;
          iz tekerleğin bu karedeki gerçek dönüşünden (duran tekerlek hep keskin);
        - basamak sayısı hedeften (8. tur); sayının henüz varmadığı öndeki tekerlek boştur ve boştan 1'e döner:
          öndeki sıfır hiç çizilmez; geçiş anı (sayısal <-> mekanik) tekdüze (round(v) ile v arasındaki fark yarım
          hücreden az, hız yarım hücreden fazla)."""
        av = abs(v)
        n = max(0, int(math.floor(av + 1e-6)))
        D = max(len(str(n)), int(b.get("basamak", 0) or 0))
        out = []
        if hiz > self.HIZLI:
            N = int(round(av))
            D = max(D, len(str(N)))
            for k in range(D - 1, -1, -1):
                g = 10 ** k
                bos = k > 0 and N < g
                s_ = hiz / g
                iz = 0.0 if (bos or s_ <= self.HIZLI) else min(1.0, 0.5 * s_)
                out.append((0.0 if bos else float((N // g) % 10), iz, bos))
                if k and k % 3 == 0:
                    out.append((".", 0.0 if bos else 1.0))
            return out
        pos = self._konumlar(av, D)
        once = self._konumlar(abs(v_once), D) if v_once is not None else None
        for k in range(D - 1, -1, -1):
            bos = k > 0 and n < 10 ** k
            konum = pos[k]
            iz = 0.0
            if once is not None:
                dk = (konum - once[k] + 5.0) % 10.0 - 5.0
                iz = min(0.5, 0.5 * abs(dk)) if abs(dk) > 0.06 else 0.0
            out.append((konum, iz, bos))
            if k and k % 3 == 0:
                # binlik ayracı: solundaki basamak boşsa görünmez, boştan 1'e dönerken onunla belirir
                out.append((".", 1.0 if not bos else min(1.0, max(0.0, konum))))
        return out

    def _bolum(self, t: float) -> tuple[int, dict]:
        i = 0
        for j, b in enumerate(self.bolumler):
            if t >= b["t0"]:
                i = j
        return i, self.bolumler[i]

    def _say_katmani(self, t: float, b: dict) -> Image.Image:
        """O anki sayı; ortalı. Yıl modunda değişen basamaklar odometre gibi aşağıdan yukarı döner.
        Sonek ('+') için baştan yer ayrılır: belirdiğinde sayı yerinden kaymaz."""
        S = self.S
        u = (t - b["t0"]) / max(b["t1"] - b["t0"], 1e-3)
        renk = b["renk"]
        if b["yil"]:
            a, c = int(b["a"]), int(b["b"])
            v = a + (c - a) * E.kirp(u)
            y0 = int(math.floor(v)) if v < c else c
            frac = E.in_out_cubic(min(1.0, (v - y0) * 1.6)) if y0 < c else 0.0
            s0, s1 = str(y0), str(min(y0 + 1, c))
        elif self.yuvarla:
            # 8. tur: rakamlar sabit sayıda tekerlekte, sağa yaslı (öndeki boş tekerlekler solda). Önek (≈) görünen
            # ilk rakamın hemen solunda ve sayının görünen genişliği 0,27 sn'lik ortalamayla değişir: basamak
            # eklenince sayı zıplamadan, yumuşakça sola açılır (eskiden 940 -> 1.005'te bir karede kayıyordu)
            dig = self._yuvarlanan_katman(t, b, min(u, 1.0))
            sonek = b["sonek"]
            son_w = self.f.getlength(sonek) if sonek else 0.0
            onek_w = sum(self._w(ch) for ch in b["onek"])
            gorunen = self._gorunen_w(t, b)
            # 10. tur: önek görünen ilk rakamın SOLUNDA kalır (ortalamalı genişlik geride kalınca "≈" yeni eklenen
            # "1"in üstüne biniyordu: 9.999 -> 10.000'de "≈0.783" gibi okunuyordu); ortalama yalnız ortalamada
            sol = max(gorunen, dig.info.get("gercek", gorunen))
            # önek bu değerle geliyorsa (1.267 -> ≈20.000) bir karede belirmez: 0,22 sn'de açılır, sayı yumuşakça kayar
            a_on = E.out_cubic((t - b["t0"]) / 0.22) if (b.get("onek_once") is not None and not b.get("ani")
                                                          and b["onek"] != b["onek_once"]) else 1.0
            Wt = int(math.ceil(max(dig.width, onek_w + sol + son_w + 4)))
            lay = Image.new("RGBA", (Wt, dig.height), (0, 0, 0, 0))
            lay.alpha_composite(dig, (Wt - dig.width, 0))
            x = Wt - 4 - son_w - sol - onek_w
            for ch in b["onek"]:
                if a_on > 0.01:
                    spr = self._rakam(ch, renk)
                    if a_on < 0.99:
                        spr = spr.copy()
                        spr.putalpha(spr.getchannel("A").point(C._alfa_lut(int(255 * a_on))))
                    lay.alpha_composite(spr, (int(round(x)), 0))
                x += self._w(ch)
            onek_w *= a_on
            if sonek and u >= 1.0:   # sonek ('+') sayım bitince belirir; yeri baştan ayrılmıştı
                a = E.out_cubic((t - b["t1"]) / 0.25)
                sk = self._rakam(sonek, renk)
                if a < 1:
                    sk = sk.copy()
                    sk.putalpha(sk.getchannel("A").point(C._alfa_lut(int(255 * a))))
                lay.alpha_composite(sk, (int(round(Wt - 4 - son_w)), int(-(1 - a) * 20 * S) if a < 1 else 0))
            lay.info["ax"] = Wt - (onek_w + gorunen + son_w + 4) / 2      # görünen sayının ortası
            lay.info["onek_sag"] = Wt - 4 - son_w - sol                     # önekin sağ kenarı
            lay.info["rakam_sol"] = Wt - 4 - son_w - dig.info.get("gercek", 0.0)   # ilk görünen rakamın solu
            return lay
        else:
            k = E.lineer(u) if b["b"] < b["a"] else E.out_cubic(u)
            v = b["a"] + (b["b"] - b["a"]) * k
            s0 = b["onek"] + C.say_bicimle(v)
            s1, frac = s0, 0.0
        sonek = b["sonek"]
        son_w = self.f.getlength(sonek) if sonek else 0.0
        W = int(sum(self._w(ch) for ch in s0) + son_w) + 4
        Hh = int(math.ceil(self.yuk))
        lay = Image.new("RGBA", (W, Hh), (0, 0, 0, 0))
        x = 0.0
        for c0, c1 in zip(s0, s1):
            if c0 == c1 or frac <= 0:
                lay.alpha_composite(self._rakam(c0, renk), (int(round(x)), 0))
            else:
                off = int(round(frac * Hh))
                hucre = Image.new("RGBA", self._rakam(c0, renk).size, (0, 0, 0, 0))
                hucre.alpha_composite(self._rakam(c0, renk), (0, -off))
                hucre.alpha_composite(self._rakam(c1, renk), (0, Hh - off))
                lay.alpha_composite(hucre, (int(round(x)), 0))
            x += self._w(c0)
        if sonek and u >= 1.0:
            a = E.out_cubic((t - b["t1"]) / 0.25)
            sk = self._rakam(sonek, renk)
            if a < 1:
                sk = sk.copy()
                sk.putalpha(sk.getchannel("A").point(C._alfa_lut(int(255 * a))))
            lay.alpha_composite(sk, (int(round(x)), int(-(1 - a) * 20 * S)) if a < 1 else (int(round(x)), 0))
        return lay

    def _deger(self, t: float, b: dict) -> float:
        if b["t1"] - b["t0"] < 1e-3:   # sure: 0 -> yeni değer bir anda
            return b["b"] if t >= b["t0"] else b["a"]
        u = (t - b["t0"]) / max(b["t1"] - b["t0"], 1e-3)
        if b.get("log") and b["b"] > b["a"] >= 0 and t > b["t0"]:
            # 9. tur (izlenme N1): olcek: log -> 0'dan 300 milyona out_cubic ilk karede 8 basamağa sıçrıyordu ("0"
            # 1 sn bekleyip 9 basamağa açılıyordu); geometrik sayımda her basamak eşit sürede eklenir
            a0 = max(1.0, b["a"])
            k = E.in_out_sine(E.kirp(u)) if u < 1 else 1.0
            return a0 * (b["b"] / a0) ** k
        k = E.lineer(u) if b["b"] < b["a"] else E.out_cubic(u)
        return b["a"] + (b["b"] - b["a"]) * k

    def _rakam_w(self, v: float) -> float:
        """v'nin rakamlarının (binlik ayraçlarıyla) genişliği."""
        d = len(str(max(0, int(math.floor(abs(v) + 1e-6)))))
        return d * self.hucre + ((d - 1) // 3) * self._w(".")

    def _gorunen_w(self, t: float, b: dict) -> float:
        """Görünen rakamların genişliği, son 0,27 sn'nin ortalaması (basamak eklenince yumuşak açılma)."""
        if b.get("ani"):
            return self._rakam_w(b["b"])
        dt = 1 / self.c.fps
        ws = [self._rakam_w(self._deger(t - k * dt, b)) for k in range(9)]
        return sum(ws) / len(ws)

    def _yuvarlanma(self, eski: Image.Image, yeni: Image.Image, e: float) -> Image.Image:
        """Bir anda gelen değerin geçişi (10. tur): iki sayı rakam bandı yüksekliğindeki pencerede, aralarında bir
        satır boşlukla birlikte yukarı kayar (e: 0 eski, 1 yeni; out_back taşması yeniyi biraz yukarı geçirir).
        Pencere dışı kırpılır: gerçek sayaç penceresi gibi."""
        h = max(eski.height, yeni.height)
        sat = self.yuk * 1.08
        Wl = int(max(eski.width, yeni.width)) + 4
        pen = Image.new("RGBA", (Wl, h), (0, 0, 0, 0))
        for lay_, dy in ((eski, -e * sat), (yeni, (1.0 - e) * sat)):
            x = int(round(Wl / 2 - lay_.info.get("ax", lay_.width / 2)))
            y = int(round(dy))
            l_, t_ = max(0, -x), max(0, -y)
            r_, b_ = min(lay_.width, Wl - x), min(lay_.height, h - y)
            if r_ > l_ and b_ > t_:
                pen.alpha_composite(lay_.crop((l_, t_, r_, b_)), (x + l_, y + t_))
        pen.info["ax"] = Wl / 2
        return pen

    def _yuvarlanan_katman(self, t: float, b: dict, u: float) -> Image.Image:
        v = self._deger(t, b)
        vo = self._deger(t - 1 / self.c.fps, b)
        hiz = 0.0 if b.get("ani") else abs(v - vo)   # birim / kare
        renk = b["renk"]
        parcalar = self._yuvarlanan(v, hiz, b, None if b.get("ani") else vo)   # önek _say_katmani'nde
        sonek = b["sonek"]
        son_w = self.f.getlength(sonek) if sonek else 0.0
        Wt = int(sum(self._w(q[0]) if isinstance(q[0], str) else self.hucre for q in parcalar) + son_w) + 4
        Hh = int(math.ceil(self.yuk))
        lay = Image.new("RGBA", (Wt, Hh), (0, 0, 0, 0))
        x = 0.0
        gercek, goruldu = 0.0, False      # görünen rakamların gerçek genişliği (önek bunun soluna)
        for q in parcalar:
            if isinstance(q[0], str):
                ch, al = q
                if al > 0.01:
                    spr = self._rakam(ch, renk)
                    if al < 0.99:
                        spr = spr.copy()
                        spr.putalpha(spr.getchannel("A").point(C._alfa_lut(int(255 * al))))
                    lay.alpha_composite(spr, (int(round(x)), 0))
                if goruldu:
                    gercek += self._w(ch) * min(1.0, max(0.0, al))
                x += self._w(ch)
            else:
                konum, iz, bos = q
                if goruldu:
                    gercek += self.hucre
                elif not bos or konum > 1e-3:
                    goruldu = True
                    gercek += self.hucre * (min(1.0, konum) if bos else 1.0)
                lay.alpha_composite(self._teker(renk, konum, iz, bos), (int(round(x)), 0))
                x += self.hucre
        lay.info["gercek"] = gercek
        return lay

    def ciz(self, t):
        S, W, H = self.S, self.W, self.H
        im = self.zemin.ciz(t, self.dur)
        i, b = self._bolum(t)
        lay = self._say_katmani(t, b)
        bit = t - b["t1"]
        ani = i > 0 and b["t1"] - b["t0"] < 1e-3      # sure: 0 -> yeni değer bir anda
        if ani and bit < SAYAC_GECIS:
            # 10. tur (animasyon hakemi S2): bir anda gelen değer tek karede değişmez ("≈20.000" -> "en az 17" kesme
            # gibi okunuyordu): eski sayı tekerlek penceresinden yukarı çıkar, yenisi alttan yuvarlanıp hafif
            # taşmayla oturur (out_back, 0,26 sn; odometrenin dili)
            onc = self.bolumler[i - 1]
            lay = self._yuvarlanma(self._say_katmani(onc["t1"] + 5.0, onc), lay,
                                   E.out_back(max(0.0, bit) / SAYAC_GECIS, SAYAC_GECIS_K))
        if ani:
            # 8. tur: yeni değer "yumruk" gibi oturur ve rengiyle kısa bir parlama yapar; 10. tur: pencereye oturduğu
            # anda (varis), yuvarlanmadan sonra
            q = t - b["varis"]
            s = 1.0 + 0.08 * (1 - E.out_cubic(q / 0.3)) if q >= 0 else 1.0
            fl = 0.16 * (1 - E.out_cubic(q / 0.35)) if q >= 0 else 0.0
            if fl > 0.004:
                im = Image.blend(im, Image.new("RGB", im.size, tuple(int(c) for c in b["renk"][:3])), fl)
        elif bit >= 0:
            s = 1.0 + 0.06 * E.tumsek(bit / 0.3)
        elif i == 0:
            s = 0.94 + 0.06 * E.out_cubic(t / 0.45)
        else:
            s = 1.0
        son_bit = t - self.t1
        s *= Z.nefes(t) if son_bit > 0.4 else 1.0
        a = E.out_cubic(t / 0.35)   # sayı sahne başında görünür (0 / başlangıç yılı), t0'da saymaya başlar
        etiketler = [x["etiket"] for x in self.bolumler]
        et_var = any(etiketler)
        cy = H * (0.45 if et_var else 0.5) + Z.suzul(t, 0.4, 2.0) * S
        spr, x0, y0 = C.afin(lay, W / 2, cy, s, s, 0, lay.info.get("ax"), lay.height / 2)
        C.bindir(im, spr, x0, y0, a)
        if self.ust is not None:
            C.bindir_alt(im, self.ust, W / 2 - self.ust.width / 2, cy - self.yuk / 2 - 40 * S - self.ust.height, a)
        # etiket: ilk bölümde sayım başlarken belirir; değiştiğinde eskisi söner, yenisi gelir
        et = self._etiket(b["etiket"])
        ey = cy + self.yuk / 2 + 52 * S
        sonraki = self.bolumler[i + 1] if i + 1 < len(self.bolumler) else None
        on_son = 1.0
        if sonraki is not None and sonraki["t1"] - sonraki["t0"] < 1e-3 and sonraki["etiket"] != b["etiket"]:
            # 9. tur (animasyon S2): bir anda gelen değerden ÖNCE eski etiket söner ("en az 17 hasta" 3 kare okunuyordu)
            on_son = 1 - E.out_cubic((t - (sonraki["t0"] - 0.2)) / 0.18)
        if i == 0:
            ae = E.out_cubic((t - self.t0 - 0.35) / 0.45) * on_son
        else:
            # 8. tur: eski etiket önce yukarı kayıp söner (0,16 sn), yenisi ondan sonra gelir (iki etiket üst üste
            # binmesin: "hasta" ile "bebek · ABD" 5 kare çakışıyordu)
            degisti = b["etiket"] != self.bolumler[i - 1]["etiket"]
            ani_b = b["t1"] - b["t0"] < 1e-3
            ae = (E.out_cubic((t - b["t0"] - (0.12 if ani_b else 0.13)) / 0.3) if degisti else 1.0) * on_son
            onceki = self._etiket(self.bolumler[i - 1]["etiket"])
            if onceki is not None and degisti and not ani_b:   # anide eski etiket zaten sönmüş
                ao = 1 - E.out_cubic((t - b["t0"]) / 0.14)
                if ao > 0:
                    C.bindir_alt(im, onceki, W / 2 - onceki.width / 2, ey - (1 - ao) * 26 * S, ao)
        if et is not None:
            C.bindir_alt(im, et, W / 2 - et.width / 2, ey + (1 - ae) * 24 * S, ae)
        # ilk bitişte sayının altında çizgi
        bit0 = t - self.bolumler[0]["t1"]
        if bit0 >= 0:
            lw = 260 * S * E.out_cubic(bit0 / 0.4)
            yl = cy + self.yuk / 2 + 22 * S
            ImageDraw.Draw(im).rectangle((W / 2 - lw, yl, W / 2 + lw, yl + 6 * S), fill=self.pal.vurgu)
        return im


# ================================================================ bölüm kartı

class BolumKartiCizici(Cizici):
    """Bölüm kartı. Varsayılan: koyu zemin + gren. bindirme: önceki sahnenin son karesi donar, kararır ve hafifçe
    bulanır; kart onun üstünde açılır (kısa, 1-1,5 sn; siyah ekran yok, müzik kesilmez). marka: önce kanal
    imzası (tarihselwojak) belirir, sonra yukarı kayıp küçülür ve bölüm başlığı gelir."""

    def hazirla(self):
        p, S, W, H = self.p, self.S, self.W, self.H
        self.bindirme = bool(p.get("bindirme"))
        self.karart = float(p.get("karart", 0.45))
        self.zem = C.gradyan_zemin(W, H, (22, 23, 27), (2, 2, 3), (0.5, 0.5))
        self.donuk = None
        ust = p.get("ust") or (f"BÖLÜM {p['numara']}" if p.get("numara") else "")
        self.ust = C.yazi(C.buyuk(str(ust)), C.FONT_BOLD, 36 * S, C.SARI, aralik=0.32) if ust else None
        self.baslik = C.yazi(str(p["baslik"]), C.FONT_DIALOG, 112 * S, C.BEYAZ, max_w=1500 * S, max_lines=2,
                             align="center", golge=(0, 5 * S, 10 * S, 0.6))
        self.marka = None
        if p.get("marka"):
            from .kanal import logotip
            self.marka = logotip(self.c.v.filigran or "tarihselwojak", self.c, 118 * S)
        # kısa kartta animasyon sıkışır (2 sn'lik kartın zamanlaması ölçeklenir); marka varsa başlık sonra gelir
        self.k = min(1.0, self.dur / 2.0)
        self.ofset = min(0.34, 0.3 * self.dur) if self.marka is not None else 0.0

    def dondur(self, onceki: Image.Image) -> None:
        """Önceki sahnenin son karesi (filigransız)."""
        self.donuk = onceki.copy()
        k = C.ayarla(onceki, bulanik=5 * self.S, karart=C.donuk_karart(onceki, self.karart), doygunluk=0.7)
        C.vinyet_uygula(k, 0.35)
        self.donuk_k = k

    def ciz(self, t):
        S, W, H = self.S, self.W, self.H
        if self.bindirme and self.donuk is not None:
            # 7. tur: kararma 0,18 sn out_cubic -> 0,3 sn in_out_sine: ikinci karede bir anda %46 kararıp bulanıyordu
            # (kare farkı 37/255, "flaş" gibi); şimdi 9 kareye yayılır
            a = E.in_out_sine(t / 0.3)
            im = Image.blend(self.donuk, self.donuk_k, a) if a < 0.999 else self.donuk_k.copy()
            z = 1.0 + 0.025 * E.in_out_sine(t / self.dur)
            if z > 1.0005:
                im = C.kamera(im, W, H, z, (0.5, 0.5))
            C.gren_uygula(im, t, 0.04)
        else:
            im = self.zem.copy()
            C.gren_uygula(im, t, 0.07)
        k, o = self.k, self.ofset
        cy = H * 0.5 + (40 * S if self.marka is not None else 0)
        if self.marka is not None:
            lg = self.marka
            u0 = E.out_back(t / (0.26 * k + 0.05), 1.4)
            yuk = E.in_out_cubic((t - o + 0.06) / 0.4)
            s = (0.6 + 0.4 * u0) * (1 - 0.42 * yuk)
            ly = E.karistir(H * 0.5, cy - 150 * S, yuk)
            spr, x0, y0 = C.afin(lg, W / 2, ly, s, s)
            C.bindir(im, spr, x0, y0, min(1.0, t / 0.08))
        tt = t - o
        # çizgi ortadan dışa
        lw = (self.baslik.width / 2 + 40 * S) * E.out_cubic((tt - 0.08 * k) / (0.5 * k))
        if lw > 1:
            ImageDraw.Draw(im).rectangle((W / 2 - lw, cy - 2 * S, W / 2 + lw, cy + 2 * S), fill=C.SARI)
        if self.ust is not None:
            a = E.out_cubic((tt - 0.2 * k) / (0.45 * k))
            C.bindir(im, self.ust, W / 2 - self.ust.width / 2, cy - 30 * S - self.ust.height - (1 - a) * 18 * S, a)
        # başlık: soldan sağa silinerek açılır + hafif yükselir
        u = E.out_cubic((tt - 0.32 * k) / (0.65 * k))
        if u > 0:
            b = self.baslik
            n = max(1, int(b.width * u))
            parca = b.crop((0, 0, n, b.height))
            C.bindir(im, parca, W / 2 - b.width / 2, cy + 26 * S + (1 - u) * 16 * S, min(1.0, u * 1.6))
        return im


# ================================================================ metin / alıntı

class MetinCizici(Cizici):
    """Alıntı / anahtar söz kartı. yazim: kelime (kelime kelime belirir, vars.) | daktilo (harf harf, imleçli).
    Kâğıt zeminde mürekkep rengi; çeviri fosforlu kalemle. `ustunu_ciz` olayı: ana yazının üstü kırmızı çizilir."""

    def hazirla(self):
        p, S = self.p, self.S
        self.zemin = Z.Zemin(self.c, p, ic=(80, 70, 64), dis=(30, 26, 25))
        pal = self.pal = self.zemin.palet
        self.renk = Z.renk(p.get("renk"), pal.metin)
        self.daktilo = p.get("yazim", "kelime") == "daktilo"
        metin = str(p["metin"])
        yol = C.FONT_MONO if self.daktilo else C.FONT_DIALOG
        f = C.font(yol, (112 if self.daktilo else 124) * S)
        maxw = 1560 * S
        while True:   # kelime kelime yerleşim (en fazla 3 satır, ortalı)
            kel = metin.split()
            satirlar, cur = [], []
            for k in kel:
                if cur and f.getlength(" ".join(cur + [k])) > maxw:
                    satirlar.append(cur)
                    cur = [k]
                else:
                    cur.append(k)
            satirlar.append(cur)
            if len(satirlar) <= 3 or f.size < 60 * S:
                break
            f = C.font(yol, f.size - 8)
        self.f = f
        lh = f.size * 1.12
        self.lh = lh
        golge = pal.golge_t(S)
        self.kelimeler = []
        top = -(len(satirlar) - 1) * lh / 2
        self.satirlar = []
        for si, s in enumerate(satirlar):
            sw = f.getlength(" ".join(s))
            x = -sw / 2
            self.satirlar.append((" ".join(s), x, top + si * lh, sw))
            if not self.daktilo:
                for k in s:
                    spr = C.yazi(k, C.FONT_DIALOG, f.size, self.renk, golge=golge, dikey_kirp=False)
                    self.kelimeler.append((spr, x, top + si * lh, si))
                    x += f.getlength(k + " ")
        self.blok_h = len(satirlar) * lh
        self.z = metin_zamanlari(self.sahne)
        cev_renk = pal.vurgu if not pal.koyu else C.SARI
        self.ceviri = C.yazi(str(p["ceviri"]), C.FONT_DIALOG, 84 * S, pal.metin if not pal.koyu else cev_renk,
                             max_w=1500 * S, max_lines=2, align="center", golge=pal.golge_t(S, 4, 8)) \
            if p.get("ceviri") else None
        self.ust = C.yazi(C.buyuk(str(p["ust"])), C.FONT_BOLD, 30 * S, pal.ikincil, aralik=0.22) \
            if p.get("ust") else None
        self.alt = C.yazi(str(p["alt"]), C.FONT_BOLD, 28 * S, pal.ikincil) if p.get("alt") else None   # 6. tur: 24 -> 28
        # süs tırnağı yalnız alıntıda (metin tırnakla başlıyorsa ya da `tirnak: true`); 5. tur: "Bir süre sonra"
        # kartında alıntı olmayan satırın üstünde 420 pt tırnak görünüyordu
        tirnak = p.get("tirnak")
        if tirnak is None:
            tirnak = metin.lstrip()[:1] in "„“\"‘«‹'"
        self.tirnak = C.yazi("“", C.FONT_DIALOG, 420 * S, pal.metin) if tirnak and not self.daktilo else None
        self._dk: dict = {}
        self._satirlar_k: dict = {}
        self.cizikler = [(o.zaman, Z.renk(o.p.get("renk"), (206, 30, 36))) for o in olaylar(self.sahne, "ustunu_ciz")]

    def _satir_katmani(self, si: int):
        """si. satırın kelimeleri tek katmanda: (katman, x ofseti (W/2'ye göre), y ofseti (satır y'sine göre), y)."""
        if si in self._satirlar_k:
            return self._satirlar_k[si]
        ks = [(spr, x, y) for spr, x, y, s_ in self.kelimeler if s_ == si]
        x0 = min(x for _, x, _ in ks)
        y_ = ks[0][2]
        ofs = [(spr, x - x0, -spr.height * 0.5) for spr, x, _ in ks]
        y0 = min(o for _, _, o in ofs)
        w = int(math.ceil(max(xx + spr.width for spr, xx, _ in ofs))) + 2
        h = int(math.ceil(max(o - y0 + spr.height for spr, _, o in ofs))) + 2
        lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        for spr, xx, o in ofs:
            lay.alpha_composite(spr, (int(round(xx)), int(round(o - y0))))
        self._satirlar_k[si] = (lay, x0, y0, y_)
        return self._satirlar_k[si]

    def _daktilo_satiri(self, metin: str) -> Image.Image:
        spr = self._dk.get(metin)
        if spr is None:
            spr = C.yazi(metin, C.FONT_MONO, self.f.size, self.renk, golge=self.pal.golge_t(self.S),
                         dikey_kirp=False) if metin else None
            self._dk[metin] = spr
        return spr

    def ciz(self, t):
        S, W, H = self.S, self.W, self.H
        im = self.zemin.ciz(t, self.dur)
        cy = H * (0.42 if self.ceviri else 0.5)
        if self.tirnak is not None:
            C.bindir(im, self.tirnak, W / 2 - self.tirnak.width / 2,
                     cy - self.blok_h / 2 - self.tirnak.height * 0.62, 0.07 * E.out_cubic(t / 0.6))
        if self.ust is not None:
            a = E.out_cubic(t / 0.45)
            C.bindir(im, self.ust, W / 2 - self.ust.width / 2, cy - self.blok_h / 2 - 40 * S - self.ust.height, a)
        if self.daktilo:
            bas, hiz = self.z["daktilo"]
            kalan = max(0, int((t - bas) * hiz) + 1) if t >= bas else 0
            imlec = None
            for i, (satir, x, y, sw) in enumerate(self.satirlar):
                parca = satir[:kalan]
                yy = cy + y + Z.suzul(t, i * 1.3, 2.0) * S
                spr = self._daktilo_satiri(parca)
                if spr is not None:
                    C.bindir_alt(im, spr, W / 2 + x, yy - spr.height * 0.5)
                imlec = (W / 2 + x + self.f.getlength(parca) + 6 * S, yy)
                if kalan <= len(satir):
                    break
                kalan -= len(satir) + 1
            bitti = t >= bas + sum(len(s_[0]) + 1 for s_ in self.satirlar) / hiz
            gecis_son = (self.sahne.gecis_kare + 1) / self.c.fps if self.sahne.gecis != "kesme" else 0.0
            if imlec and t >= max(bas - 0.4, gecis_son) and (not bitti or int(t * 2.2) % 2 == 0):
                ix, iy = imlec
                asc, desc = self.f.getmetrics()
                ImageDraw.Draw(im).rectangle((ix, iy - self.f.size * 0.4, ix + 0.33 * self.f.size,
                                              iy - self.f.size * 0.4 + asc + desc * 0.25), fill=self.renk)
        else:
            # 7. tur: kelimeleri belirmesi biten satır tek katman olarak alt pikselde süzülür (124 pt yazı tam pikselde
            # 0,3-0,4 sn'de bir 1 px zıplıyordu); belirme animasyonundaki kelime ayrı çizilir
            bitti = {}
            for (spr, x, y, si), tk in zip(self.kelimeler, self.z["kelimeler"]):
                bitti[si] = bitti.get(si, True) and t >= tk + 0.32
            for si, tamam in bitti.items():
                if tamam:
                    lay, ox, oy, y = self._satir_katmani(si)
                    C.bindir_alt(im, lay, W / 2 + ox, cy + y + Z.suzul(t, si * 1.3, 2.5) * S + oy)
            for (spr, x, y, si), tk in zip(self.kelimeler, self.z["kelimeler"]):
                u = (t - tk) / 0.32
                if u <= 0 or bitti.get(si):
                    continue
                a = E.out_cubic(u)
                yy = cy + y + Z.suzul(t, si * 1.3, 2.5) * S
                C.bindir_alt(im, spr, W / 2 + x, yy - spr.height * 0.5 + (1 - a) * 26 * S, a)
        # üstünü çiz: satır satır soldan sağa
        for tc, rk in self.cizikler:
            u = (t - tc) / 0.5
            if u <= 0:
                continue
            d = ImageDraw.Draw(im)
            n = len(self.satirlar)
            for i, (satir, x, y, sw) in enumerate(self.satirlar):
                q = E.in_out_cubic(u * n - i)
                if q <= 0:
                    continue
                yy = cy + y + Z.suzul(t, i * 1.3, 2.5) * S + 0.02 * self.f.size
                x0, x1 = W / 2 + x - 18 * S, W / 2 + x + sw + 18 * S
                d.line((x0, yy + 6 * S, x0 + (x1 - x0) * q, yy + 6 * S - 14 * S * q), fill=rk,
                       width=max(2, int(11 * S)))
        if self.ceviri is not None:
            u = (t - self.z["ceviri"]) / 0.45
            if u > 0:
                a = E.out_cubic(u)
                y = cy + self.blok_h / 2 + 60 * S + Z.suzul(t, 2.2, 2.0) * S
                cw = self.ceviri.width
                lw = cw * E.in_out_cubic((t - self.z["ceviri"] - 0.2) / 0.5)
                if lw > 1:
                    d = ImageDraw.Draw(im)
                    if self.pal.koyu:   # koyu zeminde altı sarı şerit
                        d.rectangle((W / 2 - cw / 2, y + self.ceviri.height - 4 * S,
                                     W / 2 - cw / 2 + lw, y + self.ceviri.height + 6 * S), fill=C.SARI)
                    else:               # kâğıtta fosforlu kalem yazının arkasından geçer
                        isaret = Image.new("RGB", (int(lw + 24 * S), int(self.ceviri.height * 0.62)),
                                           self.pal.isaret)
                        C.bindir(im, isaret, W / 2 - cw / 2 - 12 * S, y + self.ceviri.height * 0.3, 0.8)
                C.bindir_alt(im, self.ceviri, W / 2 - cw / 2, y + (1 - a) * 22 * S, a)
        if self.alt is not None:
            C.bindir(im, self.alt, W / 2 - self.alt.width / 2, H - 140 * S, 0.8 * E.out_cubic((t - 0.5) / 0.5))
        return im


# ================================================================ zaman çizelgesi

class ZamanCizelgesiCizici(Cizici):
    def hazirla(self):
        p, S, W, H = self.p, self.S, self.W, self.H
        self.zemin = Z.Zemin(self.c, p)
        pal = self.pal = self.zemin.palet
        self.noktalar = p["noktalar"]
        n = len(self.noktalar)
        self.x0, self.x1 = 150 * S, W - 150 * S
        self.y = H * 0.53
        aralik = (self.x1 - self.x0) / n
        self.xs = [self.x0 + aralik * (i + 0.5) for i in range(n)]
        self.ts = zc_zamanlari(self.sahne)
        self.spr = []
        for nk in self.noktalar:
            tarih = C.yazi(str(nk["tarih"]), C.FONT_CARD, 66 * S, pal.vurgu, max_w=aralik - 20 * S, max_lines=2,
                           align="center", golge=pal.golge_t(S, 3, 6))
            yz = C.yazi(str(nk.get("metin", "")), C.FONT_BOLD, 42 * S, pal.metin, max_w=aralik - 30 * S,   # 8. tur: 36 -> 42
                        max_lines=3, align="center", satir=1.18, golge=pal.golge_t(S, 3, 6)) if nk.get("metin") else None
            self.spr.append((tarih, yz))
        self.baslik = C.yazi(str(p["baslik"]), C.FONT_DIALOG, 58 * S, pal.metin, max_w=1500 * S, max_lines=1,
                             golge=pal.golge_t(S, 3, 6)) if p.get("baslik") else None
        self.cizgi_t = max(0.1, self.ts[0] - 0.6) if self.ts else 0.1

    def ciz(self, t):
        S = self.S
        pal = self.pal
        im = self.zemin.ciz(t, self.dur)
        d = ImageDraw.Draw(im)
        # eksen
        lw = (self.x1 - self.x0) * E.in_out_cubic((t - self.cizgi_t) / 0.7)
        if lw > 0:
            d.rectangle((self.x0, self.y - 2 * S, self.x0 + lw, self.y + 2 * S), fill=pal.cizgi)
        # ilerleme (sarı) çizgisi son beliren noktaya kadar
        gorunen = [i for i, tt in enumerate(self.ts) if t >= tt]
        if gorunen:
            i = gorunen[-1]
            tt = self.ts[i]
            xp0 = self.xs[i - 1] if i > 0 else self.x0
            xp = E.karistir(xp0, self.xs[i], E.out_cubic((t - tt) / 0.45))
            d.rectangle((self.x0, self.y - 3 * S, xp, self.y + 3 * S), fill=pal.vurgu)
        son = gorunen[-1] if gorunen else -1
        for i, (x, tt, (tarih, yz)) in enumerate(zip(self.xs, self.ts, self.spr)):
            u = t - tt
            if u < 0:
                continue
            aktif = i == son
            kis = 1.0 if aktif else 0.62
            r = 18 * S * (0.4 + 0.6 * E.out_back(u / 0.3, 2.0)) * (1.15 if aktif else 1.0)
            if aktif:
                rr = r + 10 * S * (0.5 + 0.5 * math.sin(2 * math.pi * 1.0 * u))
                d.ellipse((x - rr, self.y - rr, x + rr, self.y + rr), outline=pal.vurgu, width=max(1, int(3 * S)))
            dolgu = (C.BEYAZ if aktif else (170, 172, 178)) if pal.koyu else ((255, 252, 244) if aktif else (214, 204, 186))
            d.ellipse((x - r, self.y - r, x + r, self.y + r), fill=dolgu, outline=pal.vurgu, width=max(1, int(4 * S)))
            a = E.out_cubic(u / 0.4) * kis
            sz = Z.suzul(t, i * 0.9, 2.5 if aktif else 1.5) * S   # yazılar hafifçe süzülür (boşta hareket)
            C.bindir_alt(im, tarih, x - tarih.width / 2,
                         self.y - 44 * S - tarih.height - (1 - E.out_cubic(u / 0.4)) * 14 * S + sz, a)
            if yz is not None:
                C.bindir_alt(im, yz, x - yz.width / 2, self.y + 46 * S + (1 - E.out_cubic(u / 0.4)) * 14 * S + sz, a)
        if self.baslik is not None:
            a = E.out_cubic(t / 0.5)
            C.bindir(im, self.baslik, 80 * S, 64 * S - (1 - a) * 12 * S, a)
            d.rectangle((80 * S, 64 * S + self.baslik.height + 12 * S, 80 * S + 140 * S * E.out_cubic((t - 0.15) / 0.5),
                         64 * S + self.baslik.height + 18 * S), fill=pal.vurgu)
        return im


CIZICILER = {"wojak": WojakCizici, "foto": FotoCizici, "manset": MansetCizici, "harita": HaritaCizici,
             "sayac": SayacCizici, "bolum_karti": BolumKartiCizici, "metin": MetinCizici,
             "zaman_cizelgesi": ZamanCizelgesiCizici}


def cizici(sahne: Sahne, c: Baglam) -> Cizici:
    if sahne.tip not in CIZICILER:   # 2. tur tipleri ayrı modüllerde (sahneler'i içe aktarırlar)
        from . import bilgi, kanal, kapanis
        CIZICILER.update({"bolunmus": bilgi.BolunmusCizici, "izgara": bilgi.IzgaraCizici, "pano": bilgi.PanoCizici,
                          "marka": kanal.MarkaCizici, "bitis": kanal.BitisCizici,
                          "kapanis": kapanis.KapanisCizici})
    return CIZICILER[sahne.tip](sahne, c)


# ================================================================ filigran

def filigran_katmani(metin: str, c: Baglam) -> tuple[Image.Image, int, int]:
    from .. import config, text as wtext
    S = c.S
    lay = wtext.text_block(metin, font_path=config.FONT_DIALOG, size=max(10, round(34 * S)), max_w=round(600 * S),
                           max_lines=1, stroke_ratio=0.09, pitch=1.1, shadow=False, shear=config.DIALOG_SHEAR)
    bb = lay.getchannel("A").getbbox()
    lay = lay.crop(bb) if bb else lay
    lay.putalpha(lay.getchannel("A").point(C._alfa_lut(int(255 * 0.9))))
    return lay, int(c.W - 34 * S - lay.width), int(c.H - 26 * S - lay.height)
