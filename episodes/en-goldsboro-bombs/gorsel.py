"""en-goldsboro-bombs görselleri: img/ham dosyalarından arka plan ve 2 kanıt üretir (python episodes/en-goldsboro-bombs/gorsel.py)."""
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np

H = Path(__file__).resolve().parent / "img"

def stats(im):
    a = np.asarray(im.convert("RGB")).astype(float)
    g = a.mean(axis=2)
    hsv = np.asarray(im.convert("HSV")).astype(float)
    return round(g.mean(), 1), round(hsv[..., 1].mean() / 255, 3)

# arka plan: Goldsboro yakınında tarla (CC0) -> kare kırpım, hafif solgun
bg = Image.open(H / "arka_aday1.jpg").convert("RGB")
W, Hh = bg.size
bg = bg.crop((190, 150, 190 + 800, 150 + 800))
bg = ImageEnhance.Color(bg).enhance(0.62)
bg = ImageEnhance.Brightness(bg).enhance(0.93)
bg.save(H / "arka.jpg", quality=92)
print("arka", bg.size, stats(bg))

# kanıt 1: bomba ağaçta (USAF 1961), film perdesi siyah kenarları atıldı
k1 = Image.open(H / "kanit_1.jpg").convert("RGB")
k1 = k1.crop((30, 26, 1222, 696))           # 1192x670
k1 = k1.resize((1080, int(1080 * 670 / 1192)), Image.LANCZOS)
k1.save(H / "ev_bomba.jpg", quality=93)
print("ev1", k1.size)

# kanıt 2 (son kare): Eureka NC tarihî levhası (CC BY-SA 3.0), levha + dar kırpım
k6 = Image.open(H / "kanit_6.jpg").convert("RGB")
k6 = k6.crop((120, 95, 940, 95 + 615))      # 820x615 -> 1080x810
k6 = k6.resize((1080, 810), Image.LANCZOS)
k6.save(H / "ev_levha.jpg", quality=93)
print("ev2", k6.size)
