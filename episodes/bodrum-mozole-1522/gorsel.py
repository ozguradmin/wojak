"""bodrum-mozole-1522: arka plan ve iki kanıt (kaynaklar img/*_aday*.jpg, tools/commons.py ile indirildi).

    python episodes/bodrum-mozole-1522/gorsel.py

arka.jpg     'Bodrum Castle 4.JPG' (Ad Meskens, CC BY-SA 3.0): bayrak direkleri ve kuledeki ziyaretçiler kadraja girmesin
             diye bayrağın altından kare kırpım (x 370-999, y 250-879), 1080'e büyütme, renk 0,95, parlaklık 1,08.
kanit_1.jpg  Heemskerck/Galle 'Mausoleum' gravürü (1572, Rijksmuseum, kamu malı): yapıya sıkı kırpım, 1080x816.
kanit_2.jpg  Newton & Pullan, A History of Discoveries at Halicarnassus (1862), s. 78: Guichard 1581 anlatısının İngilizce
             çevirisi ("The day after ... had removed the lid of the sepulchre"). Internet Archive gri_33125008617553
             (Getty Research Institute taraması, NOT_IN_COPYRIGHT), leaf 99, w2000 -> img/kaynak_newton_s78.jpg.
             Yalnız 'The day after ...' paragrafı (9 tam satır, x 630-1720, y 1632-2150);
             üst ve alta aynı sayfanın alt boş kâğıdından 16 px şerit, 1080 genişlik (~0,99 ölçek).
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

IMG = Path(__file__).resolve().parent / "img"


def olc(im, ad):
    a = np.asarray(im.convert("RGB")).astype(float)
    hsv = np.asarray(im.convert("HSV")).astype(float)
    k = im.convert("L").resize((720, round(720 * im.height / im.width)))
    lap = np.asarray(k.filter(ImageFilter.FIND_EDGES)).astype(float).var()
    print(f"{ad}: {im.size} parlaklık {a.mean():.0f} doygunluk {hsv[..., 1].mean() / 255:.2f} kenar var {lap:.0f}")


# Küçük modern öğeler rötuşla (aynı satırlardan komşu doku kopyalanarak) silinir; özgün koordinatlar:
# sağ kuledeki bayrak direği ve anten, sağ kule tepesindeki ve kule penceresindeki ziyaretçi.
ROTUS = [((854, 300, 868, 370), -20), ((894, 330, 904, 368), -12), ((908, 348, 926, 384), -20), ((842, 444, 860, 478), -20), ((812, 472, 828, 494), 16), ((475, 474, 497, 497), 20)]


def rotus(im):
    for (x0, y0, x1, y1), dx in ROTUS:
        p = 4  # yumuşak kenar
        maske = Image.new("L", (x1 - x0 + 2 * p, y1 - y0 + 2 * p), 0)
        maske.paste(255, (p, p, p + x1 - x0, p + y1 - y0))
        maske = maske.filter(ImageFilter.GaussianBlur(2))
        im.paste(im.crop((x0 + dx - p, y0 - p, x1 + dx + p, y1 + p)), (x0 - p, y0 - p), maske)
    return im


arka = rotus(Image.open(IMG / "arka_aday4.jpg").convert("RGB")).crop((370, 290, 959, 879))
arka = arka.resize((1080, 1080), Image.LANCZOS)
arka = ImageEnhance.Brightness(ImageEnhance.Color(arka).enhance(0.85)).enhance(1.02)
arka.save(IMG / "arka.jpg", quality=92)
olc(arka, "arka")

k1 = Image.open(IMG / "kanit_aday1.jpg").convert("RGB").crop((100, 40, 1180, 856))
k1.save(IMG / "kanit_1.jpg", quality=92)
olc(k1, "kanit_1")

kaynak = Image.open(IMG / "kaynak_newton_s78.jpg").convert("RGB")
metin = kaynak.crop((630, 1632, 1720, 2150))          # yalnız "The day after ..." paragrafı (9 tam satır)
kagit = kaynak.crop((630, 2500, 1720, 2516))          # aynı sayfanın alt boş kâğıdı: 537 px alt sınırı için üst/alt pay
k2 = Image.new("RGB", (metin.width, metin.height + 2 * kagit.height))
k2.paste(kagit, (0, 0)); k2.paste(metin, (0, kagit.height)); k2.paste(kagit, (0, kagit.height + metin.height))
k2 = k2.resize((1080, round(k2.height * 1080 / k2.width)), Image.LANCZOS)
k2.save(IMG / "kanit_2.jpg", quality=92)
olc(k2, "kanit_2")
