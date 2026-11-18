"""en-great-fire-hubert gorselleri:  python episodes/en-great-fire-hubert/gorsel.py
Girdiler (serbest lisans, bkz. episode.yaml sources) img/kaynak/ altinda; ciktilar img/arka.jpg, img/ev_1.jpg, img/ev_2.jpg.
  arka : Great Fire London.jpg (1675, kamu mali), 1118x1118 kare kirpim -> 1080, gece sahnesi icin gama 0,52, renk ayni
  ev_1 : Faryner plaketi (CC BY-SA 4.0, Acabashi), 1920 px kaynaktan plaketin tamami (arma + yazi) 1590 px genislik kirpim -> 1080
  ev_2 : Pepys gunlugu, Wheatley baskisi (1893) s. 195, Internet Archive 'diaryofsamuelpep06pepy' leaf n210 (w2000); ust satirlar, 1080 genislik
"""
from pathlib import Path
import numpy as np
from PIL import Image, ImageEnhance

HERE = Path(__file__).resolve().parent
K = HERE / "img/kaynak"


def arka():
    im = Image.open(K / "great_fire_1675_1920.jpg").convert("RGB")
    im = im.crop((400, 0, 400 + 1118, 1118)).resize((1080, 1080), Image.LANCZOS)
    a = np.asarray(im).astype(float) / 255
    a = np.power(a, 0.52)
    im = Image.fromarray((a * 255).astype("uint8"))
    im = ImageEnhance.Color(im).enhance(1.0)
    im.save(HERE / "img/arka.jpg", quality=92)


def ev1():
    im = Image.open(K / "faryner_plaque_1920.jpg").convert("RGB")
    c = im.crop((200, 120, 1790, 930))
    c.resize((1080, round(c.height * 1080 / c.width)), Image.LANCZOS).save(HERE / "img/ev_1.jpg", quality=93)


def ev2():
    im = Image.open(K / "pepys_vi_p195_w2000.jpg").convert("RGB")
    W = im.width
    box = (55, 150, 1825, 150 + 1010)
    c = im.crop(box)
    s = 1080 / c.width
    c = c.resize((1080, round(c.height * s)), Image.LANCZOS)
    c.save(HERE / "img/ev_2.jpg", quality=93)
    print(c.size)


if __name__ == "__main__":
    arka(); ev1(); ev2()
