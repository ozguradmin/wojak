#!/usr/bin/env python3
"""spek.py out.png wav1[:label] wav2[:label] ... [--t0 A --t1 B --fmax F]
Side-by-side STFT spectrograms (mid channel, loudness-normalised by RMS) + 10 ms level envelopes. Measurement only."""
import argparse, numpy as np, soundfile as sf, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ORIG = "/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik/orijinal.wav"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("png")
    ap.add_argument("wavs", nargs="+")
    ap.add_argument("--t0", type=float, default=0.0)
    ap.add_argument("--t1", type=float, default=13.77)
    ap.add_argument("--fmax", type=float, default=6000)
    ap.add_argument("--nfft", type=int, default=4096)
    ap.add_argument("--orig", action="store_true", help="prepend the original (same window)")
    ap.add_argument("--ot0", type=float, default=None, help="original window start (default t0)")
    a = ap.parse_args()
    items = []
    if a.orig:
        items.append((ORIG, "ORIGINAL", a.ot0 if a.ot0 is not None else a.t0))
    for w in a.wavs:
        p, _, lab = w.partition(":")
        items.append((p, lab or p.split("/")[-1], a.t0))
    fig, ax = plt.subplots(len(items), 2, figsize=(22, 4.2 * len(items)), gridspec_kw={"width_ratios": [4, 1]},
                           squeeze=False)
    for i, (p, lab, t0) in enumerate(items):
        y, sr = sf.read(p, always_2d=True)
        m = y.mean(1)[int(t0 * sr):int((t0 + a.t1 - a.t0) * sr)]
        m = m / (np.sqrt(np.mean(m ** 2)) + 1e-12) * 0.03
        hop = 128
        w = np.hanning(a.nfft)
        fr = np.lib.stride_tricks.sliding_window_view(np.r_[m, np.zeros(a.nfft)], a.nfft)[::hop]
        X = np.abs(np.fft.rfft(fr * w, axis=1)).T
        Xd = 20 * np.log10(X + 1e-9)
        f = np.fft.rfftfreq(a.nfft, 1 / sr)
        k = f <= a.fmax
        ax[i, 0].imshow(Xd[k], origin="lower", aspect="auto", extent=[t0, t0 + len(m) / sr, 0, a.fmax],
                        vmin=Xd[k].max() - 75, vmax=Xd[k].max() - 5, cmap="magma")
        ax[i, 0].set_title(lab, loc="left", fontsize=11)
        ax[i, 0].set_ylabel("Hz")
        # LTAS of the window
        P = (X ** 2).mean(1)
        ax[i, 1].semilogx(f[1:], 10 * np.log10(P[1:] + 1e-20), lw=0.6)
        ax[i, 1].set_xlim(100, 10000)
        ax[i, 1].set_ylim(10 * np.log10(P.max()) - 80, 10 * np.log10(P.max()) + 3)
        ax[i, 1].grid(alpha=0.3, which="both")
    plt.tight_layout()
    plt.savefig(a.png, dpi=45)


if __name__ == "__main__":
    main()
