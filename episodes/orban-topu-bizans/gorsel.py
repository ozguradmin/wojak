"""orban-topu-bizans: arka plan ve kanıt görselleri (kaynaklar Commons'tan indirilir, git'e yalnız çıktılar girer).

    python episodes/orban-topu-bizans/gorsel.py <indirilenlerin klasörü>

Girdiler (klasörde):
  tekfur.jpg   'Palace of Porphyrogenitus 2007 016.jpg' (Gryffindor, 2007, {{PD-self}}), özgün 1600x1200
  top2018.jpg  'Istanbul Military Museum Bronze cannon from the time of Mehmet the Conqueror in 2018 08 006.jpg'
               (Dosseman, CC BY-SA 4.0), 3840 px küçük resim (3840x2614)
  zonaro.jpg   'Conquest of Constantinople, Zonaro.jpg' (Fausto Zonaro, 1903, {{PD-old}}), özgün 1600x1112
"""
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
SRC = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
OUT = HERE / "img"


def arka():
    im = Image.open(SRC / "tekfur.jpg").convert("RGB")
    # inşaat blokları, tuğla yığını, mavi varil (y > 1060) ve iki yandaki iskele/merdiven kadraj dışında
    im = im.crop((300, 20, 1300, 1020)).resize((1080, 1080), Image.LANCZOS)
    im.save(OUT / "arka_tekfur.jpg", quality=92)


def kanit1():
    im = Image.open(SRC / "top2018.jpg").convert("RGB")
    im = im.crop((438, 850, 3840, 2614)).resize((1080, 560), Image.LANCZOS)
    im.save(OUT / "kanit_1_top.jpg", quality=92)


def kanit2():
    im = Image.open(SRC / "zonaro.jpg").convert("RGB")
    im = im.crop((240, 290, 1600, 1060)).resize((1080, 611), Image.LANCZOS)
    im.save(OUT / "kanit_2_zonaro.jpg", quality=92)


if __name__ == "__main__":
    arka(); kanit1(); kanit2()
    for f in sorted(OUT.glob("*.jpg")):
        print(f.name, Image.open(f).size)
