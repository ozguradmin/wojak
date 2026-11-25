"""en-hess-scotland gorselleri:  python episodes/en-hess-scotland/gorsel.py
arka.jpg : Bonnyton Moor otlagi (Alec MacKinnon, CC BY-SA 2.0, geograph 4963623) 1280x960 -> koyun silinir, 650x650 kare kirpim (sol koyun disarida) (elektrik diregi disarida) -> 1080; renk/parlaklik.
ev_1.jpg : IWM H 9553, Hess'in Bf 110 enkazi, 1941 (War Office official photographer, PD-UKGov) 800x619 -> 1080x836 -> ustten/alttan 816'ya kirpim.
arka2.jpg: Spandau gozetleme kulesi (CC BY-SA 3.0), sok sahnesinin arka plani.
ev_2.jpg : Spandau Hapishanesi ana girisi (Bauamt Spandau/Einofski, CC BY-SA 3.0) 960x637 -> kirpim 760x574 -> 1080x816 (son kare).
"""
from pathlib import Path
from PIL import Image, ImageEnhance

H = Path(__file__).resolve().parent / "img"

import cv2
import numpy as np
im = cv2.imread(str(H / "bg_bonnyton_moor.jpg"))
x0, y0, x1, y1 = 965, 520, 1200, 712      # otlayan koyun ve golgesi: ayni derinlikteki sol cimen yamasi ile (seamlessClone) kapatilir
w, h = x1 - x0, y1 - y0
mask = np.zeros((h, w), np.uint8)
mask[8:-8, 8:-8] = 255
im = cv2.seamlessClone(im[y0:y1, 725:725 + w].copy(), im, mask, ((x0 + x1) // 2, (y0 + y1) // 2), cv2.NORMAL_CLONE)
bg = Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))
bg = bg.crop((630, 200, 1280, 850)).resize((1080, 1080), Image.LANCZOS)
bg = ImageEnhance.Color(bg).enhance(0.66)
bg = ImageEnhance.Brightness(bg).enhance(1.06)
bg.save(H / "arka.jpg", quality=93)

e1 = Image.open(H / "kanit_alt_iwm_h9553_800px.jpg").convert("RGB")
e1 = e1.resize((1080, round(e1.height * 1080 / e1.width)), Image.LANCZOS)
t = (e1.height - 816) // 2
e1 = e1.crop((0, t, 1080, t + 816))
print("ev_1", e1.size)
e1.save(H / "ev_1.jpg", quality=93)

e2 = Image.open(H / "gorsel_spandau_2.jpg").convert("RGB")
e2 = e2.crop((200, 40, 960, 614)).resize((1080, 816), Image.LANCZOS)
print("ev_2", e2.size)
e2.save(H / "ev_2.jpg", quality=93)

# arka2.jpg: Spandau gozetleme kulesi (Bauamt Sued / Einofski, CC BY-SA 3.0, "Kriegsverbrechergefaengnis Spandau - Wachturm.JPG") 960x640 -> 640x640 kare kirpim -> 1080
b2 = Image.open(H / "gorsel_spandau_3.jpg").convert("RGB").crop((100, 0, 740, 640)).resize((1080, 1080), Image.LANCZOS)
b2 = ImageEnhance.Color(b2).enhance(0.85)
b2 = ImageEnhance.Brightness(b2).enhance(1.0)
b2.save(H / "arka2.jpg", quality=93)
