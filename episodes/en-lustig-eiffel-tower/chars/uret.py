"""en-lustig-eiffel-tower karakterleri:  python episodes/en-lustig-eiffel-tower/chars/uret.py

A (sol, Lustig): wojakland 'Smug Suit Wojak' (kaynak/smug_suit_wojak.png); a_sakin.png = kaynağın kendisi.
B (sağ, hurdacı): wojakland 'Suit Wojak' (şapkalı gri takım, kaynak/suit_wojak_1.png), 2x LANCZOS + UnsharpMask; b_sakin.png.
  b_sok.png (ters köşe, aynı kutu): göz/ağız silinip iri yuvarlak göz + küçük göz bebeği, iç ucu kalkık kalın kaş,
  "O" ağız, alında mavi çizgiler ve başın yanında kontur dışında 3 ter damlası. Silüet, şapka ve takım aynı.
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
K = 2


def base_b() -> Image.Image:
    im = Image.open(HERE / "kaynak" / "suit_wojak_1.png").convert("RGBA")
    im = im.resize((im.width * K, im.height * K), Image.LANCZOS)
    rgb = im.convert("RGB").filter(ImageFilter.UnsharpMask(2, 60, 2))
    out = rgb.convert("RGBA")
    out.putalpha(im.getchannel("A"))
    return out


def pad(im, left=70, right=70):
    c = Image.new("RGBA", (im.width + left + right, im.height), (0, 0, 0, 0))
    c.paste(im, (left, 0))
    return c


def sok(b: Image.Image) -> Image.Image:
    L0, R0 = 70, 70
    b = pad(b, L0, R0)
    a = np.array(b)
    for (x0, y0, x1, y1) in [(L0 + 490, 322, L0 + 752, 440), (L0 + 585, 538, L0 + 745, 585)]:
        reg = a[y0:y1, x0:x1]
        reg[reg[..., 3] > 0, :3] = 255
    im = Image.fromarray(a)
    W, H = im.size
    L = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    k = lambda p: (p[0] * SS, p[1] * SS)
    o = L0
    for cx, cy, r in [(o + 560, 410, 38), (o + 716, 416, 34)]:
        d.ellipse([k((cx - r, cy - r)), k((cx + r, cy + r))], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=8 * SS)
        px = cx + 8
        d.ellipse([k((px - 9, cy - 9 + 3)), k((px + 9, cy + 9 + 3))], fill=(0, 0, 0, 255))
    d.line([k((o + 506, 358)), k((o + 548, 340)), k((o + 612, 346))], fill=(0, 0, 0, 255), width=11 * SS, joint="curve")
    d.line([k((o + 680, 350)), k((o + 735, 338)), k((o + 768, 360))], fill=(0, 0, 0, 255), width=11 * SS, joint="curve")
    d.ellipse([k((o + 622, 530)), k((o + 698, 612))], fill=(70, 25, 25, 255), outline=(0, 0, 0, 255), width=8 * SS)
    kit_varyant.SS = SS
    for x, y, s in [(o + 285, 470, 22), (o + 250, 600, 20), (o + 880, 460, 22), (o + 905, 590, 20)]:
        kit_varyant._drop(d, x, y, s)
    L = L.resize((W, H), Image.LANCZOS)
    return Image.alpha_composite(im, L)


if __name__ == "__main__":
    Image.open(HERE / "kaynak" / "smug_suit_wojak.png").convert("RGBA").save(HERE / "a_sakin.png")
    b = base_b()
    CUT = 900   # gövde göğüs hizasında kesilir: şapkalı karakterde yüz büyür
    pad(b, 70, 70).crop((0, 0, b.width + 140, CUT)).save(HERE / "b_sakin.png")
    sok(b).crop((0, 0, b.width + 140, CUT)).save(HERE / "b_sok.png")
