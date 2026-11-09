"""en-pig-war görselleri (ham indirilenlerden):  python episodes/en-pig-war/gorsel.py
 arka.jpg : 'American Camp, San Juan Island (23758)' (Buidhe, CC BY-SA 4.0): üst kısım kare kırpım (çit dışarıda), renk/parlaklık ayarı
 ev_1.jpg : NARA 1860 haritası 'Map of South East End of San Juan Island' (PD-USGov): başlık + harita + açıklama, 1080 genişlik
 ev_2.jpg : 'British troops evacuate San Juan Island, 1872' (BC Mining Record 1899, PD-1923): 1080x816 kırpım
"""
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np

H = Path(__file__).resolve().parent / "img"


def arka():
    im = Image.open(H / "arka_1_1920.jpg").convert("RGB")
    W, Hh = im.size
    box = (int(W * 0.03), 130, int(W * 0.03) + 830, 960)
    im = im.crop(box).resize((1080, 1080), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(0.72)
    im = ImageEnhance.Brightness(im).enhance(0.80)
    im.save(H / "arka.jpg", quality=93)
    a = np.asarray(im.convert("HSV")).astype(float)
    print("arka  V=%.0f S=%.2f" % (a[..., 2].mean() * 1.0, a[..., 1].mean() / 255))


def ev1():
    im = Image.open(H / "map_1920.jpg").convert("RGB")
    s = 1920 / 1000
    box = (int(150 * s), int(70 * s), int(870 * s), int(70 * s) + int(720 * s * 816 / 1080))
    im = im.crop(box).resize((1080, 816), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 60, 2))
    im.save(H / "ev_1.jpg", quality=94)
    print("ev1", im.size)


def ev2():
    im = Image.open(H / "evac_orig.jpg").convert("RGB")
    im = im.crop((0, 57, 1280, 1024)).resize((1080, 816), Image.LANCZOS)
    im.save(H / "ev_2.jpg", quality=94)
    print("ev2", im.size)


if __name__ == "__main__":
    arka(); ev1(); ev2()
