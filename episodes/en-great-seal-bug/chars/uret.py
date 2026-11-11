"""en-great-seal-bug karakterleri:  python episodes/en-great-seal-bug/chars/uret.py

A (sol, Sovyet heyet temsilcisi): wojakland 'Soviet Cap Wojak' (kaynak/a_kaynak.png), a_sakin.png = kaynağın kendisi.
B (sağ, ABD büyükelçisi rolü): wojakland 'Grey Suit Wojak' (kaynak/b_kaynak.png), b_sakin.png = kaynak (yanlara boşluk).
  b_sok.png (ters köşe, aynı kutu): göz/ağız silinip iri yuvarlak göz + küçük göz bebeği, iç ucu kalkık kalın kaş,
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
PADX = 130


def pad(im: Image.Image) -> Image.Image:
    c = Image.new("RGBA", (im.width + 2 * PADX, im.height), (0, 0, 0, 0))
    c.paste(im, (PADX, 0))
    return c


def sok(b: Image.Image) -> Image.Image:
    a = np.array(b)
    # göz bölgeleri ve ağız: yüz rengi (beyaz) ile doldur (yalnız opak pikseller)
    for (x0, y0, x1, y1) in [(455, 255, 745, 352), (528, 488, 690, 545)]:
        reg = a[y0:y1, x0:x1]
        m = reg[..., 3] > 0
        reg[m, :3] = 255
    im = Image.fromarray(a)
    W, H = im.size
    L = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    k = lambda p: (p[0] * SS, p[1] * SS)
    for cx, cy, r in [(512, 312, 40), (700, 322, 37)]:
        d.ellipse([k((cx - r, cy - r)), k((cx + r, cy + r))], fill=(255, 255, 255, 255), outline=BLK, width=8 * SS)
        px = cx + 9
        d.ellipse([k((px - 9, cy - 6)), k((px + 9, cy + 12))], fill=BLK)
    # kaşlar: iç uçlar yukarı
    d.line([k((440, 262)), k((500, 238)), k((570, 222))], fill=BLK, width=11 * SS, joint="curve")
    d.line([k((640, 224)), k((705, 240)), k((748, 268))], fill=BLK, width=11 * SS, joint="curve")
    # "O" ağız
    d.ellipse([k((568, 482)), k((636, 562))], fill=(70, 25, 25, 255), outline=BLK, width=8 * SS)
    # alında mavi çizgiler
    for (x0, y0, x1, y1) in [(520, 128, 523, 158), (575, 124, 578, 154), (630, 126, 633, 156), (685, 134, 689, 164), (730, 156, 735, 186)]:
        d.line([k((x0, y0)), k((x1, y1))], fill=BLUE, width=6 * SS)
    L = L.resize((W, H), Image.LANCZOS)
    return Image.alpha_composite(im, L)


def drops(im: Image.Image, pts) -> Image.Image:
    W, H = im.size
    L = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    kit_varyant.SS = SS
    for x, y, s in pts:
        kit_varyant._drop(d, x, y, s)
    return Image.alpha_composite(im, L.resize((W, H), Image.LANCZOS))


if __name__ == "__main__":
    a = Image.open(HERE / "kaynak" / "a_kaynak.png").convert("RGBA")
    a.save(HERE / "a_sakin.png")
    b = Image.open(HERE / "kaynak" / "b_kaynak.png").convert("RGBA")
    pad(b).save(HERE / "b_sakin.png")
    sk = sok(b)
    out = pad(sk)
    out = drops(out, [(PADX + 812, 260, 22), (PADX + 836, 380, 20), (PADX + 818, 490, 18), (PADX + 215, 330, 20)])
    out.save(HERE / "b_sok.png")
