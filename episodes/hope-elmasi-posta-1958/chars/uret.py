"""Hope Elması postası (1958) karakterleri: hazır wojak çizimlerinden kırpım + ters köşe yüzü.

A  kuyumcu çalışanı : wojakland '1950s_businessman_wojak' (fötr, takım, kravat; 1243x1400). Göğüsten kesilir
                      (yüz büyüsün). Dosyada yüz sağa bakıyor.
B  postane memuru   : wojakland 'grey_suit_wojak' (gri ceket, beyaz gömlek; 900x870). Ters köşe: alın kırışıkları,
                      kaşlar ve gözler silinir; iç ucu kalkık kaş, iri yuvarlak göz, küçük göz bebeği, "O" ağız, alında
                      mavi soğuk ter çizgileri, yüzün önünde (konturun dışında) üç ter damlası. Dosyada yüz sağa bakıyor.
Çalıştır: python episodes/hope-elmasi-posta-1958/chars/uret.py
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

D = Path(__file__).parent
K = D / "kaynak"
SIYAH = (0, 0, 0, 255)
BEYAZ = (255, 255, 255, 255)
MAVI = (70, 150, 235, 255)
MAVI_KOYU = (25, 80, 170, 255)
W = 9


def temizle(im):
    a = np.array(im).astype(int)
    rgb = a[..., :3]
    lum = rgb.mean(axis=2)
    duz = np.ptp(rgb, axis=2) < 25
    rgb[(lum < 60) & duz] = 0
    rgb[(lum > 230) & duz] = 255
    a[..., :3] = rgb
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def kuyumcu():
    """Kaynağın yan bakan sırıtışı (tur 1 MUST: firma karakterinde kötü yüz olmaz) nötr yüze çevrilir: ağır göz
    kapaklı gözler ve sırıtan ağız silinir; düz bakan sakin wojak gözleri ve kısa düz ağız çizilir."""
    im = temizle(Image.open(K / "a_kaynak.png").convert("RGBA"))
    a = np.array(im)
    # sırıtma + çene kıvrımı: yalnız yanak konturunun sağındaki koyu pikseller silinir
    for y in range(722, 852):
        x0 = int(560 + (y - 760) * 1.1 + 28)
        x1 = 735 if y < 745 else 925  # burnun alt çizgisi (y 720-745, x 742-910) korunur
        for x in range(max(x0, 630), x1):
            if a[y, x, :3].mean() < 250 and a[y, x, 3] > 0:
                a[y, x, :3] = 255
    im = Image.fromarray(a, "RGBA")
    d = ImageDraw.Draw(im)
    d.rectangle((622, 498, 762, 574), fill=BEYAZ)
    d.rectangle((870, 510, 990, 588), fill=BEYAZ)
    # sakin gözler: badem çizgi, göz bebeği öne (dosyada sağa)
    d.line([(640, 540), (668, 522), (712, 516), (748, 526)], fill=SIYAH, width=10, joint="curve")
    d.line([(648, 548), (690, 556), (742, 548)], fill=SIYAH, width=7, joint="curve")
    d.ellipse((706, 520, 740, 554), fill=SIYAH)
    d.line([(888, 538), (914, 526), (952, 524), (978, 534)], fill=SIYAH, width=10, joint="curve")
    d.line([(894, 556), (930, 562), (972, 552)], fill=SIYAH, width=7, joint="curve")
    d.ellipse((942, 528, 972, 560), fill=SIYAH)
    # kısa, hafif aşağı kıvrık nötr ağız
    d.line([(752, 778), (800, 772), (852, 773), (886, 780)], fill=SIYAH, width=10, joint="curve")
    im.crop((0, 0, im.width, 1180)).save(D / "a_kuyumcu.png")


def memur():
    base = temizle(Image.open(K / "b_kaynak.png").convert("RGBA"))
    base.save(D / "b_memur.png")

    v = base.copy()
    d = ImageDraw.Draw(v)
    # sil: alın kırışıkları, kaşlar, kaş işaretleri, gözler, ağız
    d.rectangle((405, 148, 708, 222), fill=BEYAZ)
    d.rectangle((440, 222, 740, 290), fill=BEYAZ)
    d.rectangle((455, 282, 572, 338), fill=BEYAZ)
    d.rectangle((648, 290, 742, 346), fill=BEYAZ)
    d.rectangle((528, 494, 684, 538), fill=BEYAZ)
    # iç ucu kalkık kaşlar (dosyada yüz sağa: iç uçlar burna doğru, x ~560 ve ~650)
    d.line([(462, 262), (510, 248), (556, 220)], fill=SIYAH, width=W, joint="curve")
    d.line([(652, 220), (692, 236), (732, 256)], fill=SIYAH, width=W, joint="curve")
    # iri yuvarlak gözler, küçük göz bebekleri öne (dosyada sağa)
    d.ellipse((466, 268, 558, 352), fill=BEYAZ, outline=SIYAH, width=W)
    d.ellipse((656, 272, 736, 348), fill=BEYAZ, outline=SIYAH, width=W)
    d.ellipse((522, 300, 540, 318), fill=SIYAH)
    d.ellipse((704, 302, 721, 319), fill=SIYAH)
    # açık "O" ağız
    d.ellipse((578, 486, 634, 566), fill=(60, 25, 25, 255), outline=SIYAH, width=W)
    d.ellipse((589, 534, 623, 560), fill=(200, 90, 100, 255))
    # alında mavi soğuk ter çizgileri
    for x0, y0, ln in [(462, 160, 44), (512, 152, 52), (566, 150, 54), (620, 154, 50), (672, 164, 40)]:
        pts = [(x0 + 3.0 * np.sin(t / 5.0), y0 + t) for t in np.arange(0, ln, 1.0)]
        d.line(pts, fill=MAVI, width=8, joint="curve")
    # yüzün önünde (dosyada sağda, konturun ~35 px dışında) üç ter damlası
    for cx, cy, s in [(818, 262, 15), (834, 322, 13), (820, 380, 12)]:
        d.polygon([(cx, cy - 2.2 * s), (cx - s, cy), (cx + s, cy)], fill=MAVI)
        d.ellipse((cx - s, cy - s, cx + s, cy + s), fill=MAVI, outline=MAVI_KOYU, width=4)
        d.line([(cx, cy - 2.2 * s), (cx - s, cy - 2)], fill=MAVI_KOYU, width=4)
        d.line([(cx, cy - 2.2 * s), (cx + s, cy - 2)], fill=MAVI_KOYU, width=4)
        d.ellipse((cx - s * 0.45, cy - s * 0.5, cx - s * 0.05, cy - s * 0.1), fill=(220, 240, 255, 255))
    v.save(D / "b_memur_sok.png")


if __name__ == "__main__":
    kuyumcu()
    memur()
    print("tamam")
