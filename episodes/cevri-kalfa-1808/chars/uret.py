"""cevri-kalfa-1808: hazır kıyafetli iki karakter ve yüz varyantları.

    python episodes/cevri-kalfa-1808/chars/uret.py

Kaynaklar (kaynak/ altında, indirildiği gibi; şeffaf kenarı kırpılmış):
  kalfa_kaynak.png   wojakland "Veil Trad Wife" (https://wojakland.com/gmedia/veil_trad_wife-png/), 671x921; koyu başörtülü,
                     koyu elbiseli kadın. Videoda A: Cevri Kalfa (canlandırma). Kıyafete dokunulmaz.
  mahmud_kaynak.png  wojakland "Sultan Chad" (https://wojakland.com/gmedia/sultan_chad-png/), 842x1036; beyaz kavuk, koyu
                     sakal, profil. Videoda B: Şehzade Mahmud (canlandırma). Dokunulmadı (yalnız kontur sabitleme).
Yapılanlar (kalfa, 2x LANCZOS + UnsharpMask):
  - göğüsten kesildi (1x y 0-690).
  - kalfa_kaygi: hafif gülümseyen pembe dudak silindi, aşağı kıvrık ince ağız; iç ucu kalkık kaşlar.
  - kalfa_sok: iri yuvarlak göz + küçük göz bebeği (sağa), iç ucu kalkık kalın kaş, alında mavi çizgiler, "O" ağız,
    yüzün önünde 3 damla.
Bakış yönü dosyanın kendisine göre kaydedilir (python -m wojak yon ...); episode.yaml'da faces: yok.
Çizim yardımcıları meryem-ana-evi-1891/chars/uret.py'den kopyalandı.
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
KOYU = (70, 18, 22, 255)
TEN = (240, 225, 218)


def kalfa_temel():
    """Göğüsten kesilir (1x y 0-690): yüz kadrajda büyür."""
    im = kontur_sabitle(Image.open(KAYNAK / "kalfa_kaynak.png").convert("RGBA"))
    im = im.crop((0, 0, im.width, 690))
    return buyut(im, K)


def kalfa_kaygi(im):
    """1x hatlar: sol kaş 330-410 x 208-222, sağ kaş 470-534 x 202-222, dudak 403-500 x 404-434."""
    for b in [(326, 203, 414, 226), (466, 198, 538, 224), (398, 400, 506, 438)]:
        im = sil(im, kutu(*S(*b)), TEN, tol=-1)
    c = Cizim(im, seed=7)
    c.cizgi([tuple(S(334, 221)), tuple(S(358, 216)), tuple(S(384, 210)), tuple(S(406, 201))], 4.6 * K)
    c.cizgi([tuple(S(474, 200)), tuple(S(496, 206)), tuple(S(516, 212)), tuple(S(532, 219))], 4.6 * K)
    c.cizgi([tuple(S(420, 424)), tuple(S(436, 419)), tuple(S(452, 417)), tuple(S(468, 419)), tuple(S(484, 425))], 4.4 * K)
    return c.im


def kalfa_sok(im):
    """1x hatlar: gözler 322-416 x 230-292 ve 470-549 x 240-290; yüz konturu sağda x ~545-558."""
    for b in [(326, 203, 414, 226), (466, 198, 538, 224), (398, 400, 506, 438), (320, 228, 418, 294),
              (468, 238, 554, 292)]:
        im = sil(im, kutu(*S(*b)), TEN, tol=-1)
    c = Cizim(im, seed=11)
    c.elips(*S(372, 262, 30, 28), dolgu=WHITE, w=4.4 * K)
    c.elips(*S(511, 264, 26, 27), dolgu=WHITE, w=4.4 * K)
    c.elips(*S(380, 264, 6.0, 6.0), dolgu=BLACK)
    c.elips(*S(518, 266, 5.6, 5.6), dolgu=BLACK)
    c.cizgi([tuple(S(338, 228)), tuple(S(360, 221)), tuple(S(384, 212)), tuple(S(404, 200))], 5.0 * K)
    c.cizgi([tuple(S(478, 199)), tuple(S(496, 207)), tuple(S(516, 214)), tuple(S(536, 220))], 5.0 * K)
    for x0, y0, x1, dy in [(356, 186, 394, -1.5), (410, 185, 452, 1.5), (466, 187, 504, -1), (372, 195, 410, 1.2),
                           (432, 194, 468, -1.2)]:
        c.cizgi([tuple(S(x0, y0)), tuple(S((x0 + x1) / 2, y0 + dy)), tuple(S(x1, y0 + dy * 0.3))], 2.4 * K, renk=MAVI)
    c.elips(*S(452, 420, 12, 15), dolgu=KOYU, w=4.0 * K)
    return ter(c.im, [tuple(S(588, 232, 9)), tuple(S(596, 280, 8.5)), tuple(S(588, 326, 7.5))])


def mahmud_sakin():
    return kontur_sabitle(Image.open(KAYNAK / "mahmud_kaynak.png").convert("RGBA"))


if __name__ == "__main__":
    k = kalfa_temel()
    kaydet(kalfa_kaygi(k.copy()), "kalfa_kaygi")
    kaydet(kalfa_sok(k.copy()), "kalfa_sok")
    kaydet(mahmud_sakin(), "mahmud_sakin")
