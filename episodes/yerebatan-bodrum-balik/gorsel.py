"""yerebatan-bodrum-balik: arka plan ve kanıt görsellerini serbest kaynaklardan hazırlar (piksellere ekleme yok).

    python episodes/yerebatan-bodrum-balik/gorsel.py <indirme_klasoru>

Girdi (indirme klasöründe; lisanslar episode.yaml `sources`'ta):
  yerebatan_kadi.jpg      Commons "Yerebatan Sarnıcı (20230126) - 52650182332.jpg" (Kadı Kadı, CC BY 2.0), 1920x2560 küçük resim
  medusa_jarvis.jpg       Commons "Turkey-03561 - Medusa Head (11314887606).jpg" (Dennis G. Jarvis, CC BY-SA 2.0), 1920x2880
  gyllius_1729_s147.jpg   Internet Archive "antiquitiesofcon00gill" s. 147 (Petrus Gyllius, The Antiquities of Constantinople,
                          çev. John Ball, Londra 1729; kamu malı), 1711x2922
Çıktı: img/arka_sarnic.jpg (1080x1080), img/kanit_1_medusa.jpg (1080x816), img/kanit_2_gyllius.jpg (1080x816)
"""
import sys
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps

HERE = Path(__file__).resolve().parent
SRC = Path(sys.argv[1] if len(sys.argv) > 1 else HERE / "img" / "kaynak")
OUT = HERE / "img"


def arka():
    im = Image.open(SRC / "yerebatan_kadi.jpg").convert("RGB")
    # Sarnıcın içi: sütun sıraları, tuğla tonozlar, suda yansıma. Kaçış noktası ortanın biraz üstünde; sağdaki modern
    # yürüme yolu korkuluğu (x >= ~1395) kadraj dışında kalır.
    im = im.crop((0, 560, 1380, 1940)).resize((1080, 1080), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(0.6)  # doygunluk ~0,33 -> ~0,23 (orijinallerin diyalog karesi ~0,20)
    im.save(OUT / "arka_sarnic.jpg", quality=92)


def kanit1():
    im = Image.open(SRC / "medusa_jarvis.jpg").convert("RGB")
    # Ters konmuş Medusa başı (sütun kaidesi). Çene üstte, gözler altta; üstteki merdiven ve ziyaretçiler kadraj dışında.
    w = im.width
    h = round(w * 816 / 1080)
    y0 = 1250
    im.crop((0, y0, w, y0 + h)).resize((1080, 816), Image.LANCZOS).save(OUT / "kanit_1_medusa.jpg", quality=92)


def kanit2():
    im = Image.open(SRC / "gyllius_1729_s147.jpg").convert("RGB")
    # Gyllius'un kitabı (1729 İngilizce çevirisi), s. 147: "The People had not the least Suspicion of it, although they
    # daily drew their Water out of the Wells ... He was very intent upon catching his Fish". Yalnız kırpım + seviye.
    box = KANIT2_KUTU
    im = im.crop(box).resize((1080, 816), Image.LANCZOS)
    im = ImageOps.autocontrast(im, cutoff=(0.5, 0.2))
    im.save(OUT / "kanit_2_gyllius.jpg", quality=92)


KANIT2_KUTU = (60, 792, 1540, 1910)

if __name__ == "__main__":
    arka()
    kanit1()
    kanit2()
    print("img/ hazır")
