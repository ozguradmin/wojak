"""meryem-ana-evi-1891: arka plan ve kanıt görsellerini kaynaklardan üretir.

    python episodes/meryem-ana-evi-1891/gorsel.py

img/orman_kaynak.jpg  vom Thüringer, "Pinus brutia forest Side Turkey 2" (2011), CC BY 3.0 -> img/arka_orman.jpg
                      (S1-S3: dağda kızılçam ormanında patika; Bülbüldağı'nın kendisi değil, aynı türden Ege/Akdeniz yamacı)
img/arka_kaynak.jpg   Mfryc (varsayılan), "House of the Virgin Mary" (2005), CC BY-SA 2.5 -> img/arka_ev.jpg
                      (S4, karttan sonra: Meryem Ana Evi'nin taş cephesi; turist, tabela, saksılar, çatı kırpım dışında)
img/kitap_kaynak.jpg  "Leben der heiligen Jungfrau Maria", Stuttgart: Cotta 1890 (kamu malı; IA lebenderheiligen00emme,
                      leaf n6, başlık sayfası) -> img/kanit_1.jpg
img/kanit2_kaynak.jpg Gabriel von Max, "Anna Katharina Emmerick" (1885, Neue Pinakothek), PD-Art -> img/kanit_2.jpg (son kare)
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance

IMG = Path(__file__).resolve().parent / "img"


def olc(im, ad):
    w = 720
    h = w * im.height // im.width
    a = np.asarray(im.convert("RGB").resize((w, h))).astype(float)
    hsv = np.asarray(im.convert("RGB").convert("HSV").resize((w, h))).astype(float)
    g = np.asarray(im.convert("L").resize((w, h))).astype(float)
    lap = np.abs(g[1:-1, 1:-1] * 4 - g[:-2, 1:-1] - g[2:, 1:-1] - g[1:-1, :-2] - g[1:-1, 2:]).var() ** 0.5
    print(f"{ad}: {im.size} parlaklık {a.mean():.0f} doygunluk {hsv[..., 1].mean() / 255:.2f} laplace~{lap:.1f}")


def arka_orman(x0=380, y0=150, n=1290, renk=0.45, parlak=1.04):
    im = Image.open(IMG / "orman_kaynak.jpg").convert("RGB")
    im = im.crop((x0, y0, x0 + n, y0 + n)).resize((1080, 1080), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(renk)
    im = ImageEnhance.Brightness(im).enhance(parlak)
    im.save(IMG / "arka_orman.jpg", quality=92)
    olc(im, "arka_orman")


def arka_ev(x0=640, y0=300, n=760, gama=0.70, renk=0.66):
    """1920x1280 kaynak: kemerli kapı, ikinci kemer ve çınar gövdesi. Çatıdaki gri kubbe örtüsü (y < 300), kapı önündeki
    paspas (y > 1060), sağdaki turistler ve 'PRIVATE' tabelası (x > 1640), soldaki saksılar (x < 300) dışarıda.
    Açık kapının içindeki beyaz bilgi levhası (1036-1092 x 910-958) çevresindeki karanlık iç mekân tonuyla örtülür.
    Gölgeli cephe parlaklık yerine gama ile açılır (taş dokusu solmasın)."""
    im = Image.open(IMG / "arka_kaynak.jpg").convert("RGB")
    a = np.asarray(im).copy()
    cevre = np.concatenate([a[900:968, 1020:1034].reshape(-1, 3), a[900:968, 1094:1108].reshape(-1, 3)])
    a[906:962, 1032:1096] = np.median(cevre, axis=0).astype(np.uint8)
    # kapı içi (ikon çerçevesi, levhalar) gamadan sonra seçilmesin: karanlık iç mekânı biraz daha koyulaştır
    ic = a[690:1062, 1012:1120].astype(float)
    a[690:1062, 1012:1120] = (ic * 0.45).astype(np.uint8)
    im = Image.fromarray(a)
    im = im.crop((x0, y0, x0 + n, y0 + n)).resize((1080, 1080), Image.LANCZOS)
    im = im.point(lambda v: round(255 * (v / 255) ** gama))
    im = ImageEnhance.Color(im).enhance(renk)
    im.save(IMG / "arka_ev.jpg", quality=92)
    olc(im, "arka_ev")


def kanit_1(y0=0.058, y1=0.502, x0=0.0, x1=1.0):
    """Başlık sayfası: 'Leben der heiligen Jungfrau Maria ... Anna Katharina Emmerich' satırları; tam satırlarda kırpım,
    yalnız autocontrast (kâğıt tonu korunur)."""
    im = Image.open(IMG / "kitap_kaynak.jpg").convert("RGB")
    W, H = im.size
    im = im.crop((round(x0 * W), round(y0 * H), round(x1 * W), round(y1 * H)))
    h = round(im.height * 1080 / im.width)
    im = im.resize((1080, h), Image.LANCZOS)
    from PIL import ImageOps
    im = ImageOps.autocontrast(im, cutoff=0.5)
    im.save(IMG / "kanit_1.jpg", quality=94)
    olc(im, "kanit_1")


def kanit_2(y0=230, h=1450):
    """Yatakta, başı sargılı Emmerich; mum ve yastıklar kadrajda. Üstteki ressam yazısı (y < 120) ve alttaki haç
    (y > 1900) dışarıda."""
    im = Image.open(IMG / "kanit2_kaynak.jpg").convert("RGB")
    im = im.crop((0, y0, im.width, y0 + h)).resize((1080, round(h * 1080 / im.width)), Image.LANCZOS)
    im.save(IMG / "kanit_2.jpg", quality=94)
    olc(im, "kanit_2")


if __name__ == "__main__":
    arka_orman()
    arka_ev()
    kanit_1()
    kanit_2()
