#!/usr/bin/env python3
"""İmparator (A, solda) karakterini kaynaktan yeniden üretir.

    python episodes/kiz-kulesi-efsanesi/chars/imparator_uret.py

Kaynak: wojakland 'byzantine emperor wojak' (wl:Theocrat3_1.png, https://wojakland.com/gmedia/theocrat3_1-png/),
`python tools/wojak_site.py get wl:Theocrat3_1.png --name imparator_bizans --out-dir episodes/kiz-kulesi-efsanesi/chars`
ile indirilen imparator_bizans.png.
1. imparator_bizans_gulumser.png: aşağı kıvrık ağız çizgisi silinir, hafif gülümseme çizilir.
2. imparator_bizans_sade.png: + taç sadeleştirilir (hakem: renkli arabesk bant yüzü bastırıyordu): düz sarı
   kamelaukion (koyu altın), siyah kontur, kenar bandı; iki dikiş yerine inci dizisi (siyah çizgili dikişler
   tacı inşaat baretine benzetiyordu), bandın ortasında da inci dizisi + 3 taş, kubbede 1 taş ve tepede haç.
   Taştan taşan küçük süsler silinir. Yüz, saç, sakal ve bakış aynı kalır (sağa bakar).
   İnciler elle çizilmiş gibi: merkezler ±3 px oynar, yarıçap 6-8 px (sabit tohum; hakem: vektör gibi düzgündü).
3. Omuzlar (hakem: yüzün altında yalnız yaka + ~15 px mor vardı; orijinallerde boyun/omuz figürün %25-35'i):
   tuval 586x742 -> 586x862 uzatılır, mor cüppe aşağı devam eder. İçerideki (sağ) omuz yuvarlak bir eğriyle alt
   kenara iner (dikey kesik yok); dış (sol) kenar kadraj kenarında kesilir. Ortada yakadan aşağı altın loros
   şeridi, üstünde kırmızı + mavi taş.
4. Geniş büst (final tur 3; hakem: büst ~400 px / %37 idi, C2P/C2VH/C3dO büstleri 560-600 px / %52-55):
   tuval 586x862 -> 780x862 (yükseklik aynı: ölçek, baş üstü ve yazı yeri değişmez). İç (sağ) omuz
   (430,723) -> (560,738) -> (660,765) -> (735,810) üzerinden alt kenara (~775) iner; aynı mor + 20 px kontur.
   Loros yerinde kalır (x 262-318).
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent
sys.path.insert(0, str(ROOT))
from wojak import facing  # noqa: E402

SRC = HERE / "imparator_bizans.png"
SS = 4
INK = (0, 1, 1, 255)
YELLOW = (236, 172, 32, 255)   # koyu altın (açık sarı baret gibi okunuyordu)
PEARL = (250, 250, 245, 255)
RED = (214, 30, 40, 255)
BLUE = (36, 86, 200, 255)

# tacın alt sınırı (yüz/saç başlangıcı), soldan sağa
TAC_ALT = [(0, 324), (40, 322), (120, 316), (200, 316), (300, 316), (400, 311), (500, 304), (586, 298)]
KENAR_UST = [(40, 271), (200, 272), (350, 268), (450, 262), (575, 254)]   # kenar bandının üst çizgisi
DIKISLER = [[(232, 18), (218, 140), (210, 270)], [(392, 22), (404, 140), (414, 266)]]  # ham koordinat (_bas uygulanır)
TASLAR = [((135, 294), RED, 15), ((300, 294), BLUE, 16), ((462, 285), RED, 15), ((310, 200), BLUE, 19)]
CIZGI = 6
# kubbe silueti (düzgün eğri; eski taşan süslerin basamaklı kenarı yerine)
KUBBE_HAM = [(40, 322), (42, 230), (62, 140), (112, 66), (190, 24), (300, 10), (410, 22), (488, 64), (536, 138),
             (556, 220), (562, 298)]
BASIK = 0.68   # kubbe yüksekliği bu oranda basıklaştırılır (taç yüzü bastırmasın)
INCI_R = 7            # inci yarıçapı (beyaz, 3 px siyah kontur); çizimde 6-8 arası oynar
INCI_OYNA = 3         # inci merkezi ±px (elle çizilmiş görünüm)
RNG = np.random.default_rng(1453)
INCI_ARALIK_DIKIS = 32
INCI_ARALIK_BANT = 34
HAC_DIKEY = (292, 308)            # haç: dikey kol x aralığı, y = HAC_UST .. kubbe tepesi
HAC_UST = 50
HAC_YATAY = (276, 324)            # yatay kol x aralığı
HAC_YATAY_Y = (64, 78)
HAC_CIZGI = 5


def _bas(p, taban=320.0):
    return (p[0], taban - (taban - p[1]) * BASIK)


KUBBE = [_bas(p) for p in KUBBE_HAM]


def _curve(pts, n=20):
    pts = [np.array(p, float) for p in pts]
    pts = [pts[0]] + pts + [pts[-1]]
    out = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        for t in np.linspace(0, 1, n, endpoint=False):
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(pts[-2])
    return [tuple(map(float, p)) for p in out]


def _alt_kenar(n=60):
    """TAC_ALT'ın kubbe genişliğindeki kısmı (soldan sağa)."""
    tx, ty = zip(*TAC_ALT)
    xs = np.linspace(KUBBE[0][0], KUBBE[-1][0], n)
    return list(zip(xs, np.interp(xs, tx, ty)))


def _ss(pts):
    return [(x * SS, y * SS) for x, y in pts]


def _stroke(d, pts, width, fill):
    r = width / 2
    step = max(1.0, r / 3)
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        n = max(1, int(np.hypot(x1 - x0, y1 - y0) / step))
        for t in np.linspace(0, 1, n + 1):
            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            d.ellipse([x - r, y - r, x + r, y + r], fill=fill)


def _bez(p0, p1, p2, n=40):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in np.linspace(0, 1, n + 1)]


def _esit_aralik(pts, aralik):
    """Eğri üzerinde eşit yay uzunluğu aralıklı noktalar (iki uçtan yarım aralık içeride)."""
    p = np.array(pts, float)
    seg = np.hypot(*np.diff(p, axis=0).T)
    s = np.concatenate([[0], np.cumsum(seg)])
    n = max(1, int(s[-1] // aralik))
    pay = (s[-1] - (n - 1) * aralik) / 2 if n > 1 else s[-1] / 2
    hedef = [pay + i * aralik for i in range(n)]
    return [(float(np.interp(t, s, p[:, 0])), float(np.interp(t, s, p[:, 1]))) for t in hedef]


def _bant_orta(n=200):
    """Kenar bandının orta çizgisi: KENAR_UST ile TAC_ALT arası."""
    kx, ky = zip(*KENAR_UST)
    tx, ty = zip(*TAC_ALT)
    xs = np.linspace(KUBBE[0][0] + 30, KUBBE[-1][0] - 30, n)
    return list(zip(xs, (np.interp(xs, kx, ky) + np.interp(xs, tx, ty)) / 2))


def _inci(d, x, y):
    x += float(RNG.uniform(-INCI_OYNA, INCI_OYNA))
    y += float(RNG.uniform(-INCI_OYNA, INCI_OYNA))
    r = float(RNG.uniform(INCI_R - 1, INCI_R + 1))
    d.ellipse([(x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS], fill=PEARL, outline=INK, width=3 * SS)


def gulumse(im: Image.Image) -> Image.Image:
    im = im.copy()
    px = im.load()
    for y in range(584, 613):
        for x in range(333, 476):
            r, g, b, a = px[x, y]
            if a > 0 and r < 140 and g < 140 and b < 140:
                px[x, y] = (255, 255, 255, 255)
    lay = Image.new("RGBA", (im.width * SS, im.height * SS), (0, 0, 0, 0))
    _stroke(ImageDraw.Draw(lay), _ss(_bez((343, 589), (405, 618), (470, 588))), 6.5 * SS, INK)
    return Image.alpha_composite(im, lay.resize(im.size, Image.LANCZOS))


def sade_tac(im: Image.Image) -> Image.Image:
    W, H = im.size
    a = np.array(im)
    alt = Image.new("L", (W, H), 0)
    ImageDraw.Draw(alt).polygon([(0, 0), (W, 0)] + TAC_ALT[::-1], fill=255)
    ust = np.array(alt) > 127
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon(_curve(KUBBE) + _alt_kenar()[::-1], fill=255)
    m = Image.fromarray(np.minimum(np.array(m), np.array(alt)))
    crown2 = np.array(m) > 127
    # tacın eski piksellerini temizle
    a[ust & ~crown2, 3] = 0
    for x0, y0, x1, y1 in ((0, 296, KUBBE[0][0] - 2, 334), (KUBBE[-1][0] + 2, 280, W, 312)):  # eski kenar çizgisi uçları
        sub = a[y0:y1, x0:x1]
        sub[sub[..., :3].max(-1) < 90, 3] = 0
    out = Image.fromarray(a)
    # yeni taç: süper örneklenmiş katman
    mbig = Image.new("L", (W * SS, H * SS), 0)
    ImageDraw.Draw(mbig).polygon(_ss(_curve(KUBBE) + _alt_kenar()[::-1]), fill=255)
    mbig = Image.fromarray(np.minimum(np.array(mbig), np.array(alt.resize(mbig.size))))
    lay = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    fill = Image.new("RGBA", lay.size, YELLOW)
    lay = Image.composite(fill, lay, mbig)
    d = ImageDraw.Draw(lay)
    _stroke(d, _ss(KENAR_UST), CIZGI * SS, INK)
    for seam in DIKISLER:                          # dikiş çizgisi yerine aynı eğri boyunca inci dizisi
        for x, y in _esit_aralik(_bez(*[_bas(q) for q in seam], n=400), INCI_ARALIK_DIKIS):
            _inci(d, x, y)
    taslar_bant = [(x, y, r) for (x, y), _, r in TASLAR if y > 250]
    for x, y in _esit_aralik(_bant_orta(), INCI_ARALIK_BANT):   # bandın ortasında inci dizisi (taşların arası)
        if all(np.hypot(x - tx, y - ty) > tr + INCI_R + 6 for tx, ty, tr in taslar_bant):
            _inci(d, x, y)
    for (x, y), col, r in TASLAR:
        d.ellipse([(x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS], fill=col, outline=INK, width=3 * SS)
    # dış kontur: maskenin iç kenarı
    edge = np.array(mbig.filter(ImageFilter.MinFilter(2 * CIZGI * SS // 2 * 2 + 1)))
    ring = (np.array(mbig) > 127) & ~(edge > 127)
    la = np.array(lay)
    la[ring] = INK
    lay = Image.fromarray(la)
    # çizimleri taç maskesine kırp
    lay.putalpha(Image.fromarray(np.minimum(np.array(lay.getchannel("A")), np.array(mbig))))
    out.alpha_composite(lay.resize((W, H), Image.LANCZOS))
    # alt kenar çizgisi (yüz/saç ile taç arası)
    lay2 = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    tx, ty = zip(*TAC_ALT)
    xs = np.linspace(KUBBE[0][0] + 3, KUBBE[-1][0] - 3, 60)
    pts = list(zip(xs, np.interp(xs, tx, ty)))
    _stroke(ImageDraw.Draw(lay2), _ss(pts), CIZGI * SS, INK)
    out.alpha_composite(lay2.resize((W, H), Image.LANCZOS))
    # kubbenin tepesinde haç (koyu altın, siyah kontur; iki kolun birleşimi tek kontur)
    lay3 = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d3 = ImageDraw.Draw(lay3)
    tepe = KUBBE[len(KUBBE) // 2][1] + 6        # kubbe konturunun içine biraz girsin
    kollar = [(HAC_DIKEY[0], HAC_UST, HAC_DIKEY[1], tepe), (HAC_YATAY[0], HAC_YATAY_Y[0], HAC_YATAY[1], HAC_YATAY_Y[1])]
    for x0, y0, x1, y1 in kollar:
        d3.rectangle([(x0 - HAC_CIZGI) * SS, (y0 - HAC_CIZGI) * SS, (x1 + HAC_CIZGI) * SS, (y1 + HAC_CIZGI) * SS], fill=INK)
    for x0, y0, x1, y1 in kollar:
        d3.rectangle([x0 * SS, y0 * SS, x1 * SS, (y1 if y1 < tepe else tepe - HAC_CIZGI) * SS], fill=YELLOW)
    out.alpha_composite(lay3.resize((W, H), Image.LANCZOS))
    return out


# --- omuzlar (uzatılmış tuval) ---------------------------------------------------------------------------
YENI_H = 862
YENI_W = 780                       # final tur 3: geniş büst (586 -> 780)
MOR = (163, 73, 164, 255)          # kaynaktaki cüppe moru
ALTIN_YAKA = (200, 162, 6, 255)    # kaynaktaki yaka altını
# içteki (sağ) omuz konturu: eski omuz çizgisinin devamı, yuvarlak inip alt kenara ulaşır
SAG_OMUZ = [(430, 723), (500, 729), (560, 738), (615, 750), (660, 765), (702, 785), (735, 810), (757, 836),
            (771, 862), (777, 882)]
# dıştaki (sol) omuz: kaynağın kendi konturu kalır; dolgu onun hemen altından başlar (y kaynakta 701-742)
SOL_OMUZ_ALT = [(92, 702), (80, 712), (70, 720), (50, 733), (30, 740), (10, 743), (-10, 745)]
LOROS_X = (262, 318)               # yakadan aşağı inen altın şerit
LOROS_UST = 716
LOROS_TAS = [(768, RED, 12), (812, BLUE, 12)]
GRI_LEKE = (76, 668, 93, 687)      # yakanın solundaki küçük gri karalama


def _dilate_np(m: np.ndarray, r: int) -> np.ndarray:
    return np.array(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(2 * r + 1))) > 127


def omuz(im: Image.Image) -> Image.Image:
    W, H = im.size
    a = np.array(im)
    # küçük gri karalama
    x0, y0, x1, y1 = GRI_LEKE
    sub = a[y0:y1, x0:x1]
    sub[sub[..., :3].max(-1) > 10, 3] = 0
    # yeni siluet: solda tuval kenarı (kadrajda kesilir), altta alt kenar, sağda SAG_OMUZ eğrisi
    sag = _curve(SAG_OMUZ, n=24)
    sil = SOL_OMUZ_ALT + [(-10, YENI_H + 10)] + [(sag[-1][0], YENI_H + 10)] + sag[::-1] + [(430, 700)]
    W2 = YENI_W
    m = Image.new("L", (W2, YENI_H), 0)
    ImageDraw.Draw(m).polygon(sil, fill=255)
    ic = np.array(m) > 127
    # eski cüppenin yeni siluetin dışında kalan kısmı (sağ omuzun düz ucu) silinir; sakal/saç y<715'te kalır
    big = np.zeros((YENI_H, W2, 4), np.uint8)
    big[:H, :W] = a
    yy, xx = np.mgrid[0:YENI_H, 0:W2]
    big[(~ic) & (yy >= 715) & (xx >= 430), 3] = 0
    eski = Image.fromarray(big)
    # alt katman: mor dolgu + sağ omuz konturu
    lay = Image.new("RGBA", (W2 * SS, YENI_H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.polygon(_ss(sil), fill=MOR)
    _stroke(d, _ss(sag), CIZGI * SS, INK)
    out = lay.resize((W2, YENI_H), Image.LANCZOS)
    out.alpha_composite(eski)
    # eski kaynağın omuz kenarındaki açık renkli kenar pikselleri yeni konturun altında kalsın: omzun üst
    # kısmı (x <= 640) kontur bir kez daha üstten çizilir
    ust = Image.new("RGBA", (W2 * SS, YENI_H * SS), (0, 0, 0, 0))
    _stroke(ImageDraw.Draw(ust), _ss([q for q in sag if q[0] <= 640]), CIZGI * SS, INK)
    out.alpha_composite(ust.resize((W2, YENI_H), Image.LANCZOS))
    W = W2
    # loros: yakanın altından alt kenara altın şerit (siyah yan konturlar), iki taş
    lay2 = Image.new("RGBA", (W * SS, YENI_H * SS), (0, 0, 0, 0))
    d2 = ImageDraw.Draw(lay2)
    lx0, lx1 = LOROS_X
    d2.rectangle([lx0 * SS, LOROS_UST * SS, lx1 * SS, (YENI_H + 5) * SS], fill=ALTIN_YAKA)
    for x in (lx0, lx1):
        _stroke(d2, _ss([(x, LOROS_UST), (x, YENI_H + 5)]), CIZGI * SS, INK)
    cx = (lx0 + lx1) / 2
    for y, col, r in LOROS_TAS:
        d2.ellipse([(cx - r) * SS, (y - r) * SS, (cx + r) * SS, (y + r) * SS], fill=col, outline=INK, width=3 * SS)
    lor = lay2.resize((W, YENI_H), Image.LANCZOS)
    # şerit yakanın altında başlasın: yaka (altın + konturu) üstte kalır
    yaka = np.array(eski).copy()
    ea = yaka.astype(np.int32)
    altin = (np.abs(ea[..., 0] - 200) < 30) & (np.abs(ea[..., 1] - 162) < 30) & (ea[..., 2] < 60)
    koyu = ea[..., :3].max(-1) < 90
    yaka_m = _dilate_np(altin, 1) | (koyu & _dilate_np(altin, CIZGI + 2))
    yaka[~yaka_m | (yy > 740) | (yy < 640), 3] = 0
    out.alpha_composite(lor)
    out.alpha_composite(Image.fromarray(yaka))
    return out


def main() -> None:
    base = Image.open(SRC).convert("RGBA")
    g = gulumse(base)
    g.save(HERE / "imparator_bizans_gulumser.png", optimize=True)
    facing.register(HERE / "imparator_bizans_gulumser.png", "right")
    s = omuz(sade_tac(g))
    s.save(HERE / "imparator_bizans_sade.png", optimize=True)
    facing.register(HERE / "imparator_bizans_sade.png", "right")
    print("->", (HERE / "imparator_bizans_sade.png").relative_to(ROOT), s.size)


if __name__ == "__main__":
    main()
