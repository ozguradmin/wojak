"""kanuni-gizlenen-olum: hazır kıyafetli iki karakter ve ters köşe yüz varyantı.

    python episodes/kanuni-gizlenen-olum/chars/uret.py

Kaynaklar (kaynak/ altında, indirildiği gibi; şeffaf kenarı kırpılmış):
  yeniceri_kaynak.png  wojakland "Janissary Ottoman Feels Good Wojak"
                       (https://wojakland.com/gmedia/janissary_ottoman_feels_good_wojak-png/), 521x676, sola bakar
  vezir_kaynak.png     wojakland "Sultan Chad" (https://wojakland.com/gmedia/sultan_chad-png/), 842x1036, sola bakar
Kıyafete, ellere, börke, kavuğa dokunulmaz. Yapılanlar yalnız:
  - yeniçeri "mutlu" = kaynağın kendisi (gözleri kapalı, sevinçli; müjde vermeye hazır); kesimde yarı saydam kalan
    profil konturu opak yapılır (kontur_sabitle);
  - yeniçeri "sok": kapalı göz yayları, kaşlar ve gülen ağız ten rengiyle silinip AYNI çizgi kalınlığında yeniden
    çizilir (kalkık kaşlar, iri açık gözler, küçük göz bebekleri, açık "O" ağız) + alında kısa mavi soğuk ter
    çizgileri + ter damlaları (tools/kit_varyant.py). Eller yanaklarda kalır: sevinç pozu dehşet pozuna döner.
  - vezir: kaynağın kendisi (sakin, ciddi). Kötü/sırıtan yüz yok.
Bakış yönü bu betikte kaydedilmez (data/ dışına yazılmaz): episode.yaml'da her karakterin `faces:` alanı var.
Çizim yardımcıları karun-hazinesi-bros/chars/uret.py'den (o da talidomit hazir_uret.py'den) kopyalandı.
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
TEN = (255, 212, 161)


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

    def cizgi(self, pts, w, renk=BLACK, titrek=0.4):
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


def soguk_ter(im, cizgiler, w=4.5, seed=5):
    """Alında kısa, düzensiz, ucu kancalı mavi el çizgileri (C2kk 4,0 sn / C4V3 12,5 sn dili)."""
    W, H = im.size
    lay = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    blue = (110, 175, 230, 255)
    rng = np.random.default_rng(seed)
    for x, y0, length, amp, waves, hook in cizgiler:
        ts = np.linspace(0, 1, 12)
        pts = [(x + amp * np.sin(np.pi * waves * t) + rng.normal(0, 0.25), y0 + length * t) for t in ts]
        if hook:
            pts.append((pts[-1][0] + hook[0], pts[-1][1] + hook[1]))
        p = [(px * SS, py * SS) for px, py in pts]
        d.line(p, fill=blue, width=round(w * SS), joint="curve")
        r = w * SS / 2
        for px, py in (p[0], p[-1]):
            d.ellipse([px - r, py - r, px + r, py + r], fill=blue)
    im = im.copy()
    im.alpha_composite(lay.resize((W, H), Image.LANCZOS))
    return im


def kontur_sabitle(im):
    """Kesimde yarı saydam kalmış siyah kontur piksellerini (koyu RGB, alfa > 30) tam opak yapar: profil çizgisi koyu
    zeminde kaybolmasın. Renkli/açık piksellere dokunmaz."""
    a = np.array(im).astype(np.int32)
    m = (a[..., :3].sum(-1) < 240) & (a[..., 3] > 30)
    a[m, 3] = 255
    return Image.fromarray(a.astype(np.uint8))


def kaydet(im, ad):
    out = HERE / f"{ad}.png"
    im.save(out, optimize=True)
    print(f"-> {out.relative_to(ROOT)}  {im.width}x{im.height}")


def yeniceri():
    """Feels Good janissary (521x676), 3/4 sola bakar. Yüz hatları (px): sol kaş (250-282, 228-242), sağ kaş
    (303-368, 222-243); kapalı göz yayları (248-275, 250-266) ve (310-350, 250-266); bıyık (240-340, 288-308);
    gülen ağız (255-318, 308-338); eller y>330'dan. Çıktılar 521x580 (alt kesim). Börk kenarı y~205. Çizgi: kaş ~8 px, göz ~5 px, kontur ~4-5 px."""
    base = kontur_sabitle(Image.open(KAYNAK / "yeniceri_kaynak.png").convert("RGBA"))
    # alt kenar y=580'de kesilir (bilekler; büst zaten kadrajın altından kesik): aynı height'ta yüz ~%17 büyür
    base = base.crop((0, 0, base.width, 580))
    kaydet(base, "yeniceri_mutlu")
    im = base.copy()
    for p in (kutu(254, 220, 286, 246), kutu(300, 216, 370, 247), kutu(254, 247, 278, 268), kutu(306, 247, 352, 268),
              [(254, 309), (318, 309), (320, 324), (312, 340), (262, 340), (252, 324)]):
        im = sil(im, p)
    c = Cizim(im, seed=9)
    # endişe/dehşet kaşları: iç uçlar (burna yakın) yukarıda, dış uçlar aşağıda
    c.cizgi([(249, 229), (262, 225), (275, 219), (285, 213)], 7)
    c.cizgi([(304, 213), (318, 215), (338, 220), (356, 226), (368, 231)], 7)
    # iri açık gözler: beyaz dolgu + kontur; küçük göz bebekleri bakış yönünde (sola, karşıdaki vezire)
    for cx, cy, rx, ry, px, pr in ((264, 256, 14, 13, 258, 3.4), (331, 256, 19, 15, 324, 3.8)):
        c.elips(cx, cy, rx, ry, dolgu=WHITE, w=4.5)
        c.elips(px, cy + 1, pr, pr, dolgu=BLACK)
    # açık "O" ağız, bıyığın hemen altında
    c.elips(286, 326, 14, 14, dolgu=(45, 30, 30, 255), w=4.5)
    im = soguk_ter(c.im, [(262, 203, 10, 1.4, 1.0, (-3, 3)), (291, 202, 13, -1.6, 1.2, (3, 3)),
                          (318, 199, 9, 1.2, 1.0, None), (347, 201, 12, -1.4, 1.3, (3, 2))])
    im = ter(im, [(241, 262, 9), (392, 236, 8), (398, 290, 8)])
    kaydet(im, "yeniceri_sok")


def vezir():
    base = Image.open(KAYNAK / "vezir_kaynak.png").convert("RGBA")
    kaydet(base, "vezir_sakin")


if __name__ == "__main__":
    yeniceri()
    vezir()
