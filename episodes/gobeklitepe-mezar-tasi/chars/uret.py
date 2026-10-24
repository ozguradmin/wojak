"""gobeklitepe-mezar-tasi: hazır kıyafetli iki karakter ve ters köşe yüz varyantı.

    python episodes/gobeklitepe-mezar-tasi/chars/uret.py

Kaynaklar (kaynak/ altında, indirildiği gibi; şeffaf kenarı kırpılmış):
  koylu_kaynak.png    wojakland "Farmer Wojak" (farmer_wojak.png,
                      https://wojakland.com/wp-content/grand-media/image/original/farmer_wojak.png), 857x918,
                      3/4 sağa bakar: hasır şapka, sakal gölgesi, ağzında başak sapı, koyu gömlek
  arkeolog_kaynak.png wojakland "Safari Wojak" (safari_wojak.png,
                      https://wojakland.com/wp-content/grand-media/image/original/safari_wojak.png), 439x457,
                      3/4 sağa bakar: mantar miğfer (kolonyal kask), haki gömlek, boyun atkısı; sırıtıp sigara içiyor
Kıyafete ve şapkalara dokunulmaz. Yapılanlar yalnız:
  - koylu_merakli = kaynağın kendisi (kontur opak);
  - arkeolog: sırıtan yüz kanalda "kötü karakter" okunur ve sigara gereksiz: kaş, göz, gülme çizgileri, ağız ve
    sigara silinip AYNI çizgi kalınlığında yeniden çizilir; sonra yatay aynalanır (B sağda, sola bakar).
      arkeolog_emin: düz kaşlar, sakin gözler (bebekler karşıdaki köylüye), kapalı hafif gülümseme
      arkeolog_terli: aynı kutu; iç uçları kalkık kaşlar, gözler köylüden kaçar, titrek ağız + ter damlaları
Bakış yönü bu betikte kaydedilmez: episode.yaml'da her karakterin `faces:` alanı var.
Çizim yardımcıları ayasofya-viking-yazisi/chars/uret.py'den kopyalandı.
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
TEN = (255, 255, 255)      # wojak beyaz yüz


def poly_mask(size, pts) -> np.ndarray:
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).polygon([tuple(p) for p in pts], fill=255)
    return np.array(m) > 0


def sil(im, pts, renk=TEN, tol=10):
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



def koylu():
    base = kontur_sabitle(Image.open(KAYNAK / "koylu_kaynak.png").convert("RGBA"))
    kaydet(base, "koylu_merakli")


def arkeolog_temel():
    """Safari Wojak (439x457), kaynak yönünde (sağa bakar). Ölçülen hatlar (px): sol göz 202-243 x 151-172,
    sağ göz 281-314 x 155-171, kaş/alın vuruşları 239-249 x 139-150 ve 274-291 x 134-154, burun 239-291 x 176-221
    (korunur), gülme çizgileri 202-240 x 202-229, ağız 226-308 x 222-246, sigara 290-353 x 227-264.
    Çizgi ~3,5-4 px."""
    im = kontur_sabitle(Image.open(KAYNAK / "arkeolog_kaynak.png").convert("RGBA"))
    im = sil(im, kutu(183, 133, 319, 176))
    im = sil(im, kutu(198, 198, 237, 233))
    im = sil(im, kutu(222, 222, 307, 249))
    # sigara: yüzün dışında kalan kısmı saydam
    a = np.array(im)
    m = poly_mask(im.size, [(309, 226), (358, 252), (358, 268), (309, 246)])
    a[m, 3] = 0
    a[248:270, 328:362, 3] = 0                       # sigara ucundan kalan noktalar
    m = poly_mask(im.size, [(304, 223), (317, 223), (309, 251), (304, 251)])
    a[m] = (255, 255, 255, 255)                      # yanak, kesilen yerde konturla birleşsin
    im = Image.fromarray(a)
    Cizim(im, seed=2).cizgi([(318, 223), (313, 236), (307, 251)], 4.0, titrek=0.2)
    return im


def kirp(im):
    """Göğüs cepleri hizasından alttan kes (y 370): aynı `height`ta yüz büyür (kanuni dersi); büst yine alttan kesik."""
    return im.crop((0, 0, im.width, 370))


def arkeolog():
    base = arkeolog_temel()
    # emin
    c = Cizim(base.copy(), seed=3)
    c.cizgi([(205, 146), (222, 142), (240, 145)], 3.8)
    c.cizgi([(282, 145), (297, 141), (313, 144)], 3.8)
    c.cizgi([(204, 162), (222, 155), (243, 160)], 3.8)
    c.cizgi([(211, 171), (236, 171)], 2.6)
    c.elips(232, 164, 5.2, 5.2, dolgu=BLACK)
    c.cizgi([(283, 161), (298, 155), (314, 160)], 3.8)
    c.cizgi([(289, 170), (310, 170)], 2.6)
    c.elips(306, 164, 4.8, 4.8, dolgu=BLACK)
    c.cizgi([(246, 233), (268, 237), (291, 232)], 3.8)
    kaydet(kirp(c.im).transpose(Image.FLIP_LEFT_RIGHT), "arkeolog_emin")
    # terli (ters köşe)
    c = Cizim(base.copy(), seed=5)
    c.cizgi([(205, 149), (222, 146), (241, 138)], 3.8)
    c.cizgi([(281, 138), (297, 145), (313, 149)], 3.8)
    c.cizgi([(204, 162), (222, 155), (243, 160)], 3.8)
    c.cizgi([(211, 171), (236, 171)], 2.6)
    c.elips(212, 164, 5.2, 5.2, dolgu=BLACK)
    c.cizgi([(283, 161), (298, 155), (314, 160)], 3.8)
    c.cizgi([(289, 170), (310, 170)], 2.6)
    c.elips(288, 164, 4.8, 4.8, dolgu=BLACK)
    c.cizgi([(246, 236), (254, 232), (262, 237), (270, 232), (278, 237), (286, 233)], 3.6)
    im = ter(c.im, [(344, 168, 11), (337, 204, 8)])
    kaydet(kirp(im).transpose(Image.FLIP_LEFT_RIGHT), "arkeolog_terli")


if __name__ == "__main__":
    koylu()
    arkeolog()
