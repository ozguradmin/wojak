"""kazdagi-sarikiz: hazır kıyafetli iki karakter ve ters köşe yüz varyantı.

    python episodes/kazdagi-sarikiz/chars/uret.py

Kaynaklar (kaynak/ altında, wojakland):
  baba_kaynak.png  wl:Muslim_Wojak.png (784x954): sarıklı, başı ve boynu sargılı klasik wojak. A (sol): Sarıkız'ın
                   babası (efsane kişisi; kurgu).
  kiz_basortulu_kaynak.png  wl:eastern_europe_headscarf_tradwife_wojak.png (627x865): başörtülü, basma elbiseli kız.
                   B (sağ): Sarıkız. (Tur 1'deki wl:apron_tradwife tur 1 görsel SHOULD ile değişti.)
Düzenlemeler (el kitabı §10):
  - Sarıkız: saç altın sarısına (efsanede adı sarı saçından gelir), gri başörtüsü al yazmaya, ruj doğal pembeye.
  - Baba sakin: kaynak olduğu gibi (yalnız kontur sabitleme + sağa 60 px saydam pay, iki dosya aynı boyda kalsın).
  - Baba ters köşe varyantı baba_sok: kaşlar, gözler, kaş arası kırışıklar ve ağız silinir; iri yuvarlak göz + küçük göz
    bebeği (dosyanın baktığı yöne, sağa), iç ucu kalkık kalın kaş, "O" ağız, alında 5 mavi çizgi, başın önünde 3 damla.
Bakış yönü dosyanın kendisine göre kaydedilir (python -m wojak yon ...); episode.yaml'da faces: yok.
Çizim yardımcıları balikli-ayazma-1453/chars/uret.py'den kopyalandı.
"""
from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as nd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
KAYNAK = HERE / "kaynak"
sys.path.insert(0, str(ROOT / "tools"))
import kit_varyant  # noqa: E402

SS = 4
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)
MAVI = (60, 120, 230, 255)
PAY = 60   # sağa saydam pay (damlalar kontur dışında kalsın)


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


def kontur_sabitle(im):
    a = np.array(im).astype(np.int32)
    m = (a[..., :3].sum(-1) < 240) & (a[..., 3] > 30)
    a[m, 3] = 255
    return Image.fromarray(a.astype(np.uint8))


def kaydet(im, ad):
    out = HERE / f"{ad}.png"
    im.save(out, optimize=True)
    print(f"-> {out.relative_to(ROOT)}  {im.width}x{im.height}")


def baba_taban():
    im = kontur_sabitle(Image.open(KAYNAK / "baba_kaynak.png").convert("RGBA"))
    t = Image.new("RGBA", (im.width + PAY, im.height), (0, 0, 0, 0))
    t.paste(im, (0, 0))
    return t


def baba_sok(im):
    a = np.array(im).copy()
    dark = (a[..., 3] > 128) & (a[..., :3].astype(int).sum(-1) < 200)
    lab, _ = nd.label(dark)
    # silinecek bileşenler: kaşlar, kaş arası kırışıklar, gözler, ağız (kaynakta ölçülen kutular)
    kutular = [(351, 452, 468, 474), (565, 452, 654, 480), (468, 479, 487, 504), (572, 485, 578, 517),
               (369, 517, 473, 563), (581, 526, 659, 576), (445, 751, 594, 780)]
    for i, sl in enumerate(nd.find_objects(lab), 1):
        if sl is None:
            continue
        b = (sl[1].start, sl[0].start, sl[1].stop, sl[0].stop)
        if b in kutular:
            m = nd.binary_dilation(lab == i, iterations=3) & (a[..., 3] > 0)
            a[m] = WHITE
    im = Image.fromarray(a)
    c = Cizim(im, seed=7)
    c.elips(418, 548, 46, 44, dolgu=WHITE, w=9)
    c.elips(620, 556, 38, 41, dolgu=WHITE, w=9)
    c.elips(436, 552, 9, 9, dolgu=BLACK)
    c.elips(636, 560, 8, 8, dolgu=BLACK)
    c.cizgi([(364, 500), (402, 490), (440, 476), (472, 458)], 13)     # sol kaş, iç ucu kalkık
    c.cizgi([(566, 462), (596, 480), (628, 492), (660, 500)], 13)     # sağ kaş
    c.elips(520, 778, 30, 38, dolgu=(48, 12, 16, 255), w=9)           # "O" ağız
    c.elips(520, 800, 17, 10, dolgu=(205, 95, 105, 255))               # dil
    for pts in ([(394, 446), (414, 438), (434, 442)], [(452, 434), (472, 428), (494, 433)],
                [(512, 438), (532, 431), (552, 436)], [(572, 432), (592, 427), (612, 433)],
                [(620, 446), (636, 440), (652, 445)]):
        c.cizgi(pts, 4.5, renk=MAVI)
    return ter(c.im, [(762, 470, 15), (776, 550, 14), (764, 630, 13)])


def kiz():
    """Tur 1 görsel SHOULD: yumuşak/boyalı önlüklü kız yerine düz çizgili, başörtülü, basma elbiseli hazır kız
    (wl:eastern_europe_headscarf_tradwife_wojak.png, 627x865). Başörtüsünün altındaki koyu kahve saç altın sarısına,
    gri başörtüsü al yazmaya, koyu kırmızı ruj doğal pembeye çevrilir (bağlı bölge, gölge oranı korunur)."""
    im = kontur_sabitle(Image.open(KAYNAK / "kiz_basortulu_kaynak.png").convert("RGBA"))
    a = np.array(im).astype(np.float64)
    r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    lum = (r + g + b) / 3
    yy = np.arange(a.shape[0])[:, None] * np.ones((1, a.shape[1]))

    def bolge(m, en_az):
        lab, n = nd.label(m)
        if n == 0:
            return m
        boy = nd.sum(m, lab, range(1, n + 1))
        return np.isin(lab, 1 + np.nonzero(boy > en_az)[0])

    sac = bolge((al > 0) & (yy < 230) & (r - b > 10) & (r > 22) & (r < 130) & (g < 110) & (b < 90), 300)
    m = lum[sac].mean()
    a[sac, :3] = np.clip(np.array([226, 182, 72]) * np.clip(lum[sac] / m, 0.7, 1.2)[:, None], 0, 255)
    ruj = (al > 0) & (r > 35) & (r > 2.5 * g) & (r > 2.5 * b) & (yy > 330) & (yy < 440)
    a[ruj, :3] = np.clip(np.array([196, 104, 104]) * np.clip(lum[ruj] / max(lum[ruj].mean(), 1), 0.7, 1.2)[:, None], 0, 255)
    aday = (al > 0) & (np.abs(r - g) < 14) & (np.abs(g - b) < 14) & (lum > 38) & (lum < 215)
    lab, _ = nd.label(aday)
    tohum = [(300, 150), (120, 330), (400, 720), (301, 8), (352, 12), (328, 18), (368, 470), (420, 493)]  # başörtüsü, iç bandı, uçları, düğüm (x, y)
    ids = {lab[y, x] for x, y in tohum} - {0}
    gri = np.isin(lab, list(ids))
    a[gri, :3] = np.clip(np.array([172, 42, 44]) * np.clip(lum[gri] / 117, 0.6, 1.3)[:, None], 0, 255)
    return Image.fromarray(a.astype(np.uint8))


if __name__ == "__main__":
    t = baba_taban()
    kaydet(t.copy(), "baba_sakin")
    kaydet(baba_sok(t.copy()), "baba_sok")
    kaydet(kiz(), "kiz_sakin")
