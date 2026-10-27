"""orban-topu-bizans: hazır kıyafetli iki karakter ve ters köşe yüz varyantı.

    python episodes/orban-topu-bizans/chars/uret.py

Kaynaklar (kaynak/ altında, wojak_site.py get ile indirildiği gibi; şeffaf kenarı kırpılmış):
  usta_kaynak.png       wojakland "Medieval Man" (https://wojakland.com/wp-content/grand-media/image/original/Medieval_Man.png),
                        575x565; kır saçlı, yaşlı klasik beyaz wojak yüzü, gri zırh gömleği + deri kayış; göz bebekleri sağa
  imparator_kaynak.png  wojakland "Roman Emperor Wojak" (https://wojakland.com/wp-content/grand-media/image/original/roman_emperor_wojak.png),
                        568x552; altın taç, kırmızı pelerin, zırh; klasik beyaz yüz; burun ve göz bebekleri sağa
Kıyafete dokunulmaz. Yapılanlar:
  - usta_sakin (A, solda, Orban): 2x büyütme (LANCZOS + hafif keskinleştirme). Yüz değişmez.
  - imparator_sakin (B, sağda, XI. Konstantinos): 2x büyütme; hafif gülümseyen ağız silinip yerine düz, uçları hafif aşağı
    çizgi (para yok diyen, üzgün ama sevecen imparator; kanalda sırıtma "kötü" okunur).
  - imparator_sok (B, aynı kutu): kaşlar, gözler, ağız silinip iri yuvarlak göz + küçük göz bebeği, kalkık kaş, "O" ağız;
    başın önünde (kontur dışında) üç ter damlası.
Bakış yönü dosyanın kendisine göre kaydedilir (python -m wojak yon ... --yon sag); episode.yaml'da faces: yok.
Çizim yardımcıları yerebatan-bodrum-balik/chars/uret.py'den kopyalandı.
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




def usta_sakin():
    im = kontur_sabitle(Image.open(KAYNAK / "usta_kaynak.png").convert("RGBA"))
    return buyut(im, 2)


def imparator_temel():
    im = kontur_sabitle(Image.open(KAYNAK / "imparator_kaynak.png").convert("RGBA"))
    return buyut(im, 2)


K = 2
S = lambda *v: [x * K for x in v]  # noqa: E731


def imparator_sakin(im):
    """1x hatlar: ağız (kırmızı ince gülümseme) 303-362 x 295-305."""
    im = sil(im, kutu(*S(298, 290, 367, 310)), TEN, tol=-1)
    c = Cizim(im, seed=5)
    c.cizgi([tuple(S(308, 300)), tuple(S(322, 298)), tuple(S(343, 298)), tuple(S(358, 302))], 4.5 * K)
    return c.im


def imparator_sok(im):
    """1x hatlar: sol kaş 262-308 x 165-176 (+ iç kırışık 312-318 x 178-188), sağ kaş 352-388 x 167-178 (+ dikey 353-357 x
    182-192); sol göz 267-310 x 195-213, sağ göz 358-390 x 199-218; ağız 303-362 x 295-305. Taç bandının alt kenarı
    sol kaşın üstünde y ~163. Çizgi ~4,5 px (2x'te 9)."""
    for b in [(258, 164, 322, 192), (348, 165, 394, 195), (262, 190, 315, 218), (354, 194, 396, 223), (298, 290, 367, 310)]:
        im = sil(im, kutu(*S(*b)), TEN, tol=-1)
    c = Cizim(im, seed=9)
    # iri yuvarlak gözler + küçük göz bebeği (bakılan yöne, sağa)
    c.elips(*S(288, 204, 23, 21), dolgu=WHITE, w=4.5 * K)
    c.elips(*S(374, 208, 17, 20), dolgu=WHITE, w=4.5 * K)
    c.elips(*S(292, 205, 5, 5), dolgu=BLACK)
    c.elips(*S(378, 209, 4.5, 4.5), dolgu=BLACK)
    # kalkık kaşlar
    c.cizgi([tuple(S(265, 184)), tuple(S(278, 173)), tuple(S(296, 169)), tuple(S(313, 175))], 4.5 * K)
    c.cizgi([tuple(S(353, 177)), tuple(S(366, 168)), tuple(S(382, 167)), tuple(S(396, 175))], 4.5 * K)
    # "O" ağız: koyu iç + siyah kontur
    c.elips(*S(334, 302, 12, 16), dolgu=(70, 18, 22, 255), w=4 * K)
    return ter(c.im, [tuple(S(434, 212, 17)), tuple(S(450, 258, 14)), tuple(S(440, 302, 11))])


if __name__ == "__main__":
    kaydet(usta_sakin(), "usta_sakin")
    t = imparator_temel()
    kaydet(imparator_sakin(t.copy()), "imparator_sakin")
    kaydet(imparator_sok(t.copy()), "imparator_sok")
