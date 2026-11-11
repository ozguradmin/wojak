"""eskisehir-cinli-hamam: arka plan ve kanıt 1 hazırlığı (serbest lisanslı kaynaklardan).

    python episodes/eskisehir-cinli-hamam/gorsel.py

- img/arka.jpg (1080x1080): "Safranbolu Cinci Hamamı 2014.jpg" (Hamdigumus, CC0, Wikimedia Commons; img/arka_cinci.jpg,
  1280x853) — tarihî bir Osmanlı hamamının kubbeleri (temsilî; haberdeki Eskişehir hamamı değil). İki kubbe arasındaki
  çatı TV anteni ve sol kubbedeki iki ince paratoner direği (modern öğe) rötuşla silindi (OpenCV inpaint, yalnız
  çubuk pikselleri), kare kırpıldı, 1080'e büyütüldü, renk %70.
- img/kanit_1.jpg (1080x760): "Turkish bath-Kurna 2.jpg" (Pivox, CC BY-SA 4.0, Wikimedia Commons; img/kanit_kurna.jpg)
  — boş bir hamamın musluğu ve kurnası (temsilî). Yatay kırpıldı, 1080 genişliğe küçültüldü, hafif otomatik kontrast.
"""
from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageOps

HERE = Path(__file__).resolve().parent
IMG = HERE / "img"


def anten_sil(im):
    """Çatıdaki modern çubukları siler: TV anteni (kubbeler arası) ve sol kubbe çevresindeki iki ince paratoner direği.
    Yalnız kutu içindeki gökyüzünden farklı ve kiremit kırmızısı olmayan pikseller boyanır (OpenCV inpaint)."""
    a = np.array(im)
    gok = np.array([205, 203, 198])
    maske = np.zeros(a.shape[:2], np.uint8)
    for x0, y0, x1, y1 in [(610, 350, 692, 412), (386, 206, 397, 274), (303, 256, 314, 300)]:
        kut = a[y0:y1, x0:x1].astype(np.int32)
        kirmizi = cv2.dilate(((kut[..., 0] - kut[..., 2]) > 25).astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
        m = (np.abs(kut - gok).sum(-1) > 30) & ~kirmizi
        parca = cv2.dilate(m.astype(np.uint8) * 255, np.ones((3, 3), np.uint8))
        parca[kirmizi] = 0
        maske[y0:y1, x0:x1] = np.maximum(maske[y0:y1, x0:x1], parca)
    return Image.fromarray(cv2.inpaint(a, maske, 5, cv2.INPAINT_TELEA))


def arka():
    im = Image.open(IMG / "arka_cinci.jpg").convert("RGB")         # 1280x853
    im = anten_sil(im)
    x0, s = 200, 853
    im = im.crop((x0, 0, x0 + s, s)).resize((1080, 1080), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(0.70)
    im.save(IMG / "arka.jpg", quality=92)


def kanit_1():
    im = Image.open(IMG / "kanit_kurna.jpg").convert("RGB")       # 1280x1707
    y0 = 760
    im = im.crop((0, y0, 1280, y0 + 900)).resize((1080, 760), Image.LANCZOS)
    im = ImageOps.autocontrast(im, cutoff=0.5)
    im.save(IMG / "kanit_1.jpg", quality=92)


if __name__ == "__main__":
    arka()
    kanit_1()
    print("-> img/arka.jpg, img/kanit_1.jpg")
