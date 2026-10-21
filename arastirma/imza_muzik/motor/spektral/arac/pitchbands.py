"""per-register-band pitch deviation curves (olcum.py method) for any wav; plot for looking. measurement only."""
import sys, os, numpy as np, soundfile as sf
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "olcum"))
import olcum
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
def curves(path):
    y = olcum.decode(path)[: int(13.77 * 44100)]
    mid = y.mean(1)
    pt = olcum.peaks_and_tracks(mid, 0.0, len(mid) / 44100)
    hop_s = pt["hop_s"]
    cents = 1200 * np.log2(pt["pk_f"] / 440.0); d = (cents + 50) % 100 - 50; th = 2 * np.pi * d / 100
    wl = 10 ** ((pt["pk_a"] - pt["gmax"]) / 20); nfr = len(pt["t"])
    off = np.angle(np.sum(wl * np.exp(1j * th)))
    k = int(round(0.2 / hop_s)) | 1; win = np.hanning(k + 2)[1:-1]
    out = []
    for lo, hi in ((240, 470), (480, 940), (1400, 2500)):
        m = (pt["pk_f"] >= lo) & (pt["pk_f"] < hi)
        br = np.bincount(pt["pk_fr"][m], (wl * np.cos(th - off))[m], nfr); bi = np.bincount(pt["pk_fr"][m], (wl * np.sin(th - off))[m], nfr)
        bw = np.bincount(pt["pk_fr"][m], wl[m], nfr)
        zs = np.convolve(br, win, "same") + 1j * np.convolve(bi, win, "same"); ws = np.convolve(bw, win, "same")
        c = np.angle(zs) * 100 / (2 * np.pi); pos = ws[ws > 0]; c[ws < 0.05 * np.median(pos)] = np.nan
        out.append(c)
    return pt["t"], np.array(out), off * 100 / (2 * np.pi)
if __name__ == "__main__":
    paths = sys.argv[1:-1]; png = sys.argv[-1]
    fig, axs = plt.subplots(len(paths), 1, figsize=(18, 4 * len(paths)), squeeze=False)
    for ax, p in zip(axs[:, 0], paths):
        t, C, off = curves(p)
        for c, lab, col in zip(C, ["240-470", "480-940", "1400-2500"], ["#2a78d6", "#eb6834", "#2b9e5a"]):
            ax.plot(t, c, color=col, lw=1.2, label=f"{lab} std {np.nanstd(c):.1f}")
        ok = ~np.isnan(C).any(0)
        r = [np.corrcoef(C[i, ok], C[j, ok])[0, 1] for i, j in ((0, 1), (0, 2), (1, 2))]
        ax.set_title(f"{os.path.basename(p)}  offset {off:.1f} c   band r {np.round(r,2)}", loc="left", fontsize=10)
        ax.set_ylim(-60, 60); ax.set_xlim(0, 13.8); ax.set_xticks(np.arange(0, 13.9, 0.5)); ax.grid(alpha=0.3); ax.legend(fontsize=8, ncol=3)
    fig.tight_layout(); fig.savefig(png, dpi=70)
