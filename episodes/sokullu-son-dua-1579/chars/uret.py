"""sokullu-son-dua-1579: karakterler.

    python episodes/sokullu-son-dua-1579/chars/uret.py

Kaynaklar (chars/kaynak/):
  vezir_sakin.png     kanuni-gizlenen-olum bölümündeki sadrazam (wojakland "Sultan Chad"), 842x1036, sola bakar.
                      O bölümde de Sokullu'ya karşılık geliyordu: aynı sadrazam, 13 yıl sonra.
  hezarfen_emin.png   hezarfen-galata-ucusu'ndaki sarıklı adam (wojakland "Panjabi Muslim Chad"), profilden sağa bakar.
  hezarfen_sok.png    aynı adamın ters köşe yüzü (kalkık kaş, iri göz, açık ağız, alında mavi ter, damlalar), sağa bakar.
  (Tur 1'deki yeniçeri, görsel hakemin MUST'u üzerine çıkarıldı: ince kontur, eller yüzü kapatıyordu.)

Yapılan:
  - pasa: sadrazamın kahverengi sakal/saç rengi (75,40,18) bağlı bölgelerde kırçıla çevrildi (1579'da ~74 yaşında).
  - adam_sakin / adam_sok: kaynakların kendisi (paşayla aynı kalın kontur ailesi; varyant hezarfen bölümünde üretildi).
"""
from pathlib import Path

import numpy as np
from PIL import Image

D = Path(__file__).resolve().parent
K = D / "kaynak"


def pasa():
    im = np.array(Image.open(K / "vezir_sakin.png").convert("RGBA")).astype(int)
    rgb = im[..., :3]
    hedef = np.array([75, 40, 18])
    m = (np.abs(rgb - hedef).sum(axis=2) < 40) & (im[..., 3] > 0)
    im[m, 0], im[m, 1], im[m, 2] = 168, 166, 160
    Image.fromarray(im.astype(np.uint8)).save(D / "pasa_sakin.png")


def adam():
    for kaynak, ad in (("hezarfen_emin", "adam_sakin"), ("hezarfen_sok", "adam_sok")):
        Image.open(K / f"{kaynak}.png").convert("RGBA").save(D / f"{ad}.png")


if __name__ == "__main__":
    pasa()
    adam()
