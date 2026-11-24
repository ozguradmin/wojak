"""anemas-zindani-1376: hazır kıyafetli iki karakter ve ters köşe yüz varyantı.

    python episodes/anemas-zindani-1376/chars/uret.py

Kaynaklar (kaynak/ altında):
  imparator_kaynak.png  episodes/kiz-kulesi-efsanesi/chars/imparator_bizans.png (onaylı referans setinden; kamelaukion taç,
                        pendilia, sakal; klasik beyaz yüz, burun ve göz bebekleri sağa), 586x742
  muhafiz2_kaynak.png   wojakland "Knight 6 Wojak" (https://wojakland.com/gmedia/knight_6_wojak_1-png/), 850x1007; düz MS-Paint
                        çizimi, konik miğfer + zincir başlık, klasik beyaz yüz (tur 3'te gölgeli muhafiz_kaynak.png'nin yerine)
Kıyafete dokunulmaz. Yapılanlar:
  - imparator_sakin (A, solda, V. İoannis): 2x büyütme (LANCZOS + UnsharpMask), sağa 240 px saydam pay (ter damlaları için).
  - imparator_sok (A, aynı kutu, ters köşe): gözler ve ağız çizgisi silinip iri yuvarlak göz + küçük göz bebeği (sağa),
    iç ucu kalkık kalın kaş, sakal içinde "O" ağız, alında 4 kısa mavi çizgi, başın önünde (kontur dışında) üç ter damlası.
  - muhafiz_sakin (B, sağda): çene altından kesim (y 0-715). Yüz değişmez.
Bakış yönü dosyanın kendisine göre kaydedilir (python -m wojak yon ... --yon sag); episode.yaml'da faces: yok.
Çizim yardımcıları orban-topu-bizans/chars/uret.py'den kopyalandı.
"""
from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
KAYNAK = HERE / "kaynak"
sys.path.insert(0, str(ROOT / "tools"))
import kit_varyant  # noqa: E402

SS = 4
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)


def poly_mask(size, pts) -> np.ndarray:
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).polygon([tuple(p) for p in pts], fill=255)
    return np.array(m) > 0


def sil(im, pts, renk, tol=10):
    a = np.array(im).astype(np.int32)
    m = poly_mask(im.size, pts)
    d = np.abs(a[..., :3] - np.array(renk)).sum(-1)
    m &= (d > tol) & (a[..., 3] > 0)
    a[m, :3] = renk
    a[m, 3] = 255
    return Image.fromarray(a.astype(np.uint8))


def kutu(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def catmull(pts, n=14):
    P = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    out.append(P[-2])
    return out


class Cizim:
    def __init__(self, im, seed=1):
        self.im = im
        self.rng = random.Random(seed)

    def _maske(self):
        W, H = self.im.size
        m = Image.new("L", (W * SS, H * SS), 0)
        return m, ImageDraw.Draw(m)

    def _bas(self, m, renk):
        W, H = self.im.size
        m = m.resize((W, H), Image.LANCZOS).point(lambda v: max(0, min(255, (v - 64) * 2)))
        self.im.paste(Image.new("RGBA", (W, H), renk), (0, 0), m)

    def cizgi(self, pts, w, renk=BLACK, titrek=0.3):
        p = catmull(pts) if len(pts) > 2 else list(pts)
        ph = self.rng.random() * 6
        p = [(x + titrek * math.sin(i * 0.41 + ph), y + titrek * math.cos(i * 0.33 + ph)) for i, (x, y) in enumerate(p)]
        m, d = self._maske()
        q = [(x * SS, y * SS) for x, y in p]
        d.line(q, fill=255, width=round(w * SS), joint="curve")
        r = w * SS / 2
        for x, y in (q[0], q[-1]):
            d.ellipse([x - r, y - r, x + r, y + r], fill=255)
        self._bas(m, renk)

    def elips(self, cx, cy, rx, ry, dolgu=None, w=0, renk=BLACK):
        b = [(cx - rx) * SS, (cy - ry) * SS, (cx + rx) * SS, (cy + ry) * SS]
        if dolgu is not None:
            m, d = self._maske()
            d.ellipse(b, fill=255)
            self._bas(m, dolgu)
        if w:
            m, d = self._maske()
            d.ellipse(b, outline=255, width=round(w * SS))
            self._bas(m, renk)

    def poligon(self, pts, dolgu):
        m, d = self._maske()
        d.polygon([(x * SS, y * SS) for x, y in pts], fill=255)
        self._bas(m, dolgu)


def ter(im, damlalar):
    tmp = HERE / "__kit_tmp.png"
    im.save(tmp)
    try:
        kit_varyant.make(tmp, {"drops": [list(d) for d in damlalar]}, tmp)
        return Image.open(tmp).convert("RGBA").copy()
    finally:
        tmp.unlink(missing_ok=True)


def kontur_sabitle(im):
    """Kesimde yarı saydam kalmış siyah kontur piksellerini (koyu RGB, alfa > 30) tam opak yapar."""
    a = np.array(im).astype(np.int32)
    m = (a[..., :3].sum(-1) < 240) & (a[..., 3] > 30)
    a[m, 3] = 255
    return Image.fromarray(a.astype(np.uint8))


def kaydet(im, ad):
    out = HERE / f"{ad}.png"
    im.save(out, optimize=True)
    print(f"-> {out.relative_to(ROOT)}  {im.width}x{im.height}")



TEN = (255, 255, 255)
from PIL import ImageFilter  # noqa: E402


def buyut(im, k):
    im = im.resize((im.width * k, im.height * k), Image.LANCZOS)
    rgb = im.convert("RGB").filter(ImageFilter.UnsharpMask(2, 60, 2))
    out = rgb.convert("RGBA")
    out.putalpha(im.getchannel("A"))
    return out


def siyah_sil(im, b, esik=640):
    """Kutudaki koyu (siyah çizgi) pikselleri beyaza çevirir; sakal/bıyık kahvesi kalır."""
    a = np.array(im).astype(np.int32)
    x0, y0, x1, y1 = b
    blok = a[y0:y1, x0:x1]
    rgb = blok[..., :3]
    m = ((rgb.max(-1) - rgb.min(-1)) < 30) & (rgb.sum(-1) < esik) & (blok[..., 3] > 0)  # yalnız gri/siyah
    blok[m, :3] = 255
    blok[m, 3] = 255
    return Image.fromarray(a.astype(np.uint8))




K = 2
S = lambda *v: [x * K for x in v]  # noqa: E731


MAVI = (60, 120, 230, 255)
PAY = 240


def yumusak_buyut(im):
    """2x büyütme, basamaklı (aliasing) konturu yuvarlar (görsel hakem tur 1 SHOULD): 4x bicubic -> medyan 9 renk
    tabanı; siyah çizgi maskesi 4x'te Gauss(2,2) ile yumuşatılıp eşikle yeniden keskinleştirilir -> 2x LANCZOS."""
    big = im.resize((im.width * 4, im.height * 4), Image.BICUBIC)
    rgb = np.array(big.convert("RGB")).astype(float)
    cizgi = Image.fromarray(((rgb.max(-1) < 50) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2.2))
    c = np.clip((np.array(cizgi).astype(float) - 100) / 56, 0, 1)[..., None]   # yuvarlanmış çizgi maskesi
    taban = np.array(big.convert("RGB").filter(ImageFilter.MedianFilter(9))).astype(float)
    out = Image.fromarray((taban * (1 - c)).clip(0, 255).astype(np.uint8))
    out = out.resize((im.width * 2, im.height * 2), Image.LANCZOS).convert("RGBA")
    out.putalpha(im.resize((im.width * 2, im.height * 2), Image.LANCZOS).getchannel("A"))
    return out


def imparator_sakin():
    im = kontur_sabitle(Image.open(KAYNAK / "imparator_kaynak.png").convert("RGBA"))
    im = yumusak_buyut(im)
    out = Image.new("RGBA", (im.width + PAY, im.height), (0, 0, 0, 0))
    out.paste(im, (0, 0))
    return out


def agiz_kapat(im, tohum=(700, 1200)):
    """Sakal içindeki beyaz ağız boşluğunu (içindeki ağız çizgisi ve çevresindeki siyah halka dahil) sakal kahvesiyle
    doldurur; yama izi kalmaz. Dönen merkez, yeni "O" ağzın yeridir (2x koordinat)."""
    from scipy import ndimage
    a = np.array(im).astype(np.int32)
    rgb = a[..., :3]
    beyaz = (rgb.min(-1) > 200) & (a[..., 3] > 0)
    kutu_m = np.zeros(beyaz.shape, bool)
    kutu_m[1124:1300, 590:1030] = True       # sakal içindeki ağız çevresi (2x)
    # kontur boşluklarından yüzün beyazına sızmasın: siyahı 5 px kalınlaştırıp etiketle, sonra geri genişlet
    siyah = ndimage.binary_dilation(rgb.max(-1) < 90, iterations=5)
    lab, _ = ndimage.label(beyaz & kutu_m & ~siyah)
    bolge = ndimage.binary_dilation(lab == lab[tohum[1], tohum[0]], iterations=6) & beyaz
    dolu = ndimage.binary_fill_holes(bolge)
    halka = ndimage.binary_dilation(dolu, iterations=22) & (rgb.min(-1) < 200) & kutu_m   # kontur + kenar yumuşatma halesi
    m = dolu | halka
    # sakal içinde kalan küçük beyaz benekler (kenar yumuşatma artığı)
    blab, bn = ndimage.label((rgb.min(-1) > 200) & ndimage.binary_dilation(dolu, iterations=22) & kutu_m & ~m)
    for i, n in enumerate(ndimage.sum(np.ones_like(blab), blab, range(1, bn + 1)), 1):
        if n < 300:
            m |= blab == i
    a[m, :3] = SAKAL
    a[m, 3] = 255
    ys, xs = np.nonzero(dolu)
    return Image.fromarray(a.astype(np.uint8)), (xs.mean(), ys.mean())


SAKAL = (70, 32, 15)


def imparator_sok(im):
    """2x koordinatlar. 1x hatlar: sol göz 268-360 x 365-415, sağ göz 455-535 x 372-420; ağız sakal içindeki beyaz
    boşluk (agiz_kapat ile sakal rengine döner); taç bandının alt kenarı y ~305; yüzün sağ konturu x ~560."""
    W = (255, 255, 255)
    for b in [(262, 352, 366, 420), (450, 360, 542, 424)]:
        im = sil(im, kutu(*S(*b)), W, tol=-1)
    im, (mx, my) = agiz_kapat(im)
    c = Cizim(im, seed=11)
    c.elips(*S(312, 392, 40, 37), dolgu=WHITE, w=4.5 * K)
    c.elips(*S(496, 396, 32, 35), dolgu=WHITE, w=4.5 * K)
    # göz bebekleri bakılan yöne (sağa) belirgin kaymış
    c.elips(*S(330, 396, 7, 7), dolgu=BLACK)
    c.elips(*S(511, 399, 6.5, 6.5), dolgu=BLACK)
    # iç ucu kalkık kaşlar (yüz sağa bakıyor: soldaki gözün iç ucu sağda, sağdakinin solda)
    c.cizgi([tuple(S(270, 352)), tuple(S(300, 345)), tuple(S(330, 336)), tuple(S(356, 324))], 6 * K)
    c.cizgi([tuple(S(458, 326)), tuple(S(480, 338)), tuple(S(508, 346)), tuple(S(534, 352))], 6 * K)
    # sakal içinde "O" ağız (eski ağız boşluğunun ortasında)
    c.elips(mx, my, 34, 40, dolgu=(70, 18, 22, 255), w=4.5 * K)
    # bıyığın ortasındaki boşluk sakal rengine döndü: üstünü bıyık konturuyla kapat
    c.cizgi([(806, 1122), (836, 1118), (868, 1122)], 4.5 * K)
    # alında 5 düzensiz mavi çizgi (kaşların arası ve üstü; yanağa değil)
    for pts in ([(366, 316), (380, 311), (396, 315)], [(406, 320), (421, 315), (437, 320)],
                [(372, 332), (387, 327), (402, 331)], [(412, 338), (427, 333), (443, 338)],
                [(446, 314), (458, 310), (470, 314)]):
        c.cizgi([tuple(S(*p)) for p in pts], 4.5 * K, renk=MAVI)
    return ter(c.im, [tuple(S(612, 360, 16)), tuple(S(628, 430, 14)), tuple(S(615, 495, 12))])


def muhafiz_sakin():
    """Tur 3: gölgeli Varangian muhafız yerine düz çizimli wojakland "Knight 6 Wojak" (konik miğfer, zincir başlık;
    klasik beyaz yüz, göz bebekleri sağa). Çenenin altından kesildi (y 0-715; yüz büyüsün): alttaki kırmızı cübbedeki sarı arma (ülke işareti)
    kadraja girmez."""
    im = kontur_sabitle(Image.open(KAYNAK / "muhafiz2_kaynak.png").convert("RGBA"))
    return im.crop((0, 0, im.width, 715))


if __name__ == "__main__":
    a = imparator_sakin()
    kaydet(a, "imparator_sakin")
    kaydet(imparator_sok(a.copy()), "imparator_sok")
    kaydet(muhafiz_sakin(), "muhafiz_sakin")
