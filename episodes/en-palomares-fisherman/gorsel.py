"""en-palomares-fisherman görselleri:  python episodes/en-palomares-fisherman/gorsel.py
arka.jpg   : USS Skill (MSO-471), Şubat 1966, İspanya açıkları (US Navy film kare 428-NPC-36556, PD) -> kare kırpım 898x898 -> 1080, renk/blur
ev_1.jpg   : Águilas balıkçı limanı 1961 (Univ. Zaragoza kütüphanesi, CC BY-SA 2.0), 2:1 kırpım -> 1080x540
ev_2.jpg   : kurtarılan Mk 28 bombası ("Robert") USS Petrel güvertesinde, 1966 (U.S. Navy image, PD-USGov-Military-Navy), 617x461 -> 1080x807 (1,75x büyütme, hafif keskinleştirme)
"""
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter

HERE = Path(__file__).resolve().parent
S = HERE / "img" / "src"
O = HERE / "img"


def kaydet(im, ad):
    im.convert("RGB").save(O / ad, quality=93)


# arka plan
a = Image.open(S / "skill_src.jpg").convert("RGB")
a = a.crop((120, 0, 120 + a.height, a.height)).resize((1080, 1080), Image.LANCZOS)
a = ImageEnhance.Color(a).enhance(0.85)
a = ImageEnhance.Brightness(a).enhance(1.0)
kaydet(a, "arka.jpg")

# kanıt 1
e = Image.open(S / "aguilas_1961_src.jpg").convert("RGB")
w, h = e.size
nw = round(h * 2.0)
e = e.crop((w - nw, 0, w, h))
e = e.resize((1080, round(1080 * e.height / e.width)), Image.LANCZOS)
kaydet(e, "ev_1.jpg")

# kanıt 2
b = Image.open(S / "mk28_petrel_src.jpg").convert("RGB")
b = b.resize((1080, round(1080 * b.height / b.width)), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.6, 60, 2))
kaydet(b, "ev_2.jpg")
for n in ["arka", "ev_1", "ev_2"]:
    print(n, Image.open(O / f"{n}.jpg").size)
