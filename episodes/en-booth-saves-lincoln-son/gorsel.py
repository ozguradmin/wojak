"""en-booth-saves-lincoln-son görselleri (img/kaynak/ ham indirilenlerden):  python episodes/en-booth-saves-lincoln-son/gorsel.py
 arka.jpg : Pacific Railroad lokomotifi, 1869 (kamu malı); kare kırpım, renk 0,85, parlaklık 0,88
 ev_1.jpg : The Century Magazine, Nisan 1909, s. 920 (IA, kamu malı); 9 satır, kâğıt tonu aynen, 1080 genişlik
 ev_2.jpg : Edwin Booth, T. R. Burnham, 1865 (LoC, kamu malı, SON KARE); kart kenarı atıldı, 1080x816 kırpım
"""
from pathlib import Path
from PIL import Image, ImageEnhance

H = Path(__file__).resolve().parent / "img"
K = H / "kaynak"


def arka():
    im = Image.open(K / "peck_1920.jpg").convert("RGB").crop((420, 0, 1676, 1256)).resize((1080, 1080), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(0.85)
    ImageEnhance.Brightness(im).enhance(0.88).save(H / "arka.jpg", quality=93)


def ev1():
    im = Image.open(K / "century_1909_p920_kirpinti.jpg").convert("RGB")
    im = im.crop((0, 953, im.width, 953 + 662))
    im = im.resize((1080, round(im.height * 1080 / im.width)), Image.LANCZOS)
    im.save(H / "ev_1.jpg", quality=94)
    print("ev1", im.size)


def ev2():
    im = Image.open(K / "booth_burnham_1920.jpg").convert("RGB")
    im = im.crop((230, 440, 1730, 440 + round(1500 * 816 / 1080))).resize((1080, 816), Image.LANCZOS)
    im.save(H / "ev_2.jpg", quality=94)
    print("ev2", im.size)


if __name__ == "__main__":
    arka(); ev1(); ev2()
