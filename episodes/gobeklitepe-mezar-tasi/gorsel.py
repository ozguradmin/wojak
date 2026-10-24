"""gobeklitepe-mezar-tasi: arka plan ve kanıt 1 (gerçek fotoğraflar; yapay zekâ yok).

    python episodes/gobeklitepe-mezar-tasi/gorsel.py

Ham dosyalar .cache/gobeklitepe-mezar-tasi/ altına iner (git'e girmez; Wikimedia istekleri arasında >= 12 sn,
özgün dosyanın md5 yolu). Lisanslar Commons dosya sayfasının ham metninden (action=raw) doğrulandı, 24.10.2026.
Çıktılar:
  img/arka_dilek_agaci.jpg   diyalog arka planı: Göbeklitepe'nin tepesindeki dilek ağacı (Dosseman, 2014, CC BY-SA 4.0)
  img/kanit_1_tapinak.jpg    kanıt 1: kazılmış D yapısı, T biçimli dikilitaşlar (Kerimbesler, 2021, CC BY-SA 4.0)
  img/kanit_2_kupur.jpg      kanıt 2 (son kare): kupur.py üretir (kendi kupür tasarımımız; foto Immanuelle, CC BY-SA 4.0)
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
CACHE = ROOT / ".cache" / "gobeklitepe-mezar-tasi"
IMG = HERE / "img"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

HAM = [
    "Gobekli Tepe Wishing tree in 2014 3174.jpg",
    "Gobeklitepe.jpg",
    "Gobekli Tepe 4.jpg",
]


def commons(ad: str) -> str:
    n = ad.replace(" ", "_")
    h = hashlib.md5(n.encode()).hexdigest()
    return f"https://upload.wikimedia.org/wikipedia/commons/{h[0]}/{h[:2]}/{urllib.parse.quote(n)}"


def ham(ad: str) -> Image.Image:
    p = CACHE / ad.replace(" ", "_")
    if not p.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        r = requests.get(commons(ad), headers=UA, timeout=120)
        r.raise_for_status()
        p.write_bytes(r.content)
        time.sleep(12)
    return Image.open(p).convert("RGB")


def olc(im: Image.Image) -> tuple[float, float]:
    a = np.asarray(im.convert("RGB")).astype(float) / 255
    lum = (0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]).mean() * 255
    mx, mn = a.max(-1), a.min(-1)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0).mean()
    return lum, sat


def gama(im: Image.Image, g: float) -> Image.Image:
    return im.point(lambda v: int(255 * (v / 255) ** g))


def arka():
    """4928x3280; ağaç gövdesi x~1970. Kare kırpım ağacı ortaya alır (x 330-3610), iki yandaki taş duvar ve çakıl
    karakterlerin arkasında kalır. Beyaz çakıl parlaklığı yükseltiyor: gama 1,15 (STIL: diyalog karesi ~121)."""
    im = ham(HAM[0])
    x0 = 330
    im = im.crop((x0, 0, x0 + 3280, 3280)).resize((1080, 1080), Image.LANCZOS)
    im = gama(im, 1.15)
    im = ImageEnhance.Color(im).enhance(0.92)
    im.save(IMG / "arka_dilek_agaci.jpg", quality=92)
    print("arka", olc(im))


def kanit1():
    """4032x1960, D yapısının ortasındaki iki büyük dikilitaş ve çevresi. Sıkı kırpım (telefonda dikilitaşlar
    büyük okunsun): 1080x700; gama 1,18 + kontrast x1,12 (ilk sürüm telefonda soluk, parlaklık 170)."""
    im = ham(HAM[1])
    w = 3000
    h = int(w * 700 / 1080)
    x0, y0 = 450, 0
    im = im.crop((x0, y0, x0 + w, y0 + h)).resize((1080, 700), Image.LANCZOS)
    im = gama(im, 1.18)                                   # öğle ışığında soluk: telefonda taşlar seçilsin
    im = ImageEnhance.Contrast(im).enhance(1.12)
    im.save(IMG / "kanit_1_tapinak.jpg", quality=92)
    print("kanit1", olc(im))


if __name__ == "__main__":
    IMG.mkdir(exist_ok=True)
    arka()
    kanit1()
