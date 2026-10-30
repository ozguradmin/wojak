"""Uluburun (1982) karakterleri: hazır wojak çizimlerinden temizlik + ters köşe yüzü.

A  süngerci : wojakland 'breton_fisherman_wojak' (kırmızı bere, sarı gömlek; 442x494 kaynak). 3x LANCZOS +
              UnsharpMask, koyu çizgiler tam siyaha. (Tur 1: 'flexing_tank_top_wojak' kanal ailesi dışı bulundu.)
B  reis     : wojakland 'worker_wojak' (kasket, sakal; 464x463 kaynak). 3x LANCZOS + UnsharpMask, koyu çizgiler
              tam siyaha. Ters köşe: iri göz, küçük göz bebeği, iç ucu kalkık kaş, "O" ağız, alında mavi soğuk ter
              çizgileri, yüzün önünde (konturun dışında) üç ter damlası. Dosyada yüz sağa bakıyor.
Çalıştır: python episodes/uluburun-kulakli-biskuvi/chars/uret.py
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
S = 3  # koordinatlar 464 px'lik kaynaktan; taban 1392 px


def p(*xy):
    return tuple(int(round(v * S)) for v in xy)


def buyut(ad):
    im = Image.open(K / ad).convert("RGBA")
    im = im.resize((im.width * S, im.height * S), Image.LANCZOS)
    rgb = im.convert("RGB").filter(ImageFilter.UnsharpMask(2, 60, 2))
    a = np.array(rgb).astype(int)
    al = np.array(im)[..., 3]
    lum = a.mean(axis=2)
    a[lum < 70] = 0
    a[(lum > 225) & (np.ptp(a, axis=2) < 20)] = 255
    return Image.fromarray(np.dstack([a, al]).astype(np.uint8), "RGBA")


def reis():
    base = buyut("kaynak_reis_worker.png")
    base.save(D / "b_reis.png")

    v = base.copy()
    d = ImageDraw.Draw(v)
    W = int(3 * S)
    # eski gözler + kaşlar + kaş arası çizgiler, alın kırışıkları, ağız
    d.rectangle(p(218, 116, 277, 175), fill=BEYAZ)
    d.rectangle(p(205, 122, 218, 134), fill=BEYAZ)   # alındaki kaş artığı benek (tur 1)
    d.rectangle(p(207, 111, 214, 116), fill=BEYAZ)   # alın üstündeki kırışık artığı benek (tur 2)
    d.rectangle(p(277, 128, 303, 147), fill=BEYAZ)
    d.rectangle(p(303, 116, 351, 179), fill=BEYAZ)
    d.rectangle(p(250, 238, 323, 257), fill=BEYAZ)
    # alın kırışıkları: her sütunda siperliğin altındaki ilk beyazdan Y 118'e kadar yalnız koyu pikselleri sil
    arr = np.array(v)
    for x in range(212 * S, 340 * S):
        y = 95 * S
        while y < 118 * S and arr[y, x, :3].mean() < 200:
            y += 1
        seg = arr[y + 2:118 * S, x]
        seg[seg[:, :3].mean(axis=1) < 245] = BEYAZ
    v = Image.fromarray(arr, "RGBA")
    d = ImageDraw.Draw(v)
    # iç ucu kalkık kaşlar (dosyada yüz sağa: iç uçlar ortada)
    d.line([p(226, 132), p(250, 126), p(274, 113)], fill=SIYAH, width=W, joint="curve")
    d.line([p(304, 113), p(326, 121), p(347, 128)], fill=SIYAH, width=W, joint="curve")
    # iri yuvarlak gözler, küçük göz bebekleri öne (dosyada sağa)
    d.ellipse(p(231, 134, 273, 174), fill=BEYAZ, outline=SIYAH, width=W)
    d.ellipse(p(307, 135, 345, 171), fill=BEYAZ, outline=SIYAH, width=W)
    d.ellipse(p(259, 150, 268, 159), fill=SIYAH)
    d.ellipse(p(332, 149, 340, 158), fill=SIYAH)
    # açık "O" ağız
    d.ellipse(p(274, 233, 304, 267), fill=(60, 25, 25, 255), outline=SIYAH, width=W)
    d.ellipse(p(280, 252, 298, 263), fill=(200, 90, 100, 255))
    # alında mavi soğuk ter çizgileri (siperlik ile kaşlar arasında)
    for x0, y0, ln in [(240, 104, 11), (256, 103, 13), (276, 102, 14), (296, 103, 13), (316, 105, 10)]:
        pts = [p(x0 + 0.8 * np.sin(t / 2.5), y0 + t) for t in np.arange(0, ln, 1.0)]
        d.line(pts, fill=MAVI, width=int(1.6 * S), joint="curve")
    # yüzün önünde (dosyada sağda, konturun ~7 px dışında) üç ter damlası
    for cx, cy, s in [(378, 140, 5.5), (386, 166, 4.5), (379, 190, 4)]:
        cx, cy, s = cx * S, cy * S, s * S
        d.polygon([(cx, cy - 2.2 * s), (cx - s, cy), (cx + s, cy)], fill=MAVI)
        d.ellipse((cx - s, cy - s, cx + s, cy + s), fill=MAVI, outline=MAVI_KOYU, width=3)
        d.line([(cx, cy - 2.2 * s), (cx - s, cy - 2)], fill=MAVI_KOYU, width=3)
        d.line([(cx, cy - 2.2 * s), (cx + s, cy - 2)], fill=MAVI_KOYU, width=3)
        d.ellipse((cx - s * 0.45, cy - s * 0.5, cx - s * 0.05, cy - s * 0.1), fill=(220, 240, 255, 255))
    v.save(D / "b_reis_sok.png")


def sungerci():
    buyut("kaynak_sungerci_breton.png").save(D / "a_sungerci.png")


if __name__ == "__main__":
    reis()
    sungerci()
    print("tamam")
