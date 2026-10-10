"""Ters köşe yüzü (kaygılı) için alında mavi soğuk ter çizgileri (C2kk S2 / C4V3 S6 tarzı, Nervous Wojak çizgileri).

    python assets/kit/ingiliz_er_1915/ter_cizgileri.py
    python assets/kit/ingiliz_er_1915/kostum.py assets/kit/ingiliz_er_1915/taban/nervous_ter.png assets/kit/ingiliz_er_1915/kaygili.png

v5 (2026-10-10): çizgiler siperliğin alt kenarının en az ~10 px altından başlar ve siperlik ile kaşlar arasındaki
alın şeridine yayılır (5 çizgi, ~7 px kalınlık = ekranda ~3-4 px). Taban: taban/nervous_temiz.png (wojakland
'Nervous Wojak', klasik koordinatına hizalı, kendi mavi çizgileri silinmiş). Koordinatlar taban pikselidir (899x1022).
"""
import random
from pathlib import Path

from PIL import Image, ImageDraw

K = Path(__file__).resolve().parent
SS = 4
BLUE = (52, 164, 207, 255)
W = 7.0

# siperlik alt kenarı (kostum.py, ölçek 0,86 ve -150 sonrası): x 230 -> y ~200, x 585 -> ~185, x 700 -> ~175, x 815 -> ~168
STROKES = [
    # sol uzun "ʃ" (kırışıkların solunda)
    [(244, 214), (234, 222), (236, 246), (232, 274), (231, 298), (220, 305)],
    # küçük çentik
    [(338, 212), (344, 218), (343, 236)],
    # orta "┘" (alt kırışığın altında, kaşların üstünde)
    [(590, 276), (591, 300), (589, 318), (568, 320)],
    # sağ uzun "ʃ" (iki kırışığı keser)
    [(706, 192), (712, 198), (707, 226), (703, 256), (705, 282), (698, 300)],
    # sağ küçük çentik
    [(812, 196), (818, 203), (816, 224)],
]


def wob(pts, seed, amp=0.8):
    r = random.Random(seed)
    return [(x + r.uniform(-amp, amp), y + r.uniform(-amp, amp)) for x, y in pts]


def main():
    base = Image.open(K / "taban" / "nervous_temiz.png").convert("RGBA")
    lay = Image.new("RGBA", (base.width * SS, base.height * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for i, s in enumerate(STROKES):
        p = [(x * SS, y * SS) for x, y in wob(s, i)]
        w = (W + random.Random(10 + i).uniform(-0.6, 0.6)) * SS
        d.line(p, fill=BLUE, width=round(w), joint="curve")
        for x, y in (p[0], p[-1]):
            d.ellipse([x - w / 2, y - w / 2, x + w / 2, y + w / 2], fill=BLUE)
    lay = lay.resize(base.size, Image.LANCZOS)
    base.alpha_composite(lay)
    out = K / "taban" / "nervous_ter.png"
    base.save(out, optimize=True)
    print(out)


if __name__ == "__main__":
    main()
