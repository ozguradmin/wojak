"""Arka plan ve kanıt görselleri: python episodes/hope-elmasi-posta-1958/gorsel.py
arka.jpg   <- img/arka_3.jpg (Highsmith, Foley Post Office lobisi, Albany NY; PD-Highsmith): merkezden kare kırpım,
              kırmızı yangın alarmı kutusu ve duvardaki portre komşu mermerle örtüldü, 1080'e küçültme, renk/parlaklık ayarı.
kanit_1.jpg <- img/elmas_1.jpg (Jyothis, CC BY-SA 3.0): 1080x816 kırpım, autocontrast + gama 0,82.
kanit_2.jpg <- img/sargi_1.jpg (NPM 1992.2002.15a, CC0): 1080x816 kırpım (ön yüz, el yazısı, adres etiketi).
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

D = Path(__file__).parent / "img"


def arka():
    im = Image.open(D / "kaynak" / "arka_3.jpg").convert("RGB")
    w, h = im.size
    s = h
    x0 = (w - s) // 2
    c = im.crop((x0, 0, x0 + s, s))
    yama = c.crop((240, 574, 300, 626))
    c.paste(yama, (176, 574))
    # duvardaki 18. yy portresi (tur 1 SHOULD: 1958 postanesinde tuhaf) aynı sıradaki sol mermer panelle örtülür
    panel = c.crop((630 - 364 - 30, 320, 830 - 364 + 30, 600))
    maske = Image.new("L", panel.size, 0)
    ImageDraw.Draw(maske).rectangle((26, 26, panel.width - 26, panel.height - 26), fill=255)
    c.paste(panel, (630 - 30, 320), maske.filter(ImageFilter.GaussianBlur(12)))
    c = c.resize((1080, 1080), Image.LANCZOS)
    c = ImageEnhance.Brightness(c).enhance(BR)
    c = ImageEnhance.Color(c).enhance(CO)
    c.save(D / "arka.jpg", quality=92)


def kirp(src, box, out, auto=False):
    im = Image.open(D / "kaynak" / src).convert("RGB")
    c = im.crop(box).resize((1080, 816), Image.LANCZOS)
    if auto:
        c = ImageOps.autocontrast(c, cutoff=0.5)
        c = c.point(lambda v: round(255 * (v / 255) ** 0.82))
    c.save(D / out, quality=92)


BR, CO = 1.05, 0.62
if __name__ == "__main__":
    arka()
    kirp("elmas_1.jpg", (34, 0, 34 + 1212, 916), "kanit_1.jpg", auto=True)
    kirp("sargi_1.jpg", (0, 30, 2888, 30 + 2182), "kanit_2.jpg")
    print("tamam")
