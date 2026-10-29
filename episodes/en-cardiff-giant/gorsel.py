"""en-cardiff-giant kanıt kırpımları:  python episodes/en-cardiff-giant/gorsel.py
Kaynaklar: img/kanit_2_onondaga_litografi_1869.jpg (LoC, kamu malı, 4000x3013), img/marker_src_1920.jpg (Commons, Martin Lewison, CC BY-SA 2.0).
Çıktı: img/kanit_1.jpg, img/kanit_2.jpg (1080 genişlik). Yalnız kırpım, boyutlandırma ve autocontrast (fotoğraf).
"""
from pathlib import Path
from PIL import Image, ImageOps

HERE = Path(__file__).resolve().parent / "img"


def crop_to(src, box, out, w=1080, auto=False):
    im = Image.open(HERE / src).convert("RGB").crop(box)
    if auto:
        im = ImageOps.autocontrast(im, cutoff=0.5)
    h = round(im.height * w / im.width)
    im = im.resize((w, h), Image.LANCZOS)
    print(out, im.size, "ölçek", round(w / (box[2] - box[0]), 2))
    im.save(HERE / out, quality=94)


# Kanıt 1: Onondaga Giant litografı, üstteki figürün gövde ve başı (4000 px ölçeği = 1280 ölçeği x 3.125; autocontrast)
s = 4000 / 1280
crop_to("kanit_2_onondaga_litografi_1869.jpg", (int(578 * s), int(108 * s), int(1033 * s), int(336 * s)), "kanit_1.jpg", auto=True)
# Kanıt 2 (son kare): New York eyalet tarihî levhası "Cardiff Giant ... The Great American Hoax" (Commons, CC BY-SA 2.0, 1920 px)
crop_to("marker_src_1920.jpg", (290, 385, 1370, 945), "kanit_2.jpg")

# Arka plan: LoC stereograf (c. 1880, Kuzeydoğu ABD çiftliği); sol kare zaten kırpılmış. Yalnız parlaklık düşürüldü.
from PIL import ImageEnhance
bg = Image.open(HERE / "arka_aday_1_hiram_adams_farm_1880.jpg").convert("RGB")
bg = ImageEnhance.Brightness(bg).enhance(0.76)
bg = bg.resize((1600, round(bg.height * 1600 / bg.width)), Image.LANCZOS)
bg.save(HERE / "bg.jpg", quality=93)
print("bg", bg.size)
