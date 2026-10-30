"""Piri Reis haritası (1929) karakterleri: hazır wojak çizimlerinden temizlik + ters köşe yüzü.

A  memur  : wojakland 'suit_wojak_1' (fötr, yelek, kravat; 557x595 kaynak). Göğüsten kesilir (yüz büyüsün),
            2x LANCZOS + UnsharpMask, koyu çizgiler tam siyaha. Dosyada yüz sağa bakıyor.
B  bilgin : wojakland 'suit_wojak' (bıyık, papyon; 820x768 kaynak). 2x LANCZOS + UnsharpMask. Ters köşe: alın
            kırışıkları ve göz altı torbaları silinir; iç ucu kalkık kaş, iri yuvarlak göz, küçük göz bebeği, bıyığın
            altında "O" ağız, alında mavi soğuk ter çizgileri, yüzün önünde (konturun dışında) üç ter damlası.
            Dosyada yüz sağa bakıyor.
Çalıştır: python episodes/piri-reis-haritasi-1929/chars/uret.py
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

D = Path(__file__).parent
K = D / "kaynak"
SIYAH = (0, 0, 0, 255)
BEYAZ = (255, 255, 255, 255)
MAVI = (70, 150, 235, 255)
MAVI_KOYU = (25, 80, 170, 255)
S = 2  # koordinatlar kaynak pikselinde; taban 2x


def p(*xy):
    return tuple(int(round(v * S)) for v in xy)


def buyut(im):
    im = im.resize((im.width * S, im.height * S), Image.LANCZOS)
    rgb = im.convert("RGB").filter(ImageFilter.UnsharpMask(2, 60, 2))
    a = np.array(rgb).astype(int)
    al = np.array(im)[..., 3]
    lum = a.mean(axis=2)
    a[(lum < 70) & (np.ptp(a, axis=2) < 30)] = 0  # renkli koyu kumaş (kahve ceket) siyaha dönmesin
    a[(lum > 225) & (np.ptp(a, axis=2) < 20)] = 255
    return Image.fromarray(np.dstack([a, al]).astype(np.uint8), "RGBA")


def memur():
    im = Image.open(K / "kaynak_a_memur.png").convert("RGBA")
    im = im.crop((0, 0, im.width, 470))
    buyut(im).save(D / "a_memur.png")


def bilgin():
    src = Image.open(K / "kaynak_b_bilgin.png").convert("RGBA")
    base = buyut(src)
    base.save(D / "b_bilgin.png")

    v = base.copy()
    d = ImageDraw.Draw(v)
    W = int(6 * S)
    # sil: alın kırışıkları, kaşlar, kaş arası işaretler, gözler + göz altı torbaları
    d.rectangle(p(356, 140, 650, 210), fill=BEYAZ)
    d.rectangle(p(380, 212, 520, 278), fill=BEYAZ)
    d.rectangle(p(580, 212, 690, 282), fill=BEYAZ)
    d.rectangle(p(384, 275, 508, 378), fill=BEYAZ)
    d.rectangle(p(586, 282, 600, 342), fill=BEYAZ)
    d.rectangle(p(601, 282, 702, 392), fill=BEYAZ)
    # iç ucu kalkık kaşlar (dosyada yüz sağa: iç uçlar burna, ortaya yakın)
    d.line([p(395, 238), p(445, 226), p(494, 200)], fill=SIYAH, width=W, joint="curve")
    d.line([p(600, 200), p(636, 214), p(670, 232)], fill=SIYAH, width=W, joint="curve")
    # iri yuvarlak gözler, küçük göz bebekleri öne (dosyada sağa)
    d.ellipse(p(400, 240, 496, 336), fill=BEYAZ, outline=SIYAH, width=W)
    d.ellipse(p(604, 246, 682, 326), fill=BEYAZ, outline=SIYAH, width=W)
    d.ellipse(p(463, 282, 480, 299), fill=SIYAH)
    d.ellipse(p(652, 279, 668, 295), fill=SIYAH)
    # bıyığın altında açık "O" ağız; bıyık üstte kalsın diye sonra geri yapıştırılır
    d.ellipse(p(514, 498, 566, 580), fill=(60, 25, 25, 255), outline=SIYAH, width=W)
    d.ellipse(p(524, 548, 556, 574), fill=(200, 90, 100, 255))
    arr = np.array(v)
    org = np.array(base)
    by = slice(430 * S, 516 * S)
    bx = slice(430 * S, 660 * S)
    m = org[by, bx, :3].mean(axis=2) < 200  # bıyığın gri dolgusu ve konturu
    arr[by, bx][m] = org[by, bx][m]
    # göz altı torbaları sakin yüzdeki gibi kalsın (tur 1 SHOULD: "başka adam" hissi); yalnız yeni gözün altındaki koyu çizgiler
    for x0, y0, x1, y1 in [(384, 340, 508, 378), (601, 330, 702, 392)]:
        ys, xs = slice(y0 * S, y1 * S), slice(x0 * S, x1 * S)
        m = org[ys, xs, :3].mean(axis=2) < 120
        arr[ys, xs][m] = org[ys, xs][m]
    v = Image.fromarray(arr, "RGBA")
    d = ImageDraw.Draw(v)
    # alında mavi soğuk ter çizgileri
    for x0, y0, ln in [(418, 146, 38), (466, 140, 44), (516, 138, 46), (566, 142, 42), (612, 152, 34)]:
        pts = [p(x0 + 2.0 * np.sin(t / 4.0), y0 + t) for t in np.arange(0, ln, 1.0)]
        d.line(pts, fill=MAVI, width=int(5 * S), joint="curve")
    # yüzün önünde (dosyada sağda, konturun ~25 px dışında) üç ter damlası
    for cx, cy, s in [(758, 248, 15), (774, 306, 13), (762, 360, 12)]:
        cx, cy, s = cx * S, cy * S, s * S
        d.polygon([(cx, cy - 2.2 * s), (cx - s, cy), (cx + s, cy)], fill=MAVI)
        d.ellipse((cx - s, cy - s, cx + s, cy + s), fill=MAVI, outline=MAVI_KOYU, width=5)
        d.line([(cx, cy - 2.2 * s), (cx - s, cy - 2)], fill=MAVI_KOYU, width=5)
        d.line([(cx, cy - 2.2 * s), (cx + s, cy - 2)], fill=MAVI_KOYU, width=5)
        d.ellipse((cx - s * 0.45, cy - s * 0.5, cx - s * 0.05, cy - s * 0.1), fill=(220, 240, 255, 255))
    v.save(D / "b_bilgin_sok.png")


if __name__ == "__main__":
    memur()
    bilgin()
    print("tamam")
