"""en-habakkuk-ice-carrier: img/ dosyalarini indirilen kaynaklardan uretir (python episodes/en-habakkuk-ice-carrier/gorsel.py)."""
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter

HERE = Path(__file__).resolve().parent
IMG = HERE / "img"

# Arka plan: Chateau Frontenac (Quebec), kare kirpim, renk ve parlaklik hafif dusuruldu
bg = Image.open(IMG / "bg-frontenac-freezing-rain.jpg").convert("RGB")
bg = bg.crop((440, 40, 1190, 790)).resize((1080, 1080), Image.LANCZOS)
bg = ImageEnhance.Color(bg).enhance(0.62)
bg = ImageEnhance.Brightness(bg).enhance(0.80)
bg.save(IMG / "arka.jpg", quality=93)

# Kanit 1: Churchill, Quebec Agustos 1943 (NARA 197118), baski kenari kirpildi
m = Image.open(IMG / "ev-churchill-quebec-nara197118.jpg").convert("RGB")
m = m.crop((30, 60, 1890, 60 + int(1860 * 816 / 1080))).resize((1080, 816), Image.LANCZOS)
m.save(IMG / "ev_1.jpg", quality=93)

# Kanit 2 (son kare): King'in 9 Eylul 1943 tarihli "MEMORANDUM FOR THE PRESIDENT, Subject: HABBAKUKS" belgesi (PDF sayfa 2, gomulu tarama)
d = Image.open(IMG / "ev-naval-aide-memo-p2.jpg").convert("L")
d = d.crop((50, 125, 714, 125 + int(664 * 700 / 1080)))
d = d.resize((1080, 700), Image.LANCZOS)
d = ImageEnhance.Contrast(d).enhance(1.15).filter(ImageFilter.UnsharpMask(2, 70, 2))
d.convert("RGB").save(IMG / "ev_2.jpg", quality=93)
