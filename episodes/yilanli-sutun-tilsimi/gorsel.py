"""yilanli-sutun-tilsimi: arka plan ve kanıt görsellerini kaynaklardan üretir.

python episodes/yilanli-sutun-tilsimi/gorsel.py
Kaynaklar (img/): arka_aday_13.jpg, freshfield_kaynak.jpg, kanit_2_kaynak_b.jpg (lisanslar episode.yaml sources).
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

IMG = Path(__file__).parent / "img"


def olc(im: Image.Image, ad: str) -> None:
    k = im.convert("RGB").resize((720, int(720 * im.height / im.width)))
    hsv = np.asarray(k.convert("HSV"), dtype=float)
    gri = np.asarray(k.convert("L"), dtype=float)
    lap = (gri[1:-1, 1:-1] * 4 - gri[:-2, 1:-1] - gri[2:, 1:-1] - gri[1:-1, :-2] - gri[1:-1, 2:]).var()
    print(f"{ad}: {im.size} parlaklık {gri.mean():.0f} doygunluk {hsv[..., 1].mean() / 255:.2f} laplace {lap:.0f}")


# Arka plan: Dikilitaş ve Sultanahmet Camii (At Meydanı); alttaki lamba direkleri ve araç tavanı kırpımın dışında.
a = Image.open(IMG / "arka_aday_13.jpg").convert("RGB")
a = a.crop((0, 470, 1280, 1750))
a = ImageEnhance.Color(a).enhance(1.0)
a = ImageEnhance.Brightness(a).enhance(0.84)
a.save(IMG / "arka.jpg", quality=92)
olc(a, "arka")

# Kanıt 1: Freshfield Albümü (1574) fol. 20, üç başlı Yılanlı Sütun; sütun ortada, solda Dikilitaş, sağda Örme Dikilitaş.
f = Image.open(IMG / "freshfield_kaynak.jpg").convert("RGB")
x0, y1 = 801, 904   # özgün 1678x923 dosyada
w = 640
h = round(w * 816 / 1080)
f = f.crop((x0, y1 - h, x0 + w, y1)).resize((1080, 816), Image.LANCZOS)
f = f.filter(ImageFilter.UnsharpMask(2, 40, 2))
f = ImageOps.autocontrast(f, cutoff=0.5)
f.save(IMG / "kanit_1.jpg", quality=92)
olc(f, "kanit_1")

# Kanıt 2 (son kare): İstanbul Arkeoloji Müzeleri'ndeki yılan başı (üst çene), yandan; göz, diş sırası ve kopuk boyun.
k = Image.open(IMG / "kanit_2_kaynak_b.jpg").convert("RGB")
k = k.crop((10, 170, 1910, 1296)).resize((1080, 640), Image.LANCZOS)
k = ImageEnhance.Contrast(k).enhance(1.08)
k.save(IMG / "kanit_2.jpg", quality=92)
olc(k, "kanit_2")
