"""en-titan-ii-socket karakterleri (kaynak PNG'lerden yeniden üretir): python episodes/en-titan-ii-socket/chars/uret.py

A (sol, bakım teknisyeni): wojakland 'Worker 2 Wojak' (a_kaynak.png, 1153x1177), olduğu gibi (a_sakin.png).
B (sağ, çavuş): HF clayshoaf/Wojaks '5_Boomer/9691' 'Boomer Drill Sergeant' (b_kaynak.png, 402x522): 3x LANCZOS + UnsharpMask (b_sakin.png).
  b_sok.png (ters köşe, aynı silüet): gözler ve ağız silinir; iri yuvarlak göz + küçük göz bebeği, iç ucu kalkık kalın kaş,
  "O" ağız, alında mavi çizgiler, başın önünde kontur dışında 3 ter damlası.
Dosyalar sağa bakar (burun/göz bebeği); motor aynalar.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
SS = 4
BLUE = (60, 120, 200, 255)
INK = (0, 0, 0, 255)
UP = 3
CROP_H = 1400   # göğüs hizasından kes: yüz büyür


def a_sakin() -> Image.Image:
    return Image.open(HERE / "a_kaynak.png").convert("RGBA")


def b_sakin() -> Image.Image:
    im = Image.open(HERE / "b_kaynak.png").convert("RGBA")
    im = im.resize((im.width * UP, im.height * UP), Image.LANCZOS)
    rgb = im.convert("RGB").filter(ImageFilter.UnsharpMask(2, 60, 2))
    out = rgb.convert("RGBA")
    out.putalpha(im.getchannel("A"))
    return out.crop((0, 0, out.width, CROP_H))


def b_sok() -> Image.Image:
    im = b_sakin()
    W, H = im.size
    a = np.array(im)
    k = lambda p: (p[0] * SS, p[1] * SS)
    # gözler + ağız çizgisi: yüz içi koyu çizgileri sil (burun hattı ve yüz konturu kalır)
    for (x0, y0, x1, y1) in [(215, 575, 262, 665), (490, 575, 650, 665), (250, 738, 585, 818), (225, 515, 690, 570)]:
        reg = a[y0:y1, x0:x1]
        reg[(reg[..., 3] > 0) & (reg[..., :3].sum(2) < 745), :3] = (255, 255, 255)
    im = Image.fromarray(a)
    L = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    for cx, cy, r in [(230, 618, 58), (548, 618, 58)]:
        d.ellipse([k((cx - r, cy - r)), k((cx + r, cy + r))], fill=(255, 255, 255, 255), outline=INK, width=6 * SS)
        px = cx - 12
        d.ellipse([k((px - 11, cy - 9)), k((px + 11, cy + 13))], fill=INK)
    d.line([k((165, 540)), k((230, 520)), k((300, 500))], fill=INK, width=15 * SS, joint="curve")
    d.line([k((490, 500)), k((560, 520)), k((635, 545))], fill=INK, width=15 * SS, joint="curve")
    d.ellipse([k((335, 715)), k((415, 805))], fill=(255, 255, 255, 255), outline=INK, width=8 * SS)
    for x0, y0, x1, y1 in [(250, 440, 246, 470), (330, 436, 336, 466), (410, 436, 404, 466), (480, 440, 486, 470)]:
        d.line([k((x0, y0)), k((x1, y1))], fill=BLUE, width=9 * SS, joint="curve")
    face = Image.alpha_composite(im, L.resize((W, H), Image.LANCZOS))
    big = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    dd = ImageDraw.Draw(big)
    for cx, cy in [(740, 560), (760, 660), (730, 760)]:
        x, y = cx * SS, cy * SS
        r = 17 * SS
        dd.polygon([(x, y - 34 * SS), (x - r, y + 4 * SS), (x + r, y + 4 * SS)], fill=BLUE)
        dd.ellipse([x - r, y - 12 * SS, x + r, y + 22 * SS], fill=BLUE)
    return Image.alpha_composite(face, big.resize((W, H), Image.LANCZOS))


if __name__ == "__main__":
    a_sakin().save(HERE / "a_sakin.png")
    b_sakin().save(HERE / "b_sakin.png")
    b_sok().save(HERE / "b_sok.png")
    print("ok")
