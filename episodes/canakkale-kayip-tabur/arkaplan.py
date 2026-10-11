"""v5 arka planları (sahne 1-3: bulut + tabur kolu; sahne 5: aynı kare, bulut ve tabur yok).

    python episodes/canakkale-kayip-tabur/arkaplan.py [ara_dosya_klasörü]

Kaynak: img/suvla_bulutlu.jpg (Tevfik Teker, "Suvla Bay", CC BY 3.0, 2592x1944, değiştirilmemiş).
1. Renk: ImageEnhance.Color(1.35) ardından Brightness(1.10) (doğal gün ışığı, doygunluk ~0,15).
2. Bulut katmanı bu düzeltilmiş görselden üretilir: sis_katmani.py --mode fog --seed 11 --col 222.
3. İki görsel aynı kare kutuya kırpılır: (820, 644, 2120, 1944), 1300x1300 kaynak px.
4. Yalnız bulutlu kareye: ovadan buluta yürüyen 18 düz koyu (#2a2a24) asker siluetinden kol (24 -> 18 px) (STIL §6 ek katman,
   C1Xe/C2-U'daki yapıştırılmış hikâye öğeleri gibi); öndeki 3-4 asker bulutun içinde söner.
Çıktılar: img/suvla_bulut_inmis_kare.jpg (sahne 1-3), img/suvla_bos_kare.jpg (sahne 5).
"""
import subprocess
import tempfile
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance

EP = Path(__file__).resolve().parent
IMG = EP / "img"
TMP = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(tempfile.mkdtemp())
TMP.mkdir(parents=True, exist_ok=True)
BOX = (820, 644, 2120, 1944)
SIL = (42, 42, 36)

src = Image.open(IMG / "suvla_bulutlu.jpg").convert("RGB")
enh = ImageEnhance.Brightness(ImageEnhance.Contrast(ImageEnhance.Color(src).enhance(1.6)).enhance(1.08)).enhance(1.05)
enh_p = TMP / "suvla_renk.png"
fog_p = TMP / "suvla_renk_bulut.png"
enh.save(enh_p)
subprocess.run([sys.executable, str(EP / "sis_katmani.py"), str(enh_p), str(fog_p.with_suffix(".jpg")),
                "--mode", "fog", "--seed", "11", "--col", "222", "--alpha", str(TMP / "bulut_alfa.png")], check=True)
fog = Image.open(fog_p.with_suffix(".jpg")).convert("RGB")
alpha = np.asarray(Image.open(TMP / "bulut_alfa.png"), np.float32) / 255.0

bos = enh.crop(BOX)
bulut = fog.crop(BOX)
alpha_c = alpha[BOX[1]:BOX[3], BOX[0]:BOX[2]]


# ---------- tabur kolu ----------
SS = 4


def soldier(d, x, y, h, rifle, step):
    """Düz koyu siluet: (x, y) ayak tabanı ortası, h boy (px). Sağa (buluta) doğru yürür."""
    s = h / 20.0
    P = lambda px, py: ((x + px * s) * SS, (y - py * s) * SS)
    # mantar miğfer: kubbe + geniş siperlik
    d.ellipse([*P(-3.0, 21.0), *P(3.0, 15.8)], fill=SIL)
    d.polygon([P(-4.6, 16.8), P(4.8, 16.8), P(4.4, 15.4), P(-4.2, 15.4)], fill=SIL)
    # baş + boyun
    d.ellipse([*P(-1.9, 16.6), *P(2.1, 12.6)], fill=SIL)
    # gövde (öne eğik) + sırt çantası
    d.polygon([P(-2.8, 13.6), P(2.6, 13.8), P(2.8, 7.4), P(-2.4, 7.2)], fill=SIL)
    d.polygon([P(-4.6, 13.2), P(-2.2, 13.4), P(-2.2, 8.6), P(-4.4, 8.8)], fill=SIL)
    # bacaklar (geniş adım)
    st = 3.0 + step
    d.polygon([P(-2.0, 7.8), P(0.4, 7.8), P(-st + 1.0, 0), P(-st - 1.0, 0)], fill=SIL)
    d.polygon([P(-0.4, 7.8), P(2.2, 7.8), P(st + 1.2, 0), P(st - 0.8, 0)], fill=SIL)
    # tüfek omuzda (namlu yukarı-geri, başın üstüne taşar)
    if rifle:
        d.line([P(2.2, 9.0), P(-2.6, 24.0)], fill=SIL, width=max(1, round(1.3 * s * SS)))


H, W = alpha_c.shape
lay = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
d = ImageDraw.Draw(lay)
# kare (1080) koordinatı -> kırpım (1300) koordinatı
k = 1300 / 1080
# kol: bulutun alt kenarındaki açık yamaçtan (kare ~ x 495, y 650) sağ-yukarı bulutun içine (kare ~ x 640, y 560);
# iki karakter kutusunun (x 0-450 ve 650-1080) ve yazı bloğunun (y 321-434) arasında kalır.
# final-3 (görsel hakem 7,5/10): 18 siluet, boy kırpımda 24 -> 18 px (ekranda ~20 -> 15 px). Önceki 11 x 38 -> 30 px
# siluet, çevresindeki 6-10 px'lik ağaç tepelerinin yanında 2x'te "yapıştırılmış dev" gibi duruyordu; daha uzun kol
# "tabur" olarak da daha iyi okunur.
N = 18
start, end = np.array([495.0, 650.0]), np.array([640.0, 560.0])
rng = np.random.default_rng(5)
figs = []
for i in range(N):
    t = i / (N - 1)
    p = (start + (end - start) * t) * k
    p[1] += 6 * np.sin(t * np.pi * 1.6) * k      # yamaçta hafif kıvrılan patika
    p += rng.normal(0, 1.0, 2)
    h = 24.0 - 6.0 * t + rng.normal(0, 0.5)   # uzaklaştıkça küçülür
    figs.append((p[0], p[1], h, i % 4 != 2, rng.uniform(-0.6, 0.8), i))
# uzaktakiler önce çizilir
for x, y, h, rifle, step, i in sorted(figs, key=lambda f: f[1]):
    soldier(d, x, y, h, rifle, step)
lay = lay.resize((W, H), Image.LANCZOS)
la = np.asarray(lay, np.float32)
sa = la[..., 3] / 255.0
# bulutun içine giren öndeki 3-4 asker söner (bulut alfası 0,42'nin üstünde siluet giderek kaybolur)
vis = sa * np.clip(1 - 2.6 * np.clip(alpha_c - 0.42, 0, None), 0, 1)
b = np.asarray(bulut, np.float32)
out = b * (1 - vis[..., None]) + np.array(SIL, np.float32) * vis[..., None]
bulut_t = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))

bulut_t.save(IMG / "suvla_bulut_inmis_kare.jpg", quality=93)
bos.save(IMG / "suvla_bos_kare.jpg", quality=93)
for n, im in (("bulut", bulut_t), ("bos", bos)):
    a = np.asarray(im.convert("RGB"), np.float32)
    hsv = np.asarray(im.convert("HSV"), np.float32)
    print(n, "lum %.0f" % (0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]).mean(),
          "sat %.3f" % (hsv[..., 1].mean() / 255), "üst üçte bir lum %.0f" % a[: H // 3].mean())
print("bulut kaplama (alfa>0.35): %.2f" % (alpha_c > 0.35).mean())
