"""sokullu-son-dua-1579: arka plan ve kanıt görselleri.

    python episodes/sokullu-son-dua-1579/gorsel.py

Kaynaklar (img/*_aday1.jpg, tools/commons.py indir ile):
  arka_aday1.jpg     "Sokollu Mehmed Pasha Mosque DSCF4409.jpg", R Prazeres, CC BY-SA 4.0 (Kadırga, avlu ve şadırvan)
  kanit_1_aday1.jpg  "Sokollu Mehmet Paşa Мехмед-паша Соколовић 1603.jpg", Jacob Schrenck von Notzing'in 1603 kitabı
                     (Polona taraması), kamu malı
  kanit_2_aday1.jpg  "Fol. 254a. The murder of Sultan Murad I (cropped), Iskender-name by Ahmedi, late 15th century
                     (National Library of Russia, C133).jpg", bilinmeyen sanatçı, kamu malı
Yapılan: arka plan kare kırpım (kemerlerdeki iki projektör dışarıda) + 1080'e küçültme, renk/parlaklık; kanıtlar sıkı
kırpım + 1080 genişlik.
"""
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps

IMG = Path(__file__).resolve().parent / "img"


def arka():
    im = Image.open(IMG / "arka_aday1.jpg").convert("RGB")
    im = im.crop((320, 120, 1640, 1440)).resize((1080, 1080), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(0.85)
    im = ImageEnhance.Brightness(im).enhance(0.97)
    im.save(IMG / "arka.jpg", quality=92)


def kanit(kaynak, hedef, kutu, renk=1.0, parlak=1.0, oto=False):
    im = Image.open(IMG / kaynak).convert("RGB").crop(kutu)
    if oto:
        im = ImageOps.autocontrast(im, cutoff=0.5)
    h = round(im.height * 1080 / im.width)
    im = im.resize((1080, h), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(renk)
    im = ImageEnhance.Brightness(im).enhance(parlak)
    im.save(IMG / hedef, quality=92)
    print(hedef, im.size)


if __name__ == "__main__":
    arka()
    # gravür: sarık, yüz, göğüs; süslü çerçeve dışarıda (770x582 -> 1080x817, 1,4x)
    kanit("kanit_1_aday1.jpg", "kanit_1.jpg", (600, 560, 1370, 1142), oto=True)
    # minyatür: elinde kâğıtla eğilerek yaklaşan adam, kılıç + I. Murad (988x746 -> 1080x816, 1,09x; Murad'ın başı içeride, sol kenar şeridi dışarıda)
    kanit("kanit_2_aday1.jpg", "kanit_2.jpg", (12, 175, 1000, 921))
