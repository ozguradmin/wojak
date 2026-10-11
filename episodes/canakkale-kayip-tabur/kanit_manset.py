"""Kanıt 2: YouTube küçük resmi tarzı başlık görseli (kendi tasarımımız; medya logosu, ok, bant yok).

    python episodes/canakkale-kayip-tabur/kanit_manset.py <eo_foto.jpg> [çıktı.jpg]

<eo_foto.jpg>: East Oregonian (Pendleton, OR), 14 Şubat 1916, s. 1, "Fifth Norfolk Regiment Leaving England"
fotoğrafının LoC Chronicling America IIIF bölgesi (ABD 1916 yayını, kamu malı), 2070x1020:
https://tile.loc.gov/image-services/iiif/service:ndnp:oru:batch_oru_ashland_ver01:data:sn88086023:00202194382:1916021401:0964/1400,4700,2070,1020/full/0/default.jpg

final-2 (2026-10-11, görsel hakem): yumuşak ton (autocontrast cutoff 0,3; yüzler siyah leke olmasın), Anton başlık
aynı (124 px, 9 px siyah kontur, sağa yaslı; beyaz "ÇANAKKALE'DE" / sarı #FFE600 "KAYBOLAN TABUR!"), ardından
bütün görsel yeniden yüklenmiş bir küçük resim gibi bozulur: 540x304 (LANCZOS) -> 1080x608 (BICUBIC), JPEG kalite 70.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

EP = Path(__file__).resolve().parent
FONT = EP.parents[1] / "assets" / "fonts" / "Anton-Regular.ttf"
src = Path(sys.argv[1])
out = Path(sys.argv[2]) if len(sys.argv) > 2 else EP / "img" / "kanit_manset_kaybolan_tabur.jpg"

W, H = 1080, 608
K = 2  # 2x çiz, sonra indir

ph = Image.open(src).convert("L").crop((371, 70, 2060, 1020))       # 16:9, sağdaki büyük askerler kadrajda
ph = ImageOps.autocontrast(ph, cutoff=0.3)
ph = ph.resize((W * K, H * K), Image.LANCZOS).convert("RGB")

d = ImageDraw.Draw(ph)
f = ImageFont.truetype(str(FONT), 124 * K)
RIGHT = 1039 * K                       # ink sağ kenarı (v5 ile aynı)
lines = [("ÇANAKKALE'DE", (255, 255, 255)), ("KAYBOLAN TABUR!", (255, 230, 0))]
tops = [41 * K, 181 * K]               # ink üst kenarları (v5 ile aynı yerleşim)
for (t, col), top in zip(lines, tops):
    l, tp, r, b = f.getbbox(t, stroke_width=0)
    x = RIGHT - r
    y = top - tp
    d.text((x, y), t, font=f, fill=col, stroke_width=9 * K, stroke_fill=(0, 0, 0))

im = ph.resize((W, H), Image.LANCZOS)
# yeniden yüklenmiş küçük resim dokusu (orijinallerin son kanıtları gibi yumuşak, sıkıştırılmış)
im = im.resize((540, 304), Image.LANCZOS).resize((W, H), Image.BICUBIC)
im.save(out, quality=70)
print(out, im.size)
