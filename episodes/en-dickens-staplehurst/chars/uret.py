"""en-dickens-staplehurst karakterleri:  python episodes/en-dickens-staplehurst/chars/uret.py

A (sol, yolcu rolu, kurgu): wl:irish_wojak (569x677, siyah-gri Viktorya ceketi, bıyıklı) -> yumuşak 2x büyütme -> a_sakin.png.
  a_sok.png (ters köşe, aynı kutu): göz/kaş/alın çizgisi silinir; iri yuvarlak göz + küçük göz bebeği, kalkık kalın kaş,
  "O" ağız, alında mavi çizgiler, baş dışında ter damlaları. Silüet ve kıyafet aynı.
B (sağ, Dickens rolu, kurgu): wl:victorian_man_wojak (1207x1400; silindir şapka, bıyık, siyah ceket). Şapkada soluk
  "ChrisClipArt" filigranı var: koyu piksellerde açma (min+max 25 px) filtresiyle silinir -> göğüsten kesilir -> b_sakin.png.
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
    """2x büyütme; basamaklı konturu yuvarlar (4x bicubic -> medyan 9 renk tabanı + yumuşatılmış çizgi maskesi -> 2x LANCZOS)."""
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
    """Siyah çizgileri ~2 px kalınlaştırır (v2 çıtasındaki çizgi kalınlığı; ince/titrek MS-Paint çizgisi)."""
    rgb = np.array(im.convert("RGB")).astype(int)
    kara = Image.fromarray(((rgb.max(-1) < 70) * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(r)).filter(ImageFilter.GaussianBlur(0.8))
    c = (np.array(kara).astype(float) / 255)[..., None]
    out = (rgb * (1 - c)).clip(0, 255).astype(np.uint8)
    res = Image.fromarray(out).convert("RGBA")
    res.putalpha(im.getchannel("A"))
    return res


def a_sakin() -> Image.Image:
    return pad(kalinlastir(yumusak_buyut(Image.open(HERE / "src/a_src.png").convert("RGBA"))))


def b_sakin() -> Image.Image:
    im = Image.open(HERE / "src/b_src.png").convert("RGBA")
    a = np.array(im.convert("RGB")).astype(int)
    op = np.array(im.convert("RGB").filter(ImageFilter.MinFilter(25)).filter(ImageFilter.MaxFilter(25))).astype(int)
    mask = np.zeros(a.shape[:2], bool)
    mask[:600, :] = True
    mask &= a.sum(-1) < 260
    out = a.copy()
    out[mask] = np.minimum(a, op)[mask]
    res = Image.fromarray(out.astype(np.uint8)).convert("RGBA")
    res.putalpha(im.getchannel("A"))
    return pad(res.crop((0, 0, res.width, 1150)), 60) if False else res.crop((0, 0, im.width, 1150))


def sok(a: Image.Image) -> Image.Image:
    im = a.copy()
    W, H = im.size
    L = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    k = lambda p: (p[0] * SS, p[1] * SS)
    o = PAD
    # eski göz, alın çizgisi ve kaşları beyazla (kontur korunur)
    iç = [(300, 174), (655, 172), (688, 255), (688, 455), (330, 462), (270, 400), (262, 255)]   # yüz iç bölgesi (kontura değmez)
    d.polygon([k(p) for p in iç], fill=WHT)
    # iri göz + küçük bebek (dosya sağa bakar)
    for cx, cy, r in [(o + 215, 380, 56), (o + 420, 372, 56)]:
        d.ellipse([k((cx - r, cy - r)), k((cx + r, cy + r))], fill=WHT, outline=BLK, width=10 * SS)
        d.ellipse([k((cx + 2, cy - 6)), k((cx + 26, cy + 18))], fill=BLK)
    # kalkık kalın kaşlar
    d.line([k((o + 150, 310)), k((o + 205, 292)), k((o + 275, 268))], fill=BLK, width=14 * SS, joint="curve")
    d.line([k((o + 365, 262)), k((o + 430, 276)), k((o + 490, 300))], fill=BLK, width=14 * SS, joint="curve")
    # alın çizgileri
    for x0, y0 in [(o + 190, 215), (o + 245, 205), (o + 300, 200), (o + 360, 205)]:
        d.line([k((x0, y0)), k((x0 + 3, y0 + 20))], fill=BLUE, width=9 * SS)
    # O ağız (bıyığın altında)
    d.ellipse([k((o + 307, 636)), k((o + 367, 700))], fill=(70, 25, 25, 255), outline=BLK, width=8 * SS)
    kit_varyant.SS = SS
    for x, y, s in [(o + 630, 300, 22), (o + 650, 420, 20), (o + 625, 540, 18), (o + 80, 350, 20), (o + 70, 478, 18)]:
        kit_varyant._drop(d, x, y, s)
    L = L.resize((W, H), Image.LANCZOS)
    return Image.alpha_composite(im, L)


if __name__ == "__main__":
    a = a_sakin()
    a.save(HERE / "a_sakin.png")
    b_sakin().save(HERE / "b_sakin.png")
    sok(a).save(HERE / "a_sok.png")
    print(a.size)
