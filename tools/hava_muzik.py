#!/usr/bin/env python3
"""Hava müzikleri: kısa reel'ler için konuya göre seçilen, bize ait 14 sn'lik müzik yatakları.

Hesap sahibi (12.11.2026): "sürekli aynı müzik sıkıyor". Kanalın imza valsi (`music: kanal`, hüzünlü) yanına farklı
havalarda parçalar: gizem, merak, ironik, destansı, masalsı. Besteler `tools/hava_besteler.py`'de (özgün; bilinen bir
ezgiden alıntı yok). Kanal tanınırlığı için her parça imza valsinin "5-4 | 3" düşen iç çekiş motifini bir yerde anar.

Ses kaynağı: MuseScore General SoundFont (MIT; içindeki yaylılar VSCO-2 CE, CC0; kuyruklu piyano kamu malı), Debian
paketi `musescore-general-soundfont-lossless` (/usr/share/sounds/sf2/MuseScore_General_Full.sf2). Kayıt ya da başka
bir parçadan ses yok. Yankı, eşitleme ve son işlem burada sentezlenir.

Akış: beste (nota listeleri) -> parça başına MIDI -> FluidSynth (yankısız, kuru kanal) -> numpy karışım (eşitleme,
ortak yankı) -> döngü: 14,0 sn'de kesilir, yankı kuyruğu başa sarılır (Instagram/YouTube reel'i döngüye alınca dikiş
duyulmasın) -> -14 LUFS, tepe <= -1,5 dBTP -> assets/music/hava/<ad>.m4a (+ out/hava/<ad>.wav, piyano rulosu PNG).

    python tools/hava_muzik.py gizem_a            # bir parça
    python tools/hava_muzik.py --hepsi            # hepsi
    python tools/hava_muzik.py --liste            # besteler
    python tools/hava_muzik.py --hepsi --dinleme  # hepsini tek dinleme videosunda topla (hesap sahibine)

Kurulum: apt-get install fluidsynth musescore-general-soundfont-lossless; pip install pyfluidsynth mido scipy soundfile
"""

from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SF2 = Path("/usr/share/sounds/sf2/MuseScore_General_Full.sf2")
SR = 48000
SURE = 14.0                      # reel süresi (STIL): parça tam bu uzunlukta döngü olur
HEDEF_LUFS = -14.0               # wojak/config.py LOUDNESS_LUFS ile aynı (31.10'dan beri)
HEDEF_TP = -1.5
KUYRUK = 4.0                     # yankı ve sönüm için kesimden sonra işlenen süre (sn)
CIKTI = ROOT / "assets" / "music" / "hava"
CALISMA = ROOT / "out" / "hava"

NOTA_ADLARI = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def m(ad: str) -> int:
    """'C#4' / 'Bb3' / 'F5' -> MIDI numarası (C4 = 60)."""
    r = re.fullmatch(r"([A-G])([#b]*)(-?\d)", ad.strip())
    if not r:
        raise ValueError(f"nota adı anlaşılmadı: {ad!r}")
    n = NOTA_ADLARI[r.group(1)] + r.group(2).count("#") - r.group(2).count("b")
    return 12 * (int(r.group(3)) + 1) + n


@dataclass
class Nota:
    bas: float          # vuruş (beste birimi)
    sure: float         # vuruş
    nota: int           # MIDI
    hiz: int = 80       # velocity


@dataclass
class Parca:
    ad: str
    program: int
    banka: int = 0
    davul: bool = False
    notalar: list[Nota] = field(default_factory=list)
    db: float = 0.0                 # karışım kazancı
    pan: float = 0.0                # -1 sol .. +1 sağ (MIDI CC10)
    yanki: float = 0.25             # ortak yankıya gönderim (0..1)
    eq: list = field(default_factory=list)   # [("hp", f), ("lp", f), ("raf_alt", f, dB), ("raf_ust", f, dB), ("tepe", f, dB, q)]
    ifade: list = field(default_factory=list)  # CC11: [(vuruş, 0..127), ...] doğrusal geçişli
    pedal: list = field(default_factory=list)  # CC64: [(vuruş, 0|127), ...]
    insan: float = 0.006            # zamanlama oynaması (sn, standart sapma)

    def ekle(self, bas, sure, nota, hiz=80):
        self.notalar.append(Nota(float(bas), float(sure), m(nota) if isinstance(nota, str) else int(nota), int(hiz)))
        return self


@dataclass
class Beste:
    ad: str                 # dosya adı: gizem_a
    hava: str               # gizem | merak | ironik | destansi | masal
    baslik: str             # "Saat"
    olcu: str               # "4/4", "6/8" (yalnız bilgi)
    vurus: float            # toplam vuruş (beste birimi); tempo = vurus*60/SURE
    parcalar: list[Parca]
    akorlar: list = field(default_factory=list)   # [(bas, sure, "Dm"), ...] denetim için
    not_: str = ""
    yanki_rt60: float = 1.8
    yanki_on: float = 0.022          # ön gecikme (sn)
    yanki_db: float = -14.0          # yankı dönüş seviyesi

    @property
    def bpm(self) -> float:
        return self.vurus * 60.0 / SURE

    def t(self, vurus: float) -> float:
        return vurus * 60.0 / self.bpm


# ------------------------------------------------------------------------------------------------- akor yardımcıları
AKOR_ARALIK = {"": (0, 4, 7), "m": (0, 3, 7), "dim": (0, 3, 6), "aug": (0, 4, 8), "sus4": (0, 5, 7), "sus2": (0, 2, 7),
               "7": (0, 4, 7, 10), "m7": (0, 3, 7, 10), "maj7": (0, 4, 7, 11), "m6": (0, 3, 7, 9), "6": (0, 4, 7, 9),
               "dim7": (0, 3, 6, 9), "m7b5": (0, 3, 6, 10), "7b9": (0, 4, 7, 10, 13), "add9": (0, 4, 7, 14),
               "madd9": (0, 3, 7, 14), "mmaj7": (0, 3, 7, 11), "7sus4": (0, 5, 7, 10), "maj7#11": (0, 4, 7, 11, 18),
               "9": (0, 4, 7, 10, 14), "m9": (0, 3, 7, 10, 14)}


def akor_sinifi(sembol: str) -> set[int]:
    """'Dm7' / 'Bbmaj7' / 'A7b9' / 'F/C' -> perde sınıfları (bas notası dahil)."""
    s, _, bas = sembol.partition("/")
    r = re.fullmatch(r"([A-G][#b]?)(.*)", s)
    if not r:
        raise ValueError(sembol)
    kok = m(r.group(1) + "4") % 12
    tur = r.group(2)
    if tur not in AKOR_ARALIK:
        raise ValueError(f"akor türü bilinmiyor: {sembol}")
    out = {(kok + a) % 12 for a in AKOR_ARALIK[tur]}
    if bas:
        out.add(m(bas + "4") % 12)
    return out


def ezgi(parca: Parca, metin: str, bas: float = 0.0, hiz: int = 80) -> float:
    """Kısa ezgi yazımı: 'A4:1 G4:1 | F4:3 r:1 E4:0.5. D4:0.5>' -> notalar. '|' yalnız okunurluk için; 'r' sus;
    sonda '.' kesik (sürenin %55'i), '>' vurgu (+14 hız), '<' yumuşak (-12), '_' bir sonrakine bağlı (legato %100).
    Bitiş vuruşunu döndürür."""
    t = bas
    for tok in metin.split():
        if tok == "|":
            continue
        ad, _, gerisi = tok.partition(":")
        r = re.fullmatch(r"([\d.]+?)([.>_<]*)", gerisi)
        if not r:
            raise ValueError(f"ezgi parçası anlaşılmadı: {tok!r}")
        sure = float(r.group(1))
        isaret = r.group(2)
        if ad != "r":
            v = hiz + (14 if ">" in isaret else 0) - (12 if "<" in isaret else 0)
            gercek = sure * (0.55 if "." in isaret else (1.0 if "_" in isaret else 0.94))
            parca.ekle(t, gercek, ad, max(1, min(127, v)))
        t += sure
    return t


# ------------------------------------------------------------------------------------------------- MIDI + FluidSynth
def _midi(parca: Parca, beste: Beste, yol: Path, tohum: int) -> None:
    import mido
    tpb = 960
    mf = mido.MidiFile(ticks_per_beat=tpb)
    tr = mido.MidiTrack()
    mf.tracks.append(tr)
    tr.append(mido.MetaMessage("set_tempo", tempo=int(round(60e6 / beste.bpm)), time=0))
    kanal = 9 if parca.davul else 0
    olaylar = []   # (tick, sıra, mesaj)
    if not parca.davul:
        olaylar += [(0, 0, mido.Message("control_change", channel=kanal, control=0, value=parca.banka)),
                    (0, 1, mido.Message("program_change", channel=kanal, program=parca.program))]
    else:
        olaylar += [(0, 1, mido.Message("program_change", channel=kanal, program=parca.program))]
    olaylar += [(0, 2, mido.Message("control_change", channel=kanal, control=7, value=110)),
                (0, 2, mido.Message("control_change", channel=kanal, control=10,
                                    value=int(round(64 + 63 * max(-1, min(1, parca.pan)))))),
                (0, 2, mido.Message("control_change", channel=kanal, control=91, value=0)),
                (0, 2, mido.Message("control_change", channel=kanal, control=93, value=0))]
    # ifade (CC11): doğrusal geçiş, 1/16 vuruş adımlı
    ifd = sorted(parca.ifade) or [(0.0, 110)]
    if ifd[0][0] > 0:
        ifd = [(0.0, ifd[0][1])] + ifd
    for (b0, v0), (b1, v1) in zip(ifd, ifd[1:] + [(ifd[-1][0], ifd[-1][1])]):
        adim = 1 / 16
        b = b0
        while b < b1 - 1e-9:
            v = v0 + (v1 - v0) * (b - b0) / (b1 - b0)
            olaylar.append((int(round(b * tpb)), 2, mido.Message("control_change", channel=kanal, control=11,
                                                                  value=int(round(v)))))
            b += adim
        olaylar.append((int(round(b1 * tpb)), 2, mido.Message("control_change", channel=kanal, control=11,
                                                               value=int(round(v1)))))
    for b, v in parca.pedal:
        olaylar.append((int(round(b * tpb)), 2, mido.Message("control_change", channel=kanal, control=64, value=v)))
    rng = np.random.default_rng(tohum)
    sn_basina_tick = tpb * beste.bpm / 60.0
    for n in parca.notalar:
        kay = rng.normal(0, parca.insan) * sn_basina_tick if parca.insan else 0
        a = max(0, int(round(n.bas * tpb + kay)))
        z = max(a + 1, int(round((n.bas + n.sure) * tpb + kay * 0.5)))
        hiz = int(max(1, min(127, n.hiz + rng.normal(0, 2.5))))
        olaylar.append((a, 4, mido.Message("note_on", channel=kanal, note=n.nota, velocity=hiz)))
        olaylar.append((z, 3, mido.Message("note_off", channel=kanal, note=n.nota, velocity=0)))
    son = int(round((beste.vurus + KUYRUK * beste.bpm / 60.0) * tpb))
    olaylar.append((son, 9, mido.Message("control_change", channel=kanal, control=11, value=0)))
    olaylar.sort(key=lambda x: (x[0], x[1]))
    onceki = 0
    for tick, _, msg in olaylar:
        msg.time = tick - onceki
        tr.append(msg)
        onceki = tick
    mf.save(str(yol))


def _cal(midi: Path, wav: Path) -> np.ndarray:
    subprocess.run(["fluidsynth", "-ni", "-q", "-F", str(wav), "-O", "float", "-r", str(SR), "-g", "0.6",
                    "-o", "synth.reverb.active=0", "-o", "synth.chorus.active=0", "-o", "synth.polyphony=512",
                    str(SF2), str(midi)], check=True, capture_output=True)
    import soundfile as sf
    x, sr = sf.read(str(wav), dtype="float32", always_2d=True)
    assert sr == SR, sr
    return x


# ------------------------------------------------------------------------------------------------- süzgeçler, yankı
def _biquad(tur: str, f: float, db: float = 0.0, q: float = 0.707) -> np.ndarray:
    """RBJ biquad -> sos satırı."""
    A = 10 ** (db / 40)
    w = 2 * math.pi * f / SR
    cs, sn = math.cos(w), math.sin(w)
    al = sn / (2 * q)
    if tur == "hp":
        b = [(1 + cs) / 2, -(1 + cs), (1 + cs) / 2]
        a = [1 + al, -2 * cs, 1 - al]
    elif tur == "lp":
        b = [(1 - cs) / 2, 1 - cs, (1 - cs) / 2]
        a = [1 + al, -2 * cs, 1 - al]
    elif tur == "tepe":
        b = [1 + al * A, -2 * cs, 1 - al * A]
        a = [1 + al / A, -2 * cs, 1 - al / A]
    elif tur in ("raf_alt", "raf_ust"):
        s = 2 * math.sqrt(A) * al
        if tur == "raf_alt":
            b = [A * ((A + 1) - (A - 1) * cs + s), 2 * A * ((A - 1) - (A + 1) * cs), A * ((A + 1) - (A - 1) * cs - s)]
            a = [(A + 1) + (A - 1) * cs + s, -2 * ((A - 1) + (A + 1) * cs), (A + 1) + (A - 1) * cs - s]
        else:
            b = [A * ((A + 1) + (A - 1) * cs + s), -2 * A * ((A - 1) + (A + 1) * cs), A * ((A + 1) + (A - 1) * cs - s)]
            a = [(A + 1) - (A - 1) * cs + s, 2 * ((A - 1) - (A + 1) * cs), (A + 1) - (A - 1) * cs - s]
    else:
        raise ValueError(tur)
    return np.array([[b[0] / a[0], b[1] / a[0], b[2] / a[0], 1.0, a[1] / a[0], a[2] / a[0]]])


def _eq(x: np.ndarray, eq: list) -> np.ndarray:
    from scipy.signal import sosfilt
    for e in eq:
        tur = e[0]
        if tur in ("hp", "lp"):
            sos = _biquad(tur, e[1], q=e[2] if len(e) > 2 else 0.707)
        elif tur == "tepe":
            sos = _biquad(tur, e[1], e[2], e[3] if len(e) > 3 else 1.0)
        else:
            sos = _biquad(tur, e[1], e[2], 0.707)
        x = sosfilt(sos, x, axis=0).astype(np.float32)
    return x


def yanki_ir(rt60: float, on: float, tohum: int = 7) -> np.ndarray:
    """Sentez oda yanıtı (stereo): ön gecikme, ilk yansımalar, frekansa göre sönen yoğun kuyruk. Kayıt değil."""
    from scipy.signal import sosfilt
    rng = np.random.default_rng(tohum)
    n = int(SR * (rt60 * 1.4 + on + 0.1))
    t = np.arange(n) / SR
    ir = np.zeros((n, 2), np.float32)
    o = int(on * SR)
    for k in range(2):
        # ilk yansımalar: 8 ayrık vuruş, 6-70 ms
        for d in np.sort(rng.uniform(0.006, 0.07, 8)):
            i = o + int(d * SR)
            ir[i, k] += rng.uniform(0.25, 0.6) * (1 if rng.random() > 0.5 else -1)
        kuyruk = rng.standard_normal(n).astype(np.float32)
        # yüksek frekans daha hızlı söner: üç bant, ayrı RT60
        bantlar = [("lp", 600, 1.15), (None, None, 1.0), ("hp", 4500, 0.55)]
        top = np.zeros(n, np.float32)
        ara = kuyruk.copy()
        alt = sosfilt(_biquad("lp", 600), kuyruk)
        ust = sosfilt(_biquad("hp", 4500), kuyruk)
        orta = ara - alt - ust
        for parca, kat in ((alt, 1.15), (orta, 1.0), (ust, 0.55)):
            zarf = np.exp(-6.91 * np.maximum(t - on, 0) / (rt60 * kat))
            top += (parca * zarf).astype(np.float32)
        top[: o] = 0
        # yumuşak başlangıç (kuyruk 30 ms'de yükselir)
        r = np.clip((t - on) / 0.03, 0, 1).astype(np.float32)
        ir[:, k] += top * r * 0.35
    ir /= np.sqrt((ir ** 2).sum() / 2)
    return ir


def _ebur(x: np.ndarray) -> tuple[float, float]:
    """(entegre LUFS, gerçek tepe dBTP) — ffmpeg ebur128."""
    import soundfile as sf
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "x.wav"
        sf.write(str(p), x, SR, subtype="FLOAT")
        r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(p), "-af", "ebur128=peak=true",
                            "-f", "null", "-"], capture_output=True, text=True)
    txt = r.stderr[r.stderr.rfind("Summary:"):]
    I = float(re.search(r"I:\s*(-?[\d.]+) LUFS", txt).group(1))
    tp = float(re.search(r"Peak:\s*(-?[\d.inf]+) dBFS", txt).group(1)) if "Peak:" in txt else 0.0
    return I, tp


def _sinirla(x: np.ndarray, tavan_db: float) -> np.ndarray:
    """Basit ileri bakışlı tepe sınırlayıcı (4x örneklemeli tepe ile), 5 ms atak, 80 ms bırakma."""
    from scipy.signal import resample_poly
    tavan = 10 ** (tavan_db / 20)
    tepe = np.abs(resample_poly(x, 4, 1, axis=0)).max(axis=1).reshape(-1, 4).max(axis=1)[: len(x)]
    if len(tepe) < len(x):
        tepe = np.pad(tepe, (0, len(x) - len(tepe)))
    kazanc = np.minimum(1.0, tavan / np.maximum(tepe, 1e-9))
    ileri = int(0.005 * SR)
    # ileri bakış: her örnek önümüzdeki 5 ms'nin en küçüğünü alır
    from scipy.ndimage import minimum_filter1d
    k = minimum_filter1d(kazanc, size=2 * ileri + 1, origin=0)
    birak = math.exp(-1 / (0.08 * SR))
    out = np.empty_like(k)
    g = 1.0
    for i in range(len(k)):          # tek kutuplu bırakma (kısa sinyal: 14 sn, hızlı yeter)
        g = k[i] if k[i] < g else k[i] + (g - k[i]) * birak
        out[i] = g
    return (x * out[:, None]).astype(np.float32)


# ------------------------------------------------------------------------------------------------- işleme
def isle(beste: Beste, tohum: int = 1) -> dict:
    import soundfile as sf
    CALISMA.mkdir(parents=True, exist_ok=True)
    CIKTI.mkdir(parents=True, exist_ok=True)
    L = int(round(SURE * SR))
    toplam = L + int(KUYRUK * SR)
    kuru = np.zeros((toplam, 2), np.float32)
    gonder = np.zeros((toplam, 2), np.float32)
    stemler: dict[str, np.ndarray] = {}
    with tempfile.TemporaryDirectory() as d:
        for i, p in enumerate(beste.parcalar):
            if not p.notalar:
                continue
            mid = Path(d) / f"{i}.mid"
            _midi(p, beste, mid, tohum * 100 + i)
            x = _cal(mid, Path(d) / f"{i}.wav")
            x = x[:toplam]
            if len(x) < toplam:
                x = np.pad(x, ((0, toplam - len(x)), (0, 0)))
            x = _eq(x, p.eq) * (10 ** (p.db / 20))
            kuru += x
            gonder += x * p.yanki
            stemler[p.ad] = x[:L]
    from scipy.signal import fftconvolve
    ir = yanki_ir(beste.yanki_rt60, beste.yanki_on, tohum)
    islak = np.stack([fftconvolve(gonder[:, k], ir[:, k])[:toplam] for k in range(2)], axis=1).astype(np.float32)
    islak *= 10 ** (beste.yanki_db / 20) * 4.0
    # döngü: kuru kısım kesimde 15 ms'de söner; yankı kuyruğu başa sarılır (reel tekrar başlayınca dikiş duyulmaz)
    out = kuru[:L].copy()
    fo = int(0.015 * SR)
    out[-fo:] *= np.linspace(1, 0.0, fo, dtype=np.float32)[:, None] ** 0.5
    out += islak[:L]
    kuyruk = islak[L:]
    out[: len(kuyruk)] += kuyruk[: L]
    out = _eq(out, [("hp", 28)])
    # seviye: -14 LUFS, sonra 4x tepe sınırlayıcı
    I, _ = _ebur(out)
    kazanc = HEDEF_LUFS - I
    # karışım dengesi: her parçanın (kuru) ve yankının son seviyedeki LUFS'u -> ezgi öne çıkıyor mu, bas boğuyor mu
    denge = {ad: round(_ebur(x)[0] + kazanc, 1) for ad, x in stemler.items()}
    denge["(yankı)"] = round(_ebur(islak[:L])[0] + kazanc, 1)
    out *= 10 ** (kazanc / 20)
    out = _sinirla(out, HEDEF_TP - 0.3)
    I2, tp2 = _ebur(out)
    out *= 10 ** ((HEDEF_LUFS - I2) / 20)
    out = _sinirla(out, HEDEF_TP - 0.3)
    I3, tp3 = _ebur(out)
    wav = CALISMA / f"{beste.ad}.wav"
    sf.write(str(wav), out, SR, subtype="FLOAT")
    m4a = CIKTI / f"{beste.ad}.m4a"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(wav), "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
                    "-movflags", "+faststart", str(m4a)], check=True)
    olc = {"ad": beste.ad, "hava": beste.hava, "baslik": beste.baslik, "olcu": beste.olcu, "bpm": round(beste.bpm, 2),
           "lufs": I3, "tp": tp3, "dikis_db": _dikis(out), "dosya": str(m4a.relative_to(ROOT)), "denge": denge,
           "uyarilar": denetle(beste)}
    _rulo(beste, CALISMA / f"{beste.ad}_rulo.png")
    _spektrogram(out, CALISMA / f"{beste.ad}_spek.png")
    (CALISMA / f"{beste.ad}.json").write_text(json.dumps(olc, ensure_ascii=False, indent=1), encoding="utf-8")
    return olc


def _dikis(x: np.ndarray) -> float:
    """Döngü dikişi: son 50 ms ile ilk 50 ms arasındaki RMS farkı (dB). Büyükse tekrar başlarken sıçrama duyulur."""
    n = int(0.05 * SR)
    a = np.sqrt((x[-n:] ** 2).mean() + 1e-12)
    b = np.sqrt((x[:n] ** 2).mean() + 1e-12)
    return round(20 * math.log10(b / a), 1)


def denetle(beste: Beste) -> list[str]:
    """Kaba armoni denetimi: güçlü vuruşta (tam vuruş başı, en az 1 vuruş süren) bir notanın, o anki akorda olmayıp
    başka bir parçanın tutan notasıyla küçük ikili (yarım ses) sürtüşmesi yapması. Bilinçli gecikmeler de çıkar:
    rapor dinlemeye yardımcıdır, hata listesi değil."""
    out = []
    akor_at = lambda b: next((a for (s, d, a) in beste.akorlar if s <= b < s + d), None)
    perdeli = [p for p in beste.parcalar if not p.davul]
    for p in perdeli:
        for n in p.notalar:
            if n.sure < 0.99 or abs(n.bas - round(n.bas)) > 1e-6:
                continue
            ak = akor_at(n.bas)
            if not ak:
                continue
            if n.nota % 12 in akor_sinifi(ak):
                continue
            for q in perdeli:
                if q is p:
                    continue
                for k in q.notalar:
                    if k.bas <= n.bas < k.bas + k.sure and abs((k.nota - n.nota) % 12) in (1, 11):
                        out.append(f"{p.ad} {n.bas:g}: {n.nota} akor dışı ({ak}), {q.ad} {k.nota} ile yarım ses")
                        break
    return out[:20]


def _rulo(beste: Beste, yol: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(14, 6), dpi=90)
    renk = plt.cm.tab10
    for i, p in enumerate(beste.parcalar):
        for n in p.notalar:
            ax.add_patch(plt.Rectangle((n.bas, n.nota - 0.4), n.sure, 0.8, color=renk(i % 10), alpha=0.5 + n.hiz / 300))
        if p.notalar:
            ax.plot([], [], color=renk(i % 10), label=p.ad, lw=6)
    for (s, d, a) in beste.akorlar:
        ax.axvline(s, color="k", lw=0.4, alpha=0.4)
        ax.text(s + 0.05, 101, a, fontsize=8)
    ax.set_xlim(0, beste.vurus)
    ax.set_ylim(24, 104)
    ax.set_title(f"{beste.ad} · {beste.baslik} · {beste.olcu} · {beste.bpm:.1f} bpm")
    ax.legend(loc="lower right", fontsize=7)
    fig.tight_layout()
    fig.savefig(yol)
    plt.close(fig)


def _spektrogram(x: np.ndarray, yol: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from scipy.signal import spectrogram
    f, t, S = spectrogram(x.mean(axis=1), SR, nperseg=4096, noverlap=3072)
    fig, ax = plt.subplots(figsize=(14, 4), dpi=90)
    ax.pcolormesh(t, f, 10 * np.log10(S + 1e-12), vmin=-120, vmax=-30, shading="auto", cmap="magma")
    ax.set_yscale("symlog", linthresh=200)
    ax.set_ylim(30, 16000)
    fig.tight_layout()
    fig.savefig(yol)
    plt.close(fig)


# ------------------------------------------------------------------------------------------------- dinleme videosu
def dinleme(adlar: list[str], besteler: dict) -> Path:
    """Hesap sahibi için tek video: her aday için numaralı kart + 14 sn müzik + 1 sn sessizlik."""
    from PIL import Image, ImageDraw, ImageFont
    CALISMA.mkdir(parents=True, exist_ok=True)
    yazi = None
    for aday in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",):
        if Path(aday).exists():
            yazi = aday
    parcalar = []
    with tempfile.TemporaryDirectory() as d:
        for i, ad in enumerate(adlar, 1):
            b = besteler[ad]()
            img = Image.new("RGB", (1080, 1080), (24, 24, 28))
            dr = ImageDraw.Draw(img)
            f1 = ImageFont.truetype(yazi, 120) if yazi else ImageFont.load_default()
            f2 = ImageFont.truetype(yazi, 64) if yazi else ImageFont.load_default()
            f3 = ImageFont.truetype(yazi, 40) if yazi else ImageFont.load_default()
            dr.text((540, 380), str(i), font=f1, fill=(240, 200, 80), anchor="mm")
            dr.text((540, 540), HAVA_ADI.get(b.hava, b.hava).replace("i", "İ").replace("ı", "I").upper(), font=f2, fill=(240, 240, 240), anchor="mm")
            dr.text((540, 640), f"music: {b.ad}  ·  {b.baslik}", font=f3, fill=(180, 180, 190), anchor="mm")
            if ad in KONU:
                dr.text((540, 720), KONU[ad], font=f3, fill=(130, 130, 140), anchor="mm")
            png = Path(d) / f"{i}.png"
            img.save(png)
            parca = Path(d) / f"{i}.mp4"
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", str(png), "-i", str(CIKTI / f"{ad}.m4a"),
                            "-f", "lavfi", "-t", "1", "-i", "anullsrc=r=44100:cl=stereo",
                            "-filter_complex", "[1:a][2:a]concat=n=2:v=0:a=1[a]", "-map", "0:v", "-map", "[a]",
                            "-t", f"{SURE + 1:.2f}", "-r", "30", "-c:v", "libx264", "-tune", "stillimage",
                            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "44100", str(parca)],
                           check=True)
            parcalar.append(parca)
        liste = Path(d) / "liste.txt"
        liste.write_text("".join(f"file '{p}'\n" for p in parcalar))
        out = CALISMA / "hava_dinleme.mp4"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(liste), "-c", "copy",
                        str(out)], check=True)
    return out


KONU = {  # dinleme kartındaki kısa kullanım (asıl tablo: docs/KISA_REEL_EL_KITABI.md §6)
    "gizem_a": "çözülmemiş gizem, kaybolma, soruşturma", "gizem_b": "ürkütücü yer, lanet, söylenti",
    "merak_a": "buluş, rekor, şaşırtıcı bilgi", "merak_b": "keşif, arkeoloji, bilim",
    "ironik_a": "kurnazlık, kandırmaca, sinsi plan", "ironik_b": "tuhaf olay, aksilik, ters köşe",
    "destansi_a": "zafer, kurtarma, direniş", "destansi_b": "anma, fedakârlık, onurlu ölüm",
    "masal_a": "efsane, kule, kehanet", "masal_b": "mit, rüya, halk masalı",
}

HAVA_ADI = {"gizem": "Gizem / gerilim", "merak": "Merak / keşif", "ironik": "İronik / hafif komik",
            "destansi": "Destansı / kahramanlık", "masal": "Masalsı / efsane", "huzun": "Hüzünlü"}


def main() -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import hava_besteler
    besteler = hava_besteler.BESTELER
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("adlar", nargs="*")
    ap.add_argument("--hepsi", action="store_true")
    ap.add_argument("--liste", action="store_true")
    ap.add_argument("--dinleme", action="store_true")
    ap.add_argument("--tohum", type=int, default=1)
    a = ap.parse_args()
    if a.liste:
        for ad, f in besteler.items():
            b = f()
            print(f"{ad:<14} {b.hava:<9} {b.baslik:<14} {b.olcu:<4} {b.bpm:6.1f} bpm  {b.not_[:70]}")
        return
    adlar = list(besteler) if a.hepsi else a.adlar
    for ad in adlar:
        olc = isle(besteler[ad](), a.tohum)
        print(f"{ad:<14} {olc['lufs']:6.1f} LUFS  tepe {olc['tp']:5.1f}  dikiş {olc['dikis_db']:+5.1f} dB  "
              f"uyarı {len(olc['uyarilar'])}  -> {olc['dosya']}")
        print("    denge (LUFS):", "  ".join(f"{k} {v}" for k, v in sorted(olc["denge"].items(), key=lambda kv: -kv[1])))
        for u in olc["uyarilar"][:8]:
            print("    ·", u)
    if a.dinleme:
        print("dinleme ->", dinleme(adlar, besteler))


if __name__ == "__main__":
    main()
