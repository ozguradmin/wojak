"""karun-hazinesi-bros: hazır kıyafetli iki karakter ve ters köşe yüz varyantı.

    python episodes/karun-hazinesi-bros/chars/uret.py

Kaynaklar (kaynak/ altında, indirildiği gibi; şeffaf kenarı kırpılmış):
  mufettis_kaynak.png  wojakland "Grey Suit Wojak" (https://wojakland.com/gmedia/grey_suit_wojak-png/)
  mudur_kaynak.png     HF clayshoaf/Wojaks 5_Doomer/13657 "Brownic Office Doomer Wojak, 2000-2010"
Kıyafete, gövdeye, saça dokunulmaz. Yapılanlar yalnız:
  - müdür: göz altı mor tonu ve pembe göz akı düz renkle temizlenir (çizgiler kalır);
  - müfettiş "sok": kaş, göz ve ağız silinip AYNI çizgi kalınlığında, kenarı sert yeniden çizilir (kalkık kaşlar,
    iri açık gözler, küçük açık ağız) + kanalın kit dilinde ter damlaları (tools/kit_varyant.py).
Bakış yönü bu betikte kaydedilmez (data/ dışına yazılmaz): episode.yaml'da her karakterin `faces:` alanı var.
Çizim yardımcıları uzun/talidomit-turkiye/chars/hazir_uret.py'den kopyalandı (aynı çizgi dili).
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


def sil(im, pts, renk=(255, 255, 255), tol=10):
    a = np.array(im).astype(np.int32)
    m = poly_mask(im.size, pts)
    d = np.abs(a[..., :3] - np.array(renk)).sum(-1)
    m &= (d > tol) & (a[..., 3] > 0)
    a[m, :3] = renk
    return Image.fromarray(a.astype(np.uint8))


def kutu(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def elips_pts(cx, cy, rx, ry, n=48):
    return [(cx + rx * math.cos(2 * math.pi * k / n), cy + ry * math.sin(2 * math.pi * k / n)) for k in range(n)]


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

    def cizgi(self, pts, w, renk=BLACK, titrek=0.5):
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


def acik_gozler(c, gozler, w):
    for cx, cy, rx, ry, px, pr in gozler:
        c.elips(cx, cy, rx, ry, dolgu=WHITE, w=w)
        c.cizgi([(cx - rx * 0.97, cy - ry * 0.10), (cx - rx * 0.62, cy - ry * 0.80), (cx, cy - ry * 1.0),
                 (cx + rx * 0.62, cy - ry * 0.80), (cx + rx * 0.97, cy - ry * 0.10)], w + 3, titrek=0.3)
        c.elips(px, cy + 1, pr, pr, dolgu=BLACK)


def ter(im, damlalar):
    tmp = HERE / "__kit_tmp.png"
    im.save(tmp)
    try:
        kit_varyant.make(tmp, {"drops": [list(d) for d in damlalar]}, tmp)
        return Image.open(tmp).convert("RGBA").copy()
    finally:
        tmp.unlink(missing_ok=True)


def kaydet(im, ad):
    out = HERE / f"{ad}.png"
    im.save(out, optimize=True)
    print(f"-> {out.relative_to(ROOT)}  {im.width}x{im.height}")


def mufettis():
    """Grey Suit Wojak (900x870), 3/4 sağa bakar. Yüz hatları (px): sol kaş (452-557, 228-248) + kırışık (557-572,
    252-275); sağ kaş (595-725, 228-255) + kırışık (603-612, 258-280); sol göz (465-563, 287-330); sağ göz (622-748,
    295-345); ağız (537-670, 502-524); alın kırışıkları y 160-210. Çizgi ~6-7 px."""
    base = Image.open(KAYNAK / "mufettis_kaynak.png").convert("RGBA")
    kaydet(base, "mufettis_sakin")
    W = 7
    im = base.copy()
    # alttaki alın kırışığı (420-668, 186-214) da silinir: kalkık kaşlar onun yerine oturur (üstüne binmesin)
    kirisik = [(422, 212), (450, 210), (475, 206), (500, 197), (530, 186), (560, 188), (580, 195), (600, 200),
               (650, 202), (668, 208)]
    bant = [(x, y - 10) for x, y in kirisik] + [(x, y + 10) for x, y in reversed(kirisik)]
    for p in (bant, kutu(422, 206, 668, 216), kutu(445, 216, 580, 282), kutu(592, 220, 752, 284),
              kutu(455, 278, 575, 346), kutu(616, 276, 752, 350), kutu(528, 494, 680, 532)):
        im = sil(im, p)
    c = Cizim(im, seed=7)
    c.cizgi([(452, 222), (478, 202), (514, 191), (548, 194), (566, 206)], W + 1)
    c.cizgi([(644, 220), (670, 203), (704, 197), (736, 210)], W + 1)
    acik_gozler(c, [(512, 312, 46, 32, 533, 12), (694, 322, 35, 27, 712, 11)], W)
    c.elips(606, 516, 19, 24, dolgu=(45, 30, 30, 255), w=W)
    im = ter(c.im, [(420, 262, 17), (752, 240, 14)])
    kaydet(im, "mufettis_sok")


def mudur():
    """HF 5_Doomer/13657 (504x544), 3/4 sağa bakar: gözlük, bıyık, lacivert takım. Göz altı mor tonu (257-414,
    197-214) ve pembe göz akı beyaza: kişi yorgun-bitkin değil, kendinden emin okunsun (çizgiler aynen kalır)."""
    a = np.array(Image.open(KAYNAK / "mudur_kaynak.png").convert("RGBA")).astype(np.int32)
    r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    bolge = poly_mask((a.shape[1], a.shape[0]), kutu(220, 170, 440, 235))
    mor = bolge & (al > 0) & (r - g > 8) & (b - g > 8)
    gri = np.clip(g * 255.0 / 205.0, 0, 255).astype(np.int32)
    for ch in range(3):
        a[..., ch][mor] = gri[mor]
    pembe = bolge & (al > 0) & (r - g > 12) & (np.abs(g - b) < 18) & (r > 180)
    a[pembe, :3] = 255
    im = Image.fromarray(a.astype(np.uint8))
    # camların içi (yorgun göz + göz altı çizgileri) silinir; çerçeve ve burun pedleri kalır. Yerine sakin, uyanık
    # klasik gözler (müfettişin taban yüzüyle aynı dil, bu çizimin ~4 px çizgisinde)
    for p in (elips_pts(274, 207, 36, 26), elips_pts(395, 209, 30, 23), kutu(239, 184, 250, 195)):
        im = sil(im, p)
    c = Cizim(im, seed=11)
    for (x0, x1, y, px, pr) in ((259, 306, 194, 291, 6.5), (371, 410, 198, 399, 5.5)):
        c.cizgi([(x0, y + 2), (x0 + (x1 - x0) * 0.3, y - 2), (x0 + (x1 - x0) * 0.7, y - 2), (x1, y + 1)], 5)
        c.cizgi([(x0 + 5, y + 10), (x0 + (x1 - x0) * 0.5, y + 12), (x1 - 4, y + 9)], 3)
        c.elips(px, y + 5, pr * 0.85, pr, dolgu=BLACK)
    kaydet(c.im, "mudur_sakin")


if __name__ == "__main__":
    mufettis()
    mudur()
