#!/usr/bin/env python3
"""render.py -- sound engine "sf" for the signature-waltz project (sample-based, FluidR3 SoundFont).

    python3 render.py <melody.json> <out.wav> [--seed N] [--set key=value ...] [--stems DIR]

    --seed N      all random parts (intonation, wow, room, noise) come from N: same JSON + seed = same file (md5)
    --set k=v     override any CFG value, dotted path, JSON values (e.g. --set accomp.level_db=-4,
                  --set chain.grain.db=-14, --set 'lead.layers=[{"prog":22},{"prog":22,"gain_db":-4,"detune":"beat"}]')
    --stems DIR   also write the dry lead / accomp / counter stems
    A melody JSON may carry its own overrides in "engine": {...} (same structure as CFG) for per-video variation.

Input (BAGLAM.md format): tempo_bpm, pickup_beats, notes [{bar, beat, dur_beats, midi, vel, (bend, art)}],
chords [{bar, beat, dur_beats, midi[], (bass, pattern)}], accomp {pattern: text}, optional counter [same as notes].
  - bars may start at 0 or 1; the earliest event is placed at 0.00 s. A pickup with no chord under it gets the first
    chord extended back (the pa-pa of the opening bar).
  - accomp pattern text: default waltz (bass/oom on 1, chord/pah on 2-3, held inner tones). Tokens "B C C" / "B H H"
    / "R C C" set roles per beat (B bass, C chord swell, H held chord, R rest); keywords: staccato, legato/sustained,
    no bass, pedal/drone, no pad/dry.
  - note "bend": [[beat_offset, cents], ...] adds an explicit pitch bend; "art": "stacc" / "accent" / "phrase".

What it does (numbers are measured targets from analiz/tini.md, analiz/muzik.md, olcum/teshis.md and olcum.py):
  1. Performance, note by note, with real recorded FluidR3 samples (each note rendered alone, started 0.35-0.5 s into
     its sample, past FluidR3's +4-5 dB attack bloom, so the engine shapes every attack itself):
       lead     tini recipe R2: tango accordion P23 (2-reed musette sample) + harmonica P22 detuned +14 c at -3 dB.
                Equal-power legato crossfades (no level dip at note changes), 45 ms entrance rise, bellows swell inside
                long notes, phrase arch + contour dynamics (capped at 4 dB range), louder = brighter, per-note intonation
                (5 c) and slow wander, measured-style bends (falling scoop into each phrase's first note, a rising
                push on the climax, the final held note drifting sharp).
       accomp   oom-pah-pah derived from the chords. Beat 1: bass in C3-B3 with its octave (heard through its partials),
                0.30 s body then easing to a held floor, dark. Beats 2-3: 4-voice close, voice-led chord. Two-band
                envelopes: below 1 kHz a smooth bed, above 1 kHz a bright swell (-10 dB in 55 ms to -16 dB), per-beat
                brightness/fullness so beat 2 is fuller and beat 3 lighter ("u a a"). Held inner tones keep the bed
                continuous; the whole accompaniment follows the lead's phrase dynamics; pahs settle under the final
                held note. Per-key static mistuning of the reed set (9 c). Tango accordion P23.
       counter  optional second line (accordion P21) at -6 dB, legato like the lead.
  2. Lo-fi chain: mono mix -> pitch wow before the room (periodic ~0.5 Hz upward excursions of ~55 c, flat-topped,
     plus 9 c 1-12 Hz flutter; olcum's per-band pitch curves of the original wrap at +-50 c together every ~2 s)
     -> short decorrelated stereo room (early cluster 19 ms, RT60 0.06 s, wet -11.5 dB; fitted with olcum's
     side-from-mid estimator) -> signal-following noise fill at -10.5 dB per 1/3 octave, 220-3000 Hz (the original's
     dense inter-harmonic floor / flatness; codec-like) -> codec-like band edge at 4.8 kHz with an SBR-style replicated
     band above -> 1/3-octave long-term-spectrum match EQ toward the original's measured curve (3 passes, kernel
     [0.1,0.8,0.1], local prominence <= 10 dB) -> side/mid set to the measured -6.6 dB -> -29.5 LUFS (BS.1770)
     -> 100/150/200/250/50 Hz hum family and 4-20 Hz rumble at the measured dBFS -> rare-peak control so the true
     peak stays <= -17 dBTP (smooth, no limiter pumping) -> end fade so all sound stops by 13.74 s (shorter pieces end
     after their own release).

Deterministic for a given JSON + seed. Nothing from the original audio is used: only its measured numbers
(the LTAS target table below is a 1/3-octave smoothed long-term spectrum, allowed by rule 1).

Sound source licence: FluidR3_GM.sf2 by Frank Wen, MIT licence (Debian package fluid-soundfont-gm,
/usr/share/sounds/sf2/FluidR3_GM.sf2). No other samples; all noise, room and wow are synthesised here.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import sys

import numpy as np
import scipy.signal as ss
import soundfile as sf

SR = 44100
SF2 = "/usr/share/sounds/sf2/FluidR3_GM.sf2"

# --------------------------------------------------------------------------------------------- configuration
CFG = {
    "tuning_c": -15.0,                 # flat stretches; with the wow excursions olcum reads about -11 c like the original
    "jitter_ms": 5.0,                  # onset humanisation (original beat residual SD 21 ms incl. measurement noise)
    "lead": {
        # tini R2: tango accordion (2-reed musette sample) + harmonica detuned +14 c (odd-heavy, beating, bends well)
        "layers": [{"prog": 23, "bank": 0, "gain_db": 0.0, "detune": 0.0},
                   {"prog": 22, "bank": 0, "gain_db": -3.0, "detune": 14.0}],
        "beat_hz_c5": 6.7,             # musette beat at C5 (measured 6.7 Hz), scales with sqrt(f) -> 8.3 Hz @ Ab5
        "beat_exp": 0.5,
        "detune_jitter_c": 2.0,
        "intonation_c": 5.0,           # per-note random mistuning, both voices together
        "vel": 90,
        "vel_per_db": 3.0,             # louder phrase points get a higher velocity = brighter sample filter
        "attack_ms": 45.0,             # measured lead entrance rise 45 ms
        "xfade_ms": 50.0,              # legato crossfade (next note starts 30-60 ms before the previous releases)
        "release_ms": 110.0,
        "rearticulate_dip_db": -2.5,   # same pitch repeated legato: a small bellows re-push
        "swell_db": 1.2,               # bellows swell inside notes >= 0.5 s
        "arch_db": 2.0,                # phrase arch (peak at the phrase's highest note)
        "contour_db_per_st": 0.25,
        "downbeat_db": 0.4,
        "max_range_db": 4.0,           # cap on the lead's note-to-note dynamic range (phrase arch + contour + vel)
        "final_dim_db": -3.0,          # last note: diminuendo over its hold
        "scoop_c": -35.0,              # expressive scoop into a long note reached by an upward leap >= 5 st
        "scoop_ms": 110.0,
        "drift_c": 5.0, "drift_hz": 1.5,   # slow per-note pitch wander (free-reed player, bellows)
        "bends": {"entry_c": 60.0, "entry_ms": 250.0, "climax_c": 50.0, "climax_ms": 200.0, "climax_at": 0.35,
                  "final_c": 30.0, "final_s": 1.0},
        "gain_db": 0.0,
        "skip_s": 0.5,                 # start each sample past its attack bloom (FluidR3 P22: +4.6 dB at 0.1-0.2 s)
        "bright_per_db": 0.6,          # high-shelf (>1 kHz) dB per dB of phrase dynamics
        "key_tune_sd_c": 0.0,          # static per-key mistuning of the reed set
    },
    "counter": {
        "layers": [{"prog": 21, "bank": 0, "gain_db": 0.0, "detune": 0.0}],
        "level_db": -6.0,              # re lead energy
        "vel": 80,
    },
    "accomp": {
        "prog": 23, "bank": 0,         # tango accordion (2-reed musette sample, ~15 c)
        "level_db": -2.0,              # accompaniment energy re lead energy (measured: 1-6 dB below the lead)
        "oom_vel": 62, "oom_dur_s": 0.30, "oom_attack_ms": 35.0, "oom_octaves": [0, 12], "oom_db": -2.0,
        "oom_floor_db": -8.0, "oom_fall_s": 0.2,   # after the 0.30 s body the oom eases down to a held floor
        "bass_lo": 48,                 # bass in C3..B3: fundamentals 130-247 Hz fall under the band edge
        "pah_vel": 96, "pah_attack_ms": 45.0, "pah_top_split": False,
        "pah_fall_ms": 55.0, "pah_floor_db": -16.0,         # >1 kHz: -10 dB in 55 ms, floor -16 dB (measured)
        "pah_fall_lo_ms": 160.0, "pah_floor_lo_db": -6.0,   # <1 kHz: gentle, the bed stays continuous
        "voicing_lo": 58, "voicing_hi": 72, "pah_voices": 4,
        "pad_db": -17.0,               # held inner chord tones under the pahs (measured inner sustained D4/F4/G4)
        "pad_vel": 70,
        "xfade_ms": 40.0,
        "release_ms": 80.0,            # measured chord releases 60-80 ms
        "follow": 0.35,
        "final_calm": 0.6,            # pah swell depth under the lead's final held note (x of normal)                 # accompaniment follows the lead's phrase dynamics (dB per dB)
        "skip_s": 0.35,
        "oom_bright_db": -6.0,         # beat 1 dark (measured centroid ~1.07 kHz vs 1.61 kHz on beats 2-3)
        "pah_bright_db": [4.0, 5.0],   # extra >1 kHz gain at the pah swell peak, beat 2 / beat 3
        "pah_low_db": [-4.0, -7.0],    # <1 kHz gain on the pahs, beat 2 / beat 3 (original: beat 2 +3.7 dB at 250-500 Hz, beat 3 +0.8)
        "pad_bright_db": -3.0,
        "key_tune_sd_c": 9.0,          # accordion reed set: static per-key mistuning
    },
    "ensemble": {"hyper_db": 0.0, "bar_swell_db": 0.0},
    "chain": {
        "sat_drive": 0.0,              # tanh drive (0 = off)
        # fitted with olcum's side-from-mid estimator: early cluster ~16 ms, short decay, wet -11.5 dB (tools/roomfit.py)
        "room": {"rt60": 0.06, "pd_ms": 2.0, "build_ms": 4.0, "cluster_ms": 19.0, "cluster_w_ms": 8.0,
                 "tail_db": -40.0, "tail_rt": 1.2, "hp": 150.0, "lp": 3000.0, "wet_db": -11.5},
        "wow_pos": "pre",              # pitch movement before the room (fits the original's side-from-mid response)
        # periodic upward excursions ~every 2 s (muzik.json wow; olcum per-band curves wrap at +-50 c together)
        "wow": {"bump_c": 55.0, "bump_flat": 0.3, "bump_c_sd": 8.0, "bump_w_s": 0.7, "bump_w_sd": 0.15, "period_s": 2.0,
                "period_sd": 0.22, "first_s": 0.9, "drift_c": 4.0, "flutter_c": 9.0, "flutter_band": [1.0, 12.0]},
        # signal-following noise fill: noise-to-signal ratio per 1/3 octave (olcum floor/flatness of the original ~ -10 dB)
        "grain": {"db": -10.5, "nfft": 2048, "oct": 0.5, "corr": 0.8, "f_hi": 3000.0, "f_lo": 220.0},
        # codec-like band edge: real harmonics to ~4.7 kHz, noise-like replicated band above (tini: SBR above ~5 kHz)
        "sbr": {"on": True, "fx": 4800.0, "noise": 0.6, "db": -6.0},
        "side_mid_db": -6.6,           # measured side minus mid (L/R corr 0.64)
        "pre_hp_hz": 90.0,
        "match": {"on": True, "passes": 3, "fmin": 125.0, "fmax": 12500.0, "max_boost": 14.0, "max_cut": -30.0,
                  "strength": 1.0, "smooth": [0.1, 0.8, 0.1], "max_local_db": 10.0},
        "lp_hz": 12000.0,
        "hum": [[100.0, -70.4], [150.0, -78.3], [200.0, -83.5], [250.0, -83.5], [50.0, -87.3]],
        "rumble_db": -55.7,
        "hiss_db": None,
        "lufs": -29.5,
        "peak_db": -17.8,              # rare-peak control so true peak stays <= -17 dBTP (original -16.8)
        "fade_s": 0.25,
        "end_s": 13.74,
        "length_s": 13.77,
    },
}

# 1/3-octave long-term spectrum of the original's mid channel, dB re its loudest band (tini.json eq_curve).
LTAS_TARGET = [(20.0, -31.3), (25.0, -34.5), (31.5, -37.6), (40.0, -38.2), (50.0, -38.1), (63.0, -39.3), (80.0, -40.4),
               (100.0, -30.4), (125.0, -32.0), (160.0, -31.2), (200.0, -32.2), (250.0, -19.7), (315.0, -11.6),
               (400.0, -9.3), (500.0, -6.6), (630.0, -1.3), (800.0, -6.8), (1000.0, -10.2), (1250.0, -7.9),
               (1600.0, 0.0), (2000.0, -1.6), (2500.0, -4.7), (3150.0, -12.5), (4000.0, -15.2), (5000.0, -25.7),
               (6300.0, -34.7), (8000.0, -37.0), (10000.0, -39.5), (12500.0, -45.4), (16000.0, -55.9),
               (20000.0, -61.5)]


# ------------------------------------------------------------------------------------------------- helpers
def deep_update(d, u):
    for k, v in u.items():
        if isinstance(v, dict) and isinstance(d.get(k), dict):
            deep_update(d[k], v)
        else:
            d[k] = v
    return d


def set_path(d, path, value):
    keys = [int(k) if k.isdigit() else k for k in path.split(".")]
    for k in keys[:-1]:
        d = d[k] if isinstance(d, list) else d.setdefault(k, {})
    try:
        value = json.loads(value)
    except (json.JSONDecodeError, TypeError):
        pass
    d[keys[-1]] = value


def db2a(x):
    return 10.0 ** (x / 20.0)


def raised_cos(n):
    if n <= 0:
        return np.ones(0)
    return 0.5 - 0.5 * np.cos(np.pi * (np.arange(n) + 0.5) / n)


_HP = ss.butter(2, 1000.0, "highpass", fs=SR, output="sos")


def hp1k(x):
    """the part of x above ~1 kHz (for brightness shelving: x + (g - 1) * hp1k(x))"""
    return ss.sosfiltfilt(_HP, x) if len(x) > 30 else x * 0


_HPT = ss.butter(2, 2800.0, "highpass", fs=SR, output="sos")


def hp_top(x):
    return ss.sosfiltfilt(_HPT, x) if len(x) > 30 else x * 0


_LP = ss.butter(2, 500.0, "lowpass", fs=SR, output="sos")


def lp500(x):
    return ss.sosfiltfilt(_LP, x) if len(x) > 30 else x * 0


KEYTUNE = {"seed": 0}


def key_tune(midi, tag):
    """static per-key mistuning of an instrument (cents), like a real reed set; sd from CFG[tag]['key_tune_sd_c']"""
    sd = (CFG.get("lead" if tag == "lead" else "accomp") or {}).get("key_tune_sd_c", 0.0)
    if not sd:
        return 0.0
    return float(rng_for(KEYTUNE["seed"], "key", tag, int(midi)).normal(0, sd))


def rng_for(seed, *tags):
    h = hashlib.sha1(("%d|" % seed + "|".join(str(t) for t in tags)).encode()).digest()
    return np.random.default_rng(int.from_bytes(h[:8], "little"))


# ------------------------------------------------------------------------------------------- melody input
def load_melody(path):
    with open(path) as fh:
        J = json.load(fh)
    bpm = float(J.get("tempo_bpm", 152))
    bpb = int(J.get("beats_per_bar", 3))
    beat_s = 60.0 / bpm
    pick = float(J.get("pickup_beats", 0) or 0)

    def pos(bar, beat):
        return (float(bar) - 1.0) * bpb + (float(beat) - 1.0)

    def notes_of(lst):
        out = []
        for n in lst or []:
            if n.get("midi") is None:
                continue
            out.append({"p0": pos(n["bar"], n.get("beat", 1)), "dur": float(n.get("dur_beats", 1)),
                        "midi": int(n["midi"]), "vel": float(n.get("vel", 90)), "bend": n.get("bend"),
                        "art": n.get("art", "")})
        out.sort(key=lambda e: e["p0"])
        return out

    lead = notes_of(J.get("notes"))
    counter = notes_of(J.get("counter"))
    chords = []
    for c in J.get("chords") or []:
        chords.append({"p0": pos(c["bar"], c.get("beat", 1)), "dur": float(c.get("dur_beats", bpb)),
                       "midi": [int(m) for m in c["midi"]], "bass": c.get("bass"), "pattern": c.get("pattern")})
    chords.sort(key=lambda e: e["p0"])
    allp = [e["p0"] for e in lead + counter + chords]
    if not allp:
        raise SystemExit("melody has no notes or chords")
    p_first = min(allp)
    # pickup: if the composer wrote a pickup melody but the first chord starts later, extend the first chord back
    if chords and lead and pick > 0 and chords[0]["p0"] > p_first + 1e-6:
        c0 = dict(chords[0])
        c0["dur"] = chords[0]["p0"] - p_first
        c0["p0"] = p_first
        chords.insert(0, c0)
    acc = J.get("accomp") or {}
    if isinstance(acc, str):
        acc = {"pattern": acc}
    return {"id": J.get("id", os.path.basename(path)), "bpm": bpm, "bpb": bpb, "beat_s": beat_s, "p_first": p_first,
            "lead": lead, "counter": counter, "chords": chords, "accomp": acc, "engine": J.get("engine") or J.get("sf") or {},
            "raw": J}


def t_of(M, p):
    return (p - M["p_first"]) * M["beat_s"]


# ------------------------------------------------------------------------------------- FluidR3 note renderer
class Fluid:
    """One FluidSynth instance; renders single notes (dry, reverb/chorus off) with an optional pitch curve."""

    def __init__(self):
        import fluidsynth
        self.s = fluidsynth.Synth(gain=0.6, samplerate=float(SR),
                                  **{"synth.reverb.active": 0, "synth.chorus.active": 0, "synth.polyphony": 64})
        self.sfid = self.s.sfload(SF2)
        self.cache = {}
        self.cur = None

    def _prog(self, prog, bank):
        if self.cur != (prog, bank):
            self.s.program_select(0, self.sfid, bank, prog)
            self.cur = (prog, bank)
            for c, v in ((7, 127), (11, 127), (91, 0), (93, 0), (1, 0)):
                self.s.cc(0, c, v)

    def note(self, prog, bank, midi, vel, hold_s, cents, tail_s=0.25, skip_s=0.0):
        """cents: float (constant) or array of control points sampled every 64 samples (after the skip).
        skip_s: start playback this far into the note (past the sample's attack bloom); the engine shapes its own
        attack. Returns mono float64 of length ~ hold_s + tail_s."""
        const = np.isscalar(cents)
        key = (prog, bank, midi, int(vel), round(hold_s, 4), round(skip_s, 3), round(float(cents), 2) if const else
               hashlib.sha1(np.round(np.asarray(cents), 2).tobytes()).hexdigest())
        if key in self.cache:
            return self.cache[key]
        nsk = int(round(skip_s * SR / 64))
        if not const and nsk > 0:
            cents = np.r_[np.full(nsk, float(np.asarray(cents)[0])), np.asarray(cents, dtype=float)]
        hold_s = hold_s + nsk * 64 / SR
        self._prog(prog, bank)
        s = self.s
        def bend(c):
            return int(np.clip(round(c / 200.0 * 8192), -8192, 8191))
        n_hold = int(round(hold_s * SR))
        n_tail = int(round(tail_s * SR))
        blk = 64
        out = []
        if const:
            s.pitch_bend(0, bend(float(cents)))
            s.noteon(0, midi, int(np.clip(vel, 1, 127)))
            out.append(np.array(s.get_samples(n_hold), dtype=np.float64))
        else:
            cc = np.asarray(cents, dtype=float)
            s.pitch_bend(0, bend(cc[0]))
            s.noteon(0, midi, int(np.clip(vel, 1, 127)))
            done = 0
            k = 0
            while done < n_hold:
                m = min(blk, n_hold - done)
                s.pitch_bend(0, bend(cc[min(k, len(cc) - 1)]))
                out.append(np.array(s.get_samples(m), dtype=np.float64))
                done += m
                k += 1
        s.noteoff(0, midi)
        if n_tail > 0:
            out.append(np.array(s.get_samples(n_tail), dtype=np.float64))
        s.all_sounds_off(0)
        s.get_samples(2048)            # flush
        a = np.concatenate([o for o in out if len(o)]).reshape(-1, 2).mean(1) / 32768.0
        a = a[nsk * 64:]
        self.cache[key] = a
        return a


# -------------------------------------------------------------------------------------------- performance
def smooth_noise(rng, n_ctl, sd, fmax_hz, ctl_rate=SR / 64):
    """random slow wander: unit-sd noise low-passed at fmax_hz, scaled to sd cents, on the 64-sample control grid"""
    k = max(int(40 / max(fmax_hz, 0.1)), 1)
    need = int(n_ctl / ctl_rate * 40) + 4                    # 40 Hz grid
    m = max(need, 4 * k + 8)
    w = rng.standard_normal(m)
    w = np.convolve(w, np.hanning(2 * k + 1), "same")[:m]
    w = (w - w.mean()) / (w.std() + 1e-9) * sd
    return np.interp(np.arange(n_ctl) / ctl_rate, np.arange(m) / 40.0, w)


def musette_detune(f0, C):
    bh = C["beat_hz_c5"] * (f0 / 523.25) ** C["beat_exp"]
    return 1200.0 * math.log2(1.0 + bh / f0)


def midi_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)


def plan_line(M, notes, C, seed, tag):
    """Turn a note list into performance events with times, gains, bend curves and envelope flags."""
    rng = rng_for(seed, tag, "line")
    bs = M["beat_s"]
    ev = []
    if not notes:
        return ev
    # phrase segmentation: gaps >= 0.5 beat or explicit art 'phrase'
    phrases, cur = [], [0]
    for i in range(1, len(notes)):
        prev = notes[i - 1]
        gap = notes[i]["p0"] - (prev["p0"] + prev["dur"])
        if gap >= 0.5 or "phrase" in str(notes[i].get("art", "")):
            phrases.append(cur)
            cur = []
        cur.append(i)
    phrases.append(cur)
    mean_pitch = float(np.mean([n["midi"] for n in notes]))
    gains = np.zeros(len(notes))
    for ph in phrases:
        pitches = [notes[i]["midi"] for i in ph]
        imax = ph[int(np.argmax(pitches))]
        t0 = notes[ph[0]]["p0"]
        tm = notes[imax]["p0"]
        t1 = notes[ph[-1]]["p0"] + notes[ph[-1]]["dur"]
        for i in ph:
            p = notes[i]["p0"]
            if p <= tm:
                x = (p - t0) / max(tm - t0, 1e-6)
                a = 0.5 - 0.5 * math.cos(math.pi * x) if tm > t0 else 1.0
            else:
                x = (p - tm) / max(t1 - tm, 1e-6)
                a = 0.5 + 0.5 * math.cos(math.pi * x)
            gains[i] += C.get("arch_db", 0) * (a - 0.5)
    for i, n in enumerate(notes):
        gains[i] += C.get("contour_db_per_st", 0) * (n["midi"] - mean_pitch)
        beat_in_bar = (n["p0"] % M["bpb"])
        if abs(beat_in_bar) < 1e-3:
            gains[i] += C.get("downbeat_db", 0)
        gains[i] += 20 * math.log10(max(n["vel"], 1) / 90.0) * 0.5
        if "accent" in str(n.get("art", "")):
            gains[i] += 2.0
    auto_bends = {"entry": {ph[0] for ph in phrases}, "climax": set()}
    longs = [i for i in range(len(notes)) if notes[i]["dur"] >= 1.5]
    if longs:
        hi = max(notes[i]["midi"] for i in longs)
        auto_bends["climax"] = {min(i for i in longs if notes[i]["midi"] == hi)}
    rmax = C.get("max_range_db")
    if rmax and len(gains) > 1 and np.ptp(gains) > rmax:
        # keep the macro-dynamics in the measured range (original LRA 3.6 LU) whatever the melody's span
        gains = np.mean(gains) + (gains - np.mean(gains)) * (rmax / np.ptp(gains))
    for i, n in enumerate(notes):
        t0 = t_of(M, n["p0"]) + rng.normal(0, CFG["jitter_ms"] / 1000.0) * (0 if i == 0 and n["p0"] == M["p_first"] else 1)
        t0 = max(t0, 0.0)
        t1 = t_of(M, n["p0"] + n["dur"])
        stacc = "stacc" in str(n.get("art", ""))
        if stacc:
            t1 = t0 + 0.5 * (t1 - t0)
        nxt = notes[i + 1] if i + 1 < len(notes) else None
        prv = notes[i - 1] if i > 0 else None
        legato_next = (nxt is not None and not stacc and nxt["p0"] - (n["p0"] + n["dur"]) < 0.26)
        legato_prev = (prv is not None and "stacc" not in str(prv.get("art", "")) and
                       n["p0"] - (prv["p0"] + prv["dur"]) < 0.26)
        if legato_next:
            t1 = max(t1, t_of(M, nxt["p0"]))      # tie the end to the next onset (crossfade added later)
        dur_s = t1 - t0
        # pitch curve (cents re the tuned pitch), at 64-sample control rate: per-note intonation + slow wander +
        # measured-style bends (entrance scoop, climax push, final drift) + explicit JSON bends
        nctl = int(math.ceil((dur_s + 0.4) * SR / 64)) + 2
        tc = np.arange(nctl) * 64 / SR
        curve = np.zeros(nctl) + rng.normal(0, C.get("intonation_c", 0))
        if C.get("drift_c"):
            curve += smooth_noise(rng, nctl, C["drift_c"], C.get("drift_hz", 2.0))
        sc = C.get("scoop_c", 0)
        if sc and prv is not None and n["midi"] - prv["midi"] >= 5 and n["dur"] >= 1.5:
            w = C.get("scoop_ms", 100) / 1000.0
            curve += sc * np.clip(1 - tc / w, 0, 1) ** 2
        B = C.get("bends") or {}
        if B:
            if i in auto_bends.get("entry", ()) and n["dur"] >= 1.0:
                # falling scoop into the first melody note (measured -77 c over 0.25 s at the lead entrance)
                w = B.get("entry_ms", 250) / 1000.0
                curve += B.get("entry_c", 60) * (1 + rng.normal(0, 0.15)) * np.clip(1 - tc / w, 0, 1) ** 1.5
            if i in auto_bends.get("climax", ()):
                # rising push on the climax note that then holds (measured +69 c over 0.2 s)
                ts = min(B.get("climax_at", 0.35) * dur_s, 0.5)
                w = B.get("climax_ms", 200) / 1000.0
                curve += B.get("climax_c", 50) * (1 + rng.normal(0, 0.15)) * (0.5 - 0.5 * np.cos(np.pi * np.clip((tc - ts) / w, 0, 1)))
            if nxt is None and dur_s > 1.0:
                # held final note drifts sharp (measured +44 c over its last ~0.8 s)
                ts = max(0.3, dur_s - B.get("final_s", 1.0))
                curve += B.get("final_c", 30) * np.clip((tc - ts) / max(dur_s - ts, 0.2), 0, 1) ** 1.5
        if n.get("bend"):
            # bend: [[beat_offset, cents], ...] linear segments within the note
            pts = np.array(n["bend"], dtype=float)
            curve += np.interp(tc, pts[:, 0] * bs, pts[:, 1])
        # in-note bellows swell / final diminuendo (dB curve, evaluated later on the sample grid)
        ev.append({"t0": t0, "t1": t1, "midi": n["midi"], "gain_db": gains[i], "curve": curve,
                   "legato_prev": legato_prev, "legato_next": legato_next,
                   "same_prev": bool(legato_prev and prv["midi"] == n["midi"]),
                   "last": nxt is None, "vel": n["vel"]})
    return ev


def env_for(e, n, C, is_final):
    """amplitude envelope (length n samples, starting at e['t0'])."""
    t = np.arange(n) / SR
    dur = e["t1"] - e["t0"]
    env = np.ones(n)
    xf = C["xfade_ms"] / 1000.0
    # onset
    if e["legato_prev"]:
        k = int(xf * SR)
        if e["same_prev"]:
            k = int(0.025 * SR)
        r = np.sin(0.5 * np.pi * np.clip(t / (k / SR), 0, 1)) if k > 0 else np.ones(n)
        env *= r
    else:
        k = int(C["attack_ms"] / 1000.0 * SR)
        env[:k] *= raised_cos(k)[:n]
    # offset
    if e["legato_next"]:
        k = int(xf * SR)
        i0 = int(dur * SR)
        seg = np.cos(0.5 * np.pi * np.clip((t - dur) / xf, 0, 1))
        env *= np.where(t >= dur, seg, 1.0)
    else:
        rel = C["release_ms"] / 1000.0
        seg = 0.5 + 0.5 * np.cos(np.pi * np.clip((t - dur) / rel, 0, 1))
        env *= np.where(t >= dur, seg, 1.0)
    # dynamics inside the note
    gdb = np.zeros(n)
    if dur >= 0.5 and C.get("swell_db", 0):
        tp = min(0.35 * dur, 0.45)
        x = np.clip(t / tp, 0, 1)
        up = 0.5 - 0.5 * np.cos(np.pi * x)
        down = np.clip((t - tp) / max(dur - tp, 1e-3), 0, 1)
        gdb += C["swell_db"] * np.where(t < tp, up, 1 - 0.8 * down)
    if is_final and C.get("final_dim_db", 0):
        gdb += C["final_dim_db"] * np.clip((t - 0.25) / max(dur - 0.25, 0.2), 0, 1)
    if e.get("same_prev") and C.get("rearticulate_dip_db"):
        gdb += C["rearticulate_dip_db"] * np.clip(1 - t / 0.06, 0, 1)
    return env * db2a(gdb)


def render_line(F, M, ev, C, n_total, seed, tag):
    rng = rng_for(seed, tag, "voices")
    out = np.zeros(n_total)
    xf = C["xfade_ms"] / 1000.0
    for e in ev:
        f0 = midi_hz(e["midi"])
        dur = e["t1"] - e["t0"]
        tail = xf if e["legato_next"] else C["release_ms"] / 1000.0
        n = int((dur + tail) * SR)
        env = env_for(e, n, C, e["last"])
        vel = np.clip(C["vel"] + (e["vel"] - 90) * 0.5 + C.get("vel_per_db", 0) * e["gain_db"], 30, 127)
        sig = np.zeros(n)
        for L in C["layers"]:
            det = L.get("detune", 0.0)
            if det == "beat":
                det = musette_detune(f0, C) + rng.normal(0, C.get("detune_jitter_c", 0))
            base = CFG["tuning_c"] + float(det) + key_tune(e["midi"], "lead")
            curve = e["curve"] + base
            if np.ptp(curve) < 0.05:
                curve = float(curve[0])
            x = F.note(L["prog"], L.get("bank", 0), e["midi"], vel, dur + tail, curve, tail_s=0.05,
                       skip_s=C.get("skip_s", 0.0))
            m = min(n, len(x))
            sig[:m] += x[:m] * db2a(L.get("gain_db", 0.0))
        if C.get("bright_per_db"):
            # louder = brighter (FluidR3 velocity does not move the filter): static high shelf per note
            sig = sig + (db2a(C["bright_per_db"] * e["gain_db"]) - 1.0) * hp1k(sig)
        sig *= env * db2a(e["gain_db"] + C.get("gain_db", 0.0))
        i0 = int(round(e["t0"] * SR))
        i1 = min(n_total, i0 + n)
        out[i0:i1] += sig[:i1 - i0]
    return out


# ------------------------------------------------------------------------------------------ accompaniment
def parse_pattern(text, bpb):
    """Accomp pattern text -> per-beat roles and style flags.
    Tokens 'B C C' (B bass/oom, C chord/pah, H held chord, R rest, P pedal) map to beats; otherwise keywords:
    'staccato', 'legato'/'sustained', 'no bass', 'pedal'/'drone', 'no pad', 'arpeggio'."""
    t = (text or "").lower()
    st = {"roles": ["B"] + ["C"] * (bpb - 1), "legato": True, "staccato": False, "pad": True, "pedal": False,
          "arp": False}
    toks = t.replace(",", " ").split()
    if toks and all(tok.rstrip("._") in ("b", "c", "h", "r", "p") for tok in toks):
        st["roles"] = [tok.rstrip("._").upper() for tok in toks][:bpb] + ["R"] * max(0, bpb - len(toks))
    if "staccato" in t or "detached" in t:
        st["staccato"], st["legato"] = True, False
    if "no bass" in t or "without bass" in t:
        st["roles"] = ["C" if r == "B" else r for r in st["roles"]]
    if "pedal" in t or "drone" in t:
        st["pedal"] = True
    if "no pad" in t or "dry" in t:
        st["pad"] = False
    if "arpegg" in t or "broken" in t:
        st["arp"] = True
    return st


def voicing(pcs, prev, lo, hi):
    """close-position voicing of pitch classes within [lo, hi], nearest to prev (voice leading)."""
    pcs = sorted(set(p % 12 for p in pcs))
    cands = []
    for base in range(lo - 12, hi + 1):
        if base % 12 not in pcs:
            continue
        v = [base]
        for p in pcs:
            if p == base % 12:
                continue
            m = base + ((p - base) % 12)
            v.append(m)
        v = sorted(v)
        if v[0] >= lo and v[-1] <= hi:
            cands.append(v)
    if not cands:
        v = sorted(lo + ((p - lo) % 12) for p in pcs)
        return v
    if prev is None:
        return min(cands, key=lambda v: abs(np.mean(v) - 64.5))
    return min(cands, key=lambda v: sum(min(abs(a - b) for b in prev) for a in v) + 0.1 * abs(np.mean(v) - 64.5))


def plan_accomp(M, seed):
    A = CFG["accomp"]
    rng = rng_for(seed, "acc")
    st = parse_pattern(M["accomp"].get("pattern", ""), M["bpb"])
    for k in ("legato", "staccato", "pad", "pedal"):
        if k in M["accomp"]:
            st[k] = M["accomp"][k]
    bs = M["beat_s"]
    ev = []      # dict(t0, t1, midis, kind)
    prev_v = None
    for c in M["chords"]:
        pcs = c["midi"]
        bass = c["bass"] if c.get("bass") is not None else min(pcs)
        bass = A["bass_lo"] + ((bass - A["bass_lo"]) % 12)
        v = voicing(pcs, prev_v, A["voicing_lo"], A["voicing_hi"])
        prev_v = v
        vp = list(v)
        pcl = sorted(set(p % 12 for p in pcs))
        while len(vp) < int(A.get("pah_voices", 3)):
            # extend upward with the next chord tones (the original's pah tops reach Eb5/F5)
            top = vp[-1]
            nxt_up = min(top + ((pc - top) % 12 or 12) for pc in pcl)
            vp.append(nxt_up)
        roles = st["roles"]
        if c.get("pattern"):
            roles = parse_pattern(c["pattern"], M["bpb"])["roles"]
        nb = int(round(c["dur"]))
        for j in range(nb):
            p = c["p0"] + j
            bib = int(round(p)) % M["bpb"]
            role = roles[bib] if bib < len(roles) else "C"
            t0 = t_of(M, p) + rng.normal(0, CFG["jitter_ms"] / 1000.0)
            t0 = max(0.0, t0) if p > M["p_first"] + 1e-6 else 0.0
            t1 = t_of(M, p + 1)
            if role == "B":
                ev.append({"t0": t0, "t1": t1, "midis": [bass + o for o in A["oom_octaves"]], "kind": "oom"})
            elif role in ("C", "H"):
                ev.append({"t0": t0, "t1": t1, "midis": vp, "kind": "pah" if role == "C" else "hold", "bib": bib})
        if st["pad"]:
            # inner held tones: the chord's two lowest voicing notes, held for the chord duration
            ev.append({"t0": t_of(M, c["p0"]) if c["p0"] > M["p_first"] + 1e-6 else 0.0,
                       "t1": t_of(M, c["p0"] + c["dur"]), "midis": v[:2], "kind": "pad"})
        if st["pedal"]:
            ev.append({"t0": t_of(M, c["p0"]), "t1": t_of(M, c["p0"] + c["dur"]), "midis": [bass + 12],
                       "kind": "pad"})
    return ev, st


def acc_layers(A):
    return A.get("layers") or [{"prog": A["prog"], "bank": A.get("bank", 0), "gain_db": 0.0}]


def render_accomp(F, M, ev, st, n_total, calm_from=None):
    A = CFG["accomp"]
    out = np.zeros(n_total)
    xf = A["xfade_ms"] / 1000.0
    rel = A["release_ms"] / 1000.0
    pads = [e for e in ev if e["kind"] == "pad"]
    beats = [e for e in ev if e["kind"] != "pad"]
    beats.sort(key=lambda e: e["t0"])
    for i, e in enumerate(beats):
        nxt = beats[i + 1] if i + 1 < len(beats) else None
        cont = st["legato"] and nxt is not None and nxt["t0"] - e["t1"] < 0.05
        end = nxt["t0"] if (cont and nxt is not None) else e["t1"]
        dur = max(end - e["t0"], 0.05)
        if st["staccato"]:
            dur = min(dur, 0.16)
            cont = False
        tail = xf if cont else rel
        n = int((dur + tail) * SR)
        t = np.arange(n) / SR
        # two-band envelopes: below ~1 kHz the bed stays smooth (the original's 250-1000 Hz envelopes have little
        # 4-8 Hz modulation), above ~1 kHz the pahs swell bright (3rd harmonics +15 dB, 120-150 ms swells)
        def per_beat(v):
            if isinstance(v, (list, tuple)):
                return v[min(max(e.get("bib", 1), 1) - 1, len(v) - 1)]
            return v
        if e["kind"] == "oom":
            vel, k_att = A["oom_vel"], A["oom_attack_ms"] / 1000.0
            body = A["oom_dur_s"]
            lo = np.where(t < body, 0.0, (A["oom_floor_db"]) * np.clip((t - body) / A["oom_fall_s"], 0, 1))
            hi = lo + A["oom_bright_db"]
            g = A["oom_db"]
        elif e["kind"] == "pah":
            vel, k_att = A["pah_vel"], A["pah_attack_ms"] / 1000.0
            # under the lead's final held note the pahs settle (original: +3 dB swells there vs +8-12 dB elsewhere)
            calm = A.get("final_calm", 1.0) if (calm_from is not None and e["t0"] >= calm_from) else 1.0
            x_ = np.clip(t - k_att, 0, None)
            lo = np.maximum(-10.0 * x_ / (A["pah_fall_lo_ms"] / 1000.0), A["pah_floor_lo_db"] * calm) + per_beat(A["pah_low_db"])
            hi = np.maximum(-10.0 * x_ / (A["pah_fall_ms"] / 1000.0), A["pah_floor_db"] * calm)
            hi = hi + calm * per_beat(A["pah_bright_db"]) * np.clip(1 - hi / min(A["pah_floor_db"] * calm, -1e-3), 0, 1)
            g = 0.0
        else:
            vel, k_att = A["pah_vel"], A["pah_attack_ms"] / 1000.0
            lo = np.full(n, A["pah_floor_lo_db"])
            hi = np.full(n, A["pah_floor_db"] * 0.5)
            g = 0.0
        env = np.ones(n)
        ka = int(k_att * SR)
        env[:ka] *= raised_cos(ka)[:min(ka, n)]
        if cont:
            env *= np.where(t >= dur, np.cos(0.5 * np.pi * np.clip((t - dur) / xf, 0, 1)), 1.0)
        else:
            env *= np.where(t >= dur, 0.5 + 0.5 * np.cos(np.pi * np.clip((t - dur) / rel, 0, 1)), 1.0)
        sig = np.zeros(n)
        for L in acc_layers(A):
            for m in e["midis"]:
                x = F.note(L["prog"], L.get("bank", 0), m, vel, dur + tail,
                           CFG["tuning_c"] + A.get("tune_offset_c", 0.0) + key_tune(m, "acc") + L.get("detune", 0.0),
                           tail_s=0.05, skip_s=A["skip_s"])
                k = min(n, len(x))
                sig[:k] += x[:k] * db2a(L.get("gain_db", 0.0))
        sh = hp1k(sig)
        top = hp_top(sig) if A.get("pah_top_split") else np.zeros(n)   # optional: > 2.8 kHz follows the bed
        sh = sh - top
        lo_a = db2a(lo)
        if e["kind"] == "pah" and A.get("pah_attack_lo_ms"):
            kl = int(A["pah_attack_lo_ms"] / 1000.0 * SR)          # the low part rises more slowly (smooth bed)
            lo_a[:kl] *= raised_cos(kl)[:min(kl, n)] ** 0.5
        sig = (sig - sh - top) * lo_a + sh * db2a(hi) + top * db2a(0.5 * (lo + hi))
        i0 = int(round(e["t0"] * SR))
        i1 = min(n_total, i0 + n)
        out[i0:i1] += (sig * env * db2a(g))[:i1 - i0]
    # pads
    for e in pads:
        dur = e["t1"] - e["t0"]
        n = int((dur + xf) * SR)
        t = np.arange(n) / SR
        env = np.ones(n)
        ka = int(0.06 * SR)
        env[:ka] *= np.sin(0.5 * np.pi * np.clip(np.arange(ka) / ka, 0, 1))
        env *= np.where(t >= dur, np.cos(0.5 * np.pi * np.clip((t - dur) / xf, 0, 1)), 1.0)
        sig = np.zeros(n)
        for L in acc_layers(A):
            for m in e["midis"]:
                x = F.note(L["prog"], L.get("bank", 0), m, A["pad_vel"], dur + xf,
                           CFG["tuning_c"] + A.get("tune_offset_c", 0.0) + key_tune(m, "acc") + L.get("detune", 0.0),
                           tail_s=0.05, skip_s=A["skip_s"])
                k = min(n, len(x))
                sig[:k] += x[:k] * db2a(L.get("gain_db", 0.0))
        sig = sig + (db2a(A["pad_bright_db"]) - 1.0) * hp1k(sig)
        i0 = int(round(e["t0"] * SR))
        i1 = min(n_total, i0 + n)
        out[i0:i1] += (sig * env * db2a(A["pad_db"]))[:i1 - i0]
    return out


# ------------------------------------------------------------------------------------------------- chain
def room_ir(R, seed):
    rng = rng_for(seed, "room")
    n = int(1.6 * SR)
    t = np.arange(n) / SR
    pd = R["pd_ms"] / 1000.0
    tt = np.clip(t - pd, 0, None)
    on = (t > pd).astype(float)
    e1 = on * (1 - np.exp(-tt / (R["build_ms"] / 1000.0 + 1e-9))) * np.exp(-6.91 * tt / R["rt60"])
    if R.get("cluster_ms"):
        # early-reflection cluster (Gaussian energy bump) + diffuse decay after it
        c, w = R["cluster_ms"] / 1000.0, R.get("cluster_w_ms", 8.0) / 1000.0
        bump = np.exp(-0.5 * ((t - c) / w) ** 2)
        e1 = np.maximum(bump, (t > c) * np.exp(-6.91 * np.clip(t - c, 0, None) / R["rt60"])) * on
    e2 = on * (1 - np.exp(-tt / 0.02)) * np.exp(-6.91 * tt / R["tail_rt"]) * db2a(R["tail_db"])
    sos = ss.butter(2, [R["hp"], R["lp"]], "bandpass", fs=SR, output="sos")
    h = []
    for ch in range(2):
        x = rng.standard_normal(n) * e1 + rng.standard_normal(n) * e2
        x = ss.sosfilt(sos, x)
        h.append(x / np.sqrt(np.sum(x ** 2)))
    return np.stack(h, 1)


def apply_room(x, R, seed):
    h = room_ir(R, seed)
    g = db2a(R["wet_db"])
    n = len(x)
    L = ss.fftconvolve(x, h[:, 0])[:n]
    Rr = ss.fftconvolve(x, h[:, 1])[:n]
    return np.stack([x + g * L, x + g * Rr], 1)


def wow_curve(n, W, seed):
    """cents vs sample: slow upward excursions (~every 2 s, 0.3-0.8 s wide) + slow drift + 0.8-5 Hz flutter."""
    rng = rng_for(seed, "wow")
    fs_c = 1000.0
    nc = int(n / SR * fs_c) + 2
    tc = np.arange(nc) / fs_c
    c = np.zeros(nc)
    tk = W["first_s"] + rng.uniform(-0.3, 0.3)
    while tk < tc[-1] + 1.0:
        h = max(0.0, W["bump_c"] + rng.normal(0, W["bump_c_sd"]))
        w = float(np.clip(W["bump_w_s"] + rng.normal(0, W["bump_w_sd"]), 0.25, 0.9))
        flat = float(W.get("bump_flat", 0.0))     # plateau share of the excursion
        r = w * (1 - flat) * rng.uniform(0.4, 0.6)
        f = w * (1 - flat) - r
        x = tc - tk
        up = np.clip((x + r) / max(r, 1e-3), 0, 1)
        dn = np.clip(1 - (x - flat * w) / max(f, 1e-3), 0, 1)
        shape = np.where(x < 0, 0.5 - 0.5 * np.cos(np.pi * up),
                         np.where(x < flat * w, 1.0, 0.5 - 0.5 * np.cos(np.pi * dn)))
        c += h * shape
        tk += W["period_s"] + rng.normal(0, W["period_sd"])
    if W.get("drift_c"):
        d = rng.standard_normal(nc)
        d = ss.sosfiltfilt(ss.butter(2, 0.4, fs=fs_c, output="sos"), d)
        c += d / (np.std(d) + 1e-12) * W["drift_c"]
    if W.get("flutter_c"):
        f = rng.standard_normal(nc)
        f = ss.sosfiltfilt(ss.butter(2, W["flutter_band"], "bandpass", fs=fs_c, output="sos"), f)
        c += f / (np.std(f) + 1e-12) * W["flutter_c"]
    c -= np.median(c)                           # flat stretches sit at the tuned pitch
    return np.interp(np.arange(n) / SR, tc, c)


def apply_wow(y, W, seed):
    n = len(y)
    cents = wow_curve(n, W, seed)
    ratio = 2.0 ** (cents / 1200.0)
    pos = np.cumsum(ratio)
    pos -= pos[0]
    pos = np.clip(pos, 0, n - 1)
    idx = np.arange(n)
    return np.stack([np.interp(pos, idx, y[:, ch]) for ch in range(y.shape[1])], 1), cents


TO = np.array([20, 25, 31.5, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000,
               2500, 3150, 4000, 5000, 6300, 8000, 10000, 12500, 16000, 20000], dtype=float)


def third_oct(x):
    n, hop = 8192, 2048
    w = np.hanning(n)
    if len(x) < n:
        x = np.pad(x, (0, n - len(x)))
    fr = np.fft.rfftfreq(n, 1 / SR)
    frames = np.lib.stride_tricks.sliding_window_view(x, n)[::hop]
    F = np.abs(np.fft.rfft(frames * w, axis=1)) ** 2 * 2 / (n * np.sum(w ** 2))
    out = []
    for fc in TO:
        m = (fr >= fc / 2 ** (1 / 6)) & (fr < fc * 2 ** (1 / 6))
        out.append(F[:, m].sum(1).mean() if m.any() else np.nan)
    return 10 * np.log10(np.array(out) / 0.5 + 1e-20)


def grain(y, G, seed):
    """signal-following noise fill (emulates the dense inter-harmonic floor of a worn, low-bit-rate transfer):
    per STFT frame, noise with the 1/3-octave-smoothed power envelope of the signal, G['db'] below it."""
    if G is None or G.get("db") is None:
        return y
    rng = rng_for(seed, "grain")
    n = int(G.get("nfft", 2048))
    hop = n // 4
    f = np.fft.rfftfreq(n, 1 / SR)
    # smoothing kernel in log-frequency: average power over +-1/6 octave around each bin
    lo = np.searchsorted(f, f * 2 ** (-G.get("oct", 1 / 3) / 2))
    hi = np.searchsorted(f, f * 2 ** (G.get("oct", 1 / 3) / 2)) + 1
    w = np.hanning(n)
    out = np.zeros_like(y)
    norm = np.zeros(len(y) + n)
    g = db2a(G["db"] + 9.4)        # +9.4 dB: measured OLA/window loss, so G['db'] is the real noise-to-signal ratio
    # band limits: the original's floor is dense up to ~3.2 kHz and clean in the 4 kHz band (codec band edge)
    fw = np.clip((G.get("f_hi", 3300.0) * 1.25 - f) / (G.get("f_hi", 3300.0) * 0.25), 0, 1)
    fw *= np.clip((f - 0.7 * G.get("f_lo", 220.0)) / (0.3 * G.get("f_lo", 220.0)), 0, 1)
    g = g * fw
    mono = y.mean(1)
    pad = np.r_[mono, np.zeros(n)]
    ts = int(G.get("tsmooth", 0))
    Pprev = []
    for i in range(0, len(mono), hop):
        fr = pad[i:i + n] * w
        X = np.fft.rfft(fr)
        P = np.abs(X) ** 2
        if ts:
            Pprev.append(P)
            Pprev = Pprev[-(ts + 1):]
            P = np.mean(Pprev, 0)
        cs = np.r_[0, np.cumsum(P)]
        Ps = (cs[np.minimum(hi, len(P))] - cs[lo]) / np.maximum(np.minimum(hi, len(P)) - lo, 1)
        for ch in range(y.shape[1]):
            ph = rng.uniform(0, 2 * np.pi, len(P))
            N = np.sqrt(Ps) * g * np.exp(1j * ph)
            z = np.fft.irfft(N, n) * w
            seg = out[i:i + n, ch]
            seg += z[:len(seg)]
        norm[i:i + n] += w ** 2
    out /= np.maximum(norm[:len(y), None], 1e-3)
    c = float(G.get("corr", 0.8))                 # L/R correlation of the grain
    m = (out[:, 0] + out[:, 1]) / 2
    sd = (out[:, 0] - out[:, 1]) / 2
    k = math.sqrt(max(1 - c, 0) / max(1 + c, 1e-6))
    out = np.stack([m + k * sd, m - k * sd], 1)
    return y + out


def sbr(y, S, seed):
    """codec-like band edge: steep low-pass of the core at S['fx'], then the band [fx/2, fx] is shifted up by fx/2 and
    by fx (single-sideband) and partly replaced by envelope-following noise, as spectral band replication does.
    The match EQ that follows sets its level to the measured long-term spectrum."""
    if not S or not S.get("on"):
        return y
    rng = rng_for(seed, "sbr")
    fx = float(S["fx"])
    core = ss.sosfiltfilt(ss.butter(12, fx, "lowpass", fs=SR, output="sos"), y, axis=0)
    src = ss.sosfiltfilt(ss.butter(6, [fx / 2, fx * 0.98], "bandpass", fs=SR, output="sos"), core, axis=0)
    t = np.arange(len(y)) / SR
    hf = np.zeros_like(y)
    an = ss.hilbert(src, axis=0)
    env_sos = ss.butter(2, 60.0, "lowpass", fs=SR, output="sos")
    for k, shift in enumerate((fx / 2, fx)):
        sh = np.real(an * np.exp(2j * np.pi * shift * t)[:, None])
        # envelope-following noise in the same band
        env = ss.sosfiltfilt(env_sos, np.abs(an), axis=0)
        lo, hi = fx / 2 + shift, min(fx + shift, SR / 2 * 0.95)
        nz = ss.sosfiltfilt(ss.butter(4, [lo, hi], "bandpass", fs=SR, output="sos"), rng.standard_normal(y.shape), axis=0)
        nz = nz / (np.std(nz) + 1e-12) * env * 1.0
        m = float(S.get("noise", 0.5))
        hf += (1 - m) ** 0.5 * sh + m ** 0.5 * nz * (np.std(sh) / (np.std(nz) + 1e-12))
    hf = ss.sosfiltfilt(ss.butter(8, fx * 1.02, "highpass", fs=SR, output="sos"), hf, axis=0)
    return core + db2a(S.get("db", -6.0)) * hf


def match_eq(y, Mc):
    tgt = np.array([v for f, v in LTAS_TARGET])
    sel = (TO >= Mc["fmin"]) & (TO <= Mc["fmax"])
    core = (TO >= 250) & (TO <= 4000)
    total = np.zeros(len(TO))
    for _ in range(int(Mc["passes"])):
        L = third_oct(y.mean(1))
        # level-normalise on 250-4000 energy
        off = 10 * np.log10(np.sum(10 ** (tgt[core] / 10)) / np.sum(10 ** (L[core] / 10)))
        g = (tgt - (L + off)) * Mc.get("strength", 1.0)
        g = np.where(sel, g, np.nan)
        gi = np.interp(np.log2(TO), np.log2(TO[sel]), g[sel])
        gi = np.clip(gi, Mc["max_cut"] - total, Mc["max_boost"] - total)
        gs = np.convolve(np.r_[gi[0], gi, gi[-1]], Mc.get("smooth", [0.25, 0.5, 0.25]), "valid")   # >= 1/3-octave smoothing
        if Mc.get("max_local_db"):
            # limit how far one band's cumulative gain may stick out of its neighbours (no narrow resonances that
            # only fit one melody's note distribution)
            cand = total + gs
            nb = 0.5 * (np.r_[cand[0], cand[:-1]] + np.r_[cand[1:], cand[-1]])
            lim = float(Mc["max_local_db"])
            band = sel & (TO >= 315) & (TO <= 4000)
            cand = np.where(band, np.clip(cand, nb - lim, nb + lim), cand)
            gs = cand - total
        total += gs
        ff = np.linspace(0, SR / 2, 4097)
        gg = np.interp(np.log2(np.clip(ff, 15, None)), np.log2(TO), gs)
        fir = ss.firwin2(8193, ff / (SR / 2), db2a(gg))
        z = ss.fftconvolve(y, fir[:, None], mode="full", axes=0)
        y = z[4096:4096 + len(y)]
    return y, total


def k_weight(x):
    # BS.1770 K-weighting (pre-filter + RLB) designed for SR
    f0, G, Q = 1681.974450955533, 3.999843853973347, 0.7071752369554196
    K = math.tan(math.pi * f0 / SR)
    Vh, Vb = 10 ** (G / 20), (10 ** (G / 20)) ** 0.4996667741545416
    a0 = 1 + K / Q + K * K
    b = [(Vh + Vb * K / Q + K * K) / a0, 2 * (K * K - Vh) / a0, (Vh - Vb * K / Q + K * K) / a0]
    a = [1, 2 * (K * K - 1) / a0, (1 - K / Q + K * K) / a0]
    x = ss.lfilter(b, a, x, axis=0)
    f0, Q = 38.13547087602444, 0.5003270373238773
    K = math.tan(math.pi * f0 / SR)
    a0 = 1 + K / Q + K * K
    b = [1, -2, 1]
    a = [1, 2 * (K * K - 1) / a0, (1 - K / Q + K * K) / a0]
    return ss.lfilter(b, a, x, axis=0)


def lufs(y):
    z = k_weight(y)
    blk, hop = int(0.4 * SR), int(0.1 * SR)
    if len(z) < blk:
        return -120.0
    p = np.array([np.mean(z[i:i + blk] ** 2, axis=0).sum() for i in range(0, len(z) - blk + 1, hop)])
    l = -0.691 + 10 * np.log10(p + 1e-20)
    p = p[l > -70]
    if not len(p):
        return -120.0
    lr = -0.691 + 10 * np.log10(p.mean()) - 10
    p2 = p[(-0.691 + 10 * np.log10(p)) > lr]
    return float(-0.691 + 10 * np.log10(p2.mean()))


def peak_control(y, thr_db, win_ms=12.0):
    """rare-peak control (not a loudness limiter): smooth gain dip only where |y| would exceed thr.
    min-filter then moving average of the same width keeps the gain at or below the needed value with no steps."""
    if thr_db is None:
        return y
    from scipy.ndimage import maximum_filter1d, minimum_filter1d, uniform_filter1d
    thr = db2a(thr_db)
    a = np.abs(y).max(1)
    w = int(win_ms / 1000.0 * SR) | 1
    env = maximum_filter1d(a, 2 * (int(0.002 * SR)) + 1)
    g = np.minimum(1.0, thr / np.maximum(env, 1e-12))
    g = uniform_filter1d(minimum_filter1d(g, w), w)
    g = uniform_filter1d(minimum_filter1d(g, w), w)      # second pass: smoother (no audible step)
    return y * g[:, None]


def noises(n, Ch, seed):
    rng = rng_for(seed, "noise")
    t = np.arange(n) / SR
    out = np.zeros(n)
    for f, d in Ch["hum"]:
        out += db2a(d) * np.sin(2 * np.pi * f * t + rng.uniform(0, 2 * np.pi))
    if Ch.get("rumble_db") is not None:
        r = ss.sosfiltfilt(ss.butter(2, [4, 20], "bandpass", fs=SR, output="sos"), rng.standard_normal(n))
        out += r / np.sqrt(np.mean(r ** 2)) * np.sqrt(0.5) * db2a(Ch["rumble_db"])
    if Ch.get("hiss_db") is not None:
        h = ss.sosfiltfilt(ss.butter(2, [250, 4500], "bandpass", fs=SR, output="sos"), rng.standard_normal(n))
        out += h / np.sqrt(np.mean(h ** 2)) * np.sqrt(0.5) * db2a(Ch["hiss_db"])
    return out


def stem_rms(x, a, b):
    seg = x[int(a * SR):int(b * SR)]
    return float(np.sqrt(np.mean(seg ** 2)) + 1e-12)


# --------------------------------------------------------------------------------------------------- main
def render(melody_path, out_path, seed=0, overrides=(), stems_dir=None, verbose=True):
    M = load_melody(melody_path)
    deep_update(CFG, copy.deepcopy(M["engine"]))
    for o in overrides:
        k, v = o.split("=", 1)
        set_path(CFG, k, v)
    Ch = CFG["chain"]
    KEYTUNE["seed"] = seed
    length = float(Ch["length_s"])
    n_total = int(round(length * SR)) + int(1.0 * SR)
    F = Fluid()
    lead_ev = plan_line(M, M["lead"], CFG["lead"], seed, "lead")
    lead = render_line(F, M, lead_ev, CFG["lead"], n_total, seed, "lead")
    cC = copy.deepcopy(CFG["lead"])
    deep_update(cC, CFG["counter"])
    cnt_ev = plan_line(M, M["counter"], cC, seed, "counter")
    cnt = render_line(F, M, cnt_ev, cC, n_total, seed, "counter") if cnt_ev else np.zeros(n_total)
    acc_ev, st = plan_accomp(M, seed)
    calm_from = None
    if lead_ev and (lead_ev[-1]["t1"] - lead_ev[-1]["t0"]) >= 3 * M["beat_s"]:
        calm_from = lead_ev[-1]["t0"] + 0.5 * M["beat_s"]
    acc = render_accomp(F, M, acc_ev, st, n_total, calm_from)
    if lead_ev and CFG["accomp"].get("follow", 0):
        # the whole ensemble breathes with the lead's phrase dynamics (one bellows): smoothed lead gain curve
        tt = np.array([e["t0"] for e in lead_ev])
        gg = np.array([e["gain_db"] for e in lead_ev])
        tc = np.arange(0, n_total / SR + 0.01, 0.01)               # 100 Hz control grid
        dc = np.interp(tc, tt, gg)
        k = 25                                                     # +-0.25 s smoothing
        win = np.hanning(2 * k + 1)
        dc = np.convolve(np.r_[np.full(k, dc[0]), dc, np.full(k, dc[-1])], win / win.sum(), "valid")
        dcurve = np.interp(np.arange(n_total) / SR, tc, dc)
        acc *= db2a(CFG["accomp"]["follow"] * (dcurve - np.median(gg)))
    # balance: energies over the span where the lead plays (or everything if no lead)
    if lead_ev:
        a, b = lead_ev[0]["t0"], min(lead_ev[-1]["t1"], length)
    else:
        a, b = 0.0, length
    rl = stem_rms(lead, a, b) if lead_ev else 1.0
    if np.any(acc):
        acc *= rl / stem_rms(acc, a, b) * db2a(CFG["accomp"]["level_db"])
    if cnt_ev:
        ca, cb = cnt_ev[0]["t0"], cnt_ev[-1]["t1"]
        cnt *= rl / stem_rms(cnt, ca, cb) * db2a(CFG["counter"]["level_db"])
    dry = lead + acc + cnt
    E = CFG.get("ensemble", {})
    if E.get("hyper_db") or E.get("bar_swell_db"):
        # performance-level bellows phrasing of the whole band: 2-bar heavy/light pairs and a small swell inside each
        # bar (smooth, 100 Hz control rate)
        tc = np.arange(0, n_total / SR + 0.01, 0.01)
        pb = tc / M["beat_s"] + M["p_first"]                         # position in beats (bar 1 beat 1 = 0)
        bar = np.floor(pb / M["bpb"])
        ph = (pb / M["bpb"]) - bar                                  # 0..1 inside the bar
        gdb = E.get("hyper_db", 0.0) * np.cos(np.pi * (pb / M["bpb"])) * 0.5            # +-hyper/2, 2-bar period
        gdb += E.get("bar_swell_db", 0.0) * (0.5 - 0.5 * np.cos(2 * np.pi * np.clip(ph, 0, 1)))
        k = 15
        win = np.hanning(2 * k + 1)
        gdb = np.convolve(np.r_[np.full(k, gdb[0]), gdb, np.full(k, gdb[-1])], win / win.sum(), "valid")
        dry = dry * db2a(np.interp(np.arange(n_total) / SR, tc, gdb))
    if stems_dir:
        os.makedirs(stems_dir, exist_ok=True)
        for nm, s in (("lead", lead), ("accomp", acc), ("counter", cnt)):
            sf.write(os.path.join(stems_dir, nm + ".wav"), (s / (np.abs(dry).max() + 1e-9) * 0.5).astype(np.float32), SR)
    # ---- chain
    x = dry / (np.abs(dry).max() + 1e-12) * 0.5
    if Ch.get("sat_drive"):
        d = float(Ch["sat_drive"])
        x = np.tanh(d * x) / np.tanh(d)
    if Ch.get("pre_hp_hz"):
        x = ss.sosfilt(ss.butter(2, Ch["pre_hp_hz"], "highpass", fs=SR, output="sos"), x)
    if Ch.get("wow_pos", "pre") == "pre":
        xw, wc = apply_wow(x[:, None], Ch["wow"], seed)
        y = apply_room(xw[:, 0], Ch["room"], seed)
    else:
        y = apply_room(x, Ch["room"], seed)
        y, wc = apply_wow(y, Ch["wow"], seed)
    end_s = min(float(Ch["end_s"]), length)
    fade = float(Ch["fade_s"])
    music_end = max([e["t1"] for e in lead_ev + cnt_ev + acc_ev] or [end_s])
    if music_end + 0.2 < end_s:
        # a piece shorter than the clip: end after its own release instead of padding with hum
        end_s = music_end + 0.2
        fade = min(fade, 0.15)
        length = end_s + 0.03
    y = y[:int(round(length * SR))]
    # end fade (before the match so the LTAS is measured on what is heard)
    t = np.arange(len(y)) / SR
    g = np.where(t < end_s - fade, 1.0, 0.5 + 0.5 * np.cos(np.pi * np.clip((t - (end_s - fade)) / fade, 0, 1)))
    g[t >= end_s] = 0.0
    y = grain(y, Ch.get("grain"), seed)
    y = sbr(y, Ch.get("sbr"), seed)
    if Ch["match"]["on"]:
        y, eqc = match_eq(y, Ch["match"])
    else:
        eqc = None
    if Ch.get("lp_hz"):
        y = ss.sosfiltfilt(ss.butter(8, Ch["lp_hz"], "lowpass", fs=SR, output="sos"), y, axis=0)
    if Ch.get("side_mid_db") is not None:
        # stereo width: scale the side so side/mid energy hits the measured value (random room IRs vary +-1.5 dB)
        mid, sd = (y[:, 0] + y[:, 1]) / 2, (y[:, 0] - y[:, 1]) / 2
        k = math.sqrt(db2a(Ch["side_mid_db"]) ** 2 * np.mean(mid ** 2) / (np.mean(sd ** 2) + 1e-20))
        y = np.stack([mid + k * sd, mid - k * sd], 1)
    y = y * g[:, None]
    # loudness of the music, then add the noise floor at absolute dBFS levels
    L = lufs(y)
    y = y * db2a(Ch["lufs"] - L)
    nz = noises(len(y), Ch, seed)
    y = y + nz[:, None] * g[:, None] ** 0 * (t < end_s + 0.02)[:, None]
    L2 = lufs(y)
    y = y * db2a(Ch["lufs"] - L2)
    if Ch.get("peak_db") is not None:
        for _ in range(2):
            y = peak_control(y, Ch["peak_db"])
            y = y * db2a(Ch["lufs"] - lufs(y))
    sf.write(out_path, y.astype(np.float32), SR, subtype="PCM_24")
    info = {"id": M["id"], "seed": seed, "bpm": M["bpm"], "lead_notes": len(lead_ev), "accomp_events": len(acc_ev),
            "counter_notes": len(cnt_ev), "lufs": round(lufs(y), 2), "peak_dbfs": round(20 * np.log10(np.abs(y).max()), 2),
            "end_s": end_s, "wow_c_p5_p95": [round(float(np.percentile(wc, 5)), 1), round(float(np.percentile(wc, 95)), 1)],
            "match_eq_db": None if eqc is None else {str(int(f)): round(float(v), 1) for f, v in zip(TO, eqc)
                                                     if 100 <= f <= 12500}}
    if verbose:
        print(json.dumps(info))
    return info


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("melody")
    ap.add_argument("out")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--set", action="append", default=[], help="override a config value, e.g. accomp.level_db=-5")
    ap.add_argument("--stems", help="write dry stems to this folder")
    a = ap.parse_args()
    render(a.melody, a.out, a.seed, a.set, a.stems)


if __name__ == "__main__":
    main()
