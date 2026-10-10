"""Suvla fotoğrafına ovaya oturmuş alçak bulut katmanı ekler (C2kk S2 duman katmanı gibi; STIL §6 ek katman).

    python sis_katmani.py <src.jpg> <out.jpg> [--mode fog|loaf] [--seed N] [--col N]

v5: arkaplan.py bu betiği renk düzeltilmiş fotoğrafla çağırır (--mode fog --seed 11 --col 222 --alpha <png>),
sonra kare kırpar (820, 644, 2120, 1944) ve tabur siluetlerini ekler. Alt kenar artık dalgalı (bot gürültülü,
sönme 160 px); üst kenar v4 ile aynı.

Koordinatlar kaynak görselin pikselleridir (2592x1944).
"""
import sys
import numpy as np
from PIL import Image, ImageFilter

src, out = sys.argv[1], sys.argv[2]
mode = "fog"
seed = 7
for i, a in enumerate(sys.argv):
    if a == "--mode":
        mode = sys.argv[i + 1]
    if a == "--seed":
        seed = int(sys.argv[i + 1])

im = Image.open(src).convert("RGB")
W, H = im.size
rng = np.random.default_rng(seed)


def octave_noise(w, h, grids=((6, 5), (12, 9), (24, 18), (48, 36), (96, 72)), weights=(1, .55, .3, .16, .08)):
    acc = np.zeros((h, w), np.float32)
    for (gx, gy), wt in zip(grids, weights):
        g = rng.standard_normal((gy, gx)).astype(np.float32)
        gi = Image.fromarray(g).resize((w, h), Image.BICUBIC)
        acc += wt * np.asarray(gi, np.float32)
    acc -= acc.min()
    acc /= acc.max()
    return acc


def smooth(t):
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


X, Y = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
n = octave_noise(W, H)
n2 = octave_noise(W, H, grids=((10, 8), (20, 15), (40, 30), (80, 60), (160, 120)), weights=(1, .6, .35, .2, .1))

if mode == "fog":
    # üst kenar: dalgalı, x'e göre hafif eğimli (ova uzaklaştıkça yukarı)
    xs = np.arange(W, dtype=np.float32)
    top_noise = octave_noise(W, 1, grids=((7, 1), (15, 1), (31, 1)), weights=(1, .5, .25))[0]
    top = 935 + 90 * (top_noise - 0.5) + (xs - 1400) * 0.02
    # üst kenar biraz daha belirgin ve kabarık (bulut tepesi), alt kenar tepelerin içine yavaşça söner
    billow = octave_noise(W, H, grids=((30, 8), (60, 16), (120, 32)), weights=(1, .5, .25))
    # v5: alt kenar düz cetvel çizgisi değil, dalgalı (gürültü billow'dan SONRA üretilir: üst kenar v4 ile aynı kalır)
    bot = 1330 + 110 * (octave_noise(W, 1, grids=((9, 1), (19, 1), (41, 1)), weights=(1, .5, .25))[0][None, :] - 0.5)
    edge = top[None, :] - 45 * (billow - 0.5)
    v = smooth((Y - edge) / 38.0) * (1 - smooth((Y - bot) / 160.0))
    # yatay: merkez yoğun, en sağ ve en sol (deniz) daha seyrek
    hcx = smooth((X - 300) / 500.0) * (1 - smooth((X - 2300) / 400.0))
    a = v * hcx * (0.55 + 0.6 * n)
    a = np.clip(a, 0, 0.92)
elif mode == "loaf":
    # tek, yoğun, "somun" biçimli bulut: düz taban, kabarık üst (1965 ifadesi)
    cx, base_y, half_w, height = 1450, 1180, 700, 260
    dx = (X - cx) / half_w
    prof = np.sqrt(np.clip(1 - dx ** 2, 0, 1)) ** 0.6
    bump = octave_noise(W, 1, grids=((9, 1), (19, 1), (41, 1)), weights=(1, .5, .3))[0]
    topy = base_y - height * prof * (0.75 + 0.5 * bump[None, :])
    inside = smooth((Y - topy) / 35.0) * (1 - smooth((Y - base_y) / 90.0))
    a = inside * (0.75 + 0.35 * n2)
    a = np.clip(a, 0, 0.95)

a_img = Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6))
a = np.asarray(a_img, np.float32) / 255.0

# renk: güneşli tarafta sıcak beyaz, gölgede mavimsi gri; dokuyla gölgelendir
shade = 0.86 + 0.14 * n2
FC = float(next((sys.argv[i + 1] for i, a in enumerate(sys.argv) if a == "--col"), 236))
col = np.stack([FC * shade, FC * shade, (FC + 4) * shade], -1)
base = np.asarray(im, np.float32)
outa = base * (1 - a[..., None]) + col * a[..., None]
Image.fromarray(np.clip(outa, 0, 255).astype(np.uint8)).save(out, quality=93)
if "--alpha" in sys.argv:  # v5: katmanın alfasını ayrıca kaydet (tabur siluetleri bulutun içinde sönsün)
    Image.fromarray((a * 255).astype(np.uint8)).save(sys.argv[sys.argv.index("--alpha") + 1])
print(out, mode, "max alpha", float(a.max()))
