#!/usr/bin/env python3
"""side-by-side zoom: waveform + linear-frequency spectrogram (0-4.5 kHz) of the original and candidate(s) over a time
window, same dB scale after loudness matching. usage: yakin.py <t0> <t1> <png> <cand.wav> [cand2.wav ...]"""
import sys, os, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "olcum"))
import olcum
import scipy.signal as ss
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
t0, t1, png = float(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
paths = [olcum.REF_WAV] + sys.argv[4:]
fig, axs = plt.subplots(2 * len(paths), 1, figsize=(16, 4.2 * len(paths)), gridspec_kw={"height_ratios": [1, 3] * len(paths)})
for i, p in enumerate(paths):
    y = olcum.decode(p)
    L = olcum.ebur128(p)["I"] or -29.5
    m = y.mean(1) * 10 ** ((-29.5 - L) / 20)
    x = m[int(t0 * 44100):int(t1 * 44100)]
    ta = t0 + np.arange(len(x)) / 44100
    axs[2 * i].plot(ta, x, lw=0.3, color="#2a78d6" if i == 0 else "#eb6834")
    axs[2 * i].set_xlim(t0, t1); axs[2 * i].set_ylim(-0.12, 0.12)
    axs[2 * i].set_title(("ORIGINAL" if i == 0 else os.path.basename(p)) + f"  (shown at -29.5 LUFS)", loc="left", fontsize=9)
    f, t, Z = ss.stft(x, 44100, nperseg=4096, noverlap=4096 - 256)
    S = 20 * np.log10(np.abs(Z) + 1e-9)
    mk = f <= 4500
    axs[2 * i + 1].imshow(S[mk], origin="lower", aspect="auto", cmap="magma", vmin=-95, vmax=-35,
                          extent=[t0 + t[0], t0 + t[-1], 0, f[mk][-1]])
    axs[2 * i + 1].set_ylabel("Hz")
fig.tight_layout(); fig.savefig(png, dpi=65)
