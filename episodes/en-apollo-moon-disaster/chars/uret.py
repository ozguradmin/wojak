"""en-apollo-moon-disaster karakterleri (kaynak PNG'lerden yeniden üretir):  python episodes/en-apollo-moon-disaster/chars/uret.py

A (sol, konuşma yazarı): wojakland 'Grey Suit Wojak' (a_kaynak.png, 900x870); a_sakin.png = kaynak.
B (sağ, amir): wojakland 'Suit Wojak' fötr şapkalı (b_kaynak.png, 557x595), 1.65x LANCZOS + UnsharpMask -> b_sakin.png.
  b_sok.png (ters köşe, aynı kutu): gözler/kaş/ağız silinip iri yuvarlak göz + küçük göz bebeği, iç ucu kalkık kalın kaş,
  "O" ağız, alında mavi çizgiler, başın önünde kontur dışında 3 ter damlası. Silüet, şapka, giysi aynı. İkisi de y=760'tan (kravat/yaka) kesilir.
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import kit_varyant  # noqa: E402

SS = 4
BLUE = (60, 120, 200, 255)


def b_sakin() -> Image.Image:
    im = Image.open(HERE / "b_kaynak.png").convert("RGBA")
    f = 1.65
    im = im.resize((int(im.width * f), int(im.height * f)), Image.LANCZOS)
    rgb = im.convert("RGB").filter(ImageFilter.UnsharpMask(2, 60, 2))
    out = rgb.convert("RGBA")
    out.putalpha(im.getchannel("A"))
    return out


def b_sok() -> Image.Image:
    a = np.array(b_sakin())
    # yalnız yüz içindeki koyu çizgileri sil (şapka kenarı y<=268 ve yüz konturu korunur)
    for (x0, y0, x1, y1) in [(405, 282, 505, 345), (535, 285, 614, 350), (460, 436, 594, 482), (478, 270, 506, 294),
                             (542, 270, 566, 304), (590, 270, 606, 286)]:
        reg = a[y0:y1, x0:x1]
        dark = reg[..., :3].mean(axis=2) < 235
        reg[dark & (reg[..., 3] > 0), :3] = 255
    im = Image.fromarray(a)
    W, H = im.size
    L = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    k = lambda p: (p[0] * SS, p[1] * SS)
    LW = 6
    for cx, cy, r in [(452, 338, 29), (574, 340, 27)]:
        d.ellipse([k((cx - r, cy - r)), k((cx + r, cy + r))], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=LW * SS)
        px = cx + 8
        d.ellipse([k((px - 7, cy - 5)), k((px + 7, cy + 9))], fill=(0, 0, 0, 255))
    d.line([k((418, 306)), k((438, 294)), k((478, 291))], fill=(0, 0, 0, 255), width=8 * SS, joint="curve")
    d.line([k((548, 291)), k((582, 294)), k((612, 308))], fill=(0, 0, 0, 255), width=8 * SS, joint="curve")
    d.ellipse([k((498, 436)), k((540, 480))], fill=(70, 25, 25, 255), outline=(0, 0, 0, 255), width=LW * SS)
    for pts in [[(425, 276), (440, 272), (452, 279), (466, 275)], [(480, 277), (494, 273), (506, 280), (520, 276)],
                [(534, 277), (548, 273), (560, 280), (574, 276)], [(588, 279), (600, 275), (610, 281), (620, 278)]]:
        d.line([k(p) for p in pts], fill=BLUE, width=4 * SS, joint="curve")
    kit_varyant.SS = SS
    for x, y, s in [(662, 345, 18), (680, 410, 17), (655, 470, 17)]:
        kit_varyant._drop(d, x, y, s)
    L = L.resize((W, H), Image.LANCZOS)
    return Image.alpha_composite(im, L)


if __name__ == "__main__":
    Image.open(HERE / "a_kaynak.png").convert("RGBA").save(HERE / "a_sakin.png")
    # şapka uzun: göğüsten kes, yüz büyüsün
    b_sakin().crop((0, 0, 891, 760)).save(HERE / "b_sakin.png")
    b_sok().crop((0, 0, 891, 760)).save(HERE / "b_sok.png")
