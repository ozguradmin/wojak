"""hannibal-gebze-yedi-kapi: arka plan ve iki kanıt (kaynaklar img/kaynak_*.jpg; tools/commons.py ve Internet Archive).

    python episodes/hannibal-gebze-yedi-kapi/gorsel.py

arka.jpg     'Priene Hellenistic houses 2007 4276.jpg' (Dosseman, CC BY-SA 4.0): Priene'de Helenistik (MÖ 4.-2. yy) bir
             evin taş döşeli avlusu ve payeleri (aynı türden yer: Libyssa'daki ev bugün yok, yeri de tartışmalı).
             Kare kırpım, 1080'e küçültme, renk ve parlaklık ayarı (aşağıda).
kanit_1.jpg  'Hanibal's Tomb Gebze 19022022 01.jpg' (Yamen, CC BY-SA 4.0): Gebze'de TÜBİTAK arazisindeki 1981 tarihli
             sembolik Hannibal anıt mezarı, kaya blok içinde Hannibal kabartması. Soldaki uzak beyaz tabela dışarıda kalacak
             kırpım, 1080x810. (Tur 1 takipçi SHOULD için Türkçe kitabe karesi (06) denendi: 390 px'te okunmuyor, levhanın
             üstünde ağaç gölgesi; kabartma kaldı.)
kanit_2.jpg  Livius, The History of Rome, Books 37-end, çev. W. A. M'Devitte (George Bell & Sons, Londra 1900), s. 1848
             (XXXIX.51): "seven passages from his house ... the king's soldiers ... he called for poison ... Let us release
             the Romans from their long anxiety, since they think it too long to wait for the death of an old man."
             Internet Archive historyofrome04livy (kamu malı, 1929 öncesi), leaf 204, page/n203_w2000.jpg ->
             img/kaynak_livius.jpg. Tur 1 görsel MUST (yarım kelimeyle başlayıp bitiyordu): "him. Encircled by enemies" satırından
             "tory over one unarmed and betrayed. What an alteration has" satırına kadar 18 tam satır (hecelenmiş kelime
             ile başlamaz ve bitmez), 1080x743; tur 2 SHOULD: üst kenarda önceki satırın uzantısı kalmasın, alt satırın uzantıları kesilmesin diye y 478-1668. Tarama rengine dokunulmadı.
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


ARKA_KUTU = (330, 0, 1605, 1275)
arka = Image.open(IMG / "kaynak_arka.jpg").convert("RGB").crop(ARKA_KUTU).resize((1080, 1080), Image.LANCZOS)
arka = arka.point(lambda v: round(255 * (v / 255) ** 0.78))          # gölgeleri aç (gama 0,78)
arka = ImageEnhance.Brightness(ImageEnhance.Color(arka).enhance(1.15)).enhance(1.1)
arka.save(IMG / "arka.jpg", quality=92)
olc(arka, "arka")

k1 = Image.open(IMG / "kaynak_anit.jpg").convert("RGB").crop((260, 240, 1560, 1215)).resize((1080, 810), Image.LANCZOS)
k1.save(IMG / "kanit_1.jpg", quality=92)
olc(k1, "kanit_1")

k2 = Image.open(IMG / "kaynak_livius.jpg").convert("RGB").crop((280, 478, 2010, 1668))
k2 = k2.resize((1080, round(k2.height * 1080 / k2.width)), Image.LANCZOS)
k2.save(IMG / "kanit_2.jpg", quality=92)
olc(k2, "kanit_2")
