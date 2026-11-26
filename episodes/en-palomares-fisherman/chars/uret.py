"""en-palomares-fisherman karakterleri:  python episodes/en-palomares-fisherman/chars/uret.py

FISHER (solda, balıkçı rolü, kurgu): wl:breton_fisherman_wojak (442x500; kırmızı bere, sarı gömlek) -> 2x yumuşak büyütme -> fisher_sakin.png.
ADMIRAL (sağda, ABD Donanması amirali rolü, kurgu): wl:us_marines_wojak (1032x1645 -> 878x1400; siyah üniforma, beyaz kep), göğüsten kesilir -> admiral_sakin.png.
  admiral_sok.png (ters köşe, aynı kutu): göz/kaş/ağız silinir; iri yuvarlak göz + küçük bebek, kalkık kalın kaş, "O" ağız, baş dışında ter damlaları.
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
WHT = (255, 255, 255, 255)
PAD = 100


def buyut2(im: Image.Image) -> Image.Image:
    a = im.resize((im.width * 2, im.height * 2), Image.LANCZOS)
    rgb = a.convert("RGB").filter(ImageFilter.UnsharpMask(2, 70, 2))
    out = rgb.convert("RGBA")
    out.putalpha(a.getchannel("A").point(lambda v: 255 if v > 127 else 0))
    return out


def pad(im: Image.Image, p: int = PAD) -> Image.Image:
    out = Image.new("RGBA", (im.width + 2 * p, im.height), (0, 0, 0, 0))
    out.alpha_composite(im, (p, 0))
    return out


def fisher_sakin() -> Image.Image:
    return pad(buyut2(Image.open(HERE / "src/fisher_src.png").convert("RGBA")))


CROP_Y = 880


def admiral_sakin() -> Image.Image:
    im = Image.open(HERE / "src/admiral_src.png").convert("RGBA").crop((0, 0, 878, CROP_Y))
    return pad(im)


def admiral_sok(a: Image.Image) -> Image.Image:
    im = a.copy()
    W, H = im.size
    L = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    k = lambda p: (p[0] * SS, p[1] * SS)
    X = lambda x: x + PAD
    # eski göz, kaş, göz altı çizgileri ve ağız beyazlanır
    d.polygon([k((X(405), 338)), k((X(590), 330)), k((X(690), 345)), k((X(690), 440)), k((X(520), 452)), k((X(405), 440))], fill=WHT)
    d.polygon([k((X(500), 530)), k((X(650), 530)), k((X(650), 585)), k((X(500), 585))], fill=WHT)
    for cx, cy, r in [(X(472), 392, 38), (X(618), 394, 38)]:
        d.ellipse([k((cx - r, cy - r)), k((cx + r, cy + r))], fill=WHT, outline=BLK, width=8 * SS)
        d.ellipse([k((cx + 7, cy - 4)), k((cx + 25, cy + 14))], fill=BLK)
    d.line([k((X(425), 360)), k((X(462), 342)), k((X(512), 334))], fill=BLK, width=11 * SS, joint="curve")
    d.line([k((X(580), 334)), k((X(634), 344)), k((X(676), 362))], fill=BLK, width=11 * SS, joint="curve")
    d.ellipse([k((X(540), 534)), k((X(594), 596))], fill=(70, 25, 25, 255), outline=BLK, width=8 * SS)
    kit_varyant.SS = SS
    for x, y, s in [(X(745), 330, 22), (X(762), 450, 20), (X(735), 570, 18), (X(190), 360, 20), (X(175), 470, 18)]:
        kit_varyant._drop(d, x, y, s)
    L = L.resize((W, H), Image.LANCZOS)
    return Image.alpha_composite(im, L)


if __name__ == "__main__":
    fisher_sakin().save(HERE / "fisher_sakin.png")
    a = admiral_sakin()
    a.save(HERE / "admiral_sakin.png")
    admiral_sok(a).save(HERE / "admiral_sok.png")
    print(a.size)
