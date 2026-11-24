"""anemas-zindani-1376: arka plan ve iki kanıt (kaynaklar img/kaynak_*.jpg; tools/commons.py ile indirildi).

    python episodes/anemas-zindani-1376/gorsel.py

arka.jpg     'Prison of Anemas.jpg' (Isabeau, 2018, CC BY-SA 4.0): Ayvansaray'da Blakhernai surları ve bugün "Anemas
             Zindanları" diye anılan yapının kulesi. Sağ kare kırpım (soldaki cami, minare ve bayrak dışarıda), 1080'e
             küçültme, renk ve parlaklık ayarı.
kanit_1.jpg  'John V Palaiologos, Fossati drawing of mosaic in Hagia Sophia.jpg' (Gaspare ve Giuseppe Fossati, 1847; PD-Art):
             Fossati kardeşlerin Ayasofya'daki V. İoannis mozaiğini sıvayla örtmeden önce çizdiği kopya. Baş ve omuz kırpımı,
             kitap baskısı fotoğrafındaki mor döküm alınıp nötr gri-beyaza çekildi, kontrast artırıldı. (Tur 1 takipçi MUST: önceki
             'Restored mosaic ... (head)' dijital olarak iyileştirilmiş bir fotoğraftı, kaynağı Flickr'da "All rights reserved".)
kanit_2.jpg  Son kare. 'Millingen - Plan of Anemas Prison.jpg' (Alexander van Millingen, "Byzantine Constantinople", 1899;
             PD-old): "Plan of the so-called Prison of Anemas" başlığı ve tonozlu hücreler. Başlık telefonda okunsun diye
             üst-orta kırpım, hafif autocontrast.
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

IMG = Path(__file__).resolve().parent / "img"


def olc(im, ad):
    a = np.asarray(im.convert("RGB")).astype(float)
    hsv = np.asarray(im.convert("HSV")).astype(float)
    k = im.convert("L").resize((720, round(720 * im.height / im.width)))
    lap = np.asarray(k.filter(ImageFilter.FIND_EDGES)).astype(float).var()
    print(f"{ad}: {im.size} parlaklık {a.mean():.0f} doygunluk {hsv[..., 1].mean() / 255:.2f} kenar var {lap:.0f}")


ARKA_KUTU = (1010, 200, 1920, 1110)   # soldaki minare dışarıda
arka = Image.open(IMG / "kaynak_arka.jpg").convert("RGB").crop(ARKA_KUTU).resize((1080, 1080), Image.LANCZOS)
arka = ImageEnhance.Brightness(ImageEnhance.Color(arka).enhance(0.66)).enhance(1.32)
arka.save(IMG / "arka.jpg", quality=92)
olc(arka, "arka")

k1 = Image.open(IMG / "kaynak_fossati.jpg").convert("L").crop((180, 150, 1100, 845))
k1 = ImageOps.autocontrast(k1, cutoff=(2, 12))
k1 = k1.point(lambda v: round(255 * (v / 255) ** 1.6))
k1 = ImageOps.colorize(k1, black=(28, 28, 30), white=(244, 243, 240))   # tur 3 görsel SHOULD: iki bej kanıt arka arkaya gelmesin
k1 = k1.resize((1080, round(k1.height * 1080 / k1.width)), Image.LANCZOS)
k1.save(IMG / "kanit_1.jpg", quality=92)
olc(k1, "kanit_1")

k2 = Image.open(IMG / "kaynak_plan.jpg").convert("RGB").crop((300, 0, 1500, 740))   # sağdaki 'Court of Palace' etiketi ve alttaki lejant dışarıda
k2 = ImageOps.autocontrast(k2, cutoff=(2, 0.3), preserve_tone=True)
k2 = k2.point(lambda v: round(255 * (v / 255) ** 1.25))   # tur 1 görsel SHOULD: kâğıt ve çizgiler koyulaşsın
k2 = k2.resize((1080, round(k2.height * 1080 / k2.width)), Image.LANCZOS)
k2.save(IMG / "kanit_2.jpg", quality=92)
olc(k2, "kanit_2")
