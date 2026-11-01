"""en-roosevelt-bullet-speech görselleri: python episodes/en-roosevelt-bullet-speech/gorsel.py
Ham indirmeler img/ içinde (bg_1, kanit_1, kanit_2, kanit_3); kaynaklar/lisanslar yaml sources + RAPOR.
"""
from pathlib import Path
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

H = Path(__file__).resolve().parent / "img"

# arka plan: LOC Photochrom (c.1900), siyah kenar/yazı dışı; teller ve tabelalar altta kalır -> üst kare kırpım
bg = Image.open(H / "bg_1.jpg").convert("RGB")
bg = bg.crop((211, 56, 1732, 1577)).resize((1080, 1080), Image.LANCZOS)
bg = ImageEnhance.Color(bg).enhance(0.75)
bg = ImageEnhance.Brightness(bg).enhance(0.80)
bg.save(H / "bg.jpg", quality=93)

# kanıt 1: Roosevelt şapkasını kaldırıyor (960x1115) -> 960x725 üst kısım -> 1080x816
k1 = Image.open(H / "kanit_1.jpg").convert("RGB").crop((0, 10, 960, 735)).resize((1080, 816), Image.LANCZOS)
k1.save(H / "ev_1.jpg", quality=94)

# kanıt 3 (ilk kanıt): Bain 1912 fotoğrafı, delikli konuşma sayfaları (715x465) -> 1080x702; alt yazı ve yüz dışarıda; yalnız autocontrast
k3 = Image.open(H / "kanit_3.jpg").convert("RGB").crop((1015, 1340, 1730, 1805)).resize((1080, 702), Image.LANCZOS)
ImageOps.autocontrast(k3, cutoff=1).save(H / "ev_3.jpg", quality=94)

# kanıt 2 (son kare): delinmiş çelik gözlük kutusu (750x750 kolajın alt yarısı, kolaj kenarlığı içeride bırakıldı) -> 1080 genişlik.
# Kaynak fotoğraf aşırı işlenmiş (sarı-mavi renk sapması, patlak ışık); siyah-beyaza çevrilir, autocontrast + gama, hafif blur (JPEG blokları)
c = Image.open(H / "kanit_2.jpg").convert("RGB").crop((102, 436, 656, 714))
c = c.resize((1080, int(1080 * 278 / 554)), Image.LANCZOS).convert("L")
c = ImageOps.autocontrast(c, cutoff=0.1)
c = Image.eval(c, lambda v: int(255 * (v / 255) ** 0.95)).filter(ImageFilter.GaussianBlur(0.9)).convert("RGB")
c.save(H / "ev_2.jpg", quality=94)
