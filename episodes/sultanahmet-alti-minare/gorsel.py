"""Arka plan ve kanıt görselleri: python episodes/sultanahmet-alti-minare/gorsel.py
arka.jpg    <- img/kaynak/arka_divan.jpg (Dosseman, Topkapı Kubbealtı / Divan-ı Hümayun, CC BY-SA 4.0): merkezden kare
               kırpım, 1080'e küçültme, renk ve parlaklık ayarı.
kanit_1.jpg <- img/kaynak/ahmed_met.jpg (Met Museum 450516, I. Ahmed portresi, erken 17. yy, CC0): 1080x816 kırpım
               (kavuk, yüz, gövde; mavi albüm kenarı dışarıda).
kanit_2.jpg <- img/kaynak/cami_abdullah.jpg (Abdullah Frères, ~1880, LOC 2003677072, PD-old-70-1923): 1080x769 kırpım
               (altı minarenin hepsi; karton kenarı ve alttaki el yazısı damga dışarıda), hafif autocontrast.
Sonda ölçüler yazılır: parlaklık, doygunluk, Laplace varyansı (720 ölçeğinde).
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

D = Path(__file__).parent / "img"
K = D / "kaynak"


def olc(path):
    im = Image.open(path).convert("RGB")
    a = np.asarray(im.convert("L"), dtype=np.float32)
    hsv = np.asarray(im.convert("HSV"), dtype=np.float32) / 255
    k = im.resize((720, round(720 * im.height / im.width))).convert("L")
    lap = np.asarray(k.filter(ImageFilter.Kernel((3, 3), (0, 1, 0, 1, -4, 1, 0, 1, 0), 1, 128)), dtype=np.float32)
    print(f"{path.name}: {im.size} parlaklık {a.mean():.0f} doygunluk {hsv[..., 1].mean():.2f} laplace {lap.var():.0f}")


def arka(br=1.25, co=0.90):
    im = Image.open(K / "arka_divan.jpg").convert("RGB")
    w, h = im.size
    x0 = (w - h) // 2
    c = im.crop((x0, 0, x0 + h, h)).resize((1080, 1080), Image.LANCZOS)
    c = ImageEnhance.Brightness(c).enhance(br)
    c = ImageEnhance.Color(c).enhance(co)
    c.save(D / "arka.jpg", quality=92)


def kanit_1():
    im = Image.open(K / "ahmed_met.jpg").convert("RGB")
    c = im.crop((160, 390, 900, 390 + 559)).resize((1080, 816), Image.LANCZOS)
    c.save(D / "kanit_1.jpg", quality=92)


def kanit_2():
    im = Image.open(K / "cami_abdullah.jpg").convert("RGB")
    c = im.crop((44, 40, 44 + 1832, 40 + 1304)).resize((1080, 769), Image.LANCZOS)
    c = ImageOps.autocontrast(c, cutoff=0.3)
    c.save(D / "kanit_2.jpg", quality=92)


if __name__ == "__main__":
    arka()
    kanit_1()
    kanit_2()
    for n in ("arka.jpg", "kanit_1.jpg", "kanit_2.jpg"):
        olc(D / n)
