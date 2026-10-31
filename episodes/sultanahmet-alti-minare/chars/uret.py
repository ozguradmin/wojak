"""sultanahmet-alti-minare: hazır kıyafetli iki karakter ve ters köşe yüz varyantı.

    python episodes/sultanahmet-alti-minare/chars/uret.py

Kaynaklar (kaynak/ altında, indirildiği gibi):
  aga_kaynak.png   wojakland "Sultan Chad" (sultan_chad_2.png,
                   https://wojakland.com/wp-content/grand-media/image/original/sultan_chad_2.png), 842x1036,
                   beyaz kavuk (kırmızı tepe), kahverengi sakal, kırmızı kaftan yakası; profilden sola bakar
  usta_kaynak.png  wojakland "Peasant Wojak" (peasant_wojak.png,
                   https://wojakland.com/wp-content/grand-media/image/original/peasant_wojak.png), 552x667,
                   klasik beyaz wojak yüzü, siyah takke, kahverengi entari; gözler sağa bakar
Kıyafete ve başlıklara dokunulmaz. Yapılanlar:
  - aga_sakin: kaynağın kendisi (kontur opak), boynun altından kesilir (yüz büyür).
  - usta_sakin / usta_sok: kasikci-elmasi/chars/uret.py'deki tarif (lekeler silinir; şokta iri göz, küçük bebek,
    kalkık kaş, "O" ağız, alında 6 mavi çizgi, başın önünde 3 damla); gri yüz çizgileri koyulaştırılıp ~1 px
    kalınlaştırılır (cizgi_koyulastir; tur 1 SHOULD).
Bakış yönü: python -m wojak yon ... ile kaydedilir (aga: sol, usta: sag).
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






def cizgi_koyulastir(im, boyut=3, gama=0.55):
    """Gri ve ince yüz çizgilerini koyulaştırıp ~1 px kalınlaştırır (hakem tur 1 SHOULD: talidomit v2 çizgi ağırlığı).
    Yalnız nötr (gri/beyaz/siyah) ve opak pikseller: entari, mavi ter çizgileri ve damlalar etkilenmez."""
    from PIL import ImageFilter
    a = np.array(im).astype(np.float32)
    rgb, al = a[..., :3], a[..., 3]
    notr = (rgb.max(-1) - rgb.min(-1) < 20) & (al > 0)
    v0 = rgb.min(-1)
    d = np.where(notr & (v0 < 185), (255 - v0) / 255, 0)    # silik gri benekler (eski leke izleri) beyaza döner
    dm = Image.fromarray((d * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(boyut))
    d2 = (np.array(dm).astype(np.float32) / 255) ** gama
    d2 = np.maximum(d2, d)
    v = 255 * (1 - d2)
    for k in range(3):
        a[..., k] = np.where(notr, v, a[..., k])
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))


def aga():
    im = kontur_sabitle(Image.open(KAYNAK / "aga_kaynak.png").convert("RGBA"))
    kaydet(im.crop((0, 0, im.width, 1000)), "aga_sakin")


def usta_temel():
    """Peasant Wojak 552x667 (kasikci-elmasi ile aynı ölçüler)."""
    im = kontur_sabitle(Image.open(KAYNAK / "usta_kaynak.png").convert("RGBA"))
    for b in [(175, 128, 263, 231), (258, 242, 315, 305), (398, 238, 445, 267)]:
        im = sil(im, kutu(*b), tol=-1)
    a = np.array(im).astype(np.int32)
    yuz = poly_mask(im.size, kutu(125, 100, 485, 430))
    rgb = a[..., :3]
    notr = (rgb.max(-1) - rgb.min(-1) < 14) & (rgb.min(-1) >= 168) & (a[..., 3] > 0)
    m = yuz & notr
    a[m, :3] = 255
    return Image.fromarray(a.astype(np.uint8))


def usta_sok(im):
    im = sil(im, kutu(268, 182, 336, 242), tol=-1)
    im = sil(im, kutu(384, 186, 446, 242), tol=-1)
    im = sil(im, kutu(311, 333, 413, 355), tol=-1)
    c = Cizim(im, seed=7)
    c.elips(303, 219, 25, 19, dolgu=WHITE, w=3.6)
    c.elips(417, 219, 20, 18, dolgu=WHITE, w=3.6)
    c.elips(305, 220, 4.6, 4.6, dolgu=BLACK)
    c.elips(418, 220, 4.2, 4.2, dolgu=BLACK)
    c.cizgi([(274, 196), (300, 189), (334, 175)], 3.6)
    c.cizgi([(386, 176), (410, 186), (436, 194)], 3.6)
    c.elips(361, 346, 10, 13, dolgu=(60, 20, 20, 255), w=3.6)
    MAVI = (70, 130, 230, 255)
    for x, y0, L, s in [(296, 126, 30, 1), (318, 122, 36, -1), (342, 124, 32, 1), (366, 127, 28, -1), (388, 131, 22, 1)]:
        c.cizgi([(x, y0), (x + 2.5 * s, y0 + L * 0.35), (x - 1.5 * s, y0 + L * 0.7), (x + 1 * s, y0 + L)], 3.0, renk=MAVI, titrek=0.5)
    # tur 1 SHOULD: alında 6. çizgi ve üçüncü damla (yüz değişimi eşikten yukarı)
    c.cizgi([(408, 136), (410.5, 142), (406.5, 148), (409, 154)], 3.0, renk=MAVI, titrek=0.5)
    return ter(c.im, [(492, 214, 9), (500, 262, 7), (508, 168, 7)])


if __name__ == "__main__":
    aga()
    t = usta_temel()
    s = usta_sok(t.copy())
    kaydet(cizgi_koyulastir(t).crop((0, 0, t.width, 560)), "usta_sakin")
    kaydet(cizgi_koyulastir(s).crop((0, 0, s.width, 560)), "usta_sok")
