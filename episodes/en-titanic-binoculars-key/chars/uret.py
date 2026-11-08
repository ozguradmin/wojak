"""en-titanic-binoculars-key karakterleri:  python episodes/en-titanic-binoculars-key/chars/uret.py

A (sol, gözcü): wojakland 'Worker 2 Wojak' (a_kaynak.png, 1153x1177, kasket + tulum): a_sakin.png = özgün.
  a_sok.png (ters köşe, aynı kutu): gözler silinip iri yuvarlak göz + küçük göz bebeği (özgün gibi sola bakar), iç ucu kalkık kalın kaş,
  "O" ağız, alında mavi çizgiler, başın yanında kontur dışında 3 ter damlası. Silüet, kasket, giysi aynı.
B (sağ, subay): wojakland 'Sailor Captain Wojak' (b_kaynak.png, 566x725), göğüsten (y 520) kesilir (gövde kenardan taşan dikey çizgi olmasın), 2x LANCZOS: b_sakin.png.
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import kit_varyant  # noqa: E402

SS = 4
BLUE = (60, 120, 200, 255)

EREASE = [(655, 318, 780, 392), (850, 322, 955, 398)]
EYES = [(716, 355, 46), (905, 360, 46)]
BROWS = [[(640, 316), (700, 292), (775, 270)], [(850, 270), (915, 290), (975, 316)]]
MOUTH = (775, 545, 860, 625)
FOREHEAD = [[(752, 258), (772, 251), (792, 263), (814, 256)], [(826, 256), (848, 249), (868, 261), (890, 254)],
            [(768, 240), (790, 233), (810, 245), (840, 238)]]
DROPS = [(1040, 390, 26), (1060, 500, 24), (1030, 610, 24)]


def a_sakin() -> Image.Image:
    return Image.open(HERE / "a_kaynak.png").convert("RGBA")


def a_sok() -> Image.Image:
    im = a_sakin()
    a = np.array(im)
    for (x0, y0, x1, y1) in EREASE:
        reg = a[y0:y1, x0:x1]
        m = reg[..., 3] > 0
        reg[m, :3] = 255
    im = Image.fromarray(a)
    W, H = im.size
    L = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    k = lambda p: (p[0] * SS, p[1] * SS)
    for cx, cy, r in EYES:
        d.ellipse([k((cx - r, cy - r)), k((cx + r, cy + r))], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=6 * SS)
        px = cx - 13
        d.ellipse([k((px - 10, cy - 7)), k((px + 10, cy + 13))], fill=(0, 0, 0, 255))
    for pts in BROWS:
        d.line([k(p) for p in pts], fill=(0, 0, 0, 255), width=9 * SS, joint="curve")
    (mx0, my0, mx1, my1) = MOUTH
    d.ellipse([k((mx0, my0)), k((mx1, my1))], fill=(70, 25, 25, 255), outline=(0, 0, 0, 255), width=6 * SS)
    for pts in FOREHEAD:
        d.line([k(p) for p in pts], fill=BLUE, width=6 * SS, joint="curve")
    kit_varyant.SS = SS
    for x, y, s in DROPS:
        kit_varyant._drop(d, x, y, s)
    L = L.resize((W, H), Image.LANCZOS)
    return Image.alpha_composite(im, L)


def b_sakin() -> Image.Image:
    im = Image.open(HERE / "b_kaynak.png").convert("RGBA").crop((0, 0, 566, 520))  # göğüs hizasından kes: kol/gövde kenarı kareden taşmasın
    big = im.resize((im.width * 2, im.height * 2), Image.LANCZOS)
    rgb = big.convert("RGB").filter(ImageFilter.GaussianBlur(0.8)).filter(ImageFilter.UnsharpMask(2, 50, 2))
    out = rgb.convert("RGBA")
    out.putalpha(big.getchannel("A"))
    return out


if __name__ == "__main__":
    a_sakin().save(HERE / "a_sakin.png")
    a_sok().save(HERE / "a_sok.png")
    b_sakin().save(HERE / "b_sakin.png")
