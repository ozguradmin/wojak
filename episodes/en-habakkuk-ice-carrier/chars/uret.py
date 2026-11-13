"""en-habakkuk-ice-carrier karakterleri:  python episodes/en-habakkuk-ice-carrier/chars/uret.py

A (sol, sivil mucit rolu): assets/kit/klasik/sakin.png (a_sakin.png = kitin kendisi).
B (sag, Muttefik subay rolu): assets/kit/ingiliz_er_1915/sakin.png (b_sakin.png = kitin kendisi).
b_sok.png (ters kose, ayni kutu): b_sakin uzerinde goz/bag/agiz silinip iri yuvarlak goz + kucuk goz bebegi,
  ic ucu kalkik kalin kas, "O" agiz, alinda mavi cizgiler, basin disinda ter damlalari. Silüet ve kiyafet ayni.
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


def sok(b: Image.Image) -> Image.Image:
    a = np.array(b)
    # silinecek bolgeler: gozler+gobekler, kas arasi kucuk cizgiler, agiz
    for (x0, y0, x1, y1) in [(480, 655, 730, 775), (735, 665, 905, 765), (615, 598, 655, 655), (755, 598, 785, 665), (585, 945, 815, 1005)]:
        reg = a[y0:y1, x0:x1]
        m = reg[..., 3] > 0
        reg[m, :3] = 255
    im = Image.fromarray(a)
    W, H = im.size
    L = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    k = lambda p: (p[0] * SS, p[1] * SS)
    for cx, cy, r in [(585, 695, 52), (815, 700, 48)]:
        d.ellipse([k((cx - r, cy - r)), k((cx + r, cy + r))], fill=(255, 255, 255, 255), outline=BLK, width=9 * SS)
        px = cx + 10
        d.ellipse([k((px - 11, cy - 7)), k((px + 11, cy + 15))], fill=BLK)
    # kalin kaslar, ic uclari (burun koprusu) yukarida
    d.line([k((470, 650)), k((550, 610)), k((655, 583))], fill=BLK, width=13 * SS, joint="curve")
    d.line([k((715, 583)), k((815, 610)), k((905, 655))], fill=BLK, width=13 * SS, joint="curve")
    # O agiz
    d.ellipse([k((665, 940)), k((745, 1035))], fill=(70, 25, 25, 255), outline=BLK, width=9 * SS)
    # alinda mavi ter cizgileri
    for (x0, y0, x1, y1) in [(515, 470, 519, 505), (590, 462, 594, 500), (665, 470, 668, 506), (740, 478, 744, 514), (805, 492, 809, 526)]:
        d.line([k((x0, y0)), k((x1, y1))], fill=BLUE, width=7 * SS)
    kit_varyant.SS = SS
    for x, y, s in [(975, 560, 24), (990, 690, 22), (968, 820, 20), (150, 700, 22)]:
        kit_varyant._drop(d, x, y, s)
    L = L.resize((W, H), Image.LANCZOS)
    return Image.alpha_composite(im, L)


if __name__ == "__main__":
    b = Image.open(ROOT / "assets/kit/ingiliz_er_1915/sakin.png").convert("RGBA")
    sok(b).save(HERE / "b_sok.png")
