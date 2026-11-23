"""en-jfk-coconut gorselleri:  python episodes/en-jfk-coconut/gorsel.py
arka.jpg   : Marovo Lagoon (CC BY 2.0) sol-ust kare kirpim 1200x1200 (sag uctaki iskele disarida) -> 1080, renk 0,68, parlaklik 1,2.
ev_1.jpg   : PT-109 teknesi, 1942 (Navsource/US Navy, PD-USGov) 840x635 kirpim -> 1080x816.
ev_2.jpg   : hindistancevizi kabugu (JFK Library, PD) 647x632 -> yukseklik 816 (1,29x), yanlar nesnesiz zemin uzatilarak 1080'e tamamlanir.
"""
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np

H = Path(__file__).resolve().parent / "img"

bg = Image.open(H / "arka-plan-marovo-lagoon-1920.jpg").convert("RGB").crop((0, 0, 1200, 1200)).resize((1080, 1080), Image.LANCZOS)
bg = ImageEnhance.Color(bg).enhance(0.68)
bg = ImageEnhance.Brightness(bg).enhance(1.2)
bg.save(H / "arka.jpg", quality=93)

p = Image.open(H / "kanit-pt109-navy-1942.jpg").convert("RGB")
sc = p.width / 1280
x0, y0, w0, h0 = 190, 95, 840, 635
p = p.crop((round(x0 * sc), round(y0 * sc), round((x0 + w0) * sc), round((y0 + h0) * sc))).resize((1080, 816), Image.LANCZOS)
p = p.filter(ImageFilter.UnsharpMask(1.2, 40, 2)).convert("RGB")
p.save(H / "ev_1.jpg", quality=93)

c = Image.open(H / "kanit-jfk-coconut-647.jpg").convert("RGB")
w = round(c.width * 816 / c.height)
c = c.resize((w, 816), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.5, 50, 2))
out = Image.new("RGB", (1080, 816))
arr = np.asarray(c).astype(float)
left = arr[:, :6].mean(axis=1, keepdims=True)    # (816,1,3) kenar sutunu ortalamasi
right = arr[:, -6:].mean(axis=1, keepdims=True)
x1 = (1080 - w) // 2
out.paste(Image.fromarray(np.repeat(left, x1, axis=1).astype("uint8")), (0, 0))
out.paste(Image.fromarray(np.repeat(right, 1080 - x1 - w, axis=1).astype("uint8")), (x1 + w, 0))
out.paste(c, (x1, 0))
out = out.filter(ImageFilter.GaussianBlur(0.0))
out.save(H / "ev_2.jpg", quality=93)
print("ok", w)
