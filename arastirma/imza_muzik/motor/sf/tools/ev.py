#!/usr/bin/env python3
"""ev.py <wav> <tag> [--log "change"] [--melody json]: run olcum.py on a render, save JSON+PNG, print a compact table,
optionally append a row to ../log.md. Measurement only."""
import argparse, json, os, subprocess, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SFD = os.path.dirname(HERE)
OLCUM = os.path.abspath(os.path.join(SFD, "..", "..", "olcum", "olcum.py"))


def g(d, *ks, default=None):
    for k in ks:
        if not isinstance(d, dict) or k not in d:
            return default
        d = d[k]
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("wav")
    ap.add_argument("tag")
    ap.add_argument("--log")
    ap.add_argument("--melody")
    a = ap.parse_args()
    os.makedirs(os.path.join(SFD, "out"), exist_ok=True)
    os.makedirs(os.path.join(SFD, "png"), exist_ok=True)
    jp = os.path.join(SFD, "out", a.tag + ".olcum.json")
    pp = os.path.join(SFD, "png", a.tag + "_olcum.png")
    cmd = [sys.executable, OLCUM, a.wav, "--png", pp]
    if a.melody:
        cmd += ["--notalar", a.melody]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-3000:])
        sys.exit(1)
    J = json.loads(r.stdout)
    open(jp, "w").write(r.stdout)
    S = J["timbre_subscores"]
    T = J["timbre"]
    tech = J["technical"]
    print(f"TIMBRE_SCORE {J['TIMBRE_SCORE']}  (olcum {J.get('olcum_version')})")
    print("  " + "  ".join(f"{k}:{v['score']:.0f}({v['dist']:.3g})" for k, v in S.items()))
    def vo(k, sub=None):
        m = T.get(k, {})
        return m.get("value") if sub is None else m.get(sub), m.get("original") if sub is None else m.get(sub + "_original")
    rows = [
        ("flatness", vo("flatness")),
        ("centroid", vo("centroid_hz")),
        ("mod 0.5-2/2-8/8-20", (g(T, "modulation", "value"), g(T, "modulation", "original"))),
        ("vibrato_c", vo("vibrato_rms_c")),
        ("pitch_instab_c", vo("pitch_instability_c")),
        ("common_std_c", (g(T, "pitch_instability_c", "common_std_c"), g(T, "pitch_instability_c", "common_std_c_original"))),
        ("glide_share", vo("glide_share")),
        ("partial_spread", vo("partial_spread_c")),
        ("peaks/frame", vo("texture_peaks_per_frame")),
        ("tuning_c", vo("tuning_offset_c")),
        ("lr_corr", vo("stereo_lr_corr")),
        ("side_mid", (g(T, "stereo_lr_corr", "side_mid_db"), g(T, "stereo_lr_corr", "side_mid_db_original"))),
        ("rev_ir", vo("reverb_ir_env_db")),
        ("lvl_std100", vo("level_std_100ms_db")),
        ("fast_fluct", vo("level_fast_fluct_db")),
        ("crest50", vo("crest_50ms_db")),
        ("accent tilt", vo("accent_uaa")),
        ("accent level", (g(T, "accent_uaa", "level_from_dark_db"), g(T, "accent_uaa", "level_from_dark_db_original"))),
        ("noise floor", (g(T, "noise_floor", "value"), g(T, "noise_floor", "original"))),
        ("LUFS/LRA/TP", ((g(tech, "lufs_integrated", "value"), g(tech, "lra_lu", "value"), g(tech, "true_peak_dbtp", "value")),
                         (g(tech, "lufs_integrated", "original"), g(tech, "lra_lu", "original"), g(tech, "true_peak_dbtp", "original")))),
        ("first/last", ((g(tech, "first_sound_s", "value"), g(tech, "last_sound_s", "value"), g(tech, "tail_end_s", "value")), None)),
        ("ltas diff", (T.get("ltas_diff_by_band_db"), None)),
    ]
    def fmt(v):
        if isinstance(v, float):
            return f"{v:.3g}"
        if isinstance(v, (list, tuple)):
            return "[" + ",".join(fmt(x) for x in v) + "]"
        if isinstance(v, dict):
            return "{" + ",".join(f"{k}:{fmt(x)}" for k, x in v.items()) + "}"
        return str(v)
    for nm, (v, o) in rows:
        print(f"  {nm:18s} {fmt(v):60s} orig {fmt(o)}")
    print("  checks", J.get("technical_checks"))
    if a.log:
        lp = os.path.join(SFD, "log.md")
        sub = " ".join(f"{k[:5]}{v['score']:.0f}" for k, v in S.items())
        with open(lp, "a") as fh:
            fh.write(f"| {a.tag} | {J['TIMBRE_SCORE']} | {sub} | {a.log} |\n")


if __name__ == "__main__":
    main()
