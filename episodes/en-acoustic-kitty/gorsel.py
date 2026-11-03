"""en-acoustic-kitty görsel hazırlığı: img/ içindeki ham dosyalardan bg.jpg, kanit_1.jpg, kanit_2.jpg üretir."""
from pathlib import Path
import numpy as np
from PIL import Image, ImageEnhance, ImageOps

H = Path(__file__).resolve().parent / "img"

# arka plan: 1965 Washington havadan (CC BY-SA 2.0), kare kırpım, hafif doygunluk/parlaklık düzeltme
im = Image.open(H / "arka_dc_renkli.jpg").convert("RGB")
w, h = im.size
x0 = 40
im = im.crop((x0, 0, x0 + h, h)).resize((1080, 1080), Image.LANCZOS)
im = ImageEnhance.Color(im).enhance(0.55)
im = ImageEnhance.Brightness(im).enhance(1.08)
im.save(H / "bg.jpg", quality=93)
a = np.asarray(im.convert("HSV")).astype(float)
print("bg parlaklik", a[..., 2].mean() * 100 / 255 * 1.0, "doygunluk", a[..., 1].mean() / 255)

# kanıt 1 ve 2: CIA notu, NSA PDF'indeki 2056x2654 / 2032x2640 tarama (pdfimages ile çıkarıldı), 1080 genişlik
def sayfa(png, y0, y1, x1=1625):
    d = Image.open(png).convert("L")
    d = d.crop((230, y0, x1, y1))
    d = d.resize((1080, round(d.height * 1080 / d.width)), Image.LANCZOS)
    return ImageOps.autocontrast(d, cutoff=0.5).convert("RGB")

SRC = H
sayfa(SRC / "cia_memo_s1_ham.png", 750, 1640).save(H / "kanit_1.jpg", quality=95)   # s.1: SUBJECT ... prevail
sayfa(SRC / "cia_memo_s2_ham.png", 395, 1130, 1700).save(H / "kanit_2.jpg", quality=95)   # s.2: "would not be practical"
