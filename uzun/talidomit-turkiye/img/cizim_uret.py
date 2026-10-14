"""uzun/talidomit-turkiye: kendi düz (MS-Paint) çizimlerimiz ve dokularımız. Hepsi bu betikle üretilir; dış kaynak yok
(tek istisna: talidomit formülü, Commons'taki kamu malı SVG'nin PNG'si -> molekül çizimleri).

    python uzun/talidomit-turkiye/img/cizim_uret.py              # hepsi -> img/cizim/
    python uzun/talidomit-turkiye/img/cizim_uret.py gazete kapi  # yalnız bazıları

Kurallar (senaryo §E, kanal kuralları): gerçek firma adı/logosu yok, gerçek gazete/dergi adı ya da logosu yok, kişi/bebek/
hasta yok. Yazılar yalnız belgeli olgular ya da genel etiketler. Çizgi ~8-10 px siyah, düz dolgu, hafif titrek kenar.
Saydam PNG'ler nesnedir (motorda foto/manşet/üst katman olarak), JPG'ler 2560x1440 zemindir.
"""
from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = HERE / "cizim"
SS = 3
BLACK = (0, 0, 0, 255)


def font(ad: str, size: int) -> ImageFont.FreeTypeFont:
    cands = {
        "serif": ["/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
                  "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf", str(ROOT / "assets/fonts/Anton-Regular.ttf")],
        "serif_r": ["/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
                    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", str(ROOT / "assets/fonts/Poppins-Bold.ttf")],
        "anton": [str(ROOT / "assets/fonts/Anton-Regular.ttf")],
        "poppins": [str(ROOT / "assets/fonts/Poppins-Bold.ttf")],
        "mono": [str(ROOT / "assets/fonts/LiberationMono-Bold.ttf")],
    }[ad]
    for c in cands:
        if Path(c).exists():
            return ImageFont.truetype(c, size)
    raise FileNotFoundError(ad)


# ------------------------------------------------------------------------------------------------ çizim yardımcıları
def catmull(pts, n=12, closed=False):
    P = list(pts)
    P = ([P[-1]] + P + [P[0], P[1]]) if closed else ([P[0]] + P + [P[-1]])
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    if not closed:
        out.append(P[-2])
    return out


def wob(pts, amp=0.7, seed=1):
    r = random.Random(seed)
    ph = r.random() * 6
    return [(x + amp * math.sin(i * 0.37 + ph) + r.uniform(-0.3, 0.3),
             y + amp * math.cos(i * 0.29 + ph) + r.uniform(-0.3, 0.3)) for i, (x, y) in enumerate(pts)]


def dens(pts, step=14):
    """Düz çokgen kenarlarını sık noktalara böler (titrek çizgi için)."""
    out = []
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        n = max(1, int(math.hypot(x1 - x0, y1 - y0) / step))
        out += [(x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n) for i in range(n)]
    out.append(pts[-1])
    return out


class Tuval:
    def __init__(self, w, h, bg=(0, 0, 0, 0)):
        self.w, self.h = w, h
        self.im = Image.new("RGBA", (w * SS, h * SS), bg)
        self.d = ImageDraw.Draw(self.im)
        self.seed = 1

    def _s(self):
        self.seed += 1
        return self.seed

    def P(self, pts):
        return [(x * SS, y * SS) for x, y in pts]

    def line(self, pts, w=8, fill=BLACK, smooth=False, closed=False, amp=0.7):
        p = list(pts) + (list(pts[:1]) if closed else [])
        p = catmull(p, 10) if smooth and len(p) > 2 else dens(p)
        if amp:
            p = wob(p, amp, self._s())
        q = self.P(p)
        self.d.line(q, fill=fill, width=round(w * SS), joint="curve")
        r = w * SS / 2
        for x, y in (q[0], q[-1]):
            self.d.ellipse([x - r, y - r, x + r, y + r], fill=fill)

    def shape(self, pts, fill, w=8, smooth=False, outline=BLACK, amp=0.6):
        p = catmull(pts, 10, True) if smooth else list(pts)
        self.d.polygon(self.P(p), fill=fill)
        if outline and w:
            self.line(p, w=w, fill=outline, closed=True, amp=amp)

    def ellipse(self, cx, cy, rx, ry, fill=None, outline=BLACK, w=8):
        self.d.ellipse([(cx - rx) * SS, (cy - ry) * SS, (cx + rx) * SS, (cy + ry) * SS], fill=fill,
                       outline=outline, width=round(w * SS) if outline else 0)

    def rect(self, x0, y0, x1, y1, fill, w=8, outline=BLACK):
        self.shape([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], fill, w=w, outline=outline)

    def text(self, xy, s, fnt, fill=(20, 20, 20, 255), anchor="la", angle=0):
        f = font(fnt[0], fnt[1] * SS)
        if not angle:
            self.d.text((xy[0] * SS, xy[1] * SS), s, font=f, fill=fill, anchor=anchor)
            return
        tmp = Image.new("RGBA", self.im.size, (0, 0, 0, 0))
        ImageDraw.Draw(tmp).text((xy[0] * SS, xy[1] * SS), s, font=f, fill=fill, anchor=anchor)
        tmp = tmp.rotate(angle, center=(xy[0] * SS, xy[1] * SS), resample=Image.BICUBIC)
        self.im.alpha_composite(tmp)

    def text_box(self, s, fnt, xy, anchor="la"):
        f = font(fnt[0], fnt[1] * SS)
        b = self.d.textbbox((xy[0] * SS, xy[1] * SS), s, font=f, anchor=anchor)
        return tuple(round(v / SS) for v in b)

    def done(self):
        return self.im.resize((self.w, self.h), Image.LANCZOS)


def kaydet(im: Image.Image, ad: str, trim=True):
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / ad
    if p.suffix == ".png":
        if trim:
            bb = im.getchannel("A").point(lambda v: 255 if v > 4 else 0).getbbox()
            pad = 6
            im = im.crop((max(0, bb[0] - pad), max(0, bb[1] - pad), min(im.width, bb[2] + pad), min(im.height, bb[3] + pad)))
        im.save(p, optimize=True)
    else:
        im.convert("RGB").save(p, quality=82 if "mantar" in ad else 90, optimize=True)
    print(f"cizim/{ad} {im.size}")
    return im


GREY_TXT = (128, 128, 128, 255)


def yazi_satirlari(t: Tuval, x0, x1, y0, n, gap=30, w=9, renk=(150, 150, 150, 255), kisa_son=True, seed=0):
    r = random.Random(seed)
    for j in range(n):
        y = y0 + j * gap
        xe = x1 - (r.randint(80, 220) if (kisa_son and j == n - 1) else r.randint(0, 30))
        t.line([(x0, y), (xe, y)], w=w, fill=renk, amp=0)


# ------------------------------------------------------------------------------------------------ nesneler
def tablet(r=60):
    t = Tuval(2 * r + 40, 2 * r + 40)
    c = r + 20
    t.ellipse(c, c, r, r, fill=(250, 250, 248, 255), w=7)
    t.line([(c - r * 0.62, c), (c + r * 0.62, c)], w=5, fill=(170, 170, 170, 255), amp=0)   # çentik
    t.ellipse(c - r * 0.35, c - r * 0.45, r * 0.18, r * 0.1, fill=(255, 255, 255, 255), outline=None)
    return t.done()


def numune_kutusu():
    """Adsız beyaz ilaç/numune kutusu (yazı, logo yok; yalnız mavi şerit)."""
    t = Tuval(1000, 760)
    front = [(90, 300), (690, 300), (690, 660), (90, 660)]
    top = [(90, 300), (250, 170), (850, 170), (690, 300)]
    side = [(690, 300), (850, 170), (850, 530), (690, 660)]
    t.shape(top, (232, 232, 226, 255))
    t.shape(side, (208, 208, 202, 255))
    t.shape(front, (246, 246, 242, 255))
    blue = (84, 132, 196, 255)
    t.shape([(92, 420), (688, 420), (688, 500), (92, 500)], blue, w=0, outline=None)
    t.shape([(692, 420), (848, 292), (848, 370), (692, 500)], (70, 112, 170, 255), w=0, outline=None)
    t.line(front, w=8, closed=True)
    t.line(side, w=8, closed=True)
    # kapak dili
    t.line([(250, 170), (210, 120), (790, 120), (850, 170)], w=7)
    return t.done()


def numune_tabletler():
    box = numune_kutusu()
    tb = tablet(58)
    c = Image.new("RGBA", (1300, 800), (0, 0, 0, 0))
    c.alpha_composite(box, (0, 30))
    c.alpha_composite(tb, (980, 600))
    c.alpha_composite(tb.rotate(30, resample=Image.BICUBIC, expand=False), (1130, 640))
    return c


def fare_kafesi():
    t = Tuval(1200, 820)
    # taban tepsisi
    t.shape([(80, 640), (1120, 640), (1080, 760), (120, 760)], (180, 180, 186, 255))
    # tel kafes
    for x in range(110, 1100, 52):
        t.line([(x, 640), (x, 250)], w=5, fill=(90, 90, 96, 255), amp=0)
    t.line([(100, 250), (1100, 250)], w=9)
    t.line([(100, 640), (1100, 640)], w=9)
    t.line([(100, 250), (100, 640)], w=9)
    t.line([(1100, 250), (1100, 640)], w=9)
    t.line([(100, 250), (300, 150), (900, 150), (1100, 250)], w=9)
    for x in range(330, 900, 70):
        t.line([(x, 150), (x - 40, 250)], w=4, fill=(110, 110, 116, 255), amp=0)
    # fareler (gri, düz)
    for cx, cy, s, flip in ((330, 580, 1.0, 1), (640, 595, 0.9, -1), (900, 575, 1.05, 1)):
        g = (150, 150, 156, 255)
        t.ellipse(cx, cy, 80 * s, 46 * s, fill=g, w=7)
        hx = cx + flip * 82 * s
        t.ellipse(hx, cy - 14 * s, 36 * s, 30 * s, fill=g, w=7)
        t.ellipse(hx - flip * 16 * s, cy - 44 * s, 18 * s, 18 * s, fill=(232, 170, 180, 255), w=6)
        t.ellipse(hx + flip * 14 * s, cy - 20 * s, 6 * s, 6 * s, fill=BLACK, outline=None)
        t.line([(cx - flip * 78 * s, cy + 6), (cx - flip * 130 * s, cy - 20 * s), (cx - flip * 170 * s, cy + 10 * s)],
               w=6, smooth=True, fill=(200, 140, 150, 255))
    return t.done()


def doz_sisesi():
    """Adsız kahverengi ilaç şişesi (etiketi boş). Kevadon yedeği de bu."""
    t = Tuval(560, 900)
    t.shape([(150, 120), (410, 120), (410, 230), (150, 230)], (240, 240, 236, 255))           # kapak
    for x in range(170, 400, 26):
        t.line([(x, 132), (x, 218)], w=3, fill=(190, 190, 186, 255), amp=0)
    t.shape([(170, 230), (390, 230), (400, 290), (160, 290)], (120, 62, 24, 255))            # boyun
    body = [(160, 290), (400, 290), (470, 360), (470, 820), (440, 860), (120, 860), (90, 820), (90, 360)]
    t.shape(body, (138, 72, 26, 255))
    t.shape([(110, 450), (450, 450), (450, 720), (110, 720)], (244, 240, 226, 255), w=7)      # boş etiket
    yazi_satirlari(t, 150, 410, 520, 4, gap=46, w=10, renk=(180, 176, 166, 255), seed=4)
    t.line([(130, 380), (140, 800)], w=14, fill=(196, 132, 80, 160), amp=0)                    # parlama
    return t.done()


def molekul(src: Path):
    """Kamu malı talidomit formülü (siyah, beyaz zemin) -> beyaz ve siyah çizgili saydam PNG."""
    im = Image.open(src).convert("L")
    a = 255 - np.array(im)
    a = np.clip(a.astype(np.int32) * 1.15, 0, 255).astype(np.uint8)
    beyaz = Image.new("RGBA", im.size, (255, 255, 255, 0))
    beyaz.putalpha(Image.fromarray(a))
    siyah = Image.new("RGBA", im.size, (20, 20, 20, 0))
    siyah.putalpha(Image.fromarray(a))
    return beyaz, siyah


def cereblon():
    """Cereblon proteini şeması: cebi olan yumuşak mor kütle (yalnız simge, ölçekli model değil)."""
    t = Tuval(900, 760)
    pts = [(120, 380), (160, 220), (300, 120), (480, 110), (640, 160), (760, 280), (790, 420), (730, 560),
           (600, 640), (560, 560), (600, 470), (560, 380), (470, 360), (420, 420), (440, 520), (380, 640),
           (220, 620), (130, 520)]
    t.shape(pts, (150, 112, 196, 255), w=9, smooth=True)
    t.line([(250, 260), (330, 210), (420, 205)], w=6, smooth=True, fill=(190, 160, 226, 255))
    return t.done()


def sall4(kirik=False):
    # 2. hakem turu: açık yeşil üstünde koyu yazı (eskiden yeşil üstünde açık gri yazı telefonda okunmuyordu)
    t = Tuval(820, 420)
    green = (150, 214, 160, 255)
    ink = (14, 40, 22, 255)
    if not kirik:
        t.shape([(60, 70), (760, 60), (770, 350), (50, 360)], green, w=9)
        t.text((410, 210), "SALL4", ("anton", 160), fill=ink, anchor="mm")
        return t.done()
    pieces = [[(60, 70), (300, 64), (250, 200), (320, 356), (50, 360)],
              [(300, 64), (540, 62), (480, 210), (560, 352), (320, 356), (250, 200)],
              [(540, 62), (760, 60), (770, 350), (560, 352), (480, 210)]]
    for i, p in enumerate(pieces):
        dx, dy, ang = [(-40, 18, 0), (0, 40, 0), (46, 10, 0)][i]
        t.shape([(x + dx, y + dy) for x, y in p], green, w=9)
    t.text((410 - 30, 250), "SALL4", ("anton", 160), fill=ink, anchor="mm")
    return t.done()


def zarlar():
    """7. tur (kapanış çağrısı, 'ŞANS' seçeneği): iki düz çizim zar (numune kutusuyla aynı küp çizimi, siyah kontur,
    fildişi yüzler, siyah noktalar). Yazı/logo yok."""
    t = Tuval(1180, 820)

    def zar(x, y, a, d, on_nokta, ust_nokta, yan_nokta):
        # x, y: ön yüzün sol üst köşesi; a: ön yüz kenarı; d: derinlik (üst/yan yüzün kayması)
        front = [(x, y), (x + a, y), (x + a, y + a), (x, y + a)]
        top = [(x, y), (x + d, y - d * 0.8), (x + a + d, y - d * 0.8), (x + a, y)]
        side = [(x + a, y), (x + a + d, y - d * 0.8), (x + a + d, y + a - d * 0.8), (x + a, y + a)]
        t.shape(top, (236, 230, 214, 255))
        t.shape(side, (206, 198, 180, 255))
        t.shape(front, (250, 246, 234, 255))
        t.line(front, w=8, closed=True)
        t.line(side, w=8, closed=True)
        t.line(top, w=8, closed=True)
        r = a * 0.085
        for u, v in on_nokta:      # ön yüz: yuvarlak noktalar (0..1 yüz koordinatı)
            t.ellipse(x + u * a, y + v * a, r, r, fill=(18, 18, 18, 255), outline=None)
        for u, v in ust_nokta:     # üst yüz: basık (perspektif)
            cx = x + u * a + v * d
            cy = y - v * d * 0.8
            t.ellipse(cx, cy, r * 0.95, r * 0.5, fill=(18, 18, 18, 255), outline=None)
        for u, v in yan_nokta:     # yan yüz: dar
            cx = x + a + u * d
            cy = y + v * a - u * d * 0.8
            t.ellipse(cx, cy, r * 0.5, r * 0.9, fill=(18, 18, 18, 255), outline=None)

    bes = [(0.25, 0.25), (0.75, 0.25), (0.5, 0.5), (0.25, 0.75), (0.75, 0.75)]
    uc_yan = [(0.25, 0.25), (0.5, 0.5), (0.75, 0.75)]
    zar(90, 300, 440, 170, bes, [(0.5, 0.5)], uc_yan)
    iki = [(0.27, 0.27), (0.73, 0.73)]
    alti_ust = [(0.27, 0.25), (0.27, 0.5), (0.27, 0.75), (0.73, 0.25), (0.73, 0.5), (0.73, 0.75)]
    zar(720, 420, 300, 120, iki, alti_ust, [(0.5, 0.5)])
    return t.done()


def sall4_cift():
    """7. tur (animasyon B9): sağlam ve kırık SALL4 aynı tuvalde (motor aynı tuvaldeki yüzleri ortak kutuyla kırpar;
    ayrı tuvalde kırılma anında nesne ~%2 büyüyüp kayıyordu)."""
    a, b = sall4(False), sall4(True)
    kutu = None
    for im in (a, b):
        bb = im.getchannel("A").point(lambda v: 255 if v > 4 else 0).getbbox()
        kutu = bb if kutu is None else (min(kutu[0], bb[0]), min(kutu[1], bb[1]), max(kutu[2], bb[2]), max(kutu[3], bb[3]))
    pad = 6
    kutu = (max(0, kutu[0] - pad), max(0, kutu[1] - pad), min(a.width, kutu[2] + pad), min(a.height, kutu[3] + pad))
    return a.crop(kutu), b.crop(kutu)


def kapi(acik: bool):
    """Düz çizim kapı (kasa + kanat). acik: kanat içeri açık, arkası karanlık."""
    t = Tuval(700, 1100)
    wood, dark = (150, 98, 58, 255), (120, 76, 44, 255)
    t.shape([(80, 60), (620, 60), (620, 1060), (80, 1060)], (96, 62, 36, 255), w=9)          # kasa
    if acik:
        t.shape([(120, 100), (580, 100), (580, 1060), (120, 1060)], (24, 22, 26, 255), w=6)  # karanlık boşluk
        t.shape([(120, 100), (250, 150), (250, 1010), (120, 1060)], wood, w=8)                # kanat (kenardan)
        t.ellipse(222, 590, 12, 12, fill=(214, 176, 70, 255), w=5)
    else:
        t.shape([(120, 100), (580, 100), (580, 1060), (120, 1060)], wood, w=8)
        for (x0, y0, x1, y1) in ((170, 150, 530, 520), (170, 600, 530, 1000)):
            t.shape([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], dark, w=6)
        t.ellipse(530, 590, 16, 16, fill=(214, 176, 70, 255), w=5)
    return t.done()


def kapi_ara(g: float):
    """8. tur (animasyon hakemi S4): kanadın kapanırken ara hâli (g: 0 = açık, 1 = kapalı). Kanat menteşeden (sol)
    döner: serbest kenarı perspektifle sağa gelir, üst/alt kenarı kasaya yaklaşır; panolar kanatla birlikte daralır.
    Kasa aynı: açık/kapalı çizimlerle aynı tuval ve kırpım (motorda yüz varyantı gibi art arda geçer)."""
    t = Tuval(700, 1100)
    wood, dark = (150, 98, 58, 255), (120, 76, 44, 255)
    t.shape([(80, 60), (620, 60), (620, 1060), (80, 1060)], (96, 62, 36, 255), w=9)          # kasa
    t.shape([(120, 100), (580, 100), (580, 1060), (120, 1060)], (24, 22, 26, 255), w=6)      # karanlık boşluk
    xe = 250 + (580 - 250) * g
    yt, yb = 150 - 50 * g, 1010 + 50 * g

    def P(u, v):   # kapalı kanattaki (u, v) -> ara hâl
        sx = (u - 120) / 460.0
        r = (v - 100) / 960.0
        X = 120 + sx * (xe - 120)
        top = 100 + sx * (yt - 100)
        bot = 1060 + sx * (yb - 1060)
        return (X, top + r * (bot - top))

    t.shape([P(120, 100), P(580, 100), P(580, 1060), P(120, 1060)], wood, w=8)
    if g > 0.35:
        for (x0, y0, x1, y1) in ((170, 150, 530, 520), (170, 600, 530, 1000)):
            t.shape([P(x0, y0), P(x1, y0), P(x1, y1), P(x0, y1)], dark, w=6)
    kx, ky = P(530, 590)
    t.ellipse(kx, ky, 10 + 6 * g, 16, fill=(214, 176, 70, 255), w=5)
    return t.done()


def gazete_1961():
    """Kendi çizimimiz, adsız/logosuz 'pazar gazetesi' sayfası (canlandırma). Manşet tek kelime + soru işareti; gerçek
    gazete başlığı ya da alıntı YOK. Fosforlu kalem kutusu: aşağıda yazdırılan 'kutu'."""
    W, H = 1500, 1960
    t = Tuval(W, H, (236, 231, 214, 255))
    ink = (28, 28, 28, 255)
    # isimsiz künye bandı: kalın çizgi + karalama (okunmaz), tarih satırı
    t.line([(70, 70), (W - 70, 70)], w=6, fill=ink, amp=0)
    for i, (x0, x1) in enumerate(((330, 560), (600, 820), (860, 1170))):
        t.line([(x0, 150), (x1, 150)], w=46, fill=(60, 60, 60, 255), amp=0)
    t.line([(70, 228), (W - 70, 228)], w=5, fill=ink, amp=0)
    t.text((W // 2, 262), "SONNTAG, 26. NOVEMBER 1961", ("serif_r", 44), fill=ink, anchor="mt")
    t.line([(70, 330), (W - 70, 330)], w=5, fill=ink, amp=0)
    # manşet
    s = "CONTERGAN?"
    fnt = ("serif", 150)
    t.text((W // 2, 380), s, fnt, fill=ink, anchor="mt")
    full = t.text_box(s, fnt, (W // 2, 380), anchor="mt")
    cw = t.text_box("CONTERGAN", fnt, (0, 0))
    kutu = (full[0] - 12, full[1] - 12, full[0] + (cw[2] - cw[0]) + 12, full[3] + 12)
    # alt başlık bandı (okunmaz gri çubuklar) + sütunlar
    for j in range(2):
        t.line([(170, 640 + j * 56), (W - 170 - j * 220, 640 + j * 56)], w=26, fill=(90, 90, 90, 255), amp=0)
    t.line([(70, 770), (W - 70, 770)], w=4, fill=ink, amp=0)
    cols = [(90, 520), (560, 990), (1030, 1430)]
    for ci, (x0, x1) in enumerate(cols):
        yazi_satirlari(t, x0, x1, 820, 32, gap=34, w=10, renk=(120, 120, 120, 255), seed=10 + ci)
        if ci < 2:
            t.line([(x1 + 20, 800), (x1 + 20, 1900)], w=3, fill=(150, 150, 150, 255), amp=0)
    im = t.done()
    print("  gazete_1961 'CONTERGAN' kutusu (piksel):", kutu)
    return im, kutu


def bulten_karti():
    """TFD Bülteni 26 (1994) sayfası yerine kendi bilgi kartımız (gerçek sayfanın taklidi değil)."""
    W, H = 1400, 900
    t = Tuval(W, H)
    t.shape([(30, 30), (W - 30, 30), (W - 30, H - 30), (30, H - 30)], (247, 244, 232, 255), w=9)
    t.line([(30, 150), (W - 30, 150)], w=6, fill=(170, 60, 60, 255), amp=0)
    for y in range(230, H - 60, 66):
        t.line([(60, y), (W - 60, y)], w=3, fill=(150, 180, 210, 255), amp=0)
    ink = (30, 30, 34, 255)
    t.text((70, 70), "TÜRK FARMAKOLOJİ DERNEĞİ BÜLTENİ", ("mono", 50), fill=ink)
    t.text((70, 186), "Sayı 26 · Temmuz 1994", ("mono", 44), fill=ink)
    t.text((70, 318), "Şükrü Kaymakçalan anma yazıları", ("mono", 48), fill=ink)
    t.text((70, 450), "Bakanlığa ilaç danışmanlığı: VAR", ("mono", 44), fill=(30, 100, 50, 255))
    t.text((70, 582), "Talidomit: YOK", ("mono", 44), fill=(170, 40, 40, 255))
    t.text((W - 70, H - 80), "bilgi kartı · kendi çizimimiz", ("mono", 28), fill=(120, 120, 120, 255), anchor="rs")
    return t.done()


def yumurta_tablasi():
    t = Tuval(1300, 700)
    tray = (196, 184, 160, 255)
    t.shape([(60, 330), (300, 120), (1240, 120), (1000, 330), (1000, 620), (60, 620)], (176, 164, 140, 255))
    t.shape([(60, 330), (300, 120), (1240, 120), (1000, 330)], tray)
    t.shape([(1000, 330), (1240, 120), (1240, 420), (1000, 620)], (160, 148, 124, 255))
    t.line([(60, 330), (1000, 330)], w=8)
    # yumurtalar (4 sıra x 7), arkadan öne; tablanın üst yüzeyinde
    for row in range(4):
        fy = (row + 0.5) / 4.0                     # 0 = arka kenar (y 120), 1 = ön kenar (y 330)
        y = 120 + fy * 210
        xl = 300 - fy * 240 + 50                   # sol kenar arkadan öne kayar
        for col in range(7):
            x = xl + col * 124
            s = 0.78 + 0.1 * row
            t.ellipse(x + 40, y - 18 * s, 44 * s, 54 * s, fill=(246, 236, 214, 255), w=6)
            t.ellipse(x + 26, y - 38 * s, 9 * s, 13 * s, fill=(255, 252, 244, 255), outline=None)
    return t.done()


def dosya(acik: bool, etiket: str | None = None, kalin=False):
    """Manila karton dosya. acik=True: kapağı açık, içi BOMBOŞ. etiket: kapaktaki yazı (daktilo)."""
    W, H = 1300, 900 if not acik else 820
    t = Tuval(W, H)
    manila, manila2 = (226, 196, 128, 255), (208, 176, 108, 255)
    if acik:
        t.shape([(60, 180), (620, 160), (640, 760), (80, 780)], manila2)                     # sol kanat (iç)
        t.shape([(640, 160), (660, 120), (900, 118), (920, 158), (1220, 170), (1240, 770), (650, 760)], manila)
        t.line([(640, 160), (650, 760)], w=7)
    else:
        if kalin:
            for k in range(6, 0, -1):
                t.shape([(70 + k * 6, 200 + k * 14), (1220 + k * 4, 200 + k * 14), (1230 + k * 4, 780 + k * 14),
                         (80 + k * 6, 780 + k * 14)], (250, 250, 246, 255), w=5)
        t.shape([(70, 200), (90, 150), (420, 146), (440, 196), (1220, 200), (1230, 780), (80, 780)], manila)
        if etiket:
            t.shape([(250, 330), (1060, 326), (1064, 560), (254, 564)], (250, 248, 240, 255), w=7)
            lines = etiket.split("\n")
            for i, s in enumerate(lines):
                t.text((657, 360 + i * 66), s, ("mono", 52 if len(lines) <= 3 else 44), fill=(30, 30, 34, 255), anchor="mt")
    return t.done()


def dosya_k3():
    """10. tur (animasyon hakemi S9): K3'te büyüteç üç satırlık etiketi ortadan kesiyordu ("TALİDO… RUHSAT B… ANKAF",
    telefonda bulamaç). Etikette tek temiz satır ("RUHSAT BAŞVURUSU"), "19??" kapağın alt sağında ayrı daktilo satırı:
    büyüteç yalnız onu örter. Gövde ve etiket `dosya()` ile aynı çizim dili."""
    W, H = 1300, 900
    t = Tuval(W, H)
    manila = (226, 196, 128, 255)
    t.shape([(70, 200), (90, 150), (420, 146), (440, 196), (1220, 200), (1230, 780), (80, 780)], manila)
    t.shape([(200, 300), (1110, 296), (1114, 430), (204, 434)], (250, 248, 240, 255), w=7)
    t.text((657, 336), "RUHSAT BAŞVURUSU", ("mono", 64), fill=(30, 30, 34, 255), anchor="mt")
    t.text((560, 640), "TARİH:", ("mono", 44), fill=(60, 52, 40, 255), anchor="lm")
    t.text((1010, 640), "19??", ("mono", 68), fill=(30, 30, 34, 255), anchor="mm")
    return t.done()


def makale_sayfasi():
    """Hamuryudan ve ark., Ann Intern Med 1998 ilk sayfasının KENDİ çizimimiz (dergi adı/logosu yok; başlık ve künye
    belgeli olgu)."""
    W, H = 1400, 1900
    t = Tuval(W, H, (252, 252, 250, 255))
    ink = (24, 24, 24, 255)
    t.line([(90, 120), (W - 90, 120)], w=4, fill=ink, amp=0)
    title = ["Thalidomide in the Treatment of the", "Mucocutaneous Lesions of the", "Behçet Syndrome"]
    for i, s in enumerate(title):
        t.text((W // 2, 190 + i * 78), s, ("serif", 60), fill=ink, anchor="mt")
    t.text((W // 2, 450), "A Randomized, Double-Blind, Placebo-Controlled Trial", ("serif_r", 40), fill=ink, anchor="mt")
    t.text((W // 2, 530), "Hamuryudan V, Mat C, Saip S, et al.", ("serif_r", 40), fill=(60, 60, 60, 255), anchor="mt")
    t.line([(90, 610), (W - 90, 610)], w=3, fill=(120, 120, 120, 255), amp=0)
    for ci, (x0, x1) in enumerate(((100, 670), (730, 1300))):
        yazi_satirlari(t, x0, x1, 670, 34, gap=34, w=9, renk=(150, 150, 150, 255), seed=30 + ci)
    t.text((100, H - 90), "1998", ("serif_r", 36), fill=(90, 90, 90, 255))
    return t.done()


def eczane_raf(bos_yer=True):
    """Düz çizim eczane rafı (kutular adsız). bos_yer: ortadaki kutunun yeri boş (Türkiye tezgâhı)."""
    W, H = 1600, 1100
    t = Tuval(W, H)
    wood, wood2 = (140, 92, 54, 255), (118, 76, 44, 255)
    t.shape([(40, 40), (W - 40, 40), (W - 40, H - 40), (40, H - 40)], wood2, w=9)
    shelves = [300, 560, 820]
    for y in shelves:
        t.shape([(70, y), (W - 70, y), (W - 70, y + 30), (70, y + 30)], wood, w=6)
    r = random.Random(5)
    colors = [(238, 238, 232, 255), (210, 226, 238, 255), (236, 222, 200, 255), (220, 236, 220, 255)]
    for si, y in enumerate(shelves):
        x = 100
        while x < W - 220:
            w = r.randint(110, 170)
            h = r.randint(150, 220)
            if bos_yer and si == 1 and 650 < x < 900:
                t.shape([(x, y - 210), (x + 200, y - 210), (x + 200, y), (x, y)], None, w=5,
                        outline=(240, 220, 120, 255))                          # boş yer (kesik çerçeve yerine sarı)
                x += 230
                continue
            c = colors[r.randrange(len(colors))]
            t.shape([(x, y - h), (x + w, y - h), (x + w, y), (x, y)], c, w=6)
            t.line([(x + 14, y - h + 40), (x + w - 14, y - h + 40)], w=10, fill=(84, 132, 196, 255), amp=0)
            x += w + r.randint(16, 30)
    # tezgâh
    t.shape([(40, 880), (W - 40, 880), (W - 40, H - 40), (40, H - 40)], (166, 112, 68, 255), w=9)
    t.shape([(20, 860), (W - 20, 860), (W - 20, 900), (20, 900)], (196, 160, 120, 255), w=7)
    return t.done()


def mantar_pano():
    W, H = 2560, 1440
    rng = np.random.default_rng(7)
    base = np.array([186, 140, 92], np.float32)
    noise = rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32)
    n = np.array(Image.fromarray(((noise * 40) + 128).clip(0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
                 .filter(ImageFilter.GaussianBlur(1.2))).astype(np.float32) / 128 - 1
    speck = (rng.random((H, W)) < 0.035).astype(np.float32)
    speck = np.array(Image.fromarray((speck * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3))).astype(np.float32) / 255
    img = base[None, None, :] * (1 + 0.16 * n[..., None]) - 55 * speck[..., None]
    im = Image.fromarray(img.clip(0, 255).astype(np.uint8))
    # ahşap çerçeve
    d = ImageDraw.Draw(im)
    fr = 70
    wood = (104, 70, 42)
    for box in ((0, 0, W, fr), (0, H - fr, W, H), (0, 0, fr, H), (W - fr, 0, W, H)):
        d.rectangle(box, fill=wood)
    d.rectangle((fr, fr, W - fr, H - fr), outline=(60, 40, 24), width=10)
    d.rectangle((4, 4, W - 5, H - 5), outline=(60, 40, 24), width=8)
    return im


def kagit_doku(koyu=False):
    W, H = 2560, 1440
    rng = np.random.default_rng(3 if not koyu else 4)
    base = np.array([238, 230, 210] if not koyu else [46, 42, 40], np.float32)
    big = rng.normal(0, 1, (H // 40, W // 40)).astype(np.float32)
    big = np.array(Image.fromarray(((big * 30) + 128).clip(0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
                   .filter(ImageFilter.GaussianBlur(30))).astype(np.float32) / 128 - 1
    fine = rng.normal(0, 1, (H, W)).astype(np.float32)
    fibers = np.array(Image.fromarray(((fine * 40) + 128).clip(0, 255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(0.8))).astype(np.float32) / 128 - 1
    k1, k2 = (0.05, 0.035) if not koyu else (0.18, 0.12)
    img = base[None, None, :] * (1 + k1 * big[..., None] + k2 * fibers[..., None])
    # hafif kenar kararması
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    img *= (1 - 0.12 * np.clip(r - 0.6, 0, 1))[..., None]
    return Image.fromarray(img.clip(0, 255).astype(np.uint8))


AYLAR = ["OCAK", "ŞUBAT", "MART", "NİSAN", "MAYIS", "HAZİRAN", "TEMMUZ", "AĞUSTOS", "EYLÜL", "EKİM", "KASIM", "ARALIK"]


def takvim_yapragi(gun: str | None, ay: str, yil: str, gri=False):
    """Koparılan takvim yaprağı: üst bant (yıl), büyük gün, ay adı. gun=None: ay + yıl büyük."""
    W, H = 700, 860
    t = Tuval(W, H)
    paper = (250, 248, 240, 255) if not gri else (214, 214, 210, 255)
    band = (196, 46, 46, 255) if not gri else (140, 140, 140, 255)
    t.shape([(40, 60), (W - 40, 60), (W - 40, H - 40), (40, H - 40)], paper, w=8)
    t.shape([(40, 60), (W - 40, 60), (W - 40, 200), (40, 200)], band, w=8)
    for x in range(110, W - 80, 80):
        t.ellipse(x, 60, 14, 14, fill=(60, 60, 60, 255), outline=None)                      # kopma delikleri
    ink = (30, 30, 30, 255) if not gri else (90, 90, 90, 255)
    t.text((W // 2, 130), yil, ("anton", 92), fill=(255, 255, 255, 255), anchor="mm")
    if gun:
        t.text((W // 2, 470), gun, ("anton", 360), fill=ink, anchor="mm")
        t.text((W // 2, 730), ay, ("anton", 110), fill=ink, anchor="mm")
    else:
        t.text((W // 2, 500), ay, ("anton", 170 if len(ay) <= 6 else 140), fill=ink, anchor="mm")
    return t.done()


def telefon_simge():
    t = Tuval(820, 640)
    blk = (36, 36, 40, 255)
    t.shape([(120, 300), (700, 300), (780, 580), (40, 580)], blk, w=8)                        # gövde
    t.ellipse(410, 430, 120, 120, fill=(230, 230, 226, 255), w=8)                             # kadran
    for k in range(10):
        a = math.radians(200 + k * 27)
        t.ellipse(410 + 82 * math.cos(a), 430 + 82 * math.sin(a), 16, 16, fill=blk, outline=None)
    t.ellipse(410, 430, 34, 34, fill=(196, 46, 46, 255), w=6)
    t.shape([(60, 200), (160, 140), (660, 140), (760, 200), (720, 270), (600, 230), (220, 230), (100, 270)], blk, w=8,
            smooth=True)                                                                       # ahize
    return t.done()


def zarf(damga: bool):
    t = Tuval(1100, 720)
    paper = (244, 238, 222, 255)
    t.shape([(60, 80), (1040, 80), (1040, 660), (60, 660)], paper, w=9)
    t.line([(60, 80), (550, 420), (1040, 80)], w=8)
    t.shape([(840, 120), (990, 120), (990, 290), (840, 290)], (226, 120, 90, 255), w=6)       # pul
    if damga:
        tmp = Tuval(1100, 720)
        red = (196, 40, 40, 235)
        tmp.shape([(170, 420), (830, 420), (830, 560), (170, 560)], None, w=12, outline=red, amp=1.2)
        tmp.text((500, 492), "TAAHHÜTLÜ", ("anton", 100), fill=red, anchor="mm")
        lay = tmp.done().rotate(8, center=(500, 490), resample=Image.BICUBIC)
        im = t.done()
        im.alpha_composite(lay)
        return im
    return t.done()


def raptiye():
    t = Tuval(260, 300)
    red = (206, 44, 44, 255)
    t.line([(130, 190), (150, 290)], w=10, fill=(150, 150, 150, 255), amp=0)
    t.ellipse(130, 170, 80, 40, fill=(176, 30, 30, 255), w=7)
    t.shape([(90, 170), (100, 70), (160, 70), (170, 170)], red, w=7)
    t.ellipse(130, 70, 60, 34, fill=red, w=7)
    t.ellipse(110, 62, 16, 8, fill=(250, 170, 170, 255), outline=None)
    return t.done()


def buyutec():
    t = Tuval(900, 900)
    t.shape([(560, 560), (620, 520), (860, 780), (800, 840)], (60, 40, 30, 255), w=8)
    t.ellipse(380, 380, 300, 300, fill=(210, 230, 245, 70), w=26, outline=(40, 40, 44, 255))
    t.line([(200, 250), (260, 180), (340, 140)], w=14, smooth=True, fill=(255, 255, 255, 200))
    return t.done()


def telefon_cerceve():
    """Akıllı telefon çerçevesi: ekran SAYDAM (viral iddia kartı içine konur). Ekran: (70,150)-(630,1290)."""
    W, H = 700, 1440
    t = Tuval(W, H)
    t.shape([(20, 40), (W - 20, 40), (W - 20, H - 40), (20, H - 40)], (24, 24, 28, 255), w=8, smooth=False)
    im = t.done()
    a = np.array(im)
    a[150:1290, 70:630, 3] = 0
    im = Image.fromarray(a)
    t2 = Tuval(W, H)
    t2.line([(70, 150), (630, 150), (630, 1290), (70, 1290)], w=5, closed=True, fill=(70, 70, 76, 255), amp=0)
    t2.ellipse(W // 2, 95, 14, 14, fill=(70, 70, 76, 255), outline=None)
    t2.line([(W // 2 - 80, 1350), (W // 2 + 80, 1350)], w=10, fill=(90, 90, 96, 255), amp=0)
    im.alpha_composite(t2.done())
    return im


def hap_simge():
    """Harita için küçük beyaz talidomit tableti simgesi (koyu kontur)."""
    t = Tuval(220, 220)
    t.ellipse(110, 110, 82, 82, fill=(250, 250, 246, 255), w=12, outline=(30, 30, 30, 255))
    t.line([(62, 110), (158, 110)], w=7, fill=(160, 160, 160, 255), amp=0)
    t.ellipse(84, 80, 20, 11, fill=(255, 255, 255, 255), outline=None)
    return t.done()


def gebelik_piktogram():
    """Düz piktogram: yandan hamile kadın silüeti + kırmızı yasak çemberi (kendi çizimimiz; ilaç kutularındaki
    uyarının simgesi, kişi değil)."""
    t = Tuval(800, 800)
    t.ellipse(400, 400, 340, 340, fill=(255, 255, 255, 255), w=0, outline=None)
    sil = (30, 30, 30, 255)
    t.ellipse(392, 196, 52, 56, fill=sil, outline=None)                                        # baş
    body = [(362, 262), (414, 262), (424, 300), (440, 334), (482, 372), (522, 428), (530, 480), (512, 528),
            (470, 556), (446, 566), (452, 680), (404, 680), (398, 590), (378, 590), (372, 680), (326, 680),
            (334, 560), (330, 470), (336, 380), (344, 318)]
    t.shape(body, sil, w=0, outline=None, smooth=True)
    t.shape([(344, 318), (300, 420), (318, 430), (360, 340)], sil, w=0, outline=None)          # kol
    t.ellipse(400, 400, 330, 330, fill=None, w=54, outline=(206, 32, 32, 255))
    t.line([(168, 168), (632, 632)], w=54, fill=(206, 32, 32, 255), amp=0)
    return t.done()


def hastane_odasi():
    """1960'lar hastane odası, düz çizim zemin (2560x1440): boş yatak kenarı sağda, hasta YOK (senaryo B6.1)."""
    W, H = 2560, 1440
    t = Tuval(W, H, (236, 232, 214, 255))
    t.shape([(0, 760), (W, 760), (W, 1180), (0, 1180)], (172, 202, 178, 255), w=0, outline=None)   # yeşil lambri
    t.line([(0, 760), (W, 760)], w=10, fill=(120, 150, 126, 255), amp=0)
    t.shape([(0, 1180), (W, 1180), (W, H), (0, H)], (156, 154, 144, 255), w=0, outline=None)      # yer
    for x in range(-200, W + 400, 260):
        t.line([(x, 1180), (x - 220, H)], w=4, fill=(136, 134, 126, 255), amp=0)
    t.line([(0, 1180), (W, 1180)], w=8, fill=(90, 90, 84, 255), amp=0)
    # pencere (solda) + perde
    t.shape([(250, 200), (780, 200), (780, 700), (250, 700)], (206, 228, 242, 255), w=12)
    t.line([(515, 200), (515, 700)], w=12)
    t.line([(250, 450), (780, 450)], w=12)
    t.shape([(180, 160), (300, 170), (290, 760), (170, 770)], (226, 214, 180, 255), w=8)
    t.shape([(740, 170), (860, 160), (870, 770), (750, 760)], (226, 214, 180, 255), w=8)
    t.line([(150, 160), (890, 160)], w=10)
    # kapı (sağ arkada)
    t.shape([(1880, 300), (2240, 300), (2240, 1180), (1880, 1180)], (220, 216, 196, 255), w=10)
    t.ellipse(1910, 760, 14, 14, fill=(150, 150, 150, 255), w=5)
    # duvar lambası
    t.shape([(1240, 300), (1340, 300), (1370, 360), (1210, 360)], (240, 240, 230, 255), w=7)
    # komodin + su bardağı
    t.shape([(1150, 880), (1400, 880), (1400, 1310), (1150, 1310)], (240, 240, 236, 255), w=9)
    t.line([(1150, 1030), (1400, 1030)], w=7)
    t.ellipse(1365, 1090, 12, 12, fill=(150, 150, 150, 255), w=4)
    t.shape([(1230, 780), (1290, 780), (1282, 880), (1238, 880)], (214, 232, 240, 200), w=6)
    # demir yatak (önde, sağda, kadraj dışına uzanır): başlık, şilte, beyaz çarşaf, katlı battaniye; BOŞ
    iron = (200, 204, 206, 255)
    t.line([(1480, 560), (1480, 1360)], w=20, fill=iron, amp=0)
    t.line([(1640, 540), (1640, 1360)], w=20, fill=iron, amp=0)
    t.line([(1480, 590), (1560, 530), (1640, 550)], w=18, fill=iron)
    for x in (1530, 1590):
        t.line([(x, 580), (x, 960)], w=10, fill=iron, amp=0)
    t.shape([(1490, 960), (W + 20, 930), (W + 20, 1110), (1490, 1140)], (250, 250, 248, 255), w=10)  # çarşaf
    t.shape([(1660, 860), (1960, 850), (1985, 960), (1650, 972)], (252, 252, 250, 255), w=9, smooth=True)  # yastık
    t.shape([(2230, 920), (W + 20, 910), (W + 20, 1100), (2200, 1110)], (150, 182, 214, 255), w=9)     # battaniye
    t.line([(1490, 1140), (W + 20, 1110)], w=10)
    t.line([(1700, 1140), (1700, 1380)], w=16, fill=iron, amp=0)                                       # ayak
    return t.done()


# ------------------------------------------------------------------------------------------------ 4. tur zeminleri
# İzlenme hakemi + hesap sahibi (4. tur): hiçbir görsel 2'den çok çekimde kullanılmasın (Sağlık Bakanlığı fotoğrafı 5,
# teneke 5, büro 5 çekimdeydi). Wikimedia bu turda HTTP 429 verdiği için yeni fotoğraf yerine kendi düz çizimlerimiz:
# bakanlık koridoru, bakanlık odası, eczane, büro; doku: kara tahta, kraft karton, iki renkli duvar, mavi kâğıt.
# Hepsi orta parlaklıkta (kare ortalaması >= ~60/255), yazısız/logosuz, kişisiz.
def _zemin_tuval(duvar, W=2560, H=1440):
    return Tuval(W, H, duvar + (255,))


def _zemin(t, y, renk, cizgi=(90, 78, 64, 255)):
    W, H = t.w, t.h
    t.shape([(0, y), (W, y), (W, H), (0, H)], renk + (255,), w=0, outline=None)
    t.line([(0, y), (W, y)], w=8, fill=cizgi, amp=0)


def _kapi_kasasi(t, x0, y0, x1, y1, kanat=(146, 98, 58), cam=True, no=None):
    t.shape([(x0 - 26, y0 - 26), (x1 + 26, y0 - 26), (x1 + 26, y1), (x0 - 26, y1)], (98, 64, 38, 255), w=8)
    t.shape([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], kanat + (255,), w=8)
    if cam:
        t.shape([(x0 + 40, y0 + 40), (x1 - 40, y0 + 40), (x1 - 40, y0 + (y1 - y0) * 0.42), (x0 + 40, y0 + (y1 - y0) * 0.42)],
                (214, 226, 228, 255), w=6)
    t.shape([(x0 + 40, y0 + (y1 - y0) * 0.52), (x1 - 40, y0 + (y1 - y0) * 0.52), (x1 - 40, y1 - 50), (x0 + 40, y1 - 50)],
            tuple(int(c * 0.86) for c in kanat) + (255,), w=6)
    t.ellipse(x1 - 36, y0 + (y1 - y0) * 0.48, 13, 13, fill=(214, 176, 70, 255), w=5)
    if no:
        t.rect(x0 + (x1 - x0) / 2 - 60, y0 - 110, x0 + (x1 - x0) / 2 + 60, y0 - 46, (236, 230, 210, 255), w=5)
        t.text((x0 + (x1 - x0) / 2, y0 - 78), no, ("mono", 40), fill=(40, 40, 40, 255), anchor="mm")


def koridor():
    """Bakanlık koridoru (dönem belirsiz; SA.6 ve B6.6 kapı sahneleri): krem duvar, ceviz lambri, iki kapı, bank,
    tavan lambası, duyuru panosu (yazısız)."""
    t = _zemin_tuval((228, 220, 196))
    W, H = t.w, t.h
    t.shape([(0, 860), (W, 860), (W, 1180), (0, 1180)], (138, 98, 62, 255), w=0, outline=None)     # lambri
    for x in range(0, W, 220):
        t.line([(x, 870), (x, 1170)], w=4, fill=(110, 76, 46, 255), amp=0)
    t.line([(0, 860), (W, 860)], w=10, fill=(92, 62, 38, 255), amp=0)
    _zemin(t, 1180, (150, 140, 124))
    for x in range(-300, W + 600, 300):    # parke
        t.line([(x, 1180), (x - 260, H)], w=4, fill=(126, 116, 102, 255), amp=0)
    _kapi_kasasi(t, 1180, 330, 1560, 1180, no="12")
    _kapi_kasasi(t, 2160, 330, 2500, 1180, kanat=(132, 88, 52), no="14")
    # duyuru panosu (yazısız kâğıtlar)
    t.shape([(240, 360), (820, 360), (820, 720), (240, 720)], (176, 132, 86, 255), w=8)
    r = random.Random(4)
    for (x, y) in ((290, 400), (470, 420), (640, 390), (330, 560), (560, 560)):
        w, h = r.randint(120, 160), r.randint(110, 140)
        t.shape([(x, y), (x + w, y + 6), (x + w - 4, y + h), (x - 4, y + h - 4)], (244, 240, 228, 255), w=5)
        for j in range(3):
            t.line([(x + 18, y + 30 + j * 26), (x + w - 24, y + 32 + j * 26)], w=6, fill=(150, 150, 150, 255), amp=0)
    # tavan lambaları
    for x in (700, 1900):
        t.line([(x, 0), (x, 120)], w=6, fill=(60, 60, 60, 255), amp=0)
        t.shape([(x - 110, 120), (x + 110, 120), (x + 70, 200), (x - 70, 200)], (240, 236, 214, 255), w=7)
    # bank (lambri önünde)
    t.shape([(1660, 1000), (2080, 1000), (2080, 1040), (1660, 1040)], (110, 74, 44, 255), w=7)
    for x in (1690, 2040):
        t.line([(x, 1040), (x, 1170)], w=12, fill=(70, 70, 70, 255), amp=0)
    return t.done()


def bakanlik_oda():
    """1950'ler-60'lar bakanlık odası (B5.2, B5.3c): açık yeşil duvar, lambri, pencerede yalın şehir silueti, dosya
    dolabı, yeşil çuhalı masa ve daktilo, portmanto. Portre/bayrak/yazı yok."""
    t = _zemin_tuval((196, 212, 190))
    W, H = t.w, t.h
    t.shape([(0, 900), (W, 900), (W, 1200), (0, 1200)], (126, 96, 66, 255), w=0, outline=None)
    t.line([(0, 900), (W, 900)], w=10, fill=(88, 64, 40, 255), amp=0)
    _zemin(t, 1200, (138, 120, 100))
    # pencere: gökyüzü + yalın bina siluetleri
    t.shape([(860, 200), (1700, 200), (1700, 820), (860, 820)], (196, 222, 240, 255), w=12)
    for (x0, x1, y) in ((880, 1040, 640), (1040, 1200, 560), (1200, 1330, 680), (1330, 1520, 600), (1520, 1690, 660)):
        t.shape([(x0, y), (x1, y), (x1, 812), (x0, 812)], (168, 176, 186, 255), w=5)
        for wy in range(y + 30, 800, 60):
            for wx in range(x0 + 20, x1 - 30, 50):
                t.rect(wx, wy, wx + 22, wy + 30, (120, 130, 146, 255), w=0, outline=None)
    t.line([(1280, 200), (1280, 820)], w=12)
    t.line([(860, 470), (1700, 470)], w=12)
    t.shape([(780, 160), (900, 170), (890, 880), (770, 890)], (186, 64, 52, 255), w=8)      # perdeler
    t.shape([(1660, 170), (1780, 160), (1790, 890), (1670, 880)], (186, 64, 52, 255), w=8)
    t.line([(740, 160), (1820, 160)], w=10)
    # dosya dolabı (solda)
    t.shape([(160, 520), (560, 520), (560, 1220), (160, 1220)], (126, 140, 128, 255), w=9)
    for y in (690, 860, 1030):
        t.line([(160, y), (560, y)], w=7)
    for y in (600, 770, 940, 1110):
        t.rect(310, y, 410, y + 26, (210, 206, 190, 255), w=5)
    for (x0, x1) in ((190, 300), (330, 420), (440, 540)):    # dolabın üstünde dosyalar
        t.shape([(x0, 440), (x1, 440), (x1 - 6, 520), (x0 + 6, 520)], (214, 186, 120, 255), w=6)
    # masa (sağda): yeşil çuha + daktilo
    t.shape([(1860, 980), (2560, 980), (2560, 1040), (1860, 1040)], (64, 108, 76, 255), w=8)
    t.shape([(1880, 1040), (2540, 1040), (2540, 1300), (1880, 1300)], (120, 82, 50, 255), w=8)
    t.shape([(2020, 860), (2300, 860), (2340, 980), (1990, 980)], (52, 52, 56, 255), w=7)  # daktilo
    t.shape([(2060, 800), (2260, 800), (2250, 862), (2070, 862)], (236, 234, 222, 255), w=5)
    # portmanto
    t.line([(1790, 330), (1790, 1200)], w=14, fill=(90, 60, 36, 255), amp=0)
    for dx in (-60, 60):
        t.line([(1790, 360), (1790 + dx, 420)], w=10, fill=(90, 60, 36, 255), amp=0)
    t.line([(1720, 1200), (1860, 1200)], w=12, fill=(90, 60, 36, 255), amp=0)
    return t.done()


def eczane_zemin():
    """Eczane (B1.8 ve B2.4b; ülke/yazı yok): arka duvar boyu ahşap raflar, kavanoz ve şişeler, önde tezgâh, terazi."""
    t = _zemin_tuval((214, 204, 180))
    W, H = t.w, t.h
    t.shape([(80, 120), (W - 80, 120), (W - 80, 1000), (80, 1000)], (120, 80, 46, 255), w=10)
    r = random.Random(11)
    renkler = [(238, 236, 228), (196, 222, 236), (226, 206, 170), (206, 230, 206), (120, 150, 190), (176, 90, 70)]
    for y in (340, 560, 780, 990):
        t.shape([(100, y), (W - 100, y), (W - 100, y + 28), (100, y + 28)], (150, 104, 62, 255), w=6)
    for y in (340, 560, 780):
        x = 130
        while x < W - 240:
            w, h = r.randint(70, 130), r.randint(110, 170)
            c = renkler[r.randrange(len(renkler))] + (255,)
            if r.random() < 0.5:   # kavanoz (yuvarlak omuz + kapak)
                t.shape([(x, y), (x + w, y), (x + w, y - h + 30), (x + w - 14, y - h + 14), (x + 14, y - h + 14),
                         (x, y - h + 30)], c, w=5)
                t.rect(x + 10, y - h - 10, x + w - 10, y - h + 16, (60, 60, 64, 255), w=4)
            else:                  # şişe (dar boyun)
                t.shape([(x, y), (x + w, y), (x + w, y - h + 50), (x + w * 0.65, y - h + 20), (x + w * 0.65, y - h),
                         (x + w * 0.35, y - h), (x + w * 0.35, y - h + 20), (x, y - h + 50)], c, w=5)
            t.rect(x + 10, y - h * 0.55, x + w - 10, y - h * 0.3, (248, 246, 236, 255), w=3)
            x += w + r.randint(14, 34)
    # tezgâh
    t.shape([(0, 1080), (W, 1080), (W, H), (0, H)], (150, 100, 58, 255), w=0, outline=None)
    t.shape([(-20, 1040), (W + 20, 1040), (W + 20, 1100), (-20, 1100)], (190, 150, 104, 255), w=8)
    for x in range(200, W, 560):
        t.shape([(x, 1150), (x + 360, 1150), (x + 360, 1380), (x, 1380)], (136, 90, 52, 255), w=6)
    # terazi (sağda tezgâhta)
    t.line([(2140, 1040), (2140, 860)], w=12, fill=(150, 120, 60, 255), amp=0)
    t.line([(2000, 870), (2280, 870)], w=10, fill=(150, 120, 60, 255), amp=0)
    for x in (2000, 2280):
        t.line([(x, 870), (x, 940)], w=4, fill=(90, 90, 90, 255), amp=0)
        t.shape([(x - 70, 940), (x + 70, 940), (x + 40, 980), (x - 40, 980)], (196, 160, 80, 255), w=6)
    return t.done()


def buro():
    """1960'lar ABD bürosu (B4.3, B4.5; FDA değil, yer etiketi yok): jaluzili pencere, metal dosya dolapları, duvar saati,
    dosya yığınlı masa."""
    t = _zemin_tuval((206, 208, 200))
    W, H = t.w, t.h
    _zemin(t, 1160, (120, 116, 110))
    # jaluzili pencere
    t.shape([(900, 180), (1700, 180), (1700, 820), (900, 820)], (232, 236, 230, 255), w=12)
    for y in range(210, 810, 34):
        t.line([(910, y), (1690, y)], w=7, fill=(170, 172, 164, 255), amp=0)
    t.line([(1300, 180), (1300, 820)], w=6, fill=(140, 140, 136, 255), amp=0)
    # duvar saati
    t.ellipse(560, 330, 120, 120, fill=(248, 246, 238, 255), w=10)
    for k in range(12):
        a = k * math.pi / 6
        t.line([(560 + 92 * math.sin(a), 330 - 92 * math.cos(a)), (560 + 106 * math.sin(a), 330 - 106 * math.cos(a))],
               w=6, amp=0)
    t.line([(560, 330), (560, 262)], w=9, amp=0)
    t.line([(560, 330), (612, 352)], w=7, amp=0)
    # metal dosya dolapları (solda)
    for x0 in (120, 460):
        t.shape([(x0, 560), (x0 + 320, 560), (x0 + 320, 1170), (x0, 1170)], (150, 160, 166, 255), w=9)
        for y in (710, 860, 1010):
            t.line([(x0, y), (x0 + 320, y)], w=6)
        for y in (620, 770, 920, 1070):
            t.rect(x0 + 120, y, x0 + 200, y + 22, (214, 214, 206, 255), w=4)
    # masa + dosya yığınları (sağda)
    t.shape([(1860, 960), (2560, 960), (2560, 1010), (1860, 1010)], (110, 84, 60, 255), w=8)
    t.shape([(1890, 1010), (2530, 1010), (2530, 1260), (1890, 1260)], (96, 72, 50, 255), w=8)
    y = 960
    for j, (w, c) in enumerate(((300, (232, 214, 160)), (280, (214, 196, 140)), (310, (236, 222, 176)),
                                (270, (220, 200, 150)), (300, (232, 214, 160)))):
        t.shape([(1960 + j * 6, y - 42), (1960 + j * 6 + w, y - 42), (1960 + j * 6 + w, y), (1960 + j * 6, y)],
                c + (255,), w=5)
        y -= 42
    return t.done()


def hekim_odasi():
    """6. tur (izlenme hakemi S7: B2.5a düz mavi kâğıt zeminde "ucuz" görünüyordu): 1950'ler hekim çalışma odası,
    düz çizim (2560x1440). Kitaplık (renkli sırtlar, yazısız), pencere, boş çerçeveli diploma, manzara tablosu,
    masa lambası, kâğıtlı masa, kalorifer. Kişi/yazı/logo yok; orta parlaklık. Yer etiketi yok (Voss'un odası değil)."""
    t = _zemin_tuval((214, 200, 170))
    W, H = t.w, t.h
    t.shape([(0, 930), (W, 930), (W, 1190), (0, 1190)], (112, 84, 58, 255), w=0, outline=None)      # lambri
    for x in range(0, W, 240):
        t.line([(x, 940), (x, 1180)], w=4, fill=(92, 68, 46, 255), amp=0)
    t.line([(0, 930), (W, 930)], w=10, fill=(78, 56, 36, 255), amp=0)
    _zemin(t, 1190, (128, 104, 82))
    for x in range(-300, W + 600, 300):
        t.line([(x, 1190), (x - 260, H)], w=4, fill=(108, 88, 70, 255), amp=0)
    # kitaplık (solda): 4 raf, renkli sırtlar
    t.shape([(120, 170), (860, 170), (860, 1210), (120, 1210)], (118, 78, 44, 255), w=10)
    r = random.Random(31)
    sirt = [(150, 52, 44), (52, 78, 120), (60, 104, 70), (182, 150, 84), (110, 60, 90), (196, 186, 160), (70, 70, 74)]
    for y in (420, 670, 920, 1170):
        t.shape([(140, y), (840, y), (840, y + 22), (140, y + 22)], (146, 100, 58, 255), w=5)
        x = 160
        while x < 800:
            w, h = r.randint(36, 62), r.randint(170, 220)
            if r.random() < 0.12:   # yatık kitap yığını
                for k in range(3):
                    t.shape([(x, y - 34 * (k + 1)), (x + 150, y - 34 * (k + 1)), (x + 150, y - 34 * k), (x, y - 34 * k)],
                            sirt[r.randrange(len(sirt))] + (255,), w=4)
                x += 165
                continue
            c = sirt[r.randrange(len(sirt))] + (255,)
            t.shape([(x, y), (x + w, y), (x + w, y - h), (x, y - h)], c, w=4)
            t.line([(x + 8, y - h + 30), (x + w - 8, y - h + 30)], w=4, fill=(230, 210, 150, 255), amp=0)
            x += w + r.randint(2, 8)
    # pencere (ortada) + perde
    t.shape([(1080, 200), (1640, 200), (1640, 760), (1080, 760)], (200, 224, 236, 255), w=12)
    t.line([(1360, 200), (1360, 760)], w=12)
    t.line([(1080, 470), (1640, 470)], w=12)
    for (x0, x1) in ((1000, 1110), (1610, 1720)):
        t.shape([(x0, 160), (x1, 170), (x1 + 6, 820), (x0 - 6, 830)], (150, 120, 76, 255), w=8)
    t.line([(980, 158), (1740, 158)], w=10)
    # duvarda boş çerçeveli diploma ve manzara tablosu (sağda)
    t.shape([(1860, 250), (2160, 250), (2160, 480), (1860, 480)], (238, 232, 212, 255), w=10)
    t.shape([(1900, 290), (2120, 290), (2120, 440), (1900, 440)], (246, 242, 226, 255), w=4)
    yazi_satirlari(t, 1930, 2090, 330, 3, gap=34, w=7, renk=(170, 160, 140, 255), seed=5)
    t.shape([(2220, 230), (2480, 230), (2480, 560), (2220, 560)], (150, 112, 70, 255), w=10)          # manzara tablosu
    t.shape([(2250, 260), (2450, 260), (2450, 530), (2250, 530)], (190, 218, 232, 255), w=4)
    t.shape([(2250, 440), (2320, 380), (2390, 420), (2450, 370), (2450, 530), (2250, 530)], (112, 156, 98, 255), w=4)
    t.ellipse(2400, 310, 22, 22, fill=(244, 214, 120, 255), w=3)
    # masa (sağ önde) + lamba + kâğıtlar + mürekkep hokkası
    t.shape([(1500, 1000), (2560, 1000), (2560, 1060), (1500, 1060)], (96, 64, 38, 255), w=8)
    t.shape([(1540, 1060), (2520, 1060), (2520, 1380), (1540, 1380)], (120, 82, 50, 255), w=8)
    for x0 in (1600, 2140):
        t.shape([(x0, 1110), (x0 + 320, 1110), (x0 + 320, 1330), (x0, 1330)], (108, 72, 44, 255), w=6)
        t.ellipse(x0 + 160, 1220, 14, 14, fill=(196, 166, 90, 255), w=4)
    t.line([(1700, 1000), (1700, 760)], w=14, fill=(60, 74, 60, 255), amp=0)                # lamba
    t.line([(1700, 760), (1800, 700)], w=12, fill=(60, 74, 60, 255), amp=0)
    t.shape([(1760, 650), (1900, 650), (1940, 740), (1730, 740)], (44, 104, 70, 255), w=8)
    t.shape([(1640, 990), (1760, 990), (1760, 1004), (1640, 1004)], (60, 74, 60, 255), w=5)
    for k, (x, y) in enumerate(((1960, 960), (2010, 950), (2230, 970))):
        t.shape([(x, y), (x + 220, y - 8), (x + 228, y + 34), (x + 6, y + 40)], (246, 244, 236, 255), w=5)
    t.shape([(2400, 930), (2470, 930), (2480, 998), (2390, 998)], (40, 40, 52, 255), w=6)
    # kalorifer (pencere altında)
    t.shape([(1120, 960), (1600, 960), (1600, 1150), (1120, 1150)], (222, 222, 214, 255), w=8)
    for x in range(1150, 1600, 50):
        t.line([(x, 975), (x, 1135)], w=6, fill=(180, 180, 172, 255), amp=0)
    return t.done()


def doku_tebesir():
    """Kara tahta (yeşil, tebeşir lekeli, alt kenarda ahşap tebeşirlik): B5.13, B6.4a molekül/mekanizma."""
    W, H = 2560, 1440
    rng = np.random.default_rng(12)
    base = np.array([50, 84, 70], np.float32)
    big = rng.normal(0, 1, (H // 60, W // 60)).astype(np.float32)
    big = np.array(Image.fromarray(((big * 30) + 128).clip(0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
                   .filter(ImageFilter.GaussianBlur(40))).astype(np.float32) / 128 - 1
    fine = rng.normal(0, 1, (H, W)).astype(np.float32)
    img = base[None, None, :] * (1 + 0.10 * big[..., None] + 0.05 * fine[..., None])
    im = Image.fromarray(img.clip(0, 255).astype(np.uint8))
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for _ in range(26):   # silinmiş tebeşir izleri
        x, y = rng.uniform(0, W), rng.uniform(0, H * 0.85)
        w, h = rng.uniform(200, 700), rng.uniform(40, 140)
        d.ellipse((x, y, x + w, y + h), fill=(230, 236, 230, int(rng.uniform(8, 22))))
    lay = lay.filter(ImageFilter.GaussianBlur(30))
    im.paste(lay, (0, 0), lay)
    d = ImageDraw.Draw(im)
    d.rectangle((0, H - 70, W, H), fill=(132, 92, 56))
    d.rectangle((0, H - 70, W, H - 60), fill=(92, 62, 36))
    for x in (400, 1300, 2100):
        d.rectangle((x, H - 92, x + 80, H - 70), fill=(240, 240, 232))
    return im


def doku_duz(renk, tohum, k1=0.06, k2=0.03, lambri=None):
    """Düz boyalı duvar / karton: hafif leke + lif; lambri=(y, renk) iki renkli duvar."""
    W, H = 2560, 1440
    rng = np.random.default_rng(tohum)
    big = rng.normal(0, 1, (H // 40, W // 40)).astype(np.float32)
    big = np.array(Image.fromarray(((big * 30) + 128).clip(0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
                   .filter(ImageFilter.GaussianBlur(30))).astype(np.float32) / 128 - 1
    fine = rng.normal(0, 1, (H, W)).astype(np.float32)
    tab = np.zeros((H, W, 3), np.float32) + np.array(renk, np.float32)
    if lambri:
        y, r2 = lambri
        tab[y:] = np.array(r2, np.float32)
    img = tab * (1 + k1 * big[..., None] + k2 * fine[..., None])
    im = Image.fromarray(img.clip(0, 255).astype(np.uint8))
    if lambri:
        ImageDraw.Draw(im).rectangle((0, lambri[0] - 6, W, lambri[0] + 6), fill=tuple(int(c * 0.7) for c in lambri[1]))
    return im


def doku_ahsap():
    """Ahşap masa yüzeyi (yatay damar, tahta ekleri): B3.11b tek tablet."""
    W, H = 2560, 1440
    rng = np.random.default_rng(24)
    base = np.array([150, 104, 66], np.float32)
    yy = np.arange(H, dtype=np.float32)[:, None]
    xx = np.arange(W, dtype=np.float32)[None, :]
    big = rng.normal(0, 1, (H // 8, W // 160)).astype(np.float32)
    big = np.array(Image.fromarray(((big * 40) + 128).clip(0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
                   ).astype(np.float32) / 128 - 1
    damar = np.sin(yy / 9.0 + 3.0 * big) * 0.5 + 0.5
    fine = rng.normal(0, 1, (H, W)).astype(np.float32)
    img = base[None, None, :] * (0.86 + 0.16 * damar[..., None] + 0.03 * fine[..., None])
    im = Image.fromarray(img.clip(0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    for y in (330, 700, 1080):
        d.line((0, y, W, y), fill=(92, 62, 38), width=6)
    return im


def kanun_sayfasi():
    """B1.7 sağ paneli: 1262 sayılı Kanun (1928), kendi çizimimiz: masada eski bir kanun sayfası. Yazılar: kanunun adı
    ve belgeli özü (Bakanlık ruhsatı olmadan ilaç satılamaz); gerçek Resmî Gazete künyesi/logosu yok."""
    t = Tuval(1920, 1080, (120, 88, 58, 255))
    for y in range(0, 1080, 90):   # masa ahşabı
        t.line([(0, y + 20), (1920, y + 34)], w=5, fill=(104, 74, 48, 255), amp=0.4)
    # 4. tur: sayfa aşağıda (bölünmüş ekranın panel başlığı "TÜRKİYE" üstte, sayfanın başlığına binmesin)
    x0, y0, x1, y1 = 630, 250, 1290, 1060
    t.shape([(x0 + 14, y0 + 16), (x1 + 14, y0 + 16), (x1 + 14, y1 + 16), (x0 + 14, y1 + 16)], (70, 50, 34, 255), w=0,
            outline=None)
    t.shape([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], (240, 232, 212, 255), w=6)
    ink = (34, 30, 28, 255)
    t.text((960, 300), "1262 SAYILI KANUN", ("serif", 52), fill=ink, anchor="mt")
    t.text((960, 370), "1928", ("anton", 120), fill=(168, 40, 34, 255), anchor="mt")
    t.line([(710, 530), (1210, 530)], w=4, fill=ink, amp=0)
    t.text((960, 560), "Bakanlık ruhsatı olmadan", ("serif_r", 44), fill=ink, anchor="mt")
    t.text((960, 618), "ilaç satılamaz.", ("serif_r", 44), fill=ink, anchor="mt")
    yazi_satirlari(t, 700, 1220, 720, 9, gap=34, w=9, renk=(150, 146, 136, 255), seed=31)
    return t.done()


def gazete_2008():
    """B5.8: 2008 tarihli bir haber kupürü, kendi çizimimiz (CANLANDIRMA): adsız künye, okunmaz başlık ve sütunlar,
    yalnız tarih satırı ('2008') okunur. Gerçek gazete adı, başlığı ya da alıntısı YOK. Kutular: tarih ve başlık."""
    W, H = 1700, 1180
    t = Tuval(W, H, (238, 236, 228, 255))
    ink = (30, 30, 32, 255)
    t.line([(60, 60), (W - 60, 60)], w=6, fill=ink, amp=0)
    for (x0, x1) in ((520, 760), (800, 1180)):      # okunmaz künye
        t.line([(x0, 128), (x1, 128)], w=44, fill=(70, 70, 74, 255), amp=0)
    t.line([(60, 196), (W - 60, 196)], w=4, fill=ink, amp=0)
    t.text((W // 2, 226), "2008", ("serif", 64), fill=ink, anchor="mt")
    tarih = t.text_box("2008", ("serif", 64), (W // 2, 226), anchor="mt")
    t.line([(60, 320), (W - 60, 320)], w=4, fill=ink, amp=0)
    for j, x1 in enumerate((W - 160, W - 420)):      # başlık (okunmaz kalın çubuklar)
        t.line([(160, 400 + j * 92), (x1, 400 + j * 92)], w=60, fill=(46, 46, 50, 255), amp=0)
    baslik = (140, 360, W - 140, 530)
    t.line([(60, 590), (W - 60, 590)], w=3, fill=ink, amp=0)
    for ci, (x0, x1) in enumerate(((90, 560), (610, 1080), (1130, 1610))):
        yazi_satirlari(t, x0, x1, 640, 15, gap=34, w=10, renk=(128, 128, 132, 255), seed=40 + ci)
    im = t.done()
    kutu = (tarih[0] - 16, tarih[1] - 12, tarih[2] + 16, tarih[3] + 12)
    print("  gazete_2008 kutular (piksel): tarih", kutu, "başlık", baslik)
    return im


# ------------------------------------------------------------------------------------------------ hepsi
def hepsi(sec: list[str]):
    def on(n):
        return not sec or n in sec

    if on("tablet"):
        kaydet(tablet(120), "tablet.png")
    if on("numune"):
        kaydet(numune_kutusu(), "numune_kutusu.png")
        kaydet(numune_tabletler(), "numune_kutusu_tabletler.png")
    if on("fare"):
        kaydet(fare_kafesi(), "fare_kafesi.png")
        kaydet(doz_sisesi(), "doz_sisesi.png")
    if on("molekul"):
        src = HERE / "talidomit_molekul_pd.png"
        if src.exists():
            b, s = molekul(src)
            kaydet(b, "molekul_beyaz.png")
            kaydet(s, "molekul_siyah.png")
        kaydet(cereblon(), "cereblon.png")
    if on("molekul") or on("sall4"):   # 7. tur: iki hâl aynı tuvalde
        a, b = sall4_cift()
        kaydet(a, "sall4.png", trim=False)
        kaydet(b, "sall4_kirik.png", trim=False)
    if on("zar"):
        kaydet(zarlar(), "zarlar.png")
    if on("kapi"):
        kaydet(kapi(True), "kapi_acik.png")
        kaydet(kapi(False), "kapi_kapali.png")
    if on("kapi") or on("kapi_ara"):   # 8. tur: kapanırken ara kareler (açık ve kapalı çizimlere dokunmaz)
        kaydet(kapi_ara(0.4), "kapi_ara_1.png")
        kaydet(kapi_ara(0.78), "kapi_ara_2.png")
    if on("gazete"):
        im, kutu = gazete_1961()
        kaydet(im, "gazete_1961_canlandirma.png", trim=False)
    if on("bulten"):
        kaydet(bulten_karti(), "bulten_karti_yedek.png")
    if on("yumurta"):
        kaydet(yumurta_tablasi(), "yumurta_tablasi.png")
    if on("dosya"):
        kaydet(dosya(True), "dosya_bos_acik.png")
        kaydet(dosya(False), "dosya_kapali.png")
        kaydet(dosya(False, "TALİDOMİT\nRUHSAT BAŞVURUSU\nANKARA 19??"), "dosya_k3_etiketli.png")
    if on("dosya") or on("dosya_k3"):   # 10. tur: K3'ün tek satır etiketli dosyası
        kaydet(dosya_k3(), "dosya_k3_tek_satir.png")
        kaydet(dosya(False, "RUHSAT BAŞVURUSU", kalin=True), "dosya_ruhsat_basvurusu.png")
        kaydet(dosya(False, "KEVADON"), "dosya_kevadon.png")
        kaydet(dosya(False, "SİNİR HASARI\nRAPORLARI · 1961"), "dosya_sinir_hasari_1961.png")
    if on("makale"):
        kaydet(makale_sayfasi(), "makale_behcet_1998_cizim.png", trim=False)
    if on("raf"):
        kaydet(eczane_raf(True), "eczane_raf_turkiye_bos.png")
        kaydet(eczane_raf(False), "eczane_raf_dolu.png")
    if on("hastane"):
        kaydet(hastane_odasi(), "../arka_hastane_odasi_cizim.jpg")
    if on("zemin4"):   # 4. tur zeminleri
        kaydet(koridor(), "../arka_koridor_cizim.jpg")
        kaydet(bakanlik_oda(), "../arka_bakanlik_oda_cizim.jpg")
        kaydet(eczane_zemin(), "../arka_eczane_cizim.jpg")
        kaydet(buro(), "../arka_buro_cizim.jpg")
        kaydet(doku_tebesir(), "../doku_tebesir.jpg")
        kaydet(doku_duz((178, 140, 98), 21, 0.07, 0.05), "../doku_karton.jpg")
        kaydet(doku_duz((206, 222, 210), 22, 0.04, 0.02, lambri=(900, (122, 162, 140))), "../doku_duvar_yesil.jpg")
        kaydet(doku_duz((152, 168, 186), 23, 0.05, 0.03), "../doku_kagit_mavi.jpg")
        kaydet(doku_ahsap(), "../doku_ahsap.jpg")
        kaydet(kanun_sayfasi(), "kanun_1262_sayfa.jpg")
        kaydet(gazete_2008(), "gazete_2008_canlandirma.png", trim=False)
    if on("hekim"):   # 6. tur
        kaydet(hekim_odasi(), "../arka_hekim_odasi_cizim.jpg")
    if on("doku"):
        kaydet(mantar_pano(), "../arka_mantar_pano.jpg")
        kaydet(kagit_doku(False), "../doku_kagit.jpg")
        kaydet(kagit_doku(True), "../doku_kagit_koyu.jpg")
    if on("takvim"):
        for ad, (g, a, y, gri) in {
            "aralik_1956": (None, "ARALIK", "1956", False), "eylul_1960": (None, "EYLÜL", "1960", False),
            "30_ekim_1961": ("30", "EKİM", "1961", True), "15_kasim_1961": ("15", "KASIM", "1961", False),
            "16_kasim_1961": ("16", "KASIM", "1961", False), "20_kasim_1961": ("20", "KASIM", "1961", False),
            "26_kasim_1961": ("26", "KASIM", "1961", False), "27_kasim_1961": ("27", "KASIM", "1961", False),
            "31_mayis_2004": ("31", "MAYIS", "2004", False), "1_ekim_1957": ("1", "EKİM", "1957", False),
        }.items():
            kaydet(takvim_yapragi(g, a, y, gri), f"takvim_{ad}.png")
    if on("simge"):
        kaydet(telefon_simge(), "telefon_simge.png")
        kaydet(zarf(False), "zarf.png")
        kaydet(zarf(True), "zarf_taahhutlu.png")
        kaydet(raptiye(), "raptiye.png")
        kaydet(buyutec(), "buyutec.png")
        kaydet(telefon_cerceve(), "telefon_cerceve.png", trim=False)
        kaydet(hap_simge(), "hap_simge.png")
        kaydet(gebelik_piktogram(), "gebelik_yasak_piktogram.png")


if __name__ == "__main__":
    hepsi(sys.argv[1:])
