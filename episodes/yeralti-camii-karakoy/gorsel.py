"""yeralti-camii-karakoy: arka plan ve kanıt görselleri.

    python episodes/yeralti-camii-karakoy/gorsel.py

Kaynaklar (img/kaynak_*.jpg, tools/commons.py indir ile 1920 px):
  kaynak_ic.jpg      "20110722 interior Yeralti Cami Karakoy Istanbul Turkey.jpg", User:Ggia, CC BY-SA 3.0
  kaynak_giris.jpg   "20110722 south entrance Yeralti Cami Karakoy Istanbul Turkey.jpg", User:Ggia, CC BY-SA 3.0
  kaynak_turbe1.jpg  "20110722 Yeralti Cami turbe Karakoy Istanbul Turkey 1.jpg", User:Ggia, CC BY-SA 3.0
                     (türbe 2 numaralı çekim yeşil neonla aşırı doygundu: hakem tur 1 MUST)
Yapılan: arka plan kare kırpım + 1080'e küçültme, renk 1,15 / parlaklık 1,32, parlak tonlar sıkıştırıldı; kanıtlar 1080 genişliğe küçültme, sıkı kırpım.
"""
from pathlib import Path

from PIL import Image, ImageEnhance

IMG = Path(__file__).resolve().parent / "img"


def arka():
    im = Image.open(IMG / "kaynak_ic.jpg").convert("RGB")
    W, H = im.size
    x0 = (W - H) // 2
    im = im.crop((x0, 0, x0 + H, H)).resize((1080, 1080), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(1.15)
    im = ImageEnhance.Brightness(im).enhance(1.32)
    # tavandaki kandil parlamasını yumuşat: 200 üstü tonları sıkıştır
    im = im.point(lambda v: v if v < 200 else 200 + (v - 200) * 0.45)
    im.save(IMG / "arka.jpg", quality=92)


def kanit(kaynak, hedef, kutu=None, renk=1.0, parlak=1.0):
    im = Image.open(IMG / kaynak).convert("RGB")
    if kutu:
        im = im.crop(kutu)
    h = round(im.height * 1080 / im.width)
    im = im.resize((1080, h), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(renk)
    im = ImageEnhance.Brightness(im).enhance(parlak)
    im.save(IMG / hedef, quality=92)
    print(hedef, im.size)


if __name__ == "__main__":
    arka()
    kanit("kaynak_giris.jpg", "kanit_1.jpg", kutu=(700, 0, 1920, 820))
    kanit("kaynak_turbe1.jpg", "kanit_2.jpg", kutu=(200, 40, 1920, 1315), renk=0.6)
