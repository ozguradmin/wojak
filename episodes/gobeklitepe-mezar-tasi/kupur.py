"""gobeklitepe-mezar-tasi: son kare için telifsiz, gerçekçi gazete kupürü (kendi tasarımımız).

    python episodes/gobeklitepe-mezar-tasi/kupur.py            # -> img/kanit_2_kupur.jpg (1080x810; STIL §8 sınırı 816)

Yöntem karun-hazinesi-bros/kupur.py'den (iki hakem 8/8, "gerçek sanılır" 8+); görünüm bilerek farklı (son kare
çeşitliliği): 2018'in renkli hafta sonu eki gibi daha beyaz kâğıt, serif manşet, RENKLİ raster fotoğraf (CMYK
noktaları), alt kenar yırtık, sağa +1,2° eğik, mavi-gri kumaş zemin.
- Başlık kaynakla birebir: Hürriyet Seyahat, 9 Temmuz 2018, "Tarihi değiştiren dünya mirası: Göbeklitepe"
  (https://www.hurriyet.com.tr/seyahat/tarihi-degistiren-dunya-mirasi-gobeklitepe-40888331). Üst başlık + ana manşet
  bu başlığın kendisi; spot satırı aynı haberin spotundan birebir bir cümle: "Stonehenge'den 7 bin, Mısır
  piramitlerinden ise 7 bin 500 yıl daha eski."
- Hürriyet'in logosu, adı taşıyan başlığı, yazı karakteri, rengi ve düzeni yok. Yayın adı yalnız alttaki
  "Kaynak: Hürriyet Seyahat, 9 Temmuz 2018" satırında.
- Fontlar SIL OFL, karun-hazinesi-bros/fonts/ altındaki dosyalar: Source Serif 4 (manşet, spot), Libre Franklin
  (üst başlık, kaynak satırı).
- Okunabilir uydurma haber metni YOK: sütunlar rastgele harf dizilerinden çizilip okunamayacak kadar bulanıklaştırıldı.
- Fotoğraf: Immanuelle, "Gobekli Tepe 4.jpg" (Wikimedia Commons, 2018, CC BY-SA 4.0), renkli gazete rasterine çevrildi.
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FONTS = ROOT / "episodes" / "karun-hazinesi-bros" / "fonts"
FOTO = ROOT / ".cache" / "gobeklitepe-mezar-tasi" / "Gobekli_Tepe_4.jpg"
OUT = HERE / "img" / "kanit_2_kupur.jpg"
RNG = np.random.default_rng(2018)

W, H = 1080, 810
PW, PH = 980, 680
SS = 2
UST = "Tarihi değiştiren dünya mirası:"
MANSET = "Göbeklitepe"
SPOT = ["Stonehenge’den 7 bin, Mısır piramitlerinden", "ise 7 bin 500 yıl daha eski."]
KAYNAK = "Kaynak: Hürriyet Seyahat, 9 Temmuz 2018"


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
    """Daha yeni (2018) gazete kâğıdı: açık kirli beyaz, hafif gri-sarı, gren ve lif; kenarda az sararma."""
    a = np.zeros((h, w, 3), np.float32)
    a[...] = (233, 229, 216)
    a += gurultu(h, w, 140, 4)[..., None] * np.array([1.0, 1.0, 1.25])
    a += gurultu(h, w, 22, 2.5)[..., None]
    a += RNG.normal(0, 4.0, (h, w, 1))
    yy, xx = np.mgrid[0:h, 0:w]
    kenar = np.minimum.reduce([xx, w - 1 - xx, yy, h - 1 - yy]).astype(np.float32)
    a -= np.clip(1 - kenar / 30, 0, 1)[..., None] * np.array([8, 9, 15])
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


def kupur() -> Image.Image:
    p = kagit(PW, PH)
    ink = Image.new("L", (PW, PH), 0)
    # solda kesilmiş komşu sütun + sütun çizgisi; ana haber sağda geniş
    sol_x1 = 118
    ana_x0, ana_x1 = sol_x1 + 26, PW - 34
    ink.paste(255, (sol_x1 + 12, 22, sol_x1 + 13, PH - 18))
    ink = ImageChops.lighter(ink, _yerlestir(okunmaz_satirlar(sol_x1 + 26, PH - 50), (-28, 26), (PW, PH)))
    ust = font("LibreFranklin-wght.ttf", 38, 700)
    man = font("SourceSerif4-opsz-wght.ttf", 160, 900, 60)
    spot = font("SourceSerif4-opsz-wght.ttf", 33, 560, 24)
    olc = ImageDraw.Draw(Image.new("L", (1, 1)))
    while olc.textlength(MANSET, font=man) / SS > (ana_x1 - ana_x0) * 0.99:
        man = font("SourceSerif4-opsz-wght.ttf", int(man.size / SS) - 2, 900, 60)
    mboy = man.size / SS
    y = 30
    isler = [(UST, ust, (ana_x0, y), "la")]
    y += 50
    isler.append((MANSET, man, (ana_x0 - 5, y + mboy * 0.74), "ls"))
    y += mboy * 0.74 + 22
    ink.paste(255, (int(ana_x0), int(y), int(ana_x1), int(y + 2)))
    y += 14
    for i, s in enumerate(SPOT):
        isler.append((s, spot, (ana_x0, y + 30 + i * 40), "ls"))
    y += 30 + 40 * (len(SPOT) - 1) + 20
    ink = ImageChops.lighter(ink, yazi_maskesi((PW, PH), isler))
    # gövde: solda renkli fotoğraf (genişçe), sağda iki okunmaz sütun
    fw = int((ana_x1 - ana_x0) * 0.60)
    fh = PH - int(y) - 58
    foto = Image.open(FOTO).convert("RGB")
    hedef = fw / fh
    cw = 3100
    chh = int(cw / hedef)
    foto = foto.crop((420, 0, 420 + cw, chh))
    carp, _ = renkli_raster(foto, fw, fh)
    p_a = np.asarray(p).astype(np.float32)
    fx, fy = int(ana_x0), int(y)
    p_a[fy:fy + fh, fx:fx + fw] *= carp
    p = Image.fromarray(np.clip(p_a, 0, 255).astype(np.uint8))
    ink = ImageChops.lighter(ink, _yerlestir(okunmaz_satirlar(fw - 30, 28, satir=13, boy=11, bulanik=2.0, paragraf=False),
                                             (fx, fy + fh + 9), (PW, PH)))
    sx0 = fx + fw + 18
    kol = (int(ana_x1) - sx0 - 14) // 2
    for k in range(2):
        ink = ImageChops.lighter(ink, _yerlestir(okunmaz_satirlar(kol, fh + 30), (sx0 + k * (kol + 14), fy + 2), (PW, PH)))
    lay = Image.new("RGB", (PW, PH), (24, 23, 22))
    p = Image.composite(lay, p, murekkep(ink))
    return p


def kenar_alfa(w, h):
    """Üç yanda makas kenarı; ALT kenar elle yırtılmış (düzensiz, lifli)."""
    pts = []
    n = 60
    for i in range(n + 1):                                   # üst: makas
        pts.append((w * i / n, 5 + RNG.uniform(-1.2, 1.2) + 3 * math.sin(i / n * 2.6 + 0.3)))
    for i in range(1, n + 1):                                # sağ: makas
        pts.append((w - 5 + RNG.uniform(-1.2, 1.2) + 3 * math.sin(i / n * 3.1), h * i / n - 10))
    k = 420
    yol = np.cumsum(RNG.normal(0, 0.9, k + 1))
    yol = yol - np.linspace(yol[0], yol[-1], k + 1)
    yol = h - 10 + yol / (np.abs(yol).max() + 1e-6) * 6 + RNG.normal(0, 0.8, k + 1)
    for i in range(k, -1, -1):                               # alt: yırtık
        dis = -RNG.uniform(1.5, 3.5) if RNG.random() < 0.04 else 0
        pts.append((w * i / k, float(yol[i]) + dis))
    for i in range(n - 1, 0, -1):                            # sol: makas
        pts.append((5 + RNG.uniform(-1.2, 1.2) + 3 * math.sin(i / n * 2.2 + 1.3), h * i / n))
    m = Image.new("L", (w * 2, h * 2), 0)
    ImageDraw.Draw(m).polygon([(x * 2, y * 2) for x, y in pts], fill=255)
    return m.resize((w, h), Image.LANCZOS)


def zemin():
    """Mavi-gri kumaş masa örtüsü; ince dokuma deseni, yumuşak ışık."""
    a = np.zeros((H, W, 3), np.float32)
    a[...] = (52, 58, 66)
    a += gurultu(H, W, 80, 4)[..., None]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    a += (np.sin(xx * 1.9) * np.sin(yy * 1.9) * 2.2)[..., None]       # dokuma
    a += RNG.normal(0, 2.2, (H, W, 1))
    a *= (1.12 - 0.38 * (((xx - W * 0.5) / W) ** 2 + ((yy - H * 0.38) / H) ** 2))[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def main():
    p = kupur()
    alfa = kenar_alfa(PW, PH)
    yirtik = Image.new("L", (PW, PH), 0)
    ImageDraw.Draw(yirtik).rectangle([0, PH - 20, PW, PH], fill=120)
    yirtik = ImageChops.multiply(yirtik.filter(ImageFilter.GaussianBlur(3)), alfa)
    p = Image.composite(Image.new("RGB", (PW, PH), (246, 243, 232)), p, yirtik.point(lambda v: v // 2))
    pa = np.asarray(p).astype(np.float32)
    yy, xx = np.mgrid[0:PH, 0:PW].astype(np.float32)
    kivrim = 1.04 - 0.05 * (xx / PW) - 0.06 * (yy / PH) - 0.05 * np.clip((PW * 0.12 - xx) / (PW * 0.12), 0, 1) ** 2
    p = Image.fromarray(np.clip(pa * kivrim[..., None], 0, 255).astype(np.uint8))
    rgba = p.convert("RGBA")
    rgba.putalpha(alfa)
    rgba = rgba.rotate(1.2, resample=Image.BICUBIC, expand=True)
    z = zemin()
    ox, oy = (W - rgba.width) // 2, 26
    golge = Image.new("L", (W, H), 0)
    golge.paste(rgba.getchannel("A"), (ox - 6, oy + 12))
    golge = golge.filter(ImageFilter.GaussianBlur(11)).point(lambda v: int(v * 0.6))
    z = Image.composite(Image.new("RGB", (W, H), (10, 11, 13)), z, golge)
    z.paste(rgba, (ox, oy), rgba)
    a = np.asarray(z).astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    a *= (0.97 + 0.07 * (xx / W) - 0.05 * (yy / H))[..., None]
    z = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.35))
    fk = font("LibreFranklin-wght.ttf", 30, 600)
    kayit = Image.new("L", (W * SS, H * SS), 0)
    ImageDraw.Draw(kayit).text((W / 2 * SS, (H - 38) * SS), KAYNAK, font=fk, fill=255, anchor="mm")
    z = Image.composite(Image.new("RGB", (W, H), (206, 208, 212)), z, kayit.resize((W, H), Image.LANCZOS))
    z.save(OUT, quality=93)
    print("->", OUT.relative_to(ROOT), z.size)


if __name__ == "__main__":
    main()
