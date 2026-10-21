"""b1 composer toolkit: compact notation -> BAGLAM melody JSON, symbolic checks, quick FluidR3 preview.

Notation
  melody / counter: one string per bar (bar 0 = the 2-beat pickup, starting on beat 2), tokens "PITCH:DUR[:VEL]"
    PITCH  C5 Eb5 F#4 ... (C4 = 60) or r (rest);  DUR in beats: 1, 2, 3, t (=1/3), 2t (=2/3), h (=1/2), 1.5 ...
    A note may run past its bar line (then the next bar string continues from where it ends).
  chords: one entry per bar, either "Sym" (whole bar) or "Sym Sym Sym" (one per beat; "-" repeats the previous one).
"""
import json, math, os, re, subprocess, sys
import numpy as np

SP = "/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2"
OUT = os.path.join(SP, "besteler", "b1")
SF2 = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
SR = 44100

PC = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def pm(name):
    m = re.fullmatch(r"([A-G])([b#]?)(-?\d)", name)
    if not m:
        raise ValueError(name)
    return 12 * (int(m.group(3)) + 1) + PC[m.group(1)] + (1 if m.group(2) == "#" else -1 if m.group(2) == "b" else 0)


def dur(s):
    s = s.strip()
    if s == "t":
        return 1 / 3
    if s == "2t":
        return 2 / 3
    if s == "h":
        return 0.5
    return float(s)


# chord symbol -> (bass midi, close voicing in the C4-C5 octave, name for olcum chord_check, roman)
CH = {
    "Cm":      (48, [60, 63, 67], "Cm", "i"),
    "Cm/G":    (43, [60, 63, 67], "Cm", "i6/4"),
    "Cm/Eb":   (51, [60, 63, 67], "Cm", "i6"),
    "Cm7":     (48, [58, 60, 63, 67], "Cm", "i7"),
    "Cm(maj7)/C": (48, [59, 63, 67], "Cm", "i(maj7)"),
    "Ab/C":    (48, [60, 63, 68], "Ab", "VI6"),
    "Ab":      (44, [60, 63, 68], "Ab", "VI"),
    "Abmaj7":  (44, [60, 63, 67], "Ab", "VImaj7"),
    "Fm":      (41, [60, 65, 68], "Fm", "iv"),
    "Fm/Ab":   (44, [60, 65, 68], "Fm", "iv6"),
    "Fm/C":    (48, [60, 65, 68], "Fm", "iv6/4"),
    "Fm6/Ab":  (44, [62, 65, 68], "Fm", "iv6 (+6)"),
    "Fm7":     (41, [60, 63, 65, 68], "Fm", "iv7"),
    "G":       (43, [59, 62, 67], "G", "V"),
    "G/B":     (47, [59, 62, 67], "G", "V6"),
    "G/D":     (50, [59, 62, 67], "G", "V6/4"),
    "G7":      (43, [59, 62, 65], "G7", "V7"),
    "G7/B":    (47, [59, 62, 65, 67], "G7", "V6/5"),
    "G7/D":    (50, [59, 62, 65], "G7", "V4/3"),
    "G7/F":    (41, [59, 62, 67], "G7", "V4/2"),
    "Gsus4":   (43, [60, 62, 67], "G", "Vsus4"),
    "G7b9":    (43, [59, 62, 65, 68], "G7", "V7(b9)"),
    "Bdim7":   (47, [59, 62, 65, 68], "Bdim", "vii°7"),
    "Bdim7/C": (48, [59, 62, 65, 68], "Bdim", "vii°7/C (over tonic pedal)"),
    "Bdim7/Ab": (44, [59, 62, 65], "Bdim", "vii°4/2"),
    "Bdim/D":  (50, [59, 62, 65], "Bdim", "vii°6"),
    "Bb/D":    (50, [58, 62, 65], "Bb", "VII6"),
    "Bb":      (46, [58, 62, 65], "Bb", "VII"),
    "Bb7":     (46, [58, 62, 65, 68], "Bb7", "VII7"),
    "Eb":      (51, [58, 63, 67], "Eb", "III"),
    "Eb/G":    (43, [58, 63, 67], "Eb", "III6"),
    "Ddim/F":  (41, [62, 65, 68], "Ddim", "ii°6"),
    "Dm7b5/F": (41, [60, 62, 65, 68], "Ddim", "iiø6/5"),
    "Dm7b5":   (50, [60, 65, 68], "Ddim", "iiø7"),
    "D7/F#":   (42, [60, 62, 66], "D7", "V7/V (6/5)"),
    "F#dim7":  (42, [60, 63, 66, 69], "F#dim", "vii°7/V"),
    "F#dim7/C": (48, [60, 63, 66, 69], "F#dim", "vii°7/V over C"),
    "Db/F":    (41, [61, 65, 68], "Db", "N6"),
    "Db/Ab":   (44, [61, 65, 68], "Db", "N6/4"),
    "Db":      (49, [61, 65, 68], "Db", "N"),
}


def parse_line(bars, start_beat_of_bar0=2.0):
    """bars: list of strings, bars[0] = pickup bar (bar 0). returns notes [(bar, beat, dur, midi, vel)]"""
    out = []
    p = (start_beat_of_bar0 - 1.0)            # absolute beat position from bar 0 beat 1
    for bi, s in enumerate(bars):
        s = s.strip()
        # each bar string starts at the bar line unless a long note has run into this bar
        bar_start = bi * 3.0
        if p < bar_start - 1e-6 and s:
            p = bar_start if bi > 0 else p
        if not s:
            continue
        for tok in s.split():
            f = tok.split(":")
            d = dur(f[1]) if len(f) > 1 else 1.0
            v = int(f[2]) if len(f) > 2 else None
            if f[0] != "r":
                bar = int(math.floor(p / 3.0 + 1e-6))
                beat = round(p - 3 * bar + 1, 4)
                out.append([bar, beat, round(d, 4), pm(f[0]), v])
            p += d
        end = (bi + 1) * 3.0
        if abs(p - end) > 1e-3 and p < end:
            print(f"  WARNING bar {bi}: ends at beat {p - bi * 3 + 1:.3f} (underfilled)", file=sys.stderr)
    return out


def parse_chords(chords):
    """chords[i] = string for bar i (bar 0 = pickup: beats 2-3). returns per-beat list [(bar, beat, sym)]"""
    out = []
    prev = None
    for bi, s in enumerate(chords):
        toks = s.split()
        if len(toks) == 1:
            toks = toks * 3
        if len(toks) != 3:
            raise ValueError(f"bar {bi}: {s}")
        for k, t in enumerate(toks):
            if bi == 0 and k == 0:
                continue                     # pickup bar: beats 2-3 only
            if t == "-":
                t = prev
            if t not in CH:
                raise KeyError(t)
            out.append((bi, k + 1, t))
            prev = t
    return out


def build(piece):
    """piece dict -> BAGLAM JSON dict"""
    bpm = piece.get("tempo_bpm", 152)
    beat_s = 60.0 / bpm
    dyn = piece.get("dyn", {})                   # bar -> default velocity

    def T(bar, beat):
        return (3 * bar + beat - 1 - 1.0) * beat_s   # bar 0 beat 2 = 0.00 s

    def notes_of(lines, default_vel, accent=True):
        res = []
        climax = piece.get("climax_bar", 7)
        for bar, beat, d, m, v in parse_line(lines):
            vel = v if v is not None else dyn.get(bar, default_vel)
            if accent and v is None and bar != climax and 1 <= bar <= 9:
                # the "u a a": soft, dark beat 1, struck beats 2-3 (performance accent written into the score)
                if abs(beat - 1.0) < 1e-6:
                    vel -= 7
                elif abs(beat - 2.0) < 1e-6 or abs(beat - 3.0) < 1e-6:
                    vel += 3
            res.append({"bar": bar, "beat": round(beat, 3), "dur_beats": round(d, 3), "midi": m, "vel": int(vel),
                        "t_s": round(T(bar, beat), 3)})
        return res

    notes = notes_of(piece["melody"], 88)
    counter = notes_of(piece["counter"], 60, accent=False) if piece.get("counter") else []
    for c in counter:
        c["vel"] = int(piece.get("counter_vel", {}).get(c["bar"], c["vel"]))
    beats = parse_chords(piece["chords"])
    chords = []
    for bar, beat, sym in beats:
        bass, voi, name, roman = CH[sym]
        v = piece.get("voicing", {}).get(sym, voi)
        chords.append({"bar": bar, "beat": float(beat), "dur_beats": 1, "midi": list(v), "bass": bass,
                       "chord": name, "symbol": sym, "roman": roman, "t_s": round(T(bar, beat), 3)})
    # explicit accompaniment events (um on beat 1 = bass; pa on beats 2-3 = close chord)
    acc = []
    for c in chords:
        if c["beat"] == 1.0:
            acc.append({"bar": c["bar"], "beat": 1.0, "dur_beats": 0.75, "midi": [c["bass"]], "role": "um",
                        "vel": int(piece.get("um_vel", 72))})
        else:
            acc.append({"bar": c["bar"], "beat": c["beat"], "dur_beats": 0.55, "midi": c["midi"], "role": "pa",
                        "vel": int(piece.get("pa_vel", 84))})
    # nothing may sound past 13.75 s: clip chord and accompaniment durations at the end of the clip
    end_beats = 13.75 / beat_s
    for c in chords + acc:
        pos = 3 * c["bar"] + c["beat"] - 2.0
        c["dur_beats"] = round(min(c["dur_beats"], end_beats - pos), 3)
    J = {
        "id": piece["id"],
        "title": piece.get("title", ""),
        "composer": "b1 (Claude, original composition)",
        "key": "C minor", "meter": "3/4", "tempo_bpm": bpm, "beats_per_bar": 3,
        "pickup_beats": 2,
        "timing": {"rule": "bar 0 is the 2-beat pickup (beats 2-3); bar 0 beat 2 = 0.00 s; "
                           "t = (3*bar + beat - 2) * 60/tempo_bpm; bar 1 is the first full bar; all sound ends by 13.75 s",
                   "beat_s": round(beat_s, 5), "bar_s": round(3 * beat_s, 5),
                   "tonic_arrival_s": None, "climax_s": None, "end_s": 13.75,
                   "fade": [13.45, 13.75]},
        "instruments": piece.get("instruments", {
            "lead": "free-reed tremolo/musette: FluidR3 P22 harmonica + P22 detuned +20 c at -3 dB (tini R1), "
                    "or P23 tango accordion + P22 +14 c at -2 dB (tini R2); legato, 45 ms attacks, no vibrato",
            "accomp": "P23 tango accordion (alt. P21): um = soft dark bass reed on beat 1 (fundamental removed by the "
                      "250 Hz band, heard through its partials); pa = bright close chord swells on beats 2-3, "
                      "3-4 dB louder than the um, over a quiet held chord bed",
            "counter": "P21 accordion or P20 reed organ, soft (-8..-12 dB under the lead), legato inner voice"}),
        "notes": notes,
        "chords": chords,
        "accomp": {"pattern": "B C C waltz um-pa-pa, legato bed; beat 1 soft dark bass (um), beats 2-3 bright close "
                              "chord swells (pa), pa 3-4 dB above um; continues softly under the final hold",
                   "events": acc},
        "counter": counter,
        "form": piece.get("form", {}),
        "expression": piece.get("expression", []),
        "notes_text": piece.get("notes_text", ""),
    }
    # timing facts
    last = max(notes, key=lambda n: n["t_s"])
    J["timing"]["tonic_arrival_s"] = last["t_s"] if last["midi"] % 12 == 0 else None
    top = max(n["midi"] for n in notes)
    J["timing"]["climax_s"] = min(n["t_s"] for n in notes if n["midi"] == top)
    return J


def stats(J):
    ms = [n["midi"] for n in J["notes"]]
    iv = np.diff(ms)
    a = np.abs(iv)
    lo, hi = min(ms), max(ms)
    # best 4th/5th zone share (zone of 7 semitones)
    best = max((sum(1 for m in ms if z <= m <= z + 7) / len(ms), z) for z in range(lo, hi + 1))
    return {"n": len(ms), "range": f"{lo}-{hi} ({hi - lo} st)", "steps": round(float(np.mean((a >= 1) & (a <= 2))), 2),
            "thirds": round(float(np.mean((a >= 3) & (a <= 4))), 2), "repeats": round(float(np.mean(a == 0)), 2),
            "leaps>=4th": round(float(np.mean(a >= 5)), 2), "zone5_share": round(best[0], 2), "zone_lo": best[1],
            "triplets": sum(1 for n in J["notes"] if abs(n["dur_beats"] - 1 / 3) < 0.02),
            "climax_s": J["timing"]["climax_s"], "tonic_s": J["timing"]["tonic_arrival_s"]}


def symcheck(J):
    sys.path.insert(0, os.path.join(SP, "olcum"))
    sys.path.insert(0, os.path.join(SP, "analiz", "muzik", "py"))
    import olcum, offlimits
    notes = olcum.norm_notes(J["notes"])
    ref_notes, ref_json = olcum.load_ref_melody()
    s = olcum.symbolic(notes, olcum.norm_notes(ref_notes), 0)
    ol = offlimits.check([{"bar": b, "beat": bt, "dur_beats": d, "midi": m} for b, bt, d, m in notes], 0)
    cc = olcum.chord_check(J["chords"], ref_json)
    return s, ol, cc


def brief(s, ol, cc):
    return {"verdict": s["verdict"], "reasons": s["reasons"], "viol": ol["violations"], "POV": ol["POV"],
            "N5": ol["N5"], "sig": ol["signatures"], "rc": ol["rhythm_cells"], "SK": ol["SK"], "ALT": ol["ALT_warn"],
            "ng3m": round(s["ngram3_metric"]["share"], 3), "ng4f": round(s["ngram4_free"]["share"], 3),
            "cbar": None if s["contour_bar_corr"]["value"] is None else round(s["contour_bar_corr"]["value"], 3),
            "cphr": None if s["contour_phrase_corr"]["value"] is None else round(s["contour_phrase_corr"]["value"], 3),
            "rhy": s["rhythm_distinctive_same_bar"], "chords": cc}


def save(J, path=None):
    path = path or os.path.join(OUT, J["id"] + ".json")
    with open(path, "w") as fh:
        json.dump(J, fh, ensure_ascii=False, indent=1)
    return path


# ------------------------------------------------------------------------------------------------ preview render
class FS:
    def __init__(self):
        import fluidsynth
        self.fs = fluidsynth.Synth(gain=0.4, samplerate=float(SR),
                                   **{"synth.reverb.active": 0, "synth.chorus.active": 0, "synth.polyphony": 64})
        self.sfid = self.fs.sfload(SF2)

    def note(self, prog, midi, dur_s, vel, cents=0.0, tail_s=0.35):
        fs = self.fs
        fs.program_select(0, self.sfid, 0, prog)
        fs.cc(0, 7, 127); fs.cc(0, 11, 127); fs.cc(0, 91, 0); fs.cc(0, 93, 0)
        fs.pitch_bend(0, int(round(cents / 200.0 * 8192)))
        fs.noteon(0, int(midi), int(np.clip(vel, 1, 127)))
        a = np.array(fs.get_samples(int(dur_s * SR)), dtype=np.float64)
        fs.noteoff(0, int(midi))
        b = np.array(fs.get_samples(int(tail_s * SR)), dtype=np.float64)
        fs.all_sounds_off(0)
        fs.get_samples(int(0.05 * SR))
        y = np.concatenate([a, b]).reshape(-1, 2).mean(1) / 32768.0
        return y


def env(n_on, n_tot, att, rel):
    e = np.ones(n_tot)
    na = max(1, int(att * SR))
    e[:na] = 0.5 - 0.5 * np.cos(np.pi * np.arange(na) / na)
    nr = max(1, int(rel * SR))
    if n_on < n_tot:
        r = np.zeros(n_tot - n_on)
        k = min(nr, len(r))
        r[:k] = 0.5 + 0.5 * np.cos(np.pi * np.arange(k) / k)
        e[n_on:] *= r
    return e


def render_preview(J, wav_path, lead_layers=None, acc_prog=23, ctr_prog=21, seed=1, total=13.75):
    sys.path.insert(0, os.path.join(SP, "analiz", "tini", "py"))
    import zincir as Z, eslestir as E
    tini = json.load(open(os.path.join(SP, "analiz", "tini.json")))
    target = np.array([v for f, v in tini["eq_curve"]])
    bpm = J["tempo_bpm"]; bs = 60.0 / bpm
    N = int((total + 0.6) * SR)
    fs = FS()
    tune = -23.0
    lead_layers = lead_layers or [(22, 0.0, 0.0), (22, 20.0, -3.0)]
    lead = np.zeros(N); accb = np.zeros(N); ctr = np.zeros(N)

    def T(bar, beat):
        return (3 * bar + beat - 2.0) * bs

    def put(buf, y, t0):
        i0 = int(round(t0 * SR))
        if i0 < 0:
            y = y[-i0:]; i0 = 0
        i1 = min(N, i0 + len(y))
        buf[i0:i1] += y[:i1 - i0]

    rng = np.random.default_rng(seed)
    # lead: legato, each note overlaps the next by 50 ms, 45 ms attacks
    ns = sorted(J["notes"], key=lambda n: T(n["bar"], n["beat"]))
    for i, n in enumerate(ns):
        t0 = T(n["bar"], n["beat"])
        t1 = t0 + n["dur_beats"] * bs
        if i + 1 < len(ns):
            t1 = max(t1, T(ns[i + 1]["bar"], ns[i + 1]["beat"])) + 0.05
        t1 = min(t1, total)
        d = max(0.05, t1 - t0)
        det = float(rng.normal(0, 9.0))                       # per-note reed intonation, preview only
        for prog, cents, gdb in lead_layers:
            y = fs.note(prog, n["midi"], d, n["vel"], tune + cents + det)
            y = y * env(int(d * SR), len(y), 0.045 if i == 0 or (t0 - T(ns[i-1]["bar"], ns[i-1]["beat"])) > 0.2 else 0.03, 0.07)
            put(lead, y * 10 ** (gdb / 20), t0)
    # accompaniment from explicit events
    for e in J["accomp"]["events"]:
        t0 = T(e["bar"], e["beat"])
        if e["role"] == "um":
            d = 0.30
            for m in e["midi"]:
                for mm, g in ((m, 0.0), (m + 12, -6.0)):
                    y = fs.note(acc_prog, mm, d, e["vel"], tune)
                    y = y * env(int(d * SR), len(y), 0.04, 0.08)
                    put(accb, y * 10 ** ((g - 8.0) / 20), t0)
        else:
            d = 0.17
            for m in e["midi"]:
                y = fs.note(acc_prog, m, d, e["vel"], tune)
                y = y * env(int(d * SR), len(y), 0.035, 0.06)
                put(accb, y * 10 ** (-3.0 / 20) / math.sqrt(len(e["midi"])), t0)
    # quiet held bed: chord tones per bar (reed organ), keeps the texture continuous
    bars = {}
    for c in J["chords"]:
        bars.setdefault((c["bar"], c["beat"]), c)
    for c in J["chords"]:
        t0 = T(c["bar"], c["beat"]); d = bs + 0.04
        for m in c["midi"]:
            y = fs.note(20, m, d, 60, tune)
            y = y * env(int(d * SR), len(y), 0.03, 0.05)
            put(accb, y * 10 ** (-20.0 / 20) / math.sqrt(len(c["midi"])), t0)
    for i, n in enumerate(sorted(J.get("counter", []), key=lambda n: T(n["bar"], n["beat"]))):
        t0 = T(n["bar"], n["beat"]); d = min(total - t0, n["dur_beats"] * bs + 0.05)
        y = fs.note(ctr_prog, n["midi"], d, n["vel"], tune)
        y = y * env(int(d * SR), len(y), 0.05, 0.08)
        put(ctr, y * 10 ** (-9.0 / 20), t0)
    fs.fs.delete()
    mix = lead + accb * 10 ** (1.0 / 20) + ctr
    # chain: random wow + slow 0.5 Hz upward-excursion wow, room, band, LTAS match, hum
    y = Z.wow(mix, 4.5, seed=seed)
    t = np.arange(len(y)) / SR
    slow = 14.0 * np.maximum(0, np.sin(2 * np.pi * 0.5 * t + 0.7)) ** 2 - 4.0        # cents, upward excursions
    ratio = 2 ** (slow / 1200.0)
    pos = np.cumsum(ratio); pos = pos - pos[0]; pos = pos * (len(y) - 1) / pos[-1]
    y = np.interp(pos, np.arange(len(y)), y)
    y = Z.reverb(y, -8.0, rt60=0.09, pd_ms=6, build_ms=4, tail_db=-30, tail_rt=1.5, lp=3000)
    y = Z.bandeq(y, hp=250, lp=4800)
    for _ in range(2):
        fir, _g = E.match_fir(y, target)
        y = E.apply(y, fir)
    y = Z.bandeq(y, hp=200, hp_order=2, lp=5000, lp_order=8)
    n_end = int(total * SR)
    y = y[:n_end]
    fade = np.ones(n_end)
    f0 = int(13.45 * SR)
    fade[f0:] = 0.5 + 0.5 * np.cos(np.pi * np.arange(n_end - f0) / (n_end - f0))
    y = y * fade[:, None]
    fi = int(0.004 * SR)
    y[:fi] *= np.linspace(0, 1, fi)[:, None]
    # loudness to -29.5 LUFS (measure with ffmpeg) then hum
    import soundfile as sf
    tmp = wav_path + ".tmp.wav"
    sf.write(tmp, y.astype(np.float32), SR, subtype="FLOAT")
    I = lufs(tmp)
    y = y * 10 ** ((-29.5 - I) / 20)
    y = y + Z.noises(len(y))[:, None] * fade[:, None]
    sf.write(wav_path, y.astype(np.float32), SR, subtype="PCM_24")
    os.remove(tmp)
    return wav_path, lufs(wav_path)


def lufs(path):
    p = subprocess.run(["ffmpeg", "-nostats", "-hide_banner", "-i", path, "-af", "ebur128=peak=true:framelog=quiet",
                        "-f", "null", "-"], capture_output=True, text=True)
    txt = p.stderr[p.stderr.rfind("Summary:"):]
    m = re.search(r"I:\s+(-?[\d.]+) LUFS", txt)
    return float(m.group(1))
