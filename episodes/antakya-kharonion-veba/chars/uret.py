"""antakya-kharonion-veba: hazır kıyafetli iki karakter ve ters köşe yüz varyantı.

    python episodes/antakya-kharonion-veba/chars/uret.py

Kaynaklar (kaynak/ altında, tools/wojak_site.py get ile indirildiği gibi):
  koylu_kaynak.png    wojakland "Peasant Wojak" (https://wojakland.com/gmedia/peasant_wojak-png/), 552x667; düz MS-Paint,
                      kara takke, kahverengi tunik. Videoda adsız bir Antakyalı (A, solda).
  telestes_kaynak.png wojakland "Ancient Greece Chad" (https://wojakland.com/gmedia/ancient_greece_chad-png/), 439x463;
                      ak sakallı, defne taçlı yaşlı Yunan. Videoda Malalas'ın andığı tılsımcı Leios (B, sağda).
Kıyafete dokunulmaz. Yapılanlar:
  - koylu: yüzdeki üç çamur lekesi silindi (hastalık lekesi gibi okunmasın), yüzün gri fırça gölgesi düz beyaza çevrildi
    (siyah kontur ve kırışık çizgileri kalır); kaynağın üst kenarında kesik kalan takke tepesi kubbe olarak tamamlandı; 2x.
  - koylu_sok: el kitabı §10 tarifi (iri yuvarlak göz + küçük göz bebeği, iç ucu kalkık kaş, "O" ağız, alında mavi çizgi,
    başın önünde 3 damla).
  - telestes: 3x büyütme, başka değişiklik yok.
Bakış yönü dosyanın kendisine göre kaydedilir (python -m wojak yon ...); episode.yaml'da faces: yok.
Çizim yardımcıları hierapolis-cehennem-kapisi/chars/uret.py'den kopyalandı.
"""
from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
KAYNAK = HERE / "kaynak"
sys.path.insert(0, str(ROOT / "tools"))
import kit_varyant  # noqa: E402

SS = 4
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)
MAVI = (60, 120, 230, 255)


def poly_mask(size, pts) -> np.ndarray:
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).polygon([tuple(p) for p in pts], fill=255)
    return np.array(m) > 0


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
    a = np.array(im).astype(np.int32)
    m = (a[..., :3].sum(-1) < 240) & (a[..., 3] > 30)
    a[m, 3] = 255
    return Image.fromarray(a.astype(np.uint8))


def buyut(im, k):
    im = im.resize((im.width * k, im.height * k), Image.LANCZOS)
    rgb = im.convert("RGB").filter(ImageFilter.UnsharpMask(2, 60, 2))
    out = rgb.convert("RGBA")
    out.putalpha(im.getchannel("A"))
    return out


def kaydet(im, ad):
    out = HERE / f"{ad}.png"
    im.save(out, optimize=True)
    print(f"-> {out.relative_to(ROOT)}  {im.width}x{im.height}")


PAD = 14   # takke tepesi için üstte şeffaf pay (1x)
K = 2


def S(*v):
    """1x kaynak koordinatı -> 2x, üst pay dahil (x, y, [r])."""
    out = []
    for i, x in enumerate(v):
        out.append((x + (PAD if i == 1 else 0)) * K)
    return out


def koylu_sakin():
    im = kontur_sabitle(Image.open(KAYNAK / "koylu_kaynak.png").convert("RGBA"))
    a = np.array(im).astype(np.int32)
    rgb = a[..., :3]
    # çamur lekeleri: kahverengi bölge + kendi siyah konturu (yüz konturuna değmeyen poligonlar)
    for pts in ([(196, 128), (258, 128), (258, 232), (196, 232)],
                [(258, 243), (314, 243), (314, 304), (258, 304)],
                [(399, 236), (444, 236), (444, 266), (399, 266)]):
        m = poly_mask(im.size, pts) & (a[..., 3] > 0)
        a[m, :3] = 255
    # yüz/boyun gri fırça gölgesi -> düz beyaz (kontur ve orta-gri kırışıklar kalır)
    yuz = poly_mask(im.size, [(140, 95), (470, 95), (470, 440), (140, 440)])
    sat = rgb.max(-1) - rgb.min(-1)
    lum = rgb.mean(-1)
    m = yuz & (sat < 20) & (lum > 175) & (a[..., 3] > 0)
    a[m, :3] = 255
    im = Image.fromarray(a.astype(np.uint8))
    # silinen lekelerin geçtiği yerde yüz konturunu (sol yanak) ve sağ göz alt kapağını geri çiz
    c = Cizim(im, seed=5)
    c.cizgi([(250, 222), (262, 236), (276, 240)], 3)   # sol göz altındaki eski kırışık izi (hafif)
    im = c.im
    # üst pay + kesik takke tepesini kubbe olarak tamamla
    W, H = im.size
    can = Image.new("RGBA", (W, H + PAD), (0, 0, 0, 0))
    can.paste(im, (0, PAD))
    d = ImageDraw.Draw(can)
    d.ellipse([228, PAD - 9, 317, PAD + 9], fill=BLACK)
    im = buyut(can, K)
    # tur 1 görsel hakem SHOULD: yüz çizgileri kalın siyah olsun (şok varyantıyla aynı ağırlık). Yüz/boyun bölgesindeki
    # koyu ve orta-gri çizgi pikselleri siyaha, 2 px genişletilerek.
    a = np.array(im).astype(np.int32)
    yuz = np.zeros(a.shape[:2], bool)
    yuz[S(0, 90)[1]:S(0, 440)[1], S(140, 0)[0]:S(475, 0)[0]] = True
    rgb = a[..., :3]
    sat = rgb.max(-1) - rgb.min(-1)
    lum = rgb.mean(-1)
    cizgi = yuz & (sat < 40) & (lum < 175) & (a[..., 3] > 0)
    from scipy import ndimage
    goz = np.zeros_like(yuz)
    for x0, y0, x1, y1 in [(262, 192, 334, 246), (384, 196, 446, 248)]:   # gözler genişletilmez (göz bebeği büyümesin)
        X0, Y0, X1, Y1 = *S(x0, y0), *S(x1, y1)
        goz[Y0:Y1, X0:X1] = True
    lab, n = ndimage.label(cizgi)
    boy = ndimage.sum(cizgi, lab, range(1, n + 1))
    kirinti = np.isin(lab, 1 + np.nonzero(boy < 60)[0])          # göz kenarındaki gri kırıntılar silinir
    a[kirinti & ~goz, :3] = 255
    cizgi &= ~kirinti
    kalin = ndimage.binary_dilation(cizgi & ~goz, iterations=2) & yuz & ~goz & (a[..., 3] > 0)
    kalin |= cizgi & goz & (lum < 110)
    alfa = ndimage.gaussian_filter(kalin.astype(float), 0.9)        # kenar yumuşatma (tırtık kalmasın)
    alfa = np.clip(alfa * 1.6, 0, 1) * (a[..., 3] > 0)
    a[..., :3] = (a[..., :3] * (1 - alfa[..., None])).round().astype(np.int32)
    return Image.fromarray(a.astype(np.uint8))


def koylu_sok(im):
    """1x hatlar: sol göz merkezi ~(298,218), sağ göz ~(418,222); kaşlar y 190-205; ağız 318-400 x 336-350;
    alın y 120-175; sağ yüz konturu x ~460."""
    a = np.array(im).astype(np.int32)
    for x0, y0, x1, y1 in [(262, 186, 334, 246), (384, 192, 446, 248), (312, 330, 408, 360)]:
        X0, Y0, X1, Y1 = *S(x0, y0), *S(x1, y1)
        a[Y0:Y1, X0:X1, :3] = 255
    im = Image.fromarray(a.astype(np.uint8))
    c = Cizim(im, seed=13)
    w = 4.2 * K
    # iri yuvarlak gözler + küçük göz bebeği (dosyanın baktığı yöne, sağa)
    c.elips(*S(298, 219), 27 * K, 25 * K, dolgu=WHITE, w=w)
    c.elips(*S(419, 222), 22 * K, 23 * K, dolgu=WHITE, w=w)
    c.elips(*S(305, 220), 5.5 * K, 5.5 * K, dolgu=BLACK)
    c.elips(*S(425, 223), 5.0 * K, 5.0 * K, dolgu=BLACK)
    # iç ucu kalkık kalın kaşlar
    c.cizgi([tuple(S(266, 190)), tuple(S(288, 186)), tuple(S(308, 180)), tuple(S(326, 172))], 4.6 * K)
    c.cizgi([tuple(S(392, 172)), tuple(S(408, 178)), tuple(S(426, 184)), tuple(S(444, 190))], 4.6 * K)
    # "O" ağız
    c.elips(*S(360, 344), 15 * K, 18 * K, dolgu=(70, 18, 22, 255), w=4.0 * K)
    # alında düzensiz mavi çizgiler
    for x0, y0, x1 in [(300, 150, 342), (352, 146, 394), (318, 162, 356), (370, 160, 410), (284, 166, 312)]:
        c.cizgi([tuple(S(x0, y0)), tuple(S((x0 + x1) / 2, y0 - 2)), tuple(S(x1, y0 + 1))], 2.4 * K, renk=MAVI)
    # başın önünde (sağda), konturdan ~12 px (1x) uzakta 3 damla
    return ter(c.im, [tuple(S(482, 180, 10)), tuple(S(490, 222, 9)), tuple(S(484, 262, 8))])


def telestes():
    im = kontur_sabitle(Image.open(KAYNAK / "telestes_kaynak.png").convert("RGBA"))
    # tur 1 görsel hakem SHOULD: iki tonlu bej ten tek açık tona
    a = np.array(im).astype(np.int32)
    rgb = a[..., :3]
    sat = rgb.max(-1) - rgb.min(-1)
    ten = (rgb[..., 0] > 185) & (sat >= 12) & (sat <= 60) & (rgb[..., 0] > rgb[..., 2] + 10) & (a[..., 3] > 0)
    a[ten, :3] = (240, 226, 210)
    return buyut(Image.fromarray(a.astype(np.uint8)), 3)


KES = (540 + PAD) * K   # tur 1 görsel hakem SHOULD: omuz çizgisinin altından kes, yüz kadrajda büyüsün (el kitabı §10)


if __name__ == "__main__":
    s = koylu_sakin()
    kaydet(s.crop((0, 0, s.width, KES)), "koylu_sakin")
    o = koylu_sok(s.copy())
    kaydet(o.crop((0, 0, o.width, KES)), "koylu_sok")
    kaydet(telestes(), "telestes")
