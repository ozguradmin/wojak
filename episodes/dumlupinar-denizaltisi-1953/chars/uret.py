"""dumlupinar-denizaltisi-1953: hazır kıyafetli iki denizci ve ters köşe yüz varyantı.

    python episodes/dumlupinar-denizaltisi-1953/chars/uret.py

Kaynaklar (kaynak/ altında, indirildiği gibi; şeffaf kenarı kırpılmış):
  ispanyol_denizci.png wojakland "Spanish Civil War Sailor Wojak"
                       (https://wojakland.com/wp-content/grand-media/image/original/spanish_civil_war_sailor_wojak.webp),
                       1080x1169; lacivert bahriyeli yakası, şeritli denizci kepi. A (sol), er.
  subay_beyaz.png      wojakland "US navy White Wojak"
                       (https://wojakland.com/wp-content/grand-media/image/original/us_marines_white_wojak.png),
                       878x1400; klasik wojak yüzü, subay kasketi. B (sağ), astsubay/subay.
Kıyafet hazır; yalnız ülke işaretleri silinir (el kitabı §10):
  - A: kep şeridindeki "MARINA" yazısı ve kırmızı ponpon silindi (kep tepesi konturu yeniden çizildi).
  - B: ABD kartal rozeti yerine sade altın çapa; göğüs şeridi ve apolet kartalları silindi; beyaz ceket
    haki çalışma üniformasına çevrildi (gölge tonları korunarak); göğüsten kesildi (yüz büyüsün).
  - B ters köşe varyantı: subay_sok (iri göz, küçük göz bebeği, iç ucu kalkık kaş, "O" ağız, alında mavi çizgi, 3 damla).
Bakış yönü dosyanın kendisine göre kaydedilir (python -m wojak yon ...); episode.yaml'da faces: yok.
Çizim yardımcıları hierapolis-cehennem-kapisi/chars/uret.py'den kopyalandı.
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
from scipy import ndimage  # noqa: E402

MAVI = (60, 120, 230, 255)
ALTIN = (196, 156, 72, 255)


def denizci_sakin():
    im = kontur_sabitle(Image.open(KAYNAK / "ispanyol_denizci.png").convert("RGBA"))
    a = np.array(im).astype(np.int32)
    # 1) ponpon: kep tepesinin üstü saydam, kep içi kep rengiyle dolar, tepe konturu yeniden çizilir
    xs = np.array([395, 410, 430, 460, 490, 520, 550, 580, 595])
    ys = np.array([121, 112, 101, 86, 72, 60, 50, 40, 39])
    egri = lambda x: np.interp(x, xs, ys)  # noqa: E731
    for x in range(400, 592):
        yc = int(round(egri(x)))
        a[: max(0, yc - 3), x, 3] = 0
        kolon = a[yc - 3: yc + 60, x]
        kirmizi = (kolon[:, 0] > kolon[:, 2] + 25)
        kolon[kirmizi, :3] = (36, 38, 42)
        kolon[kirmizi, 3] = 255
    im = Image.fromarray(a.astype(np.uint8))
    c = Cizim(im, seed=3)
    c.cizgi([(x, float(egri(x)) - 1) for x in range(392, 600, 16)], 8)
    a = np.array(c.im).astype(np.int32)
    # 2) "MARINA" yazısı: şeridin içi (üst ve alt siyah kontur arası) sütun sütun, harf olmayan şerit
    #    piksellerinin medyan rengiyle düz boyanır; renkler yatayda yumuşatılır. Konturlar aynen kalır.
    lum = a[..., :3].mean(-1)
    xs, renk, araliklar = [], [], []
    for x in range(436, 820):
        kol = lum[100:330, x] < 14
        kos = []
        y = 0
        while y < len(kol):
            if kol[y]:
                b = y
                while y < len(kol) and kol[y]:
                    y += 1
                kos.append((100 + b, 100 + y - 1))
            y += 1
        kos = [k for k in kos if k[0] > 120]
        if len(kos) < 2:
            continue
        y0, y1 = kos[0][1] + 2, kos[1][0] - 1
        seg = a[y0:y1, x, :3]
        sl = seg.mean(-1)
        iyi = seg[(sl > 25) & (sl < 88)]
        if len(iyi) < 5:
            continue
        xs.append(x)
        renk.append(np.median(iyi, 0))
        araliklar.append((y0, y1))
    renk = np.array(renk)
    k = np.ones(31) / 31
    renk = np.stack([np.convolve(np.pad(renk[:, i], 15, mode="edge"), k, "valid") for i in range(3)], 1)
    for x, (y0, y1), r in zip(xs, araliklar, renk):
        a[y0:y1, x, :3] = r
    # 3a) sakal taraması seyreltilir: yüzdeki küçük koyu noktaların yarısı ten rengine (kontur çizgileri büyük bileşen, kalır)
    lum = a[..., :3].mean(-1)
    koyu = (lum < 110) & (a[..., 3] > 0)
    koyu[:380], koyu[740:] = False, False
    koyu[:, :440], koyu[:, 880:] = False, False
    lab, n = ndimage.label(koyu)
    alan = ndimage.sum(koyu, lab, range(1, n + 1))
    rng = np.random.default_rng(7)
    sil_ = [i + 1 for i in range(n) if alan[i] <= 30 and rng.random() < 0.5]
    m = np.isin(lab, sil_)
    m = cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    m &= (a[..., :3].min(-1) < 250) & (a[..., 3] > 0) & ~((a[..., 2] > a[..., 0] + 6) & (lum < 160))  # yalnız ten üstü
    a[m, :3] = 255
    # 3) üniformanın fırça gölgesi iki düz tona indirilir (düz MS-Paint ailesine yaklaşsın; hakem SHOULD, tur 1)
    rgb = a[..., :3]
    lum = rgb.mean(-1)
    yy = np.arange(a.shape[0])[:, None]
    uni = (a[..., 3] > 0) & (yy > 640) & (lum > 45) & (lum < 160) & (rgb[..., 2] > rgb[..., 0] + 6)
    esik = np.median(lum[uni])
    koyu, acik = uni & (lum < esik), uni & (lum >= esik)
    a[koyu, :3] = np.median(rgb[koyu], 0)
    a[acik, :3] = np.median(rgb[acik], 0)
    return Image.fromarray(a.astype(np.uint8))


def subay_temel():
    im = kontur_sabitle(Image.open(KAYNAK / "subay_beyaz.png").convert("RGBA"))
    a = np.array(im).astype(np.int32)
    # 1) ABD rozeti: siyah alan içindeki gri/altın pikseller siyaha
    x0, y0, x1, y1 = 488, 38, 668, 218
    blok = a[y0:y1, x0:x1]
    rgb = blok[..., :3]
    sat = rgb.max(-1) - rgb.min(-1)
    lum = rgb.mean(-1)
    m = (lum < 185) | ((sat > 35) & (lum < 230))   # rozet alanının tamamı (beyaz kasket hariç) düz siyah
    m &= blok[..., 3] > 0
    m &= poly_mask(im.size, [(500, 70), (530, 45), (600, 38), (640, 55), (662, 110), (650, 160), (640, 215),
                             (505, 215), (490, 150)])[y0:y1, x0:x1]
    blok[m, :3] = (22, 22, 22)
    # 2) göğüs şeridi -> ceket beyazı; apolet kartalları -> apolet siyahı
    a[815:842, 590:657, :3] = (244, 244, 244)
    for (cx, cy) in [(170, 655), (712, 688)]:
        b = a[cy - 18: cy + 18, cx - 26: cx + 26]
        s = b[..., :3].max(-1) - b[..., :3].min(-1)
        b[(s > 35) & (b[..., 3] > 0), :3] = (25, 25, 25)
    # 3) beyaz ceket -> haki (yüz/boyun bileşeni ve kasket beyazı hariç)
    rgb = a[..., :3]
    lum = rgb.mean(-1)
    sat = rgb.max(-1) - rgb.min(-1)
    acik = (lum > 150) & (sat < 25) & (a[..., 3] > 0)
    lab, n = ndimage.label(acik)
    yuz = lab[450, 560]
    kask = lab[60, 300]
    merk = ndimage.center_of_mass(acik, lab, range(1, n + 1))
    boy = ndimage.sum(acik, lab, range(1, n + 1))
    hedef = [i + 1 for i, (cy, cx) in enumerate(merk) if cy > 560 and boy[i] > 30 and (i + 1) not in (yuz, kask)]
    m = np.isin(lab, hedef)
    k = (lum[m] / 245.0)[:, None]
    a[m, :3] = np.clip(k * np.array([206, 186, 140]), 0, 255)
    im = Image.fromarray(a.astype(np.uint8))
    # 4) sade altın çapa
    c = Cizim(im, seed=5)
    cx = 577
    c.cizgi([(cx, 92), (cx, 186)], 13)
    c.cizgi([(cx, 92), (cx, 186)], 7, renk=ALTIN)
    c.elips(cx, 80, 11, 11, w=4)
    c.elips(cx, 80, 7, 7, w=3.5, renk=ALTIN)
    c.cizgi([(552, 108), (602, 108)], 12)
    c.cizgi([(552, 108), (602, 108)], 6, renk=ALTIN)
    c.cizgi([(540, 158), (548, 176), (562, 188), (577, 192), (592, 188), (606, 176), (614, 158)], 12)
    c.cizgi([(540, 158), (548, 176), (562, 188), (577, 192), (592, 188), (606, 176), (614, 158)], 6, renk=ALTIN)
    for x, d in [(540, -1), (614, 1)]:
        c.poligon([(x - 9, 160), (x + 9, 160), (x, 146)], BLACK)
        c.poligon([(x - 5, 158), (x + 5, 158), (x, 150)], ALTIN)
    return c.im.crop((0, 0, c.im.width, 1080))


def subay_sok(im):
    """Telefonun sustuğunu fark eden astsubay: iri göz, küçük göz bebeği (sağa), iç ucu kalkık kaş, O ağız."""
    # gözler, alın kırışıkları ve ağız silinir (yüz konturu x>=688 korunur)
    for b in [(428, 352, 530, 404), (594, 362, 676, 414), (510, 318, 538, 358), (586, 330, 606, 368),
              (488, 534, 622, 576)]:
        im = sil(im, kutu(*b), TEN, tol=-1)
    c = Cizim(im, seed=11)
    c.elips(478, 386, 31, 29, dolgu=WHITE, w=7)
    c.elips(636, 390, 27, 29, dolgu=WHITE, w=7)
    c.elips(486, 388, 6.5, 6.5, dolgu=BLACK)
    c.elips(643, 392, 6, 6, dolgu=BLACK)
    # iç ucu kalkık kalın kaşlar
    c.cizgi([(440, 350), (466, 344), (494, 337), (518, 330)], 9)
    c.cizgi([(600, 330), (622, 337), (648, 344), (670, 350)], 9)
    # alında mavi çizgiler (kasket siperi ile kaş arası)
    for x0, y0, x1 in [(470, 326, 505), (540, 322, 580), (596, 320, 628), (520, 334, 560), (455, 336, 480)]:
        c.cizgi([(x0, y0), ((x0 + x1) / 2, y0 - 2), (x1, y0 + 1)], 3.4, renk=MAVI)
    # O ağız
    c.elips(556, 562, 25, 29, dolgu=(70, 18, 22, 255), w=7)
    return ter(c.im, [(742, 392, 20), (752, 440, 18), (744, 488, 16)])


if __name__ == "__main__":
    kaydet(denizci_sakin(), "denizci_sakin")
    s = subay_temel()
    kaydet(s, "subay_sakin")
    kaydet(subay_sok(s.copy()), "subay_sok")
