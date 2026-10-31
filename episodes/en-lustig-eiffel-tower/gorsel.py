"""en-lustig-eiffel-tower görselleri (ham indirilenlerden):  python episodes/en-lustig-eiffel-tower/gorsel.py
 arka.jpg  : Hôtel de Crillon cephesi (Claus, 2007, kamu malı), kare kırpım (arabalar dışarıda), renk 0.72, parlaklık 1.10
 ev_1.jpg  : ABD Adalet Bakanlığı / BOI kimlik kartı, 25.6.1931 (kamu malı); üst başlık kırpıldı, 2,35x LANCZOS + UnsharpMask
 ev_2.jpg  : LoC Photochrom baskısı, Eyfel Kulesi ve çeşme, ~1890-1905 (kamu malı); yanlardan kırpıldı, 1080x816
"""
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter

H = Path(__file__).resolve().parent / "img"


def arka():
    im = Image.open(H / "arka_2_crillon.jpg").convert("RGB").crop((420, 0, 1620, 1200)).resize((1080, 1080), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(0.72)
    im = ImageEnhance.Brightness(im).enhance(1.10)
    im.save(H / "arka.jpg", quality=93)


def ev1():
    im = Image.open(H / "kanit_1_doj_1931_orijinal.jpg").convert("RGB")
    im = im.crop((0, 62, 460, 348))
    W = 1080
    im = im.resize((W, round(im.height * W / im.width)), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 70, 2))
    im.save(H / "ev_1.jpg", quality=94)
    print("ev1", im.size)


def ev2():
    im = Image.open(H / "kanit_2_photochrom.jpg").convert("RGB")
    im = im.crop((30, 0, 1890, 1405)).resize((1080, 816), Image.LANCZOS)
    im.save(H / "ev_2.jpg", quality=94)
    print("ev2", im.size)


if __name__ == "__main__":
    arka(); ev1(); ev2()
