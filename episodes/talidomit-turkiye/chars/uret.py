"""talidomit-turkiye karakterleri: kaynak PNG'lerden yeniden üretir.

    python episodes/talidomit-turkiye/chars/uret.py

B (sağ) veteriner hoca (Süreyya Tahsin Aygün'e benzerlik: yaşlı, kır saçlı, bıyıksız, gözlüksüz; laboratuvar önlüğü):
  - wojakland 'Grandpa Wojak' (veteriner_kaynak_grandpa.png). Gözlük kaldırıldı (cam içindeki göz çizimleri aynen
    kaldı; çerçeve, köprü ve saplar beyaza boyandı, sağ yüz konturu ve sol sapın kestiği saç sınırı geri çizildi).
    Bıyık ve iki yanındaki "parantez" yanak çizgileri silindi; alt yüz (kısa yanak çizgileri, düz ciddi ağız, kısa
    alt dudak gölgesi) düz çizgilerle yeniden çizildi (Aygün'ün portrelerinde bıyık ve gözlük yok).
  - Saç: koyu gri -> tek düz açık kır dolgu (200), ton bantları yerine 3 ince (5 px) siyah saç teli; siyah kontur aynen.
  - Kahverengi süveter yelek ve gri kollar düz beyaza boyandı, dış silüet konturu korundu; gri gömlek yakası beyaz
    gömleğe (236/222) açıldı; önlük revers'i, yaka kontur çizgisi, V açıklığında beyaz gömlek + siyah kravat, göğüs
    cebi ve kalem düz MS-Paint çizgileriyle eklendi.
A (sol) ilaç firması temsilcisi (adsız; logo/firma adı yok):
  - wojakland '1950s Businessman Wojak' (temsilci_kaynak_1950s.png): fötr şapka, lacivert takım, çizgili kravat.
  - temsilci_gulumsuyor.png: kaynağın kendisi (kendinden emin satıcı gülümsemesi).
  - temsilci_gergin.png (ters köşe, aynı kutu): göz/kaş/ağız silinip klasik 'Nervous Wojak' yüz hatları
    (assets/kit/ingiliz_er_1915/taban/nervous_temiz_ice.png: endişeli kaşlar, göz ucuyla sağa/karşıya bakış;
    gergin dalgalı ağız x1,18 büyük) x0,92 yapıştırıldı; burun, yanak ve çene konturu, kulak/saç, şapka ve takım
    aynı. Şapka kenarının altında 4 düzensiz, elle çizilmiş mavi soğuk ter çizgisi (farklı boy, S kıvrımı, kanca)
    + 5 ter damlası (tools/kit_varyant.py damlası; şakakta ve yüz konturu boyunca).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import kit_varyant  # noqa: E402  (yalnız _drop çizimi için)

SS = 3


def dil(m: np.ndarray, r: int) -> np.ndarray:
    return np.array(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(2 * r + 1))) > 0


def ero(m: np.ndarray, r: int) -> np.ndarray:
    return np.array(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(2 * r + 1))) > 0


def poly_mask(shape, pts) -> np.ndarray:
    im = Image.new("L", (shape[1], shape[0]), 0)
    ImageDraw.Draw(im).polygon(pts, fill=255)
    return np.array(im) > 0


def flood(mask: np.ndarray, seed) -> np.ndarray:
    """mask içinde seed (x, y) noktasına 4-komşulukla bağlı bölge."""
    im = Image.fromarray((mask * 255).astype(np.uint8)).copy()
    ImageDraw.floodfill(im, seed, 128)
    return np.array(im) == 128


def trim(im: Image.Image) -> Image.Image:
    bb = im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
    return im.crop(bb)


# ------------------------------------------------------------------------------------------------
# B: veteriner hoca
# ------------------------------------------------------------------------------------------------
def veteriner() -> Image.Image:
    g = np.array(Image.open(HERE / "veteriner_kaynak_grandpa.png").convert("RGBA")).astype(np.int32)
    H, W = g.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    rgb = g[..., :3]
    lum = rgb.mean(-1)
    sat = rgb.max(-1) - rgb.min(-1)
    op = g[..., 3] > 0

    # 0) gözlük kaldırılır (Aygün'ün portrelerinde gözlük yok). Cam içi (241 gri + parıltı) taşma dolgusuyla
    #    bulunur; içindeki göz çizimleri (göz, göz bebeği, göz altı çizgisi) aynen kalır. Çerçeve (196 gri dolgu +
    #    iki yanındaki siyah çizgiler), köprü ve saplar beyaza boyanır; silüet kenarına denk gelen yerde dış
    #    kontur geri çizilir, sol sapın kestiği saç alt sınırı yeniden çizilir.
    box = (yy > 245) & (yy < 450) & (xx > 330) & (xx < 835)
    frame0 = (np.abs(rgb - 196).sum(-1) < 12) & box
    light = (lum > 215) & box & op & ~frame0
    interior = flood(light, (548, 400)) | flood(light, (745, 410))
    filled = ~flood(~interior, (0, 0))
    eyes = filled & ~interior
    zone = (dil(filled, 24) | poly_mask((H, W), [(335, 318), (462, 294), (472, 320), (345, 340)])
            | poly_mask((H, W), [(625, 262), (685, 262), (685, 315), (625, 315)])
            | poly_mask((H, W), [(790, 318), (834, 318), (834, 350), (790, 350)]))
    frame = frame0 & zone
    er = (dil(frame, 9) & box) | filled
    src = g.copy()
    g[er, :3] = 255
    g[dil(frame, 15) & box & (lum > 100) & ~eyes, :3] = 255
    g[poly_mask((H, W), [(612, 255), (690, 255), (690, 330), (612, 330)]) & (lum < 200) & ~eyes, :3] = 255
    g[poly_mask((H, W), [(790, 318), (834, 318), (834, 350), (790, 350)]) & (lum < 200), :3] = 255
    g[poly_mask((H, W), [(684, 398), (714, 398), (714, 428), (684, 428)]) & (lum < 200), :3] = 255  # kopuk yanak parçası
    g[eyes] = src[eyes]
    g[er & op & ~ero(op, 6), :3] = 0                                   # sağ yüz konturu (camın dış kenarı)
    hs = poly_mask((H, W), [(426, 262), (421, 268), (395, 290), (360, 319), (334, 342), (300, 342), (300, 262)]) & op & (g[..., :3].mean(-1) > 200)
    g[hs, :3] = (169, 162, 156)                                        # sapın sildiği saç parçası
    spikes = poly_mask((H, W), [(392, 282), (360, 314), (334, 337), (325, 326), (352, 296), (378, 276)]) & op \
        & (g[..., :3].mean(-1) < 200)
    g[spikes, :3] = (169, 162, 156)                                    # eski saç/sap çizgisi kırıntıları
    rgb = g[..., :3]
    lum = rgb.mean(-1)
    sat = rgb.max(-1) - rgb.min(-1)

    # 1) bıyık + iki yanındaki "parantez" yanak çizgileri + altındaki küçük "︵": yüzün alt yarısı yeniden
    #    çizilecek (bıyıksız yüzde bu çizgiler boş bir kutu gibi duruyordu). Burun ve çene konturu korunur.
    low = poly_mask((H, W), [(522, 478), (585, 470), (640, 482), (722, 470), (750, 480), (748, 535),
                             (738, 572), (700, 598), (585, 598), (522, 560)])
    low &= ~((yy < 478) & (xx < 700))
    face = (lum > 200) | ((lum < 215) & (sat < 25))
    g[low & op, :3] = 255

    src_hair = g[..., :3].copy()
    # 2) saç: koyu gri -> tek düz açık kır (~200). Kaynaktaki geniş ton bantları (önceki sürümde 172/190) telefon
    #    boyunda gri bir takke gibi okunuyordu; bantlar kaldırıldı, yerine 3-4 ince siyah saç teli çizildi (aşağıda).
    #    Siyah kontur aynen. (Kenar yumuşatma maskesi ana saç dolgusunu yakalamaz.)
    hair_zone = ((yy < 345) | ((yy < 380) & (xx < 345))) & op
    mapped = np.zeros((H, W), bool)
    for c0, dst in (((104, 99, 95), (200, 200, 200)), ((133, 127, 122), (200, 200, 200)),
                    ((169, 162, 156), (200, 200, 200))):
        d = np.abs(src_hair - np.array(c0)).sum(-1)
        m = hair_zone & (d < 18)
        g[m, :3] = dst
        mapped |= m
    # eski ton bantlarının arasındaki yumuşatma pikselleri de aynı düz kıra (yoksa ince gri bant sınırları kalıyor)
    seam = dil(mapped, 3) & hair_zone & ~mapped & (lum >= 90) & (lum <= 185) & (sat < 20)
    g[seam, :3] = 200
    mapped |= seam
    # kenar yumuşatma pikselleri (saç rengi ile siyah arası; ana dolgu hariç): parlaklığı orantılı aç
    mid = hair_zone & ~mapped & (lum > 20) & (lum < 100) & (sat < 16)
    g[mid, :3] = np.clip(g[mid, :3] * 2.0, 0, 255)

    # 3) laboratuvar önlüğü: gömlek yakasının dışında kalan bütün gövde (süveter yelek + kollar) düz beyaza
    #    boyanır; yalnız dış silüet konturu kalır. Üstüne düz MS-Paint çizgileriyle rever, kravat, cep çizilir.
    coat = poly_mask((H, W), [(0, 600), (292, 578), (300, 600), (318, 650), (378, 728), (468, 806), (548, 862),
                              (642, 798), (714, 736), (746, 684), (738, 640), (760, 640), (996, 690), (996, 947),
                              (0, 947)])
    coat &= op
    edge = op & ~ero(op, 9)          # silüetin dış kenarındaki kontur bandı
    keep_outline = edge & (lum < 120)
    vest = (yy > 540) & op & (rgb[..., 0] > rgb[..., 2] + 5) & (lum > 18) & (lum < 75)
    paint = (coat | vest) & ~keep_outline
    g[paint, :3] = 250
    # gömlek yakası: gri -> beyaz gömlek (~236; gölge tonu ~222). Gri yaka telefon boyunda atkı gibi okunuyordu.
    body = (yy > 520) & op & ~paint
    for c0, dst in (((159, 159, 159), (236, 236, 236)), ((128, 128, 128), (222, 222, 222)),
                    ((170, 169, 176), (236, 236, 236))):
        m = body & (np.abs(g[..., :3] - np.array(c0)).sum(-1) < 14)
        g[m, :3] = dst
    out = Image.fromarray(g.astype(np.uint8))
    lay = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    rng = np.random.default_rng(7)

    def line(pts, w=8, fill=(0, 0, 0, 255), jit=1.0):
        p = []
        for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
            n = max(2, int(np.hypot(x1 - x0, y1 - y0) / 18))
            for i in range(n):
                tt = i / n
                p.append(((x0 + (x1 - x0) * tt + rng.normal(0, jit)) * SS, (y0 + (y1 - y0) * tt + rng.normal(0, jit)) * SS))
        p.append((pts[-1][0] * SS, pts[-1][1] * SS))
        d.line(p, fill=fill, width=w * SS, joint="curve")
        for x, y in (p[0], p[-1]):
            r = w * SS / 2
            d.ellipse([x - r, y - r, x + r, y + r], fill=fill)

    def poly(pts, fill):
        d.polygon([(x * SS, y * SS) for x, y in pts], fill=fill)

    # saç alt sınırı (gözlüğün sol sapı kaldırılınca açılan parça)
    line([(421, 268), (395, 290), (360, 319), (334, 342)], w=8, jit=0.3)
    # saç telleri: ince (5 px) siyah, kısa ve hafif kavisli, taranmış saçın akışında: tepede bir, sol şakakta iki
    def curve(p0, p1, bow, n=7):
        (x0, y0), (x1, y1) = p0, p1
        nx, ny = -(y1 - y0), (x1 - x0)
        ln = np.hypot(nx, ny)
        return [(x0 + (x1 - x0) * t + nx / ln * bow * np.sin(np.pi * t),
                 y0 + (y1 - y0) * t + ny / ln * bow * np.sin(np.pi * t)) for t in np.linspace(0, 1, n)]

    line(curve((382, 80), (520, 48), 6), w=5, jit=0.3)
    line(curve((298, 228), (364, 176), 6), w=5, jit=0.3)
    line(curve((308, 302), (370, 242), 6), w=5, jit=0.3)
    # yüzün alt yarısı: kısa yanak çizgileri burun kanatlarından ağız köşelerine, düz/ciddi ağız
    line([(578, 466), (556, 492), (552, 522)], w=8, jit=0.5)
    line([(726, 478), (738, 500), (736, 526)], w=8, jit=0.5)
    line([(588, 552), (618, 545), (655, 543), (690, 546), (708, 554)], w=8, jit=0.4)
    line([(628, 586), (652, 582), (672, 586)], w=6, jit=0.3)   # alt dudak gölgesi (kısa)
    # yaka kontur çizgisi (gömlek yakası ile önlük arası)
    line([(296, 588), (318, 650), (378, 728), (468, 806), (548, 860), (642, 798), (714, 736), (744, 684), (736, 642)],
         w=8, jit=0.6)
    # önlüğün V açıklığı: gri gömlek + siyah kravat (yaka ucunun altından)
    poly([(548, 860), (500, 947), (606, 947)], (236, 236, 236, 255))
    poly([(538, 866), (560, 866), (572, 934), (550, 947), (530, 934)], (14, 14, 14, 255))
    line([(548, 860), (500, 947)], w=8)
    line([(550, 862), (606, 947)], w=8)
    # revers (yaka katları): omuzdan çentiğe, çentikten önlüğün önüne
    line([(300, 610), (262, 700), (232, 772)])
    line([(232, 772), (270, 786), (254, 808)])
    line([(254, 808), (380, 885), (470, 947)])
    line([(734, 650), (778, 716), (812, 778)])
    line([(812, 778), (776, 792), (796, 812)])
    line([(796, 812), (700, 885), (636, 947)])
    # göğüs cebi (sağ) + kalem
    line([(700, 906), (812, 900)], w=7)
    line([(744, 904), (748, 862)], w=6)
    d.ellipse([740 * SS, 852 * SS, 756 * SS, 868 * SS], fill=(14, 14, 14, 255))
    lay = lay.resize((W, H), Image.LANCZOS)
    out.alpha_composite(lay)
    return trim(out)


# ------------------------------------------------------------------------------------------------
# A: firma temsilcisi
# ------------------------------------------------------------------------------------------------
def temsilci() -> tuple[Image.Image, Image.Image]:
    src = Image.open(HERE / "temsilci_kaynak_1950s.png").convert("RGBA")
    base = src.copy()
    a = np.array(src).astype(np.int32)
    H, W = a.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    lum = a[..., :3].mean(-1)
    dark = lum < 252

    # gözler + alın çizgileri, gülümseme + gamze bölgeleri (burun ve yanak çizgisi dışarıda)
    eyes = poly_mask((H, W), [(612, 428), (850, 428), (990, 440), (995, 600), (870, 600), (760, 590), (612, 590)])
    nose = poly_mask((H, W), [(735, 585), (800, 585), (905, 640), (920, 735), (800, 752), (735, 752)])
    # ağız bölgesi: sol alt köşe kesik (çene konturu 615,805 -> 690,860 arası korunur; önceki dikdörtgen onu siliyordu)
    mouth = poly_mask((H, W), [(615, 735), (930, 735), (935, 860), (690, 860), (615, 805)])
    face_white = (lum > 230)
    # gülümsemenin/alın çizgilerinin bölge dışında kalan kırıntıları (burnun solu, sol kaş ucu, sağ alın)
    crumbs = (poly_mask((H, W), [(690, 718), (716, 718), (716, 745), (690, 745)])
              | poly_mask((H, W), [(596, 446), (618, 446), (618, 470), (596, 470)])
              | poly_mask((H, W), [(910, 430), (934, 430), (934, 444), (910, 444)]))
    erase = (eyes | mouth | crumbs) & ~nose & dark
    # yalnız beyaz yüzün içindeki çizgiler (şapka kenarı, saç ve dış kontur bölge dışında kalır)
    erase &= dil(face_white, 6)
    g = a.copy()
    g[erase, :3] = 255

    # klasik nervous (göz ucuyla sağa bakan) yüz hatları
    nv = np.array(Image.open(ROOT / "assets/kit/ingiliz_er_1915/taban/nervous_temiz_ice.png").convert("RGBA")).astype(np.int32)
    s = 0.92
    feats = []
    for (x0, y0, x1, y1), k in (((430, 330, 830, 490), 1.0), ((560, 690, 760, 765), 1.18)):
        reg = nv[y0:y1, x0:x1]
        l = reg[..., :3].mean(-1)
        alpha = np.clip((235 - l) / 235 * 255, 0, 255) * (reg[..., 3] > 0)
        rgba = np.zeros_like(reg)
        rgba[..., 3] = alpha
        im = Image.fromarray(rgba.astype(np.uint8)).resize((round((x1 - x0) * s * k), round((y1 - y0) * s * k)),
                                                           Image.LANCZOS)
        feats.append((im, x0, y0, x1, y1, k))
    # hizalama: nervous sol göz merkezi (507, 430) -> temsilci sol göz merkezi (690, 540)
    ax, ay = 690, 540
    out = Image.fromarray(g.astype(np.uint8))
    for im, x0, y0, x1, y1, k in feats:
        # ağız k kat büyük (telefon boyunda okunur, gergin dalgalı ağız); merkezi aynı yerde kalır
        cx = ax + ((x0 + x1) / 2 - 507) * s
        cy = ay + ((y0 + y1) / 2 - 430) * s
        out.alpha_composite(im, (round(cx - im.width / 2), round(cy - im.height / 2)))

    # ter: şapka kenarı altında mavi soğuk ter çizgileri + damlalar
    lay = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    blue = (110, 175, 230, 255)
    # 4 düzensiz, elle çizilmiş soğuk ter çizgisi (C2kk 4,0 sn ve C4V3 12,5 sn alnındaki "}", "ʃ", "j" biçimleri):
    # farklı boy (55/40/70/45), hafif S kıvrımı, ucunda küçük kanca, eşit olmayan aralık (82/92/66 px). Kaşların
    # üstünde biter (kaşlar ifadenin taşıyıcısı; üstlerinden geçmez); en uzunu iki kaşın arasındaki boşlukta.
    rng = np.random.default_rng(11)

    def stroke(x, y0, length, amp, waves, hook_top, hook_bot, w=8.5):
        ts = np.linspace(0, 1, 14)
        pts = [(x + amp * np.sin(np.pi * waves * t) + rng.normal(0, 0.5), y0 + length * t + rng.normal(0, 0.4))
               for t in ts]
        if hook_top:   # (dx, dy): üst uçtan kısa kıvrık kanca
            pts.insert(0, (pts[0][0] + hook_top[0], pts[0][1] + hook_top[1]))
        if hook_bot:
            pts.append((pts[-1][0] + hook_bot[0], pts[-1][1] + hook_bot[1]))
        p = [(px * SS, py * SS) for px, py in pts]
        d.line(p, fill=blue, width=round(w * SS), joint="curve")
        for px, py in (p[0], p[-1]):
            r = w * SS / 2
            d.ellipse([px - r, py - r, px + r, py + r], fill=blue)

    stroke(618, 438, 53, 4.0, 2.0, (-8, -5), (-7, 4))      # "}" sol şakak, kaşın solunda
    stroke(700, 430, 36, -3.0, 1.0, (7, -6), None)          # kısa, üstte kanca; sol kaşın 8 px üstünde biter
    stroke(792, 428, 66, -5.0, 1.5, None, (9, 3))           # en uzun "L/ʃ", iki kaşın arasında, altta sağa kanca
    stroke(858, 440, 42, -3.5, 1.2, (6, -6), None)          # kısa, üstte kanca; sağ kaşın solunda
    # damlalar: şakakta ve yüz konturunun 25-35 px içinde (yanak ortasındaki damla gözyaşı gibi okunuyordu)
    for x, y, r in ((585, 600, 22), (1000, 640, 20), (568, 712, 19), (968, 745, 17), (624, 784, 17)):
        kit_varyant._drop(d, x, y, r)
    lay = lay.resize((W, H), Image.LANCZOS)
    out.alpha_composite(lay)
    return base, out


def main() -> None:
    v = veteriner()
    v.save(HERE / "veteriner.png", optimize=True)
    print("veteriner.png", v.size)
    g, n = temsilci()
    g.save(HERE / "temsilci_gulumsuyor.png", optimize=True)
    n.save(HERE / "temsilci_gergin.png", optimize=True)
    print("temsilci_*.png", g.size)


if __name__ == "__main__":
    main()
