"""en-titan-ii-socket görselleri (python episodes/en-titan-ii-socket/gorsel.py): arka plan + 2 kanıt.
Kaynaklar img/arka_1.jpg (Titan II silo, USAF 1987, PD), img/kanit_1.jpg (Titan Missile Museum, CC BY-SA 4.0),
img/ham_levha.jpg (DVIDS 9948943, 2000 px)."""
from pathlib import Path
from PIL import Image, ImageEnhance
import numpy as np

H = Path(__file__).resolve().parent / "img"


def stats(im):
    a = np.asarray(im.convert("RGB")).astype(float)
    hsv = np.asarray(im.convert("HSV")).astype(float)
    return round(a.mean(), 1), round(hsv[..., 1].mean() / 255, 3)


bg = Image.open(H / "arka_1.jpg").convert("RGB").crop((440, 0, 1440, 1000))
bg = ImageEnhance.Color(bg).enhance(0.8)
bg = ImageEnhance.Brightness(bg).enhance(0.88)
bg.save(H / "arka.jpg", quality=92)
print("arka", bg.size, stats(bg))

k1 = Image.open(H / "kanit_1.jpg").convert("RGB")
W, Hh = k1.size
k1 = k1.crop((0, 250, W, 250 + int(W * 700 / 1080)))
k1 = k1.resize((1080, 700), Image.LANCZOS)
k1.save(H / "ev_fuze.jpg", quality=93)
print("ev1", k1.size)

# kanit 2 (son kare): Arkansas tarihi levhasi (DVIDS, USAF foto, kamu malı), yalniz levha: kisiler kadrajdan atildi
lv = Image.open(H / "ham_levha.jpg").convert("RGB").crop((606, 159, 1144, 447))
lv = lv.resize((1080, int(lv.height * 1080 / lv.width)), Image.LANCZOS)
lv.save(H / "ev_levha.jpg", quality=93)
print("ev2", lv.size)
