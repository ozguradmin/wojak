"""hayirsizada-kopekleri-1910: arka plan ve kanıt görselleri (kaynaklar img/kaynak_*.jpg; lisanslar episode.yaml sources).

    python episodes/hayirsizada-kopekleri-1910/gorsel.py
"""
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps

IMG = Path(__file__).resolve().parent / "img"


def arka():
    # Sivriada (Hayırsızada), denizden; Julian Nyča 2014, CC BY-SA 4.0. Kare kırpım adanın tepesine ortalı.
    im = Image.open(IMG / "kaynak_kanit1.jpg").convert("RGB")
    x0 = 1060 - im.height // 2
    im = im.crop((x0, 0, x0 + im.height, im.height)).resize((1080, 1080), Image.LANCZOS)
    # tepedeki küçük işaret direği (modern öğe) yanındaki gökyüzü yamasıyla örtülür
    from PIL import ImageDraw, ImageFilter
    a = im.copy()
    yama = a.crop((650, 306, 690, 344))
    a.paste(yama, (684, 306))
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).rectangle((688, 308, 718, 340), fill=255)
    im = Image.composite(a, im, m.filter(ImageFilter.GaussianBlur(3)))
    im = ImageEnhance.Contrast(im).enhance(1.15)
    im = ImageEnhance.Color(im).enhance(0.75)
    im = ImageEnhance.Brightness(im).enhance(0.98)
    im.save(IMG / "arka.jpg", quality=92)


def kanit_1():
    # Rijksmuseum RP-F-F01141-CG 'Groupe de chiens', İstanbul, ca. 1900 - Nisan 1910 öncesi, CC0: köpek grubu, sıkı kırpım
    im = Image.open(IMG / "kaynak_kanit1_alt2.jpg").convert("RGB")
    s = im.width / 1000
    im = im.crop((round(24 * s), round(255 * s), round(976 * s), round(790 * s)))
    im = ImageOps.autocontrast(im, cutoff=0.5)
    im = im.resize((1080, round(1080 * im.height / im.width)), Image.LANCZOS)
    im.save(IMG / "kanit_1.jpg", quality=92)


def kanit_2():
    # Le Petit Parisien Supplément littéraire illustré, 7.8.1910, s. 260 (Gallica/BnF, kamu malı): alt bölüm,
    # adaya indirilen köpekler + gazetenin kendi alt yazısı (tam satır)
    im = Image.open(IMG / "kaynak_sonkare_cizim.jpg").convert("RGB")
    W, H = im.size
    x0, x1 = 70, W - 70
    h = round((x1 - x0) / 1.33)
    im = im.crop((x0, 2495 - h, x1, 2495))
    im = im.resize((1080, round(1080 * im.height / im.width)), Image.LANCZOS)
    im.save(IMG / "kanit_2.jpg", quality=92)


if __name__ == "__main__":
    arka(); kanit_1(); kanit_2()
    import numpy as np
    for f in ("arka.jpg", "kanit_1.jpg", "kanit_2.jpg"):
        im = Image.open(IMG / f)
        hsv = np.array(im.convert("HSV")).astype(float)
        print(f, im.size, "parlaklık %.0f doygunluk %.2f" % (hsv[..., 2].mean(), hsv[..., 1].mean() / 255))
