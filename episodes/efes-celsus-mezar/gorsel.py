"""efes-celsus-mezar görselleri: arka plan + kanıt 1 (kaynak dosyalardan; yalnız kırpım, ölçek, renk/kontrast). Kanıt 2: belge.py."""
from pathlib import Path
from PIL import Image, ImageEnhance, ImageOps, ImageFilter
import numpy as np

D = Path(__file__).resolve().parent / "img"

# Arka plan: 'Ephesus Celsus Library Façade.jpg' (Benh LIEU SONG, CC BY-SA 3.0). Özgün 9163x7100 dosyadan üst bölümden kare
# kırpım (2291,406,6873,4988; 1920'lik küçük resimde 480,85,1440,1045), 1620'ye küçültülüp kaynak_arka_cephe_kare.jpg olarak
# saklandı (özgün 15 MB, depoya girmez). Alt kattaki kapılarda oturan/duran ziyaretçiler ve merdivendeki turistler kadraj dışında.
im = Image.open(D / "kaynak_arka_cephe_kare.jpg").convert("RGB")
im = im.resize((1080, 1080), Image.LANCZOS)
im = ImageEnhance.Color(im).enhance(0.72)
im = ImageEnhance.Brightness(im).enhance(0.93)
im.save(D / "arka.jpg", quality=92)

# Kanıt 1: Heberdey 1905 (ÖJh 8, Beiblatt Sp. 63-64), Fig. 15 "Ansicht der Ruine" — 1904 kazısında kütüphane kalıntısı.
pg = Image.open(D / "kaynak_heberdey1905_sp63.jpg").convert("L")
FIG15 = (324, 320, 1836, 1322)   # yalnız fotoğraf (sayfa başlığı, kenar ve alt yazı dışarıda); satır/sütun yoğunluğuyla ölçüldü
k1 = pg.crop(FIG15)
k1 = ImageOps.autocontrast(k1, cutoff=0.5)
w, h = k1.size
k1 = k1.resize((1080, round(h * 1080 / w)), Image.LANCZOS)
k1.convert("RGB").save(D / "kanit_1.jpg", quality=92)

# Kanıt 2 (son kare): belge.py üretir (Belleten, Ekim 1979 cümlesinin yeniden dizilmiş sayfa yakın çekimi).

for ad in ("arka", "kanit_1"):
    x = Image.open(D / f"{ad}.jpg")
    a = np.asarray(x.convert("HSV")).astype(float)
    g = np.asarray(x.convert("L").resize((720, round(720 * x.height / x.width))), dtype=float)
    lap = (np.roll(g, 1, 0) + np.roll(g, -1, 0) + np.roll(g, 1, 1) + np.roll(g, -1, 1) - 4 * g)[2:-2, 2:-2]
    print(f"{ad}: {x.size} parlaklik {a[...,2].mean():.0f} doygunluk {a[...,1].mean()/255:.2f} laplace {lap.var():.0f}")
