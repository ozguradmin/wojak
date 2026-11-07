"""edirne-sarayi-1878: arka plan ve kanıt görselleri (kaynaklar img/kaynak_*.jpg, Wikimedia Commons; lisanslar episode.yaml sources).

    python episodes/edirne-sarayi-1878/gorsel.py
"""
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps

IMG = Path(__file__).resolve().parent / "img"


def arka():
    # Adalet Kasrı (Kasr-ı Adalet), Edirne Sarayı'nın bugüne ulaşan yapısı; kare kırpım: kulenin tepesi dahil,
    # alttaki grafiti, gölgelik, bayraklar ve yol kadraj dışında
    im = Image.open(IMG / "kaynak_arka4.jpg").convert("RGB").crop((0, 330, 1920, 2250))
    im = im.resize((1080, 1080), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(0.70)
    im = ImageEnhance.Brightness(im).enhance(0.86)
    im.save(IMG / "arka.jpg", quality=92)


def kanit_1():
    # Sayger & Desarnod taşbaskısı 'Palais du Sultan à Eski-serai près d'Andrinople' (1829-30 gezisi, 1834): saraya sıkı kırpım
    im = Image.open(IMG / "kaynak_tasbaski.jpg").convert("RGB").crop((300, 200, 1000, 630))
    im = ImageOps.autocontrast(im, cutoff=1).point(lambda v: round(255 * (v / 255) ** 1.15))
    im = im.resize((1080, round(1080 * im.height / im.width)), Image.LANCZOS)
    im.save(IMG / "kanit_1.jpg", quality=92)


def kanit_2():
    # Cihannüma Kasrı kalıntısı (2015)
    im = Image.open(IMG / "kaynak_cihannuma.jpg").convert("RGB").crop((400, 30, 1760, 1000))
    im = im.resize((1080, round(1080 * im.height / im.width)), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(0.85)
    im.save(IMG / "kanit_2.jpg", quality=92)


if __name__ == "__main__":
    arka(); kanit_1(); kanit_2()
    for f in ("arka.jpg", "kanit_1.jpg", "kanit_2.jpg"):
        print(f, Image.open(IMG / f).size)
