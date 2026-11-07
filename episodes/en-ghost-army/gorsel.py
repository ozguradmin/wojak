"""en-ghost-army görselleri (img/kaynak/ -> img/):  python episodes/en-ghost-army/gorsel.py
arka.jpg      : Bettembourg (Lüksemburg) ormanı, levhayı hariç tutan sol kırpım (Commons, GilPe, CC BY-SA 4.0); renk/parlaklık ayarı
ev_levha.jpg  : Ghost Army Bettembourg anma levhasının başlığı (Commons, Zinneke, CC BY-SA 4.0); başlık satırına sıkı kırpım, 1080 genişlik
ev_tank.jpg   : Uluslararası Casusluk Müzesi'ndeki şişirme tank (Commons, ArtemisiaGentileschiFan, CC0); 1080x810 kırpım
"""
from pathlib import Path
from PIL import Image, ImageEnhance
import numpy as np

HERE = Path(__file__).resolve().parent
K = HERE / "img" / "kaynak"
O = HERE / "img"


def arka():
    im = Image.open(K / "woods.jpg").convert("RGB").crop((0, 20, 760, 780)).resize((960, 960), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(0.62)
    im = ImageEnhance.Brightness(im).enhance(1.2)
    im.save(O / "arka.jpg", quality=93)


def levha():
    im = Image.open(K / "plate.jpg").convert("RGB")
    c = im.crop(BOX_LEVHA)
    c = c.resize((1080, int(c.height * 1080 / c.width)), Image.LANCZOS)
    c.save(O / "ev_levha.jpg", quality=93)


def tank():
    im = Image.open(K / "museum_tank.jpg").convert("RGB")
    c = im.crop(BOX_TANK)
    c = c.resize((1080, int(c.height * 1080 / c.width)), Image.LANCZOS)
    c.save(O / "ev_tank.jpg", quality=93)


BOX_LEVHA = (420, 230, 1235, 640)
BOX_TANK = (150, 330, 1740, 1340)

if __name__ == "__main__":
    arka(); levha(); tank()
