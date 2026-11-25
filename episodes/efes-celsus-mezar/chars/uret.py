"""efes-celsus-mezar karakterleri (hazır kıyafetli wojak'lar).

A (sol) kazı işçisi: episodes/schliemann-sal-1873/chars/isci_sakin.png (552x560), olduğu gibi (render ~540 px'e küçültür;
  tur 1'deki 2x büyütme kenarları tırtıklı yapıyordu).
B (sağ) fesli ustabaşı: episodes/karakoy-tunel-1874/chars/esnaf_sakin.png ve esnaf_sok.png (870x900).
  Şok yüzünde iki göz bebeği dosyanın baktığı yöne (sağa) sol gözde 6, sağ gözde 3 px kaydırıldı: tur 1 görsel hakem "neredeyse karşıya bakıyor".
  Göz bebekleri bağlı bölge ile bulunur (scipy.ndimage.label), yerleri beyaz sklera ile doldurulur.
"""
from pathlib import Path
import shutil
import numpy as np
from PIL import Image
from scipy import ndimage as nd

D = Path(__file__).resolve().parent
EP = D.parent.parent
KAY = EP / "karakoy-tunel-1874/chars"

shutil.copy(EP / "schliemann-sal-1873/chars/isci_sakin.png", D / "isci_sakin.png")
shutil.copy(KAY / "esnaf_sakin.png", D / "usta_sakin.png")

im = np.asarray(Image.open(KAY / "esnaf_sok.png").convert("RGBA")).copy()
dark = (im[..., 3] > 128) & (im[..., :3].astype(int).sum(-1) < 200)
lab, _ = nd.label(dark)
KAYMA = 6
for i, sl in enumerate(nd.find_objects(lab), 1):
    m = lab == i
    alan, h, w = m.sum(), sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
    if 250 < alan < 500 and 300 < sl[0].start < 500 and 0.8 < h / w < 1.25:   # iki göz bebeği (22x22, 20x20)
        m = nd.binary_dilation(m, iterations=2) & ((lab == 0) | m)   # kenar halkası da taşınsın; göz konturu korunur
        ys, xs = np.nonzero(m)
        renk = im[ys, xs].copy()
        im[ys, xs] = (255, 255, 255, 255)
        acik = renk[:, :3].astype(int).sum(-1) > 600            # halkanın beyaz pikselleri sklerayı bozmasın
        k = KAYMA if sl[1].start < 600 else 3                     # sağ gözde bebek kontura değmesin
        im[ys[~acik], xs[~acik] + k] = renk[~acik]
Image.fromarray(im).save(D / "usta_sok.png")
