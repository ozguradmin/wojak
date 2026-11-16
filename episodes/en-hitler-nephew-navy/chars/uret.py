"""en-hitler-nephew-navy karakterleri:  python episodes/en-hitler-nephew-navy/chars/uret.py

A (sol, William rolu): wl:grey_suit_wojak (900x870), degistirilmedi -> a_sakin.png.
B (sag, Donanma subayi rolu): wl:us_marines_white_wojak (878x1400), gogusten kesilir (y<900) -> b_sakin.png.
b_sok.png (ters kose, ayni kutu): goz/kas cizgileri silinip iri yuvarlak goz + kucuk goz bebegi, ic ucu kalkik kalin kas,
  "O" agiz, alinda mavi cizgiler, basin disinda ter damlalari. Siluet ve kiyafet ayni.
Ham kaynaklar chars/src/ (wojak_site.py get ile indirildi).
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
CROP_Y = 900


def a_sakin() -> Image.Image:
    return Image.open(HERE / "src/a_src.png").convert("RGBA")


def b_sakin() -> Image.Image:
    b = Image.open(HERE / "src/b_src.png").convert("RGBA")
    return b.crop((0, 0, b.width, CROP_Y))


def sok(b: Image.Image) -> Image.Image:
    a = np.array(b)
    for (x0, y0, x1, y1) in [(425, 328, 684, 411), (485, 535, 622, 600)]:
        reg = a[y0:y1, x0:x1]
        m = reg[..., 3] > 0
        reg[m, :3] = 255
    im = Image.fromarray(a)
    W, H = im.size
    L = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    k = lambda p: (p[0] * SS, p[1] * SS)
    for cx, cy, r in [(485, 392, 36), (632, 392, 34)]:
        d.ellipse([k((cx - r, cy - r)), k((cx + r, cy + r))], fill=(255, 255, 255, 255), outline=BLK, width=7 * SS)
        px = cx + 8  # dosyada saga bakiyor
        d.ellipse([k((px - 9, cy - 5)), k((px + 9, cy + 13))], fill=BLK)
    d.line([k((428, 356)), k((470, 342)), k((520, 332))], fill=BLK, width=11 * SS, joint="curve")
    d.line([k((600, 332)), k((650, 342)), k((690, 358))], fill=BLK, width=11 * SS, joint="curve")
    d.ellipse([k((530, 528)), k((600, 612))], fill=(70, 25, 25, 255), outline=BLK, width=7 * SS)
    for (x0, y0, x1, y1) in [(440, 318, 442, 332), (482, 316, 484, 330), (540, 318, 542, 333), (600, 316, 602, 330), (650, 319, 652, 333)]:
        d.line([k((x0, y0)), k((x1, y1))], fill=BLUE, width=7 * SS)
    kit_varyant.SS = SS
    for x, y, s in [(750, 350, 22), (775, 455, 21), (745, 560, 20), (205, 470, 21)]:
        kit_varyant._drop(d, x, y, s)
    L = L.resize((W, H), Image.LANCZOS)
    return Image.alpha_composite(im, L)


if __name__ == "__main__":
    a_sakin().save(HERE / "a_sakin.png")
    b = b_sakin()
    b.save(HERE / "b_sakin.png")
    sok(b).save(HERE / "b_sok.png")
