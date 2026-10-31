"""en-apollo-moon-disaster görselleri: python episodes/en-apollo-moon-disaster/gorsel.py
Kaynaklar (ham indirilenler img/ altında): NASA GPN-2000-000630 (arka plan), NARA Safire notu s.1-2 (kanıt)."""
from pathlib import Path
from PIL import Image, ImageEnhance, ImageOps
import numpy as np

H = Path(__file__).resolve().parent / "img"

# Arka plan: kare kırpım, renk 0,55, parlaklık 1,0
bg = Image.open(H / "arka-plan-apollo11-launch-1969.jpg").convert("RGB")
bg = bg.crop((0, 130, 1920, 2050)).resize((1080, 1080), Image.LANCZOS)
bg = ImageEnhance.Color(bg).enhance(0.42)
bg = ImageEnhance.Brightness(bg).enhance(1.15)
bg.save(H / "bg.jpg", quality=93)
hsv = np.array(bg.convert("HSV")).astype(float)
print("bg parlaklık %.0f doygunluk %.2f" % (np.array(bg.convert("L")).mean(), hsv[..., 1].mean() / 255))


def crop_w(src, box, out, hh=None):
    im = Image.open(H / src).convert("RGB").crop(box)
    s = 1080 / im.width
    im = im.resize((1080, round(im.height * s)), Image.LANCZOS)
    im = ImageOps.autocontrast(im, cutoff=0.1)
    im.save(H / out, quality=95)
    print(out, im.size, "ölçek %.2f" % s)


# Kanıt 1: Aldrin Ay'da (NASA AS11-40-5903), figür bütün, 1080x816
im = Image.open(H / "kanit-3-aldrin-apollo11-as11-40-5903.jpg").convert("RGB").crop((258, 40, 1758, 1174)).resize((1080, 816), Image.LANCZOS)
im.save(H / "kanit_1.jpg", quality=95)
print("kanit_1", im.size)
# Kanıt 2 (son kare): sayfa 1 üst (To/From/tarih, başlık, ilk cümleler), tam satırda kesim
crop_w("kanit-1-nara-safire-memo-sayfa-1.png", (120, 66, 1012, 512), "kanit_2.jpg")
