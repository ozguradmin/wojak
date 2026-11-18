"""hipodrom-nika-532: hazır kıyafetli iki isyancı ve ters köşe yüz varyantı.

    python episodes/hipodrom-nika-532/chars/uret.py

Kaynaklar (kaynak/ altında, wojak_site.py get ile indirildiği gibi):
  isyanci_kaynak.png  wojakland "Peasant Wojak" (https://wojakland.com/gmedia/peasant_wojak-png/), 552x667: klasik
                      beyaz wojak yüzü, siyah takke, kahverengi tunik; göz bebekleri sağa
  uyaran_kaynak.png   wojakland "Medieval 2 Wojak" (https://wojakland.com/gmedia/medieval_2_wojak-png/), 353x600:
                      düz MS-Paint wojak, turuncu takke, zeytin tunik, kırmızı iç gömlek; göz bebekleri sağa
Kıyafet boyanmaz. Yapılanlar:
  - isyanci_sakin (A, solda): göğüsten (y 575) kesildi; yüzdeki kahverengi lekeler (konturlarıyla) ve gri yanak gölgesi beyaza çevrildi; 2x büyütme.
  - isyanci_sok (A, aynı kutu): kaş, göz, göz altı, alın kırışıkları ve ağız silindi; iri yuvarlak göz + küçük göz bebeği
    (sağa, içeri; tur 1 SHOULD: +5 px), iç ucu kalkık kalın kaş, "O" ağız, alında 5 kısa mavi çizgi, başın önünde 3 ter damlası.
  - uyaran_terli (B, sağda): göğüsten kesildi (yüz büyüsün), 3x büyütme; turuncu takke koyu kahveye çevrildi (fes
    okunmasın: olay 532); dişli açık ağız silinip uçları aşağı düz çizgi (endişeli uyarı) + 2 ter damlası.
Bakış yönü dosyanın kendisine göre kaydedilir (python -m wojak yon ... --yon sag); episode.yaml'da faces: yok.
Çizim yardımcıları orban-topu-bizans/chars/uret.py'den kopyalandı.
"""
from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
KAYNAK = HERE / "kaynak"
sys.path.insert(0, str(ROOT / "tools"))
import kit_varyant  # noqa: E402

SS = 4
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)


def poly_mask(size, pts) -> np.ndarray:
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).polygon([tuple(p) for p in pts], fill=255)
    return np.array(m) > 0


def sil(im, pts, renk, tol=10):
    a = np.array(im).astype(np.int32)
    m = poly_mask(im.size, pts)
    d = np.abs(a[..., :3] - np.array(renk)).sum(-1)
    m &= (d > tol) & (a[..., 3] > 0)
    a[m, :3] = renk
    a[m, 3] = 255
    return Image.fromarray(a.astype(np.uint8))


def kutu(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


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

    def poligon(self, pts, dolgu):
        m, d = self._maske()
        d.polygon([(x * SS, y * SS) for x, y in pts], fill=255)
        self._bas(m, dolgu)


def ter(im, damlalar):
    tmp = HERE / "__kit_tmp.png"
    im.save(tmp)
    try:
        kit_varyant.make(tmp, {"drops": [list(d) for d in damlalar]}, tmp)
        return Image.open(tmp).convert("RGBA").copy()
    finally:
        tmp.unlink(missing_ok=True)


def kontur_sabitle(im):
    """Kesimde yarı saydam kalmış siyah kontur piksellerini (koyu RGB, alfa > 30) tam opak yapar."""
    a = np.array(im).astype(np.int32)
    m = (a[..., :3].sum(-1) < 240) & (a[..., 3] > 30)
    a[m, 3] = 255
    return Image.fromarray(a.astype(np.uint8))


def kaydet(im, ad):
    out = HERE / f"{ad}.png"
    im.save(out, optimize=True)
    print(f"-> {out.relative_to(ROOT)}  {im.width}x{im.height}")



TEN = (255, 255, 255)
from PIL import ImageFilter  # noqa: E402


def buyut(im, k):
    im = im.resize((im.width * k, im.height * k), Image.LANCZOS)
    rgb = im.convert("RGB").filter(ImageFilter.UnsharpMask(2, 60, 2))
    out = rgb.convert("RGBA")
    out.putalpha(im.getchannel("A"))
    return out


def siyah_sil(im, b, esik=640):
    """Kutudaki koyu (siyah çizgi) pikselleri beyaza çevirir; sakal/bıyık kahvesi kalır."""
    a = np.array(im).astype(np.int32)
    x0, y0, x1, y1 = b
    blok = a[y0:y1, x0:x1]
    rgb = blok[..., :3]
    m = ((rgb.max(-1) - rgb.min(-1)) < 30) & (rgb.sum(-1) < esik) & (blok[..., 3] > 0)  # yalnız gri/siyah
    blok[m, :3] = 255
    blok[m, 3] = 255
    return Image.fromarray(a.astype(np.uint8))




K = 2
S = lambda *v: [x * K for x in v]  # noqa: E731


def isyanci_temel():
    a = np.array(Image.open(KAYNAK / "isyanci_kaynak.png").convert("RGBA")).astype(np.int32)
    H, W = a.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    rgb = a[..., :3]
    yuz = (yy > 90) & (yy < 420) & (xx > 140) & (xx < 470) & (a[..., 3] > 0)
    gri = (rgb.max(-1) - rgb.min(-1)) < 20
    a[yuz & gri & (rgb.mean(-1) >= 175), :3] = 255            # yanak gölgesi
    kahve = yuz & (yy < 330) & (rgb[..., 0] - rgb[..., 2] > 30) & (rgb[..., 0] > 60)
    a[kahve, :3] = 255                                          # lekelerin içi
    for x0, y0, x1, y1 in [(193, 126, 259, 233), (257, 244, 311, 303), (397, 239, 444, 266)]:
        blok = a[y0:y1, x0:x1]
        blok[blok[..., 3] > 0, :3] = 255                        # leke konturu dahil
    im = kontur_sabitle(Image.fromarray(a.astype(np.uint8))).crop((0, 0, W, 575))   # göğüsten kes: yüz büyür
    return takke_yumusat(buyut(im, 2))


def takke_yumusat(im, y1=330, r=3.0):
    """Tur 1 görsel SHOULD: 2x büyütülmüş siyah takkenin tırtıklı kenarı. Takke maskesi (y < y1, koyu ve opak)
    Gauss ile yumuşatılıp yeniden eşiklenir; maskeden çıkan pikseller dışarıdaysa saydam, alında beyaz olur."""
    a = np.array(im).astype(np.int32)
    bolge = np.zeros(a.shape[:2], bool)
    bolge[:y1] = True
    siyah = bolge & (a[..., :3].max(-1) < 70) & (a[..., 3] > 128)
    yumusak = np.array(Image.fromarray((siyah * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r))) >= 128
    yumusak &= bolge
    opak = np.array(Image.fromarray(((a[..., 3] > 128) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r))) >= 128
    eklenen = yumusak & ~siyah
    a[eklenen, :3] = 0
    a[eklenen, 3] = 255
    cikan = siyah & ~yumusak
    a[cikan & ~opak, 3] = 0
    a[cikan & opak, :3] = 255
    a[cikan & opak, 3] = 255
    im = Image.fromarray(a.astype(np.uint8))
    # Tur 2 görsel SHOULD: takke 390 px'te düz siyah blok -> sol üstte koyu gri parlaklık kavisi (hacim)
    c = Cizim(im, seed=21)
    c.cizgi([tuple(S(170, 62)), tuple(S(205, 40)), tuple(S(255, 28)), tuple(S(305, 26))], 7 * K, renk=(78, 78, 82, 255), titrek=0.2)
    return c.im


def isyanci_sok(im):
    """1x hatlar: sol göz+kaş 258-336 x 186-242, sağ göz+kaş 384-447 x 180-238, alın kırışıkları 250-425 x 118-176,
    ağız 303-402 x 333-354. Çizgi ~4 px (2x'te 8)."""
    for b in [(258, 184, 337, 244), (383, 178, 447, 239), (248, 116, 428, 178), (302, 331, 404, 356), (328, 174, 346, 200), (252, 168, 270, 186)]:
        im = sil(im, kutu(*S(*b)), TEN, tol=-1)
    c = Cizim(im, seed=11)
    c.elips(*S(297, 216, 25, 23), dolgu=WHITE, w=4.5 * K)
    c.elips(*S(418, 214, 19, 22), dolgu=WHITE, w=4.5 * K)
    c.elips(*S(308, 217, 5.5, 5.5), dolgu=BLACK)
    c.elips(*S(428, 215, 5, 5), dolgu=BLACK)
    c.cizgi([tuple(S(268, 186)), tuple(S(285, 181)), tuple(S(303, 177)), tuple(S(322, 168))], 5.5 * K)
    c.cizgi([tuple(S(398, 167)), tuple(S(412, 175)), tuple(S(428, 181)), tuple(S(444, 185))], 5.5 * K)
    mavi = (60, 120, 230, 255)
    for x, y0, y1 in [(300, 128, 150), (322, 122, 146), (345, 126, 152), (368, 121, 145), (390, 128, 149)]:
        c.cizgi([tuple(S(x, y0)), tuple(S(x + 3, (y0 + y1) / 2)), tuple(S(x - 1, y1))], 3 * K, renk=mavi)
    c.elips(*S(352, 344, 12, 16), dolgu=(70, 18, 22, 255), w=4 * K)
    return ter(c.im, [tuple(S(498, 175, 16)), tuple(S(512, 228, 13)), tuple(S(503, 276, 11))])


def uyaran_terli():
    im = Image.open(KAYNAK / "uyaran_kaynak.png").convert("RGBA").crop((0, 0, 353, 335))
    a = np.array(im).astype(np.int32)
    rgb = a[..., :3]
    takke = (rgb[..., 0] - rgb[..., 2] > 40) & (rgb[..., 0] > 60) & (a[..., 3] > 0)
    takke[110:, :] = False
    t = np.clip(rgb[..., 0] / 184.0, 0, 1)[..., None]           # kenar yumuşatmasındaki koyulaşmayı koru
    a[..., :3] = np.where(takke[..., None], (t * np.array([92, 72, 58])).astype(np.int32), a[..., :3])
    im = kontur_sabitle(Image.fromarray(a.astype(np.uint8)))
    im = buyut(im, 3)
    k = 3
    T = lambda *v: [x * k for x in v]  # noqa: E731
    im = sil(im, kutu(*T(190, 136, 252, 154)), TEN, tol=-1)        # dişli açık ağız
    c = Cizim(im, seed=13)
    c.cizgi([tuple(T(198, 149)), tuple(T(210, 145)), tuple(T(228, 144)), tuple(T(244, 148))], 3 * k)
    return ter(c.im, [tuple(T(292, 110, 7)), tuple(T(299, 138, 6))])


if __name__ == "__main__":
    t = isyanci_temel()
    kaydet(t, "isyanci_sakin")
    kaydet(isyanci_sok(t.copy()), "isyanci_sok")
    kaydet(uyaran_terli(), "uyaran_terli")
