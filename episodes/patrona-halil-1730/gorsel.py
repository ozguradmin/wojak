"""patrona-halil-1730: arka plan ve kanıtlar (kaynaklar img/kaynak_*.jpg, Commons; lisanslar episode.yaml sources).

    python episodes/patrona-halil-1730/gorsel.py
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageOps


def aydinlat(im, gama=0.75):
    """Koyu yağlıboya tarama: autocontrast + gama (yalnız ton; içerik değişmez)."""
    im = ImageOps.autocontrast(im, cutoff=0.5)
    lut = [round(255 * (i / 255) ** gama) for i in range(256)]
    return im.point(lut * 3)

D = Path(__file__).resolve().parent / "img"


def olc(im, ad):
    a = np.asarray(im.convert("RGB")).astype(float) / 255
    mx, mn = a.max(-1), a.min(-1)
    doy = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0).mean()
    g = np.asarray(im.convert("L").resize((720, int(720 * im.height / im.width))), dtype=float)
    lap = (np.roll(g, 1, 0) + np.roll(g, -1, 0) + np.roll(g, 1, 1) + np.roll(g, -1, 1) - 4 * g)[2:-2, 2:-2].var()
    print(f"{ad}: {im.size} parlaklık {g.mean():.0f} doygunluk {doy:.2f} laplace {lap:.0f}")


# Arka plan: Topkapı 2. avlu, Divan-ı Hümayun (Kubbealtı) revağı ve Adalet Kulesi. Sağdaki büyük kitabe kaidesi kırpımla dışarıda.
im = Image.open(D / "kaynak_arka_1.jpg").convert("RGB")
im = im.crop((55, 55, 850, 850)).resize((1080, 1080), Image.LANCZOS)  # üstten 30 px: yazı ağaç üstüne insin
im = ImageEnhance.Color(im).enhance(1.0)
im = ImageEnhance.Brightness(im).enhance(1.1)
im.save(D / "arka.jpg", quality=92)
olc(im, "arka")

# Kanıt 1: Vanmour, "Patrona Halil" (Rijksmuseum SK-A-4082) — kılıcı havada Patrona; dikey tablodan yatay kırpım.
im = Image.open(D / "kaynak_kanit_2.jpg").convert("RGB")
w = im.width
h = int(w * 816 / 1080)
y0 = 560
im = aydinlat(im.crop((0, y0, w, y0 + h)).resize((1080, 816), Image.LANCZOS))
im.save(D / "kanit_1.jpg", quality=92)
olc(im, "kanit_1")

# Kanıt 2 (son kare): "De moord op Patrona Halil en zijn volgelingen" (Rijksmuseum SK-A-2012) — saraydaki pusu sahnesi.
im = Image.open(D / "kaynak_moord.jpg").convert("RGB")
x0, y0, cw = 760, 430, 1040  # pusu anına sıkı kırpım (tur 1 SHOULD)
im = im.crop((x0, y0, x0 + cw, y0 + int(cw * 816 / 1080))).resize((1080, 816), Image.LANCZOS)
im = aydinlat(im, 0.7)
im.save(D / "kanit_2.jpg", quality=92)
olc(im, "kanit_2")
