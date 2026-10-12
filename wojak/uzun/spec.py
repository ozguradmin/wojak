"""Uzun video spesifikasyonu: uzun/<id>/video.yaml yükleme ve doğrulama.

Tüm alanların açıklamalı örneği: uzun/_sablon/video.yaml. Başvuru: docs/UZUN_MOTOR.md.
Hatalar SpecHatasi olarak, sahnenin yeriyle ("bölüm 2, sahne 3") birlikte bildirilir.
"""

from __future__ import annotations

import re
import zlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .. import config

VARSAYILAN_SESLER = {
    "murat": "5a31e4fb-f823-4359-aa91-82c0ae9a991c",
    "aylin": "bb2347fe-69e9-4810-873f-ffd759fe8420",
    "leyla": "fa7bfcdc-603c-4bf1-a600-a371400d2f8c",
    "azra": "0f95596c-09c4-4418-99fe-5c107e0713c0",
}

VARSAYILAN_ZAMANLAMA = {
    "bas": 0.35,        # sahne başı ile ilk satır arası (sn)
    "ara": 0.35,        # aynı sahnedeki iki satır arası
    "son": 0.55,        # son satırdan sonra sahnenin sürmesi
    "min_sahne": 2.0,   # satırlı sahnenin en kısa süresi
    "kart": 2.6,        # bölüm kartı süresi
    "sabit": 3.0,       # satırsız sahnenin varsayılan süresi
    "max_bos": 6.0,     # hareket denetimi: ekranda yeni bir şey olmadan geçebilecek en uzun süre
}

GECISLER = {"kesme": "kesme", "cut": "kesme", "gecis": "gecis", "crossfade": "gecis", "xfade": "gecis",
            "kaydir": "kaydir", "push": "kaydir", "itme": "kaydir"}
GECIS_KARE = {"kesme": 0, "gecis": 8, "kaydir": 10}

# sahne tipi -> izinli parametreler (ortak anahtarlar ayrıca)
SAHNE_PARAMLARI: dict[str, set[str]] = {
    "wojak": {"arka", "kamera", "karakterler", "karart", "bulanik", "doygunluk", "kirp", "odak", "etiket"},
    "foto": {"gorsel", "etiket", "egim", "zoom", "atif", "boy", "giris", "arka", "odak"},
    "manset": {"gorsel", "kutular", "zoom", "arka", "renk", "boy", "etiket"},
    "harita": {"bolge", "ulkeler", "vurgu", "baslik", "aralik", "cozunurluk", "renk", "etiketler", "zoom",
               "aciklama"},
    "sayac": {"deger", "yil", "etiket", "ust", "onek", "sonek", "sure_say", "arka"},
    "bolum_karti": {"numara", "baslik", "ust"},
    "metin": {"metin", "ceviri", "ust", "alt", "arka", "ceviri_t"},
    "zaman_cizelgesi": {"noktalar", "baslik", "arka"},
}
TIP_TAKMA = {"liste": "zaman_cizelgesi", "zaman": "zaman_cizelgesi", "kart": "bolum_karti", "fotograf": "foto",
             "belge": "manset", "sayi": "sayac"}
ZORUNLU = {"wojak": ["arka"], "foto": ["gorsel"], "manset": ["gorsel"], "sayac": [], "bolum_karti": ["baslik"],
           "metin": ["metin"], "zaman_cizelgesi": ["noktalar"], "harita": []}
ORTAK = {"tip", "satirlar", "olaylar", "sfx", "gecis", "gecis_kare", "sure", "min_sure", "bas", "ara", "son",
         "isim_etiketi", "kelime", "not", "otomatik_sfx"}

# olay tipi -> izinli parametreler (çapa anahtarları satir/ofset/an/t ayrıca)
OLAY_TIPLERI: dict[str, set[str]] = {
    "yuz": {"karakter", "gorsel"},            # yüz varyantına geç (kısa sıkışma efektiyle)
    "balon": {"karakter", "metin", "sure"},   # konuşma balonu (yalnız görsel)
    "kelime": {"metin", "sure", "konum"},     # ekranda vurgu kelimesi (konum: ust | orta | alt)
    "isim": {"ad", "unvan", "sure", "konum", "karakter"},  # isim etiketi (lower third); konum: sol | sag
    "giris": {"karakter"},                    # karakter bu anda kayarak girer
    "cikis": {"karakter"},                    # karakter bu anda çıkar
    "vurgula": {"kutu"},                      # manset: fosforlu kalem bu kutudan geçer (1'den başlar)
    "basla": set(),                           # sayac/harita/zaman_cizelgesi: ana animasyon başlar
    "nokta": {"indeks"},                      # zaman_cizelgesi: bu nokta belirir (1'den başlar)
    "ulke": {"kod"},                          # harita: bu ülke yanar (ISO3)
    "etiket": set(),                          # foto: yer-tarih etiketi yazılmaya başlar
    "ceviri": set(),                          # metin: çeviri satırı belirir
}
OLAY_ZORUNLU = {"yuz": ["karakter", "gorsel"], "balon": ["karakter", "metin"], "kelime": ["metin"],
                "isim": ["ad"], "giris": ["karakter"], "cikis": ["karakter"], "vurgula": ["kutu"],
                "nokta": ["indeks"], "ulke": ["kod"]}
CAPA = {"tip", "satir", "ofset", "an", "t"}

SFX_DIR = config.SFX
BREAK_RE = re.compile(r"<break\s+time=\"?([\d.]+)\s*(ms|s)\"?\s*/>", re.I)
TAG_RE = re.compile(r"<[^>]+>")


class SpecHatasi(ValueError):
    pass


def temiz_metin(s: str) -> str:
    """Altyazı/ekran metni: SSML benzeri etiketler (<break .../>) ve satır sonları çıkar."""
    s = TAG_RE.sub(" ", s).replace("\n", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return re.sub(r"\s+([,.;:!?…])", r"\1", s)


def ara_sureleri(s: str) -> float:
    """Metindeki <break time="..."/> etiketlerinin toplam süresi (sn)."""
    tot = 0.0
    for v, unit in BREAK_RE.findall(s):
        tot += float(v) / (1000 if unit.lower() == "ms" else 1)
    return tot


@dataclass
class Satir:
    metin: str                   # ekranda/altyazıda görünen metin (etiketler altyazıdan çıkarılır)
    ses: str                     # ses adı (sesler anahtarı) ya da doğrudan Cartesia ses kimliği
    hiz: float = 1.0
    duygu: str | None = None
    once: float | None = None    # bu satırdan önce bekleme (sahnenin 'ara'sı yerine)
    sonra: float | None = None   # bu satırdan sonra ek bekleme
    tts: str | None = None       # TTS'e giden metin (verilmezse metin + telaffuz)
    balon: str | None = None     # karakter kimliği: satır o karakterin konuşma balonunda görünür
    # hesaplanan
    sure: float | None = None
    wav: Path | None = None
    t0: float = 0.0              # sahne içindeki başlangıç (sn)
    tahmini: bool = False

    @property
    def altyazi(self) -> str:
        return temiz_metin(self.metin)

    @property
    def t1(self) -> float:
        return self.t0 + (self.sure or 0.0)


@dataclass
class Olay:
    tip: str
    satir: int | None = None     # 1'den başlar; verilirse zaman o satıra göre
    ofset: float = 0.0
    an: str = "bas"              # bas | son (satırın başı/sonu)
    t: float | None = None       # satır yoksa sahne başına göre saniye
    p: dict = field(default_factory=dict)
    zaman: float = 0.0           # çözümlenmiş, sahne içi saniye


@dataclass
class Sfx:
    ad: str                      # assets/sfx/<ad>.wav ya da dosya yolu
    yol: Path
    satir: int | None = None
    ofset: float = 0.0
    an: str = "bas"
    t: float | None = None
    db: float = 0.0
    zaman: float = 0.0


@dataclass
class Sahne:
    tip: str
    p: dict
    satirlar: list[Satir] = field(default_factory=list)
    olaylar: list[Olay] = field(default_factory=list)
    sfx: list[Sfx] = field(default_factory=list)
    gecis: str = "kesme"         # bu sahneye GİRİŞ geçişi: kesme | gecis (crossfade) | kaydir (push)
    gecis_kare: int = 0
    sure: float | None = None
    min_sure: float | None = None
    bas: float | None = None
    ara: float | None = None
    son: float | None = None
    otomatik_sfx: bool = True
    bolum: int = 0               # bölüm sırası (0'dan)
    yer: str = ""                # hata mesajları için "bölüm 2, sahne 3"
    # hesaplanan (zaman.py)
    no: int = 0
    sure_hesap: float = 0.0
    n_kare: int = 0
    bas_kare: int = 0


@dataclass
class Bolum:
    baslik: str
    kart: bool
    sahneler: list[Sahne]
    numara: int | None = None
    kart_sure: float = 2.6
    youtube: str | None = None   # açıklamadaki bölüm adı (verilmezse baslik)


@dataclass
class Video:
    id: str
    baslik: str
    dir: Path
    sesler: dict[str, str]
    anlatici_ses: str
    anlatici_hiz: float
    model: str
    dil: str
    telaffuz: dict[str, str]
    muzik: dict
    zamanlama: dict
    gecis: str
    filigran: str | None
    otomatik_sfx: bool
    bolumler: list[Bolum]
    kucukresimler: list[dict]
    paket: dict
    qa_isimler: list[str]
    raw: dict

    @property
    def sahneler(self) -> list[Sahne]:
        return [s for b in self.bolumler for s in b.sahneler]

    def ses_id(self, ad: str) -> str:
        return self.sesler.get(ad, ad)

    def yol(self, p) -> Path:
        return yol_coz(p, self.dir)

    def transkript(self, satir: Satir) -> str:
        """TTS'e giden metin: telaffuz düzeltmeleri YALNIZ burada uygulanır (altyazıda değil)."""
        s = satir.tts if satir.tts is not None else satir.metin
        s = s.replace("\n", " ")
        for yazim, okunus in self.telaffuz.items():
            s = re.sub(rf"(?<!\w){re.escape(yazim)}(?!\w)", okunus, s)
        return re.sub(r"[ \t]+", " ", s).strip()


def yol_coz(p, base: Path) -> Path:
    """Önce spesifikasyon klasörüne, sonra repo köküne göre çözer."""
    q = Path(str(p)).expanduser()
    if q.is_absolute():
        return q
    for b in (base, config.ROOT):
        if (b / q).exists():
            return (b / q).resolve()
    return (base / q).resolve()


def _hata(yer: str, msg: str):
    raise SpecHatasi(f"{yer}: {msg}" if yer else msg)


def _sayi(v, yer, ad, lo=None, hi=None) -> float:
    try:
        f = float(v)
    except (TypeError, ValueError):
        _hata(yer, f"'{ad}' sayı olmalı (verilen: {v!r})")
    if (lo is not None and f < lo) or (hi is not None and f > hi):
        _hata(yer, f"'{ad}' {lo}..{hi} aralığında olmalı (verilen: {f})")
    return f


def _bilinmeyen(d: dict, izinli: set[str], yer: str, ne: str) -> None:
    fazla = sorted(set(d) - izinli)
    if fazla:
        _hata(yer, f"bilinmeyen {ne} anahtarı: {', '.join(fazla)} (izinli: {', '.join(sorted(izinli))})")


def _gecis(v, yer) -> str:
    if v is None:
        return None
    g = GECISLER.get(str(v).lower())
    if g is None:
        _hata(yer, f"geçiş '{v}' bilinmiyor (kesme | gecis | kaydir)")
    return g


def _capa(d: dict, yer: str, n_satir: int) -> dict:
    out = {}
    if "satir" in d and d["satir"] is not None:
        k = int(_sayi(d["satir"], yer, "satir"))
        if not 1 <= k <= max(n_satir, 0):
            _hata(yer, f"satir {k}: bu sahnede {n_satir} satır var (1'den başlar)")
        out["satir"] = k
    out["ofset"] = _sayi(d.get("ofset", 0.0), yer, "ofset")
    an = str(d.get("an", "bas"))
    if an not in ("bas", "son"):
        _hata(yer, f"an '{an}': bas | son olmalı")
    out["an"] = an
    if d.get("t") is not None:
        out["t"] = _sayi(d["t"], yer, "t", 0)
    return out


def _satir(v, video_ses: str, video_hiz: float, sesler: dict, yer: str) -> Satir:
    if isinstance(v, str):
        if not v.strip():
            _hata(yer, "boş satır")
        return Satir(metin=v.strip(), ses=video_ses, hiz=video_hiz)
    if not isinstance(v, dict):
        _hata(yer, f"satır metin ya da sözlük olmalı: {v!r}")
    _bilinmeyen(v, {"metin", "ses", "duygu", "hiz", "once", "sonra", "tts", "balon"}, yer, "satır")
    if not str(v.get("metin", "")).strip():
        _hata(yer, "satırda 'metin' yok")
    ses = str(v.get("ses", video_ses))
    if ses not in sesler and not re.fullmatch(r"[0-9a-f-]{36}", ses):
        _hata(yer, f"ses '{ses}' tanımlı değil (sesler: {', '.join(sesler)})")
    return Satir(metin=str(v["metin"]).strip(), ses=ses,
                 hiz=_sayi(v.get("hiz", video_hiz), yer, "hiz", 0.5, 2.0),
                 duygu=v.get("duygu"), once=None if v.get("once") is None else _sayi(v["once"], yer, "once", 0),
                 sonra=None if v.get("sonra") is None else _sayi(v["sonra"], yer, "sonra", 0),
                 tts=v.get("tts"), balon=None if v.get("balon") is None else str(v["balon"]))


def _olay(d, yer: str, n_satir: int) -> Olay:
    if not isinstance(d, dict) or "tip" not in d:
        _hata(yer, f"olay sözlük olmalı ve 'tip' içermeli: {d!r}")
    tip = str(d["tip"])
    if tip not in OLAY_TIPLERI:
        _hata(yer, f"olay tipi '{tip}' bilinmiyor ({', '.join(sorted(OLAY_TIPLERI))})")
    _bilinmeyen(d, OLAY_TIPLERI[tip] | CAPA, yer, f"'{tip}' olayı")
    for k in OLAY_ZORUNLU.get(tip, []):
        if d.get(k) in (None, ""):
            _hata(yer, f"'{tip}' olayında '{k}' zorunlu")
    p = {k: v for k, v in d.items() if k not in CAPA}
    return Olay(tip=tip, p=p, **_capa(d, yer, n_satir))


def _sfx(d, yer: str, n_satir: int, base: Path) -> Sfx:
    if isinstance(d, str):
        d = {"ad": d}
    if not isinstance(d, dict) or "ad" not in d:
        _hata(yer, f"sfx 'ad' içermeli: {d!r}")
    _bilinmeyen(d, {"ad", "db"} | CAPA - {"tip"}, yer, "sfx")
    ad = str(d["ad"])
    yol = SFX_DIR / f"{ad}.wav" if "/" not in ad and not ad.endswith(".wav") else yol_coz(ad, base)
    return Sfx(ad=ad, yol=yol, db=_sayi(d.get("db", 0.0), yer, "db", -60, 12), **_capa(d, yer, n_satir))


def _karakterler(lst, yer: str, base: Path) -> list[dict]:
    out = []
    if lst is None:
        return out
    if not isinstance(lst, list) or not 1 <= len(lst) <= 3:
        _hata(yer, "karakterler 1-3 öğelik liste olmalı")
    for i, c in enumerate(lst):
        if isinstance(c, str):
            c = {"gorsel": c}
        _bilinmeyen(c, {"id", "gorsel", "taraf", "x", "boy", "giris", "bakis", "alt"}, yer, "karakter")
        if "gorsel" not in c:
            _hata(yer, f"{i + 1}. karakterde 'gorsel' yok")
        c = dict(c)
        c.setdefault("id", chr(ord("a") + i))
        c["id"] = str(c["id"])
        taraf = c.get("taraf", ["sol", "sag", "orta"][i] if len(lst) > 1 else "sol")
        if taraf not in ("sol", "sag", "orta"):
            _hata(yer, f"taraf '{taraf}': sol | sag | orta")
        c["taraf"] = taraf
        if c.get("bakis") is True:  # YAML 'on' -> True
            c["bakis"] = "on"
        out.append(c)
    ids = [c["id"] for c in out]
    if len(set(ids)) != len(ids):
        _hata(yer, f"karakter kimlikleri tekrar ediyor: {ids}")
    return out


def _sahne(d: dict, video_ctx: dict, yer: str, base: Path) -> Sahne:
    if not isinstance(d, dict) or "tip" not in d:
        _hata(yer, "sahne sözlük olmalı ve 'tip' içermeli")
    tip = TIP_TAKMA.get(str(d["tip"]), str(d["tip"]))
    if tip not in SAHNE_PARAMLARI:
        _hata(yer, f"sahne tipi '{d['tip']}' bilinmiyor ({', '.join(sorted(SAHNE_PARAMLARI))})")
    _bilinmeyen(d, SAHNE_PARAMLARI[tip] | ORTAK, yer, f"'{tip}' sahnesi")
    for k in ZORUNLU[tip]:
        if d.get(k) in (None, "", []):
            _hata(yer, f"'{tip}' sahnesinde '{k}' zorunlu")
    p = {k: v for k, v in d.items() if k not in ORTAK}
    satirlar = [_satir(v, video_ctx["ses"], video_ctx["hiz"], video_ctx["sesler"], f"{yer}, satır {i + 1}")
                for i, v in enumerate(d.get("satirlar") or [])]
    n = len(satirlar)
    olaylar = [_olay(o, f"{yer}, olay {i + 1}", n) for i, o in enumerate(d.get("olaylar") or [])]
    # kısayollar: isim_etiketi / kelime sahne anahtarı olarak da yazılabilir
    for anahtar, tip_o in (("isim_etiketi", "isim"), ("kelime", "kelime")):
        v = d.get(anahtar)
        if v:
            for j, o in enumerate(v if isinstance(v, list) else [v]):
                if isinstance(o, str):
                    o = {"metin": o}
                olaylar.append(_olay({"tip": tip_o, **o}, f"{yer}, {anahtar} {j + 1}", n))
    sfx = [_sfx(s, f"{yer}, sfx {i + 1}", n, base) for i, s in enumerate(d.get("sfx") or [])]
    sahne = Sahne(tip=tip, p=p, satirlar=satirlar, olaylar=olaylar, sfx=sfx, yer=yer,
                  otomatik_sfx=bool(d.get("otomatik_sfx", video_ctx["otomatik_sfx"])))
    g = _gecis(d.get("gecis"), yer) or video_ctx["gecis"]
    sahne.gecis = g
    sahne.gecis_kare = int(d.get("gecis_kare", GECIS_KARE[g]))
    for k in ("sure", "min_sure", "bas", "ara", "son"):
        if d.get(k) is not None:
            setattr(sahne, k, _sayi(d[k], yer, k, 0))
    # karakter / görsel parametreleri
    if tip == "wojak":
        p["karakterler"] = _karakterler(p.get("karakterler"), yer, base)
        ids = {c["id"] for c in p["karakterler"]}
        for o in olaylar:
            if "karakter" in o.p and str(o.p["karakter"]) not in ids:
                _hata(yer, f"olay '{o.tip}': karakter '{o.p['karakter']}' yok ({', '.join(sorted(ids))})")
            if "karakter" in o.p:
                o.p["karakter"] = str(o.p["karakter"])
        for s in satirlar:
            if s.balon is not None and s.balon not in ids:
                _hata(yer, f"satır balonu: karakter '{s.balon}' yok ({', '.join(sorted(ids))})")
    else:
        for o in olaylar:
            if o.tip in ("yuz", "balon", "giris", "cikis"):
                _hata(yer, f"'{o.tip}' olayı yalnız wojak sahnesinde kullanılır")
        for s in satirlar:
            if s.balon:
                _hata(yer, "satır balonu yalnız wojak sahnesinde kullanılır")
    if tip == "zaman_cizelgesi":
        nk = p["noktalar"]
        if not isinstance(nk, list) or not 2 <= len(nk) <= 8:
            _hata(yer, "noktalar 2-8 öğelik liste olmalı (önerilen 3-6)")
        for i, n_ in enumerate(nk):
            if not isinstance(n_, dict) or "tarih" not in n_:
                _hata(yer, f"{i + 1}. noktada 'tarih' yok")
    if tip == "sayac" and p.get("deger") is None and p.get("yil") is None:
        _hata(yer, "sayac: 'deger' (ör. 10000) ya da 'yil' ([1957, 1961]) gerekli")
    if tip == "harita" and not (p.get("ulkeler") or p.get("vurgu")):
        _hata(yer, "harita: 'ulkeler' ya da 'vurgu' gerekli")
    if tip == "manset":
        kutular = p.get("kutular") or []
        if isinstance(kutular, list) and kutular and isinstance(kutular[0], (int, float)):
            kutular = [kutular]
        for k in kutular:
            if not (isinstance(k, list) and len(k) == 4):
                _hata(yer, f"manset kutusu [x0, y0, x1, y1] olmalı: {k!r}")
        p["kutular"] = kutular
    # dosya yolları
    for k in ("arka", "gorsel"):
        if p.get(k):
            p[k] = yol_coz(p[k], base)
    for c in p.get("karakterler", []):
        c["gorsel"] = yol_coz(c["gorsel"], base)
    for o in olaylar:
        if o.tip == "yuz":
            o.p["gorsel"] = yol_coz(o.p["gorsel"], base)
    return sahne


def yukle(yol) -> Video:
    """uzun/<id>/ klasörünü ya da video.yaml dosyasını yükler ve doğrular."""
    yol = Path(yol)
    if yol.is_dir():
        yol = yol / "video.yaml"
    if not yol.exists():
        raise SpecHatasi(f"bulunamadı: {yol}")
    try:
        raw = yaml.safe_load(yol.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as e:
        raise SpecHatasi(f"{yol}: YAML hatası: {e}") from e
    return yukle_sozluk(raw, yol.parent.resolve())


VIDEO_ANAHTARLARI = {"id", "baslik", "sesler", "anlatici", "model", "dil", "telaffuz", "muzik", "zamanlama",
                     "gecis", "filigran", "otomatik_sfx", "bolumler", "kucukresimler", "paket", "qa", "not"}


def yukle_sozluk(raw: dict, base: Path) -> Video:
    _bilinmeyen(raw, VIDEO_ANAHTARLARI, "video.yaml", "üst düzey")
    for k in ("id", "baslik", "bolumler"):
        if not raw.get(k):
            raise SpecHatasi(f"video.yaml: '{k}' zorunlu")
    vid = str(raw["id"])
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", vid):
        raise SpecHatasi(f"id '{vid}': küçük harf, rakam, - ve _ kullan")
    sesler = dict(VARSAYILAN_SESLER)
    sesler.update({str(k): str(v) for k, v in (raw.get("sesler") or {}).items()})
    an = raw.get("anlatici") or {}
    an_ses = str(an.get("ses", "murat"))
    if an_ses not in sesler:
        raise SpecHatasi(f"anlatici.ses '{an_ses}' sesler içinde yok")
    an_hiz = _sayi(an.get("hiz", 0.95), "anlatici", "hiz", 0.5, 2.0)
    zam = dict(VARSAYILAN_ZAMANLAMA)
    for k, v in (raw.get("zamanlama") or {}).items():
        if k not in VARSAYILAN_ZAMANLAMA:
            raise SpecHatasi(f"zamanlama: bilinmeyen anahtar '{k}' ({', '.join(VARSAYILAN_ZAMANLAMA)})")
        zam[k] = _sayi(v, "zamanlama", k, 0)
    gecis = _gecis(raw.get("gecis", "kesme"), "video.yaml")
    muzik = raw.get("muzik")
    if muzik is None or muzik is True:
        muzik = {}
    if muzik is False:
        muzik = {"yok": True}
    if isinstance(muzik, str):
        muzik = {"dosya": muzik}
    muzik = dict(muzik)
    _bilinmeyen(muzik, {"uret", "dosya", "tohum", "seviye", "acik", "giris", "cikis", "yok", "baslangic"},
                "muzik", "müzik")
    muzik.setdefault("tohum", zlib.crc32(vid.encode()) % 100000)
    if muzik.get("dosya"):
        muzik["dosya"] = yol_coz(muzik["dosya"], base)
    ctx = {"ses": an_ses, "hiz": an_hiz, "sesler": sesler, "gecis": gecis,
           "otomatik_sfx": bool(raw.get("otomatik_sfx", True))}
    bolumler: list[Bolum] = []
    kart_no = 0
    if not isinstance(raw["bolumler"], list):
        raise SpecHatasi("bolumler liste olmalı")
    for bi, b in enumerate(raw["bolumler"]):
        yer_b = f"bölüm {bi + 1}"
        if not isinstance(b, dict):
            raise SpecHatasi(f"{yer_b}: sözlük olmalı")
        _bilinmeyen(b, {"baslik", "kart", "numara", "sahneler", "kart_sure", "kart_ust", "kart_gecis",
                        "youtube", "not"}, yer_b, "bölüm")
        if not b.get("baslik"):
            raise SpecHatasi(f"{yer_b}: 'baslik' zorunlu")
        kart = bool(b.get("kart", bi > 0))
        sahneler = []
        numara = None
        if kart:
            kart_no += 1
            numara = int(b.get("numara", kart_no))
            ks = Sahne(tip="bolum_karti", p={"numara": numara, "baslik": str(b["baslik"]),
                                            "ust": b.get("kart_ust")},
                       sure=_sayi(b.get("kart_sure", zam["kart"]), yer_b, "kart_sure", 0.5),
                       yer=f"{yer_b}, kart", otomatik_sfx=ctx["otomatik_sfx"])
            ks.gecis = _gecis(b.get("kart_gecis"), yer_b) or "kesme"
            ks.gecis_kare = GECIS_KARE[ks.gecis]
            sahneler.append(ks)
        if not b.get("sahneler") and not kart:
            raise SpecHatasi(f"{yer_b}: 'sahneler' boş")
        for si, s in enumerate(b.get("sahneler") or []):
            sahneler.append(_sahne(s, ctx, f"{yer_b}, sahne {si + 1}", base))
        for s in sahneler:
            s.bolum = bi
        bolumler.append(Bolum(baslik=str(b["baslik"]), kart=kart, sahneler=sahneler, numara=numara,
                              kart_sure=float(b.get("kart_sure", zam["kart"])), youtube=b.get("youtube")))
    if bolumler and bolumler[0].sahneler:
        ilk = bolumler[0].sahneler[0]
        ilk.gecis, ilk.gecis_kare = "kesme", 0  # ilk sahnede önceki sahne yok
    tel = {str(k): str(v) for k, v in (raw.get("telaffuz") or {}).items()}
    qa = raw.get("qa") or {}
    v = Video(id=vid, baslik=str(raw["baslik"]), dir=base, sesler=sesler, anlatici_ses=an_ses,
              anlatici_hiz=an_hiz, model=str(raw.get("model", "sonic-3")), dil=str(raw.get("dil", "tr")),
              telaffuz=tel, muzik=muzik, zamanlama=zam, gecis=gecis,
              filigran=None if raw.get("filigran") is False else str(raw.get("filigran", config.WATERMARK)),
              otomatik_sfx=ctx["otomatik_sfx"], bolumler=bolumler,
              kucukresimler=list(raw.get("kucukresimler") or []), paket=dict(raw.get("paket") or {}),
              qa_isimler=[str(x) for x in (qa.get("isimler") or [])], raw=raw)
    for i, s in enumerate(v.sahneler):
        s.no = i
    return v


def eksik_dosyalar(v: Video) -> list[str]:
    """Var olmayan görsel/ses dosyaları (sahne yeriyle)."""
    out = []
    for s in v.sahneler:
        paths = [s.p.get("arka"), s.p.get("gorsel")] + [c["gorsel"] for c in s.p.get("karakterler", [])]
        paths += [o.p["gorsel"] for o in s.olaylar if o.tip == "yuz"]
        paths += [x.yol for x in s.sfx]
        for p in paths:
            if p is not None and not Path(p).exists():
                out.append(f"{s.yer}: {p}")
    if v.muzik.get("dosya") and not Path(v.muzik["dosya"]).exists():
        out.append(f"muzik: {v.muzik['dosya']}")
    return out
