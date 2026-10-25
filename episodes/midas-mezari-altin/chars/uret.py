"""midas-mezari-altin: hazır kıyafetli iki karakter ve ters köşe yüz varyantı.

    python episodes/midas-mezari-altin/chars/uret.py

Kaynaklar (kaynak/ altında, indirildiği gibi; şeffaf kenarı kırpılmış):
  madenci_kaynak.png  wojakland "Worker 2 Wojak" (worker_2_wojak.png,
                      https://wojakland.com/wp-content/grand-media/image/original/worker_2_wojak.png), 1153x1177,
                      gri kasket, bıyık + keçi sakal, bej gömlek, lacivert tulum; gözler sağa bakar
  usta_kaynak.png     wojakland "Worker Wojak" (worker_wojak.png,
                      https://wojakland.com/wp-content/grand-media/image/original/worker_wojak.png), 464x463,
                      kahverengi kasket, kirli sakal, haki ceket + çanta kayışı; gözler sağa bakar
Kıyafete ve kasketlere dokunulmaz. Yapılanlar:
  - madenci_sakin = kaynağın kendisi (kontur opak). A solda, sağa bakar.
  - madenci_sok: aynı kutu; kaşlar yukarıda ve iç uçları kalkık, gözler iri (beyaz görünür, küçük bebek), ağız
    açık "O", başın önünde (kontur dışında) ter damlaları. Yanağa mavi çizgi konmadı (telefonda gözyaşı gibi okunuyor;
    alın kasketin altında kalıyor).
  - usta_sakin: kaynak yatay aynalanır (B sağda, sola bakar). Yüz değişmez (sakin, yorgun).
Bakış yönü bu betikte kaydedilmez: episode.yaml'da her karakterin `faces:` alanı var.
Çizim yardımcıları hezarfen-galata-ucusu/chars/uret.py'den kopyalandı.
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


def madenci_temel():
    """Worker 2 Wojak 1153x1177. Ölçülen hatlar (px): sol kaş (655,285)-(760,270), sağ kaş (870,275)-(935,290);
    sol göz 672-768 x 328-372 (koyu iris 690-735), sağ göz 868-942 x 338-382; burun çizgisi x ~850 (y 395-500);
    bıyık 718-930 x 500-540; alt dudak yayı 785-855 x 548-566; keçi sakal 720-900 x 580-680; yüz sağ konturu x ~965-985.
    Çizgi ~10 px. Sağa 110 px boşluk (ter damlaları başın önüne)."""
    im = kontur_sabitle(Image.open(KAYNAK / "madenci_kaynak.png").convert("RGBA"))
    im = im.crop((0, 0, im.width, 900))        # göğüsten (tulum askıları) kesik: aynı boyda yüz büyür
    pad = Image.new("RGBA", (im.width + 110, im.height), (0, 0, 0, 0))
    pad.paste(im, (0, 0))
    return pad


def madenci_sok(im):
    # kaşlar, gözler ve alın çizgileri silinir (kasket kenarı y<250 ve burun çizgisi korunur)
    im = sil(im, kutu(640, 258, 792, 392), TEN, tol=-1)
    im = sil(im, kutu(848, 258, 956, 392), TEN, tol=-1)
    # alt dudak yayı silinir (bıyık ve keçi sakal korunur)
    im = sil(im, [(772, 542), (868, 542), (868, 576), (772, 576)], TEN, tol=-1)
    c = Cizim(im, seed=7)
    # iri gözler, bebekler sağa (B'ye) bakar
    c.elips(718, 350, 48, 38, dolgu=WHITE, w=10)
    c.elips(738, 352, 10, 10, dolgu=BLACK)
    c.elips(906, 358, 38, 32, dolgu=WHITE, w=10)
    c.elips(922, 360, 9, 9, dolgu=BLACK)
    # kaşlar: yukarıda, iç uçları (burun tarafı) kalkık
    c.cizgi([(662, 300), (712, 284), (770, 262)], 13)
    c.cizgi([(858, 266), (902, 278), (950, 302)], 12)
    # açık "O" ağız: bıyığın altında, sakalın üstünde
    c.elips(818, 570, 30, 27, dolgu=(45, 12, 12, 255), w=10)
    return ter(c.im, [(1048, 318, 40), (1092, 436, 34), (1040, 520, 26)])


def usta_temel():
    im = kontur_sabitle(Image.open(KAYNAK / "usta_kaynak.png").convert("RGBA"))
    im = im.crop((0, 0, im.width, 410))        # göğüsten kesik (madenciyle aynı oran)
    return im.transpose(Image.FLIP_LEFT_RIGHT)


if __name__ == "__main__":
    m = madenci_temel()
    kaydet(m, "madenci_sakin")
    kaydet(madenci_sok(m.copy()), "madenci_sok")
    kaydet(usta_temel(), "usta_sakin")
