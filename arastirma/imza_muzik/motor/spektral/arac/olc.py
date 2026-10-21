#!/usr/bin/env python3
"""run the shared harness (olcum.py) on a render and print a compact comparison; saves full JSON + PNG.
usage: olc.py <wav> [--png out.png] [--notalar melody.json] [--tag name]"""
import json, os, subprocess, sys, argparse
HERE = os.path.dirname(os.path.abspath(__file__))
SP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OLCUM = os.path.join(SP, "olcum", "olcum.py")
ap = argparse.ArgumentParser()
ap.add_argument("wav")
ap.add_argument("--png")
ap.add_argument("--notalar")
ap.add_argument("--tag")
a = ap.parse_args()
cmd = [sys.executable, OLCUM, a.wav]
if a.png:
    cmd += ["--png", a.png]
if a.notalar:
    cmd += ["--notalar", a.notalar]
r = subprocess.run(cmd, capture_output=True, text=True)
if r.returncode != 0:
    print(r.stderr[-3000:])
    sys.exit(1)
d = json.loads(r.stdout)
tag = a.tag or os.path.splitext(os.path.basename(a.wav))[0]
os.makedirs(os.path.join(HERE, "..", "olcumler"), exist_ok=True)
json.dump(d, open(os.path.join(HERE, "..", "olcumler", tag + ".json"), "w"), indent=1)
print(f"TIMBRE_SCORE {d['TIMBRE_SCORE']}")
print("sub:", " ".join(f"{k}={v['score']}({v['dist']})" for k, v in d["timbre_subscores"].items()))
ti = d["timbre"]
keys = ["centroid_hz", "flatness", "vibrato_rms_c", "pitch_instability_c", "partial_spread_c", "glide_share",
        "tuning_offset_c", "texture_peaks_per_frame", "stereo_lr_corr", "level_std_100ms_db", "level_fast_fluct_db",
        "crest_50ms_db", "accent_uaa", "modulation", "noise_floor", "reverb_ir_env_db"]
for k in keys:
    v = ti.get(k)
    if v is None:
        continue
    extra = {kk: vv for kk, vv in v.items() if kk not in ("value", "original", "desc") and not isinstance(vv, (list, dict))}
    def f(x):
        if isinstance(x, list):
            return "[" + ",".join(f"{y:.1f}" if isinstance(y, (int, float)) else str(y) for y in x) + "]"
        if isinstance(x, dict):
            return "{" + ",".join(f"{kk}:{vv:.2f}" for kk, vv in x.items()) + "}"
        return f"{x:.3f}" if isinstance(x, float) else str(x)
    print(f"  {k:26s} cand {f(v['value'])}  orig {f(v['original'])}  {json.dumps(extra)[:160]}")
lt = ti.get("ltas_diff_by_band_db", {})
print("  ltas diff:", lt.get("value") if isinstance(lt, dict) and "value" in lt else lt)
t = d["technical"]
print("  tech:", {k: t[k]["value"] for k in ("first_sound_s", "last_sound_s", "lufs_integrated", "lra_lu", "true_peak_dbtp", "clicks", "hum_100hz_dbfs", "rumble_lt25hz_dbfs") if k in t})
mu = d["musical"]
print("  mus:", {k: mu[k]["value"] for k in ("tempo_bpm", "triple_metre", "key", "onsets_per_bar", "legato_gap_fraction") if k in mu})
print("  checks:", d.get("technical_checks"))
