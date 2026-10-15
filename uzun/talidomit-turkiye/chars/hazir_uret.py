"""talidomit-turkiye uzun video: HAZIR kıyafetli karakterler ve temiz yüz varyantları (7. tur, 13.10.2026).

    python uzun/talidomit-turkiye/chars/hazir_uret.py              # hepsi
    python uzun/talidomit-turkiye/chars/hazir_uret.py anlatici lenz  # yalnız bazıları
    python uzun/talidomit-turkiye/chars/hazir_uret.py --kayitsiz     # bakış kaydı (data/karakter_yon.json) yazma

Neden: hesap sahibi (13.10) "kendi çizdiğimiz kıyafetler kötü" dedi (wojak başı + elle boyanmış tişört/önlük, kayık
yaka, boyunda dikiş izi). Bu betik `uret.py`'nin kafa + çizilmiş gövde karakterlerinin YERİNE, kıyafeti hazır gelen
tek parça çizimleri (wojakland, HF clayshoaf/Wojaks = wojakparadise arşivi) kullanır. Kıyafete, gövdeye, saç
çizgisine dokunulmaz; yalnız:
  - yüz içi (kaş, göz, ağız) silinip AYNI çizgi kalınlığında, kenarı sert (MS-Paint gibi, kenar yumuşatmasız)
    yeniden çizilir; ter damlası ve gözyaşı kanalın kit diliyle (tools/kit_varyant.py) eklenir;
  - gerekirse düz renk değişimi (saç rengi, allık silme, göz altı morluğu silme): çizim aynı kalır.
Kaynak PNG'ler kaynak/ altında, adresleri KARAKTER_HARITASI.md'de. Bir karakterin bütün varyantları aynı tuvalde
(motor ortak kırpım uygular: yüz değişiminde kutu zıplamaz). Hepsi 3/4 profilde sağa bakar (gözle bakıldı).

Çıktılar `<rol>_v2_<duygu>.png` (eski `uret.py` dosyaları yapımcı geçene kadar durur):
  anlatici_v2_*     anlatıcı/izleyici "feels guy": wojakland Flannel Wojak (kırmızı-siyah ekose gömlek)
  kaymakcalan_v2_*  K: HF 5_Doomer/13708 "Depressed Office Worker" (kalın siyah gözlük, takım, yeşil gömlek);
                    göz altı morlukları silinip klasik gözler çizildi, saç koyu kahve -> siyah
  lenz_v2_*         L: wojakland English Wojak (kıvırcık koyu saç, koyu palto, ekose kravat)
  voss_v2_*         V: wojakland Blushing Suit Wojak; allık silindi, saç koyu kahve -> kumral
  sheskin_v2_*      S: wojakland Turtleneck Grey Hair Wojak (kır saç, siyah çerçeve gözlük, balıkçı yaka + blazer)
  eczaci_v2_sakin   E: wojakland Suit Wojak (kır saç, bıyık, bordo ceket, papyon); değiştirilmedi
  musteri_v2_sakin  B1.8 eczane müşterisi: wojakland Tired Blonde Wojak (uykusuz yüz); değiştirilmedi
  kelsey_v2_*       F: eski kaynak (HF 5_Daddys_Girl/11087) aynı renk değişimiyle; yüz varyantları temiz yeniden
  veteriner_v2_sakin  Aygün: kısa videonun kaynağı (wojakland Grandpa Wojak); kısa videodaki yüz düzeltmeleri
                    (gözlük, bıyık, saç) aynen, ama boyanmış önlük YOK: hazır süveter yelek + gömlek
"""
from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
KAYNAK = HERE / "kaynak"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import kit_varyant  # noqa: E402  (ter damlası / gözyaşı: kanalın kit dili)

SS = 4                          # çizim süper örnekleme (sonra eşiklenir: kenar sert kalır)
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)
PAD_TOP = 16                    # tuvalin üstüne saydam pay (nefes/ölçek animasyonunda tepe kesilmesin)
KAYIT = True
SADECE: set = set()             # boşsa bütün yüzler (anlatici için `--yuz mutlu`)


# ------------------------------------------------------------------------------------------------ yardımcılar
def yukle(ad: str) -> Image.Image:
    return Image.open(KAYNAK / ad).convert("RGBA")


def tuval(im: Image.Image, ust=PAD_TOP) -> Image.Image:
    out = Image.new("RGBA", (im.width, im.height + ust), (0, 0, 0, 0))
    out.alpha_composite(im, (0, ust))
    return out


def poly_mask(size, pts) -> np.ndarray:
    W, H = size
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon([tuple(p) for p in pts], fill=255)
    return np.array(m) > 0


def dil(m, r):
    return np.array(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(2 * r + 1))) > 0


def sil(im: Image.Image, pts, renk=(255, 255, 255), tol=10, oy=0) -> Image.Image:
    """Çokgen içindeki, `renk`ten (cilt) farklı bütün pikselleri (çizgi, allık, morluk) cilt rengine boyar.
    pts kaynak koordinatında; oy: tuvale eklenen üst pay."""
    a = np.array(im).astype(np.int32)
    m = poly_mask(im.size, [(x, y + oy) for x, y in pts])
    d = np.abs(a[..., :3] - np.array(renk)).sum(-1)
    m &= (d > tol) & (a[..., 3] > 0)
    a[m, :3] = renk
    return Image.fromarray(a.astype(np.uint8))


def sil_notr(im: Image.Image, pts, renk=(255, 255, 255), tol=10, oy=0, doy=30) -> Image.Image:
    """`sil` gibi, ama yalnız renksiz (siyah/gri çizgi, doygunluk < doy) pikseller: çokgen saça taşsa da saç rengi
    kalır (9. tur: Kelsey'nin sağ göz kapağı silinirken saçta beyaz yama açılıyordu)."""
    a = np.array(im).astype(np.int32)
    m = poly_mask(im.size, [(x, y + oy) for x, y in pts])
    d = np.abs(a[..., :3] - np.array(renk)).sum(-1)
    sat = a[..., :3].max(-1) - a[..., :3].min(-1)
    m &= (d > tol) & (a[..., 3] > 0) & (sat < doy)
    a[m, :3] = renk
    return Image.fromarray(a.astype(np.uint8))


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
    """Kenarı keskin çizim katmanı (süper örnekle çiz, küçült, geçişi ~1 px'e daralt): kaynak çizimlerin MS-Paint
    çizgisine uyar.
    İşlemler sırayla basılır (ör. önce beyaz göz dolgusu, sonra siyah kontur)."""

    def __init__(self, im: Image.Image, oy=0, seed=1):
        self.im, self.oy = im, oy
        self.rng = random.Random(seed)

    def _maske(self):
        W, H = self.im.size
        m = Image.new("L", (W * SS, H * SS), 0)
        return m, ImageDraw.Draw(m)

    def _bas(self, m, renk):
        W, H = self.im.size
        # kaynak çizgileri ~1 px kenar yumuşatmalı: geniş LANCZOS geçişini 1 px'e daralt
        m = m.resize((W, H), Image.LANCZOS).point(lambda v: max(0, min(255, (v - 64) * 2)))
        lay = Image.new("RGBA", (W, H), renk)
        self.im.paste(lay, (0, 0), m)

    def P(self, pts):
        return [(x * SS, (y + self.oy) * SS) for x, y in pts]

    def cizgi(self, pts, w, renk=BLACK, yumusak=True, titrek=0.5):
        p = catmull(pts) if yumusak and len(pts) > 2 else list(pts)
        if titrek:
            ph = self.rng.random() * 6
            p = [(x + titrek * math.sin(i * 0.41 + ph), y + titrek * math.cos(i * 0.33 + ph)) for i, (x, y) in enumerate(p)]
        m, d = self._maske()
        q = self.P(p)
        d.line(q, fill=255, width=round(w * SS), joint="curve")
        r = w * SS / 2
        for x, y in (q[0], q[-1]):
            d.ellipse([x - r, y - r, x + r, y + r], fill=255)
        self._bas(m, renk)
        return self

    def elips(self, cx, cy, rx, ry, dolgu=None, w=0, renk=BLACK):
        b = [(cx - rx) * SS, (cy - ry + self.oy) * SS, (cx + rx) * SS, (cy + ry + self.oy) * SS]
        if dolgu is not None:
            m, d = self._maske()
            d.ellipse(b, fill=255)
            self._bas(m, dolgu)
        if w:
            m, d = self._maske()
            d.ellipse(b, outline=255, width=round(w * SS))
            self._bas(m, renk)
        return self

    def cokgen(self, pts, dolgu):
        m, d = self._maske()
        d.polygon(self.P(pts), fill=255)
        self._bas(m, dolgu)
        return self


def ter(im: Image.Image, damlalar, oy=0) -> Image.Image:
    """Ter damlaları (kit dili): [(x, y, yarıçap)] kaynak koordinatında."""
    spec = {"drops": [[x, y + oy, s] for x, y, s in damlalar]}
    return _kit(im, spec)


def gozyasi(im: Image.Image, yollar, w=12, oy=0) -> Image.Image:
    spec = {"tears": [{"path": [[x, y + oy] for x, y in p], "w": w} for p in yollar]}
    return _kit(im, spec)


def _kit(im, spec):
    tmp = HERE / "__kit_tmp.png"
    im.save(tmp)
    try:
        kit_varyant.make(tmp, spec, tmp)
        return Image.open(tmp).convert("RGBA").copy()
    finally:
        tmp.unlink(missing_ok=True)


def renk_degistir(im: Image.Image, bolge_pts, eslesme, oy=0, tol=40) -> Image.Image:
    """Düz renk değişimi (saç vb.): bölgede kaynak renge yakın pikseller hedef renge; aradaki kenar tonları
    parlaklık oranıyla. eslesme: [((r,g,b) kaynak, (r,g,b) hedef), ...]"""
    a = np.array(im).astype(np.int32)
    zone = poly_mask(im.size, [(x, y + oy) for x, y in bolge_pts]) & (a[..., 3] > 0)
    rgb = a[..., :3].copy()
    for c0, c1 in eslesme:
        d = np.abs(rgb - np.array(c0)).sum(-1)
        m = zone & (d < tol)
        a[m, :3] = c1
    return Image.fromarray(a.astype(np.uint8))


def kalin_siyah(im: Image.Image, r=7) -> np.ndarray:
    """Kalın siyah yapılar (gözlük çerçevesi, kontur): ince çizgiler (<= 2r px) morfolojik açmayla düşer."""
    a = np.array(im)
    blk = ((a[..., :3].max(-1) < 60) & (a[..., 3] > 128)).astype(np.uint8) * 255
    m = Image.fromarray(blk).filter(ImageFilter.MinFilter(2 * r + 1)).filter(ImageFilter.MaxFilter(2 * r + 1))
    # açma köşeleri ve kenar yumuşatma piksellerini yer: 2 px büyüt, yalnız koyu piksellerle kesiştir
    m = np.array(m.filter(ImageFilter.MaxFilter(5))) > 0
    return m & (a[..., :3].max(-1) < 200) & (a[..., 3] > 0)


def sil_koru(im: Image.Image, pts, koru: np.ndarray, renk=(255, 255, 255), tol=10, oy=0) -> Image.Image:
    """`sil` gibi, ama `koru` maskesindeki pikseller (ör. gözlük çerçevesi) olduğu gibi kalır."""
    a = np.array(im).astype(np.int32)
    m = poly_mask(im.size, [(x, y + oy) for x, y in pts])
    d = np.abs(a[..., :3] - np.array(renk)).sum(-1)
    m &= (d > tol) & (a[..., 3] > 0) & ~koru
    a[m, :3] = renk
    return Image.fromarray(a.astype(np.uint8))


def cam_ici(im: Image.Image, cx, cy, R, minrun=12, n=180):
    """Gözlük camının iç kenarı (çokgen, tuval koordinatı): merkezden R uzaktan içeri yürünür; ilk kalın (>= minrun)
    siyah koşunun bittiği yer çerçevenin iç kenarıdır. Sıçramalar komşu ortancasıyla düzeltilir."""
    a = np.array(im).astype(np.int32)
    H, W = a.shape[:2]
    black = (a[..., :3].max(-1) < 30) & (a[..., 3] > 200)
    rad = []
    for k in range(n):
        th = 2 * math.pi * k / n
        run, edge = 0, np.nan
        for r in np.arange(R, 0, -1):
            x, y = int(round(cx + r * math.cos(th))), int(round(cy + r * math.sin(th)))
            if not (0 <= x < W and 0 <= y < H):
                run = 0
                continue
            if black[y, x]:
                run += 1
            else:
                if run >= minrun:
                    edge = r
                    break
                run = 0
        rad.append(edge)
    rad = np.array(rad, float)
    for _ in range(3):
        med = np.array([np.nanmedian(np.take(rad, range(i - 6, i + 7), mode="wrap")) for i in range(n)])
        bad = np.isnan(rad) | (np.abs(rad - med) > 8)
        rad[bad] = med[bad]
    return [(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n)) for k, r in enumerate(rad)]


def parca_tasi(dst: Image.Image, src: Image.Image, box, merkez, olcek=1.0) -> Image.Image:
    """Hazır bir çizimin koyu çizgilerini (ör. klasik göz) başka bir yüze taşır: kutudaki koyuluk alfa olur, siyah
    basılır (hedefin o bölgesi önceden temizlenmiş olmalı)."""
    c = src.crop(box)
    g = np.array(c.convert("L")).astype(np.float32)
    al = np.array(c.getchannel("A")).astype(np.float32) / 255
    alpha = np.clip((255 - g) * al, 0, 255).astype(np.uint8)
    m = Image.fromarray(alpha)
    if olcek != 1.0:
        m = m.resize((round(m.width * olcek), round(m.height * olcek)), Image.LANCZOS)
    x0, y0 = round(merkez[0] - m.width / 2), round(merkez[1] - m.height / 2)
    lay = Image.new("RGBA", m.size, BLACK)
    lay.putalpha(m)
    out = dst.copy()
    out.alpha_composite(lay, (x0, y0))
    return out


def sac_rengi(im: Image.Image, bolge_pts, ana_kaynak, ana_hedef, oy=0, min_doy=6) -> Image.Image:
    """Saç rengini çizgiye dokunmadan değiştirir: bölgedeki renkli (doygunluğu > min_doy) pikseller, parlaklığın ana
    dolgu tonuna oranıyla hedef tona taşınır (gölge, parlama ve kenar yumuşatma tonları korunur)."""
    a = np.array(im).astype(np.float32)
    zone = poly_mask(im.size, [(x, y + oy) for x, y in bolge_pts]) & (a[..., 3] > 0)
    rgb = a[..., :3]
    sat = rgb.max(-1) - rgb.min(-1)
    m = zone & (sat > min_doy)
    lum0 = np.mean(ana_kaynak)
    t = rgb[m].mean(-1, keepdims=True) / lum0
    a[m, :3] = np.clip(np.array(ana_hedef, np.float32) * t, 0, 255)
    return Image.fromarray(a.astype(np.uint8))


def kaydet(im: Image.Image, ad: str, yon="sag") -> Path:
    out = HERE / f"{ad}.png"
    im.save(out, optimize=True)
    if KAYIT:
        from wojak import facing
        facing.register(out, yon)
    print(f"-> {out.relative_to(ROOT)}  {im.width}x{im.height}  bakış={yon}")
    return out


# ------------------------------------------------------------------------------------------------ anlatıcı
def anlatici():
    """Flannel Wojak (1043x1111). Yüz hatları (kaynak px): sol kaş (487-607, 266-292) + iç kırışık (607-626,
    298-330); sağ kaş (710-802, 268-298) + dikey kırışık (716-720, 303-342); sol göz (503-613, 338-394); sağ göz
    (722-808, 348-407); ağız (583-742, 598-638). Çizgi kalınlığı ~6 px."""
    base = tuval(yukle("anlatici_kaynak_flannel.png"))
    oy = PAD_TOP
    KAS_L = [(478, 252), (640, 252), (640, 336), (478, 336)]
    KAS_R = [(700, 252), (812, 252), (812, 345), (700, 345)]
    GOZ_L = [(494, 334), (622, 334), (622, 402), (494, 402)]
    GOZ_R = [(716, 344), (814, 344), (814, 414), (716, 414)]
    AGIZ = [(574, 590), (752, 590), (752, 645), (574, 645)]
    W = 6

    def yuz(kaslar=None, gozler=None, agiz=None, sil_gozler=False):
        im = base.copy()
        if kaslar is not None:
            im = sil(im, KAS_L, oy=oy)
            im = sil(im, KAS_R, oy=oy)
        if sil_gozler:
            im = sil(im, GOZ_L, oy=oy)
            im = sil(im, GOZ_R, oy=oy)
        if agiz is not None:
            im = sil(im, AGIZ, oy=oy)
        cag = kaslar is not None and any(callable(k) for k in kaslar)
        c = Cizim(im, oy, seed=(97 + len(kaslar)) if cag else len(str(kaslar)))   # 10. tur: lambda'lı kaşta tohum sabit
        for k in (kaslar or []):
            k(c) if callable(k) else c.cizgi(k, W + 1)
        if gozler:
            gozler(c)
        for a in (agiz or []):
            if callable(a):
                a(c)
            else:
                c.cizgi(a, W)
        return c.im

    def yuvarlak_gozler(c, buyuk=1.0):
        # açık göz: kalın üst kapak (kaynağın göz çizgisi gibi), ince alt kapak, büyük göz bebeği (sağa bakar)
        for cx, cy, rx, ry, px, pr in ((560, 367, 46, 32, 580, 15), (767, 379, 36, 28, 783, 13)):
            rx, ry = rx * buyuk, ry * buyuk
            c.elips(cx, cy, rx, ry, dolgu=WHITE, w=W)
            c.cizgi([(cx - rx * 0.97, cy - ry * 0.10), (cx - rx * 0.62, cy - ry * 0.80), (cx, cy - ry * 1.0),
                     (cx + rx * 0.62, cy - ry * 0.80), (cx + rx * 0.97, cy - ry * 0.10)], W + 3, titrek=0.3)
            c.elips(px, cy + 1, pr, pr, dolgu=BLACK)

    endiseli = [[(490, 300), (530, 290), (572, 276), (606, 258)],
                [(712, 262), (745, 272), (778, 286), (802, 302)]]
    out = {}
    out["sakin"] = base
    # 10. tur (animasyon hakemi S3): sakin / düşünceli / ciddi telefonda (baş ~120 px) ayrılmıyordu (fark 2-5 px
    # kaştı). Düşünceli: yakın kaş alçak ve düz, uzak kaş yüksek kemer (iki kaş arası ~45 px), ağız sağa kaymış ve
    # aşağı eğik ("hmm"). Ciddi: kalın V kaşlar (iç uçlar ~30 px aşağı), kaş arası kırışık, uçları aşağı ağız
    # (Kaymakçalan/Kelsey 'kararlı' dili). Aynı çizgi ailesi (6-9 px, kenarı keskin).
    out["dusunceli"] = yuz(
        kaslar=[lambda c: c.cizgi([(490, 318), (530, 320), (572, 322), (612, 328)], W + 2),
                lambda c: c.cizgi([(706, 294), (726, 271), (756, 260), (788, 264), (810, 280)], W + 2)],
        agiz=[[(650, 616), (682, 619), (712, 623), (738, 632)]])          # kısa, sağa kaymış, aşağı eğik
    out["ciddi"] = yuz(
        kaslar=[lambda c: c.cizgi([(490, 300), (530, 306), (574, 316), (614, 333)], W + 3),
                lambda c: c.cizgi([(708, 343), (736, 328), (770, 318), (806, 316)], W + 3),
                lambda c: c.cizgi([(654, 300), (657, 318), (655, 334)], W - 1)],
        agiz=[lambda c: c.cizgi([(588, 637), (608, 621), (640, 613), (680, 612), (716, 618), (740, 635)], W + 1)])
    out["fark"] = yuz(
        kaslar=[[(486, 276), (516, 252), (558, 240), (600, 244), (618, 256)],
                [(706, 264), (734, 248), (770, 245), (806, 262)]],
        gozler=yuvarlak_gozler, sil_gozler=True,
        agiz=[[(604, 618), (650, 620), (708, 617)]])
    out["saskin"] = yuz(
        kaslar=[[(486, 266), (516, 240), (558, 228), (600, 232), (618, 244)],
                [(706, 254), (734, 236), (770, 233), (806, 250)]],
        gozler=lambda c: yuvarlak_gozler(c, 1.08), sil_gozler=True,
        agiz=[lambda c: c.elips(660, 624, 19, 25, dolgu=(45, 30, 30, 255), w=W)])
    terli = yuz(kaslar=endiseli)
    out["terli"] = ter(terli, [(372, 318, 21), (836, 432, 18), (476, 214, 15)], oy=oy)
    gy = yuz(kaslar=endiseli)
    out["gozyasli"] = gozyasi(gy, [[(548, 398), (543, 450), (540, 505), (543, 562)],
                                   [(768, 410), (771, 452), (776, 498)]], w=12, oy=oy)

    def kapali_gozler(c):
        # 7. tur (kapanış çağrısı, abone tıkı): klasik kitin "mutlu" yüzündeki gibi kapalı, yukarı kavisli gözler
        c.cizgi([(506, 380), (530, 364), (560, 357), (592, 362), (614, 376)], W + 2)
        c.cizgi([(724, 388), (748, 374), (778, 369), (808, 380)], W + 2)

    out["mutlu"] = yuz(   # 7. tur: sakin kaşlar yerine gevşek yaylar; kapalı gözler; yumuşak gülümseme (sırıtma değil)
        kaslar=[[(488, 284), (522, 266), (566, 260), (608, 268)],
                [(712, 282), (746, 272), (782, 274), (804, 286)]],
        gozler=kapali_gozler, sil_gozler=True,
        agiz=[lambda c: c.cizgi([(598, 604), (622, 622), (660, 632), (700, 626), (730, 604)], W + 2)])
    for k, im in out.items():
        if SADECE and k not in SADECE:
            continue
        kaydet(im, f"anlatici_v2_{k}")


# ------------------------------------------------------------------------------------------------ Kaymakçalan
def kaymakcalan():
    """HF 5_Doomer/13708 "Depressed Office Worker" (1078x1108): kalın siyah gözlük, takım, yeşil gömlek, kravat.
    Camların içi (yorgun göz + mor göz altı + çizgiler) temizlenir, Flannel Wojak'ın klasik gözleri (aynı çizgi ailesi)
    taşınır: kahraman yorgun/depresif değil, uyanık okunsun. Saç koyu kahve -> siyah (Lenz'in kahve saçından
    ayrılsın). Kaşlar camın üstünde: sol (515-665, 335-372) + iç kırışık (667-690, 372-395), sağ (790-910, 336-375) +
    kırışık (802-807, 380-392); ağız (637-830, 728-762)."""
    base = tuval(yukle("kaymakcalan_kaynak_office_doomer.png"))
    oy = PAD_TOP
    base = sac_rengi(base, [(0, 0), (1078, 0), (1078, 700), (0, 700)], (59, 41, 33), (46, 43, 47), oy=oy)
    goz_kaynak = yukle("anlatici_kaynak_flannel.png")
    camlar = []
    for cx, cy, R in ((598, 480, 160), (872, 478, 140)):
        cam = cam_ici(base, cx, cy + oy, R)
        camlar.append(cam)
        a = np.array(base)
        m = poly_mask(base.size, cam)
        a[m & (a[..., 3] > 0), :3] = 255
        base = Image.fromarray(a)
    base = parca_tasi(base, goz_kaynak, (498, 334, 618, 400), (600, 462 + oy), 1.04)
    base = parca_tasi(base, goz_kaynak, (716, 344, 814, 412), (866, 468 + oy), 1.0)
    koru = kalin_siyah(base, 4)
    KAS_L = [(505, 322), (700, 322), (700, 402), (505, 394)]
    KAS_R = [(782, 322), (918, 322), (918, 384), (782, 410)]
    AGIZ = [(622, 714), (850, 714), (850, 775), (622, 775)]
    W = 7

    def yuz(kaslar=None, agiz=None):
        im = base.copy()
        if kaslar is not None:
            im = sil_koru(im, KAS_L, koru, oy=oy)
            im = sil_koru(im, KAS_R, koru, oy=oy)
        if agiz is not None:
            im = sil(im, AGIZ, oy=oy)
        c = Cizim(im, oy, seed=len(str(kaslar)) + 7)
        for k in (kaslar or []):
            c.cizgi(k, W + 1)
        for a in (agiz or []):
            c.cizgi(a, W)
        return c.im

    def kararli_yuz():
        im = sil_koru(base, KAS_L, koru, oy=oy)
        im = sil_koru(im, KAS_R, koru, oy=oy)
        im = sil(im, AGIZ, oy=oy)
        # üst göz kapakları (cam içinde; göz bebeğinin üstü de silinir: kısık göz)
        im = sil(im, [(556, 422), (668, 422), (668, 462), (556, 450)], oy=oy)
        im = sil(im, [(828, 430), (916, 430), (916, 452), (828, 466)], oy=oy)
        c = Cizim(im, oy, seed=91)
        c.cizgi([(512, 350), (560, 358), (612, 372), (662, 392)], W + 4)
        c.cizgi([(794, 398), (822, 378), (864, 364), (908, 360)], W + 4)
        c.cizgi([(722, 350), (726, 366), (725, 384)], W)
        c.cizgi([(552, 447), (590, 450), (630, 458), (664, 470)], W + 3)
        c.cizgi([(832, 471), (858, 459), (888, 453), (912, 453)], W + 3)
        c.cizgi([(630, 770), (656, 757), (720, 751), (786, 754), (820, 770)], W + 1)
        return c.im

    def dusunceli_yuz():
        """13. tur (animasyon hakemi S4): 11. turdaki düşünceli yüzün gözleri camın içinde yeniden çizilmiş ince,
        badem gözlerdi (küçük göz bebeği); öteki üç yüzün taşınan klasik Flannel gözlerinden (kalın kontur, büyük
        göz bebeği) ayrı bir çizim diliydi, 6:18-6:30 yakın çekiminde görünüyordu. Şimdi klasik gözler kalır: üst
        kapak düz ve aşağıda (gözün üst ~%25'i silinir, kalın kapak çizgisi; göz bebeği kapağın altında yarım ay, yana
        bakar), kaşlar asimetrik (yakın kaş yüksek kemer, uzak kaş alçak ve düz), ağız kısa, yana itilmiş, eğik
        ("hmm"). 'kararlı'dan farkı: kaşlar V değil, kapaklar içe eğik değil düz. Aynı çizgi kalınlığı."""
        im = sil_koru(base, KAS_L, koru, oy=oy)
        im = sil_koru(im, KAS_R, koru, oy=oy)
        im = sil(im, AGIZ, oy=oy)
        # üst göz kapakları: gözün üstü (göz bebeğinin üst kısmı dahil) silinir, düz ve kalın kapak çizgisi
        im = sil(im, [(540, 424), (670, 424), (670, 449), (540, 447)], oy=oy)
        im = sil(im, [(818, 428), (918, 428), (918, 454), (818, 456)], oy=oy)
        c = Cizim(im, oy, seed=113)
        c.cizgi([(520, 346), (556, 318), (606, 304), (656, 314)], W + 2)          # yüksek kemer
        c.cizgi([(798, 384), (838, 380), (878, 380), (906, 384)], W + 2)          # alçak, düz
        c.cizgi([(546, 450), (584, 447), (624, 448), (660, 454)], W + 3)          # sol üst kapak (düz, aşağıda)
        c.cizgi([(826, 459), (854, 455), (884, 454), (912, 457)], W + 3)          # sağ üst kapak
        c.cizgi([(726, 760), (756, 757), (786, 750), (812, 738)], W)                # kısa, sağa itilmiş, eğik
        c.cizgi([(812, 738), (818, 728)], W - 1)
        return c.im

    def ciddi_yuz():
        """11. tur (animasyon S5): kalın kaşlar camın üst kenarına basar (gözler açık; kararlı'daki V ve kısık göz
        yok), ağız uçları belirgin aşağı."""
        im = sil_koru(base, KAS_L, koru, oy=oy)
        im = sil_koru(im, KAS_R, koru, oy=oy)
        im = sil(im, AGIZ, oy=oy)
        c = Cizim(im, oy, seed=117)
        c.cizgi([(512, 384), (560, 376), (612, 378), (666, 390)], W + 4)
        c.cizgi([(794, 392), (832, 378), (872, 374), (908, 378)], W + 4)
        c.cizgi([(646, 768), (668, 752), (720, 745), (776, 747), (804, 762)], W + 1)
        return c.im

    out = {
        "sakin": base,
        "dusunceli": dusunceli_yuz(),
        "ciddi": ciddi_yuz(),
        # B5.3b doruk ("hayır"): eski `kaymakcalan_kollar` (çizilmiş kollar) yerine en sert yüz: kaşlar V, ağız
        # uçları hafif aşağı. Kollar hazır çizimde yok; poz değil yüz taşır.
        # 9. tur (animasyon S8, izlenme S4): 640x360'ta 'ciddi' ile aynı okunuyordu: kaşlar kalın ve camın üstüne
        # inen V, kaş arası kırışık, göz kapakları içten aşağı eğik (gözler kısık), ağız uçları belirgin aşağı
        "kararli": kararli_yuz(),
    }
    for k, im in out.items():
        if SADECE and k not in SADECE:   # 13. tur: yalnız istenen yüz yazılsın (ör. kaymakcalan --yuz dusunceli)
            continue
        kaydet(im, f"kaymakcalan_v2_{k}")


# ------------------------------------------------------------------------------------------------ yüz yardımcısı
def yuz_kur(base, oy, bolgeler, seed, kaslar=None, gozler=None, agiz=None, w=6, sil_goz=True):
    """Ortak varyant kurucu. bolgeler: {"kas": [çokgen, ...], "goz": [...], "agiz": [...]} (kaynak koordinatı).
    kaslar/agiz: çizgi listeleri ya da Cizim alan fonksiyonlar; gozler: Cizim alan fonksiyon."""
    im = base.copy()
    if kaslar is not None:
        for p in bolgeler["kas"]:
            im = sil(im, p, oy=oy)
    if gozler is not None and sil_goz:
        for p in bolgeler["goz"]:
            im = sil(im, p, oy=oy)
    if agiz is not None:
        for p in bolgeler["agiz"]:
            im = sil(im, p, oy=oy)
    c = Cizim(im, oy, seed=seed)
    for k in (kaslar or []):
        k(c) if callable(k) else c.cizgi(k, w + 1)
    if gozler:
        gozler(c)
    for a in (agiz or []):
        a(c) if callable(a) else c.cizgi(a, w)
    return c.im


def acik_gozler(c, gozler, w):
    """Açık (şaşkın/fark eden) gözler: [(cx, cy, rx, ry, göz bebeği x, yarıçap)]; kalın üst kapak."""
    for cx, cy, rx, ry, px, pr in gozler:
        c.elips(cx, cy, rx, ry, dolgu=WHITE, w=w)
        c.cizgi([(cx - rx * 0.97, cy - ry * 0.10), (cx - rx * 0.62, cy - ry * 0.80), (cx, cy - ry * 1.0),
                 (cx + rx * 0.62, cy - ry * 0.80), (cx + rx * 0.97, cy - ry * 0.10)], w + 3, titrek=0.3)
        c.elips(px, cy + 1, pr, pr, dolgu=BLACK)


# ------------------------------------------------------------------------------------------------ Lenz
def lenz():
    """wojakland English Wojak (970x987). Sol kaş (475-606, 328-356), sağ kaş + dikey kırışık (688-778, 330-358);
    sol göz (497-592, 368-412), sağ göz (692-762, 382-422); ağız (560-712, 594-604) + köşe parantezleri (505-528,
    570-612 / 708-730, 600-625). Taban yüz zaten hafif endişeli-ciddi: sakin = taban."""
    base = tuval(yukle("lenz_kaynak_english.png"))
    oy = PAD_TOP
    B = {"kas": [[(462, 316), (616, 316), (616, 362), (462, 362)], [(668, 316), (790, 316), (790, 376), (668, 376)]],
         "goz": [[(488, 360), (602, 360), (602, 420), (488, 420)], [(684, 370), (776, 370), (776, 430), (684, 430)]],
         # sol çene konturu (440,560)->(550,660) ve çene gamzesi (565-650, 627-640) korunur
         "agiz": [[(536, 558), (736, 558), (736, 606), (722, 630), (690, 630), (660, 624), (536, 624)]]}
    W = 7
    out = {
        "sakin": base,
        # 10. tur (animasyon hakemi S3): sakin ile ciddi telefonda aynıydı (taban yüz zaten hafif endişeli): kalın V
        # kaşlar (iç uçlar ~28 px aşağı), kaş arası kırışık, uçları aşağı ağız (köşe parantezleri arasında)
        "ciddi": yuz_kur(base, oy, B, 21, w=W,
                         kaslar=[lambda c: c.cizgi([(474, 338), (518, 342), (562, 350), (604, 364)], W + 3),
                                 lambda c: c.cizgi([(678, 372), (708, 358), (746, 350), (782, 352)], W + 3),
                                 lambda c: c.cizgi([(643, 334), (646, 350), (644, 366)], W - 1)],
                         agiz=[lambda c: c.cizgi([(574, 612), (598, 600), (638, 595), (680, 597), (706, 610)], W)]),
        "fark": yuz_kur(base, oy, B, 22, w=W,
                        kaslar=[[(472, 330), (504, 311), (548, 302), (590, 309), (608, 322)],
                                [(684, 330), (714, 314), (750, 311), (782, 325)]],
                        # 14. tur (animasyon N2): göz çizgileri öteki yüzlerin yarı kalınlığındaydı: W -> W + 3
                        gozler=lambda c: acik_gozler(c, [(545, 391, 43, 28, 566, 13), (728, 403, 32, 24, 744, 11)], W + 3),
                        agiz=[[(584, 601), (636, 599), (690, 601)]]),
    }
    for k, im in out.items():
        kaydet(im, f"lenz_v2_{k}")


# ------------------------------------------------------------------------------------------------ Voss
def allik_sil(im: Image.Image, bolge_pts, pembe_g=175, oy=0) -> Image.Image:
    """Pembe allık taramasını çizgiye dokunmadan siler: pembe (255,175,202) ile siyah/beyaz karışımı pikseller G
    kanalından geri çözülür (G = alfa * 175): gri = G * 255 / 175; pembe-beyaz geçişleri beyaz olur."""
    a = np.array(im).astype(np.float32)
    zone = poly_mask(im.size, [(x, y + oy) for x, y in bolge_pts]) & (a[..., 3] > 0)
    tint = zone & ((a[..., 0] - a[..., 1]) > 6)
    g = np.clip(a[..., 1] * 255.0 / pembe_g, 0, 255)
    for ch in range(3):
        a[..., ch][tint] = g[tint]
    return Image.fromarray(a.astype(np.uint8))


def voss():
    """wojakland Blushing Suit Wojak (806x849): koyu saç, siyah takım, siyah kravat. Allık silinir; saç koyu kahve ->
    kumral (Lenz'in koyu kıvırcık saçından ayrılsın). Sol kaş (388-475, 220-238) + kırışık (478-492, 242-262);
    sağ kaş (552-618, 220-245) + kırışık (557-561, 250-272); gözler (402-480, 272-308) / (564-625, 281-316);
    ağız (460-575, 452-478)."""
    base = tuval(yukle("voss_kaynak_blushing_suit.png"))
    oy = PAD_TOP
    base = allik_sil(base, [(360, 310), (680, 310), (680, 395), (360, 395)], oy=oy)
    base = sac_rengi(base, [(0, 0), (806, 0), (806, 420), (0, 420)], (59, 41, 33), (170, 130, 80), oy=oy)
    # alın kırışığı y <= 207, sağ baş konturu x >= 630: bölgeler bunlara değmez
    B = {"kas": [[(380, 212), (500, 212), (500, 268), (380, 268)], [(540, 212), (626, 212), (626, 276), (540, 276)]],
         "goz": [], "agiz": [[(450, 440), (586, 440), (586, 486), (450, 486)]]}
    W = 6
    out = {
        "sakin": base,
        # 10. tur (animasyon hakemi S3): 2-5 px kaş farkı telefonda görünmüyordu: kalın V kaşlar, kaş arası kırışık,
        # uçları aşağı ağız (anlatıcının 'ciddi'siyle aynı dil; taban yüz aynı çizim ailesi)
        "ciddi": yuz_kur(base, oy, B, 31, w=W,
                         kaslar=[lambda c: c.cizgi([(392, 250), (428, 254), (464, 262), (498, 278)], W + 3),
                                 lambda c: c.cizgi([(552, 278), (572, 266), (602, 258), (632, 260)], W + 3),
                                 lambda c: c.cizgi([(523, 246), (525, 260), (524, 272)], W - 1)],
                         agiz=[lambda c: c.cizgi([(470, 476), (488, 466), (518, 462), (550, 464), (570, 476)], W + 1)]),
    }
    for k, im in out.items():
        kaydet(im, f"voss_v2_{k}")


# ------------------------------------------------------------------------------------------------ Sheskin
def sheskin():
    """wojakland Turtleneck Grey Hair Wojak (873x971): kır saç, siyah dikdörtgen gözlük, gri balıkçı yaka + lacivert
    blazer. Sol kaş (425-530, 222-240) + kırışık (534-548, 247-258); sağ kaş (622-702, 222-245) + kırışık (630,
    252-265); çerçeveler (407-559, 252-357) / (622-747, 262-360); gözler (442-536, 282-325) / (637-702, 289-332);
    ağız (512-647, 497-522); en alttaki alın kırışığı y <= 205. Şaşkın yüzde çerçeve korunur (kalın siyah maskesi)."""
    base = sac_duzle(tuval(yukle("sheskin_kaynak_turtleneck.png")))
    oy = PAD_TOP
    koru = kalin_siyah(base, 4)
    W = 6
    im = base.copy()
    for p in ([(415, 210), (562, 210), (562, 264), (415, 264)], [(612, 210), (714, 210), (714, 270), (612, 270)],
              [(428, 266), (556, 266), (556, 348), (428, 348)], [(628, 274), (744, 274), (744, 352), (628, 352)]):
        im = sil_koru(im, p, koru, oy=oy)
    im = sil(im, [(505, 486), (656, 486), (656, 530), (505, 530)], oy=oy)
    c = Cizim(im, oy, seed=41)
    c.cizgi([(426, 233), (452, 218), (490, 212), (528, 215), (546, 225)], W + 1)
    c.cizgi([(624, 236), (648, 221), (676, 217), (704, 226)], W + 1)
    acik_gozler(c, [(488, 305, 38, 26, 508, 12), (670, 313, 30, 22, 686, 10)], W)
    c.elips(582, 512, 15, 20, dolgu=(45, 30, 30, 255), w=W)
    out = {"sakin": base, "saskin": c.im}
    for k, v in out.items():
        kaydet(v, f"sheskin_v2_{k}")


def sac_duzle(im: Image.Image, bolgeler=((230, 50, 425, 420), (630, 30, 770, 210)), esik=168,
              koyu=(128, 129, 132), acik=(196, 197, 200)) -> Image.Image:
    """8. tur (animasyon hakemi S8): kaynağın püskürtme (airbrush) gri saçı, wojak'ın düz dolgu diline uymuyordu:
    başın üst bölümündeki gri dolgu (siyah konturların içi) iki düz griye indirgenir. Ton haritası yumuşatılıp
    eşiklenir (sınır pürüzsüz), konturun dibindeki kenar yumuşatma pikselleri olduğu gibi kalır."""
    a = np.array(im).astype(np.int32)
    rgb = a[..., :3]
    lum = rgb.mean(-1)
    notr = (np.abs(rgb[..., 0] - rgb[..., 1]) < 14) & (np.abs(rgb[..., 1] - rgb[..., 2]) < 14)
    gri = notr & (lum > 32) & (lum < 236) & (a[..., 3] > 200)   # kontur 0-16; püskürtmenin en koyusu ~50
    bolge = np.zeros_like(gri)
    for x0, y0, x1, y1 in bolgeler:   # kaynak px (tuvalin üst payı eklenir): sol yan saç ve sağ üstteki ince saç
        bolge[y0 + PAD_TOP:y1 + PAD_TOP, x0:x1] = True
    siyah = (lum < 32) & (a[..., 3] > 100)
    kontur_yani = dil(siyah, 2)
    sac = gri & bolge
    hedef = sac & ~kontur_yani
    yum = np.array(Image.fromarray(np.where(sac, lum, 220).astype(np.uint8)).filter(ImageFilter.GaussianBlur(7)))
    k = yum < esik
    a[hedef & k, :3] = koyu
    a[hedef & ~k, :3] = acik
    # konturun yanındaki saç pikselleri de en yakın düz tona (kenar yumuşatma: siyaha doğru karışım korunur)
    yan = sac & kontur_yani & (lum > 60)
    a[yan & k, :3] = koyu
    a[yan & ~k, :3] = acik
    return Image.fromarray(a.astype(np.uint8))


# ------------------------------------------------------------------------------------------------ eczacı, müşteri
def eczaci():
    """wojakland Suit Wojak (820x768): kır saç, gri bıyık, bordo ceket, krem gömlek, yeşil papyon. Senaryo yalnız
    sakin yüz istiyor: çizime dokunulmadı (yalnız üst pay)."""
    kaydet(tuval(yukle("eczaci_kaynak_suit.png")), "eczaci_v2_sakin")


def musteri():
    """wojakland Tired Blonde Wojak (841x821): B1.8 eczane müşterisi (uyku ilacı almaya gelen, uykusuz yüz). Değişmedi."""
    kaydet(tuval(yukle("musteri_kaynak_tired_blonde.png")), "musteri_v2_sakin")


# ------------------------------------------------------------------------------------------------ Kelsey
def kelsey():
    """F, Frances O. Kelsey rolü: HF 5_Daddys_Girl/11087 "Secretary Daddy's Girl" (1080x1261), eski uret.py ile aynı
    renk değişimi (saç sarı -> koyu kahve, ceket pembe -> lacivert; bel altı kırpılır). Kaynakta kaş yok (kirpikli
    göz + iki küçük kırışık): üç yüzün hepsine aynı ince kaş çizilir (perçem altı ile kirpik arası ~30 px).
    Eski sürümün kusurları giderildi: sakin yüzde çene konturu kopuktu (silme bölgesi konturu yiyordu), kararlı
    yüzde kaş göz kapağına yapışık çift çizgi gibiydi.
      sakin   : kırışıklar, ağız altındaki aşağı kıvrık yay ve sol yanak çizgisi silinir; düz dudak çizgisi kalır
      supheci : kaynağın kendi yüzü (kırışıklar + aşağı kıvrık yay + yanak çizgisi) + biri kalkık biri alçak kaş
      kararli : aşağı kıvrık yay silinir; kaşların iç uçları alçak, kırışıklar kalır"""
    src = np.array(yukle("kelsey_kaynak_secretary.png")).astype(np.int32)
    rgb = src[..., :3]

    def near(c, tol):
        return np.abs(rgb - np.array(c)).sum(-1) < tol

    a = src.copy()
    for c0, c1 in (((250, 217, 150), (78, 56, 44)), ((243, 103, 132), (52, 58, 84))):
        m = near(c0, 60) & (src[..., 3] > 0)
        a[m, :3] = c1
        mid = dil(m, 2) & ~m & (src[..., 3] > 0) & (rgb.mean(-1) > 40) & (rgb.mean(-1) < 235) & \
            (np.abs(rgb - np.array(c0)).sum(-1) < 400) & ((rgb.max(-1) - rgb.min(-1)) > 25)
        f = np.clip(rgb[mid].mean(-1) / np.array(c0).mean(), 0, 1)[:, None]
        a[mid, :3] = (np.array(c1) * f).astype(np.int32)
    base = tuval(Image.fromarray(a[:1090].astype(np.uint8)))
    oy = PAD_TOP
    KIRISIK = [[(624, 326), (662, 326), (662, 370), (624, 370)], [(736, 346), (760, 346), (760, 382), (736, 382)]]
    YAY = [(642, 610), (728, 610), (728, 652), (642, 652)]          # ağız altındaki aşağı kıvrık yay
    YANAK = [(498, 568), (548, 568), (548, 632), (498, 632)]        # sol yanak çizgisi (çene konturu x <= 490)
    W = 6

    def yap(silinecek, kaslar, ek=None, w_kas=W, son=None):
        im = base
        for p in silinecek:
            im = (sil_notr if p in (KAPAK_L, KAPAK_R, ALT_L, ALT_R) else sil)(im, p, oy=oy)
        c = Cizim(im, oy, seed=len(str(kaslar)))
        for k in kaslar:
            c.cizgi(k, w_kas)
        for k, w_ in (ek or []):
            c.cizgi(k, w_)
        for f in (son or []):
            f(c)
        return c.im

    # 9. tur (izlenme S4, animasyon S8): üç yüz telefonda aynı okunuyordu (fark birkaç piksel kaş açısıydı).
    # Göz kapağı bölgeleri (kirpikler dahil; alt/yan kirpikler kalır), ağız (pembe dudak gölgesi dahil)
    KAPAK_L = [(500, 350), (662, 350), (662, 400), (500, 400)]
    KAPAK_R = [(756, 364), (846, 364), (846, 408), (756, 408)]
    AGIZ = [(556, 588), (802, 588), (802, 634), (556, 634)]
    # 10. tur (animasyon hakemi S4): kısık gözlerde kirpikler alt kapakta kalıyordu (üst kapakla birlikte üst kirpikler
    # silinmişti): kısık gözün alt yarısı (göz bebeği parçası, alt kapak, alt kirpikler, iç köşe kırıntısı) silinir;
    # temiz kısık göz çizilir: kalın üst kapak (ek), altında göz bebeği şeridi, ince alt kapak, dış uçta üst kirpikler
    ALT_L = [(508, 398), (664, 398), (664, 440), (508, 440)]
    ALT_R = [(734, 378), (760, 378), (760, 400), (862, 400), (862, 452), (734, 452)]

    def kisik_sol(lid_y):
        def f(c):
            y = lid_y
            c.cokgen([(566, y + 2), (614, y + 4), (610, y + 13), (590, y + 17), (570, y + 13)], BLACK)
            c.cizgi([(546, y + 8), (572, y + 18), (608, y + 18), (640, y + 11)], W - 2)
            for p in ([(546, y - 1), (535, y - 10), (529, y - 21)], [(560, y - 2), (552, y - 13), (550, y - 24)],
                      [(575, y - 3), (571, y - 14), (572, y - 24)]):
                c.cizgi(p, W - 1, titrek=0.2)
        return f

    def kisik_sag(lid_y):
        def f(c):
            y = lid_y
            c.cokgen([(800, y + 1), (836, y), (832, y + 11), (818, y + 15), (804, y + 11)], BLACK)
            c.cizgi([(778, y + 7), (800, y + 16), (830, y + 16), (850, y + 8)], W - 2)
            for p in ([(842, y - 2), (851, y - 12), (854, y - 22)], [(830, y - 3), (835, y - 14), (836, y - 24)],
                      [(818, y - 3), (820, y - 14), (818, y - 23)]):
                c.cizgi(p, W - 1, titrek=0.2)
        return f

    sakin = yap(KIRISIK + [YAY, YANAK], [[(516, 338), (552, 330), (592, 330), (620, 338)],
                                         [(770, 356), (800, 349), (834, 352)]])
    # 10. tur (animasyon hakemi S4): dudak tonu yüzden yüze değişiyordu (sakinde soluk pembe dudak gölgesi, ötekilerde
    # saf siyah ağız): pembe gölge silinir (G kanalından geri çözülür; siyah çizgi aynen kalır)
    sakin = allik_sil(sakin, [(556, 580), (802, 580), (802, 640), (556, 640)], pembe_g=180, oy=oy)
    out = {
        "sakin": sakin,
        # şüpheci: sol göz kısık (düz, kalın kapak), sol kaş alçak; sağ kaş yüksek kemer. 10. tur (izlenme S1):
        # ağzın sağ ucu kalkıktı: kırpık gözle birlikte telefonda göz kırpan bir sırıtma gibi okunuyordu: ağız düz,
        # uçları hafifçe aşağı (kararlıdan yumuşak)
        "supheci": yap([YAY, KIRISIK[0], KIRISIK[1], KAPAK_L, ALT_L, AGIZ],
                       [[(512, 352), (558, 356), (602, 361), (636, 368)],
                        [(760, 352), (790, 334), (826, 329), (854, 338)]],
                       ek=[([(538, 402), (572, 398), (610, 398), (646, 402)], W + 2),
                           ([(578, 616), (622, 611), (680, 610), (738, 612), (774, 619)], W)], w_kas=W + 1,
                       son=[kisik_sol(398)]),
        # kararlı: iki kaş kalın ve içe doğru aşağı (V), kaş arası kırışık, iki göz kısık ve kapaklar içten aşağı,
        # ağız düz ve uçları aşağı (çene sıkılı)
        "kararli": yap(KIRISIK + [YAY, KAPAK_L, KAPAK_R, ALT_L, ALT_R, AGIZ],
                       [[(512, 334), (556, 341), (600, 355), (636, 372)],
                        [(768, 386), (796, 372), (826, 362), (846, 361)]],
                       ek=[([(694, 346), (698, 362), (696, 378)], W - 1),
                           ([(538, 396), (575, 397), (612, 401), (648, 408)], W + 2),
                           ([(768, 414), (800, 408), (835, 405), (856, 408)], W + 2),
                           ([(574, 623), (600, 612), (650, 608), (720, 608), (768, 612), (792, 625)], W)],
                       w_kas=W + 2, son=[kisik_sol(398), kisik_sag(406)]),
    }
    for k, im in out.items():
        kaydet(im, f"kelsey_v2_{k}")


# ------------------------------------------------------------------------------------------------ veteriner (Aygün)
def veteriner():
    """Kısa videonun veteriner hocası (episodes/talidomit-turkiye/chars/uret.py veteriner()) ile AYNI yüz: kaynak
    wojakland Grandpa Wojak; gözlük, bıyık ve yanak parantezleri kaldırılır, saç düz açık kır, yüzün alt yarısı düz
    çizgilerle. FARK: kısa videodaki boyanmış laboratuvar önlüğü (süveter yelek beyaza boyanmış, revers/kravat/cep
    çizilmiş) YOK: hazır kahverengi süveter yelek + gri gömlek olduğu gibi kalır. (Kod kısa videonun betiğinden
    alındı; yalnız önlük adımı ve önlük çizgileri çıkarıldı.)"""
    src_path = ROOT / "episodes/talidomit-turkiye/chars/veteriner_kaynak_grandpa.png"
    g = np.array(Image.open(src_path).convert("RGBA")).astype(np.int32)
    H, W = g.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    rgb = g[..., :3]
    lum = rgb.mean(-1)
    op = g[..., 3] > 0

    def ero(m, r):
        return ~dil(~m, r)

    def flood(mask, seed):
        im = Image.fromarray((mask * 255).astype(np.uint8)).copy()
        ImageDraw.floodfill(im, seed, 128)
        return np.array(im) == 128

    def pm(pts):
        return poly_mask((W, H), pts)

    # 0) gözlük (kısa videodaki gibi)
    box = (yy > 245) & (yy < 450) & (xx > 330) & (xx < 835)
    frame0 = (np.abs(rgb - 196).sum(-1) < 12) & box
    light = (lum > 215) & box & op & ~frame0
    interior = flood(light, (548, 400)) | flood(light, (745, 410))
    filled = ~flood(~interior, (0, 0))
    eyes = filled & ~interior
    zone = (dil(filled, 24) | pm([(335, 318), (462, 294), (472, 320), (345, 340)])
            | pm([(625, 262), (685, 262), (685, 315), (625, 315)]) | pm([(790, 318), (834, 318), (834, 350), (790, 350)]))
    frame = frame0 & zone
    er = (dil(frame, 9) & box) | filled
    src = g.copy()
    g[er, :3] = 255
    g[dil(frame, 15) & box & (lum > 100) & ~eyes, :3] = 255
    g[pm([(612, 255), (690, 255), (690, 330), (612, 330)]) & (lum < 200) & ~eyes, :3] = 255
    g[pm([(790, 318), (834, 318), (834, 350), (790, 350)]) & (lum < 200), :3] = 255
    g[pm([(684, 398), (714, 398), (714, 428), (684, 428)]) & (lum < 200), :3] = 255
    g[eyes] = src[eyes]
    g[er & op & ~ero(op, 6), :3] = 0
    hs = pm([(426, 262), (421, 268), (395, 290), (360, 319), (334, 342), (300, 342), (300, 262)]) & op & \
        (g[..., :3].mean(-1) > 200)
    g[hs, :3] = (169, 162, 156)
    spikes = pm([(392, 282), (360, 314), (334, 337), (325, 326), (352, 296), (378, 276)]) & op & (g[..., :3].mean(-1) < 200)
    g[spikes, :3] = (169, 162, 156)
    # 1) bıyık + yanak parantezleri
    low = pm([(522, 478), (585, 470), (640, 482), (722, 470), (750, 480), (748, 535), (738, 572), (700, 598),
              (585, 598), (522, 560)])
    low &= ~((yy < 478) & (xx < 700))
    g[low & op, :3] = 255
    # 2) saç: tek düz açık kır
    src_hair = g[..., :3].copy()
    lum = src_hair.mean(-1)
    sat = src_hair.max(-1) - src_hair.min(-1)
    hair_zone = ((yy < 345) | ((yy < 380) & (xx < 345))) & op
    mapped = np.zeros((H, W), bool)
    for c0 in ((104, 99, 95), (133, 127, 122), (169, 162, 156)):
        m = hair_zone & (np.abs(src_hair - np.array(c0)).sum(-1) < 18)
        g[m, :3] = 200
        mapped |= m
    seam = dil(mapped, 3) & hair_zone & ~mapped & (lum >= 90) & (lum <= 185) & (sat < 20)
    g[seam, :3] = 200
    mid = hair_zone & ~mapped & ~seam & (lum > 20) & (lum < 100) & (sat < 16)
    g[mid, :3] = np.clip(g[mid, :3] * 2.0, 0, 255)
    im = tuval(Image.fromarray(g.astype(np.uint8)))
    oy = PAD_TOP
    c = Cizim(im, oy, seed=61)
    c.cizgi([(421, 268), (395, 290), (360, 319), (334, 342)], 8, titrek=0.3)

    def curve(p0, p1, bow, n=7):
        (x0, y0), (x1, y1) = p0, p1
        nx, ny = -(y1 - y0), (x1 - x0)
        ln = math.hypot(nx, ny)
        return [(x0 + (x1 - x0) * t + nx / ln * bow * math.sin(math.pi * t),
                 y0 + (y1 - y0) * t + ny / ln * bow * math.sin(math.pi * t)) for t in np.linspace(0, 1, n)]

    for p0, p1 in (((382, 80), (520, 48)), ((298, 228), (364, 176)), ((308, 302), (370, 242))):
        c.cizgi(curve(p0, p1, 6), 5, titrek=0.3)
    c.cizgi([(578, 466), (556, 492), (552, 522)], 8)
    c.cizgi([(726, 478), (738, 500), (736, 526)], 8)
    c.cizgi([(588, 552), (618, 545), (655, 543), (690, 546), (708, 554)], 8)
    c.cizgi([(628, 586), (652, 582), (672, 586)], 6)
    kaydet(c.im, "veteriner_v2_sakin")
    # 9. tur (izlenme S2): "Bakanlığı uyarmış" anında ikinci yüz: kaşlar içe doğru aşağı (kararlı uyarı), ağız
    # uçları daha aşağı; aynı çizgi kalınlığı (8)
    im2 = sil(c.im, [(574, 530), (724, 530), (724, 572), (574, 572)], oy=oy)
    c2 = Cizim(im2, oy, seed=62)
    c2.cizgi([(498, 268), (538, 268), (578, 276), (606, 288)], 10)
    c2.cizgi([(700, 298), (722, 284), (752, 278), (774, 282)], 10)
    c2.cizgi([(652, 256), (654, 272)], 6)
    c2.cizgi([(584, 564), (604, 550), (650, 545), (690, 548), (712, 564)], 8)
    kaydet(c2.im, "veteriner_v2_ciddi")


def agiz_acik():
    """9. tur (animasyon hakemi S10): balon repliklerinde oyunculuk yoktu. Balonu olan yüzlerin AÇIK AĞIZLI eşi
    (motor `balon {agiz: ...}`: balon açıkken hece vuruşlarında bu görsele geçer). Aynı tuval, aynı çizgi kalınlığı;
    yalnız ağız: koyu ağız içi + siyah kontur (kanalın MS-Paint dili).
    11. tur (animasyon S6): gülümseyen temsilcinin ağzı her hecede ince sırıtışla geniş koyu hilal arasında gidip
    geliyordu (telefonda yanıp sönen ürkütücü sırıtış): her açık ağzın bir ARA eşi var (`*_konusuyor_yari`: aynı
    genişlikte dar yarık); motor kapalı -> yarık -> açık sırasıyla, en az 4 kare tutarak geçer (`balon {agiz:
    [yari, acik]}`). Açık hilal de biraz sığlaştı. Gergin açık ağzın altında eski çizginin sağ ucundaki kanca
    (M3: ağzın sağ köşesinde siyah leke) artık siliniyor."""
    AGIZ_IC = (78, 24, 30, 255)
    # eczacı (Suit Wojak; ağız bıyığın altında): bıyığın alt kenarının altında küçük oval
    e = Image.open(HERE / "eczaci_v2_sakin.png").convert("RGBA")
    c = Cizim(e, PAD_TOP, seed=71)
    c.elips(545, 528, 27, 13, dolgu=AGIZ_IC, w=6)
    kaydet(c.im, "eczaci_v2_konusuyor")
    c = Cizim(e.copy(), PAD_TOP, seed=74)
    c.elips(545, 524, 25, 7, dolgu=AGIZ_IC, w=6)
    kaydet(c.im, "eczaci_v2_konusuyor_yari")
    ep = ROOT / "episodes/talidomit-turkiye/chars"
    # Short'tan gelen temsilci (1950s Businessman), gülümseyen yüz: gülüş çizgisi üst dudak, altı açık
    g = Image.open(ep / "temsilci_gulumsuyor.png").convert("RGBA")
    g = sil(g, [(748, 818), (852, 818), (852, 846), (748, 846)])      # çene çizgisi (açık ağız altında kalırdı)
    g = sil(g, [(628, 738), (934, 738), (934, 816), (628, 816)])      # eski gülüş çizgisi (çift çizgi olmasın; 11. tur: alt kenar payı yarıkta görünüyordu)
    ust = [(652, 762), (700, 781), (760, 791), (830, 791), (912, 780)]
    for ad, alt in (("temsilci_gulumsuyor_konusuyor",
                     [(912, 780), (872, 806), (800, 819), (730, 808), (676, 782), (652, 762)]),
                    ("temsilci_gulumsuyor_konusuyor_yari",
                     [(912, 780), (868, 801), (800, 811), (730, 803), (676, 780), (652, 762)])):
        c = Cizim(g.copy(), 0, seed=72)
        c.cokgen(ust + alt, AGIZ_IC)
        c.cizgi(ust, 9)
        c.cizgi(alt, 9)
        c.cizgi([(776, 862), (800, 858), (824, 862)], 7)             # çene çizgisi aşağıda
        kaydet(c.im, ad)
    # gergin yüz: düz endişeli çizgi yerine açık, aşağı kıvrık ağız. Silme kutusu eski çizginin sağ ucundaki aşağı
    # kancayı da (~897-907, 822-832) kapsar (10. turda kalıp siyah leke olarak görünüyordu)
    r = Image.open(ep / "temsilci_gergin.png").convert("RGBA")
    r = sil(r, [(736, 778), (930, 778), (930, 842), (736, 842)])
    ust = [(748, 814), (792, 797), (860, 796), (906, 812)]
    for ad, alt in (("temsilci_gergin_konusuyor", [(906, 812), (872, 836), (806, 842), (752, 828), (748, 814)]),
                    ("temsilci_gergin_konusuyor_yari", [(906, 812), (872, 822), (806, 826), (752, 820), (748, 814)])):
        c = Cizim(r.copy(), 0, seed=73)
        c.cokgen(ust + alt, AGIZ_IC)
        c.cizgi(ust, 9)
        c.cizgi(alt, 9)
        kaydet(c.im, ad)


KARAKTERLER = {"anlatici": anlatici, "kaymakcalan": kaymakcalan, "lenz": lenz, "voss": voss, "sheskin": sheskin,
               "eczaci": eczaci, "musteri": musteri, "kelsey": kelsey, "veteriner": veteriner,
               "agiz": agiz_acik}


def main(argv):
    global KAYIT, SADECE
    if "--kayitsiz" in argv:
        KAYIT = False
        argv = [a for a in argv if a != "--kayitsiz"]
    if "--yuz" in argv:   # 7. tur: yalnız bu yüzü yaz (ör. anlatici --yuz mutlu); öteki dosyalara dokunma
        i = argv.index("--yuz")
        SADECE = set(argv[i + 1].split(","))
        argv = argv[:i] + argv[i + 2:]
    for ad in (argv or list(KARAKTERLER)):
        KARAKTERLER[ad]()


if __name__ == "__main__":
    main(sys.argv[1:])
