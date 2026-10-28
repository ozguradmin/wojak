"""en-mechanical-turk karakterleri (kaynak PNG'lerden yeniden üretir):  python episodes/en-mechanical-turk/chars/uret.py

A (sol, oyuncu): HF clayshoaf/Wojaks 5_Tired_Wojak/10347 (a_kaynak_marat.png), genel 1790'lar yurttaşı; a_sakin.png = kaynağın kendisi.
  a_sok.png (ters köşe, aynı kutu): göz/kaş/ağız silinip iri yuvarlak göz + küçük göz bebeği (sağa bakar), iç ucu kalkık kalın kaş,
  "O" ağız, alında 5 düzensiz mavi çizgi ve başın önünde kontur dışında 3 ter damlası çizildi. Silüet, saç ve giysi aynı.
B (sağ): wojakland '1700s British Soldier Flag Wojak' (b_kaynak_brit.png) — b_sakin.png = kaynak; arkadaki bayrak ve sırığı silindi, kırpıldı.
"""
from __future__ import annotations
import sys, random
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import kit_varyant  # noqa: E402

SS = 4
BLUE = (60, 120, 200, 255)


def sok() -> Image.Image:
    im = Image.open(HERE / "a_kaynak_marat.png").convert("RGBA")
    W, H = im.size
    a = np.array(im)
    # silinecek bölgeler (yüzün içi, kontur çizgileri dışında): gözler+kaşlar, ağız
    for (x0, y0, x1, y1) in [(450, 262, 772, 392), (528, 515, 705, 600)]:
        reg = a[y0:y1, x0:x1]
        m = reg[..., 3] > 0
        reg[m, :3] = 255
    im = Image.fromarray(a)
    L = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    k = lambda p: (p[0] * SS, p[1] * SS)
    # iri gözler: beyaz dolgu, kalın kontur, küçük göz bebeği (sağa)
    for cx, cy, r in [(538, 342, 40), (722, 346, 36)]:
        d.ellipse([k((cx - r, cy - r)), k((cx + r, cy + r))], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=7 * SS)
        px = cx + 9
        d.ellipse([k((px - 9, cy - 9 + 2)), k((px + 9, cy + 9 + 2))], fill=(0, 0, 0, 255))
    # kalın kaşlar, iç uçları kalkık
    d.line([k((462, 292)), k((505, 268)), k((575, 252))], fill=(0, 0, 0, 255), width=10 * SS, joint="curve")
    d.line([k((662, 252)), k((725, 262)), k((764, 288))], fill=(0, 0, 0, 255), width=10 * SS, joint="curve")
    # "O" ağız
    d.ellipse([k((590, 540)), k((650, 612))], fill=(70, 25, 25, 255), outline=(0, 0, 0, 255), width=7 * SS)
    # alında 5 düzensiz mavi çizgi
    for pts in [[(640, 178), (675, 170), (705, 188), (738, 182)], [(690, 214), (722, 205), (745, 224), (775, 216)],
                [(432, 196), (455, 186), (470, 206), (492, 200)], [(436, 232), (458, 224), (474, 244), (492, 238)],
                [(560, 232), (585, 222), (600, 238), (625, 232)]]:
        d.line([k(p) for p in pts], fill=BLUE, width=6 * SS, joint="curve")
    # 3 ter damlası (kontur dışında ~20 px)
    for x, y, s in [(852, 330, 22), (826, 215, 18), (885, 440, 20)]:
        kit_varyant_drop(d, x, y, s)
    L = L.resize((W, H), Image.LANCZOS)
    return Image.alpha_composite(im, L)


def kit_varyant_drop(d, x, y, s):
    kit_varyant.SS = SS
    kit_varyant._drop(d, x, y, s)


if __name__ == "__main__":
    Image.open(HERE / "a_kaynak_marat.png").convert("RGBA").save(HERE / "a_sakin.png")
    sok().save(HERE / "a_sok.png")
    b = Image.open(HERE / "b_kaynak_brit.png").convert("RGBA")
    arr = np.array(b)
    H, W = arr.shape[:2]
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon([(0, 0), (338, 0), (338, 106), (250, 150), (112, 295), (112, 330), (232, 340), (226, 410),
                               (240, 470), (284, 520), (282, 572), (250, 584), (226, 664), (170, 684), (60, 700), (0, 718)], fill=255)
    arr[np.array(m) > 0, 3] = 0   # bayrak ve sırığı silindi (şapka, yüz, yaka ve ceket aynen)
    yy, xx = np.mgrid[0:H, 0:W]
    ymax = np.where(xx < 150, 626 + (150 - xx) * 0.48, np.where(xx < 250, 624, 612))
    sat = arr[..., :3].max(-1).astype(int) - arr[..., :3].min(-1).astype(int)
    arr[(sat > 30) & (xx < 300) & (yy < ymax), 3] = 0   # bayrağın kalan renkli kırıntıları
    R, G, B = (arr[..., i].astype(int) for i in range(3))
    bits = (xx > 40) & (xx < 118) & (yy > 606) & (yy < 646) & ((B > R) | ((R > 140) & (G > 90) & (B < 130)))
    arr[bits, 3] = 0   # sırık dibinden kalan kahve/mavi kırıntılar
    b = Image.fromarray(arr)
    b = b.crop(b.getchannel("A").getbbox())
    c = np.array(b)
    h2, w2 = c.shape[:2]
    y2, x2 = np.mgrid[0:h2, 0:w2]
    R, G, B = (c[..., i].astype(int) for i in range(3))
    junk = (x2 > 30) & (x2 < 130) & (y2 > 596) & (y2 < 640) & ((B > R + 30) | ((R > 140) & (G > 95) & (B < 130) & (G > R * 0.55)))
    c[junk, 3] = 0   # sırık dibinden kalan kahve/mavi kırıntılar (kırpılmış koordinat)
    Image.fromarray(c).save(HERE / "b_sakin.png")
