"""en-cadaver-synod karakterleri (kaynak PNG'lerden yeniden üretir): python episodes/en-cadaver-synod/chars/uret.py

A (sol, katip/keşiş): wojakland 'Sad Monk Wojak' (a_kaynak.png, 401x465), 2x LANCZOS + UnsharpMask. a_sakin.png.
B (sağ, papa): HF clayshoaf/Wojaks '5_Doomer/13995' 'Pope Pius' (b_kaynak.png, 1493x1400): beyaz takke + cüppe. Ağızdaki sigara + duman silinir,
  çene konturu kapatılır (b_sakin.png). b_sok.png (ters köşe, aynı silüet): gözlük camlarının içi silinir; iri yuvarlak göz + küçük göz bebeği,
  iç ucu kalkık kalın kaş, "O" ağız, alında mavi çizgiler, başın önünde kontur dışında 3 ter damlası.
Dosyalar sağa bakar (burun/göz bebeği); motor aynalar.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
SS = 4
SKIN = (247, 240, 212, 255)
BLUE = (60, 120, 200, 255)
INK = (0, 0, 0, 255)
CROP_H = 1180


def a_sakin() -> Image.Image:
    im = Image.open(HERE / "a_kaynak.png").convert("RGBA")
    im = im.resize((im.width * 2, im.height * 2), Image.LANCZOS)
    rgb = im.convert("RGB").filter(ImageFilter.UnsharpMask(2, 60, 2))
    out = rgb.convert("RGBA")
    out.putalpha(im.getchannel("A"))
    return out


def b_base() -> Image.Image:
    im = Image.open(HERE / "b_kaynak.png").convert("RGBA")
    W, H = im.size
    L = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    k = lambda p: (p[0] * SS, p[1] * SS)
    # sigara gövdesi (yüz içi kısım): ten rengi
    d.polygon([k(p) for p in [(948, 698), (1000, 700), (1052, 764), (1040, 802), (1030, 808), (958, 724)]], fill=SKIN)
    base = Image.alpha_composite(im.resize((W * SS, H * SS), Image.NEAREST), L)
    # sigara dış kısmı + duman: saydam
    a = np.array(base)
    clear = Image.new("L", base.size, 0)
    cd = ImageDraw.Draw(clear)
    cd.polygon([k(p) for p in [(1053, 762), (1170, 740), (1170, 840), (1030, 840), (1034, 808), (1044, 790)]], fill=255)
    a[np.array(clear) > 0] = (0, 0, 0, 0)
    base = Image.fromarray(a)
    # çene konturu köprüsü + ağız çizgisi devamı
    L2 = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d2 = ImageDraw.Draw(L2)
    d2.line([k((1052, 760)), k((1043, 784)), k((1033, 806))], fill=INK, width=11 * SS, joint="curve")
    d2.line([k((950, 706)), k((985, 711)), k((1005, 706))], fill=INK, width=11 * SS, joint="curve")
    base = Image.alpha_composite(base, L2)
    base = base.resize((W, H), Image.LANCZOS)
    a = np.array(base)
    yy, xx = np.mgrid[0:H, 0:W]
    dark = (a[..., 3] > 60) & (a[..., :3].sum(2) < 330)
    # gözlük çerçeveleri (iki halka, kulak çubukları, köprü) silinir; gözler kalır
    from scipy import ndimage
    r1 = np.hypot(xx - 797, yy - 423)
    r2 = np.hypot(xx - 1042, yy - 437)
    arms = ((xx > 556) & (xx < 735) & (yy > 372) & (yy < 418)) | ((xx > 868) & (xx < 988) & (yy > 392) & (yy < 432)) | ((xx > 1098) & (xx < 1132) & (yy > 404) & (yy < 426))
    d2 = dark & ~arms
    lab, _ = ndimage.label(d2)
    keep = {lab[423, 800], lab[437, 1062], lab[423, 790], lab[437, 1030]} - {0}
    eye = np.isin(lab, list(keep))
    ring = ((r1 < 92) | (r2 < 80)) & d2 & ~eye
    zone = ((r1 < 95) | (r2 < 85)) & ~dark & (a[..., 3] > 0)
    a[zone, :3] = (255, 255, 255)
    m = arms | ring
    a[m, :3] = (255, 255, 255)
    a[m & (a[..., 3] > 0), 3] = 255
    # krem ten rengi -> düz beyaz (A ile aynı çizim ailesi)
    near = (np.abs(a[..., :3].astype(int) - np.array(SKIN[:3])).sum(2) < 40) & (a[..., 3] > 0)
    a[near, :3] = (255, 255, 255)
    base = Image.fromarray(a)
    return base.crop((0, 0, W, CROP_H))


def b_sakin() -> Image.Image:
    return b_base()


def b_sok() -> Image.Image:
    im = b_base()
    a = np.array(im)
    # gözlük camı içi (gözler/kaşlar) temizle: iki mercek içi
    W, H = im.size
    yy, xx = np.mgrid[0:H, 0:W]
    for cx, cy, r in [(798, 423, 64), (1043, 435, 64)]:
        m = (xx - cx) ** 2 + (yy - cy) ** 2 < r ** 2
        solid = a[..., 3] > 200
        a[m & solid, :3] = (255, 255, 255)
    # ağız çizgisi sil (ten rengi), "O" ağız çizilecek
    reg = a[690:722, 830:1010]
    reg[reg[..., 3] > 200, :3] = (255, 255, 255)
    im = Image.fromarray(a)
    L = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    k = lambda p: (p[0] * SS, p[1] * SS)
    for cx, cy, r in [(798, 423, 58), (1043, 435, 58)]:
        d.ellipse([k((cx - r, cy - r)), k((cx + r, cy + r))], fill=(255, 255, 255, 255), outline=INK, width=6 * SS)
        px = cx + 14
        d.ellipse([k((px - 11, cy - 9)), k((px + 11, cy + 13))], fill=INK)
    d.line([k((700, 330)), k((775, 322)), k((850, 308))], fill=INK, width=17 * SS, joint="curve")
    d.line([k((1000, 308)), k((1062, 322)), k((1135, 338))], fill=INK, width=17 * SS, joint="curve")
    d.ellipse([k((878, 676)), k((968, 784))], fill=(255, 255, 255, 255), outline=INK, width=8 * SS)
    for x0, y0, x1, y1 in [(640, 262, 634, 296), (720, 268, 730, 298), (850, 264, 842, 292), (960, 266, 970, 294), (1060, 270, 1052, 300)]:
        d.line([k((x0, y0)), k((x1, y1))], fill=BLUE, width=10 * SS, joint="curve")
    face = Image.alpha_composite(im, L.resize((W, H), Image.LANCZOS))
    big = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    dd = ImageDraw.Draw(big)
    for cx, cy in [(1215, 430), (1235, 540), (1205, 640)]:
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
