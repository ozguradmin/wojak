"""en-lorz-1904-marathon gorselleri:  python episodes/en-lorz-1904-marathon/gorsel.py
Girdiler (kamu malı, bkz. episode.yaml sources) img/ altında; çıktılar img/arka.jpg, img/ev_1.jpg, img/ev_2.jpg.
  arka : StLouisWorldFair1.jpg (T. W. Ingersoll, 1904; python gorsel.py 50 62 440 452 0.8 0.85 -> sol yari kare kirpim, renk 0,8, parlaklik 0,85)
  ev_1 : Start of the 1904 Olympic Marathon Race (cropped).jpg (Missouri History Museum) -> 1080 genişlik, kenarlar kırpıldı
  ev_2 : Following the Marathon Race (The Olympic Games 1904, 1905).jpg -> 1080 genişlik (son kare)
"""
from pathlib import Path
import sys
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

HERE = Path(__file__).resolve().parent
I = HERE / "img"
BOX = tuple(int(v) for v in (sys.argv[1:5] or (22, 40, 452, 470)))
COLOR, BRIGHT = (float(sys.argv[5]) if len(sys.argv) > 5 else 0.7), (float(sys.argv[6]) if len(sys.argv) > 6 else 1.0)


def arka():
    im = Image.open(I / "fuar-1904-arka-plan.jpg").convert("RGB").crop(BOX).resize((1080, 1080), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(COLOR)
    im = ImageEnhance.Brightness(im).enhance(BRIGHT)
    im.save(I / "arka.jpg", quality=92)


def ev1():
    im = Image.open(I / "marathon-start-1904.jpg").convert("RGB")
    w, h = im.size
    im = im.crop((int(w * 0.03), int(h * 0.02), int(w * 0.98), int(h * 0.97)))
    im = im.resize((1080, round(im.height * 1080 / im.width)), Image.LANCZOS)
    print("ev1", im.size)
    im.save(I / "ev_1.jpg", quality=93)


def ev2():
    im = Image.open(I / "following.jpg").convert("RGB")
    im = im.resize((1080, round(im.height * 1080 / im.width)), Image.LANCZOS)
    print("ev2", im.size)
    im.save(I / "ev_2.jpg", quality=93)


def stats():
    for n in ["arka", "ev_1", "ev_2"]:
        im = Image.open(I / f"{n}.jpg")
        hsv = np.asarray(im.convert("HSV")).astype(float)
        g = np.asarray(im.convert("L").resize((720, round(720 * im.height / im.width)))).astype(float)
        lap = g[1:-1, 1:-1] * 4 - g[:-2, 1:-1] - g[2:, 1:-1] - g[1:-1, :-2] - g[1:-1, 2:]
        print(n, im.size, "parlaklik %.0f doygunluk %.2f laplace %.0f" % (np.asarray(im.convert("L")).mean(), hsv[..., 1].mean() / 255, lap.var()))


if __name__ == "__main__":
    arka(); ev1(); ev2(); stats()
