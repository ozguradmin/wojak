"""hezarfen-galata-ucusu: arka plan ve kanıt görsellerini Commons dosyalarından hazırlar (piksellere ekleme yok).

    python episodes/hezarfen-galata-ucusu/gorsel.py <indirme_klasoru>

Girdi (indirme klasöründe; Commons, lisanslar episode.yaml `sources`'ta):
  bg_harem.jpg  "Galata Tower from the Harem - 2014.10.23 (1).JPG" (Derzsi Elekes Andor, CC BY-SA 4.0; 3840 px sürüm)
  e1_c.jpg      "View of Topkapı Palace from the Galata Tower, Istanbul, Turkey 001 cropped.jpg" (Moonik, CC BY-SA 3.0)
  stamp.jpg     "Hezarfen Ahmed Çelebi.jpg" (Türkiye Cumhuriyeti Postaları, 1950; PD-TR), 319x493
Çıktı: img/arka_galata_harem.jpg (1080x1080), img/kanit_1_sarayburnu.jpg (1080x702), img/kanit_2_pul.jpg (1080x816)
"""
import sys
from pathlib import Path

from PIL import Image, ImageFilter

HERE = Path(__file__).resolve().parent
SRC = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
OUT = HERE / "img"


def arka():
    im = Image.open(SRC / "bg_harem.jpg").convert("RGB")     # 3840x2880
    # Topkapı Sarayı Harem'inden Galata Kulesi: kule üst ortada, solda saray bahçesinin ağacı, sağdaki Harem bacası kadraj dışında
    im.crop((360, 0, 3240, 2880)).resize((1080, 1080), Image.LANCZOS).save(OUT / "arka_galata_harem.jpg", quality=92)


def kanit1():
    im = Image.open(SRC / "e1_c.jpg").convert("RGB")         # 2802x1885
    # Galata Kulesi'nden Sarayburnu: Topkapı Sarayı, Adalet Kulesi, arkada Boğaz ve Anadolu yakası
    im.crop((700, 120, 2700, 1420)).resize((1080, 702), Image.LANCZOS).save(OUT / "kanit_1_sarayburnu.jpg", quality=92)


def kanit2():
    im = Image.open(SRC / "stamp.jpg").convert("RGB")        # 319x493
    # pulun üst kısmı tam genişlikte: ICAO 1950 başlığı, 20 kuruş, kanatlı adam ve Galata Kulesi; iki yanda dişler
    h = round(319 * 816 / 1080)
    c = im.crop((0, 22, 319, 22 + h)).resize((1080, 816), Image.LANCZOS)
    c = c.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))
    c.save(OUT / "kanit_2_pul.jpg", quality=94)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    arka()
    kanit1()
    kanit2()
    for f in sorted(OUT.glob("*.jpg")):
        print(f.relative_to(HERE), Image.open(f).size)
