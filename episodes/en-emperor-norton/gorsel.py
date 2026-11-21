"""en-emperor-norton gorselleri:  python episodes/en-emperor-norton/gorsel.py
Girdiler (kamu malı, bkz. episode.yaml sources) img/kaynak/ altında; çıktılar img/arka.jpg, img/ev_1.jpg, img/ev_2.jpg.
  arka : Montgomery Block, 1862 (Fardon, PD-old-100) 1280x980 -> kenar paspartusu atılır, kare kırpım -> 1080, renk 0,75
  ev_1 : Norton I Bradley & Rulofson Portrait (PD-US-expired) 1920x3101 -> bas-govde 1080x816 kirpim
  ev_2 : Emperor Norton 50 cent note WFHM SF (BrokenSphere, CC BY-SA 3.0) 1920x916 -> kenarlar dahil 1080x~544, autocontrast (son kare)
"""
from pathlib import Path
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

HERE = Path(__file__).resolve().parent
K = HERE / "img/kaynak"
BOX = (140, 35, 1050, 945)


def arka(box=BOX):
    im = Image.open(K / "arka_montgomery.jpg").convert("RGB").crop(box).resize((1080, 1080), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(0.9)
    im = ImageEnhance.Brightness(im).enhance(0.88)
    im.save(HERE / "img/arka.jpg", quality=92)


def ev1(box=(343, 412, 1767, 412 + 1076)):
    im = Image.open(K / "kanit_bradley_hi.jpg").convert("RGB").crop(box).resize((1080, 816), Image.LANCZOS)
    im.save(HERE / "img/ev_1.jpg", quality=93)


def ev2(box=(50, 0, 1870, 916)):
    im = Image.open(K / "kanit_scrip50.jpg").convert("RGB").crop(box)
    im = im.resize((1080, round(im.height * 1080 / im.width)), Image.LANCZOS)
    im = ImageOps.autocontrast(im, cutoff=0.5)      # soluk taramada yalniz autocontrast
    im = ImageEnhance.Color(im).enhance(0.75)       # turuncu renk dokumu icin (hakem SHOULD)
    im.save(HERE / "img/ev_2.jpg", quality=93)


def stats():
    for n in ["arka", "ev_1", "ev_2"]:
        im = Image.open(HERE / f"img/{n}.jpg")
        hsv = np.asarray(im.convert("HSV")).astype(float)
        g = np.asarray(im.convert("L").resize((720, round(720 * im.height / im.width)))).astype(float)
        lap = g[1:-1, 1:-1] * 4 - g[:-2, 1:-1] - g[2:, 1:-1] - g[1:-1, :-2] - g[1:-1, 2:]
        print(n, im.size, "parlaklik %.0f doygunluk %.2f laplace %.0f" % (np.asarray(im.convert("L")).mean(), hsv[..., 1].mean() / 255, lap.var()))


if __name__ == "__main__":
    arka(); ev1(); ev2(); stats()
