"""haydarpasa-patlamasi-1917: hazır kıyafetli iki karakter ve ters köşe yüz varyantı.

    python episodes/haydarpasa-patlamasi-1917/chars/uret.py

Kaynaklar:
  kaynak/asker_wl.png  wojakland "Ottoman Wwi Wojak" (wl:ottoman_wwi_wojak.png, 788x884, şeffaf): haki kabalak (Enveriye)
                       + haki üniforma, kahve bıyık, klasik beyaz yüz; burun ve göz bebekleri sağa. 1917 Osmanlı eri.
  memur_sakin.png      episodes/karakoy-tunel-1874/chars/memur_sakin.png'nin kopyası (5_Crying_Wojak/438'den; fes, kır saç,
                       koyu takım): gar memuru.
Kıyafete dokunulmaz. asker_sok (A, aynı kutu): gözler silinip iri yuvarlak göz + küçük göz bebeği (sağa), bıyığın altındaki
ağız çizgisi silinip "O" ağız, başın önünde (kontur dışında) üç ter damlası; damlalar için tuval sağa 125 px genişletildi
(sakin varyant da aynı tuvalde, kutu aynı kalsın). Alın kabalağın altında kaldığı için alın çizgisi yok.
Çizim yardımcıları karakoy-tunel-1874/chars/uret.py'den kopyalandı.
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








def genislet(im, sag=125):
    out = Image.new("RGBA", (im.width + sag, im.height), (0, 0, 0, 0))
    out.alpha_composite(im, (0, 0))
    return out


def agiz_sil(im, b):
    """Kutudaki siyah ağız çizgisini beyaza çevirir; bıyığın kahvesine 5 px'ten yakın koyu kontura dokunmaz."""
    from scipy import ndimage
    a = np.array(im).astype(np.int32)
    x0, y0, x1, y1 = b
    rgb = a[..., :3]
    kahve = ((rgb.max(-1) - rgb.min(-1)) >= 30) & (rgb.sum(-1) < 300) & (a[..., 3] > 0)
    yakin = ndimage.binary_dilation(kahve, iterations=5)
    siyah = ((rgb.max(-1) - rgb.min(-1)) < 30) & (rgb.sum(-1) < 750) & (a[..., 3] > 0)
    m = np.zeros(siyah.shape, bool)
    m[y0:y1, x0:x1] = True
    m &= siyah & ~yakin
    a[m, :3] = 255
    return Image.fromarray(a.astype(np.uint8))


def asker_sok(im):
    """Hatlar (asker_wl 1x): sol göz 385-482 x 422-468, sağ göz 597-672 x 435-482; kabalak siperi y ~410-425;
    bıyık 397-672 x 615-660; ağız çizgisi 455-615 x 655-688; çene alt konturu y ~760; yüzün sağ konturu x ~700-725."""
    im = sil(im, kutu(380, 431, 488, 474), TEN, tol=-1)
    im = sil(im, kutu(592, 436, 678, 488), TEN, tol=-1)
    im = agiz_sil(im, (440, 650, 630, 700))
    im = siyah_sil(im, (384, 419, 486, 432), esik=760)
    c = Cizim(im, seed=17)
    c.elips(433, 459, 41, 30, dolgu=WHITE, w=10)
    c.elips(638, 465, 35, 28, dolgu=WHITE, w=10)
    c.elips(450, 463, 9, 9, dolgu=BLACK)
    c.elips(654, 469, 8.5, 8.5, dolgu=BLACK)
    c.elips(543, 704, 23, 27, dolgu=(95, 30, 30, 255), w=9)
    return ter(c.im, [(786, 452, 22), (800, 512, 18), (788, 567, 14)])


if __name__ == "__main__":
    import shutil
    asker = kontur_sabitle(Image.open(KAYNAK / "asker_wl.png").convert("RGBA"))
    asker = genislet(asker)
    kaydet(asker, "asker_sakin")
    kaydet(asker_sok(asker.copy()), "asker_sok")
    shutil.copy(ROOT / "episodes/karakoy-tunel-1874/chars/memur_sakin.png", HERE / "memur_sakin.png")
    print("-> memur_sakin.png kopyalandı")
