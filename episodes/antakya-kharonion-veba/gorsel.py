"""antakya-kharonion-veba: arka plan ve iki kanıt görseli.

    python episodes/antakya-kharonion-veba/gorsel.py

Kaynaklar img/kaynak_*.jpg (tools/commons.py indir ve archive.org page/n<leaf>_w2000 ile indirildiği gibi):
  kaynak_arka.jpg       'Antakya Church of St. Peter exterior ın 2025 05.jpg', Dosseman, CC BY-SA 4.0 (1280 px küçük resim).
                        Yalnız kilise cephesinin ÜSTÜNDEKİ Staurin Dağı kaya yüzü kırpılır (cephe, lamba, ağaç kadraj dışı).
  kaynak_malalas_205.jpg Ioannis Malalae Chronographia, ed. L. Dindorf (Bonn, 1831), s. 205 (Kitap VIII, 8.21 pasajı);
                        Internet Archive 'ioannismalalaec00malagoog' leaf 287 (_w2000), kamu malı (NOT_IN_COPYRIGHT).
  kaynak_kharonion.jpg  'The so-called Charonion, a carved stone bust on the mountainside above Antioch, ...
                        (35430722713).jpg', Carole Raddato, CC BY-SA 2.0 (1920 px küçük resim). Baş ve omuz; graffiti dışarıda.
"""
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps

HERE = Path(__file__).resolve().parent
SRC = HERE / "img"
IMG = HERE / "img"


def arka():
    im = Image.open(SRC / "kaynak_arka.jpg").convert("RGB")
    im = im.crop((110, 0, 970, 860)).resize((1080, 1080), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(1.45)
    im = ImageEnhance.Brightness(im).enhance(1.03)
    im.save(IMG / "arka.jpg", quality=92)


def kanit_1():
    im = Image.open(SRC / "kaynak_malalas_205.jpg").convert("L")     # 2790x5084
    im = im.crop((100, 555, 2412, 2116))                        # sayfa başlığı + 8.21 pasajı (Ἐπὶ δὲ ... Χαρώνιον.)
    im = ImageOps.autocontrast(im, cutoff=0.5)
    w = 1080
    h = round(im.height * w / im.width)
    im.resize((w, h), Image.LANCZOS).convert("RGB").save(IMG / "kanit_1.jpg", quality=92)


def kanit_2():
    im = Image.open(SRC / "kaynak_kharonion.jpg").convert("RGB")      # 1920x2899
    im = im.crop((380, 470, 1720, 1483))                 # başlık (örtülü baş) kadrajın ~%75'i; omuz altı ve boya yazısı dışarıda
    im = ImageOps.autocontrast(im, cutoff=0.3)
    im.resize((1080, 816), Image.LANCZOS).save(IMG / "kanit_2.jpg", quality=92)


if __name__ == "__main__":
    arka()
    kanit_1()
    kanit_2()
    for f in ("arka.jpg", "kanit_1.jpg", "kanit_2.jpg"):
        print(f, Image.open(IMG / f).size)
