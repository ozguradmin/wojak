"""eskisehir-cinli-hamam: son kare için telifsiz, gerçekçi 2007 gazete kupürü (kendi tasarımımız).

    python episodes/eskisehir-cinli-hamam/kupur.py      # -> img/kanit_2.jpg (1080x810)

Kaynak madde: Hürriyet, 3 Mart 2007, Eskişehir'de "cinli hamam" vaazı (sayfadaki H1 başlık, tırnaklarıyla)
(https://www.hurriyet.com.tr/gundem/eskisehir-de-cinli-hamam-vaazi-6051638).
- Manşet bu başlığın kendisi (birebir, tırnaklar dahil). Spot, aynı haberde aktarılan Eskişehir Emniyet Müdürlüğü yazılı açıklamasından
  birebir tam bir cümle: "İlimizde bulunan herhangi bir hamamda böyle bir olay olmadığı gibi Emniyet Müdürlüğümüze de
  bu konuda herhangi bir müracaat yapılmamıştır" (aynı cümle AA metninde ve Radikal 3.3.2007 özetinde de var).
- Hürriyet'in logosu, adı taşıyan başlığı, yazı karakteri, rengi ve sayfa düzeni yok; yayının adı yalnız alttaki
  "Kaynak:" satırında. Hamamın ve kişilerin adı kupürde yok.
- Kompozisyon: sayfanın bir bölümünün yakın çekimi (kadrajdan taşar), altta elle yırtılmış kenar. Üstte komşu haberin
  son satırları, solda ve sağda komşu sütunlar, asıl haberde foto + iki sütun. Bütün küçük dizgi rastgele harflerden,
  telefonda okunmayacak kadar küçük ve hafif yumuşak; okunabilir uydurma metin yok.
- Fotoğraf: Derin aldanmaz, "İSTANBUL ÜNİVERSİTESİ HAMAM MÜZESİ.jpg" (Wikimedia Commons, CC0), kırpıldı ve siyah-beyaz
  gazete rasterine çevrildi (temsilî bir hamam cephesi; haberdeki hamam değil).
- Görünüm (son kare çeşitliliği; son 5 bölümde kupür yok): 2000'lerin günlük gazetesi; açık gri-beyaz ince kâğıt,
  dar grotesk siyah manşet, siyah-beyaz raster fotoğraf, yatay katlama izi, -0,7° eğik, altta koyu zemin.
- Fontlar: TeX Gyre Heros Cn Bold ve TeX Gyre Schola (GUST lisansı, dumlupinar-denizaltisi-1953/fonts/), Libre
  Franklin (SIL OFL, karun-hazinesi-bros/fonts/).
"""
from __future__ import annotations

import importlib.util
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
_spec = importlib.util.spec_from_file_location("gk", ROOT / "episodes/gobeklitepe-mezar-tasi/kupur.py")
gk = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gk)
gk.RNG = RNG = np.random.default_rng(2007)

GYRE = ROOT / "episodes" / "dumlupinar-denizaltisi-1953" / "fonts"
FOTO = HERE / "img" / "arka_iu_hamam.jpg"
FOTO_OY = 0.14
OUT = HERE / "img" / "kanit_2.jpg"

W, H = 1080, 810
PW, PH = 1140, 760
SS = 2
TARIH = "3 Mart 2007 Cumartesi"
MANSET = ["Eskişehir’de “cinli", "hamam” vaazı"]
ETIKET = "Emniyet Müdürlüğü:"
SPOT = ("“İlimizde bulunan herhangi bir hamamda böyle bir olay olmadığı gibi Emniyet Müdürlüğümüze de bu konuda "
        "herhangi bir müracaat yapılmamıştır”")
KAYNAK = "Kaynak: Hürriyet, 3 Mart 2007"


def f_gyre(ad, boy):
    return ImageFont.truetype(str(GYRE / ad), int(boy * SS))


def kagit(w, h):
    """2000'ler günlük gazete kâğıdı: açık gri-beyaz, çok hafif sarı, ince gren ve lif."""
    a = np.zeros((h, w, 3), np.float32)
    a[...] = (231, 229, 222)
    a += gk.gurultu(h, w, 160, 3.5)[..., None] * np.array([1.0, 1.0, 1.15])
    a += gk.gurultu(h, w, 18, 2.2)[..., None]
    a += RNG.normal(0, 3.6, (h, w, 1))
    yy, xx = np.mgrid[0:h, 0:w]
    kenar = np.minimum.reduce([xx, w - 1 - xx, yy, h - 1 - yy]).astype(np.float32)
    a -= np.clip(1 - kenar / 26, 0, 1)[..., None] * np.array([6, 7, 12])
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im, "RGBA")
    for _ in range(700):
        x, y = RNG.uniform(0, w), RNG.uniform(0, h)
        L, t = RNG.uniform(3, 12), RNG.uniform(0, math.pi)
        c = (255, 255, 250, int(RNG.uniform(14, 36))) if RNG.random() < 0.5 else (105, 102, 96, int(RNG.uniform(8, 20)))
        d.line([(x, y), (x + L * math.cos(t), y + L * math.sin(t))], fill=c, width=1)
    # yatay katlama izi
    kat = Image.new("L", (w, h), 0)
    y0 = h * 0.47
    ImageDraw.Draw(kat).line([(0, y0), (w, y0 - 5)], fill=50, width=3)
    im = Image.composite(Image.new("RGB", (w, h), (165, 160, 150)), im, kat.filter(ImageFilter.GaussianBlur(2.0)))
    acik = Image.new("L", (w, h), 0)
    ImageDraw.Draw(acik).line([(0, y0 + 3), (w, y0 - 2)], fill=38, width=3)
    return Image.composite(Image.new("RGB", (w, h), (248, 247, 242)), im, acik.filter(ImageFilter.GaussianBlur(2.4)))


def sb_raster(foto: Image.Image, w, h, hucre=3.4) -> np.ndarray:
    g = np.asarray(foto.convert("L").resize((w, h), Image.LANCZOS)).astype(np.float32) / 255
    lo, hi = np.percentile(g, 1), np.percentile(g, 99.5)
    g = np.clip((g - lo) / (hi - lo), 0, 1) ** 0.62
    m = gk.nokta_maskesi((1 - g) * 0.92, hucre, 45)
    return 1 - m * 0.86


def sar(metin, f, gen, d):
    satirlar, s = [], ""
    for k in metin.split():
        t = (s + " " + k).strip()
        if d.textlength(t, font=f) / SS > gen and s:
            satirlar.append(s)
            s = k
        else:
            s = t
    satirlar.append(s)
    return satirlar


def minik(w, h, boy=10.5, satir=13.0, girintili=True):
    """Telefonda okunmayacak kadar küçük, ama manşetle aynı keskinlikte sütun dizgisi (rastgele harf, iki yana yaslı)."""
    f = f_gyre("texgyreschola-regular.otf", boy)
    m = Image.new("L", (w * SS, h * SS), 0)
    d = ImageDraw.Draw(m)
    harf = "aaaabcdeeeefghiiıklmmnnnoörrsştuüvyz"
    y = boy
    girinti = girintili
    while y + 2 < h:
        kel = []
        x = 12 if girinti else 0
        son = RNG.random() < 0.10
        sinir = w * (RNG.uniform(0.3, 0.75) if son else 1.0)
        while True:
            k = "".join(RNG.choice(list(harf), int(RNG.integers(2, 10))))
            tw = d.textlength(k, font=f) / SS
            if x + tw > sinir:
                break
            kel.append((k, tw))
            x += tw + boy * 0.3
        if kel:
            x0 = 12 if girinti else 0
            toplam = sum(t for _, t in kel)
            bos = boy * 0.3 if son or len(kel) < 2 else (w - x0 - toplam) / (len(kel) - 1)
            x = x0
            for k, tw in kel:
                d.text((x * SS, y * SS), k, font=f, fill=255, anchor="ls")
                x += tw + bos
        girinti = son and girintili
        y += satir + (satir * 0.4 if son else 0)
    return m.resize((w, h), Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.75))   # minik harf seçilmesin


def sb_raster2(foto: Image.Image, w, h, hucre=3.1) -> np.ndarray:
    g = np.asarray(foto.convert("L").resize((w, h), Image.LANCZOS)).astype(np.float32) / 255
    lo, hi = np.percentile(g, 2), np.percentile(g, 99)
    g = np.clip((g - lo) / (hi - lo), 0, 1) ** 0.70
    yog = np.clip((1 - g) * 0.95 + gk.gurultu(h, w, 6, 0.04) + RNG.normal(0, 0.03, g.shape), 0, 1)
    m = gk.nokta_maskesi(yog, hucre, 45)
    m = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.45))) / 255.0
    return 1 - m * 0.88


def sayfa() -> Image.Image:
    """Sayfanın bir bölümü (kadrajdan taşar): üstte komşu haberin son satırları, solda ve sağda komşu sütunlar,
    ortada asıl haber (manşet + spot + foto + iki sütun)."""
    p = kagit(PW, PH)
    ink = Image.new("L", (PW, PH), 0)
    d = ImageDraw.Draw(Image.new("L", (1, 1)))
    L0, L1 = 0, 168            # sol komşu sütun
    A0, A1 = 192, 1004         # asıl haber
    R0 = 1028                  # sağ komşu sütun
    # üst: komşu haberin son satırları + kalın ayırıcı
    ink = ImageChops.lighter(ink, gk._yerlestir(minik(A1 - A0, 40, girintili=False), (A0, 6), (PW, PH)))
    ink.paste(255, (A0, 54, A1, 57))
    # sol ve sağ komşu sütunlar (dikey çizgiyle)
    ink = ImageChops.lighter(ink, gk._yerlestir(minik(L1 - L0, PH - 70), (L0, 8), (PW, PH)))
    ink = ImageChops.lighter(ink, gk._yerlestir(minik(PW - R0, PH - 70), (R0, 8), (PW, PH)))
    ink.paste(255, (L1 + 11, 8, L1 + 12, PH - 70))
    ink.paste(255, (A1 + 11, 8, A1 + 12, PH - 70))
    isler = []
    man = f_gyre("texgyreheroscn-bold.otf", 104)
    while max(d.textlength(s, font=man) for s in MANSET) / SS > (A1 - A0):
        man = f_gyre("texgyreheroscn-bold.otf", man.size / SS - 2)
    mb = man.size / SS
    y = 66 + mb * 0.80
    for s in MANSET:
        isler.append((s, man, (A0 - 3, y), "ls"))
        y += mb * 0.90
    y += -mb * 0.90 + 22
    fe = f_gyre("texgyreschola-bold.otf", 29)
    fs = f_gyre("texgyreschola-regular.otf", 29)
    ew = d.textlength(ETIKET + " ", font=fe) / SS
    ilk = sar(SPOT, fs, A1 - A0 - ew, d)[0]
    kalan = SPOT[len(ilk):].strip()
    y += 28
    isler.append((ETIKET, fe, (A0, y), "ls"))
    isler.append((ilk, fs, (A0 + ew, y), "ls"))
    for s in sar(kalan, fs, A1 - A0, d):
        y += 36
        isler.append((s, fs, (A0, y), "ls"))
    y += 20
    ink.paste(255, (A0, int(y), A1, int(y) + 1))
    ink = ImageChops.lighter(ink, gk.yazi_maskesi((PW, PH), isler))
    fy = int(y) + 14
    fw = int((A1 - A0) * 0.58)
    fh = PH - fy - 92
    foto = Image.open(FOTO).convert("RGB")
    hedef = fw / fh
    cw = foto.width
    ch = int(cw / hedef)
    oy = min(int(foto.height * FOTO_OY), foto.height - ch)
    foto = foto.crop((0, oy, cw, oy + ch))
    carp = sb_raster2(foto, fw, fh)
    pa = np.asarray(p).astype(np.float32)
    pa[fy:fy + fh, A0:A0 + fw] *= carp[..., None]
    p = Image.fromarray(np.clip(pa, 0, 255).astype(np.uint8))
    ink = ImageChops.lighter(ink, gk._yerlestir(minik(fw, 30, boy=10, satir=12, girintili=False), (A0, fy + fh + 6),
                                                (PW, PH)))
    sx0 = A0 + fw + 16
    kol = (A1 - sx0 - 14) // 2
    for k in range(2):
        ink = ImageChops.lighter(ink, gk._yerlestir(minik(kol, PH - fy - 70), (sx0 + k * (kol + 14), fy), (PW, PH)))
    ink.paste(255, (sx0 + kol + 6, fy + 2, sx0 + kol + 7, PH - 72))
    # tüm mürekkep aynı keskinlikte: hafif yayılma + doku
    ink = ink.filter(ImageFilter.GaussianBlur(0.55))
    lay = Image.new("RGB", (PW, PH), (22, 22, 24))
    return Image.composite(lay, p, gk.murekkep(ink))


def alt_yirtik(w, h, y0):
    """Üç yan kadraj dışında; ALT kenar elle yırtılmış."""
    k = 520
    yol = np.cumsum(RNG.normal(0, 0.9, k + 1))
    yol = yol - np.linspace(yol[0], yol[-1], k + 1)
    yol = y0 + yol / (np.abs(yol).max() + 1e-6) * 7 + RNG.normal(0, 0.8, k + 1)
    pts = [(-5, -5), (w + 5, -5)]
    for i in range(k, -1, -1):
        dis = -RNG.uniform(1.5, 3.5) if RNG.random() < 0.05 else 0
        pts.append((w * i / k, float(yol[i]) + dis))
    m = Image.new("L", (w * 2, h * 2), 0)
    ImageDraw.Draw(m).polygon([(x * 2, y * 2) for x, y in pts], fill=255)
    return m.resize((w, h), Image.LANCZOS)


def main():
    p = sayfa()
    alfa = alt_yirtik(PW, PH, PH - 14)
    lif = Image.new("L", (PW, PH), 0)
    ImageDraw.Draw(lif).rectangle([0, PH - 30, PW, PH], fill=120)
    lif = ImageChops.multiply(lif.filter(ImageFilter.GaussianBlur(3)), alfa)
    p = Image.composite(Image.new("RGB", (PW, PH), (246, 245, 239)), p, lif.point(lambda v: v // 2))
    pa = np.asarray(p).astype(np.float32)
    yy, xx = np.mgrid[0:PH, 0:PW].astype(np.float32)
    p = Image.fromarray(np.clip(pa * (1.03 - 0.04 * (xx / PW) - 0.05 * (yy / PH))[..., None], 0, 255).astype(np.uint8))
    rgba = p.convert("RGBA")
    rgba.putalpha(alfa)
    rgba = rgba.rotate(-0.7, resample=Image.BICUBIC, expand=True)
    z = np.zeros((H, W, 3), np.float32)
    z[...] = (26, 24, 23)
    z += gk.gurultu(H, W, 50, 2)[..., None] + RNG.normal(0, 1.5, (H, W, 1))
    z = Image.fromarray(np.clip(z, 0, 255).astype(np.uint8))
    ox, oy = (W - rgba.width) // 2, -22
    golge = Image.new("L", (W, H), 0)
    golge.paste(rgba.getchannel("A"), (ox + 4, oy + 10))
    golge = golge.filter(ImageFilter.GaussianBlur(9)).point(lambda v: int(v * 0.7))
    z = Image.composite(Image.new("RGB", (W, H), (6, 6, 6)), z, golge)
    z.paste(rgba, (ox, oy), rgba)
    a = np.asarray(z).astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    a *= (0.99 + 0.04 * (xx / W) - 0.05 * (yy / H))[..., None]
    z = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.3))
    fk = ImageFont.truetype(str(gk.FONTS / "LibreFranklin-wght.ttf"), 26 * SS)
    fk.set_variation_by_axes([600])
    kayit = Image.new("L", (W * SS, H * SS), 0)
    ImageDraw.Draw(kayit).text((W / 2 * SS, (H - 30) * SS), KAYNAK, font=fk, fill=255, anchor="mm")
    z = Image.composite(Image.new("RGB", (W, H), (196, 192, 186)), z, kayit.resize((W, H), Image.LANCZOS))
    z.save(OUT, quality=93)
    print("->", OUT.relative_to(ROOT), z.size)


if __name__ == "__main__":
    main()
