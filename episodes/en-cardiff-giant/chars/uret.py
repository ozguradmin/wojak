"""en-cardiff-giant karakterleri (kaynak PNG'lerden yeniden üretir):  python episodes/en-cardiff-giant/chars/uret.py

A (sol, meraklı ziyaretçi): wojakland 'Farmer Wojak' (a_kaynak.png); a_sakin.png = kaynak, hasır (saman) silindi.
  a_sok.png (ters köşe, aynı kutu): gözler/kaşlar/ağız silinip iri yuvarlak göz + küçük göz bebeği (sağa bakar), iç ucu kalkık kalın kaş,
  "O" ağız, alında 5 düzensiz mavi çizgi, başın önünde kontur dışında 3 ter damlası. Silüet, şapka, giysi aynı.
B (sağ, şüpheci): wojakland 'Top Hat British Chad 1' (b_kaynak.png; 1860'lar silindir + redingot), 1.6x LANCZOS + UnsharpMask; b_sakin.png.
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


def _erase_straw(a):
    from scipy import ndimage
    r, g, b, al = a[..., 0].astype(int), a[..., 1].astype(int), a[..., 2].astype(int), a[..., 3]
    m = (al > 0) & (r > 150) & (g > 110) & (b < 150) & (r - b > 35)
    m[:600, :] = False
    m[:, :560] = False
    m = ndimage.binary_dilation(m, iterations=3)
    m[:640, :] = False
    m[775:, :] = False
    out = m.copy(); out[:, :677] = False
    a[m, :3] = 255
    a[out, 3] = 0
    return a


def _patch_contour(im: Image.Image) -> Image.Image:
    """Saman sapının kestiği yanak konturunu (x~672, y 660-698) yeniden çizer."""
    L = Image.new("RGBA", (im.width * SS, im.height * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    pts = [(672, 662), (673, 680), (670, 693), (663, 705), (654, 717)]
    d.line([(x * SS, y * SS) for x, y in pts], fill=(38, 48, 48, 255), width=8 * SS, joint="curve")
    L = L.resize(im.size, Image.LANCZOS)
    return Image.alpha_composite(im, L)


def _extend_brim(im: Image.Image) -> Image.Image:
    """Şapka siperi kaynak PNG'nin sağ kenarında (x=856) düz kesikti: tuvali 140 px genişletip siperi sivri uçla kapatır."""
    pad = 140
    W, H = im.size
    big = Image.new("RGBA", (W + pad, H), (0, 0, 0, 0))
    big.paste(im, (0, 0))
    L = Image.new("RGBA", (big.width * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    k = lambda p: (p[0] * SS, p[1] * SS)
    tip = (W + 118, 222)
    d.polygon([k((W - 6, 207)), k(tip), k((W - 6, 268))], fill=(104, 99, 72, 255))
    d.line([k((W - 8, 208)), k(tip), k((W - 8, 267))], fill=(42, 46, 44, 255), width=5 * SS, joint="curve")
    L = L.resize(big.size, Image.LANCZOS)
    return Image.alpha_composite(big, L)


def sakin() -> Image.Image:
    a = np.array(Image.open(HERE / "a_kaynak.png").convert("RGBA"))
    a = _erase_straw(a)
    return _extend_brim(_patch_contour(Image.fromarray(a)))


def sok() -> Image.Image:
    a = np.array(Image.open(HERE / "a_kaynak.png").convert("RGBA"))
    a = _erase_straw(a)
    for (x0, y0, x1, y1) in [(330, 262, 690, 480), (455, 645, 600, 692)]:
        reg = a[y0:y1, x0:x1]
        m = reg[..., 3] > 0
        reg[m, :3] = 255
    im = _patch_contour(Image.fromarray(a))
    W, H = im.size
    L = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    k = lambda p: (p[0] * SS, p[1] * SS)
    for cx, cy, r in [(440, 405, 52), (640, 420, 46)]:
        d.ellipse([k((cx - r, cy - r)), k((cx + r, cy + r))], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=8 * SS)
        px = cx + 12
        d.ellipse([k((px - 10, cy - 8)), k((px + 10, cy + 12))], fill=(0, 0, 0, 255))
    d.line([k((345, 335)), k((400, 305)), k((470, 290))], fill=(0, 0, 0, 255), width=11 * SS, joint="curve")
    d.line([k((600, 290)), k((665, 300)), k((700, 330))], fill=(0, 0, 0, 255), width=11 * SS, joint="curve")
    d.ellipse([k((518, 640)), k((588, 722))], fill=(70, 25, 25, 255), outline=(0, 0, 0, 255), width=8 * SS)
    for pts in [[(385, 270), (410, 263), (430, 277), (455, 270)], [(470, 266), (505, 258), (530, 274), (570, 266)],
                [(590, 272), (615, 265), (635, 279), (660, 272)], [(400, 284), (430, 278), (450, 292), (480, 286)],
                [(520, 284), (550, 278), (570, 292), (600, 286)]]:
        d.line([k(p) for p in pts], fill=BLUE, width=6 * SS, joint="curve")
    kit_varyant.SS = SS
    for x, y, s in [(776, 400, 24), (800, 505, 22), (770, 610, 22)]:
        kit_varyant._drop(d, x, y, s)
    L = L.resize((W, H), Image.LANCZOS)
    return _extend_brim(Image.alpha_composite(im, L))


def b() -> Image.Image:
    """Silindirin üst kısmı kesilir (yüz büyüsün) ve düz üst kapak yeniden çizilir; 1.6x LANCZOS + UnsharpMask."""
    im = Image.open(HERE / "b_kaynak.png").convert("RGBA")
    CUT = 88
    im = im.crop((0, CUT, im.width, im.height))
    f = 1.6
    im = im.resize((int(im.width * f), int(im.height * f)), Image.LANCZOS)
    rgb = im.convert("RGB").filter(ImageFilter.UnsharpMask(2, 60, 2))
    out = rgb.convert("RGBA")
    out.putalpha(im.getchannel("A"))
    padded = Image.new("RGBA", (out.width, out.height + 10), (0, 0, 0, 0))
    padded.paste(out, (0, 10))
    out = padded
    L = Image.new("RGBA", (out.width * SS, out.height * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    x0, x1 = 134 * f, 372 * f
    ry = 16 * f
    d.ellipse([(x0 - 1) * SS, 2 * SS, (x1 + 1) * SS, (2 + 2 * ry) * SS], fill=(44, 11, 11, 255), outline=(8, 4, 4, 255), width=int(3 * f * SS))
    L = L.resize(out.size, Image.LANCZOS)
    return Image.alpha_composite(out, L)


if __name__ == "__main__":
    sakin().save(HERE / "a_sakin.png")
    sok().save(HERE / "a_sok.png")
    b().save(HERE / "b_sakin.png")
