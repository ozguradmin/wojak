"""ayasofya-viking-yazisi: hazır kıyafetli iki karakter ve ters köşe yüz varyantı.

    python episodes/ayasofya-viking-yazisi/chars/uret.py

Kaynaklar (kaynak/ altında, indirildiği gibi; şeffaf kenarı kırpılmış):
  viking_kaynak.png   wojakland "Viking Wojak" (viking_wojak_1.png,
                      https://wojakland.com/wp-content/grand-media/image/original/viking_wojak_1.png), 1167x1047,
                      sağa bakar: miğfer, sakal, kürk pelerin, sırtında kılıç
  muhafiz_kaynak.png  wojakland "Byzantine Knight Wojak" (byzantine_knight_wojak.png,
                      https://wojakland.com/wp-content/grand-media/image/original/byzantine_knight_wojak.png), 460x471,
                      sola bakar: burun siperli miğfer, zincir başlık, bordo zırh
Kıyafete ve miğfere dokunulmaz. Yapılanlar yalnız:
  - viking = kaynağın kendisi (sıkılmış/huysuz yüz); yarı saydam kontur opak yapılır;
  - muhafız "sakin" = kaynağın kendisi (ciddi, kaşları çatık);
  - muhafız "sok": kaşlar, gözler ve ağız çizgisi silinip AYNI çizgi kalınlığında yeniden çizilir (kalkık kaşlar,
    iri açık gözler, küçük göz bebekleri karşıdaki Viking'e bakar, zincir başlığın üstünde açık "O" ağız) + iki
    yanakta ter damlası (tools/kit_varyant.py). Miğfer alnı kapattığı için mavi soğuk ter çizgisi yok.
Bakış yönü bu betikte kaydedilmez (data/ dışına yazılmaz): episode.yaml'da her karakterin `faces:` alanı var.
Çizim yardımcıları kanuni-gizlenen-olum/chars/uret.py'den kopyalandı.
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
TEN = (235, 182, 138)      # muhafızın ten rengi (ölçüldü)
ZINCIR = (90, 90, 90)      # ağız çevresindeki zincir başlık tonu (ölçüldü)


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


def viking():
    base = kontur_sabitle(Image.open(KAYNAK / "viking_kaynak.png").convert("RGBA"))
    kaydet(base, "viking_sikkin")


def muhafiz():
    """Byzantine Knight (460x471), 3/4 sola bakar. Yüz hatları (px): ten alanı sol yanak x 192-276, sağ yanak
    x 318-366, y 197-285 (üstü miğfer kenarı y~195, arası burun siperi x 277-316). Sol göz (212-260, 218-238), sağ
    göz (317-343, 223-245), kaş vuruşları sol (255-268, 200-212) ve sağ (337-343, 199-203). Ağız çizgisi zincir
    başlıkta (260-315, 300-305). Çizgi ~3-4 px."""
    base = Image.open(KAYNAK / "muhafiz_kaynak.png").convert("RGBA")
    kaydet(base, "muhafiz_sakin")
    im = base.copy()
    im = sil(im, kutu(196, 198, 272, 252))
    im = sil(im, kutu(318, 198, 364, 252))
    im = sil(im, kutu(254, 298, 322, 307), renk=ZINCIR)
    c = Cizim(im, seed=7)
    # şaşkın/korkmuş kaşlar: iç uçlar (burun siperine yakın) yukarıda, kemerli
    c.cizgi([(203, 214), (222, 206), (246, 202), (266, 200)], 4.2)
    c.cizgi([(322, 200), (340, 202), (354, 207), (363, 213)], 4.0)
    # iri açık gözler: beyaz dolgu + kontur; küçük göz bebekleri sola (karşıdaki Viking'e)
    for cx, cy, rx, ry, px, pr in ((236, 230, 18, 15, 228, 3.6), (342, 232, 14, 14, 335, 3.4)):
        c.elips(cx, cy, rx, ry, dolgu=WHITE, w=3.6)
        c.elips(px, cy + 1, pr, pr, dolgu=BLACK)
    # açık "O" ağız (zincir başlığın üstünde)
    c.elips(289, 307, 12, 13, dolgu=(25, 18, 18, 255), w=3.6)
    im = ter(c.im, [(204, 262, 9), (361, 257, 8)])
    kaydet(im, "muhafiz_sok")


if __name__ == "__main__":
    viking()
    muhafiz()
