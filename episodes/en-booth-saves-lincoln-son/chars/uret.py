"""en-booth-saves-lincoln-son karakterleri:  python episodes/en-booth-saves-lincoln-son/chars/uret.py

A (sol, Robert): wojakland 'Grey Suit Wojak' (kaynak/grey_suit_wojak.png), olduğu gibi: a_sakin.png.
B (sağ, Booth): wojakland 'Top Hat British Chad 1' (kaynak/top_hat_british_chad_1.png, profil, burun sola).
  Pipo ve duman silinir (iki varyantta da, silüet aynı); b_sakin.png kapalı ağız.
  b_sok.png (ters köşe, aynı kutu): göz silinip iri yuvarlak göz + küçük göz bebeği, kızgın kaş yerine kalkık yay kaş,
  "O" ağız, alında mavi çizgiler ve yüzün önünde kontur dışında 3 ter damlası.
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
PAD = 70                      # sol boşluk: damlalar için
SKIN = (255, 215, 184, 255)
BLUE = (60, 120, 200, 255)
BLACK = (0, 0, 0, 255)


def base() -> np.ndarray:
    im = Image.open(HERE / "kaynak" / "top_hat_british_chad_1.png").convert("RGBA")
    a = np.array(im)
    # pipo + duman: yüzün önündeki bölge (x<60) temizlenir; dudağa giren sap ucu ten rengine boyanır
    a[480:556, :60] = 0
    a[400:480, :28] = 0
    # eski kaşın kontur dışına taşan ucu: çizgi (52,348)-(59,372)'nin solu silinir, kontur yeniden çizilir
    for y in range(349, 372):
        lx = 52 + (y - 348) * 7 / 24
        a[y, : int(lx) - 1] = 0
    reg = a[484:500, 60:70]
    r, g, b = reg[..., 0].astype(int), reg[..., 1].astype(int), reg[..., 2].astype(int)
    brown = (reg[..., 3] > 0) & (r - b > 40) & (r < 200)
    reg[brown] = SKIN
    out = Image.fromarray(a)
    lay = Image.new("RGBA", (out.width * SS, out.height * SS), (0, 0, 0, 0))
    ImageDraw.Draw(lay).line([(52.5 * SS, 346 * SS), (53 * SS, 352 * SS), (56 * SS, 362 * SS), (59.5 * SS, 374 * SS)], fill=BLACK, width=int(2.6 * SS), joint="curve")
    out = Image.alpha_composite(out, lay.resize(out.size, Image.LANCZOS))
    c = Image.new("RGBA", (out.width + PAD, out.height), (0, 0, 0, 0))
    c.paste(out, (PAD, 0))
    return c.crop((0, 0, c.width, 690))   # göğüs hizasında kes: yüz büyür


def L(x, y):
    return ((x + PAD) * SS, y * SS)


def sok(im: Image.Image) -> Image.Image:
    a = np.array(im)
    o = PAD
    # eski göz, kızgın kaş ve ağız çizgileri silinir (yalnız ten + siyah çizgi; kontur dışında kalan şeffaf)
    # göz/kaş bölgesi ve dudak çizgileri: her satırda soldaki 5 opak piksel (yüz konturu) korunur, kalanı ten
    for y0, y1, xe in [(340, 400, o + 172), (499, 526, o + 112)]:
        for y in range(y0, y1):
            xs = np.where(a[y, o + 50:xe, 3] > 0)[0]
            if len(xs):
                xs0 = o + 50 + xs[0] + 3
                seg = a[y, xs0:xe]
                seg[seg[:, 3] > 0] = SKIN
    # yüz konturu bozulmasın: ağız kutusunda kontur sol kenarı yeniden çizilir (ellipse içeride kalır)
    im = Image.fromarray(a)
    W, H = im.size
    layer = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.line([L(*p) for p in [(59, 326), (56, 336), (54, 342), (53, 348), (55, 358), (58, 368), (59.5, 374), (57, 379), (54, 385)]], fill=BLACK, width=int(3 * SS), joint="curve")
    # iri yuvarlak göz + küçük bebek (içe, sola bakar)
    cx, cy, r = 112, 384, 21
    d.ellipse([L(cx - r, cy - r), L(cx + r, cy + r)], fill=(255, 255, 255, 255), outline=BLACK, width=6 * SS)
    d.ellipse([L(cx - 13, cy - 5), L(cx + 1, cy + 9)], fill=BLACK)
    # kalkık yay kaş (iç uç, yani burna yakın uç yukarıda)
    d.line([L(76, 346), L(98, 334), L(126, 332), L(150, 346)], fill=BLACK, width=8 * SS, joint="curve")
    # "O" ağız
    d.ellipse([L(76, 500), L(106, 536)], fill=(90, 25, 25, 255), outline=BLACK, width=5 * SS)
    # alında mavi çizgiler
    for p in [[(100, 304), (110, 316)], [(116, 300), (124, 314)], [(133, 303), (139, 317)], [(88, 310), (96, 321)]]:
        d.line([L(*p[0]), L(*p[1])], fill=BLUE, width=4 * SS, joint="curve")
    kit_varyant.SS = SS
    for x, y, s in [(160, 356, 10), (172, 396, 10), (170, 436, 9)]:
        kit_varyant._drop(d, x + PAD, y, s)
    layer = layer.resize((W, H), Image.LANCZOS)
    return Image.alpha_composite(im, layer)


def robert_terli() -> Image.Image:
    im = Image.open(HERE / "kaynak" / "grey_suit_wojak.png").convert("RGBA")
    W, H = im.size
    layer = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    q = lambda p: (p[0] * SS, p[1] * SS)
    for p in [[(470, 112), (488, 146)], [(520, 106), (536, 142)], [(572, 108), (584, 146)], [(622, 116), (632, 150)], [(430, 132), (448, 160)]]:
        d.line([q(p[0]), q(p[1])], fill=BLUE, width=7 * SS, joint="curve")
    kit_varyant.SS = SS
    for x, y, s in [(798, 262, 22), (822, 352, 22), (790, 440, 20)]:
        kit_varyant._drop(d, x, y, s)
    layer = layer.resize((W, H), Image.LANCZOS)
    return Image.alpha_composite(im, layer)


# ---- Booth v2: wojakland/HF 'Wojak With Suit HD' (kaynak/wojak_with_suit_hd.png, kel, papyonlu siyah takım) ----
S2 = 2


def _white_black(a, box):
    x0, y0, x1, y1 = box
    reg = a[y0:y1, x0:x1]
    reg[reg[..., 3] > 0, :3] = 255


def booth_sakin() -> Image.Image:
    im = Image.open(HERE / "kaynak" / "wojak_with_suit_hd.png").convert("RGBA")
    a = np.array(im)
    _white_black(a, (800, 795, 1215, 900))          # sırıtma ve gamze çizgisi silinir
    im = Image.fromarray(a)
    L2 = Image.new("RGBA", (im.width * S2, im.height * S2), (0, 0, 0, 0))
    d = ImageDraw.Draw(L2)
    d.line([(925 * S2, 852 * S2), (1020 * S2, 862 * S2), (1125 * S2, 858 * S2)], fill=BLACK, width=10 * S2, joint="curve")
    return Image.alpha_composite(im, L2.resize(im.size, Image.LANCZOS))


def booth_sok() -> Image.Image:
    im = booth_sakin()
    a = np.array(im)
    for box in [(800, 400, 1035, 565), (1130, 400, 1318, 590), (900, 820, 1160, 900)]:
        _white_black(a, box)
    im = Image.fromarray(a)
    W, H = im.size
    L2 = Image.new("RGBA", (W * S2, H * S2), (0, 0, 0, 0))
    d = ImageDraw.Draw(L2)
    k = lambda p: (p[0] * S2, p[1] * S2)
    for cx, cy, r in [(915, 520, 52), (1225, 535, 48)]:
        d.ellipse([k((cx - r, cy - r)), k((cx + r, cy + r))], fill=(255, 255, 255, 255), outline=BLACK, width=11 * S2)
        px = cx + 12
        d.ellipse([k((px - 13, cy - 10)), k((px + 13, cy + 16))], fill=BLACK)
    d.line([k((835, 448)), k((895, 408)), k((975, 402)), k((1020, 424))], fill=BLACK, width=15 * S2, joint="curve")
    d.line([k((1150, 420)), k((1215, 398)), k((1290, 420))], fill=BLACK, width=15 * S2, joint="curve")
    d.ellipse([k((985, 820)), k((1085, 905))], fill=(90, 25, 25, 255), outline=BLACK, width=11 * S2)
    for p in [[(920, 150), (942, 198)], [(990, 135), (1006, 186)], [(1060, 132), (1070, 184)], [(1130, 145), (1138, 196)]]:
        d.line([k(p[0]), k(p[1])], fill=BLUE, width=11 * S2, joint="curve")
    kit_varyant.SS = S2
    for x, y, s in [(1385, 400, 32), (1408, 505, 32), (1378, 610, 28)]:
        kit_varyant._drop(d, x, y, s)
    return Image.alpha_composite(im, L2.resize((W, H), Image.LANCZOS))


if __name__ == "__main__":
    Image.open(HERE / "kaynak" / "grey_suit_wojak.png").convert("RGBA").save(HERE / "a_sakin.png")
    booth_sakin().save(HERE / "b_sakin.png")
    booth_sok().save(HERE / "b_sok.png")
    robert_terli().save(HERE / "a_terli.png")
