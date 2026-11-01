"""hierapolis-cehennem-kapisi: arka plan ve kanıt görsellerini kaynaklardan üretir.

    python episodes/hierapolis-cehennem-kapisi/gorsel.py

img/arka_aday4.jpg   Interfase, "Plutonion in Hierapolis 13" (2025), CC BY-SA 4.0 -> img/arka.jpg (kare kırpım, 1,42x, parlaklık)
                     (tur 1-2: arka_aday1, Raddato, Apollon Tapınağı; tur 2 hakemi mağara görünmediği için değiştirildi -> arka())
img/kanit_aday1b.jpg Interfase, "Plutonion in Hierapolis 3" (2025), CC BY-SA 4.0 -> img/kanit_1.jpg (kırpım)
img/strabon_sayfa.jpg Strabon, Geography VI, çev. H. L. Jones, Loeb 1929, s. 187 (kamu malı; IA in.ernet.dli.2015.57230, leaf 195)
                     -> img/kanit_2.jpg (tam satırlarda kırpım, yalnız autocontrast)
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

IMG = Path(__file__).resolve().parent / "img"


def olc(im, ad):
    a = np.asarray(im.convert("RGB").resize((720, 720 * im.height // im.width))).astype(float)
    hsv = np.asarray(im.convert("RGB").convert("HSV").resize((720, 720 * im.height // im.width))).astype(float)
    g = np.asarray(im.convert("L").resize((720, 720 * im.height // im.width))).astype(float)
    lap = np.abs(g[1:-1, 1:-1] * 4 - g[:-2, 1:-1] - g[2:, 1:-1] - g[1:-1, :-2] - g[1:-1, 2:]).var() ** 0.5
    print(f"{ad}: {im.size} parlaklık {a.mean():.0f} doygunluk {hsv[..., 1].mean() / 255:.2f} laplace~{lap:.1f}")


def arka():
    im = Image.open(IMG / "arka_aday1.jpg").convert("RGB")
    im = im.crop((60, 0, 60 + 1272, 1272))          # sol-orta: sağdaki çit ve anten direkleri dışarıda
    im = im.resize((1080, 1080), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(0.68)
    im = ImageEnhance.Brightness(im).enhance(0.93)
    im.save(IMG / "arka.jpg", quality=92)
    olc(im, "arka")


def arka_kapi(x0=120, y0=140, n=760):
    """Interfase, 'Plutonion in Hierapolis 13' (2025, CC BY-SA 4.0): mağara ağzı, kemer, su ve theatron basamakları.
    Üstteki modern yürüme yolu korkuluğu (y < 130) ve alttaki projektör (x 690-860, y 905-1120) kırpımın dışında."""
    im = Image.open(IMG / "arka_aday4.jpg").convert("RGB")
    im = im.crop((x0, y0, x0 + n, y0 + n)).resize((1080, 1080), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(1.12)
    im = ImageEnhance.Brightness(im).enhance(0.92)
    im.save(IMG / "arka.jpg", quality=92)
    olc(im, "arka (kapı)")


def kanit_1():
    im = Image.open(IMG / "kanit_aday1b.jpg").convert("RGB")
    im = im.crop((200, 150, 200 + 1460, 150 + 973)).resize((1080, 720), Image.LANCZOS)
    im.save(IMG / "kanit_1.jpg", quality=92)
    olc(im, "kanit_1")


def kanit_2():
    # sayfa görünümü korunur: "led into it fall ..." satırından (y 1477) dipnotlara ve sayfa numarasına (187) kadar;
    # tam satırlarda, kâğıt tonu korunur (autocontrast yok), yalnız hafif gama ile mürekkep koyulaştırılır
    im = Image.open(IMG / "strabon_sayfa.jpg").convert("L")
    blok = im.crop((135, 1477, 1385, 2196))
    im = Image.new("L", (1250, 719 + 24), 255)    # üstte kâğıt payı; komşu satırın alt uzantıları kadraja girmez
    im.paste(blok, (0, 24))
    im = im.point(lambda v: round(255 * (v / 255) ** 1.15))
    w = 1080
    im = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
    # tarama bembeyaz (kâğıt 255): beyazı kitap kâğıdı tonuna çek (renk ayarı; metin ve düzen aynen)
    im = ImageOps.colorize(im, black=(28, 24, 20), white=(236, 230, 216))
    im.save(IMG / "kanit_2.jpg", quality=94)
    olc(im, "kanit_2")


if __name__ == "__main__":
    arka_kapi()
    kanit_1()
    kanit_2()
