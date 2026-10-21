#!/usr/bin/env python3
"""Kanalın imza müziğinin bize ait benzeri: Do minör, 3/4 vals, legato akordeon/harmonyum, gramofon tınısı, 13,75 sn.

Neden: kısa reel'lerde yıllardır kullanılan "orijinal ses" (assets/music/ozel/, STIL.md §10) bir reel'in sesinden
çıkarıldı; kaynağı üçüncü taraf bir parçaysa YouTube'da Content ID / telif ihlali riski taşır (YAYIN_PLANI §0).
Bu dosya aynı HİSSİ verir, melodisi ve armonisi özgündür:

| | Orijinal (ölçüm, STIL §10.2) | Bu sentez |
|---|---|---|
| Ölçü, tempo | 3/4, ~152-155 BPM | 3/4, 154 BPM (varsayılan) |
| Ton | Do minör | Do minör (varsayılan; `--ton` ile kaydırılır) |
| Tını | Kesintisiz legato, zengin harmonik, lo-fi | Çift sesli (musette) kamış + harmonyum altlık, gramofon bandı, hışırtı |
| Yapı | 13,75 sn tek cümle, 11,5 sn'de tonikte kalış | Aynı: 1. ölçü altlık, 2-10 melodi, 11-12 tonikte kalış, sönüş |
| Melodi/armoni | Mi♭-Re-Fa motifi, La♭5-Sol5 doruğu, i ↔ ii° | Farklı motifler ve dizi (aşağıdaki MELODILER), bkz. `--karsilastir` |

    python tools/imza_muzik.py                          # -> assets/music/imza_vals.m4a (varyant: imza)
    python tools/imza_muzik.py --varyant ikinci         # başka melodi, aynı his
    python tools/imza_muzik.py --varyant imza --ton -2 --tempo 150 -o /tmp/x.m4a   # Si♭ minör, biraz yavaş
    python tools/imza_muzik.py --karsilastir assets/music/ozel/kanal_orijinal_ses.m4a   # ölçüm raporu

Her video için farklı müzik: yeni bir varyant MELODILER'e eklenir (12 ölçü, ölçü başına 3 vuruş, son iki ölçü tonik)
ya da mevcut biri `--ton`/`--tempo`/`--tohum` ile değiştirilir. Kural: orijinalin motifleri kullanılmaz (Mi♭5-Re5-Fa5
açılışı, 8. ölçüdeki La♭5-Sol5 doruğu); `--karsilastir` melodik benzerliği ölçer.
Hakkı bize ait: tamamen burada, matematiksel olarak üretilir (kayıt, örnek ya da başka bir parçanın sesi yok).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path

import numpy as np

SR = 44100
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "music" / "imza_vals.m4a"
SURE = 13.75

NOTA = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8,
        "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}


def midi(n: str) -> int:
    ad, okt = n[:-1], int(n[-1])
    return 12 * (okt + 1) + NOTA[ad]


def hz(m: float) -> float:
    return 440.0 * 2 ** ((m - 69) / 12)


# (nota | None=sus, vuruş). Her ölçü 3 vuruş; 12 ölçü. Akorlar ölçü başına (kök + tür).
MELODILER = {
    "imza": {
        "melodi": [
            [(None, 2), ("G4", 1)],
            [("C5", 2), ("D5", 1)],
            [("Eb5", 3)],
            [("D5", 1), ("C5", 1), ("Bb4", 1)],
            [("Ab4", 2), ("C5", 1)],
            [("G4", 3)],
            [("G4", 1), ("Bb4", 1), ("Eb5", 1)],
            [("G5", 2), ("F5", 1)],
            [("Eb5", 1), ("D5", 1), ("C5", 1)],
            [("B4", 2), ("D5", 1)],
            [("C5", 3)],
            [("C5", 3)],
        ],
        "akor": ["C:m", "C:m", "Ab:M", "G:m", "F:m", "C:m", "Eb:M", "C:m", "Ab:M", "G:M", "C:m", "C:m"],
    },
    "ikinci": {
        "melodi": [
            [(None, 2), ("C5", 1)],
            [("G5", 2), ("F5", 1)],
            [("Eb5", 2), ("D5", 1)],
            [("C5", 3)],
            [("F5", 2), ("Eb5", 1)],
            [("D5", 3)],
            [("Bb4", 1), ("D5", 1), ("F5", 1)],
            [("Ab5", 2), ("F5", 1)],
            [("Eb5", 1), ("C5", 1), ("G4", 1)],
            [("B4", 3)],
            [("C5", 3)],
            [("C5", 3)],
        ],
        "akor": ["C:m", "C:m", "Ab:M", "C:m", "F:m", "G:M", "Bb:M", "F:m", "C:m", "G:M", "C:m", "C:m"],
    },
    "ucuncu": {
        "melodi": [
            [(None, 2), ("Eb4", 1)],
            [("G4", 1), ("C5", 1), ("Eb5", 1)],
            [("D5", 2), ("B4", 1)],
            [("C5", 2), ("G4", 1)],
            [("Ab4", 1), ("C5", 1), ("F5", 1)],
            [("Eb5", 2), ("D5", 1)],
            [("C5", 1), ("D5", 1), ("Eb5", 1)],
            [("F5", 2), ("D5", 1)],
            [("Eb5", 2), ("Bb4", 1)],
            [("B4", 1), ("D5", 1), ("G5", 1)],
            [("C5", 3)],
            [("C5", 3)],
        ],
        "akor": ["C:m", "C:m", "G:M", "C:m", "F:m", "Ab:M", "C:m", "Bb:M", "Eb:M", "G:M", "C:m", "C:m"],
    },
}

TUR = {"m": (0, 3, 7), "M": (0, 4, 7)}


def akor_notalari(akor: str, ton: int) -> list[int]:
    kok, tur = akor.split(":")
    k = midi(kok + "3") + ton
    while k < midi("F3") + ton:
        k += 12
    return [k + a for a in TUR[tur]]


def kamis(f_egri: np.ndarray, rng: np.random.Generator, parlak: float = 0.6, sesler=(-7, 0, 7)) -> np.ndarray:
    """Akordeon kamışı: zengin harmonikler (testere dişine yakın), musette için birkaç sent açık ikinci/üçüncü ses.

    f_egri: örnek başına frekans (legato kayışlar dahil)."""
    out = np.zeros_like(f_egri)
    for sent in sesler:
        f = f_egri * 2 ** (sent / 1200)
        faz = 2 * np.pi * np.cumsum(f) / SR + rng.uniform(0, 2 * np.pi)
        for h in range(1, 18):
            a = 1.0 / h ** parlak
            # kamışın tek/çift harmonik dengesi: çiftler biraz zayıf (kare ile testere arası)
            if h % 2 == 0:
                a *= 0.7
            # band dışına taşan harmonikleri at (aliasing yok)
            maske = (f * h) < SR * 0.45
            out += a * np.sin(h * faz) * maske
    return out / len(sesler)


def zarf(n: int, atak: float, birak: float) -> np.ndarray:
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(atak, 1e-4))
    kuyruk = int(birak * SR)
    if kuyruk and kuyruk < n:
        e[-kuyruk:] *= np.linspace(1, 0, kuyruk) ** 1.5
    return e


def uret(varyant: str, ton: int, tempo: float, tohum: int) -> np.ndarray:
    v = MELODILER[varyant]
    rng = np.random.default_rng(tohum)
    vurus = 60 / tempo
    olcu = 3 * vurus
    n = int(SURE * SR)
    t = np.arange(n) / SR

    # --- melodi: tek kesintisiz frekans eğrisi (legato), sus kısımlarında genlik 0
    f_egri = np.full(n, hz(midi("C5") + ton))
    gen = np.zeros(n)
    zaman = 0.0
    onceki = None
    notalar = []
    for olc in v["melodi"]:
        for nota, vur in olc:
            notalar.append((zaman, vur * vurus, nota))
            zaman += vur * vurus
    for i, (bas, sure, nota) in enumerate(notalar):
        a, b = int(bas * SR), min(n, int((bas + sure) * SR))
        if a >= n:
            break
        if nota is None:
            onceki = None
            continue
        hedef = hz(midi(nota) + ton)
        seg = np.full(b - a, hedef)
        if onceki is not None:  # 35 ms portamento: kamış notadan notaya kayar
            k = min(len(seg), int(0.035 * SR))
            seg[:k] = np.geomspace(onceki, hedef, k)
        f_egri[a:b] = seg
        # son kalış (son iki ölçü) videonun sonuna kadar sürer ve söner
        son = i == len(notalar) - 1 or all(x[2] == nota for x in notalar[i:])
        if son:
            f_egri[b:] = hedef
            gen[a:] = 1.0
        else:
            gen[a:b] = 1.0
        onceki = hedef
    # gecikmeli vibrato (nota başından 0,25 sn sonra açılır), 5,2 Hz, ±9 sent
    degisim = np.flatnonzero(np.abs(np.diff(f_egri)) > 0.5)
    sinir = np.zeros(n)
    noktalar = np.concatenate([[0], degisim, [n]])
    for a, b in zip(noktalar[:-1], noktalar[1:]):
        L = b - a
        if L <= 0:
            continue
        r = np.clip((np.arange(L) / SR - 0.25) / 0.4, 0, 1)
        sinir[a:b] = r
    vib = 9 * sinir * np.sin(2 * np.pi * 5.2 * t + rng.uniform(0, 6.28))
    f_egri = f_egri * 2 ** (vib / 1200)
    # genlik: yumuşak atak/bırakış (nota geçişlerinde kesintisiz: legato; yalnız susta kapanır)
    yumusak = np.convolve(gen, np.hanning(int(0.06 * SR)) / np.hanning(int(0.06 * SR)).sum(), mode="same")
    # körük nefesi: ölçü başına çok hafif şişme (orijinalde ~2-3 dB dalgalanma)
    korukl = 1 + 0.12 * np.sin(2 * np.pi * t / olcu - 1.2)
    lead = kamis(f_egri, rng) * yumusak * korukl

    # --- harmonyum altlığı: ölçü başına akor, tutulan; 2-3. vuruşta hafif kabarma (vals salınımı)
    alt = np.zeros(n)
    for k, akor in enumerate(v["akor"]):
        bas = k * olcu
        if bas >= SURE:
            break
        L = min(n - int(bas * SR), int((olcu + 0.05) * SR))
        tt = np.arange(L) / SR
        for j, m in enumerate(akor_notalari(akor, ton)):
            f = np.full(L, hz(m))
            ses = kamis(f, rng, parlak=1.25, sesler=(-4, 4)) * (0.5 if j == 0 else 0.38)
            alt[int(bas * SR):int(bas * SR) + L] += ses * zarf(L, 0.05, 0.08)
        # kök notası bir oktav aşağıda, vuruş 1'de ("um"), 2-3'te akorun kabarması ("pa pa")
        kok = hz(akor_notalari(akor, ton)[0] - 12)
        um = kamis(np.full(L, kok), rng, parlak=1.1, sesler=(0,)) * np.exp(-tt / 0.5) * 0.45
        alt[int(bas * SR):int(bas * SR) + L] += um * zarf(L, 0.02, 0.05)
        pa = 1 + 0.18 * sum(np.exp(-((tt - x * vurus) / 0.09) ** 2) for x in (1, 2))
        alt[int(bas * SR):int(bas * SR) + L] *= pa
    # son ölçülerde altlık da söner
    sonus = np.clip((SURE - t) / 1.6, 0, 1) ** 1.3
    karisim = 0.62 * lead + 0.30 * alt
    karisim *= sonus
    karisim *= np.minimum(1, t / 0.03)

    # --- gramofon: wow/flutter, doygunluk, hışırtı ve seyrek çıtırtı
    sap = 0.0028 * np.sin(2 * np.pi * 0.55 * t) + 0.0009 * np.sin(2 * np.pi * 6.7 * t)
    idx = np.clip(np.arange(n) + np.cumsum(sap - sap.mean()), 0, n - 1)
    karisim = np.interp(idx, np.arange(n), karisim)
    karisim = np.tanh(1.6 * karisim / (np.max(np.abs(karisim)) + 1e-9)) / np.tanh(1.6)
    hisirti = np.convolve(rng.normal(0, 1, n), np.ones(6) / 6, mode="same") * 0.012
    citirti = np.zeros(n)
    yer = rng.integers(0, n, size=int(SURE * 3))
    citirti[yer] = rng.uniform(-1, 1, len(yer)) * 0.12
    karisim = karisim + hisirti + citirti
    # oda yankısı (kısa)
    yank = karisim.copy()
    for gec, g in ((0.029, 0.22), (0.043, 0.17), (0.071, 0.12), (0.109, 0.08)):
        d = int(gec * SR)
        yank[d:] += g * karisim[:-d]
    return yank / (np.max(np.abs(yank)) + 1e-9) * 0.9


def yaz(sinyal: np.ndarray, cikti: Path) -> None:
    sol = sinyal
    sag = np.roll(sinyal, int(0.009 * SR)) * 0.97
    pcm = (np.stack([sol, sag], axis=1) * 32767).astype(np.int16).tobytes()
    cikti.parent.mkdir(parents=True, exist_ok=True)
    # gramofon hornu: 250 Hz altı ve 4 kHz üstü kesik, 630 Hz ve 1,6 kHz'te tepe (orijinalin 1/3 oktav tepeleri)
    af = ("highpass=f=240:poles=2,highpass=f=240:poles=2,lowpass=f=3900:poles=2,lowpass=f=4200:poles=2,"
          "equalizer=f=1600:t=q:w=1.3:g=5,equalizer=f=2600:t=q:w=1.5:g=1.5,equalizer=f=630:t=q:w=1.2:g=2,"
          "equalizer=f=380:t=q:w=1.4:g=-4,"
          "loudnorm=I=-16:TP=-2:LRA=7,afade=t=out:st=13.45:d=0.3")
    kod = ["-c:a", "aac", "-b:a", "192k"] if cikti.suffix == ".m4a" else ["-c:a", "pcm_s16le"]
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", "-",
                    "-af", af, "-ar", "44100", "-t", str(SURE), *kod, str(cikti)], input=pcm, check=True)


def karsilastir(bizim: Path, orijinal: Path) -> dict:
    """Ölçüm: tempo, ton, tını/spektrum benzerliği (yüksek olmalı) ve melodik benzerlik (düşük olmalı)."""
    import librosa

    def yukle(p: Path):
        with tempfile.TemporaryDirectory() as td:
            w = Path(td) / "a.wav"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(p), "-ac", "1", "-ar", "22050", str(w)],
                           check=True)
            y, _ = librosa.load(w, sr=22050)
        return y[: int(SURE * 22050)]

    a, b = yukle(bizim), yukle(orijinal)
    sr = 22050
    r = {}
    for ad, y in (("bizim", a), ("orijinal", b)):
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr, start_bpm=150)
        S = np.abs(librosa.stft(y, n_fft=4096)) ** 2
        fr = librosa.fft_frequencies(sr=sr, n_fft=4096)
        top = S.sum()
        bant = {k: float(S[(fr >= lo) & (fr < hi)].sum() / top) for k, (lo, hi) in
                {"<250": (0, 250), "250-1k": (250, 1000), "1-4k": (1000, 4000), ">4k": (4000, 1e9)}.items()}
        rms = librosa.feature.rms(y=y)[0]
        r[ad] = {"tempo": round(float(np.atleast_1d(tempo)[0]), 1), "bant": {k: round(v, 3) for k, v in bant.items()},
                 "merkez_hz": round(float((S.sum(1) * fr).sum() / S.sum()), 0),
                 "rms_oynama_db": round(float(np.percentile(20 * np.log10(rms + 1e-9), 90)
                                              - np.percentile(20 * np.log10(rms + 1e-9), 10)), 1)}
    ca = librosa.feature.chroma_cqt(y=a, sr=sr)
    cb = librosa.feature.chroma_cqt(y=b, sr=sr)
    pa, pb = ca.mean(1), cb.mean(1)
    r["ton_profili_benzerligi"] = round(float(np.corrcoef(pa, pb)[0, 1]), 3)   # yüksek: aynı ton/renk
    # zamana hizalı kroma (melodi + armoni dizisi): kare kare kosinüs, ±2 ölçü kaydırmanın en büyüğü
    L = min(ca.shape[1], cb.shape[1])
    ca, cb = ca[:, :L], cb[:, :L]
    ca_n = ca / (np.linalg.norm(ca, axis=0, keepdims=True) + 1e-9)
    cb_n = cb / (np.linalg.norm(cb, axis=0, keepdims=True) + 1e-9)
    # ortalama profili çıkar: geriye kalan, dizinin kendisi (hangi an hangi nota)
    ca_d = ca_n - ca_n.mean(1, keepdims=True)
    cb_d = cb_n - cb_n.mean(1, keepdims=True)
    hop = 512 / sr
    en = -1.0
    for kay in range(-int(2.4 / hop), int(2.4 / hop) + 1):
        x = ca_d[:, max(0, kay):L + min(0, kay)]
        y_ = cb_d[:, max(0, -kay):L - max(0, kay)]
        c = float((x * y_).sum() / (np.linalg.norm(x) * np.linalg.norm(y_) + 1e-9))
        en = max(en, c)
    r["dizi_benzerligi_en_yuksek"] = round(en, 3)  # düşük olmalı (aynı melodi ~0,6+)
    return r


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--varyant", default="imza", choices=sorted(MELODILER))
    ap.add_argument("--ton", type=int, default=0, help="yarım ses kaydırma (0 = Do minör)")
    ap.add_argument("--tempo", type=float, default=154.0)
    ap.add_argument("--tohum", type=int, default=1957)
    ap.add_argument("-o", "--cikti", type=Path)
    ap.add_argument("--karsilastir", type=Path, help="orijinal dosya: ölçüm raporu yazdır")
    a = ap.parse_args()
    cikti = a.cikti or (OUT if a.varyant == "imza" and a.ton == 0 else
                        OUT.with_name(f"imza_vals_{a.varyant}{'' if a.ton == 0 else f'_t{a.ton:+d}'}.m4a"))
    yaz(uret(a.varyant, a.ton, a.tempo, a.tohum), cikti)
    print(f"-> {cikti}")
    if a.karsilastir:
        print(json.dumps(karsilastir(cikti, a.karsilastir), ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
