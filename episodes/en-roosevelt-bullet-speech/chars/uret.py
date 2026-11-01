"""en-roosevelt-bullet-speech karakterleri (kaynak PNG'lerden yeniden üretir):  python episodes/en-roosevelt-bullet-speech/chars/uret.py

B (sağ, Roosevelt'i canlandıran kurgusal wojak): wojakland 'Mustache Zoomer Suit Wojak' (tr_src.png, 665x612).
  b_sakin.png = omuzdaki ülke yaması dümdüz koyu gri yapıldı, kaşların üstündeki gri leke beyazlatıldı, 1.6x LANCZOS + UnsharpMask.
A (sol, yaver): wojakland 'Bow Tie Suit Wojak' (aide_src.png, 694x635), 1.6x; a_sakin.png.
  a_sok.png (ters köşe, aynı kutu): gözler/kaşlar/ağız silinip iri yuvarlak göz + küçük göz bebeği (sağa bakar), iç ucu kalkık kalın kaş,
  "O" ağız, alında mavi çizgiler, başın önünde kontur dışında 3 ter damlası. Silüet ve giysi aynı.
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

F = 1.6
SS = 4
BLUE = (60, 120, 200, 255)


def up(im: Image.Image) -> Image.Image:
    im = im.resize((int(im.width * F), int(im.height * F)), Image.LANCZOS)
    rgb = im.convert("RGB").filter(ImageFilter.UnsharpMask(2, 60, 2))
    out = rgb.convert("RGBA")
    out.putalpha(im.getchannel("A"))
    return out


def b() -> Image.Image:
    from scipy import ndimage as ndi
    a = np.array(Image.open(HERE / "tr_src.png").convert("RGBA"))
    a[566:599, 90:145, :3] = 14  # omuzdaki renkli yama
    rgb = a[..., :3].astype(int)
    gray = (abs(rgb[..., 0] - rgb[..., 1]) < 8) & (abs(rgb[..., 1] - rgb[..., 2]) < 8)
    dark = rgb.sum(-1) < 240
    near_dark = ndi.binary_dilation(dark, iterations=4)
    # çizgilerden uzak açık gri leke/nokta/dikiş izlerini beyazlat (yüz bölgesi)
    face = np.zeros(dark.shape, bool)
    face[0:520, 150:640] = True
    m = face & gray & (rgb[..., 0] > 150) & (rgb[..., 0] < 255) & ~near_dark & (a[..., 3] > 0)
    a[m, :3] = 255
    # kaş üstü gri leke: açık gri bandı beyazlat (kaş çizimi yeniden yapılır)
    band = np.zeros(dark.shape, bool)
    band[195:226, 280:625] = True
    m2 = band & gray & (rgb[..., 0] > 100) & (rgb[..., 0] < 255) & (a[..., 3] > 0)
    # lens halkası (siyah) korunur: yalnız gri tonlar boyanır
    a[m2 & (rgb[..., 0] > 100), :3] = 255
    # bıyık içi: açık artefaktları bıyık rengine çevir
    mus = np.zeros(dark.shape, bool)
    mus[372:442, 360:600] = True
    inside = ndi.binary_closing((np.abs(rgb - np.array([63, 46, 12])).sum(-1) < 40), iterations=3)
    bright = mus & (rgb.sum(-1) > 330) & ndi.binary_fill_holes(inside)
    a[bright, :3] = (63, 46, 12)
    # yüz/yaka kenarına temiz siyah kontur (beyaz kenarlar): alfa kenarından içeri 5 px
    al0 = ndi.gaussian_filter((a[..., 3] > 128).astype(float), 5) > 0.5
    lab, n = ndi.label(al0)
    if n > 1:
        sizes = ndi.sum(al0, lab, range(1, n + 1))
        al0 = lab == (1 + int(np.argmax(sizes)))
    a[..., 3] = np.where(al0, 255, 0)
    a[~al0, :3] = 0
    al = al0
    edge = al & ~ndi.binary_erosion(al, iterations=8)
    white = rgb.sum(-1) > 600
    edge[:, :3] = edge[:, -3:] = False
    edge[-3:, :] = False
    a[edge, :3] = 0
    im = Image.fromarray(a)
    # kaşlar: kalın, yatay, hafif kıvrık (saç rengi)
    L = Image.new("RGBA", (im.width * SS, im.height * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    k = lambda p: (p[0] * SS, p[1] * SS)
    d.line([k((318, 232)), k((365, 212)), k((435, 214))], fill=(63, 46, 12, 255), width=14 * SS, joint="curve")
    d.line([k((545, 205)), k((590, 202)), k((628, 220))], fill=(63, 46, 12, 255), width=14 * SS, joint="curve")
    L = L.resize(im.size, Image.LANCZOS)
    im = Image.alpha_composite(im, L)
    return up(im)


def a_sakin() -> Image.Image:
    return up(Image.open(HERE / "aide_src.png").convert("RGBA"))


def a_sok() -> Image.Image:
    a = np.array(Image.open(HERE / "aide_src.png").convert("RGBA"))
    # gözler, kaşlar, göz altı çizgileri ve ağız silinir (yalnız dolu pikseller)
    for (x0, y0, x1, y1) in [(105, 143, 332, 238), (165, 335, 280, 362)]:
        reg = a[y0:y1, x0:x1]
        m = reg[..., 3] > 0
        reg[m, :3] = 255
    im = up(Image.fromarray(a))
    W, H = im.size
    L = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    k = lambda p: (p[0] * F * SS, p[1] * F * SS)
    for cx, cy, r in [(160, 205, 40), (290, 200, 38)]:
        d.ellipse([k((cx - r, cy - r)), k((cx + r, cy + r))], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=int(7 * F * SS))
        px = cx + 18
        d.ellipse([k((px - 8, cy - 6)), k((px + 8, cy + 10))], fill=(0, 0, 0, 255))
    d.line([k((112, 160)), k((150, 143)), k((205, 140))], fill=(0, 0, 0, 255), width=int(9 * F * SS), joint="curve")
    d.line([k((255, 138)), k((300, 140)), k((345, 160))], fill=(0, 0, 0, 255), width=int(9 * F * SS), joint="curve")
    d.ellipse([k((196, 330)), k((256, 395))], fill=(70, 25, 25, 255), outline=(0, 0, 0, 255), width=int(7 * F * SS))
    for pts in [[(175, 72), (192, 66), (208, 78), (228, 72)], [(245, 58), (265, 52), (283, 64), (305, 58)],
                [(300, 80), (318, 74), (334, 86), (352, 80)], [(190, 94), (208, 88), (224, 100), (246, 94)],
                [(262, 96), (282, 90), (298, 102), (318, 96)]]:
        d.line([k(p) for p in pts], fill=BLUE, width=int(5 * F * SS), joint="curve")
    kit_varyant.SS = SS
    for x, y, s in [(488, 165, 17), (506, 250, 16), (488, 330, 16)]:
        kit_varyant._drop(d, x * F, y * F, s * F)
    L = L.resize((W, H), Image.LANCZOS)
    return Image.alpha_composite(im, L)


if __name__ == "__main__":
    a_sakin().save(HERE / "a_sakin.png")
    a_sok().save(HERE / "a_sok.png")
    b().save(HERE / "b_sakin.png")
