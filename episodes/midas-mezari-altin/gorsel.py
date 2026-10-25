"""midas-mezari-altin: arka plan ve kanıt görsellerini Commons dosyalarından hazırlar (piksellere ekleme yok).

    python episodes/midas-mezari-altin/gorsel.py <indirme_klasoru>

Girdi (indirme klasöründe; Commons, lisanslar episode.yaml `sources`'ta):
  bg_tumulus.jpg  "Gordion Midas mound (1993).jpg" (Mark Landon, CC BY 4.0), 4715x3084
  e1_oda.jpg      "Tumulus of King Midas 03.jpg" (Carole Raddato, CC BY-SA 2.0), 4879x3239
  e2_kazan.jpg    "Museum of Anatolian Civilizations Phrygian Smaller sirens' cauldron in 2019 06.jpg"
                  (Dosseman, CC BY-SA 4.0; 3840 px sürüm), 3840x2560
Çıktı: img/arka_tumulus.jpg (1080x1080), img/kanit_1_mezar_odasi.jpg (1080x810), img/kanit_2_bronz_kazan.jpg (1080x803)
"""
import sys
from pathlib import Path

from PIL import Image, ImageEnhance

HERE = Path(__file__).resolve().parent
SRC = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
OUT = HERE / "img"


def arka():
    im = Image.open(SRC / "bg_tumulus.jpg").convert("RGB")
    # Midas Tümülüsü 1993'te (bugünkü giriş yapısı ve yürüme yolu yok): tepe karenin ortasında, önde bozkır
    im = im.crop((900, 150, 3600, 2850)).resize((1080, 1080), Image.LANCZOS)
    # renk düzeltme: doygunluk 0,36 -> ~0,27, parlaklık 134 -> ~124 (orijinallerin diyalog karesi 121 / 0,20)
    im = ImageEnhance.Brightness(ImageEnhance.Color(im).enhance(0.75)).enhance(0.93)
    im.save(OUT / "arka_tumulus.jpg", quality=92)


def kanit1():
    im = Image.open(SRC / "e1_oda.jpg").convert("RGB")
    # mezar odasının ardıç/çam kütüklerden duvarı ve açılan girişi; sol üstteki modern çelik bağlantı kadraj dışı
    im.crop((813, 244, 4607, 3090)).resize((1080, 810), Image.LANCZOS).save(OUT / "kanit_1_mezar_odasi.jpg", quality=92)


def kanit2():
    im = Image.open(SRC / "e2_kazan.jpg").convert("RGB")
    # tümülüsten çıkan sirenli bronz kazan, içi bronz kaselerle dolu (Anadolu Medeniyetleri Müzesi)
    im.crop((512, 107, 3755, 2517)).resize((1080, 803), Image.LANCZOS).save(OUT / "kanit_2_bronz_kazan.jpg", quality=92)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    arka()
    kanit1()
    kanit2()
    for p in sorted(OUT.glob("*.jpg")):
        print(p.name, Image.open(p).size)
