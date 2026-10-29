"""schliemann-sal-1873: arka plan ve kanıt görsellerini kaynaklardan hazırlar.

Kaynaklar (orijinal tam dosyalar /tmp/sal_kaynak altında; repoya girmez, adresten yeniden indirilir):
  arka_2.jpg          File:Troy east tower 7865.jpg (Dosseman, 23.05.2014, CC BY-SA 4.0), 4928x3280
                      https://commons.wikimedia.org/wiki/File:Troy_east_tower_7865.jpg                -> arka plan
  kanit_hazine_1.jpg  Schliemann, Troy and Its Remains (Londra, 1875), Levha II "General View of the Treasure of
                      Priam" (gravür, kamu malı); Internet Archive troyitsremainsna00schl, yaprak n84 (_w2000)
                      https://archive.org/details/troyitsremainsna00schl/page/n84                        -> kanıt 1
  kanit_sophia_1.jpg  File:Sophia Schliemann wearing Treasure A, Troy.jpg (fotoğrafçı bilinmiyor, 1873-1877;
                      PD-old-70-1923), 1120x1656
                      https://commons.wikimedia.org/wiki/File:Sophia_Schliemann_wearing_Treasure_A,_Troy.jpg -> kanıt 2
Çalıştır: python episodes/schliemann-sal-1873/gorsel.py
"""
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

D = Path(__file__).parent / "img"
K = Path("/tmp/sal_kaynak")


def arka():
    # sol üst kare: alt-soldaki ahşap korkuluk (y>3140) ve sağ kenardaki direk kırpım dışında
    p = Image.open(K / "arka_2.jpg").convert("RGB").crop((0, 0, 3000, 3000))
    p = p.resize((1080, 1080), Image.LANCZOS)
    p = ImageEnhance.Color(p).enhance(1.35)       # doygunluk 0,16 -> ~0,22 (taş gri kalır, çimen canlanır)
    p = ImageEnhance.Brightness(p).enhance(0.98)
    p.save(D / "arka_truva.jpg", quality=92)


def kanit1():
    # levhanın üst iki rafı + takı panoları; raf çizgisinde biter, "Plate II" ve alt yazı dışarıda
    p = Image.open(K / "kanit_hazine_1.jpg").convert("RGB").crop((186, 403, 186 + 1682, 403 + 1195))
    p = p.resize((1080, 767), Image.LANCZOS)
    p = ImageOps.autocontrast(p, cutoff=(0.5, 0.5))
    p.save(D / "kanit_1_levha_1875.jpg", quality=92)


def kanit2():
    # baş süsü, yüz ve küpeler; sol kenardaki gri sayfa gradyanı dışarıda (x>=100); 1080 genişliğe ~1,06x
    p = Image.open(K / "kanit_sophia_1.jpg").convert("L").crop((100, 205, 100 + 1020, 205 + 771))
    p = p.filter(ImageFilter.MedianFilter(3))     # kaba yarı ton nokta desenini yumuşatır
    p = p.resize((1080, 816), Image.LANCZOS)
    # yarı ton taramada gölgeler ezik (gözler siyah leke): gölge açma; manşet/metin yok
    p = ImageOps.autocontrast(p, cutoff=(0.2, 0.3))
    p = p.point(lambda v: round(255 * (v / 255) ** (1 / 1.45)))
    p = p.convert("RGB")
    p.save(D / "kanit_2_sophia.jpg", quality=92)


if __name__ == "__main__":
    D.mkdir(exist_ok=True)
    arka()
    kanit1()
    kanit2()
    for f in sorted(D.glob("*.jpg")):
        print(f.name, Image.open(f).size)
