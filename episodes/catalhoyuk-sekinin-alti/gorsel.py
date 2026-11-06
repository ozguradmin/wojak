"""catalhoyuk-sekinin-alti: arka plan ve kanıt görselleri (Commons 1920 px küçük resimlerinden).

    python episodes/catalhoyuk-sekinin-alti/gorsel.py

img/arka_1.jpg       -> img/arka.jpg     Anadolu Medeniyetleri Müzesi'ndeki yeniden kurulmuş Çatalhöyük odası
                                          (Dosseman, CC BY-SA 4.0). Kare kırpım (70,250,830,1010), 1,42x büyütme, gama 0,68, Color 1,30: merdiven + ocak (sol), seki + çanaklar
                                          (sağ); alttaki camlı gömü çukuru, etiket ve müze tavanı dışarıda.
img/kanit_yer_1.jpg  -> img/kanit_1.jpg  Koruma çatısı altındaki Çatalhöyük Doğu Höyüğü evleri (Kemal Kozbaev, CC BY-SA 4.0).
img/kanit_gomu_4.jpg -> img/kanit_2.jpg  2008 kazısı (2 Ağustos): kazıda açılmış gömü çukurunda kıvrık yatan
                                          iskelet (Colleen Morgan, CC BY 2.0). Kırpım (995,410,1780,1000), 1,38x;
                                          kazı levhası ve ölçek çubuğu dışarıda.
"""
from pathlib import Path

from PIL import Image, ImageEnhance

IMG = Path(__file__).resolve().parent / "img"


def arka():
    im = Image.open(IMG / "arka_1.jpg").convert("RGB")
    im = im.crop((70, 250, 830, 1010)).resize((1080, 1080), Image.LANCZOS)
    im = im.point(lambda v: round(255 * (v / 255) ** 0.68))   # gölgedeki oda aydınlatılır (gama 0,68)
    im = ImageEnhance.Color(im).enhance(1.30)
    im.save(IMG / "arka.jpg", quality=92)


def kanit_1():
    im = Image.open(IMG / "kanit_yer_1.jpg").convert("RGB")
    im = im.crop((0, 120, 1920, 1440)).resize((1080, 742), Image.LANCZOS)
    im.save(IMG / "kanit_1.jpg", quality=92)


def kanit_2():
    im = Image.open(IMG / "kanit_gomu_4.jpg").convert("RGB")
    im = im.crop((995, 410, 1780, 1000)).resize((1080, 812), Image.LANCZOS)
    im.save(IMG / "kanit_2.jpg", quality=92)


if __name__ == "__main__":
    arka()
    kanit_1()
    kanit_2()
