"""'Bilgi' sahnelerinin (sayac, metin, zaman_cizelgesi, izgara, bölünmüş ekran metin paneli) zemini.

Düz koyu zemin boş görünüyordu (demo incelemesi). Üç stil:

- `koyu` (varsayılan): koyu degrade + düşük frekanslı leke dokusu + vinyet; `arka` verilirse ilgili fotoğrafın
  bulanık, karartılmış hâli `arka_opak` (vars. 0.5) oranında karışır.
- `foto`: `arka` fotoğrafının kendisi (bulanık, karartılmış, vinyetli) zemin olur (yoksa koyu).
- `kagit`: kendi ürettiğimiz eski kâğıt dokusu (sıcak kırık beyaz, lif, leke, kahverengi kenar); yazılar
  mürekkep renginde (palet). `arka` verilirse çok soluk, renksiz baskı gibi karışır.

Boşta hareket (hiçbir kare 2 sn'den uzun durağan kalmasın): yavaş kamera itmesi + yanal süzülme, koyu
zeminlerde süzülen toz zerreleri ve yavaşça gezinen sıcak ışık, kâğıtta gezinen yumuşak ışık; üstüne film
greni. Ön plan öğeleri `nefes()` / `suzul()` ile hafifçe nefes alır.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from . import cizim as C
from . import easing as E


@dataclass(frozen=True)
class Palet:
    metin: tuple          # ana yazı
    ikincil: tuple        # üst/alt küçük yazılar
    vurgu: tuple          # tarih, etiket, sayaç çizgisi
    cizgi: tuple          # eksen, ince çizgiler
    isaret: tuple         # fosforlu kalem
    golge: float          # yazı gölgesinin opaklığı (0: yok)
    koyu: bool

    def golge_t(self, S: float, dy: float = 5, bl: float = 10):
        """C.yazi(golge=...) değeri (ya da None)."""
        return (0, dy * S, bl * S, self.golge) if self.golge > 0 else None


KOYU = Palet(metin=C.BEYAZ, ikincil=(196, 200, 208), vurgu=C.SARI, cizgi=(110, 116, 128), isaret=C.SARI,
             golge=0.55, koyu=True)
KAGIT = Palet(metin=(36, 31, 28), ikincil=(104, 92, 78), vurgu=(170, 42, 34), cizgi=(150, 136, 116),
              isaret=(252, 214, 64), golge=0.0, koyu=False)

RENKLER = {"kirmizi": C.KIRMIZI, "yesil": C.YESIL, "sari": C.SARI, "beyaz": C.BEYAZ, "mavi": (64, 132, 222),
           "turuncu": (232, 128, 40), "gri": (150, 152, 158), "siyah": (24, 24, 26)}


def renk(v, varsayilan):
    """'kirmizi' | [r, g, b] | None -> (r, g, b)."""
    if v is None:
        return tuple(varsayilan)
    if isinstance(v, str):
        if v not in RENKLER:
            raise ValueError(f"renk '{v}' bilinmiyor ({', '.join(RENKLER)}) ya da [r, g, b] ver")
        return RENKLER[v]
    return tuple(int(x) for x in v)


def nefes(t: float, faz: float = 0.0, guc: float = 0.006) -> float:
    """Ön plan öğesinin yavaş nefesi (ölçek çarpanı)."""
    return 1.0 + guc * math.sin(2 * math.pi * 0.21 * t + faz)


def suzul(t: float, faz: float = 0.0, px: float = 3.0) -> float:
    """Ön plan öğesinin yavaş dikey süzülmesi (px, ölçeksiz)."""
    return px * math.sin(2 * math.pi * 0.17 * t + faz)


# ---------------------------------------------------------------- dokular (bir kez üretilir)

def _gurultu(W: int, H: int, olcek: int, tohum: int) -> np.ndarray:
    """Yumuşak, düşük frekanslı gürültü (-1..1), W x H."""
    rng = np.random.default_rng(tohum)
    g = rng.normal(0, 1, (max(2, H // olcek + 2), max(2, W // olcek + 2))).astype(np.float32)
    im = Image.fromarray(((np.clip(g, -3, 3) + 3) / 6 * 255).astype(np.uint8), "L").resize((W, H), Image.BICUBIC)
    return np.asarray(im, np.float32) / 127.5 - 1.0


@lru_cache(maxsize=6)
def kagit_dokusu(W: int, H: int, tohum: int = 5) -> Image.Image:
    """Eski kâğıt: sıcak kırık beyaz, büyük/orta lekeler, lifler, birkaç benek, kahverengi kenar."""
    S = W / 1920
    taban = np.array([234, 225, 205], np.float32)
    l1 = _gurultu(W, H, max(8, int(220 * S)), tohum)
    l2 = _gurultu(W, H, max(4, int(40 * S)), tohum + 1)
    l3 = _gurultu(W, H, 2, tohum + 2)
    lum = 1.0 + 0.035 * l1 + 0.018 * l2 + 0.012 * l3
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / math.sqrt(2)
    kenar = np.clip((d - 0.45) / 0.55, 0, 1) ** 1.7
    arr = taban[None, None, :] * lum[..., None]
    kahve = np.array([150, 112, 70], np.float32)
    arr = arr * (1 - 0.42 * kenar[..., None]) + kahve * (0.42 * kenar[..., None]) * 0.55
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")
    # lifler ve benekler
    rng = np.random.default_rng(tohum + 3)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(lay)
    for _ in range(int(900 * S * S) + 60):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        a, L = rng.uniform(0, math.pi), rng.uniform(6, 26) * S
        c = (120, 100, 76, int(rng.uniform(10, 28))) if rng.random() < 0.6 else (255, 252, 244, int(rng.uniform(12, 30)))
        dr.line((x, y, x + L * math.cos(a), y + L * math.sin(a)), fill=c, width=max(1, int(S)))
    for _ in range(int(60 * S) + 8):
        x, y, r = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(0.6, 2.2) * S
        dr.ellipse((x - r, y - r, x + r, y + r), fill=(96, 76, 56, int(rng.uniform(30, 80))))
    im.paste(lay, (0, 0), lay)
    return im


@lru_cache(maxsize=6)
def leke_dokusu(W: int, H: int, tohum: int = 9) -> Image.Image:
    """Koyu zemin için çok hafif, büyük ölçekli aydınlık/karanlık lekeler (L, 128 = nötr)."""
    S = W / 1920
    g = 0.6 * _gurultu(W, H, max(8, int(260 * S)), tohum) + 0.4 * _gurultu(W, H, max(4, int(70 * S)), tohum + 1)
    return Image.fromarray(np.clip(128 + 60 * g, 0, 255).astype(np.uint8), "L")


@lru_cache(maxsize=8)
def _yumusak_nokta(r: int) -> Image.Image:
    """Toz zerresi maskesi (L), yumuşak kenarlı."""
    n = 2 * r + 5
    m = Image.new("L", (n, n), 0)
    ImageDraw.Draw(m).ellipse((2, 2, n - 3, n - 3), fill=255)
    return m.filter(ImageFilter.GaussianBlur(max(0.6, r * 0.45)))


@lru_cache(maxsize=4)
def _isik(cap: int) -> Image.Image:
    """Yumuşak ışık lekesi maskesi (L, merkez 255)."""
    yy, xx = np.mgrid[0:cap, 0:cap].astype(np.float32)
    d = np.sqrt((xx - cap / 2) ** 2 + (yy - cap / 2) ** 2) / (cap / 2)
    return Image.fromarray((np.clip(1 - d, 0, 1) ** 2.2 * 255).astype(np.uint8), "L")


# ---------------------------------------------------------------- zemin

class Zemin:
    """Sahne zemini: taban görüntü (kamera payıyla) + boşta hareket katmanları. ciz(t) -> RGB kare."""

    def __init__(self, c, p: dict, varsayilan: str = "koyu", zm: float = 1.08, ic=(30, 34, 42), dis=(7, 8, 11),
                 tohum: int = 0):
        self.c, self.W, self.H, self.S = c, c.W, c.H, c.S
        stil = p.get("zemin") or varsayilan
        arka = p.get("arka")
        if stil == "foto" and not arka:
            stil = "koyu"
        self.stil = stil
        self.palet = KAGIT if stil == "kagit" else KOYU
        W, H = round(c.W * zm), round(c.H * zm)
        self.zm = zm
        opak = p.get("arka_opak")
        if stil == "kagit":
            g = kagit_dokusu(W, H)
            if arka:
                ph = C.ayarla(C.kapla(C.yukle(arka).convert("RGB"), W, H), bulanik=3 * c.S, doygunluk=0.0,
                              kontrast=1.15)
                g = _carp(g, ph, 0.12 if opak is None else float(opak))
            self.gren = (0.035, (70, 56, 40))
        else:
            if stil == "foto":
                g = C.ayarla(C.kapla(C.yukle(arka).convert("RGB"), W, H), bulanik=float(p.get("bulanik", 14)) * c.S,
                             karart=0.52 if opak is None else 1 - float(opak), doygunluk=0.6)
                g = Image.blend(g, C.gradyan_zemin(W, H, ic, dis), 0.22)
            else:
                g = C.gradyan_zemin(W, H, ic, dis)
                if arka:
                    ph = C.ayarla(C.kapla(C.yukle(arka).convert("RGB"), W, H), bulanik=22 * c.S, karart=0.42,
                                  doygunluk=0.55)
                    g = Image.blend(g, ph, 0.5 if opak is None else float(opak))
                # hafif lekeler: düz degrade 'boş' görünmesin
                lk = leke_dokusu(W, H)
                g = Image.composite(Image.eval(g, lambda v: min(255, int(v * 1.42 + 3))),
                                    Image.eval(g, lambda v: int(v * 0.7)), lk)
            C.vinyet_uygula(g, 0.5)
            self.gren = (0.05, (255, 255, 255))
        self.taban = g
        # toz zerreleri (yalnız koyu/foto): (x0, y0, hız, salınım, frekans, faz, yarıçap, opaklık)
        rng = np.random.default_rng(31 + tohum)
        self.toz = []
        if stil != "kagit":
            for _ in range(34):
                self.toz.append((rng.uniform(0, 1), rng.uniform(0, 1), rng.uniform(8, 24), rng.uniform(5, 20),
                                 rng.uniform(0.04, 0.14), rng.uniform(0, 6.28), int(rng.integers(1, 4)),
                                 rng.uniform(0.05, 0.16)))
        self.faz = rng.uniform(0, 6.28)
        cap = int(1100 * c.S)
        self.isik = _isik(cap).point(C._alfa_lut(int(255 * (0.075 if stil != "kagit" else 0.16))))

    def kamera(self, t: float, dur: float) -> tuple[float, tuple[float, float]]:
        """Zemin kamerası: yavaş itme + yanal süzülme (hep hareketli)."""
        z = 1.0 + (self.zm - 1.0 - 0.012) * E.in_out_sine(t / max(dur, 1e-3))
        mx = 0.5 + 0.010 * math.sin(2 * math.pi * t / 9.0 + self.faz)
        my = 0.5 + 0.007 * math.sin(2 * math.pi * t / 11.0 + self.faz * 0.7)
        return z, (mx, my)

    def ciz(self, t: float, dur: float) -> Image.Image:
        W, H, S = self.W, self.H, self.S
        z, m = self.kamera(t, dur)
        im = C.kamera(self.taban, W, H, z, m)
        # gezinen ışık
        cap = self.isik.width
        lx = W * (0.25 + 0.5 * (0.5 + 0.5 * math.sin(2 * math.pi * t / 15.0 + self.faz)))
        ly = H * (0.38 + 0.12 * math.sin(2 * math.pi * t / 10.0 + self.faz * 1.3))
        isik_renk = (255, 220, 170) if self.stil != "kagit" else (255, 250, 236)
        im.paste(isik_renk, (int(lx - cap / 2), int(ly - cap / 2)), self.isik)
        # toz zerreleri: yukarı süzülür, yanlara salınır
        for x0, y0, v, sal, fr, fz, r, a in self.toz:
            y = (y0 * (H + 60 * S) - v * S * t) % (H + 60 * S) - 30 * S
            x = x0 * W + sal * S * math.sin(2 * math.pi * fr * t + fz)
            m_ = _yumusak_nokta(max(1, int(round(r * S * 1.6))))
            aa = a * (0.75 + 0.25 * math.sin(2 * math.pi * 0.3 * t + fz))
            im.paste((255, 246, 228), (int(x), int(y)), m_.point(C._alfa_lut(int(255 * aa))))
        guc, renk_ = self.gren
        C.gren_uygula(im, t, guc, renk=renk_)
        return im


def _carp(a: Image.Image, b: Image.Image, oran: float) -> Image.Image:
    """a'yı b ile çarparak (multiply) oran kadar karıştırır: kâğıda basılmış soluk fotoğraf."""
    if oran <= 0:
        return a
    x = np.asarray(a, np.float32)
    y = np.asarray(b.convert("RGB"), np.float32) / 255.0
    out = x * (1 - oran + oran * y)
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB")
