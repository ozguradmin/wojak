"""karakoy-tunel-1874: arka plan ve kanıt görsellerini kaynak dosyalardan üretir.

    python episodes/karakoy-tunel-1874/gorsel.py <kaynak_klasoru>

Kaynak klasöründe (repoya girmez; Commons'tan indirilir, lisanslar episode.yaml sources'ta):
  vagon_p05.jpg     'Istambul - Tünel Carriage in the Rahmi M. Koç Museum - 2026-03 - p05.jpg' (CC0), 3840 px küçük resim
  gavand_profil.jpg 'Chemin de fer métropolitain de Constantinople.jpg' (Gavand 1876, kamu malı), 1920 px küçük resim
  pera_1884.jpg     'Tunnel Station, Pera, İstanbul (12968079504).jpg' (B. Kargopoulo 1884, SALT), 1920 px küçük resim
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

HERE = Path(__file__).resolve().parent
IMG = HERE / "img"


def arka(src):
    im = Image.open(src).convert("RGB")
    c = im.crop((625, 694, 1771, 1840)).resize((1080, 1080), Image.LANCZOS)
    # camdaki mavi tabela yansımasını (modern) nötrle: mavi tonlu piksellerin doygunluğunu düşür
    hsv = np.array(c.convert("HSV")).astype(np.float32)
    mavi = (hsv[..., 0] > 125) & (hsv[..., 0] < 185) & (hsv[..., 1] > 60)
    hsv[..., 1][mavi] *= 0.25
    c = Image.fromarray(hsv.astype(np.uint8), "HSV").convert("RGB")
    c = ImageEnhance.Brightness(ImageEnhance.Color(c).enhance(0.85)).enhance(0.92)
    c.save(IMG / "arka_vagon.jpg", quality=93)


def kanit1(src):
    im = Image.open(src).convert("RGB")
    c = im.crop((470, 30, 1370, 486)).resize((1080, 547), Image.LANCZOS)
    c = c.filter(ImageFilter.UnsharpMask(1.5, 60, 2))
    c = ImageOps.autocontrast(c, cutoff=(1.5, 0.3))
    # çizgileri telefonda okunur yap: koyu tonları koyulaştır (gama), kâğıt beyazı kalsın
    c = c.point(lambda v: int(255 * (v / 255) ** 1.8))
    c = ImageEnhance.Color(c).enhance(0.6)
    c = ImageOps.autocontrast(c, cutoff=(0.3, 20.0))  # kâğıt beyazı >= 243
    c.save(IMG / "kanit_1_gavand.jpg", quality=93)


def kanit2(src):
    im = Image.open(src).convert("RGB")
    c = im.crop((0, 170, 1920, 1521)).resize((1080, 760), Image.LANCZOS)
    c = ImageOps.autocontrast(c, cutoff=(0.5, 0.3))
    c.save(IMG / "kanit_2_istasyon_1884.jpg", quality=93)


if __name__ == "__main__":
    k = Path(sys.argv[1])
    arka(k / "vagon_p05.jpg")
    kanit1(k / "gavand_profil.jpg")
    kanit2(k / "pera_1884.jpg")
    print("-> img/arka_vagon.jpg, img/kanit_1_gavand.jpg, img/kanit_2_istasyon_1884.jpg")
