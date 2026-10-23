"""ayasofya-viking-yazisi: arka plan ve kanıt görselleri (gerçek fotoğraflar; yapay zekâ yok, kendi üretimimiz yok).

    python episodes/ayasofya-viking-yazisi/gorsel.py

Ham dosyalar .cache/ayasofya-viking-yazisi/ altına iner (git'e girmez; Wikimedia istekleri arasında >= 12 sn,
özgün dosyanın md5 yolu). Çıktılar:
  img/arka_galeri.jpg     diyalog arka planı: Ayasofya üst galerisi, mermer korkuluk, sütunlar ve nef (Commons
                          "Hagia Sophia upper gallery NE side to right of Loge of the Empress in 2004 4673.jpg",
                          Dosseman, CC BY-SA 4.0)
  img/kanit_1_runler.jpg  kanıt 1: güney galerideki mermer korkulukta, pleksiglas altındaki runik yazı (Commons
                          "PXL 20241210 064800376.MP ... Halfdan inscription Viking runic inscription 23.jpg",
                          Sourabh.biswas003, CC BY-SA 4.0)
  img/kanit_2_levha.jpg   kanıt 2 (son kare): aynı yazı ve üstündeki müze levhası "9. yy'a tarihlenen Viking'ce yazı
                          ....HALVDAN....adı okunabilmektedir" (Commons "Hagia-sofia-viking.jpg", 2005, kamu malı)
Kanıtlarda yalnız kırpım, 1080 genişliğe ölçek ve genel ton (parlaklık/kontrast) ayarı; piksel boyama yok.
"""
from __future__ import annotations

import hashlib
import time
import urllib.parse
from pathlib import Path

import numpy as np
import requests
from PIL import Image, ImageEnhance

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CACHE = ROOT / ".cache" / "ayasofya-viking-yazisi"
IMG = HERE / "img"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}


def commons(ad: str) -> str:
    n = ad.replace(" ", "_")
    h = hashlib.md5(n.encode()).hexdigest()
    return f"https://upload.wikimedia.org/wikipedia/commons/{h[0]}/{h[:2]}/{urllib.parse.quote(n)}"


HAM = {
    "galeri_ne_4673.jpg": commons("Hagia Sophia upper gallery NE side to right of Loge of the Empress in 2004 4673.jpg"),
    "halfdan_23.jpg": commons("PXL 20241210 064800376.MP Hagia Sophia Grand Mosque Ayasofya-i Kebir Cami-i Şerifi "
                              "Istanbul Turkey Halfdan inscription Viking runic inscription 23.jpg"),
    "hagia_sofia_viking.jpg": commons("Hagia-sofia-viking.jpg"),
}


def indir():
    CACHE.mkdir(parents=True, exist_ok=True)
    for ad, url in HAM.items():
        f = CACHE / ad
        if f.exists():
            continue
        for _ in range(5):
            r = requests.get(url, headers=UA, timeout=60)
            if r.status_code == 200:
                f.write_bytes(r.content)
                break
            time.sleep(15)
        else:
            raise SystemExit(f"indirilemedi: {url}")
        time.sleep(12)


def olc(im: Image.Image) -> str:
    a = np.asarray(im.convert("RGB")).astype(np.float32) / 255
    mx, mn = a.max(-1), a.min(-1)
    doy = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    return f"parlaklık {a.mean() * 255:.0f}, doygunluk {doy.mean():.2f}"


def gama(im: Image.Image, g: float) -> Image.Image:
    lut = [round(255 * (i / 255) ** g) for i in range(256)]
    return im.point(lut * 3)


def arka():
    im = Image.open(CACHE / "galeri_ne_4673.jpg").convert("RGB")   # 3008x2000; korkuluk + sütunlar x>1100
    im = im.crop((1008, 0, 3008, 2000)).resize((1080, 1080), Image.LANCZOS)
    im = gama(im, 0.72)                                             # karanlık iç mekân: ~74 -> ~115
    im = ImageEnhance.Contrast(im).enhance(1.05)
    im.save(IMG / "arka_galeri.jpg", quality=92)
    print("arka_galeri.jpg", im.size, olc(im))


def kanit_1():
    im = Image.open(CACHE / "halfdan_23.jpg").convert("RGB")       # 4080x3072
    im = im.crop((900, 640, 3700, 2215))   # runler y~1700 büyük okunsun (telefon); üstte korkuluk kenarı
    im = im.resize((1080, round(im.height * 1080 / im.width)), Image.LANCZOS)
    im.save(IMG / "kanit_1_runler.jpg", quality=93)
    print("kanit_1_runler.jpg", im.size, olc(im))


def kanit_2():
    im = Image.open(CACHE / "hagia_sofia_viking.jpg").convert("RGB")   # 1600x1200; üstü karanlık korkuluk demiri
    im = im.crop((230, 250, 1430, 1000))   # levha + runler; telefonda levha yazısı okunsun
    im = im.resize((1080, round(im.height * 1080 / im.width)), Image.LANCZOS)
    im = gama(im, 0.9)
    im = ImageEnhance.Contrast(im).enhance(1.08)
    im.save(IMG / "kanit_2_levha.jpg", quality=93)
    print("kanit_2_levha.jpg", im.size, olc(im))


if __name__ == "__main__":
    IMG.mkdir(exist_ok=True)
    indir()
    arka()
    kanit_1()
    kanit_2()
