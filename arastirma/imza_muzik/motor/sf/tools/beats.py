#!/usr/bin/env python3
"""beats.py wav bpm downbeat_s [end_s]: per beat position (1,2,3): peak level 0-120 ms after the beat in 250-500 Hz,
1-4 kHz and 250-4000 Hz (same STFT as olcum accent_pattern), mean over bars. Measurement only.
Original: beats.py orijinal.wav 151.5 -0.152"""
import sys, numpy as np, soundfile as sf, librosa

p, bpm, d0 = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
end = float(sys.argv[4]) if len(sys.argv) > 4 else 11.4
y, sr = sf.read(p, always_2d=True)
y22 = librosa.resample(y.mean(1), orig_sr=sr, target_sr=22050)
S = np.abs(librosa.stft(y22, n_fft=1024, hop_length=128)) ** 2
fr = librosa.fft_frequencies(sr=22050, n_fft=1024)
db = lambda x: 10 * np.log10(x + 1e-20)
lo = db(S[(fr >= 250) & (fr < 500)].sum(0)); hi = db(S[(fr >= 1000) & (fr < 4000)].sum(0)); al = db(S[(fr >= 250) & (fr < 4000)].sum(0))
fps = 22050 / 128; P = 60 / bpm
rows = {0: [], 1: [], 2: []}
k = 0
while d0 + k * P < end:
    t0 = d0 + k * P
    if t0 >= 0.05:
        i0, i1 = int(t0 * fps), int((t0 + 0.12) * fps) + 1
        rows[k % 3].append((lo[i0:i1].max(), hi[i0:i1].max(), al[i0:i1].max()))
    k += 1
A = {b: np.mean(np.array(v), 0) for b, v in rows.items()}
for b in range(3):
    l, h, a = A[b]
    print(f"beat {b+1}: L250-500 {l - A[0][0]:+5.1f}  L1-4k {h - A[0][1]:+5.1f}  tilt {h - l - (A[0][1] - A[0][0]):+5.1f}  level {a - A[0][2]:+5.1f}")
