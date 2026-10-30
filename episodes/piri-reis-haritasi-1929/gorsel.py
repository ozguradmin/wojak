"""Piri Reis haritası görselleri: arka plan + iki kanıt (Commons). Çalıştır: python episodes/piri-reis-haritasi-1929/gorsel.py

Ham dosyalar img/kaynak/ altında (tools/commons.py indir ile iner; betik indirmez):
arka_1.jpg      : 'Topkapı Library of Ahmed III Interior general view in 2006 16 1206.jpg' (Dosseman, CC BY-SA 4.0) -> img/arka.jpg
kolomb_piombo.jpg: 'Portrait of a Man, Said to be Christopher Columbus.jpg' (Sebastiano del Piombo 1519, Met 437645;
                  {{PD-Art|PD-old-auto-expired}} + {{cc-zero}}) -> img/kanit_1.jpg
piri_1513.jpg   : 'Piri reis world map 01.jpg' (Piri Reis 1513; {{PD-Art|PD-old-auto-expired}}) -> img/kanit_2.jpg (son kare:
                  haritanın üst yarısı: Antiller, İber ve Batı Afrika kıyısı)
Not: 'Piri Reis - Oval World Map - Google Art Project.jpg' 1513 haritası DEĞİL, Walters W.658 fol. 41a (17. yy kopya Kitab-ı Bahriye).
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

D = Path(__file__).parent / "img"
K = D / "kaynak"


def olc(im):
    a = np.asarray(im.convert("HSV")).astype(float) / 255
    return round(float(np.asarray(im.convert("L")).mean()), 1), round(float(a[..., 1].mean()), 3)


def laplas(im, blur=0.0):
    """wojak/denetim.py arka_plan_olcu ile aynı: 720 ölçeği, üst şerit + iki yan şerit (kenar Laplace varyansı)."""
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    g = np.asarray(im.resize((720, 720), Image.LANCZOS).convert("L"), dtype=float)
    lap = lambda a: (a[:-2, 1:-1] + a[2:, 1:-1] + a[1:-1, :-2] + a[1:-1, 2:] - 4 * a[1:-1, 1:-1]).var()
    return round(float(np.mean([lap(g[:150]), lap(g[:, :150]), lap(g[:, 570:])])), 1)


def arka():
    # 1920x1275 ham; kare kırpım sütunun solunda biter (yarım sütun yok), sol: kapı + sedir, sağ: kapı + hasır
    im = Image.open(K / "arka_1.jpg").convert("RGB").crop((0, 190, 1085, 1275)).resize((1080, 1080), Image.LANCZOS)
    im = ImageEnhance.Brightness(im).enhance(1.10)   # tur 1 SHOULD: 1,16 pencereleri patlatıyordu (1,05 tüm karede 107 veriyordu)
    im = ImageEnhance.Color(im).enhance(1.12)        # tur 1 SHOULD: üst bölge doygunluğu 0,10 -> ~0,12
    im.save(D / "arka.jpg", quality=92)
    print("arka", olc(im), "Laplace blur'suz", laplas(im), "blur 2.5:", laplas(im, 2.5), "blur 2.7:", laplas(im, 2.7))


def kanit_1():
    # Sebastiano del Piombo, 'Portrait of a Man, Said to be Christopher Columbus' (1519, Met 437645; PD-Art + CC0).
    # Yatay kırpım: üstteki Latince yazıt (Kolomb'u adıyla anar), baş, göğüs ve el. Ham 1280x1549.
    im = Image.open(K / "kolomb_piombo.jpg").convert("RGB").crop((0, 0, 1280, 967))
    im = im.resize((1080, 816), Image.LANCZOS)
    im.save(D / "kanit_1.jpg", quality=92)
    print("kanit_1", im.size, olc(im))


def kanit_2():
    # SON KARE: 1513 haritasının üst yarısı, geniş kadraj (görsel hakem tur 1 SHOULD: tanınırlık). Solda Antiller ve Hispaniola,
    # sağda İber ve Batı Afrika kıyısı, ortada pusula gülü ve gemiler; sol altta Kolomb'u anan kenar notu V'in başladığı yazı bloğu.
    im = Image.open(K / "piri_1513.jpg").convert("RGB").crop((20, 100, 1820, 1460))
    im = im.resize((1080, 816), Image.LANCZOS)
    im.save(D / "kanit_2.jpg", quality=92)
    print("kanit_2", im.size, olc(im))


if __name__ == "__main__":
    arka()
    kanit_1()
    kanit_2()
