"""kasikci-elmasi: hazır kıyafetli iki karakter ve ters köşe yüz varyantı.

    python episodes/kasikci-elmasi/chars/uret.py

Kaynaklar (kaynak/ altında, indirildiği gibi; şeffaf kenarı kırpılmış):
  bulan_kaynak.png    wojakland "Peasant Wojak" (peasant_wojak.png,
                      https://wojakland.com/wp-content/grand-media/image/original/peasant_wojak.png), 552x667,
                      klasik beyaz wojak yüzü, siyah takke, kahverengi entari; gözler sağa bakar
  kasikci_kaynak.png  wojakland "Turban 2 Chad" (turban_2_chad.png,
                      https://wojakland.com/wp-content/grand-media/image/original/turban_2_chad.png), 409x457,
                      beyaz sarık, kır sakal, mavi giysi; profilden sola bakar
Kıyafete ve başlıklara dokunulmaz. Yapılanlar:
  - kasikci_emin = kaynağın kendisi (kontur opak). B sağda, sola bakar.
  - bulan_sakin: yüzdeki üç kahverengi leke (telefonda yara/hastalık gibi okunuyor) ve alt yüzdeki gri yumuşak
    gölge (düz MS-Paint dışı) silinir; çizgiler korunur.
  - bulan_sok: aynı kutu; gözler iri, küçük göz bebekleri; iç uçları kalkık kaşlar; "O" ağız; alında mavi soğuk
    ter çizgileri + başın dışında ter damlası.
Bakış yönü bu betikte kaydedilmez: episode.yaml'da her karakterin `faces:` alanı var.
Çizim yardımcıları gobeklitepe-mezar-tasi/chars/uret.py'den kopyalandı.
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




def kasikci():
    kaydet(kontur_sabitle(Image.open(KAYNAK / "kasikci_kaynak.png").convert("RGBA")), "kasikci_emin")


def bulan_temel():
    """Peasant Wojak 552x667. Ölçülen hatlar (px): leke 1 175-262 x 128-230 (alın), leke 2 258-314 x 242-304
    (sol yanak), leke 3 398-444 x 238-266 (sağ göz altı); sol göz 272-332 x 198-238, sağ göz 388-442 x 198-238;
    ağız 315-408 x 336-350. Çizgi ~4 px."""
    im = kontur_sabitle(Image.open(KAYNAK / "bulan_kaynak.png").convert("RGBA"))
    for b in [(175, 128, 263, 231), (258, 242, 315, 305), (398, 238, 445, 267)]:
        im = sil(im, kutu(*b), tol=-1)
    a = np.array(im).astype(np.int32)
    yuz = poly_mask(im.size, kutu(125, 100, 485, 430))
    rgb = a[..., :3]
    notr = (rgb.max(-1) - rgb.min(-1) < 14) & (rgb.min(-1) >= 168) & (a[..., 3] > 0)
    m = yuz & notr
    a[m, :3] = 255
    return Image.fromarray(a.astype(np.uint8))


def bulan_sok(im):
    im = sil(im, kutu(268, 182, 336, 242), tol=-1)
    im = sil(im, kutu(384, 186, 446, 242), tol=-1)
    im = sil(im, kutu(311, 333, 413, 355), tol=-1)
    c = Cizim(im, seed=7)
    # iri gözler, küçük bebekler
    c.elips(303, 219, 25, 19, dolgu=WHITE, w=3.6)
    c.elips(417, 219, 20, 18, dolgu=WHITE, w=3.6)
    c.elips(305, 220, 4.6, 4.6, dolgu=BLACK)
    c.elips(418, 220, 4.2, 4.2, dolgu=BLACK)
    # iç uçları kalkık kaşlar
    c.cizgi([(274, 196), (300, 189), (334, 175)], 3.6)
    c.cizgi([(386, 176), (410, 186), (436, 194)], 3.6)
    # "O" ağız
    c.elips(361, 346, 10, 13, dolgu=(60, 20, 20, 255), w=3.6)
    # alında mavi soğuk ter çizgileri (düzensiz, hafif S, kancalı)
    MAVI = (70, 130, 230, 255)
    for x, y0, L, s in [(296, 126, 30, 1), (318, 122, 36, -1), (342, 124, 32, 1), (366, 127, 28, -1), (388, 131, 22, 1)]:
        c.cizgi([(x, y0), (x + 2.5 * s, y0 + L * 0.35), (x - 1.5 * s, y0 + L * 0.7), (x + 1 * s, y0 + L)], 3.0, renk=MAVI, titrek=0.5)
    return ter(c.im, [(492, 214, 9), (500, 262, 7)])


if __name__ == "__main__":
    kasikci()
    t = bulan_temel()
    s = bulan_sok(t.copy())
    # büst: entarinin altını kes (y 560), aynı height'ta yüz büyür
    kaydet(t.crop((0, 0, t.width, 560)), "bulan_sakin")
    kaydet(s.crop((0, 0, s.width, 560)), "bulan_sok")
