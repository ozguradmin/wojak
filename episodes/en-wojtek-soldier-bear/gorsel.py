"""en-wojtek-soldier-bear görselleri: python episodes/en-wojtek-soldier-bear/gorsel.py
Kaynaklar img/*-src.jpg (Commons 1920 px). arka.jpg: Monte Cassino manastırı (CC0, 2019) kare kırpım, renk 0,6 + parlaklık 0,9.
ev_1: Edinburgh Wojtek anıtı (M J Richardson, CC BY-SA 2.0) 1080x810; ev_2 (son kare): Weelsby Woods Wojtek heykeli (CC0), ayı + mermi, 1080x816.
"""
from pathlib import Path
from PIL import Image, ImageEnhance

H = Path(__file__).resolve().parent / "img"

im = Image.open(H / "bg-src.jpg").convert("RGB")
w, h = im.size
cx = int(w * 0.46)
x0 = max(0, min(w - h, cx - h // 2))
im = im.crop((x0, 0, x0 + h, h)).resize((1080, 1080), Image.LANCZOS)
im = ImageEnhance.Color(im).enhance(0.6)
im = ImageEnhance.Brightness(im).enhance(0.92)
im.save(H / "arka.jpg", quality=95)

im = Image.open(H / "ev1-src.jpg").convert("RGB")
im.crop((0, 0, 1920, 1440)).resize((1080, 810), Image.LANCZOS).save(H / "ev_1.jpg", quality=95)

im = Image.open(H / "ev2-src.jpg").convert("RGB")
im.crop((230, 80, 1690, 1183)).resize((1080, 816), Image.LANCZOS).save(H / "ev_2.jpg", quality=95)
