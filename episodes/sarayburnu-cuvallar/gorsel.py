"""sarayburnu-cuvallar: arka plan ve iki kanıt (kaynaklar img/kaynak_* ve img/kanit2-*, tools/commons.py ile indirildi).

    python episodes/sarayburnu-cuvallar/gorsel.py

arka.jpg     'Topkapı Palace from the Bosphorus in 2024 6700.jpg' (Dosseman, CC BY-SA 4.0): Topkapı Sarayı'nın denizden
             (Sarayburnu) görünüşü, mutfak bacaları, Has Oda, Adalet Kulesi. Kıyı yolundaki şantiye paneli, lambalar ve
             araçlar dışarıda kalsın diye kıyının üstünden kare kırpım (812x812, x 654-1466, y 0-812; tur 1: alt kenardaki tabela kırıntısı atıldı), 1080'e büyütme
             (1,33x), renk 0,85, parlaklık 0,92.
kanit_1.jpg  'Sultan İbrahim, 17. yüzyıl gravürü.jpg' (yayımcı Pieter de Jode II, Rijksmuseum RP-P-1905-4810, CC0):
             sorguç dahil, sarıktan göğse kırpım (x 160-1780, y 190-1414; 1920 genişlikli dosyada), 1080x816. Renderer kanıtı
             kareye sığdırdığı ve kanıt en çok 816 px olduğu için Latince alt yazı (gravürün en altı) kadraja girmiyor.
kanit_2.jpg  'Harem entrance Topkapi Istanbul 2007 71.JPG' (Gryffindor, 2007, PD-self): Topkapı Sarayı'nda Harem'in
             girişi (Arabalar Kapısı) ve "HAREM / THE HAREM" levhası. Özgün 1600x1200 dosyadan (md5 yolu) kapı kemeri ve
             levha, sağdaki modern boru dışarıda: x 700-1520, y 150-770, 1080x816 (1,32x).
(Tur 1 görsel hakem MUST: son kare kimlik vermiyordu. Cassas panoraması çıkarıldı; gravür kanıt 1'e, Harem levhası son kareye.)
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


arka = Image.open(IMG / "kaynak_topkapi_6700.jpg").convert("RGB").crop((654, 0, 1466, 812))
arka = arka.resize((1080, 1080), Image.LANCZOS)
arka = ImageEnhance.Brightness(ImageEnhance.Color(arka).enhance(0.85)).enhance(0.92)
arka.save(IMG / "arka.jpg", quality=92)
olc(arka, "arka")

k1 = Image.open(IMG / "kanit2-ibrahim-gravur.jpg").convert("RGB").crop((160, 190, 1780, 1414))
k1 = k1.resize((1080, 816), Image.LANCZOS)
k1.save(IMG / "kanit_1.jpg", quality=92)
olc(k1, "kanit_1")

k2 = Image.open(IMG / "kaynak_harem_kapi.jpg").convert("RGB").crop((700, 150, 1520, 770))
k2 = k2.resize((1080, 816), Image.LANCZOS)
k2.save(IMG / "kanit_2.jpg", quality=92)
olc(k2, "kanit_2")
