"""en-wojtek-soldier-bear karakterleri:  python episodes/en-wojtek-soldier-bear/chars/uret.py

A (sol, er): wojakland 'Polish Military WWII Wojak' (kaynak/polish_military_WWII_wojak.png, 757x742); a_sakin.png = kaynağın kendisi.
  a_sok.png (ters köşe, aynı kutu): göz/kaş/ağız ve alın kırışıkları silinir; iri yuvarlak göz + küçük göz bebeği,
  iç ucu kalkık kalın kaş, "O" ağız, alında mavi çizgiler, başın yanında kontur dışında ter damlaları. Silüet ve kıyafet aynı.
B (sağ, subay): wojakland 'Polish Legionary Wojak' (kaynak/polish_legionary_wojak.png, 856x812); b_sakin.png = kaynağın kendisi.
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


def sok(a: Image.Image) -> Image.Image:
    arr = np.array(a)
    # eski göz, kaş/kırışık ve ağız: ten (beyaz) üstündeki opak pikselleri beyaza boya
    for (x0, y0, x1, y1) in [(366, 166, 446, 244), (478, 166, 556, 250), (414, 340, 512, 364)]:
        reg = arr[y0:y1, x0:x1]
        m = reg[..., 3] > 0
        for cx in range(reg.shape[1]):  # miğferin altındaki ilk beyaz ten pikselinden öncesine dokunma
            col = arr[140:y1, x0 + cx, :3].astype(int).sum(-1)
            white = np.where(col > 720)[0]
            top = (140 + white[0]) if len(white) else y0
            m[: max(0, top - y0), cx] = False
        reg[m, :3] = 255
    im = Image.fromarray(arr)
    W, H = im.size
    L = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    k = lambda p: (p[0] * SS, p[1] * SS)
    for cx, cy, r in [(409, 226, 30), (524, 230, 28)]:
        d.ellipse([k((cx - r, cy - r)), k((cx + r, cy + r))], fill=(255, 255, 255, 255), outline=BLK, width=8 * SS)
        px = cx + 8
        d.ellipse([k((px - 8, cy - 6)), k((px + 8, cy + 12))], fill=BLK)
    d.line([k((368, 204)), k((400, 190)), k((442, 182))], fill=BLK, width=10 * SS, joint="curve")
    d.line([k((494, 182)), k((534, 190)), k((562, 206))], fill=BLK, width=10 * SS, joint="curve")
    d.ellipse([k((443, 330)), k((483, 382))], fill=(70, 25, 25, 255), outline=BLK, width=7 * SS)
    for (x0, y0, x1, y1) in [(398, 170, 400, 183), (430, 169, 432, 182), (468, 169, 470, 182), (506, 171, 508, 184)]:
        d.line([k((x0, y0)), k((x1, y1))], fill=BLUE, width=5 * SS)
    kit_varyant.SS = SS
    for x, y, s in [(604, 300, 14), (612, 350, 12), (598, 398, 11)]:
        kit_varyant._drop(d, x, y, s)
    L = L.resize((W, H), Image.LANCZOS)
    return Image.alpha_composite(im, L)


if __name__ == "__main__":
    a = Image.open(HERE / "kaynak" / "polish_military_WWII_wojak.png").convert("RGBA")
    a.save(HERE / "a_sakin.png")
    sok(a).save(HERE / "a_sok.png")
    Image.open(HERE / "kaynak" / "polish_legionary_wojak.png").convert("RGBA").save(HERE / "b_sakin.png")
