"""sarayburnu-cuvallar: karakterler.

    python episodes/sarayburnu-cuvallar/chars/uret.py

dalgic_terli.png  A (dalgıç, sol): assets/kit/klasik/cok_terli.png, alttan 950 px'e kırpılır (sağ omuzdaki dikey kesik). Çıplak omuzlu klasik wojak; damlalar
                  yüzeye yeni çıkmış dalgıcın suyu gibi okunur (17. yy dalgıçları iç donuyla, başı açık inerdi:
                  İstanbul Ansiklopedisi "Dalgıç").
reis_emin.png,    B (gemi reisi, sağ): patrona-halil-1730/chars/patrona_emin.png ve patrona_sok.png (wojakland "Muslim 2
reis_sok.png      Wojak" tabanı, ters köşe yüzü o bölümde §10 tarifiyle çizildi). Patrona Halil ile karışmasın diye kırmızı
                  sarık bağlı bölge olarak krem/beyaza, mavi kaftan kahverengiye çevrilir (yalnız renk; çizgi ve gölge
                  değerleri korunur). Fes yok (1829 öncesi), yeşil sarık yok.
"""
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = Path(__file__).resolve().parent
SRC = HERE.parents[1] / "patrona-halil-1730" / "chars"


def renk_degistir(ad_kaynak: str, ad_hedef: str) -> None:
    im = Image.open(SRC / ad_kaynak).convert("RGBA")
    a = np.asarray(im).astype(np.float32)
    rgb = a[..., :3]
    hsv = np.asarray(im.convert("RGB").convert("HSV")).astype(np.float32)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    opak = a[..., 3] > 0
    H = im.height
    yy = np.arange(H)[:, None].repeat(im.width, 1)
    # kırmızı sarık: üst yarıda, kırmızı ton, doygun; en büyük bağlı bölgeler
    kirmizi = opak & ((h < 14) | (h > 240)) & (s > 90) & (v > 40) & (yy < H * 0.45)
    lab, n = ndimage.label(kirmizi)
    boy = ndimage.sum(kirmizi, lab, range(1, n + 1))
    sarik = np.isin(lab, [i + 1 for i, b in enumerate(boy) if b > 2000])
    bolge = ndimage.binary_fill_holes(ndimage.binary_dilation(sarik, iterations=40)) & opak & (yy < H * 0.45)
    sarik = bolge & ((h < 16) | (h > 228)) & (s > 35) & (v > 12)   # koyu kırmızı gölgeler de
    # mavi kaftan
    mavi = opak & (h > 130) & (h < 185) & (s > 50) & (v > 30) & (yy > H * 0.55)
    lab2, n2 = ndimage.label(mavi)
    boy2 = ndimage.sum(mavi, lab2, range(1, n2 + 1))
    kaftan = np.isin(lab2, [i + 1 for i, b in enumerate(boy2) if b > 3000])
    out = rgb.copy()
    lum = rgb.mean(axis=2, keepdims=True) / 255.0
    # sarık: krem (açık), gölgeler korunur
    k = np.clip(lum / max(lum[sarik].max(), 1e-3), 0, 1)
    krem = np.array([238, 228, 205], np.float32)
    golge = np.array([150, 138, 118], np.float32)
    out[sarik] = (golge + (krem - golge) * k[sarik] ** 0.6)
    # kaftan: kahverengi
    k2 = np.clip(lum / max(lum[kaftan].max(), 1e-3), 0, 1)
    acik = np.array([128, 88, 52], np.float32)
    koyu = np.array([60, 38, 22], np.float32)
    out[kaftan] = (koyu + (acik - koyu) * k2[kaftan])
    a[..., :3] = out
    Image.fromarray(a.clip(0, 255).astype(np.uint8)).save(HERE / ad_hedef)
    print(ad_hedef, im.size, "sarık px", int(sarik.sum()), "kaftan px", int(kaftan.sum()))


renk_degistir("patrona_emin.png", "reis_emin.png")
renk_degistir("patrona_sok.png", "reis_sok.png")
# Tur 1 görsel hakem MUST: kit PNG'sinin sağ alt köşesinde omuz dolgusu PNG kenarında dikey düz kesikle bitiyordu
# (y ~960-1022). Alt 72 px atılır; kalan alt kenar yataydır ve kadrajın alt kenarının altında kalır.
_d = Image.open(HERE.parents[2] / "assets" / "kit" / "klasik" / "cok_terli.png")
_d.crop((0, 0, _d.width, 950)).save(HERE / "dalgic_terli.png")
