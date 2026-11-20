"""en-lorz-1904-marathon karakterleri:  python episodes/en-lorz-1904-marathon/chars/uret.py

A (sol, kosucu/duvarci rolu): wojakland Worker 2 Wojak (src/a_kaynak.png, 1153x1177; gri kasket + tulum), degistirilmedi.
B (sag, gorevli rolu): en-booth-saves-lincoln-son ile ayni kaynak (kaynak/wojak_with_suit_hd.png), sakin + sok.
  Pipo ve duman silinir (iki varyantta da, silüet aynı); b_sakin.png kapalı ağız.
  b_sok.png (ters köşe, aynı kutu): göz silinip iri yuvarlak göz + küçük göz bebeği, kızgın kaş yerine kalkık yay kaş,
  "O" ağız, alında mavi çizgiler ve yüzün önünde kontur dışında 3 ter damlası.
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
PAD = 70                      # sol boşluk: damlalar için
SKIN = (255, 215, 184, 255)
BLUE = (60, 120, 200, 255)
BLACK = (0, 0, 0, 255)


# ---- Booth v2: wojakland/HF 'Wojak With Suit HD' (kaynak/wojak_with_suit_hd.png, kel, papyonlu siyah takım) ----
S2 = 2


def _white_black(a, box):
    x0, y0, x1, y1 = box
    reg = a[y0:y1, x0:x1]
    reg[reg[..., 3] > 0, :3] = 255


def booth_sakin() -> Image.Image:
    im = Image.open(HERE / "kaynak" / "wojak_with_suit_hd.png").convert("RGBA")
    a = np.array(im)
    _white_black(a, (800, 795, 1215, 900))          # sırıtma ve gamze çizgisi silinir
    im = Image.fromarray(a)
    L2 = Image.new("RGBA", (im.width * S2, im.height * S2), (0, 0, 0, 0))
    d = ImageDraw.Draw(L2)
    d.line([(925 * S2, 852 * S2), (1020 * S2, 862 * S2), (1125 * S2, 858 * S2)], fill=BLACK, width=10 * S2, joint="curve")
    return Image.alpha_composite(im, L2.resize(im.size, Image.LANCZOS))


def booth_sok() -> Image.Image:
    im = booth_sakin()
    a = np.array(im)
    for box in [(800, 400, 1035, 565), (1130, 400, 1318, 590), (900, 820, 1160, 900)]:
        _white_black(a, box)
    im = Image.fromarray(a)
    W, H = im.size
    L2 = Image.new("RGBA", (W * S2, H * S2), (0, 0, 0, 0))
    d = ImageDraw.Draw(L2)
    k = lambda p: (p[0] * S2, p[1] * S2)
    for cx, cy, r in [(915, 520, 52), (1225, 535, 48)]:
        d.ellipse([k((cx - r, cy - r)), k((cx + r, cy + r))], fill=(255, 255, 255, 255), outline=BLACK, width=11 * S2)
        px = cx + 12
        d.ellipse([k((px - 13, cy - 10)), k((px + 13, cy + 16))], fill=BLACK)
    d.line([k((835, 448)), k((895, 408)), k((975, 402)), k((1020, 424))], fill=BLACK, width=15 * S2, joint="curve")
    d.line([k((1150, 420)), k((1215, 398)), k((1290, 420))], fill=BLACK, width=15 * S2, joint="curve")
    d.ellipse([k((985, 820)), k((1085, 905))], fill=(90, 25, 25, 255), outline=BLACK, width=11 * S2)
    for p in [[(920, 150), (942, 198)], [(990, 135), (1006, 186)], [(1060, 132), (1070, 184)], [(1130, 145), (1138, 196)]]:
        d.line([k(p[0]), k(p[1])], fill=BLUE, width=11 * S2, joint="curve")
    kit_varyant.SS = S2
    for x, y, s in [(1385, 400, 32), (1408, 505, 32), (1378, 610, 28)]:
        kit_varyant._drop(d, x, y, s)
    return Image.alpha_composite(im, L2.resize((W, H), Image.LANCZOS))



def runner() -> Image.Image:
    im = Image.open(HERE / "src" / "a_kaynak.png").convert("RGBA")
    return im.crop((0, 0, im.width, 1060))   # gogusten kes: yuz buyur (baska bolumle bayt ayni olmasin)


if __name__ == "__main__":
    runner().save(HERE / "a_sakin.png")
    booth_sakin().save(HERE / "b_sakin.png")
    booth_sok().save(HERE / "b_sok.png")
