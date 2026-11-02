"""en-arkhipov-b59 karakterleri:  python episodes/en-arkhipov-b59/chars/uret.py

A (sol, denizaltı komutanı rolü): dumlupinar-denizaltisi-1953/chars/denizci_sakin.png (wojakland 'Spanish Civil War Sailor Wojak',
  kep yazısı silinmiş) + terli varyant (alında 5 mavi çizgi, yüzün dışında 3 damla): tehlike söyleyen karakter sakin kalmasın.
B (sağ, subay rolü): dumlupinar-denizaltisi-1953/chars/subay_sakin.png ve subay_sok.png (wojakland 'US navy White Wojak', rozet sade çapa).
Gerçek kişi adı videoda yok; karakterler kurgudur.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import kit_varyant  # noqa: E402

SS = 3
BLUE = (60, 120, 230, 255)


def denizci_terli() -> Image.Image:
    im = Image.open(HERE / "denizci_sakin.png").convert("RGBA")
    W, H = im.size
    layer = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    q = lambda p: (p[0] * SS, p[1] * SS)
    for p in [[(470, 292), (484, 326)], [(540, 286), (552, 322)], [(612, 288), (622, 324)], [(684, 296), (692, 332)], [(430, 312), (444, 344)]]:
        d.line([q(p[0]), q(p[1])], fill=BLUE, width=7 * SS, joint="curve")
    kit_varyant.SS = SS
    for x, y, s in [(912, 372, 22), (924, 462, 22), (910, 548, 20)]:
        kit_varyant._drop(d, x, y, s)
    layer = layer.resize((W, H), Image.LANCZOS)
    return Image.alpha_composite(im, layer)


if __name__ == "__main__":
    denizci_terli().save(HERE / "denizci_terli.png", optimize=True)
    print("-> denizci_terli.png")
