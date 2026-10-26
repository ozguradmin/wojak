"""tahran-1985-ertugrul: hazır kıyafetli iki karakter ve ters köşe yüz varyantı.

    python episodes/tahran-1985-ertugrul/chars/uret.py

Kaynaklar (kaynak/ altında, wojak_site.py get ile indirildiği gibi; şeffaf kenarı kırpılmış):
  japan_business_wojak.png        wojakland "Japan Business Wojak"
                                  (https://wojakland.com/wp-content/grand-media/image/original/japan_business_wojak.png),
                                  773x829; siyah saç, kalın çerçeveli gözlük, siyah takım elbise + kravat; klasik beyaz
                                  wojak yüzü; burun ve göz bebekleri sağa
  flight_attendant_female_wojak.png  wojakland "Flight Attendant Female Wojak"
                                  (https://wojakland.com/wp-content/grand-media/image/original/flight_attendant_female_wojak.png),
                                  782x1089; topuz saç, mavi üniforma, kırmızı fular; burun sağa
Kıyafete dokunulmaz. Yapılanlar:
  - japon_endise (A, solda): kaynak, kontur opak, bel hizasından kesik; başın önünde (sağda, kontur dışında) iki ter damlası.
  - hostes_sakin (B, sağda): kaynak, göğüsten kesik. Yüz değişmez.
  - hostes_duygulu (B, aynı kutu): kaşlar silinip iç uçları kalkık "hüzünlü" kaş; göz bebeklerine iri parıltı (dolu göz);
    dış köşelerden yanağa inen mavi gözyaşı. Dudak aynı (hafif tebessüm kalır: "duygulanma", korku değil).
Bakış yönü dosyanın kendisine göre kaydedilir (python -m wojak yon ... --yon sag); episode.yaml'da faces: yok.
Çizim yardımcıları midas-mezari-altin/chars/uret.py'den kopyalandı.
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


def japon_endise():
    im = kontur_sabitle(Image.open(KAYNAK / "japan_business_wojak.png").convert("RGBA"))
    im = im.crop((0, 0, im.width, 780))
    return ter(im, [(640, 236, 22), (668, 330, 17)])


def hostes_temel():
    im = kontur_sabitle(Image.open(KAYNAK / "flight_attendant_female_wojak.png").convert("RGBA"))
    return im.crop((0, 0, im.width, 900))


def hostes_duygulu(im):
    """Ölçülen hatlar (px): sol kaş 316-430 x 218-256, sağ kaş 500-585 x 226-260; sol göz 295-415 x 270-322
    (iris merkezi ~372,302, r ~22), sağ göz 508-610 x 285-334 (iris ~546,308); dudak 420-512 x 476-512. Çizgi ~12 px."""
    im = sil(im, kutu(308, 210, 438, 262), TEN, tol=-1)
    im = sil(im, kutu(494, 220, 592, 266), TEN, tol=-1)
    c = Cizim(im, seed=11)
    # hüzünlü kaşlar: iç uçlar (burun tarafı) yukarıda
    c.cizgi([(314, 266), (340, 256), (374, 246), (432, 220)], 21)
    c.cizgi([(496, 224), (540, 244), (568, 254), (594, 266)], 20)
    # dolu gözler: iriste büyük + küçük parıltı
    c.elips(363, 295, 10, 10, dolgu=WHITE)
    c.elips(381, 311, 5, 5, dolgu=WHITE)
    c.elips(538, 301, 9, 9, dolgu=WHITE)
    c.elips(554, 315, 5, 5, dolgu=WHITE)
    tmp = HERE / "__kit_tmp.png"
    c.im.save(tmp)
    try:
        kit_varyant.make(tmp, {"tears": [
            {"path": [[312, 326], [340, 334], [372, 334], [404, 326]], "w": 10},
            {"path": [[520, 336], [548, 342], [576, 340], [600, 334]], "w": 10},
            {"path": [[318, 330], [314, 370], [312, 420], [318, 470]], "w": 22},
            {"path": [[580, 340], [580, 380], [580, 420], [574, 460]], "w": 20},
        ]}, tmp)
        return Image.open(tmp).convert("RGBA").copy()
    finally:
        tmp.unlink(missing_ok=True)


if __name__ == "__main__":
    kaydet(japon_endise(), "japon_endise")
    h = hostes_temel()
    kaydet(h, "hostes_sakin")
    kaydet(hostes_duygulu(h.copy()), "hostes_duygulu")
