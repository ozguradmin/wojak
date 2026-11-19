"""en-caesar-pirates karakterleri:  python episodes/en-caesar-pirates/chars/uret.py

A (sol, korsan kaptan rolu, kurgu): wl:eyepatch_pirate_2_wojak (880x1023; ucgen sapka, goz bandi, gri sakal) -> alttan 930'a kesilir,
  yanlara 70 px pay (ter damlasi icin) -> a_sakin.png.
B (sag, Julius Caesar rolu, kurgu): wl:julius_caesar_wojak (640x629; defne tacli) -> 2x LANCZOS + UnsharpMask, pay -> b_sakin.png.
a_sok.png (ters kose, ayni kutu): goz/kas silinir; iri yuvarlak goz + kucuk goz bebegi, ic ucu kalkik kalin kas, "O" agiz,
  alinda mavi cizgiler, basin disinda ter damlalari. Siluet ve kiyafet ayni.
"""
from __future__ import annotations
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import kit_varyant  # noqa: E402

SS = 4
BLUE = (60, 120, 200, 255)
BLK = (0, 0, 0, 255)
WHT = (255, 255, 255, 255)
PAD = 70


def a_sakin() -> Image.Image:
    a = Image.open(HERE / "src/a_src.png").convert("RGBA").crop((0, 0, 880, 930))
    out = Image.new("RGBA", (a.width + 2 * PAD, a.height), (0, 0, 0, 0))
    out.alpha_composite(a, (PAD, 0))
    return out


def b_sakin() -> Image.Image:
    b = Image.open(HERE / "src/b_src.png").convert("RGBA")
    b = b.resize((b.width * 2, b.height * 2), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 60, 2))
    out = Image.new("RGBA", (b.width + 2 * PAD, b.height), (0, 0, 0, 0))
    out.alpha_composite(b, (PAD, 0))
    return out


def sok(a: Image.Image) -> Image.Image:
    im = a.copy()
    W, H = im.size
    L = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    k = lambda p: (p[0] * SS, p[1] * SS)
    # eski goz, kas ve yara izini beyazla (sapka kenari ve goz bandi korunur)
    d.ellipse([k((PAD + 425, 425)), k((PAD + 560, 545))], fill=WHT)
    d.polygon([k((PAD + 400, 408)), k((PAD + 530, 398)), k((PAD + 532, 430)), k((PAD + 402, 436))], fill=WHT)
    d.polygon([k((PAD + 628, 372)), k((PAD + 722, 366)), k((PAD + 722, 396)), k((PAD + 628, 398))], fill=WHT)
    # iri goz (sol, acik goz): beyaz + kucuk goz bebegi (dosya sola bakar)
    cx, cy, r = PAD + 488, 478, 50
    d.ellipse([k((cx - r, cy - r)), k((cx + r, cy + r))], fill=WHT, outline=BLK, width=9 * SS)
    d.ellipse([k((cx - 27, cy - 4)), k((cx - 5, cy + 18))], fill=BLK)
    # kalkik kalin kaslar (ic uclari burna dogru yukari)
    d.line([k((PAD + 402, 432)), k((PAD + 455, 418)), k((PAD + 532, 400))], fill=BLK, width=14 * SS, joint="curve")
    d.line([k((PAD + 622, 402)), k((PAD + 672, 384)), k((PAD + 722, 388))], fill=BLK, width=14 * SS, joint="curve")
    # O agiz
    d.ellipse([k((PAD + 538, 640)), k((PAD + 618, 706))], fill=(70, 25, 25, 255), outline=BLK, width=8 * SS)
    # alin cizgileri (sapkanin altinda, yanaga degil)
    for x0, y0, x1, y1 in [(PAD + 412, 404, PAD + 414, 418), (PAD + 452, 399, PAD + 454, 413), (PAD + 492, 394, PAD + 494, 408)]:
        d.line([k((x0, y0)), k((x1, y1))], fill=BLUE, width=7 * SS)
    kit_varyant.SS = SS
    for x, y, s in [(PAD + 790, 330, 22), (PAD + 800, 470, 20), (PAD + 770, 610, 18), (PAD + 215, 520, 20), (PAD + 225, 650, 18)]:
        kit_varyant._drop(d, x, y, s)
    L = L.resize((W, H), Image.LANCZOS)
    return Image.alpha_composite(im, L)


if __name__ == "__main__":
    a = a_sakin()
    a.save(HERE / "a_sakin.png")
    b_sakin().save(HERE / "b_sakin.png")
    sok(a).save(HERE / "a_sok.png")
