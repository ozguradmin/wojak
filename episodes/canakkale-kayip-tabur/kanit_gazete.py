"""Kanıt 1: East Oregonian (Pendleton, OR), 14 Şubat 1916, s. 1 — "The Men Who Never Came Back" haberi
(başlık + "Fifth Norfolk Regiment Leaving England" fotoğrafı + altyazı), gazetenin kendi sayfasından kupür.

    python episodes/canakkale-kayip-tabur/kanit_gazete.py <iiif_bolge.jpg> [çıktı.jpg]

<iiif_bolge.jpg>: Library of Congress Chronicling America taraması, IIIF bölgesi 1250,4400,2420,2000 (tam çözünürlük):
https://tile.loc.gov/image-services/iiif/service:ndnp:oru:batch_oru_ashland_ver01:data:sn88086023:00202194382:1916021401:0964/1250,4400,2420,2000/full/0/default.jpg
ABD 1916 yayını, kamu malı. Kanıt 2 (kanit_manset.py) aynı sayfanın fotoğrafından yapılmış Türkçe küçük resimdir:
C2Fri / C2fa'daki gibi önce gerçek belge, sonra aynı şeyin Türkçe küçük resmi.

Kırpım yalnız bu haberin kutusu: üstteki başlık çerçevesinden altyazının altına kadar, iki yandaki sütun çizgilerinin
içi (yan sütunlardaki ilgisiz haberler ve haber metni dışarıda kalır). Yalnız gri ton düzeltmesi (autocontrast 0,3 +
gamma 1,4: soluk fotoğraf telefonda okunsun, kağıt beyaz kalır) ve 1080 genişliğe ölçekleme; C2kk'nin gazete kupürü
gibi gerçek tarama dokusu korunur.
"""
import sys
from pathlib import Path

from PIL import Image, ImageOps

EP = Path(__file__).resolve().parent
src = Path(sys.argv[1])
out = Path(sys.argv[2]) if len(sys.argv) > 2 else EP / "img" / "kanit_gazete_1916.jpg"

BOX = (76, 92, 2352, 1628)        # IIIF bölgesi içinde: başlık çerçevesi -> altyazının altı (haber metni dışarıda), sütun çizgilerinin içi
im = Image.open(src).convert("L").crop(BOX)
im = ImageOps.autocontrast(im, cutoff=0.3)
im = im.point([round(255 * (i / 255) ** 1.4) for i in range(256)])   # gamma 1,4: soluk tarama telefonda okunsun, kağıt beyaz kalır
W = 1080
im = im.resize((W, round(im.height * W / im.width)), Image.LANCZOS).convert("RGB")
im.save(out, quality=88)
print(out, im.size)
