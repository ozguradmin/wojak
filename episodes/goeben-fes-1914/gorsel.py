"""goeben-fes-1914: arka plan ve kanıt görsellerini kaynak dosyalardan üretir.

    python episodes/goeben-fes-1914/gorsel.py <kaynak_klasoru>

Kaynak klasöründe (repoya girmez; lisanslar episode.yaml sources'ta):
  texas_deck.jpg        Commons 'Battleship Texas on deck July 2017.jpg' (CC BY-SA 4.0), 1920 px küçük resim
  fesli_subaylar.jpg    Commons 'German & Turkish officers of the "Goeben".jpg' (Underwood & Underwood fotoğrafı,
                        Morgenthau 1918; tarama Jay Dobkin, CC BY-SA 2.0), 1709x2925
  nyt_1914_08_13_s1.jpg Internet Archive per_new-york-times-magazine_the-new-york-times_1914-08-13_63_20655, sayfa 1
                        (page/n0_w4000.jpg, 6889x8561; kamu malı, Commons'ta da var)
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

Image.MAX_IMAGE_PIXELS = None
HERE = Path(__file__).resolve().parent
IMG = HERE / "img"


def arka(src):
    im = Image.open(src).convert("RGB")
    c = im.crop((300, 900, 1860, 2460))
    # güvertedeki turuncu uzatma kablosu (modern): ton maskesi + inpaint ile güverte rengine
    a = np.array(c)
    for esik_g, esik_b in [(18, 30), (8, 16)]:
        r, g, b = [a[..., i].astype(int) for i in range(3)]
        kablo = ((r > g + esik_g) & (r > b + esik_b)).astype(np.uint8) * 255
        kablo[: int(c.height * 0.55)] = 0
        kablo = cv2.dilate(kablo, np.ones((5, 5), np.uint8), iterations=3)
        # dokuyu koru: maskeli pikseli 34 px sağdaki (aynı tahta sırasındaki) güverte pikselinden kopyala, kenarı yumuşat
        m = kablo > 0
        kay = np.roll(a, -34, axis=1)
        kay_m = np.roll(m, -34, axis=1)
        kay[kay_m] = np.roll(a, 34, axis=1)[kay_m]  # sağdaki de kabloysa soldakini al
        yumus = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 2.0)[..., None]
        yumus = np.clip(yumus * 1.6, 0, 1)
        a = (a * (1 - yumus) + kay * yumus).astype(np.uint8)
    c = Image.fromarray(a).resize((1080, 1080), Image.LANCZOS)
    c = ImageEnhance.Brightness(c).enhance(1.12)
    c = ImageEnhance.Color(c).enhance(1.15)
    c.save(IMG / "arka_guverte.jpg", quality=93)


def kanit1(src):
    """Fesli Alman ve Türk subaylar, Goeben güvertesi (1914). Festen bele, altı subay; altyazı ve © satırı dışarıda."""
    im = Image.open(src).convert("RGB")
    c = im.crop((72, 330, 1540, 1150)).resize((1080, 603), Image.LANCZOS)
    c = ImageOps.autocontrast(c, cutoff=(0.5, 0.5))
    c = c.filter(ImageFilter.UnsharpMask(1.2, 50, 2))
    c.save(IMG / "kanit_1_fesli_subaylar.jpg", quality=93)


def kanit2(src):
    """NYT 13 Ağustos 1914, s. 1: "CRUISER GOEBEN SOLD TO TURKEY?" sütun başlığı (komşu sütunlardan birer şerit)."""
    im = Image.open(src).convert("RGB")
    x0, y0, x1 = 2560, 3655, 3530
    s = 1080 / (x1 - x0)
    y1 = y0 + round(780 / s)
    c = im.crop((x0, y0, x1, y1)).resize((1080, 780), Image.LANCZOS)
    c = ImageOps.autocontrast(c.convert("L"), cutoff=(0.5, 1.0)).convert("RGB")
    c.save(IMG / "kanit_2_nyt_1914.jpg", quality=93)


if __name__ == "__main__":
    k = Path(sys.argv[1])
    IMG.mkdir(exist_ok=True)
    arka(k / "texas_deck.jpg")
    kanit1(k / "fesli_subaylar.jpg")
    kanit2(k / "nyt_1914_08_13_s1.jpg")
    for f in sorted(IMG.glob("*.jpg")):
        print(f.name, Image.open(f).size)
