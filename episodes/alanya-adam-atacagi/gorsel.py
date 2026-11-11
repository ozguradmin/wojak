"""alanya-adam-atacagi: arka plan ve iki kanıt (kaynak_*.jpg -> arka.jpg, kanit_1.jpg, kanit_2.jpg).

    python episodes/alanya-adam-atacagi/gorsel.py

kaynak_arka.jpg   'Walls of the Citadel of Alanya Castle.jpg', Julian Lupyan, CC0 (1920x851 indirildi)
kaynak_kanit1.jpg 'Cliff - Alanya - panoramio.jpg', Tanya Dedyukhina, CC BY 3.0 (1280x960)
kaynak_son_2.jpg  'Alanya Castle Cape Cilvarda View from Citadel 7914.jpg', Dosseman, CC BY-SA 4.0 (1920x1278)
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

HERE = Path(__file__).resolve().parent / "img"


def olc(im, ad):
    a = np.asarray(im.convert("RGB")).astype(float)
    hsv = np.asarray(im.convert("HSV")).astype(float)
    k = im.convert("L").resize((720, int(720 * im.height / im.width)))
    lap = np.asarray(k.filter(ImageFilter.FIND_EDGES)).astype(float)
    print(f"{ad}: {im.size} parlaklık {a.mean():.0f} doygunluk {hsv[..., 1].mean() / 255:.2f} kenar-var {lap.var():.0f}")


# Arka plan: mazgallı İç Kale siperi + deniz. Sol kare (deniz payı az); 4. mazgaldaki küçük modern bilgi tabelası
# (x 456-484, y 334-388) aynı mazgalın hemen altındaki taş dokusuyla örtülür (yumuşak kenarlı yama).
im = Image.open(HERE / "kaynak_arka.jpg").convert("RGB")
yama = im.crop((452, 392, 490, 450))
maske = Image.new("L", yama.size, 0)
maske.paste(255, (4, 4, yama.width - 4, yama.height - 4))
im.paste(yama, (450, 332), maske.filter(ImageFilter.GaussianBlur(3)))
im = im.crop((0, 0, 851, 851)).resize((1080, 1080), Image.LANCZOS)
im = ImageEnhance.Color(im).enhance(0.35)
im = ImageEnhance.Brightness(im).enhance(1.05)
im.save(HERE / "arka.jpg", quality=92)
olc(im, "arka")

# Kanıt 1: kalenin denize inen uçurumu, denizden. Sağdaki otel ve evler (x>840) ve tepedeki anten (y<200) kırpımın dışında.
im = Image.open(HERE / "kaynak_kanit1.jpg").convert("RGB")
im = im.crop((0, 250, 820, 250 + 574)).resize((1080, 756), Image.LANCZOS)
im.save(HERE / "kanit_1.jpg", quality=92)
olc(im, "kanit_1")

# Kanıt 2 (son kare): İç Kale'den Cilvarda yönü; mazgallı sur, altında dik uçurum ve basamaklı kayalık yamaç, dipte kaya
# burnu ve deniz. Üstteki gri gökyüzünün çoğu ve soldaki ağaç kümesi kırpımın dışında; modern öğe yok.
im = Image.open(HERE / "kaynak_son_2.jpg").convert("RGB")
im = im.crop((416, 300, 1920, 1278)).resize((1080, 702), Image.LANCZOS)
im = ImageEnhance.Brightness(im).enhance(1.12)
im.save(HERE / "kanit_2.jpg", quality=92)
olc(im, "kanit_2")
