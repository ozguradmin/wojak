"""dumlupinar-denizaltisi-1953: arka plan ve ilk kanıt (son kare kupur.py'de).

    python episodes/dumlupinar-denizaltisi-1953/gorsel.py

img/arka2_cod_kic_torpido.jpg  'USS Cod, After Torpedo Room - 53057069719.jpg' (Eric Friedebach, 2022, CC BY 2.0;
                               Commons 1920 px küçük resmi). Balao/Gato dönemi ABD denizaltısının KIÇ torpido dairesi;
                               TCG Dumlupınar eski USS Blower (Balao sınıfı): aynı türden yer.
img/kanit1_blower_ss325.jpg    'Blower (SS-325) off the New England coast.jpg' (US Navy 80-G-286090, 24.10.1944, PD-USN).
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance

HERE = Path(__file__).resolve().parent
IMG = HERE / "img"


def olc(im):
    import cv2
    a = np.asarray(im.convert("RGB")).astype(np.float32)
    hsv = cv2.cvtColor(a.astype(np.uint8), cv2.COLOR_RGB2HSV)
    g = cv2.cvtColor(np.asarray(im.convert("RGB").resize((720, 720))), cv2.COLOR_RGB2GRAY)
    return round(a.mean(), 1), round(hsv[..., 1].mean() / 255, 3), round(cv2.Laplacian(g, cv2.CV_64F).var(), 1)


def arka():
    im = Image.open(IMG / "arka2_cod_kic_torpido.jpg").convert("RGB")      # 1920x1081
    im = im.crop((900, 0, 1800, 900)).resize((1080, 1080), Image.LANCZOS)    # sol: sandalye/pano, alt: turuncu makara ve parlak zemin dışarıda (1,2x)
    im = ImageEnhance.Color(im).enhance(0.45)
    im = ImageEnhance.Brightness(im).enhance(1.2)
    im.save(IMG / "arka.jpg", quality=92)
    print("arka.jpg", im.size, "parlaklık/doygunluk/laplace:", olc(im))


def kanit_1():
    im = Image.open(IMG / "kanit1_blower_ss325.jpg").convert("RGB")         # 1920x1263
    im = im.crop((0, 40, 1800, 1225)).resize((1080, 710), Image.LANCZOS)
    im.save(IMG / "kanit_1.jpg", quality=93)
    print("kanit_1.jpg", im.size)


if __name__ == "__main__":
    arka()
    kanit_1()
