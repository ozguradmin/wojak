"""frame.py out.png wav:t ... : 186 ms frame spectra (8192 hann) 200-4500 Hz, linear frequency. measurement only"""
import sys, numpy as np, soundfile as sf, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
items = sys.argv[2:]
fig, ax = plt.subplots(len(items), 1, figsize=(20, 3.6 * len(items)), squeeze=False)
for i, it in enumerate(items):
    p, t = it.rsplit(':', 1); t = float(t)
    y, sr = sf.read(p, always_2d=True); m = y.mean(1)
    seg = m[int(t * sr):int(t * sr) + 8192] * np.hanning(8192)
    X = 20 * np.log10(np.abs(np.fft.rfft(seg)) + 1e-12); f = np.fft.rfftfreq(8192, 1 / sr)
    k = (f > 200) & (f < 4500)
    ax[i, 0].plot(f[k], X[k] - X[k].max(), lw=0.7); ax[i, 0].set_ylim(-80, 2); ax[i, 0].grid(alpha=.3)
    ax[i, 0].set_title(f"{p.split('/')[-1]} @ {t:.2f} s", loc='left')
plt.tight_layout(); plt.savefig(sys.argv[1], dpi=45)
