"""en-lincoln-body-snatchers karakterleri:  python episodes/en-lincoln-body-snatchers/chars/uret.py

A (sol, sahte para cetesi lideri rolu): wl:irish_wojak (569x677), 2x LANCZOS + UnsharpMask -> a_sakin.png.
B (sag, cete uyesi rolu): wl:worker_2_wojak (1153x1177), gogusten kesilir -> b_sakin.png.
b_sok.png (ters kose, ayni kutu): goz/kas/forehead cizgileri silinip iri yuvarlak goz + kucuk goz bebegi,
  ic ucu kalkik kalin kas, "O" agiz, mavi cizgiler, basin disinda ter damlalari. Siluet ve kiyafet ayni.
Ham kaynaklar chars/src/ (wojak_site.py get ile indirildi).
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
BLK = (0, 0, 0, 255)
CROP_Y = 1010


def a_sakin() -> Image.Image:
    a = Image.open(HERE / "src/a_src.png").convert("RGBA")
    a = a.resize((a.width * 2, a.height * 2), Image.LANCZOS)
    return a.filter(ImageFilter.UnsharpMask(2, 60, 2))


def b_sakin() -> Image.Image:
    b = Image.open(HERE / "src/b_src.png").convert("RGBA")
    return b.crop((0, 0, b.width, CROP_Y))


def sok(b: Image.Image) -> Image.Image:
    a = np.array(b)
    # yuz ici: gozler, kaslar, alin cizgileri silinir (yalniz opak pikseller beyaz)
    for (x0, y0, x1, y1) in [(640, 280, 975, 440)]:
        reg = a[y0:y1, x0:x1]
        m = reg[..., 3] > 0
        reg[m, :3] = 255
    im = Image.fromarray(a)
    W, H = im.size
    L = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    k = lambda p: (p[0] * SS, p[1] * SS)
    for cx, cy, r in [(722, 388, 40), (893, 394, 38)]:
        d.ellipse([k((cx - r, cy - r)), k((cx + r, cy + r))], fill=(255, 255, 255, 255), outline=BLK, width=8 * SS)
        px = cx - 8  # bakis iceri (dosyada sagdan bakiyor degil: sola) -> asagida yon kaydina gore
        d.ellipse([k((px - 10, cy - 6)), k((px + 10, cy + 14))], fill=BLK)
    d.line([k((655, 345)), k((730, 322)), k((806, 308))], fill=BLK, width=12 * SS, joint="curve")
    d.line([k((850, 312)), k((905, 326)), k((962, 354))], fill=BLK, width=12 * SS, joint="curve")
    # O agiz (bıyık altinda, sakal ustu)
    d.ellipse([k((768, 578)), k((852, 678))], fill=(70, 25, 25, 255), outline=BLK, width=8 * SS)
    # mavi cizgiler (yuz ustunde, alin/sakak)
    for (x0, y0, x1, y1) in [(690, 280, 693, 300), (745, 282, 748, 302), (800, 280, 802, 298), (905, 286, 908, 304), (950, 296, 952, 314)]:
        d.line([k((x0, y0)), k((x1, y1))], fill=BLUE, width=7 * SS)
    kit_varyant.SS = SS
    for x, y, s in [(1040, 340, 24), (1075, 470, 22), (1050, 600, 20), (385, 500, 22)]:
        kit_varyant._drop(d, x, y, s)
    L = L.resize((W, H), Image.LANCZOS)
    return Image.alpha_composite(im, L)


if __name__ == "__main__":
    a_sakin().save(HERE / "a_sakin.png")
    b = b_sakin()
    b.save(HERE / "b_sakin.png")
    sok(b).save(HERE / "b_sok.png")
