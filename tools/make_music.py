#!/usr/bin/env python3
"""Kanalın imza müziğini sentezler: "gece valsi" — ürkütücü müzik kutusu / gramofon valsi.

    python tools/make_music.py            # -> assets/music/imza_gece_vals.mp3 (32 sn, döngüye uygun)

Neden kendi müziğimiz: altın dönemde kullanılan ürpertici sesin hak sahibi belirsiz (büyük
ihtimalle "Phantomimes"). Başkasının parçasını dosyaya gömmek sessize alınma / telif talebi
riski taşır. Bu parça tamamen burada, matematiksel olarak üretilir: hakkı bize ait, üç
platformda da "orijinal ses" olarak gider. Melodi özgündür; yalnızca HİS benzer
(minör, 3/4 vals, müzik kutusu tınısı, plak cızırtısı, hafif akortsuzluk).
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np

SR = 44100
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "music" / "imza_gece_vals.mp3"
BPM = 132                      # vals: ölçü başına 3 vuruş
BEAT = 60 / BPM
RNG = np.random.default_rng(1959)


def hz(note: str) -> float:
    names = {"C": -9, "C#": -8, "D": -7, "D#": -6, "E": -5, "F": -4, "F#": -3, "G": -2, "G#": -1,
             "A": 0, "A#": 1, "B": 2}
    n, octave = note[:-1], int(note[-1])
    return 440.0 * 2 ** ((names[n] + 12 * (octave - 4)) / 12)


def music_box(freq: float, dur: float, vel: float = 1.0) -> np.ndarray:
    """Müzik kutusu tınısı: uyumsuz kısmi tonlar + hızlı sönüm + hafif akortsuzluk."""
    t = np.arange(int(SR * dur)) / SR
    detune = 1 + RNG.normal(0, 0.0025)  # eski, gergin yay hissi
    f = freq * detune
    partials = [(1.0, 1.0, 3.2), (2.0, 0.35, 5.0), (2.76, 0.25, 7.5), (5.4, 0.12, 11.0), (8.93, 0.05, 15.0)]
    sig = sum(a * np.sin(2 * np.pi * f * m * t) * np.exp(-d * t) for m, a, d in partials)
    attack = np.minimum(1, t / 0.004)
    return vel * sig * attack


def bass(freq: float, dur: float) -> np.ndarray:
    t = np.arange(int(SR * dur)) / SR
    return 0.55 * np.sin(2 * np.pi * freq * t) * np.exp(-2.2 * t) * np.minimum(1, t / 0.01)


def place(buf: np.ndarray, sig: np.ndarray, at: float) -> None:
    i = int(at * SR)
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i]


# Özgün melodi (La minör). Her ölçü 3 vuruş; (nota, vuruş sayısı)
MELODY = [
    [("E5", 1), ("A5", 1), ("C6", 1)], [("B5", 2), ("G#5", 1)],
    [("A5", 1), ("E5", 1), ("C5", 1)], [("D5", 3)],
    [("F5", 1), ("E5", 1), ("D5", 1)], [("C5", 1), ("B4", 1), ("A4", 1)],
    [("G#4", 1), ("B4", 1), ("E5", 1)], [("A4", 3)],
    [("E5", 1), ("A5", 1), ("C6", 1)], [("D6", 2), ("C6", 1)],
    [("B5", 1), ("A5", 1), ("F5", 1)], [("E5", 3)],
    [("D5", 1), ("F5", 1), ("A5", 1)], [("G#5", 1), ("F5", 1), ("D5", 1)],
    [("C5", 1), ("B4", 1), ("G#4", 1)], [("A4", 3)],
]
# Bas (ölçü başı) ve 2-3. vuruştaki yumuşak akor
HARMONY = ["A2", "E2", "A2", "D2", "D2", "A2", "E2", "A2", "A2", "D2", "F2", "E2", "D2", "E2", "E2", "A2"]
CHORDS = {"A2": ["A3", "C4", "E4"], "E2": ["G#3", "B3", "E4"], "D2": ["F3", "A3", "D4"], "F2": ["F3", "A3", "C4"]}


def compose(repeats: int = 2) -> np.ndarray:
    bar = 3 * BEAT
    total = len(MELODY) * bar * repeats + 2.5
    buf = np.zeros(int(SR * total))
    t = 0.0
    for r in range(repeats):
        for m, (notes, root) in enumerate(zip(MELODY, HARMONY)):
            beat_t = t
            for note, beats in notes:
                # ikinci turda bazı notalar oktav düşük ve biraz geç: "bozulan kutu"
                f = hz(note) / (2 if (r == 1 and m % 4 == 3) else 1)
                lag = RNG.uniform(0, 0.025) if r == 1 else 0
                place(buf, music_box(f, 2.2, 0.55), beat_t + lag)
                beat_t += beats * BEAT
            place(buf, bass(hz(root), bar), t)
            for k in (1, 2):
                for cn in CHORDS[root]:
                    place(buf, 0.12 * music_box(hz(cn), 0.9, 0.6), t + k * BEAT)
            t += bar
    return buf


def vinyl(n: int) -> np.ndarray:
    """Plak cızırtısı: seyrek tıklar + filtrelenmiş hışırtı."""
    crackle = np.zeros(n)
    idx = RNG.integers(0, n, size=n // 2500)
    crackle[idx] = RNG.uniform(-1, 1, size=len(idx)) * RNG.uniform(0.2, 1.0, size=len(idx))
    hiss = np.convolve(RNG.normal(0, 1, n), np.ones(30) / 30, mode="same")
    return 0.06 * crackle + 0.012 * hiss


def reverb(x: np.ndarray) -> np.ndarray:
    out = x.copy()
    for delay, g in ((0.031, 0.35), (0.047, 0.28), (0.073, 0.22), (0.113, 0.16), (0.167, 0.1)):
        d = int(delay * SR)
        out[d:] += g * x[:-d]
    return out


def main() -> None:
    mus = reverb(compose())
    # gramofon hoparlörü: bandı daralt (yüksek/alçak kes), hafif titreme (wow & flutter)
    n = len(mus)
    t = np.arange(n) / SR
    wow = 1 + 0.004 * np.sin(2 * np.pi * 0.55 * t)
    idx = np.clip((np.cumsum(wow) - 1).astype(int), 0, n - 1)
    mus = mus[idx]
    mus = mus + vinyl(n)
    mus = mus / np.max(np.abs(mus)) * 0.85
    stereo = np.stack([mus, np.roll(mus, int(0.012 * SR))], axis=1)
    pcm = (stereo * 32767).astype(np.int16).tobytes()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", "-",
                    "-af", "highpass=f=180,lowpass=f=5500,afade=t=in:d=0.05",
                    "-c:a", "libmp3lame", "-b:a", "160k", str(OUT)], input=pcm, check=True)
    print(f"-> {OUT.relative_to(ROOT)} ({n / SR:.1f} sn)")


if __name__ == "__main__":
    main()
