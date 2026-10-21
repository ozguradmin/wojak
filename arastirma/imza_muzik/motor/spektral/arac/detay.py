#!/usr/bin/env python3
"""detailed diagnostics with olcum.py internals: mel envelope diff per band, MFCC diff, modulation spectra per band,
accent per beat class, level stats. usage: detay.py <wav> [png]"""
import sys, os, json, pickle
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "olcum"))
import olcum
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

R = olcum.ref_features(olcum.REF_WAV)
C = olcum.features(sys.argv[1], with_cqt=False)
cm = olcum.compare(R, C)
print("TIMBRE", round(cm["TIMBRE_SCORE"], 1), {k: round(v, 1) for k, v in cm["subscores"].items()})
mf = np.array(R["melmfcc"]["mel_f"])
er, ec = np.array(R["melmfcc"]["mel_env"]), np.array(C["melmfcc"]["mel_env"])
sel = (mf >= 80) & (mf <= 6000)
print("mel env diff (cand-orig) by mel band:")
print(" ".join(f"{int(f)}:{d:+.1f}" for f, d in zip(mf[sel][::3], (ec - er)[sel][::3])))
d = np.array(C["melmfcc"]["mfcc_mean"]) - np.array(R["melmfcc"]["mfcc_mean"])
print("mfcc diff c1..c19:", " ".join(f"{x:+.1f}" for x in d))
print("mfcc std orig", " ".join(f"{x:.1f}" for x in R["melmfcc"]["mfcc_std"][:8]), "| cand", " ".join(f"{x:.1f}" for x in C["melmfcc"]["mfcc_std"][:8]))
Ms, Mc = np.array(R["mod"]["spec_db"]), np.array(C["mod"]["spec_db"])
e = np.array(R["mod"]["edges_hz"]); ce = np.sqrt(e[1:] * e[:-1])
print("modulation diff per band (rows 250-500,500-1k,1-2k,2-4k) at", " ".join(f"{x:.1f}" for x in ce))
for b in range(4):
    print("  ", " ".join(f"{x:+.1f}" for x in (Mc[b] - Ms[b])), " | orig", " ".join(f"{x:.0f}" for x in Ms[b]))
print("accent orig", {k: (np.round(v, 2).tolist() if isinstance(v, list) else round(v, 2)) for k, v in R["accent"].items()})
print("accent cand", {k: (np.round(v, 2).tolist() if isinstance(v, list) else round(v, 2)) for k, v in C["accent"].items()})
for k in ("rms100_std_db", "rms100_p10_p90_db", "fast_fluct_std_db", "crest50_median_db", "p2_level_re_median_db", "fastest_drop_db_s"):
    print(f"  {k:24s} orig {R['level'][k]:.2f} cand {C['level'][k]:.2f}")
print("  LRA orig", R["loud"].get("LRA"), "cand", C["loud"].get("LRA"))
pr, pc = R["pitch"], C["pitch"]
for k in ("vibrato_rms_c", "vibrato_rate_hz", "vibrato_peakiness", "pitch_dev_band_std_c", "pitch_dev_coherence_r", "partial_spread_c", "tuning_offset_c", "peaks_per_frame_median"):
    print(f"  {k:24s} orig {pr.get(k)} cand {pc.get(k)}")
print("  spec", {k: (round(R['spec'][k], 4), round(C['spec'][k], 4)) for k in ("centroid_hz", "frame_centroid_median_hz", "flatness_median", "flatness_core_median", "rolloff95_hz")})
if len(sys.argv) > 2:
    fig, axs = plt.subplots(2, 3, figsize=(18, 8))
    ax = axs[0, 0]; ax.semilogx(mf[sel], er[sel], label="orig"); ax.semilogx(mf[sel], ec[sel], label="cand"); ax.set_title("mel env"); ax.legend(); ax.grid(alpha=.3)
    ax = axs[0, 1]; ax.bar(np.arange(19) - 0.2, R["melmfcc"]["mfcc_mean"], 0.4, label="orig"); ax.bar(np.arange(19) + 0.2, C["melmfcc"]["mfcc_mean"], 0.4, label="cand"); ax.set_title("mfcc mean c1-19"); ax.legend()
    ax = axs[0, 2]; ax.bar(np.arange(19) - 0.2, R["melmfcc"]["mfcc_std"], 0.4); ax.bar(np.arange(19) + 0.2, C["melmfcc"]["mfcc_std"], 0.4); ax.set_title("mfcc std")
    for b in range(3):
        ax = axs[1, b]
        ax.semilogx(ce, Ms[b], label="orig"); ax.semilogx(ce, Mc[b], label="cand")
        ax.semilogx(ce, Ms[3], "--", color="C0", alpha=.5, label="orig 2-4k"); ax.semilogx(ce, Mc[3], "--", color="C1", alpha=.5, label="cand 2-4k")
        ax.set_title(["mod 250-500", "mod 500-1k", "mod 1-2k"][b]); ax.grid(alpha=.3); ax.legend(fontsize=7)
    fig.tight_layout(); fig.savefig(sys.argv[2], dpi=70)
