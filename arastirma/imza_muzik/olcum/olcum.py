#!/usr/bin/env python3
"""olcum.py: measurement harness for signature-waltz candidates against the channel's original sound.

    python3 olcum.py <candidate audio> [--notalar melody.json] [--png out.png] [--ozet] [--ref ref.wav]

Prints one JSON object. Every metric is {"value", "original", "desc"} (plus "dist"/"score" where it feeds TIMBRE_SCORE).
The original is used ONLY for measurement: its features are computed once and cached in ./cache/.

Sections
  technical   duration, first/last sound, LUFS-I / LRA / true peak (ffmpeg ebur128), sample peak, clipping, clicks, DC, hum
  timbre      1/3-oct LTAS, mel envelope, MFCC, band shares, centroid, flatness, inter-harmonic noise floor,
              modulation spectrum, vibrato, pitch drift (wow + intonation), partial spread, stereo, reverb (side-from-mid
              system identification), level micro-variation, waltz accent pattern ("u a a")
  musical     tempo, triple-metre strength, key profile, onsets per bar, legato (gaps)
  originality chroma-sequence similarity (tools/imza_muzik.py karsilastir method, plus a transposition-invariant
              version), spectral-peak fingerprint match (sample-reuse detector, pitch-shift searched),
              and with --notalar the symbolic checks against analiz/muzik.json (offlimits.py + n-grams, contour,
              rhythm cells) with a PASS/FAIL verdict
  TIMBRE_SCORE 0-100 (100 = the original), weights and scales in TIMBRE_WEIGHTS below and in kalibrasyon.md

Nobody listens: these are measurements. Read the PNG to look at it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import pickle
import re
import subprocess
import sys
import time
import warnings

import numpy as np
import scipy.signal as ss
from scipy import ndimage

warnings.filterwarnings("ignore")

HERE = os.path.dirname(os.path.abspath(__file__))
SCR = os.path.abspath(os.path.join(HERE, "..", ".."))            # .../scratchpad
REF_WAV = os.path.join(SCR, "muzik", "orijinal.wav")
MUZIK_JSON = os.path.join(SCR, "muzik2", "analiz", "muzik.json")
OFFLIMITS_DIR = os.path.join(SCR, "muzik2", "analiz", "muzik", "py")
CACHE_DIR = os.path.join(HERE, "cache")
VERSION = "1.0"

SR = 44100
WIN_S = 13.77            # analysis window from t=0 (the original is 13.77 s; sound to 13.735 s)
SURE = 13.75             # tools/imza_muzik.py window for the chroma method
TOOLS_BASE = {"copy": 0.986, "unrelated": 0.139}

THIRD_OCT = [round(1000 * 2 ** (k / 3), 1) for k in range(-13, 13)]     # 50 Hz .. 15.9 kHz
CORE = (250, 4000)


# ----------------------------------------------------------------------------------------------------------- io
def probe(path):
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                              "stream=codec_name,profile,sample_rate,channels,bit_rate:format=duration",
                              "-of", "json", path], capture_output=True, text=True, check=True).stdout
        j = json.loads(out)
        st = [s for s in j.get("streams", []) if "channels" in s]
        s = st[0] if st else {}
        return {"codec": s.get("codec_name"), "profile": s.get("profile"), "sample_rate": int(s.get("sample_rate", 0) or 0),
                "channels": int(s.get("channels", 0) or 0), "bit_rate": int(s.get("bit_rate", 0) or 0) or None,
                "container_duration_s": float(j.get("format", {}).get("duration", 0) or 0)}
    except Exception as e:  # pragma: no cover
        return {"error": str(e)}


def decode(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-acodec", "pcm_f32le", "-ac", "2",
                          "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    y = np.frombuffer(raw, dtype=np.float32).astype(np.float64).reshape(-1, 2)
    return y


def ebur128(path):
    p = subprocess.run(["ffmpeg", "-nostats", "-hide_banner", "-i", path, "-af", "ebur128=peak=true:framelog=quiet",
                        "-f", "null", "-"], capture_output=True, text=True)
    txt = p.stderr[p.stderr.rfind("Summary:"):]
    def g(pat):
        m = re.search(pat, txt)
        return float(m.group(1)) if m else None
    return {"I": g(r"I:\s+(-?[\d.]+|-inf) LUFS"), "LRA": g(r"LRA:\s+(-?[\d.]+) LU"), "TP": g(r"Peak:\s+(-?[\d.]+|-inf) dBFS")}


# ------------------------------------------------------------------------------------------------------ helpers
def db(x, floor=1e-12):
    return 10 * np.log10(np.maximum(x, floor))


def frame_pow(x, win, hop):
    if len(x) < win:
        x = np.pad(x, (0, win - len(x)))
    v = np.lib.stride_tricks.sliding_window_view(x, win)[::hop]
    return np.mean(v ** 2, axis=1)


def rnd(v, n=3):
    if v is None:
        return None
    if isinstance(v, (list, tuple, np.ndarray)):
        return [rnd(x, n) for x in v]
    if isinstance(v, (np.floating, float)):
        if not np.isfinite(v):
            return None
        return round(float(v), n)
    if isinstance(v, (np.integer,)):
        return int(v)
    return v


def cauchy(d, tau):
    """sub-score 0-100: 100 at d=0, 50 at d=tau, 20 at 2 tau, 10 at 3 tau"""
    if d is None or not np.isfinite(d):
        return None
    return 100.0 / (1.0 + (abs(d) / tau) ** 2)


# -------------------------------------------------------------------------------------------------- technical
def active_region(y, lufs=None):
    """10 ms RMS of the channel-power mean. Sound = frames above (LUFS-I - 16 dB) (the original: -45.5 dBFS, as STIL's
    -45 dBFS rule); tail = frames above (LUFS-I - 40 dB). Without a loudness value: median active level - 20 / - 44 dB."""
    p = (y[:, 0] ** 2 + y[:, 1] ** 2) / 2
    hop = SR // 100
    fr = db(frame_pow(np.sqrt(p), hop, hop))
    good = fr[fr > -90]
    med = np.median(good) if len(good) else -90
    if lufs is not None and np.isfinite(lufs):
        thr, thr_tail = lufs - 16, lufs - 40
    else:
        thr, thr_tail = med - 20, med - 44
    idx = np.flatnonzero(fr >= thr)
    idt = np.flatnonzero(fr >= thr_tail)
    if len(idx) == 0:
        return 0, len(y), thr, len(y) / SR
    tail_end = (idt[-1] + 1) * hop / SR if len(idt) else len(y) / SR
    return idx[0] * hop, min(len(y), (idx[-1] + 1) * hop), thr, min(tail_end, len(y) / SR)


def clicks(x):
    """AR(32) residual spikes: |residual| > 16 robust sigmas (50 ms MAD, floored at 0.25 x the median window sigma),
    merged within 3 ms; isolated events (< 3 ms) are clicks, longer runs are reported as bursts."""
    import librosa
    order, blk = 32, 4096
    res = np.zeros_like(x)
    rng = np.random.default_rng(0)
    for s in range(0, len(x), blk):
        a0 = max(0, s - order)
        seg = x[a0:s + blk]
        if len(seg) <= order * 2 or np.max(np.abs(seg)) < 1e-7:
            continue
        try:
            a = librosa.lpc(seg + 1e-9 * rng.standard_normal(len(seg)), order=order)
        except Exception:
            continue
        e = ss.lfilter(a, [1.0], seg)
        res[s:s + blk] = e[s - a0:][:len(res[s:s + blk])]
    res[:order + 8] = 0.0                       # no history for the very first samples
    w = int(0.05 * SR)
    sig = np.zeros_like(res)
    vals = []
    for s in range(0, len(res), w):
        v = 1.4826 * np.median(np.abs(res[s:s + w]))
        sig[s:s + w] = v
        vals.append(v)
    sig = np.maximum(sig, max(0.25 * np.median(vals), 1e-5))
    z = np.abs(res) / sig
    hit = np.flatnonzero(z > 16)
    events = []
    gap = int(0.003 * SR)
    for h in hit:
        if events and h - events[-1][1] <= gap:
            events[-1][1] = h
            events[-1][2] = max(events[-1][2], z[h])
        else:
            events.append([h, h, z[h]])
    iso = [e for e in events if (e[1] - e[0]) < gap]
    # one corrupted LPC block can echo a real click as a second hit nearby: count hits within 60 ms as one click
    merged = []
    for e in iso:
        if merged and e[0] - merged[-1][1] < int(0.06 * SR):
            merged[-1][1] = e[1]
            merged[-1][2] = max(merged[-1][2], e[2])
        else:
            merged.append(list(e))
    iso = merged
    from scipy.stats import kurtosis
    return {"count": len(iso), "times_s": [round(e[0] / SR, 3) for e in iso[:20]], "max_z": float(max([e[2] for e in iso], default=0)),
            "bursts": len(events) - len(iso), "resid_kurtosis": float(kurtosis(res[np.abs(res) > 0]))}


def hum_lines(mid):
    n = len(mid)
    w = np.hanning(n)
    X = np.abs(np.fft.rfft(mid * w)) * 2 / w.sum()
    f = np.fft.rfftfreq(n, 1 / SR)
    out = {}
    for h in (50, 100, 150, 200):
        m = (f > h - 1.5) & (f < h + 1.5)
        out[str(h)] = float(20 * np.log10(X[m].max() + 1e-12))
    sos = ss.butter(4, 25, "lowpass", fs=SR, output="sos")
    r = ss.sosfilt(sos, mid)
    out["rumble_lt25_rms_dbfs"] = float(10 * np.log10(np.mean(r[SR // 2:] ** 2) + 1e-20))
    return out


# ----------------------------------------------------------------------------------------------- spectra
def ltas_third(mid):
    f, P = ss.welch(mid, SR, nperseg=8192, noverlap=6144)
    bands = []
    for fc in THIRD_OCT:
        lo, hi = fc * 2 ** (-1 / 6), fc * 2 ** (1 / 6)
        m = (f >= lo) & (f < hi)
        bands.append(P[m].sum() if m.any() else 1e-20)
    bands = np.array(bands)
    core = np.array([CORE[0] * 0.89 <= fc <= CORE[1] * 1.12 for fc in THIRD_OCT])
    ref = bands[core].sum()
    return {"fc": THIRD_OCT, "rel_db": db(bands / ref).tolist(), "abs_dbfs": db(bands * 2).tolist()}


def mel_mfcc(y22, act22):
    import librosa
    S = librosa.feature.melspectrogram(y=y22, sr=22050, n_fft=2048, hop_length=512, n_mels=64, fmin=50, fmax=11025,
                                       power=2.0)
    L = librosa.power_to_db(S, ref=np.max, top_db=70)     # level-invariant; near-silent bands clamped at -70 dB
    nfr = L.shape[1]
    fr_db = db(np.mean(S, axis=0))
    t = np.arange(nfr) * 512 / 22050
    sel = (t >= act22[0]) & (t <= act22[1]) & (fr_db > np.median(fr_db) - 25)
    if sel.sum() < 10:
        sel = np.ones(nfr, bool)
    mf = librosa.feature.mfcc(S=L, n_mfcc=20)
    melf = librosa.mel_frequencies(n_mels=64, fmin=50, fmax=11025)
    core = (melf >= CORE[0]) & (melf <= CORE[1])
    env = L[:, sel].mean(1)
    env = env - env[core].mean()
    return {"mfcc_mean": mf[1:, sel].mean(1).tolist(), "mfcc_std": mf[1:, sel].std(1).tolist(),
            "mel_env": env.tolist(), "mel_f": melf.tolist()}


def shares_centroid_flatness(y22, act22):
    import librosa
    S = np.abs(librosa.stft(y22, n_fft=4096, hop_length=1024)) ** 2
    fr = librosa.fft_frequencies(sr=22050, n_fft=4096)
    top = S.sum() + 1e-20
    sh = {k: float(S[(fr >= lo) & (fr < hi)].sum() / top) for k, (lo, hi) in
          {"<250": (0, 250), "250-1k": (250, 1000), "1-4k": (1000, 4000), ">4k": (4000, 1e9)}.items()}
    cent = float((S.sum(1) * fr).sum() / top)
    t = np.arange(S.shape[1]) * 1024 / 22050
    e = S.sum(0)
    sel = (t >= act22[0]) & (t <= act22[1]) & (db(e) > np.median(db(e)) - 25)
    if sel.sum() < 5:
        sel = np.ones(S.shape[1], bool)
    fcent = (S * fr[:, None]).sum(0) / (e + 1e-20)
    flat = librosa.feature.spectral_flatness(S=np.sqrt(S))[0]
    # core-band flatness (250-4000): tonal vs noisy inside the musical band
    cm = (fr >= CORE[0]) & (fr < CORE[1])
    Sc = S[cm][:, sel] + 1e-20
    flat_core = np.exp(np.mean(np.log(Sc), 0)) / np.mean(Sc, 0)
    # spectral 95 % roll-off on the long-term spectrum
    cs = np.cumsum(S.sum(1)) / top
    roll = float(fr[np.searchsorted(cs, 0.95)])
    return {"shares": sh, "centroid_hz": cent, "frame_centroid_median_hz": float(np.median(fcent[sel])),
            "flatness_median": float(np.median(flat[sel])), "flatness_core_median": float(np.median(flat_core)),
            "rolloff95_hz": roll}


def noise_floor(mid, a0, a1):
    f, t, Z = ss.stft(mid, SR, nperseg=8192, noverlap=6144, boundary=None, padded=False)
    P = np.abs(Z) ** 2
    tt = t
    e = P[(f >= CORE[0]) & (f < CORE[1])].sum(0)
    sel = (tt >= a0) & (tt <= a1) & (db(e) > np.median(db(e)) - 20)
    if sel.sum() < 3:
        sel = np.ones(P.shape[1], bool)
    P = P[:, sel]
    total = P[(f >= CORE[0]) & (f < CORE[1])].mean()
    rel, absr, fcs = [], [], []
    for fc in THIRD_OCT:
        if not (CORE[0] * 0.89 <= fc <= CORE[1] * 1.12):
            continue
        lo, hi = fc * 2 ** (-1 / 6), fc * 2 ** (1 / 6)
        m = (f >= lo) & (f < hi)
        sub = P[m]
        p10 = np.percentile(sub, 10, axis=0)
        mean = sub.mean(0) + 1e-20
        rel.append(float(np.median(db(p10 / mean))))
        absr.append(float(db(np.median(p10) / total)))
        fcs.append(fc)
    return {"fc": fcs, "floor_rel_band_db": rel, "floor_re_music_db": absr}


# ------------------------------------------------------------------------------------------------ envelopes
def band_envelopes(mid, a0, a1, hop=220, nfft=1024):
    f, t, Z = ss.stft(mid, SR, nperseg=nfft, noverlap=nfft - hop, boundary=None, padded=False)
    P = np.abs(Z) ** 2
    t = t
    sel = (t >= a0) & (t <= a1)
    bands = [(250, 500), (500, 1000), (1000, 2000), (2000, 4000)]
    env = np.array([P[(f >= lo) & (f < hi)].sum(0) for lo, hi in bands])
    return t[sel], env[:, sel], SR / hop


def modulation(tenv, env, fs_env):
    edges = np.geomspace(0.5, 20, 17)
    out_bins, depth = [], {}
    n = env.shape[1]
    nper = min(n, int(4 * fs_env))
    spec = []
    rng = {"0.5-2": (0.5, 2), "2-8": (2, 8), "8-20": (8, 20)}
    acc = {k: [] for k in rng}
    for b in range(env.shape[0]):
        e = db(env[b])
        e = np.maximum(e, e.max() - 60)
        e = e - e.mean()
        fm, Pm = ss.welch(e, fs_env, nperseg=nper, noverlap=nper * 3 // 4, detrend="linear")
        row = []
        for lo, hi in zip(edges[:-1], edges[1:]):
            m = (fm >= lo) & (fm < hi)
            row.append(Pm[m].mean() if m.any() else np.interp((lo + hi) / 2, fm, Pm))
        spec.append(db(np.array(row)))
        df = fm[1] - fm[0]
        for k, (lo, hi) in rng.items():
            m = (fm >= lo) & (fm < hi)
            acc[k].append(np.sqrt(Pm[m].sum() * df))        # RMS dB fluctuation in that modulation range
    spec = np.array(spec)
    for k in rng:
        depth[k] = float(np.mean(acc[k]))
    return {"edges_hz": edges.tolist(), "spec_db": spec.tolist(), "fluct_rms_db": depth}


def level_stats(mid, a0i, a1i):
    x = mid[a0i:a1i]
    r100 = db(frame_pow(x, SR // 10, SR // 10))
    r10 = db(frame_pow(x, SR // 100, SR // 100))
    r20 = db(frame_pow(x, int(0.02 * SR), int(0.01 * SR)))
    k = 31
    smooth = ndimage.uniform_filter1d(r20, k, mode="nearest")
    fast = r20 - smooth
    r50 = frame_pow(x, int(0.05 * SR), int(0.05 * SR))
    pk = np.lib.stride_tricks.sliding_window_view(np.abs(x), int(0.05 * SR))[::int(0.05 * SR)].max(1)
    crest = 20 * np.log10(pk[: len(r50)] / np.sqrt(r50[: len(pk)] + 1e-20) + 1e-12)
    med10 = np.median(r10)
    gaps = r10 < med10 - 20
    longest, cur = 0, 0
    for g in gaps:
        cur = cur + 1 if g else 0
        longest = max(longest, cur)
    # fastest level drops (articulation + room): 5th percentile of the 20 ms-to-20 ms slope, dB/s
    sl = np.diff(r20) / 0.01
    r500 = db(frame_pow(x, SR // 2, SR // 2))
    med500 = float(np.median(r500)) if len(r500) else 0.0
    rb = db(frame_pow(x, int(1.1879 * SR), int(1.1879 * SR)))
    bar_db = (rb - np.median(rb)).tolist()
    start_db = float(r500[0] - med500) if len(r500) else 0.0
    end_seg = x[max(0, len(x) - SR):]
    end_db = float(db(np.mean(end_seg ** 2) + 1e-20) - med500)
    return {"bar_db": bar_db, "start_db": start_db, "end_db": end_db, "rms100_std_db": float(np.std(r100)), "rms100_p10_p90_db": float(np.percentile(r100, 90) - np.percentile(r100, 10)),
            "fast_fluct_std_db": float(np.std(fast)), "crest50_median_db": float(np.median(crest)),
            "gap_fraction": float(gaps.mean()), "longest_gap_ms": float(longest * 10),
            "p2_level_re_median_db": float(np.percentile(r10, 2) - med10),
            "fastest_drop_db_s": float(np.percentile(sl, 2)), "rms100_curve": r100.tolist()}


# ------------------------------------------------------------------------------------------------- pitch
def peaks_and_tracks(mid, a0, a1):
    f, t, Z = ss.stft(mid, SR, window="hann", nperseg=2048, noverlap=2048 - 256, nfft=8192, boundary=None, padded=False)
    band = (f >= 240) & (f <= 2600)
    fb = f[band]
    M = db(np.abs(Z[band]) ** 2)
    sel = (t >= a0) & (t <= a1)
    gmax = M[:, sel].max() if sel.any() else M.max()
    df = fb[1] - fb[0]
    pk_fr, pk_f, pk_a = [], [], []
    for j in np.flatnonzero(sel):
        col = M[:, j]
        thr = max(col.max() - 30, gmax - 65)
        idx, pr = ss.find_peaks(col, height=thr, prominence=6, distance=8)
        if len(idx) == 0:
            continue
        idx = idx[(idx > 0) & (idx < len(col) - 1)]
        a, b, c = col[idx - 1], col[idx], col[idx + 1]
        den = a - 2 * b + c
        p = np.where(np.abs(den) > 1e-9, 0.5 * (a - c) / den, 0.0)
        pk_fr.append(np.full(len(idx), j))
        pk_f.append(fb[idx] + p * df)
        pk_a.append(b - 0.25 * (a - c) * p)
    if not pk_fr:
        return None
    pk_fr, pk_f, pk_a = np.concatenate(pk_fr), np.concatenate(pk_f), np.concatenate(pk_a)
    hop_s = 256 / SR
    # greedy track linking (30 cents, no gaps)
    tracks, live = [], []
    order = np.argsort(pk_fr, kind="stable")
    pk_fr, pk_f, pk_a = pk_fr[order], pk_f[order], pk_a[order]
    starts = np.flatnonzero(np.r_[True, np.diff(pk_fr) != 0])
    ends = np.r_[starts[1:], len(pk_fr)]
    prev_frame = None
    for s0, e0 in zip(starts, ends):
        fr = pk_fr[s0]
        fs_, as_ = pk_f[s0:e0], pk_a[s0:e0]
        cents = 1200 * np.log2(fs_)
        newlive = []
        used = np.zeros(len(fs_), bool)
        if prev_frame is not None and fr == prev_frame + 1 and live:
            lc = np.array([1200 * np.log2(tr["f"][-1]) for tr in live])
            D = np.abs(lc[:, None] - cents[None, :])
            for _ in range(min(len(live), len(fs_))):
                i, k = np.unravel_index(np.argmin(D), D.shape)
                if D[i, k] > 30:
                    break
                live[i]["f"].append(fs_[k]); live[i]["a"].append(as_[k]); live[i]["fr"].append(fr)
                newlive.append(live[i]); used[k] = True
                D[i, :] = 1e9; D[:, k] = 1e9
            for tr in live:
                if tr not in newlive:
                    tracks.append(tr)
        else:
            tracks.extend(live)
        for k in np.flatnonzero(~used):
            newlive.append({"f": [fs_[k]], "a": [as_[k]], "fr": [fr]})
        live = newlive
        prev_frame = fr
    tracks.extend(live)
    tracks = [{"t": t[np.array(tr["fr"])], "f": np.array(tr["f"]), "a": np.array(tr["a"])} for tr in tracks
              if len(tr["fr"]) * hop_s >= 0.25]
    return {"pk_fr": pk_fr, "pk_f": pk_f, "pk_a": pk_a, "t": t, "tracks": tracks, "hop_s": hop_s, "gmax": gmax}


def pitch_features(pt):
    if pt is None:
        return None
    hop_s = pt["hop_s"]
    fs_tr = 1 / hop_s
    sos = ss.butter(2, [3.5, 9.0], "bandpass", fs=fs_tr, output="sos")
    vib, w = [], []
    specs, sw = [], []
    nfft = 1024
    ff = np.fft.rfftfreq(nfft, hop_s)
    for tr in pt["tracks"]:
        dur = len(tr["f"]) * hop_s
        if dur < 0.4 or np.median(tr["a"]) < pt["gmax"] - 35:
            continue
        c = 1200 * np.log2(tr["f"] / np.median(tr["f"]))
        try:
            bp = ss.sosfiltfilt(sos, c)
        except ValueError:
            continue
        vib.append(np.sqrt(np.mean(bp[10:-10] ** 2)) if len(bp) > 30 else np.sqrt(np.mean(bp ** 2)))
        wt = dur * 10 ** (np.median(tr["a"]) / 20)
        w.append(wt)
        if dur >= 0.6:
            n = len(c)
            x = np.arange(n)
            cd = c - np.polyval(np.polyfit(x, c, 2), x)
            X = np.abs(np.fft.rfft(cd * np.hanning(n), nfft)) ** 2 / n
            specs.append(X); sw.append(wt)
    out = {"n_tracks": len(vib)}
    if vib:
        vib, w = np.array(vib), np.array(w)
        o = np.argsort(vib)
        cw = np.cumsum(w[o]) / w.sum()
        out["vibrato_rms_c"] = float(vib[o][np.searchsorted(cw, 0.5)])
    if specs:
        S = np.average(np.array(specs), axis=0, weights=np.array(sw))
        m = (ff >= 3) & (ff <= 9)
        m2 = (ff >= 2) & (ff <= 12)
        k = np.argmax(S[m])
        out["vibrato_rate_hz"] = float(ff[m][k])
        out["vibrato_peakiness"] = float(S[m][k] / np.median(S[m2]))
    # pitch deviation from the 12-TET A440 grid, per register band (240-470 / 480-940 / 1400-2500 Hz): weighted circular
    # mean of the partials in the band, global offset removed, 0.2 s smoothing. Its std = pitch instability (per-note
    # mistuning, bends, wow); the correlation between bands tells a common wow (high r) from per-note intonation (low r).
    cents = 1200 * np.log2(pt["pk_f"] / 440.0)
    d = (cents + 50) % 100 - 50
    th = 2 * np.pi * d / 100
    wl = 10 ** ((pt["pk_a"] - pt["gmax"]) / 20)
    nfr = len(pt["t"])
    zall = np.sum(wl * np.exp(1j * th))
    off = np.angle(zall)
    out["tuning_offset_c"] = float(off * 100 / (2 * np.pi))
    W = np.bincount(pt["pk_fr"], wl, nfr)
    has = W > 0
    zr = np.bincount(pt["pk_fr"], wl * np.cos(th), nfr)
    zi = np.bincount(pt["pk_fr"], wl * np.sin(th), nfr)
    R = np.abs(zr + 1j * zi)[has] / W[has]
    spread = np.sqrt(-2 * np.log(np.clip(R, 1e-6, 1))) * 100 / (2 * np.pi)
    o = np.argsort(spread)
    cw = np.cumsum(W[has][o]) / W[has].sum()
    out["partial_spread_c"] = float(spread[o][np.searchsorted(cw, 0.5)])
    k = int(round(0.2 / hop_s)) | 1
    win = np.hanning(k + 2)[1:-1]
    curves = []
    for lo, hi in ((240, 470), (480, 940), (1400, 2500)):
        m = (pt["pk_f"] >= lo) & (pt["pk_f"] < hi)
        br = np.bincount(pt["pk_fr"][m], (wl * np.cos(th - off))[m], nfr)
        bi = np.bincount(pt["pk_fr"][m], (wl * np.sin(th - off))[m], nfr)
        bw = np.bincount(pt["pk_fr"][m], wl[m], nfr)
        zs = np.convolve(br, win, "same") + 1j * np.convolve(bi, win, "same")
        ws = np.convolve(bw, win, "same")
        c = np.angle(zs) * 100 / (2 * np.pi)
        pos = ws[ws > 0]
        c[ws < 0.05 * (np.median(pos) if len(pos) else 1)] = np.nan
        curves.append(c)
    Cb = np.array(curves)
    okb = ~np.isnan(Cb).any(0)
    out["pitch_dev_band_std_c"] = float(np.mean([np.nanstd(c) for c in Cb]))
    out["pitch_dev_band_std_each_c"] = [float(np.nanstd(c)) for c in Cb]
    if okb.sum() > 50:
        rr = [np.corrcoef(Cb[i, okb], Cb[j, okb])[0, 1] for i, j in ((0, 1), (0, 2), (1, 2))]
        out["pitch_dev_coherence_r"] = float(np.mean(rr))
    else:
        out["pitch_dev_coherence_r"] = None
    common = np.nanmean(Cb, 0)
    out["pitch_dev_common_std_c"] = float(np.nanstd(common))
    v = common[np.isfinite(common)]
    out["pitch_dev_p5_p95_c"] = [float(np.percentile(v, 5)), float(np.percentile(v, 95))] if len(v) else None
    gl, gw = 0.0, 0.0
    for tr in pt["tracks"]:
        if len(tr["f"]) < 12:
            continue
        c = 1200 * np.log2(tr["f"])
        vel = np.abs(np.diff(ndimage.uniform_filter1d(c, 5))) / hop_s
        wv = 10 ** ((tr["a"][1:] - pt["gmax"]) / 20)
        inner = slice(3, len(vel) - 3)
        gl += float(np.sum(wv[inner] * (vel[inner] > 600)))
        gw += float(np.sum(wv[inner]))
    out["glide_share"] = gl / gw if gw > 0 else 0.0
    cnt = np.bincount(pt["pk_fr"], minlength=nfr)
    out["peaks_per_frame_median"] = float(np.median(cnt[cnt > 0])) if (cnt > 0).any() else 0.0
    out["drift_curve_t"] = pt["t"][::4].tolist()
    out["drift_curve_c"] = [None if not np.isfinite(x) else float(x) for x in common[::4]]
    return out


# ------------------------------------------------------------------------------------------------ stereo / room
def stereo_room(y, a0i, a1i):
    L, R = y[a0i:a1i, 0], y[a0i:a1i, 1]
    M, S = (L + R) / 2, (L - R) / 2
    pm, ps = np.mean(M ** 2), np.mean(S ** 2)
    out = {"lr_corr": float(np.corrcoef(L, R)[0, 1]) if np.std(L) > 0 and np.std(R) > 0 else 1.0,
           "side_mid_db": float(db(ps / (pm + 1e-20))) if ps > 0 else -99.0}
    f_, PL = ss.welch(L, SR, nperseg=16384)
    _, PR = ss.welch(R, SR, nperseg=16384)
    _, PM = ss.welch(M, SR, nperseg=16384)
    mm = (f_ > 300) & (f_ < 3000)
    rr = db(PM[mm] / ((PL[mm] + PR[mm]) / 2 + 1e-30))
    out["mono_fold_mean_db"], out["mono_fold_std_db"], out["mono_fold_min_db"] = float(rr.mean()), float(rr.std()), float(rr.min())
    bp = ss.butter(4, [300, 4000], "bandpass", fs=SR, output="sos")
    Lb, Rb = ss.sosfilt(bp, L), ss.sosfilt(bp, R)
    out["lr_corr_300_4k"] = float(np.corrcoef(Lb, Rb)[0, 1]) if np.std(Lb) > 0 and np.std(Rb) > 0 else 1.0
    if out["side_mid_db"] < -40:
        out["ir_env_db"] = None
        return out
    Mb, Sb = ss.sosfiltfilt(bp, M), ss.sosfiltfilt(bp, S)
    n = 16384
    f, Pxy = ss.csd(Mb, Sb, SR, nperseg=n, noverlap=n * 3 // 4, window="hann")
    f, Pxx = ss.welch(Mb, SR, nperseg=n, noverlap=n * 3 // 4, window="hann")
    m = (f > 300) & (f < 4000)
    H = np.zeros_like(Pxy)
    H[m] = Pxy[m] / (Pxx[m] + 1e-3 * Pxx[m].max())
    h = np.fft.irfft(H, n)
    e = h ** 2
    k = int(0.005 * SR)
    es = np.convolve(e, np.ones(k) / k, "same")
    env = db(es / (es[: int(0.3 * SR)].max() + 1e-30))
    tms = np.arange(len(h)) / SR * 1000
    probe_ms = [10, 20, 30, 50, 75, 100, 150, 200, 300]
    out["ir_probe_ms"] = probe_ms
    out["ir_env_db"] = [float(env[int(p / 1000 * SR)]) for p in probe_ms]
    out["ir_peak_ms"] = float(tms[np.argmax(env[: int(0.3 * SR)])])
    # side envelope lag vs mid (ms)
    return out


# ---------------------------------------------------------------------------------------------- musical
KK_MAJ = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
KK_MIN = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
PCN = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]


def musical(y22, act22):
    import librosa
    S = librosa.feature.melspectrogram(y=y22, sr=22050, n_fft=2048, hop_length=256, n_mels=96, fmin=150, fmax=6000)
    L = librosa.power_to_db(S, ref=np.max)
    oenv = librosa.onset.onset_strength(S=L, sr=22050, hop_length=256)
    fps = 22050 / 256
    t = np.arange(len(oenv)) / fps
    sel = (t >= act22[0]) & (t <= act22[1])
    oe = oenv.copy()
    oe[~sel] = 0
    x = oe - oe[sel].mean()
    x[~sel] = 0
    ac = np.correlate(x, x, "full")[len(x) - 1:]
    ac /= ac[0] + 1e-20
    lags = np.arange(len(ac)) / fps
    def acf_at(lag):
        return float(np.interp(lag, lags, ac))
    # beat-grid fit: the period/phase whose grid points collect the most (smoothed) onset strength, 110-190 BPM
    oe_s = ndimage.gaussian_filter1d(np.where(sel, oenv, 0.0), 0.02 * fps)
    best = (-1, 150.0, 0.0)
    span = act22[1] - act22[0]
    for b in np.arange(110, 190.01, 0.1):
        P = 60 / b
        n = max(2, int(span / P))
        ph = act22[0] + np.arange(0, P, 0.004)
        grid = ph[:, None] + np.arange(n)[None, :] * P
        ok = grid <= act22[1]
        v = np.where(ok, np.interp(grid, t, oe_s), 0.0)
        scv = v.sum(1) / ok.sum(1)
        k = int(np.argmax(scv))
        if scv[k] > best[0]:
            best = (float(scv[k]), float(b), float(ph[k]))
    tempo = best[1]
    P = 60 / tempo
    bs = np.arange(110, 190.01, 0.25)
    comb = np.array([sum(acf_at(k * 60 / b) for k in range(1, 13)) for b in bs])
    tempo_comb = float(bs[np.argmax(comb)])
    triple = acf_at(3 * P) - 0.5 * (acf_at(2 * P) + acf_at(4 * P))
    try:
        bt, _ = librosa.beat.beat_track(onset_envelope=oenv, sr=22050, hop_length=256, start_bpm=150)
        bt = float(np.atleast_1d(bt)[0])
    except Exception:
        bt = None
    ons = librosa.onset.onset_detect(onset_envelope=oenv, sr=22050, hop_length=256, units="time")
    ons = ons[(ons >= act22[0]) & (ons <= act22[1])]
    act_dur = act22[1] - act22[0]
    ch = librosa.feature.chroma_cqt(y=y22, sr=22050)
    prof = ch.mean(1)
    keys = []
    for k in range(12):
        keys.append((float(np.corrcoef(prof, np.roll(KK_MAJ, k))[0, 1]), PCN[k] + " major"))
        keys.append((float(np.corrcoef(prof, np.roll(KK_MIN, k))[0, 1]), PCN[k] + " minor"))
    keys.sort(reverse=True)
    cmin = float(np.corrcoef(prof, KK_MIN)[0, 1])
    # harmonic rhythm: chroma self-similarity at 1 and 2 bars (own tempo); original rocks i <-> vii (low at 1, high at 2)
    chop = 512 / 22050
    cn = ch / (np.linalg.norm(ch, axis=0, keepdims=True) + 1e-9)
    cn = cn - cn.mean(1, keepdims=True)
    tch = np.arange(ch.shape[1]) * chop
    selc = (tch >= act22[0]) & (tch <= act22[1] - 2.0)
    def lag_sim(lag_s):
        k = int(round(lag_s / chop))
        idx = np.flatnonzero(selc[:-k] & selc[k:]) if k < len(selc) else []
        if len(idx) < 20:
            return None
        a, b = cn[:, idx], cn[:, idx + k]
        return float((a * b).sum() / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))
    sim1, sim2 = lag_sim(3 * P), lag_sim(6 * P)
    return {"tempo_bpm": tempo, "tempo_comb_bpm": tempo_comb, "beat_phase_s": best[2], "beat_track_bpm": bt,
            "triple_metre": triple,
            "onsets_per_bar": float(len(ons) / (act_dur / (3 * P))) if act_dur > 0 else None,
            "onsets_per_s": float(len(ons) / act_dur) if act_dur > 0 else None,
            "onset_times": ons.tolist(), "key_best": keys[0][1], "key_best_r": keys[0][0], "c_minor_r": cmin,
            "chroma_profile": prof.tolist(), "oenv": oenv, "oenv_fps": fps, "chroma_lag1bar": sim1, "chroma_lag2bar": sim2}


def accent_pattern(y22, tempo, phase, act22):
    """'u a a': on the fitted beat grid, per beat the peak level (0-120 ms after the beat) in 250-500 Hz and 1-4 kHz.
    tilt = L(1-4k) - L(250-500) (brightness). Beats are grouped by position mod 3; the darkest class is called 'u'.
    contrast = mean tilt of the other two - tilt of 'u' (original: beat 1 dark, beats 2-3 ~4-5 dB brighter);
    balance = |tilt difference between the two bright classes| (original: small = 'a a')."""
    import librosa
    S = np.abs(librosa.stft(y22, n_fft=1024, hop_length=128)) ** 2
    fr = librosa.fft_frequencies(sr=22050, n_fft=1024)
    lo = db(S[(fr >= 250) & (fr < 500)].sum(0))
    hi = db(S[(fr >= 1000) & (fr < 4000)].sum(0))
    al = db(S[(fr >= 250) & (fr < 4000)].sum(0))
    fps = 22050 / 128
    P = 60 / tempo
    end = act22[1] - 2.3 if act22[1] - act22[0] > 6 else act22[1]
    k0 = int(np.ceil((act22[0] - phase) / P))
    beats = []
    k = k0
    while phase + k * P < end:
        t0 = phase + k * P
        i0, i1 = int(t0 * fps), int((t0 + 0.12) * fps) + 1
        if i0 >= 0 and i1 < len(lo):
            beats.append((k % 3, lo[i0:i1].max(), hi[i0:i1].max(), al[i0:i1].max()))
        k += 1
    if len(beats) < 9:
        return {"tilt_from_dark_db": None, "level_from_dark_db": None, "contrast_db": 0.0, "balance_db": 0.0,
                "level_contrast_db": 0.0}
    B = np.array(beats)
    tilt = [np.mean(B[B[:, 0] == c, 2] - B[B[:, 0] == c, 1]) for c in range(3)]
    lev = [np.mean(B[B[:, 0] == c, 3]) for c in range(3)]
    d = int(np.argmin(tilt))
    rt = [tilt[(d + j) % 3] for j in range(3)]
    rl = [lev[(d + j) % 3] for j in range(3)]
    return {"tilt_from_dark_db": [float(x - rt[0]) for x in rt], "level_from_dark_db": [float(x - rl[0]) for x in rl],
            "contrast_db": float(np.mean(rt[1:]) - rt[0]), "balance_db": float(abs(rt[1] - rt[2])),
            "level_contrast_db": float(np.mean(rl[1:]) - rl[0]), "n_beats": len(beats)}


# -------------------------------------------------------------------------------------------- originality
def chroma_seq(y22):
    import librosa
    yy = y22[: int(SURE * 22050)]
    return librosa.feature.chroma_cqt(y=yy, sr=22050)


def chroma_sim(ca, cb, transpose=False, scales=(1.0,)):
    """tools/imza_muzik.py karsilastir method: frame-wise cosine of mean-removed chroma, best over +-2.4 s lags.
    transpose=True also takes the best of the 12 rotations of the candidate chroma; scales = candidate time-scale
    factors tried (tempo changes)."""
    hop = 512 / 22050
    best, best_rot, best_lag, best_sc = -1.0, 0, 0, 1.0
    for sc in scales:
        if sc != 1.0:
            n_new = int(ca.shape[1] / sc)
            src = np.arange(n_new) * sc
            ca_s = np.array([np.interp(src, np.arange(ca.shape[1]), row) for row in ca])
        else:
            ca_s = ca
        L = min(ca_s.shape[1], cb.shape[1])
        A, Bm = ca_s[:, :L], cb[:, :L]
        cb_n = Bm / (np.linalg.norm(Bm, axis=0, keepdims=True) + 1e-9)
        cb_d = cb_n - cb_n.mean(1, keepdims=True)
        for rot in (range(12) if transpose else [0]):
            c = np.roll(A, rot, axis=0)
            ca_n = c / (np.linalg.norm(c, axis=0, keepdims=True) + 1e-9)
            ca_d = ca_n - ca_n.mean(1, keepdims=True)
            for kay in range(-int(2.4 / hop), int(2.4 / hop) + 1):
                x = ca_d[:, max(0, kay):L + min(0, kay)]
                y_ = cb_d[:, max(0, -kay):L - max(0, kay)]
                v = float((x * y_).sum() / (np.linalg.norm(x) * np.linalg.norm(y_) + 1e-9))
                if v > best:
                    best, best_rot, best_lag, best_sc = v, rot, kay, sc
    return best, (best_rot if best_rot <= 6 else best_rot - 12), best_lag * hop, best_sc


SCALES = tuple(np.round(np.arange(0.94, 1.0601, 0.01), 2))


def fingerprint(y22):
    import librosa
    C = np.abs(librosa.cqt(y22, sr=22050, hop_length=512, fmin=librosa.note_to_hz("C3"), n_bins=180,
                           bins_per_octave=36))
    D = librosa.amplitude_to_db(C, ref=np.max)
    mx = ndimage.maximum_filter(D, size=(7, 7))
    pk = (D == mx) & (D > -45) & (D > D.max(0, keepdims=True) - 30)
    fb, tf = np.nonzero(pk)
    # at most 5 per frame
    keep = []
    for fr in np.unique(tf):
        idx = np.flatnonzero(tf == fr)
        if len(idx) > 5:
            idx = idx[np.argsort(-D[fb[idx], fr])[:5]]
        keep.extend(idx.tolist())
    keep = np.array(sorted(keep, key=lambda i: (tf[i], fb[i])), dtype=int)
    fb, tf = fb[keep], tf[keep]
    hashes = []
    for i in range(len(tf)):
        j = i + 1
        n = 0
        while j < len(tf) and tf[j] - tf[i] <= 24 and n < 8:
            if tf[j] > tf[i] and abs(fb[j] - fb[i]) <= 24:
                hashes.append((int(fb[i]), int(fb[j] - fb[i]), int(tf[j] - tf[i]), int(tf[i])))
                n += 1
            j += 1
    return hashes


def fp_match(cand, ref):
    idx = {}
    for f1, dfb, dt, t1 in ref:
        idx.setdefault((f1, dfb, dt), []).append(t1)
    best, best_s = 0, 0
    for s in range(-27, 28):
        offs = []
        for f1, dfb, dt, t1 in cand:
            for tr in idx.get((f1 + s, dfb, dt), ()):
                offs.append(tr - t1)
        if not offs:
            continue
        h = np.bincount(np.array(offs) - min(offs))
        hh = h + np.r_[h[1:], 0] + np.r_[0, h[:-1]]
        c = int(hh.max())
        if c > best:
            best, best_s = c, s
    return best / max(1, len(cand)), best_s / 3.0


# ------------------------------------------------------------------------------------------------- symbolic
def load_ref_melody():
    j = json.load(open(MUZIK_JSON))
    return [(int(n["bar"]), float(n["beat"]), float(n["dur_beats"]), int(n["midi"])) for n in j["melody"]], j


def norm_notes(notes):
    out = []
    for n in notes:
        if isinstance(n, dict):
            out.append((int(n["bar"]), float(n["beat"]), float(n.get("dur_beats", n.get("dur", 1))), int(n["midi"])))
        else:
            out.append((int(n[0]), float(n[1]), float(n[2]), int(n[3])))
    out.sort(key=lambda x: (x[0], x[1]))
    return out


def slot(bar, beat):
    return int(round((3 * bar + beat - 1) * 3))


def ngram_set(notes, n, metric=True):
    """n = number of intervals. key = (intervals, IOIs in triplet slots[, start slot in bar])"""
    out = []
    for i in range(len(notes) - n):
        w = notes[i:i + n + 1]
        iv = tuple(w[k + 1][3] - w[k][3] for k in range(n))
        sl = [slot(x[0], x[1]) for x in w]
        ioi = tuple(sl[k + 1] - sl[k] for k in range(n))
        key = (iv, ioi, sl[0] % 9) if metric else (iv, ioi)
        out.append(key)
    return out


def bar_grid(notes):
    """pitch at each triplet slot (held notes carried), per bar index -> dict bar -> 9 values"""
    if not notes:
        return {}
    s0 = min(slot(b, bt) for b, bt, d, m in notes)
    s1 = max(slot(b, bt) + max(1, int(round(d * 3))) for b, bt, d, m in notes)
    g = np.full(s1 - min(0, s0) + 9, np.nan)
    base = min(0, s0)
    for b, bt, d, m in notes:
        a = slot(b, bt) - base
        e = a + max(1, int(round(d * 3)))
        g[a:e] = m
    # carry forward through rests
    last = np.nan
    for i in range(len(g)):
        if np.isnan(g[i]):
            g[i] = last
        else:
            last = g[i]
    bars = {}
    for b in sorted(set(n[0] for n in notes)):
        a = 9 * b - base
        if a >= 0 and a + 9 <= len(g):
            bars[b] = g[a:a + 9]
    return bars


def onset_patterns(notes):
    bp = {}
    for b, bt, d, m in notes:
        bp.setdefault(b, set()).add(int(round((bt - 1) * 3)))
    return {b: frozenset(v) for b, v in bp.items()}


GENERIC_CELLS = {frozenset({0, 3, 6}), frozenset({0, 3}), frozenset({0, 6}), frozenset({0}), frozenset({3, 6}),
                 frozenset({3}), frozenset({6}), frozenset({0, 6}), frozenset()}


def symbolic(cand_notes, ref_notes, tonic=0):
    sys.path.insert(0, OFFLIMITS_DIR)
    import offlimits
    res = {}
    ol = offlimits.check([{"bar": b, "beat": bt, "dur_beats": d, "midi": m} for b, bt, d, m in cand_notes], tonic)
    res["offlimits"] = {"violations": ol["violations"], "POV": ol["POV"], "POV_status": ol["POV_status"],
                        "N5": len(ol["N5"]), "signatures": [s[0] for s in ol["signatures"]],
                        "rhythm_cells": [r[0] for r in ol["rhythm_cells"]], "SK": len(ol["SK"]),
                        "ALT_warn": len(ol["ALT_warn"])}
    for n in (3, 4):
        for metric in (True, False):
            cs = ngram_set(cand_notes, n, metric)
            rs = set(ngram_set(ref_notes, n, metric))
            shared = [k for k in cs if k in rs]
            key = f"ngram{n}_{'metric' if metric else 'free'}"
            res[key] = {"shared": len(shared), "of": len(cs), "share": (len(shared) / len(cs)) if cs else 0.0}
    # contour: per-bar correlation and whole-phrase correlation, best over bar offsets -2..2
    cg, rg = bar_grid(cand_notes), bar_grid(ref_notes)
    best_bar, best_phrase = (-2.0, None), (-2.0, None)
    for off in range(-2, 3):
        rs_, xs, ys = [], [], []
        for b, v in cg.items():
            r = rg.get(b + off)
            if r is None:
                continue
            xs.append(v); ys.append(r)
            if np.std(v) > 0 and np.std(r) > 0:
                rs_.append(np.corrcoef(v, r)[0, 1])
        if len(rs_) >= 3:
            mb = float(np.mean(rs_))
            if mb > best_bar[0]:
                best_bar = (mb, off)
        if len(xs) >= 4:
            X, Y = np.concatenate(xs), np.concatenate(ys)
            if np.std(X) > 0 and np.std(Y) > 0:
                pc = float(np.corrcoef(X, Y)[0, 1])
                if pc > best_phrase[0]:
                    best_phrase = (pc, off)
    res["contour_bar_corr"] = {"value": best_bar[0] if best_bar[1] is not None else None, "bar_offset": best_bar[1]}
    res["contour_phrase_corr"] = {"value": best_phrase[0] if best_phrase[1] is not None else None,
                                  "bar_offset": best_phrase[1]}
    # rhythm cells: same onset pattern in the same bar (best offset); distinctive = patterns with subdivisions
    cp, rp = onset_patterns(cand_notes), onset_patterns(ref_notes)
    best_all, best_dist = 0.0, 0.0
    for off in range(-2, 3):
        same = [b for b, p in cp.items() if rp.get(b + off) == p]
        dist = [b for b in same if cp[b] not in GENERIC_CELLS]
        best_all = max(best_all, len(same) / max(1, len(cp)))
        best_dist = max(best_dist, len(dist))
    ref_cells = {p for p in rp.values() if p not in GENERIC_CELLS}
    cand_cells = {p for p in cp.values() if p not in GENERIC_CELLS}
    res["rhythm_same_bar_share"] = best_all
    res["rhythm_distinctive_same_bar"] = best_dist
    res["rhythm_distinctive_cells_shared"] = len(ref_cells & cand_cells)
    # melody statistics vs the original's
    def stats(ns):
        ms = [m for _, _, _, m in ns]
        iv = np.diff(ms)
        a = np.abs(iv)
        return {"range_semitones": int(max(ms) - min(ms)), "low": int(min(ms)), "high": int(max(ms)),
                "steps": float(np.mean((a >= 1) & (a <= 2))), "thirds": float(np.mean((a >= 3) & (a <= 4))),
                "repeats": float(np.mean(a == 0)), "leaps_ge4": float(np.mean(a >= 5)),
                "triplet_share": float(np.mean([abs(d - 1 / 3) < 0.02 for _, _, d, _ in ns])),
                "notes": len(ns), "notes_per_bar": len(ns) / max(1, len(set(b for b, _, _, _ in ns)))}
    res["melody_stats"] = stats(cand_notes)
    res["melody_stats_original"] = stats(ref_notes)
    # verdict
    reasons = []
    o = res["offlimits"]
    if o["violations"] > 0:
        reasons.append(f"offlimits violations={o['violations']}")
    if o["POV"] >= SYM_THR["POV"]:
        reasons.append(f"POV {o['POV']:.2f} >= {SYM_THR['POV']}")
    if res["ngram3_metric"]["share"] > SYM_THR["ngram3_metric_share"]:
        reasons.append(f"ngram3_metric share {res['ngram3_metric']['share']:.2f} > {SYM_THR['ngram3_metric_share']}")
    if res["ngram4_free"]["share"] > SYM_THR["ngram4_free_share"]:
        reasons.append(f"ngram4_free share {res['ngram4_free']['share']:.2f} > {SYM_THR['ngram4_free_share']}")
    cb = res["contour_bar_corr"]["value"]
    if cb is not None and cb > SYM_THR["contour_bar_corr"]:
        reasons.append(f"contour_bar_corr {cb:.2f} > {SYM_THR['contour_bar_corr']}")
    cpv = res["contour_phrase_corr"]["value"]
    if cpv is not None and cpv > SYM_THR["contour_phrase_corr"]:
        reasons.append(f"contour_phrase_corr {cpv:.2f} > {SYM_THR['contour_phrase_corr']}")
    if res["rhythm_distinctive_same_bar"] > SYM_THR["rhythm_distinctive_same_bar"]:
        reasons.append(f"distinctive rhythm cells in the same bars {res['rhythm_distinctive_same_bar']} > "
                       f"{SYM_THR['rhythm_distinctive_same_bar']}")
    res["verdict"] = "FAIL" if reasons else "PASS"
    res["reasons"] = reasons
    res["rule"] = SYM_RULE
    return res


def parse_chords(chords):
    """accepts ["Cm","G7",...] (one per bar from bar 0) or [{"bar":..,"chord":..}]; returns {bar: (root_pc, qual)}"""
    out = {}
    def rq(name):
        m = re.match(r"\s*([A-G])([b#]?)(.*)", name or "")
        if not m:
            return None
        pc = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}[m.group(1)]
        pc = (pc + (1 if m.group(2) == "#" else -1 if m.group(2) == "b" else 0)) % 12
        rest = m.group(3).lower()
        q = "dim" if ("dim" in rest or "°" in rest) else "min" if (rest.startswith("m") and not rest.startswith("maj")) or rest.startswith(":m") else "maj"
        return pc, q
    for i, c in enumerate(chords or []):
        if isinstance(c, dict):
            b = int(c.get("bar", i))
            if b in out:
                continue
            v = rq(c.get("chord") or c.get("name") or c.get("root", ""))
        else:
            b, v = i, rq(str(c))
        if v:
            out[b] = v
    return out


def chord_check(cand_chords, ref_json):
    rc = parse_chords([{"bar": h["bar"], "chord": h["chord"].replace("Bdim", "Bdim")} for h in ref_json["harmony"]])
    cc = parse_chords(cand_chords)
    best = (0, 0)
    for off in range(-2, 3):
        run = mx = 0
        for b in sorted(cc):
            if rc.get(b + off) == cc[b]:
                run += 1; mx = max(mx, run)
            else:
                run = 0
        best = max(best, (mx, off))
    # strict i <-> V/vii alternation runs
    alt = run = 0
    bars = sorted(cc)
    for i in range(1, len(bars)):
        a, b = cc[bars[i - 1]], cc[bars[i]]
        tonic_dom = {a[0], b[0]} in ({0, 11}, {0, 7}, {0, 2})
        run = run + 1 if tonic_dom and a != b else 0
        alt = max(alt, run + 1 if run else 0)
    return {"longest_same_chord_run": best[0], "bar_offset": best[1], "i_V_alternation_bars": alt,
            "warn": alt >= 4}


# symbolic thresholds (derived in kalibrasyon.md from 3000 random C-minor waltz melodies; p99 of the null)
SYM_THR = {"POV": 0.25, "ngram3_metric_share": 0.15, "ngram4_free_share": 0.10, "contour_bar_corr": 0.75,
           "contour_phrase_corr": 0.65, "rhythm_distinctive_same_bar": 2}
SYM_RULE = ("FAIL if any: offlimits.py violations > 0 (its N5/S/R/SK rules); POV >= 0.25; share of the candidate's 4-note "
            "windows (3 intervals + IOIs + start slot in bar) found in the original > 0.15; share of its 5-note windows "
            "(4 intervals + IOIs, any metric position) found in the original > 0.10; mean per-bar contour correlation "
            "(best bar offset -2..2) > 0.75; whole-phrase contour correlation > 0.65; more than 2 bars with the same "
            "distinctive (subdivided) rhythm cell as the original's same bar. Null (3000 random C-minor waltz melodies): "
            "max POV 0.24, max ngram3 0.13, max ngram4 0.09, p99 contour_bar 0.66, p99 contour_phrase 0.53, p99 rhythm 2; "
            "null FAIL rate about 2-3 % (mostly offlimits.py chance hits). Every disguised copy of the original FAILs "
            "(kalibrasyon.md).")


# ---------------------------------------------------------------------------------------------- features
def features(path, y=None, with_cqt=True):
    t0 = time.time()
    info = probe(path) if path else {}
    if y is None:
        y = decode(path)
    full_dur = len(y) / SR
    loud = ebur128(path) if path else {}
    y = y[: int(WIN_S * SR)]
    if len(y) < int(WIN_S * SR):
        y = np.pad(y, ((0, int(WIN_S * SR) - len(y)), (0, 0)))
    a0i, a1i, thr, tail_end = active_region(y, loud.get("I"))
    a0, a1 = a0i / SR, a1i / SR
    mid = (y[:, 0] + y[:, 1]) / 2
    F = {"info": info, "duration_s": full_dur, "first_sound_s": a0, "last_sound_s": a1, "active_thr_dbfs": thr, "tail_end_s": tail_end,
         "loud": loud, "sample_peak_dbfs": float(20 * np.log10(np.max(np.abs(y)) + 1e-12)),
         "clip_samples": int(np.sum(np.abs(y) >= 0.9999)),
         "dc_dbfs": [float(20 * np.log10(abs(np.mean(y[a0i:a1i, c])) + 1e-12)) for c in range(2)]}
    F["clicks"] = clicks(mid[a0i:a1i])
    F["hum"] = hum_lines(mid[a0i:a1i])
    F["ltas"] = ltas_third(mid[a0i:a1i])
    y22 = ss.resample_poly(mid, 1, 2)
    F["melmfcc"] = mel_mfcc(y22, (a0, a1))
    F["spec"] = shares_centroid_flatness(y22, (a0, a1))
    F["noise"] = noise_floor(mid, a0, a1)
    te, env, fse = band_envelopes(mid, a0, a1)
    F["mod"] = modulation(te, env, fse)
    F["level"] = level_stats(mid, a0i, a1i)
    pt = peaks_and_tracks(mid, a0, a1)
    F["pitch"] = pitch_features(pt)
    F["stereo"] = stereo_room(y, a0i, a1i)
    F["mus"] = musical(y22, (a0, a1))
    F["accent"] = accent_pattern(y22, F["mus"]["tempo_bpm"], F["mus"]["beat_phase_s"], (a0, a1))
    F["chroma"] = chroma_seq(y22)
    F["fp"] = fingerprint(y22)
    if with_cqt:
        import librosa
        g = 10 ** ((-29.5 - (loud.get("I") or -29.5)) / 20) if loud.get("I") is not None else 1.0
        C = np.abs(librosa.cqt(y22 * g, sr=22050, hop_length=256, fmin=librosa.note_to_hz("C2"), n_bins=7 * 24,
                               bins_per_octave=24))
        F["cqt_db"] = librosa.amplitude_to_db(C, ref=1.0, amin=1e-7).astype(np.float32)
        F["cqt_gain_db"] = float(20 * np.log10(g))
    F["elapsed_s"] = time.time() - t0
    return F


def ref_features(ref_path, refresh=False):
    os.makedirs(CACHE_DIR, exist_ok=True)
    st = os.stat(ref_path)
    key = hashlib.sha1(f"{os.path.abspath(ref_path)}|{st.st_size}|{st.st_mtime}|{VERSION}".encode()).hexdigest()[:12]
    cp = os.path.join(CACHE_DIR, f"ref_{key}.pkl")
    src_hash = hashlib.sha1(open(__file__, "rb").read()).hexdigest()[:12]
    if os.path.exists(cp) and not refresh:
        with open(cp, "rb") as fh:
            d = pickle.load(fh)
        if d.get("src_hash") == src_hash:
            return d["F"]
    F = features(ref_path)
    with open(cp, "wb") as fh:
        pickle.dump({"F": F, "src_hash": src_hash}, fh)
    return F


# -------------------------------------------------------------------------------------------- comparison
TIMBRE_WEIGHTS = {
    # name: (weight, tau, description)
    "ltas_db": (14, 3.0, "1/3-oct long-term spectrum, 125 Hz-6.3 kHz, dB RMS difference (level-normalised on 250-4000)"),
    "mel_env_db": (7, 3.0, "mean log-mel envelope (typical frame), dB RMS difference 80 Hz-6 kHz"),
    "mfcc": (7, 15.0, "Euclidean distance of mean MFCC c1-c19"),
    "band_shares": (5, 0.10, "total-variation distance of the <250/250-1k/1-4k/>4k energy shares"),
    "centroid": (4, 0.25, "|log2| ratio of the power-weighted spectral centroid (octaves)"),
    "flatness": (4, 0.30, "|log10| ratio of the median core-band (250-4000) spectral flatness"),
    "noise_floor": (8, 4.0, "inter-harmonic floor (p10 of bins per 1/3-oct band re band mean), mean |dB| difference"),
    "modulation": (14, 0.20, "modulation spectrum 0.5-20 Hz of 4 band envelopes: 1 - Pearson r (shape) + depth/12 dB"),
    "pitch": (10, 1.0, "pitch behaviour: |d vibrato|/4 c + |d band pitch-deviation std|/6 c + |d partial spread|/6 c + |log d vibrato peakiness|/log 4"),
    "stereo": (6, 1.0, "|d L/R corr|/0.15 + |d side-mid dB|/3"),
    "reverb": (6, 6.0, "side-from-mid identified response, dB RMS difference at 10-300 ms (mono: fixed 15 dB)"),
    "dynamics": (8, 1.0, "|d 100 ms level std|/1.5 + |d fast fluct|/1 + |d crest|/2 + |d LRA|/2 (sum)"),
    "accent": (7, 1.0, "waltz beat accent ('u a a'): |d brightness contrast|/2 dB + |d bright-pair balance|/2 + |d level contrast|/2"),
}


def compare(R, C):
    out = {}
    # ---- LTAS
    fc = np.array(R["ltas"]["fc"])
    m = (fc >= 125) & (fc <= 6300)
    r = np.maximum(np.array(R["ltas"]["rel_db"]), -45)
    c = np.maximum(np.array(C["ltas"]["rel_db"]), -45)
    core = (fc >= 250) & (fc <= 4000)
    out["ltas_db"] = float(np.sqrt(np.mean((c[m] - r[m]) ** 2)))
    out["ltas_core_db"] = float(np.sqrt(np.mean((c[core] - r[core]) ** 2)))
    out["ltas_diff_by_band"] = {str(int(f) if f >= 100 else f): round(float(d), 1) for f, d in zip(fc[m], (c - r)[m])}
    mf = np.array(R["melmfcc"]["mel_f"])
    mm = (mf >= 80) & (mf <= 6000)
    out["mel_env_db"] = float(np.sqrt(np.mean((np.array(C["melmfcc"]["mel_env"])[mm] -
                                               np.array(R["melmfcc"]["mel_env"])[mm]) ** 2)))
    out["mfcc"] = float(np.linalg.norm(np.array(C["melmfcc"]["mfcc_mean"]) - np.array(R["melmfcc"]["mfcc_mean"])))
    out["mfcc_std_dist"] = float(np.linalg.norm(np.array(C["melmfcc"]["mfcc_std"]) - np.array(R["melmfcc"]["mfcc_std"])))
    rs, cs = R["spec"]["shares"], C["spec"]["shares"]
    out["band_shares"] = float(0.5 * sum(abs(cs[k] - rs[k]) for k in rs))
    out["centroid"] = float(abs(np.log2(C["spec"]["centroid_hz"] / R["spec"]["centroid_hz"])))
    out["flatness"] = float(abs(np.log10(C["spec"]["flatness_core_median"] / R["spec"]["flatness_core_median"])))
    nr, nc = np.array(R["noise"]["floor_rel_band_db"]), np.array(C["noise"]["floor_rel_band_db"])
    out["noise_floor"] = float(np.mean(np.abs(nc - nr)))
    out["noise_floor_signed_db"] = float(np.mean(nc - nr))
    out["noise_shape_db"] = float(np.sqrt(np.mean(((nc - nc.mean()) - (nr - nr.mean())) ** 2)))
    # ---- modulation
    Ms, Mc = np.array(R["mod"]["spec_db"]).ravel(), np.array(C["mod"]["spec_db"]).ravel()
    rmod = float(np.corrcoef(Ms, Mc)[0, 1])
    depth = float(np.mean(Mc - Ms))
    out["modulation_r"] = rmod
    out["modulation_depth_db"] = depth
    out["modulation"] = (1 - rmod) + abs(depth) / 12
    # ---- pitch
    pr, pc = R["pitch"] or {}, C["pitch"] or {}
    def g(d, k, default=0.0):
        v = d.get(k)
        return default if v is None else v
    out["pitch"] = (abs(g(pc, "vibrato_rms_c") - g(pr, "vibrato_rms_c")) / 4 +
                    abs(g(pc, "pitch_dev_band_std_c") - g(pr, "pitch_dev_band_std_c")) / 6 +
                    abs(g(pc, "partial_spread_c") - g(pr, "partial_spread_c")) / 6 +
                    abs(np.log(g(pc, "vibrato_peakiness", 1) / g(pr, "vibrato_peakiness", 1))) / np.log(4))
    # ---- stereo / room
    sr_, sc_ = R["stereo"], C["stereo"]
    out["stereo"] = abs(sc_["lr_corr"] - sr_["lr_corr"]) / 0.15 + abs(max(sc_["side_mid_db"], -30) - sr_["side_mid_db"]) / 3
    if sc_.get("ir_env_db") is None or sr_.get("ir_env_db") is None:
        out["reverb"] = 15.0
    else:
        out["reverb"] = float(np.sqrt(np.mean((np.maximum(np.array(sc_["ir_env_db"]), -40) -
                                               np.maximum(np.array(sr_["ir_env_db"]), -40)) ** 2)))
    # ---- dynamics
    lr, lc = R["level"], C["level"]
    lra_r, lra_c = (R["loud"].get("LRA") or 0), (C["loud"].get("LRA") or 0)
    out["dynamics"] = (abs(lc["rms100_std_db"] - lr["rms100_std_db"]) / 1.5 + abs(lc["fast_fluct_std_db"] - lr["fast_fluct_std_db"]) / 1.0
                       + abs(lc["crest50_median_db"] - lr["crest50_median_db"]) / 2 + abs(lra_c - lra_r) / 2)
    ar, ac = R["accent"], C["accent"]
    out["accent"] = (abs(ac["contrast_db"] - ar["contrast_db"]) / 2 + abs(ac["balance_db"] - ar["balance_db"]) / 2
                     + abs(ac["level_contrast_db"] - ar["level_contrast_db"]) / 2)
    # ---- score
    subs, tot, wsum = {}, 0.0, 0.0
    for k, (w, tau, _) in TIMBRE_WEIGHTS.items():
        s = cauchy(out[k], tau)
        subs[k] = s
        tot += w * s
        wsum += w
    out["subscores"] = subs
    out["TIMBRE_SCORE"] = tot / wsum
    return out


# ---------------------------------------------------------------------------------------------------- report
def M(value, original, desc, **kw):
    d = {"value": rnd(value), "original": rnd(original), "desc": desc}
    d.update({k: rnd(v) for k, v in kw.items()})
    return d


def report(path, R, C, cmpd, sym=None, chords=None):
    L, LR = C["loud"], R["loud"]
    tech = {
        "duration_s": M(C["duration_s"], R["duration_s"], "decoded file length"),
        "first_sound_s": M(C["first_sound_s"], R["first_sound_s"], "first 10 ms frame above (LUFS-I - 16 dB; original -45.5 dBFS); target 0.00"),
        "last_sound_s": M(C["last_sound_s"], R["last_sound_s"], "end of the last 10 ms frame above (LUFS-I - 16 dB); target <= 13.75"),
        "tail_end_s": M(C["tail_end_s"], R["tail_end_s"], "end of the last 10 ms frame above (LUFS-I - 40 dB): any residual tail"),
        "lufs_integrated": M(L.get("I"), LR.get("I"), "EBU R128 integrated loudness (ffmpeg ebur128); target -29.5 +-0.5"),
        "lra_lu": M(L.get("LRA"), LR.get("LRA"), "EBU R128 loudness range"),
        "true_peak_dbtp": M(L.get("TP"), LR.get("TP"), "true peak (ffmpeg ebur128 peak=true); target <= -17"),
        "sample_peak_dbfs": M(C["sample_peak_dbfs"], R["sample_peak_dbfs"], "max |sample|"),
        "clip_samples": M(C["clip_samples"], R["clip_samples"], "samples with |x| >= 0.9999"),
        "clicks": M(C["clicks"]["count"], R["clicks"]["count"], "isolated AR(32)-residual spikes > 16 robust sigma (< 3 ms; hits within 60 ms count once)",
                    first_times_s=C["clicks"]["times_s"][:10], resid_kurtosis=C["clicks"]["resid_kurtosis"],
                    resid_kurtosis_original=R["clicks"]["resid_kurtosis"]),
        "dc_dbfs": M(max(C["dc_dbfs"]), max(R["dc_dbfs"]), "channel mean (worse channel), dBFS"),
        "hum_100hz_dbfs": M(C["hum"]["100"], R["hum"]["100"], "100 Hz line, sine-peak dBFS (original -70.4)",
                            hz50=C["hum"]["50"], hz150=C["hum"]["150"], hz200=C["hum"]["200"]),
        "rumble_lt25hz_dbfs": M(C["hum"]["rumble_lt25_rms_dbfs"], R["hum"]["rumble_lt25_rms_dbfs"], "RMS below 25 Hz"),
        "format": C["info"],
    }
    tim = {
        "ltas_dist_db": M(cmpd["ltas_db"], 0, "1/3-oct LTAS distance 125-6300 Hz, dB RMS (bands floored at -45 dB re 250-4k)",
                          core_250_4k=cmpd["ltas_core_db"], diff_by_band_db=None),
        "ltas_diff_by_band_db": cmpd["ltas_diff_by_band"],
        "mel_env_dist_db": M(cmpd["mel_env_db"], 0, "mean log-mel envelope distance 80-6000 Hz, dB RMS"),
        "mfcc_dist": M(cmpd["mfcc"], 0, "Euclidean distance of mean MFCC c1-c19 (librosa units)", std_vector_dist=cmpd["mfcc_std_dist"]),
        "band_shares": M(C["spec"]["shares"], R["spec"]["shares"], "energy shares <250 / 250-1k / 1-4k / >4k",
                         tv_dist=cmpd["band_shares"]),
        "centroid_hz": M(C["spec"]["centroid_hz"], R["spec"]["centroid_hz"], "power-weighted spectral centroid",
                         frame_median=C["spec"]["frame_centroid_median_hz"], frame_median_original=R["spec"]["frame_centroid_median_hz"]),
        "rolloff95_hz": M(C["spec"]["rolloff95_hz"], R["spec"]["rolloff95_hz"], "95 % energy roll-off of the long-term spectrum"),
        "flatness": M(C["spec"]["flatness_core_median"], R["spec"]["flatness_core_median"],
                      "median spectral flatness inside 250-4000 Hz (higher = noisier / denser)",
                      fullband=C["spec"]["flatness_median"], fullband_original=R["spec"]["flatness_median"]),
        "noise_floor": M(C["noise"]["floor_rel_band_db"], R["noise"]["floor_rel_band_db"],
                         "per 1/3-oct band 250-4k: median over frames of p10(bin power)/mean(bin power), dB (more negative = cleaner valleys)",
                         mean_abs_diff_db=cmpd["noise_floor"], signed_diff_db=cmpd["noise_floor_signed_db"],
                         shape_diff_db=cmpd["noise_shape_db"], fc=C["noise"]["fc"]),
        "modulation": M(C["mod"]["fluct_rms_db"], R["mod"]["fluct_rms_db"],
                        "band-envelope fluctuation, RMS dB in modulation ranges 0.5-2 / 2-8 / 8-20 Hz",
                        spectrum_r=cmpd["modulation_r"], depth_diff_db=cmpd["modulation_depth_db"]),
        "vibrato_rms_c": M((C["pitch"] or {}).get("vibrato_rms_c"), (R["pitch"] or {}).get("vibrato_rms_c"),
                           "3.5-9 Hz pitch modulation of partial tracks >= 0.4 s, cents RMS (weighted median)",
                           rate_hz=(C["pitch"] or {}).get("vibrato_rate_hz"), peakiness=(C["pitch"] or {}).get("vibrato_peakiness"),
                           peakiness_original=(R["pitch"] or {}).get("vibrato_peakiness")),
        "pitch_instability_c": M((C["pitch"] or {}).get("pitch_dev_band_std_c"), (R["pitch"] or {}).get("pitch_dev_band_std_c"),
                                 "std of the 0.2 s-smoothed deviation from 12-TET in 3 register bands (240-470/480-940/1400-2500 Hz), mean of bands: per-note mistuning + bends + wow",
                                 per_band=(C["pitch"] or {}).get("pitch_dev_band_std_each_c"),
                                 coherence_r=(C["pitch"] or {}).get("pitch_dev_coherence_r"),
                                 coherence_r_original=(R["pitch"] or {}).get("pitch_dev_coherence_r"),
                                 common_std_c=(C["pitch"] or {}).get("pitch_dev_common_std_c"),
                                 common_std_c_original=(R["pitch"] or {}).get("pitch_dev_common_std_c"),
                                 common_p5_p95=(C["pitch"] or {}).get("pitch_dev_p5_p95_c")),
        "texture_peaks_per_frame": M((C["pitch"] or {}).get("peaks_per_frame_median"), (R["pitch"] or {}).get("peaks_per_frame_median"),
                                     "median number of spectral peaks per 46 ms frame in 240-2600 Hz (>= -30 dB re frame max, 6 dB prominence): texture density"),
        "glide_share": M((C["pitch"] or {}).get("glide_share"), (R["pitch"] or {}).get("glide_share"),
                         "weighted share of partial-track frames moving faster than 600 cents/s (portamento / bends)"),
        "tuning_offset_c": M((C["pitch"] or {}).get("tuning_offset_c"), (R["pitch"] or {}).get("tuning_offset_c"), "mean deviation from A440 12-TET"),
        "partial_spread_c": M((C["pitch"] or {}).get("partial_spread_c"), (R["pitch"] or {}).get("partial_spread_c"),
                              "circular std of simultaneous partials' deviations (ensemble detune / mistuning), weighted median"),
        "stereo_lr_corr": M(C["stereo"]["lr_corr"], R["stereo"]["lr_corr"], "L/R Pearson correlation (active part)",
                            side_mid_db=C["stereo"]["side_mid_db"], side_mid_db_original=R["stereo"]["side_mid_db"],
                            corr_300_4k=C["stereo"]["lr_corr_300_4k"], corr_300_4k_original=R["stereo"]["lr_corr_300_4k"]),
        "mono_fold_db": M(C["stereo"]["mono_fold_std_db"], R["stereo"]["mono_fold_std_db"],
                          "mono fold-down: std over 300-3000 Hz of 10log10(P_mid / mean(P_L, P_R)) in 2.7 Hz bins (comb filtering in mono)",
                          mean_db=C["stereo"]["mono_fold_mean_db"], min_db=C["stereo"]["mono_fold_min_db"],
                          min_db_original=R["stereo"]["mono_fold_min_db"]),
        "reverb_ir_env_db": M(C["stereo"].get("ir_env_db"), R["stereo"].get("ir_env_db"),
                              "side-from-mid identified response energy (dB re peak) at 10,20,30,50,75,100,150,200,300 ms; None = mono/no side",
                              dist_db=cmpd["reverb"], peak_ms=C["stereo"].get("ir_peak_ms"), peak_ms_original=R["stereo"].get("ir_peak_ms")),
        "level_std_100ms_db": M(C["level"]["rms100_std_db"], R["level"]["rms100_std_db"], "std of 100 ms RMS (active part)",
                                p10_p90=C["level"]["rms100_p10_p90_db"], p10_p90_original=R["level"]["rms100_p10_p90_db"]),
        "level_fast_fluct_db": M(C["level"]["fast_fluct_std_db"], R["level"]["fast_fluct_std_db"],
                                 "std of 20 ms level minus its 0.3 s moving average (shimmer / articulation)"),
        "crest_50ms_db": M(C["level"]["crest50_median_db"], R["level"]["crest50_median_db"], "median crest factor of 50 ms windows"),
        "fastest_drop_db_s": M(C["level"]["fastest_drop_db_s"], R["level"]["fastest_drop_db_s"],
                               "2nd percentile of the 20 ms level slope (how fast sound can fall: articulation + room)"),
        "accent_uaa": M(C["accent"]["tilt_from_dark_db"], R["accent"]["tilt_from_dark_db"],
                        "per-beat brightness tilt L(1-4k)-L(250-500) by beat position, rotated to start on the darkest ('u a a' = dark, bright, bright)",
                        contrast_db=C["accent"]["contrast_db"], contrast_db_original=R["accent"]["contrast_db"],
                        balance_db=C["accent"]["balance_db"], balance_db_original=R["accent"]["balance_db"],
                        level_from_dark_db=C["accent"]["level_from_dark_db"], level_from_dark_db_original=R["accent"]["level_from_dark_db"]),
    }
    mus = {
        "tempo_bpm": M(C["mus"]["tempo_bpm"], R["mus"]["tempo_bpm"], "beat-grid fit to the onset envelope, 110-190 BPM, 0.1 BPM steps",
                       comb_acf=C["mus"]["tempo_comb_bpm"], comb_acf_original=R["mus"]["tempo_comb_bpm"],
                       librosa_beat_track=C["mus"]["beat_track_bpm"], librosa_original=R["mus"]["beat_track_bpm"]),
        "triple_metre": M(C["mus"]["triple_metre"], R["mus"]["triple_metre"], "ACF(3 beats) - mean(ACF(2), ACF(4)): > 0 = 3/4 feel"),
        "key": M(C["mus"]["key_best"], R["mus"]["key_best"], "Krumhansl-Kessler best key on mean chroma",
                 r=C["mus"]["key_best_r"], r_original=R["mus"]["key_best_r"], c_minor_r=C["mus"]["c_minor_r"],
                 profile_corr_with_original=float(np.corrcoef(C["mus"]["chroma_profile"], R["mus"]["chroma_profile"])[0, 1])),
        "onsets_per_bar": M(C["mus"]["onsets_per_bar"], R["mus"]["onsets_per_bar"], "librosa onsets in the active part / bars at the measured tempo",
                            per_s=C["mus"]["onsets_per_s"], per_s_original=R["mus"]["onsets_per_s"]),
        "harmonic_rocking": M(C["mus"]["chroma_lag2bar"], R["mus"]["chroma_lag2bar"],
                              "chroma self-similarity at a 2-bar lag (own tempo); with lag1bar: original rocks i<->vii (lag2 high, lag1 low)",
                              lag1bar=C["mus"]["chroma_lag1bar"], lag1bar_original=R["mus"]["chroma_lag1bar"]),
        "bar_levels_db": M(C["level"]["bar_db"], R["level"]["bar_db"], "RMS per 1.19 s window from the first sound, dB re the median window (dynamic arch)"),
        "start_level_db": M(C["level"]["start_db"], R["level"]["start_db"], "first 0.5 s RMS re the median 0.5 s window"),
        "end_hold_db": M(C["level"]["end_db"], R["level"]["end_db"], "RMS of the last 1.0 s before the last sound re the median (held tonic vs fade)"),
        "legato_gap_fraction": M(C["level"]["gap_fraction"], R["level"]["gap_fraction"], "share of 10 ms frames > 20 dB under the median level",
                                 longest_gap_ms=C["level"]["longest_gap_ms"], p2_level_re_median_db=C["level"]["p2_level_re_median_db"],
                                 p2_level_re_median_db_original=R["level"]["p2_level_re_median_db"]),
    }
    cs, rot, lag, _ = chroma_sim(C["chroma"], R["chroma"], transpose=False)
    cst, rott, lagt, sct = chroma_sim(C["chroma"], R["chroma"], transpose=True, scales=SCALES)
    fpm, fps = fp_match(C["fp"], R["fp"])
    org = {
        "chroma_seq_sim": M(cs, 1.0, "tools/imza_muzik.py karsilastir method (baselines: copy 0.986, unrelated 0.139)",
                            lag_s=lag),
        "chroma_seq_sim_transposed": M(cst, 1.0, "same, best of 12 chroma rotations and of time scales 0.94-1.06 "
                                       "(catches transposed / tempo-changed copies)", rotation_semitones=rott, lag_s=lagt,
                                       time_scale=sct),
        "fingerprint_match": M(fpm, 1.0, "share of candidate peak-pair hashes that match the original with one consistent time offset "
                               "(pitch shift searched +-9 semitones); detects reused audio", shift_semitones=fps),
    }
    reasons = []
    if cst >= AUD_THR["chroma_fail"]:
        reasons.append(f"chroma_seq_sim_transposed {cst:.2f} >= {AUD_THR['chroma_fail']}")
    if fpm >= AUD_THR["fp_fail"]:
        reasons.append(f"fingerprint_match {fpm:.3f} >= {AUD_THR['fp_fail']}")
    warn = []
    if AUD_THR["chroma_warn"] <= cst < AUD_THR["chroma_fail"]:
        warn.append(f"chroma_seq_sim_transposed {cst:.2f} in warn zone [{AUD_THR['chroma_warn']}, {AUD_THR['chroma_fail']})")
    org["audio_verdict"] = "FAIL" if reasons else "PASS"
    org["audio_reasons"] = reasons
    org["audio_warnings"] = warn
    org["audio_rule"] = AUD_RULE
    if sym is not None:
        org["symbolic"] = {k: rnd(v) if not isinstance(v, dict) else {kk: rnd(vv) for kk, vv in v.items()} for k, v in sym.items()}
        if chords is not None:
            org["symbolic"]["chords"] = chords
    verdict = org["audio_verdict"]
    if sym is not None and sym["verdict"] == "FAIL":
        verdict = "FAIL"
    org["verdict"] = verdict if sym is not None else verdict + " (audio only; pass --notalar for the symbolic check)"
    out = {"file": os.path.abspath(path), "olcum_version": VERSION, "TIMBRE_SCORE": round(cmpd["TIMBRE_SCORE"], 1),
           "timbre_subscores": {k: {"score": rnd(v, 1), "dist": rnd(cmpd[k]), "weight": TIMBRE_WEIGHTS[k][0],
                                    "tau": TIMBRE_WEIGHTS[k][1], "desc": TIMBRE_WEIGHTS[k][2]}
                                for k, v in cmpd["subscores"].items()},
           "originality_verdict": org["verdict"],
           "technical": tech, "timbre": tim, "musical": mus, "originality": org,
           "technical_checks": tech_checks(C)}
    return out


AUD_THR = {"chroma_fail": 0.40, "chroma_warn": 0.32, "fp_fail": 0.02}
AUD_RULE = ("audio FAIL if the transposition/tempo-invariant chroma-sequence similarity >= 0.40 or the fingerprint match "
            ">= 0.02; WARN at chroma >= 0.32. Null (40 random C-minor waltzes through the same chain): chroma max 0.31 over "
            "the original's own i/vii harmony, 0.20 over other harmony; fingerprint max 0.005. The original's composition "
            "re-synthesised with FluidR3 scores 0.50; re-encoded/pitch/tempo-shifted copies 0.88-1.0 and fingerprint >= 0.048")


def tech_checks(C):
    L = C["loud"]
    chk = {
        "starts_at_0": C["first_sound_s"] <= 0.05,
        "ends_by_13_75": C["last_sound_s"] <= 13.75 + 0.005,
        "no_tail_after_13_8": C["tail_end_s"] <= 13.80,
        "lufs_-29.5_pm0.5": (L.get("I") is not None and abs(L["I"] + 29.5) <= 0.5),
        "true_peak_le_-17": (L.get("TP") is not None and L["TP"] <= -17.0),
        "no_clipping": C["clip_samples"] == 0,
        "no_clicks": C["clicks"]["count"] == 0,
        "dc_lt_-60dbfs": max(C["dc_dbfs"]) < -60,
    }
    chk["all_ok"] = all(chk.values())
    return chk


# -------------------------------------------------------------------------------------------------------- PNG
def plot(path_png, R, C, cmpd, title):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import librosa.display  # noqa: F401
    BLUE, ORANGE, INK, MUTED = "#2a78d6", "#eb6834", "#222222", "#777777"
    fig = plt.figure(figsize=(16, 17), dpi=80)
    gs = fig.add_gridspec(5, 2, height_ratios=[1.25, 1.25, 1.0, 0.8, 0.8], hspace=0.42, wspace=0.18)
    vmin, vmax = -95, -25
    t_ax = np.arange(R["cqt_db"].shape[1]) * 256 / 22050
    fmin = 65.406
    for row, (F, lab) in enumerate(((R, "ORIGINAL"), (C, "CANDIDATE"))):
        ax = fig.add_subplot(gs[row, :])
        Z = F["cqt_db"]
        tt = np.arange(Z.shape[1]) * 256 / 22050
        ax.imshow(Z, origin="lower", aspect="auto", cmap="magma", vmin=vmin, vmax=vmax,
                  extent=[tt[0], tt[-1], 0, Z.shape[0]])
        yt = [24 * k for k in range(8)]
        ax.set_yticks(yt)
        ax.set_yticklabels([f"C{k + 2}\n{fmin * 2 ** k:.0f}" for k in range(8)], fontsize=8)
        ax.set_xlim(0, 13.8)
        ax.set_xticks(np.arange(0, 14.01, 1.0))
        g = F.get("cqt_gain_db", 0)
        ax.set_title(f"{lab}: CQT 24 bins/oct, loudness-matched to -29.5 LUFS (applied {g:+.1f} dB), colour {vmin}..{vmax} dB"
                     + (f"   |  {title}" if row == 1 else ""), fontsize=10, loc="left", color=INK)
        for x in (F["first_sound_s"], F["last_sound_s"]):
            ax.axvline(x, color="white", lw=0.8, ls=":")
    # LTAS + noise floor
    ax = fig.add_subplot(gs[2, 0])
    fc = np.array(R["ltas"]["fc"])
    ax.semilogx(fc, R["ltas"]["rel_db"], color=BLUE, lw=2, label="original")
    ax.semilogx(fc, C["ltas"]["rel_db"], color=ORANGE, lw=2, label="candidate")
    ax.set_ylim(-60, 5)
    ax.set_xlim(50, 16000)
    ax.axvspan(250, 4000, color="#000000", alpha=0.04)
    ax.set_title(f"1/3-oct long-term spectrum, dB re 250-4k total  (dist {cmpd['ltas_db']:.1f} dB RMS)", fontsize=10, loc="left")
    ax.set_xlabel("Hz"); ax.grid(alpha=0.25, which="both"); ax.legend(fontsize=9, frameon=False)
    # noise floor + modulation
    ax = fig.add_subplot(gs[2, 1])
    e = np.array(R["mod"]["edges_hz"]); ce = np.sqrt(e[1:] * e[:-1])
    ax.semilogx(ce, np.mean(R["mod"]["spec_db"], 0), color=BLUE, lw=2, label="original")
    ax.semilogx(ce, np.mean(C["mod"]["spec_db"], 0), color=ORANGE, lw=2, label="candidate")
    ax.set_title(f"modulation spectrum of band envelopes (mean of 4 bands), r={cmpd['modulation_r']:.2f}, "
                 f"depth {cmpd['modulation_depth_db']:+.1f} dB", fontsize=10, loc="left")
    ax.set_xlabel("modulation Hz"); ax.set_ylabel("dB"); ax.grid(alpha=0.25, which="both"); ax.legend(fontsize=9, frameon=False)
    # level envelope
    ax = fig.add_subplot(gs[3, :])
    for F, col, lab in ((R, BLUE, "original"), (C, ORANGE, "candidate")):
        I = F["loud"].get("I") or -29.5
        r = np.array(F["level"]["rms100_curve"]) + (-29.5 - I)
        tt = F["first_sound_s"] + np.arange(len(r)) * 0.1
        ax.step(tt, r, where="post", color=col, lw=1.6, label=f"{lab} (LUFS {I:.1f}, shown at -29.5)")
    ax.set_xlim(0, 13.8); ax.set_xticks(np.arange(0, 14.01, 1.0))
    ax.set_title("level: 100 ms RMS of mid, dBFS after loudness matching", fontsize=10, loc="left")
    ax.grid(alpha=0.25); ax.legend(fontsize=9, frameon=False, loc="lower center", ncol=2)
    # noise floor
    ax = fig.add_subplot(gs[4, 0])
    ax.semilogx(R["noise"]["fc"], R["noise"]["floor_rel_band_db"], color=BLUE, lw=2, marker="o", ms=5, label="original")
    ax.semilogx(C["noise"]["fc"], C["noise"]["floor_rel_band_db"], color=ORANGE, lw=2, marker="o", ms=5, label="candidate")
    ax.set_title("inter-harmonic floor: p10 bin power re band mean, dB", fontsize=10, loc="left")
    ax.grid(alpha=0.25, which="both"); ax.legend(fontsize=9, frameon=False); ax.set_xlabel("Hz")
    # pitch drift
    ax = fig.add_subplot(gs[4, 1])
    for F, col, lab in ((R, BLUE, "original"), (C, ORANGE, "candidate")):
        p = F["pitch"] or {}
        if p.get("drift_curve_t"):
            v = np.array([np.nan if x is None else x for x in p["drift_curve_c"]], dtype=float)
            ax.plot(p["drift_curve_t"], v, color=col, lw=1.4,
                    label=f"{lab} (band std {p.get('pitch_dev_band_std_c', 0):.1f} c, coherence r {p.get('pitch_dev_coherence_r') or 0:.2f}, "
                          f"vib {p.get('vibrato_rms_c', 0):.1f} c)")
    ax.set_xlim(0, 13.8); ax.set_ylim(-60, 80)
    ax.set_title("pitch deviation from 12-TET, mean of 3 register bands (offset removed), cents", fontsize=10, loc="left")
    ax.grid(alpha=0.25); ax.legend(fontsize=8, frameon=True, framealpha=0.9, loc="upper left", ncol=1)
    fig.suptitle(f"olcum.py  TIMBRE_SCORE {cmpd['TIMBRE_SCORE']:.1f}/100   ({os.path.basename(title)})", fontsize=13, x=0.01,
                 ha="left", color=INK)
    fig.savefig(path_png, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("aday", help="candidate audio file (any format ffmpeg reads)")
    ap.add_argument("--notalar", help='melody JSON {"tempo_bpm":..,"notes":[{"bar","beat","dur_beats","midi"}],"chords":[..]}')
    ap.add_argument("--tonic", type=int, default=0, help="tonic pitch class of the candidate (0 = C)")
    ap.add_argument("--png", help="write the comparison PNG here")
    ap.add_argument("--ref", default=REF_WAV, help="reference (default: the original's WAV copy)")
    ap.add_argument("--yenile", action="store_true", help="recompute the cached reference features")
    ap.add_argument("--ozet", action="store_true", help="print a compact summary instead of the full JSON")
    a = ap.parse_args()
    t0 = time.time()
    R = ref_features(a.ref, a.yenile)
    C = features(a.aday)
    cmpd = compare(R, C)
    sym = chords = None
    if a.notalar:
        mj = json.load(open(a.notalar))
        notes = mj.get("notes", mj.get("melody")) if isinstance(mj, dict) else mj
        ref_notes, ref_json = load_ref_melody()
        sym = symbolic(norm_notes(notes), norm_notes(ref_notes), a.tonic)
        if isinstance(mj, dict) and mj.get("chords"):
            chords = chord_check(mj["chords"], ref_json)
    out = report(a.aday, R, C, cmpd, sym, chords)
    if a.png:
        plot(a.png, R, C, cmpd, a.aday)
        out["png"] = os.path.abspath(a.png)
    out["elapsed_s"] = round(time.time() - t0, 1)
    if a.ozet:
        print(json.dumps(summary(out), ensure_ascii=False, indent=1, default=_js))
    else:
        print(json.dumps(out, ensure_ascii=False, indent=1, default=_js))


def _js(o):
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return None if not np.isfinite(o) else float(o)
    if isinstance(o, (np.ndarray,)):
        return o.tolist()
    if isinstance(o, (set, frozenset, tuple)):
        return list(o)
    return str(o)


def summary(o):
    t, ti, mu, og = o["technical"], o["timbre"], o["musical"], o["originality"]
    return {"file": os.path.basename(o["file"]), "TIMBRE_SCORE": o["TIMBRE_SCORE"],
            "sub": {k: v["score"] for k, v in o["timbre_subscores"].items()},
            "LUFS": t["lufs_integrated"]["value"], "TP": t["true_peak_dbtp"]["value"], "first": t["first_sound_s"]["value"],
            "last": t["last_sound_s"]["value"], "clicks": t["clicks"]["value"], "tempo": mu["tempo_bpm"]["value"],
            "key": mu["key"]["value"], "onsets_bar": mu["onsets_per_bar"]["value"],
            "chroma": og["chroma_seq_sim"]["value"], "chroma_T": og["chroma_seq_sim_transposed"]["value"],
            "fp": og["fingerprint_match"]["value"], "verdict": o["originality_verdict"],
            "checks_ok": o["technical_checks"]["all_ok"], "elapsed_s": o.get("elapsed_s")}


if __name__ == "__main__":
    main()
