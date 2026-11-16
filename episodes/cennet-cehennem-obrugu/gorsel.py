"""cennet-cehennem-obrugu: arka plan ve iki kanıt (img/*_aday*.jpg -> arka.jpg, kanit_1.jpg, kanit_2.jpg).

    python episodes/cennet-cehennem-obrugu/gorsel.py

arka_aday1.jpg      'Narlıkuyu Cennet (Heaven) sinkhole 2353.jpg', Dosseman, 2015, CC BY-SA 4.0 (1920x1071 indirildi)
kanit_cehennem.jpg  'Narlıkuyu Cehenem (Hell) sinkhole 1438.jpg', Dosseman, 2011, CC BY-SA 4.0 (1920x1278)
kanit_kilise.jpg    'Cennet Cehennem, Cennet deki Kilise - panoramio.jpg', Korkut Tas, 2011, CC BY-SA 3.0 (1920x1440)
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

HERE = Path(__file__).resolve().parent / "img"


def olc(im, ad):
    a = np.asarray(im.convert("RGB")).astype(float)
    hsv = np.asarray(im.convert("HSV")).astype(float)
    k = im.convert("L").resize((720, int(720 * im.height / im.width)))
    lap = np.asarray(k.filter(ImageFilter.FIND_EDGES)).astype(float)
    print(f"{ad}: {im.size} parlaklık {a.mean():.0f} doygunluk {hsv[..., 1].mean() / 255:.2f} kenar-var {lap.var():.0f}")


def gama(im, g):
    lut = [round(255 * (i / 255) ** g) for i in range(256)]
    return im.point(lut * 3)


# Arka plan: Cennet obruğunun içi; turuncu kaya duvar ve mağara nişi, yeşil makili taban. Sağdan kare kırpım
# (soldaki çıplak kaya kenarı dışarıda); modern öğe yok.
im = Image.open(HERE / "arka_aday1.jpg").convert("RGB")
im = im.crop((700, 0, 1771, 1071)).resize((1080, 1080), Image.LANCZOS)
im = ImageEnhance.Color(im).enhance(0.75)
im = ImageEnhance.Brightness(im).enhance(1.1)
im.save(HERE / "arka.jpg", quality=92)
olc(im, "arka")

# Kanıt 1: Cehennem obruğuna yukarıdan bakış (içe eğik duvarlar, dipte makilik). Kenarlardan hafif kırpım.
im = Image.open(HERE / "kanit_cehennem.jpg").convert("RGB")
im = im.crop((52, 0, 1868, 1278)).resize((1080, 760), Image.LANCZOS)
im = gama(im, 0.88)
a = np.asarray(im).astype(float)
parlak = np.clip((a.mean(-1, keepdims=True) - 190) / 40, 0, 1)
im = Image.fromarray((a * (1 - 0.22 * parlak)).clip(0, 255).astype(np.uint8))  # göğe açılan parlak delik %22'ye kadar kısıldı
im.save(HERE / "kanit_1.jpg", quality=92)
olc(im, "kanit_1")

# Kanıt 2 (son kare): Cennet obruğunun dibinde, mağara ağzının kemeri altındaki kilise. Kiliseye sıkı kırpım (hakem
# tur 1 SHOULD: telefonda kilise >= 130 px); kemerin alt kenarı ve mağara ağzı kadrajda. Gölgeler gama ile açıldı, patlak gökyüzü hafif kısıldı.
im = Image.open(HERE / "kanit_kilise.jpg").convert("RGB")
im = im.crop((560, 400, 1710, 1205)).resize((1080, 756), Image.LANCZOS)
im = gama(im, 0.8)
a = np.asarray(im).astype(float)
parlak = np.clip((a.mean(-1, keepdims=True) - 225) / 30, 0, 1)
a = a * (1 - 0.08 * parlak)
im = Image.fromarray(a.clip(0, 255).astype(np.uint8))
im.save(HERE / "kanit_2.jpg", quality=92)
olc(im, "kanit_2")
