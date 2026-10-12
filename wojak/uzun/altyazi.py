"""SRT altyazı: satırların gerçek zamanlamasından, okunabilir parçalara bölünmüş.

Kurallar: satır başına en fazla 42 karakter, parça başına en fazla 2 satır, her parça en az 1 sn,
parçalar çakışmaz. Bir anlatım satırı cümle/virgül sınırlarından bölünür; parçanın süresi uzunluğuyla
orantılıdır. Metin `metin`den gelir (telaffuz düzeltmeleri altyazıya girmez), UTF-8.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .zaman import Zaman

MAX_SATIR = 42
MAX_KARAKTER = 2 * MAX_SATIR
MIN_SURE = 1.0
UZATMA = 0.35    # satır sesi bittikten sonra yazının ekranda kalabileceği en fazla süre


@dataclass
class Parca:
    bas: float
    son: float
    metin: str


def iki_satir(metin: str, genislik: int = MAX_SATIR) -> str | None:
    """Metni en fazla iki dengeli satıra böler; sığmazsa None."""
    metin = " ".join(metin.split())
    if len(metin) <= genislik:
        return metin
    kel = metin.split(" ")
    en_iyi = None
    for i in range(1, len(kel)):
        a, b = " ".join(kel[:i]), " ".join(kel[i:])
        if len(a) <= genislik and len(b) <= genislik:
            # dengeli ve tercihen noktalama sonrası kır
            skor = abs(len(a) - len(b)) - (8 if a[-1] in ",;:.!?" else 0)
            if en_iyi is None or skor < en_iyi[0]:
                en_iyi = (skor, a + "\n" + b)
    return en_iyi[1] if en_iyi else None


def _kelime_bol(metin: str, limit: int) -> list[str]:
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


def parcala(metin: str) -> list[str]:
    """Bir anlatım satırını ekranda okunabilir parçalara böler (her parça <= 2x42 karakter)."""
    metin = " ".join(metin.split())
    if not metin:
        return []
    cumleler = [c for c in re.split(r"(?<=[.!?…])\s+", metin) if c]
    parcalar: list[str] = []
    for c in cumleler:
        if iki_satir(c):
            parcalar.append(c)
            continue
        # virgül/noktalı virgül/iki nokta sınırlarından böl
        alt = [x for x in re.split(r"(?<=[,;:])\s+", c) if x]
        tampon = ""
        for x in alt:
            aday = (tampon + " " + x).strip()
            if iki_satir(aday):
                tampon = aday
            else:
                if tampon:
                    parcalar.append(tampon)
                if iki_satir(x):
                    tampon = x
                else:
                    parcalar += _kelime_bol(x, MAX_KARAKTER - 6)[:-1]
                    tampon = _kelime_bol(x, MAX_KARAKTER - 6)[-1]
        if tampon:
            parcalar.append(tampon)
    # çok kısa parçaları komşusuyla birleştir
    birlesik: list[str] = []
    for p in parcalar:
        if birlesik and (len(p) < 14 or len(birlesik[-1]) < 14) and iki_satir(birlesik[-1] + " " + p):
            birlesik[-1] = birlesik[-1] + " " + p
        else:
            birlesik.append(p)
    return birlesik


def parcalar(z: Zaman) -> list[Parca]:
    satirlar = z.satirlar()
    out: list[Parca] = []
    for i, sz in enumerate(satirlar):
        metin = sz.satir.altyazi
        ps = parcala(metin)
        if not ps:
            continue
        sure = max(sz.son - sz.bas, 0.01)
        # parça sayısı süreye sığmıyorsa birleştir (her biri >= 1 sn olsun)
        while len(ps) > 1 and sure / len(ps) < MIN_SURE:
            j = min(range(len(ps) - 1), key=lambda k: len(ps[k]) + len(ps[k + 1]))
            ps[j:j + 2] = [ps[j] + " " + ps[j + 1]]
        agirlik = [len(p) + 6 for p in ps]
        top = sum(agirlik)
        t = sz.bas
        for p, w in zip(ps, agirlik):
            d = sure * w / top
            out.append(Parca(t, t + d, p))
            t += d
    # uzatma, en az süre ve çakışmasızlık
    for i, p in enumerate(out):
        sonraki = out[i + 1].bas if i + 1 < len(out) else z.sure
        p.son = min(max(p.son + UZATMA, p.bas + MIN_SURE), sonraki - 0.04 if i + 1 < len(out) else z.sure)
        if p.son - p.bas < MIN_SURE:   # sıkışık: sonraki parçayı biraz ötele (kendi süresinden yer)
            if i + 1 < len(out):
                kay = p.bas + MIN_SURE - p.son
                out[i + 1].bas += kay + 0.04
                p.son = p.bas + MIN_SURE
    for p in out:
        p.metin = iki_satir(p.metin) or "\n".join(_kelime_bol(p.metin, MAX_SATIR)[:2])
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
        bloklar.append(f"{i}\n{zaman_damgasi(p.bas)} --> {zaman_damgasi(p.son)}\n{p.metin}\n")
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
