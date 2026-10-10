"""assets/kit/kurtarmaci_klasik tabanini (sakin.png) kaynaklardan yeniden uretir, sonra varyantlari cikarir.

    python assets/kit/kurtarmaci_klasik/uret.py

Kurtarmaci: klasik 'feels guy' basi (assets/kit/klasik/sakin.png) + wojakland 'Annoyed Construction
Worker' govdesinden mont ve baret; renkler Izmir Sivil Savunma (kanit 1) gibi: kirmizi mont, lacivert
yaka/kol, gumus reflektor, kirmizi baret + beyaz bant."""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path('/home/user/wojak')
AW = ROOT / 'episodes/van-depremi-azra-bebek/chars/kurtarmaci_baretli.png'   # wojakland kaynak
KL = ROOT / 'assets/kit/klasik/sakin.png'
KIT = Path(__file__).resolve().parent
OUT = KIT / 'sakin.png'
P = dict(scale=1 / 0.67, kx=181, ky=64, helmet_dy=-45)

aw_im = Image.open(AW).convert('RGBA')
S = P['scale']
aw_im = aw_im.resize((round(aw_im.width * S), round(aw_im.height * S)), Image.LANCZOS)
aw = np.array(aw_im).astype(np.float32)
H, W = aw.shape[:2]
r, g, b, al = aw[..., 0], aw[..., 1], aw[..., 2], aw[..., 3]
opaque = al > 128
mx = np.maximum(np.maximum(r, g), b)
mn = np.minimum(np.minimum(r, g), b)
sat = (mx - mn) / np.maximum(mx, 1)
dark = (mx < 90) & opaque
white = (mn > 215) & opaque
yellow = (r > 180) & (g > 170) & (b < 140) & opaque
orange = (r > 180) & (g >= 50) & (g < 170) & (b < 110) & opaque & ~yellow   # parlak turuncu yelek/baret
redbrown = (r >= 90) & (r <= 215) & (g < 70) & (b < 60) & opaque & ~dark   # koyu kirmizi-kahve mont/yaka

yy, xx = np.mgrid[0:H, 0:W]
brim_y = 315 * S   # baret alt siniri (kaynak 0.67 olcekte ~305)


def dilate(m, r):
    im = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(r * 2 + 1))
    return np.array(im) > 128


helmet_fill = orange & (yy < brim_y)
helmet = (helmet_fill | (dark & dilate(helmet_fill, 9))) & (yy < brim_y + 12)
helmet = helmet | (dilate(helmet, 1) & ~white & opaque & (yy < brim_y + 12))

jacket_fill = (orange | yellow | redbrown) & (yy > 520 * S)
jacket = jacket_fill | (dark & dilate(jacket_fill, 9) & (yy > 520 * S))
jacket = jacket | (dilate(jacket, 1) & ~white & opaque & (yy > 520 * S))

# --- renk eslemesi -------------------------------------------------------------------------------
out = aw.copy()
lum = 0.299 * r + 0.587 * g + 0.114 * b


def remap(mask, base_src_lum, dst_rgb):
    """mask icindeki pikselleri kaynak parlakligina gore hedef renge (golgeler korunur)."""
    k = np.clip(lum / base_src_lum, 0, 1.25)[mask]
    d = np.array(dst_rgb, np.float32)
    out[..., :3][mask] = np.clip(d[None, :] * k[:, None], 0, 255)


RED = (200, 32, 42)
NAVY = (36, 48, 82)
SILVER = (205, 210, 216)
# yelek turuncusu -> kirmizi (ana turuncu lum ~ 0.299*240+0.587*120+0.114*24 = 145)
remap(orange & jacket, 140, RED)
remap(orange & helmet, 140, RED)
# koyu kirmizi-kahve (yaka, kollar) -> lacivert (lum ~ 0.299*168+0.587*48 = 78)
remap(redbrown & jacket, 78, NAVY)
remap(redbrown & helmet, 78, (150, 22, 32))
# sari reflektor -> gumus (lum ~ 0.299*216+0.587*216+0.114*48 = 197)
remap(yellow & jacket, 200, SILVER)
# yarim tonlu kenar pikselleri (turuncu-siyah karisimi): doygun turuncu-kahve tonlari
mixed = jacket & ~(orange | yellow | redbrown | dark) & (sat > 0.25) & (r > b + 25)
near_navy = dilate(redbrown & jacket, 4) & ~dilate(orange & jacket, 2)
remap(mixed & near_navy, 78, NAVY)
remap(mixed & ~near_navy, 120, RED)
# koyu kirmizimsi cizgiler (yaka dikisi, kenar) -> notr koyu lacivert
dk = jacket & dark & (r > b + 20)
remap(dk, 60, (30, 38, 66))
mixed_h = helmet & ~(orange | redbrown | dark) & (sat > 0.35) & (r > g + 30)
remap(mixed_h, 120, RED)

layer_h = np.zeros_like(out)
layer_h[helmet] = out[helmet]
layer_j = np.zeros_like(out)
layer_j[jacket] = out[jacket]

# --- baret: beyaz bant -----------------------------------------------------------------------------
hel = Image.fromarray(layer_h.astype(np.uint8))
fillmask = np.zeros((H, W), bool)
hm = helmet_fill & (yy < 255 * S)   # kubbe (siperlik haric)
# bant: kubbe icinde, siperlige paralel egri (kaynakta y~185-215)
band_top = (178 + 0.00012 * (xx / S - 500) ** 2) * S
band = hm & (yy > band_top) & (yy < band_top + 26 * S)
ha = np.array(hel).astype(np.float32)
ha[..., :3][band] = (246, 246, 246)
hel = Image.fromarray(ha.astype(np.uint8))
d = ImageDraw.Draw(hel)
# bant kenar cizgileri (ince siyah)
for off in (0, 26):
    pts = []
    for x in range(0, W, 4):
        col = hm[:, x]
        if not col.any():
            continue
        y = (178 + off + 0.00012 * (x / S - 500) ** 2) * S
        if col[int(min(H - 1, y))]:
            pts.append((x, y))
    if len(pts) > 2:
        d.line(pts, fill=(0, 0, 0, 255), width=round(3.2 * S), joint='curve')

# --- kompozit ----------------------------------------------------------------------------------------
kl = Image.open(KL).convert('RGBA')
canvas = Image.new('RGBA', (W, H), (0, 0, 0, 0))
canvas.alpha_composite(kl, (int(P['kx']), int(P['ky'])))
canvas.alpha_composite(Image.fromarray(layer_j.astype(np.uint8)))
canvas.alpha_composite(hel, (0, int(P['helmet_dy'])))
bbox = canvas.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox()
canvas = canvas.crop(bbox)
canvas.save(OUT)
print(OUT.relative_to(ROOT), canvas.size)
sys.path.insert(0, str(ROOT))
from wojak import facing  # noqa: E402
facing.register(OUT, 'right')
import subprocess  # noqa: E402
subprocess.run([sys.executable, str(ROOT / 'tools' / 'kit_varyant.py'), str(OUT), '--kit', KIT.name], check=True)
