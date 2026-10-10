#!/usr/bin/env python3
"""anne_basortulu2 kitini kaynaktan yeniden üretir (kit.json'daki açıklamaya bakın).

    python assets/kit/anne_basortulu2/uret.py

1. Kaynak: HF clayshoaf/Wojaks 5_Doomer_Girl/2341 ("muslim doomer girl", 244x349), `python tools/wojak_lib.py get`
   ile episodes/van-depremi-azra-bebek/chars/anne_basortulu2_kaynak.png olarak indirildi.
2. x1,6 büyütme (4x + yumuşatma + keskinleştirme, basamaklı kenarlar için), göğüs altı kesilir (kaynak y>300); pembe gömlek -> kahverengi hırka (gölgeler korunur, yalnız gömlek bölgesi).
3. tek_gozyasi: tools/kit_varyant.py ile (kit.json 'variants').
4. agliyor: iki gözden gözyaşı (kit_varyant'ın çizgisiyle) + açık, titreyen ağız.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

KIT = Path(__file__).resolve().parent
ROOT = KIT.parent.parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))
import kit_varyant  # noqa: E402
from wojak import facing  # noqa: E402

SRC = ROOT / "episodes" / "van-depremi-azra-bebek" / "chars" / "anne_basortulu2_kaynak.png"
SCALE = 1.6
CROP_H = 300   # kaynak piksel: bu satırın altı kesilir
BROWN = np.array((138, 96, 70), np.float32)   # ana gömlek pembesinin (lum ~159) karşılığı


def base() -> Image.Image:
    src = Image.open(SRC).convert("RGBA")
    # kaynak düşük çözünürlüklü ve kenarları basamaklı: 4x büyüt, premultiplied hafif bulanıklık + keskinleştirme,
    # sonra x1,6'ya indir (çizgiler keskin kalır, basamaklar yumuşar)
    big = src.convert("RGBa").resize((src.width * 4, src.height * 4), Image.BICUBIC)
    big = big.filter(ImageFilter.GaussianBlur(2.0)).convert("RGBA").filter(ImageFilter.UnsharpMask(2, 120, 0))
    im = big.resize((round(src.width * SCALE), round(src.height * SCALE)), Image.LANCZOS)
    # büst: göğüs altını kes (baş/omuz oranı kanalın başörtülü kadınıyla aynı, ~%65 baş)
    im = im.crop((0, 0, im.width, round(CROP_H * SCALE)))
    a = np.array(im).astype(np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    yy = np.mgrid[0:a.shape[0], 0:a.shape[1]][0]
    pink = (r - g > 0.3 * np.maximum(r, 1)) & (b - g > 0.18 * np.maximum(r, 1)) & (yy > 170 * SCALE) & (a[..., 3] > 0)
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    k = np.clip(lum / 159.0, 0, 1.2)[pink]
    a[..., :3][pink] = np.clip(BROWN[None, :] * k[:, None], 0, 255)
    return Image.fromarray(a.astype(np.uint8))


def open_mouth(im: Image.Image, spec: dict) -> Image.Image:
    """Dudakların yerine açık, titreyen ağız (üst dişler görünür), 4x süper örnekleme."""
    SS = 4
    x0, y0, x1, y1 = spec["box"]          # eski dudakları örten alan
    skin = tuple(spec["skin"])
    big = im.resize((im.width * SS, im.height * SS), Image.LANCZOS)
    d = ImageDraw.Draw(big)
    # eski dudakları ten rengiyle ört (yumuşak elips)
    d.ellipse([x0 * SS, y0 * SS, x1 * SS, y1 * SS], fill=skin + (255,))
    # ağız: üstü dalgalı, altı yay
    top = [(x * SS, y * SS) for x, y in spec["top"]]
    bot = [(x * SS, y * SS) for x, y in spec["bottom"]]
    poly = top + bot[::-1]
    d.polygon(poly, fill=(78, 22, 30, 255))
    # üst dişler: üst kenarın hemen altında beyaz şerit
    teeth = [(x, y + 0.6 * SS) for x, y in top] + [(x, y + spec["teeth_h"] * SS) for x, y in top[::-1]]
    mask = Image.new("L", big.size, 0)
    ImageDraw.Draw(mask).polygon(poly, fill=255)
    tl = Image.new("RGBA", big.size, (0, 0, 0, 0))
    ImageDraw.Draw(tl).polygon(teeth, fill=(250, 248, 242, 255))
    tl.putalpha(Image.fromarray(np.minimum(np.array(tl.getchannel("A")), np.array(mask))))
    big.alpha_composite(tl)
    lw = round(spec["line"] * SS)
    d = ImageDraw.Draw(big)
    d.line(top, fill=(20, 8, 8, 255), width=lw, joint="curve")
    d.line(bot, fill=(20, 8, 8, 255), width=lw, joint="curve")
    for p in (top[0], top[-1]):
        d.ellipse([p[0] - lw / 2, p[1] - lw / 2, p[0] + lw / 2, p[1] + lw / 2], fill=(20, 8, 8, 255))
    # alt dudak gölgesi (ince pembe yay)
    lip = [(x, y + spec["lip_dy"] * SS) for x, y in bot[1:-1]]
    d.line(lip, fill=(196, 104, 110, 255), width=round(spec["lip_w"] * SS), joint="curve")
    out = big.resize(im.size, Image.LANCZOS)
    out.putalpha(im.getchannel("A"))
    return out


def main() -> None:
    cfg = json.loads((KIT / "kit.json").read_text(encoding="utf-8"))
    b = base()
    b.save(KIT / "sakin.png", optimize=True)
    facing.register(KIT / "sakin.png", "right")
    for name, spec in cfg["variants"].items():
        kit_varyant.make(KIT / "sakin.png", spec, KIT / f"{name}.png")
        facing.register(KIT / f"{name}.png", "right")
    ag = cfg["agliyor"]
    tmp = KIT / ".agliyor_tmp.png"
    kit_varyant.make(KIT / "sakin.png", {"tears": []}, tmp)
    im = open_mouth(Image.open(tmp).convert("RGBA"), ag["mouth"])
    im.save(tmp)
    kit_varyant.make(tmp, {"tears": ag["tears"]}, KIT / "agliyor.png")
    tmp.unlink()
    facing.register(KIT / "agliyor.png", "right")
    for f in sorted(KIT.glob("*.png")):
        print("->", f.relative_to(ROOT))


if __name__ == "__main__":
    main()
