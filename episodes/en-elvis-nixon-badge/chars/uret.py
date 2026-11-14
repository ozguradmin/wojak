"""en-elvis-nixon-badge karakterleri:  python episodes/en-elvis-nixon-badge/chars/uret.py

A (sol, Beyaz Saray gorevlisi rolu): assets/kit/klasik/sakin.png (a_sakin.png = kitin kendisi).
B (sag, Kurmay baskani rolu; gercek kisiyi temsil etmez): wojakland 'Grey Suit Wojak' (b_sakin.png = indirilen PNG, filigransiz).
b_sok.png (ters kose, ayni kutu): b_sakin uzerinde goz/kas/agiz/alin cizgileri silinip iri yuvarlak goz + kucuk goz bebegi,
  ic ucu kalkik kalin kas, "O" agiz, alinda mavi cizgiler, basin disinda ter damlalari. Siluet ve kiyafet ayni.
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
    # yuz ici silinecek bolgeler (yalniz koyu cizgi pikselleri beyaza)
    for (x0, y0, x1, y1) in [(440, 150, 725, 262), (455, 275, 585, 350), (650, 275, 745, 355),
                              (548, 238, 592, 290), (640, 238, 668, 295), (535, 495, 675, 545), (415, 195, 450, 232)]:
        reg = a[y0:y1, x0:x1]
        m = (reg[..., 3] > 0) & (reg[..., :3].mean(axis=2) < 250)
        reg[m, :3] = 255
    im = Image.fromarray(a)
    W, H = im.size
    L = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    k = lambda p: (p[0] * SS, p[1] * SS)
    for cx, cy, r in [(520, 312, 50), (690, 320, 46)]:
        d.ellipse([k((cx - r, cy - r)), k((cx + r, cy + r))], fill=(255, 255, 255, 255), outline=BLK, width=9 * SS)
        px = cx + 15
        d.ellipse([k((px - 11, cy - 7)), k((px + 11, cy + 15))], fill=BLK)
    # kalin kaslar, ic uclari (burun koprusu) yukarida
    d.line([k((438, 262)), k((510, 232)), k((590, 212))], fill=BLK, width=13 * SS, joint="curve")
    d.line([k((628, 214)), k((700, 238)), k((750, 268))], fill=BLK, width=13 * SS, joint="curve")
    # O agiz
    d.ellipse([k((578, 492)), k((634, 560))], fill=(70, 25, 25, 255), outline=BLK, width=9 * SS)
    # alinda mavi ter cizgileri
    for (x0, y0, x1, y1) in [(480, 128, 484, 164), (545, 122, 549, 160), (610, 120, 613, 158), (675, 124, 679, 162)]:
        d.line([k((x0, y0)), k((x1, y1))], fill=BLUE, width=7 * SS)
    kit_varyant.SS = SS
    for x, y, s in [(838, 290, 24), (850, 400, 22), (830, 505, 20), (190, 360, 22)]:
        kit_varyant._drop(d, x, y, s)
    L = L.resize((W, H), Image.LANCZOS)
    return Image.alpha_composite(im, L)


if __name__ == "__main__":
    b = Image.open(HERE / "b_sakin.png").convert("RGBA")
    sok(b).save(HERE / "b_sok.png")
