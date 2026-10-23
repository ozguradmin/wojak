"""kanuni-gizlenen-olum: arka plan ve kanıt görselleri (gerçek fotoğraf ve 16. yüzyıl minyatürleri; yapay zekâ yok).

    python episodes/kanuni-gizlenen-olum/gorsel.py

Ham dosyalar .cache/kanuni-gizlenen-olum/ altına iner (git'e girmez; Wikimedia istekleri arasında >= 12 sn,
özgün dosyanın md5 yolu). Çıktılar:
  img/arka_szigetvar.jpg       diyalog arka planı: Szigetvár kalesinin köşe burcu ve surları (Commons "Szigetvár vár 3.jpg", PD-self, Csanády, 2006)
  img/kanit_1_araba.jpg        kanıt 1: padişahın naaşını taşıyan araba, sarığı arabanın içinde (Seyyid Lokman,
                               Tarih-i Sultan Süleyman, Chester Beatty Library T 413, 1579-80; kamu malı)
  img/kanit_2_belgrad.jpg      kanıt 2 (son kare): naaş Belgrad'a varır, II. Selim siyah kaftanla arabanın önünde dua
                               eder (Feridun Ahmed Bey, Nüzhet-i Esrârü'l-Ahyâr, 1568-69, Topkapı H.1339 107b; kamu malı)
Minyatürlerin piksellerine dokunulmaz: yalnız kırpım ve 1080 genişliğe ölçek.
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
CACHE = ROOT / ".cache" / "kanuni-gizlenen-olum"
IMG = HERE / "img"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}


def commons(ad: str) -> str:
    n = ad.replace(" ", "_")
    h = hashlib.md5(n.encode()).hexdigest()
    return f"https://upload.wikimedia.org/wikipedia/commons/{h[0]}/{h[:2]}/{urllib.parse.quote(n)}"


HAM = {
    "szigetvar_var_3.jpg": commons("Szigetvár vár 3.jpg"),
    "lokman_cenaze_sol.jpg": commons("1566-The Funeral of Sultan Suleyman the Magnificent-left-large.jpg"),
    "belgrad_naas_A.jpg": commons("The body of Suleiman I arrives to Belgrade, Selim II is waiting for it A.jpg"),
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


def arka():
    im = Image.open(CACHE / "szigetvar_var_3.jpg").convert("RGB")   # 2080x1544, köşe burcu x~830
    im = im.crop((120, 0, 1664, 1544)).resize((1080, 1080), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(0.66)
    im.save(IMG / "arka_szigetvar.jpg", quality=92)
    print("arka_szigetvar.jpg", im.size, olc(im))


def kanit_1():
    im = Image.open(CACHE / "lokman_cenaze_sol.jpg").convert("RGB")   # 1257x1852
    im = im.crop((300, 760, 1200, 1520))
    im = im.resize((1080, round(im.height * 1080 / im.width)), Image.LANCZOS)
    im.save(IMG / "kanit_1_araba.jpg", quality=93)
    print("kanit_1_araba.jpg", im.size)


def kanit_2():
    im = Image.open(CACHE / "belgrad_naas_A.jpg").convert("RGB")   # 2180x3104
    im = im.crop((80, 1180, 1650, 2120))
    im = im.resize((1080, round(im.height * 1080 / im.width)), Image.LANCZOS)
    im.save(IMG / "kanit_2_belgrad.jpg", quality=93)
    print("kanit_2_belgrad.jpg", im.size)


if __name__ == "__main__":
    IMG.mkdir(exist_ok=True)
    indir()
    arka()
    kanit_1()
    kanit_2()
