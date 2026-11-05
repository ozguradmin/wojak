"""en-cadaver-synod görselleri: python episodes/en-cadaver-synod/gorsel.py
Kaynaklar (img/kaynak/): arka_plan1_lateran_nef_2_1920.jpg (Commons 'Roma, Basilica di San Giovanni in Laterano, interno (2).jpg', Palickap, CC BY-SA 4.0),
alt_kanit2_lachatre_gravur_1280.jpg (Commons 'Cadaver Synod illustration on Maurice de La Châtre's Histoire des papes.jpg', PD-old-70-expired),
kanit1_son_kare_laurens_nantes_1920.jpg (Commons 'Jean Paul Laurens Le Pape Formose et Etienne VI 1870.jpg', PD-Art).
Çıktılar: img/arka.jpg (1080x1080), img/kanit_1.jpg (gravür, 1080x760), img/kanit_2.jpg (Laurens, 1080x717).
"""
from pathlib import Path
import sys
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np

H = Path(__file__).resolve().parent / "img"
R = H / "kaynak"
COLOR = float(sys.argv[1]) if len(sys.argv) > 1 else 0.38
BRIGHT = float(sys.argv[2]) if len(sys.argv) > 2 else 1.22

# arka plan: Lateran nefi, üst kısım (sandalye, insan ve ekran kadraj dışında), kare kırpım
a = Image.open(R / "arka_plan1_lateran_nef_2_1920.jpg").convert("RGB")
x0, y0, sz = 470, 0, 930
a = a.crop((x0, y0, x0 + sz, y0 + sz)).resize((1080, 1080), Image.LANCZOS)
a = ImageEnhance.Color(a).enhance(COLOR)
a = ImageEnhance.Brightness(a).enhance(BRIGHT)
a.save(H / "arka.jpg", quality=93)

# kanıt 1: La Châtre gravürü (c. 1870), sahne kırpımı 790x555 -> 1080x760
g = Image.open(R / "alt_kanit2_lachatre_gravur_1280.jpg").convert("RGB")
g = g.crop((250, 685, 1000, 1213)).resize((1080, 760), Image.LANCZOS)
g.save(H / "kanit_1.jpg", quality=95)

# kanıt 2: Laurens (1870), tam tablo 1920x1276 -> 1080x717
p = Image.open(R / "kanit1_son_kare_laurens_nantes_1920.jpg").convert("RGB")
p = p.resize((1080, 717), Image.LANCZOS)
p.save(H / "kanit_2.jpg", quality=95)

# ölçüm (arka plan)
import colorsys
sm = a.resize((720, 720))
arr = np.asarray(sm).astype(float) / 255
mx, mn = arr.max(2), arr.min(2)
sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0).mean()
gray = np.asarray(sm.convert("L")).astype(float)
lap = gray[1:-1, 1:-1] * 4 - gray[:-2, 1:-1] - gray[2:, 1:-1] - gray[1:-1, :-2] - gray[1:-1, 2:]
print(f"arka: parlaklık {gray.mean():.0f} doygunluk {sat:.3f} laplace {lap.var():.0f}")
