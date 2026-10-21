"""per-band pitch-deviation curves exactly as olcum computes them; PSD of the curves and a plot. measurement only"""
import sys, numpy as np, soundfile as sf, scipy.signal as ss, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
sys.path.insert(0, '/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/olcum')
import olcum
def curves(path):
    y = olcum.decode(path)[:int(13.77 * 44100)]
    mid = y.mean(1)
    pt = olcum.peaks_and_tracks(mid, 0.05, 13.7)
    hop_s = pt["hop_s"]; cents = 1200 * np.log2(pt["pk_f"] / 440.0); d = (cents + 50) % 100 - 50
    th = 2 * np.pi * d / 100; wl = 10 ** ((pt["pk_a"] - pt["gmax"]) / 20); nfr = len(pt["t"])
    off = np.angle(np.sum(wl * np.exp(1j * th)))
    k = int(round(0.2 / hop_s)) | 1; win = np.hanning(k + 2)[1:-1]; out = []
    for lo, hi in ((240, 470), (480, 940), (1400, 2500)):
        m = (pt["pk_f"] >= lo) & (pt["pk_f"] < hi)
        br = np.bincount(pt["pk_fr"][m], (wl * np.cos(th - off))[m], nfr); bi = np.bincount(pt["pk_fr"][m], (wl * np.sin(th - off))[m], nfr)
        bw = np.bincount(pt["pk_fr"][m], wl[m], nfr)
        zs = np.convolve(br, win, "same") + 1j * np.convolve(bi, win, "same"); ws = np.convolve(bw, win, "same")
        c = np.angle(zs) * 100 / (2 * np.pi); pos = ws[ws > 0]; c[ws < 0.05 * np.median(pos)] = np.nan
        out.append(c)
    return pt["t"], np.array(out), off * 100 / (2 * np.pi)
fig, ax = plt.subplots(len(sys.argv) - 2, 1, figsize=(18, 4 * (len(sys.argv) - 2)), squeeze=False)
for i, p in enumerate(sys.argv[2:]):
    t, C, off = curves(p)
    st = [np.nanstd(c) for c in C]
    # PSD of each band curve (nan->0 after mean removal)
    fs = 1 / (t[1] - t[0]); rows = []
    for c in C:
        x = np.nan_to_num(c - np.nanmean(c)); f, P = ss.welch(x, fs, nperseg=512)
        rows.append([np.sqrt(P[(f >= a) & (f < b)].sum() * (f[1] - f[0])) for a, b in ((0, 0.5), (0.5, 2), (2, 5), (5, 20))])
    print(p.split('/')[-1], 'offset', round(off, 1), 'std', [round(s, 1) for s in st], 'rms by rate 0-.5/.5-2/2-5/5-20 Hz:', [[round(v, 1) for v in r] for r in rows])
    for j, c in enumerate(C): ax[i, 0].plot(t, c, lw=0.8, label=['240-470', '480-940', '1400-2500'][j])
    ax[i, 0].set_ylim(-60, 60); ax[i, 0].set_title(p.split('/')[-1]); ax[i, 0].legend(); ax[i, 0].grid(alpha=.3)
plt.tight_layout(); plt.savefig(sys.argv[1], dpi=45)
