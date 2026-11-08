"""hayirsizada-kopekleri-1910: iki hazır kıyafetli karakter.

    python episodes/hayirsizada-kopekleri-1910/chars/uret.py

Kaynaklar (kaynak/ altında):
  hf_5_Bloomer_3574.png     HF clayshoaf/Wojaks 5_Bloomer/3574 "Ottoman Bloomer" (435x499): fes, siyah takım. A (sol),
                            adsız belediye memuru (1910, fes dönemine uygun). 2x LANCZOS + UnsharpMask(2,60,2).
  kasikci_bulan_*.png       episodes/kasikci-elmasi/chars/bulan_{sakin,sok}.png: düz klasik wojak, kahverengi iş gömleği,
                            siyah takke. B (sağ), adsız sandalcı; ters köşe yüzü (iri göz, kalkık kaş, O ağız, alında
                            mavi çizgiler, 3 damla) o bölümde hakemlerden geçti.
Bakış yönü dosyanın kendisine göre kaydedilir (python -m wojak yon ...); episode.yaml'da faces: yok.
"""
from pathlib import Path
import shutil

import numpy as np
from PIL import Image, ImageFilter

HERE = Path(__file__).resolve().parent
K = HERE / "kaynak"


def kontur_sabitle(im):
    a = np.array(im).astype(np.int32)
    m = (a[..., :3].sum(-1) < 240) & (a[..., 3] > 30)
    a[m, 3] = 255
    return Image.fromarray(a.astype(np.uint8))


im = kontur_sabitle(Image.open(K / "hf_5_Bloomer_3574.png").convert("RGBA"))
im = im.resize((im.width * 2, im.height * 2), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 60, 2))
im.save(HERE / "memur.png", optimize=True)
shutil.copy(K / "kasikci_bulan_sakin.png", HERE / "sandalci_sakin.png")
shutil.copy(K / "kasikci_bulan_sok.png", HERE / "sandalci_sok.png")
for f in ("memur.png", "sandalci_sakin.png", "sandalci_sok.png"):
    print(f, Image.open(HERE / f).size)
