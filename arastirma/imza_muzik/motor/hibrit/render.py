#!/usr/bin/env python3
"""hibrit: hybrid sound engine for the signature waltz (musette accordion, small room, lo-fi medium).

    python3 render.py <melody.json> <out.wav> [--seed N] [--recipe NAME] [--set key=value ...] [--stems DIR]

Deterministic for a given (melody, seed, recipe). Self-contained: it needs numpy/scipy/soundfile, pyfluidsynth +
FluidR3_GM.sf2 (MIT) only for the FluidR3 layers, and the CC0 Hohner accordion samples in ./samples/hohner_cc0/.
The original recording is NOT used at render time. The only things taken from it are measured numbers (tempo-free
timbre statistics and a 1/3-octave long-term spectrum used as a smoothed match-EQ target, BAGLAM rule 1).

Signal flow (see log.md for why each stage exists and how it was tuned):
  score -> parts (lead, counter, oom bass, pah chords)
  -> per-note sources, layered: CC0 Hohner tremolo-accordion samples / FluidR3 P23+P22 / own wavetable reed model
  -> per-note envelope (soft attack, legato overlap, pah swell, oom), brightness follows bellows pressure
  -> mono dry mix -> synthetic decorrelated stereo room -> wow + flutter (variable delay) -> tape modulation noise
  -> band EQ (HPF 250, steep LPF) + fixed patch EQ + adaptive 1/3-oct LTAS match EQ toward the measured target
  -> hum + rumble -> -29.5 LUFS (BS.1770), no limiter -> fade so all sound ends by the clip length
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys

import numpy as np
import scipy.signal as ss
import soundfile as sf

SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))
SF2 = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
HN_DIR = os.path.join(HERE, "samples", "hohner_cc0")

# 1/3-octave long-term spectrum of the original's mid channel, dB re the 1.6 kHz band (analiz/tini.json eq_curve).
# Used ONLY as the target of a >= 1/3-octave smoothed match EQ (BAGLAM rule 1). Above 8 kHz it is codec SBR.
TARGET_LTAS = [(20.0, -31.3), (25.0, -34.5), (31.5, -37.6), (40.0, -38.2), (50.0, -38.1), (63.0, -39.3), (80.0, -40.4),
               (100.0, -30.4), (125.0, -32.0), (160.0, -31.2), (200.0, -32.2), (250.0, -19.7), (315.0, -11.6),
               (400.0, -9.3), (500.0, -6.6), (630.0, -1.3), (800.0, -6.8), (1000.0, -10.2), (1250.0, -7.9),
               (1600.0, 0.0), (2000.0, -1.6), (2500.0, -4.7), (3150.0, -12.5), (4000.0, -15.2), (5000.0, -25.7),
               (6300.0, -34.7), (8000.0, -37.0), (10000.0, -39.5), (12500.0, -45.4), (16000.0, -55.9),
               (20000.0, -61.5)]

# --------------------------------------------------------------------------------------------------- recipes
BASE = {
    # global
    "tuning_c": -21.0,          # original sits at A4 ~ 434.5 Hz
    "reed_mistune_c": 12.0,     # per-pitch fixed mistuning of an old instrument (std, cents)
    "humanize_ms": 6.0,         # onset jitter std
    "length_s": 13.75,          # clip length; all sound ends before it
    "fade_s": 0.04,             # end fade (the original is a hard cut at 13.735 s; brief: fade 13.45-13.75)
    "end_margin_s": 0.012,
    # parts: source layers [(source, gain_db, detune_c)], sources: hn | fs:<prog> | reed
    "lead_layers": [["hn", 0.0, 0.0]],
    "acc_layers": [["hn", 0.0, 0.0]],
    "bass_layers": [["hn", 0.0, 0.0]],
    "lead_db": -1.0,
    "counter_db": -6.0,
    "pah_db": 6.0,              # per chord (sum of its notes), re lead
    "oom_db": -1.0,
    "bass_oct_db": -5.0,        # stradella octave reed on the bass note (+12)
    # articulation
    "lead_attack_ms": 60,
    "lead_release_ms": 70.0,
    "legato_overlap_ms": 45.0,
    "pah_attack_ms": 40.0,
    "pah_decay_ms": 35,       # exp decay time constant after the swell peak
    "pah_floor_db": -18,      # sustained level after the swell (legato bed)
    "pah_hold_ms": 0.0,         # time at the swell peak before the decay
    "pah_release_ms": 70.0,
    "pah_len_beats": 0.97,      # chord sounds until (almost) the next beat
    "oom_attack_ms": 35.0,
    "oom_len_beats": 0.95,
    "oom_decay_ms": 220.0,
    "oom_floor_db": -6.0,
    "bright_lp_hz": 1100.0,     # dark version of a note = lowpassed copy; brightness follows the swell
    "pah_bright": 1.0,          # 1 = full brightness at swell peak
    "oom_bright": 0.35,
    "lead_bright": 0.85,
    "shelf_hz": 1200.0,         # per-part high shelf (instrument colour before the shared chain)
    "lead_shelf_db": 0.0,
    "pah_shelf_db": 0.0,
    "oom_shelf_db": 0.0,
    "oom_hp_hz": 0.0,           # steep high-pass on the bass part only (fundamentals gone before the room)
    # expression
    "expr": 1.0,                # scales automatic bends (scoop on leaps, climax glide, final-hold drift)
    "scoop_prob": 0.5,          # chance of a scoop into a note reached by a leap >= 3 semitones
    "scoop_c": 35.0,
    "scoop_ms": 90.0,
    # reed wavetable model
    "reed_voices": [[-15.0, 0.0], [0.0, 0.0], [17.0, -1.0]],
    "reed_tilt": 1.0,
    "reed_oe_db": 7.0,
    "reed_ripple_db": 2.5,
    "reed_noise_db": -26.0,
    "reed_fmax": 6500.0,
    # sampler
    "hn_skip_extra_ms": 0.0,    # extra skip into the sample (past any recorded valve/onset noise)
    "hn_skip_db": -4.0,         # start the sample where it reaches this level re its sustain
    # chain
    "room_wet_db": -9,
    "room_rt60": 0.04,
    "room_pd_ms": 7,
    "room_build_ms": 2,
    "room_tail_db": -45,
    "room_tail_rt": 1.5,
    "room_lp": 3000.0,
    "room_hp": 150.0,
    "wow_c": 19,               # slow quasi-periodic wow, cents (std)
    "wow_rate": 0.5,
    "wow_pre": 1,               # 1 = apply the slow pitch motion to the dry source (before the room)
    "wow_skew": 1.2,            # >0: upward excursions, flat-ish stretches
    "wow_rand_c": 4.4,          # random 0.8-5 Hz component (cents RMS)
    "flutter_c": 4.0,           # 3.5-9 Hz (cents RMS)
    "room_hold_ms": 8,
    "room_seed": 7,             # the room is a fixed property of the engine (>= 0: same IR for every render)
    "wander_c": 14.0,           # per-note slow pitch wander (cents std), lead/counter
    "wander_acc_c": 2,        # same for accompaniment notes
    "wander_knot_s": 0.18,
    "medium_db": -6.0,          # lossy-medium noise level re local smoothed spectrum (dB); <= -90 = off
    "medium_shape": [[100, 4], [250, 4], [400, 0], [3150, 0], [3600, -6], [4000, -30], [20000, -30]],
    "medium_tsmooth": 3,
    "medium_ms": 1,             # 1 = add the medium noise in mid/side (joint stereo) instead of L/R
    "sbr_hz": 5000.0,
    "sbr_db": -22,           # SBR-like HF regeneration level (dB re the copied band); <= -90 = off
    "flutter_per_c": 0,       # quasi-periodic flutter component (cents RMS) at flutter_rate
    "flutter_rate": 4.6,
    "dyn_pitch_db": 0.4,        # bellows: dB per semitone of the (smoothed) melody register re its median
    "dyn_arch_db": 3.0,         # bellows: phrase arch depth (dB)
    "dyn_smooth_s": 0.6,
    "dyn_wander_db": 0.0,
    "hyper_db": 3,
    "pulse_bright_db": 0.0,     # bellows waltz pulse: extra brightness (>1.2 kHz) on beats 2-3 re beat 1 (dB)
    "pulse_level_db": 0.0,      # bellows waltz pulse: level on beats 2-3 re beat 1 (dB)
    "pulse_decay_s": 0.12,            # two-bar hypermetric bellows accent (peak-to-peak dB)
    "dyn_bright": 0.5,          # extra dB on the >1.2 kHz band per dB of bellows gain
    "modnoise": 0.0,            # tape modulation noise: RMS of the AM noise (linear)
    "modnoise_band": [40.0, 1200.0],
    "hp_hz": 250.0,
    "hp_order": 4,
    "lp_hz": 4800.0,
    "lp_order": 10,
    "patch_eq": [],             # [(Hz, dB)] fixed EQ before the match
    "match": 1.0,               # strength of the adaptive LTAS match EQ (0 = off)
    "match_cap_db": 10.0,
    "match_passes": 3,
    "match_smooth": 0,
    "match_fmin": 125.0,
    "match_fmax": 12500,
    "hum": [[100.0, -70.4], [150.0, -78.3], [200.0, -83.5], [250.0, -83.5], [50.0, -87.3]],
    "rumble_db": -56.0,
    "lf_noise_db": -69,      # diffuse 30-260 Hz floor (sine-referenced RMS dBFS); <= -120 = off
    "lufs": -29.5,
    "peak_ceiling_dbtp": -17.0,  # rare-peak ceiling (None = off)
    "peak_mode": "shave",       # shave = look-ahead gain dip; soft = soft-knee waveshaper on the tops only
    "peak_look_ms": 1.5,
    "peak_rel_ms": 8.0,
    "calibrate_sources": 1,
}

RECIPES = {
    # recipe A: FluidR3 samples (tango accordion musette + detuned harmonica) for the lead, P23 accompaniment
    "A_fluid": {
        "lead_layers": [["fs:23", 0.0, 0.0], ["fs:22", -2.0, 14.0]],
        "acc_layers": [["fs:23", 0.0, 0.0]],
        "bass_layers": [["fs:23", 0.0, 0.0]],
        "pah_db": 3.0, "lead_db": -4.0, "medium_db": -3.0,     # balance re-tuned for these layers (log.md i13)
    },
    # recipe B: CC0 Hohner tremolo-accordion samples + own reed model as a density layer
    "B_hohner": {
        "lead_layers": [["hn", 0.0, 0.0], ["reed", -8.0, 0.0]],
        "acc_layers": [["hn", 0.0, 0.0], ["reed", -10.0, 0.0]],
        "bass_layers": [["hn", 0.0, 0.0]],
    },
    # recipe C: own reed model only (pure synthesis baseline)
    "C_reed": {
        "lead_layers": [["reed", 0.0, 0.0]],
        "acc_layers": [["reed", 0.0, 0.0]],
        "bass_layers": [["reed", 0.0, 0.0]],
    },
}
DEFAULT_RECIPE = "B_hohner"


CHAIN_PREFIXES = ("room_", "wow_", "flutter", "modnoise", "hp_", "lp_", "patch_eq", "match", "hum", "rumble", "lufs",
                  "medium", "sbr", "fade_s", "end_margin")


def make_params(recipe, sets):
    P = json.loads(json.dumps(BASE))
    P.update(json.loads(json.dumps(RECIPES[recipe])))
    for s in sets or []:
        k, v = s.split("=", 1)
        if k not in P:
            raise SystemExit(f"unknown parameter {k}")
        try:
            P[k] = json.loads(v)
        except json.JSONDecodeError:
            P[k] = v
    return P


# ------------------------------------------------------------------------------------------------- dsp utils
def db2a(d):
    return 10.0 ** (np.asarray(d) / 20.0)


def hermite(x, pos):
    """4-point cubic Hermite interpolation of x at fractional positions pos (clamped)."""
    i = np.floor(pos).astype(np.int64)
    f = pos - i
    i = np.clip(i, 1, len(x) - 3)
    xm1, x0, x1, x2 = x[i - 1], x[i], x[i + 1], x[i + 2]
    c1 = 0.5 * (x1 - xm1)
    c2 = xm1 - 2.5 * x0 + 2.0 * x1 - 0.5 * x2
    c3 = 0.5 * (x2 - xm1) + 1.5 * (x0 - x1)
    return ((c3 * f + c2) * f + c1) * f + x0


def bandnoise(n, lo, hi, rng, fs=SR):
    """unit-RMS band-limited gaussian noise (computed at a low rate when the band is low)."""
    if hi < 60:
        dec = 100
        m = n // dec + 8
        w = rng.standard_normal(m)
        sos = ss.butter(2, [lo, hi], "bandpass", fs=fs / dec, output="sos")
        w = ss.sosfiltfilt(sos, w)
        w = np.interp(np.arange(n) / dec, np.arange(m), w)
    else:
        w = rng.standard_normal(n)
        sos = ss.butter(2, [lo, min(hi, fs / 2 * 0.95)], "bandpass", fs=fs, output="sos")
        w = ss.sosfiltfilt(sos, w)
    return w / (np.std(w) + 1e-12)


def raised(n):
    return 0.5 - 0.5 * np.cos(np.pi * np.arange(n) / max(n, 1))


def shelf(x, fc, gain_db):
    """2nd-order high shelf (RBJ), gain_db above fc."""
    A = 10 ** (gain_db / 40)
    w0 = 2 * np.pi * fc / SR
    al = np.sin(w0) / (2 * 0.7071)
    cw = np.cos(w0)
    b = [A * ((A + 1) + (A - 1) * cw + 2 * np.sqrt(A) * al), -2 * A * ((A - 1) + (A + 1) * cw),
         A * ((A + 1) + (A - 1) * cw - 2 * np.sqrt(A) * al)]
    a = [(A + 1) - (A - 1) * cw + 2 * np.sqrt(A) * al, 2 * ((A - 1) - (A + 1) * cw),
         (A + 1) - (A - 1) * cw - 2 * np.sqrt(A) * al]
    return ss.lfilter(np.array(b) / a[0], np.array(a) / a[0], x)


def slow_noise(n, knot_s, rng):
    """smooth random curve, unit std at the knots, cosine-interpolated between knots every knot_s seconds."""
    k = int(n / (knot_s * SR)) + 3
    v = rng.standard_normal(k)
    x = np.arange(n) / (knot_s * SR)
    i = np.floor(x).astype(int)
    f = x - i
    w = 0.5 - 0.5 * np.cos(np.pi * f)
    return v[i] * (1 - w) + v[i + 1] * w


def smooth_logf(A, f, frac=1 / 3):
    """average |X|^2 over a +-frac/2-octave window around each bin (A: bins x frames)."""
    c = np.vstack([np.zeros((1, A.shape[1])), np.cumsum(A, axis=0)])
    lo = np.searchsorted(f, f * 2 ** (-frac / 2))
    hi = np.searchsorted(f, f * 2 ** (frac / 2), side="right")
    hi = np.maximum(hi, lo + 1)
    return (c[hi] - c[lo]) / (hi - lo)[:, None]


# ------------------------------------------------------------------------------------------------- score
def load_score(path):
    J = json.load(open(path))
    bpm = float(J.get("tempo_bpm", 152))
    beat_s = 60.0 / bpm
    p = float(J.get("pickup_beats", 0) or 0)
    notes = [dict(n) for n in J.get("notes", [])]
    counter = [dict(n) for n in (J.get("counter") or [])]
    chords = [dict(c) for c in J.get("chords", [])]
    acc = J.get("accomp") or {}
    if isinstance(acc, str):
        acc = {"pattern": acc}

    def ab(e):
        return (float(e["bar"]) - 1) * 3 + (float(e.get("beat", 1)) - 1)

    allev = notes + counter + chords
    has_bar0 = any(float(e["bar"]) < 1 for e in allev)
    fill_pickup = 0.0
    if has_bar0:
        origin = -p if p > 0 else min(ab(e) for e in allev)
    elif p > 0:
        bar1 = [e for e in allev if int(e["bar"]) == 1]
        if bar1 and all(float(e.get("beat", 1)) >= 3 - p + 1 - 1e-6 for e in bar1):
            origin = 3 - p                       # bar 1 is the (partial) pickup bar
        else:
            origin = -p                          # bar 1 is the first full bar: fill the pickup with pa-pa
            fill_pickup = p
    else:
        origin = 0.0
    return {"bpm": bpm, "beat_s": beat_s, "origin_ab": origin, "notes": notes, "counter": counter, "chords": chords,
            "accomp": acc, "fill_pickup": fill_pickup, "ab": ab, "id": J.get("id", os.path.basename(path))}


def tsec(S, ab):
    return (ab - S["origin_ab"]) * S["beat_s"]


def parse_pattern(acc):
    """accomp pattern -> per-beat token list + modifiers.
    Tokens per beat (space separated): B = bass (lowest written chord tone or chord 'bass'), F = chord fifth (or 2nd
    chord tone above the bass), A = alternating bass (B on odd bars, F on even bars), C = chord, c = soft chord,
    BC = bass+chord, '-' = hold previous, '.' = rest. Free text (e.g. 'waltz: root on beat 1, chord on beats 2-3')
    gives the default waltz 'B C C'. Modifiers anywhere in the text: legato/sustained, staccato/short, no-bass."""
    txt = (acc.get("pattern") or "").strip()
    low = txt.lower()
    mods = {"legato": any(w in low for w in ("legato", "sustain")), "staccato": any(w in low for w in ("staccato", "short", "detached")),
            "nobass": "no-bass" in low or "no bass" in low}
    toks = None
    m = re.fullmatch(r"\s*([BFACc\-\.]+(?:\s+[BFACc\-\.]+){2})\s*(.*)", txt)
    if m:
        toks = m.group(1).split()
    if toks is None:
        if "arp" in low:
            toks = ["B", "C1", "C2"]
        elif "alt" in low and "bass" in low:
            toks = ["A", "C", "C"]
        else:
            toks = ["B", "C", "C"]
    return toks, mods


def voice_chord(pcs, prev, lo=57, hi=74, center=65.0):
    """close-position voicing of the pitch classes inside [lo, hi], nearest to the previous voicing."""
    pcs = sorted(set(int(p) % 12 for p in pcs))
    cands = []
    for root_oct in range(lo, hi + 1):
        if root_oct % 12 not in pcs:
            continue
        v = [root_oct]
        for _ in range(len(pcs) - 1):
            nxt = v[-1] + 1
            while nxt % 12 not in pcs or nxt % 12 in [x % 12 for x in v]:
                nxt += 1
            v.append(nxt)
        if v[-1] <= hi:
            cands.append(v)
    if not cands:
        base = sorted(lo + ((p - lo) % 12) for p in pcs)
        return base
    if prev:
        def cost(v):
            return sum(min(abs(a - b) for b in prev) for a in v) + 0.15 * abs(np.mean(v) - center)
    else:
        def cost(v):
            return abs(np.mean(v) - center) + 0.5 * abs(v[0] - 60)
    return min(cands, key=cost)


def build_parts(S, P, rng):
    """returns list of note events: dict(part, t, dur, midi, vel, kind, bend)"""
    ev = []
    bs = S["beat_s"]
    hum = P["humanize_ms"] / 1000.0

    def jit():
        return float(np.clip(rng.normal(0, hum), -2.5 * hum, 2.5 * hum)) if hum > 0 else 0.0

    # ---- lead + counter (legato)
    for part, lst, gdb in (("lead", S["notes"], P["lead_db"]), ("counter", S["counter"], P["counter_db"])):
        L = sorted(lst, key=lambda n: S["ab"](n))
        for i, n in enumerate(L):
            t0 = tsec(S, S["ab"](n))
            dur = float(n.get("dur_beats", 1)) * bs
            ev.append({"part": part, "t": max(0.0, t0 + jit()), "dur": dur, "midi": int(n["midi"]),
                       "vel": float(n.get("vel", 90)), "gdb": gdb, "bend": n.get("bend"), "i": i})
    # ---- accompaniment from chords
    toks, mods = parse_pattern(S["accomp"])
    chords = sorted(S["chords"], key=lambda c: S["ab"](c))
    prev_voicing = None
    acc_events = []
    pickup_chord = chords[0] if (chords and S["fill_pickup"] > 0) else None
    spans = []
    if pickup_chord is not None:
        a0 = S["ab"](pickup_chord) - S["fill_pickup"]
        spans.append((a0, S["fill_pickup"], pickup_chord, True))
    for c in chords:
        spans.append((S["ab"](c), float(c.get("dur_beats", 3)), c, False))
    for a0, du, c, is_pick in spans:
        pcs = [int(m) for m in c["midi"]]
        bass = int(c.get("bass", min(pcs)))
        voicing = voice_chord(pcs, prev_voicing)
        prev_voicing = voicing
        sorted_pcs = sorted(pcs)
        fifth = sorted_pcs[2] if len(sorted_pcs) >= 3 else sorted_pcs[-1]
        nb = int(round(du))
        for k in range(max(nb, 1)):
            ab_k = a0 + k
            pos = int(round(ab_k)) % 3            # 0 = beat 1
            bar_no = int(math.floor(ab_k / 3)) + 1
            tok = toks[pos]
            if is_pick and "B" in tok:
                tok = "C"                         # the pickup is the pa-pa of the first chord
            t0 = tsec(S, ab_k)
            if t0 < -1e-6:
                continue
            t = max(0.0, t0 + jit())
            if any(ch in tok for ch in "BFA") and not mods["nobass"]:
                use_fifth = ("F" in tok) or ("A" in tok and bar_no % 2 == 0)
                bp = (fifth if use_fifth else bass) % 12
                bm = 45 + ((bp - 45) % 12)        # bass register A2..Ab3 (fundamental removed by the 250 Hz HPF)
                acc_events.append({"part": "oom", "t": t, "dur": P["oom_len_beats"] * bs, "midi": bm, "vel": 90.0,
                                   "gdb": P["oom_db"]})
                acc_events.append({"part": "oom", "t": t, "dur": P["oom_len_beats"] * bs, "midi": bm + 12, "vel": 90.0,
                                   "gdb": P["oom_db"] + P["bass_oct_db"]})
            if "C" in tok or "c" in tok:
                soft = "c" in tok
                per = P["pah_db"] - 10 * math.log10(max(len(voicing), 1)) - (4.0 if soft else 0.0)
                tones = voicing
                if tok.startswith("C") and tok[1:].isdigit():  # arpeggio: one chord tone per beat
                    tones = [voicing[int(tok[1:]) % len(voicing)]]
                ln = P["pah_len_beats"] * bs
                if mods["legato"]:
                    ln = 1.02 * bs
                if mods["staccato"]:
                    ln = 0.45 * bs
                for m_ in tones:
                    acc_events.append({"part": "pah", "t": t, "dur": ln, "midi": int(m_), "vel": 90.0, "gdb": per,
                                       "legato": mods["legato"], "stacc": mods["staccato"]})
    ev.extend(acc_events)
    return ev


# --------------------------------------------------------------------------------------------- sources
class HohnerSampler:
    """CC0 FreePats 'Button Accordion HN' (Hohner, tremolo reeds) played from its SFZ mapping, own envelopes."""

    def __init__(self, P):
        sfz = open(os.path.join(HN_DIR, "PRESET Button Accordion HN tuned.sfz")).read()
        sustain = sfz.split("trigger=release")[0]
        regs = re.findall(r"sample=(Button Accordion HN [^ ]+\.wav) pitch_keycenter=(\d+) lokey=(\d+) hikey=(\d+) "
                          r"tune=(-?\d+)\s+loop_start=(\d+) loop_end=(\d+)", sustain)
        self.R = []
        for name, kc, lo, hi, tune, ls, le in regs:
            x, sr = sf.read(os.path.join(HN_DIR, name))
            assert sr == SR
            x = x.mean(1) if x.ndim > 1 else x
            ls, le = int(ls), int(le)
            # loop RMS normalisation (equal sustain level per sample)
            rms = np.sqrt(np.mean(x[ls:le] ** 2))
            x = x / (rms + 1e-12) * 0.1
            # start offset: where the envelope first reaches hn_skip_db re sustain
            env = np.sqrt(np.convolve(x ** 2, np.ones(441) / 441, "same"))
            thr = 0.1 * db2a(P["hn_skip_db"])
            st = int(np.argmax(env > thr))
            st = max(0, st - 220 + int(P["hn_skip_extra_ms"] / 1000 * SR))
            # crossfaded loop, extended to ~12 s
            L = x[ls:le].copy()
            xf = min(2048, len(L) // 4, ls)
            w = np.linspace(0, 1, xf)
            L[-xf:] = L[-xf:] * (1 - w) + x[ls - xf:ls] * w
            reps = int(np.ceil(12.0 * SR / len(L))) + 1
            ext = np.concatenate([x[:ls], np.tile(L, reps)])
            self.R.append({"name": name, "kc": int(kc), "tune": float(tune), "x": ext, "start": st})
        self.R.sort(key=lambda r: r["kc"])

    def note(self, midi, dur, cents, rng):
        kcs = np.array([r["kc"] for r in self.R])
        d = np.abs(kcs - midi) + 0.01 * (kcs > midi)      # tie: prefer shifting up from a lower sample
        r = self.R[int(np.argmin(d))]
        ratio = 2.0 ** ((midi - r["kc"]) / 12.0 + (r["tune"] + cents) / 1200.0)
        n = int(dur * SR)
        pos = r["start"] + rng.integers(0, 60) + ratio * np.arange(n)
        pos = np.minimum(pos, len(r["x"]) - 4)
        return hermite(r["x"], pos)


class FluidSource:
    """FluidR3_GM (MIT) program, one note at a time (so every note gets our own envelope)."""

    def __init__(self, prog):
        import fluidsynth
        self.fs = fluidsynth.Synth(gain=0.6, samplerate=float(SR), **{"synth.reverb.active": 0,
                                                                     "synth.chorus.active": 0,
                                                                     "synth.polyphony": 64})
        self.sfid = self.fs.sfload(SF2)
        self.fs.program_select(0, self.sfid, 0, prog)
        for cc, v in ((7, 127), (11, 127), (91, 0), (93, 0)):
            self.fs.cc(0, cc, v)

    def note(self, midi, dur, cents, rng):
        semi = int(round(cents / 100.0))
        c = cents - 100 * semi
        m = int(np.clip(midi + semi, 0, 127))
        self.fs.pitch_bend(0, int(np.clip(round(c / 200.0 * 8192), -8192, 8191)))
        n = int(dur * SR)
        self.fs.noteon(0, m, 100)
        a = np.array(self.fs.get_samples(n), dtype=np.float64).reshape(-1, 2).mean(1)
        self.fs.noteoff(0, m)
        _ = self.fs.get_samples(int(0.6 * SR))           # flush the release
        return a / 32768.0 * 6.0


class ReedModel:
    """own spectral model of a free reed: wavetable per reed voice (odd-heavy source, random spectral ripple),
    2-3 detuned voices (musette), slow per-voice drift, pitch-synchronous reed (air) noise."""

    def __init__(self, P):
        self.P = P
        self.N = 4096

    def table(self, f0, rng):
        P = self.P
        K = max(1, int(P["reed_fmax"] / f0))
        k = np.arange(1, K + 1)
        amp = k ** (-P["reed_tilt"]) * np.where(k % 2 == 1, 1.0, db2a(-P["reed_oe_db"]))
        amp = amp * db2a(rng.normal(0, P["reed_ripple_db"], K))
        ph = rng.uniform(0, 2 * np.pi, K)
        spec = np.zeros(self.N // 2 + 1, complex)
        spec[1:K + 1] = amp * np.exp(1j * ph)
        tab = np.fft.irfft(spec, self.N) * self.N / 2
        return tab / (np.sqrt(np.mean(tab ** 2)) + 1e-12)

    def note(self, midi, dur, cents, rng):
        P = self.P
        n = int(dur * SR)
        f0 = 440.0 * 2 ** ((midi - 69) / 12 + cents / 1200)
        t = np.arange(n) / SR
        out = np.zeros(n)
        for det, g in P["reed_voices"]:
            fv = f0 * 2 ** ((det + rng.normal(0, 2.0)) / 1200)
            drift = 1.5 * bandnoise(n, 0.3, 3.0, rng)          # cents, slow
            ph = np.cumsum(fv * 2 ** (drift / 1200) / SR) + rng.uniform()
            ta, tb = self.table(fv, rng), self.table(fv, rng)
            xa = np.interp((ph % 1.0) * self.N, np.arange(self.N + 1), np.r_[ta, ta[0]])
            xb = np.interp((ph % 1.0) * self.N, np.arange(self.N + 1), np.r_[tb, tb[0]])
            mix = 0.5 + 0.5 * np.sin(2 * np.pi * rng.uniform(0.2, 0.7) * t + rng.uniform(0, 6.28))
            v = xa * mix + xb * (1 - mix)
            if P["reed_noise_db"] > -90:
                pulse = np.maximum(0.0, np.cos(2 * np.pi * ph)) ** 3
                nz = rng.standard_normal(n) * pulse
                nz = ss.sosfilt(ss.butter(2, [400, 6000], "bandpass", fs=SR, output="sos"), nz)
                v = v + db2a(P["reed_noise_db"]) * nz / (np.std(nz) + 1e-12)
            out += db2a(g) * v
        return out * 0.1 / math.sqrt(len(P["reed_voices"]))


class _Scaled:
    def __init__(self, src, g):
        self.src, self.g = src, g

    def note(self, *a):
        return self.src.note(*a) * self.g


class Sources:
    """source registry. Every source is calibrated so that a sustained note has the same RMS (0.1) in the middle of
    its range: layer gains in the recipes are then dB re a common reference."""

    def __init__(self, P):
        self.P = P
        self.cache = {}
        self.cal = {}

    def calib(self, name):
        if name not in self.cal:
            src = self.get_raw(name)
            r = []
            for m in (60, 67, 72):
                x = src.note(m, 0.9, 0.0, np.random.default_rng(0))
                r.append(np.sqrt(np.mean(x[int(0.3 * SR):int(0.8 * SR)] ** 2)))
            self.cal[name] = 0.1 / (np.sqrt(np.mean(np.square(r))) + 1e-12)
            if name.startswith("fs:"):
                src.fs.system_reset() if hasattr(src.fs, "system_reset") else None
                src.fs.program_select(0, src.sfid, 0, int(name[3:]))
                for cc, v in ((7, 127), (11, 127), (91, 0), (93, 0)):
                    src.fs.cc(0, cc, v)
        return self.cal[name]

    def get(self, name):
        return _Scaled(self.get_raw(name), self.calib(name) if self.P.get("calibrate_sources", 1) else 1.0)

    def get_raw(self, name):
        if name not in self.cache:
            if name == "hn":
                self.cache[name] = HohnerSampler(self.P)
            elif name.startswith("fs:"):
                self.cache[name] = FluidSource(int(name[3:]))
            elif name == "reed":
                self.cache[name] = ReedModel(self.P)
            else:
                raise SystemExit(f"unknown source {name}")
        return self.cache[name]


# ------------------------------------------------------------------------------------------- note shaping
def lead_bends(ev, P, rng):
    """automatic, sparse expressive pitch (measured in the original: falling scoop ~ -77 c, rising glide ~ +69 c on
    the climax, held tonic drifting ~ +44 c). Returns dict index -> (kind, cents, ms)."""
    if P["expr"] <= 0:
        return {}
    lead = [e for e in ev if e["part"] == "lead"]
    if not lead:
        return {}
    out = {}
    longs = [e for e in lead if e["dur"] >= 1.4 * 0.39]
    if longs:
        top = max(longs, key=lambda e: (e["midi"], e["dur"]))
        out[id(top)] = ("glide", 55.0 * P["expr"], 170.0)
    last = max(lead, key=lambda e: e["t"])
    if last["dur"] >= 1.2:
        out[id(last)] = ("drift", 30.0 * P["expr"], last["dur"] * 1000 * 0.45)
    prev = None
    for e in sorted(lead, key=lambda e: e["t"]):
        if prev is not None and id(e) not in out and abs(e["midi"] - prev["midi"]) >= 3 and e["dur"] >= 0.35:
            if rng.uniform() < P["scoop_prob"]:
                out[id(e)] = ("scoop", -P["scoop_c"] * P["expr"] * np.sign(e["midi"] - prev["midi"]), P["scoop_ms"])
        prev = e
    return out


def pitch_curve(n, bend):
    """cents curve for one note: glide = start below and rise into the note, scoop = start at `cents` (signed) and
    return to pitch, drift = move to `cents` over the last `ms`."""
    c = np.zeros(n)
    if not bend:
        return c
    kind, cents, ms = bend
    k = min(int(ms / 1000 * SR), n)
    if k <= 1:
        return c
    if kind == "glide":
        c[:k] = -abs(cents) * (1 - raised(k))
    elif kind == "scoop":
        c[:k] = cents * (1 - raised(k))
    elif kind == "drift":
        c[n - k:] = cents * raised(k)
    return c


def shape(x, e, P, bs):
    """amplitude envelope (and brightness) per part. x: dry note at nominal pitch, len = dur+release."""
    n = len(x)
    part = e["part"]
    if part in ("lead", "counter"):
        a = int(P["lead_attack_ms"] / 1000 * SR)
        r = int(P["lead_release_ms"] / 1000 * SR)
        body = n - r
        env = np.ones(n)
        env[:a] = raised(a)
        env[body:] = 1 - raised(n - body)
        bright = np.full(n, P["lead_bright"])
    elif part == "pah":
        a = int(P["pah_attack_ms"] / 1000 * SR)
        r = int(P["pah_release_ms"] / 1000 * SR)
        body = n - r
        tt = np.arange(n) / SR
        fl = db2a(P["pah_floor_db"] - (6 if e.get("stacc") else 0) + (5 if e.get("legato") else 0))
        hold = P["pah_hold_ms"] / 1000
        dec = fl + (1 - fl) * np.exp(-np.maximum(tt - a / SR - hold, 0) / (P["pah_decay_ms"] / 1000))
        env = dec.copy()
        env[:a] = raised(a)
        env[body:] *= 1 - raised(n - body)
        bright = P["pah_bright"] * (dec - fl) / (1 - fl + 1e-9)
        bright[:a] = P["pah_bright"] * raised(a)
    else:  # oom
        a = int(P["oom_attack_ms"] / 1000 * SR)
        r = int(0.08 * SR)
        body = n - r
        tt = np.arange(n) / SR
        fl = db2a(P["oom_floor_db"])
        dec = fl + (1 - fl) * np.exp(-np.maximum(tt - a / SR, 0) / (P["oom_decay_ms"] / 1000))
        env = dec.copy()
        env[:a] = raised(a)
        env[body:] *= 1 - raised(n - body)
        bright = np.full(n, P["oom_bright"])
    if np.any(bright < 0.999):
        dark = ss.sosfilt(ss.butter(2, P["bright_lp_hz"], "lowpass", fs=SR, output="sos"), x)
        x = dark + (x - dark) * np.clip(bright, 0, 1)
    return x * env


def render_parts(ev, P, seed, stems=None):
    rng = np.random.default_rng(seed)
    src = Sources(P)
    bs = 60 / 152
    total = int((P["length_s"] + 1.0) * SR)
    out = {k: np.zeros(total) for k in ("lead", "counter", "pah", "oom")}
    mist = rng.normal(0, P["reed_mistune_c"], 128)        # fixed per-pitch mistuning
    bends = lead_bends(ev, P, rng)
    # legato: extend each lead/counter note to the next onset + overlap
    for part in ("lead", "counter"):
        L = sorted([e for e in ev if e["part"] == part], key=lambda e: e["t"])
        for a, b in zip(L, L[1:]):
            gap = b["t"] - (a["t"] + a["dur"])
            if gap < 0.25:
                a["dur"] = max(a["dur"], b["t"] - a["t"]) + P["legato_overlap_ms"] / 1000
    layers_of = {"lead": P["lead_layers"], "counter": P["lead_layers"], "pah": P["acc_layers"], "oom": P["bass_layers"]}
    for e in ev:
        rel = (P["lead_release_ms"] if e["part"] in ("lead", "counter") else P["pah_release_ms"]) / 1000
        dur = e["dur"] + rel
        n = int(dur * SR)
        i0 = int(round(e["t"] * SR))
        if i0 >= total:
            continue
        n = min(n, total - i0)
        if n <= 16:
            continue
        bend = bends.get(id(e))
        if e.get("bend"):
            b = e["bend"]
            bend = (b.get("kind", "scoop"), float(b.get("cents", -40)), float(b.get("ms", 120)))
        pc = pitch_curve(n, bend)
        wc = P["wander_c"] if e["part"] in ("lead", "counter") else P["wander_acc_c"]
        if wc > 0:
            pc = pc + wc * slow_noise(n, P["wander_knot_s"], rng)
        acc = np.zeros(n)
        for lay in layers_of[e["part"]]:
            name, gdb, det = lay[0], lay[1], lay[2]
            tr = int(lay[3]) if len(lay) > 3 else 0
            midi = e["midi"] + tr
            cents = P["tuning_c"] + mist[midi % 128] + det
            # render a bit longer than needed (pitch curve may read ahead)
            raw = src.get(name).note(midi, dur * 1.1 + 0.05, cents, rng)
            if np.any(pc != 0):
                pos = np.cumsum(2 ** (pc / 1200))
                pos -= pos[0]
                y = np.interp(pos, np.arange(len(raw)), raw)
            else:
                y = raw[:n]
            if len(y) < n:
                y = np.pad(y, (0, n - len(y)))
            acc += db2a(gdb) * y[:n]
        acc = shape(acc, e, P, bs)
        g = db2a(e["gdb"]) * (e["vel"] / 90.0) ** 1.2
        out[e["part"]][i0:i0 + n] += g * acc
    if P["oom_hp_hz"] > 0 and np.any(out["oom"]):
        out["oom"] = ss.sosfilt(ss.butter(8, P["oom_hp_hz"], "highpass", fs=SR, output="sos"), out["oom"])
    for k, key in (("lead", "lead_shelf_db"), ("counter", "lead_shelf_db"), ("pah", "pah_shelf_db"), ("oom", "oom_shelf_db")):
        if P[key] != 0 and np.any(out[k]):
            out[k] = shelf(out[k], P["shelf_hz"], P[key])
    if stems:
        os.makedirs(stems, exist_ok=True)
        for k, v in out.items():
            sf.write(os.path.join(stems, f"{k}.wav"), v[: int(P["length_s"] * SR)], SR, subtype="FLOAT")
    dry = sum(out.values())
    return bellows(dry, ev, P, rng)


S_GRID = {}


def bellows(y, ev, P, rng):
    """one bellows drives every reed: a smooth phrase-level gain (arch + follows the melody register + slow random
    pressure wander); higher pressure = brighter reeds (the upper band gets an extra share of the gain)."""
    n = len(y)
    t = np.arange(n) / SR
    lead = sorted([e for e in ev if e["part"] == "lead"], key=lambda e: e["t"])
    d = np.zeros(n)
    if lead and (P["dyn_pitch_db"] != 0 or P["dyn_arch_db"] != 0):
        pitch = np.full(n, np.nan)
        for e in lead:
            i0, i1 = int(e["t"] * SR), int((e["t"] + e["dur"]) * SR)
            pitch[i0:i1] = e["midi"]
        ok = np.isfinite(pitch)
        if ok.any():
            pitch = np.interp(np.arange(n), np.flatnonzero(ok), pitch[ok])
            w = int(P["dyn_smooth_s"] * SR / 50)
            p50 = pitch[::50]
            p50 = np.convolve(np.pad(p50, w, mode="edge"), np.hanning(2 * w + 1) / np.hanning(2 * w + 1).sum(), "valid")
            pitch = np.interp(np.arange(n), np.arange(len(p50)) * 50, p50)
            mref = np.median([e["midi"] for e in lead])
            d += P["dyn_pitch_db"] * np.clip(pitch - mref, -7, 7)
        T = P["length_s"]
        d += P["dyn_arch_db"] * (np.sin(np.pi * np.clip(t / T, 0, 1)) ** 1.5 - 0.5)
    if P["hyper_db"] != 0 and S_GRID.get("beat_s"):
        # two-bar hypermeter: the odd bar of each pair is pushed harder (smooth, peak at its downbeat)
        bar = 3 * S_GRID["beat_s"]
        ph = (t - S_GRID["bar1_s"]) / (2 * bar)
        d += P["hyper_db"] * 0.5 * np.cos(2 * np.pi * ph)
    if P["dyn_wander_db"] > 0:
        d += P["dyn_wander_db"] * slow_noise(n, 0.9, rng)
    # waltz pulse in the bellows: beats 2-3 pushed (brighter), beat 1 eased ("u a a"), shared by every reed
    pb = np.zeros(n)
    if (P["pulse_bright_db"] != 0 or P["pulse_level_db"] != 0) and S_GRID.get("beat_s"):
        bs = S_GRID["beat_s"]
        k0 = int(np.floor(-S_GRID["bar1_s"] / bs)) - 1
        tt = np.arange(int(0.5 * SR)) / SR
        a = P["pah_attack_ms"] / 1000
        shape_ = np.where(tt < a, 0.5 - 0.5 * np.cos(np.pi * tt / a), np.exp(-(tt - a) / P["pulse_decay_s"]))
        k = k0
        while True:
            t0 = S_GRID["bar1_s"] + k * bs
            k += 1
            if t0 > n / SR:
                break
            if t0 < -0.5 or (k - 1) % 3 == 0:
                continue
            i0 = int(t0 * SR)
            seg = shape_[max(0, -i0):min(len(shape_), n - i0)]
            pb[max(0, i0):max(0, i0) + len(seg)] = np.maximum(pb[max(0, i0):max(0, i0) + len(seg)], seg)
        pb = pb - pb.mean()
    d = d + P["pulse_level_db"] * pb
    if not np.any(d) and not np.any(pb):
        return y
    d = np.clip(d, -12, 12)
    g = db2a(d)
    lo = ss.sosfiltfilt(ss.butter(2, 1200, "lowpass", fs=SR, output="sos"), y)
    return lo * g + (y - lo) * g * db2a(P["dyn_bright"] * d + P["pulse_bright_db"] * pb)


# ------------------------------------------------------------------------------------------------ chain
def room_ir(P, rng, dur=1.6):
    n = int(dur * SR)
    t = np.arange(n) / SR
    pd = P["room_pd_ms"] / 1000
    tt = np.clip(t - pd, 0, None)
    on = t > pd
    hold = P["room_hold_ms"] / 1000
    env = on * (1 - np.exp(-tt / (P["room_build_ms"] / 1000 + 1e-9))) * np.exp(-6.91 * np.maximum(tt - hold, 0) / P["room_rt60"])
    env2 = on * (1 - np.exp(-tt / 0.02)) * np.exp(-6.91 * tt / P["room_tail_rt"]) * db2a(P["room_tail_db"])
    sos = ss.butter(2, [P["room_hp"], P["room_lp"]], "bandpass", fs=SR, output="sos")
    h = []
    for _ in range(2):
        x = rng.standard_normal(n) * env + rng.standard_normal(n) * env2
        h.append(ss.sosfilt(sos, x))
    h = np.array(h).T
    h /= np.sqrt(np.sum(h ** 2) / 2)
    return h


def wow_cents(n, P, rng):
    t = np.arange(n) / SR
    out = np.zeros(n)
    if P["wow_c"] > 0:
        rate = P["wow_rate"] * (1 + 0.08 * bandnoise(n, 0.02, 0.3, rng))
        ph = 2 * np.pi * np.cumsum(rate) / SR + rng.uniform(0, 2 * np.pi)
        s = np.exp(P["wow_skew"] * np.cos(ph)) if P["wow_skew"] > 0 else np.cos(ph)
        s = (s - s.mean()) / (s.std() + 1e-12)
        out += P["wow_c"] * s
    if P["wow_rand_c"] > 0:
        out += P["wow_rand_c"] * bandnoise(n, 0.8, 5.0, rng)
    if P["flutter_c"] > 0:
        out += P["flutter_c"] * bandnoise(n, 3.5, 9.0, rng)
    if P["flutter_per_c"] > 0:
        r = P["flutter_rate"] * (1 + 0.05 * bandnoise(n, 0.05, 0.5, rng))
        out += P["flutter_per_c"] * np.sqrt(2) * np.sin(2 * np.pi * np.cumsum(r) / SR + rng.uniform(0, 6.28))
    return out


def medium(y, P, rng):
    """lossy-medium model (the original reached us through low-bitrate HE-AAC; tape/codec noise is signal-dependent):
    complex gaussian noise added in the STFT domain at medium_db re the 1/3-oct smoothed local spectrum (shape
    medium_shape), and an SBR-like regeneration above sbr_hz: noise with the smoothed envelope of the band below."""
    if P["medium_db"] <= -90 and P["sbr_db"] <= -90:
        return y
    nper, hop = 2048, 512
    pts = sorted(P["medium_shape"])
    ms = P["medium_ms"] and y.shape[1] == 2
    if ms:                                   # joint-stereo coding: noise in mid and side, each re its own spectrum
        y = np.stack([(y[:, 0] + y[:, 1]) / 2, (y[:, 0] - y[:, 1]) / 2], 1)
    out = np.zeros_like(y)
    for c in range(y.shape[1]):
        f, t, Z = ss.stft(y[:, c], SR, nperseg=nper, noverlap=nper - hop)
        A = smooth_logf(np.abs(Z) ** 2, f, 1 / 3)
        A = np.maximum(A, 1e-30)
        k = max(1, int(P["medium_tsmooth"]))
        if k > 1:
            # causal smoothing over the current and previous frames: no noise before an onset (no pre-echo bursts)
            cs = np.cumsum(np.pad(A, ((0, 0), (k, 0)), mode="edge"), axis=1)
            A = (cs[:, k:] - cs[:, :-k]) / k
        A = np.nan_to_num(np.maximum(A, 1e-30), nan=1e-30)
        shp = np.interp(np.log2(np.clip(f, 20, None)), np.log2([p[0] for p in pts]), [p[1] for p in pts])
        G = db2a(P["medium_db"] + shp)
        noise = (rng.standard_normal(Z.shape) + 1j * rng.standard_normal(Z.shape)) / np.sqrt(2)
        Z2 = Z + np.sqrt(A) * G[:, None] * noise
        if P["sbr_db"] > -90:
            fx = P["sbr_hz"]
            hi = f >= fx
            src = fx / 2 + (f[hi] - fx) % (fx / 2)
            si = np.clip(np.searchsorted(f, src), 0, len(f) - 1)
            ph = (rng.standard_normal((hi.sum(), Z.shape[1])) + 1j * rng.standard_normal((hi.sum(), Z.shape[1]))) / np.sqrt(2)
            Z2[hi] = Z2[hi] + db2a(P["sbr_db"]) * np.sqrt(A[si]) * ph
        _, x = ss.istft(Z2, SR, nperseg=nper, noverlap=nper - hop)
        out[:, c] = x[: len(y)] if len(x) >= len(y) else np.pad(x, (0, len(y) - len(x)))
    if ms:
        out = np.stack([out[:, 0] + out[:, 1], out[:, 0] - out[:, 1]], 1)
    return out


def vary_speed(y, cents):
    ratio = 2 ** (cents / 1200)
    pos = np.cumsum(ratio)
    pos -= pos[0]
    pos *= (len(y) - 4) / pos[-1]
    return np.stack([hermite(y[:, c], pos + 1) for c in range(y.shape[1])], 1)


THIRD = np.array([f for f, _ in TARGET_LTAS])


def third_oct_db(m):
    f, Pw = ss.welch(m, SR, nperseg=8192, noverlap=6144)
    out = []
    for fc in THIRD:
        msk = (f >= fc * 2 ** (-1 / 6)) & (f < fc * 2 ** (1 / 6))
        out.append(Pw[msk].sum() if msk.any() else 1e-20)
    return 10 * np.log10(np.array(out) + 1e-20)


def fir_from_bands(gdb_bands, n=4097):
    ff = np.linspace(0, SR / 2, 2049)
    gg = np.interp(np.log2(np.clip(ff, 15, None)), np.log2(THIRD), gdb_bands)
    return ss.firwin2(n, ff / (SR / 2), 10 ** (gg / 20))


def apply_fir(y, h):
    z = ss.fftconvolve(y, h[:, None], mode="full", axes=0)
    d = len(h) // 2
    return z[d:d + len(y)]


def patch_eq(y, pts):
    if not pts:
        return y
    pts = sorted(pts)
    g = np.interp(np.log2(THIRD), np.log2([p[0] for p in pts]), [p[1] for p in pts])
    return apply_fir(y, fir_from_bands(g))


def match_eq(y, P, active):
    tgt = np.array([d for _, d in TARGET_LTAS])
    sel = (THIRD >= P["match_fmin"]) & (THIRD <= P["match_fmax"])
    ref = (THIRD >= 250) & (THIRD <= 4000)
    for _ in range(int(P["match_passes"])):
        m = y[active].mean(1)
        L = third_oct_db(m)
        Lr = L - np.log10(np.sum(10 ** (L[ref] / 10))) * 10
        Tr = tgt - np.log10(np.sum(10 ** (tgt[ref] / 10))) * 10
        g = (Tr - Lr) * P["match"]
        g = np.where(sel, g, np.nan)
        gi = np.interp(np.arange(len(THIRD)), np.flatnonzero(sel), g[sel])
        gi = np.clip(gi, -P["match_cap_db"] * 2, P["match_cap_db"])
        if P["match_smooth"]:
            gs = np.convolve(np.r_[gi[0], gi, gi[-1]], [0.25, 0.5, 0.25], "valid")   # ~2/3-oct smoothing
        else:
            gs = gi.copy()                       # one gain per 1/3-octave band (= 1/3-octave smoothing)
        idx = np.flatnonzero(sel)
        gs[: idx[0]] = gs[idx[0]]
        gs[idx[-1] + 1:] = gs[idx[-1]]
        y = apply_fir(y, fir_from_bands(gs))
    return y


# ---- BS.1770 loudness
def _biquad_kweight():
    fs = SR
    G, Q, fc = 4.0, 1 / np.sqrt(2), 1500.0
    A = 10 ** (G / 40)
    w0 = 2 * np.pi * fc / fs
    al = np.sin(w0) / (2 * Q)
    b = [A * ((A + 1) + (A - 1) * np.cos(w0) + 2 * np.sqrt(A) * al), -2 * A * ((A - 1) + (A + 1) * np.cos(w0)),
         A * ((A + 1) + (A - 1) * np.cos(w0) - 2 * np.sqrt(A) * al)]
    a = [(A + 1) - (A - 1) * np.cos(w0) + 2 * np.sqrt(A) * al, 2 * ((A - 1) - (A + 1) * np.cos(w0)),
         (A + 1) - (A - 1) * np.cos(w0) - 2 * np.sqrt(A) * al]
    fc2, Q2 = 38.0, 0.5
    w0 = 2 * np.pi * fc2 / fs
    al = np.sin(w0) / (2 * Q2)
    b2 = [(1 + np.cos(w0)) / 2, -(1 + np.cos(w0)), (1 + np.cos(w0)) / 2]
    a2 = [1 + al, -2 * np.cos(w0), 1 - al]
    return (np.array(b) / a[0], np.array(a) / a[0]), (np.array(b2) / a2[0], np.array(a2) / a2[0])


def lufs(y):
    (b1, a1), (b2, a2) = _biquad_kweight()
    z = ss.lfilter(b2, a2, ss.lfilter(b1, a1, y, axis=0), axis=0)
    blk, hop = int(0.4 * SR), int(0.1 * SR)
    ms = np.array([np.sum(np.mean(z[i:i + blk] ** 2, axis=0)) for i in range(0, len(z) - blk + 1, hop)])
    lk = -0.691 + 10 * np.log10(ms + 1e-20)
    g = ms[lk > -70]
    if len(g) == 0:
        return -99.0
    rel = -0.691 + 10 * np.log10(np.mean(g)) - 10
    g2 = ms[(lk > -70) & (lk > rel)]
    return float(-0.691 + 10 * np.log10(np.mean(g2)))


def true_peak_db(y):
    u = ss.resample_poly(y, 4, 1, axis=0)
    return float(20 * np.log10(np.max(np.abs(u)) + 1e-12))


def peak_shave(y, ceil_db, look_ms=3.0, rel_ms=40.0):
    """rare-peak ceiling (the original peaks at -16.8 dBTP with no limiting; our pah swells occasionally stack higher).
    Gain = min(1, ceiling / local 4x-oversampled peak), look-ahead min-filter, smooth release. Touches only the few
    windows above the ceiling."""
    ceil = db2a(ceil_db)
    up = np.abs(ss.resample_poly(y, 4, 1, axis=0)).max(1)
    pk = up.reshape(-1, 4).max(1)[: len(y)] if len(up) >= 4 * len(y) else np.pad(up, (0, 4 * len(y) - len(up))).reshape(-1, 4).max(1)
    need = np.minimum(1.0, ceil / np.maximum(pk, 1e-12))
    if need.min() >= 1.0:
        return y
    from scipy.ndimage import minimum_filter1d, uniform_filter1d
    k = int(look_ms / 1000 * SR) * 2 + 1
    g = minimum_filter1d(need, k)
    # release: exponential recovery toward 1 (run backwards+forwards keeps it symmetric around the peak)
    a = np.exp(-1.0 / (rel_ms / 1000 * SR))
    gf = g.copy()
    for i in range(1, len(gf)):
        gf[i] = min(g[i], 1 - (1 - gf[i - 1]) * a)
    gb = gf.copy()
    for i in range(len(gb) - 2, -1, -1):
        gb[i] = min(gb[i], 1 - (1 - gb[i + 1]) * a)
    gb = uniform_filter1d(gb, int(0.002 * SR) + 1)
    return y * gb[:, None]


def soft_peak(y, ceil_db, knee_db=4.0):
    """instantaneous soft knee above (ceiling - knee), 4x oversampled; only the tops of the rare peaks are bent."""
    c = db2a(ceil_db)
    k = c * db2a(-knee_db)
    u = ss.resample_poly(y, 4, 1, axis=0)
    a = np.abs(u)
    over = a > k
    w = c - k
    out = u.copy()
    out[over] = np.sign(u[over]) * (k + w * np.tanh((a[over] - k) / w))
    return ss.resample_poly(out, 1, 4, axis=0)[: len(y)]


def peak_limit(y, P, extra=0.0):
    if P["peak_mode"] == "soft":
        return soft_peak(y, P["peak_ceiling_dbtp"] - 0.3 + extra)
    return peak_shave(y, P["peak_ceiling_dbtp"] + extra, P["peak_look_ms"], P["peak_rel_ms"])


def chain(dry, P, seed):
    rng = np.random.default_rng(seed + 1000)
    n = len(dry)
    # room (mono dry source in a decorrelated stereo room)
    wc = wow_cents(n, P, rng)
    if P["wow_pre"]:
        # pitch motion in the source (common drift of all reeds) instead of on the playback medium
        dry = vary_speed(dry[:, None], wc)[:, 0]
    h = room_ir(P, np.random.default_rng(int(P["room_seed"])) if P["room_seed"] >= 0 else rng)
    g = db2a(P["room_wet_db"])
    y = np.stack([dry + g * ss.fftconvolve(dry, h[:, 0])[:n], dry + g * ss.fftconvolve(dry, h[:, 1])[:n]], 1)
    # wow + flutter (common to both channels)
    if not P["wow_pre"]:
        y = vary_speed(y, wc)
    # tape modulation noise (signal-dependent noise sidebands)
    if P["modnoise"] > 0:
        lo, hi = P["modnoise_band"]
        m = bandnoise(n, lo, hi, rng) * P["modnoise"]
        y = y * (1 + m[:, None])
    # band limits + patch EQ + lossy-medium noise / HF regeneration + match EQ
    y = ss.sosfilt(ss.butter(P["hp_order"], P["hp_hz"], "highpass", fs=SR, output="sos"), y, axis=0)
    y = ss.sosfilt(ss.butter(P["lp_order"], P["lp_hz"], "lowpass", fs=SR, output="sos"), y, axis=0)
    y = patch_eq(y, P["patch_eq"])
    y = medium(y, P, rng)
    L = int(P["length_s"] * SR)
    y = y[:L]
    env = np.sqrt(np.convolve(y.mean(1) ** 2, np.ones(441) / 441, "same"))
    active = env > env.max() * 1e-3
    if P["match"] > 0:
        y = match_eq(y, P, active)
    # level first (hum/rumble are absolute dBFS)
    fade = int(P["fade_s"] * SR)
    end = L - int(P["end_margin_s"] * SR)
    win = np.ones(L)
    win[end - fade:end] = 1 - raised(fade)
    win[end:] = 0
    y = y * win[:, None]
    lu = lufs(y)
    y = y * db2a(P["lufs"] - lu)
    t = np.arange(L) / SR
    nz = np.zeros(L)
    for f, d in P["hum"]:
        nz += db2a(d) * np.sin(2 * np.pi * f * t + rng.uniform(0, 6.28))
    if P["lf_noise_db"] > -120:
        # diffuse low-frequency floor of the medium (mono, like the original's LF): ~flat per 1/3 octave 30-250 Hz
        w = rng.standard_normal(L)
        w = ss.sosfilt(ss.butter(2, [30.0, 260.0], "bandpass", fs=SR, output="sos"), w)
        w = ss.lfilter([1.0], [1.0, -0.97], w)          # tilt toward the low end
        w = ss.sosfilt(ss.butter(2, 30.0, "highpass", fs=SR, output="sos"), w)
        w = ss.sosfilt(ss.butter(4, 260.0, "lowpass", fs=SR, output="sos"), w)
        nz += w / (np.std(w) + 1e-12) * np.sqrt(0.5) * db2a(P["lf_noise_db"])
    if P["rumble_db"] > -120:
        r = bandnoise(L, 4.0, 20.0, rng)
        nz += r * np.sqrt(0.5) * db2a(P["rumble_db"])
    nz *= win
    y = y + nz[:, None]
    lu2 = lufs(y)
    y = y * db2a(P["lufs"] - lu2)
    if P["peak_ceiling_dbtp"] is not None:
        for _ in range(3):                  # ceiling and loudness together (shaving lowers LUFS a little)
            y = peak_limit(y, P)
            y = y * db2a(P["lufs"] - lufs(y))
        y = peak_limit(y, P, 0.05)
    return y, {"lufs": lufs(y), "true_peak_dbtp": true_peak_db(y), "sample_peak_dbfs": float(20 * np.log10(np.abs(y).max()))}


# ------------------------------------------------------------------------------------------------- main
def render(melody, out, seed=1, recipe=DEFAULT_RECIPE, sets=None, stems=None, quiet=False):
    P = make_params(recipe, sets)
    S = load_score(melody)
    cache = os.environ.get("HIBRIT_CACHE")
    dry = None
    if cache and not stems:
        import hashlib
        key = {k: v for k, v in P.items() if not k.startswith(CHAIN_PREFIXES)}
        h = hashlib.sha1((open(melody).read() + json.dumps(key, sort_keys=True) + str(seed)).encode()).hexdigest()[:16]
        cp = os.path.join(cache, f"dry_{h}.npy")
        if os.path.exists(cp):
            dry = np.load(cp).astype(np.float64)
    if dry is None:
        rng = np.random.default_rng(seed)
        S_GRID.update({"beat_s": S["beat_s"], "bar1_s": tsec(S, 0.0)})
        ev = build_parts(S, P, rng)
        dry = render_parts(ev, P, seed, stems)
        if cache and not stems:
            os.makedirs(cache, exist_ok=True)
            old = sorted((os.path.getmtime(os.path.join(cache, f)), f) for f in os.listdir(cache) if f.startswith("dry_"))
            for _, f in old[:-12]:                       # keep the cache small (disk is shared)
                os.remove(os.path.join(cache, f))
            np.save(cp, dry.astype(np.float32))
    y, info = chain(dry, P, seed)
    sf.write(out, y.astype(np.float32), SR, subtype="FLOAT")
    info.update({"file": out, "recipe": recipe, "seed": seed, "bpm": S["bpm"]})
    if not quiet:
        print(json.dumps(info))
    return info


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("melody")
    ap.add_argument("out")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--recipe", default=DEFAULT_RECIPE, choices=sorted(RECIPES))
    ap.add_argument("--set", action="append", default=[], help="override a parameter: key=JSON value")
    ap.add_argument("--stems", help="also write the dry part stems to this folder")
    a = ap.parse_args()
    render(a.melody, a.out, a.seed, a.recipe, a.set, a.stems)


if __name__ == "__main__":
    main()
