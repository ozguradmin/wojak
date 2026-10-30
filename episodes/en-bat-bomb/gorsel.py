"""en-bat-bomb görselleri: python episodes/en-bat-bomb/gorsel.py
Kaynaklar (hepsi kamu malı; ayrıntı yaml sources): LOC 2017878478 (arka plan, Palmer 1942 Kodachrome), Commons Carlsbad AAF Fire... (kanıt 2, son kare),
Commons Bat Bomb Canister (kanıt 1). Ham indirmeler img/ içinde kaynak_*.jpg adıyla durur.
"""
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

H = Path(__file__).resolve().parent / "img"

# arka plan: LOC Kodachrome (1a35097u.tif master) iç alanından kare kırpım (230,190,3310,3270), 1600 px kaydedildi -> 1080x1080
bg = Image.open(H / "kaynak_arka_plan_loc.jpg").convert("RGB").resize((1080, 1080), Image.LANCZOS)
bg.save(H / "bg.jpg", quality=93)

# kanıt 1: kovan (1081x426) -> 1080x540; nesnesiz üst/alt kenar, kumaş dokusu simetrik uzatılır (nesne yok)
c = np.array(Image.open(H / "kaynak_kanit_kovan.jpg").convert("RGB"))[:, :1080].astype(float)
rng = np.random.default_rng(7)


def _uzat(band, n, yukari):
    """Kenar bandının sütun ortalamasını yumuşatır, kumaş dokusuna benzer ince gürültü ekler; nesne yok."""
    from scipy.ndimage import gaussian_filter, gaussian_filter1d
    m = gaussian_filter1d(band.mean(0), 10, axis=0)
    sd = band.std(axis=(0, 1)).mean() * 0.55
    e = np.repeat(m[None], n, 0) + gaussian_filter(rng.normal(0, sd, (n, 1080, 3)), (0.7, 0.7, 0))
    return e


top = _uzat(c[:20], 57, True)
bot = _uzat(c[-30:], 57, False)
out = np.concatenate([top, c, bot], 0).clip(0, 255)
from scipy.ndimage import gaussian_filter
for y in (57, 57 + c.shape[0]):  # dikiş izlerini yumuşat
    band = slice(y - 14, y + 14)
    out[band] = gaussian_filter(out[band], (4, 0, 0))
out = out.astype(np.uint8)
Image.fromarray(out).filter(ImageFilter.GaussianBlur(0.5)).save(H / "kanit_1.jpg", quality=94)

# kanıt 2 (son kare): yangın fotoğrafı (791x1122) -> alt kısım kule + yanan bina, 791x598 -> 1080x816
f = Image.open(H / "kaynak_kanit_yangin.jpg").convert("L")
f = f.crop((0, 490, 791, 1088)).resize((1080, 816), Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.5)).convert("RGB")
f.save(H / "kanit_2.jpg", quality=94)
