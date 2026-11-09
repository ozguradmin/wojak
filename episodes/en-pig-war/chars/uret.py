"""en-pig-war karakterleri:  python episodes/en-pig-war/chars/uret.py

A (sol, Amerikalı yerleşimci): wojakland 'Farmer Wojak' (kaynak/farmer_wojak.png), a_sakin.png = kaynağın kendisi.
B (sağ, İngiliz görevli): wojakland 'English Wojak' (koyu ceket, kravat), b_sakin.png = göğüsten kesilmiş kaynak.
  b_sok.png (ters köşe, aynı kutu): göz/kaş/ağız silinip iri yuvarlak göz + küçük göz bebeği, iç ucu kalkık kalın kaş,
  "O" ağız, alında mavi çizgiler, başın yanında kontur dışında ter damlaları. Silüet ve kıyafet aynı.
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import kit_varyant  # noqa: E402

SS = 4
BLUE = (60, 120, 200, 255)
BLK = (0, 0, 0, 255)
CUT = 900


def fix_brim(a: Image.Image) -> Image.Image:
    """Kaynakta şapka kenarı tuval sınırında düz kesik: sağa 70 px uzatıp uca doğru sivriltir."""
    W, H = a.size
    ext = 70
    c = Image.new("RGBA", (W + ext, H), (0, 0, 0, 0))
    c.paste(a, (0, 0))
    col = a.getpixel((W - 12, 246))[:3]
    L = Image.new("RGBA", (c.width * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    k = lambda p: (p[0] * SS, p[1] * SS)
    tip = (W + 50, 232)
    poly = [(W - 4, 207), (W + 22, 216), tip, (W + 22, 252), (W - 4, 267)]
    d.polygon([k(p) for p in poly], fill=col + (255,))
    d.line([k((W - 4, 208)), k((W + 22, 216)), k(tip)], fill=(30, 30, 25, 255), width=5 * SS, joint="curve")
    d.line([k((W - 4, 267)), k((W + 22, 252)), k(tip)], fill=(30, 30, 25, 255), width=4 * SS, joint="curve")
    L = L.resize(c.size, Image.LANCZOS)
    return Image.alpha_composite(c, L)


def sok(b: Image.Image) -> Image.Image:
    a = np.array(b)
    for (x0, y0, x1, y1) in [(468, 318, 788, 440), (548, 575, 728, 660)]:
        reg = a[y0:y1, x0:x1]
        m = reg[..., 3] > 0
        reg[m, :3] = 255
    im = Image.fromarray(a)
    W, H = im.size
    L = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    k = lambda p: (p[0] * SS, p[1] * SS)
    for cx, cy, r in [(548, 400, 40), (728, 404, 37)]:
        d.ellipse([k((cx - r, cy - r)), k((cx + r, cy + r))], fill=(255, 255, 255, 255), outline=BLK, width=8 * SS)
        px = cx + 9
        d.ellipse([k((px - 9, cy - 6)), k((px + 9, cy + 12))], fill=BLK)
    d.line([k((478, 345)), k((540, 322)), k((618, 304))], fill=BLK, width=11 * SS, joint="curve")
    d.line([k((668, 302)), k((730, 322)), k((785, 350))], fill=BLK, width=11 * SS, joint="curve")
    d.ellipse([k((610, 584)), k((676, 662))], fill=(70, 25, 25, 255), outline=BLK, width=8 * SS)
    for (x0, y0, x1, y1) in [(520, 212, 524, 240), (585, 208, 590, 238), (650, 210, 653, 236), (712, 218, 717, 246), (760, 232, 764, 256)]:
        d.line([k((x0, y0)), k((x1, y1))], fill=BLUE, width=6 * SS)
    kit_varyant.SS = SS
    for x, y, s in [(865, 330, 22), (888, 450, 20), (870, 560, 18), (300, 540, 20)]:
        kit_varyant._drop(d, x, y, s)
    L = L.resize((W, H), Image.LANCZOS)
    return Image.alpha_composite(im, L)


if __name__ == "__main__":
    a = Image.open(HERE / "kaynak" / "farmer_wojak.png").convert("RGBA")
    a.crop((0, 0, 0, 0)) if False else None
    fix_brim(a).save(HERE / "a_sakin.png")
    b = Image.open(HERE / "kaynak" / "english_wojak.png").convert("RGBA")
    pad = lambda im: (lambda c: (c.paste(im, (70, 0)), c)[1])(Image.new("RGBA", (im.width + 140, im.height), (0, 0, 0, 0)))
    bp = pad(b)
    # sok() koordinatları kaynak düzleminde: pad kaydırmasını geri al
    sk = sok(b).crop((0, 0, b.width, CUT))
    Image.new("RGBA", (0, 0))
    out_s = pad(sk)
    out_s.save(HERE / "b_sok.png")
    bp.crop((0, 0, bp.width, CUT)).save(HERE / "b_sakin.png")
