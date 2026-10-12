"""talidomit-turkiye arka plan ve kanıt görselleri (kaynaklardan yeniden üretir).

    python episodes/talidomit-turkiye/gorsel.py

- img/arka_lille_lab.jpg: Lille, Musée de l'Institut Pasteur, Calmette-Guérin laboratuvarı (Pierre André Leclercq,
  CC BY-SA 4.0; kaynak 4912x3264, img/arka_lille_lab_kaynak.jpg = 2456x1632 küçültülmüş kopya). Kare kırpım
  (masa + daktilo + küre solda, deney masası ve tüp rafları sağda), mavi duvarların doygunluğu azaltıldı,
  hafif aydınlatma (STIL §6: diyalog karesi parlaklığı ~121, doygunluk ~0,2).
- img/kanit_1_protez_810.jpg (kanıt 1, videoda): Science Museum London, 'Artificial limbs for a thalidomide child,
  1961-1965' (CC BY-SA 2.0). y 50-731 kırpım (omuz askısı, iki yapay kol ve kanca eller, deri kalça parçası),
  1080x810 (4:3 letterbox, altın dönem kanıt boyu); fon genişletilmedi.
- img/kanit_1_protez.jpg: (yedek, kullanılmıyor) aynı nesnenin tamamı (omuz askısından ayakkabılara), y 80-1210
  kırpım, düz mavi stüdyo fonu iki yandan 111 px aynalanıp yumuşatılarak 1080x1080 kareye genişletildi.
- img/telifli/kanit_2_sdd_mobil.png (son kanıt, 1080x667): Sağlık Dünyası Dergisi haber sayfasının mobil ekran
  görüntüsü (img/telifli/kanit_2_sdd_mobil_kaynak.png; 412 px CSS genişlik, 2,62x DPR, 12.10.2026, açılır reklam
  katmanı gizlendi). Üstte site logo çubuğu (telefon arayüzünün hamburger menü ve arama simgesi çubuk rengiyle
  boyandı) + sayfa başlığı (y 0-282), altta haber başlık görseli (y 705-1076):
  aradaki özet paragrafı ("yüzlerce, binlerce çocuğun hayatını kurtarmıştır") ile tarih/paylaş satırı ve görselin
  altındaki doğrulanmamış "kök hücre ... ilk bilim insanı" bandı çıkarıldı. Telifli: git'e girmez.
- img/telifli/kanit_2_sdd_manset.jpg: (eski, kullanılmıyor) aynı başlık görselinin 1080x436 şeridi.
- img/telifli/kanit_yedek_tfd_2012.png (YEDEK, videoda yok; 1080x~630): Türk Farmakoloji Derneği E-Bülteni 114 (2012)
  s. 10, "Türkiye'de Talidomid Gerçeği" (kaynak: PDF sayfa 11, 220 dpi, img/telifli/kanit_yedek_tfd_kaynak.png).
  Üstte bülten bandı + başlık/yazar, altta Akcasu tanıklığı paragrafı (Kaymakçalan, ruhsat, Bakanlık). Telifli.
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

HERE = Path(__file__).resolve().parent
IMG = HERE / "img"
BAR = (250, 250, 250)  # Sağlık Dünyası mobil logo çubuğunun rengi


def arka() -> None:
    im = Image.open(IMG / "arka_lille_lab_kaynak.jpg").convert("RGB")
    # kare: x 300-1932 (1632 px), tam yükseklik
    sq = im.crop((300, 0, 1932, 1632))
    sq = ImageEnhance.Color(sq).enhance(0.45)
    sq = ImageEnhance.Brightness(sq).enhance(1.07)
    sq.save(IMG / "arka_lille_lab.jpg", quality=92)
    print("arka_lille_lab.jpg", sq.size)


def protez() -> None:
    im = Image.open(IMG / "kanit_1_protez_kaynak.jpg").convert("RGB")
    c = im.crop((0, 80, 908, 1210))
    h = c.height
    side = (h - 908) // 2
    can = Image.new("RGB", (h, h))
    ls = c.crop((0, 0, side, h)).transpose(Image.FLIP_LEFT_RIGHT).filter(ImageFilter.GaussianBlur(5))
    rs = c.crop((908 - side, 0, 908, h)).transpose(Image.FLIP_LEFT_RIGHT).filter(ImageFilter.GaussianBlur(5))
    can.paste(ls, (0, 0))
    can.paste(rs, (side + 908, 0))
    can.paste(c, (side, 0))
    a = np.array(can).astype(np.float32)
    bl = np.array(can.filter(ImageFilter.GaussianBlur(4))).astype(np.float32)
    for sx in (side, side + 908):
        for dx in range(-6, 7):
            w = 1 - abs(dx) / 7
            a[:, sx + dx] = a[:, sx + dx] * (1 - w) + bl[:, sx + dx] * w
    out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).resize((1080, 1080), Image.LANCZOS)
    out.save(IMG / "kanit_1_protez.jpg", quality=93)
    print("kanit_1_protez.jpg", out.size)


def protez_810() -> None:
    """Kanıt 1 (videoda kullanılan): 4:3 letterbox, altın dönem kanıt boyu (537-816 px; STIL §8).

    y 50-731 kırpım (908x681): omuz askısı, iki yapay kol ve kanca eller, deri kalça parçası; fon genişletilmez,
    LANCZOS ile 1080x810. Tuvalde y 555-1365'e oturur; 10,5 sn'de siyah bantlar geri gelir ve kanıt bloğunu belli eder.
    """
    im = Image.open(IMG / "kanit_1_protez_kaynak.jpg").convert("RGB")
    assert im.size == (908, 1250)
    out = im.crop((0, 50, 908, 731)).resize((1080, 810), Image.LANCZOS)
    out.save(IMG / "kanit_1_protez_810.jpg", quality=93)
    print("kanit_1_protez_810.jpg", out.size)


def sdd() -> None:
    im = Image.open(IMG / "telifli" / "kanit_2_sdd_kaynak.jpg").convert("RGB")
    # soldaki boş bej kenar ve sağdaki cübbe ucu kırpılır: manşet yazısı ~%6 büyür (1080x436); yazı x 61-473
    c = im.crop((36, 0, 884, 342))
    c = c.resize((1080, round(342 * 1080 / 848)), Image.LANCZOS)
    c.save(IMG / "telifli" / "kanit_2_sdd_manset.jpg", quality=93)
    print("telifli/kanit_2_sdd_manset.jpg", c.size)


def sdd_mobil() -> None:
    im = Image.open(IMG / "telifli" / "kanit_2_sdd_mobil_kaynak.png").convert("RGB")
    assert im.width == 1080
    ust = im.crop((0, 0, 1080, 282))       # logo çubuğu + sayfa başlığı (H1)
    # telefon arayüzü (hamburger menü ve arama simgesi) çubuk rengiyle boyanır: logo çubuğu ekran görüntüsü
    # gibi değil, haber bandı gibi okunur (onaylı van'daki Takvim bandı gibi)
    d = ImageDraw.Draw(ust)
    for box in ((74, 55, 142, 115), (954, 50, 1030, 126)):
        d.rectangle(box, fill=BAR)
    gorsel = im.crop((0, 705, 1080, 1076))  # başlık görseli, kırmızı "kök hücre" bandının gölgesinden önce biter
    out = Image.new("RGB", (1080, ust.height + 14 + gorsel.height), (255, 255, 255))
    out.paste(ust, (0, 0))
    out.paste(gorsel, (0, ust.height + 14))
    out.save(IMG / "telifli" / "kanit_2_sdd_mobil.png", optimize=True)
    print("telifli/kanit_2_sdd_mobil.png", out.size)


def tfd_yedek() -> None:
    im = Image.open(IMG / "telifli" / "kanit_yedek_tfd_kaynak.png").convert("RGB")
    ust = im.crop((150, 82, 1690, 545))      # bülten bandı, "Sayfa 10", başlık, yazar
    par = im.crop((150, 1815, 1690, 2232))   # "Farmakoloji biliminin ... Bakanlığı aynen dikkate alarak ... vermemiştir"
    out = Image.new("RGB", (1540, ust.height + 20 + par.height), (255, 255, 255))
    out.paste(ust, (0, 0))
    out.paste(par, (0, ust.height + 20))
    out = out.resize((1080, round(out.height * 1080 / 1540)), Image.LANCZOS)
    out.save(IMG / "telifli" / "kanit_yedek_tfd_2012.png", optimize=True)
    print("telifli/kanit_yedek_tfd_2012.png", out.size)


if __name__ == "__main__":
    arka()
    protez()
    protez_810()
    sdd()
    sdd_mobil()
    tfd_yedek()
