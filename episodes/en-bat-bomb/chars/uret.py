"""en-bat-bomb karakterleri (kaynak PNG'lerden yeniden üretir):  python episodes/en-bat-bomb/chars/uret.py

A (sol, planı anlatan görevli): wojakland '1950s Businessman Wojak' (a_kaynak.png, 1243x1400); a_sakin.png = kaynak.
  a_sok.png (ters köşe, aynı kutu): gözler/kaşlar/ağız silinip iri yuvarlak göz + küçük göz bebeği (sağa bakar), iç ucu kalkık kalın kaş,
  "O" ağız, alında mavi çizgiler, başın önünde kontur dışında 3 ter damlası. Silüet, şapka, giysi aynı.
B (sağ, şüpheci): wojakland 'Suit Wojak' (b_kaynak.png, 557x595), 1.6x LANCZOS + UnsharpMask; b_sakin.png.
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


def sakin() -> Image.Image:
    return Image.open(HERE / "a_kaynak.png").convert("RGBA")


def sok() -> Image.Image:
    a = np.array(Image.open(HERE / "a_kaynak.png").convert("RGBA"))
    for (x0, y0, x1, y1) in [(600, 490, 1000, 620), (625, 730, 930, 815), (755, 815, 835, 848)]:
        reg = a[y0:y1, x0:x1]
        m = reg[..., 3] > 0
        reg[m, :3] = 255
    im = Image.fromarray(a)
    W, H = im.size
    L = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    k = lambda p: (p[0] * SS, p[1] * SS)
    for cx, cy, r in [(690, 548, 54), (900, 560, 50)]:
        d.ellipse([k((cx - r, cy - r)), k((cx + r, cy + r))], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=9 * SS)
        px = cx + 14
        d.ellipse([k((px - 11, cy - 8)), k((px + 11, cy + 14))], fill=(0, 0, 0, 255))
    d.line([k((620, 488)), k((665, 474)), k((730, 470))], fill=(0, 0, 0, 255), width=12 * SS, joint="curve")
    d.line([k((870, 468)), k((930, 474)), k((975, 495))], fill=(0, 0, 0, 255), width=12 * SS, joint="curve")
    d.ellipse([k((770, 735)), k((850, 825))], fill=(70, 25, 25, 255), outline=(0, 0, 0, 255), width=9 * SS)
    for pts in [[(640, 448), (665, 441), (685, 455), (710, 448)], [(725, 444), (755, 437), (780, 452), (815, 444)],
                [(830, 446), (855, 439), (880, 453), (905, 446)], [(655, 462), (680, 456), (700, 468), (730, 462)],
                [(770, 460), (800, 454), (820, 466), (850, 460)]]:
        d.line([k(p) for p in pts], fill=BLUE, width=7 * SS, joint="curve")
    kit_varyant.SS = SS
    for x, y, s in [(1105, 480, 26), (1130, 590, 24), (1100, 700, 24)]:
        kit_varyant._drop(d, x, y, s)
    L = L.resize((W, H), Image.LANCZOS)
    return Image.alpha_composite(im, L)


def b() -> Image.Image:
    im = Image.open(HERE / "b_kaynak.png").convert("RGBA")
    f = 1.6
    im = im.resize((int(im.width * f), int(im.height * f)), Image.LANCZOS)
    rgb = im.convert("RGB").filter(ImageFilter.UnsharpMask(2, 60, 2))
    out = rgb.convert("RGBA")
    out.putalpha(im.getchannel("A"))
    return out


if __name__ == "__main__":
    sakin().save(HERE / "a_sakin.png")
    sok().save(HERE / "a_sok.png")
    b().save(HERE / "b_sakin.png")
