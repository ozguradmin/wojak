"""en-abbott-golf-1900 gorselleri:  python episodes/en-abbott-golf-1900/gorsel.py
Kaynaklar img/ altinda (Commons, kamu mali; bkz. episode.yaml sources). Ciktilar: arka.jpg, ev_1.jpg, ev_2.jpg."""
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

HERE = Path(__file__).resolve().parent
IMG = HERE / "img"


def arka():
    im = Image.open(IMG / "bg1_expo_grand_entrance_1900.jpg").convert("RGB")
    im = im.crop((250, 60, 1580, 1390)).resize((1080, 1080), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(0.8)
    im = ImageEnhance.Brightness(im).enhance(0.8)
    im.save(IMG / "arka.jpg", quality=93)


def ev1():
    im = Image.open(IMG / "kanit2_la_vie_au_grand_air_1900.png").convert("RGB")
    im = im.crop((60, 60, 1221, 760))
    im = im.resize((1080, round(im.height * 1080 / im.width)), Image.LANCZOS)
    im.save(IMG / "ev_1.jpg", quality=93)
    print("ev_1", im.size)


def ev2():
    im = Image.open(IMG / "kanit1_chicago_tribune_1900-10.jpg").convert("RGB")
    im = im.crop((30, 150, 1215, 800))
    im = im.resize((1080, round(im.height * 1080 / im.width)), Image.LANCZOS)
    im.save(IMG / "ev_2.jpg", quality=93)
    print("ev_2", im.size)


if __name__ == "__main__":
    arka(); ev1(); ev2()
