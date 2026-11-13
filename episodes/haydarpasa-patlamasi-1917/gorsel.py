"""haydarpasa-patlamasi-1917: arka plan ve kanıtları img/ altındaki Commons indirmelerinden hazırlar.

    python episodes/haydarpasa-patlamasi-1917/gorsel.py
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

IMG = Path(__file__).resolve().parent / "img"


def olc(im, ad):
    g = np.asarray(im.convert("L").resize((720, int(720 * im.height / im.width))), dtype=np.float32)
    hsv = np.asarray(im.convert("HSV"), dtype=np.float32)
    lap = np.abs(g[1:-1, 1:-1] * 4 - g[:-2, 1:-1] - g[2:, 1:-1] - g[1:-1, :-2] - g[1:-1, 2:]).var()
    print(f"{ad}: {im.size} parlaklık {g.mean():.0f} doygunluk {hsv[..., 1].mean() / 255:.2f} laplace {lap:.0f}")


# Arka plan: Fruchtermann renkli kartpostalı; üstteki Osmanlıca ve Fransızca başlık şeridi kırpıldı, kare kadraj.
k = Image.open(IMG / "arka_aday1.jpg").convert("RGB")
arka = k.crop((300, 190, 300 + 1028, 190 + 1028))
arka = ImageEnhance.Color(arka).enhance(1.15)
arka = ImageEnhance.Brightness(arka).enhance(0.95)
arka.save(IMG / "arka.jpg", quality=92)
olc(arka, "arka")

# Kanıt 1: Avusturya Devlet Arşivi (Kriegsarchiv BS I WK Fronten Türkei 711), "Haidar Pascha, Brand des Bahnhofes":
# yangından sonra gar sahası, devrilmiş fıçılar ve bükülmüş demir. Arşiv kartonu ve alttaki daktilo etiketi kırpıldı.
d = Image.open(IMG / "kanit1_oesta.jpg").convert("L")
d = d.crop((48, 95, 1800, 1235))
d = ImageOps.autocontrast(d, cutoff=0.5).resize((1080, round(1080 * 1140 / 1752)), Image.LANCZOS)
d.convert("RGB").save(IMG / "kanit_1.jpg", quality=92)
olc(d.convert("RGB"), "kanit_1")

# Kanıt 2 (son kare): patlamadan sonra harap gar, Eylül 1917; gar kadrajın ~%90'ı (gökyüzü, su ve alt yazı şeridi kırpıldı).
g = Image.open(IMG / "kanit2_aday3.jpg").convert("L")
g = g.crop((262, 112, 1712, 1052))
g = ImageOps.autocontrast(g, cutoff=0.5).resize((1080, round(1080 * 940 / 1450)), Image.LANCZOS)
g = g.filter(ImageFilter.UnsharpMask(1.2, 40, 2))
g.convert("RGB").save(IMG / "kanit_2.jpg", quality=92)
olc(g.convert("RGB"), "kanit_2")
