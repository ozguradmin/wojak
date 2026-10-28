"""Pera Palas 1979: arka plan ve kanıt görsellerini kaynaklardan hazırlar.

Kaynaklar (Wikimedia Commons, standart küçük resim genişlikleri 960/1280/1920 ile indirildi; /tmp/w/g altında):
  d1.jpg  File:Pera Palas Hotel eenpersoonskamer in 2004 DSCN3818.jpg  (FredTC, CC BY-SA 4.0)      -> arka plan
  c1.jpg  File:Christie at Hydro.jpg  (Daily Herald, 15.12.1926, s. 1; kamu malı)                     -> kanıt 1
  c0.jpg  File:Agatha Christie Odası.jpg  (Canerol86, CC BY-SA 4.0)                                  -> kanıt 2
Çalıştır: python episodes/pera-palas-anahtar-1979/gorsel.py
"""
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

D = Path(__file__).parent / "img"
K = Path("/tmp/w/g")


def arka():
    im = cv2.imread(str(K / "d1.jpg"))
    # kapı askısındaki çizgi film karakterli "rahatsız etmeyin" kartı: kapının kendi dokusuyla örtülür
    # (alttaki aynı kapı panelinden kopya; cv2.inpaint gri leke bırakıyordu)
    im[362:498, 698:781] = im[500:636, 698:781]
    p = Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))
    p = p.crop((300, 120, 1500, 1320)).resize((1080, 1080), Image.LANCZOS)
    p = ImageEnhance.Color(p).enhance(0.9)
    p = ImageEnhance.Brightness(p).enhance(0.98)
    p.save(D / "arka_oda.jpg", quality=92)


def kanit1():
    p = Image.open(K / "c1.jpg").convert("RGB").crop((0, 0, 800, 575))
    p = p.resize((1080, round(575 * 1080 / 800)), Image.LANCZOS)
    p = p.filter(ImageFilter.UnsharpMask(2, 60, 2))
    p = ImageOps.autocontrast(p, cutoff=(1, 0.5))
    p.save(D / "kanit_1_daily_herald_1926.jpg", quality=92)


def kanit2():
    p = Image.open(K / "c0.jpg").convert("RGB").crop((640, 300, 2140, 1200))
    p = p.resize((1080, 648), Image.LANCZOS)
    p.save(D / "kanit_2_oda_411.jpg", quality=92)


if __name__ == "__main__":
    D.mkdir(exist_ok=True)
    arka()
    kanit1()
    kanit2()
    for f in sorted(D.glob("*.jpg")):
        print(f.name, Image.open(f).size)
