"""vezir-bostanci-kosusu: karakterler.

    python episodes/vezir-bostanci-kosusu/chars/uret.py

bostanci_emin.png,  A (bostancıbaşı, sol): patrona-halil-1730/chars/patrona_emin.png ve patrona_sok.png (wojakland "Muslim 2
bostanci_sok.png    Wojak" tabanı; ters köşe yüzü o bölümde §10 tarifiyle çizildi). Kırmızı sarık kalır (bostancıların
                    kırmızı başlığı; Dalvimart 1813 levhasındaki kırmızı külahla aynı renk), mavi kaftan Dalvimart'taki yeşil
                    dolamaya çevrilir (yalnız renk; çizgi ve gölge değerleri korunur). Fes yok (1829 öncesi).
pasa_sakin.png      B (sadrazam, sağ): sokullu-son-dua-1579/chars/pasa_sakin.png (wojakland "Sultan Chad" tabanı, ak sakallı,
                    büyük beyaz kavuk), değişiklik yok.
"""
import shutil
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = Path(__file__).resolve().parent
EP = HERE.parents[1]


def kaftan_yesil(ad_kaynak: str, ad_hedef: str) -> None:
    im = Image.open(EP / "patrona-halil-1730" / "chars" / ad_kaynak).convert("RGBA")
    a = np.asarray(im).astype(np.float32)
    rgb = a[..., :3]
    hsv = np.asarray(im.convert("RGB").convert("HSV")).astype(np.float32)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    opak = a[..., 3] > 0
    H = im.height
    yy = np.arange(H)[:, None].repeat(im.width, 1)
    mavi = opak & (h > 130) & (h < 185) & (s > 50) & (v > 30) & (yy > H * 0.55)
    lab, n = ndimage.label(mavi)
    boy = ndimage.sum(mavi, lab, range(1, n + 1))
    kaftan = np.isin(lab, [i + 1 for i, b in enumerate(boy) if b > 3000])
    lum = rgb.mean(axis=2, keepdims=True) / 255.0
    k = np.clip(lum / max(lum[kaftan].max(), 1e-3), 0, 1)
    acik = np.array([58, 112, 74], np.float32)
    koyu = np.array([22, 52, 32], np.float32)
    out = rgb.copy()
    out[kaftan] = koyu + (acik - koyu) * k[kaftan]
    a[..., :3] = out
    Image.fromarray(a.clip(0, 255).astype(np.uint8)).save(HERE / ad_hedef)
    print(ad_hedef, im.size, "kaftan px", int(kaftan.sum()))


kaftan_yesil("patrona_emin.png", "bostanci_emin.png")
kaftan_yesil("patrona_sok.png", "bostanci_sok.png")
shutil.copy(EP / "sokullu-son-dua-1579" / "chars" / "pasa_sakin.png", HERE / "pasa_sakin.png")
