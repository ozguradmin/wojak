"""vezir-bostanci-kosusu görselleri: arka plan + iki kanıt (yalnız kırpım, ölçek, rötuş, renk; üretken model yok).

    python episodes/vezir-bostanci-kosusu/gorsel.py
"""
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageOps

D = Path(__file__).resolve().parent / "img"

# Arka plan: 'Topkapi - Mittleres Tor.jpg' (Rabe!, CC BY-SA 3.0), 1920x1280 küçük resim. Orta Kapı (Babüsselam): anlatıya
# göre ölüm hükmü bostancıbaşına bu kapıda verilirdi. Kare kırpım (425,90)-(1505,1170): alt şeritteki yürüyen ziyaretçiler,
# zemin spotları ve çimdeki armatürler kadraj dışında. Kapının üstündeki modern bayrak ve direği OpenCV inpaint (Telea,
# klasik rötuş) ile gökyüzü/mazgalla dolduruldu.
src = Image.open(D / "kaynak_arka_ortakapi.jpg").convert("RGB")
arr = np.asarray(src).copy()
mask = np.zeros(arr.shape[:2], np.uint8)
cv2.rectangle(mask, (910, 538), (962, 632), 255, -1)      # bayrak
cv2.rectangle(mask, (947, 536), (960, 768), 255, -1)      # direk (mazgalların arasına kadar)
bgr = cv2.inpaint(cv2.cvtColor(arr, cv2.COLOR_RGB2BGR), mask, 9, cv2.INPAINT_TELEA)
im = Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)).crop((425, 90, 1505, 1170))
im = ImageEnhance.Color(im).enhance(0.80)
im = ImageEnhance.Brightness(im).enhance(0.86)
im.save(D / "arka.jpg", quality=92)

# Kanıt 1: '29 - Bostangi.jpg' — Octavien Dalvimart, The Military Costume of Turkey (Londra, Thomas McLean, 1813), kamu malı.
# Figüre sıkı kırpım (külah ucu - ayakkabı), büyütmeden 816 px yüksekliğe sığdırıldı; yanlar levhanın kâğıt rengiyle 1080'e
# tamamlandı; levhanın beyaz kâğıdı telefonda flaş gibi parlamasın diye bütün kare eski kâğıt tonuyla çarpıldı (krem).
fg = Image.open(D / "kaynak_bostangi_1813.jpg").convert("RGB")
fg = fg.crop((40, 50, 680, 820))
s_ = 816 / fg.height
fg = fg.resize((round(fg.width * s_), 816), Image.LANCZOS)
k1 = Image.new("RGB", (1080, 816), (255, 255, 255))
k1.paste(fg, ((1080 - fg.width) // 2, 0))
krem = np.array([238, 226, 200], np.float32) / 255.0
k1 = Image.fromarray((np.asarray(k1).astype(np.float32) * krem).clip(0, 255).astype(np.uint8))
k1.save(D / "kanit_1.jpg", quality=92)

# Kanıt 2 (son kare): 'Carte de Constantinople - Levée par F. Kauffer et J.B. Lechevalier - btv1b10100568w.jpg' — François
# Kauffer ve J.-B. Lechevalier, "Carte de Constantinople, l'an 1786", BnF, kamu malı. Özgün 11968x7666 dosyadan Sarayburnu
# bölümü (5900,3000)-(7300,4800) kaynak_kauffer_1786_serail.jpg olarak saklandı; buradan Topkapı: "PALAIS DU Gd SEIGNEUR",
# "Orta Kapou", deniz surları ve "Indgiouli Keuchk" (İncili Köşk; Balıkhane Kapısı bu sur boyunda) okunur kırpım, 1,35x.
pl = Image.open(D / "kaynak_kauffer_1786_serail.jpg").convert("RGB")
k2 = pl.crop((270, 600, 1070, 1204))                      # 800x604 -> 1080x815
k2 = k2.resize((1080, round(k2.height * 1080 / k2.width)), Image.LANCZOS)
k2 = ImageOps.autocontrast(k2, cutoff=0.3)
k2.save(D / "kanit_2.jpg", quality=92)

for ad in ("arka", "kanit_1", "kanit_2"):
    x = Image.open(D / f"{ad}.jpg")
    a = np.asarray(x.convert("HSV")).astype(float)
    g = np.asarray(x.convert("L").resize((720, round(720 * x.height / x.width))), dtype=float)
    lap = (np.roll(g, 1, 0) + np.roll(g, -1, 0) + np.roll(g, 1, 1) + np.roll(g, -1, 1) - 4 * g)[2:-2, 2:-2]
    print(f"{ad}: {x.size} parlaklik {a[..., 2].mean():.0f} doygunluk {a[..., 1].mean() / 255:.2f} laplace {lap.var():.0f}")
