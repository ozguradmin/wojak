#!/usr/bin/env python3
"""spektral: a measurement-driven spectral-modelling sound engine for the channel's signature waltz.

    python3 render.py <melody.json> <out.wav> [--seed N] [--params P.json] [--set section.key=value ...]
                      [--stems DIR] [--no-chain] [--quiet]

Everything is synthesised from numbers. The original recording is NOT read at render time: its measured properties
(analiz/tini.json, olcum.py reports) are stored as parameters in params.json next to this file, and the fitting that
produced them is logged in log.md.

Signal model
  Instrument  free-reed family (tremolo harmonica lead, accordion-like accompaniment). Each note is one or more reeds;
              each reed is an additive oscillator bank (harmonics k*f0, no inharmonicity, as measured) whose partial
              amplitudes come from a source term (spectral slope, odd>even penalty, fixed per-reed random partial offsets)
              times a fixed body/formant envelope E(f) evaluated at the partial's current frequency. Amplitudes and
              brightness follow a breath/bellows "pressure" curve (higher pressure = louder AND brighter, gamma dB per
              octave of harmonic number per dB), with slow per-partial shimmer.
  Micro-motion  two reeds detuned by a pitch-dependent beat rate (musette/tremolo beating, measured k x 6.7 Hz at C5,
              k x 8.3 Hz at Ab5), per-reed slow pitch drift and 3-9 Hz pressure jitter, pressure-pitch coupling, per-pitch
              reed intonation offsets, an onset pitch settle, scoops into long notes after leaps, a sharpening drift on
              the final hold, breath noise pulsed by the reed (so it lives near the harmonics), a soft onset chiff.
  Articulation  45 ms-class entrance attacks, partial-dependent attack bloom, overlapping legato transitions (no dips),
              phrase dynamics from velocity, pitch height, climax and final hold.
  Accompaniment  waltz "oom-pah-pah": beat 1 = dark bass reed pair (fundamental removed later by the band, heard through
              its partials), beats 2-3 = bright 48/55 ms bellows swells of the chord over a sustained legato chord bed
              (the measured "u a a" = brightness + level pattern). Pattern text is parsed (see parse_pattern).
  Chain       wow/flutter (variable delay), short decorrelated stereo room, band limits, optional signal-following
              codec-like noise fill, smoothed (>= 1/3 octave) LTAS match EQ toward the original's measured LTAS,
              hum + infrasonic rumble, loudness to -29.5 LUFS with a true-peak ceiling, end fade.

Melody JSON (BAGLAM.md): {"id","tempo_bpm","pickup_beats","notes":[{"bar","beat","dur_beats","midi","vel"}],
  "chords":[{"bar","beat","dur_beats","midi":[..], optional "bass"}], "accomp":{"pattern": "..."}, "counter":[..]}
  bars are 1-based, beats 1.0-3.x; time(bar,beat) = (pickup_beats + 3*(bar-1) + beat-1) * 60/tempo.
"""
from __future__ import annotations

import argparse
import copy
import json
import math
import os
import re
import sys

import numpy as np
import scipy.signal as ss
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 44100
HOP = 64                      # control-rate hop (689 Hz)

try:                          # numba is optional (pure-numpy fallback below)
    from numba import njit
except Exception:             # pragma: no cover
    njit = None


# ------------------------------------------------------------------------------------------------ oscillator bank
def _osc_np(phase, amps, ph0, hop, out):
    n = len(phase)
    tc = np.arange(n) / hop
    xc = np.arange(amps.shape[1])
    for k in range(amps.shape[0]):
        a = np.interp(tc, xc, amps[k])
        if a.max() > 1e-9:
            out += a * np.sin((k + 1) * phase + ph0[k])


if njit is not None:
    @njit(cache=True, fastmath=True)
    def _osc_nb(phase, amps, ph0, hop, out):
        n = phase.shape[0]
        K = amps.shape[0]
        nc = amps.shape[1]
        for i in range(n):
            c = i / hop
            j = int(c)
            if j >= nc - 1:
                j = nc - 2
                fr = 1.0
            else:
                fr = c - j
            p = phase[i]
            acc = 0.0
            for k in range(K):
                a0 = amps[k, j]
                a = a0 + (amps[k, j + 1] - a0) * fr
                if a > 1e-9:
                    acc += a * math.sin((k + 1) * p + ph0[k])
            out[i] += acc
    osc_bank = _osc_nb
else:                         # pragma: no cover
    osc_bank = _osc_np


# ---------------------------------------------------------------------------------------------------- helpers
def db2a(x):
    return 10.0 ** (np.asarray(x, dtype=float) / 20.0)


_SOS = {}


def _bp_sos(lo, hi, fs):
    k = (round(lo, 6), round(hi, 6), round(fs, 3))
    if k not in _SOS:
        _SOS[k] = ss.butter(2, [lo, hi], "bandpass", fs=fs, output="sos")
    return _SOS[k]


def band_noise(rng, n, fs, band, rms):
    """band-limited gaussian noise (zero-phase), unit-variance scaled to rms; n samples at rate fs"""
    if rms == 0 or n < 8:
        return np.zeros(n)
    pad = int(fs * 2) + 16
    w = rng.standard_normal(n + 2 * pad)
    lo, hi = band
    hi = min(hi, 0.45 * fs)
    sos = _bp_sos(lo, hi, fs)
    w = ss.sosfiltfilt(sos, w)[pad:pad + n]
    s = np.std(w)
    return w / (s + 1e-12) * rms


def pan_gains(p):
    th = (np.clip(p, -1, 1) + 1) * math.pi / 4
    return math.cos(th) * math.sqrt(2), math.sin(th) * math.sqrt(2)


def raised_cos(x):
    x = np.clip(x, 0.0, 1.0)
    return 0.5 - 0.5 * np.cos(math.pi * x)


def midi_hz(m, cents=0.0):
    return 440.0 * 2.0 ** ((m - 69) / 12.0 + cents / 1200.0)


def seeded(seed, *keys):
    """deterministic RNG for (seed, keys...): stable across runs and machines"""
    import hashlib
    h = hashlib.sha1(repr((int(seed),) + tuple(str(k) for k in keys)).encode()).digest()
    return np.random.default_rng(int.from_bytes(h[:8], "little"))


# ---------------------------------------------------------------------------------------------------- score
def load_score(path, G):
    js = json.load(open(path))
    bpm = float(js.get("tempo_bpm", 152))
    beat = 60.0 / bpm
    bpb = int(js.get("beats_per_bar", G.get("beats_per_bar", 3)))
    pick = float(js.get("pickup_beats", 0))

    def T(bar, bt):
        return (pick + bpb * (float(bar) - 1) + float(bt) - 1) * beat

    def notes_of(lst):
        out = []
        for n in lst or []:
            if n.get("midi") is None:
                continue
            t0 = T(n["bar"], n.get("beat", 1))
            out.append({"t0": t0, "t1": t0 + float(n.get("dur_beats", 1)) * beat, "midi": float(n["midi"]),
                        "vel": float(n.get("vel", 90)), "dur_beats": float(n.get("dur_beats", 1)),
                        "beat_pos": float(n.get("beat", 1))})
        out.sort(key=lambda d: (d["t0"], d["midi"]))
        return out

    chords = []
    for c in js.get("chords", []) or []:
        t0 = T(c["bar"], c.get("beat", 1))
        mids = c.get("midi") or []
        if isinstance(mids, (int, float)):
            mids = [mids]
        chords.append({"t0": t0, "t1": t0 + float(c.get("dur_beats", bpb)) * beat, "midi": [float(m) for m in mids],
                       "bass": c.get("bass"), "bar": c["bar"], "beat": float(c.get("beat", 1))})
    chords.sort(key=lambda d: d["t0"])
    acc = js.get("accomp") or {}
    pattern = acc.get("pattern", "") if isinstance(acc, dict) else str(acc)
    return {"id": js.get("id", os.path.basename(path)), "bpm": bpm, "beat": beat, "bpb": bpb, "pickup": pick,
            "notes": notes_of(js.get("notes")), "counter": notes_of(js.get("counter")), "chords": chords,
            "pattern": pattern, "T": T}


def parse_pattern(text, default="B C C", bpb=3):
    """Accompaniment pattern. Explicit grid: one token per beat, e.g. "B C C" (B bass, C chord swell, A arpeggio
    tone, H hold/bed only, - rest/nothing), optionally with '|' bar separators (first bar is used). Otherwise keywords:
    waltz / um-pa-pa / oom-pah / root on beat 1 -> B C C; block / chord on every beat -> C C C; bass only -> B - -;
    no bass -> - C C; arpeggio / broken -> B A A. Modifiers: staccato/dry (no sustained bed), sustained/legato/held
    (bed on, default), soft/quiet (-3 dB), loud (+2 dB), sparse (only beat 2 swell)."""
    t = (text or "").strip()
    flags = {"bed": True, "gain_db": 0.0}
    low = t.lower()
    m = re.fullmatch(r"[\sBCAH\-|.]+", t) if t else None
    if m and any(ch in t for ch in "BCAH"):
        first = t.split("|")[0] if t.split("|")[0].strip() else t.replace("|", " ")
        toks = [x for x in re.split(r"\s+", first.strip()) if x]
        if len(toks) == 1 and len(toks[0]) == bpb:
            toks = list(toks[0])
        roles = [(toks[i] if i < len(toks) else "-").replace(".", "-") for i in range(bpb)]
        return roles, flags
    roles = default.split()
    if any(w in low for w in ("block", "every beat", "all beats", "beats 1-3", "beats 1, 2, 3")):
        roles = ["C"] * bpb
    if "bass only" in low or "root only" in low:
        roles = ["B"] + ["-"] * (bpb - 1)
    if "no bass" in low or "without bass" in low:
        roles = ["-"] + roles[1:]
    if "arpegg" in low or "broken" in low:
        roles = ["B"] + ["A"] * (bpb - 1)
    if "sparse" in low:
        roles = [roles[0], "C"] + ["H"] * (bpb - 2)
    if any(w in low for w in ("staccato", "dry", "detached")) and "sustain" not in low and "legato" not in low:
        flags["bed"] = False
    if "soft" in low or "quiet" in low:
        flags["gain_db"] -= 3.0
    if "loud" in low:
        flags["gain_db"] += 2.0
    while len(roles) < bpb:
        roles.append("C")
    return roles[:bpb], flags


def chord_root(mids):
    """root pitch class of a chord (triad/seventh stacked in thirds); falls back to the lowest note"""
    pcs = sorted(set(int(round(m)) % 12 for m in mids))
    if not pcs:
        return None
    best, bs = int(round(min(mids))) % 12, -1
    for r in pcs:
        iv = set((p - r) % 12 for p in pcs)
        s = (3 if (4 in iv or 3 in iv) else 0) + (2 if 7 in iv else 0) + (1 if 6 in iv else 0) + (1 if 10 in iv or 11 in iv else 0)
        s -= 2 * len(iv - {0, 3, 4, 6, 7, 10, 11, 9})
        if s > bs:
            bs, best = s, r
    return best


def voice_chord_top(mids, top_target, n_max=4):
    """close-position inversion whose top note is nearest top_target (the measured pah sits with its top two tones in
    the C5-F5 octave: C5/Eb5 over i, D5/F5 over vii); returns ascending midi list (<= n_max tones, top-most kept)"""
    pcs = sorted(set(int(round(m)) % 12 for m in mids))
    if not pcs:
        return []
    best, bd = None, 1e9
    for top_pc in pcs:
        for octv in range(4, 8):
            top = 12 * octv + top_pc
            if abs(top - top_target) > 6:
                continue
            v = [top]
            for _ in range(len(pcs) - 1):
                cands = [12 * o + p for p in pcs for o in range(2, 8) if 12 * o + p < v[-1] and (12 * o + p) % 12 not in [x % 12 for x in v]]
                v.append(max(cands))
            d = abs(top - top_target) + 0.01 * (v[0] - v[-1])
            if d < bd:
                bd, best = d, sorted(v)
    best = best or sorted(mids)
    return best[-n_max:]


def voice_chord(mids, lo, hi):
    """keep the written voicing when it lies inside [lo, hi]; otherwise move the whole chord by octaves, then fold
    single outliers, so the pah chord sits in the measured C4-C5 register"""
    v = sorted(float(m) for m in mids)
    if not v:
        return v
    while min(v) < lo and max(v) + 12 <= hi + 6:
        v = [m + 12 for m in v]
    while max(v) > hi and min(v) - 12 >= lo - 6:
        v = [m - 12 for m in v]
    v = [m + 12 if m < lo - 6 else (m - 12 if m > hi + 6 else m) for m in v]
    return sorted(set(v))


# ------------------------------------------------------------------------------------------------ reed model
def spec_db(k, f, inst, tilt=0.0):
    """source + body envelope in dB for harmonic numbers k at frequencies f (arrays of equal shape)"""
    lk = np.log2(k)
    d = -(inst["slope_db_oct"] - tilt) * lk - inst["even_pen_db"] * ((k % 2) == 0)
    lf = np.log2(np.maximum(f, 20.0))
    for F, g, w in inst["formants"]:
        d = d + g * np.exp(-0.5 * ((lf - math.log2(F)) / w) ** 2)
    return d


class ReedVoice:
    """renders reed notes into a stereo buffer from control curves"""

    def __init__(self, n_total, seed):
        self.n = n_total
        self.out = np.zeros((2, n_total))
        self.seed = seed

    def note(self, s0, nc, f0c, ampc, pressc, reeds, inst, rng, key, breath=None, chiff=None):
        """s0: first audio sample; nc control frames; f0c: nominal f0 (Hz) per control frame (incl. bends/drift common
        to the reeds); ampc: linear amplitude per control frame; pressc: pressure dB per control frame (brightness);
        reeds: list of dicts (det_c may be a number per frame array); key: deterministic id for per-reed randomness"""
        n = (nc - 1) * HOP + 1
        if s0 >= self.n or nc < 2:
            return
        n = min(n, self.n - s0)
        nc_eff = (n - 1) // HOP + 2
        nc_eff = min(nc_eff, nc)
        tc = np.arange(n) / HOP
        xc = np.arange(nc)
        fmax = inst["fmax_hz"]
        mono_breath = None
        for ri, rd in enumerate(reeds):
            det = rd["det_c_arr"] if "det_c_arr" in rd else np.full(nc, float(rd.get("det_c", 0.0)))
            mult = 2.0 ** (rd.get("oct", 0))
            fr = f0c * mult * 2.0 ** (det / 1200.0)
            if "pitch_dev_c" in rd:
                fr = fr * 2.0 ** (rd["pitch_dev_c"] / 1200.0)
            fmin_ = float(fr.min())
            K = int(min(fmax, 0.45 * SR) / max(float(fr.max()), 1.0))
            if K < 1:
                continue
            k = np.arange(1, K + 1, dtype=float)[:, None]
            fk = k * fr[None, :]
            sd = spec_db(k, fk, inst, tilt=rd.get("tilt_db_oct", 0.0))
            r2 = seeded(self.seed, key, "reed", ri)
            sd = sd + r2.normal(0.0, inst["partial_sigma_db"], (K, 1))
            # pressure brightness: gamma dB per octave of k per dB of pressure
            sd = sd + inst["bright_gamma"] * np.log2(k) * pressc[None, :]
            # slow per-partial shimmer
            if inst.get("shimmer_db", 0) > 0:
                nk = max(4, int(nc * HOP / SR * inst["shimmer_hz"]) + 4)
                knots = r2.normal(0.0, inst["shimmer_db"], (K, nk))
                xs = np.linspace(0, nc - 1, nk)
                sh = np.array([np.interp(xc, xs, kn) for kn in knots])
                sd = sd + sh
            amps = db2a(sd) * (ampc[None, :] * db2a(rd.get("gain_db", 0.0)))
            # attack bloom: higher partials reach full level a little later
            if rd.get("bloom") is not None:
                amps = amps * rd["bloom"](k)
            amps[fk > min(fmax, 0.45 * SR)] = 0.0
            # band-edge taper of partials close to fmax
            amps *= np.clip((min(fmax, 0.45 * SR) - fk) / (0.08 * fmax), 0, 1)
            fa = np.interp(tc, xc, fr)
            ph = np.cumsum(fa) * (2 * math.pi / SR)
            # reed waveform phases: a free reed is a pulse-like source (coherent cosine phases); 'phase_coherence'
            # mixes that with random phases (fitted to the measured 50 ms crest factor)
            coh = float(inst.get("phase_coherence", 0.0))
            ph0 = (1 - coh) * r2.uniform(0, 2 * math.pi, K) + coh * (math.pi / 2 + r2.normal(0, 0.3, K))
            buf = np.zeros(n)
            osc_bank(ph, np.ascontiguousarray(amps), ph0, float(HOP), buf)
            gl, gr = pan_gains(rd.get("pan", 0.0))
            self.out[0, s0:s0 + n] += gl * buf
            self.out[1, s0:s0 + n] += gr * buf
            if ri == 0:
                mono_breath = ph
        if breath is not None and mono_breath is not None:
            # breath / bellows noise, pulsed by the reed opening (lives around the harmonics), through a band filter
            lvl, band, powp, pan = breath
            r3 = seeded(self.seed, key, "breath")
            z = r3.standard_normal(n + 512)
            sos = ss.butter(2, [band[0], min(band[1], 0.45 * SR)], "bandpass", fs=SR, output="sos")
            z = ss.sosfilt(sos, z)[512:]
            pulse = (0.5 + 0.5 * np.cos(mono_breath)) ** powp
            pulse = pulse / (np.sqrt(np.mean(pulse ** 2)) + 1e-12)
            a = np.interp(tc, xc, ampc)
            z = z * pulse * a * db2a(lvl) * 0.25
            if chiff is not None:
                cl, cms = chiff
                m = int(cms / 1000 * SR)
                if m > 8 and m < n:
                    win = np.zeros(n)
                    win[:m] = np.sin(np.linspace(0, math.pi, m)) ** 2
                    z = z + r3.standard_normal(n) * win * db2a(cl) * float(ampc.max()) * 0.25
            gl, gr = pan_gains(pan)
            self.out[0, s0:s0 + n] += gl * z
            self.out[1, s0:s0 + n] += gr * z


def beat_det_c(f0, inst):
    """detune (cents) giving the measured pitch-dependent beat rate: beat = ref * (f0/f_ref)^exp"""
    b = inst["beat_hz_ref"] * (f0 / inst["beat_f_ref"]) ** inst["beat_exp"]
    return 1200.0 * np.log2(1.0 + b / f0)


# --------------------------------------------------------------------------------------------------- phrasing
def phrase_arch(notes, G, T):
    """dB curve over time (function of t): rise from the first melody note to the climax (highest note, preferring the
    middle 35-85 % of the line), then fall to G['arch_end'] of the height at the end (measured arch: bars 4-8 3-4 dB over
    bars 0-3, bars 9-10 1-2 dB lower)"""
    h = G.get("arch_db", 0.0)
    if not notes or h == 0:
        return lambda t: np.zeros_like(np.asarray(t, float))
    t0, t1 = notes[0]["t0"], max(n["t1"] for n in notes)
    span = max(t1 - t0, 1e-3)
    mids = np.array([n["midi"] for n in notes])
    on = np.array([n["t0"] for n in notes])
    rel = (on - t0) / span
    pref = (rel >= 0.35) & (rel <= 0.85)
    cand = np.flatnonzero(pref) if pref.any() else np.arange(len(notes))
    top = mids[cand].max()
    tc = on[cand][mids[cand] == top][0]
    e = G.get("arch_end", 0.35)
    s0 = G.get("arch_start", 0.0)
    def f(t):
        t = np.asarray(t, float)
        up = s0 + (1 - s0) * raised_cos((t - t0) / max(tc - t0, 1e-3))
        dn = 1 - (1 - e) * raised_cos((t - tc) / max(t1 - tc, 1e-3))
        return h * np.where(t < tc, up, dn)
    return f


# --------------------------------------------------------------------------------------------------- melody line
def render_line(notes, inst, reeds_spec, G, rng_seed, n_total, beat, voice, tag, is_lead=True, arch=None):
    """legato reed line (lead or counter). Returns stereo array."""
    if not notes:
        return np.zeros((2, n_total))
    nctot = n_total // HOP + 2
    tct = np.arange(nctot) * HOP / SR
    rng = seeded(rng_seed, tag, "line")
    fsc = SR / HOP
    # line-wide breath pressure: slow swell + tremor (dB)
    press_line = (band_noise(rng, nctot, fsc, inst["press_slow_band_hz"], inst["press_slow_db"]) +
                  band_noise(rng, nctot, fsc, inst["press_trem_band_hz"], inst["press_trem_db"]))
    mids = np.array([n["midi"] for n in notes])
    med = float(np.median(mids))
    top = float(mids.max())
    jit = G["timing_jitter_ms"] / 1000.0
    tun = G["tuning_cents"]
    N = len(notes)
    for i, nt in enumerate(notes):
        if nt["t1"] <= 0.0 or nt["t0"] >= n_total / SR:
            continue                                    # entirely before the clip start / after its end
        prev = notes[i - 1] if i > 0 else None
        nxt = notes[i + 1] if i + 1 < N else None
        gap_tol = inst["legato_gap_beats"] * beat
        leg_in = prev is not None and (nt["t0"] - prev["t1"]) <= gap_tol and nt["t0"] > prev["t0"] + 1e-6
        leg_out = nxt is not None and (nxt["t0"] - nt["t1"]) <= gap_tol and nxt["t0"] > nt["t0"] + 1e-6
        r_on = rng.normal(0, jit) if nt["t0"] > 0.02 else 0.0
        t_on = max(0.0, nt["t0"] + r_on)
        att = (inst["legato_attack_ms"] if leg_in else inst["attack_ms"]) / 1000.0
        if leg_out and abs(nxt["midi"] - nt["midi"]) < 0.5:
            # repeated pitch: the same reed re-speaks -> a short breath/bellows re-articulation dip, no overlap
            t_off = nxt["t0"] - inst.get("repeat_gap_ms", 5) / 1000.0
            rel = inst.get("repeat_release_ms", 30) / 1000.0
        elif leg_out:
            t_off = nxt["t0"] + inst["legato_overlap_ms"] / 1000.0
            rel = inst["legato_release_ms"] / 1000.0
        else:
            t_off = nt["t1"]
            rel = inst["release_ms"] / 1000.0
        s0 = int(t_on * SR)
        dur = t_off - t_on + rel
        nc = int(dur * fsc) + 3
        tl = np.arange(nc) / fsc                        # local time
        tg = t_on + tl                                  # global time
        # ---------- amplitude
        if t_on < 0.005:                                # excerpt starts mid-sound (measured: sound at 0.000 s)
            att = 0.004
        a_att = raised_cos(tl / max(att, 1e-3))
        t_rel0 = t_off - t_on
        a_rel = 1.0 - raised_cos((tl - t_rel0) / max(rel, 1e-3))      # continuous, reaches 0 at t_rel0 + rel
        # ---------- phrase dynamics (dB)
        dyn = inst["dyn_db_per_st"] * (nt["midi"] - med) + inst["dyn_vel_db_per_10"] * (nt["vel"] - 90) / 10.0
        is_final = nxt is None and nt["dur_beats"] >= 2.5
        if nt["midi"] >= top and nt["dur_beats"] >= 1:
            dyn += inst["dyn_climax_db"]
        p_note = np.full(nc, dyn)
        # metric onset accent (breath push on each new note, stronger on the downbeat), decaying
        acc_db = inst.get("onset_accent_db", 0.0)
        if abs(nt.get("beat_pos", 0) - 1.0) < 0.02:
            acc_db += inst.get("downbeat_accent_db", 0.0)
        if acc_db:
            p_note += acc_db * np.exp(-tl / max(inst.get("accent_decay_ms", 150) / 1000.0, 1e-3))
        if is_final:
            p_note += inst["dyn_final_db"] + inst["dyn_final_decay_db"] * np.clip(tl / max(dur, 1e-3), 0, 1)
        pl = np.interp(tg, tct, press_line)
        press = p_note + pl + (arch(tg) if arch is not None else 0.0)
        amp = a_att * a_rel * db2a(press)
        # brightness follows pressure, and the attack ramp (a reed speaks dark first)
        press_b = press + 20 * np.log10(np.maximum(a_att, 1e-3)) * inst.get("attack_dark", 0.0)
        # ---------- pitch (cents, common to the reeds)
        rr = seeded(rng_seed, tag, "into", int(round(nt["midi"])))
        c = np.full(nc, tun + rr.normal(0.0, inst["intonation_sigma_c"]))
        c += inst["settle_c"] * np.exp(-tl / max(inst["settle_ms"] / 1000.0, 1e-3)) * (0.6 if leg_in else 1.0)
        if prev is not None and nt["dur_beats"] >= inst["scoop_min_beats"] and nt["midi"] - prev["midi"] >= inst["scoop_leap_st"]:
            sc = inst["scoop_ms"] / 1000.0
            c += inst["scoop_c"] * (1 - raised_cos(tl / sc))
        if is_final:
            c += inst["final_drift_c"] * raised_cos((tl - 0.35 * t_rel0) / max(0.65 * t_rel0, 1e-3))
        c += inst["press_pitch_c_per_db"] * (press - dyn)
        f0c = midi_hz(nt["midi"], c)
        # ---------- reeds
        reeds = []
        for ri, rd in enumerate(reeds_spec):
            r = dict(rd)
            rr2 = seeded(rng_seed, tag, "reed", i, ri)
            dc = beat_det_c(midi_hz(nt["midi"]), inst) if rd.get("det_c") == "beat" else float(rd.get("det_c", 0.0))
            drift = (band_noise(rr2, nc, fsc, inst["drift_band_hz"], inst["drift_c"]) +
                     band_noise(rr2, nc, fsc, inst["jitter_band_hz"], inst["jitter_c"]))
            r["det_c_arr"] = dc + drift
            spread = inst["k_attack_spread"]
            if spread > 0:
                def bloom(k, att=att, tl=tl, spread=spread):
                    # partial k reaches full level after att*(1+spread*log2 k); amp already holds the base ramp
                    tau = att * (1.0 + spread * np.log2(k))                      # (K,1)
                    ramp_k = raised_cos(tl[None, :] / np.maximum(tau, 1e-3))
                    base = raised_cos(tl[None, :] / max(att, 1e-3))
                    return np.where(base > 1e-3, ramp_k / np.maximum(base, 1e-3), 0.0).clip(0, 1)
                r["bloom"] = bloom
            reeds.append(r)
        breath = (inst["breath_db"], inst["breath_band_hz"], inst["breath_pulse_pow"], 0.0) if inst.get("breath_db") is not None else None
        chiff = (inst["chiff_db"], inst["chiff_ms"]) if (inst.get("chiff_db") is not None and not leg_in) else None
        voice.note(s0, nc, f0c, amp, press_b, reeds, inst, rng, f"{tag}:{i}:{int(nt['midi'])}", breath, chiff)
    return voice.out


# ----------------------------------------------------------------------------------------------- accompaniment
def render_acc(score, P, G, seed, n_total, arch=None):
    A = P["acc"]
    roles, flags = parse_pattern(score["pattern"], A["pattern_default"], score["bpb"])
    beat, bpb = score["beat"], score["bpb"]
    fsc = SR / HOP
    v_ch = ReedVoice(n_total, seed + 11)
    v_bs = ReedVoice(n_total, seed + 13)
    inst_ch = {k: A[k] for k in ("slope_db_oct", "even_pen_db", "formants", "partial_sigma_db", "shimmer_db",
                                 "shimmer_hz", "fmax_hz", "bright_gamma")}
    inst_bs = dict(inst_ch, slope_db_oct=A["bass_slope_db_oct"], even_pen_db=A["bass_even_pen_db"],
                   formants=A["bass_formants"])
    tun = G["tuning_cents"]
    jit = G["timing_jitter_ms"] / 1000.0
    rng = seeded(seed, "acc")
    T_end = n_total / SR
    chords = [c for c in score["chords"] if c["midi"] and c["t0"] < T_end]
    xf = A["chord_change_xfade_ms"] / 1000.0
    for ci, ch in enumerate(chords):
        t0, t1 = ch["t0"], min(ch["t1"], T_end + 0.2)
        nxt = chords[ci + 1] if ci + 1 < len(chords) else None
        legato_next = nxt is not None and abs(nxt["t0"] - t1) < 0.05
        if A.get("voicing_mode", "range") == "top":
            voiced = voice_chord_top(ch["midi"], A.get("top_target", 76))
            tg_ = A.get("tone_gain_db_from_top", [0.0, 0.0, 0.0, 0.0])
            tones = [(m, tg_[min(len(voiced) - 1 - i, len(tg_) - 1)]) for i, m in enumerate(voiced)]
        else:
            voiced = voice_chord(ch["midi"], *A["voicing_range"])
            tones = [(m, 0.0) for m in voiced]
            if A.get("double_top_db") is not None and voiced and voiced[0] + 12 > voiced[-1] and voiced[0] + 12 <= 77:
                tones.append((voiced[0] + 12, A["double_top_db"]))
        # beats covered by this chord and their roles
        b0 = (t0 / beat) - score["pickup"]
        nb = int(round((t1 - t0) / beat))
        swells, bass_on = [], []
        for j in range(max(nb, 1)):
            gb = int(round(b0)) + j                   # global beat index from bar 1 beat 1
            pos = gb % bpb
            role = roles[pos]
            tb = t0 + j * beat
            if role == "C" or (role == "A"):
                swells.append((tb + rng.normal(0, jit), role, j, pos))
            elif role == "B":
                bass_on.append(tb + rng.normal(0, jit) * 0.5)
        # ---------- chord tones: bed + swells
        tail = A["swell_tail_ms"] / 1000.0
        rel = 0.06 if not legato_next else xf
        tb_on = max(0.0, t0 - (0.0 if ci == 0 else xf * 0.5))
        dur = (t1 - tb_on) + rel + tail
        nc = int(dur * fsc) + 3
        tl = np.arange(nc) / fsc
        tg = tb_on + tl
        att_b = raised_cos(tl / (0.004 if tb_on < 0.005 else (0.045 if ci == 0 else xf)))
        rel_b = 1.0 - raised_cos((tg - t1) / max(rel, 1e-3))
        tail_w = 1.0 - raised_cos((tg - t1) / max(tail, 1e-3))
        # The measured burst shape (attack -10 dB->peak 48 ms, decay to -10 dB 55 ms) is that of the BRIGHT band
        # (900-4000 Hz). Partial k moves (1 + gamma*log2 k) dB per dB of bellows pressure, so the pressure curve is the
        # bright-band dB curve divided by (1 + gamma*L), L = log2 of a typical bright-band harmonic number.
        gam = A["bright_gamma"]
        kfac = 1.0 + gam * A.get("bright_ref_log2k", 2.3)
        a_s, d_s = A["swell_attack_ms"] / 1000.0, A["swell_decay_ms"] / 1000.0
        bedP = A["bed_db"] if flags["bed"] else -80.0          # bed in pressure dB (k = 1)
        for ti, (m, gdb) in enumerate(tones):
            pw = np.zeros(nc)                                    # swell power (pressure, linear power)
            br = np.zeros(nc)
            for si, (ts, role, j, pos) in enumerate(swells):
                if role == "A":          # arpeggio: one tone per beat (cycling upward)
                    if ti != (j % len(tones)):
                        continue
                x = tg - ts - A.get("swell_peak_delay_ms", 0.0) / 1000.0     # onset on the beat, peak later
                # held until the next beat of this chord span that is not a swell continuation (legato pah-pah):
                # measured bright-band plateau ~-11 dB re the burst peak after the 55 ms decay, until the next attack
                t_hold = (swells[si + 1][0] - ts) if si + 1 < len(swells) else (t1 - ts)
                t_hold = max(t_hold, 0.05)
                hold = A.get("swell_hold_db", -80.0)
                hrel = A.get("swell_hold_release_ms", 60) / 1000.0
                held = np.where(x <= t_hold, hold, hold - 40.0 * (x - t_hold) / hrel)
                sdb = np.where(x < 0, -10.0 * (x / a_s) ** 2, np.maximum(-10.0 * x / d_s, held))   # bright-band dB
                sdb = np.maximum(sdb, -80.0) + A.get("swell_pos_level_db", [0, 0, 0])[pos % 3] * kfac
                Pdb = sdb / kfac
                pw = pw + 10 ** (Pdb / 10)
                br = br + A.get("swell_pos_bright_db", [0, 0, 0])[pos % 3] * 10 ** (np.minimum(sdb, 0) / 10)
            bedw = (10 ** (bedP / 10)) * (att_b * rel_b) ** 2
            lin = np.sqrt(bedw + pw * tail_w ** 2)
            if arch is not None:
                lin = lin * db2a(A.get("arch_share", 0.5) * arch(tg))
            press = 20 * np.log10(np.maximum(lin, 1e-4)) + br   # 0 dB at swell peak
            amp = lin * db2a(gdb + flags["gain_db"])
            rr = seeded(seed, "acc_into", int(round(m)))
            c = np.full(nc, tun + rr.normal(0.0, A["intonation_sigma_c"]))
            f0c = midi_hz(m, c)
            reeds = []
            for ri, rd in enumerate(A["chord_reeds"]):
                r = dict(rd)
                rr2 = seeded(seed, "accreed", ci, ti, ri)
                r["det_c_arr"] = float(rd.get("det_c", 0.0)) + band_noise(rr2, nc, fsc, A["drift_band_hz"], A["drift_c"])
                reeds.append(r)
            v_ch.note(int(tb_on * SR), nc, f0c, amp, press, reeds, inst_ch, rng, f"ch:{ci}:{ti}:{int(m)}")
        # ---------- bass ("oom")
        if bass_on:
            if ch.get("bass") is not None:
                bm = float(ch["bass"])
            else:
                r = chord_root(ch["midi"])
                lo, hi = A["bass_range"]
                bm = lo + ((r - lo) % 12)
                if bm > hi:
                    bm -= 12
            for bi, tb in enumerate(bass_on):
                tb = max(0.0, tb)
                hold = A["bass_hold_s"]
                bat, brl = A["bass_attack_ms"] / 1000.0, A["bass_release_ms"] / 1000.0
                dur = hold + brl * 3
                nc = int(dur * fsc) + 3
                tl = np.arange(nc) / fsc
                if tb < 0.005:
                    bat = 0.004
                lin = raised_cos(tl / bat) * np.where(tl <= hold, 1.0, np.exp(-(tl - hold) / (brl / 3)))
                lin *= 1.0 - raised_cos((tl - hold - 2.2 * brl) / (0.8 * brl))
                press = 20 * np.log10(np.maximum(lin, 1e-4)) - 3.0
                amp = lin * db2a(A["bass_db"] + flags["gain_db"])
                if arch is not None:
                    amp = amp * db2a(A.get("arch_share", 0.5) * arch(tb + tl))
                rr = seeded(seed, "bass_into", int(round(bm)))
                c = np.full(nc, tun + rr.normal(0.0, A["intonation_sigma_c"]))
                f0c = midi_hz(bm, c)
                reeds = []
                for ri, rd in enumerate(A["bass_reeds"]):
                    r = dict(rd)
                    rr2 = seeded(seed, "bassreed", ci, bi, ri)
                    r["det_c_arr"] = float(rd.get("det_c", 0.0)) + band_noise(rr2, nc, fsc, A["drift_band_hz"], A["drift_c"])
                    reeds.append(r)
                v_bs.note(int(tb * SR), nc, f0c, amp, press, reeds, inst_bs, rng, f"bs:{ci}:{bi}:{int(bm)}")
    return v_ch.out + v_bs.out


# -------------------------------------------------------------------------------------------------------- chain
def third_oct_ltas(x, fcs):
    f, Pw = ss.welch(x, SR, nperseg=8192, noverlap=6144)
    out = []
    for fc in fcs:
        lo, hi = fc * 2 ** (-1 / 6), fc * 2 ** (1 / 6)
        m = (f >= lo) & (f < hi)
        out.append(Pw[m].sum() if m.any() else 1e-20)
    return 10 * np.log10(np.array(out) + 1e-20)


def wow_curve(m, fs2, C, seed):
    """pitch deviation (cents) of the transfer: random slow drift + flutter + a warped-record bump train.
    Measured on the original (analiz/muzik wow curve, olcum per-band deviation): the whole texture rises by
    ~55-65 c for 0.3-0.8 s once per ~2.0 s revolution (intervals 1.73-2.26 s), flat in between."""
    rng = seeded(seed, "wow")
    w = band_noise(rng, m, fs2, C["wow_slow_band_hz"], C["wow_slow_c"]) + \
        band_noise(rng, m, fs2, C["wow_fast_band_hz"], C["wow_fast_c"])
    B = C.get("warp")
    if B:
        t = np.arange(m) / fs2
        tb = rng.uniform(0.15, 1.0) * B["period_s"]
        bump = np.zeros(m)
        while tb < t[-1] + 1.0:
            A = rng.uniform(*B["height_c"])
            wd = rng.uniform(*B["width_s"])
            r = B["rise_s"]
            x = t - tb
            sh = raised_cos(x / r + 0.5) * (1 - raised_cos((x - wd) / r + 0.5))
            # a little internal wobble on the plateau (double peaks / dips seen in the measured curve)
            wob = 1 + B.get("wobble", 0.15) * np.sin(2 * math.pi * x / max(wd, 0.2) * rng.uniform(1.0, 2.0) + rng.uniform(0, 6.28))
            bump = np.maximum(bump, A * sh * wob)
            tb += B["period_s"] * (1 + rng.uniform(-B["jitter"], B["jitter"]))
        w = w + bump - np.mean(bump)
    return w


def apply_wow(y, C, seed):
    n = y.shape[1]
    fs2 = SR / 100.0
    m = n // 100 + 10
    w = wow_curve(m, fs2, C, seed)
    w = np.interp(np.arange(n) / 100.0, np.arange(m), w)
    pos = np.cumsum(2.0 ** (w / 1200.0))
    pos = pos - pos[0]
    pos = pos * (n - 1) / pos[-1]
    idx = np.arange(n)
    return np.stack([np.interp(pos, idx, y[c]) for c in range(y.shape[0])])


def room_ir(R, seed):
    rng = seeded(seed, "room")
    n = int(1.6 * SR)
    t = np.arange(n) / SR
    pd = R["predelay_ms"] / 1000.0
    tt = np.clip(t - pd, 0, None)
    env = (t > pd) * (1 - np.exp(-tt / (R["build_ms"] / 1000.0 + 1e-9))) * np.exp(-6.91 * tt / R["rt60"])
    env2 = (t > pd) * (1 - np.exp(-tt / 0.02)) * np.exp(-6.91 * tt / R["tail_rt60"]) * db2a(R["tail_db"])
    h = []
    sos = ss.butter(2, [R["hp"], R["lp"]], "bandpass", fs=SR, output="sos")
    for _ in range(2):
        z = rng.standard_normal(n) * env + rng.standard_normal(n) * env2
        h.append(ss.sosfilt(sos, z))
    h = np.array(h)
    h /= np.sqrt(np.sum(h ** 2) / 2)
    return h


def apply_room(y, R, seed):
    h = room_ir(R, seed)
    mid = y.mean(0)
    g = db2a(R["wet_db"])
    n = y.shape[1]
    wet = np.stack([ss.fftconvolve(mid, h[c])[:n] for c in range(2)])
    return y + g * wet


def transfer_noise(y, C, seed):
    """the measured recording/transfer character in the STFT domain:
    (1) modulation noise: complex noise whose power follows the signal's 1/3-octave-smoothed, 3-frame-smoothed power at
        C['modnoise_db'] (a [[Hz, dB], ...] curve) -> fills the inter-harmonic valleys the way the original's floor does
        (its floor is level-relative per band, i.e. signal-following, and no steady hiss is measurable);
    (2) high-band regeneration (SBR-like): above C['hf_regen_hz'] the original holds noise-like content without harmonic
        peaks; here noise whose per-frame level follows the 2.8-4.6 kHz band power, shaped by C['hf_regen_db'] curve.
    Correlated between channels by C['modnoise_corr'] (mid-heavy like the original's codec stereo)."""
    md = C.get("modnoise_db")
    hr = C.get("hf_regen_db")
    if md is None and hr is None:
        return y
    rng = seeded(seed, "transfer")
    nfft, hop = 1024, 256
    f = np.fft.rfftfreq(nfft, 1 / SR)
    lf = np.log2(np.maximum(f, 20))
    bw = C.get("modnoise_band_oct", 0.33)
    W = np.exp(-0.5 * ((lf[:, None] - lf[None, :]) / (bw / 2.355)) ** 2)
    W /= W.sum(1, keepdims=True)
    Zs = [ss.stft(y[c], SR, nperseg=nfft, noverlap=nfft - hop)[2] for c in range(y.shape[0])]
    shp = Zs[0].shape
    rho = float(C.get("modnoise_corr", 0.6))
    n_common = (rng.standard_normal(shp) + 1j * rng.standard_normal(shp)) / math.sqrt(2)
    ker = np.ones(3) / 3
    out = []
    for c, Z in enumerate(Zs):
        Pw = np.abs(Z) ** 2
        Ps = ss.convolve2d(W @ Pw, ker[None, :], mode="same", boundary="symm")
        n_own = (rng.standard_normal(shp) + 1j * rng.standard_normal(shp)) / math.sqrt(2)
        noise = math.sqrt(rho) * n_common + math.sqrt(1 - rho) * n_own
        Z2 = Z.copy()
        if md is not None:
            md_a = np.array(md, float)
            gg = db2a(np.interp(lf, np.log2(md_a[:, 0]), md_a[:, 1]) + C.get("modnoise_gain_db", 0.0))[:, None]
            Z2 = Z2 + noise * np.sqrt(Ps) * gg
        if hr is not None:
            hr_a = np.array(hr, float)
            f0 = float(C.get("hf_regen_hz", 5000))
            ref = (f >= 2800) & (f < 4600)
            Eref = ss.convolve2d(Pw[ref].mean(0, keepdims=True), ker[None, :], mode="same", boundary="symm")
            hf = f >= f0
            shape = db2a(np.interp(lf[hf], np.log2(hr_a[:, 0]), hr_a[:, 1]) + C.get("hf_regen_gain_db", 0.0))[:, None]
            Z2[hf] = Z2[hf] * 0.0 + noise[hf] * np.sqrt(Eref) * shape
        holes = C.get("codec_holes")
        if holes:
            # low-bitrate core-codec band edge: weak coefficients quantised to zero (the original's 4 kHz band has
            # valleys -47 dB under its band mean, far deeper than its 250-3150 Hz bands)
            lo_h, hi_h, thr = holes
            hb = (f >= lo_h) & (f < hi_h)
            Pb = np.abs(Z2[hb]) ** 2
            ref_b = ss.convolve2d(Pb, np.ones((9, 1)) / 9, mode="same", boundary="symm")
            Z2[hb] = np.where(Pb < ref_b * db2a(thr) ** 2, Z2[hb] * 0.03, Z2[hb])
        _, x = ss.istft(Z2, SR, nperseg=nfft, noverlap=nfft - hop)
        out.append(x[: y.shape[1]])
    return np.array(out)


LAST_EQ = {}


def apply_curve(y, fc, gdb):
    ff = np.linspace(0, SR / 2, 4097)
    gg = np.interp(np.log2(np.clip(ff, 15, None)), np.log2(np.array(fc, float)), np.array(gdb, float))
    fir = ss.firwin2(4097, ff / (SR / 2), db2a(gg))
    return np.stack([ss.fftconvolve(y[c], fir)[2048:2048 + y.shape[1]] for c in range(y.shape[0])])


def match_eq(y, tgt_fc, tgt_db, C):
    fc = np.array(tgt_fc, float)
    td = np.array(tgt_db, float)
    if C.get("fixed_eq"):                       # analysis only: re-use a frozen match curve (single-note probes)
        return apply_curve(y, C["fixed_eq"][0], C["fixed_eq"][1])
    total = np.zeros(len(fc))
    sel = (fc >= C["match_fmin"]) & (fc <= C["match_fmax"])
    core = (fc >= 250) & (fc <= 4000)
    for _ in range(int(C["match_passes"])):
        L = third_oct_ltas(y.mean(0), fc)
        # normalise both on the 250-4000 energy (as olcum.py)
        Ln = L - 10 * np.log10(np.sum(10 ** (L[core] / 10)))
        Tn = td - 10 * np.log10(np.sum(10 ** (td[core] / 10)))
        g = np.where(sel, Tn - Ln, np.nan)
        gi = np.interp(np.log2(fc), np.log2(fc[sel]), g[sel])
        gi = np.clip(gi, -C["match_max_cut_db"], C["match_max_boost_db"])
        gs = np.convolve(np.r_[gi[0], gi, gi[-1]], [0.25, 0.5, 0.25], "valid")      # >= 1/3-octave smoothing
        y = apply_curve(y, fc, gs)
        total += gs
    LAST_EQ["fc"], LAST_EQ["db"] = fc.tolist(), total.tolist()
    return y


def k_weight(x):
    """ITU-R BS.1770 K-weighting at 44.1 kHz (pre-filter shelf + RLB high-pass, bilinear designs)"""
    fs = SR
    f0, G, Q = 1681.974450955533, 3.999843853973347, 0.7071752369554196
    K = math.tan(math.pi * f0 / fs)
    Vh = 10 ** (G / 20)
    Vb = Vh ** 0.4996667741545416
    a0 = 1 + K / Q + K * K
    b = [(Vh + Vb * K / Q + K * K) / a0, 2 * (K * K - Vh) / a0, (Vh - Vb * K / Q + K * K) / a0]
    a = [1, 2 * (K * K - 1) / a0, (1 - K / Q + K * K) / a0]
    y = ss.lfilter(b, a, x)
    f0, Q = 38.13547087602444, 0.5003270373238773
    K = math.tan(math.pi * f0 / fs)
    a0 = 1 + K / Q + K * K
    b = [1, -2, 1]
    a = [1, 2 * (K * K - 1) / a0, (1 - K / Q + K * K) / a0]
    return ss.lfilter(b, a, y)


def lufs(y):
    z = np.stack([k_weight(y[c]) for c in range(y.shape[0])])
    blk, hop = int(0.4 * SR), int(0.1 * SR)
    ms = []
    for s in range(0, z.shape[1] - blk + 1, hop):
        ms.append(np.sum(np.mean(z[:, s:s + blk] ** 2, axis=1)))
    ms = np.array(ms)
    lk = -0.691 + 10 * np.log10(ms + 1e-20)
    m1 = lk > -70
    if not m1.any():
        return -99.0
    rel = -0.691 + 10 * np.log10(np.mean(ms[m1])) - 10
    m2 = m1 & (lk > rel)
    return float(-0.691 + 10 * np.log10(np.mean(ms[m2])))


def true_peak_db(y):
    up = ss.resample_poly(y, 4, 1, axis=1)
    return float(20 * np.log10(np.max(np.abs(up)) + 1e-12))


def add_noises(y, C, seed):
    n = y.shape[1]
    rng = seeded(seed, "noise")
    t = np.arange(n) / SR
    m = np.zeros(n)
    for f, d in C["hum"]:
        m += db2a(d) * np.sin(2 * math.pi * f * t + rng.uniform(0, 2 * math.pi))
    if C.get("rumble_db") is not None:
        r = band_noise(rng, n, SR, (4, 20), math.sqrt(0.5) * db2a(C["rumble_db"]))
        m += r
    return y + m[None, :]


def chain(y, P, seed, T):
    C = P["chain"]
    y = apply_wow(y, C, seed)
    y = apply_room(y, C["room"], seed)
    sos = ss.butter(C["hpf_order"], C["hpf_hz"], "highpass", fs=SR, output="sos")
    y = ss.sosfiltfilt(sos, y, axis=1)
    if C.get("lpf_hz"):
        sos = ss.butter(C["lpf_order"], C["lpf_hz"], "lowpass", fs=SR, output="sos")
        y = ss.sosfiltfilt(sos, y, axis=1)
    y = transfer_noise(y, C, seed)
    tl = P["target_ltas"]
    y = match_eq(y, tl["fc"], tl["db"], C)
    # level (music only), then the measured hum / rumble floor, then re-check loudness
    g = db2a(C["lufs"] - lufs(y))
    y = y * g
    y = add_noises(y, C, seed)
    for _ in range(2):
        y = y * db2a(C["lufs"] - lufs(y))
    tp = true_peak_db(y)
    if tp > C["tp_max_db"]:
        y = soft_ceiling(y, C["tp_max_db"])
    return y


def soft_ceiling(y, ceil_db):
    """only used if a melody's peaks exceed the measured true-peak ceiling: gentle per-sample tanh knee"""
    c = db2a(ceil_db) * 0.97
    return c * np.tanh(y / c)


# --------------------------------------------------------------------------------------------------------- main
def deep_update(d, u):
    for k, v in u.items():
        if isinstance(v, dict) and isinstance(d.get(k), dict):
            deep_update(d[k], v)
        else:
            d[k] = v
    return d


def set_param(P, spec):
    key, val = spec.split("=", 1)
    try:
        v = json.loads(val)
    except Exception:
        v = val
    d = P
    parts = key.split(".")
    for p in parts[:-1]:
        d = d[int(p)] if isinstance(d, list) else d[p]
    last = parts[-1]
    if isinstance(d, list):
        d[int(last)] = v
    else:
        d[last] = v


def render(melody_path, seed=1, P=None, stems_dir=None, do_chain=True, quiet=False):
    if P is None:
        P = json.load(open(os.path.join(HERE, "params.json")))
    G = P["global"]
    sc = load_score(melody_path, G)
    ends = [n["t1"] for n in sc["notes"] + sc["counter"]] + [c["t1"] for c in sc["chords"]]
    T = min(G["max_len_s"], (max(ends) if ends else 4.0) + 0.4)
    n_total = int(round(T * SR))
    lead_inst = P["lead"]
    arch = phrase_arch(sc["notes"], G, T)
    lead = render_line(sc["notes"], lead_inst, lead_inst["reeds"], G, seed, n_total, sc["beat"],
                       ReedVoice(n_total, seed + 1), "lead", arch=arch)
    acc = render_acc(sc, P, G, seed, n_total, arch=arch)
    ctr = np.zeros((2, n_total))
    if sc["counter"]:
        ci = dict(lead_inst)
        ci.update({k: v for k, v in P["counter"].items() if k not in ("reeds", "level_db")})
        ctr = render_line(sc["counter"], ci, P["counter"]["reeds"], G, seed, n_total, sc["beat"],
                          ReedVoice(n_total, seed + 3), "counter", arch=arch)
    # stem balance by RMS where the lead plays (energy), measured relation acc = lead + level_db
    act = np.abs(lead).sum(0) > 1e-6 * (np.abs(lead).max() + 1e-12)
    def rms(x, m):
        return math.sqrt(float(np.mean(x[:, m] ** 2))) if m.any() else 0.0
    rl = rms(lead, act) if act.any() else 0.0
    ra = rms(acc, act if act.any() else np.ones(n_total, bool))
    g_acc = (db2a(P["acc"]["level_db"]) * rl / ra) if (rl > 0 and ra > 0) else (1.0 / max(ra, 1e-9) * 0.1)
    rc = rms(ctr, np.abs(ctr).sum(0) > 0) if sc["counter"] else 0.0
    g_ctr = db2a(P["counter"]["level_db"]) * rl / rc if (rc > 0 and rl > 0) else 0.0
    mix = lead + g_acc * acc + g_ctr * ctr
    if stems_dir:
        os.makedirs(stems_dir, exist_ok=True)
        for nm, s in (("lead", lead), ("acc", g_acc * acc), ("counter", g_ctr * ctr)):
            sf.write(os.path.join(stems_dir, nm + ".wav"), (s.T / (np.abs(mix).max() + 1e-9) * 0.5).astype(np.float32), SR)
    if not do_chain:
        y = mix / (np.abs(mix).max() + 1e-9) * 0.5
    else:
        y = chain(mix, P, seed, T)
    # end: all sound stops by end_by_s, short fade
    n_end = min(y.shape[1], int(G["end_by_s"] * SR))
    y = y[:, :n_end]
    nf = int(G["fade_s"] * SR)
    if n_end >= G["end_by_s"] * SR - 2 and nf > 0:
        y[:, -nf:] *= raised_cos(np.linspace(1, 0, nf))[None, :]
    if do_chain:                                    # final loudness after the end fade (gain only)
        y = y * db2a(P["chain"]["lufs"] - lufs(y))
        if true_peak_db(y) > P["chain"]["tp_max_db"]:
            y = soft_ceiling(y, P["chain"]["tp_max_db"])
    # pad to the clip length
    n_out = int(round(min(G["max_len_s"], T) * SR))
    if y.shape[1] < n_out:
        y = np.pad(y, ((0, 0), (0, n_out - y.shape[1])))
    if not quiet:
        print(json.dumps({"id": sc["id"], "len_s": round(y.shape[1] / SR, 3), "lufs": round(lufs(y), 2),
                          "true_peak_db": round(true_peak_db(y), 2), "notes": len(sc["notes"]),
                          "chords": len(sc["chords"]), "pattern": parse_pattern(sc["pattern"], P["acc"]["pattern_default"], sc["bpb"])[0]}))
    return y


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("melody")
    ap.add_argument("out")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--params", help="parameter JSON (default: params.json next to render.py)")
    ap.add_argument("--set", action="append", default=[], help="override, e.g. --set lead.breath_db=-26")
    ap.add_argument("--stems", help="write lead/acc/counter stems (pre-chain) here")
    ap.add_argument("--no-chain", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    P = json.load(open(a.params or os.path.join(HERE, "params.json")))
    for s in a.set:
        set_param(P, s)
    y = render(a.melody, a.seed, P, a.stems, not a.no_chain, a.quiet)
    sf.write(a.out, y.T.astype(np.float32), SR, subtype="FLOAT" if a.out.endswith(".wav") else None)


if __name__ == "__main__":
    main()
