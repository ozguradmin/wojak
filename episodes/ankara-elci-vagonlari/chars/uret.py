"""Ankara elçi vagonları (1925) karakterleri: hazır wojak çizimlerinden temizlik + ters köşe yüzü.

A  diplomat : wojakland '1930s Top Hat Wojak' (melon şapka, gri takım; 352x405 kaynak). 3x LANCZOS + UnsharpMask,
              koyu çizgiler tam siyaha. Ters köşe: iri göz, küçük göz bebeği, iç ucu kalkık kaş, "O" ağız, alında mavi
              soğuk ter çizgileri, yüzün önünde (konturun dışında) üç ter damlası.
B  memur    : repo içi episodes/karakoy-tunel-1874/chars/memur_sakin.png (bordo fes, gri bıyık); değişmedi.
Çalıştır: python episodes/ankara-elci-vagonlari/chars/uret.py
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
S = 1.5  # koordinatlar 704 px'lik önizlemeden; taban 1056 px


def p(*xy):
    return tuple(int(round(v * S)) for v in xy)


def diplomat():
    im = Image.open(K / "kaynak_melon_704.png").convert("RGBA")
    im = im.resize((int(im.width * S), int(im.height * S)), Image.LANCZOS)
    rgb = im.convert("RGB").filter(ImageFilter.UnsharpMask(2, 60, 2))
    a = np.array(rgb).astype(int)
    al = np.array(im)[..., 3]
    lum = a.mean(axis=2)
    a[lum < 70] = 0                                   # çizgiler net siyah
    a[(lum > 225) & (np.ptp(a, axis=2) < 20)] = 255   # beyaz yüz düz beyaz
    out = np.dstack([a, al]).astype(np.uint8)
    base = Image.fromarray(out, "RGBA")
    base.save(D / "a_diplomat.png")

    v = base.copy()
    d = ImageDraw.Draw(v)
    W = int(6 * S)
    # eski gözler + kaşlar + alttaki kırışık parçası, ağız
    d.rectangle(p(318, 256, 434, 364), fill=BEYAZ)
    d.rectangle(p(470, 272, 541, 370), fill=BEYAZ)
    d.rectangle(p(394, 466, 502, 498), fill=BEYAZ)
    # iç ucu kalkık kaşlar (dosyada kişi sağa bakıyor: soldaki kaşın iç ucu sağda)
    d.line([p(338, 298), p(378, 286), p(420, 264)], fill=SIYAH, width=W, joint="curve")
    d.line([p(476, 266), p(506, 276), p(536, 290)], fill=SIYAH, width=W, joint="curve")
    # iri yuvarlak gözler, küçük göz bebekleri öne (dosyada sağa)
    d.ellipse(p(344, 300, 416, 372), fill=BEYAZ, outline=SIYAH, width=W)
    d.ellipse(p(480, 304, 538, 368), fill=BEYAZ, outline=SIYAH, width=W)
    d.ellipse(p(388, 330, 404, 346), fill=SIYAH)
    d.ellipse(p(514, 332, 528, 346), fill=SIYAH)
    # açık "O" ağız
    d.ellipse(p(424, 458, 472, 514), fill=(60, 25, 25, 255), outline=SIYAH, width=W)
    d.ellipse(p(434, 490, 462, 508), fill=(200, 90, 100, 255))
    # alında mavi soğuk ter çizgileri (şapka siperliği ile kırışıklar arasında)
    for x0, y0, ln in [(372, 196, 26), (398, 192, 30), (424, 190, 32), (450, 192, 30), (476, 197, 24)]:
        pts = [p(x0 + 2 * np.sin(t / 6.0), y0 + t) for t in range(0, ln, 3)]
        d.line(pts, fill=MAVI, width=int(4 * S), joint="curve")
    # yüzün önünde (dosyada sağda, konturun ~20 px dışında) üç ter damlası
    for cx, cy, s in [(602, 262, 15), (620, 314, 12), (603, 360, 10)]:
        cx, cy, s = cx * S, cy * S, s * S
        d.polygon([(cx, cy - 2.2 * s), (cx - s, cy), (cx + s, cy)], fill=MAVI)
        d.ellipse((cx - s, cy - s, cx + s, cy + s), fill=MAVI, outline=MAVI_KOYU, width=3)
        d.line([(cx, cy - 2.2 * s), (cx - s, cy - 2)], fill=MAVI_KOYU, width=3)
        d.line([(cx, cy - 2.2 * s), (cx + s, cy - 2)], fill=MAVI_KOYU, width=3)
        d.ellipse((cx - s * 0.45, cy - s * 0.5, cx - s * 0.05, cy - s * 0.1), fill=(220, 240, 255, 255))
    v.save(D / "a_diplomat_sok.png")


def memur():
    import shutil; shutil.copy(K / "kaynak_memur_fesli.png", D / "b_memur.png")


if __name__ == "__main__":
    diplomat()
    memur()
    print("tamam")
