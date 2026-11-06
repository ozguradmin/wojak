"""catalhoyuk-sekinin-alti: hazır kıyafetli iki Neolitik köylü ve ters köşe yüz varyantı.

    python episodes/catalhoyuk-sekinin-alti/chars/uret.py

Kaynaklar (kaynak/ altında, indirildiği gibi; şeffaf kenarı kırpılmış):
  fat_grug.png          HF clayshoaf/Wojaks 5_Grug/12770 "Fat Grug", 1024x953; leopar desenli post (Çatalhöyük
                        duvar resimlerindeki leopar postu giyen figürlerle uyumlu). A (sol), yaşlı akraba.
  tired_neanderthal.png HF clayshoaf/Wojaks 5_Grug/12827 "Tired Neanderthals", 645x450; uzun saç, sakal,
                        yorgun/üzgün göz. B (sağ), babası ölen genç.
Kıyafet hazır; düzenlemeler (el kitabı §10):
  - B: gözün üstünden geçen kırmızı yara çizgisi silindi (cv2.inpaint); 3x LANCZOS + UnsharpMask(2,60,2);
    büyütmede bulanıklaşan mor torbalı gözler silinip temiz çizgiyle yarı kapalı üzgün göz ve kaş çizildi;
    yüz büyüsün diye boyundan kesildi (y 1200).
  - B ters köşe varyantı: genc_sok (iri göz, küçük göz bebeği, iç ucu kalkık kaş, sakal içinde "O" ağız, 3 damla).
    Alın saçla kapalı olduğu için mavi alın çizgileri saç ile kaş arasındaki dar şeride kondu.
Bakış yönü dosyanın kendisine göre kaydedilir (python -m wojak yon ...); episode.yaml'da faces: yok.
Çizim yardımcıları dumlupinar-denizaltisi-1953/chars/uret.py'den kopyalandı.
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
import cv2  # noqa: E402
from PIL import ImageFilter  # noqa: E402

MAVI = (60, 120, 230, 255)
SAKAL = (63, 34, 16, 255)


def yasli_sakin():
    im = kontur_sabitle(Image.open(KAYNAK / "fat_grug.png").convert("RGBA"))
    return im


def genc_temel():
    im = Image.open(KAYNAK / "tired_neanderthal.png").convert("RGBA")
    a = np.array(im)
    r, g, b = [a[..., i].astype(int) for i in range(3)]
    # kırmızı yara çizgisi: yalnız göz çevresindeki kutuda, kırmızı baskın pikseller
    m = np.zeros(r.shape, bool)
    m[125:255, 255:325] = True
    m &= (r > g + 45) & (r > b + 15) & (a[..., 3] > 0)
    m = cv2.dilate(m.astype(np.uint8), np.ones((5, 5), np.uint8))
    rgb = cv2.inpaint(np.ascontiguousarray(a[..., :3]), m, 4, cv2.INPAINT_TELEA)
    a[..., :3] = rgb
    im = Image.fromarray(a)
    im = im.resize((im.width * 3, im.height * 3), Image.LANCZOS)
    rgb = im.convert("RGB").filter(ImageFilter.UnsharpMask(2, 60, 2))
    im = Image.merge("RGBA", (*rgb.split(), im.split()[3]))
    a = np.array(kontur_sabitle(im)).astype(np.int32)
    acik = (a[..., :3].min(-1) > 200) & (a[..., 3] > 0)
    a[acik, :3] = 255   # büyütmenin bıraktığı açık gri ten gölgesi düz beyaz
    im = Image.fromarray(a.astype(np.uint8))
    # büyütmeden bulanık kalan mor torbalı gözler silinir, aynı çizgi kalınlığında temiz yorgun/üzgün göz çizilir
    im = gozleri_sil(im)
    c = Cizim(im, seed=7)
    for cx, cy, rx, ix, ir in [(955, 598, 66, 978, 30), (1513, 602, 56, 1532, 27)]:
        c.elips(cx, cy + 6, rx, 38, dolgu=WHITE)
        c.elips(ix, cy + 12, ir, ir, dolgu=BLACK)
        # yarı kapalı üst kapak: kapak çizgisinin üstü ten rengi, dış köşe aşağı düşük
        c.poligon([(cx - rx - 6, cy - 70), (cx + rx + 6, cy - 70), (cx + rx + 6, cy - 14), (cx, cy - 10),
                   (cx - rx - 6, cy + 6)], WHITE)
        c.cizgi([(cx - rx - 4, cy + 8), (cx - rx / 2, cy - 6), (cx, cy - 11), (cx + rx / 2, cy - 12), (cx + rx + 4, cy - 10)], 14)
        c.cizgi([(cx - rx + 6, cy + 42), (cx, cy + 48), (cx + rx - 6, cy + 40)], 8)
    # iç ucu hafif kalkık üzgün kaşlar
    c.cizgi([(865, 512), (920, 506), (975, 498), (1030, 486)], 13)
    c.cizgi([(1445, 486), (1485, 494), (1525, 502), (1568, 508)], 13)
    return c.im.crop((0, 0, c.im.width, 1200))


def gozleri_sil(im):
    """Göz bölgesinde saç/sakal kahvesi olmayan pikseller beyaza (saç kenarı ve burun korunur)."""
    a = np.array(im).astype(np.int32)
    for x0, y0, x1, y1 in [(722, 452, 1025, 700), (1025, 452, 1095, 600), (1425, 462, 1582, 700)]:
        blok = a[y0:y1, x0:x1]
        kahve = (blok[..., 0] - blok[..., 2] > 25) & (blok[..., 0] > 35) & (blok[..., 0] < 140)
        blok[~kahve & (blok[..., 3] > 0), :3] = 255
    # sağ gözün çevresindeki gri büyütme artıkları (siyah kontur ve kırışık çizgisi korunur)
    blok = a[452:700, 1405:1600]
    gri = (blok[..., :3].mean(-1) > 90) & (blok[..., 3] > 0)
    gri &= ~((blok[..., 0] - blok[..., 2] > 25) & (blok[..., 0] < 140))
    blok[gri, :3] = 255
    for x0, y0, x1, y1 in [(1405, 455, 1425, 560), (1575, 480, 1593, 600)]:   # yarım kalan kırışık parçaları
        blok = a[y0:y1, x0:x1]
        blok[(blok[..., 3] > 0) & ~((blok[..., 0] - blok[..., 2] > 25) & (blok[..., 0] < 140)), :3] = 255
    return Image.fromarray(a.astype(np.uint8))


def genc_sok(im):
    """Yıllardır atalarının üstünde uyuduğunu fark eden genç: iri göz, küçük göz bebeği (sağa), kalkık kaş, O ağız."""
    # gözler (torbalarıyla) silinir
    im = gozleri_sil(im)
    # ağız: beyaz ağız boşluğu ve konturu sakal rengine (blok sakalın içinde)
    a = np.array(im).astype(np.int32)
    blok = a[775:925, 960:1410]
    cevre = a[730:960, 900:1470]
    kahve = (cevre[..., 0] - cevre[..., 2] > 25) & (cevre[..., 3] > 0) & (cevre[..., 0] < 140)
    blok[blok[..., 3] > 0, :3] = np.median(cevre[kahve][:, :3], 0)   # sakalın kendi rengi (yama kalmasın)
    im = Image.fromarray(a.astype(np.uint8))
    c = Cizim(im, seed=11)
    c.elips(955, 585, 84, 80, dolgu=WHITE, w=13)
    c.elips(1515, 590, 70, 78, dolgu=WHITE, w=13)
    c.elips(980, 590, 14, 14, dolgu=BLACK)
    c.elips(1535, 595, 13, 13, dolgu=BLACK)
    # iç ucu kalkık kalın kaşlar (saç ile göz arası)
    c.cizgi([(865, 492), (920, 482), (975, 470), (1035, 452)], 15)
    c.cizgi([(1440, 455), (1480, 466), (1525, 476), (1570, 486)], 15)
    # O ağız (sakalın içinde)
    c.elips(1185, 852, 56, 62, dolgu=(70, 18, 22, 255), w=11)
    return ter(c.im, [(1690, 470, 24), (1705, 560, 22), (1695, 650, 20)])


if __name__ == "__main__":
    kaydet(yasli_sakin(), "yasli_sakin")
    g = genc_temel()
    kaydet(g, "genc_uzgun")
    kaydet(genc_sok(g.copy()), "genc_sok")
