"""en-boston-molasses-flood görselleri: python episodes/en-boston-molasses-flood/gorsel.py
Kaynaklar (img/ham/): twharf.jpg (Commons 'Fishing Schooners at T Wharf, Boston, Mass (NYPL b12647398-68427).tiff', PD), globe_1919.png (Commons 'Boston Daily Globe Jan. 16, 1919.png', PD),
plaque.jpg (Commons 'Molasses Flood Historical Marker.jpg', CC BY-SA 3.0, MLHalsey).
Çıktılar: img/arka.jpg (1080x1080), img/kanit_1.jpg (Globe, 1080x607), img/kanit_2.jpg (levha, 1080x815).
"""
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter

H = Path(__file__).resolve().parent / "img"
R = H / "ham"

# arka plan: T Wharf, Boston (Detroit Publishing Co. photochrom kartpostalı, 1905 ~; renkli), kare kırpım, kart kenarı dışarıda
t = Image.open(R / "twharf.jpg").convert("RGB")
sc = t.width / 1280
x0, y0, sz = round(150 * sc), round(80 * sc), round(640 * sc)
t = t.crop((x0, y0, x0 + sz, y0 + sz)).resize((1080, 1080), Image.LANCZOS)
t = ImageEnhance.Color(t).enhance(1.0)
t = ImageEnhance.Brightness(t).enhance(0.92)
t.save(H / "arka.jpg", quality=93)

# kanıt 1: Boston Daily Globe 16 Ocak 1919 (üst yarı), 850 -> 1080 (1,27x)
g = Image.open(R / "globe_1919.png").convert("RGB")
g = g.resize((1080, round(g.height * 1080 / g.width)), Image.LANCZOS)
g.save(H / "kanit_1.jpg", quality=95)

# kanıt 2: Bostonian Society levhası (renkli), tam metin, 1366x1031 -> 1080x815
p = Image.open(R / "plaque.jpg").convert("RGB")
p = p.crop((292, 277, 1658, 1308)).resize((1080, 815), Image.LANCZOS)
p.save(H / "kanit_2.jpg", quality=95)
print("ok")
