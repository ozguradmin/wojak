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
    for i, c in enumerate(sahne.p.get("karakterler", [])):
        g = c.get("giris", True)
        giris = None if g is False else (float(g) if isinstance(g, (int, float)) and g is not True else 0.05 + 0.22 * i)
        out[c["id"]] = {"giris": giris, "cikis": None, "yuz": []}
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


def sayac_bolumleri(sahne: Sahne) -> list[dict]:
    """Sayacın sayım bölümleri: [{t0, t1, a, b, yil, etiket, renk, onek, sonek}]. İlki sahnenin `deger`/`yil`'ından
    (`deger: [60, 0]` azalan), sonrakiler `deger` olaylarından (bir önceki değerden yenisine)."""
    p = sahne.p
    bas = basla_zamani(sahne, 0.35)
    pal = Z.KAGIT if p.get("zemin") == "kagit" else Z.KOYU
    renk0 = Z.renk(p.get("renk"), pal.metin)
    if p.get("yil"):
        a, b = p["yil"]
        sure = float(p.get("sure_say", max(1.0, 0.42 * abs(int(b) - int(a)))))
        return [{"t0": bas, "t1": bas + sure, "a": int(a), "b": int(b), "yil": True, "etiket": p.get("etiket"),
                 "renk": renk0, "onek": "", "sonek": str(p.get("sonek", ""))}]
    d = p["deger"]
    liste = isinstance(d, list)
    a, b = (float(d[0]), float(d[1])) if liste else (0.0, float(d))
    sure = float(p.get("sure_say", 2.2))
    out = [{"t0": bas, "t1": bas + sure, "a": a, "b": b, "yil": False, "etiket": p.get("etiket"), "renk": renk0,
            "onek": str(p.get("onek", "")), "sonek": str(p.get("sonek", "" if liste else "+"))}]
    for o in olaylar(sahne, "deger"):
        q, onc = o.p, out[-1]
        t0 = max(o.zaman, onc["t0"] + 0.05)
        out.append({"t0": t0, "t1": t0 + float(q.get("sure", 1.2)), "a": onc["b"], "b": float(q["deger"]),
                    "yil": False, "etiket": q.get("etiket", onc["etiket"]),
                    "renk": Z.renk(q.get("renk"), onc["renk"]) if q.get("renk") is not None else onc["renk"],
                    "onek": str(q.get("onek", "")), "sonek": str(q.get("sonek", ""))})
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
        self.katman = UstKatman(sahne, c)

    def hazirla(self):
        pass

    def ciz(self, t: float) -> Image.Image:
        raise NotImplementedError

    def dondur(self, onceki: Image.Image) -> None:
        """Bindirme sahneleri için önceki sahnenin son karesi (filigransız)."""

    def kare(self, t: float) -> Image.Image:
        im = self.ciz(t)
        self.katman.uygula(im, t)
        return im

    def px(self, v: float) -> float:
        return v * self.S


# ================================================================ üst katmanlar

class UstKatman:
    def __init__(self, sahne: Sahne, c: Baglam):
        self.c = c
        S = c.S
        self.isimler = []
        for o in olaylar(sahne, "isim"):
            konum = str(o.p.get("konum", "sol"))
            if o.p.get("karakter") is not None:   # adı verilen karakterin tarafına
                for c_ in sahne.p.get("karakterler", []):
                    if c_["id"] == str(o.p["karakter"]):
                        cx = float(c_["x"]) if c_.get("x") is not None else {"sol": 0.25, "sag": 0.75, "orta": 0.5}[c_["taraf"]]
                        konum = "sag" if cx > 0.5 else "sol"
            self.isimler.append((o.zaman, float(o.p.get("sure", 4.2)), self._isim(o.p["ad"], o.p.get("unvan")), konum))
        self.vurgular = []
        for o in olaylar(sahne, "kelime"):
            spr = C.yazi(str(o.p["metin"]), C.FONT_DIALOG, 92 * S, C.BEYAZ, stroke=7 * S, max_w=1500 * S,
                         max_lines=2, align="center", golge=(0, 5 * S, 9 * S, 0.55))
            self.vurgular.append((o.zaman, float(o.p.get("sure", 2.3)), spr, str(o.p.get("konum", "alt"))))
        self.damgalar = [Damga(o, c, i) for i, o in enumerate(damga_olaylari(sahne))]
        ko = kose_olaylari(sahne)
        self.kose = KoseGostergesi(sahne, c, ko) if (sahne.kose is not None or ko) else None

    def _isim(self, ad: str, unvan: str | None) -> Image.Image:
        S = self.c.S
        a = C.yazi(ad, C.FONT_BOLD, 46 * S, C.BEYAZ)
        u = C.yazi(unvan, C.FONT_BOLD, 27 * S, (206, 208, 214)) if unvan else None
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

    def uygula(self, im: Image.Image, t: float) -> None:
        S, W, H = self.c.S, self.c.W, self.c.H
        if self.kose is not None:
            self.kose.ciz(im, t)
        for t0, sure, spr, konum in self.isimler:
            u = t - t0
            if u < 0 or u > sure + 0.4:
                continue
            x_dur = 64 * S if konum == "sol" else W - 64 * S - spr.width
            git = (spr.width + x_dur + 20 * S) if konum == "sol" else -(W - x_dur + 20 * S)
            x = x_dur - (1 - E.out_cubic(u / 0.5)) * git - E.in_cubic((u - sure) / 0.38) * git
            C.bindir(im, spr, x, H - 92 * S - spr.height)
        for t0, sure, spr, konum in self.vurgular:
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


class Karakter:
    GIRIS = 0.75
    CIKIS = 0.45

    def __init__(self, spec: dict, zam: dict, c: Baglam, sira: int, konusma: Konusma | None = None):
        S, W, H = c.S, c.W, c.H
        self.c = c
        yollar = [Path(spec["gorsel"])] + [p for _, p in zam["yuz"]]
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
        self.taban = H + float(spec.get("alt", 0.0)) * H + 0.04 * self.h
        self.giris, self.cikis = zam["giris"], zam["cikis"]
        self.yuz_t = [t for t, _ in zam["yuz"]]
        self.konusma = konusma or Konusma()
        self.faz = 1.7 * sira
        # baş: üst %18'lik bandın yatay merkezi
        a = np.asarray(self.ims[0].getchannel("A"))
        band = a[: max(2, int(self.h * 0.18))] > 60
        xs = np.where(band.any(axis=0))[0]
        self.bas_x = self.cx - self.w / 2 + (xs.mean() if len(xs) else self.w / 2)
        ys = np.where((a > 60).any(axis=1))[0]
        self.ust_y = self.taban - self.h + (ys[0] if len(ys) else 0)
        self.ic_yon = 1 if self.cx < W / 2 else -1   # kadrajın ortasına doğru
        self._onbellek: dict = {}

    def odak(self) -> tuple[float, float]:
        """Kamera itmesinin hedefi (sahne 0..1): başın biraz altı."""
        return self.bas_x / self.c.W, (self.ust_y + 0.22 * self.h) / self.c.H

    def _mesafe(self) -> tuple[float, float]:
        W, H = self.c.W, self.c.H
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

    def ciz(self, im: Image.Image, t: float, kam: Kam | None = None) -> None:
        if not self.gorunur(t):
            return
        S = self.c.S
        mx, my = self._mesafe()
        dx = dy = 0.0
        if self.giris is not None:
            e = E.out_back((t - self.giris) / self.GIRIS, 1.1)
            dx += (1 - e) * mx
            dy += (1 - e) * my
        if self.cikis is not None and t > self.cikis:
            e = E.in_cubic((t - self.cikis) / self.CIKIS)
            dx += e * mx
            dy += e * my
        vi = sum(1 for ts in self.yuz_t if t >= ts)
        sx = sy = 1 + 0.01 * math.sin(2 * math.pi * 0.3 * t + self.faz)
        for ts in self.yuz_t:
            b = E.tumsek((t - ts + 0.13) / 0.26)
            if b:
                sy *= 1 - 0.075 * b
                sx *= 1 + 0.05 * b
        # konuşma: hece başlarında küçük sekme + dikey esneme (sesle eş zamanlı)
        k = self.konusma.deger(t)
        if k:
            dy -= 9 * S * k * (1 - 0.3 * self.derinlik)
            sy *= 1 + 0.016 * k
            sx *= 1 - 0.005 * k
        dy += 3 * S * math.sin(2 * math.pi * 0.21 * t + self.faz * 0.6)
        z = 1.0
        x, y = self.cx + dx, self.taban + dy
        if kam is not None:
            z = kam.z
            x, y = kam.nokta(x, y)
        # alt piksel yerleştirme: ölçek (nefes, sıkışma, kamera) ve konum tek bir örneklemeyle, kesirli olarak
        # uygulanır (C.alt_piksel). Eskiden sprite 0.001 adımla ölçeklenip tam piksele yuvarlanıyordu: arka plan
        # kamerayla alt pikselde kayarken büyük karakter 3-10 karede bir ~1 px sıçrıyordu (yavaş itmede titreme).
        # Önceden çarpılmış alfa (RGBa) ile örneklenir: saydam kenarda koyu saçak olmaz.
        src = self._onbellek.get(vi)
        if src is None:
            src = self._onbellek[vi] = C.alt_piksel_hazirla(self.ims[vi])
        w0, h0 = self.ims[vi].size
        spr, x0, y0 = C.alt_piksel(src, x - w0 * sx * z / 2, y - h0 * sy * z, sx * z, sy * z)
        C.bindir(im, spr, x0, y0)


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
            C.bindir(im, self.spr, ux - self.ax, uy - self.ay, a)
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
        zm = max(z) * (1 + self.it) + 0.01
        bg = C.yukle(p["arka"]).convert("RGB")
        if p.get("kirp"):   # [x0, y0, x1, y1] (0..1): fotoğrafın istenmeyen kenarını at
            k_ = [float(v) for v in p["kirp"]]
            bg = bg.crop((round(k_[0] * bg.width), round(k_[1] * bg.height), round(k_[2] * bg.width),
                          round(k_[3] * bg.height)))
        bg = C.kapla(bg, round(W * zm), round(H * zm), tuple(p.get("odak", (0.5, 0.5))))
        self.bg = C.ayarla(bg, bulanik=float(p.get("bulanik", 1.6)) * S, karart=float(p.get("karart", 0.12)),
                           doygunluk=float(p.get("doygunluk", 0.85)))
        C.vinyet_uygula(self.bg, 0.42)   # kaynağa bir kez (her karede maske bindirmek pahalı)
        self.balonlar = []
        for i, o in enumerate(bal):
            sure = float(o.p.get("sure") or 2.5)
            sonraki = [x.zaman for x in bal[i + 1:] if x.p["karakter"] == o.p["karakter"]]
            if sonraki:
                sure = min(sure, sonraki[0] - o.zaman - 0.05)
            self.balonlar.append(Balon(str(o.p["metin"]), kmap[o.p["karakter"]], o.zaman, sure, self.c))

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
        return Kam(z, mx, my, self.W, self.H)

    def ciz(self, t):
        k = self.kam(t)
        im = C.kamera(self.bg, self.W, self.H, k.z, (k.cx, k.cy))
        for kr in self.cizim_sirasi:
            kr.ciz(im, t, k)
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
        self.egim = float(p.get("egim", -2.2))
        self.giris = str(p.get("giris", "alt"))
        z = p.get("zoom", 1.05)
        self.zoom = float(z[1] if isinstance(z, list) else z)
        self.z = foto_zamanlari(self.sahne)
        self.etiket = DaktiloEtiket(p.get("etiket"), self.c, olaylar(self.sahne, "etiket"), self.z["etiket"], None)
        self.atif = C.yazi(str(p["atif"]), C.FONT_BOLD, 19 * S, (230, 230, 230)) if p.get("atif") else None

    def ciz(self, t):
        W, H, S = self.W, self.H, self.S
        im = C.kamera(self.arka, W, H, 1.0 + 0.06 * E.in_out_sine(t / self.dur), (0.5, 0.5))
        u = (t - self.z["inis"]) / 0.72
        e = E.out_back(u, 1.0)
        cx, cy = W / 2, H * 0.455
        yon = {"alt": (0, 1), "ust": (0, -1), "sag": (1, 0), "sol": (-1, 0)}.get(self.giris, (0, 1))
        cx += (1 - e) * yon[0] * W * 0.9
        cy += (1 - e) * yon[1] * H * 0.95
        aci = self.egim + (1 - E.out_cubic(u)) * (7.0 if yon[0] >= 0 else -7.0)
        s = (1.0 + 0.07 * (1 - E.out_cubic(u))) * (1 + (self.zoom - 1) * E.in_out_sine(t / self.dur))
        if u > 0:
            spr, x0, y0 = C.afin(self.spr, cx, cy, s, s, aci, self.ax, self.ay)
            C.bindir(im, spr, x0, y0)
        self.etiket.ciz(im, t)
        if self.atif is not None:
            C.bindir(im, self.atif, W - 70 * S - self.atif.width, H - 82 * S - self.atif.height, 0.65)
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

    def ciz(self, t):
        pg = self.page.copy()
        for (bx, mask), t0 in zip(self.kutular, self.ts):
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
        self.baslik = None
        if p.get("baslik"):
            self.baslik = C.yazi(str(p["baslik"]), C.FONT_DIALOG, 54 * S, C.BEYAZ, max_w=1100 * S, max_lines=2,
                                 golge=(0, 3 * S, 6 * S, 0.6))
        self.aciklama = None
        if p.get("aciklama"):
            yz = C.yazi(str(p["aciklama"]), C.FONT_BOLD, 26 * S, (226, 228, 232))
            sq = int(22 * S)
            w, h = int(sq + 14 * S + yz.width + 36 * S), int(max(sq, yz.height) + 24 * S)
            lay = C.yuvarlak_kutu(w, h, 5 * S, (8, 10, 14, 200))
            ImageDraw.Draw(lay).rectangle((int(18 * S), (h - sq) // 2, int(18 * S) + sq, (h - sq) // 2 + sq),
                                          fill=renk + (255,))
            lay.alpha_composite(yz, (int(18 * S + sq + 14 * S), (h - yz.height) // 2))
            self.aciklama = lay

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
                C.bindir(im, spr, x - spr.width / 2, y - spr.height / 2 + (1 - a) * 8 * S, a)
        if self.vurgu:
            t0, mask, bbox, vr, _, pt, kutu = self.vurgu
            u = t - t0 - 0.25
            if u >= 0:
                x, y = self._nokta(pt, zoom, self.merkez)
                a = E.out_cubic(u / 0.3)
                bx = min(x + 110 * S, W - kutu.width - 40 * S)
                by = max(y - 150 * S, 140 * S)
                d = ImageDraw.Draw(im)
                lu = E.out_cubic(u / 0.25)
                d.line((x, y, x + (bx + 12 * S - x) * lu, y + (by - y) * lu), fill=(245, 255, 248),
                       width=max(1, int(4 * S)))
                d.ellipse((x - 8 * S, y - 8 * S, x + 8 * S, y + 8 * S), fill=(245, 255, 248))
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

    def ciz(self, t):
        S, W, H = self.S, self.W, self.H
        im = self.zemin.ciz(t, self.dur)
        i, b = self._bolum(t)
        lay = self._say_katmani(t, b)
        bit = t - b["t1"]
        if bit >= 0:
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
        spr, x0, y0 = C.afin(lay, W / 2, cy, s, s, 0)
        C.bindir(im, spr, x0, y0, a)
        if self.ust is not None:
            C.bindir(im, self.ust, W / 2 - self.ust.width / 2, cy - self.yuk / 2 - 40 * S - self.ust.height, a)
        # etiket: ilk bölümde sayım başlarken belirir; değiştiğinde eskisi söner, yenisi gelir
        et = self._etiket(b["etiket"])
        ey = cy + self.yuk / 2 + 52 * S
        if i == 0:
            ae = E.out_cubic((t - self.t0 - 0.35) / 0.45)
        else:
            ae = E.out_cubic((t - b["t0"]) / 0.35) if b["etiket"] != self.bolumler[i - 1]["etiket"] else 1.0
            onceki = self._etiket(self.bolumler[i - 1]["etiket"])
            if onceki is not None and b["etiket"] != self.bolumler[i - 1]["etiket"]:
                ao = 1 - E.out_cubic((t - b["t0"]) / 0.25)
                if ao > 0:
                    C.bindir(im, onceki, W / 2 - onceki.width / 2, ey - (1 - ao) * 18 * S, ao)
        if et is not None:
            C.bindir(im, et, W / 2 - et.width / 2, ey + (1 - ae) * 24 * S, ae)
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
            a = E.out_cubic(t / 0.18)
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
        self.zemin = Z.Zemin(self.c, p, ic=(38, 32, 30), dis=(9, 8, 8))
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
                    spr = C.yazi(k, C.FONT_DIALOG, f.size, self.renk, golge=golge)
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
        self.alt = C.yazi(str(p["alt"]), C.FONT_BOLD, 24 * S, pal.ikincil) if p.get("alt") else None
        self.tirnak = C.yazi("“", C.FONT_DIALOG, 420 * S, pal.metin) if not self.daktilo else None
        self._dk: dict = {}
        self.cizikler = [(o.zaman, Z.renk(o.p.get("renk"), (206, 30, 36))) for o in olaylar(self.sahne, "ustunu_ciz")]

    def _daktilo_satiri(self, metin: str) -> Image.Image:
        spr = self._dk.get(metin)
        if spr is None:
            spr = C.yazi(metin, C.FONT_MONO, self.f.size, self.renk, golge=self.pal.golge_t(self.S)) if metin else None
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
                    C.bindir(im, spr, W / 2 + x, yy - spr.height * 0.42)
                imlec = (W / 2 + x + self.f.getlength(parca) + 6 * S, yy)
                if kalan <= len(satir):
                    break
                kalan -= len(satir) + 1
            bitti = t >= bas + sum(len(s_[0]) + 1 for s_ in self.satirlar) / hiz
            if imlec and t >= bas - 0.4 and (not bitti or int(t * 2.2) % 2 == 0):
                ix, iy = imlec
                asc, desc = self.f.getmetrics()
                ImageDraw.Draw(im).rectangle((ix, iy - self.f.size * 0.4, ix + 0.33 * self.f.size,
                                              iy - self.f.size * 0.4 + asc + desc * 0.25), fill=self.renk)
        else:
            for (spr, x, y, si), tk in zip(self.kelimeler, self.z["kelimeler"]):
                u = (t - tk) / 0.32
                if u <= 0:
                    continue
                a = E.out_cubic(u)
                yy = cy + y + Z.suzul(t, si * 1.3, 2.5) * S
                C.bindir(im, spr, W / 2 + x, yy - spr.height * 0.42 + (1 - a) * 26 * S, a)
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
                C.bindir(im, self.ceviri, W / 2 - cw / 2, y + (1 - a) * 22 * S, a)
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
            yz = C.yazi(str(nk.get("metin", "")), C.FONT_BOLD, 36 * S, pal.metin, max_w=aralik - 30 * S,
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
            C.bindir(im, tarih, x - tarih.width / 2,
                     self.y - 44 * S - tarih.height - (1 - E.out_cubic(u / 0.4)) * 14 * S + sz, a)
            if yz is not None:
                C.bindir(im, yz, x - yz.width / 2, self.y + 46 * S + (1 - E.out_cubic(u / 0.4)) * 14 * S + sz, a)
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
        from . import bilgi, kanal
        CIZICILER.update({"bolunmus": bilgi.BolunmusCizici, "izgara": bilgi.IzgaraCizici, "pano": bilgi.PanoCizici,
                          "marka": kanal.MarkaCizici, "bitis": kanal.BitisCizici})
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
