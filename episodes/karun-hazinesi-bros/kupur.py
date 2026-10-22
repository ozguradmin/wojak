"""karun-hazinesi-bros: son kare için telifsiz, gerçekçi gazete kupürü (kendi tasarımımız).

    python episodes/karun-hazinesi-bros/kupur.py            # -> img/kanit_2_kupur.jpg (1080x810)

Hesap sahibi (21.10.2026): telifli Milliyet sayfası yok; düz alıntı kartı 1/10 aldı ("telefonda gerçek kupür
sanılmalı"). Ölçüt: Commons'taki gerçek kupür fotoğrafları (ör. "Alas de libertad" – El Comercio – 1996, CC BY 4.0).
- Söz kaynakla birebir: Milliyet 31.05.2006 1. sayfa kutu başlığı "Bakan Koç: Hırsız evin içindeymiş"; üst başlık
  "Bakan Koç:" ve ana manşet "Hırsız evin içindeymiş" bu başlığın kendisi. Spot: "Kültür ve Turizm Bakanı Atilla Koç"
  (unvan Vatan 29.05.2006; Milliyet metninde "Kültür Bakanı Atilla Koç").
- Milliyet'in logosu, adı taşıyan başlığı, yazı karakteri, rengi ve düzeni yok. Yayın adı yalnız kupürün altındaki
  küçük "Kaynak: Milliyet, 31.05.2006" satırında.
- Fontlar fonts/ altında, SIL OFL: Libre Franklin (grotesk manşet), Source Serif 4 (spot ve sütun metni dokusu).
- Okunabilir uydurma haber metni YOK: sütunlardaki "metin", rastgele harf dizilerinden çizilip okunamayacak kadar
  bulanıklaştırılmış satır dokusudur.
- Fotoğraf: img/kanit_1_sahte_bros.jpg (Dosseman, CC BY-SA 4.0) gri tonda gazete rasterine çevrildi.
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
FONTS = HERE / "fonts"
OUT = HERE / "img" / "kanit_2_kupur.jpg"
RNG = np.random.default_rng(2006)

W, H = 1080, 810                       # kanıt görseli (STIL §8: tam genişlik, 537-816 yükseklik)
PW, PH = 1000, 660                     # kupürün kendisi (dönmeden önce)
SS = 2                                 # yazılar 2x çizilip küçültülür


def font(ad, boy, agirlik, opsz=None):
    f = ImageFont.truetype(str(FONTS / ad), boy * SS)
    axes = [agirlik] if opsz is None else [agirlik, opsz]
    if ad.startswith("SourceSerif"):
        axes = [agirlik, opsz or 20]
    f.set_variation_by_axes(axes)
    return f


def gurultu(h, w, olcek, sigma=1.0):
    """Düşük frekanslı leke gürültüsü (0 ortalamalı, ~sigma)."""
    k = RNG.normal(0, 1, (max(2, h // olcek), max(2, w // olcek))).astype(np.float32)
    im = Image.fromarray(((k - k.min()) / (np.ptp(k) + 1e-6) * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
    a = np.asarray(im).astype(np.float32) / 255 - 0.5
    return a / (a.std() + 1e-6) * sigma


def kagit(w, h):
    """Sararmış gazete kâğıdı: ton, büyük lekeler, gren, lifler, kenarda koyulaşma."""
    a = np.zeros((h, w, 3), np.float32)
    a[...] = (222, 211, 184)
    a += gurultu(h, w, 120, 6)[..., None] * np.array([1.0, 1.0, 1.3])
    a += gurultu(h, w, 25, 3)[..., None]
    a += RNG.normal(0, 4.5, (h, w, 1))
    yy, xx = np.mgrid[0:h, 0:w]
    kenar = np.minimum.reduce([xx, w - 1 - xx, yy, h - 1 - yy]).astype(np.float32)
    a -= np.clip(1 - kenar / 40, 0, 1)[..., None] * np.array([14, 16, 24])      # kenar sararması
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im, "RGBA")
    for _ in range(900):                                                        # lifler
        x, y = RNG.uniform(0, w), RNG.uniform(0, h)
        L, t = RNG.uniform(4, 16), RNG.uniform(0, math.pi)
        c = (255, 250, 235, int(RNG.uniform(18, 45))) if RNG.random() < 0.5 else (120, 105, 80, int(RNG.uniform(10, 30)))
        d.line([(x, y), (x + L * math.cos(t), y + L * math.sin(t))], fill=c, width=1)
    # hafif bir leke (eski kâğıt)
    lk = Image.new("L", (w, h), 0)
    ImageDraw.Draw(lk).ellipse([w * 0.70, h * 0.62, w * 0.93, h * 0.95], fill=26)
    lk = lk.filter(ImageFilter.GaussianBlur(40))
    im = Image.composite(Image.new("RGB", (w, h), (190, 165, 120)), im, lk)
    # hafif katlanma izi (açık + koyu çizgi çifti, yumuşak)
    kat = Image.new("L", (w, h), 0)
    kd = ImageDraw.Draw(kat)
    y0, y1 = h * 0.58, h * 0.55
    kd.line([(0, y0), (w, y1)], fill=60, width=3)
    kat = kat.filter(ImageFilter.GaussianBlur(2.2))
    im = Image.composite(Image.new("RGB", (w, h), (150, 135, 105)), im, kat)
    acik = Image.new("L", (w, h), 0)
    ImageDraw.Draw(acik).line([(0, y0 - 3), (w, y1 - 3)], fill=45, width=3)
    im = Image.composite(Image.new("RGB", (w, h), (245, 238, 220)), im, acik.filter(ImageFilter.GaussianBlur(2.5)))
    return im


def okunmaz_satirlar(w, h, satir=16, boy=12, bulanik=2.3, paragraf=True, yogunluk=0.78):
    """Okunamayan sütun metni dokusu: rastgele harf dizileri, küçük serif, sonra bulanıklaştırma. Çıktı: L maske."""
    f = ImageFont.truetype(str(FONTS / "SourceSerif4-opsz-wght.ttf"), boy * SS)
    f.set_variation_by_axes([430, 10])
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


def raster(foto: Image.Image, w, h, hucre=4.2, aci=45):
    """Gri ton gazete rasteri (yuvarlak noktalar). Çıktı: L mürekkep maskesi (255 = mürekkep)."""
    # altın broş mavi kumaşta: düz gri tonda ikisi aynı griye düşüyor; sarı-mavi farkıyla ayır (broş açık, fon koyu)
    c = np.asarray(foto.convert("RGB").resize((w, h), Image.LANCZOS)).astype(np.float32)
    gg = 0.55 * c[..., 0] + 0.45 * c[..., 1] - 0.55 * c[..., 2] + 60
    gg = (gg - np.percentile(gg, 2)) / (np.percentile(gg, 99.5) - np.percentile(gg, 2) + 1e-6) * 235 + 10
    g = Image.fromarray(np.clip(gg, 0, 255).astype(np.uint8))
    g = Image.eval(g, lambda v: int(255 * min(1.0, max(0.0, ((v / 255) ** 0.62 - 0.08) * 1.12))))
    a = np.asarray(g).astype(np.float32) / 255
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    t = math.radians(aci)
    u = (xx * math.cos(t) + yy * math.sin(t)) / hucre
    v = (-xx * math.sin(t) + yy * math.cos(t)) / hucre
    du, dv = u - np.round(u), v - np.round(v)
    r = np.sqrt(du ** 2 + dv ** 2)                     # 0..0.707
    koyu = 1 - a
    nokta = (r < np.sqrt(koyu / math.pi) * 1.05).astype(np.float32)
    m = Image.fromarray((nokta * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))
    return m


def murekkep(maske: Image.Image) -> Image.Image:
    """Baskı izi: hafif dağılma + düzensiz mürekkep yoğunluğu."""
    m = maske.filter(ImageFilter.GaussianBlur(0.7))
    a = np.asarray(m).astype(np.float32) / 255
    a = np.clip((a - 0.12) * 1.25, 0, 1)
    a *= np.clip(0.86 + gurultu(*a.shape, 18, 0.06) + RNG.normal(0, 0.05, a.shape), 0, 1)
    return Image.fromarray((a * 255).astype(np.uint8))


def bas(kagit_im: Image.Image, maske: Image.Image, renk=(28, 26, 24)):
    lay = Image.new("RGB", kagit_im.size, renk)
    return Image.composite(lay, kagit_im, murekkep(maske))


def yazi_maskesi(size, isler):
    """isler: [(metin, font, (x, y), anchor)] 1x koordinat; maske 2x çizilip küçültülür."""
    w, h = size
    m = Image.new("L", (w * SS, h * SS), 0)
    d = ImageDraw.Draw(m)
    for t, f, (x, y), anc in isler:
        d.text((x * SS, y * SS), t, font=f, fill=255, anchor=anc)
    return m.resize((w, h), Image.LANCZOS)


def kupur() -> Image.Image:
    p = kagit(PW, PH)
    ink = Image.new("L", (PW, PH), 0)

    # sütunlar: solda ve sağda kesilmiş komşu sütunlar, aralarında ince sütun çizgileri
    sol_x1, sag_x0 = 96, PW - 96
    ana_x0, ana_x1 = sol_x1 + 22, sag_x0 - 22
    ink.paste(255, (sol_x1 + 10, 18, sol_x1 + 11, PH - 14))
    ink.paste(255, (sag_x0 - 11, 18, sag_x0 - 10, PH - 14))
    ink = ImageChops.lighter(ink, _yerlestir(okunmaz_satirlar(sol_x1 + 30, PH - 40), (-34, 22), (PW, PH)))
    ink = ImageChops.lighter(ink, _yerlestir(okunmaz_satirlar(120, PH - 40), (sag_x0 + 6, 22), (PW, PH)))
    cx = (ana_x0 + ana_x1) / 2
    ust = font("LibreFranklin-wght.ttf", 30, 800)
    man = font("LibreFranklin-wght.ttf", 128, 900)
    spot = font("SourceSerif4-opsz-wght.ttf", 33, 600, 24)
    # manşeti ana sütuna sığdır
    while ImageDraw.Draw(Image.new("L", (1, 1))).textlength("içindeymiş", font=man) / SS > (ana_x1 - ana_x0) * 0.98:
        man = font("LibreFranklin-wght.ttf", int(man.size / SS) - 2, 900)
    mboy = man.size / SS
    y = 34
    isler = [("Bakan Koç:", ust, (ana_x0, y), "la")]
    y += 46
    ink.paste(255, (int(ana_x0), int(y - 8), int(ana_x0 + 150), int(y - 5)))          # üst başlık altı kısa çizgi
    isler += [("Hırsız evin", man, (ana_x0 - 4, y + mboy * 0.80), "ls"),
              ("içindeymiş", man, (ana_x0 - 4, y + mboy * 0.80 + mboy * 0.98), "ls")]
    y = y + mboy * 0.80 + mboy * 0.98 + 30
    isler += [("Kültür ve Turizm Bakanı Atilla Koç", spot, (ana_x0, y + 34), "ls")]
    y += 52
    ink = ImageChops.lighter(ink, yazi_maskesi((PW, PH), isler))
    ink.paste(255, (int(ana_x0), int(y), int(ana_x1), int(y + 2)))                   # spot altı çizgi
    y += 16

    # gövde: solda raster fotoğraf, sağda iki okunmaz sütun
    fw = int((ana_x1 - ana_x0) * 0.40)
    fh = PH - int(y) - 26
    fh = fh - 26                                                                  # alt yazı payı
    foto = Image.open(HERE / "img" / "kanit_1_sahte_bros.jpg").crop((70, 0, 1010, 0))
    hedef = fw / fh
    foto = Image.open(HERE / "img" / "kanit_1_sahte_bros.jpg")
    fw0 = 940
    fh0 = int(fw0 / hedef)
    foto = foto.crop((70, 0, 70 + fw0, min(foto.height, fh0)))
    ink = ImageChops.lighter(ink, _yerlestir(raster(foto, fw, fh), (int(ana_x0), int(y)), (PW, PH)))
    ink.paste(255, (int(ana_x0), int(y), int(ana_x0) + fw, int(y) + 1))
    ink = ImageChops.lighter(ink, _yerlestir(okunmaz_satirlar(fw - 20, 30, satir=13, boy=11, bulanik=2.0, paragraf=False),
                                             (int(ana_x0), int(y) + fh + 8), (PW, PH)))   # foto alt yazısı (okunmaz)
    sx0 = int(ana_x0) + fw + 18
    kol = (int(ana_x1) - sx0 - 16) // 2
    for k in range(2):
        ink = ImageChops.lighter(ink, _yerlestir(okunmaz_satirlar(kol, fh), (sx0 + k * (kol + 16), int(y) + 2), (PW, PH)))
    p = bas(p, ink)
    return p


def _yerlestir(m: Image.Image, xy, size):
    out = Image.new("L", size, 0)
    out.paste(m, xy)
    return out


def kesik_kenar(w, h):
    """Makas kenarı (hafif dalgalı düz) + üst kenar elle yırtılmış (düzensiz). Çıktı: L alfa."""
    pts = []
    n = 60
    k = 400
    yol = np.cumsum(RNG.normal(0, 0.9, k + 1))
    yol = yol - np.linspace(yol[0], yol[-1], k + 1)                     # uçlar aynı yükseklikte
    yol = 8 + yol / (np.abs(yol).max() + 1e-6) * 5 + RNG.normal(0, 0.7, k + 1)
    for i in range(k + 1):                                   # üst: elle yırtılmış (düzensiz)
        dis = RNG.uniform(1.5, 3.5) if RNG.random() < 0.04 else 0
        pts.append((w * i / k, float(yol[i]) + dis))
    for i in range(1, n + 1):                                # sağ: makas
        pts.append((w - 4 + RNG.uniform(-1.3, 1.3) + 3.5 * math.sin(i / n * 3 + 0.4), h * i / n))
    for i in range(n, -1, -1):                               # alt: makas, hafif eğri
        pts.append((w * i / n, h - 5 + RNG.uniform(-1.3, 1.3) - 4 * math.sin(i / n * math.pi * 1.3)))
    for i in range(n - 1, 0, -1):                            # sol: makas
        pts.append((4 + RNG.uniform(-1.3, 1.3) + 3 * math.sin(i / n * 2.5 + 1.0), h * i / n))
    m = Image.new("L", (w * 2, h * 2), 0)
    ImageDraw.Draw(m).polygon([(x * 2, y * 2) for x, y in pts], fill=255)
    return m.resize((w, h), Image.LANCZOS)


def zemin():
    """Kupürün altındaki yüzey: koyu, sıcak gri masa; yukarıdan yumuşak ışık."""
    a = np.zeros((H, W, 3), np.float32)
    a[...] = (54, 49, 44)
    a += gurultu(H, W, 90, 5)[..., None]
    a += RNG.normal(0, 2.5, (H, W, 1))
    lif = gurultu(H, 8, 3, 1.0)                                     # yatay ince lif bantları (ahşap/keçe)
    a += np.asarray(Image.fromarray(((lif - lif.min()) / (np.ptp(lif) + 1e-6) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)).astype(np.float32)[..., None] / 255 * 7 - 3.5
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    a *= (1.12 - 0.35 * (((xx - W * 0.45) / W) ** 2 + ((yy - H * 0.35) / H) ** 2))[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def main():
    p = kupur()
    alfa = kesik_kenar(PW, PH)
    # üst yırtık kenarda kâğıt lifi beyazlığı
    yirtik = Image.new("L", (PW, PH), 0)
    ImageDraw.Draw(yirtik).rectangle([0, 0, PW, 14], fill=110)
    yirtik = ImageChops.multiply(yirtik.filter(ImageFilter.GaussianBlur(3)), alfa)
    p = Image.composite(Image.new("RGB", (PW, PH), (238, 232, 214)), p, yirtik.point(lambda v: v // 2))
    pa = np.asarray(p).astype(np.float32)
    yy, xx = np.mgrid[0:PH, 0:PW].astype(np.float32)
    kivrim = 1.05 - 0.07 * (xx / PW) - 0.06 * (yy / PH) - 0.05 * np.clip((xx - PW * 0.86) / (PW * 0.14), 0, 1) ** 2
    p = Image.fromarray(np.clip(pa * kivrim[..., None], 0, 255).astype(np.uint8))
    rgba = p.convert("RGBA")
    rgba.putalpha(alfa)
    aci = -1.4
    rgba = rgba.rotate(aci, resample=Image.BICUBIC, expand=True)
    z = zemin()
    ox, oy = (W - rgba.width) // 2, 34
    golge = Image.new("L", (W, H), 0)
    golge.paste(rgba.getchannel("A"), (ox + 7, oy + 11))
    golge = golge.filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * 0.62))
    z = Image.composite(Image.new("RGB", (W, H), (12, 10, 9)), z, golge)
    z.paste(rgba, (ox, oy), rgba)
    # fotoğraflanmış hissi: hafif ışık eğimi ve çok hafif yumuşaklık
    a = np.asarray(z).astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    a *= (1.04 - 0.10 * (xx / W) - 0.05 * (yy / H))[..., None]
    z = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.35))
    d = ImageDraw.Draw(z)
    fk = font("LibreFranklin-wght.ttf", 30, 600)
    kayit = Image.new("L", (W * SS, H * SS), 0)
    ImageDraw.Draw(kayit).text((W / 2 * SS, (H - 40) * SS), "Kaynak: Milliyet, 31.05.2006", font=fk, fill=255, anchor="mm")
    kayit = kayit.resize((W, H), Image.LANCZOS)
    z = Image.composite(Image.new("RGB", (W, H), (208, 202, 190)), z, kayit)
    z.save(OUT, quality=93)
    print("->", OUT.relative_to(HERE.parents[1]), z.size)


if __name__ == "__main__":
    main()
