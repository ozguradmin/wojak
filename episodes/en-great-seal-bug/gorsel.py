"""en-great-seal-bug görselleri: python episodes/en-great-seal-bug/gorsel.py
arka.jpg  : Spaso House (2019) 08 by shakko (CC BY-SA 4.0): kare kırpım, "LADIES' ROOM" tabelası inpaint, renk/parlaklık, hafif yumuşak
ev_1.jpg  : NSA Great Seal bug.jpg (kapalı mühür, PD NSA)  -> 1080x816 sıkı kırpım
ev_2.jpg  : Great Seal bug - National Cryptologic Museum - DSC08049 (Daderot, CC0) -> 1080x816
"""
from pathlib import Path
import numpy as np, cv2
from PIL import Image, ImageEnhance

H = Path(__file__).resolve().parent / "img"

# --- arka plan
im = Image.open(H / "arka_kaynak_shakko.jpg").convert("RGB")
im = im.crop((520, 640, 1460, 1580))
a = np.array(im)
mask = np.zeros(a.shape[:2], np.uint8)
mask[1330 - 640:1395 - 640, 1262 - 520:1348 - 520] = 255
a = cv2.inpaint(a, mask, 5, cv2.INPAINT_TELEA)
im = Image.fromarray(a).resize((1080, 1080), Image.LANCZOS)
im = ImageEnhance.Color(im).enhance(0.62)
im = ImageEnhance.Brightness(im).enhance(1.02)
im.save(H / "arka.jpg", quality=93)

# --- kanit 1
k = Image.open(H / "kanit1_kaynak.jpg").convert("RGB")
print("kanit1", k.size)
W, Hh = k.size
# 1080x816 oranı: genişlik 1280 -> yükseklik 967; sıkı kırpım (şalter plaka dışarıda)
k1 = k.crop((230, 250, 230 + 980, 250 + int(980 * 816 / 1080)))
k1.resize((1080, 816), Image.LANCZOS).save(H / "ev_1.jpg", quality=93)

# --- kanit 2
k = Image.open(H / "kanit2_kaynak.jpg").convert("RGB")
print("kanit2", k.size)
cw = 1250
x0 = 670
k2 = k.crop((x0, 130, x0 + cw, 130 + int(cw * 816 / 1080)))
k2.resize((1080, 816), Image.LANCZOS).save(H / "ev_2.jpg", quality=93)
