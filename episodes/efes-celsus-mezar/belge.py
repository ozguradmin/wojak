"""efes-celsus-mezar: kanıt için kendi ürettiğimiz gerçekçi dergi sayfası yakın çekimi (canlandırma).

    python episodes/efes-celsus-mezar/belge.py        # -> img/kanit_belleten.jpg (1080x760)

Neden: Celsus'un lahdinin ya da mezar odasının serbest lisanslı fotoğrafı yok (Commons kategorileri, Openverse/Flickr,
Internet Archive'daki ÖJh 8-9 ciltleri tarandı). Türkçe okunur ve belgeli cevap: Türk Tarih Kurumu'nun Belleten dergisinde,
Ekim 1979 (Cilt 43, Sayı 172, s. 809-822; 12 Nisan 1976'da TTK'da verilen konferansın Türkçe metni) geçen cümle:
    "Lahit Mezar içinde bugün Kitaplığın kurucusu yatmaktadır."
Dergi CC BY-NC 4.0 (ticari olmayan) olduğu için sayfanın kendisi kullanılmaz; metin kendi düzenimizle yeniden dizildi.
- Sayfadaki BÜTÜN metin kaynaktaki paragraftan birebir ("Res. 7,8'deki kesit aracılığı ile ..." paragrafı,
  https://belleten.gov.tr/tam-metin/1578/tur); uydurma metin yok. Satır sonları ve heceleme bizim (iki yana yaslı dizgi).
- Belleten'in logosu, başlığı, koşan başlığı, sayfa numarası ve sayfa düzeni taklit edilmedi; yayın adı yalnız alttaki
  "Kaynak:" satırında (hesap sahibinin kupür/kart kuralı: altına "Kaynak: <yayın>, <tarih>").
- Tur 2 görsel hakem: satır satır bulanıklık, modern font, masa şeridi ve vinyet "alıntı kartı" gibi duruyordu. Şimdi: bütün
  satırlar aynı keskinlikte, Times benzeri Liberation Serif (SIL OFL), iki yana yaslı ve heceli dizgi, sol kenar boşluğu
  görünüyor, cevap cümlesinin üstünde elle çekilmiş sarı fosforlu kalem izi, sayfa kadrajı dolduruyor (+0,6° eğik), hafif
  düzensiz ışık; masa ve vinyet yok.
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SANS = HERE.parents[0] / "karun-hazinesi-bros" / "fonts" / "LibreFranklin-wght.ttf"
OUT = HERE / "img" / "kanit_belleten.jpg"
RNG = np.random.default_rng(1979)

W, H = 1080, 760
SS = 2
PARAGRAF = (
    "Res. 7,8'deki kesit aracılığı ile bütün yapıyı tanıyabilir ve ön cephenin büyüklüğünü görebiliriz. Farklı temel "
    "yüksekliğinden meydana gelen iç ve dış alanlardan başka, apsisin altında küçük kapalı bir oda ve içinde bir lahit "
    "bulunmaktadır. Bu lahit çok ince bir işçilikle yapılmış, bugüne dek bulunduğu oda içinde hiçbir zarar görmeden "
    "durmaktadır. Lahit kitaplığın yapıldığı sırada küçük odanın içine konmuştu ve lahit çok zengin bir biçimde "
    "bezenmiştir. Ortada Eros ve yanında girlandlar yeralmaktadır. Bir mezarın bir kitaplık yapısı içinde bulunması "
    "önceleri bizlere ters geldi. Acaba bu mezar bir gizliliği mi saklıyordu? Josef Keil tarafından cepheye ait birçok "
    "yazıtlar toplanmış ve okunmuştu. Bu yazıtlar bize Kitaplık yapısı ile ilgili bilgiler vermiştir. Lahit Mezar "
    "içinde bugün Kitaplığın kurucusu yatmaktadır. Kamuya açık bir yapı içinde bir mezarın bulunması, yalnızca "
    "kurucusunun zenginliğine bağlı değil, özellikle onun politik durumu da, bu işleme izin vermiştir."
)
# Kaynaktaki "Res. 7,8'deki" satırındaki dipnot işareti ([5]) ve dipnotlar alınmadı.
CEVAP = "Lahit Mezar içinde bugün Kitaplığın kurucusu yatmaktadır."
KAYNAK = "Kaynak: Belleten (Türk Tarih Kurumu), Ekim 1979"
UNLU = set("aeıioöuüAEIİOÖUÜ")


def heceler(k: str) -> list[int]:
    """Türkçe hece sınırları (basit kural: ünlüden sonraki tek ünsüz yeni heceye, iki ünsüzün ikincisi yeni heceye)."""
    sinir = []
    i = 0
    while i < len(k):
        if k[i] in UNLU:
            j = i + 1
            while j < len(k) and k[j] not in UNLU and k[j].isalpha():
                j += 1
            if j < len(k) and k[j] in UNLU:
                n = j - i - 1
                if n >= 1:
                    sinir.append(j - 1)
            i = j
        else:
            i += 1
    return [s for s in sinir if 2 <= s <= len(k) - 2]


def diz(d: ImageDraw.ImageDraw, f, metin: str, genislik: float):
    """İki yana yaslı, heceli satırlar: [(kelimeler, son_satir_mi)]."""
    kel = metin.split(" ")
    satirlar, cur = [], []
    bos = d.textlength(" ", font=f)

    def gen(ks):
        return sum(d.textlength(x, font=f) for x in ks) + bos * (len(ks) - 1)

    while kel:
        k = kel.pop(0)
        if gen(cur + [k]) <= genislik:
            cur.append(k)
            continue
        # sığmadı: hecele
        kondu = False
        for s in reversed(heceler(k.rstrip(".,?"))):
            on = k[:s] + "-"
            if gen(cur + [on]) <= genislik and len(cur) >= 3:
                cur.append(on)
                kel.insert(0, k[s:])
                kondu = True
                break
        if not kondu:
            kel.insert(0, k)
        satirlar.append((cur, False))
        cur = []
    satirlar.append((cur, True))
    return satirlar


def gurultu(h, w, olcek, sigma=1.0):
    k = RNG.normal(0, 1, (max(2, h // olcek), max(2, w // olcek))).astype(np.float32)
    im = Image.fromarray(((k - k.min()) / (np.ptp(k) + 1e-6) * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
    a = np.asarray(im).astype(np.float32) / 255 - 0.5
    return a / (a.std() + 1e-6) * sigma


def kagit(w, h):
    a = np.zeros((h, w, 3), np.float32)
    a[...] = (232, 224, 204)                                        # 45 yıllık dergi kâğıdı: fildişi, hafif sararmış
    a += gurultu(h, w, 180, 4)[..., None] * np.array([1.0, 1.0, 1.4])
    a += gurultu(h, w, 24, 1.8)[..., None]
    a += RNG.normal(0, 3.0, (h, w, 1))
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im, "RGBA")
    for _ in range(1100):
        x, y = RNG.uniform(0, w), RNG.uniform(0, h)
        L, t = RNG.uniform(3, 11), RNG.uniform(0, math.pi)
        c = (255, 252, 240, int(RNG.uniform(10, 30))) if RNG.random() < 0.5 else (120, 108, 88, int(RNG.uniform(6, 18)))
        d.line([(x, y), (x + L * math.cos(t), y + L * math.sin(t))], fill=c, width=1)
    for _ in range(10):
        x, y, r = RNG.uniform(0, w), RNG.uniform(0, h), RNG.uniform(2, 6)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(170, 130, 80, int(RNG.uniform(8, 22))))
    return im.filter(ImageFilter.GaussianBlur(0.35))


def murekkep(maske: Image.Image) -> np.ndarray:
    m = maske.filter(ImageFilter.GaussianBlur(0.6))
    a = np.asarray(m).astype(np.float32) / 255
    a = np.clip((a - 0.06) * 1.18, 0, 1)
    a *= np.clip(0.88 + gurultu(*a.shape, 12, 0.05) + RNG.normal(0, 0.045, a.shape), 0, 1)
    return a


def sayfa():
    PW, PH = 1160, 1800
    p = kagit(PW, PH)
    f = ImageFont.truetype(SERIF, 47 * SS)
    olc = ImageDraw.Draw(Image.new("L", (1, 1)))
    x0, sut = 100, 940                                               # sol ve sağ kenar boşluğu kadrajda görünür
    girinti = 46
    satirlar = diz(olc, f, PARAGRAF, (sut - girinti) * SS)
    # ilk satır girintili; öteki satırları tam genişlikte yeniden diz
    ilk = satirlar[0][0]
    kalan = " ".join(" ".join(k) for k, _ in satirlar[1:]).replace("- ", "")
    satirlar = [(ilk, False)] + diz(olc, f, kalan, sut * SS)
    satir_y = 66
    y0 = 52
    maske = Image.new("L", (PW * SS, PH * SS), 0)
    d = ImageDraw.Draw(maske)
    cevap_kutulari = []
    for i, (ks, son) in enumerate(satirlar):
        x = (x0 + (girinti if i == 0 else 0)) * SS
        gen = (sut - (girinti if i == 0 else 0)) * SS
        tw = sum(d.textlength(k, font=f) for k in ks)
        bos = d.textlength(" ", font=f) if son or len(ks) < 2 else (gen - tw) / (len(ks) - 1)
        y = (y0 + i * satir_y) * SS
        for k in ks:
            d.text((x, y), k, font=f, fill=255)
            kw = d.textlength(k, font=f)
            cevap_kutulari.append((i, k, x / SS, y / SS, kw / SS))
            x += kw + bos
    ink = murekkep(maske.resize((PW, PH), Image.LANCZOS))
    # sarı fosforlu kalem: cevap cümlesinin kelimeleri üzerinde, satır başına bir elle çekilmiş şerit
    hedef = CEVAP.split(" ")
    kel = [k for k in cevap_kutulari]
    for bas in range(len(kel)):
        if [k[1] for k in kel[bas:bas + len(hedef)]] == hedef:
            secim = kel[bas:bas + len(hedef)]
            break
    fos = Image.new("L", (PW, PH), 0)
    fd = ImageDraw.Draw(fos)
    for i in sorted({k[0] for k in secim}):
        ks = [k for k in secim if k[0] == i]
        xa, xb = ks[0][2] - 8, ks[-1][2] + ks[-1][4] + 10
        yt = y0 + i * satir_y + 4
        yb = yt + satir_y - 6
        n = 40
        ust = [(xa + (xb - xa) * t / n, yt + RNG.normal(0, 1.4) + 2 * math.sin(t / 6)) for t in range(n + 1)]
        alt = [(xa + (xb - xa) * t / n, yb + RNG.normal(0, 1.4) - 2 * math.sin(t / 7)) for t in range(n, -1, -1)]
        fd.polygon(ust + alt, fill=255)
    fos = fos.filter(ImageFilter.GaussianBlur(1.6))
    fa = np.asarray(fos).astype(np.float32) / 255
    fa *= np.clip(0.78 + gurultu(PH, PW, 8, 0.06), 0, 1)              # kalem izi düzensiz yoğunlukta
    pa = np.asarray(p).astype(np.float32)
    sari = np.array([250, 236, 92], np.float32)
    pa = pa * (1 - fa[..., None]) + (pa * sari / 255) * fa[..., None]   # çarpma karışımı: kâğıt dokusu görünür
    murek = np.array([34, 30, 28], np.float32)
    pa = pa * (1 - ink[..., None] * 0.92) + murek * ink[..., None] * 0.92
    # kaynak satırı: kanalın kupür kuralı (alt kenar boşluğunda, küçük)
    yk = y0 + len(satirlar) * satir_y + 26
    km = Image.new("L", (PW * SS, 60 * SS), 0)
    kf = ImageFont.truetype(str(SANS), 25 * SS)
    kf.set_variation_by_axes([520])
    ImageDraw.Draw(km).text((x0 * SS, 8 * SS), KAYNAK, font=kf, fill=255)
    ka = murekkep(km.resize((PW, 60), Image.LANCZOS))
    if yk + 60 <= PH:
        pa[yk:yk + 60] = pa[yk:yk + 60] * (1 - ka[..., None] * 0.85) + murek * ka[..., None] * 0.85
    cevap_satir = secim[0][0]
    return Image.fromarray(np.clip(pa, 0, 255).astype(np.uint8)), y0 + (cevap_satir - 5) * satir_y + 30, yk


def kompozisyon() -> Image.Image:
    s, ust, yk = sayfa()
    s = s.rotate(0.6, resample=Image.BICUBIC, expand=False, fillcolor=(232, 224, 204))
    # kadraj: cevaptan 5 satır öncesinden paragraf sonuna ve alttaki kaynak satırına kadar; sol kenar boşluğu görünür
    oy = yk + 125 - H                                     # tur 3: kaynak satırı tam kadrajda, altında boşluk
    im = s.crop((40, oy, 40 + W, oy + H))
    # hafif düzensiz ışık (pencere ışığı soldan), çok hafif
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    isik = 1.03 - 0.06 * (xx / W) - 0.03 * (yy / H) + gurultu(H, W, 300, 0.012)
    a = np.asarray(im).astype(np.float32) * isik[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


if __name__ == "__main__":
    im = kompozisyon()
    im.save(OUT, quality=92)
    print(OUT, im.size)
