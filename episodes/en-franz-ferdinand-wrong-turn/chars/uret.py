"""en-franz-ferdinand-wrong-turn karakterleri:  python episodes/en-franz-ferdinand-wrong-turn/chars/uret.py

A (sol, konvoydaki yetkili/asker rolü): wojakland 'Ww1 Soldier Wojak' (kaynak/a2_src.png, edelweiss'li dağ kepi), a_sakin.png = göğüsten kesilmiş kaynak.
B (sağ, şoför rolü): wojakland 'Ww1 Pilot Wojak' (kaynak/b_src.png; deri başlık + gözlük). Sigara silindi (çene çizgisi yeniden çizildi);
  b_sakin.png = göğüsten kesilmiş. b_sok.png (ters köşe, aynı kutu): göz/ağız silinip iri yuvarlak göz + küçük göz bebeği,
  iç ucu kalkık kalın kaş, "O" ağız, alında mavi çizgiler, kontur dışında ter damlaları. Silüet ve kıyafet aynı.
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
BLK = (0, 0, 0, 255)
CUT = 600


def no_cig(im: Image.Image) -> Image.Image:
    a = np.array(im)
    H, W = a.shape[:2]
    p0 = np.array([524, 358.0]); p1 = np.array([608, 424.0])
    yy, xx = np.mgrid[0:H, 0:W]
    P = np.stack([xx, yy], -1).astype(float)
    d = p1 - p0
    t = np.clip(((P - p0) @ d) / (d @ d), 0, 1)
    dist = np.linalg.norm(P - (p0 + t[..., None] * d), axis=-1)
    m = (dist < 10) & (t > 0.04)
    m[:, :515] = False
    a[m & (yy <= 392)] = (255, 255, 255, 255)
    a[392:448, 532:662] = (0, 0, 0, 0)  # sigaranın çene altı kalıntısı: bölge silinip çene/boyun yeniden çizilir
    out = Image.fromarray(a)
    L = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    dr = ImageDraw.Draw(L)
    k = lambda p: (p[0] * SS, p[1] * SS)
    WHT = (255, 255, 255, 255)
    dr.polygon([k(p) for p in [(532, 391), (584, 391), (578, 388), (574, 398), (566, 408), (556, 416), (540, 421), (532, 423)]], fill=WHT)
    dr.polygon([k(p) for p in [(532, 421), (556, 417), (572, 426), (602, 449), (532, 449)]], fill=WHT)
    dr.line([k(p) for p in [(578, 386), (574, 398), (566, 408), (556, 416), (540, 421), (531, 422)]], fill=BLK, width=5 * SS, joint="curve")
    dr.line([k(p) for p in [(560, 416), (574, 427), (590, 439), (604, 450)]], fill=BLK, width=5 * SS, joint="curve")
    dr.line([k((518, 358)), k((540, 361)), k((562, 359))], fill=BLK, width=5 * SS, joint="curve")
    return Image.alpha_composite(out, L.resize((W, H), Image.LANCZOS))


def sok(b: Image.Image) -> Image.Image:
    a = np.array(b)
    for (x0, y0, x1, y1) in [(398, 192, 500, 250), (540, 200, 625, 258), (455, 340, 575, 385)]:
        reg = a[y0:y1, x0:x1]
        m = reg[..., 3] > 0
        reg[m, :3] = 255
    im = Image.fromarray(a)
    W, H = im.size
    L = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    k = lambda p: (p[0] * SS, p[1] * SS)
    for cx, cy, r in [(448, 222, 29), (583, 230, 28)]:
        d.ellipse([k((cx - r, cy - r)), k((cx + r, cy + r))], fill=(255, 255, 255, 255), outline=BLK, width=7 * SS)
        px = cx + 7
        d.ellipse([k((px - 7, cy - 4)), k((px + 7, cy + 10))], fill=BLK)
    d.line([k((408, 196)), k((440, 186)), k((482, 178))], fill=BLK, width=9 * SS, joint="curve")
    d.line([k((548, 180)), k((588, 186)), k((622, 204))], fill=BLK, width=9 * SS, joint="curve")
    d.ellipse([k((492, 342)), k((542, 402))], fill=(70, 25, 25, 255), outline=BLK, width=7 * SS)
    kit_varyant.SS = SS
    for x, y, s in [(688, 240, 17), (700, 330, 15), (320, 330, 15)]:
        kit_varyant._drop(d, x, y, s)
    return Image.alpha_composite(im, L.resize((W, H), Image.LANCZOS))


if __name__ == "__main__":
    a = Image.open(HERE / "kaynak" / "a2_src.png").convert("RGBA")
    a.crop((0, 0, a.width, 780)).save(HERE / "a_sakin.png")
    b = no_cig(Image.open(HERE / "kaynak" / "b_src.png").convert("RGBA"))
    b.crop((0, 0, b.width, CUT)).save(HERE / "b_sakin.png")
    sok(b).crop((0, 0, b.width, CUT)).save(HERE / "b_sok.png")
