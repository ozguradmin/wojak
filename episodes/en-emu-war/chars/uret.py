"""en-emu-war karakterleri (kaynak PNG'lerden yeniden üretir):  python episodes/en-emu-war/chars/uret.py

A (sol, çiftçi): wojakland 'Farmer Boomer' (a_kaynak.png, 421x416; cardiff-giant'ın 'Farmer Wojak'ından farklı karakter), 2.4x LANCZOS + UnsharpMask = a_sakin.png.
  a_sok.png (ters köşe, aynı kutu/silüet): gözler, kaşlar, ağız ve ağızdaki saman silinir; iri yuvarlak göz + küçük göz bebeği (sağa bakar),
  iç ucu kalkık kalın kaş, "O" ağız, alında mavi çizgiler, başın önünde kontur dışında 3 ter damlası. Şapka, giysi aynı.
B (sağ, şüpheci): wojakland '1930s Top Hat Wojak' (b_kaynak.png, 352x405), 2x LANCZOS + UnsharpMask; b_sakin.png.
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
F = 2.4
FACE = (247, 249, 247)


def sakin() -> Image.Image:
    im = Image.open(HERE / "a_kaynak.png").convert("RGBA")
    big = im.resize((round(im.width * F), round(im.height * F)), Image.LANCZOS)
    rgb = big.convert("RGB").filter(ImageFilter.UnsharpMask(2, 70, 2))
    out = rgb.convert("RGBA")
    al = np.array(big.getchannel("A"))
    from scipy import ndimage as ndi
    al = ndi.grey_erosion(al, size=3)            # şapka kenarındaki beyaz hale
    out.putalpha(Image.fromarray(al).filter(ImageFilter.GaussianBlur(0.6)))
    a = np.array(out).astype(np.float32)
    mavi = (a[..., 2] > a[..., 0] + 60) & (a[..., 3] > 0)          # tulum mavisini ~%30 desatüre et
    gri = a[..., :3].mean(axis=2, keepdims=True)
    a[mavi, :3] = (gri + (a[..., :3] - gri) * 0.70)[mavi]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def sok() -> Image.Image:
    from scipy import ndimage as ndi
    im = sakin()
    a = np.array(im)
    # silinecek bölgeler (iki göz, kaşlar, ağız çizgisi)
    for (x0, y0, x1, y1) in [(268, 385, 386, 455), (455, 368, 585, 452), (268, 335, 615, 395), (300, 522, 505, 578)]:
        reg = a[y0:y1, x0:x1]
        solid = reg[..., 3] > 200
        reg[solid, :3] = FACE
    # ağızdaki saman: yüz içinde beyaz, dışında şeffaf
    reg = a[500:760, 0:360]
    r, g, b = reg[..., 0].astype(int), reg[..., 1].astype(int), reg[..., 2].astype(int)
    straw = ndi.binary_dilation((g > 150) & (b < 150) & (r - b > 60), iterations=4)
    xs = np.arange(0, 360)[None, :].repeat(reg.shape[0], 0)
    dark = reg[..., :3].sum(axis=2) < 250
    reg[straw & (xs >= 300) & ~dark, :3] = FACE
    reg[straw & (xs < 300) & ~dark, 3] = 0
    a[640:745, 0:230, 3] = 0
    reg = a[500:745, 0:340]
    rr, gg, bb = reg[..., 0].astype(int), reg[..., 1].astype(int), reg[..., 2].astype(int)
    kal = (rr - bb > 10)       # saman ucu artıkları (dış kenar)
    reg[kal, 3] = 0
    im = Image.fromarray(a)
    W, H = im.size
    # saman silinince çene konturunda kalan oyuk: yüz rengiyle doldur, kontur çizgisini sürekli çiz
    fix = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fix)
    kk = lambda p: (p[0] * SS, p[1] * SS)
    fd.polygon([kk(p) for p in [(260, 538), (301, 538), (301, 584), (286, 573), (262, 558)]], fill=FACE + (255,))
    fd.line([kk(p) for p in [(255, 551), (262, 558), (274, 565), (287, 573)]], fill=(30, 28, 27, 255), width=8 * SS, joint="curve")
    fd.rectangle([kk((298, 570)), kk((330, 584))], fill=FACE + (255,))
    im = Image.alpha_composite(im, fix.resize((W, H), Image.LANCZOS))
    L = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    k = lambda p: (p[0] * SS, p[1] * SS)
    for cx, cy, r_ in [(308, 420, 40), (518, 410, 44)]:
        d.ellipse([k((cx - r_, cy - r_)), k((cx + r_, cy + r_))], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=7 * SS)
        px = cx - 12   # dosya SOLA bakar; motor aynalar
        d.ellipse([k((px - 9, cy - 7)), k((px + 9, cy + 11))], fill=(0, 0, 0, 255))
    d.line([k((262, 366)), k((310, 350)), k((362, 328))], fill=(0, 0, 0, 255), width=10 * SS, joint="curve")
    d.line([k((468, 326)), k((525, 342)), k((582, 370))], fill=(0, 0, 0, 255), width=10 * SS, joint="curve")
    d.ellipse([k((352, 524)), k((402, 590))], fill=(70, 25, 25, 255), outline=(0, 0, 0, 255), width=7 * SS)
    for pts in [[(320, 268), (350, 260), (380, 272), (412, 264)], [(430, 262), (460, 254), (490, 266), (522, 258)],
                [(350, 300), (380, 292), (410, 304), (445, 296)], [(470, 296), (500, 288), (530, 300), (560, 292)],
                [(395, 238), (425, 230), (455, 242), (488, 234)]]:
        d.line([k(p) for p in pts], fill=BLUE, width=7 * SS, joint="curve")
    kit_varyant.SS = SS
    for x, y, s_ in [(175, 430, 22), (150, 520, 20), (178, 610, 20)]:
        kit_varyant._drop(d, x, y, s_)
    L = L.resize((W, H), Image.LANCZOS)
    return Image.alpha_composite(im, L)


def b() -> Image.Image:
    im = Image.open(HERE / "b_kaynak.png").convert("RGBA")
    f = 2.0
    im = im.resize((int(im.width * f), int(im.height * f)), Image.LANCZOS)
    rgb = im.convert("RGB").filter(ImageFilter.UnsharpMask(3, 90, 2))
    out = rgb.convert("RGBA")
    out.putalpha(im.getchannel("A"))
    return out


if __name__ == "__main__":
    sakin().save(HERE / "a_sakin.png")
    sok().save(HERE / "a_sok.png")
    b().save(HERE / "b_sakin.png")
