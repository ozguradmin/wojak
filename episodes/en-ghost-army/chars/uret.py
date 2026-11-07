"""en-ghost-army karakterleri:  python episodes/en-ghost-army/chars/uret.py

A (sol, asker): HF 5_Doomer/13611 'American GI' (ga_b_raw.png, 640x779), düzenlemesiz: a_sakin.png.
B (sağ, subay): HF 5_Bloomer/3664 'US Soldier' (ga_a_raw.png, 419x418). Paraşüt rozeti (kep) ve 101. Hava İndirme omuz yaması bu birliğe ait değil:
  rozet kep rengiyle kapatılıp paspas çizgisi yeniden çizilir, göğüsten (y 310) kesilir (yama/şeritler dışarıda), 3x LANCZOS + UnsharpMask: b_sakin.png.
  b_sok.png (ters köşe, aynı kutu): gözler/kaşlar/ağız silinip iri yuvarlak göz + küçük göz bebeği (sola bakar), iç ucu kalkık kalın kaş,
  "O" ağız, alında mavi çizgiler, başın önünde kontur dışında 3 ter damlası. Silüet, kep, giysi aynı.
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

F = 3
SS = 4
BLUE = (60, 120, 200, 255)
PIPE = (114, 123, 170, 255)
CAP = (49, 36, 22, 255)


def a_sakin() -> Image.Image:
    """Ham PNG'nin sağ kenarı gövdeyi düz kesiyor: omuz yuvarlanıp kol dış çizgisi (kontur kalınlığında) çizilir."""
    im = Image.open(HERE / "ga_b_raw.png").convert("RGBA")
    W, H = im.size
    S = 4
    cut = 604
    # maske: omuz üst kenarı x=568'e kadar özgün, sonra yarı çaplı yay, sonra düz kol çizgisi
    pts = [(0, 0), (W, 0), (W, 456), (570, 456)]
    import math
    for t in range(0, 91, 6):
        a = math.radians(t)
        pts.append((570 + (cut - 570) * math.sin(a), 456 + 44 * (1 - math.cos(a))))
    pts += [(cut, H), (0, H)]
    m = Image.new("L", (W * S, H * S), 0)
    ImageDraw.Draw(m).polygon([(x * S, y * S) for x, y in pts], fill=255)
    m = m.resize((W, H), Image.LANCZOS)
    a = np.array(im)
    a[..., 3] = (a[..., 3].astype(float) * np.array(m) / 255).astype(np.uint8)
    out = Image.fromarray(a)
    L = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    ImageDraw.Draw(L).line([(x * S, y * S) for x, y in pts[3:]], fill=(0, 0, 0, 255), width=5 * S, joint="curve")
    L = L.resize((W, H), Image.LANCZOS)
    return Image.alpha_composite(out, L)


def officer_base() -> Image.Image:
    im = Image.open(HERE / "ga_a_raw.png").convert("RGBA")
    d = ImageDraw.Draw(im)
    d.ellipse([72, 44, 96, 75], fill=CAP)
    d.line([(74, 51), (84, 56), (96, 61)], fill=PIPE, width=2)
    return im.crop((0, 0, 419, 310))


def up(im: Image.Image) -> Image.Image:
    big = im.resize((im.width * F, im.height * F), Image.LANCZOS)
    rgb = big.convert("RGB").filter(ImageFilter.GaussianBlur(1.3)).filter(ImageFilter.UnsharpMask(2, 50, 2))
    out = rgb.convert("RGBA")
    out.putalpha(big.getchannel("A").filter(ImageFilter.GaussianBlur(1.0)))
    return out


def b_sakin() -> Image.Image:
    return up(officer_base())


def b_sok() -> Image.Image:
    base = b_sakin()
    a = np.array(base)
    # silinecek yüz bölgeleri (büyütülmüş koordinat; kontur dışı kalan çizgiler korunur)
    for (x0, y0, x1, y1) in EREASE:
        reg = a[y0:y1, x0:x1]
        m = reg[..., 3] > 0
        reg[m, :3] = 255
    im = Image.fromarray(a)
    W, H = im.size
    L = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    k = lambda p: (p[0] * SS, p[1] * SS)
    for cx, cy, r in EYES:
        d.ellipse([k((cx - r, cy - r)), k((cx + r, cy + r))], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=5 * SS)
        px = cx - 12
        d.ellipse([k((px - 9, cy - 6)), k((px + 9, cy + 12))], fill=(0, 0, 0, 255))
    for pts in BROWS:
        d.line([k(p) for p in pts], fill=(0, 0, 0, 255), width=7 * SS, joint="curve")
    (mx0, my0, mx1, my1) = MOUTH
    d.ellipse([k((mx0, my0)), k((mx1, my1))], fill=(70, 25, 25, 255), outline=(0, 0, 0, 255), width=5 * SS)
    for pts in FOREHEAD:
        d.line([k(p) for p in pts], fill=BLUE, width=5 * SS, joint="curve")
    kit_varyant.SS = SS
    for x, y, s in DROPS:
        kit_varyant._drop(d, x, y, s)
    L = L.resize((W, H), Image.LANCZOS)
    return Image.alpha_composite(im, L)


EREASE = [(235, 295, 610, 455), (310, 560, 505, 628)]
EYES = [(272, 425, 42), (478, 408, 42)]
BROWS = [[(222, 372), (275, 352), (345, 336)], [(415, 332), (480, 342), (545, 368)]]
MOUTH = (352, 572, 428, 652)
FOREHEAD = [[(250, 300), (270, 293), (290, 305), (312, 298)], [(335, 296), (360, 289), (380, 301), (405, 294)],
            [(430, 298), (455, 291), (475, 303), (500, 296)], [(265, 316), (290, 309), (310, 321), (340, 314)]]
DROPS = [(168, 440, 24), (150, 540, 22), (175, 640, 22)]

if __name__ == "__main__":
    a_sakin().save(HERE / "a_sakin.png")
    b_sakin().save(HERE / "b_sakin.png")
    b_sok().save(HERE / "b_sok.png")
