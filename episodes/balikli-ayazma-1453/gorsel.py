"""balikli-ayazma-1453: arka plan ve iki kanıt (kaynaklar img/kaynak_*.jpg; tools/commons.py ve Internet Archive).

    python episodes/balikli-ayazma-1453/gorsel.py

arka.jpg     'Church of St. Mary of the Spring 9133.jpg' (Dosseman, CC BY-SA 4.0): Balıklı Ayazması'nın mahzeni, mermer
             sütunlar, tuğla kemer, ikon nişi ve mermer çeşme teknesi. Kare kırpım (1026 px -> 1080; sol duvardaki kablo, mum rafı, plastik
             şişeler ve tavandaki avize dışarıda), 1080'e küçültme, renk ve parlaklık ayarı (renk 0,55, parlaklık 1,17).
kanit_1.jpg  'Turkey, Istanbul, Zoodochos Pege (Fish Church) (3946146620).jpg' (Dave Proffer, 2006, CC BY 2.0): ayazmanın
             havuzunda yüzen kırmızı-turuncu balık. Tur 1-2 (takipçi MUST, görsel SHOULD: tek küçük karanlık balık, üstte siyah direk): balığa
             yakın 590x393 kırpım, MedianFilter(3) -> 1080x720 (1,83x), gama 0,55 + parlaklık 1,12.
kanit_2.jpg  Son kare. 'People visiting the spring of the "miraculous fishes" at Bal Wellcome V0020099.jpg' (Commons; Thomas
             Allom çizimi, J. Tingle gravürü, 1830'lar, R. Walsh "Constantinople and the Scenery of the Seven Churches of Asia
             Minor"; Wellcome Collection taraması CC BY 4.0): gravürün alt yarısı (kaynaktan su içen ziyaretçiler) ve basılı
             alt yazısı "Spring of the Miraculous Fishes, at Baloukli". Kırpım (147,1450,1768,2545), autocontrast(1/0,3,
             tonu koruyarak), 1080x730. Tur 1 görsel MUST: De Amicis 1878 s. 259 kitap sayfası telefonda okunmuyordu
             (büyük harf ~20 px), çıkarıldı; sayfa img/kaynak_amicis_259.jpg olarak kaynakta durur.
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

IMG = Path(__file__).resolve().parent / "img"


def olc(im, ad):
    a = np.asarray(im.convert("RGB")).astype(float)
    hsv = np.asarray(im.convert("HSV")).astype(float)
    k = im.convert("L").resize((720, round(720 * im.height / im.width)))
    lap = np.asarray(k.filter(ImageFilter.FIND_EDGES)).astype(float).var()
    print(f"{ad}: {im.size} parlaklık {a.mean():.0f} doygunluk {hsv[..., 1].mean() / 255:.2f} kenar var {lap:.0f}")


ARKA_KUTU = (450, 252, 1476, 1278)   # tavandaki demir çubuklar da dışarıda
arka = Image.open(IMG / "kaynak_arka.jpg").convert("RGB").crop(ARKA_KUTU).resize((1080, 1080), Image.LANCZOS)


def yama(im, hedef, dx, dy=0, yumusak=6):
    """hedef kutusunu (x0, y0, x1, y1) aynı satırdaki komşu bölgeden (dx, dy kaydırılmış) yumuşak maskeyle örter."""
    x0, y0, x1, y1 = hedef
    parca = im.crop((x0 + dx, y0 + dy, x1 + dx, y1 + dy))
    m = Image.new("L", parca.size, 0)
    ImageDraw.Draw(m).rectangle((yumusak, yumusak, parca.width - yumusak, parca.height - yumusak), fill=255)
    im.paste(parca, (x0, y0), m.filter(ImageFilter.GaussianBlur(yumusak / 2)))


# tur 1 görsel MUST: teknenin üstündeki tepsi + iki gümüş kupa ve teknenin dört musluk başı komşu mermerden yamayla örtülür
yama(arka, (462, 588, 636, 656), -190)
for x0 in (82, 232, 386, 536):
    yama(arka, (x0, 736, x0 + 62, 826), 70)
# renk: sıcak sepya döküm azaltılır (mermer nötr gri-beyaza yaklaşır), sonra doygunluk/parlaklık
r, g, b = arka.split()
arka = Image.merge("RGB", (r.point(lambda v: round(v * 0.93)), g.point(lambda v: round(v * 0.98)), b.point(lambda v: min(255, round(v * 1.10)))))
arka = ImageEnhance.Brightness(ImageEnhance.Color(arka).enhance(0.85)).enhance(1.12)
arka.save(IMG / "arka.jpg", quality=92)
olc(arka, "arka")

k1 = Image.open(IMG / "kaynak_gravur.jpg").convert("RGB").crop((147, 1450, 1768, 2545))
k1 = ImageOps.autocontrast(k1, cutoff=(1, 0.3), preserve_tone=True)
k1 = k1.resize((1080, round(k1.height * 1080 / k1.width)), Image.LANCZOS)
k1.save(IMG / "kanit_2.jpg", quality=92)   # son kare
olc(k1, "kanit_2")

k2 = Image.open(IMG / "kaynak_balik.jpg").convert("RGB").crop((700, 1632, 1290, 2025))   # tur 2: üstteki siyah direk dışarıda
k2 = k2.filter(ImageFilter.MedianFilter(3)).resize((1080, 720), Image.LANCZOS)   # tur 2: gren azaltma, 1,83x
k2 = k2.point(lambda v: round(255 * (v / 255) ** 0.55))          # karanlık havuzu aç (gama 0,55)
k2 = ImageEnhance.Brightness(k2).enhance(1.12)
k2.save(IMG / "kanit_1.jpg", quality=92)
olc(k2, "kanit_1")
