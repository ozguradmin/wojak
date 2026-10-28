"""goeben-fes-1914: hazır kıyafetli iki karakter ve ters köşe yüz varyantı.

    python episodes/goeben-fes-1914/chars/uret.py

Kaynaklar (kaynak/ altında, indirildiği gibi):
  denizci_kaynak.png  wojakland "Spanish Civil War Sailor Wojak" (1080x1169, tools/wojak_site.py get
                      wl:spanish_civil_war_sailor_wojak.webp): koyu denizci kepi (Matrosenmütze biçimi), lacivert denizci
                      yakası + siyah fular; yorgun klasik wojak yüzü, sakal gölgesi; burun ve göz bebekleri sağa.
  osmanli_kaynak.png  HF clayshoaf/Wojaks 5_Twinkjak/15359 "Twinjak Ottoman" (392x574): kırmızı fes, siyah bıyık, yeşil
                      subay ceketi (kırmızı yaka), klasik beyaz yüz; ağız dişli yarım sırıtış.
Kıyafete renk/çizim eklenmez. Yapılanlar:
  - denizci_sakin (A, solda, Alman denizci): kepin üstündeki kırmızı ponpon (İspanyol/Fransız kepi işareti; Alman kepinde
    yok) silindi, kepin üst konturu yeniden çizildi; şeritteki "MARINA" yazısı şerit rengiyle kapatıldı (inpaint).
  - denizci_sok (A, aynı kutu): kaşlar ve göz altı torbaları silinip iri yuvarlak göz + küçük göz bebeği (sağa), yukarı
    kalkık kaş; ağız yerine küçük "O"; başın önünde (kontur dışında, B tarafında) üç ter damlası.
  - osmanli_sakin (B, sağda, Osmanlı subayı, kurgu): 2x büyütme, göğüsten kesim (y 880); dişli yarım sırıtış (kanalda kötü karakter kodu) silinip
    düz, sakin ağız çizildi; göz bebekleri göz yarığının sağ ucuna alındı (burun çizgisi zaten sağda).
Bakış yönü dosyanın kendisine göre kaydedilir (python -m wojak yon ... --yon sag); episode.yaml'da faces: yok.
Çizim yardımcıları karakoy-tunel-1874/chars/uret.py'den kopyalandı.
"""
from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
KAYNAK = HERE / "kaynak"
sys.path.insert(0, str(ROOT / "tools"))
import kit_varyant  # noqa: E402

SS = 4
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)
TEN = (255, 255, 255)


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


def buyut(im, k):
    im = im.resize((im.width * k, im.height * k), Image.LANCZOS)
    rgb = im.convert("RGB").filter(ImageFilter.UnsharpMask(2, 60, 2))
    out = rgb.convert("RGBA")
    out.putalpha(im.getchannel("A"))
    return out


def kaydet(im, ad):
    out = HERE / f"{ad}.png"
    im.save(out, optimize=True)
    print(f"-> {out.relative_to(ROOT)}  {im.width}x{im.height}")


# ---------------------------------------------------------------- A: Alman denizci
KEP = (29, 29, 31)
# kepin üst konturu (ponponun altından geçen çizgi; soldaki (300,118) ve sağdaki (650,34) konturları birleştirir)
KEP_UST = [(398, 114), (420, 105), (450, 95), (500, 76), (540, 60), (588, 44)]


def denizci_temel():
    im = kontur_sabitle(Image.open(KAYNAK / "denizci_kaynak.png").convert("RGBA"))
    a = np.array(im).astype(np.int32)
    H, W = a.shape[:2]
    # 1) ponpon: kontur çizgisinin üstünde kalan her şey saydam; altında kalan turuncu pikseller kep rengine
    yy, xx = np.mgrid[0:H, 0:W]
    xs = [p[0] for p in KEP_UST]
    ys = [p[1] for p in KEP_UST]
    hat = np.interp(xx, xs, ys)
    bolge = (xx >= 330) & (xx <= 592) & (yy < 140)
    ust = bolge & (yy < hat - 3)
    a[ust, 3] = 0
    turuncu = (a[..., 0] > a[..., 2] + 25) & (a[..., 0] > a[..., 1] + 15) & (yy < 160) & (a[..., 3] > 0)
    a[turuncu, :3] = KEP
    im = Image.fromarray(a.astype(np.uint8))
    c = Cizim(im, seed=3)
    c.cizgi(KEP_UST, 7, titrek=0.2)
    im = c.im
    # 2) şeritteki "MARINA" yazısı: açık gri harf pikselleri + kenar yumuşatması inpaint ile şerit rengine
    a = np.array(im)
    rgb = a[..., :3].astype(np.int32)
    harf = np.zeros(a.shape[:2], np.uint8)
    x0, y0, x1, y1 = 455, 160, 800, 300
    blok = rgb[y0:y1, x0:x1]
    harf[y0:y1, x0:x1] = ((blok.mean(-1) > 92) & (a[y0:y1, x0:x1, 3] > 0)).astype(np.uint8) * 255
    harf = cv2.dilate(harf, np.ones((5, 5), np.uint8), iterations=2)
    yuz = rgb.min(-1) > 235  # beyaz alın: inpaint şeride beyaz taşımasın
    harf[cv2.dilate(yuz.astype(np.uint8), np.ones((13, 13), np.uint8)) > 0] = 0
    kaynak = a[..., :3].copy()
    kaynak[yuz] = (66, 66, 80)
    bgr = cv2.inpaint(cv2.cvtColor(kaynak, cv2.COLOR_RGB2BGR), harf, 9, cv2.INPAINT_TELEA)
    dolu = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    m = harf > 0
    a[m, :3] = dolu[m]
    return Image.fromarray(a)


def denizci_sok(im):
    """Hatlar (1x): sol göz + torba 530-660 x 400-485, sağ göz + torba 740-840 x 410-485; kaşlar ve orta alın çizgisi
    535-780 x 336-402; ağız çizgisi 630-760 x 608-636; yüzün sağ konturu x ~845-860 (y 350-520). Çizgi ~7 px."""
    for b in [(528, 336, 782, 404), (528, 398, 662, 488), (738, 404, 838, 488), (622, 604, 768, 640)]:
        im = sil(im, kutu(*b), TEN, tol=-1)
    c = Cizim(im, seed=11)
    # yukarı kalkık, iç uçları yükselmiş kaşlar
    c.cizgi([(536, 372), (566, 352), (604, 344), (640, 350)], 9)
    c.cizgi([(690, 352), (728, 342), (762, 348), (790, 364)], 9)
    # iri yuvarlak gözler, küçük göz bebeği sağa (B'ye doğru)
    c.elips(598, 438, 40, 36, dolgu=WHITE, w=7)
    c.elips(616, 441, 10, 10, dolgu=BLACK)
    c.elips(790, 442, 32, 34, dolgu=WHITE, w=7)
    c.elips(805, 445, 9, 9, dolgu=BLACK)
    # küçük "O" ağız
    c.elips(694, 622, 22, 19, dolgu=(70, 30, 30, 255), w=7)
    im = c.im
    # ter damlaları: başın önünde, yüz konturunun dışında (sağ = B tarafı)
    im = ter(im, [(888, 392, 30), (904, 468, 24), (884, 540, 19)])
    return im


# ---------------------------------------------------------------- B: Osmanlı subayı
K = 2
S = lambda *v: [x * K for x in v]  # noqa: E731


def osmanli_sakin():
    """1x hatlar: ağız (dişli sırıtış) 208-264 x 284-303, çene işareti 236-250 x 306-315; sol göz yarığı 174-219 x 207-223
    (siyah göz 186-210 x 209-222), sağ göz yarığı 261-299 x 207-222 (siyah göz 272-292 x 209-221). Çizgi ~3 px (1x)."""
    im = kontur_sabitle(Image.open(KAYNAK / "osmanli_kaynak.png").convert("RGBA"))
    im = buyut(im, K)
    for b in [(207, 284, 266, 304), (234, 305, 252, 316)]:
        im = sil(im, kutu(*S(*b)), TEN, tol=-1)
    # göz bebekleri: eski siyah blokları silip yarığın sağ ucuna yeniden koy (üst kapak çizgisine dokunmadan)
    for b in [(184, 210, 212, 221), (270, 210, 293, 220)]:
        im = sil(im, kutu(*S(*b)), TEN, tol=-1)
    c = Cizim(im, seed=5)
    c.poligon([tuple(S(196, 209)), tuple(S(217, 209)), tuple(S(216, 221)), tuple(S(197, 221))], BLACK)
    c.poligon([tuple(S(279, 209)), tuple(S(298, 209)), tuple(S(297, 220)), tuple(S(280, 220))], BLACK)
    # sakin, düz ağız (bıyığın altında)
    c.cizgi([tuple(S(220, 293)), tuple(S(238, 294.5)), tuple(S(256, 293))], 6)
    # büst göğüsten kesilir (fesli uzun başta yüz büyüsün; aynı height'ta ~%17 büyük)
    return c.im.crop((0, 0, c.im.width, 880))


if __name__ == "__main__":
    t = denizci_temel()
    kaydet(t, "denizci_sakin")
    kaydet(denizci_sok(t.copy()), "denizci_sok")
    kaydet(osmanli_sakin(), "osmanli_sakin")
