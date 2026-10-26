"""yerebatan-bodrum-balik: hazır kıyafetli iki karakter ve ters köşe yüz varyantı.

    python episodes/yerebatan-bodrum-balik/chars/uret.py

Kaynaklar (kaynak/ altında, wojak_site.py get ile indirildiği gibi; şeffaf kenarı kırpılmış):
  medieval_2_wojak.png   wojakland "Medieval 2 Wojak"
                         (https://wojakland.com/wp-content/grand-media/image/original/medieval_2_wojak.png), 353x600;
                         turuncu takke, zeytin yeşili cüppe, kırmızı gömlek; klasik beyaz wojak yüzü, kirli sakal;
                         burun ve göz bebekleri sağa
  renaissance_wojak.png  wojakland "Renaissance Wojak"
                         (https://wojakland.com/wp-content/grand-media/image/original/renaissance_wojak.png), 523x579;
                         mor Rönesans beresi, kızıl sakal, gömlek + çapraz kuşak; klasik beyaz yüz; burun ve göz bebekleri sağa
Kıyafete dokunulmaz. Yapılanlar:
  - evsahibi_sakin (A, solda): turuncu silindir takke koyu kahve keçeye boyandı (turuncusu telefonda fes gibi okunuyordu;
    fes 1829 sonrası), 3x büyütme (LANCZOS + hafif keskinleştirme), göğüsten kesik; somurtan dişli ağız silinip
    yerine hafif gülümseyen tek çizgi (kanalda dişli somurtma "kötü/aptal" okunuyor; ev sahibi masum).
  - gyllius_sakin (B, sağda): 2x büyütme. Yüz değişmez.
  - gyllius_sok (B, aynı kutu): kaşlar ve gözler silinip iri yuvarlak göz + küçük göz bebeği, kalkık kaş, sakalın içinde
    "O" ağız; başın önünde (kontur dışında) üç ter damlası.
Bakış yönü dosyanın kendisine göre kaydedilir (python -m wojak yon ... --yon sag); episode.yaml'da faces: yok.
Çizim yardımcıları tahran-1985-ertugrul/chars/uret.py'den kopyalandı.
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


def takke_boya(im):
    """Turuncu silindir takke telefonda fes gibi okunuyor (fes 1829 sonrası). Bağlı bölge (tohum takkenin içinde)
    koyu kahve keçe rengine boyanır; tonlama korunur."""
    from scipy import ndimage
    a = np.array(im).astype(np.float64)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    turuncu = (r > 120) & (r - b > 70) & (g < r - 30) & (a[..., 3] > 0)
    lab, _ = ndimage.label(turuncu)
    m = lab == lab[45, 150]
    lum = (0.299 * r + 0.587 * g + 0.114 * b)[m]
    f = lum / np.median(lum)
    hedef = np.array([86.0, 62.0, 46.0])
    a[m, :3] = np.clip(hedef[None, :] * f[:, None], 0, 255)
    return Image.fromarray(a.astype(np.uint8))


def evsahibi_sakin():
    k = 3
    im = kontur_sabitle(Image.open(KAYNAK / "medieval_2_wojak.png").convert("RGBA"))
    im = takke_boya(im)
    im = buyut(im, k).crop((0, 0, 353 * k, 330 * k))
    # dişli somurtma ağzı (1x: x 190-252, y 134-154) -> beyaz, yerine hafif gülümseme
    im = sil(im, kutu(187 * k, 133 * k, 254 * k, 155 * k), TEN, tol=-1)
    c = Cizim(im, seed=3)
    c.cizgi([(200 * k, 141 * k), (215 * k, 147 * k), (233 * k, 147 * k), (247 * k, 140 * k)], 4.5 * k)
    return c.im


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


def gyllius_temel():
    im = kontur_sabitle(Image.open(KAYNAK / "renaissance_wojak.png").convert("RGBA"))
    return buyut(im, 2)


def gyllius_sok(im):
    """1x ölçülen hatlar (px): sol kaş 237-302 x 158-176, sağ kaş 355-405 x 160-182, kaş arası dikey çizgi 352-362 x
    172-198; sol göz 248-305 x 195-226, sağ göz 365-405 x 205-232; ağız 295-350 x 324-338 (bıyık ile sakal arası).
    Çizgi ~6 px (2x'te 12)."""
    k = 2
    S = lambda *v: [x * k for x in v]  # noqa: E731
    for b in [(234, 152, 308, 180), (350, 154, 410, 186), (349, 170, 364, 200), (244, 190, 310, 232), (360, 198, 410, 238)]:
        im = sil(im, kutu(*S(*b)), TEN, tol=-1)
    im = siyah_sil(im, S(284, 316, 378, 346))  # eski ağız çizgisi
    c = Cizim(im, seed=7)
    # iri yuvarlak gözler + küçük göz bebeği (bakılan yöne, sağa)
    c.elips(*S(277, 212, 27, 25), dolgu=WHITE, w=6 * k)
    c.elips(*S(386, 218, 20, 23), dolgu=WHITE, w=6 * k)
    c.elips(*S(282, 213, 6, 6), dolgu=BLACK)
    c.elips(*S(390, 219, 5.5, 5.5), dolgu=BLACK)
    # kalkık kaşlar
    c.cizgi([tuple(S(240, 176)), tuple(S(258, 160)), tuple(S(284, 154)), tuple(S(306, 160))], 6 * k)
    c.cizgi([tuple(S(360, 160)), tuple(S(380, 152)), tuple(S(398, 156)), tuple(S(410, 166))], 6 * k)
    # "O" ağız: koyu iç + siyah kontur
    c.elips(*S(324, 334, 15, 20), dolgu=(70, 18, 22, 255), w=5 * k)
    return ter(c.im, [tuple(S(458, 222, 20)), tuple(S(476, 282, 16)), tuple(S(462, 336, 13))])


if __name__ == "__main__":
    kaydet(evsahibi_sakin(), "evsahibi_sakin")
    g = gyllius_temel()
    kaydet(g, "gyllius_sakin")
    kaydet(gyllius_sok(g.copy()), "gyllius_sok")
