"""edirne-sarayi-1878: hazır kıyafetli iki Osmanlı askeri ve ters köşe yüz varyantı.

    python episodes/edirne-sarayi-1878/chars/uret.py

Kaynaklar (kaynak/ altında):
  goeben_osmanli_sakin.png  episodes/goeben-fes-1914/chars/osmanli_sakin.png (HF clayshoaf/Wojaks 5_Twinkjak/15359
                            "Twinjak Ottoman", 2x büyütülmüş, sırıtışı silinmiş). A (sol), er.
  pasa_doomer.png           HF clayshoaf/Wojaks 5_Doomer/13926, 516x476: fes, apoletli siyah üniforma. B (sağ), adsız paşa.
Düzenlemeler (el kitabı §10):
  - A: haki yeşil ceket (1909 sonrası renk) 1877-78 Osmanlı piyadesinin lacivert ceketine boyandı (bağlı bölge).
  - A ters köşe varyantı asker_sok: iri göz + küçük göz bebeği (sağa), iç ucu kalkık kaş, "O" ağız, alında mavi
    çizgiler, başın önünde 3 damla.
  - B: 2x LANCZOS + UnsharpMask(2,60,2).
Bakış yönü dosyanın kendisine göre kaydedilir (python -m wojak yon ...); episode.yaml'da faces: yok.
Çizim yardımcıları catalhoyuk-sekinin-alti/chars/uret.py'den kopyalandı.
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
LACIVERT = np.array([28, 36, 72])


def asker_sakin():
    im = Image.open(KAYNAK / "goeben_osmanli_sakin.png").convert("RGBA")
    a = np.array(im).astype(np.int32)
    r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    yesil = (al > 0) & (g > r + 3) & (g > b + 3) & (g < 200)
    lab, n = ndimage.label(ndimage.binary_dilation(yesil, iterations=1))
    buyuk = [i for i in range(1, n + 1) if (lab == i).sum() > 400]
    m = np.isin(lab, buyuk) & yesil
    # gölge tonunu koru: parlaklık oranıyla lacivert
    parl = (g[m] / max(1, g[m].max()))[:, None]
    a[m, :3] = np.clip(LACIVERT[None, :] * (0.55 + 0.9 * parl), 0, 255).astype(np.int32)
    return Image.fromarray(a.astype(np.uint8))


def asker_sok(im):
    W = (255, 255, 255)
    im = sil(im, kutu(315, 333, 478, 385), W)        # sol kaş
    im = sil(im, kutu(498, 330, 615, 368), W)        # sağ kaş
    im = sil(im, kutu(338, 385, 448, 463), W)        # sol göz
    im = sil(im, kutu(512, 388, 610, 460), W)        # sağ göz
    im = sil(im, kutu(428, 576, 522, 597), W)        # ağız çizgisi
    c = Cizim(im, seed=7)
    c.elips(395, 422, 47, 45, dolgu=WHITE, w=7)
    c.elips(561, 422, 43, 43, dolgu=WHITE, w=7)
    c.elips(410, 424, 8, 8, dolgu=BLACK)
    c.elips(576, 424, 8, 8, dolgu=BLACK)
    c.cizgi([(328, 376), (370, 368), (410, 358), (446, 341)], 14)
    c.cizgi([(516, 340), (550, 352), (582, 360), (612, 368)], 14)
    c.elips(477, 610, 19, 25, dolgu=(70, 18, 22, 255), w=6)
    for pts in ([(452, 330), (470, 326), (490, 329)], [(500, 324), (520, 320), (540, 324)],
                [(550, 320), (568, 316), (586, 319)], [(400, 334), (418, 331), (436, 334)]):
        c.cizgi(pts, 4, renk=MAVI)
    return ter(c.im, [(672, 372, 15), (684, 436, 14), (676, 500, 13)])


def pasa():
    im = kontur_sabitle(Image.open(KAYNAK / "pasa_doomer.png").convert("RGBA"))
    im = im.resize((im.width * 2, im.height * 2), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 60, 2))
    # gözlük camı: renkli cam tonu ve çapraz yansıma şeritleri düz ten rengine, gri iris düz siyaha (düz MS-Paint ailesi)
    a = np.array(im).astype(np.int32)
    blk = a[480:530, 600:660].reshape(-1, 4)
    ten = np.median(blk[blk[:, 3] == 255][:, :3], 0)
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    for (x0, y0, x1, y1), (cx, cy, rx, ry) in [((478, 362, 596, 444), (548, 398, 46, 22)),
                                               ((676, 372, 786, 444), (720, 404, 42, 20))]:
        kutu_m = (xx >= x0) & (xx < x1) & (yy >= y0) & (yy < y1)
        goz = kutu_m & (((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1)
        rgb = a[..., :3]
        mx, mn = rgb.max(-1), rgb.min(-1)
        koyu = rgb.sum(-1) < 220
        beyaz = (mn > 205) & (mx - mn < 30)
        gri = ~koyu & ~beyaz & (mx - mn < 25) & (mx < 200)
        rgb[kutu_m & ~goz & ~koyu] = ten
        rgb[goz & beyaz] = 255
        rgb[goz & gri] = 25
        rgb[goz & ~koyu & ~beyaz & ~gri & (mx - mn >= 30)] = ten
        rgb[goz & ~koyu & ~beyaz & ~gri & (mx - mn < 30)] = 255
    im = Image.fromarray(a.astype(np.uint8))
    c = Cizim(im, seed=3)
    c.elips(554, 396, 12, 12, dolgu=BLACK)
    c.elips(724, 402, 11, 11, dolgu=BLACK)
    return c.im


if __name__ == "__main__":
    a = asker_sakin()
    kaydet(a, "asker_sakin")
    kaydet(asker_sok(a.copy()), "asker_sok")
    kaydet(pasa(), "pasa")
