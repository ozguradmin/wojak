"""en-elvis-nixon-badge: img/ dosyalarini indirilen kaynaklardan uretir (python episodes/en-elvis-nixon-badge/gorsel.py)."""
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter

HERE = Path(__file__).resolve().parent
IMG = HERE / "img"

# Arka plan: Beyaz Saray kuzey cephesi (Nminow, CC BY-SA 3.0), kare kirpim, renk ve parlaklik hafif dusuruldu
bg = Image.open(IMG / "bg-whitehouse-north-lawn.jpg").convert("RGB")
W, H = bg.size
bg = bg.crop((560, 20, 560 + 1250, 20 + 1250)).resize((1080, 1080), Image.LANCZOS)
bg = ImageEnhance.Color(bg).enhance(0.92)
bg = ImageEnhance.Brightness(bg).enhance(0.80)
bg.save(IMG / "arka.jpg", quality=93)

# Kanit 2 (son kare): Ollie Atkins fotografi (21.12.1970), 1080 genislik
p = Image.open(IMG / "ev-elvis-nixon-atkins.jpg").convert("RGB")
w, h = p.size
p = p.resize((1080, int(h * 1080 / w)), Image.LANCZOS)
p.save(IMG / "ev_2.jpg", quality=93)

# Kanit 1: 21.12.1970 Beyaz Saray notu, 2. sayfa (NSA/GWU kopyasi, ABD hukumeti belgesi); el yazisi "You must be kidding"
m = Image.open(IMG / "ev-memo-p2-000.png").convert("L")
m = m.crop((110, 224, 1190, 224 + 545)).resize((1080, 545), Image.LANCZOS)
m = m.point(lambda v: 255 if v > 150 else int(v * 0.9))
rgb = Image.merge("RGB", [m.point(lambda v: v), m.point(lambda v: int(v * 0.985)), m.point(lambda v: int(v * 0.95))])
rgb.save(IMG / "ev_1.jpg", quality=93)
