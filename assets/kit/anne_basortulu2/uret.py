#!/usr/bin/env python3
"""anne_basortulu2 kitini kaynaktan yeniden üretir (kit.json'daki açıklamaya bakın).

    python assets/kit/anne_basortulu2/uret.py

1. Kaynak (anne): wojakland "Blushing Hijab Wojak" (458x538 RGBA, büyütme yok),
   `python tools/wojak_site.py get wl:blushing_hijab_wojak.png --out-dir episodes/van-depremi-azra-bebek/chars
   --name anne_hijab_kaynak` ile indirildi. Kanalın C3De/C2Fr kadınıyla aynı aile: yumuşak gölgeli, dökümlü
   açık başörtüsü, kirpikli anime gözler, görünen saç çizgisi, dişleri görünen aralık ağız.
2. Düzeltmeler: boyun zinciri (choker) ve asma kilitli kolye silinir; yanak allığı %80 azaltılır (gülümseme yok);
   pembe üst -> kahverengi örgü (#6B4A2E, C3De'deki hırka); başörtüsü ve gömlek hafif krem tona çekilir;
   büst kırpımı (göğüs altı kesilir).
   Yön: kaynak zaten 3/4 SAĞA dönük (burun yüz ortasının sağında, sağ göz sağ kontura yakın; kanalın
   C3De/C2Fr kadını da aynı açıda, solda durup içeri bakıyor) -> aynalanmaz, 'right' kaydedilir. Renderer
   sol tarafta aynalamaz; sağ tarafta kullanılırsa kendisi aynalar.
3. Kucaktaki bebek (hazır çizim): wojakland "Redhead Tradwife with Baby Wojak" içindeki askılı bezde uyuyan
   yenidoğan + onu tutan el (bkz. bebek_katmani); üç varyantta da aynı yerde (kutu sabit).
4. tek_gozyasi: tools/kit_varyant.py ile (kit.json 'variants'); agliyor: iki gözden kalın yaş + açık, titreyen ağız.
5. Ten (son adım, her PNG'de ayrı): yüz, boyun ve bebeği tutan el kanalın kadını gibi şeftali (ten_rengi()).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

KIT = Path(__file__).resolve().parent
ROOT = KIT.parent.parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))
import kit_varyant  # noqa: E402
from wojak import facing  # noqa: E402

CHARS = ROOT / "episodes" / "van-depremi-azra-bebek" / "chars"
SRC = CHARS / "anne_hijab_kaynak.png"      # wojakland blushing_hijab_wojak.png
BEBEK_SRC = CHARS / "bebek_kucak_kaynak.png"  # wojakland redhead_tradwife_with_baby_wojak.png
CROP_H = 490                                # büst: bu satırın altı kesilir (alt kenar düz ve opak kalır)
BROWN = np.array((107, 74, 46), np.float32)  # #6B4A2E, C3De'deki kahverengi örgü
WARM = np.array((1.0, 0.975, 0.935), np.float32)  # başörtüsü/gömlek: soğuk gri -> krem (C3De/C2Fr)
DEBLUSH = 0.80
HAIR = np.array((78, 58, 46), np.float32)       # görünen saç (kaynakta düz gri)
SAC_TOHUM = (305, 40)                           # gri alanın içinden bir nokta
BOYUN_TOHUM = (230, 280)                        # çene çizgisinin altındaki boyun (beyaz)
BOYUN_SAG_TOHUM = (282, 271)                    # dikey boyun çizgisinin sağında kalan küçük beyaz cep


def _lum(a: np.ndarray) -> np.ndarray:
    return 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]


def _cene_y(x: int) -> float:
    """Çene çizgisinin beklenen y'si (kaynakta ölçüldü: (188,212) -> (240,262) -> (272,268))."""
    return 212 + (x - 188) * 50 / 52 if x <= 240 else 262 + (x - 240) * 6 / 32


def zincir_sil(a: np.ndarray) -> np.ndarray:
    """Boyundaki zincir: her sütunda çene çizgisinin altı ile boyun alt konturu arasında kalan gri halkalar
    beyaza boyanır (çene çizgisi, ağız, boyun konturu ve sağdaki dikey boyun çizgisi korunur)."""
    lum = _lum(a)
    for x in range(187, 274):
        col = lum[200:330, x]
        runs, y = [], 0
        while y < len(col):
            if col[y] < 80:
                y0 = y
                while y + 1 < len(col) and col[y + 1] < 80:
                    y += 1
                runs.append((y0, y))
            y += 1
        exp = _cene_y(x) - 200
        runs = [r for r in runs if abs(r[0] - exp) <= 9]
        if not runs:
            continue
        j1 = runs[0][1]
        # alttan yukarı: boyun konturu + başörtüsü (lum<240 kesintisiz koşu) başlangıcı
        t = len(col) - 1
        while t > j1 and col[t] < 240:
            t -= 1
        y0, y1 = 200 + j1 + 3, 200 + t - 1
        if y1 > y0:
            seg = a[y0:y1 + 1, x]
            m = _lum(seg) < 253
            seg[m, :3] = 253
    return a


def allik_azalt(a: np.ndarray) -> np.ndarray:
    """Yanak allığını %80 azaltır: yüz kutusunda pembe (R>G, G~B) piksellerin G/B'si R'ye doğru çekilir."""
    sub = a[120:225, 185:355]
    r, g, b = sub[..., 0], sub[..., 1], sub[..., 2]
    m = (r - g > 6) & (np.abs(g - b) < 9) & (sub[..., 3] > 0)
    sub[..., 1] = np.where(m, g + DEBLUSH * (r - g), g)
    sub[..., 2] = np.where(m, b + DEBLUSH * (r - b), b)
    return a


def _knit(h: int, w: int) -> np.ndarray:
    """Örgü dokusu çarpanı: dikey fitiller + her 26 px'de bir saç örgüsü (cable) sütunu, çok hafif."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    rib = 0.055 * np.cos(2 * np.pi * xx / 6.5)
    cx = (xx % 26) - 13
    cable_col = np.clip(1 - np.abs(cx) / 7.0, 0, 1)
    cable = 0.09 * cable_col * np.sin(2 * np.pi * (yy / 11.0) + np.sign(cx) * 1.3)
    return 1 + rib * (1 - cable_col) + cable


def ust_kahve(a: np.ndarray) -> np.ndarray:
    """Pembe üst -> kahverengi örgü; asma kilitli kolye üstle birlikte boyanır."""
    r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    pink = (r - g > 25) & (b - g > 8) & (yy > 400) & (al > 0)
    m = Image.fromarray((pink * 255).astype(np.uint8))
    closed = np.array(m.filter(ImageFilter.MaxFilter(31)).filter(ImageFilter.MinFilter(31))) > 0
    lum = _lum(a)
    sat = a[..., :3].max(-1) - a[..., :3].min(-1)
    kolye = (xx > 195) & (xx < 340) & (yy > 431)        # zincir + asma kilit bölgesi
    chain = closed & ~pink & (sat < 40) & (lum > 95) & kolye
    reg = pink | chain
    # düz dolgu; yalnız üstün sol/sağ siyah kenarındaki yumuşatma koyulaşır (kolye bölgesinde iz kalmaz)
    k = np.where((lum < 150) & ~(kolye & closed), np.clip(lum / 203.0, 0, 1.0), 1.0)
    tex = _knit(*a.shape[:2])
    col = BROWN[None, None, :] * (k * tex)[..., None]
    a[..., :3] = np.where(reg[..., None], np.clip(col, 0, 255), a[..., :3])
    return a


def sicak_ton(a: np.ndarray) -> np.ndarray:
    """Başörtüsü ve gömleğin soğuk grisini kreme çeker; yüzün saf beyazı (lum>=250) ve siyah çizgiler aynı kalır."""
    lum = _lum(a)
    sat = a[..., :3].max(-1) - a[..., :3].min(-1)
    m = (sat < 22) & (a[..., 3] > 0)
    t = (np.clip((lum - 60) / 60.0, 0, 1) * np.clip((250 - lum) / 8.0, 0, 1))[..., None]
    warm = a[..., :3] * (1 + t * (WARM[None, None, :] - 1))
    a[..., :3] = np.where(m[..., None], warm, a[..., :3])
    return a


def sac(a: np.ndarray) -> np.ndarray:
    """Alnın üstünde başörtüsünün altından görünen düz gri alan (saç) koyu kahve yapılır (C3De/C2Fr: koyu saç).
    Kenarda yumuşak geçiş: çekirdek maske hafif bulanıklaştırılıp karıştırılır."""
    lum = _lum(a)
    sat = a[..., :3].max(-1) - a[..., :3].min(-1)
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    grey = (np.abs(lum - 159) < 9) & (sat < 8) & (yy < 90) & (xx > 250) & (xx < 360) & (a[..., 3] > 200)
    m = Image.fromarray((grey * 255).astype(np.uint8)).copy()
    ImageDraw.floodfill(m, SAC_TOHUM, 128)            # yalnız ana gri alan (dış kenardaki gri pikseller değil)
    core = np.array(m) == 128
    soft = np.array(Image.fromarray((core * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8)))
    w = (np.maximum(soft / 255.0, core) * (lum < 236))[..., None]
    a[..., :3] = a[..., :3] * (1 - w) + HAIR[None, None, :] * w
    return a


def boyun_maske(a: np.ndarray, tohumlar: tuple = (BOYUN_TOHUM,)) -> np.ndarray:
    """Çene çizgisinin altındaki beyaz boyun bölgesi (sağdaki dikey boyun çizgisine ve başörtüsüne kadar)."""
    lum = _lum(a)
    wh = ((lum > 232) & (a[..., 3] > 200)).astype(np.uint8) * 255
    m = Image.fromarray(wh).copy()
    for t in tohumlar:
        if wh[t[1], t[0]] != 255:
            raise SystemExit(f"boyun_maske: tohum {t} beyaz boyun alanında değil")
        ImageDraw.floodfill(m, t, 128)
    return np.array(m) == 128


def boyun_golge(a: np.ndarray) -> np.ndarray:
    """Çene çizgisinin altındaki boyun (yüzle aynı saf beyaz olduğu için çene çizgisi 'maske kenarı' gibi
    okunuyordu) çenenin hemen altında hafif sıcak gölge alır, aşağı doğru açılır (C3De/C2Fr kadınında boyun
    çenenin altında koyulaşır). Çizgiler değişmez."""
    neck = boyun_maske(a)
    ust = np.full(a.shape[1], 10 ** 6)
    ys, xs = np.where(neck)
    np.minimum.at(ust, xs, ys)
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    d = np.clip((yy - ust[None, :]) / 30.0, 0, 1)
    guc = np.where(neck, 1.0 - 0.6 * d, 0.0)[..., None]          # çenede 1, 30 px aşağıda 0,4
    golge = np.array((0.93, 0.89, 0.86), np.float32)[None, None, :]
    a[..., :3] = a[..., :3] * (1 - guc * (1 - golge))
    return a


def anne_taban() -> tuple[Image.Image, np.ndarray]:
    """Anne tabanı (büst kırpımı) ve boyun maskesi (ten_rengi() için, aynı kırpımda)."""
    a = np.array(Image.open(SRC).convert("RGBA")).astype(np.float32)
    a = zincir_sil(a)
    a = allik_azalt(a)
    a = ust_kahve(a)
    a = sac(a)
    a = sicak_ton(a)
    boyun = boyun_maske(a, (BOYUN_TOHUM, BOYUN_SAG_TOHUM))[:CROP_H]   # + dikey boyun çizgisinin sağındaki beyaz
    a = boyun_golge(a)
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return im.crop((0, 0, im.width, CROP_H)), boyun


# ---- ten rengi -----------------------------------------------------------------------------------------
# Kanalın kadını (C3DeLN1sU7O, C2FriLUM2DR) şeftali tenli: yanak ölçüldü (247-253, 202-208, 161-163).
# Saf beyaz yüz, gölgeli başörtüsünün yanında "maske" gibi okunuyordu. Son adım olarak (üç PNG'nin her
# birinde ayrı ayrı; varyantlar boyanmamış tabandan üretilir, çift boyama olmaz) yüz, boyun ve bebeği tutan el
# bu renkle ÇARPILIR: gölge ve çizgiler korunur. Mavi gözyaşı (doygunluk >= 40), çizgiyle kapalı beyaz diş
# bandı ve bebek (beyaz, ayrı alan) dışarıda kalır; alfa değişmez (kutu aynı).
TEN = np.array((252, 207, 163), np.float32) / 255.0
YUZ_TOHUM = [(270, 100), (250, 200), (300, 250), (230, 240),
             (337, 185)]                                # agliyor: kalın sağ gözyaşının sağında kalan yanak şeridi
EL_TOHUM = [(300, 455), (380, 440)]                     # bebeği tutan el (bebek katmanıyla gelen)


def _dolgu(kosul: np.ndarray, tohumlar: list[tuple[int, int]]) -> np.ndarray:
    m = Image.fromarray((kosul * 255).astype(np.uint8))
    out = np.zeros(kosul.shape, bool)
    for t in tohumlar:
        if not kosul[t[1], t[0]]:
            raise SystemExit(f"ten_rengi: tohum {t} beyaz ten alanında değil")
        mm = m.copy()
        ImageDraw.floodfill(mm, t, 128)
        out |= np.array(mm) == 128
    return out


def ten_rengi(im: Image.Image, boyun: np.ndarray) -> Image.Image:
    a = np.array(im).astype(np.float32)
    rgb, al = a[..., :3], a[..., 3]
    mean = rgb.mean(-1)
    sat = rgb.max(-1) - rgb.min(-1)
    ten = (al > 200) & (mean >= 200) & (sat < 40)
    m = _dolgu(ten, YUZ_TOHUM + EL_TOHUM) | (boyun & (sat < 40))
    # kenar: maskeye 2 px komşu çizgi/yumuşatma pikselleri (doygunluğu düşük, saf beyazdan koyu) de çarpılır,
    # böylece çizginin iç kenarında açık gri hale kalmaz; dişler (~247) ve bebek (~253) gibi saf beyaz alanlar
    # (mean >= 240) dokunulmaz
    gen = np.array(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5))) > 0
    kenar = gen & ~m & (mean < 240) & (sat < 40) & (al > 0)
    w = (m | kenar)[..., None]
    a[..., :3] = np.where(w, rgb * TEN[None, None, :], rgb)
    return Image.fromarray(np.clip(np.rint(a), 0, 255).astype(np.uint8))


# ---- kucaktaki bebek (hazır çizim) ---------------------------------------------------------------------
# wojakland "Redhead Tradwife with Baby Wojak": kızıl saçlı annenin göğsündeki askılı bezde (sling) uyuyan
# yenidoğan (gözleri kapalı, yeşil örgü bere) ve onu tutan beyaz el. Annenin göğsü/boynu, omuz askısı, somon
# elbise ve çiçekli kol silinir; kalan bez + bebek + el kendi çizgileriyle (kod çizimi yok) bu annenin göğsüne,
# bebeğin başı kadrajın içine (sağa) bakacak şekilde konur. Bezin sol ucu annenin krem gömleğinin altına girer
# (gömleğin kenarı doğal sınır; düz kesik kenar görünmez), alt kısmı büst kırpımıyla kesilir.
BEBEK = {"olcek": 0.47, "yuz_x": 335, "yuz_y": 366}   # bebek yüzünün merkezi (anne görselinde, kırpım sonrası)
BEBEK_KUTU = (262, 600, 980, 1180)                     # kaynakta bez + bebek + el
BEBEK_YUZ = (705, 710)                                 # kaynakta bebek yüzünün merkezi
# kaynakta silinecek bölge: kızıl annenin göğsü/boynu ve omuz askısı (bebeğin başının üstü ve solu)
BEBEK_SIL = [(240, 590), (725, 590), (712, 630), (690, 650), (662, 690), (644, 712), (612, 713), (590, 718),
             (572, 731), (556, 752), (541, 775), (536, 800), (470, 817), (300, 860), (270, 866), (240, 870)]
GOMLEK_X, GOMLEK_Y = 163, 433                          # krem gömleğin kahverengi örgüyle sınırı (sol kenar, üst)


def bebek_katmani() -> Image.Image:
    im = Image.open(BEBEK_SRC).convert("RGBA")
    a = np.array(im).astype(np.float32)
    r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    somon = (r > 200) & (g > 130) & (g < 205) & (b > 110) & (b < 190) & (r - b > 45)
    sil = Image.new("L", im.size, 0)
    ImageDraw.Draw(sil).polygon(BEBEK_SIL, fill=255)
    sil = np.array(sil) > 0
    # çiçekli kol: bezin siyah sol kenar çizgisinin solu (satır satır)
    lum = _lum(a)
    kol = np.zeros_like(sil)
    for y in range(860, 1180):
        idx = np.where(lum[y, 255:300] < 70)[0]
        if len(idx):
            kol[y, :255 + idx[0]] = True
    a[..., 3] = np.where(somon | sil | kol, 0, al)
    # yanakta hafif pembe allık (kanalın kadın/çocuk ailesi gibi), çarpma karışımı
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    w = 0.22 * np.exp(-(((xx - 726) / 15.0) ** 2 + ((yy - 738) / 11.0) ** 2))
    pembe = np.array((255, 196, 200), np.float32) / 255.0
    beyaz = (lum > 200)[..., None]
    a[..., :3] = np.where(beyaz, a[..., :3] * (1 - w[..., None] * (1 - pembe)), a[..., :3])
    out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).crop(BEBEK_KUTU)
    s = BEBEK["olcek"]
    return out.resize((round(out.width * s), round(out.height * s)), Image.LANCZOS)


def ile_bebek(im: Image.Image) -> Image.Image:
    """Bebeği anneye yerleştirir; bezin sol ucu krem gömleğin altına girer. Alfa = anne ∪ bebek
    (üç varyant da bu görselden türediği için kutu üçünde aynı)."""
    bl = bebek_katmani()
    s = BEBEK["olcek"]
    x0 = round(BEBEK["yuz_x"] - (BEBEK_YUZ[0] - BEBEK_KUTU[0]) * s)
    y0 = round(BEBEK["yuz_y"] - (BEBEK_YUZ[1] - BEBEK_KUTU[1]) * s)
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    lay.paste(bl, (x0, y0), bl)
    out = im.copy()
    out.alpha_composite(lay)
    ta = np.array(im)
    kahve = (ta[..., 0].astype(int) - ta[..., 2] > 35) & (ta[..., 0] < 170) & (ta[..., 1] < 120)
    yy, xx = np.mgrid[0:im.height, 0:im.width]
    on = (ta[..., 3] > 0) & ~kahve & (xx < GOMLEK_X) & (yy >= GOMLEK_Y)
    oa = np.array(out)
    oa[on] = ta[on]
    return Image.fromarray(oa)


# ---- ağlayan gözler (yalnız agliyor) -------------------------------------------------------------------
def goz_aki_kizar(im: Image.Image, spec: dict) -> Image.Image:
    """Göz aklarını pembeleştirir (kanalın ağlayan kadınları C4V3eMFM6lF / C3iXf2zsRvo: kızarmış gözler).
    Yalnız göz elipslerinin içindeki beyaz (yüzün beyaz dolgusuna bağlı olmayan) pikseller çarpılır;
    kirpik parlaklıkları ve başörtüsü elips dışında kalır."""
    a = np.array(im).astype(np.float32)
    rgb = a[..., :3]
    mean = rgb.mean(-1)
    sat = rgb.max(-1) - rgb.min(-1)
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    el = np.zeros(mean.shape, bool)
    for cx, cy, rx, ry in spec["elips"]:
        el |= ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1
    yuz = _dolgu((a[..., 3] > 200) & (mean >= 200) & (sat < 40), YUZ_TOHUM[:4])
    m = el & (mean >= 190) & (sat < 40) & ~yuz & (a[..., 3] > 200)
    a[..., :3] = np.where(m[..., None], rgb * np.array(spec["carpan"], np.float32)[None, None, :], rgb)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


# ---- ağlayan ağız --------------------------------------------------------------------------------------
SS = 4
def acik_agiz(im: Image.Image, spec: dict) -> Image.Image:
    """Mevcut aralık ağzın yerine daha açık, titreyen (dalgalı) ağız; yalnız ağız bölgesi yeniden çizilir."""
    bx0, by0, bx1, by1 = spec["patch"]
    patch = im.crop((bx0, by0, bx1, by1))
    big = patch.resize((patch.width * SS, patch.height * SS), Image.LANCZOS)
    d = ImageDraw.Draw(big)
    P = lambda pts: [((x - bx0) * SS, (y - by0) * SS) for x, y in pts]  # noqa: E731
    x0, y0, x1, y1 = spec["cover"]
    d.ellipse(P([(x0, y0), (x1, y1)]), fill=tuple(spec["skin"]) + (255,))
    top, bot = P(spec["top"]), P(spec["bottom"])
    poly = top + bot[::-1]
    d.polygon(poly, fill=tuple(spec.get("ic", (70, 20, 26))) + (255,))
    mask = Image.new("L", big.size, 0)
    ImageDraw.Draw(mask).polygon(poly, fill=255)
    teeth = [(x, y + 0.5 * SS) for x, y in top] + [(x, y + spec["teeth_h"] * SS) for x, y in top[::-1]]
    tl = Image.new("RGBA", big.size, (0, 0, 0, 0))
    ImageDraw.Draw(tl).polygon(teeth, fill=(250, 248, 244, 255))
    tl.putalpha(Image.fromarray(np.minimum(np.array(tl.getchannel("A")), np.array(mask))))
    big.alpha_composite(tl)
    d = ImageDraw.Draw(big)
    lw = round(spec["line"] * SS)
    d.line(top, fill=(16, 12, 12, 255), width=lw, joint="curve")
    d.line(bot, fill=(16, 12, 12, 255), width=lw, joint="curve")
    for p in (top[0], top[-1]):
        d.ellipse([p[0] - lw / 2, p[1] - lw / 2, p[0] + lw / 2, p[1] + lw / 2], fill=(16, 12, 12, 255))
    small = big.resize(patch.size, Image.LANCZOS)
    out = im.copy()
    out.paste(small, (bx0, by0))
    out.putalpha(im.getchannel("A"))
    return out


def main() -> None:
    cfg = json.loads((KIT / "kit.json").read_text(encoding="utf-8"))
    taban, boyun = anne_taban()
    sakin = ile_bebek(taban)                       # boyanmamış taban: bütün varyantlar bundan üretilir
    ham = KIT / ".sakin_ham.png"
    sakin.save(ham)

    def bitir(src: Path, name: str) -> None:       # son adım: ten rengi, kaydet, bakış yönünü kaydet
        out = KIT / f"{name}.png"
        ten_rengi(Image.open(src).convert("RGBA"), boyun).save(out, optimize=True)
        facing.register(out, "right")

    for name, spec in cfg["variants"].items():
        tmp = KIT / f".{name}_tmp.png"
        kit_varyant.make(ham, spec, tmp)
        bitir(tmp, name)
        tmp.unlink()
    ag = cfg["agliyor"]
    tmp = KIT / ".agliyor_tmp.png"
    goz_aki_kizar(acik_agiz(sakin, ag["mouth"]), ag["goz_aki"]).save(tmp)
    kit_varyant.make(tmp, {"tears": ag["tears"]}, tmp)
    bitir(tmp, "agliyor")
    tmp.unlink()
    bitir(ham, "sakin")
    ham.unlink()
    for f in sorted(KIT.glob("*.png")):
        print("->", f.relative_to(ROOT), Image.open(f).size)


if __name__ == "__main__":
    main()
