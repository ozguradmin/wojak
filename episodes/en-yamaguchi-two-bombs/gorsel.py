"""en-yamaguchi-two-bombs görselleri (kaynakları img/'den hazırlar): python episodes/en-yamaguchi-two-bombs/gorsel.py
bg_dock.jpg: 'No2 Dock Nagasaki' (c.1910, el boyamalı kartpostal, PD-Japan-oldphoto; ABD'de 1930 öncesi yayın): alttaki yazı bandı atılarak
  960x960 kare kırpım, 1080'e büyütülür, renk 1,2 / parlaklık 0,95.
ev_hiroshima.jpg: NARA 542192 (George R. Caron, PD-USGov): dikey -> mantar başı + üst gövde, sağ alttaki kayıt numarası kırpımla dışarıda, 1080x814.
ev_nagasaki.jpg: HD.4F.002 (Charles Levy, PD-USGov-DOE): tam kare, 1080x740.
"""
from pathlib import Path
from PIL import Image, ImageEnhance

H = Path(__file__).resolve().parent / "img"

d = Image.open(H / "dock_1920_kaynak.jpg").convert("RGB").crop((400, 20, 1360, 980)).resize((1080, 1080), Image.LANCZOS)
d = ImageEnhance.Brightness(ImageEnhance.Color(d).enhance(1.2)).enhance(0.95)
d.save(H / "bg_dock.jpg", quality=93)

h = Image.open(H / "kanit1-hiroshima-mantar-bulutu.jpg").convert("RGB").crop((290, 300, 1630, 1310)).resize((1080, 814), Image.LANCZOS)
h.save(H / "ev_hiroshima.jpg", quality=93)

n = Image.open(H / "kanit2-nagasaki-mantar-bulutu.jpg").convert("RGB")
n = n.resize((1080, round(n.height * 1080 / n.width)), Image.LANCZOS)
n.save(H / "ev_nagasaki.jpg", quality=93)
print(d.size, h.size, n.size)
