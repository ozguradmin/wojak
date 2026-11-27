"""kazdagi-sarikiz: arka plan ve iki kanıt görseli.

    python episodes/kazdagi-sarikiz/gorsel.py

Kaynaklar img/kaynak_*.jpg (tools/commons.py indir ile, olduğu gibi):
  kaynak_arka.jpg            'Kazdağı 09 2005 Blockmeer.jpg', Volker Höhfeld, CC BY-SA 4.0 (1280 px küçük resim):
                             Kaz Dağı'nın yüksek kesiminde karaçam ve kaya blokları. Modern öğe yok.
  kaynak_sarikiz_tepesi.jpg  'Sarıkız (10).jpg', Alfinkedisi (2015), CC BY-SA 4.0 (1920 px): Sarıkız Tepesi'nin konisi.
                             Sağ alttaki yürüyüşçü (arkası dönük) kadraj dışında bırakılır; yamaçtaki uzak siluetler seçilmez.
  kaynak_altinoluk.jpg       'Altinoluk-form-up.jpg', İmmortalance (2014), CC0 (1920 px): Kaz Dağı'nın güney yamacından
                             aşağıda Edremit Körfezi ve Altınoluk kıyısı.
"""
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps

IMG = Path(__file__).resolve().parent / "img"


def arka():
    im = Image.open(IMG / "kaynak_arka.jpg").convert("RGB")        # 1280x859
    im = im.crop((230, 90, 999, 859)).resize((1080, 1080), Image.LANCZOS)   # tur 1 SHOULD: üst köşelerdeki beyaz gök dışarıda
    im = ImageEnhance.Color(im).enhance(0.85)
    im = ImageEnhance.Brightness(im).enhance(1.15)
    im.save(IMG / "arka.jpg", quality=92)


def kanit_1():
    im = Image.open(IMG / "kaynak_sarikiz_tepesi.jpg").convert("RGB")  # 1920x1280
    im = im.crop((160, 300, 1640, 1110))       # koni kadrajın ortasında; sağ alttaki yürüyüşçü (y > 1130) dışarıda
    im = ImageOps.autocontrast(im, cutoff=0.3)
    w = 1080
    im.resize((w, round(im.height * w / im.width)), Image.LANCZOS).save(IMG / "kanit_1.jpg", quality=92)


def kanit_2():
    im = Image.open(IMG / "kaynak_altinoluk.jpg").convert("RGB")       # 1920x1080
    # tur 1 görsel SHOULD: sisli gök çıkarıldı, deniz kadrajın yarısı; kıyı çizgisi ve öndeki çam yamaçta durulduğunu gösterir
    im = im.crop((560, 400, 1920, 1080))   # tur 2 görsel SHOULD: üstteki pus şeridi kısaltıldı
    im = ImageOps.autocontrast(im, cutoff=1.5)
    im = ImageEnhance.Contrast(im).enhance(1.12)
    im = ImageEnhance.Color(im).enhance(1.05)
    w = 1080
    im.resize((w, round(im.height * w / im.width)), Image.LANCZOS).save(IMG / "kanit_2.jpg", quality=92)


if __name__ == "__main__":
    arka()
    kanit_1()
    kanit_2()
    for f in ("arka.jpg", "kanit_1.jpg", "kanit_2.jpg"):
        print(f, Image.open(IMG / f).size)
