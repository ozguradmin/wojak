"""Üst katman yerleşimi ve çakışma denetimi (10. tur).

Animasyon hakemi (9. tur, M1/M3/S5-S7): iki isim etiketi 4-5 sn yüzün (çene, ağız köşesi) üstündeydi, Kennedy
etiketi çıkarken "BU ÖDÜLÜ ALAN 2. KADIN" üstüne çizildi, iki damga köşeden birbirine değdi. Hepsi video.yaml'dan
düzeltilebilirdi ama motor uyarmadı. Bu modül:

- karakter görselinin alfa kutusunu ve yüz bölgesini (baştan boyuna kadar) bulur;
- `isim` etiketi için yer seçer (sahneler.UstKatman): kutusu her karakterin alfa kutusundan en az `BOSLUK` (40 px,
  1080p) uzak; sığmazsa satır kırar, küçülür ya da boş tarafa geçer;
- `kontrol` için bütün üst katmanları (isim, kelime, damga, daktilo etiketi, köşe göstergesi) sahne boyunca 0,1 sn
  arayla örnekler; bir yüze ya da başka bir üst katmana binenleri zaman aralığıyla bildirir (`denetle`).
"""

from __future__ import annotations

import math

import numpy as np
from PIL import Image

BOSLUK = 40.0          # px (1080p): isim etiketi ile karakterin alfa kutusu arası en az
BOSLUK_NESNE = 8.0     # px: isim etiketi ile dekor/nesne (`canli: false`: dosya, kapı, şişe) arası
BOSLUK_UST = 20.0      # px: isim etiketi ile başka bir üst katman arası
YUZ_DERIN = 8.0        # px: yüze bu kadardan derin giren üst katman uyarılır
UST_DERIN = -8.0       # px: iki üst katman arası bundan azsa (değme, köşeden binme dahil) uyarılır; eksi = boşluk
ADIM = 0.1             # sn: denetim örnek aralığı
EN_AZ_SURE = 0.15      # sn: bundan kısa çakışma (geçiş anı) bildirilmez


# ---------------------------------------------------------------- görsel kutuları

def alfa_kutusu(im: Image.Image, esik: int = 40) -> tuple[int, int, int, int] | None:
    """Opak piksellerin kutusu (görsel pikseli)."""
    return im.getchannel("A").point(lambda v: 255 if v > esik else 0).getbbox()


def yuz_kutusu(im: Image.Image, esik: int = 40) -> tuple[int, int, int, int] | None:
    """Baş/yüz bölgesi (görsel pikseli): alfa kutusunun üstünden boyuna kadar.

    Kit ve hazır wojak görselleri göğüsten kesik büst: satır genişliği başta büyür, boyunda daralır, omuzlarda
    yeniden açılır. Boyun = kutu boyunun %40-90'ı arasındaki en dar satır (altında genişlik en az %15 artıyorsa);
    yoksa (tam boy, nesne) üst %62. Yatayda baş satırlarının birleşimi."""
    a = np.asarray(im.getchannel("A")) > esik
    rows = np.where(a.any(axis=1))[0]
    if not len(rows):
        return None
    y0, y1 = int(rows[0]), int(rows[-1]) + 1
    h = y1 - y0
    sol = np.full(h, -1)
    sag = np.full(h, -1)
    for i, y in enumerate(range(y0, y1)):
        xs = np.where(a[y])[0]
        if len(xs):
            sol[i], sag[i] = xs[0], xs[-1] + 1
    gen = np.where(sol >= 0, sag - sol, 0).astype(np.float32)
    k = max(1, int(0.02 * h))
    gen_s = np.convolve(gen, np.ones(k) / k, mode="same")
    lo, hi = int(0.40 * h), int(0.90 * h)
    boyun = int(0.62 * h)
    if hi - lo > 4:
        j = lo + int(np.argmin(gen_s[lo:hi]))
        if gen_s[j:].max() > 1.15 * max(gen_s[j], 1.0):
            boyun = j
    bas = slice(0, max(1, boyun))
    gecerli = sol[bas] >= 0
    if not gecerli.any():
        return None
    return int(sol[bas][gecerli].min()), y0, int(sag[bas][gecerli].max()), y0 + boyun


# ---------------------------------------------------------------- geometri

def dikdortgen(x0: float, y0: float, x1: float, y1: float) -> list[tuple[float, float]]:
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def donuk_dikdortgen(cx: float, cy: float, w: float, h: float, aci: float) -> list[tuple[float, float]]:
    """cizim.afin ile aynı dönüş (aci derece, saat yönünün tersi +, ekranda y aşağı)."""
    th = math.radians(aci)
    c, s = math.cos(th), math.sin(th)
    out = []
    for dx, dy in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)):
        out.append((c * dx + s * dy + cx, -s * dx + c * dy + cy))
    return out


def derinlik(p: list, q: list) -> float:
    """İki dışbükey çokgenin iç içe geçme derinliği (ayırıcı eksen teoremi): ayrıksa <= 0, değiyorsa ~0,
    iç içe geçtikçe büyür (px)."""
    en_az = float("inf")
    for poli in (p, q):
        n = len(poli)
        for i in range(n):
            x0, y0 = poli[i]
            x1, y1 = poli[(i + 1) % n]
            ex, ey = y1 - y0, -(x1 - x0)
            L = math.hypot(ex, ey)
            if L < 1e-9:
                continue
            ex, ey = ex / L, ey / L
            pa = [x * ex + y * ey for x, y in p]
            qa = [x * ex + y * ey for x, y in q]
            ort = min(max(pa), max(qa)) - max(min(pa), min(qa))
            # 12. tur: ilk ayırıcı eksende dönülmüyor: eğik iki kart başka bir eksende 3 px "değiyor" görünüp gerçekte
            # 260 px uzaktaydı (B5.8b 'g' ile 'y'); ayrıklıkta en büyük boşluk (en küçük örtüşme) asıl uzaklıktır
            en_az = min(en_az, ort)
    return en_az


def kutu_kesisim(a: tuple, b: tuple) -> float:
    """İki eksen hizalı kutunun kesişim alanı."""
    w = min(a[2], b[2]) - max(a[0], b[0])
    h = min(a[3], b[3]) - max(a[1], b[1])
    return w * h if (w > 0 and h > 0) else 0.0


def kutu_icin(poli: list) -> tuple[float, float, float, float]:
    xs, ys = [x for x, _ in poli], [y for _, y in poli]
    return min(xs), min(ys), max(xs), max(ys)


# ---------------------------------------------------------------- isim etiketi metni

def ikiye_bol(metin: str | None) -> str | None:
    """Uzun satırı ortaya en yakın yerden ikiye böler: önce ' · ' / ', ' ayraçlarından, yoksa boşluktan."""
    if not metin or "\n" in metin:
        return None
    for ayrac in (" · ", ", ", " – ", " - "):
        if ayrac in metin:
            parcalar = metin.split(ayrac)
            en_iyi = None
            for i in range(1, len(parcalar)):
                a, b = ayrac.join(parcalar[:i]), ayrac.join(parcalar[i:])
                fark = abs(len(a) - len(b))
                if en_iyi is None or fark < en_iyi[0]:
                    en_iyi = (fark, a + ("," if ayrac == ", " else "") + "\n" + b)
            return en_iyi[1]
    kel = metin.split(" ")
    if len(kel) < 2:
        return None
    en_iyi = None
    for i in range(1, len(kel)):
        a, b = " ".join(kel[:i]), " ".join(kel[i:])
        fark = abs(len(a) - len(b))
        if en_iyi is None or fark < en_iyi[0]:
            en_iyi = (fark, a + "\n" + b)
    return en_iyi[1]


# ---------------------------------------------------------------- denetim (kontrol)

def denetle(v, z, W: int = 960) -> list[str]:
    """Bütün sahnelerde üst katman çakışmaları (kontrol uyarısı). Sahne çizicisi W genişliğinde kurulur (yalnız
    yerleşim; kare çizilmez); ölçüler 1080p'ye göre bildirilir."""
    from . import zaman as Zm
    from .sahneler import Baglam, cizici
    H = W * 9 // 16
    c = Baglam(v, W, H, z.fps)
    S = c.S
    out = []
    for i, s in enumerate(z.sahneler):
        if s.tip == "pano":
            out += _pano_denetle(s, c, z)
        if not _ust_var(s):
            continue
        try:
            cz = cizici(s, c)
        except Exception as e:   # noqa: BLE001 — denetim çizimi durdurmasın
            out.append(f"{Zm.zaman_str(z.sahne_basi(s))}: üst katman denetimi kurulamadı ({type(e).__name__}: {e})")
            continue
        uk = cz.katman
        b0 = z.sahne_basi(s)
        for it in uk.isimler:
            if it["ihlal"] > 0:
                out.append(f"{Zm.zaman_str(b0 + it['t0'])}: isim etiketi '{it['ad']}' hiçbir yerde karakterlerden "
                           f"{BOSLUK:.0f} px uzak durmuyor (en az çakışan yer seçildi) — ad/unvanı kısalt ya da "
                           f"karakteri kaydır")
            elif it.get("olcek", 1.0) < 1.0:
                out.append(f"{Zm.zaman_str(b0 + it['t0'])}: isim etiketi '{it['ad']}' karakterlerden uzak dursun diye "
                           f"%{100 - round(100 * it['olcek'])} küçültüldü (telefonda küçük okunur) — ad/unvanı kısalt")
        cak: dict = {}
        n = max(1, int(s.sure_hesap / ADIM))
        for j in range(n + 1):
            t = min(j * ADIM, s.sure_hesap - 1e-3)
            ustler = uk.kutular(t)
            yuzler = uk.yuz_kutulari(t)
            for a_ad, a_p in ustler:
                for k_ad, kb in yuzler:
                    d = derinlik(a_p, dikdortgen(*kb))
                    if d >= YUZ_DERIN * S:
                        cak.setdefault((a_ad, k_ad, "yüz"), []).append(t)
            for x in range(len(ustler)):
                for y in range(x + 1, len(ustler)):
                    (a_ad, a_p), (b_ad, b_p) = ustler[x], ustler[y]
                    if derinlik(a_p, b_p) > UST_DERIN * S:
                        cak.setdefault((a_ad, b_ad, "üst"), []).append(t)
        for (a_ad, b_ad, tur), ts in sorted(cak.items(), key=lambda q: q[1][0]):
            for t0, t1 in _araliklar(ts):
                if t1 - t0 + ADIM < EN_AZ_SURE:
                    continue
                if tur == "yüz":
                    ne = f"{a_ad} {b_ad} karakterinin yüzüne biniyor"
                else:
                    ne = f"{a_ad} ile {b_ad} üst üste biniyor ya da birbirine değiyor"
                out.append(f"{Zm.zaman_str(b0 + t0)}-{Zm.zaman_str(b0 + t1 + ADIM)}: {ne} "
                           f"({t1 - t0 + ADIM:.1f} sn) — x/y/konum/ofset/sure ile ayır")
    return out


def _pano_denetle(s, c, z) -> list[str]:
    """Soruşturma panosunda üst üste binen kartlar (10. tur, animasyon hakemi S6: "BAKANLIK YAZISI ?" ile "FİRMA ?")."""
    from . import zaman as Zm
    from .sahneler import cizici
    S = c.S
    try:
        cz = cizici(s, c)
    except Exception:   # noqa: BLE001
        return []
    kartlar = list(cz.kartlar.values())
    poli = {}
    for k in kartlar:
        x0, y0, x1, y1 = k["govde"]
        poli[k["id"]] = donuk_dikdortgen((x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, k["egim"])
    out = []
    for i in range(len(kartlar)):
        for j in range(i + 1, len(kartlar)):
            a, b = kartlar[i], kartlar[j]
            d = derinlik(poli[a["id"]], poli[b["id"]])
            if d > UST_DERIN * S:
                t = max(a["t"], b["t"])
                out.append(f"{Zm.zaman_str(z.sahne_basi(s) + t)}: pano kartları '{a['id']}' ile '{b['id']}' "
                           f"{'üst üste biniyor' if d > 0 else 'birbirine değiyor'} — kartın x/y'sini kaydır")
    return out


def _araliklar(ts: list[float]) -> list[tuple[float, float]]:
    out = []
    for t in sorted(ts):
        if out and t - out[-1][1] <= ADIM * 1.5:
            out[-1] = (out[-1][0], t)
        else:
            out.append((t, t))
    return out


def _ust_var(s) -> bool:
    """Sahnede denetlenecek üst katman var mı (en az biri ve karakter ya da ikinci bir üst katman)."""
    n = sum(1 for o in s.olaylar if o.tip in ("isim", "kelime") or (o.tip == "damga" and not o.p.get("kart")))
    n += 1 if (s.kose is not None or any(o.tip == "kose" for o in s.olaylar)) else 0
    n += 1 if (s.tip in ("wojak", "foto", "manset") and s.p.get("etiket")) else 0
    kar = bool(s.p.get("karakterler") or s.p.get("konuk"))
    return n >= 2 or (n >= 1 and kar)
