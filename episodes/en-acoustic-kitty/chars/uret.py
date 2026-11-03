"""en-acoustic-kitty karakterleri (kaynak PNG'lerden yeniden üretir):  python episodes/en-acoustic-kitty/chars/uret.py

A (sol, subay): wojakland 'Grey Suit Wojak' (a_kaynak.png, 900x870); a_sakin.png = kaynak.
  a_sok.png (ters köşe, aynı kutu): gözler/ağız silinip iri yuvarlak göz + küçük göz bebeği, iç ucu kalkık kalın kaş,
  "O" ağız, alında mavi çizgiler, başın önünde kontur dışında 3 ter damlası. Silüet ve giysi aynı.
B (sağ, şüpheci patron): wojakland 'Suit Wojak' (fötr şapkalı, b_kaynak.png, 557x595), 1.6x LANCZOS + UnsharpMask; b_sakin.png.
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
    for (x0, y0, x1, y1) in [(450, 278, 750, 352), (530, 490, 690, 540)]:
        reg = a[y0:y1, x0:x1]
        m = reg[..., 3] > 0
        reg[m, :3] = 255
    im = Image.fromarray(a)
    W, H = im.size
    L = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    k = lambda p: (p[0] * SS, p[1] * SS)
    for cx, cy, r in [(520, 318, 56), (700, 326, 52)]:
        d.ellipse([k((cx - r, cy - r)), k((cx + r, cy + r))], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=7 * SS)
        px = cx + 14
        d.ellipse([k((px - 12, cy - 8)), k((px + 12, cy + 16))], fill=(0, 0, 0, 255))
    d.line([k((450, 270)), k((510, 250)), k((590, 244))], fill=(0, 0, 0, 255), width=9 * SS, joint="curve")
    d.line([k((640, 246)), k((710, 252)), k((760, 276))], fill=(0, 0, 0, 255), width=9 * SS, joint="curve")
    d.ellipse([k((570, 492)), k((650, 575))], fill=(70, 25, 25, 255), outline=(0, 0, 0, 255), width=7 * SS)
    for pts in [[(470, 190), (495, 183), (515, 197), (540, 190)], [(555, 186), (585, 179), (610, 194), (645, 186)],
                [(520, 205), (545, 199), (565, 211), (595, 205)], [(610, 207), (640, 200), (660, 213), (690, 206)],
                [(480, 222), (505, 216), (525, 228), (550, 222)]]:
        d.line([k(p) for p in pts], fill=BLUE, width=8 * SS, joint="curve")
    kit_varyant.SS = SS
    for x, y, s in [(815, 330, 28), (835, 440, 26), (805, 545, 26)]:
        kit_varyant._drop(d, x, y, s)
    L = L.resize((W, H), Image.LANCZOS)
    return Image.alpha_composite(im, L)


def b() -> Image.Image:
    im = Image.open(HERE / "b_kaynak.png").convert("RGBA")
    im = im.crop((0, 0, im.width, 470))  # göğüsten kes: baş A'ya yaklaşsın
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
