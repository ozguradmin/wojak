"""en-yamaguchi-two-bombs karakterleri:  python episodes/en-yamaguchi-two-bombs/chars/uret.py

A (sol, Yamaguchi): wojakland 'Japan Business Wojak' (a_kaynak.png, 773x829). Kaynak PNG'nin sol kenarında omuz düz çizgiyle kesikti
  (hakem MUST, tur 1): tuvale 170 px sol genişletilip omuz konturu aşağı doğru yuvarlanarak sürdürüldü, gövde dolgusu aynı renk -> a_sakin.png.
B (sağ, patron): en-apollo-moon-disaster'daki 'Suit Wojak' fötr şapkalı PNG'ler (b_sakin, b_sok = ters köşe), ayna/silüet aynı.
"""
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
SS = 4
PAD = 170

im = Image.open(HERE / "a_kaynak.png").convert("RGBA")
W, H = im.size
a = np.array(im)
fill = tuple(int(v) for v in a[H - 40, 60, :3])
col = a[:, 0, 3]
y0 = int(np.where(col > 128)[0].min())          # kesik kenarda omuz üst konturu
canvas = Image.new("RGBA", (W + PAD, H), (0, 0, 0, 0))
canvas.paste(im, (PAD, 0))
L = Image.new("RGBA", (canvas.width * SS, H * SS), (0, 0, 0, 0))
d = ImageDraw.Draw(L)
k = lambda p: (p[0] * SS, p[1] * SS)
# omuz yayı: (PAD, y0) -> sola doğru önce hafif, sonra dikleşerek iner
pts = []
for i in range(0, 41):
    t = i / 40
    x = PAD - t * PAD
    y = y0 + 3 * t + (H - y0 - 3) * t ** 2.0
    pts.append((x, y))
poly = [k((PAD + 2, y0 + 2))] + [k(p) for p in pts] + [k((0, H + 5)), k((PAD + 2, H + 5))]
d.polygon(poly, fill=fill + (255,))
d.line([k(p) for p in pts], fill=(0, 0, 0, 255), width=7 * SS, joint="curve")
L = L.resize(canvas.size, Image.LANCZOS)
out = Image.alpha_composite(canvas, L)
out.save(HERE / "a_sakin.png")
print(out.size, fill, y0)
