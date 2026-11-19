"""en-caesar-pirates gorselleri:  python episodes/en-caesar-pirates/gorsel.py
Girdiler (serbest lisans, bkz. episode.yaml sources) img/kaynak/ altinda; ciktilar img/arka.jpg, img/ev_1.jpg, img/ev_2.jpg.
  arka : Miletos Port des Lions (CC BY-SA 3.0, rene boulay) 1920x1440 -> kare kirpim -> 1080, renk 0,5 parlaklik 0,93
  ev_1 : Trireme 1 (CC BY-SA 2.0 fr, Rama), trireme maketi, 1920 px -> 1080 genislik, ortadan 760 px kirpim
  ev_2 : Silver denarius of Julius Caesar, MET (CC0) -> sikke ortali 1080x816 kirpim (son kare)
"""
from pathlib import Path
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

HERE = Path(__file__).resolve().parent
K = HERE / "img/kaynak"
BOX = (180, 0, 1620, 1440)


def arka(box=BOX):
    im = Image.open(K / "arka_miletos_liman.jpg").convert("RGB").crop(box).resize((1080, 1080), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(0.5)
    im = ImageEnhance.Brightness(im).enhance(0.93)
    im.save(HERE / "img/arka.jpg", quality=92)


def ev1():
    im = Image.open(K / "kanit_3_trireme.jpg").convert("RGB")
    im = im.resize((1080, round(im.height * 1080 / im.width)), Image.LANCZOS)
    top = (im.height - 760) // 2
    im.crop((0, top, 1080, top + 760)).save(HERE / "img/ev_1.jpg", quality=93)


def ev2():
    im = Image.open(K / "kanit_yedek_denaryus.jpg").convert("RGB")
    im = im.resize((1080, round(im.height * 1080 / im.width)), Image.LANCZOS)
    cy = im.height // 2 + 10
    c = im.crop((0, cy - 408, 1080, cy + 408))
    c.save(HERE / "img/ev_2.jpg", quality=93)


def stats():
    for n in ["arka", "ev_1", "ev_2"]:
        im = Image.open(HERE / f"img/{n}.jpg")
        hsv = np.asarray(im.convert("HSV")).astype(float)
        g = np.asarray(im.convert("L").resize((720, round(720 * im.height / im.width))))
        lap = g[1:-1, 1:-1] * 4 - g[:-2, 1:-1] - g[2:, 1:-1] - g[1:-1, :-2] - g[1:-1, 2:]
        print(n, im.size, "parlaklik %.0f doygunluk %.2f laplace %.0f" % (np.asarray(im.convert("L")).mean(), hsv[..., 1].mean() / 255, lap.var()))


if __name__ == "__main__":
    arka(); ev1(); ev2(); stats()
