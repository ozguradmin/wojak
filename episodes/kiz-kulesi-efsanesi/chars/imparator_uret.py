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
5. imparator_bizans_sepet.png (final tur 4; görsel hakem: kanca "bak sana üzüm getirdim" ekranda görünsün,
   C2VH'nin ölü balığı gibi): iç alt köşede, alt kenardan kesilen düz MS-Paint hasır sepet + mor üzüm yığını.
   Sepet x ~489-767, ağız y ~744 (elips), gövde alt kenarın altına iner; dolgu (176,118,52), 6 px siyah kontur,
   koyu (120,78,30) dalgalı örgü + dikey çubuklar. Üzüm: 19 tane, r 17-19, (112,38,128), 4 px kontur, sol üstte
   küçük açık parlama; tepede sap + yeşil yaprak. Tuval, ölçek, baş üstü ve yazı yeri aynı kalır (alfa kutusu
   değişmez). Bakış kaydı bilerek elle yapılır (bak, sonra: python -m wojak yon <png> --yon sag).
6. imparator_bizans_baba.png (final tur 5; takipçi hakemi: ağır göz kapaklı yan bakış + kalkık kaş + yarım
   gülümseme kanalın yüz dilinde "sinsi" okunuyordu, oysa efsanedeki baba seven ve trajik): sepet + sevecen
   yüz. Kalkık dış kaş ve eski gözler silinir; düz, hafif kavisli iki kaş; açık, yuvarlak gözler (gözbebeği
   sağ kenarda: prensese bakar, küçük beyaz parıltı kaynağın sağ gözündeki gibi); ağız açık, gururlu gülüş
   (üstte beyaz diş şeridi, koyu kırmızı ağız içi, pembe dil; tek tek diş çizgisi yok, "creepy grin" olmasın).
   Tuval, alfa kutusu, baş üstü ve yazı yeri değişmez. Bakış kaydı yine elle (bak, sonra --yon sag).
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


# --- üzüm sepeti (final tur 4) ----------------------------------------------------------------------------
HASIR = (176, 118, 52, 255)
HASIR_KOYU = (120, 78, 30, 255)
YAPRAK = (70, 140, 50, 255)
SAP = (96, 70, 30, 255)
UZUM = (112, 38, 128, 255)
PARLAK = (235, 220, 245, 255)
SEPET_K = 1.1                     # genel ölçek
SEPET_CX, SEPET_AGIZ_Y = 628, 744  # sepet merkezi x, ağız elipsinin merkezi y
SEPET_RX, SEPET_RY = 126 * SEPET_K, 22 * SEPET_K
SEPET_ALT = SEPET_AGIZ_Y + 150 * SEPET_K   # gövde tuvalin altına (862) iner: kadraj kenarında kesilir


def sepet(im: Image.Image) -> Image.Image:
    W, H = im.size
    K, CX, Y, RX, RY = SEPET_K, SEPET_CX, SEPET_AGIZ_Y, SEPET_RX, SEPET_RY

    def S(v):
        return v * SS

    def ell(d, x, y, r, **kw):
        d.ellipse([S(x - r), S(y - r), S(x + r), S(y + r)], **kw)

    lay = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    rng = np.random.default_rng(18)
    # ağzın üstünde kubbe gibi üzüm yığını: alttan üste sıralar (y, adet, x kayması)
    rows = [(Y - 2 * K, 7, 0.0), (Y - 26 * K, 6, 8.0 * K), (Y - 50 * K, 4, 2.0 * K), (Y - 72 * K, 2, 10.0 * K)]
    grapes = []
    for y, n, off in rows:
        span = 2 * (RX - 26 * K) * ((n - 1) / 6)
        for x in np.linspace(CX - span / 2, CX + span / 2, n) + off - 4:
            grapes.append((x + rng.uniform(-3, 3), y + rng.uniform(-2, 2), rng.uniform(15.5, 17.5) * K))
    top = min(g[1] for g in grapes)
    sx, sy = CX + 10 * K, top - 14 * K               # sap + yaprak
    d.line([(S(sx - 4), S(sy + 14)), (S(sx), S(sy - 2)), (S(sx + 10), S(sy - 12))], fill=SAP, width=S(7),
           joint="curve")
    leaf = [(sx + a * K, sy + b * K) for a, b in ((6, -6), (30, -34), (66, -34), (58, -10), (30, 2))]
    d.polygon([(S(x), S(y)) for x, y in leaf], fill=YAPRAK, outline=INK, width=S(4))
    d.line([(S(sx + 14 * K), S(sy - 6 * K)), (S(sx + 52 * K), S(sy - 26 * K))], fill=INK, width=S(3))
    for x, y, r in sorted(grapes, key=lambda g: g[1]):
        ell(d, x, y, r, fill=UZUM, outline=INK, width=S(4))
        ell(d, x - r * 0.38, y - r * 0.38, r * 0.24, fill=PARLAK)
    # gövde: ağız elipsinden aşağı yarım elips, örgü gövdeye kırpılır
    body = [(CX - RX * np.cos(t), Y + (SEPET_ALT - Y) * np.sin(t)) for t in np.linspace(0, np.pi, 60)]
    bm = Image.new("L", lay.size, 0)
    ImageDraw.Draw(bm).polygon([(S(x), S(y)) for x, y in body], fill=255)
    blay = Image.new("RGBA", lay.size, (0, 0, 0, 0))
    bd = ImageDraw.Draw(blay)
    bd.polygon([(S(x), S(y)) for x, y in body], fill=HASIR)
    for k in range(1, 6):
        yy = Y + (6 + k * 22) * K
        bd.line([(S(x), S(yy + 5 * np.sin((x - CX) / 12))) for x in np.linspace(CX - RX, CX + RX, 60)],
                fill=HASIR_KOYU, width=S(4), joint="curve")
    for x in np.arange(CX - RX + 18 * K, CX + RX, 30 * K):
        bd.line([(S(x), S(Y + 10)), (S(x + 4), S(SEPET_ALT))], fill=HASIR_KOYU, width=S(4))
    blay.putalpha(Image.fromarray(np.minimum(np.array(blay.getchannel("A")), np.array(bm))))
    lay.alpha_composite(blay)
    d = ImageDraw.Draw(lay)
    d.line([(S(x), S(y)) for x, y in body], fill=INK, width=S(6), joint="curve")
    # ön ağız bandı (ağız elipsinin alt yarısı, üzümlerin önünde)
    rim = Image.new("L", lay.size, 0)
    ImageDraw.Draw(rim).chord([S(CX - RX), S(Y - RY), S(CX + RX), S(Y + RY)], 0, 180, fill=255)
    rimlay = Image.new("RGBA", lay.size, (0, 0, 0, 0))
    rd = ImageDraw.Draw(rimlay)
    rd.ellipse([S(CX - RX), S(Y - RY), S(CX + RX), S(Y + RY)], fill=HASIR, outline=INK, width=S(6))
    rd.ellipse([S(CX - RX + 13), S(Y - RY + 9), S(CX + RX - 13), S(Y + RY - 9)], fill=(0, 0, 0, 0), outline=INK,
               width=S(4))
    rimlay.putalpha(Image.fromarray(np.minimum(np.array(rimlay.getchannel("A")), np.array(rim))))
    lay.alpha_composite(rimlay)
    out = im.copy()
    out.alpha_composite(lay.resize((W, H), Image.LANCZOS))
    return out


# --- sevecen baba yüzü (final tur 5) ------------------------------------------------------------------------
BEYAZ = (255, 255, 255, 255)
AGIZ_IC = (120, 28, 34, 255)
DIL = (226, 112, 124, 255)
# beyaza boyanan eski yüz çizgileri: sol göz, sol iç kaş, sağ göz, kalkık sağ kaş, eski gülümseme çizgisi
YUZ_SIL = [(262, 362, 368, 420), (350, 330, 380, 366), (452, 372, 536, 432), (440, 316, 534, 346),
           (334, 576, 480, 611)]
# göz: (sol köşe, üst kapak kontrol, sağ köşe, alt kapak kontrol, gözbebeği merkezi, gözbebeği yarıçapı)
GOZLER = [((276, 395), (313, 356), (352, 390), (314, 428), (333, 392), 14.5),
          ((466, 403), (495, 368), (525, 399), (497, 432), (511, 400), 12.0)]
KASLAR = [((274, 353), (312, 334), (352, 347)), ((464, 360), (494, 344), (526, 356))]
AGIZ_SOL, AGIZ_SAG = (334, 581), (480, 579)
AGIZ_UST_K, AGIZ_ALT_K = (407, 601), (407, 650)          # üst dudak / alt dudak kontrol noktaları
DIS_ALT = ((330, 578), (407, 618), (484, 576))            # diş şeridinin alt çizgisi
DIL_KUTU = (377, 606, 437, 626)


def _maske_ile(lay: Image.Image, poly) -> Image.Image:
    m = Image.new("L", lay.size, 0)
    ImageDraw.Draw(m).polygon(_ss(poly), fill=255)
    lay.putalpha(Image.fromarray(np.minimum(np.array(lay.getchannel("A")), np.array(m))))
    return lay


def sevecen_yuz(im: Image.Image) -> Image.Image:
    a = np.array(im)
    for x0, y0, x1, y1 in YUZ_SIL:
        sub = a[y0:y1, x0:x1]
        sub[(sub[..., 3] > 0) & (sub[..., :3].min(-1) < 235)] = BEYAZ
    out = Image.fromarray(a)
    W, H = out.size
    lay = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for sol, ust, sag, alt, (cx, cy), r in GOZLER:
        up, lo = _bez(sol, ust, sag, 60), _bez(sol, alt, sag, 60)
        goz = up + lo[::-1]
        d.polygon(_ss(goz), fill=BEYAZ)
        pl = Image.new("RGBA", lay.size, (0, 0, 0, 0))
        pd = ImageDraw.Draw(pl)
        pd.ellipse([(cx - r) * SS, (cy - r) * SS, (cx + r) * SS, (cy + r) * SS], fill=INK)
        hr, hx, hy = r * 0.33, cx - r * 0.35, cy - r * 0.38
        pd.ellipse([(hx - hr) * SS, (hy - hr) * SS, (hx + hr) * SS, (hy + hr) * SS], fill=BEYAZ)
        lay.alpha_composite(_maske_ile(pl, goz))
        d = ImageDraw.Draw(lay)
        _stroke(d, _ss(up), 6.5 * SS, INK)
        _stroke(d, _ss(lo), 4.5 * SS, INK)
    for p0, p1, p2 in KASLAR:
        _stroke(d, _ss(_bez(p0, p1, p2, 60)), 6 * SS, INK)
    ust, alt = _bez(AGIZ_SOL, AGIZ_UST_K, AGIZ_SAG, 60), _bez(AGIZ_SOL, AGIZ_ALT_K, AGIZ_SAG, 60)
    agiz = ust + alt[::-1]
    ml = Image.new("RGBA", lay.size, (0, 0, 0, 0))
    md = ImageDraw.Draw(ml)
    md.polygon(_ss(agiz), fill=AGIZ_IC)
    md.ellipse([v * SS for v in DIL_KUTU], fill=DIL)
    dis = _bez(*DIS_ALT, 60)
    md.polygon(_ss(ust + dis[::-1]), fill=BEYAZ)
    md.line(_ss(dis), fill=INK, width=3 * SS)
    lay.alpha_composite(_maske_ile(ml, agiz))
    _stroke(ImageDraw.Draw(lay), _ss(agiz + [agiz[0]]), 5.5 * SS, INK)
    out.alpha_composite(lay.resize((W, H), Image.LANCZOS))
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
    k = sepet(s)
    k.save(HERE / "imparator_bizans_sepet.png", optimize=True)
    print("->", (HERE / "imparator_bizans_sepet.png").relative_to(ROOT), k.size,
          "(bak, sonra: python -m wojak yon <png> --yon sag)")
    b = sevecen_yuz(k)
    b.save(HERE / "imparator_bizans_baba.png", optimize=True)
    print("->", (HERE / "imparator_bizans_baba.png").relative_to(ROOT), b.size,
          "(bak, sonra: python -m wojak yon <png> --yon sag)")


if __name__ == "__main__":
    main()
