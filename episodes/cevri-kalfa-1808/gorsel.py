"""cevri-kalfa-1808: arka plan ve kanıt görsellerini kaynaklardan üretir.

    python episodes/cevri-kalfa-1808/gorsel.py

Kaynaklar (img/kaynak/; hepsi Wikimedia Commons, lisanslar episode.yaml sources'ta):
  hunkar_sofasi.jpg  "Sultan's Throne, Imperial Hall, Topkapı Palace Harem.jpg", Julian Lupyan, CC0 (1920 px küçük resim)
  mahmud_orj.jpg     "Mahmud II.jpg", Henri-Guillaume Schlesinger, 1839, kamu malı (özgün 1503x2000)
"""
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps

HERE = Path(__file__).resolve().parent
K = HERE / "img" / "kaynak"
OUT = HERE / "img"


def arka():
    im = Image.open(K / "hunkar_sofasi.jpg").convert("RGB")
    im = im.crop((320, 0, 1600, 1280)).resize((1080, 1080), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(0.48)
    im = ImageEnhance.Brightness(im).enhance(1.24)
    im.save(OUT / "arka.jpg", quality=92)


def kanit_1():
    """II. Mahmud portresi: yüz ve göğüs, 1080x816 (1,5x)."""
    im = Image.open(K / "mahmud_orj.jpg").convert("RGB")
    x0, y0, w = 398, 333, 720
    im = im.crop((x0, y0, x0 + w, y0 + round(w * 816 / 1080))).resize((1080, 816), Image.LANCZOS)
    im.save(OUT / "kanit_1.jpg", quality=92)


if __name__ == "__main__":
    arka()
    kanit_1()
    print("arka.jpg, kanit_1.jpg yazıldı (kanit_2.jpg: kupur.py)")
