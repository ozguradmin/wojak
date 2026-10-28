"""Pera Palas 1979 karakterleri: hazır wojakland çizimlerinden temizlik + ters köşe yüzü.

A  otelci   : wl:bow_tie_suit_wojak.png (papyon + yelek). Yüzdeki gri-mavi gölge düz beyaza çevrilir.
B  gazeteci : wl:grey_suit_wojak.png (siyah saç, gri ceket). Ters köşe: iri göz, kalkık kaş, "O" ağız,
              alında mavi soğuk ter çizgileri, yüzün önünde üç ter damlası.
Çalıştır: python episodes/pera-palas-anahtar-1979/chars/uret.py
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


def otelci():
    im = Image.open(K / "kaynak_papyon.png").convert("RGBA")
    a = np.array(im).astype(int)
    r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    mn = np.minimum(np.minimum(r, g), b)
    mx = np.maximum(np.maximum(r, g), b)
    # açık gri-mavi gölgeler (yüz, boyun, gömlek) düz beyaza; koyu yelek değişmez
    yy = np.arange(a.shape[0])[:, None] * np.ones((1, a.shape[1]))
    m = (mn >= 168) & (mx - mn < 40) & (al > 200)
    a[m, 0:3] = 255
    # başın üstünde ve sağında kontur yok (yalnız gölge vardı): alfa sınırına aynı kalınlıkta siyah kontur
    from scipy import ndimage
    mask = ndimage.gaussian_filter((al > 128).astype(float), 2.0) > 0.5
    ic = ndimage.binary_erosion(mask, iterations=5)
    koyu = (mx < 90) & (al > 128)
    sec = mask & ~ic & (yy < 420)
    a[sec, 0:3] = 0
    a[sec, 3] = 255
    a[(yy < 420) & ~mask, 3] = 0   # kenar yumuşatmasından kalan beyaz hale
    out = Image.fromarray(a.astype(np.uint8), "RGBA")
    out.save(D / "a_otelci.png")


def _sil(d, kutu):
    d.rectangle(kutu, fill=BEYAZ)


def gazeteci():
    im = Image.open(K / "kaynak_gri.png").convert("RGBA")
    im.save(D / "b_gazeteci.png")
    v = im.copy()
    d = ImageDraw.Draw(v)
    # eski gözler, kaşlar, kaş arası çizgiler, ağız
    _sil(d, (448, 222, 580, 340))
    _sil(d, (640, 224, 735, 347))
    _sil(d, (645, 255, 662, 295))
    _sil(d, (528, 494, 684, 536))
    W = 8
    # kalkık, iç uçları yukarı kaşlar
    d.line([(452, 262), (490, 244), (548, 226)], fill=SIYAH, width=W, joint="curve")
    d.line([(648, 228), (690, 236), (732, 256)], fill=SIYAH, width=W, joint="curve")
    # iri yuvarlak gözler, küçük göz bebekleri öne (dosyada sağa) ve biraz aşağı
    d.ellipse((470, 270, 556, 344), fill=BEYAZ, outline=SIYAH, width=W)
    d.ellipse((664, 278, 732, 346), fill=BEYAZ, outline=SIYAH, width=W)
    d.ellipse((520, 304, 540, 324), fill=SIYAH)
    d.ellipse((700, 308, 718, 326), fill=SIYAH)
    # açık "O" ağız
    d.ellipse((572, 484, 636, 560), fill=(60, 25, 25, 255), outline=SIYAH, width=W)
    d.ellipse((586, 528, 622, 552), fill=(200, 90, 100, 255))
    # alında mavi soğuk ter çizgileri (düzensiz, hafif kıvrık)
    for x0, y0, ln in [(505, 112, 40), (538, 104, 48), (572, 100, 52), (606, 102, 48), (640, 110, 40)]:
        pts = [(x0 + 3 * np.sin(t / 9.0), y0 + t) for t in range(0, ln, 4)]
        d.line(pts, fill=MAVI, width=7, joint="curve")
        d.line([(pts[-1][0], pts[-1][1]), (pts[-1][0] - 6, pts[-1][1] + 6)], fill=MAVI, width=6)
    # yüzün önünde (dosyada sağda, konturun dışında) üç ter damlası
    for cx, cy, s in [(822, 250, 26), (846, 318, 21), (818, 384, 17)]:
        d.polygon([(cx, cy - 2.2 * s), (cx - s, cy), (cx + s, cy)], fill=MAVI)
        d.ellipse((cx - s, cy - s, cx + s, cy + s), fill=MAVI, outline=MAVI_KOYU, width=3)
        d.line([(cx, cy - 2.2 * s), (cx - s, cy - 2)], fill=MAVI_KOYU, width=3)
        d.line([(cx, cy - 2.2 * s), (cx + s, cy - 2)], fill=MAVI_KOYU, width=3)
        d.ellipse((cx - s * 0.45, cy - s * 0.5, cx - s * 0.05, cy - s * 0.1), fill=(220, 240, 255, 255))
    v.save(D / "b_gazeteci_sok.png")


if __name__ == "__main__":
    otelci()
    gazeteci()
    print("tamam")
