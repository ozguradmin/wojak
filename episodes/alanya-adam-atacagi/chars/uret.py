"""alanya-adam-atacagi: iki hazır kıyafetli karakter.

    python episodes/alanya-adam-atacagi/chars/uret.py

Kaynaklar (kaynak/ altında):
  wl_knight_chad_2.png      wojakland "Knight Chad" (knight_chad_2.png, 536x642): konik miğfer, pullu zırh başlığı, mavi
                            pelerin. B (sağ), adsız kale askeri (efsane Roma/Bizans dönemine bağlanır; konik miğfer ve pullu
                            zırh Bizans askerine uyar). 2x LANCZOS + UnsharpMask(2,60,2). Dosya sola bakar.
  kasikci_bulan_*.png       episodes/kasikci-elmasi/chars/bulan_{sakin,sok}.png: düz klasik wojak, kahverengi iş gömleği,
                            siyah takke. A (sol), adsız mahkûm; ters köşe yüzü (iri göz, kalkık kaş, O ağız, alında mavi
                            çizgiler, 3 damla) önceki bölümlerde hakemlerden geçti.
Bakış yönü dosyanın kendisine göre kaydedilir (python -m wojak yon ...); episode.yaml'da faces: yok.
"""
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

HERE = Path(__file__).resolve().parent
K = HERE / "kaynak"


def kontur_sabitle(im):
    a = np.array(im).astype(np.int32)
    m = (a[..., :3].sum(-1) < 240) & (a[..., 3] > 30)
    a[m, 3] = 255
    return Image.fromarray(a.astype(np.uint8))


im = kontur_sabitle(Image.open(K / "wl_knight_chad_2.png").convert("RGBA"))
im = im.resize((im.width * 2, im.height * 2), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 60, 2))
im.save(HERE / "asker.png", optimize=True)
for kaynak, hedef in (("kasikci_bulan_sakin.png", "mahkum_sakin.png"), ("kasikci_bulan_sok.png", "mahkum_sok.png")):
    m = kontur_sabitle(Image.open(K / kaynak).convert("RGBA"))   # 552x560: 2x LANCZOS + UnsharpMask (el kitabı §10)
    m = m.resize((m.width * 2, m.height * 2), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 60, 2))
    m.save(HERE / hedef, optimize=True)
for f in ("asker.png", "mahkum_sakin.png", "mahkum_sok.png"):
    print(f, Image.open(HERE / f).size)
