"""kasikci-elmasi: arka plan ve kanıt görsellerini Commons özgünlerinden hazırlar (piksellere ekleme yok).

    python episodes/kasikci-elmasi/gorsel.py <indirme_klasoru>

Girdi (indirme klasöründe; Commons, lisanslar episode.yaml `sources`'ta):
  bg1.jpg  "Eğri Kapı (possibly the Kaligaria Gate) of the Blachernae Walls of Constantinople.jpg" (Isabeau, CC BY-SA 4.0)
  e1.jpg   "Imperial Treasury Topkapi 69.JPG" (Gryffindor, kamu malı / PD-self)
  e2.jpg   "Spoonmaker's Diamond5, Topkapi Palace, Istanbul 2023.jpg" (Karakalem, CC BY 4.0; 1920 px küçük sürüm)
Çıktı: img/arka_egrikapi.jpg (1080x1080), img/kanit_1_hazine.jpg (1080x608), img/kanit_2_elmas.jpg (1080x816)
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

HERE = Path(__file__).resolve().parent
SRC = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
OUT = HERE / "img"


def arka():
    im = Image.open(SRC / "bg1.jpg").convert("RGB")          # 3840x2891
    # trafik tabelaları ve kapının modern şeridi kadraj dışında kalsın: kule + servi + sur + hazire parmaklığı
    im.crop((800, 0, 2350, 1550)).resize((1080, 1080), Image.LANCZOS).save(OUT / "arka_egrikapi.jpg", quality=92)


def kanit1():
    im = Image.open(SRC / "e1.jpg").convert("RGB")           # 1600x1200
    im.crop((0, 150, 1600, 1050)).resize((1080, 608), Image.LANCZOS).save(OUT / "kanit_1_hazine.jpg", quality=92)


def kanit2():
    im = Image.open(SRC / "e2.jpg").convert("RGB")           # 1920x2560
    c = im.crop((0, 200, 1920, 2150))                        # elmasın tamamı (1920x1950)
    W = round(c.height * 1080 / 816)                         # 1080x816 oranı için gereken genişlik
    pad = (W - c.width) // 2
    # iki yan: fotoğrafın elmassız koyu kenar şeridi yatay uzatılıp bulanıklaştırılır (ayna değil)
    a = np.array(c)
    sol = np.repeat(a[:, :8].mean(1, keepdims=True), pad, 1)
    sag = np.repeat(a[:, -8:].mean(1, keepdims=True), W - c.width - pad, 1)
    yeni = Image.fromarray(np.concatenate([sol, a, sag], 1).astype(np.uint8))
    bul = yeni.filter(ImageFilter.GaussianBlur(24))
    m = np.zeros((yeni.height, yeni.width), np.float32)
    m[:, pad + 40: pad + c.width - 40] = 1.0
    m = np.array(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(20))) / 255.0
    out = (np.array(yeni) * m[..., None] + np.array(bul) * (1 - m[..., None])).astype(np.uint8)
    Image.fromarray(out).resize((1080, 816), Image.LANCZOS).save(OUT / "kanit_2_elmas.jpg", quality=92)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    arka(); kanit1(); kanit2()
    for f in sorted(OUT.glob("*.jpg")):
        print(f.name, Image.open(f).size)
