"""1915 İngiliz eri: klasik feels guy + Wolseley mantar miğfer + haki drill ceket (düz MS-Paint stili).

    python assets/kit/ingiliz_er_1915/kostum.py <taban.png> <çıktı.png> [--biyik]

Taban klasik koordinatındadır (899x1022, sağa bakar; assets/kit/klasik/sakin.png ile aynı kafa).
v3 (2026-10-10): miğfer HELM_DY kadar yukarı alınıp HELM_SCALE ile biraz küçültüldü, böylece klasik alın
kırışıkları (taban y 200-300) ve ters köşe yüzündeki mavi soğuk ter çizgileri siperliğin altında görünür.
Görsel CROP_Y'de (taban koordinatı) yaka hizasından kesilir: yüz, aynı `height` ile daha büyük görünür.
--biyik: A karakteri için düz siyah MS-Paint bıyık (A ile B bir bakışta ayrılsın).
Bütün varyantlar aynı kostüm yerleşimini ve aynı tuvali kullanır: kutu sahneler arasında aynı kalır.
"""
import math, random, sys
from PIL import Image, ImageDraw

SS = 3
LW = 9            # klasik çizgi kalınlığı (~8-10 px)
BLACK = (0, 0, 0, 255)
HELM = (176, 150, 104, 255)
HELM_BAND = (150, 126, 86, 255)
JACKET = (196, 174, 130, 255)
BRASS = (214, 176, 70, 255)
PAD_SIDE_R, PAD_SIDE_L = 70, 60

HELM_DY = -150            # miğfer kaç px yukarı (taban koordinatı)
HELM_SCALE = 0.86         # miğfer ölçeği (siperlik alt-orta noktası çevresinde)
HELM_PIVOT = (500, 334)   # siperliğin alt orta noktası (orijinal çizimde)
HELM_TOP = -158           # orijinal çizimde miğferin en üst noktası (tepe topuzu)
CROP_Y = 985              # taban y: görsel buradan kesilir (yaka + ceketin üst şeridi kalır)
PAD_TOP = int(-((HELM_TOP - HELM_PIVOT[1]) * HELM_SCALE + HELM_PIVOT[1] + HELM_DY)) + 12


def catmull(pts, n=24, closed=False):
    P = list(pts)
    if closed:
        P = [P[-1]] + P + [P[0], P[1]]
    else:
        P = [P[0]] + P + [P[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i-1], P[i], P[i+1], P[i+2]
        for k in range(n):
            t = k / n
            t2, t3 = t*t, t*t*t
            x = 0.5*((2*p1[0]) + (-p0[0]+p2[0])*t + (2*p0[0]-5*p1[0]+4*p2[0]-p3[0])*t2 + (-p0[0]+3*p1[0]-3*p2[0]+p3[0])*t3)
            y = 0.5*((2*p1[1]) + (-p0[1]+p2[1])*t + (2*p0[1]-5*p1[1]+4*p2[1]-p3[1])*t2 + (-p0[1]+3*p1[1]-3*p2[1]+p3[1])*t3)
            out.append((x, y))
    if not closed:
        out.append(P[-2])
    return out


def wob(pts, amp=1.2, seed=1):
    r = random.Random(seed)
    o = []
    ph = r.random()*6
    for i, (x, y) in enumerate(pts):
        o.append((x + amp*math.sin(i*0.37+ph) + r.uniform(-0.4, 0.4), y + amp*math.cos(i*0.29+ph) + r.uniform(-0.4, 0.4)))
    return o


def S_(pts, dx, dy):
    return [((x+dx)*SS, (y+dy)*SS) for x, y in pts]


def H_(pts):
    """Miğfer noktaları: pivot çevresinde ölçek + yukarı kaydırma."""
    px, py = HELM_PIVOT
    return [(px + (x - px) * HELM_SCALE, py + (y - py) * HELM_SCALE + HELM_DY) for x, y in pts]


def stroke(d, pts, w=LW, closed=False):
    pts = pts + pts[:1] if closed else pts
    d.line(pts, fill=BLACK, width=round(w*SS), joint="curve")
    r = w*SS/2
    for x, y in (pts[0], pts[-1]):
        d.ellipse([x-r, y-r, x+r, y+r], fill=BLACK)


def mustache(d, dx, dy):
    """Düz siyah gür pala bıyık (v5: ~340x60 px, eskisinin 1,4 katı; C2fa A'daki gibi uçları aşağı sarkıp yukarı kıvrılır).

    Burnun altında, yüz sağa baktığı için orta nokta hafif sağda; uzak (sağ) kanat kısaltılmış. Tek parça düz siyah
    dolgu: kanat omurgası boyunca incelen dairelerle damgalanır (kontur boşluğu yok).
    """
    cx, cy = 662, 664
    # kanat omurgaları (merkezden uca): yakın (sol) kanat uzun, uzak (sağ) kanat kısa; uçlar yukarı-içe kıvrılır
    wings = [
        [(cx, cy), (620, 665), (575, 671), (535, 683), (503, 693), (481, 688), (471, 672), (476, 656), (488, 650)],
        [(cx, cy), (700, 664), (738, 669), (771, 679), (797, 686), (813, 678), (817, 662), (809, 652)],
    ]
    for k, sp in enumerate(wings):
        pts = catmull(sp, 14)
        n = len(pts)
        for i, (x, y) in enumerate(pts):
            t = i / (n - 1)
            r = 5.0 + 25.0 * (1 - t) ** 1.1         # merkezde ~30 px yarıçap, uçta ~5
            yy = y + 4 * (1 - t) ** 2               # merkez gövdesi biraz aşağı dolgun
            X, Y = (x + dx) * SS, (yy + dy) * SS
            R = r * SS
            d.ellipse([X - R, Y - R * 0.92, X + R, Y + R * 0.92], fill=BLACK)


def build(base_path, out_path, extra=None, biyik=False):
    base = Image.open(base_path).convert("RGBA")
    W, H = base.width + PAD_SIDE_L + PAD_SIDE_R, base.height + PAD_TOP
    dx, dy = PAD_SIDE_L, PAD_TOP
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    canvas.alpha_composite(base, (dx, dy))
    L = Image.new("RGBA", (W*SS, H*SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)

    if biyik:
        mustache(d, dx, dy)

    # ---------- CEKET (haki drill, kapalı dik yaka) ----------
    T = [(212, 836), (262, 834), (345, 858), (450, 880), (553, 893)]          # sol yaka üst kenarı
    T2 = [(570, 893), (640, 893), (672, 884), (704, 890)]                        # sağ yaka üst kenarı
    Bm_l = [(548, 960), (450, 948), (340, 922), (250, 893), (196, 878)]           # sol yaka alt kenarı
    Bm_r = [(722, 935), (660, 952), (576, 960)]                                  # sağ yaka alt kenarı
    body = ([(-40, 955), (40, 918), (120, 885), (212, 836)] + T + [(561, 902)] + T2 +
            [(800, 915), (880, 940), (940, 962), (940, 1060), (-40, 1060)])
    d.polygon(S_(body, dx, dy), fill=JACKET)
    # omuz çizgileri
    stroke(d, S_(wob(catmull([(-40, 956), (40, 919), (120, 886), (196, 856), (214, 840)], 14), 1.0, 2), dx, dy))
    stroke(d, S_(wob(catmull([(704, 890), (800, 916), (880, 941), (940, 963)], 14), 1.0, 3), dx, dy))
    # yaka kanatları
    flap_l = catmull(T, 10) + catmull([(553, 893), (549, 925), (548, 960)], 6)[1:] + catmull(Bm_l, 10)[1:]
    flap_r = catmull(T2, 10) + catmull([(704, 890), (716, 912), (722, 935)], 6)[1:] + catmull(Bm_r, 10)[1:] + [(572, 925)]
    d.polygon(S_(flap_l, dx, dy), fill=JACKET)
    d.polygon(S_(flap_r, dx, dy), fill=JACKET)
    stroke(d, S_(wob(flap_l, 0.8, 4), dx, dy))
    stroke(d, S_(wob(flap_r, 0.8, 5), dx, dy))
    # pat (önden düğme hattı)
    stroke(d, S_(wob(catmull([(562, 962), (564, 1010), (566, 1060)], 8), 0.6, 7), dx, dy), w=7)
    # omuz apoleti
    ep = [(752, 925), (880, 957), (872, 985), (744, 953)]
    d.polygon(S_(ep, dx, dy), fill=JACKET)
    stroke(d, S_(wob(catmull(ep, 8, closed=True), 0.6, 8), dx, dy), w=7, closed=True)
    r = 8*SS; X, Y = (764+dx)*SS, (943+dy)*SS
    d.ellipse([X-r, Y-r, X+r, Y+r], fill=BRASS, outline=BLACK, width=4*SS)

    # ---------- MIĞFER (Wolseley) ----------
    brim_bot = [(958, 298), (880, 298), (700, 314), (500, 334), (300, 345), (150, 356), (48, 374)]
    # v4: siperliğin üst kenarı dolguyla birebir aynı eğriden çizilir (konturu olmayan ten rengi şerit kalmasın)
    brim_l_edge = [(48, 374), (85, 335), (130, 292), (170, 262)]
    brim_r_edge = [(830, 228), (900, 254), (958, 298)]
    brim = (catmull(brim_bot, 16)[:-1] + catmull(brim_l_edge, 10)
            + [(300, 262), (500, 262), (700, 250)] + catmull(brim_r_edge, 10)[:-1])
    d.polygon(S_(H_(brim), dx, dy), fill=HELM)
    stroke(d, S_(wob(H_(catmull(brim_bot, 16)), 1.0, 9), dx, dy))
    stroke(d, S_(H_(catmull(brim_l_edge, 10)), dx, dy))
    stroke(d, S_(H_(catmull(brim_r_edge, 10)), dx, dy))
    dome = [(165, 268), (160, 150), (195, 40), (270, -50), (380, -108), (500, -126), (620, -108),
            (725, -50), (800, 40), (830, 140), (836, 232)]
    dome_bottom = [(836, 232), (700, 268), (500, 290), (300, 290), (165, 268)]
    dpoly = catmull(dome, 16)[:-1] + catmull(dome_bottom, 16)[:-1]
    d.polygon(S_(H_(dpoly), dx, dy), fill=HELM)
    stroke(d, S_(wob(H_(catmull(dome, 16)), 1.0, 10), dx, dy))
    band_top = [(161, 195), (320, 222), (500, 226), (680, 205), (833, 165)]
    bpoly = catmull(band_top, 14) + catmull(dome_bottom, 14)
    d.polygon(S_(H_(bpoly), dx, dy), fill=HELM_BAND)
    stroke(d, S_(wob(H_(catmull(band_top, 14)), 0.8, 11), dx, dy), w=8)
    stroke(d, S_(wob(H_(catmull(dome_bottom, 14)), 0.8, 12), dx, dy))
    stroke(d, S_(wob(H_(catmull([(200, 236), (350, 256), (520, 259), (690, 236), (805, 206)], 12)), 0.6, 13), dx, dy), w=5)
    # dilim dikişleri
    stroke(d, S_(wob(H_(catmull([(470, -122), (430, -30), (410, 90), (405, 218)], 12)), 0.6, 14), dx, dy), w=6)
    stroke(d, S_(wob(H_(catmull([(565, -120), (640, -30), (685, 80), (698, 200)], 12)), 0.6, 15), dx, dy), w=6)
    stroke(d, S_(wob(H_(catmull([(330, -85), (255, 10), (222, 110), (212, 204)], 12)), 0.6, 16), dx, dy), w=6)
    # tepe topuzu
    knob = [(458, -122), (470, -150), (512, -158), (546, -147), (556, -120)]
    d.polygon(S_(H_(catmull(knob, 10)), dx, dy), fill=HELM)
    stroke(d, S_(wob(H_(catmull(knob, 10)), 0.5, 17), dx, dy), w=7)
    if extra:
        extra(d, dx, dy)

    L = L.resize((W, H), Image.LANCZOS)
    canvas.alpha_composite(L)
    canvas = canvas.crop((0, 0, W, CROP_Y + dy))
    canvas.save(out_path, optimize=True)
    return canvas


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    build(args[0], args[1], biyik="--biyik" in sys.argv)
    print(args[1])
