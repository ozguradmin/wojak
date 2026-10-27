"""karakoy-tunel-1874: hazır kıyafetli iki fesli karakter ve ters köşe yüz varyantı.

    python episodes/karakoy-tunel-1874/chars/uret.py

Kaynaklar (kaynak/ altında, tools/wojak_lib.py get ile indirildiği gibi; HF clayshoaf/Wojaks = wojakparadise arşivi):
  fesli_kaynak.png   5_Doomer/13970 "Ottoman Doomer" (435x514): kırmızı fes, siyah takım + kravat, siyah bıyık, pipo;
                     klasik beyaz wojak yüzü; mavi gözyaşları; burun ve göz bebekleri sağa
  fesli2_kaynak.png  5_Crying_Wojak/438 "Sad Ottoman Person" (429x492): kırmızı fes, kır saç, kır bıyık, koyu takım + kahve
                     kravat; klasik beyaz yüz; mavi gözyaşları; burun ve göz bebekleri sağa
Kıyafete dokunulmaz; büst göğüsten kesilir (A y 450, B y 492 = tam boy; 1x). Yapılanlar:
  - esnaf_sakin (A, solda, İstanbullu): 2x büyütme (LANCZOS + hafif keskinleştirme); mavi gözyaşları silindi (ağır kapaklı,
    kuşkulu ama sakin göz kalır). Pipo yerinde.
  - memur_sakin (B, sağda, Tünel şirketinin memuru): 2x büyütme; gözyaşları silindi.
  - esnaf_sok (A, aynı kutu): gözler ve alın kırışıkları silinip iri yuvarlak göz + küçük göz bebeği (sağa), kalkık kaş;
    başın önünde (kontur dışında) üç ter damlası.
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


def gozyasi_sil(im, b):
    """Kutudaki mavi gözyaşı piksellerini ve açık renkli kenar yumuşatmasını beyaza çevirir; siyah çizgiler kalır."""
    a = np.array(im).astype(np.int32)
    x0, y0, x1, y1 = b
    blok = a[y0:y1, x0:x1]
    rgb = blok[..., :3]
    mavi = (rgb[..., 2] > rgb[..., 0] + 25) & (rgb[..., 1] > rgb[..., 0] + 10)
    koyu_mavi = mavi & (rgb.max(-1) < 90)
    acik = (rgb.sum(-1) > 330) & (blok[..., 3] > 0)  # hayalet kenarlar (açık gri-camgöbeği)
    blok[(mavi & ~koyu_mavi) | acik, :3] = 255
    blok[koyu_mavi, :3] = 0
    return Image.fromarray(a.astype(np.uint8))


def temel(ad, yas_kutu):
    im = kontur_sabitle(Image.open(KAYNAK / ad).convert("RGBA"))
    im = gozyasi_sil(im, yas_kutu)
    return buyut(im, K)


def esnaf_sok(im):
    """1x hatlar (fesli_kaynak): sol göz 214-266 x 202-226 (siyah göz 225-250 x 208-222), sağ göz 296-342 x 203-226;
    alın kırışıkları 255-275 x 183-203 ve 296-308 x 186-206; yüzün sağ konturu x ~352-360 (y 200-300). Çizgi ~4 px."""
    for b in [(212, 200, 268, 228), (294, 201, 344, 228), (255, 182, 276, 204), (295, 185, 309, 207)]:
        im = sil(im, kutu(*S(*b)), TEN, tol=-1)
    c = Cizim(im, seed=11)
    c.elips(*S(240, 213, 21, 19), dolgu=WHITE, w=4.2 * K)
    c.elips(*S(321, 214, 16, 18), dolgu=WHITE, w=4.2 * K)
    c.elips(*S(247, 214, 5.5, 5.5), dolgu=BLACK)
    c.elips(*S(327, 215, 5, 5), dolgu=BLACK)
    c.cizgi([tuple(S(219, 196)), tuple(S(231, 187)), tuple(S(248, 184)), tuple(S(263, 190))], 4.2 * K)
    c.cizgi([tuple(S(304, 192)), tuple(S(315, 185)), tuple(S(330, 185)), tuple(S(342, 192))], 4.2 * K)
    return ter(c.im, [tuple(S(375, 205, 14)), tuple(S(382, 245, 12)), tuple(S(375, 281, 9))])


def kes(im, y1):
    """Büstü göğüsten keser (kadrajın altından zaten kesik): aynı height'ta yüz büyür (fes PNG'nin üstünü alıyor)."""
    return im.crop((0, 0, im.width, y1 * K))


if __name__ == "__main__":
    esnaf = temel("fesli_kaynak.png", (205, 200, 350, 270))
    kaydet(kes(esnaf, 450), "esnaf_sakin")
    kaydet(kes(esnaf_sok(esnaf.copy()), 450), "esnaf_sok")
    kaydet(kes(temel("fesli2_kaynak.png", (215, 240, 360, 315)), 492), "memur_sakin")
