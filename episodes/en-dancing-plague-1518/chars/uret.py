"""en-dancing-plague-1518 karakterleri (kaynak PNG'lerden yeniden üretir):  python episodes/en-dancing-plague-1518/chars/uret.py

A (sol, ironik): HF clayshoaf/Wojaks 5_Groomer/12722 'Peasant Groomer' (a_kaynak_kel.png); a_sakin.png = kaynak, boyun dibindeki mavi leke silindi.
B (sağ): wojakland 'Medieval Peasant 2 Wojak' (b_kaynak_koylu.png); b_sakin.png = kaynak (sağa 90 px şeffaf boşluk eklendi ki sok'la aynı tuval olsun).
  b_sok.png (ters köşe, aynı kutu): göz/kaş/ağız silinip iri yuvarlak göz + küçük göz bebeği, iç ucu kalkık kalın kaş, "O" ağız,
  alında düzensiz mavi çizgiler ve başın önünde kontur dışında 3 ter damlası çizildi. Silüet, şapka, sakal ve giysi aynı.
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import kit_varyant  # noqa: E402

SS = 4
BLUE = (60, 120, 200, 255)
PAD = 90


def a_sakin() -> Image.Image:
    im = Image.open(HERE / "a_kaynak_kel.png").convert("RGBA")
    a = np.array(im)
    R, G, B = (a[..., i].astype(int) for i in range(3))
    a[(B > R + 40) & (a[..., 3] > 0)] = [255, 255, 255, 255]   # boyundaki mavi leke
    return Image.fromarray(a)


def b_sakin() -> Image.Image:
    im = Image.open(HERE / "b_kaynak_koylu.png").convert("RGBA")
    W, H = im.size
    out = Image.new("RGBA", (W + PAD, H), (0, 0, 0, 0))
    out.paste(im, (0, 0))
    return out


def drop(d, x, y, s):
    kit_varyant.SS = SS
    kit_varyant._drop(d, x, y, s)


def b_sok() -> Image.Image:
    im = b_sakin()
    W, H = im.size
    a = np.array(im)
    dark = a[..., :3].max(-1) < 90
    # gözler + kaşlar (yüz içi)
    reg = a[212:340, 292:600]
    m = (reg[..., :3].max(-1) < 90) & (reg[..., 3] > 0)
    reg[m, :3] = 255
    # ağız çizgisi (sakal içinde, açık gri zemin)
    reg = a[476:516, 384:548]
    m = (reg[..., :3].max(-1) < 110) & (reg[..., 3] > 0)
    reg[m, :3] = 196
    im = Image.fromarray(a)
    L = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    k = lambda p: (p[0] * SS, p[1] * SS)
    for cx, cy, r in [(358, 292, 44), (546, 306, 38)]:
        d.ellipse([k((cx - r, cy - r)), k((cx + r, cy + r))], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=7 * SS)
        px = cx + 9
        d.ellipse([k((px - 9, cy - 7)), k((px + 9, cy + 11))], fill=(0, 0, 0, 255))
    d.line([k((300, 258)), k((345, 226)), k((410, 214))], fill=(0, 0, 0, 255), width=10 * SS, joint="curve")
    d.line([k((492, 218)), k((552, 226)), k((594, 262))], fill=(0, 0, 0, 255), width=10 * SS, joint="curve")
    d.ellipse([k((434, 482)), k((492, 552))], fill=(70, 25, 25, 255), outline=(0, 0, 0, 255), width=7 * SS)
    for pts in [[(350, 126), (376, 118), (402, 134), (430, 126)], [(452, 120), (478, 112), (504, 128), (532, 120)],
                [(344, 166), (370, 158), (394, 174), (420, 166)], [(480, 170), (506, 162), (530, 178), (556, 170)]]:
        d.line([k(p) for p in pts], fill=BLUE, width=6 * SS, joint="curve")
    for x, y, s in [(648, 250, 20), (636, 150, 17), (664, 400, 19)]:
        drop(d, x, y, s)
    L = L.resize((W, H), Image.LANCZOS)
    return Image.alpha_composite(im, L)


if __name__ == "__main__":
    a_sakin().save(HERE / "a_sakin.png")
    b_sakin().save(HERE / "b_sakin.png")
    b_sok().save(HERE / "b_sok.png")
