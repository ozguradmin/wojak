"""Görselleri hazırlar: python episodes/en-franz-ferdinand-wrong-turn/gorsel.py
arka.jpg  : Latin Bridge 02 (sundeviljeff, CC BY 2.0) kare kırpım, renk 0,62; sonbahar ağacı yeşile boyandı (Haziran), parlaklık 0,93
ev_1.jpg  : Tausch 1914 (PD) 1080 genişlik, autocontrast
ev_2.jpg  : NYT 29 Haz 1914 (PD) başlık + portreler, 1080x816 (1:1)
"""
from pathlib import Path
from PIL import Image, ImageEnhance, ImageOps
H = Path(__file__).resolve().parent / "img"
a = Image.open(H / "arka_aday1.jpg").convert("RGB")
import numpy as np
hsv = np.array(a.convert("HSV")).astype(float)
yy, xx = np.mgrid[0:hsv.shape[0], 0:hsv.shape[1]]
box = (xx > 705) & (xx < 1100) & (yy < 460)
hue = hsv[..., 0] * 360 / 255
m = box & (hue > 18) & (hue < 62) & (hsv[..., 1] > 70)
hsv[..., 0][m] = 85 * 255 / 360
hsv[..., 1][m] *= 0.55
hsv[..., 2][m] *= 0.85
a = Image.fromarray(hsv.astype("uint8"), "HSV").convert("RGB")
a = a.crop((112, 0, 112 + 894, 894)).resize((1080, 1080), Image.LANCZOS)
a = ImageEnhance.Brightness(ImageEnhance.Color(a).enhance(0.62)).enhance(0.93)
a.save(H / "arka.jpg", quality=93)
e = Image.open(H / "kanit_a.jpg").convert("RGB")
e = e.resize((1080, round(e.height * 1080 / e.width)), Image.LANCZOS)
e = ImageOps.autocontrast(e, cutoff=1)
e.save(H / "ev_1.jpg", quality=93)
c = Image.open(H / "kanit_c_1920.jpg").convert("RGB")
c.crop((790, 225, 1870, 1041)).save(H / "ev_2.jpg", quality=93)
