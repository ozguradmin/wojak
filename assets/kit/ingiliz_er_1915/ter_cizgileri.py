"""Ters köşe yüzü (kaygılı) için alında mavi soğuk ter çizgileri (C2kk S2 / C4V3 S6 tarzı, Nervous Wojak çizgileri).

    python assets/kit/ingiliz_er_1915/ter_cizgileri.py
    python assets/kit/ingiliz_er_1915/kostum.py assets/kit/ingiliz_er_1915/taban/nervous_ter.png assets/kit/ingiliz_er_1915/kaygili.png

v5 (2026-10-10): çizgiler siperliğin alt kenarının en az ~10 px altından başlar ve siperlik ile kaşlar arasındaki
alın şeridine yayılır. final-2: 6 çizgi, ~11 px. final-3 (2026-10-11): 5 ince seyrek işaret, ~6,5 px (ekranda ~3 px), Nervous Wojak mavisi. Taban: taban/nervous_temiz.png (wojakland
'Nervous Wojak', klasik koordinatına hizalı, kendi mavi çizgileri silinmiş). Koordinatlar taban pikselidir (899x1022).
"""
import random
from pathlib import Path

from PIL import Image, ImageDraw

K = Path(__file__).resolve().parent
SS = 4
BLUE = (92, 173, 211, 255)   # Nervous Wojak'ın kendi mavisi
W = 6.5

# final-3 (2026-10-11, görsel hakem 7,5/10): 5 ince, seyrek, düzensiz işaret (~6,5 px; ekranda ~3 px, ~400-600 mavi px).
# Orijinallerde (C4V3 S6 181 px / 3 px, C2kk S2 425 px / 4 px, C2fa S5 87 px / 2 px) çizgiler ince ve dağınık;
# final-2'deki 6 x 11 px çizgi siperliğin altında "mavi tarak" gibi okunuyordu. Siperliğin alt kenarı
# (yüzün başladığı y: x 240 -> 204, 350 -> 196, 460 -> 192, 580 -> 181, 700 -> 169) altından başlar, kaşların üstünde biter.
STROKES = [
    [(250, 222), (242, 232), (240, 262), (242, 292), (236, 308), (226, 314)],
    [(352, 214), (356, 220), (355, 238)],
    [(470, 236), (476, 242), (474, 268), (477, 296), (470, 306)],
    [(600, 206), (603, 214), (601, 232), (588, 236)],
    [(697, 190), (704, 198), (700, 232), (697, 262), (701, 290), (692, 308)],
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
