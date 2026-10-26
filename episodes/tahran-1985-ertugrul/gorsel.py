"""tahran-1985-ertugrul: arka plan ve kanıt görsellerini Commons dosyalarından hazırlar (piksellere ekleme yok).

    python episodes/tahran-1985-ertugrul/gorsel.py <indirme_klasoru>

Girdi (indirme klasöründe; Commons, lisanslar episode.yaml `sources`'ta):
  bg_mehrabad1971.jpg  "Mehrabad-1971.jpg" (Land of Kings, Tahran 1971; {{PD-Art|PD-Iran}}), 1320x908
  e1_voyage.jpg        "Voyage of frigate Ertugrul to Japan by Commodore Mirliva Nuri 1839 1906.jpg"
                       (Osman Nuri Paşa, 1891-1906, İstanbul Deniz Müzesi; PD-old-100 / PD-Turkey), 1852x1516
  e2_cenaze.jpg        "Cérémonie funéraire Ertugrul.jpg" (1890, fotoğrafçı bilinmiyor; {{PD-Japan-oldphoto}}), 6266x4769
Çıktı: img/arka_mehrabad.jpg (1080x1080), img/kanit_1_ertugrul.jpg (1080x814), img/kanit_2_cenaze.jpg (1080x815)
"""
import sys
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps

HERE = Path(__file__).resolve().parent
SRC = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
OUT = HERE / "img"


def arka():
    im = Image.open(SRC / "bg_mehrabad1971.jpg").convert("RGB")
    # Mehrabad (Tahran) apronu: Iran Air 707'nin burnu, yer araçları, arkada terminal ve kule. Kare kırpım, 1,19x büyütme
    im = im.crop((300, 0, 1208, 908)).resize((1080, 1080), Image.LANCZOS)
    # renk: basılı kitap taraması; doygunluk ~0,31 -> ~0,21 (hakem 1: 0,23 yüksek), parlaklık ~136 -> ~123 (orijinallerin diyalog karesi 121 / 0,20)
    im = ImageEnhance.Brightness(ImageEnhance.Color(im).enhance(0.62)).enhance(0.9)
    im.save(OUT / "arka_mehrabad.jpg", quality=92)


def kanit1():
    im = Image.open(SRC / "e1_voyage.jpg").convert("RGB")
    # Osman Nuri Paşa'nın tablosu: Osmanlı sancaklı Ertuğrul fırtınalı denizde. Gemi ve dalgalar kadrajda, gökyüzü kısaltıldı
    im.crop((140, 560, 1440, 1540)).resize((1080, 814), Image.LANCZOS).save(OUT / "kanit_1_ertugrul.jpg", quality=92)


def kanit2():
    im = Image.open(SRC / "e2_cenaze.jpg").convert("RGB")
    # Japonya'da Ertuğrul kazazedeleri için tören: yapraklı torii kapısında ay-yıldızlı Osmanlı bayrağı, yanda
    # "土耳其軍艦遭難者兆域" (Türk savaş gemisi kazazedelerinin mezarlığı) direği, Japon subaylar ve halk.
    im = im.crop((738, 539, 5622, 4225)).resize((1080, 815), Image.LANCZOS)
    # soluk sepya baskı: siyah ve beyaz noktayı ger (yüzdelik), ton değişmez
    im = ImageOps.autocontrast(im, cutoff=(1, 0.5))
    im.save(OUT / "kanit_2_cenaze.jpg", quality=92)


if __name__ == "__main__":
    arka()
    kanit1()
    kanit2()
    print("img/ hazır")
