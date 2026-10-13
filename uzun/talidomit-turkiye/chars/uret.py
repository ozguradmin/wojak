"""talidomit-turkiye uzun video karakterleri: kaynak PNG'lerden ve repo kitlerinden yeniden üretir.

    python uzun/talidomit-turkiye/chars/uret.py            # hepsi
    python uzun/talidomit-turkiye/chars/uret.py lenz kelsey  # yalnız bazıları

Senaryo: scratchpad senaryo_v2.md "Gerekli varlıklar §A". Kural: düz MS-Paint wojak ailesi, içeri bakış (hepsi sağa bakar;
motor gerekirse aynalar), kötü/sırıtan yüz yok, gerçek kişinin fotoğrafına benzetilmez (yalnız rol: gözlük, önlük, dönem).

Erkek karakterler (K, L, S, E) aynı klasik kafadan (assets/kit/klasik/sakin.png = kütüphane 5_Tired_Wojak/10441;
899x1022, sağa bakar) kurulur. Yüz varyantları aynı koordinatta:
  sakin      = klasik sakin
  gulumsuyor = assets/kit/ingiliz_er_1915_biyikli/taban_klasik_gulumsuyor.png (klasik gülümseyen, aynı kafa)
  ciddi      = klasik gözler + alçak, düz kalın kaşlar + düz sıkı ağız (bu betik çizer)
  dusunceli  = klasik gözler + bir kaş kalkık + kısa yana kaymış ağız (bu betik çizer)
  fark       = kalkık kavisli kaşlar + açık yuvarlak gözler, küçük göz bebeği + kısa düz ağız (bu betik çizer)
  saskin     = fark + küçük açık "o" ağız (bu betik çizer)
Her karakterin bütün varyantları AYNI tuvalde (motor aynı boyutlu varyantlara ortak kırpım uygular: kutu zıplamaz).
Tuval: taban 110 px yanlara, 130 px yukarı (saç hacmi), 230 px aşağı (gövde) genişletilir; gövde/önlük düz çizimle
yeniden çizilir (klasik omuz çizgileri önlüğün altında kalır).

  K  kaymakcalan_*  Şükrü Kaymakçalan rolü: 30'ların ortası, siyah, düzgün yandan ayrılmış saç, kalın siyah kemik gözlük,
                    beyaz önlük + beyaz gömlek + bordo kravat. sakin, dusunceli, ciddi, kollar (ciddi + kollar kavuşmuş;
                    K2 küçük resmi)
  L  lenz_*         Widukind Lenz rolü: kahverengi geriye taranmış saç (yüksek alın), ince yuvarlak gözlük, beyaz önlük +
                    açık mavi gömlek + lacivert kravat + stetoskop (çocuk doktoru). sakin, fark, ciddi, telefon (ciddi +
                    1960'lar siyah ahize, el ve kıvrık kablo), gazete (ciddi + adsız/logosuz gazete, iki el)
  S  sheskin_*      Jacob Sheskin rolü: kır, geri çekilmiş saç (yüksek alın), gözlüksüz, beyaz önlük + gri-mavi gömlek + koyu yeşil
                    kravat. sakin, saskin
  E  eczaci_sakin   1950'ler eczacısı: ortadan ayrılmış kır-kahve saç, geniş, uçları sarkık bıyık, beyaz önlük + bordo
                    papyon. Yalnız sakin (gülümseyen klasik yüz bıyığın altında üzgün okunuyordu).
Diğerleri:
  F  kelsey_*       Frances O. Kelsey rolü: kütüphane 5_Daddys_Girl/11087 "Secretary Daddy's Girl" (1960'lar ceket,
                    bluz, kabarık saç). Saç sarı -> koyu kahve, ceket pembe -> lacivert; bel altı kırpılır.
                    supheci = kaynağın kendi yüzü (düz dudak + aşağı kıvrık ağız + yanak çizgileri) + çatık sol kaş;
                    sakin = aşağı kıvrık ağız ve yanak çizgileri silinmiş, düz dudak. Gözlük yok (1960-62 fotoğraflarında
                    gözlüksüz).
  —  anne_adayi_sakin  1950'ler anne adayı: wojakland "Trad Wife" (yeşil çiçekli elbise, sakin yüz). Yüz değişimi yok.
  A  temsilci_notr  Kısa videonun A temsilcisi (episodes/talidomit-turkiye/chars/temsilci_gulumsuyor.png): gülümseme,
                    gamze ve alt dudak silinir, düz nötr ağız çizilir (gözler, şapka, takım aynı; aynı tuval 1243x1400).
  A2 temsilci2000_sakin  2000'ler adsız temsilci: wojakland "Grey Suit Wojak" (şapkasız, siyah saç, gri takım, açık
                    yaka); gömlek açık maviye boyanır (A'nın lacivert takım + fötr şapkasından ayrılsın).
Kaynak PNG'ler kaynak/ altında (adresleri VARLIKLAR.md'de).
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
SS = 3
LW = 9
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)

KLASIK = {
    "sakin": ROOT / "assets/kit/klasik/sakin.png",
    "gulumsuyor": ROOT / "assets/kit/ingiliz_er_1915_biyikli/taban_klasik_gulumsuyor.png",
}
PADX, PADT, EXT = 110, 130, 230         # tuval genişletmesi (taban koordinatına göre). PADT 40 -> 130 (3. hakem turu:
                                        # saçın tepe kabarıklığı tuvalin üstünden taşıp düz kesiliyordu)
CW, CH = 899 + 2 * PADX, 1022 + PADT + EXT


# ------------------------------------------------------------------------------------------------ çizim yardımcıları
def catmull(pts, n=16, closed=False):
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


def wob(pts, amp=0.8, seed=1):
    r = random.Random(seed)
    ph = r.random() * 6
    return [(x + amp * math.sin(i * 0.37 + ph) + r.uniform(-0.3, 0.3),
             y + amp * math.cos(i * 0.29 + ph) + r.uniform(-0.3, 0.3)) for i, (x, y) in enumerate(pts)]


class Kat:
    """Süper örneklenmiş çizim katmanı; koordinatlar TABAN düzleminde (ox, oy kaydırmasıyla tuvale)."""

    def __init__(self, w, h, ox=0, oy=0):
        self.w, self.h, self.ox, self.oy = w, h, ox, oy
        self.im = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)

    def P(self, pts):
        return [((x + self.ox) * SS, (y + self.oy) * SS) for x, y in pts]

    def poly(self, pts, fill):
        self.d.polygon(self.P(pts), fill=fill)

    def line(self, pts, w=LW, fill=BLACK, smooth=True, closed=False, seed=1, amp=0.7):
        p = catmull(pts, 12, closed) if smooth and len(pts) > 2 else (list(pts) + (pts[:1] if closed else []))
        if amp:
            p = wob(p, amp, seed)
        if closed and smooth and len(pts) > 2:
            p = p + p[:1]
        q = self.P(p)
        self.d.line(q, fill=fill, width=round(w * SS), joint="curve")
        r = w * SS / 2
        for x, y in (q[0], q[-1]):
            self.d.ellipse([x - r, y - r, x + r, y + r], fill=fill)

    def shape(self, pts, fill, w=LW, smooth=True, seed=1, amp=0.6):
        p = catmull(pts, 12, True) if smooth else list(pts)
        self.poly(p, fill)
        self.line(p + p[:1], w=w, smooth=False, seed=seed, amp=amp)

    def ellipse(self, cx, cy, rx, ry, fill=None, outline=BLACK, w=LW):
        b = [(cx - rx + self.ox) * SS, (cy - ry + self.oy) * SS, (cx + rx + self.ox) * SS, (cy + ry + self.oy) * SS]
        self.d.ellipse(b, fill=fill, outline=outline, width=round(w * SS) if outline else 0)

    def done(self):
        return self.im.resize((self.w, self.h), Image.LANCZOS)


def dil(m, r):
    if r > 12:  # büyük yarıçap: 4x küçültülmüş maskede genişlet (PIL MaxFilter büyük çekirdekte çok yavaş)
        H, W = m.shape
        im = Image.fromarray((m * 255).astype(np.uint8)).resize((W // 4 + 1, H // 4 + 1), Image.BOX)
        im = im.point(lambda v: 255 if v > 0 else 0).filter(ImageFilter.MaxFilter(2 * (r // 4) + 1))
        return np.array(im.resize((W, H), Image.BILINEAR)) > 127
    return np.array(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(2 * r + 1))) > 0


def ero(m, r):
    if r > 12:
        return ~dil(~m, r)
    return np.array(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(2 * r + 1))) > 0


def poly_mask(shape, pts):
    im = Image.new("L", (shape[1], shape[0]), 0)
    ImageDraw.Draw(im).polygon([tuple(p) for p in pts], fill=255)
    return np.array(im) > 0


def trim(im):
    return im.crop(im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox())


def blur_mask(m, r=1.2):
    """İkili maskeyi yumuşak kenarlı alfaya çevirir."""
    return np.array(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r))) / 255.0


# ------------------------------------------------------------------------------------------------ yüzler (taban 899x1022)
def _beyazla(a, mask):
    """Klasik tabanda maske içindeki koyu çizgileri beyaza boyar (yüzün içi)."""
    a = a.copy()
    lum = a[..., :3].mean(-1)
    m = mask & (a[..., 3] > 0) & (lum < 250)
    a[m, :3] = 255
    return a


BROW_EYE = [(400, 300), (600, 300), (690, 330), (840, 318), (848, 380), (835, 530), (700, 530), (690, 470),
            (600, 528), (400, 528)]
BROWS_ONLY = [(400, 300), (600, 300), (690, 318), (840, 318), (845, 395), (705, 412), (600, 395), (400, 405)]
MOUTH = [(525, 695), (760, 695), (760, 765), (525, 765)]


def yuz(tip: str) -> Image.Image:
    """Klasik kafada yüz varyantı (899x1022)."""
    if tip in KLASIK:
        return Image.open(KLASIK[tip]).convert("RGBA")
    a = np.array(Image.open(KLASIK["sakin"]).convert("RGBA")).astype(np.int32)
    H, W = a.shape[:2]
    if tip in ("fark", "saskin"):
        a = _beyazla(a, poly_mask((H, W), BROW_EYE))
    else:
        a = _beyazla(a, poly_mask((H, W), BROWS_ONLY))
    a = _beyazla(a, poly_mask((H, W), MOUTH))
    im = Image.fromarray(a.astype(np.uint8))
    k = Kat(W, H)
    if tip == "ciddi":
        # alçak, düz, kalın kaşlar (iç uçları hafif aşağı: kararlı, kızgın değil)
        k.line([(418, 352), (480, 345), (540, 350), (585, 362)], w=13, seed=3)
        k.line([(700, 364), (745, 352), (790, 348), (818, 352)], w=13, seed=4)
        # düz sıkı ağız, uçlarda çok hafif aşağı
        k.line([(552, 734), (600, 728), (660, 727), (712, 729), (738, 737)], w=10, seed=5)
    elif tip == "dusunceli":
        k.line([(420, 345), (480, 338), (540, 340), (582, 350)], w=11, seed=6)          # sol kaş düz
        k.line([(700, 330), (735, 305), (780, 298), (816, 312)], w=11, seed=7)          # sağ kaş kalkık
        k.line([(598, 734), (640, 731), (680, 726), (706, 718)], w=10, seed=8)          # kısa, sağa yükselen ağız
        k.line([(700, 708), (712, 716), (708, 728)], w=7, seed=9)                       # ağız ucu kıvrımı
    elif tip in ("fark", "saskin"):
        k.line([(418, 318), (455, 282), (505, 268), (552, 278), (584, 300)], w=11, seed=10)  # kalkık kavisli kaşlar
        k.line([(702, 300), (735, 276), (775, 270), (812, 286)], w=11, seed=11)
        # açık yuvarlak gözler + küçük göz bebekleri (karşıya/sağa bakar)
        k.ellipse(505, 458, 64, 44, fill=WHITE, w=10)
        k.ellipse(768, 462, 50, 40, fill=WHITE, w=10)
        k.ellipse(522, 458, 15, 15, fill=BLACK, outline=None)
        k.ellipse(782, 462, 13, 13, fill=BLACK, outline=None)
        # göz altı çizgisi (klasik yorgunluk, hafif)
        k.line([(470, 518), (505, 524), (540, 516)], w=6, seed=12)
        k.line([(740, 516), (768, 521), (795, 514)], w=6, seed=13)
        if tip == "fark":
            k.line([(590, 735), (640, 731), (690, 733)], w=10, seed=14)
        else:
            k.ellipse(640, 738, 24, 30, fill=(45, 30, 30, 255), w=9)
    else:
        raise ValueError(tip)
    im.alpha_composite(k.done())
    return im


# ------------------------------------------------------------------------------------------------ saç
_HEAD = None


def kafa_maskesi():
    """Klasik kafanın (taban) opak alanı, tuval koordinatında."""
    global _HEAD
    if _HEAD is None:
        a = np.array(Image.open(KLASIK["sakin"]).convert("RGBA"))[..., 3] > 128
        m = np.zeros((CH, CW), bool)
        m[PADT:PADT + 1022, PADX:PADX + 899] = a
        m[PADT + 880:] = False          # yalnız kafa (omuzlar hariç)
        _HEAD = m
    return _HEAD


def _yumusat(m, r=8):
    """İkili maskenin köşelerini yuvarlar (bulanıklaştır + eşikle)."""
    return blur_mask(m, r) > 0.5


_SAC = {}


def _sac_maskesi(hairline, hacim, tepe, kel, tutam=(26, 12, 24)):
    head = kafa_maskesi()
    H, W = head.shape
    yy, xx = np.mgrid[0:H, 0:W]
    big = dil(head, hacim)
    if tepe:
        top = (yy < PADT + 250) & (xx > PADX + 220) & (xx < PADX + 840)
        big |= dil(head, hacim + tepe) & top
    # tutam tutam kabarık üst kenar: başın üst konturu boyunca rastgele daireler (düz kask görünmesin)
    rng = random.Random(len(str(hairline)) + hacim)
    edge = big & ~ero(big, 3)
    ys, xs = np.where(edge & (yy < PADT + 330))
    bump = Image.new("L", (W, H), 0)
    bd = ImageDraw.Draw(bump)
    if len(xs):
        n, r0, r1 = tutam
        for i in rng.sample(range(len(xs)), min(n, len(xs))):
            r = rng.uniform(r0, r1)
            bd.ellipse([xs[i] - r, ys[i] - r, xs[i] + r, ys[i] + r], fill=255)
    big = big | (np.array(bump) > 0)
    big = _yumusat(big, 5)
    if kel:
        band = big & ~ero(head, 64)
        back = band & (xx < PADX + 300) & (yy > PADT + 130) & (yy < PADT + 560)
        temple = band & (xx > PADX + 800) & (yy > PADT + 230) & (yy < PADT + 380)
        m = _yumusat(back | temple, 6)
    else:
        hl = [(x + PADX, y + PADT) for x, y in catmull(hairline, 14)]
        pts = [(hl[0][0] - 400, hl[0][1])] + hl + [(hl[-1][0] + 400, hl[-1][1]), (W + 400, -10), (-400, -10)]
        m = big & poly_mask((H, W), pts)
        # ense: kulak hizasının üstünde eğik kesilir (kask kenarı gibi aşağı inmesin)
        m &= ~poly_mask((H, W), [(0, PADT + 420), (PADX + 175, PADT + 360), (PADX + 215, PADT + 470),
                                  (PADX + 230, H), (0, H)])
    return m


def sac(canvas: Image.Image, hairline, renk, hacim=22, tepe=44, teller=(), parlak=None, seed=1, kel=False,
        tutam=(26, 12, 24)):
    """Kafanın tepesine düz dolgulu saç (MS-Paint: düz renk + siyah kontur + birkaç tel + bir parlama şeridi).
    hairline: taban koordinatında (x, y) noktaları soldan sağa; saç bu çizginin ÜSTÜNDE kalır.
    hacim: kafa konturunun yanlarda kaç px dışına taşar; tepe: başın üstünde ek kabarıklık.
    kel=True: tepe açık, yalnız ense/yan (at nalı) + sağ şakakta küçük tutam."""
    key = (str(hairline), hacim, tepe, kel, tutam)
    m = _SAC.get(key)
    if m is None:
        m = _SAC[key] = _sac_maskesi(hairline, hacim, tepe, kel, tutam)
    H, W = m.shape
    a = np.array(canvas).astype(np.float32)
    al = blur_mask(m, 1.0)[..., None]
    col = np.array(renk[:3], np.float32)
    a[..., :3] = a[..., :3] * (1 - al) + col * al
    a[..., 3] = np.maximum(a[..., 3], al[..., 0] * 255)
    out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    k = Kat(CW, CH, PADX, PADT)
    if parlak:                                     # parlama şeridi (saçın kendi renginden açık)
        pr, pts = parlak
        k.line(pts, w=20, fill=pr, seed=seed + 50, amp=0.5)
    for i, t in enumerate(teller):
        k.line(t, w=5, seed=seed + i, amp=0.4)
    lay = k.done()
    # parlama ve teller saçın dışına taşmasın
    la = np.array(lay)
    la[..., 3] = (la[..., 3] * ero(m, 6)).astype(np.uint8)
    out.alpha_composite(Image.fromarray(la))
    # siyah kontur (saçın bütün kenarı)
    a = np.array(out).astype(np.float32)
    edge = m & ~ero(m, 9)
    ea = blur_mask(edge, 0.9)[..., None]
    a[..., :3] = a[..., :3] * (1 - ea)
    a[..., 3] = np.maximum(a[..., 3], ea[..., 0] * 255)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


# ------------------------------------------------------------------------------------------------ gözlük
def gozluk(canvas, tip):
    k = Kat(CW, CH, PADX, PADT)
    if tip == "kemik":       # kalın siyah dikdörtgen (K)
        w = 14
        L = [(420, 404), (598, 400), (602, 470), (585, 520), (440, 524), (418, 480)]
        R = [(690, 408), (838, 410), (842, 470), (826, 518), (704, 520), (688, 470)]
        k.line(L, w=w, closed=True, seed=21, amp=0.4)
        k.line(R, w=w, closed=True, seed=22, amp=0.4)
        k.line([(600, 432), (645, 420), (690, 432)], w=12, seed=23)          # köprü
        k.line([(420, 420), (300, 418), (190, 430)], w=11, seed=24)           # sap (kulağa)
        k.line([(840, 425), (868, 430)], w=10, seed=25)
    elif tip == "yuvarlak":  # ince yuvarlak (L)
        k.ellipse(508, 462, 80, 72, w=8)
        k.ellipse(770, 466, 62, 68, w=8)
        k.line([(588, 448), (630, 434), (708, 450)], w=8, seed=26)
        k.line([(430, 445), (300, 440), (192, 448)], w=7, seed=27)
        k.line([(832, 452), (870, 456)], w=7, seed=28)
    canvas.alpha_composite(k.done())
    return canvas


# ------------------------------------------------------------------------------------------------ gövde / önlük
COAT = (247, 247, 245, 255)
SKIN = (255, 255, 255, 255)
NECK_L, NECK_R = 236, 662      # klasik boyun çizgileri (taban x), y ~ 880'de


def govde(canvas, gomlek=(255, 255, 255, 255), kravat=(120, 30, 40, 255), tip="onluk", seed=30):
    """Klasik omuzların üstüne yeniden çizilen gövde: boyun + gömlek yakası + kravat + beyaz önlük (yakalı)."""
    k = Kat(CW, CH, PADX, PADT)
    yb = 1022 + EXT + 5         # tuvalin altı (taban y)
    # 1) gövde silüeti (önlük rengi): boyun dibinden omuzlara, yanlarda kol çizgisi olarak aşağı iner
    torso = [(NECK_L, 840), (205, 880), (150, 925), (40, 965), (-50, 1010), (-92, 1090), (-100, yb), (1005, yb),
             (995, 1080), (950, 995), (850, 950), (740, 925), (NECK_R + 6, 895), (NECK_R, 860)]
    k.poly(torso, COAT)
    k.line(torso[1:-1], w=LW, smooth=False, seed=seed, amp=0.6)
    # 2) boyun (ten): klasik boyun çizgilerinin arası
    k.poly([(NECK_L + 4, 760), (NECK_R - 2, 850), (NECK_R - 6, 960), (NECK_L + 10, 960)], SKIN)
    # 3) gömlek V'si (reverslerin arası) + kravat + yaka
    # üst kenar yaka uçlarının üst çizgisini izler (3. hakem turu: düz yatay üst kenar renkli gömlekte boyunda sert
    # bir dikiş gibi görünüyordu); yakaların arası kravat düğümünün altında kalır
    V = [(250, 905), (468, 958), (505, 950), (548, 958), (650, 912), (640, 1020), (575, 1110), (518, 1215), (472, 1215),
         (330, 1080), (250, 1000)]
    k.poly(V, gomlek)
    if kravat == "papyon":
        k.shape([(440, 952), (492, 975), (440, 1000)], (110, 28, 38, 255), w=7, seed=seed + 1, smooth=False)
        k.shape([(548, 950), (496, 975), (548, 1002)], (110, 28, 38, 255), w=7, seed=seed + 2, smooth=False)
        k.ellipse(494, 976, 14, 14, fill=(110, 28, 38, 255), w=6)
        for y in (1060, 1130):
            k.ellipse(496 + (y - 1000) * 0.02, y, 9, 9, fill=(225, 225, 225, 255), w=5)
    elif kravat:
        k.shape([(470, 962), (540, 960), (532, 1008), (478, 1010)], kravat, w=8, seed=seed + 1)
        k.shape([(482, 1008), (530, 1006), (552, 1150), (507, 1205), (462, 1150)], kravat, w=8, seed=seed + 2)
    k.shape([(256, 904), (468, 958), (436, 1032)], gomlek, w=8, seed=seed + 3, smooth=False)
    k.shape([(646, 912), (548, 958), (588, 1036)], gomlek, w=8, seed=seed + 4, smooth=False)
    # 4) revers kenarları ve önlüğün önden kapanması
    k.line([(250, 905), (250, 1000), (330, 1080), (472, 1215), (480, yb)], w=LW, smooth=False, seed=seed + 5)
    k.line([(650, 912), (640, 1020), (575, 1110), (518, 1215), (512, yb)], w=LW, smooth=False, seed=seed + 6)
    k.line([(250, 1000), (292, 1052), (318, 1042)], w=7, smooth=False, seed=seed + 7)        # revers çentikleri
    k.line([(640, 1020), (604, 1072), (582, 1062)], w=7, smooth=False, seed=seed + 8)
    if tip == "onluk":
        # göğüs cebi + kalem (sağ)
        k.line([(660, 1190), (790, 1180)], w=7, smooth=False, seed=seed + 9)
        k.line([(720, 1186), (723, 1140)], w=6, smooth=False, seed=seed + 10)
        k.ellipse(723, 1136, 7, 7, fill=BLACK, outline=None)
    canvas.alpha_composite(k.done())
    return canvas


def stetoskop(canvas, seed=40):
    k = Kat(CW, CH, PADX, PADT)
    grey = (70, 70, 74, 255)
    k.line([(300, 940), (250, 980), (240, 1060), (300, 1140), (330, 1180)], w=12, fill=grey, seed=seed)
    k.line([(600, 950), (650, 990), (670, 1070), (640, 1150)], w=12, fill=grey, seed=seed + 1)
    k.ellipse(640, 1172, 26, 26, fill=(190, 190, 195, 255), w=7)
    k.ellipse(330, 1196, 12, 12, fill=grey, outline=None)
    canvas.alpha_composite(k.done())
    return canvas


def biyik(canvas, renk=(96, 86, 80, 255), seed=50):
    """Geniş, uçları aşağı sarkan dolgun bıyık (ağız genişliğini aşar; kısa/küt 'blok' bıyık ASLA)."""
    k = Kat(CW, CH, PADX, PADT)
    pts = [(648, 660), (700, 655), (748, 666), (780, 694), (786, 726), (766, 724), (742, 700), (700, 690),
           (650, 694), (600, 692), (560, 702), (528, 728), (510, 730), (514, 700), (548, 670), (598, 658)]
    k.shape(pts, renk, w=8, seed=seed)
    k.line([(560, 690), (600, 680), (646, 682)], w=5, seed=seed + 1)
    k.line([(660, 680), (705, 676), (745, 690)], w=5, seed=seed + 2)
    canvas.alpha_composite(k.done())
    return canvas


def el(k, pts, seed):
    """Düz beyaz el (eldiven gibi) + kontur."""
    k.shape(pts, SKIN, w=8, seed=seed)


def telefon(canvas, seed=60):
    """1960'lar siyah ahize, sol yanakta (yakın kulak), el ve önlük kolu; kıvrık kablo."""
    k = Kat(CW, CH, PADX, PADT)
    yb = 1022 + EXT + 5
    dark = (38, 38, 40, 255)
    # kol (önlük kolu) aşağıdan yukarı
    sleeve = [(-100, yb), (-100, 1000), (150, 820), (300, 860), (180, 1000), (90, yb)]
    k.shape(sleeve, COAT, seed=seed, smooth=False)
    # kablo
    cpts = []
    for i in range(40):
        t = i / 39
        x = 330 + (-60 - 330) * t + 18 * math.sin(t * 40)
        y = 830 + (yb - 830) * t + 10 * math.cos(t * 40)
        cpts.append((x, y))
    k.line(cpts, w=7, fill=dark, smooth=False, seed=seed + 1, amp=0)
    # ahize: kulaklık, sap, ağızlık
    k.shape([(130, 470), (230, 450), (262, 520), (170, 560)], dark, w=7, seed=seed + 2)
    k.shape([(200, 520), (250, 500), (420, 770), (370, 800)], dark, w=7, seed=seed + 3, smooth=False)
    k.shape([(330, 770), (430, 740), (452, 820), (352, 850)], dark, w=7, seed=seed + 4)
    # el: sapı kavrayan yumruk
    hand = [(200, 640), (260, 600), (330, 640), (345, 700), (300, 760), (230, 770), (180, 720)]
    el(k, hand, seed + 5)
    for (x0, y0, x1, y1) in ((262, 640, 318, 668), (255, 675, 320, 700), (250, 708, 312, 730)):
        k.line([(x0, y0), (x1, y1)], w=6, smooth=False, seed=seed + 6)
    canvas.alpha_composite(k.done())
    return canvas


def gazete(canvas, seed=70):
    """Göğüs hizasında iki elle tutulan adsız gazete (gerçek ad/logo yok)."""
    k = Kat(CW, CH, PADX, PADT)
    yb = 1022 + EXT + 5
    paper = (238, 234, 220, 255)
    ink = (40, 40, 40, 255)
    pg = [(70, 985), (840, 960), (880, yb), (40, yb)]
    k.poly(pg, paper)
    k.line(pg + pg[:1], w=LW, smooth=False, seed=seed, amp=0.6)
    k.line([(458, 975), (468, yb)], w=5, smooth=False, seed=seed + 1)            # orta kıvrım
    # manşet bloğu + sütunlar (okunamaz "yazı" çizgileri)
    k.poly([(110, 1010), (800, 992), (802, 1040), (112, 1058)], ink)
    for c0, c1 in ((110, 440), (490, 820)):
        for j in range(5):
            y = 1080 + j * 32
            k.line([(c0, y - (c0 - 100) * 0.03), (c1 - (j % 2) * 60, y - (c1 - 100) * 0.03)], w=7, smooth=False,
                   fill=(120, 120, 120, 255), seed=seed + 2 + j, amp=0)
    # eller üst köşelerde (başparmak önde)
    el(k, [(40, 960), (110, 945), (140, 1000), (120, 1060), (60, 1070), (30, 1020)], seed + 9)
    el(k, [(790, 940), (860, 930), (895, 985), (880, 1045), (815, 1050), (785, 1000)], seed + 10)
    canvas.alpha_composite(k.done())
    return canvas


def kollar(canvas, seed=80):
    """Göğüste kavuşturulmuş kollar (önlük kolları + iki el)."""
    k = Kat(CW, CH, PADX, PADT)
    yb = 1022 + EXT + 5
    # arkadaki kol: dirsek solda (aşağıda), bilek sağda yukarıda; eli karşı pazıyı kavrar
    a1 = [(-80, 1150), (-40, 1110), (300, 1070), (760, 1012), (790, 1104), (330, 1180), (-80, 1262)]
    k.shape(a1, COAT, seed=seed, smooth=False)
    k.line([(752, 1014), (782, 1104)], w=8, smooth=False, seed=seed + 4)           # manşet
    el(k, [(772, 1010), (850, 990), (915, 1015), (925, 1085), (878, 1122), (800, 1105)], seed + 1)
    k.line([(845, 1012), (905, 1032)], w=6, smooth=False, seed=seed + 6)             # parmak çizgileri
    k.line([(842, 1048), (910, 1066)], w=6, smooth=False, seed=seed + 7)
    # öndeki kol: dirsek sağda (aşağıda), bilek solda yukarıda; çapraz (X) üstte
    a2 = [(1005, 1160), (960, 1118), (620, 1078), (205, 1035), (185, 1132), (600, 1180), (1005, 1262)]
    k.shape(a2, COAT, seed=seed + 2, smooth=False)
    k.line([(212, 1036), (192, 1132)], w=8, smooth=False, seed=seed + 5)           # manşet
    el(k, [(200, 1030), (125, 1012), (62, 1045), (55, 1120), (110, 1160), (185, 1140)], seed + 3)
    k.line([(80, 1060), (150, 1050)], w=6, smooth=False, seed=seed + 8)
    k.line([(76, 1095), (146, 1088)], w=6, smooth=False, seed=seed + 9)
    k.line([(820, 1140), (860, 1180), (850, 1230)], w=6, seed=seed + 10)           # dirsek kıvrımları
    k.line([(70, 1190), (30, 1225)], w=6, seed=seed + 11)
    canvas.alpha_composite(k.done())
    return canvas


# ------------------------------------------------------------------------------------------------ erkek karakter kurulumu
def tuval(yuz_im):
    c = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    a = np.array(yuz_im)
    a[880:, ..., 3] = np.where(np.arange(880, 1022)[:, None] < 0, a[880:, ..., 3], a[880:, ..., 3])
    c.alpha_composite(Image.fromarray(a), (PADX, PADT))
    return c


HAIR = {
    # yandan ayrılmış, sağa taranmış siyah saç; alnın üstünde kıvrık perçem tutamları
    "kaymakcalan": dict(
        hairline=[(150, 520), (172, 430), (205, 330), (255, 252), (325, 206), (400, 214), (470, 204), (540, 198),
                  (585, 236), (612, 210), (655, 246), (690, 222), (750, 238), (810, 262), (856, 306), (892, 372)],
        renk=(26, 24, 24, 255), hacim=22, tepe=46, tutam=(30, 7, 12),
        teller=[[(326, 206), (300, 120), (262, 40)], [(352, 160), (500, 120), (660, 150), (760, 200)],
                [(360, 90), (520, 58), (680, 92)]],
        parlak=((78, 78, 84, 255), [(420, 40), (560, 28), (700, 70)])),
    # geriye taranmış kahverengi saç, yüksek alın, hafif dul tepesi
    "lenz": dict(
        hairline=[(150, 520), (170, 430), (198, 330), (240, 252), (300, 190), (370, 152), (440, 140), (488, 162),
                  (520, 142), (590, 140), (660, 150), (735, 178), (805, 225), (855, 290), (890, 362)],
        renk=(96, 66, 44, 255), hacim=22, tepe=40,
        teller=[[(640, 120), (500, 84), (330, 120), (240, 220)], [(560, 145), (440, 118), (300, 180)]],
        parlak=((150, 110, 78, 255), [(380, 40), (520, 26), (650, 60)])),
    # çok geri çekilmiş kır saç: tepede seyrek, alın çok yüksek
    "sheskin": dict(
        hairline=[(150, 520), (168, 420), (192, 320), (228, 236), (285, 170), (350, 128), (420, 112), (470, 126),
                  (520, 110), (590, 108), (665, 124), (740, 160), (808, 212), (858, 284), (892, 360)],
        renk=(192, 192, 190, 255), hacim=18, tepe=24, tutam=(22, 9, 16),
        teller=[[(300, 150), (240, 240), (205, 330)], [(600, 70), (460, 60), (340, 110)]],
        parlak=((222, 222, 220, 255), [(380, 30), (500, 16)])),
    # 4. tur: Ralf Voss rolü (1959'da firmayı uyaran nörolog): yandan ayrılmış kumral-sarı saç, gözlüksüz
    "voss": dict(
        hairline=[(150, 520), (172, 430), (205, 330), (255, 252), (325, 206), (400, 214), (470, 204), (540, 198),
                  (585, 236), (612, 210), (655, 246), (690, 222), (750, 238), (810, 262), (856, 306), (892, 372)],
        renk=(196, 162, 96, 255), hacim=20, tepe=40, tutam=(26, 7, 12),
        teller=[[(326, 206), (300, 120), (262, 40)], [(352, 160), (500, 120), (660, 150), (760, 200)]],
        parlak=((226, 200, 140, 255), [(420, 40), (560, 28), (700, 70)])),
    # ortadan ayrılmış, yağla taranmış kır-kahve saç
    "eczaci": dict(
        hairline=[(150, 520), (172, 430), (205, 330), (265, 248), (360, 200), (455, 186), (500, 205), (545, 186),
                  (640, 196), (720, 214), (800, 252), (854, 306), (890, 374)],
        renk=(118, 108, 100, 255), hacim=20, tepe=36, tutam=(26, 8, 14),
        teller=[[(500, 205), (488, 110), (470, 25)], [(470, 160), (360, 150), (270, 230)],
                [(530, 160), (650, 160), (760, 220)]],
        parlak=((160, 150, 142, 255), [(300, 90), (420, 40)])),
}
def erkek(ad, yuz_tipi, gozluk_tipi=None, govde_kw=None, ekler=()):
    im = tuval(yuz(yuz_tipi))
    im = govde(im, **(govde_kw or {}))
    for e in ekler:
        if e == "stetoskop":
            im = stetoskop(im)
        elif e == "biyik":
            im = biyik(im)
    im = sac(im, **HAIR[ad])
    if gozluk_tipi:
        im = gozluk(im, gozluk_tipi)
    return im


def kaydet(im, ad, yon="sag"):
    """PNG'yi yazar ve bakışını data/karakter_yon.json'a kaydeder. Bütün karakterler 3/4 profilde SAĞA bakar
    (her biri gözle kontrol edildi; motor sağdaki karakteri aynalar). Aynı dosyanın eski sha1 girdisi silinir."""
    p = HERE / f"{ad}.png"
    im.save(p, optimize=True)
    sys.path.insert(0, str(ROOT))
    import json
    from wojak import facing
    reg = facing._load()
    rel = str(p.relative_to(ROOT))
    stale = [k for k, v in reg.items() if v.get("file") == rel]
    if stale:
        for k in stale:
            reg.pop(k)
        facing.REGISTRY.write_text(json.dumps(reg, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    facing.register(p, yon)
    print(f"{rel} {im.size} bakış={yon}")
    return p


def kazak(canvas, renk=(214, 150, 62, 255), seed=120):
    """Anlatıcı (izleyicinin yerine geçen 'feels guy'): hardal rengi bisiklet yaka kazak (önlük/takım yok). Klasik
    omuz çizgisi kazağın altında kalır; boyun bandı iki çizgi."""
    k = Kat(CW, CH, PADX, PADT)
    yb = 1022 + EXT + 5
    torso = [(NECK_L, 840), (205, 880), (150, 925), (40, 965), (-50, 1010), (-92, 1090), (-100, yb), (1005, yb),
             (995, 1080), (950, 995), (850, 950), (740, 925), (NECK_R + 6, 895), (NECK_R, 860)]
    k.poly(torso, renk)
    k.line(torso[1:-1], w=LW, smooth=False, seed=seed, amp=0.6)
    k.poly([(NECK_L + 4, 760), (NECK_R - 2, 850), (NECK_R - 6, 935), (NECK_L + 10, 935)], SKIN)   # boyun
    koyu = tuple(int(c * 0.78) for c in renk[:3]) + (255,)
    yaka = [(NECK_L - 6, 900), (330, 958), (450, 978), (560, 972), (NECK_R + 10, 918)]
    alt = [(NECK_L + 4, 940), (330, 1000), (450, 1022), (560, 1016), (NECK_R + 4, 960)]
    k.poly(yaka + alt[::-1], koyu)
    k.line(yaka, w=LW, seed=seed + 1)
    k.line(alt, w=7, seed=seed + 2)
    for x in range(260, 660, 46):   # örgü çizgileri (yaka bandı)
        k.line([(x, 912 + (x - 260) * 0.12), (x + 6, 958 + (x - 260) * 0.1)], w=4, fill=(0, 0, 0, 120), seed=seed + x,
               smooth=False, amp=0.3)
    canvas.alpha_composite(k.done())
    return canvas


KIT = ROOT / "assets/kit/klasik"


def anlatici():
    """4. tur: bilgi sahnelerinde (harita, sayaç, pano, belge) köşeden tepki veren anlatıcı/izleyici wojak. Klasik kafa
    (saçsız), hardal kazak. Yüzler aynı tuvalde: sakin, dusunceli, ciddi, fark, saskin (bu betik) + terli, gozyasli
    (assets/kit/klasik, aynı 899x1022 taban)."""
    for v in ("sakin", "dusunceli", "ciddi", "fark", "saskin"):
        kaydet(kazak(tuval(yuz(v))), f"anlatici_{v}")
    for v in ("terli", "gozyasli"):
        kaydet(kazak(tuval(Image.open(KIT / f"{v}.png").convert("RGBA"))), f"anlatici_{v}")


def voss():
    """4. tur: Ralf Voss rolü (nörolog, 1959'da firmayı sinir hasarı konusunda uyaran hekim): kumral-sarı saç,
    gözlüksüz, beyaz önlük + açık gri gömlek + lacivert kravat. sakin, ciddi."""
    kw = dict(gomlek=(228, 230, 234, 255), kravat=(40, 52, 92, 255))
    for v in ("sakin", "ciddi"):
        kaydet(erkek("voss", v, None, kw), f"voss_{v}")


def kaymakcalan():
    kw = dict(gomlek=(255, 255, 255, 255), kravat=(120, 30, 40, 255))
    for v in ("sakin", "dusunceli", "ciddi"):
        kaydet(erkek("kaymakcalan", v, "kemik", kw), f"kaymakcalan_{v}")
    kaydet(kollar(erkek("kaymakcalan", "ciddi", "kemik", kw)), "kaymakcalan_kollar")


def lenz():
    kw = dict(gomlek=(206, 224, 242, 255), kravat=(34, 44, 78, 255))
    for v in ("sakin", "fark", "ciddi"):
        kaydet(erkek("lenz", v, "yuvarlak", kw, ("stetoskop",)), f"lenz_{v}")
    kaydet(telefon(erkek("lenz", "ciddi", "yuvarlak", kw, ("stetoskop",))), "lenz_telefon")
    kaydet(gazete(erkek("lenz", "ciddi", "yuvarlak", kw, ("stetoskop",))), "lenz_gazete")


def sheskin():
    kw = dict(gomlek=(214, 222, 228, 255), kravat=(40, 80, 52, 255))
    for v in ("sakin", "saskin"):
        kaydet(erkek("sheskin", v, None, kw), f"sheskin_{v}")


def eczaci():
    kw = dict(tip="eczaci", gomlek=(255, 255, 255, 255), kravat="papyon")
    kaydet(erkek("eczaci", "sakin", None, kw, ("biyik",)), "eczaci_sakin")


# ------------------------------------------------------------------------------------------------ Kelsey (F)
def kelsey():
    src = np.array(Image.open(KAYNAK / "kelsey_kaynak_secretary.png").convert("RGBA")).astype(np.int32)
    H, W = src.shape[:2]
    rgb = src[..., :3]

    def near(c, tol=40):
        return np.abs(rgb - np.array(c)).sum(-1) < tol

    a = src.copy()
    # saç sarı -> koyu kahve; ceket pembe -> lacivert (kenar yumuşatma pikselleri renk oranıyla)
    for c0, c1 in (((250, 217, 150), (78, 56, 44)), ((243, 103, 132), (52, 58, 84))):
        m = near(c0, 60) & (src[..., 3] > 0)
        a[m, :3] = c1
        # kontur ile dolgu arası ara tonlar: dolguya uzaklığa göre karıştır
        mid = dil(m, 2) & ~m & (src[..., 3] > 0) & (rgb.mean(-1) > 40) & (rgb.mean(-1) < 235) & \
            (np.abs(rgb - np.array(c0)).sum(-1) < 400) & ((rgb.max(-1) - rgb.min(-1)) > 25)
        lum0 = np.array(c0).mean()
        f = np.clip(rgb[mid].mean(-1) / lum0, 0, 1)[:, None]
        a[mid, :3] = (np.array(c1) * f).astype(np.int32)
    # bel altı kırpılır (yüz daha büyük görünsün)
    a = a[:1090]
    sup = Image.fromarray(a.astype(np.uint8))
    # şüpheci: çatık sol kaş (iç ucu aşağı) + sağ kaş hafif kalkık
    k = Kat(W, 1090)
    k.line([(520, 338), (560, 334), (605, 344), (632, 356)], w=9, seed=91)
    k.line([(752, 338), (785, 326), (822, 330)], w=8, seed=92)
    supheci = sup.copy()
    supheci.alpha_composite(k.done())
    # sakin: aşağı kıvrık ağız ve yanak çizgileri silinir, kaşlar sakin
    b = a.copy()
    lum = src[:1090, :, :3].mean(-1)          # kaynak parlaklığı (orada saç sarı, çizgiler siyah)
    hh, ww = b.shape[:2]
    face = poly_mask((hh, ww), [(500, 560), (795, 560), (795, 660), (500, 660)])
    lipline = poly_mask((hh, ww), [(555, 588), (790, 588), (790, 612), (555, 612)])
    erase = face & ~lipline & (lum < 200)
    b[erase, :3] = 255
    sakin = Image.fromarray(b.astype(np.uint8))
    k = Kat(W, 1090)
    k.line([(522, 340), (565, 332), (612, 336)], w=8, seed=93)
    k.line([(752, 336), (790, 330), (824, 336)], w=8, seed=94)
    sakin.alpha_composite(k.done())
    kaydet(sakin, "kelsey_sakin")
    kaydet(supheci, "kelsey_supheci")
    # 4. tur (izlenme hakemi S5): kararlı/sert yüz ("Onay da vermiyor."): iki kaş da alçak ve içe eğik, düz dudak
    k = Kat(W, 1090)
    k.line([(518, 346), (560, 344), (600, 352), (632, 364)], w=10, seed=95)
    k.line([(750, 360), (782, 346), (822, 342)], w=10, seed=96)
    kararli = Image.fromarray(b.astype(np.uint8))
    kararli.alpha_composite(k.done())
    kaydet(kararli, "kelsey_kararli")


# ------------------------------------------------------------------------------------------------ anne adayı, A2, A nötr
def anne():
    im = Image.open(KAYNAK / "anne_kaynak_tradwife.png").convert("RGBA")
    kaydet(trim(im), "anne_adayi_sakin")


def temsilci2000():
    im = Image.open(KAYNAK / "temsilci2000_kaynak_greysuit.png").convert("RGBA")
    kaydet(trim(im), "temsilci2000_sakin")


def temsilci_notr():
    src = Image.open(ROOT / "episodes/talidomit-turkiye/chars/temsilci_gulumsuyor.png").convert("RGBA")
    a = np.array(src).astype(np.int32)
    H, W = a.shape[:2]
    lum = a[..., :3].mean(-1)
    dark = lum < 252
    face_white = lum > 230
    nose = poly_mask((H, W), [(735, 585), (800, 585), (905, 640), (920, 735), (800, 752), (735, 752)])
    mouth = poly_mask((H, W), [(615, 738), (930, 738), (935, 860), (690, 860), (615, 805)])
    crumbs = poly_mask((H, W), [(690, 718), (716, 718), (716, 745), (690, 745)])
    erase = (mouth | crumbs) & ~nose & dark & dil(face_white, 6)
    a[erase, :3] = 255
    out = Image.fromarray(a.astype(np.uint8))
    k = Kat(W, H)
    k.line([(712, 792), (760, 796), (820, 795), (872, 788)], w=10, seed=95)
    out.alpha_composite(k.done())
    kaydet(out, "temsilci_notr")


ALL = {"kaymakcalan": kaymakcalan, "lenz": lenz, "sheskin": sheskin, "eczaci": eczaci, "kelsey": kelsey,
       "anne": anne, "temsilci2000": temsilci2000, "temsilci_notr": temsilci_notr, "anlatici": anlatici, "voss": voss}

if __name__ == "__main__":
    for n in (sys.argv[1:] or ALL):
        ALL[n]()
