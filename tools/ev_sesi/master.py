#!/usr/bin/env python3
"""master.py -- delivery master for a house-sound render (plain gain, no limiter, no EQ).

    python3 master.py <in.wav> <out.m4a> [--lufs -15] [--tp -2] [--hp 0] [--wav out_master.wav]

  1. measures integrated loudness and true peak of the engine render (ffmpeg ebur128, the same meter the repo uses);
  2. applies ONE linear gain so the file sits at --lufs (default -15 LUFS). If that gain would push the true peak
     over --tp (default -2 dBTP) the gain is reduced until the peak fits (no limiter: the CLASSIC has none);
  3. encodes AAC-LC 192 kb/s, 44.1 kHz, stereo (.m4a, faststart), decodes it again and re-measures; if the codec
     overshoot lifts the true peak above --tp it lowers the gain by the overshoot and encodes once more;
  4. prints one JSON line with the measured numbers of the DECODED m4a.

  --hp HZ   optional 2nd-order zero-phase high-pass before the gain (e.g. 30) to drop the engine's 4-20 Hz rumble
            layer. Default 0 = off (Gölge's repo file keeps the rumble). Measured effect: OKU.md.

Reference: Gölge's repo file (assets/music/imza_v2_golge.m4a) measures -15.4 LUFS / -2.9 dBTP, AAC-LC 191 kb/s.
The video renderer (wojak/audio.py) brings every mix to -14 LUFS with a linear gain capped at -1.5 dBTP anyway.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

import numpy as np
import scipy.signal as ss
import soundfile as sf


def measure(path):
    """(integrated LUFS, true peak dBTP, LRA) with ffmpeg ebur128"""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True)
    txt = r.stderr[r.stderr.rfind("Summary:"):]
    i = float(re.search(r"I:\s*(-?[\d.]+) LUFS", txt).group(1))
    lra = float(re.search(r"LRA:\s*(-?[\d.]+) LU", txt).group(1))
    tp = float(re.search(r"Peak:\s*(-?[\d.]+|-inf) dBFS", txt).group(1))
    return i, tp, lra


def encode(wav, m4a):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", wav, "-vn", "-c:a", "aac", "-b:a", "192k",
                    "-ar", "44100", "-ac", "2", "-movflags", "+faststart", m4a], check=True)


def master(src, dst, lufs=-15.0, tp=-2.0, hp=0.0, wav_out=None):
    y, sr = sf.read(src, dtype="float64", always_2d=True)
    if sr != 44100:
        raise SystemExit("expected a 44.1 kHz engine render, got %d Hz" % sr)
    if hp and hp > 0:
        y = ss.sosfiltfilt(ss.butter(2, hp, "highpass", fs=sr, output="sos"), y, axis=0)
    tmpd = tempfile.mkdtemp(prefix="master_")
    t_in = os.path.join(tmpd, "in.wav")
    sf.write(t_in, y, sr, subtype="PCM_24")
    i0, tp0, _ = measure(t_in)
    gain = lufs - i0
    limited = False
    if tp0 + gain > tp:
        gain = tp - tp0
        limited = True
    out = {"in": os.path.basename(src), "in_lufs": i0, "in_tp": tp0}
    t_g = os.path.join(tmpd, "g.wav")
    for attempt in range(3):
        z = y * 10 ** (gain / 20.0)
        sf.write(t_g, z, sr, subtype="PCM_24")
        encode(t_g, dst)
        i1, tp1, lra1 = measure(dst)
        if tp1 <= tp + 0.05:
            break
        gain -= (tp1 - tp) + 0.05          # codec overshoot: back off by the excess
        limited = True
    if wav_out:
        sf.write(wav_out, z, sr, subtype="PCM_24")
    pr = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_name,profile,sample_rate,channels,bit_rate:"
                         "format=duration", "-of", "json", dst], capture_output=True, text=True)
    pj = json.loads(pr.stdout)
    st = pj["streams"][0]
    out.update({"gain_db": round(gain, 2), "gain_capped_by_true_peak": limited, "out": dst, "out_lufs": i1, "out_tp": tp1,
                "out_lra": lra1, "codec": st.get("codec_name"), "profile": st.get("profile"),
                "sample_rate": int(st.get("sample_rate", 0)), "bit_rate": int(st.get("bit_rate", 0) or 0),
                "duration_s": round(float(pj["format"]["duration"]), 3), "hp_hz": hp or 0,
                "ok": bool(tp1 <= tp + 0.05 and abs(i1 - lufs) <= 1.0)})
    for f in (t_in, t_g):
        try:
            os.remove(f)
        except OSError:
            pass
    try:
        os.rmdir(tmpd)
    except OSError:
        pass
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--lufs", type=float, default=-15.0)
    ap.add_argument("--tp", type=float, default=-2.0)
    ap.add_argument("--hp", type=float, default=0.0)
    ap.add_argument("--wav", help="also write the gained WAV (24 bit)")
    a = ap.parse_args()
    print(json.dumps(master(a.src, a.dst, a.lufs, a.tp, a.hp, a.wav)))


if __name__ == "__main__":
    main()
