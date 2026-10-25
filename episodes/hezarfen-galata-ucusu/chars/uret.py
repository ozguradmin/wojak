"""hezarfen-galata-ucusu: hazır kıyafetli iki karakter ve ters köşe yüz varyantı.

    python episodes/hezarfen-galata-ucusu/chars/uret.py

Kaynaklar (kaynak/ altında, indirildiği gibi; şeffaf kenarı kırpılmış, en çok 1400 px):
  hezarfen_kaynak.png  wojakland "Panjabi Muslim Chad" (Panjabi_Muslim_chad.png,
                       https://wojakland.com/wp-content/grand-media/image/original/Panjabi_Muslim_chad.png), 1024x1400,
                       beyaz sarık, siyah sakal, beyaz gömlek + yelek; profilden sağa bakar
  murad_kaynak.png     wojakland "Sultan Wojak" (sultan_wojak_3.png,
                       https://wojakland.com/wp-content/grand-media/image/original/sultan_wojak_3.png), 1518x1400,
                       klasik beyaz wojak yüzü, sorguçlu kavuk, kürklü kaftan, kır sakal; gözler sola bakar
Kıyafete ve başlıklara dokunulmaz. Yapılanlar:
  - hezarfen_emin = kaynağın kendisi (kontur opak), göğüsten kesik. A solda, sağa bakar.
  - hezarfen_sok: aynı kutu; kaş yukarıda ve iç ucu kalkık, göz iri (beyaz görünür, küçük bebek), ağız açık,
    alında mavi soğuk ter çizgileri + başın önünde ter damlaları.
  - murad_sakin: IV. Murad tahta 11 yaşında çıktı, 27 yaşında öldü; 1630'larda genç bir adam. Kır sakal koyu
    kahveye boyanır; dişlerini sıkan ağız (kanalda "kötü/öfkeli" okunur) silinip düz, ciddi bir ağız çizilir.
    Kötü ya da sırıtan yüz yok. B sağda, sola bakar.
Bakış yönü bu betikte kaydedilmez: episode.yaml'da her karakterin `faces:` alanı var.
Çizim yardımcıları kasikci-elmasi/chars/uret.py'den kopyalandı.
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
TEN_H = (210, 169, 147)        # Hezarfen'in ten rengi (kaynaktan ölçüldü)
SAKAL_M = (177, 173, 147)      # Sultan Wojak kır sakal (kaynaktan ölçüldü)
SAKAL_KOYU = (62, 48, 40)


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


def hezarfen_temel():
    """Panjabi Muslim Chad 1024x1400. Ölçülen hatlar (px): kaş 735-937 x 617-685 (kalın, düz-çatık), göz 775-880 x
    657-725 (kahve iris 822-870, bebek ~857,695), göz altı çizgisi 795-860 x 735-748, yanak çizgisi 907-937 x 695-765,
    dudak 870-930 x 945-978, alın-burun konturu x ~950-975 (y 470-640). Çizgi ~12 px. Sağa 70 px boşluk açılır
    (ter damlaları başın önüne, kontur dışına)."""
    im = kontur_sabitle(Image.open(KAYNAK / "hezarfen_kaynak.png").convert("RGBA"))
    pad = Image.new("RGBA", (im.width + 70, im.height), (0, 0, 0, 0))
    pad.paste(im, (0, 0))
    return pad


def hezarfen_sok(im):
    # kaş + göz + göz altı çizgisi silinir (yanak çizgisi ve kontur korunur)
    im = sil(im, [(728, 612), (944, 600), (944, 640), (900, 690), (900, 752), (790, 755), (728, 700)], TEN_H, tol=-1)
    c = Cizim(im, seed=11)
    # iri göz: beyaz badem, üstte ve altta beyaz görünür, küçük bebek (telefonda okunsun diye büyük)
    c.elips(836, 696, 62, 46, dolgu=WHITE, w=12)
    c.elips(862, 697, 16, 16, dolgu=(70, 42, 20, 255))
    c.elips(863, 697, 8, 8, dolgu=BLACK)
    # kaş: yukarıda, iç ucu (burun tarafı) kalkık -> endişe/korku
    c.cizgi([(748, 632), (798, 600), (858, 582), (922, 556)], 19)
    # alın kırışıkları
    c.cizgi([(800, 540), (846, 530), (894, 524)], 7)
    # açık ağız (sakalın içinde, dudağın yerinde): pembe dudak + koyu iç
    c.elips(898, 972, 44, 38, dolgu=(205, 125, 120, 255), w=11)
    c.elips(898, 976, 30, 25, dolgu=(45, 12, 12, 255))
    # alında mavi soğuk ter çizgileri (düzensiz, hafif S, kancalı)
    MAVI = (60, 120, 230, 255)
    for x, y0, L, s in [(766, 472, 56, 1), (800, 462, 64, -1), (836, 458, 62, 1), (872, 462, 54, -1), (906, 474, 42, 1)]:
        c.cizgi([(x, y0), (x + 5 * s, y0 + L * 0.35), (x - 3 * s, y0 + L * 0.7), (x + 2 * s, y0 + L)], 11, renk=MAVI, titrek=0.6)
    return ter(c.im, [(1030, 496, 44), (1058, 604, 36), (1018, 652, 26)])


def murad_temel():
    """Sultan Wojak 1518x1400. Ölçülen hatlar (px): dişleri sıkan ağız (beyaz alan + konturu) 580-800 x 955-1050,
    bıyık üst çizgisi y ~925-965, sakal düz rengi (177,173,147). Çizgi ~8 px."""
    im = kontur_sabitle(Image.open(KAYNAK / "murad_kaynak.png").convert("RGBA"))
    # ağız: beyaz diş alanı ve iç çizgileri sakal rengine boyanır
    im = sil(im, [(578, 975), (600, 958), (650, 948), (700, 950), (760, 965), (800, 990), (800, 1052), (578, 1052)],
             SAKAL_M, tol=-1)
    c = Cizim(im, seed=5)
    # düz, ciddi ağız (uçları hafif aşağı)
    c.cizgi([(612, 1012), (650, 1002), (700, 1000), (748, 1010)], 9)
    im = c.im
    # kır sakal -> koyu kahve (yalnız sakal rengindeki pikseller; kontur siyah kalır)
    # yalnız sakalın bağlı bölgesi (kaftan kürkü benzer renkte; taşmasın): tohum (700,1050), komşu 4'lü taşma
    from scipy import ndimage
    a = np.array(im).astype(np.int32)
    d = np.abs(a[..., :3] - np.array(SAKAL_M)).sum(-1)
    aday = (d < 30) & (a[..., 3] > 0)
    lab, _ = ndimage.label(aday)
    m = lab == lab[1050, 700]
    m = ndimage.binary_dilation(m, iterations=2) & (d < 60)   # kenar yumuşatma pikselleri
    a[m, :3] = SAKAL_KOYU
    im = Image.fromarray(a.astype(np.uint8))
    # bıyık altında kalan diş ucu kırıntısı (beyaz üçgen + iki kısa çizgi)
    return sil(im, kutu(668, 945, 700, 966), SAKAL_KOYU, tol=-1)


if __name__ == "__main__":
    h = hezarfen_temel()
    s = hezarfen_sok(h.copy())
    # büst: göğüsten kes (y 1260), aynı height'ta yüz büyür
    kaydet(h.crop((0, 0, h.width, 1260)), "hezarfen_emin")
    kaydet(s.crop((0, 0, s.width, 1260)), "hezarfen_sok")
    m = murad_temel()
    kaydet(m.crop((0, 0, m.width, 1235)), "murad_sakin")
