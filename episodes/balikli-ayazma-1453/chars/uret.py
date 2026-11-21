"""balikli-ayazma-1453: hazır kıyafetli iki karakter ve ters köşe yüz varyantı.

    python episodes/balikli-ayazma-1453/chars/uret.py

Kaynaklar (kaynak/ altında):
  kesis_kaynak.png  HF clayshoaf/Wojaks 5_Bloomer/3585 "Patriach Bloomer", 1014x1400: siyah kalimavki ve örtü, uzun gri
                    sakal. A (sol): ayazmada balık kızartan yaşlı keşiş (efsanedeki adsız keşiş; kurgu).
  genc_kesis_kaynak.png  HF clayshoaf/Wojaks 5_Doomer/13969 "Orthodox Doomer", 1139x1400: siyah kukuletalı keşiş, kahve
                    sakal, haç. B (sağ): haberi getiren öteki keşiş (De Amicis s. 258 "another monk"; kurgu). Tur 1 görsel
                    MUST: önceki B (wl:byzantine_knight_wojak) gölgeli/degrade ve 11-12. yy miğferli olduğu için çıkarıldı.
Düzenlemeler (el kitabı §10):
  - A sakin: bloomer sırıtması (açık ağız) sakal grisiyle (195) silindi, sakal içine kısa düz ağız çizildi.
    PNG sakalın ortasından (y 1040) kesildi: yüz büyür.
  - A ters köşe varyantı kesis_sok: iri yuvarlak göz + küçük göz bebeği (sağa), iç ucu kalkık kalın kaş, sakal içinde
    "O" ağız, alında mavi çizgiler, başın önünde 3 damla.
  - B: Y biçimli gri kablo silindi (demre-noel-baba-kemik-1087 ile aynı tarif); kahve sakal koyu kır sakala çevrildi,
    PNG göğüsten (y 1200) kesildi; tur 2 SHOULD: kaşlar iç ucu kalkık (endişeli) yeniden çizildi, bıyık altına hafif açık
    ağız, kukuletanın tırtıklı dış kenarı alfa yumuşatmasıyla düzeltildi.
Bakış yönü dosyanın kendisine göre kaydedilir (python -m wojak yon ...); episode.yaml'da faces: yok.
Çizim yardımcıları demre-noel-baba-kemik-1087/chars/uret.py'den kopyalandı.
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

MAVI = (60, 120, 230, 255)
SAKAL = (195, 195, 195)
DERI = (235, 182, 138)
W3 = (255, 255, 255)


def kesis_taban():
    im = kontur_sabitle(Image.open(KAYNAK / "kesis_kaynak.png").convert("RGBA"))
    im = sil(im, kutu(398, 752, 612, 880), SAKAL)                 # sırıtan ağız (çizgiler dahil)
    im = sil(im, [(345, 752), (398, 744), (398, 800), (345, 800)], SAKAL)   # sol bıyık ucu
    return im


def kesis_sakin(im):
    c = Cizim(im, seed=3)
    c.cizgi([(448, 806), (490, 810), (532, 806)], 10)
    return c.im.crop((0, 0, im.width, 1040))


def kesis_sok(im):
    # kaşlar, gözler ve alın kırışığı silinir (yüz konturuna değmeden)
    im = sil(im, [(330, 478), (480, 478), (480, 625), (330, 625)], W3)
    im = sil(im, [(540, 478), (650, 478), (650, 600), (640, 625), (540, 625)], W3)
    c = Cizim(im, seed=11)
    c.elips(415, 585, 44, 42, dolgu=WHITE, w=9)
    c.elips(608, 592, 36, 38, dolgu=WHITE, w=9)
    c.elips(432, 590, 9, 9, dolgu=BLACK)
    c.elips(624, 596, 8, 8, dolgu=BLACK)
    c.cizgi([(352, 548), (392, 538), (430, 526), (462, 508)], 13)      # sol kaş, iç ucu (burna yakın) kalkık
    c.cizgi([(566, 512), (596, 526), (626, 536), (648, 544)], 13)      # sağ kaş
    c.elips(482, 814, 42, 48, dolgu=(48, 12, 16, 255), w=10)           # "O" ağız
    c.elips(482, 840, 24, 13, dolgu=(205, 95, 105, 255))                # dil
    for pts in ([(372, 488), (392, 484), (414, 488)], [(430, 482), (452, 478), (474, 482)],
                [(560, 482), (582, 478), (604, 482)], [(616, 488), (636, 484), (656, 489)]):
        c.cizgi(pts, 4.5, renk=MAVI)
    im = ter(c.im, [(790, 520, 17), (812, 600, 16), (800, 680, 15)])
    return im.crop((0, 0, im.width, 1040))


def genc_kesis():
    """B: kaynaktaki Y biçimli gri kablo (telefonda kulaklık kablosu okunuyor) silinir: gri pikseller maskelenip çevredeki
    renkten (beyaz yüz, siyah cüppe, kahve yaka) doldurulur; haç kalır (demre-noel-baba-kemik-1087/chars/uret.py kesis())."""
    import cv2
    from scipy import ndimage
    im = kontur_sabitle(Image.open(KAYNAK / "genc_kesis_kaynak.png").convert("RGBA"))
    a = np.array(im)
    rgb = a[..., :3].astype(int)
    gri = ((np.abs(rgb[..., 0] - rgb[..., 1]) < 18) & (np.abs(rgb[..., 1] - rgb[..., 2]) < 18)
           & (rgb[..., 0] > 110) & (rgb[..., 0] < 225) & (a[..., 3] > 0))
    kutu_m = np.zeros(gri.shape, bool)
    kutu_m[820:1265, 170:700] = True
    m = ndimage.binary_dilation(gri & kutu_m, iterations=3).astype(np.uint8) * 255
    a[..., :3] = cv2.inpaint(np.ascontiguousarray(a[..., :3]), m, 5, cv2.INPAINT_TELEA)
    # demre'deki keşişten ayrılsın diye kahve sakal koyu kır sakala çevrilir (kenar yumuşatması dahil, oran korunarak)
    rgb = a[..., :3].astype(float)
    d = np.abs(rgb - np.array([59, 18, 3])).sum(-1)
    sakal = (d < 60) & (a[..., 3] > 0)
    sakal[:480] = False
    sakal[960:] = False
    t = np.clip(rgb[..., 0] / 59.0, 0, 1.6)[..., None]
    a[..., :3] = np.where(sakal[..., None], np.clip(np.array([92, 88, 86]) * t, 0, 255), rgb).astype(np.uint8)
    im = Image.fromarray(a)
    # tur 2 görsel SHOULD: "şehir düştü" diyen haberci kaşı kalkık, yarı sırıtır görünüyordu -> endişeli yüz:
    # iki kaş silinip iç uçları kalkık çizilir, bıyık altına hafif açık ağız
    im = sil(im, kutu(410, 380, 588, 440), W3)
    im = sil(im, [(652, 402), (700, 384), (742, 386), (796, 418), (796, 450), (652, 426)], W3)
    c = Cizim(im, seed=21)
    c.cizgi([(428, 438), (470, 428), (515, 414), (566, 396)], 15)
    c.cizgi([(668, 398), (712, 410), (752, 424), (790, 440)], 15)
    c.elips(612, 752, 52, 15, dolgu=(48, 12, 16, 255), w=7)
    im = c.im
    # tur 2 görsel SHOULD: kukuletanın tırtıklı dış kenarı yumuşatılır (yalnız alfa)
    al = im.getchannel("A").filter(ImageFilter.GaussianBlur(1.6)).point(lambda v: 0 if v < 40 else (255 if v > 215 else round((v - 40) * 255 / 175)))
    im.putalpha(al)
    return im.crop((0, 0, im.width, 1200))


if __name__ == "__main__":
    t = kesis_taban()
    kaydet(kesis_sakin(t.copy()), "kesis_sakin")
    kaydet(kesis_sok(t.copy()), "kesis_sok")
    kaydet(genc_kesis(), "genc_kesis_sakin")
