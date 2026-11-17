"""en-abbott-golf-1900 karakterleri:  python episodes/en-abbott-golf-1900/chars/uret.py

A (sol, Margaret rolu, kurgu): HF clayshoaf/Wojaks 5_Doomer_Girl/2418 'Southern Belle' (768x1030; pembe sapka, elbise)
  -> bel ustunden kesilir, 2x LANCZOS + UnsharpMask -> a_sakin.png.
B (sag, arkadas/anlatici rolu): wl:suit_wojak (820x768; biyik, papyon) -> 60 px pay, b_sakin.png.
b_sok.png (ters kose, ayni kutu): goz/kas/alin cizgileri silinir; iri yuvarlak goz + kucuk goz bebegi, ic ucu kalkik kalin kas,
  "O" agiz, alinda mavi cizgiler, basin disinda ter damlalari. Siluet ve kiyafet ayni.
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
PAD = 70


def a_sakin() -> Image.Image:
    a = Image.open(HERE / "src/a_src.png").convert("RGBA")
    a = a.crop((0, 0, a.width, 700))
    a = a.resize((a.width * 2, a.height * 2), Image.LANCZOS)
    return a.filter(ImageFilter.UnsharpMask(2, 60, 2))


def b_sakin() -> Image.Image:
    b = Image.open(HERE / "src/b_src.png").convert("RGBA")
    out = Image.new("RGBA", (b.width + 2 * PAD, b.height), (0, 0, 0, 0))
    out.alpha_composite(b, (PAD, 0))
    return out


def sok(b: Image.Image) -> Image.Image:
    a = np.array(b)
    # yuz ici ozellikleri (goz, kas, alin cizgileri) siler: kutudaki KUCUK koyu bilesenler; kontur ve sac buyuk bilesen, kalir
    from scipy import ndimage
    dark = (a[..., 3] > 0) & (a[..., :3].sum(axis=2) < 200)
    lab, n = ndimage.label(dark, structure=np.ones((3, 3)))
    sizes = ndimage.sum(dark, lab, range(1, n + 1))
    x0, y0, x1, y1 = PAD + 330, 130, PAD + 700, 412
    for i in range(1, n + 1):
        ys, xs = np.nonzero(lab == i)
        if sizes[i - 1] < 6000 and xs.min() >= x0 and xs.max() <= x1 and ys.min() >= y0 and ys.max() <= y1:
            m = ndimage.binary_dilation(lab == i, iterations=4) & (a[..., 3] > 0) & (a[..., :3].sum(axis=2) > 150) | (lab == i)
            a[m, :3] = 255
    im = Image.fromarray(a)
    W, H = im.size
    L = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    k = lambda p: (p[0] * SS, p[1] * SS)
    for cx, cy, r in [(PAD + 447, 312, 46), (PAD + 632, 318, 44)]:
        d.ellipse([k((cx - r, cy - r)), k((cx + r, cy + r))], fill=(255, 255, 255, 255), outline=BLK, width=8 * SS)
        px = cx - 8
        d.ellipse([k((px - 10, cy - 4)), k((px + 10, cy + 16))], fill=BLK)
    d.line([k((PAD + 372, 250)), k((PAD + 448, 222)), k((PAD + 515, 215))], fill=BLK, width=12 * SS, joint="curve")
    d.line([k((PAD + 575, 222)), k((PAD + 635, 228)), k((PAD + 700, 262))], fill=BLK, width=12 * SS, joint="curve")
    # O agiz (biyigin altinda)
    d.ellipse([k((PAD + 505, 540)), k((PAD + 575, 596))], fill=(70, 25, 25, 255), outline=BLK, width=8 * SS)
    for (x0, y0, x1, y1) in [(PAD + 420, 150, PAD + 423, 172), (PAD + 480, 143, PAD + 483, 166),
                             (PAD + 545, 142, PAD + 547, 164), (PAD + 610, 148, PAD + 613, 170), (PAD + 665, 160, PAD + 667, 182)]:
        d.line([k((x0, y0)), k((x1, y1))], fill=BLUE, width=7 * SS)
    kit_varyant.SS = SS
    for x, y, s in [(PAD + 748, 250, 20), (PAD + 762, 390, 18), (PAD + 735, 520, 16), (212, 330, 20)]:
        kit_varyant._drop(d, x, y, s)
    L = L.resize((W, H), Image.LANCZOS)
    return Image.alpha_composite(im, L)


if __name__ == "__main__":
    a_sakin().save(HERE / "a_sakin.png")
    b = b_sakin()
    b.save(HERE / "b_sakin.png")
    sok(b).save(HERE / "b_sok.png")
