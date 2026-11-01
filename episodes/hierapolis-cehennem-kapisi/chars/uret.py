"""hierapolis-cehennem-kapisi: hazır kıyafetli iki karakter ve ters köşe yüz varyantı.

    python episodes/hierapolis-cehennem-kapisi/chars/uret.py

Kaynaklar (kaynak/ altında, indirildiği gibi; şeffaf kenarı kırpılmış):
  gezgin2_kaynak.png wojakland "Roman Crying Wojak" (https://wojakland.com/wp-content/grand-media/image/original/roman_crying_wojak.png),
                     1313x1212; düz MS-Paint, saç bandı, kırmızı pelerin. Videoda adsız bir gezgin (Strabon'un anlattığı ziyaretçi).
  rahip_kaynak.png   HF clayshoaf/Wojaks 5_Doomer/13985 "Phrygian Doomer", 473x669; Frig başlığı (Kybele rahiplerinin başlığı).
Kıyafete dokunulmaz. Yapılanlar:
  - gezgin: ağlayan yüzün içi silinip sakin klasik wojak yüzü çizildi (gezgin2_sakin); göz bebekleri sağa.
  - rahip: doomer yüzündeki kan izi, kırmızı çatlaklar ve göz altı gri gölgesi silindi (siyah kontur kalır); 2x büyütme.
  - ters köşe varyantı: aşağıdaki *_sok fonksiyonu.
Bakış yönü dosyanın kendisine göre kaydedilir (python -m wojak yon ... ); episode.yaml'da faces: yok.
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


def rahip_temel():
    im = kontur_sabitle(Image.open(KAYNAK / "rahip_kaynak.png").convert("RGBA"))
    a = np.array(im).astype(np.int32)
    x0, y0, x1, y1 = 180, 296, 372, 371   # göz altı + burun üstü bölgesi (1x)
    blok = a[y0:y1, x0:x1]
    rgb = blok[..., :3]
    sat = rgb.max(-1) - rgb.min(-1)
    lum = rgb.mean(-1)
    kontur = (sat < 45) & (lum < 95)
    m = ~kontur & (blok[..., 3] > 0)
    blok[m, :3] = 255
    # yüz ve boyundaki gri fırça gölgesi düz beyaza (kontur ve sakal kalır)
    x0, y0, x1, y1 = 100, 240, 473, 620
    blok = a[y0:y1, x0:x1]
    rgb = blok[..., :3]
    sat = rgb.max(-1) - rgb.min(-1)
    lum = rgb.mean(-1)
    m = (sat < 30) & (lum > 135) & (blok[..., 3] > 0)
    blok[m, :3] = 255
    # göz altlarında kalan kahverengi/koyu çatlak kırıntıları
    for x0, y0, x1, y1 in [(228, 316, 262, 329), (316, 296, 327, 328)]:
        a[y0:y1, x0:x1, :3] = 255
    return buyut(Image.fromarray(a.astype(np.uint8)), K)


MAVI = (60, 120, 230, 255)


def gezgin2_sakin():
    """wojakland 'Roman Crying Wojak' (roman_crying_wojak.png, 1313x1212; düz MS-Paint, saç bandı, kırmızı pelerin).
    Ağlayan yüzün içi (kızarık göz, gözyaşı, kırışık, sıkılı diş) silinip sakin klasik wojak yüzü çizildi; kontur, saç ve
    kıyafet aynen kalır. 1x koordinat: yüz içi x 655-985, y 305-672; göz bebekleri sağa (içeri)."""
    im = kontur_sabitle(Image.open(KAYNAK / "gezgin2_kaynak.png").convert("RGBA"))
    a = np.array(im).astype(np.int32)
    m = poly_mask(im.size, [(620, 305), (975, 305), (987, 420), (978, 495), (958, 535), (936, 578), (920, 612),
                            (892, 642), (850, 660), (800, 664), (762, 652), (704, 614), (672, 575), (640, 540), (620, 470)])
    rgb = a[..., :3]
    sat = rgb.max(-1) - rgb.min(-1)
    lum = rgb.mean(-1)
    sac = (sat >= 8) & (sat <= 40) & (lum < 90)   # kahverengi saç; kızarık göz kenarı (sat > 40) silinir
    from scipy import ndimage
    lab, n = ndimage.label(sac)
    boy = ndimage.sum(sac, lab, range(1, n + 1))
    sac = np.isin(lab, 1 + np.nonzero(boy > 1500)[0])  # yalnız büyük saç bölgeleri; kırıntılar silinir
    m &= ~sac & (a[..., 3] > 0)
    a[m, :3] = 255
    # kontur dışına taşan gözyaşı (mavi) kalıntıları
    blok = a[300:720, 600:1000]
    mavi = (blok[..., 2] > blok[..., 0] + 35) & (blok[..., 3] > 0)
    blok[mavi, :3] = 255
    im = Image.fromarray(a.astype(np.uint8))
    c = Cizim(im, seed=21)
    w = 9
    # kaşlar (hafif üzgün, iç uçlar az yukarıda)
    c.cizgi([(675, 338), (712, 330), (752, 326), (778, 322)], w)
    c.cizgi([(848, 322), (875, 326), (915, 330), (950, 338)], w)
    # gözler: üst kapak + alt kapak, göz bebeği sağa
    for cx in (728, 902):
        c.cizgi([(cx - 42, 378), (cx - 18, 364), (cx + 12, 362), (cx + 40, 372)], w)
        c.cizgi([(cx - 38, 380), (cx - 10, 388), (cx + 20, 388), (cx + 40, 374)], 6)
        c.elips(cx + 18, 376, 11, 11, dolgu=BLACK)
        c.cizgi([(cx - 26, 408), (cx, 414), (cx + 26, 410)], 4)
    # burun
    c.cizgi([(838, 400), (842, 450), (848, 500), (838, 516), (808, 514), (790, 500)], w)
    # ağız (düz, uçları hafif aşağı)
    c.cizgi([(758, 596), (785, 588), (835, 586), (872, 590), (884, 598)], w)
    return buyut(c.im, 1) if False else c.im


def rahip_sok(im):
    """Mağaradan çıkan rahip: nefesini tutmuş, boğulma belirtisi (Strabon). 1x hatlar: sol göz 197-257 x 292-315,
    sağ göz 322-365 x 302-320, kaşlar y 277-290, ağız 242-335 x 420-442, alın bandın altında y 262-276."""
    for b in [(192, 270, 266, 330), (316, 274, 372, 329)]:
        im = sil(im, kutu(*S(*b)), TEN, tol=-1)
    c = Cizim(im, seed=11)
    # iri yuvarlak gözler + küçük göz bebeği (dosyanın baktığı yöne, sağa)
    c.elips(*S(228, 304, 23, 21), dolgu=WHITE, w=4.0 * K)
    c.elips(*S(344, 308, 19, 20), dolgu=WHITE, w=4.0 * K)
    c.elips(*S(233, 305, 4.5, 4.5), dolgu=BLACK)
    c.elips(*S(349, 309, 4.0, 4.0), dolgu=BLACK)
    # iç ucu kalkık kaşlar
    c.cizgi([tuple(S(202, 282)), tuple(S(218, 279)), tuple(S(236, 275)), tuple(S(254, 270))], 4.0 * K)
    c.cizgi([tuple(S(326, 272)), tuple(S(340, 276)), tuple(S(354, 280)), tuple(S(368, 284))], 4.0 * K)
    # alında mavi çizgiler (bant ile kaş arası)
    for x0, y0, x1 in [(262, 262, 300), (272, 268, 312), (306, 263, 330), (214, 266, 240), (282, 274, 310)]:
        c.cizgi([tuple(S(x0, y0)), tuple(S((x0 + x1) / 2, y0 - 1.5)), tuple(S(x1, y0 + 0.5))], 2.2 * K, renk=MAVI)
    # sakal içinde "O" ağız: ten rengi halka + koyu iç
    c.elips(*S(290, 433, 17, 18), dolgu=WHITE)
    c.elips(*S(290, 433, 12, 14), dolgu=(70, 18, 22, 255), w=3.5 * K)
    return ter(c.im, [tuple(S(420, 296, 10)), tuple(S(432, 334, 9)), tuple(S(422, 370, 8))])


if __name__ == "__main__":
    kaydet(gezgin2_sakin(), "gezgin_sakin")
    r = rahip_temel()
    r = r.crop((0, 0, r.width, 1060))   # uzun Frig başlığı: sakalın altından kes, yüz büyüsün
    kaydet(r, "rahip_sakin")
    kaydet(rahip_sok(r.copy()), "rahip_sok")
