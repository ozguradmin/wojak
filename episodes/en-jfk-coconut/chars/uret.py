"""en-jfk-coconut karakterleri:  python episodes/en-jfk-coconut/chars/uret.py

A (sol, denizci rolu, kurgu): wl:us_marines_wojak (878x1400; siyah donanma ceketi, sakalli) -> gogusten 960'a kesilir,
  yanlara 70 px pay (ter damlasi icin) -> a_sakin.png.
B (sag, Teğmen Kennedy rolu, kurgu): wl:us_marines_white_wojak (878x1400; beyaz donanma ceketi) -> gogusten 960'a kesilir -> b_sakin.png.
a_sok.png (ters kose, ayni kutu): goz/kas silinir; iri yuvarlak goz + kucuk goz bebegi, ic ucu kalkik kalin kas, "O" agiz,
  alinda mavi cizgiler, basin disinda ter damlalari. Siluet ve kiyafet ayni.
"""
from __future__ import annotations
import sys
from pathlib import Path
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import kit_varyant  # noqa: E402

SS = 4
BLUE = (60, 120, 200, 255)
BLK = (0, 0, 0, 255)
WHT = (255, 255, 255, 255)
PAD = 70
CUT = 960


def kes(src: str) -> Image.Image:
    a = Image.open(HERE / src).convert("RGBA").crop((0, 0, 878, CUT))
    out = Image.new("RGBA", (a.width + 2 * PAD, a.height), (0, 0, 0, 0))
    out.alpha_composite(a, (PAD, 0))
    return out


def sok(a: Image.Image) -> Image.Image:
    im = a.copy()
    W, H = im.size
    L = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    k = lambda p: (p[0] * SS, p[1] * SS)
    # eski goz, goz torbasi, kas ve agiz cizgisini beyazla (sapka ve yuz konturu korunur)
    d.ellipse([k((PAD + 418, 352)), k((PAD + 545, 448))], fill=WHT)
    d.ellipse([k((PAD + 578, 358)), k((PAD + 678, 452))], fill=WHT)
    d.rectangle([k((PAD + 495, 535)), k((PAD + 615, 580))], fill=WHT)
    # iri goz + kucuk goz bebegi (dosya saga bakar)
    for cx, cy, r in [(PAD + 478, 402, 44), (PAD + 628, 408, 44)]:
        d.ellipse([k((cx - r, cy - r)), k((cx + r, cy + r))], fill=WHT, outline=BLK, width=6 * SS)
        d.ellipse([k((cx + 2, cy - 6)), k((cx + 22, cy + 14))], fill=BLK)
    # kalkik kalin kaslar (ic uclari burna dogru yukari)
    d.line([k((PAD + 420, 350)), k((PAD + 468, 340)), k((PAD + 530, 322))], fill=BLK, width=9 * SS, joint="curve")
    d.line([k((PAD + 596, 330)), k((PAD + 650, 340)), k((PAD + 692, 352))], fill=BLK, width=9 * SS, joint="curve")
    # O agiz
    d.ellipse([k((PAD + 527, 540)), k((PAD + 597, 612))], fill=(70, 25, 25, 255), outline=BLK, width=8 * SS)
    # alin cizgileri (sapkanin altinda, yanaga degil)
    for x0, y0, x1, y1 in [(PAD + 440, 318, PAD + 442, 332), (PAD + 485, 312, PAD + 487, 326), (PAD + 530, 308, PAD + 532, 322),
                           (PAD + 600, 310, PAD + 602, 324)]:
        d.line([k((x0, y0)), k((x1, y1))], fill=BLUE, width=6 * SS)
    kit_varyant.SS = SS
    for x, y, s in [(PAD + 738, 410, 20), (PAD + 750, 510, 18), (PAD + 725, 615, 16), (PAD + 245, 470, 18), (PAD + 250, 590, 16)]:
        kit_varyant._drop(d, x, y, s)
    L = L.resize((W, H), Image.LANCZOS)
    return Image.alpha_composite(im, L)


if __name__ == "__main__":
    a = kes("src/a_src.png")
    a.save(HERE / "a_sakin.png")
    kes("src/b_src.png").save(HERE / "b_sakin.png")
    sok(a).save(HERE / "a_sok.png")
