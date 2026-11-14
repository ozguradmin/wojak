"""patrona-halil-1730: hazır kıyafetli iki karakter ve ters köşe yüz varyantı.

    python episodes/patrona-halil-1730/chars/uret.py

Kaynaklar (chars/kaynak/, indirildiği gibi; wojak_site.py get):
  muslim2_kaynak.png  wojakland "Muslim 2 Wojak" (https://wojakland.com/gmedia/muslim_2_wojak-png/), 906x1003:
                      klasik wojak yüzü, sarık, bıyık + ince çene sakalı, koyu kaftan; burun ve göz bebekleri sağa.
  muslim4_kaynak.png  wojakland "Muslim 4 Wojak" (https://wojakland.com/gmedia/muslim_4_wojak-png/), 1032x1144:
                      beyaz wojak yüzü, kürk kenarlı sarık, kızıl kahve sakal, ciddi kaşlar; göz bebekleri sağa.
                      Patrona'nın kurgu yol arkadaşı (gerçek kimseyi temsil etmez).
Tur 1'de (görsel hakem 7/10) kullanılan "Chad" profil tabanları (hezarfen/sokullu tekrarı) bırakıldı.

Yapılan (kıyafete ve ellere dokunulmaz):
  - patrona_emin: mavi sarık bağlı bölge olarak kırmızıya çevrilir (Vanmour portresinde Patrona kırmızı sarıklı; kanıt 1
    ile görsel bağ). Kaftan mavisi ayrı bölge, değişmez. Damlalar için tuval sağa 120 px genişletilir (iki varyant aynı tuval).
  - patrona_sok (A, aynı kutu): gözler ve kaşlar ten rengiyle silinip AYNI çizgi kalınlığında iri yuvarlak göz + küçük
    göz bebeği (sağa), iç ucu kalkık kalın kaş; bıyıkla çene sakalı arasındaki ağız çizgisi silinip koyu "O" ağız;
    alında 5 düzensiz mavi çizgi; başın önünde kontur dışında 3 ter damlası (el kitabı §10 tarifi).
  - patrona PNG'leri göğüsten (y 790) kesilir; yoldas_sakin göğüsten (y 900) kesilir.
"""
from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
K = HERE / "kaynak"
sys.path.insert(0, str(ROOT / "tools"))
import kit_varyant  # noqa: E402

SS = 4
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)
TEN = (235, 184, 118)
MAVI_TER = (70, 140, 230, 255)
KIRMIZI = np.array([200, 50, 38])


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
    """haydarpasa-patlamasi-1917/chars/uret.py'den (o da karakoy-tunel-1874'ten) kopya."""

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


def sil(im, box):
    """Kutudaki opak, ten olmayan pikselleri (çizgi) ten rengine boyar."""
    a = np.array(im).astype(np.int32)
    x0, y0, x1, y1 = box
    b = a[y0:y1, x0:x1]
    m = (np.abs(b[..., :3] - np.array(TEN)).sum(-1) > 12) & (b[..., 3] > 0)
    b[m, :3] = TEN
    return Image.fromarray(a.astype(np.uint8))


def agiz_sil(im, box):
    """Kutudaki ağız çizgisini siler: bıyık/sakal büyük bağlı bölge olduğu için dokunulmaz, yalnız kutuya düşen
    küçük koyu bölgeler (ağız çizgisi) ten rengine boyanır."""
    a = np.array(im).astype(np.int32)
    koyu = (a[..., :3].max(-1) < 110) & (a[..., 3] > 0)
    lab, n = ndimage.label(koyu)
    x0, y0, x1, y1 = box
    for i in np.unique(lab[y0:y1, x0:x1]):
        if i and (lab == i).sum() < 4000:
            m = ndimage.binary_dilation(lab == i, iterations=4) & (a[..., 3] > 0) & ~(koyu & (lab != i))
            a[m, :3] = TEN
    return Image.fromarray(a.astype(np.uint8))


def kirmizi_sarik(im):
    """Mavi sarık: mavimsi piksellerin (b > r + 25) üstteki (y < 420) bağlı bölgeleri; gölgeler parlaklıkla korunur."""
    a = np.array(im).astype(float)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mavi = (b > r + 25) & (a[..., 3] > 0)
    lab, n = ndimage.label(mavi)
    sarik = np.zeros_like(mavi)
    for i in range(1, n + 1):
        ys, _ = np.where(lab == i)
        if ys.mean() < 330:
            sarik |= lab == i
    lum = a[..., :3].mean(-1)
    a[sarik, :3] = KIRMIZI * np.clip(lum[sarik, None] / 175.0, 0, 1.1)
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))


def genislet(im, sag=120):
    out = Image.new("RGBA", (im.width + sag, im.height), (0, 0, 0, 0))
    out.alpha_composite(im, (0, 0))
    return out


def patrona_sok(im):
    """Hatlar (1x): sol göz 395-470 x 330-365, sağ göz 550-612 x 340-376; kaşlar y 275-300; alın çizgileri y 220-260;
    ağız çizgisi bıyık ile çene sakalı arasında 450-560 x 500-520; yüzün sağ konturu x ~650."""
    im = sil(im, (388, 268, 474, 374))
    im = sil(im, (542, 276, 618, 384))
    im = agiz_sil(im, (444, 502, 568, 533))
    c = Cizim(im, seed=23)
    c.elips(432, 344, 37, 31, dolgu=WHITE, w=8)
    c.elips(580, 356, 31, 27, dolgu=WHITE, w=8)
    c.elips(446, 349, 8, 8, dolgu=BLACK)
    c.elips(592, 360, 7, 7, dolgu=BLACK)
    c.cizgi([(390, 300), (430, 286), (466, 262)], 9)
    c.cizgi([(550, 266), (585, 280), (614, 296)], 9)
    c.elips(505, 528, 29, 35, dolgu=(90, 25, 25, 255), w=8)
    for k, (x0, y0, x1, y1) in enumerate([(430, 214, 470, 222), (482, 206, 528, 212), (540, 210, 584, 218),
                                          (452, 238, 500, 244), (520, 236, 566, 242)]):
        c.cizgi([(x0 - 6, y0), ((x0 + x1) / 2, (y0 + y1) / 2 - 5), (x1 + 6, y1)], 6.5, renk=MAVI_TER)
    return ter(c.im, [(700, 330, 20), (716, 392, 17), (702, 448, 13)])


def kaydet(im, ad):
    out = HERE / f"{ad}.png"
    im.save(out, optimize=True)
    print(f"-> {out.relative_to(ROOT)}  {im.width}x{im.height}")


if __name__ == "__main__":
    p = genislet(kirmizi_sarik(Image.open(K / "muslim2_kaynak.png").convert("RGBA")))
    p = p.crop((0, 0, p.width, 790))   # göğüsten kes: yüz yol arkadaşıyla aynı boya gelsin (el kitabı §10)
    kaydet(p, "patrona_emin")
    kaydet(patrona_sok(p.copy()), "patrona_sok")
    y = Image.open(K / "muslim4_kaynak.png").convert("RGBA")
    kaydet(y.crop((0, 0, y.width, 900)), "yoldas_sakin")
