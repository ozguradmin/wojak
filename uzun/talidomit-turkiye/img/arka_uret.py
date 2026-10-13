"""uzun/talidomit-turkiye arka planları ve doku görselleri: kaynak fotoğraflardan kırpım + kendi düz çizimlerimiz.

    python uzun/talidomit-turkiye/img/arka_uret.py <kaynak_klasoru>

<kaynak_klasoru>: indirilen tam boy fotoğrafların bulunduğu yer (repo dışı; adresleri ve lisansları VARLIKLAR.md'de).
Çıktılar bu klasöre yazılır. Fotoğraf kırpımları 16:9, en az 1920x1080 (çoğu 2560x1440: Ken Burns payı).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

HERE = Path(__file__).resolve().parent


def kirp169(im: Image.Image, x0: int, y0: int, w: int, out_w: int = 2560) -> Image.Image:
    h = round(w * 9 / 16)
    c = im.crop((x0, y0, x0 + w, y0 + h))
    out_w = min(out_w, max(1920, w)) if w >= 1920 else 1920
    return c.resize((out_w, round(out_w * 9 / 16)), Image.LANCZOS)


def yama(im: Image.Image, box, dx: int, dy: int = 0, blur: float = 2.0) -> Image.Image:
    """box bölgesini (dx, dy) kaydırılmış komşu bölgeyle örter (modern priz vb. için), kenarı yumuşatır."""
    x0, y0, x1, y1 = box
    patch = im.crop((x0 + dx, y0 + dy, x1 + dx, y1 + dy))
    m = Image.new("L", patch.size, 0)
    ImageDraw.Draw(m).rectangle([6, 6, patch.width - 7, patch.height - 7], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(blur * 2))
    im = im.copy()
    im.paste(patch, (x0, y0), m)
    return im


def kaydet(im: Image.Image, ad: str, q: int = 90) -> None:
    p = HERE / ad
    im.convert("RGB").save(p, quality=q, optimize=True)
    print(f"{p.name} {im.size}")


def lille(src: Path) -> None:
    im = Image.open(src / "lille_calmette_guerin_lab.jpg").convert("RGB")
    im = yama(im, (2988, 1964, 3082, 2060), 100)                    # masanın altındaki modern priz
    kaydet(kirp169(im, 0, 380, 4100), "arka_lille_lab_169.jpg")     # sağdaki prizler ve şalter dışarıda
    kaydet(kirp169(im, 2380, 1060, 1840), "arka_lille_masa_169.jpg")  # laboratuvar masası (B5.7, yumurta tablası)
    kaydet(kirp169(im, 0, 860, 2700), "arka_lille_yazihane_169.jpg")  # yazı masası, daktilo, küre (yedek)


def eczane(src: Path) -> None:
    """Arppeanum (Helsinki) eski eczane odası, CC0. Yer etiketi YOK (yalnız 'bir eczane')."""
    im = Image.open(src / "arppeanum_eczane_cc0.jpg").convert("RGB")
    im = yama(im, (2545, 1552, 2632, 1798), 86)                      # kapı yanındaki modern prizler
    kaydet(kirp169(im, 0, 330, 4320), "arka_eczane_169.jpg")
    kaydet(kirp169(im, 0, 120, 2700), "arka_eczane_raflar_169.jpg")  # yakın: kırmızı raflar + çekmeceler


def muayenehane(src: Path) -> None:
    """Dorfmuseum Mönchhof (Avusturya) muayenehanesi, CC BY 3.0 (Dguendel). B3.3-B3.7 (Lenz). Yer etiketi YOK."""
    im = Image.open(src / "arztpraxis_dorfmuseum_moenchhof_ccby3.jpg").convert("RGB")
    kaydet(kirp169(im, 0, 420, 3840), "arka_muayenehane_169.jpg")


def ofis(src: Path) -> None:
    """Fabrika müzesinde 1950'ler-60'lar bürosu, CC0 (Wolf1949H). B4.2-B4.4 (Kelsey, FDA); yer etiketi YOK."""
    im = Image.open(src / "buero_arbeitsplatz_cc0.jpg").convert("RGB")
    kaydet(kirp169(im, 0, 140, 3840), "arka_ofis_169.jpg")


if __name__ == "__main__":
    src = Path(sys.argv[1])
    for f in (lille, eczane, muayenehane, ofis):
        f(src)
