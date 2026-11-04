"""en-boston-molasses-flood karakterleri (kaynak PNG'lerden yeniden üretir): python episodes/en-boston-molasses-flood/chars/uret.py

A (sol, işçi): wojakland 'Worker 2 Wojak' (a_kaynak.png, 1153x1177), gri kasket + tulum; sakin yüz değiştirilmedi. a_sakin.png = göğüsten kesilmiş.
B (sağ, yönetici): wojakland '1950s Businessman Wojak' (b_kaynak.png, 1243x1400): fötr şapka + ceket (1919 için makul). Sırıtma silinip düz ağız
  çizilir (b_sakin.png; "firma" karakterinde kötü yüz yok). b_sok.png (ters köşe, aynı silüet): gözler/kaşlar silinir; iri yuvarlak göz + küçük göz bebeği,
  iç ucu kalkık kalın kaş, "O" ağız, alında mavi çizgiler, başın önünde kontur dışında 3 ter damlası.
Dosyalar sağa bakar (burun/göz bebeği); motor aynalar.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
SS = 4
FACE = (255, 255, 255)
BLUE = (60, 120, 200, 255)
INK = (0, 0, 0, 255)


def a_sakin() -> Image.Image:
    im = Image.open(HERE / "a_kaynak.png").convert("RGBA")
    return im.crop((0, 0, im.width, 960))


def b_base() -> Image.Image:
    im = Image.open(HERE / "b_kaynak.png").convert("RGBA")
    return im.crop((0, 0, im.width, 1010))


def erase(a: np.ndarray, boxes) -> None:
    for (x0, y0, x1, y1) in boxes:
        reg = a[y0:y1, x0:x1]
        solid = reg[..., 3] > 200
        reg[solid, :3] = FACE


def b_sakin() -> Image.Image:
    a = np.array(b_base())
    erase(a, [(625, 735, 915, 797), (715, 797, 915, 850)])
    im = Image.fromarray(a)
    W, H = im.size
    L = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    k = lambda p: (p[0] * SS, p[1] * SS)
    d.line([k((690, 792)), k((780, 800)), k((880, 790))], fill=INK, width=11 * SS, joint="curve")
    return Image.alpha_composite(im, L.resize((W, H), Image.LANCZOS))


def b_sok() -> Image.Image:
    a = np.array(b_base())
    erase(a, [(625, 735, 915, 797), (715, 797, 915, 850), (600, 430, 790, 600), (850, 430, 990, 600)])
    im = Image.fromarray(a)
    W, H = im.size
    L = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    k = lambda p: (p[0] * SS, p[1] * SS)
    for cx, cy, r in [(698, 548, 46), (925, 556, 44)]:
        d.ellipse([k((cx - r, cy - r)), k((cx + r, cy + r))], fill=(255, 255, 255, 255), outline=INK, width=7 * SS)
        px = cx + 14
        d.ellipse([k((px - 10, cy - 8)), k((px + 10, cy + 12))], fill=INK)
    d.line([k((625, 492)), k((705, 468)), k((775, 448))], fill=INK, width=12 * SS, joint="curve")
    d.line([k((860, 448)), k((920, 468)), k((985, 492))], fill=INK, width=12 * SS, joint="curve")
    # "O" ağız
    d.ellipse([k((735, 745)), k((815, 835))], fill=(255, 255, 255, 255), outline=INK, width=8 * SS)
    # alında mavi çizgiler (şapka kenarı altı)
    for x0, y0, x1, y1 in [(650, 432, 642, 462), (700, 430, 710, 456), (792, 430, 784, 452), (850, 430, 862, 454), (915, 432, 908, 464)]:
        d.line([k((x0, y0)), k((x1, y1))], fill=BLUE, width=10 * SS, joint="curve")
    face = Image.alpha_composite(im, L.resize((W, H), Image.LANCZOS))
    # ter damlaları: başın önünde (sağ), kontur dışında
    big = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    dd = ImageDraw.Draw(big)
    for cx, cy in [(1052, 560), (1075, 650), (1040, 735)]:
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
