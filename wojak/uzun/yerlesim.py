"""Üst katman yerleşimi ve çakışma denetimi (10. tur).

Animasyon hakemi (9. tur, M1/M3/S5-S7): iki isim etiketi 4-5 sn yüzün (çene, ağız köşesi) üstündeydi, Kennedy
etiketi çıkarken "BU ÖDÜLÜ ALAN 2. KADIN" üstüne çizildi, iki damga köşeden birbirine değdi. Hepsi video.yaml'dan
düzeltilebilirdi ama motor uyarmadı. Bu modül:

- karakter görselinin alfa kutusunu ve yüz bölgesini (baştan boyuna kadar) bulur;
- `isim` etiketi için yer seçer (sahneler.UstKatman): kutusu her karakterin alfa kutusundan en az `BOSLUK` (40 px,
  1080p) uzak; sığmazsa satır kırar, küçülür ya da boş tarafa geçer;
- `kontrol` için bütün üst katmanları (isim, kelime, damga, daktilo etiketi, köşe göstergesi) sahne boyunca 0,1 sn
  arayla örnekler; bir yüze ya da başka bir üst katmana binenleri zaman aralığıyla bildirir (`denetle`);
- 14. tur: pano kartlarının (kamera `yakin`/`zoom` altında, ekran pikseline çevrilerek), karta basılı damgaların ve
  bütün üst katmanların kadrajdan taşmasını bildirir (`_kadraj_denetle`).
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
KELIME_ARA = 0.3       # sn (13. tur): aynı yerdeki iki vurgu kelimesi arasında, öncekinin sönmesinden sonra en az
YUZ_DISARI = 0.12      # 13. tur: yüz kutusunun bu oranından fazlası kadraj dışında (sol/sağ/üst) kalırsa uyarılır
YUZ_ORTU = 0.10        # 13. tur: sonra çizilen görsel bir yüz kutusunun bu oranından fazlasını örterse uyarılır
SABIT_PAY = 16.0       # px (13. tur): sahnenin sabit kutusu (harita lejantı, foto atfı) ile canlı karakter arası en az
KARAKTER_SURE = 0.4    # sn: karakter denetimlerinde bundan kısa durum (giriş/çıkış, itme anı) bildirilmez
KADRAJ_TASMA = 2.0     # px (14. tur): pano kartı, karta basılı damga, vurgu kelimesi, damga, isim, köşe göstergesi
                       # kadraj kenarını bundan fazla aşarsa (yakin/zoom/kamera dahil) uyarılır
KENAR_BANT = 24.0      # px (14. tur): vurgu kelimesi bir fotoğraf baskısının, pano kartının ya da dekor görselinin üst/alt
                       # kenarına bundan yakınsa ya da kenarın üstüne biniyorsa (yarısı içeride yarısı dışarıda) uyarılır


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
        ust = _ust_var(s)
        if not (ust or s.p.get("karakterler") or s.p.get("konuk") or s.tip == "pano" or _ust_herhangi(s)):
            continue
        try:
            cz = cizici(s, c)
        except Exception as e:   # noqa: BLE001 — denetim çizimi durdurmasın
            out.append(f"{Zm.zaman_str(z.sahne_basi(s))}: üst katman denetimi kurulamadı ({type(e).__name__}: {e})")
            continue
        uk = cz.katman
        b0 = z.sahne_basi(s)
        out += _kadraj_denetle(s, cz, b0, c)
        out += _kenar_denetle(s, cz, b0, c)
        if not (ust or s.p.get("karakterler") or s.p.get("konuk")):
            continue
        out += _kelime_sirasi(uk, b0, c)
        out += _karakter_denetle(s, cz, b0, c)
        if not ust:
            continue
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


def _kadraj_denetle(s, cz, b0: float, c) -> list[str]:
    """14. tur (izlenme hakemi 13. tur M1: B5.8a'da `yakin: 1.22` ile "ANMA YAZILARI, 1994" kartının alt satırı
    kadrajın altında kesildi; anlatım tam o satırı okuyordu; eski denetimler yalnız çakışmaya bakıyordu). Sahne boyunca
    0,1 sn arayla: pano kartlarının gövdesi ve karta basılı damgalar (tuvalde çizilir: `yakin`/`zoom`/kamera kayması
    dahil, ekran pikseline çevrilerek), vurgu kelimeleri, damgalar, köşe göstergesi, daktilo etiketi ve yerine oturmuş
    isim etiketleri kadraj kenarını `KADRAJ_TASMA`'dan fazla aşıyor mu. `EN_AZ_SURE`'den kısası (kelimenin büyüme
    sıçraması) bildirilmez."""
    from . import zaman as Zm
    S, W, H = c.S, c.W, c.H
    uk = cz.katman
    pano = getattr(cz, "ekran_kutulari", None) if s.tip == "pano" else None
    tas: dict = {}
    n = max(1, int(s.sure_hesap / ADIM))
    for j in range(n + 1):
        t = min(j * ADIM, s.sure_hesap - 1e-3)
        polis = list(uk.kutular(t, isim=False))
        for it in getattr(uk, "isimler", []):
            u = t - it["t0"]
            if uk.ISIM_GIRIS <= u <= it["sure"]:   # kenardan kayarak giren/çıkan etiket bilerek dışarıdadır
                x, y, a = uk._isim_xy(it, u)
                pb = uk._kutu_ici(it["spr"])
                polis.append((f"isim '{it['ad']}'", dikdortgen(x + pb[0], y + pb[1], x + pb[2], y + pb[3])))
        if pano is not None:
            polis += pano(t)
        for ad, poli in polis:
            x0, y0, x1, y1 = kutu_icin(poli)
            asim = {"sol": -x0, "sağ": x1 - W, "üst": -y0, "alt": y1 - H}
            kenar, px = max(asim.items(), key=lambda q: q[1])
            if px > KADRAJ_TASMA * S:
                tas.setdefault((ad, kenar), []).append((t, px / S))
    out = []
    for (ad, kenar), ts in sorted(tas.items(), key=lambda q: q[1][0][0]):
        for t0, t1 in _araliklar([t for t, _ in ts]):
            if t1 - t0 + ADIM < EN_AZ_SURE:
                continue
            en = max(v for t, v in ts if t0 <= t <= t1)
            ipucu = ("kartın x/y/en'ini ya da sahnenin `yakin`/`zoom`'unu değiştir"
                     if ad.startswith("pano") or "(kart " in ad else "x/y/boy/konum ile kadraja al")
            out.append(f"{Zm.zaman_str(b0 + t0, True)}-{Zm.zaman_str(b0 + t1 + ADIM, True)}: {ad} kadrajın {kenar} kenarından "
                       f"{en:.0f} px taşıyor ({t1 - t0 + ADIM:.1f} sn) — {ipucu}")
    return out


def _kenar_denetle(s, cz, b0: float, c) -> list[str]:
    """14. tur (animasyon hakemi 13. tur S1: "HAMİLE BİR KADIN ALIRSA?" Köln fotoğrafının üst kenarını kesiyordu,
    "TAVUK EMBRİYOSU DENEYİ?" baskının köşesinde, "DOĞU ALMANYA: RUHSAT YOK" baskının üst kenarına oturmuş, Brezilya
    kutusunda iki yazı kenarın üstünde: okunuyor ama "yapıştırılmış" görünüyor). Vurgu kelimesinin kutusu bir fotoğraf
    baskısının, pano kartının ya da dekor görselinin (chars/ dışı, `canli: false`) üst ya da alt kenarına `KENAR_BANT`'tan
    yakın ya da kenarın üstündeyse (yatayda örtüşürken) bildirilir: ya bütünüyle görselin içinde ya da en az bant kadar
    dışında olmalı."""
    from . import zaman as Zm
    S = c.S
    uk = cz.katman
    if not uk.vurgular:
        return []
    kenarlik = getattr(cz, "kenar_kutulari", None)
    sira = [k for k in list(getattr(cz, "cizim_sirasi", []) or []) + list(uk.konuklar) if not k.yuzlu]
    kamf = {id(k): kf for k, kf in uk.kars}
    bant = KENAR_BANT * S
    cak: dict = {}
    n = max(1, int(s.sure_hesap / ADIM))
    for j in range(n + 1):
        t = min(j * ADIM, s.sure_hesap - 1e-3)
        kelimeler = [(ad, kutu_icin(p_)) for ad, p_ in uk.kutular(t, isim=False) if ad.startswith("kelime")]
        if not kelimeler:
            continue
        polis = list(kenarlik(t) if kenarlik else [])   # 4 köşe: sol üst, sağ üst, sağ alt, sol alt (dönük olabilir)
        for k in sira:
            if k.giris is not None and k.giris <= t < k.giris + k.GIRIS + 0.15:
                continue
            if k.cikis is not None and t >= k.cikis - 0.05:
                continue
            kf = kamf.get(id(k))
            kb = k.ekran_kutulari(t, kf(t) if kf else None)
            if kb is not None:
                polis.append((f"görsel '{k.ad}'", dikdortgen(*kb[0])))
        for k_ad, kk in kelimeler:
            for r_ad, pp in polis:
                for kenar, (a_, b_) in (("üst", (pp[0], pp[1])), ("alt", (pp[3], pp[2]))):
                    # kenar doğrusunun kelimeyle yatayda örtüşen parçasındaki en düşük/en yüksek y (eğik baskı)
                    xa, xb = max(kk[0], min(a_[0], b_[0])), min(kk[2], max(a_[0], b_[0]))
                    if xb <= xa:
                        continue
                    dx = b_[0] - a_[0]
                    ys = [a_[1] + (b_[1] - a_[1]) * ((x - a_[0]) / dx if abs(dx) > 1e-6 else 0.0) for x in (xa, xb)]
                    if kk[3] > min(ys) - bant and kk[1] < max(ys) + bant:
                        cak.setdefault((k_ad, r_ad, kenar), []).append(t)
    out = []
    for (k_ad, r_ad, kenar), ts in sorted(cak.items(), key=lambda q: q[1][0]):
        for t0, t1 in _araliklar(ts):
            if t1 - t0 + ADIM < EN_AZ_SURE:
                continue
            out.append(f"{Zm.zaman_str(b0 + t0, True)}-{Zm.zaman_str(b0 + t1 + ADIM, True)}: {k_ad} {r_ad} "
                       f"kutusunun {kenar} kenarının üstünde (en az {KENAR_BANT:.0f} px dışında ya da bütünüyle içinde "
                       f"olmalı) — kelimeye `y` ver ya da görseli kaydır")
    return out


def _kelime_sirasi(uk, b0: float, c) -> list[str]:
    """13. tur (animasyon hakemi S1: 4:57.5'te "ABD · FDA · 1960" önceki kelime sönerken aynı yerde belirdi, 6 kare
    üst üste iki yazı): aynı dikey bantta yeni vurgu kelimesi öncekinin sönmesi bittikten en az `KELIME_ARA` sonra
    başlamalı. Çakışma denetimi yarı saydamı saymadığı için bunu kaçırıyordu."""
    from . import zaman as Zm
    from .sahneler import KELIME_CIKIS
    out = []
    vs = sorted(uk.vurgular, key=lambda q: q[0])
    for j in range(1, len(vs)):
        t1, _, spr1, cy1, m1 = vs[j]
        for t0, su0, spr0, cy0, m0 in vs[:j]:
            bitis = t0 + su0 + KELIME_CIKIS
            if t1 >= bitis + KELIME_ARA or t1 + 0.05 < t0:
                continue
            h0, h1 = spr0.height / 2, spr1.height / 2
            if abs(cy0 * c.H - cy1 * c.H) >= (h0 + h1) * 0.8:
                continue
            ne = "sönmesi bitmeden" if t1 < bitis else f"söndükten {t1 - bitis:.2f} sn sonra (en az {KELIME_ARA} sn)"
            out.append(f"{Zm.zaman_str(b0 + t1)}: kelime '{m1}', aynı yerdeki '{m0}' {ne} beliriyor — ofset/sure "
                       f"ile ayır ya da `y` ver")
    return out


def _karakter_denetle(s, cz, b0: float, c) -> list[str]:
    """13. tur (animasyon hakemi M1: 9:23'te kamera itmesinde makale çizimi anlatıcının yüzünün yarısını örttü, 'fark'
    tepkisi kayboldu; S3: harita lejantı anlatıcının omzuna biniyordu). Sahne boyunca (giriş/çıkış animasyonu dışında):
    (a) yüz kutusunun `YUZ_DISARI`'dan fazlası kadraj dışında (sol/sağ/üst; kamera ve `it` dahil),
    (b) çizim sırasında SONRA gelen bir görsel (nesne ya da karakter) yüz kutusunun `YUZ_ORTU`'sundan fazlasını örtüyor,
    (c) sahnenin sabit kutusu (harita lejantı, foto atfı) canlı bir karakterin alfa kutusuna `SABIT_PAY`'dan yakın."""
    from . import zaman as Zm
    uk = cz.katman
    S, W, H = c.S, c.W, c.H
    sira = list(getattr(cz, "cizim_sirasi", []) or []) + list(uk.konuklar)
    if not sira:
        return []
    kamf = {id(k): kf for k, kf in uk.kars}
    try:
        sabit = list(cz.sabit_engeller())
    except Exception:   # noqa: BLE001
        sabit = []
    cak: dict = {}
    n = max(1, int(s.sure_hesap / ADIM))
    for j in range(n + 1):
        t = min(j * ADIM, s.sure_hesap - 1e-3)
        kutular = []
        for k in sira:
            kf = kamf.get(id(k))
            kb = k.ekran_kutulari(t, kf(t) if kf else None)
            sakin = kb is not None and not (k.giris is not None and k.giris <= t < k.giris + k.GIRIS + 0.15) \
                and not (k.cikis is not None and t >= k.cikis - 0.05)
            kutular.append((k, kb, sakin))
        for x, (k, kb, sakin) in enumerate(kutular):
            if not (sakin and k.yuzlu):
                continue
            fb = kb[1]
            fw, fh = max(1.0, fb[2] - fb[0]), max(1.0, fb[3] - fb[1])
            dis = max((max(0.0, -fb[0]) + max(0.0, fb[2] - W)) / fw, max(0.0, -fb[1]) / fh)
            if dis > YUZ_DISARI:
                cak.setdefault((k.ad, "", "dış"), []).append((t, dis))
            for k2, kb2, _ in kutular[x + 1:]:
                if kb2 is None:
                    continue
                o = kutu_kesisim(fb, kb2[0]) / (fw * fh)
                if o > YUZ_ORTU and not k2.sabit:   # canlı karakterin kutusu omuz boşluklarını da sayar: alfa maskesiyle
                    o = _maske_ortusu(k2, t, kb2[0], fb) / (fw * fh)
                if o > YUZ_ORTU:
                    cak.setdefault((k.ad, k2.ad, "ört"), []).append((t, o))
            for b in sabit:
                ab = kb[0]
                gx = max(b[0] - ab[2], ab[0] - b[2])
                gy = max(b[1] - ab[3], ab[1] - b[3])
                ara = max(gx, gy)
                if ara < SABIT_PAY * S:
                    cak.setdefault((k.ad, "", "sabit"), []).append((t, ara / S))
    out = []
    for (a_ad, b_ad, tur), ts in sorted(cak.items(), key=lambda q: q[1][0][0]):
        for t0, t1 in _araliklar([t for t, _ in ts]):
            if t1 - t0 + ADIM < KARAKTER_SURE:
                continue
            en = [v for t, v in ts if t0 <= t <= t1]
            if tur == "dış":
                ne = f"{a_ad} yüzünün %{100 * max(en):.0f}'i kadraj dışında — x/boy, kamera ya da `it` hedefini değiştir"
            elif tur == "ört":
                ne = (f"{b_ad} {a_ad} yüzünün %{100 * max(en):.0f}'ini örtüyor (sonra çiziliyor) — yerini/boyunu "
                      f"değiştir ya da karakterler listesinde sırasını")
            else:
                ne = (f"sabit kutu (lejant/atıf) {a_ad} karakterine {min(en):.0f} px "
                      f"({'biniyor' if min(en) < 0 else 'yakın'}; en az {SABIT_PAY:.0f}) — konuğu kaydır ya da kısalt")
            out.append(f"{Zm.zaman_str(b0 + t0)}-{Zm.zaman_str(b0 + t1 + ADIM)}: {ne}")
    return out


def _maske_ortusu(k, t: float, ab: tuple, fb: tuple) -> float:
    """k karakterinin (ekranda alfa kutusu `ab`) gerçekten opak pikselleriyle `fb` kutusunun kesişim alanı (px²)."""
    x0, y0 = max(ab[0], fb[0]), max(ab[1], fb[1])
    x1, y1 = min(ab[2], fb[2]), min(ab[3], fb[3])
    if x1 <= x0 or y1 <= y0:
        return 0.0
    im = k.ims[k.poz(t)["vi"]]
    bb = alfa_kutusu(im)
    if bb is None:
        return 0.0
    a = np.asarray(im.getchannel("A").crop(bb)) > 40
    h, w = a.shape
    sx, sy = w / max(1e-6, ab[2] - ab[0]), h / max(1e-6, ab[3] - ab[1])
    ix0, ix1 = int(max(0, (x0 - ab[0]) * sx)), int(min(w, math.ceil((x1 - ab[0]) * sx)))
    iy0, iy1 = int(max(0, (y0 - ab[1]) * sy)), int(min(h, math.ceil((y1 - ab[1]) * sy)))
    if ix1 <= ix0 or iy1 <= iy0:
        return 0.0
    return float(a[iy0:iy1, ix0:ix1].mean()) * (x1 - x0) * (y1 - y0)


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


def _ust_herhangi(s) -> bool:
    """Sahnede kadraj denetimine girecek en az bir üst katman (isim, kelime, damga, köşe göstergesi) var mı."""
    return (s.kose is not None or any(o.tip in ("isim", "kelime", "damga", "kose") for o in s.olaylar)
            or bool(s.tip in ("wojak", "foto", "manset") and s.p.get("etiket")))


def _ust_var(s) -> bool:
    """Sahnede denetlenecek üst katman var mı (en az biri ve karakter ya da ikinci bir üst katman)."""
    n = sum(1 for o in s.olaylar if o.tip in ("isim", "kelime") or (o.tip == "damga" and not o.p.get("kart")))
    n += 1 if (s.kose is not None or any(o.tip == "kose" for o in s.olaylar)) else 0
    n += 1 if (s.tip in ("wojak", "foto", "manset") and s.p.get("etiket")) else 0
    kar = bool(s.p.get("karakterler") or s.p.get("konuk"))
    return n >= 2 or (n >= 1 and kar)
