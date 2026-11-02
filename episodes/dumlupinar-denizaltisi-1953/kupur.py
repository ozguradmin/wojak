"""dumlupinar-denizaltisi-1953: son kare için telifsiz, gerçekçi 1953 gazete kupürü (kendi tasarımımız).

    python episodes/dumlupinar-denizaltisi-1953/kupur.py      # -> img/kanit_2.jpg (1080x810)

Kaynak madde (birincil): Milliyet, 6 Nisan 1953, "Şehitlerimizin isimleri" — "Ankara 5 (A.A.) Millî Savunma Vekâleti
Temsil Bürosundan bildirilmiştir: Tebliğ numarası: 7 — Çanakkalede Nara önünde batan Dumlupınar denizaltı gemisinde
kalmış olan personelin kurtarılmasından tamamen ümit kesilmiştir." (Milliyet arşivi OCR'ı "kurta..." ya kadar birebir:
http://gazetearsivi.milliyet.com.tr/Arsiv/1953/04/06 ; cümlenin sonu TGB, Dibace, Trakya Gezi, MSB Askerî Müze ile aynı.)
- Başlık, künye ve söz Milliyet arşivinin OCR'ındaki yazımla ("Milli", "Vekâleti", "Çanakkalede"); OCR'da düşen
  parantez "(A.A.)" ve tırnak «» aynı sayfanın öteki künyelerine ("Ankara 4 (Milliyet)", «Dumlupınar») göre geri kondu.
- Milliyet'in logosu, adı taşıyan başlığı, yazı karakteri ve sayfa düzeni taklit edilmedi; yayının adı yalnız alttaki
  "Kaynak:" satırında (hesap sahibinin kupür kuralı).
- Komşu sütunlar: rastgele harflerden, telefonda okunamayacak kadar küçük ama keskin dizgi; okunabilir uydurma metin yok.
- Görünüm (son kare çeşitliliği): soluk gri-bej kâğıt, yatay katlama izi, dört kenarı yıpranmış makas kesimi, sıcak
  kurşun dizgi izi (harf başına ±1 px kayma, mürekkep taşması ve kırıkları), siyaha yakın zemin.
- Fontlar (fonts/, GUST Font License): TeX Gyre Heros Cn (dar grotesk manşet), TeX Gyre Schola (Century Schoolbook
  ailesi gövde); kaynak satırı Libre Franklin (SIL OFL).
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FONTS = ROOT / "episodes" / "karun-hazinesi-bros" / "fonts"
HEROS_CN = HERE / "fonts" / "texgyreheroscn-bold.otf"
SCHOLA_B = HERE / "fonts" / "texgyreschola-bold.otf"
SCHOLA_R = HERE / "fonts" / "texgyreschola-regular.otf"
OUT = HERE / "img" / "kanit_2.jpg"
RNG = np.random.default_rng(1953)

W, H = 1080, 810
PW, PH = 1000, 690
SS = 2
BASLIK = "Şehitlerimizin isimleri"
KUNYE = "Ankara 5 (A.A.) — Milli Savunma Vekâleti Temsil Bürosundan bildirilmiştir:"
NUMARA = "Tebliğ numarası: 7"
SOZ = ("«Çanakkalede Nara önünde batan Dumlupınar denizaltı gemisinde kalmış olan personelin "
       "kurtarılmasından tamamen ümit kesilmiştir.»")
KAYNAK = "Kaynak: Milliyet, 6 Nisan 1953"


def font(ad, boy, agirlik, opsz=None):
    f = ImageFont.truetype(str(FONTS / ad), boy * SS)
    if ad.startswith("SourceSerif"):
        f.set_variation_by_axes([agirlik, opsz or 20])
    else:
        f.set_variation_by_axes([agirlik])
    return f


def gurultu(h, w, olcek, sigma=1.0):
    k = RNG.normal(0, 1, (max(2, h // olcek), max(2, w // olcek))).astype(np.float32)
    im = Image.fromarray(((k - k.min()) / (np.ptp(k) + 1e-6) * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
    a = np.asarray(im).astype(np.float32) / 255 - 0.5
    return a / (a.std() + 1e-6) * sigma


def kagit(w, h):
    """1953 gazete kâğıdı: sararmış, kahverengiye çalan; iri gren, lif, kenarda koyu sararma, küf lekeleri."""
    a = np.zeros((h, w, 3), np.float32)
    a[...] = (214, 196, 156)
    a += gurultu(h, w, 140, 4)[..., None] * np.array([1.0, 1.0, 1.25])
    a += gurultu(h, w, 22, 2.5)[..., None]
    a += RNG.normal(0, 4.0, (h, w, 1))
    yy, xx = np.mgrid[0:h, 0:w]
    kenar = np.minimum.reduce([xx, w - 1 - xx, yy, h - 1 - yy]).astype(np.float32)
    a -= np.clip(1 - kenar / 46, 0, 1)[..., None] * np.array([26, 30, 38])
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im, "RGBA")
    for _ in range(800):
        x, y = RNG.uniform(0, w), RNG.uniform(0, h)
        L, t = RNG.uniform(3, 14), RNG.uniform(0, math.pi)
        c = (255, 255, 248, int(RNG.uniform(15, 40))) if RNG.random() < 0.5 else (110, 105, 95, int(RNG.uniform(8, 24)))
        d.line([(x, y), (x + L * math.cos(t), y + L * math.sin(t))], fill=c, width=1)
    # dikey katlanma izi (sayfa ortadan katlanmış)
    kat = Image.new("L", (w, h), 0)
    x0 = w * 0.63
    ImageDraw.Draw(kat).line([(x0, 0), (x0 + 6, h)], fill=55, width=3)
    im = Image.composite(Image.new("RGB", (w, h), (160, 152, 136)), im, kat.filter(ImageFilter.GaussianBlur(2.0)))
    acik = Image.new("L", (w, h), 0)
    ImageDraw.Draw(acik).line([(x0 + 3, 0), (x0 + 9, h)], fill=40, width=3)
    im = Image.composite(Image.new("RGB", (w, h), (250, 248, 240)), im, acik.filter(ImageFilter.GaussianBlur(2.4)))
    return im


def okunmaz_satirlar(w, h, satir=15, boy=12, bulanik=2.2, paragraf=True, yogunluk=0.78):
    f = ImageFont.truetype(str(FONTS / "SourceSerif4-opsz-wght.ttf"), boy * SS)
    f.set_variation_by_axes([420, 10])
    m = Image.new("L", (w * SS, h * SS), 0)
    d = ImageDraw.Draw(m)
    harf = "aaabcdeeefghiiıklmmnnoörssştuüvyz"
    y = 0
    while y + satir < h:
        x = 0
        son = paragraf and RNG.random() < 0.12
        sinir = w * (RNG.uniform(0.35, 0.8) if son else 1.0)
        while x < sinir - 10:
            n = int(RNG.integers(2, 9))
            kel = "".join(RNG.choice(list(harf), n))
            tw = d.textlength(kel, font=f) / SS
            if x + tw > sinir:
                break
            d.text((x * SS, y * SS), kel, font=f, fill=255)
            x += tw + boy * 0.33
        y += satir + (satir * 0.6 if son else 0)
    m = m.resize((w, h), Image.LANCZOS).filter(ImageFilter.GaussianBlur(bulanik))
    return m.point(lambda v: int(min(255, v * 1.6) * yogunluk))


def nokta_maskesi(yogun: np.ndarray, hucre: float, aci: float) -> np.ndarray:
    """yogun 0..1 (mürekkep miktarı) -> yuvarlak raster noktaları (0..1, hafif yumuşak)."""
    h, w = yogun.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    t = math.radians(aci)
    u = (xx * math.cos(t) + yy * math.sin(t)) / hucre
    v = (-xx * math.sin(t) + yy * math.cos(t)) / hucre
    r = np.sqrt((u - np.round(u)) ** 2 + (v - np.round(v)) ** 2)
    rr = np.sqrt(np.clip(yogun, 0, 1) / math.pi) * 0.98
    return np.clip((rr - r) * hucre * 0.9 + 0.5, 0, 1)


def renkli_raster(foto: Image.Image, w, h, hucre=3.6) -> tuple[np.ndarray, np.ndarray]:
    """CMYK raster: C 15°, M 75°, Y 0°, K 45°. Döndürür: (çarpan RGB 0..1, mürekkep alanı maskesi)."""
    c = np.asarray(foto.convert("RGB").resize((w, h), Image.LANCZOS)).astype(np.float32) / 255
    lo, hi = np.percentile(c, 1), np.percentile(c, 99.5)
    c = np.clip((c - lo) / (hi - lo), 0, 1) ** 0.95                     # soluk kaynağı ger (taşlar seçilsin)
    g = c.mean(-1, keepdims=True)
    c = np.clip(g + (c - g) * 1.35, 0, 1)                               # renk biraz doygun (kâğıt emer)
    k = 1 - c.max(-1)
    cmy = (1 - c - k[..., None]) / np.maximum(1 - k[..., None], 1e-3)
    k = k * 0.85
    kanal = [(cmy[..., 0], 15, (0.10, 0.62, 0.86)), (cmy[..., 1], 75, (0.86, 0.18, 0.55)),
             (cmy[..., 2] * 0.9, 0, (0.98, 0.92, 0.18)), (k, 45, (0.12, 0.11, 0.11))]
    carp = np.ones((h, w, 3), np.float32)
    for yog, aci, renk in kanal:
        m = nokta_maskesi(yog, hucre, aci)[..., None]
        carp *= 1 - m * (1 - np.array(renk, np.float32))
    return carp, np.ones((h, w), np.float32)


def murekkep(maske: Image.Image) -> Image.Image:
    m = maske.filter(ImageFilter.GaussianBlur(0.65))
    a = np.asarray(m).astype(np.float32) / 255
    a = np.clip((a - 0.12) * 1.25, 0, 1)
    a *= np.clip(0.88 + gurultu(*a.shape, 18, 0.05) + RNG.normal(0, 0.045, a.shape), 0, 1)
    return Image.fromarray((a * 255).astype(np.uint8))


def yazi_maskesi(size, isler):
    w, h = size
    m = Image.new("L", (w * SS, h * SS), 0)
    d = ImageDraw.Draw(m)
    for t, f, (x, y), anc in isler:
        d.text((x * SS, y * SS), t, font=f, fill=255, anchor=anc)
    return m.resize((w, h), Image.LANCZOS)


def _yerlestir(m: Image.Image, xy, size):
    out = Image.new("L", size, 0)
    out.paste(m, xy)
    return out


def kagit(w, h):
    """Soluk gri-bej 1950'ler gazete kâğıdı (R≈G+8, B≈G−22), lif, gren, kenarda hafif kirlenme, yatay katlama izi."""
    a = np.zeros((h, w, 3), np.float32)
    a[...] = (205, 197, 175)
    a += gurultu(h, w, 160, 5)[..., None] * np.array([1.0, 1.0, 1.15])
    a += gurultu(h, w, 18, 2.6)[..., None]
    a += RNG.normal(0, 4.2, (h, w, 1))
    yy, xx = np.mgrid[0:h, 0:w]
    kenar = np.minimum.reduce([xx, w - 1 - xx, yy, h - 1 - yy]).astype(np.float32)
    a -= np.clip(1 - kenar / 26, 0, 1)[..., None] * np.array([16, 17, 20])
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im, "RGBA")
    for _ in range(1100):
        x, y = RNG.uniform(0, w), RNG.uniform(0, h)
        L, t = RNG.uniform(3, 12), RNG.uniform(0, math.pi)
        c = (240, 236, 222, int(RNG.uniform(15, 40))) if RNG.random() < 0.5 else (100, 96, 86, int(RNG.uniform(8, 22)))
        d.line([(x, y), (x + L * math.cos(t), y + L * math.sin(t))], fill=c, width=1)
    return im


def katlama(p: Image.Image, y0: float) -> Image.Image:
    """Yatay katlama: koyu çizgi + altında açık sırt + hafif ton farkı."""
    w, h = p.size
    a = np.asarray(p).astype(np.float32)
    yy = np.arange(h, dtype=np.float32)[:, None]
    xs = np.arange(w, dtype=np.float32)[None, :]
    yc = y0 + 3.0 * np.sin(xs / w * 2.2)
    dy = yy - yc
    a -= (np.exp(-(dy ** 2) / (2 * 1.6 ** 2)) * 42)[..., None]
    a += (np.exp(-((dy - 4.5) ** 2) / (2 * 2.2 ** 2)) * 14)[..., None]
    a -= ((dy > 0) * 5.0)[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def minik_sutun(w, h, boy=10, satir=12.5, kalin=False):
    """Hafif yumuşak, telefonda okunmayacak kadar küçük sütun dizgisi (rastgele harf), iki yana yaslı, paragraf girintili."""
    f = ImageFont.truetype(str(SCHOLA_B if kalin else SCHOLA_R), boy * SS)
    m = Image.new("L", (w * SS, h * SS), 0)
    d = ImageDraw.Draw(m)
    harf = "aaaabcdeeeefghiiıklmmnnnoörrsştuüvyz"
    y = boy
    girinti = True
    while y + 2 < h:
        kel = []
        x = 14 if girinti else 0
        son = RNG.random() < 0.10
        sinir = w * (RNG.uniform(0.3, 0.75) if son else 1.0)
        while True:
            n = int(RNG.integers(2, 10))
            k = "".join(RNG.choice(list(harf), n))
            tw = d.textlength(k, font=f) / SS
            if x + tw > sinir:
                break
            kel.append((k, tw))
            x += tw + boy * 0.3
        if kel:
            toplam = sum(t for _, t in kel)
            x0 = 14 if girinti else 0
            bos = boy * 0.3 if son or len(kel) < 2 else (w - x0 - toplam) / (len(kel) - 1)
            x = x0
            for k, tw in kel:
                d.text((x * SS, (y + RNG.uniform(-0.3, 0.3)) * SS), k, font=f, fill=255, anchor="ls")
                x += tw + bos
        girinti = son
        y += satir + (satir * 0.4 if son else 0)
    return m.resize((w, h), Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.9))   # minik harf seçilmesin


def kursun_yazi(size, isler):
    """Sıcak kurşun dizgi izi: harf harf yaz, her harfe ±0,7 px kayma."""
    w, h = size
    m = Image.new("L", (w * SS, h * SS), 0)
    d = ImageDraw.Draw(m)
    for metin, f, (x, y), bosluk in isler:
        cx = x * SS
        for ch in metin:
            d.text((cx + RNG.uniform(-0.7, 0.7) * SS, (y + RNG.uniform(-0.7, 0.7)) * SS), ch, font=f, fill=255,
                   anchor="ls")
            cx += d.textlength(ch, font=f) + (bosluk * SS if ch == " " else 0)
    return m.resize((w, h), Image.LANCZOS)


UNLU = set("aeıioöuüâîûAEIİOÖUÜÂÎÛ")


def heceler(kelime):
    """Türkçe hece sınırları: ünsüzden önce, ardından ünlü geliyorsa (ka-lmış değil, kal-mış)."""
    harf = [i for i, c in enumerate(kelime) if c.isalpha()]
    sinir = []
    for j in range(1, len(harf) - 1):
        i = harf[j]
        if kelime[i] not in UNLU and kelime[harf[j + 1]] in UNLU and any(c in UNLU for c in kelime[:i]):
            sinir.append(i)
    return sinir


def satirla(metin, f, genislik, hecele=False):
    """Açgözlü satır doldurma; hecele=True ise sığmayan kelime hece sınırından tireyle bölünür (gazete dizgisi)."""
    olc = ImageDraw.Draw(Image.new("L", (1, 1)))
    tw = lambda t: olc.textlength(t, font=f) / SS  # noqa: E731
    satirlar, s = [], ""
    kelimeler = metin.split()
    while kelimeler:
        k = kelimeler.pop(0)
        t = (s + " " + k).strip()
        if tw(t) <= genislik or not s:
            s = t
            continue
        if hecele:
            for i in reversed(heceler(k)):
                if len(k[:i]) >= 2 and len(k[i:]) >= 2 and tw(s + " " + k[:i] + "-") <= genislik:
                    satirlar.append(s + " " + k[:i] + "-")
                    s = ""
                    kelimeler.insert(0, k[i:])
                    break
            else:
                satirlar.append(s)
                s = k
            continue
        satirlar.append(s)
        s = k
    if s:
        satirlar.append(s)
    return satirlar


def iki_yana_pay(satir, f, genislik):
    """İki yana yaslamak için kelime arası ek boşluk (px)."""
    olc = ImageDraw.Draw(Image.new("L", (1, 1)))
    n = satir.count(" ")
    return max(0.0, (genislik - olc.textlength(satir, font=f) / SS) / n) if n else 0.0


def murekkep2(maske: Image.Image) -> Image.Image:
    """Mürekkep taşması + kırıklar: hafif yayılma, kenarda erozyon gürültüsü, yer yer açık harf."""
    m = maske.filter(ImageFilter.GaussianBlur(0.7))
    a = np.asarray(m).astype(np.float32) / 255
    a = np.clip((a - 0.10) * 1.3, 0, 1)
    a *= np.clip(0.86 + gurultu(*a.shape, 14, 0.06) + gurultu(*a.shape, 34, 0.07) + RNG.normal(0, 0.07, a.shape), 0, 1)
    m = Image.fromarray((a * 255).astype(np.uint8))
    d = ImageDraw.Draw(m)                                      # birkaç küçük mürekkep lekesi
    for _ in range(14):
        x, y, r = RNG.uniform(0, m.width), RNG.uniform(0, m.height), RNG.uniform(0.6, 1.6)
        d.ellipse([x - r, y - r, x + r, y + r], fill=int(RNG.uniform(120, 220)))
    return m


def kupur() -> Image.Image:
    p = kagit(PW, PH)
    ink = Image.new("L", (PW, PH), 0)
    # sütunlar: sol komşu (kesik), orta iki sütunluk madde, sağ komşu (kesik)
    sol1, sag0 = 168, PW - 168
    for x in (sol1 + 12, sag0 - 13):
        ink.paste(255, (x, 26, x + 1, PH - 22))
    ink = ImageChops.lighter(ink, _yerlestir(minik_sutun(sol1 + 18, PH - 50), (-22, 26), (PW, PH)))
    ink = ImageChops.lighter(ink, _yerlestir(minik_sutun(190, PH - 50), (sag0, 26), (PW, PH)))
    x0, x1 = sol1 + 32, sag0 - 32
    gen = x1 - x0
    bas = ImageFont.truetype(str(HEROS_CN), 84 * SS)
    kun = ImageFont.truetype(str(SCHOLA_B), 19 * SS)
    num = ImageFont.truetype(str(SCHOLA_B), 21 * SS)
    soz = ImageFont.truetype(str(SCHOLA_B), 31 * SS)
    olc = ImageDraw.Draw(Image.new("L", (1, 1)))
    while olc.textlength(BASLIK, font=bas) / SS > gen:
        bas = ImageFont.truetype(str(HEROS_CN), int(bas.size) - 2)
    isler = []
    y = 34 + bas.size / SS * 0.86
    bw = olc.textlength(BASLIK, font=bas) / SS
    isler.append((BASLIK, bas, (x0 + (gen - bw) / 2, y), 0))
    y += 16
    ink.paste(255, (int(x0), int(y), int(x1), int(y + 2)))
    y += 34
    for i, s in enumerate(satirla(KUNYE, kun, gen)):
        isler.append((s, kun, (x0, y), 0))
        y += 24
    y += 8
    nw = olc.textlength(NUMARA, font=num) / SS
    isler.append((NUMARA, num, (x0, y), 0))
    y += 44
    satirlar = satirla(SOZ, soz, gen, hecele=True)
    for i, s in enumerate(satirlar):
        pay = 0 if i == len(satirlar) - 1 else iki_yana_pay(s, soz, gen)   # gazete gibi iki yana yaslı
        isler.append((s, soz, (x0, y), pay))
        y += 39
    ink = ImageChops.lighter(ink, kursun_yazi((PW, PH), isler))
    # maddenin devamı: isim listesi (minik, okunmaz) iki sütun
    y0 = int(y - 18)
    kol = (gen - 22) // 2
    for k in range(2):
        ink = ImageChops.lighter(ink, _yerlestir(minik_sutun(kol, PH - y0 - 24, boy=10, satir=12.5),
                                                 (int(x0) + k * (kol + 22), y0), (PW, PH)))
    ink.paste(255, (int(x0) + kol + 10, y0 + 4, int(x0) + kol + 11, PH - 26))
    lay = Image.new("RGB", (PW, PH), (28, 26, 24))
    p = Image.composite(lay, p, murekkep2(ink))
    p = katlama(p, PH * 0.47)
    print("söz satırları:", satirlar, "söz sonu y:", round(y))
    return p


def kenar_alfa(w, h):
    """Dört kenarda makas kesimi, yer yer yıpranmış (küçük lif çentikleri)."""
    pts = []
    n = 90
    def tit():
        return RNG.uniform(-1.0, 1.0) - (RNG.uniform(1.5, 3.2) if RNG.random() < 0.06 else 0)
    for i in range(n + 1):
        pts.append((w * i / n, 6 - tit() + 2.5 * math.sin(i / n * 2.6 + 0.3)))
    for i in range(1, n + 1):
        pts.append((w - 6 + tit() + 2.5 * math.sin(i / n * 3.1), h * i / n))
    for i in range(n, -1, -1):
        pts.append((w * i / n, h - 6 + tit() + 2.5 * math.sin(i / n * 2.4 + 0.8)))
    for i in range(n - 1, 0, -1):
        pts.append((6 - tit() + 2.5 * math.sin(i / n * 2.2 + 1.3), h * i / n))
    m = Image.new("L", (w * 2, h * 2), 0)
    ImageDraw.Draw(m).polygon([(x * 2, y * 2) for x, y in pts], fill=255)
    return m.resize((w, h), Image.LANCZOS)


def main():
    p = kupur()
    alfa = kenar_alfa(PW, PH)
    pa = np.asarray(p).astype(np.float32)
    yy, xx = np.mgrid[0:PH, 0:PW].astype(np.float32)
    isik = 1.03 - 0.04 * (xx / PW) - 0.05 * (yy / PH)
    p = Image.fromarray(np.clip(pa * isik[..., None], 0, 255).astype(np.uint8))
    rgba = p.convert("RGBA")
    rgba.putalpha(alfa)
    rgba = rgba.rotate(0.7, resample=Image.BICUBIC, expand=True)
    z = Image.new("RGB", (W, H), (0, 0, 0))   # kanıt 1 gibi siyah letterbox ile birleşsin
    ox, oy = (W - rgba.width) // 2, 22
    golge = Image.new("L", (W, H), 0)
    golge.paste(rgba.getchannel("A"), (ox + 5, oy + 9))
    golge = golge.filter(ImageFilter.GaussianBlur(9)).point(lambda v: int(v * 0.8))
    z = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), z, golge)
    z.paste(rgba, (ox, oy), rgba)
    z = z.filter(ImageFilter.GaussianBlur(0.3))
    fk = font("LibreFranklin-wght.ttf", 28, 500)
    kayit = Image.new("L", (W * SS, H * SS), 0)
    alt = oy + rgba.height                      # kupürün alt kenarı; kaynak satırı 30 px altında
    ImageDraw.Draw(kayit).text((W / 2 * SS, (alt + 30 + 14) * SS), KAYNAK, font=fk, fill=255, anchor="mm")
    z = Image.composite(Image.new("RGB", (W, H), (170, 170, 170)), z, kayit.resize((W, H), Image.LANCZOS))
    z.save(OUT, quality=93)
    print("->", OUT.relative_to(ROOT), z.size)


if __name__ == "__main__":
    main()
