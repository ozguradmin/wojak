"""Kanıt 2: YouTube küçük resmi tarzı başlık görseli (kendi tasarımımız; medya logosu, ok, bant yok).

    python episodes/canakkale-kayip-tabur/kanit_manset.py [kaynak.png] [çıktı.jpg] [--crop x0,y0,x1,y1]

final-4 (2026-10-11, iki hakemin ortak önerisi): kaynak artık kanıt 1'deki gazete fotoğrafı DEĞİL (12,5. sn'deki
kesme aynı fotoğrafa yakınlaşma gibi okunuyordu ve üst kenarda gazetenin çizgisi/süsü kalıyordu), Sandringham
Bölüğü'nün kendi fotoğrafı: Wikimedia Commons "File:Norfolk_Regiment_1915.png" (358x204), "Men of the Sandringham
Company, 1/5th Battalion, Norfolk Regiment, in tropical uniform, 1915", yazarı bilinmiyor, kamu malı (PD-old).
Yerel kopya: img/sandringham_bolugu_1915.png. Askerler bizim iki wojak'ın taktığı Wolseley mantar miğferleriyle.

Tarif (görsel hakem): kırp (0, 1, 358, 203) -> gri ton autocontrast cutoff 0,5 -> BICUBIC 2160x1216 -> Anton 124 px
(2x), 9 px siyah kontur, sağa yaslı (ink sağ kenarı 1050), ink üst kenarları 30 ve 170: beyaz "ÇANAKKALE'DE" / sarı
#FFE600 "KAYBOLAN TABUR!" -> LANCZOS 1080x608 -> yeniden yüklenmiş küçük resim dokusu: 540x304 (LANCZOS) ->
1080x608 (BICUBIC), JPEG kalite 70.
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

EP = Path(__file__).resolve().parent
FONT = EP.parents[1] / "assets" / "fonts" / "Anton-Regular.ttf"

ap = argparse.ArgumentParser()
ap.add_argument("src", nargs="?", default=str(EP / "img" / "sandringham_bolugu_1915.png"))
ap.add_argument("out", nargs="?", default=str(EP / "img" / "kanit_manset_kaybolan_tabur.jpg"))
ap.add_argument("--crop", default="0,1,358,203", help="kaynakta 16:9 kırpım kutusu x0,y0,x1,y1")
ap.add_argument("--cutoff", type=float, default=0.5)
a = ap.parse_args()

W, H = 1080, 608
K = 2  # 2x çiz, sonra indir

box = tuple(int(v) for v in a.crop.split(","))
ph = Image.open(a.src).convert("L").crop(box)
ph = ImageOps.autocontrast(ph, cutoff=a.cutoff)
ph = ph.resize((W * K, H * K), Image.BICUBIC).convert("RGB")

d = ImageDraw.Draw(ph)
f = ImageFont.truetype(str(FONT), 124 * K)
RIGHT = 1050 * K                       # ink sağ kenarı
lines = [("ÇANAKKALE'DE", (255, 255, 255)), ("KAYBOLAN TABUR!", (255, 230, 0))]
tops = [30 * K, 170 * K]               # ink üst kenarları
for (t, col), top in zip(lines, tops):
    l, tp, r, b = f.getbbox(t)
    d.text((RIGHT - r, top - tp), t, font=f, fill=col, stroke_width=9 * K, stroke_fill=(0, 0, 0))

im = ph.resize((W, H), Image.LANCZOS)
# yeniden yüklenmiş küçük resim dokusu (orijinallerin son kanıtları gibi yumuşak, sıkıştırılmış)
im = im.resize((540, 304), Image.LANCZOS).resize((W, H), Image.BICUBIC)
im.save(a.out, quality=70)
print(a.out, im.size)
