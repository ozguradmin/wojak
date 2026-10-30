"""Uluburun görselleri: arka plan + iki kanıt (Commons, CC BY-SA). Çalıştır: python episodes/uluburun-kulakli-biskuvi/gorsel.py

arka_1.jpg  : 'Datça – 2 alte Fischerboote (1984)' (ingostrutz, CC BY-SA 3.0) -> img/arka.jpg (kırpım, renk)
kanit1_c.jpg: 'Bodrum Museum Uluburun shipwreck reconstruction in 2015 3711' (Dosseman, CC BY-SA 4.0) -> img/kanit_1.jpg
              (tur 1'de 3707 kullanılmıştı: mankenler öne çıkıyor, külçeler küçük kalıyordu)
son_a.jpg   : 'Uluburun copper ingot oxhide shaped' (Zunkir, CC BY-SA 4.0) -> img/kanit_2.jpg (son kare)
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageOps

D = Path(__file__).parent / "img"


def olc(im):
    a = np.asarray(im.convert("HSV")).astype(float) / 255
    return round(float(np.asarray(im.convert("L")).mean()), 1), round(float(a[..., 1].mean()), 3)


def arka():
    im = Image.open(D / "arka_1.jpg").convert("RGB").crop((110, 120, 1236, 1246)).resize((1080, 1080), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(0.52)
    im = ImageEnhance.Brightness(im).enhance(1.18)
    im.save(D / "arka.jpg", quality=92)
    print("arka", olc(im))


def kanit_1():
    im = Image.open(D / "kanit1_c.jpg").convert("RGB").crop((240, 180, 1840, 1080))
    im = im.resize((1080, round(im.height * 1080 / im.width)), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(0.70)
    im.save(D / "kanit_1.jpg", quality=92)
    print("kanit_1", im.size, olc(im))


def kanit_2():
    im = Image.open(D / "son_a.jpg").convert("RGB").crop((30, 45, 1890, 1060))
    im = im.resize((1080, round(im.height * 1080 / im.width)), Image.LANCZOS)
    im = ImageOps.autocontrast(im, cutoff=1)
    im = im.point(lambda v: round(255 * (v / 255) ** 0.78))   # gama: koyu külçe telefonda okunsun
    im.save(D / "kanit_2.jpg", quality=92)
    print("kanit_2", im.size, olc(im))


if __name__ == "__main__":
    arka()
    kanit_1()
    kanit_2()
