"""hannibal-gebze-yedi-kapi: hazır kıyafetli iki karakter ve ters köşe yüz varyantı.

    python episodes/hannibal-gebze-yedi-kapi/chars/uret.py

Kaynaklar (kaynak/ altında):
  gezgin2_kaynak.png wojakland "Roman Crying Wojak" (https://wojakland.com/wp-content/grand-media/image/original/roman_crying_wojak.png),
                     1313x1212; düz MS-Paint, saç bandı, kırmızı pelerin. Videoda Hannibal'in adsız hizmetkârı (Nepos 12'deki "puer").
                     Sakin yüz hierapolis-cehennem-kapisi'ndeki gezgin2_sakin() ile aynı yoldan çizilir.
  kaynak_helm.png    wojakland "Ancient Helm Wojak" (https://wojakland.com/gmedia/ancient_helm_wojak-png/), 726x1011; Frig/Trak tipi
                     sarı miğfer, sakallı. Videoda yaşlı Hannibal.
Kıyafete dokunulmaz. Yapılanlar:
  - hizmetkar_sakin: ağlayan yüzün içi silinip sakin klasik wojak yüzü (göz bebekleri sağa).
  - hizmetkar_sok: ters köşe yüzü (el kitabı §10 tarifi: iri yuvarlak göz + küçük bebek, iç ucu kalkık kaş, "O" ağız,
    alında mavi çizgiler, başın önünde 3 damla).
  - hannibal: sarı sakal (yalnız sakal bölgeleri, scipy.ndimage.label) yaşlılık için gri; dişleri görünen gergin ağız
    kapalı, yorgun bir ağza çevrildi; 1,5x büyütme.
Bakış yönü dosyanın kendisine göre kaydedilir (python -m wojak yon ... ); episode.yaml'da faces: yok.
Çizim yardımcıları hierapolis-cehennem-kapisi/chars/uret.py'den (oradan orban-topu-bizans'tan) kopyalandı.
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




MAVI = (60, 120, 230, 255)
GRI = (196, 196, 192, 255)


def hizmetkar_sok(im):
    """gezgin2_sakin yüzü üzerine şok: 1x hatlar: gözler cx 728/902, y 362-414; kaşlar y 322-338; ağız y 586-598.
    İlk sürüm (göz r 36, damla 20/18/16) telefonda alt yarıda %0,32 kaldı; büyütüldü."""
    im = sil(im, kutu(664, 312, 794, 432), TEN, tol=-1)
    im = sil(im, kutu(850, 312, 972, 432), TEN, tol=-1)
    im = sil(im, kutu(744, 570, 900, 616), TEN, tol=-1)
    c = Cizim(im, seed=33)
    w = 12
    for cx in (726, 910):
        c.elips(cx, 384, 46, 44, dolgu=WHITE, w=10)
        c.elips(cx + 14, 386, 10, 10, dolgu=BLACK)
    # iç ucu kalkık kalın kaşlar
    c.cizgi([(676, 336), (708, 326), (744, 314), (782, 300)], w)
    c.cizgi([(852, 300), (888, 314), (926, 326), (962, 336)], w)
    # büyük "O" ağız
    c.elips(820, 606, 26, 32, dolgu=(70, 18, 22, 255), w=10)
    # alında mavi çizgiler (kaşın üstü, saç perçeminin altı)
    for x0, y0, x1 in [(752, 290, 800), (812, 286, 856), (764, 300, 806), (826, 296, 868), (870, 292, 912)]:
        c.cizgi([(x0, y0), ((x0 + x1) / 2, y0 - 2), (x1, y0 + 1)], 7, renk=MAVI)
    return ter(c.im, [(1076, 318, 40), (1102, 398, 34), (1082, 468, 28)])


def hannibal():
    from scipy import ndimage
    im = kontur_sabitle(Image.open(KAYNAK / "kaynak_helm.png").convert("RGBA"))
    a = np.array(im).astype(np.int32)
    rgb = a[..., :3]
    sari = (rgb[..., 0] > 200) & (rgb[..., 1] > 150) & (rgb[..., 2] < 80) & (a[..., 3] > 0)
    lab, n = ndimage.label(sari)
    for i in range(1, n + 1):
        ys, xs = np.nonzero(lab == i)
        if ys.min() >= 470 and xs.min() >= 200:   # miğfer (y < 470) ve ense parçası (x < 200) değil, yalnız sakal
            a[lab == i, :3] = GRI[:3]
    im = Image.fromarray(a.astype(np.uint8))
    # dişleri görünen ağız: iç kısmı gri sakalla doldur, kapalı yorgun ağız çiz
    c = Cizim(im, seed=5)
    c.poligon([(396, 708), (586, 708), (586, 804), (396, 804)], GRI)
    # sakal dokusu: kaynaktaki gibi küçük kıvrımlar (ağız çizgisinin çevresinde boşluk bırakılır)
    rng = random.Random(7)
    for _ in range(46):
        x, y = rng.uniform(402, 580), rng.uniform(714, 800)
        if 430 < x < 545 and 742 < y < 772:
            continue
        r = rng.uniform(5, 9)
        c.cizgi([(x - r, y), (x - r / 2, y - r * 0.8), (x + r / 2, y - r * 0.6), (x + r, y + r * 0.2)], 3, titrek=0.6)
    c.cizgi([(424, 760), (455, 754), (492, 752), (528, 754), (552, 762)], 8)
    return buyut(c.im, 1)


if __name__ == "__main__":
    g = gezgin2_sakin()
    kaydet(g, "hizmetkar_sakin")
    kaydet(hizmetkar_sok(g.copy()), "hizmetkar_sok")
    h = hannibal()
    h = h.resize((round(h.width * 1.5), round(h.height * 1.5)), Image.LANCZOS)
    kaydet(h, "hannibal_sakin")   # tur 1 görsel SHOULD: 1400'e kesilince filigran sakala biniyordu; tunik tam kalır
