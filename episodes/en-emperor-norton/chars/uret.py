"""en-emperor-norton karakterleri:  python episodes/en-emperor-norton/chars/uret.py

A (sol, 1867 SF mahalle muhafizi rolu, kurgu): wl:suit_wojak (820x768; yirtik ucu gri, biyikli, papyon) -> yanlara 70 px pay -> a_sakin.png.
B (sag, Norton rolu, kurgu): wl:civil_war_wojak (640x860; mavi kepi, mavi ceket, sari dugme). Dis gulusu (sirıtma = kotu karakter)
  beyaza boyanip kapali sakin agiz cizilir; 2x LANCZOS + UnsharpMask -> gogusten (y=660) kesilir -> b_sakin.png.
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
PAD = 72


def a_sakin() -> Image.Image:
    a = Image.open(HERE / "src/suit_wojak.png").convert("RGBA")
    out = Image.new("RGBA", (a.width + 2 * PAD, a.height), (0, 0, 0, 0))
    out.alpha_composite(a, (PAD, 0))
    return out


def b_sakin() -> Image.Image:
    b = Image.open(HERE / "src/civil_war_wojak.png").convert("RGBA")
    W, H = b.size
    L = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    k = lambda p: (p[0] * SS, p[1] * SS)
    d.ellipse([k((366, 404)), k((476, 470))], fill=WHT)           # dis gulusu + biyik izi
    d.line([k((386, 442)), k((425, 447)), k((466, 436))], fill=BLK, width=7 * SS, joint="curve")  # kapali sakin agiz
    L = L.resize((W, H), Image.LANCZOS)
    b = Image.alpha_composite(b, L).crop((0, 0, W, 660))  # gogusten kes: yuz buyur
    b = b.resize((W * 2, H * 2), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 60, 2))
    out = Image.new("RGBA", (b.width + 2 * PAD, b.height), (0, 0, 0, 0))
    out.alpha_composite(b, (PAD, 0))
    return out


def sok(a: Image.Image) -> Image.Image:
    im = a.copy()
    W, H = im.size
    L = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    k = lambda p: (p[0] * SS, p[1] * SS)
    # eski goz, kas ve goz alti kirisikliklarini beyazla
    d.ellipse([k((PAD + 372, 250)), k((PAD + 526, 400))], fill=WHT)
    d.ellipse([k((PAD + 576, 250)), k((PAD + 704, 412))], fill=WHT)
    # iri goz (dosya saga bakar: goz bebegi gozun sag ucuna)
    for cx, cy in [(PAD + 448, 318), (PAD + 640, 322)]:
        r = 50
        d.ellipse([k((cx - r, cy - r)), k((cx + r, cy + r))], fill=WHT, outline=BLK, width=9 * SS)
        d.ellipse([k((cx + 3, cy - 4)), k((cx + 25, cy + 18))], fill=BLK)
    # kalkik kalin kaslar (ic uclari burna dogru yukari)
    d.line([k((PAD + 372, 235)), k((PAD + 420, 232)), k((PAD + 496, 206))], fill=BLK, width=14 * SS, joint="curve")
    d.line([k((PAD + 590, 206)), k((PAD + 650, 226)), k((PAD + 706, 238))], fill=BLK, width=14 * SS, joint="curve")
    # O agiz (biyigin alt ortasinda)
    d.ellipse([k((PAD + 512, 482)), k((PAD + 590, 562))], fill=(70, 25, 25, 255), outline=BLK, width=8 * SS)
    # alin cizgileri (alin uzerinde, yanaga degil)
    for x0, y0 in [(PAD + 410, 128), (PAD + 470, 120), (PAD + 530, 118), (PAD + 590, 124), (PAD + 640, 134)]:
        d.line([k((x0, y0)), k((x0 + 2, y0 + 30))], fill=BLUE, width=7 * SS)
    kit_varyant.SS = SS
    for x, y, s in [(PAD + 770, 250, 22), (PAD + 780, 400, 20), (PAD + 760, 540, 18), (PAD + 170, 200, 20), (PAD + 150, 330, 18)]:
        kit_varyant._drop(d, x, y, s)
    L = L.resize((W, H), Image.LANCZOS)
    return Image.alpha_composite(im, L)


if __name__ == "__main__":
    a = a_sakin()
    a.save(HERE / "a_sakin.png")
    b_sakin().save(HERE / "b_sakin.png")
    sok(a).save(HERE / "a_sok.png")
