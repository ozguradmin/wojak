"""uzun/talidomit-turkiye: video.yaml'ın sahne kompozitleri (img/kompozit/) ve küçük resim zeminleri.

Motorun wojak sahnesi 1-3 saydam PNG'yi kenardan kaydırıp sokar; karakter yerine bu "dekor" parçaları da
kullanılabilir (bakis: on). Bu betik o parçaları üretir:

- baskı: arşiv fotoğrafının beyaz kenarlı, gölgeli, hafif eğik "masaya konmuş" baskısı (saydam PNG)
- kâğıt şeritler / kartlar: kontrol listesi satırları, "neredeyse zehirsiz" kartı (+ fosforlu kalem kutusu)
- aynı tuvalde büyüyen dekorlar (yüz değişimiyle "pop"): doz şişesi, dosya yığını
- telefon ekranında viral iddia (marka/platform adı yok)
- küçük resim zeminleri (kendi çizimimiz + Natural Earth; CC BY-SA fotoğraf YOK)
- `pano`: B5.8 panosunun son karesi (KP.2 bölünmüş ekranı için; seslendirmeden sonra çalıştır)

    python uzun/talidomit-turkiye/img/kompozit_uret.py           # hepsi (pano hariç)
    python uzun/talidomit-turkiye/img/kompozit_uret.py pano      # seslendir'den sonra: img/kompozit/pano_son.jpg
    python uzun/talidomit-turkiye/img/kompozit_uret.py kr        # yalnız küçük resim zeminleri

Bütün girdiler bu klasördeki hazır görseller (VARLIKLAR.md); çıktılar img/kompozit/ altında.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = HERE / "kompozit"
CIZ = HERE / "cizim"
sys.path.insert(0, str(ROOT))

FONTS = ROOT / "assets" / "fonts"
INK = (34, 30, 27)
KUTU: dict[str, dict] = {}


def f(ad: str, size: int) -> ImageFont.FreeTypeFont:
    yol = {"mono": FONTS / "LiberationMono-Bold.ttf", "poppins": FONTS / "Poppins-Bold.ttf",
           "anton": FONTS / "Anton-Regular.ttf",
           "serif": Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf")}[ad]
    if not yol.exists():
        yol = FONTS / "Poppins-Bold.ttf"
    return ImageFont.truetype(str(yol), size)


def kaydet(im: Image.Image, ad: str) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / ad
    if p.suffix == ".png":
        im.save(p, optimize=True)
    else:
        im.convert("RGB").save(p, quality=92, optimize=True)
    print(f"kompozit/{ad} {im.size}")
    return p


def golge(lay: Image.Image, r: int = 18, a: float = 0.55, dx: int = 8, dy: int = 14) -> Image.Image:
    pad = r * 3
    out = Image.new("RGBA", (lay.width + 2 * pad, lay.height + 2 * pad), (0, 0, 0, 0))
    g = Image.new("RGBA", out.size, (0, 0, 0, 0))
    m = Image.new("L", out.size, 0)
    m.paste(lay.getchannel("A"), (pad + dx, pad + dy))
    g.putalpha(m.filter(ImageFilter.GaussianBlur(r)).point(lambda v: int(v * a)))
    out.alpha_composite(g)
    out.alpha_composite(lay, (pad, pad))
    bb = out.getchannel("A").point(lambda v: 255 if v > 3 else 0).getbbox()
    return out.crop(bb)


def kagit(w: int, h: int, koyu: bool = False) -> Image.Image:
    src = Image.open(HERE / ("doku_kagit_koyu.jpg" if koyu else "doku_kagit.jpg")).convert("RGB")
    if src.width < w or src.height < h:
        src = src.resize((max(w, src.width), max(h, src.height)))
    x0, y0 = (src.width - w) // 3, (src.height - h) // 3
    return src.crop((x0, y0, x0 + w, y0 + h))


# ------------------------------------------------------------------------------------------------ baskılar
def baski(src: Path, ad: str, en: int = 1000, egim: float = -3.0, kenar: int = 26) -> None:
    im = Image.open(src).convert("RGB")
    h = round(im.height * en / im.width)
    im = im.resize((en, h), Image.LANCZOS)
    pr = Image.new("RGBA", (en + 2 * kenar, h + 2 * kenar), (247, 245, 238, 255))
    pr.paste(im, (kenar, kenar))
    ImageDraw.Draw(pr).rectangle((0, 0, pr.width - 1, pr.height - 1), outline=(214, 210, 200, 255), width=2)
    pr = pr.rotate(egim, resample=Image.BICUBIC, expand=True)
    kaydet(golge(pr), ad)


# ------------------------------------------------------------------------------------------------ kâğıt şeritler
def serit(sol: str, sag: str, ad: str, sag_renk=(168, 30, 28), w: int = 1500, h: int = 170) -> None:
    """Kontrol listesi satırı: kâğıt şerit, solda kutucuk + madde, sağda kırmızı sonuç (daktilo)."""
    im = kagit(w, h).convert("RGBA")
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w - 1, h - 1), outline=(150, 132, 108, 255), width=3)
    fm = f("mono", 56)
    d.rectangle((48, h // 2 - 26, 100, h // 2 + 26), outline=INK + (255,), width=6)
    d.line((54, h // 2 - 20, 94, h // 2 + 20), fill=sag_renk + (255,), width=8)
    d.line((54, h // 2 + 20, 94, h // 2 - 20), fill=sag_renk + (255,), width=8)
    d.text((136, h // 2), sol, font=fm, fill=INK + (255,), anchor="lm")
    d.text((w - 50, h // 2), sag, font=fm, fill=sag_renk + (255,), anchor="rm")
    kaydet(golge(im.rotate(-0.8, resample=Image.BICUBIC, expand=True), 12, 0.5, 4, 8), ad)


def kart_neredeyse() -> None:
    """B1.4: firmanın çıkardığı sonuç, tırnak içinde; 'neredeyse zehirsiz' fosforlu kalem kutusu."""
    W, H = 1800, 1000
    im = kagit(W, H)
    d = ImageDraw.Draw(im)
    fs = f("serif", 44)
    d.text((140, 210), "Hayvan deneylerinden çıkarılan sonuç (firma):", font=fs, fill=(110, 98, 84))
    fb = f("mono", 104)
    satir1 = "„Bu ilaç"
    satir2 = "neredeyse zehirsiz.“"
    d.text((140, 380), satir1, font=fb, fill=INK)
    d.text((140, 540), satir2, font=fb, fill=INK)
    bx = d.textbbox((140, 540), "neredeyse zehirsiz.", font=fb)
    fk = f("serif", 34)
    d.text((140, 800), "Kendi çizimimiz · firma iddiasının özeti, belge kopyası değil", font=fk, fill=(140, 128, 112))
    kaydet(im, "kart_neredeyse_zehirsiz.jpg")
    KUTU["kart_neredeyse_zehirsiz.jpg"] = {"neredeyse zehirsiz": [bx[0] - 8, bx[1] - 14, bx[2] + 8, bx[3] + 10]}


def kart(metin: list[tuple[str, str, int, tuple]], ad: str, w: int, h: int, egim: float = 1.5) -> None:
    """Küçük kâğıt not kartı (dekor): [(metin, font, boyut, renk)] ortalı satırlar."""
    im = kagit(w, h).convert("RGBA")
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w - 1, h - 1), outline=(150, 132, 108, 255), width=3)
    toplam = sum(s + 18 for _, _, s, _ in metin) - 18
    y = (h - toplam) / 2
    for m, fa, s, r in metin:
        d.text((w / 2, y + s / 2), m, font=f(fa, s), fill=tuple(r) + (255,), anchor="mm")
        y += s + 18
    kaydet(golge(im.rotate(egim, resample=Image.BICUBIC, expand=True), 12, 0.5, 4, 8), ad)


# ------------------------------------------------------------------------------------------------ büyüyen dekorlar
def ayni_tuval(ims: list[Image.Image], adlar: list[str], hizala: str = "alt") -> None:
    W = max(i.width for i in ims)
    H = max(i.height for i in ims)
    for im, ad in zip(ims, adlar):
        t = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        y = H - im.height if hizala == "alt" else (H - im.height) // 2
        t.alpha_composite(im, ((W - im.width) // 2, y))
        kaydet(t, ad)


def doz_siseleri() -> None:
    s = Image.open(CIZ / "doz_sisesi.png").convert("RGBA")
    ims = [s.resize((round(s.width * k), round(s.height * k)), Image.LANCZOS) for k in (0.55, 0.78, 1.0)]
    ayni_tuval(ims, ["doz_1.png", "doz_2.png", "doz_3.png"])


def dosya_yiginlari() -> None:
    d = Image.open(CIZ / "dosya_kapali.png").convert("RGBA")
    d = d.resize((d.width // 2, d.height // 2), Image.LANCZOS)
    adim = 60
    ims = []
    for n in (1, 2, 3, 4):
        t = Image.new("RGBA", (d.width + 40, d.height + adim * 3), (0, 0, 0, 0))
        for i in range(n):
            x = 20 + (12 if i % 2 else -8) + 8
            t.alpha_composite(d, (max(0, x), t.height - d.height - i * adim))
        ims.append(t)
    ayni_tuval(ims, ["yigin_1.png", "yigin_2.png", "yigin_3.png", "yigin_4.png"])


def dosya_kagit() -> None:
    """Pano 'foto' kartı için saydam dosya çizimini kâğıt rengine düzleştirir (RGB)."""
    for ad, cikti in (("dosya_bos_acik.png", "dosya_bos_kagit.jpg"), ("bulten_karti_yedek.png", "bulten_kagit.jpg")):
        im = Image.open(CIZ / ad).convert("RGBA")
        t = Image.new("RGBA", (im.width + 80, im.height + 80), (238, 230, 210, 255))
        t.alpha_composite(im, (40, 40))
        kaydet(t.convert("RGB"), cikti)


# ------------------------------------------------------------------------------------------------ telefon: viral iddia
def telefon_iddia() -> None:
    fr = Image.open(CIZ / "telefon_cerceve.png").convert("RGBA")
    W, H = fr.size
    ekran = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    x0, y0, x1, y1 = 70, 150, 630, 1290
    d = ImageDraw.Draw(ekran)
    d.rectangle((x0, y0, x1, y1), fill=(24, 26, 32, 255))
    # gönderi kartı (genel; platform/marka yok)
    d.rounded_rectangle((x0 + 28, y0 + 120, x1 - 28, y0 + 860), radius=26, fill=(38, 41, 50, 255))
    d.ellipse((x0 + 58, y0 + 150, x0 + 138, y0 + 230), fill=(92, 98, 112, 255))
    d.rounded_rectangle((x0 + 160, y0 + 162, x0 + 380, y0 + 186), radius=10, fill=(120, 126, 140, 255))
    d.rounded_rectangle((x0 + 160, y0 + 200, x0 + 300, y0 + 218), radius=8, fill=(80, 86, 98, 255))
    fb = f("poppins", 64)
    satirlar = ["Etkilenmeyen", "tek iki ülke:", "Türkiye", "ve ABD!"]
    y = y0 + 270
    for s in satirlar:
        d.text((x0 + 58, y), s, font=fb, fill=(244, 244, 246, 255))
        y += 92
    for i in range(3):   # beğeni / paylaşım simgeleri yerine sade çubuklar
        cx = x0 + 90 + i * 150
        d.rounded_rectangle((cx - 40, y0 + 780, cx + 40, y0 + 810), radius=12, fill=(70, 76, 90, 255))
    d.rounded_rectangle((x0 + 28, y0 + 900, x1 - 28, y0 + 1060), radius=22, fill=(34, 37, 45, 255))
    d.rounded_rectangle((x0 + 58, y0 + 940, x1 - 120, y0 + 966), radius=10, fill=(70, 76, 90, 255))
    d.rounded_rectangle((x0 + 58, y0 + 990, x1 - 200, y0 + 1014), radius=10, fill=(60, 66, 78, 255))
    ekran.alpha_composite(fr)
    kaydet(golge(ekran, 22, 0.6, 0, 16), "telefon_iddia.png")


# ------------------------------------------------------------------------------------------------ küçük resim zeminleri
def kirmizi_blok(metin: str, boy: int = 120, egim: float = -6.0) -> Image.Image:
    """Küçük resim etiketi: düz kırmızı blok + beyaz Anton yazı + beyaz kenar + gölge (3. hakem turu: kırmızı
    damga yeşil üstünde 168 px'te okunmuyordu; blok her zeminde okunur)."""
    fn = f("anton", boy)
    pad_x, pad_y = int(boy * 0.32), int(boy * 0.12)
    w = int(fn.getlength(metin)) + 2 * pad_x
    bb = fn.getbbox(metin)
    h = bb[3] - bb[1] + 2 * pad_y
    k = max(6, boy // 16)
    lay = Image.new("RGBA", (w + 2 * k, h + 2 * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle((0, 0, w + 2 * k - 1, h + 2 * k - 1), radius=boy // 7, fill=(255, 255, 255, 255))
    d.rounded_rectangle((k, k, w + k - 1, h + k - 1), radius=boy // 9, fill=(214, 28, 32, 255))
    d.text((k + pad_x, k + pad_y - bb[1]), metin, font=fn, fill=(255, 255, 255, 255))
    lay = lay.rotate(egim, resample=Image.BICUBIC, expand=True)
    return golge(lay, 12, 0.6, 6, 10)


def turkiye_silueti(en: int) -> Image.Image:
    """Yeşil Türkiye silueti (Natural Earth, kamu malı) + 10 px beyaz kontur, saydam PNG."""
    from wojak.uzun.harita import HaritaCizer
    hc = HaritaCizer("turkiye", 1600, 900, "50m")
    m, bb = hc.maske("TUR")
    m = m.crop(m.getbbox())
    h = round(m.height * en / m.width)
    m = m.resize((en, h), Image.LANCZOS)
    pad = 16
    a = Image.new("L", (en + 2 * pad, h + 2 * pad), 0)
    a.paste(m, (pad, pad))
    kont = a.filter(ImageFilter.MaxFilter(21))
    out = Image.new("RGBA", a.size, (0, 0, 0, 0))
    out.paste((255, 255, 255, 255), (0, 0), kont)
    out.paste((60, 210, 112, 255), (0, 0), a)
    return golge(out, 14, 0.55, 6, 10)


def harita_zemini() -> None:
    """K2: koyu Akdeniz haritası; satıldığı belgeli ülkeler kırmızı + hap simgeleri; Türkiye genişliğin ~%35'i, parlak
    yeşil, 8 px beyaz kontur, üstünde çapraz kırmızı "RUHSAT YOK" damgası. Sol taraf yazıya boş (2. hakem turu:
    eski K2'de Türkiye küçük, yazıya değiyor, damga yoktu). Natural Earth (kamu malı) + kendi çizimimiz."""
    from wojak.uzun.harita import HaritaCizer
    from wojak.uzun.ust import damga_sprite
    W, H = 1920, 1080
    # 3. tur: Türkiye biraz sola (sağ altta gergin temsilciye yer), damga yerine kırmızı blok
    bolge = {"merkez": (32.0, 39.0), "sinir": (2.0, 24.0, 64.0, 52.0), "proj": "laea"}
    # küçük resim koyu kalır (4. turda videodaki haritalar aydınlatıldı; küçük resmin kontrastı için eski koyu palet)
    hc = HaritaCizer(bolge, W, H, "50m", renk={"deniz": (13, 20, 30), "deniz2": (22, 34, 48), "kara": (60, 66, 76),
                                               "sinir": (28, 33, 41), "izgara": (26, 38, 52)})
    im = hc.taban().convert("RGBA")
    kirmizi = (205, 62, 52)
    # 4. tur (izlenme hakemi S8): Almanya, Avusturya ve İtalya'daki beyaz hap simgeleri 168x94'te bozuk piksel gibi
    # okunuyordu: kaldırıldı (kırmızı ülkeler yeterli)
    for kod in ("DEU", "AUT", "CHE", "BEL", "NLD", "LUX", "ITA", "GBR"):
        mk = hc.maske(kod)
        if not mk:
            continue
        m, bb = mk
        im.paste(kirmizi + (255,), bb[:2], m)
    m, bb = hc.maske("TUR")
    kont = Image.new("L", (W, H), 0)
    kont.paste(m, bb[:2])
    kalin = kont.filter(ImageFilter.MaxFilter(17))          # ~8 px beyaz kontur
    im.paste((255, 255, 255, 255), (0, 0), kalin)
    im.paste((60, 230, 120, 255), (0, 0), kont)
    print(f"Türkiye: x {bb[0] / W:.2f}-{(bb[0] + m.width) / W:.2f} ({m.width / W:.0%} genişlik)")
    dm = kirmizi_blok("RUHSAT YOK", 104, 6.0)
    cx, cy = bb[0] + m.width * 0.48, bb[1] + m.height * 0.5
    im.alpha_composite(dm, (int(cx - dm.width / 2), int(cy - dm.height / 2)))
    kaydet(im.convert("RGB"), "kr_harita.jpg")


def zehirsiz_zemini() -> None:
    """K1: kırmızıdan siyaha radyal zemin (koyu kâğıt dokusuyla), solda yeşil Türkiye silueti + kırmızı "HAYIR" bloğu
    (kendi çizimimiz; Natural Earth). 6. tur (izlenme hakemi N3): dört öğe yarışıyordu ve çamur kahve zemin açık/koyu
    akışta kayboluyordu: gebelik piktogramı çıktı, Türkiye büyüdü, zemin doygun kırmızı-siyah."""
    W, H = 1920, 1080
    doku = np.asarray(kagit(W, H, koyu=True).convert("L"), np.float32)
    doku = 0.82 + 0.36 * (doku - doku.mean()) / max(1.0, doku.std() * 4)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.clip(np.sqrt(((xx - W * 0.58) / (W * 0.62)) ** 2 + ((yy - H * 0.42) / (H * 0.78)) ** 2), 0, 1)
    ic, dis = np.array([188, 26, 30], np.float32), np.array([16, 3, 5], np.float32)
    k = (d ** 1.35)[..., None]
    rgb = (ic * (1 - k) + dis * k) * doku[..., None]
    im = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).convert("RGBA")
    tr = turkiye_silueti(860)
    x0, y0 = 10, H - tr.height - 40
    im.alpha_composite(tr, (x0, y0))
    hb = kirmizi_blok("HAYIR", 150, -7.0)
    im.alpha_composite(hb, (x0 + tr.width // 2 - hb.width // 2 - 30, y0 + tr.height // 2 - hb.height // 2))
    kaydet(im.convert("RGB"), "kr_zehirsiz.jpg")


def dosya_zemini() -> None:
    """K3: koyu masa (kendi dokumuz); açık ve bomboş dosya + etiketli dosya kapağı + büyüteç + kırmızı damga."""
    from wojak.uzun.ust import damga_sprite
    W, H = 1920, 1080
    im = kagit(W, H, koyu=True).convert("RGBA")
    ac = Image.open(CIZ / "dosya_bos_acik.png").convert("RGBA")
    ac = ac.resize((1250, round(ac.height * 1250 / ac.width)), Image.LANCZOS)
    im.alpha_composite(golge(ac, 22, 0.6, 10, 20), (520, 250))
    bu = Image.open(CIZ / "buyutec.png").convert("RGBA")
    bu = bu.resize((470, round(bu.height * 470 / bu.width)), Image.LANCZOS)
    im.alpha_composite(golge(bu, 16, 0.5, 8, 14), (700, 300))
    et = Image.open(CIZ / "dosya_k3_etiketli.png").convert("RGBA")
    et = et.resize((820, round(et.height * 820 / et.width)), Image.LANCZOS).rotate(-5, resample=Image.BICUBIC,
                                                                                   expand=True)
    im.alpha_composite(golge(et, 18, 0.6, 8, 16), (1060, 600))
    # 3. hakem turu: karakterin altında kesik kalan "…AT VERİLMEDİ" damgası kaldırıldı
    kaydet(im.convert("RGB"), "kr_dosya.jpg")


# ------------------------------------------------------------------------------------------------ pano son karesi
def pano_son() -> None:
    """KP.2'nin sağ paneli: B5.8 panosunun son karesi (filigransız; köşe göstergesi dahil)."""
    from wojak.uzun import render, spec, tts, zaman
    v = spec.yukle(HERE.parent)
    tts.sureleri_yukle(v)
    z = zaman.hesapla(v, tahmin=True)
    # 3. tur: pano iki çekime bölündü (B5.8a/b): tam pano SONUNCUSU
    i = max(k for k, s in enumerate(z.sahneler) if s.tip == "pano" and s.p.get("baslik") == "Elimizdekiler")
    im = render.son_kare(v, z, i, 1920, 1080)
    kaydet(im, "pano_son.jpg")


def hepsi() -> None:
    baski(HERE / "foto_contergan_forte.jpg", "baski_forte.png", en=1100, egim=4.0)
    baski(HERE / "foto_kelsey_masa.jpg", "baski_kelsey.png", en=760, egim=-3.0)
    baski(HERE / "foto_kelsey_kennedy_1962.jpg", "baski_kelsey_kennedy.png", en=760, egim=2.5)
    serit("Kandaki ilaç düzeyi", "ÖLÇÜLMEDİ", "serit_kan_duzeyi.png")
    serit("Gebe hayvan deneyi", "", "serit_gebe_deney.png")      # sonuç sahnede damgayla basılır
    kart_neredeyse()
    kart([("1262 sayılı Kanun", "mono", 60, INK), ("1928", "anton", 110, (168, 30, 28)),
          ("Bakanlık ruhsatı olmadan", "serif", 40, (90, 80, 70)), ("ilaç satılamaz", "serif", 40, (90, 80, 70))],
         "kart_1262.png", 720, 470, egim=-2.0)
    doz_siseleri()
    dosya_yiginlari()
    dosya_kagit()
    telefon_iddia()
    harita_zemini()
    zehirsiz_zemini()
    dosya_zemini()
    (OUT / "kutular.json").write_text(json.dumps(KUTU, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "pano":
        pano_son()
    elif len(sys.argv) > 1 and sys.argv[1] == "kr":      # yalnız küçük resim zeminleri
        harita_zemini()
        zehirsiz_zemini()
        dosya_zemini()
    else:
        hepsi()
