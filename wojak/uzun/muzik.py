"""Uzun video için kendi müzik altlığımız: karanlık, ölçülü belgesel ambiyansı (tamamen sentez, telifsiz).

Kanalın imzası Do minör bir vals; altlık da Do minörde kalır:
- Drone/pad: yavaşça değişen akorlar (Cm, Ab, Fm, G, Eb) — her bölüm 14-22 sn, 5 sn çapraz geçiş.
  Akor sırası tohumlu rastgele yürüyüşle seçilir: parça döngü gibi duyulmaz.
- Seyrek motif: 3/4 vals kalıbında kısa bir Do minör motif (G-C-Eb | D-C | B-C-D | G), her seferinde
  farklı varyant/oktav/tını (piyano ya da müzik kutusu), ortalama 25-30 sn'de bir.
- Hava: filtrelenmiş gürültü, çok düşük seviyede; alçak pedal (akor kökü).
- Yankı: sentetik darbe yanıtıyla FFT evrişimi.
- Kipler (`mod`, sahneden sahneye `muzik_mod` ile): drone (vars.), nabiz (alçak kalp atışı, ~64 vuruş/dk: geri
  sayım, takip), gerilim (tiz, titreyen yarım ton kümesi, bölüm boyunca crescendo: soruşturma), major (Do majör
  akorlar + majör motif: çözülme, ferahlık). `uret_bolumlu` kip değişimlerini 3 sn çapraz geçişle birleştirir;
  bölümler aynı RMS'e getirilir (kip değişince seviye zıplamaz, doku değişir).

    from wojak.uzun import muzik; x = muzik.uret(540, tohum=1957)   # (n, 2) float32, 48 kHz
    python tools/uzun_muzik.py --sure 540 --tohum 1957             # dosyaya yaz ve dinle
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np

SR = 48000
AKORLAR = {  # MIDI notaları (kök, ...): Do minör (armonik minörde G majör: gerilim)
    "Cm": [36, 43, 48, 51, 55],
    "Ab": [32, 39, 48, 51, 56],
    "Fm": [29, 36, 48, 53, 56],
    "G": [31, 38, 47, 50, 55],
    "Eb": [27, 34, 46, 51, 55],
}
GECIS = {"Cm": ["Ab", "Fm", "G", "Eb", "Ab"], "Ab": ["Fm", "Cm", "Eb", "G"], "Fm": ["G", "Cm", "Ab"],
         "G": ["Cm", "Ab", "Cm"], "Eb": ["Ab", "Fm", "Cm"]}
AKORLAR_MAJOR = {  # Do majör: çözülme (major kipi)
    "C": [36, 43, 48, 52, 55],
    "F": [29, 36, 48, 53, 57],
    "Am": [33, 40, 48, 52, 57],
    "G": [31, 38, 47, 50, 55],
    "Eb": [27, 34, 46, 51, 55],
}
GECIS_MAJOR = {"C": ["F", "Am", "G", "F"], "F": ["C", "G", "Am"], "Am": ["F", "C"], "G": ["C", "Am"],
               "Eb": ["F", "C"]}
MOTIFLER_MAJOR = [
    [(67, 1), (72, 1), (76, 1), (74, 2), (72, 1), (71, 1), (72, 1), (74, 1), (72, 3)],
    [(60, 1), (64, 1), (67, 1), (72, 3), (71, 1), (69, 1), (67, 1), (64, 3)],
]
MODLAR = ("drone", "nabiz", "gerilim", "major")
# motif: (nota MIDI, vuruş) — 3/4, vuruş = 0.8 sn civarı
MOTIFLER = [
    [(67, 1), (72, 1), (75, 1), (74, 2), (72, 1), (71, 1), (72, 1), (74, 1), (67, 3)],
    [(67, 1), (72, 1), (75, 1), (74, 3), (72, 1), (70, 1), (68, 1), (67, 3)],
    [(75, 1), (74, 1), (72, 1), (71, 2), (67, 1), (68, 1), (67, 1), (65, 1), (63, 3)],
    [(60, 1), (63, 1), (67, 1), (72, 3), (71, 1), (68, 1), (67, 1), (63, 3)],
]


def hz(m: float) -> float:
    return 440.0 * 2 ** ((m - 69) / 12)


def _pad_nota(f: float, n: int, rng) -> np.ndarray:
    t = np.arange(n, dtype=np.float32) / SR
    out = np.zeros(n, np.float32)
    for det in (-0.0009, 0.0008):
        ff = f * (1 + det + rng.normal(0, 0.0002))
        ph = rng.uniform(0, 2 * np.pi)
        for h, a in ((1, 1.0), (2, 0.18), (3, 0.05)):
            if ff * h > 4000:
                continue
            out += a * np.sin(2 * np.pi * ff * h * t + ph * h).astype(np.float32)
    lfo = 1 + 0.18 * np.sin(2 * np.pi * rng.uniform(0.04, 0.09) * t + rng.uniform(0, 6.28))
    return (out * lfo.astype(np.float32)) / 2.5


def _zarf(n: int, atak: float, birak: float) -> np.ndarray:
    e = np.ones(n, np.float32)
    a, r = int(atak * SR), int(birak * SR)
    if a:
        e[:a] = np.linspace(0, 1, a) ** 1.5
    if r:
        e[-r:] *= np.linspace(1, 0, r) ** 1.5
    return e


def piyano(f: float, sure: float = 4.5, hiz: float = 0.6, rng=None) -> np.ndarray:
    n = int(sure * SR)
    t = np.arange(n, dtype=np.float32) / SR
    B = 0.00035
    out = np.zeros(n, np.float32)
    for k in range(1, 9):
        fk = f * k * np.sqrt(1 + B * k * k)
        if fk > 9000:
            break
        a = (1.0 / k ** 1.25) * (1.0 if k > 1 else 1.1)
        d = 0.55 + 0.45 * k
        for det in (-0.0003, 0.0003):
            out += a * np.sin(2 * np.pi * fk * (1 + det) * t) * np.exp(-d * t)
    out *= np.minimum(1, t / 0.003)
    return (hiz * out / 4).astype(np.float32)


def muzik_kutusu(f: float, sure: float = 2.8, hiz: float = 0.5) -> np.ndarray:
    n = int(sure * SR)
    t = np.arange(n, dtype=np.float32) / SR
    out = np.zeros(n, np.float32)
    for m, a, d in ((1.0, 1.0, 2.6), (2.0, 0.3, 4.5), (2.76, 0.22, 7.0), (5.4, 0.1, 10.0), (8.93, 0.04, 14.0)):
        if f * m > 12000:
            continue
        out += a * np.sin(2 * np.pi * f * m * t) * np.exp(-d * t)
    out *= np.minimum(1, t / 0.003)
    return (hiz * out / 2).astype(np.float32)


def _yerlestir(buf: np.ndarray, sig: np.ndarray, i: int) -> None:
    if i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i]


def _renkli_gurultu(n: int, rng, lo: float, hi: float) -> np.ndarray:
    x = rng.normal(0, 1, n).astype(np.float32)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    g = np.exp(-0.5 * (np.log(np.maximum(f, 1) / np.sqrt(lo * hi)) / np.log(hi / lo) * 2.2) ** 2)
    y = np.fft.irfft(X * g, n).astype(np.float32)
    return y / (np.abs(y).max() + 1e-9)


def _yanki_ir(sure: float, rng, rt60: float = 3.2) -> np.ndarray:
    n = int(sure * SR)
    t = np.arange(n) / SR
    env = np.exp(-6.91 * t / rt60)
    ir = np.zeros((n, 2), np.float32)
    for ch in range(2):
        w = rng.normal(0, 1, n) * env
        k = 24  # kuyruğu koyulaştır (basit alçak geçiren)
        w = np.convolve(w, np.ones(k) / k, mode="same")
        ir[:, ch] = w
    pre = int(0.025 * SR)
    ir = np.concatenate([np.zeros((pre, 2), np.float32), ir])
    return ir / np.sqrt((ir ** 2).sum(axis=0, keepdims=True)) * 0.6


def _evris(x: np.ndarray, ir: np.ndarray) -> np.ndarray:
    """Blok blok FFT evrişimi (overlap-add); x mono, ir (m, 2) -> (len(x), 2)."""
    m = len(ir)
    blok = 1 << 18
    nfft = 1 << int(np.ceil(np.log2(blok + m)))
    IR = [np.fft.rfft(ir[:, c], nfft) for c in range(2)]
    out = np.zeros((len(x) + m, 2), np.float32)
    for i in range(0, len(x), blok):
        seg = x[i:i + blok]
        S = np.fft.rfft(seg, nfft)
        for c in range(2):
            y = np.fft.irfft(S * IR[c], nfft)[: len(seg) + m]
            out[i:i + len(y), c] += y.astype(np.float32)
    return out[: len(x)]


def _kalp(n: int, rng, bpm: float = 64.0) -> np.ndarray:
    """Alçak kalp atışı (lub-dub): perdesi düşen sinüs darbeleri, yumuşak."""
    out = np.zeros(n, np.float32)
    per = 60.0 / bpm
    m = int(0.42 * SR)
    t = np.arange(m, dtype=np.float32) / SR
    def vurus(f0, f1, a):
        f = f1 + (f0 - f1) * np.exp(-t / 0.05)
        ph = 2 * np.pi * np.cumsum(f) / SR
        return (a * np.sin(ph) * np.exp(-t / 0.11) * np.minimum(1, t / 0.004)).astype(np.float32)
    lub, dub = vurus(78, 44, 1.0), vurus(70, 42, 0.62)
    tt = float(rng.uniform(0.1, 0.4))
    while tt < n / SR:
        _yerlestir(out, lub, int(tt * SR))
        _yerlestir(out, dub, int((tt + 0.27) * SR))
        tt += per * float(rng.uniform(0.985, 1.015))
    return out


def _gerilim(n: int, rng) -> np.ndarray:
    """Tiz, titreyen yarım ton kümesi (G5-Ab5 + D6), bölüm boyunca yavaşça yükselir (crescendo)."""
    t = np.arange(n, dtype=np.float32) / SR
    out = np.zeros(n, np.float32)
    for nn, a in ((79, 1.0), (80, 0.7), (86, 0.35)):
        f = hz(nn) * (1 + rng.normal(0, 0.0004))
        trem = 1 + 0.35 * np.sin(2 * np.pi * float(rng.uniform(5.2, 6.4)) * t + rng.uniform(0, 6.28))
        out += a * np.sin(2 * np.pi * f * t + rng.uniform(0, 6.28)).astype(np.float32) * trem.astype(np.float32)
    kres = (0.25 + 0.75 * (t / max(t[-1], 1e-6)) ** 1.6).astype(np.float32)
    return out * kres / 2.0


def uret(sure: float, tohum: int = 1957, motif_sikligi: float = 27.0, mod: str = "drone",
         kenar: bool = True) -> np.ndarray:
    """sure sn uzunluğunda stereo altlık (float32, 48 kHz, tepe ~ -1 dBFS). kenar=False: giriş/çıkış sönümü yok
    (uret_bolumlu'nun iç bölümleri)."""
    if mod not in MODLAR:
        raise ValueError(f"müzik kipi '{mod}': {' | '.join(MODLAR)}")
    rng = np.random.default_rng(int(tohum))
    akorlar, gecisler, motifler = ((AKORLAR_MAJOR, GECIS_MAJOR, MOTIFLER_MAJOR) if mod == "major"
                                   else (AKORLAR, GECIS, MOTIFLER))
    n = int(sure * SR) + SR
    pad = np.zeros(n, np.float32)
    pedal = np.zeros(n, np.float32)
    motif = np.zeros(n, np.float32)
    xfade = 5.0
    t = 0.0
    akor = "C" if mod == "major" else "Cm"
    bolumler = []
    while t < sure + 1:
        L = float(rng.uniform(14, 22))
        bolumler.append((t, L, akor))
        t += L
        akor = str(rng.choice(gecisler[akor]))
    for (t0, L, ak) in bolumler:
        i0 = max(0, int((t0 - xfade / 2) * SR))
        m = int((L + xfade) * SR)
        sig = np.zeros(m, np.float32)
        notalar = akorlar[ak]
        for j, nn in enumerate(notalar):
            if j > 0 and rng.random() < 0.25:   # bazı akor tonlarını atla: doku değişsin
                continue
            sig += _pad_nota(hz(nn), m, rng) * (1.0 if j == 0 else 0.38)
        sig *= _zarf(m, xfade, xfade)
        _yerlestir(pad, sig, i0)
        pn = notalar[0] - 12 if hz(notalar[0] - 12) >= 36 else notalar[0]   # duyulmayan <36 Hz yok
        ped = np.sin(2 * np.pi * hz(pn) * np.arange(m) / SR).astype(np.float32)
        _yerlestir(pedal, ped * _zarf(m, xfade, xfade) * 0.6, i0)
        # bölüm başında bazen alçak, yumuşak bir piyano notası
        if rng.random() < 0.45:
            _yerlestir(motif, piyano(hz(notalar[0] + 12), 5.0, 0.35), int(t0 * SR) + int(rng.uniform(0.2, 2) * SR))
    # seyrek motifler
    tm = float(rng.uniform(6, 14)) if mod != "major" else float(rng.uniform(0.8, 2.0))
    if mod == "nabiz":
        motif_sikligi *= 1.6   # nabızda motif seyrek: ritim kalp atışında
    while tm < sure - (8 if kenar else 2):
        var = motifler[int(rng.integers(len(motifler)))]
        oktav = int(rng.choice([0, 0, 12, -12]))
        kutu = rng.random() < 0.45
        vurus = float(rng.uniform(0.72, 0.86))
        kisalt = rng.random() < 0.35
        notlar = var[: max(3, len(var) // 2)] if kisalt else var
        ti = tm
        for k, (nn, b) in enumerate(notlar):
            h = hz(nn + oktav)
            v = float(rng.uniform(0.4, 0.62)) * (0.85 if k % 3 else 1.0)
            sig = muzik_kutusu(h * 2, 2.6, v * 0.5) if kutu else piyano(h, 4.0, v)
            _yerlestir(motif, sig, int((ti + rng.uniform(0, 0.02)) * SR))
            ti += b * vurus
        tm = ti + float(rng.uniform(0.6, 1.4)) * motif_sikligi
    hava = _renkli_gurultu(n, rng, 250, 2500) * 0.035
    hava *= (0.6 + 0.4 * np.sin(2 * np.pi * 0.031 * np.arange(n) / SR)).astype(np.float32)
    ir = _yanki_ir(3.4, rng)
    ir_pad = _yanki_ir(2.2, rng, rt60=2.2)
    st = np.zeros((n, 2), np.float32)
    kuru = 0.55 * pad + 0.5 * pedal
    st += kuru[:, None] * np.array([[1.0, 0.94]], np.float32)
    st += 0.35 * _evris(pad, ir_pad)
    st += 0.55 * motif[:, None] + 0.75 * _evris(motif, ir)
    st += np.stack([hava, np.roll(hava, 1500)], axis=1)
    if mod == "nabiz":
        k = _kalp(n, rng)
        st *= 0.8
        st += 0.9 * k[:, None] + 0.25 * _evris(k, ir_pad)
    elif mod == "gerilim":
        g = _gerilim(n, rng)
        st += 0.16 * g[:, None] * np.array([[0.9, 1.0]], np.float32) + 0.22 * _evris(g, ir_pad)
    st = st[: int(sure * SR)]
    if kenar:   # giriş/çıkış
        fi, fo = min(int(3.0 * SR), len(st) // 3), min(int(4.0 * SR), len(st) // 3)   # kısa parçada da çalışsın
        st[:fi] *= np.linspace(0, 1, fi, dtype=np.float32)[:, None]
        st[-fo:] *= np.linspace(1, 0, fo, dtype=np.float32)[:, None]
        st /= np.abs(st).max() + 1e-9
        return (st * 0.89).astype(np.float32)
    return st.astype(np.float32)


def _rms(x: np.ndarray) -> float:
    return float(np.sqrt((x.astype(np.float64) ** 2).mean() + 1e-12))


def uret_bolumlu(sure: float, tohum: int, bolumler: list[tuple[float, str]], xfade: float = 3.0) -> np.ndarray:
    """Kip değişen altlık: bolumler = [(başlangıç sn, kip), ...] (ilki 0). Her bölüm kendi tohumuyla üretilir,
    aynı RMS'e getirilir ve eşit güçlü çapraz geçişle (xfade sn, sınırın ortasında) birleştirilir."""
    bl = sorted((max(0.0, float(t)), str(m)) for t, m in bolumler)
    if not bl or bl[0][0] > 0:
        bl = [(0.0, "drone")] + bl
    tek = [bl[0]]
    for t, m in bl[1:]:   # aynı kip art arda gelirse birleştir; çok kısa bölüm (< 2 xfade) bir öncekine katılır
        if m == tek[-1][1] or t - tek[-1][0] < 2 * xfade:
            if t - tek[-1][0] < 2 * xfade and m != tek[-1][1] and len(tek) > 1 and tek[-1][0] > 0:
                tek[-1] = (tek[-1][0], m)
            continue
        tek.append((t, m))
    if len(tek) == 1:
        return uret(sure, tohum, mod=tek[0][1])
    n = int(sure * SR)
    out = np.zeros((n, 2), np.float32)
    hedef = None
    h = int(xfade * SR / 2)
    for k, (t0, m) in enumerate(tek):
        t1 = tek[k + 1][0] if k + 1 < len(tek) else sure
        a, b = max(0, int(t0 * SR) - h), min(n, int(t1 * SR) + h)
        x = uret((b - a) / SR + 0.05, tohum + 101 * k, mod=m, kenar=False)[: b - a]   # kayan nokta: 1 örnek eksik kalmasın
        if len(x) < b - a:
            x = np.concatenate([x, np.zeros((b - a - len(x), 2), np.float32)])
        r = _rms(x)
        hedef = hedef or r
        x *= hedef / r
        w = np.ones(b - a, np.float32)
        if k > 0:
            q = np.linspace(0, 1, 2 * h, dtype=np.float32)
            w[: 2 * h] = np.sin(q * np.pi / 2)
        if k + 1 < len(tek):
            q = np.linspace(0, 1, 2 * h, dtype=np.float32)
            w[-2 * h:] *= np.cos(q * np.pi / 2)
        out[a:b] += x * w[:, None]
    fi, fo = min(int(3.0 * SR), n // 3), min(int(4.0 * SR), n // 3)
    out[:fi] *= np.linspace(0, 1, fi, dtype=np.float32)[:, None]
    out[-fo:] *= np.linspace(1, 0, fo, dtype=np.float32)[:, None]
    out /= np.abs(out).max() + 1e-9
    return (out * 0.89).astype(np.float32)


def kaydet(x: np.ndarray, yol: Path) -> Path:
    yol = Path(yol)
    yol.parent.mkdir(parents=True, exist_ok=True)
    pcm = (np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes()
    args = ["-c:a", "libmp3lame", "-b:a", "192k"] if yol.suffix == ".mp3" else ["-c:a", "pcm_s16le"]
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", "-",
                    *args, str(yol)], input=pcm, check=True)
    return yol
