"""meryem-ana-evi-1891: hazır kıyafetli iki rahip ve ters köşe yüz varyantı.

    python episodes/meryem-ana-evi-1891/chars/uret.py

Kaynaklar (kaynak/ altında, indirildiği gibi; şeffaf kenarı kırpılmış):
  a_kaynak.png  wojakland "Surprised Priest Wojak" (https://wojakland.com/gmedia/surprised_priest_wojak-png/), 485x526;
                düz MS-Paint, kel, siyah cüppe ve beyaz yaka. Videoda A: kuşkucu genç rahip (kurgu).
  b_kaynak.png  wojakland "Era Priest Wojak" (https://wojakland.com/gmedia/era_priest_wojak-png/), 953x913; ak saçlı yaşlı
                rahip, siyah cüppe. Videoda B: kitaba inanan yaşlı rahip (kurgu). Dokunulmadı (yalnız kontur sabitleme).
Kıyafete dokunulmaz. Yapılanlar:
  - a: 2x LANCZOS + UnsharpMask; hafif açık gülümseme silinip düz, kapalı ağız çizildi (a_sakin).
  - a_sok: iri yuvarlak göz + küçük göz bebeği, iç ucu kalkık kaş, alında mavi çizgiler, "O" ağız, başın önünde 3 damla.
Bakış yönü dosyanın kendisine göre kaydedilir (python -m wojak yon ...); episode.yaml'da faces: yok.
Çizim yardımcıları hierapolis-cehennem-kapisi/chars/uret.py'den kopyalandı.
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
MAVI = (60, 120, 230, 255)
KOYU = (70, 18, 22, 255)


def a_temel():
    im = kontur_sabitle(Image.open(KAYNAK / "a_kaynak.png").convert("RGBA"))
    return buyut(im, K)


def a_sakin(im):
    """1x hatlar: ağız 260-332 x 258-284 (hafif açık gülümseme) -> düz kapalı ağız."""
    im = sil(im, kutu(*S(255, 254, 337, 289)), TEN, tol=-1)
    c = Cizim(im, seed=5)
    c.cizgi([tuple(S(266, 271)), tuple(S(284, 268)), tuple(S(306, 268)), tuple(S(326, 272))], 4.2 * K)
    return c.im


def a_sok(im):
    """1x hatlar: sol göz 225-270 x 147-168, sağ göz 325-360 x 152-173, kaşlar y 117-128, alın çizgileri
    200-345 x 77-108, ağız 260-332 x 258-284; baş konturu sağda x ~370-382."""
    for b in [(210, 108, 275, 177), (313, 108, 369, 181), (196, 70, 352, 111), (255, 254, 337, 289)]:
        im = sil(im, kutu(*S(*b)), TEN, tol=-1)
    c = Cizim(im, seed=13)
    # iri yuvarlak gözler + küçük göz bebeği (dosyanın baktığı yöne, sağa)
    c.elips(*S(245, 157, 25, 23), dolgu=WHITE, w=4.2 * K)
    c.elips(*S(342, 161, 21, 23), dolgu=WHITE, w=4.2 * K)
    c.elips(*S(251, 158, 5.0, 5.0), dolgu=BLACK)
    c.elips(*S(348, 162, 4.6, 4.6), dolgu=BLACK)
    # iç ucu kalkık kaşlar
    c.cizgi([tuple(S(214, 124)), tuple(S(232, 120)), tuple(S(250, 114)), tuple(S(268, 105))], 4.4 * K)
    c.cizgi([tuple(S(318, 105)), tuple(S(334, 112)), tuple(S(350, 118)), tuple(S(366, 122))], 4.4 * K)
    # alında düzensiz mavi çizgiler
    for x0, y0, x1, dy in [(222, 80, 262, -2), (276, 78, 330, 1.5), (236, 92, 290, 2), (300, 94, 342, -1.5),
                           (214, 101, 246, 1)]:
        c.cizgi([tuple(S(x0, y0)), tuple(S((x0 + x1) / 2, y0 + dy)), tuple(S(x1, y0 + dy * 0.3))], 2.4 * K, renk=MAVI)
    # "O" ağız
    c.elips(*S(296, 272, 13, 16), dolgu=KOYU, w=4.0 * K)
    return ter(c.im, [tuple(S(400, 120, 9)), tuple(S(410, 160, 8.5)), tuple(S(403, 200, 7.5))])


def b_sakin():
    return kontur_sabitle(Image.open(KAYNAK / "b_kaynak.png").convert("RGBA"))


if __name__ == "__main__":
    a = a_temel()
    kaydet(a_sakin(a.copy()), "a_sakin")
    kaydet(a_sok(a.copy()), "a_sok")
    kaydet(b_sakin(), "b_sakin")
