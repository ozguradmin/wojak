"""en-dickens-staplehurst gorselleri:  python episodes/en-dickens-staplehurst/gorsel.py
arka.jpg : Ouse Valley Viaduct (HJ Mitchell, CC BY 4.0), 1440x1440 kare kirpim (sagdan) -> 1080; renk/parlaklik ayari.
ev_1.jpg : Illustrated London News 1865 Staplehurst gravuru (PD-old) 1280x901 -> 1080x760.
ev_2.jpg : Our Mutual Friend, Chapman & Hall 1865, cilt II baslik sayfasi (IA ourmutualfriend00stongoog, leaf n11): baslik + yazar, 2400x1700 kirpim -> 1080x765.
ev_3.jpg : Dickens'in Westminster Abbey tasi (Zmbro, CC BY-SA 4.0, "Charles Dickens grave.jpg"): 1480x800 kirpim -> 1080x584 (son kare).
"""
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import numpy as np

H = Path(__file__).resolve().parent / "img"

bg = Image.open(H / "arka-plan-balcombe-viaduct-1920.jpg").convert("RGB")
bg = bg.crop((276, 0, 1608, 1332)).resize((1080, 1080), Image.LANCZOS)
bg = ImageEnhance.Color(bg).enhance(0.85)
bg = ImageEnhance.Brightness(bg).enhance(1.15)
bg.save(H / "arka.jpg", quality=93)

e1 = Image.open(H / "kanit1-staplehurst-rail-crash-ILN-1865.jpg").convert("RGB")
e1 = e1.resize((1080, round(e1.height * 1080 / e1.width)), Image.LANCZOS)
print("ev_1", e1.size)
e1.save(H / "ev_1.jpg", quality=93)

t = Image.open(H / "kanit2-baslik-sayfasi-n11-w2000.jpg").convert("L")
c = t.crop((330, 380, 2730, 2080)).resize((1080, 765), Image.LANCZOS)
c = ImageOps.autocontrast(c, cutoff=0.3).convert("RGB")
c = Image.fromarray((np.asarray(c).astype(float) * np.array([0.965, 0.93, 0.83])).clip(0, 255).astype("uint8"))   # kagit tonu (yalniz zemin rengi)
print("ev_2", c.size)
c.save(H / "ev_2.jpg", quality=93)

g = Image.open(H / "grave-zmbro-2022-src-1920.jpg").convert("RGB")
c = g.crop((185, 353, 1665, 1153)).resize((1080, 584), Image.LANCZOS)
print("ev_3", c.size)
c.save(H / "ev_3.jpg", quality=93)
