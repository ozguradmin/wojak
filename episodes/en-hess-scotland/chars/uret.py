"""en-hess-scotland karakterleri:  python episodes/en-hess-scotland/chars/uret.py

HESS (sağda, kurgu): wl:ww1_pilot_wojak (825x810; deri kask, gözlük, kürk yaka). Sigara silinir (src/a_nocig.png),
  2x yumuşak büyütme -> hess_sakin.png. hess_sok.png (ters köşe, aynı kutu): göz/kaş/alın/ağız silinir; iri yuvarlak göz + küçük bebek,
  kalkık kalın kaş, "O" ağız, alında mavi çizgiler, baş dışında ter damlaları.
FARMER (solda, çiftlik işçisi rolu, kurgu): wl:farmer_wojak (857x918; hasır olmayan keçe şapka, koyu mavi gömlek) -> farmer_sakin.png.
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
BLK = (0, 0, 0, 255)
WHT = (255, 255, 255, 255)
PAD = 120


def yumusak_buyut(im: Image.Image) -> Image.Image:
    big = im.resize((im.width * 4, im.height * 4), Image.BICUBIC)
    rgb = np.array(big.convert("RGB")).astype(float)
    cizgi = Image.fromarray(((rgb.max(-1) < 50) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2.2))
    c = np.clip((np.array(cizgi).astype(float) - 100) / 56, 0, 1)[..., None]
    taban = np.array(big.convert("RGB").filter(ImageFilter.MedianFilter(9))).astype(float)
    out = Image.fromarray((taban * (1 - c)).clip(0, 255).astype(np.uint8))
    out = out.resize((im.width * 2, im.height * 2), Image.LANCZOS).convert("RGBA")
    out.putalpha(im.resize((im.width * 2, im.height * 2), Image.LANCZOS).getchannel("A").point(lambda v: 255 if v > 127 else 0))
    return out


def pad(im: Image.Image, p: int = PAD) -> Image.Image:
    out = Image.new("RGBA", (im.width + 2 * p, im.height), (0, 0, 0, 0))
    out.alpha_composite(im, (p, 0))
    return out


def kalinlastir(im: Image.Image, r: int = 5) -> Image.Image:
    rgb = np.array(im.convert("RGB")).astype(int)
    kara = Image.fromarray(((rgb.max(-1) < 70) * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(r)).filter(ImageFilter.GaussianBlur(0.8))
    c = (np.array(kara).astype(float) / 255)[..., None]
    out = (rgb * (1 - c)).clip(0, 255).astype(np.uint8)
    res = Image.fromarray(out).convert("RGBA")
    res.putalpha(im.getchannel("A"))
    return res


def hess_sakin() -> Image.Image:
    return pad(kalinlastir(yumusak_buyut(Image.open(HERE / "src/a_nocig.png").convert("RGBA"))))


def farmer_sakin() -> Image.Image:
    im = pad(kalinlastir(yumusak_buyut(Image.open(HERE / "src/b_src.png").convert("RGBA"))))
    # kaynakta şapka kenarı dosya kenarında düz kesik: ucu yuvarlak kapatılır (2x+pad koordinatı)
    W, H = im.size
    L = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    k = lambda p: (p[0] * SS, p[1] * SS)
    cx = 1832
    alt = [(cx, 410), (cx + 40, 417), (cx + 66, 430), (cx + 62, 446), (cx + 30, 484), (cx, 540)]
    d.polygon([k(p) for p in alt], fill=(104, 98, 72, 255))
    d.polygon([k(p) for p in [(cx, 410), (cx + 40, 417), (cx + 66, 430), (cx + 60, 441), (cx, 428)]], fill=(168, 158, 124, 255))
    d.line([k(p) for p in [(cx - 2, 411), (cx + 40, 417), (cx + 66, 430), (cx + 62, 446), (cx + 30, 484), (cx - 2, 538)]], fill=BLK, width=7 * SS, joint="curve")
    d.line([k((cx - 2, 427)), k((cx + 60, 441))], fill=BLK, width=5 * SS)
    L = L.resize((W, H), Image.LANCZOS)
    return Image.alpha_composite(im, L)


def sok(a: Image.Image) -> Image.Image:
    im = a.copy()
    W, H = im.size
    L = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    k = lambda p: (p[0] * SS, p[1] * SS)
    o = PAD
    X = lambda x: o + 2 * x      # kaynak (1x) koordinatından 2x + pad
    Y = lambda y: 2 * y
    # eski göz, kaş, alın çizgisi ve ağız çizgisi beyazlanır (kontur ve burun korunur)
    d.polygon([k((X(392), Y(173))), k((X(618), Y(173))), k((X(630), Y(250))), k((X(560), Y(250))), k((X(400), Y(250))), k((X(366), Y(250)))], fill=WHT)
    d.polygon([k((X(452), Y(338))), k((X(566), Y(338))), k((X(566), Y(374))), k((X(452), Y(374)))], fill=WHT)
    # iri göz + küçük bebek (dosya sağa bakar)
    for cx, cy, r in [(X(445), Y(226), 44), (X(578), Y(228), 44)]:
        d.ellipse([k((cx - r, cy - r)), k((cx + r, cy + r))], fill=WHT, outline=BLK, width=9 * SS)
        d.ellipse([k((cx + 10, cy - 2)), k((cx + 32, cy + 20))], fill=BLK)
    # kalkık kalın kaşlar (iç uç yukarı)
    d.line([k((X(408), Y(196))), k((X(435), Y(186))), k((X(470), Y(178)))], fill=BLK, width=12 * SS, joint="curve")
    d.line([k((X(552), Y(178))), k((X(588), Y(186))), k((X(612), Y(196)))], fill=BLK, width=12 * SS, joint="curve")
    # alın çizgileri (kask kenarının altı)
    for x0 in (430, 470, 510, 550):
        d.line([k((X(x0), Y(176))), k((X(x0) + 2, Y(176) + 22))], fill=BLUE, width=8 * SS)
    # O ağız
    d.ellipse([k((X(480), Y(342))), k((X(520), Y(386)))], fill=(70, 25, 25, 255), outline=BLK, width=8 * SS)
    kit_varyant.SS = SS
    for x, y, s in [(X(668), 250, 22), (X(684), 360, 20), (X(660), 470, 18), (X(165), 260, 20), (X(155), 360, 18)]:
        kit_varyant._drop(d, x, y, s)
    L = L.resize((W, H), Image.LANCZOS)
    return Image.alpha_composite(im, L)


if __name__ == "__main__":
    a = hess_sakin()
    a.save(HERE / "hess_sakin.png")
    farmer_sakin().save(HERE / "farmer_sakin.png")
    sok(a).save(HERE / "hess_sok.png")
    print(a.size)
