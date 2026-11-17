"""demre-noel-baba-kemik-1087: arka plan ve iki kanıt (img/aday/*.jpg -> img/arka.jpg, kanit_1.jpg, kanit_2.jpg).

    python episodes/demre-noel-baba-kemik-1087/gorsel.py

aday/arka_1_nef_5395.jpg        'Myra Saint Nicolas church interior nave and apse 5395.jpg', Dosseman, 2011, CC BY-SA 4.0
aday/kanit1_alt_lahit_5874.jpg  'Myra Saint Nicolas church interior Another alternative sarcophagus of the saint 5874.jpg',
                                Dosseman, 2011, CC BY-SA 4.0
aday/manna_sforzesco.jpg        'Musei Castello Sforzesco - Bottigliette di Manna di San Nicola.jpg', Sciking, 2024, CC BY-SA 4.0
(eski, tur 1) aday/kanit2_mhs_nakil_resmi.jpg 'MHS przeniesienie relikwi Mikolaja XVII w p.jpg' (1682 tarihli ikona, Dobra, Sanok Tarih Müzesi; ressamı
                                bilinmiyor; fotoğraf Przykuta, 2007), PD-old
"""
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

HERE = Path(__file__).resolve().parent / "img"
ADAY = HERE / "aday"


def olc(im, ad):
    a = np.asarray(im.convert("RGB")).astype(float)
    hsv = np.asarray(im.convert("HSV")).astype(float)
    k = im.convert("L").resize((720, int(720 * im.height / im.width)))
    lap = np.asarray(k.filter(ImageFilter.FIND_EDGES)).astype(float)
    print(f"{ad}: {im.size} parlaklık {a.mean():.0f} doygunluk {hsv[..., 1].mean() / 255:.2f} kenar-var {lap.var():.0f}")


def gama(im, g):
    lut = [round(255 * (i / 255) ** g) for i in range(256)]
    return im.point(lut * 3)


# Arka plan: Myra (Demre) Aziz Nikolaos Kilisesi'nin içi; tonoz, apsis, sütunlar, taş zemin. Sağdan kare kırpım:
# soldaki spot lamba ve ızgaralı kapı + tabela kadraj dışında.
im = Image.open(ADAY / "arka_1_nef_5395.jpg").convert("RGB")
# Sol üst saçak çıkıntısındaki modern projektör (kaynakta ~x 795-835, y 145-190) çevresindeki taştan doldurulur.
a = np.asarray(im).copy()
maske = np.zeros(a.shape[:2], np.uint8)
cv2.rectangle(maske, (790, 140), (840, 195), 255, -1)
a = cv2.inpaint(a, maske, 9, cv2.INPAINT_TELEA)
im = Image.fromarray(a).crop((640, 0, 1920, 1280)).resize((1080, 1080), Image.LANCZOS)
im = gama(im, 0.72)
im = ImageEnhance.Color(im).enhance(1.8)  # gri-mavi taş; hakem tur 1-2 SHOULD: doygunluk ~0,13-0,2, turkuaz sapma olmasın
im.save(HERE / "arka.jpg", quality=92)
olc(im, "arka")

# Kanıt 1: kilisede azizin olası lahitlerinden biri olarak gösterilen, kapağı kırık mermer lahit.
im = Image.open(ADAY / "kanit1_alt_lahit_5874.jpg").convert("RGB")
im = im.crop((260, 330, 1700, 1230)).resize((1080, 675), Image.LANCZOS)
im = gama(im, 0.9)
im.save(HERE / "kanit_1.jpg", quality=92)
olc(im, "kanit_1")

# Kanıt 2 (son kare): Milano Castello Sforzesco müzesindeki "Aziz Nikolaos mannası" şişecikleri (1876 bağışı) ve etiketi
# ("Fialette per la manna di San Nicola"). Tur 1 takipçi MUST: ters köşe sıvıyı soruyor, son kare sıvıyla bağlanmalı
# (önceki son kare 1682 "kemiklerin nakli" ikonasıydı).
im = Image.open(ADAY / "manna_sforzesco.jpg").convert("RGB")
im = im.crop((330, 230, 1890, 1097)).resize((1080, 600), Image.LANCZOS)
im.save(HERE / "kanit_2.jpg", quality=92)
olc(im, "kanit_2")
