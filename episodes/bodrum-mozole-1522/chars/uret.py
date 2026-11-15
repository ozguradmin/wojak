"""bodrum-mozole-1522: hazır kıyafetli iki şövalye ve ters köşe yüz varyantı.

    python episodes/bodrum-mozole-1522/chars/uret.py

Kaynaklar (chars/kaynak/, wojak_site.py get ile indirildiği gibi):
  hosp_kaynak.png   wojakland "Knight 5 Wojak" (https://wojakland.com/gmedia/knight_5_wojak-png/), 563x630: klasik wojak
                    yüzü, zincir başlık + miğfer, siyah üstlük üzerinde beyaz haç (Saint-Jean şövalyesi), balta.
                    Burun ve göz bebekleri sağa. A (solda): mezarı bulan genç şövalye. 2x LANCZOS + UnsharpMask(2,60,2).
  plaka_kaynak.png  wojakland "Knight 4 Wojak" (https://wojakland.com/gmedia/knight_4_wojak-png/), 938x1147: yaşlı
                    wojak yüzü, plaka zırh, 16. yy armet benzeri miğfer. Göz bebekleri sağa. B (sağda): komutan.
                    Göğüsten (y 690) kesilir: yüz büyür.
Karakterler kurgudur, gerçek bir kişiyi temsil etmez. Ters köşe (hosp_sok): el kitabı §10 tarifi; Cizim/ter/sil
patrona-halil-1730/chars/uret.py'den kopya (ten rengi beyaz).
"""
from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
K = HERE / "kaynak"
sys.path.insert(0, str(ROOT / "tools"))
import kit_varyant  # noqa: E402

SS = 4
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)
TEN = (255, 255, 255)
MAVI_TER = (70, 140, 230, 255)
KIRMIZI = np.array([200, 50, 38])


def catmull(pts, n=14):
    P = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    out.append(P[-2])
    return out


class Cizim:
    """haydarpasa-patlamasi-1917/chars/uret.py'den (o da karakoy-tunel-1874'ten) kopya."""

    def __init__(self, im, seed=1):
        self.im = im
        self.rng = random.Random(seed)

    def _maske(self):
        W, H = self.im.size
        m = Image.new("L", (W * SS, H * SS), 0)
        return m, ImageDraw.Draw(m)

    def _bas(self, m, renk):
        W, H = self.im.size
        m = m.resize((W, H), Image.LANCZOS).point(lambda v: max(0, min(255, (v - 64) * 2)))
        self.im.paste(Image.new("RGBA", (W, H), renk), (0, 0), m)

    def cizgi(self, pts, w, renk=BLACK, titrek=0.3):
        p = catmull(pts) if len(pts) > 2 else list(pts)
        ph = self.rng.random() * 6
        p = [(x + titrek * math.sin(i * 0.41 + ph), y + titrek * math.cos(i * 0.33 + ph)) for i, (x, y) in enumerate(p)]
        m, d = self._maske()
        q = [(x * SS, y * SS) for x, y in p]
        d.line(q, fill=255, width=round(w * SS), joint="curve")
        r = w * SS / 2
        for x, y in (q[0], q[-1]):
            d.ellipse([x - r, y - r, x + r, y + r], fill=255)
        self._bas(m, renk)

    def elips(self, cx, cy, rx, ry, dolgu=None, w=0, renk=BLACK):
        b = [(cx - rx) * SS, (cy - ry) * SS, (cx + rx) * SS, (cy + ry) * SS]
        if dolgu is not None:
            m, d = self._maske()
            d.ellipse(b, fill=255)
            self._bas(m, dolgu)
        if w:
            m, d = self._maske()
            d.ellipse(b, outline=255, width=round(w * SS))
            self._bas(m, renk)


def ter(im, damlalar):
    tmp = HERE / "__kit_tmp.png"
    im.save(tmp)
    try:
        kit_varyant.make(tmp, {"drops": [list(d) for d in damlalar]}, tmp)
        return Image.open(tmp).convert("RGBA").copy()
    finally:
        tmp.unlink(missing_ok=True)


def sil(im, box):
    """Kutudaki opak, ten olmayan pikselleri (çizgi) ten rengine boyar."""
    a = np.array(im).astype(np.int32)
    x0, y0, x1, y1 = box
    b = a[y0:y1, x0:x1]
    m = (np.abs(b[..., :3] - np.array(TEN)).sum(-1) > 12) & (b[..., 3] > 0)
    b[m, :3] = TEN
    return Image.fromarray(a.astype(np.uint8))




def sok(im):
    """Hatlar (2x tuval): sol göz 650-765 x 400-450, sağ göz 885-970 x 410-465; kaşlar y 330-360; alın izleri
    760-780 x 355-385 ve 875-882 x 365-400; ağız 735-900 x 655-690; yüzün sağ konturu x ~1015; miğfer kenarı y ~330."""
    im = sil(im, (636, 338, 780, 466))
    im = sil(im, (868, 332, 985, 474))
    im = sil(im, (752, 352, 790, 392))
    im = sil(im, (868, 360, 890, 404))
    im = sil(im, (728, 640, 910, 702))
    c = Cizim(im, seed=7)
    c.elips(708, 432, 46, 40, dolgu=WHITE, w=9)
    c.elips(930, 440, 39, 35, dolgu=WHITE, w=9)
    c.elips(726, 438, 9, 9, dolgu=BLACK)
    c.elips(944, 445, 8, 8, dolgu=BLACK)
    c.cizgi([(652, 384), (694, 372), (742, 350)], 10)
    c.cizgi([(884, 350), (920, 364), (962, 382)], 10)
    c.elips(818, 672, 27, 34, dolgu=(90, 25, 25, 255), w=9)
    for x0, y0, x1, y1 in [(770, 360, 812, 366), (824, 354, 866, 360), (784, 384, 826, 390), (836, 380, 870, 386)]:
        c.cizgi([(x0 - 4, y0), ((x0 + x1) / 2, (y0 + y1) / 2 - 4), (x1 + 4, y1)], 6.5, renk=MAVI_TER)
    return ter(c.im, [(1060, 420, 20), (1074, 484, 17), (1062, 540, 13)])


def duzlestir(im):
    """Gölgeli/ressamsı kask ve zincir zırhı düz MS-Paint renklerine çeker (el kitabı §10): siyah kontur (lum < 30),
    yüzün ve haçın büyük beyaz bölgeleri korunur; ara tonlar ve küçük beyaz parlamalar/zincir halkaları bölgeye göre düz
    renge boyanır (yüz, deliksiz doldurulmuş en büyük beyaz bölge, korunur): kask ve kenar bandı (bileşen ortalaması y < 360) açık gri, zincir başlık ve balta koyu gri, sap düz kahve."""
    a = np.array(im).astype(np.int32)
    rgb, al = a[..., :3], a[..., 3]
    lum = rgb.mean(-1)
    beyaz = (al > 0) & (lum > 235)
    lab, n = ndimage.label(beyaz)
    boy = ndimage.sum(beyaz, lab, range(1, n + 1))
    kucuk_beyaz = np.isin(lab, [i + 1 for i, v in enumerate(boy) if v < 3000])
    ara = (al > 0) & (((lum >= 30) & (lum <= 235)) | kucuk_beyaz)
    yuz = [i + 1 for i, v in enumerate(boy) if v >= 3000]
    yuz = max(yuz, key=lambda i: boy[i - 1])            # en büyük beyaz bölge yüz
    yuz = ndimage.binary_fill_holes(lab == yuz)          # göz, kaş, burun, ağız içeride kalır
    ara &= ~yuz
    kahve = ara & (rgb[..., 0] > rgb[..., 2] + 25)
    gri = ara & ~kahve
    glab, gn = ndimage.label(gri)
    ort_y = ndimage.mean(np.indices(gri.shape)[0], glab, range(1, gn + 1))
    kask = np.isin(glab, [i + 1 for i, y in enumerate(ort_y) if y < 360])
    zincir = gri & ~kask
    a[kask, :3] = (168, 172, 172)
    a[zincir, :3] = (104, 106, 110)
    a[kahve, :3] = (122, 74, 40)
    return Image.fromarray(a.astype(np.uint8))


def kaydet(im, ad):
    out = HERE / f"{ad}.png"
    im.save(out, optimize=True)
    print(f"-> {out.relative_to(ROOT)}  {im.width}x{im.height}")


if __name__ == "__main__":
    from PIL import ImageFilter
    h = Image.open(K / "hosp_kaynak.png").convert("RGBA")
    h = h.resize((h.width * 2, h.height * 2), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 60, 2))
    h = duzlestir(h.crop((0, 0, h.width, 1180)))
    out = Image.new("RGBA", (h.width + 0, h.height), (0, 0, 0, 0))
    out.alpha_composite(h)
    kaydet(out, "hosp_sakin")
    kaydet(sok(out.copy()), "hosp_sok")
    p = Image.open(K / "plaka_kaynak.png").convert("RGBA")
    kaydet(p.crop((0, 0, p.width, 690)), "komutan")
