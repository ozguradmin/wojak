"""en-lincoln-body-snatchers: img/ dosyalarini indirilen kaynaklardan uretir (python episodes/en-lincoln-body-snatchers/gorsel.py)."""
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter

HERE = Path(__file__).resolve().parent
IMG = HERE / "img"

# Arka plan: Lincoln Tomb, Oak Ridge (Adam63, CC BY-SA 4.0), kare kirpim, renk ve parlaklik dusuruldu
bg = Image.open(IMG / "bg_1.jpg").convert("RGB")
bg = bg.crop((560, 600, 1400, 1440)).resize((1080, 1080), Image.LANCZOS)
bg = ImageEnhance.Color(bg).enhance(0.7)
bg = ImageEnhance.Brightness(bg).enhance(1.15)
bg.save(IMG / "arka.jpg", quality=93)

# Kanit 1: J. C. Power, History of an Attempt to Steal the Body of Abraham Lincoln (1890), kapak sayfasi (Internet Archive)
t = Image.open(IMG / "ia_power_title_n8.jpg").convert("RGB")
x0, y0, w = 160, 230, 2500
t = t.crop((x0, y0, x0 + w, y0 + int(w * 740 / 1080))).resize((1080, 740), Image.LANCZOS)
t = ImageEnhance.Contrast(t).enhance(1.1).filter(ImageFilter.UnsharpMask(1.5, 60, 2))
t.save(IMG / "ev_1.jpg", quality=93)

# Kanit 2 (son kare): ayni kitaptan "Interior of the Catacomb, as the Thieves Left It" (s. 56), sayfa 90 derece dondurulup plaka kirpildi
c = Image.open(IMG / "ia_power_catacomb_n63.jpg").convert("RGB").rotate(-90, expand=True)
x0, y0, w = 1320, 640, 2560
c = c.crop((x0, y0, x0 + w, y0 + int(w * 816 / 1080))).resize((1080, 816), Image.LANCZOS)
c = ImageEnhance.Contrast(c).enhance(1.1).filter(ImageFilter.UnsharpMask(1.5, 60, 2))
c.save(IMG / "ev_2.jpg", quality=93)
