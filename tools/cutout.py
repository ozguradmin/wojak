#!/usr/bin/env python3
"""Beyaz/düz arka planlı wojak görselini şeffaf PNG'ye çevirir.

Wojak'lar siyah konturlu çizimler olduğu için, kenarlardan içeri doğru
"flood fill" ile arka planı silmek rembg gibi yapay zekâ modellerinden daha
temiz sonuç verir (wojak'ın beyaz yüzü arka planla karışmaz; kontur onu korur).

    python tools/cutout.py girdi.jpg                       # -> girdi_cut.png
    python tools/cutout.py girdi.jpg -o assets/characters/isim.png --tol 40
    python tools/cutout.py girdi.png --rembg               # fotoğraf gibi karmaşık görseller için

--rembg için: pip install "rembg[cpu]"
"""

from __future__ import annotations

import argparse
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter


def flood_cutout(im: Image.Image, tol: int = 38, feather: float = 1.0) -> Image.Image:
    rgb = np.asarray(im.convert("RGB")).astype(np.int16)
    h, w, _ = rgb.shape
    # Arka plan rengi: kenar piksellerinin medyanı
    border = np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]])
    bg = np.median(border, axis=0)
    close = np.abs(rgb - bg).max(axis=2) <= tol
    mask = np.zeros((h, w), bool)
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if close[y, x] and not mask[y, x]:
                mask[y, x] = True
                q.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if close[y, x] and not mask[y, x]:
                mask[y, x] = True
                q.append((y, x))
    while q:
        y, x = q.popleft()
        for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
            if 0 <= ny < h and 0 <= nx < w and close[ny, nx] and not mask[ny, nx]:
                mask[ny, nx] = True
                q.append((ny, nx))
    alpha = Image.fromarray(np.where(mask, 0, 255).astype(np.uint8))
    if feather:
        # Kenar yumuşatma: önce 1 px içeri al, sonra hafif bulanıklaştır
        alpha = alpha.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(feather))
    out = im.convert("RGBA")
    out.putalpha(alpha)
    return out


def rembg_cutout(im: Image.Image) -> Image.Image:
    from rembg import new_session, remove  # isteğe bağlı bağımlılık
    return remove(im, session=new_session("isnet-general-use"))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input")
    ap.add_argument("-o", "--output")
    ap.add_argument("--tol", type=int, default=38, help="arka plan renk toleransı (0-255)")
    ap.add_argument("--rembg", action="store_true", help="flood fill yerine rembg kullan")
    a = ap.parse_args()
    src = Path(a.input)
    im = Image.open(src)
    out = rembg_cutout(im) if a.rembg else flood_cutout(im, a.tol)
    bbox = out.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
    if bbox:
        out = out.crop(bbox)
    dst = Path(a.output) if a.output else src.with_name(src.stem + "_cut.png")
    out.save(dst, optimize=True)
    print(f"-> {dst} ({out.width}x{out.height})")


if __name__ == "__main__":
    main()
