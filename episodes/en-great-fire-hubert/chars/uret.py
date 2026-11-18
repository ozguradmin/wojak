"""en-great-fire-hubert karakterleri:  python episodes/en-great-fire-hubert/chars/uret.py

A (sol, Hubert rolu, kurgu): wl:medieval_2_wojak (353x600; turuncu takke, yun tunik) -> belden kesilir, 2x LANCZOS + UnsharpMask -> a_sakin.png.
B (sag, sorgulayan/komsu rolu, kurgu): wl:medieval_citizen_wojak (387x400; gri kukuletali) -> 2x -> b_sakin.png.
b_sok.png (ters kose, ayni kutu): goz/kas cizgileri silinir; iri yuvarlak goz + kucuk goz bebegi, ic ucu kalkik kalin kas,
  "O" agiz, alin/sac cizgisinde mavi cizgiler, basin disinda ter damlalari. Siluet ve kiyafet ayni.
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


def a_sakin() -> Image.Image:
    a = Image.open(HERE / "src/medieval_2_wojak.png").convert("RGBA")
    a = a.crop((0, 0, a.width, 330))
    a = a.resize((a.width * 2, a.height * 2), Image.LANCZOS)
    return a.filter(ImageFilter.UnsharpMask(2, 60, 2))


def b_sakin() -> Image.Image:
    b = Image.open(HERE / "src/medieval_citizen_wojak.png").convert("RGBA")
    b = b.resize((b.width * 2, b.height * 2), Image.LANCZOS)
    return b.filter(ImageFilter.UnsharpMask(2, 60, 2))


def sok(b: Image.Image) -> Image.Image:
    from scipy import ndimage
    a = np.array(b)
    dark = (a[..., 3] > 0) & (a[..., :3].sum(axis=2) < 200)
    lab, n = ndimage.label(dark, structure=np.ones((3, 3)))
    sizes = ndimage.sum(dark, lab, range(1, n + 1))
    x0, y0, x1, y1 = 320, 215, 645, 372
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
    for cx, cy, r in [(403, 318, 40), (572, 322, 38)]:
        d.ellipse([k((cx - r, cy - r)), k((cx + r, cy + r))], fill=(255, 255, 255, 255), outline=BLK, width=7 * SS)
        px = cx + 8
        d.ellipse([k((px - 9, cy - 4)), k((px + 9, cy + 14))], fill=BLK)
    d.line([k((335, 265)), k((400, 238)), k((455, 232))], fill=BLK, width=11 * SS, joint="curve")
    d.line([k((520, 238)), k((575, 240)), k((632, 262))], fill=BLK, width=11 * SS, joint="curve")
    d.ellipse([k((455, 470)), k((515, 520))], fill=(70, 25, 25, 255), outline=BLK, width=7 * SS)
    for (x0_, y0_, x1_, y1_) in [(360, 200, 363, 226), (415, 192, 418, 218), (480, 188, 482, 214), (545, 192, 548, 218), (600, 205, 602, 230)]:
        d.line([k((x0_, y0_)), k((x1_, y1_))], fill=BLUE, width=7 * SS)
    kit_varyant.SS = SS
    for x, y, s in [(690, 300, 20), (700, 420, 18), (672, 520, 16), (120, 360, 20)]:
        kit_varyant._drop(d, x, y, s)
    L = L.resize((W, H), Image.LANCZOS)
    return Image.alpha_composite(im, L)


def kubbe(im: Image.Image, pad: int = 24) -> Image.Image:
    """Kaynak PNG'de kukuletanin tepesi ust kenarda kesik (y=0'da 180 px duz); yuvarlak kubbe ekler (satir 0'in rengi yukari kopyalanir)."""
    a = np.array(im)
    out = np.zeros((a.shape[0] + pad, a.shape[1], 4), dtype=np.uint8)
    out[pad:] = a
    xs = np.nonzero(a[0, :, 3] > 128)[0]
    cx, hw = (xs.min() + xs.max()) / 2, (xs.max() - xs.min()) / 2
    for d in range(1, pad + 1):
        w2 = hw * hw - 377 * d
        if w2 <= 0:
            break
        w = w2 ** 0.5
        for x in range(int(cx - w), int(cx + w) + 1):
            out[pad - d, x] = a[0, min(max(x, xs.min()), xs.max())]
    return Image.fromarray(out).filter(ImageFilter.GaussianBlur(0.0))


if __name__ == "__main__":
    a_sakin().save(HERE / "a_sakin.png")
    b = b_sakin()
    kubbe(b).save(HERE / "b_sakin.png")
    kubbe(sok(b)).save(HERE / "b_sok.png")
