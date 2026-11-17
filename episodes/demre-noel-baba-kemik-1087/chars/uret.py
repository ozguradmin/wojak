"""demre-noel-baba-kemik-1087: hazır kıyafetli iki karakter ve ters köşe yüz varyantı.

    python episodes/demre-noel-baba-kemik-1087/chars/uret.py

Kaynaklar (kaynak/ altında):
  denizci3_kaynak.png  wojakland "Knight Wojak" (wl:knight_wojak.png), 504x564: burun siperli miğfer, zırh gömlek
                       (11. yy Norman/Güney İtalya). A (sol): Bari'li silahlı denizci (kurgu; adı verilmez).
  kesis_kaynak.png     HF clayshoaf/Wojaks 5_Doomer/13969 "Orthodox Doomer", 1139x1400: siyah kukuletalı keşiş, haç.
                       B (sağ): Myra'daki bekçi keşiş (kurgu).
Düzenlemeler (el kitabı §10):
  - A: 2,4x LANCZOS + UnsharpMask(2,60,2).
  - A ters köşe varyantı denizci_sok: iri göz + küçük göz bebeği (sağa), iç ucu kalkık kaş, "O" ağız, alında mavi
    çizgiler, başın önünde 3 damla.
  - B: Y biçimli gri kablo (kulaklık kablosu gibi okunuyordu) silindi, çevre renkten dolduruldu; haç kaldı.
Bakış yönü dosyanın kendisine göre kaydedilir (python -m wojak yon ...); episode.yaml'da faces: yok.
Çizim yardımcıları edirne-sarayi-1878/chars/uret.py'den kopyalandı.
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





from PIL import ImageFilter  # noqa: E402
from scipy import ndimage  # noqa: E402

MAVI = (60, 120, 230, 255)


def denizci_sakin():
    im = kontur_sabitle(Image.open(KAYNAK / "denizci3_kaynak.png").convert("RGBA"))
    return im.resize((round(im.width * 2.4), round(im.height * 2.4)), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 60, 2))


def denizci_sok(im):
    W = (255, 255, 255)
    im = sil(im, kutu(612, 572, 772, 652), W)        # sol göz
    im = sil(im, kutu(905, 585, 1022, 662), W)       # sağ göz
    im = sil(im, kutu(735, 888, 925, 930), W)        # ağız çizgisi
    c = Cizim(im, seed=7)
    c.elips(690, 628, 52, 50, dolgu=WHITE, w=8)
    c.elips(965, 632, 46, 46, dolgu=WHITE, w=8)
    c.elips(708, 632, 9, 9, dolgu=BLACK)
    c.elips(982, 636, 9, 9, dolgu=BLACK)
    c.cizgi([(630, 578), (672, 572), (712, 566), (752, 552)], 13)
    c.cizgi([(920, 566), (950, 574), (982, 580), (1010, 586)], 13)
    c.elips(830, 914, 27, 34, dolgu=(70, 18, 22, 255), w=7)
    for pts in ([(640, 556), (660, 552), (682, 556)], [(700, 552), (720, 548), (742, 552)],
                [(930, 552), (950, 548), (972, 552)], [(985, 556), (1005, 552), (1025, 557)]):
        c.cizgi(pts, 4.5, renk=MAVI)
    return ter(c.im, [(1130, 600, 17), (1145, 680, 16), (1135, 760, 15)])


def kesis():
    """Kaynaktaki Y biçimli gri kablo (kulaktan göğse; telefonda kulaklık kablosu okunuyor, görsel hakem tur 1 MUST)
    silinir: gri pikseller maskelenip çevredeki renkten (beyaz yüz, siyah cüppe, kahve yaka) doldurulur. Haç kalır."""
    import cv2
    im = kontur_sabitle(Image.open(KAYNAK / "kesis_kaynak.png").convert("RGBA"))
    a = np.array(im)
    rgb = a[..., :3].astype(int)
    gri = ((np.abs(rgb[..., 0] - rgb[..., 1]) < 18) & (np.abs(rgb[..., 1] - rgb[..., 2]) < 18)
           & (rgb[..., 0] > 110) & (rgb[..., 0] < 225) & (a[..., 3] > 0))
    kutu_m = np.zeros(gri.shape, bool)
    kutu_m[820:1265, 170:700] = True
    m = ndimage.binary_dilation(gri & kutu_m, iterations=3).astype(np.uint8) * 255
    a[..., :3] = cv2.inpaint(np.ascontiguousarray(a[..., :3]), m, 5, cv2.INPAINT_TELEA)
    return Image.fromarray(a)


if __name__ == "__main__":
    a = denizci_sakin()
    kaydet(a, "denizci_sakin")
    kaydet(denizci_sok(a.copy()), "denizci_sok")
    kaydet(kesis(), "kesis_sakin")
