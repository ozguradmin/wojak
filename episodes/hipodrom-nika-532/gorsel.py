"""hipodrom-nika-532: arka plan ve iki kanıt (kaynaklar img/*_kaynak*.jpg, tools/commons.py ile indirildi).

    python episodes/hipodrom-nika-532/gorsel.py

arka.jpg     'Aphrodisias - Stadium 01.jpg' (Bernard Gagnon, CC BY-SA 3.0): Aphrodisias stadyumunun taş tribünleri
             (aynı türden yer: Konstantinopolis Hipodromu değil). Gökyüzünün çoğu ve sağ üstteki harabe dışarıda kalacak
             kare kırpım, 1080'e büyütme (1,24x), renk 0,64, parlaklık 1,06.
kanit_1.jpg  'Hippodrome of Constantinople and Obelisk of Theodosius on Sultanahmet Meydanı square (8396071658).jpg'
             (Jorge Láscar, CC BY 2.0): şafakta boş Sultanahmet Meydanı = Hipodrom'un yeri, ortada Dikilitaş.
             Dikilitaşa ortalı 1200x822 kırpım, 1080x740, parlaklık 1,12.
kanit_2.jpg  Prokopios, History of the Wars I-II, çev. H. B. Dewing (Loeb, 1914), s. 237 (I.xxiv.50-56): "sally into the
             hippodrome ... Gate of Death ... more than thirty thousand." Internet Archive procopius00procgoog (Google
             taraması, NOT_IN_COPYRIGHT), leaf 254, n253_w2000 -> img/kaynak_prokopios_s237.jpg. Tur 1 görsel hakem
             MUST (telefonda okunmuyor): 9 satırın sol kısmı ("the rout had become ..." - "emperor commanded ..."),
             x 215-1665 (sol kenar boşluğundan "thirty thousand." sonuna), y 1712-2447, 1080 genişlik (~0,74 ölçek);
             siyah-beyaz taramaya hafif kâğıt tonu verildi (yalnız renk; metin pikselleri değişmedi).
             Tur 2 görsel SHOULD (sağda sözcük ortasında kesik, başlıksız kesit): sayfanın üstü, başlık satırı
             "HISTORY OF THE WARS, I. xxiv. 50-56" dahil, ilk satırdan "that day more than thirty thousand." satırına
             kadar 24 tam satır ve altında 4 tam satır daha (x 68-2228, kenar boşlukları dahil; y 215-2692), 1080x1238 dikey
             (STIL §8: uzun görsel en çok 1260 px). "thirty thousand." satırı filigranın (y ~1475) üstünde kalsın diye
             sayfa 4 satır aşağı uzatıldı. Sağ kenar boşluğundaki (x > 2100, metin yok) tarama lekeleri beyazlatıldı.
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


arka = Image.open(IMG / "arka_kaynak.jpg").convert("RGB").crop((526, 400, 1394, 1268))
arka = arka.resize((1080, 1080), Image.LANCZOS)
arka = ImageEnhance.Brightness(ImageEnhance.Color(arka).enhance(0.64)).enhance(1.06)
arka.save(IMG / "arka.jpg", quality=92)
olc(arka, "arka")

k1 = Image.open(IMG / "kanit_1_kaynak.jpg").convert("RGB").crop((334, 330, 1534, 1152))
k1 = ImageEnhance.Brightness(k1.resize((1080, 740), Image.LANCZOS)).enhance(1.12)
k1.save(IMG / "kanit_1.jpg", quality=92)
olc(k1, "kanit_1")

k2 = Image.open(IMG / "kaynak_prokopios_s237.jpg").convert("L")
k2.paste(255, (2100, 0, k2.width, k2.height))                          # sağ kenar boşluğundaki tarama lekeleri (metin yok)
k2 = k2.crop((68, 215, 2228, 2692))
k2 = k2.resize((1080, round(k2.height * 1080 / k2.width)), Image.LANCZOS)
t = np.asarray(k2).astype(float)[..., None] / 255.0                  # ikili taramaya kâğıt tonu (yalnız renk)
k2 = Image.fromarray((np.array([28, 24, 22]) + t * (np.array([234, 226, 210]) - np.array([28, 24, 22]))).astype(np.uint8))
k2.save(IMG / "kanit_2.jpg", quality=92)
olc(k2, "kanit_2")
