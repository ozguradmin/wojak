"""en-dancing-plague-1518 görselleri: python episodes/en-dancing-plague-1518/gorsel.py
Kaynaklar img/ altında (Commons, bkz. episode.yaml sources). Üretilen: bg_katedral.jpg, kanit_1_brant.jpg, kanit_2_bruegel.jpg
"""
from pathlib import Path
from PIL import Image, ImageEnhance
HERE = Path(__file__).resolve().parent
IMG = HERE / "img"

# arka plan: Strasbourg Katedrali batı cephesi (Diliff, CC BY-SA 3.0), gökyüzünü atan kare kırpım, renk/parlaklık azaltıldı
b = Image.open(IMG / "bg_katedral_1920.jpg").convert("RGB")
c = b.crop((330, 760, 1630, 2060))
c = ImageEnhance.Color(c).enhance(0.45)
c = ImageEnhance.Brightness(c).enhance(0.95)
c.save(IMG / "bg_katedral.jpg", quality=93)

# kanıt 1: Brant imzalı 2 Ağustos 1518 kaydı, alt yarı (tarih satırı + imza), yalnız kırpım
d = Image.open(IMG / "kanit_1_brant_1518_tam.jpg").convert("RGB")
d.crop((240, 380, 1320, 1196)).save(IMG / "kanit_1_brant.jpg", quality=95)

# kanıt 2 (son kare): Brueghel II, 'Saint John's Dancers in Molenbeeck' (1592), tam kare, 1080 genişliğe küçültüldü
p = Image.open(IMG / "kanit_bruegel_orijinal.jpg").convert("RGB")
p.resize((1080, round(p.height * 1080 / p.width)), Image.LANCZOS).save(IMG / "kanit_2_bruegel.jpg", quality=95)
