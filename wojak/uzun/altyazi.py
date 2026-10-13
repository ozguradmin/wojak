"""SRT altyazı: satırların gerçek zamanlamasından, okunabilir parçalara bölünmüş.

Kurallar: satır başına en fazla 42 karakter, parça başına en fazla 2 satır, her parça en az 1 sn,
parçalar çakışmaz. Bir anlatım satırı cümle/virgül sınırlarından bölünür; sığmayan yan cümle kelime
sınırlarından EŞİT parçalara bölünür (tek kelimelik yetim parça yok). Hiçbir kelime atılmaz: sığmayan
birleşim yapılmaz, parça ayrı blok olur (`kelime_farki` bunu denetler). Parçanın süresi uzunluğuyla
orantılıdır. Metin `metin`den gelir (telaffuz düzeltmeleri altyazıya girmez), UTF-8. Anlatıcıdan başka sesin satırları
(alıntılar: reklam sloganı, ürün bilgisi) `<i>…</i>` ile italik yazılır (YouTube SRT'de destekler); satır uzunluğu
denetimi etiketsiz metne bakar, alıntı parçası önce 38 karakterle kırılır ki etiketlerle de 42'yi geçmesin.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import numpy as np

from .spec import temiz_metin
from .zaman import Zaman

MAX_SATIR = 42
MAX_KARAKTER = 2 * MAX_SATIR
MIN_SURE = 1.0
UZATMA = 0.35    # satır sesi bittikten sonra yazının ekranda kalabileceği en fazla süre


SAYI = {"bir", "iki", "üç", "dört", "beş", "altı", "yedi", "sekiz", "dokuz", "on", "yirmi", "otuz", "kırk", "elli",
        "altmış", "yetmiş", "seksen", "doksan", "yüz", "bin", "milyon", "milyar"}
EKLER = {"da", "de", "ta", "te", "mi", "mı", "mu", "mü", "ki"}   # ayrı yazılan ek/edat: satır başına düşmesin
# soru eki ve çekimli hâlleri ('yeterli | miydi?'): satır başına düşmesin (5. tur, dil hakemi)
SORU = re.compile(r"^(mi|mı|mu|mü)(ydi|ydı|ydu|ydü|ymiş|ymış|ymuş|ymüş|dir|dır|dur|dür|sin|sın|sun|sün|yim|yım|yum|yüm|"
                  r"yiz|yız|yuz|yüz|siniz|sınız|sunuz|sünüz)?$")
# belirleyici / niteleyici: arkasından kırılmasın ('her | seferinde', 'en | eski', 'yarım | asırdan', 'o | ‘deneme’')
BELIRLEYICI = {"o", "bu", "şu", "en", "her", "yarım", "hiçbir", "birkaç", "pek", "aynı", "bütün", "tüm"}
# ek-fiil / yardımcı: önünden kırılmasın ('yetersiz | olduğunu', 'sakinleştirici | olarak')
YARDIMCI = {"olduğunu", "olduğu", "olduğunda", "olan", "olarak", "olur", "oldu", "olmuş", "olmadığını", "değil",
            "değildi"}
# rakamla sayı + ek ('1928'den', '300'), kesme işaretli ya da değil
RAKAM = re.compile(r"^[≈~]?\d[\d.,]*(['’]\w+)?$")
# ilgi hâli (tamlayan) eki: arkasından kırılmasın ('Grünenthal'in | laboratuvarında', 'ilacın | tanıtım')
TAMLAYAN = re.compile(r"(ın|in|un|ün)$")
TAMLAYAN_DEGIL = {"için", "önce", "sonra", "bin", "gün", "dün", "kin", "din", "tün", "yün", "un", "şimdin", "neden"}
NOKTALAMA = ".,;:!?…"
ACAN, KAPAYAN = "‘„“«", "’“”»"


def _kucuk(k: str) -> str:
    return k.replace("I", "ı").replace("İ", "i").lower()


def _yalin(k: str) -> str:
    return _kucuk(k.strip(NOKTALAMA + ACAN + KAPAYAN + "\"'()"))


def _buyuk_mu(k: str) -> bool:
    k = k.lstrip(ACAN + "\"'(")
    return bool(k) and k[0].isupper()


def kirma_cezalari(kel: list[str]) -> list[float]:
    """c[i]: kel[i-1] ile kel[i] arasından satır/blok kırmanın cezası (0 = serbest). talidomit-turkiye 3. hakem turu:
    'on | yedi', 'üç yüz | milyonu', '‘etkilenmeyen tek | iki ülke’', 'Ankara Veteriner | Fakültesi'nden',
    'Ankara'da | da', 'çocuk | doktoru Widukind Lenz' gibi kırılmalar okumayı bozuyordu.
      - sayı öbeği: önceki kelime yalın bir sayı (yazıyla ya da rakamla) -> 40
      - tırnak içi ('…', „…“) -> 80
      - özel ad: iki büyük harfli kelime arası -> 30
      - satır başına düşen ayrı ek ('da', 'de', 'mi', 'ki') -> 60
      - ad tamlaması + özel ad ('çocuk | doktoru Widukind') -> 15
    Önceki kelime noktalamayla bitiyorsa ceza yok (virgül, iki nokta, nokta sonrası kırmak iyidir)."""
    n = len(kel)
    c = [0.0] * (n + 1)
    derin = 0
    tirnak = [0] * n            # kel[i]'den SONRA tırnak açık mı
    for i, k in enumerate(kel):
        if k[:1] in ACAN:
            derin = 1
            if any(ch in KAPAYAN for ch in k[1:]):
                derin = 0
        elif derin and any(ch in KAPAYAN for ch in k):
            derin = 0
        tirnak[i] = derin
    for i in range(1, n):
        a, b = kel[i - 1], kel[i]
        if a[-1] in NOKTALAMA:
            continue
        x = 0.0
        ay, by = _yalin(a), _yalin(b)
        if ay in SAYI or ay.replace(".", "").isdigit() or RAKAM.match(ay) or \
                any(ay.startswith(r) and 0 < len(ay) - len(r) <= 3 for r in ("milyon", "milyar", "bin", "yüz")
                    if len(r) > 3):
            x += 40
        if ay in BELIRLEYICI or ay == "bir":
            x += 50
        if SORU.match(by):
            x += 60
        if ay.endswith(("lık", "lik", "luk", "lük", "sal", "sel")) and not _buyuk_mu(b):
            x += 20   # sıfat + ad ('günlük | doz', 'doğumsal | kusur')
        if by in YARDIMCI:
            x += 30
        if (TAMLAYAN.search(ay) and ay not in TAMLAYAN_DEGIL and len(ay) > 3 and not _buyuk_mu(b)
                and not SORU.match(by)):
            x += 25
        if _buyuk_mu(a) and not _buyuk_mu(b) and re.search(r"(ı|i|u|ü)(n(da|de|dan|den|ın|in|a|e)(ki)?)?$", by) \
                and len(by) > 6:
            x += 25   # özel ad + iyelikli ad ('Behçet | hastalığındaki')
        if tirnak[i - 1]:
            x += 80
        if _buyuk_mu(a) and _buyuk_mu(b):
            x += 30
        if by in EKLER:
            x += 60
        if (not _buyuk_mu(a) and not _buyuk_mu(b) and i + 1 < n and _buyuk_mu(kel[i + 1])
                and by[-1:] in "ıiuü" and b[-1] not in NOKTALAMA):
            x += 15
        c[i] = x
    return c


@dataclass
class Parca:
    bas: float
    son: float
    metin: str
    alinti: bool = False   # anlatıcıdan başka sesin satırı (alıntı: reklam, ürün bilgisi): SRT'de <i>…</i>


def iki_satir(metin: str, genislik: int = MAX_SATIR) -> str | None:
    """Metni en fazla iki dengeli satıra böler; sığmazsa None."""
    metin = " ".join(metin.split())
    if len(metin) <= genislik:
        return metin
    kel = metin.split(" ")
    ceza = kirma_cezalari(kel)
    en_iyi = None
    for i in range(1, len(kel)):
        a, b = " ".join(kel[:i]), " ".join(kel[i:])
        if len(a) <= genislik and len(b) <= genislik:
            # dengeli, tercihen noktalama sonrası; sayı öbeği, tırnak, özel ad içinden ve ekten önce kırma
            skor = abs(len(a) - len(b)) - (8 if a[-1] in ",;:.!?" else 0) + ceza[i]
            if en_iyi is None or skor < en_iyi[0]:
                en_iyi = (skor, a + "\n" + b)
    return en_iyi[1] if en_iyi else None


def _kelime_bol(metin: str, limit: int) -> list[str]:
    """Açgözlü kelime bölme (eski davranış; yalnız geriye dönük uyumluluk için)."""
    out, cur = [], []
    for k in metin.split():
        if cur and len(" ".join(cur + [k])) > limit:
            out.append(" ".join(cur))
            cur = [k]
        else:
            cur.append(k)
    if cur:
        out.append(" ".join(cur))
    return out


def _dengeli_bol(metin: str, sigar=None) -> list[str]:
    """Kelime sınırlarından EN AZ sayıda, olabildiğince EŞİT uzunlukta parçaya böler; her parça `sigar(parça)`
    koşulunu sağlar (vars. iki dengeli satıra sığmak). Açgözlü bölmenin aksine sonda tek kelimelik yetim
    ("sentezleniyor.") bırakmaz; noktalama sonrası kırılmayı tercih eder. Hiçbir kelime atılmaz."""
    sigar = sigar or (lambda x: iki_satir(x) is not None)
    kel = metin.split()
    m = len(kel)
    if m == 0:
        return []
    if sigar(" ".join(kel)):
        return [" ".join(kel)]
    uz = [len(k) for k in kel]
    ceza = kirma_cezalari(kel)
    on = [0]
    for x in uz:
        on.append(on[-1] + x)

    def ln(i, j):   # kel[i:j] birleşik uzunluğu
        return on[j] - on[i] + (j - i - 1)

    for n in range(2, m + 1):
        hedef = ln(0, m) / n
        # dp[k][j]: ilk j kelimeyi k parçaya bölmenin en iyi maliyeti
        INF = float("inf")
        dp = [[INF] * (m + 1) for _ in range(n + 1)]
        geri = [[-1] * (m + 1) for _ in range(n + 1)]
        dp[0][0] = 0.0
        for k in range(1, n + 1):
            for j in range(k, m + 1):
                for i in range(k - 1, j):
                    if dp[k - 1][i] == INF:
                        continue
                    parca = " ".join(kel[i:j])
                    if not sigar(parca):
                        continue
                    c = (ln(i, j) - hedef) ** 2
                    if j < m and kel[j - 1][-1] in ",;:.!?…":
                        c -= 40.0   # noktalamadan sonra kırmak okunur
                    if j < m:
                        c += 8.0 * ceza[j]   # sayı öbeği / tırnak / özel ad içinden, ekten önce kırma
                    if j - i == 1 and m > 1:
                        c += 400.0  # tek kelimelik parça (yetim) istenmez
                    if dp[k - 1][i] + c < dp[k][j]:
                        dp[k][j], geri[k][j] = dp[k - 1][i] + c, i
        if dp[n][m] < INF:
            out, j = [], m
            for k in range(n, 0, -1):
                i = geri[k][j]
                out.append(" ".join(kel[i:j]))
                j = i
            return out[::-1]
    return kel   # tek kelime bile sığmıyorsa (olmaz): kelime kelime


def parcala(metin: str) -> list[str]:
    """Bir anlatım satırını ekranda okunabilir parçalara böler (her parça iki dengeli satıra sığar).
    Kelime kaybı yok: parçaların birleşimi her zaman metnin kendisidir."""
    metin = " ".join(metin.split())
    if not metin:
        return []
    cumleler = [c for c in re.split(r"(?<=[.!?…])\s+", metin) if c]
    parcalar: list[str] = []
    for c in cumleler:
        if iki_satir(c):
            parcalar.append(c)
            continue
        # virgül/noktalı virgül/iki nokta sınırlarından böl; sığmayan yan cümle dengeli bölünür
        alt = [x for x in re.split(r"(?<=[,;:])\s+", c) if x]
        tampon = ""
        for x in alt:
            aday = (tampon + " " + x).strip()
            if iki_satir(aday):
                tampon = aday
                continue
            if tampon:
                parcalar.append(tampon)
                tampon = ""
            if iki_satir(x):
                tampon = x
            else:
                bol = _dengeli_bol(x)
                parcalar += bol[:-1]
                tampon = bol[-1]
        if tampon:
            parcalar.append(tampon)
    # çok kısa parçaları komşusuyla birleştir (sığıyorsa); sığmıyorsa çifti dengeli yeniden böl
    birlesik: list[str] = []
    for p in parcalar:
        if birlesik and (len(p) < 18 or len(birlesik[-1]) < 18):
            ikili = birlesik[-1] + " " + p
            if iki_satir(ikili):
                birlesik[-1] = ikili
                continue
            yeniden = _dengeli_bol(ikili)
            if len(yeniden) == 2 and min(len(x) for x in yeniden) >= 14:
                birlesik[-1:] = yeniden
                continue
        birlesik.append(p)
    return birlesik


@lru_cache(maxsize=512)
def _sessizlikler(yol: str, mtime: float) -> tuple[tuple[float, float], ...]:
    """Satır sesindeki iç sessizlikler (sn, satır başına göre): 20 ms RMS, en yüksek seviyenin %90'lık diliminin 28 dB
    altı, en az 0,1 sn; baştaki ve sondaki sessizlik sayılmaz."""
    from .tts import wav_oku
    x, sr = wav_oku(Path(yol))
    h = max(1, int(sr * 0.02))
    n = len(x) // h
    if n < 10:
        return ()
    r = np.sqrt((x[: n * h].reshape(n, h) ** 2).mean(axis=1) + 1e-12)
    db = 20 * np.log10(r + 1e-9)
    sil = db < float(np.percentile(db, 90)) - 28
    out, i = [], 0
    while i < n:
        if sil[i]:
            j = i
            while j < n and sil[j]:
                j += 1
            if i > 0 and j < n and (j - i) * 0.02 >= 0.1:
                out.append((i * 0.02, j * 0.02))
            i = j
        else:
            i += 1
    return tuple(out)


def sessizlige_otur(sinirlar: list[float], sessiz: tuple, sure: float, pencere: float = 1.6) -> list[float]:
    """9. tur (teknik hakem S3): satır içindeki parça sınırları (uzunlukla orantılı tahmin) en yakın iç sessizliğe
    oturur: sonraki parça konuşma yeniden başlamadan 0,08 sn önce açılır. Ekranda olup söylenmeyen yazı ('(FDA)')
    tahmini 1,4 sn kaydırıyordu. Sıra korunur; parçalar en az 0,6 sn kalır."""
    out, onceki = [], 0.0
    for k, b in enumerate(sinirlar):
        sonraki_sinir = sinirlar[k + 1] if k + 1 < len(sinirlar) else sure
        adaylar = [(abs((a + c) / 2 - b), max(a, c - 0.08)) for a, c in sessiz
                   if abs((a + c) / 2 - b) <= pencere and onceki + 0.6 <= max(a, c - 0.08) <= sonraki_sinir + pencere
                   and max(a, c - 0.08) <= sure - 0.6]
        yeni = min(adaylar)[1] if adaylar else b
        if yeni < onceki + 0.6:
            yeni = b
        out.append(yeni)
        onceki = yeni
    return out


def parcalar(z: Zaman) -> list[Parca]:
    satirlar = z.satirlar()
    out: list[Parca] = []
    for i, sz in enumerate(satirlar):
        metin = sz.satir.altyazi
        # metindeki satır sonu ("\n") blok kırma ipucudur (4. tur, dil hakemi: 'önemli | bir çalışma',
        # 'kimsenin | belgeleyemediği' gibi kırılmalar); TTS metninden ve ekrandan çıkarılır, önbellek anahtarı değişmez
        ham = sz.satir.metin
        if "\n" in ham.strip():
            ps = [x for seg in ham.split("\n") if seg.strip() for x in parcala(temiz_metin(seg))]
        else:
            ps = parcala(metin)
        if not ps:
            continue
        sure = max(sz.son - sz.bas, 0.01)
        # parça sayısı süreye sığmıyorsa birleştir (her biri >= 1 sn olsun) — ama yalnız birleşim iki satıra
        # sığıyorsa: hiçbir zaman kelime atılmaz; sığmazsa parça kısa kalır, aşağıdaki geçiş en az süreyi sağlar
        while len(ps) > 1 and sure / len(ps) < MIN_SURE:
            adaylar = [k for k in range(len(ps) - 1) if iki_satir(ps[k] + " " + ps[k + 1])]
            if not adaylar:
                break
            j = min(adaylar, key=lambda k: len(ps[k]) + len(ps[k + 1]))
            ps[j:j + 2] = [ps[j] + " " + ps[j + 1]]
        agirlik = [len(p) + 6 for p in ps]
        top = sum(agirlik)
        alinti = sz.satir.ses != z.video.anlatici_ses
        sinirlar, acc = [], 0.0
        for w in agirlik[:-1]:
            acc += sure * w / top
            sinirlar.append(acc)
        wav = sz.satir.wav
        if sinirlar and wav is not None and not sz.satir.tahmini and Path(wav).exists():
            sinirlar = sessizlige_otur(sinirlar, _sessizlikler(str(wav), Path(wav).stat().st_mtime), sure)
        kenar = [0.0] + sinirlar + [sure]
        for k, p in enumerate(ps):
            out.append(Parca(sz.bas + kenar[k], sz.bas + kenar[k + 1], p, alinti))
    # uzatma, en az süre ve çakışmasızlık
    for i, p in enumerate(out):
        sonraki = out[i + 1].bas if i + 1 < len(out) else z.sure
        p.son = min(max(p.son + UZATMA, p.bas + MIN_SURE), sonraki - 0.04 if i + 1 < len(out) else z.sure)
        if p.son - p.bas < MIN_SURE:   # sıkışık: sonraki parçayı biraz ötele (kendi süresinden yer)
            if i + 1 < len(out):
                kay = p.bas + MIN_SURE - p.son
                out[i + 1].bas += kay + 0.04
                out[i + 1].son = max(out[i + 1].son, out[i + 1].bas + MIN_SURE)
                p.son = p.bas + MIN_SURE
    for p in out:
        # alıntıda <i> etiketleri (3-4 karakter) satıra sığsın: önce dar genişlik
        iki = (iki_satir(p.metin, MAX_SATIR - 4) if p.alinti else None) or iki_satir(p.metin)
        if iki is None:   # parcala() bunu engeller; yine de kelime atma, bölünmüş ama tam metin yaz
            raise ValueError(f"altyazı parçası iki satıra sığmıyor: {p.metin!r}")
        p.metin = iki
    return out


def kelime_farki(z: Zaman, ps: list[Parca] | None = None) -> list[str]:
    """Altyazıda eksik/fazla kelime: satır metinlerinin kelimeleri ile SRT kelimeleri birebir aynı olmalı."""
    ps = ps if ps is not None else parcalar(z)
    beklenen = " ".join(sz.satir.altyazi for sz in z.satirlar()).split()
    gelen = " ".join(p.metin.replace("\n", " ") for p in ps).split()
    if beklenen == gelen:
        return []
    import difflib
    out = []
    for op, a0, a1, b0, b1 in difflib.SequenceMatcher(None, beklenen, gelen, autojunk=False).get_opcodes():
        if op != "equal":
            out.append(f"{op}: {' '.join(beklenen[a0:a1])!r} -> {' '.join(gelen[b0:b1])!r}")
    return out


def zaman_damgasi(t: float) -> str:
    ms = int(round(max(0.0, t) * 1000))
    h, ms = divmod(ms, 3600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def srt(ps: list[Parca]) -> str:
    bloklar = []
    for i, p in enumerate(ps, 1):
        metin = f"<i>{p.metin}</i>" if p.alinti else p.metin   # 6. tur (dil hakemi N5): alıntı italik
        bloklar.append(f"{i}\n{zaman_damgasi(p.bas)} --> {zaman_damgasi(p.son)}\n{metin}\n")
    return "\n".join(bloklar)


def yaz(z: Zaman, yol: Path) -> Path:
    yol.parent.mkdir(parents=True, exist_ok=True)
    yol.write_text(srt(parcalar(z)), encoding="utf-8")
    return yol


def denetle(ps: list[Parca]) -> list[str]:
    hatalar = []
    for i, p in enumerate(ps, 1):
        satirlar = p.metin.split("\n")
        if len(satirlar) > 2:
            hatalar.append(f"{i}: {len(satirlar)} satır")
        for s in satirlar:
            if len(s) > MAX_SATIR:
                hatalar.append(f"{i}: {len(s)} karakter: {s}")
        if p.son - p.bas < MIN_SURE - 1e-6:
            hatalar.append(f"{i}: {p.son - p.bas:.2f} sn")
        if i < len(ps) and ps[i].bas < p.son:
            hatalar.append(f"{i}: sonraki parçayla çakışıyor")
    return hatalar
