"""yeralti-camii-karakoy: iki hazır kıyafetli karakter ve ters köşe yüz varyantı.

    python episodes/yeralti-camii-karakoy/chars/uret.py

Kaynaklar (kaynak/ altında):
  dervis_a.png             wojakland "Muslim Wojak" (Muslim_Wojak.png,
                           https://wojakland.com/wp-content/grand-media/image/original/Muslim_Wojak.png), 784x955 kesilmiş;
                           klasik beyaz wojak yüzü, sarık + boyun örtüsü; gözler sağa bakar. B (sağ), adsız yaşlı derviş.
  hezarfen_emin.png        episodes/hezarfen-galata-ucusu/chars/hezarfen_emin.png (wojakland "Muslim Chad" ailesi):
                           beyaz sarık, siyah sakal, profilden sağa bakar. A (sol), adsız genç derviş.
Kıyafete ve başlıklara dokunulmaz. Yapılanlar:
  - dervis_sakin = kaynağın kendisi (kontur opak).
  - dervis_sok: aynı kutu; alındaki kırışık çizgileri yerine 5 düzensiz mavi soğuk ter çizgisi, iri yuvarlak gözler
    ve küçük göz bebekleri, iç uçları kalkık kalın kaşlar, "O" ağız, başın önünde (sağ) kontur dışında 3 damla.
Bakış yönü dosyanın kendisine göre kaydedilir (python -m wojak yon ...); episode.yaml'da faces: yok.
Çizim yardımcıları kasikci-elmasi/chars/uret.py'den kopyalandı.
"""
from __future__ import annotations

import math
import random
import shutil
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
TEN = (255, 255, 255)


def poly_mask(size, pts) -> np.ndarray:
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).polygon([tuple(p) for p in pts], fill=255)
    return np.array(m) > 0


def sil(im, pts, renk=TEN, tol=10):
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


def ter(im, damlalar):
    tmp = HERE / "__kit_tmp.png"
    im.save(tmp)
    try:
        kit_varyant.make(tmp, {"drops": [list(d) for d in damlalar]}, tmp)
        return Image.open(tmp).convert("RGBA").copy()
    finally:
        tmp.unlink(missing_ok=True)


def sil_koyu(im, pts, esik=740):
    a = np.array(im).astype(np.int32)
    m = poly_mask(im.size, pts) & (a[..., :3].sum(-1) < esik) & (a[..., 3] > 0)
    a[m, :3] = 255
    a[m, 3] = 255
    return Image.fromarray(a.astype(np.uint8))


def kontur_sabitle(im):
    a = np.array(im).astype(np.int32)
    m = (a[..., :3].sum(-1) < 240) & (a[..., 3] > 30)
    a[m, 3] = 255
    return Image.fromarray(a.astype(np.uint8))


def kaydet(im, ad):
    out = HERE / f"{ad}.png"
    im.save(out, optimize=True)
    print(f"-> {out.relative_to(ROOT)}  {im.width}x{im.height}")


def dervis_sok(im):
    """Muslim Wojak 784x955. Ölçülen hatlar (px, gerçek boyut): alın kırışıkları 405-625 x 374-432; sol kaş
    352-467 x 450-480, sağ kaş 563-655 x 458-480, kaş arası çizgiler (467-486 x 478-503) ve (571-579 x 484-518);
    sol göz 368-474 x 514-564, sağ göz 578-662 x 525-576; ağız 442-598 x 752-780; yüz konturu sağda x ~705-712."""
    # alın kırışıkları ve sol kaş: yalnız koyu/gri çizgi pikselleri silinir; çokgenler sarığın konturunun
    # birkaç px içinde kalır (sarığın açık gri kumaşı ve konturu korunur)
    im = sil_koyu(im, [(408, 434), (408, 424), (424, 408), (448, 380), (460, 369), (500, 367), (590, 373),
                       (642, 382), (642, 436)])
    im = sil_koyu(im, [(366, 446), (492, 446), (492, 506), (356, 506), (354, 480), (362, 460)])
    im = sil(im, kutu(560, 452, 660, 520), tol=-1)
    im = sil(im, kutu(364, 510, 478, 568), tol=-1)
    im = sil(im, kutu(574, 520, 666, 580), tol=-1)
    im = sil(im, kutu(438, 748, 602, 786), tol=-1)
    c = Cizim(im, seed=11)
    # iri yuvarlak gözler, küçük göz bebekleri (sağa, dosyanın baktığı yöne)
    c.elips(422, 538, 36, 30, dolgu=WHITE, w=5.0)
    c.elips(622, 548, 30, 28, dolgu=WHITE, w=5.0)
    c.elips(428, 540, 6.5, 6.5, dolgu=BLACK)
    c.elips(627, 549, 6.0, 6.0, dolgu=BLACK)
    # iç uçları kalkık kalın kaşlar
    c.cizgi([(362, 492), (410, 478), (470, 446)], 6.0)
    c.cizgi([(570, 450), (614, 466), (660, 482)], 6.0)
    # "O" ağız
    c.elips(520, 768, 17, 22, dolgu=(60, 20, 20, 255), w=5.0)
    # alında 5 düzensiz mavi soğuk ter çizgisi
    MAVI = (70, 130, 230, 255)
    for x, y0, L, s in [(432, 392, 34, 1), (462, 386, 40, -1), (494, 384, 42, 1), (526, 386, 38, -1), (556, 392, 30, 1)]:
        c.cizgi([(x, y0), (x + 3 * s, y0 + L * 0.35), (x - 2 * s, y0 + L * 0.7), (x + 1.5 * s, y0 + L)], 4.2,
                renk=MAVI, titrek=0.6)
    # başın önünde (sağ), kontur dışında ~20 px uzakta 3 damla
    return ter(c.im, [(738, 470, 13), (748, 530, 11), (740, 590, 10)])


if __name__ == "__main__":
    shutil.copy(KAYNAK / "hezarfen_emin.png", HERE / "genc_sakin.png")
    print("-> genc_sakin.png", Image.open(HERE / "genc_sakin.png").size)
    t = kontur_sabitle(Image.open(KAYNAK / "dervis_a.png").convert("RGBA"))
    kaydet(t, "dervis_sakin")
    kaydet(dervis_sok(t.copy()), "dervis_sok")
