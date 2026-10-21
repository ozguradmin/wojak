"""b2 composer toolkit: bar notation -> melody JSON (BAGLAM format), symbolic checks, FluidR3 preview render.

Bar notation (one string per bar):  tokens separated by spaces, onsets accumulate from beat 1 (or '@2' = start at beat 2)
    G5:1       note G5 for 1 beat           Ab5:1.5  dotted quarter    F#5:.5  eighth
    [Ab5 G5 F#5]   triplet group, 1/3 beat each (one beat in total)
    [B5:2 C6]      triplet with a 2/3 + 1/3 split (durations in triplet units)
    C6:hold    hold to the end of the piece (13.75 s)        r:1  rest
Timing: bar 0 is the 2-beat pickup (beats 2-3); t = 0 at bar 0 beat 2; t(bar, beat) = (3*bar + beat - 2) * 60/bpm.
"""
import json, os, re, sys, subprocess
import numpy as np

SP = "/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2"
OUT = os.path.join(SP, "besteler", "b2")
END_S = 13.75
NOTA = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def midi(name):
    m = re.fullmatch(r"([A-G])([b#]?)(-?\d)", name)
    if not m:
        raise ValueError(name)
    pc = NOTA[m.group(1)] + {"": 0, "b": -1, "#": 1}[m.group(2)]
    return 12 * (int(m.group(3)) + 1) + pc


def parse_bar(bar, s, end_beats_abs=None):
    """returns list of (bar, beat, dur, midi)"""
    out = []
    beat = 1.0
    toks = re.findall(r"\[[^\]]*\]|\S+", s)
    for tk in toks:
        if tk.startswith("@"):
            beat = float(tk[1:]); continue
        if tk.startswith("["):
            items = tk[1:-1].split()
            units = []
            for it in items:
                if ":" in it:
                    n, u = it.split(":"); units.append((n, int(u)))
                else:
                    units.append((it, 1))
            for n, u in units:
                d = u / 3.0
                if n != "r":
                    out.append([bar, round(beat, 3), round(d, 3), midi(n)])
                beat += d
            continue
        n, d = tk.split(":")
        if d == "hold":
            ab = 3 * bar + beat - 1
            dur = end_beats_abs - ab
            out.append([bar, round(beat, 3), round(dur, 3), midi(n)])
            beat += dur
            continue
        d = float(d)
        if n != "r":
            out.append([bar, round(beat, 3), round(d, 3), midi(n)])
        beat += d
    return out


# ---------------------------------------------------------------------------------------------- chords
# pa voicings (close position, C4..C5 octave unless noted) and bass midi for each symbol used by the b2 pieces
CH = {
    "Cm":      dict(pa=["C4", "Eb4", "G4"],        name="Cm"),
    "Cm+":     dict(pa=["Eb4", "G4", "C5"],        name="Cm"),          # higher inversion under high melodies
    "Cm64":    dict(pa=["Eb4", "G4", "C5"],        name="Cm/G"),
    "B07":     dict(pa=["D4", "F4", "Ab4", "B4"],  name="Bdim7"),
    "Fm":      dict(pa=["C4", "F4", "Ab4"],        name="Fm"),
    "Fm+":     dict(pa=["F4", "Ab4", "C5"],        name="Fm"),
    "Fm6":     dict(pa=["D4", "F4", "Ab4", "C5"],  name="Fm6"),
    "F7":      dict(pa=["Eb4", "F4", "A4", "C5"],  name="F7"),
    "Db":      dict(pa=["Db4", "F4", "Ab4"],       name="Db"),
    "Db+":     dict(pa=["F4", "Ab4", "Db5"],       name="Db"),
    "Ab":      dict(pa=["Eb4", "Ab4", "C5"],       name="Ab"),
    "G7":      dict(pa=["D4", "F4", "G4", "B4"],   name="G7"),
    "G7b9":    dict(pa=["D4", "F4", "Ab4", "B4"],  name="G7b9"),
    "G":       dict(pa=["D4", "G4", "B4"],         name="G"),
    "D7":      dict(pa=["D4", "F#4", "A4", "C5"],  name="D7"),
    "Fs07":    dict(pa=["Eb4", "F#4", "A4", "C5"], name="F#dim7"),
    "Dm7b5":   dict(pa=["D4", "F4", "Ab4", "C5"],  name="Dm7b5"),
    "C7b9":    dict(pa=["E4", "G4", "Bb4", "Db5"], name="C7b9"),
    "Bbm":     dict(pa=["Db4", "F4", "Bb4"],       name="Bbm"),
    "Ger6":    dict(pa=["Eb4", "F#4", "Ab4"],       name="Ab7"),   # C stays in the bass pedal
}
ROMAN = {"Cm": "i", "Cm+": "i", "Cm64": "i6/4", "B07": "vii°7", "Fm": "iv", "Fm+": "iv", "Fm6": "iv6 (iiø6/5)",
         "F7": "IV7 (Dorian)", "Db": "bII (Neapolitan)", "Db+": "bII", "Ab": "VI", "G7": "V7", "G7b9": "V7(b9)",
         "G": "V", "D7": "II7 (V7/V)", "Fs07": "#iv°7", "Dm7b5": "iiø7", "C7b9": "V7(b9)/iv", "Bbm": "v/iv", "Ger6": "German +6 (Ab-C-Eb-F#) over the C pedal"}


def parse_harm(spec):
    """'Cm/C' or 'Cm/C | b2 B07 | b3 G7' -> list of 3 (sym, bass_midi or None) per beat"""
    parts = [p.strip() for p in spec.split("|")]
    first = parts[0]
    sym, bass = (first.split("/") + [None])[:2]
    beats = [[sym, bass], [sym, bass], [sym, bass]]
    for p in parts[1:]:
        b, s = p.split()
        b = int(b[1:])
        s2, bs2 = (s.split("/") + [None])[:2]
        for k in range(b - 1, 3):
            beats[k] = [s2, bs2 or beats[k][1]]
    res = []
    for s, b in beats:
        bm = midi(b + "3") if b and not b[-1].isdigit() else (midi(b) if b else None)
        if bm is not None and bm > 55:
            bm -= 12
        res.append((s, bm))
    return res


# ---------------------------------------------------------------------------------------------- build
def build(P):
    bpm = P["tempo"]
    bs = 60.0 / bpm
    end_abs = END_S / bs + 1.0 - 0.015 / bs            # beats from bar 0 beat 1 (t = (abs - 1) * bs), 15 ms margin
    end_abs = round(end_abs + 1.0 - 1.0, 3)
    # t(bar,beat) = (3*bar + beat - 2) * bs  -> abs index a = 3*bar+beat-1 ; t = (a-1)*bs ; a_end = END/bs + 1
    a_end = END_S / bs + 1.0 - 0.02
    notes, counter = [], []
    for bar, s in sorted(P["mel"].items()):
        for b, bt, d, m in parse_bar(bar, s, a_end):
            notes.append([b, bt, d, m])
    for bar, s in sorted(P.get("counter", {}).items()):
        for b, bt, d, m in parse_bar(bar, s, a_end):
            counter.append([b, bt, d, m])
    dyn = P.get("dyn", {})
    def vel(bar, base=88):
        return int(round(base * 10 ** (dyn.get(bar, 0) / 20)))
    # inverted accent in the melody too: downbeat attacks 2 dB softer than beats 2-3 (supports the "u a a")
    N = [{"bar": b, "beat": bt, "dur_beats": d, "midi": m,
          "vel": min(127, int(round(vel(b, P.get("lead_vel", 92)) * (0.8 if abs(bt - 1.0) < 1e-6 else 1.0))))}
         for b, bt, d, m in notes]
    C = [{"bar": b, "beat": bt, "dur_beats": d, "midi": m, "vel": min(127, vel(b, 70))} for b, bt, d, m in counter]
    chords, events = [], []
    last_bar = max(P["harm"])
    for bar in sorted(P["harm"]):
        hb = parse_harm(P["harm"][bar])
        for k, (sym, bass) in enumerate(hb):
            beat = k + 1
            if bar == 0 and beat == 1:
                continue
            t = (3 * bar + beat - 2) * bs
            if t >= END_S - 0.1:
                continue
            ch = CH[sym]
            pa = [midi(x) for x in ch["pa"]]
            chords.append({"bar": bar, "beat": beat, "dur_beats": 1, "chord": ch["name"], "roman": ROMAN[sym],
                           "bass": bass, "midi": pa})
            if beat == 1:
                bm = bass if bass is not None else pa[0] - 12
                events.append({"bar": bar, "beat": 1, "role": "um", "midi": [bm, bm + 12], "dur_s": 0.30,
                               "vel": vel(bar, 72)})
            else:
                events.append({"bar": bar, "beat": beat, "role": "pa", "midi": pa, "dur_s": 0.12,
                               "vel": vel(bar, 96)})
    J = {"id": P["id"], "title": P["title"], "composer": "b2", "tempo_bpm": bpm, "meter": "3/4", "key": "C minor",
         "pickup_beats": 2,
         "timing": {"bar_numbering": "bar 0 = the 2-beat pickup (beats 2-3); bar 1 = first full bar; t = 0 at bar 0 beat 2",
                    "formula": "t_s(bar, beat) = (3*bar + beat - 2) * 60/tempo_bpm",
                    "bar1_downbeat_s": round(2 * bs, 3), "bar10_downbeat_s": round(29 * bs, 3), "end_s": END_S},
         "notes": N, "chords": chords,
         "accomp": {"pattern": P["accomp_text"],
                    "um": "beat 1: bass + its octave, soft and dark (vel ~64, 0.30 s); fundamentals below 250 Hz are removed by the chain, so it is heard through its partials",
                    "pa": "beats 2-3: close triad in the C4-C5 octave (the 'midi' of each chords entry), bright 120-150 ms swell (vel ~86, ~3-4 dB over the um)",
                    "pad": "under the pa swells: the same chord sustained very softly (reed organ, about -14 dB) so there are no gaps (legato bed)",
                    "events": events},
         "counter": C,
         "counter_text": P.get("counter_text", ""),
         "instruments": P.get("instruments", {}),
         "dynamics_db_by_bar": dyn,
         "notes_text": P["notes_text"]}
    return J


# ---------------------------------------------------------------------------------------------- checks
def symbolic(J):
    sys.path.insert(0, os.path.join(SP, "olcum"))
    import olcum
    ref_notes, ref_json = olcum.load_ref_melody()
    cand = olcum.norm_notes(J["notes"])
    sym = olcum.symbolic(cand, olcum.norm_notes(ref_notes), 0)
    ch = olcum.chord_check([{"bar": c["bar"], "chord": c["chord"]} for c in J["chords"]], ref_json)
    return sym, ch


def stats(J):
    ns = J["notes"]
    ms = np.array([n["midi"] for n in ns])
    iv = np.abs(np.diff(ms))
    bars = sorted(set(n["bar"] for n in ns if n["bar"] <= 9))
    trip = [abs(n["dur_beats"] - 1 / 3) < 0.02 or abs(n["dur_beats"] - 2 / 3) < 0.02 for n in ns]
    hi = int(ms.max())
    hi_idx = [i for i, n in enumerate(ns) if n["midi"] == hi]
    bs = 60 / J["tempo_bpm"]
    t_hi = [(3 * ns[i]["bar"] + ns[i]["beat"] - 2) * bs for i in hi_idx]
    # pitch-class share in the main 5th zone
    pcs = [m % 12 for m in ms]
    return {"notes": len(ns), "notes_per_bar_0_9": round(len([n for n in ns if n["bar"] <= 9]) / 9.0, 2),
            "triplet_share": round(float(np.mean(trip)), 2), "range": int(ms.max() - ms.min()),
            "low": int(ms.min()), "high": hi, "climax_t_s": [round(x, 2) for x in t_hi],
            "climax_pct": [round(100 * x / END_S) for x in t_hi],
            "steps": round(float(np.mean((iv >= 1) & (iv <= 2))), 2), "thirds": round(float(np.mean((iv >= 3) & (iv <= 4))), 2),
            "repeats": round(float(np.mean(iv == 0)), 2), "leaps_ge4th": round(float(np.mean(iv >= 5)), 2),
            "below_C5": int(np.sum(ms < 72))}


def report_sym(J):
    sym, ch = symbolic(J)
    o = sym["offlimits"]
    print(f"[{J['id']}] symbolic {sym['verdict']}  viol={o['violations']} POV={o['POV']} N5={o['N5']} sig={o['signatures']} "
          f"rc={o['rhythm_cells']} SK={o['SK']} ALT={o['ALT_warn']}")
    print(f"   ng3m={sym['ngram3_metric']['share']:.2f} ng4f={sym['ngram4_free']['share']:.2f} "
          f"cbar={sym['contour_bar_corr']['value']} cphr={sym['contour_phrase_corr']['value']} "
          f"rhy_same={sym['rhythm_same_bar_share']:.2f} rhy_dist={sym['rhythm_distinctive_same_bar']} reasons={sym['reasons']}")
    print(f"   chords: {ch}")
    print(f"   stats: {stats(J)}")
    return sym, ch


# ---------------------------------------------------------------------------------------------- render
def render(J, wav_path, lead=None, acc_prog=21, pad_prog=20, ctr_prog=23, acc_db=-1.0, pad_db=-10.0, ctr_db=-9.0, seed=1):
    sys.path.insert(0, os.path.join(SP, "analiz", "tini", "py"))
    import soundfile as sf, scipy.signal as ss
    import zincir as Z
    from fsr import render_layers
    from eslestir import match_fir, apply
    SR = 44100
    bs = 60.0 / J["tempo_bpm"]
    T = lambda bar, beat: (3 * bar + beat - 2) * bs
    total = END_S + 0.6
    lead = lead or [dict(prog=22), dict(prog=22, detune_c=20, gain_db=-3)]
    ln = []
    for n in J["notes"]:
        t0 = T(n["bar"], n["beat"]); du = n["dur_beats"] * bs + 0.05
        ln.append((max(0.0, t0), min(du, END_S + 0.2 - t0), n["midi"], n["vel"]))
    acc, pad = [], []
    for e in J["accomp"]["events"]:
        t0 = max(0.0, T(e["bar"], e["beat"]))
        for m in e["midi"]:
            acc.append((t0, e["dur_s"], m, e["vel"]))
    # pad: chord sustained from each chord change to the next
    chs = J["chords"]
    for i, c in enumerate(chs):
        t0 = max(0.0, T(c["bar"], c["beat"]))
        t1 = T(chs[i + 1]["bar"], chs[i + 1]["beat"]) if i + 1 < len(chs) else END_S + 0.1
        for m in c["midi"]:
            pad.append((t0, t1 - t0 + 0.04, m, 60))
    ctr = []
    for n in J.get("counter", []):
        t0 = T(n["bar"], n["beat"]); du = n["dur_beats"] * bs + 0.05
        ctr.append((max(0.0, t0), min(du, END_S + 0.2 - t0), n["midi"], n["vel"]))
    # FluidSynth note-off releases the newest instance of a pitch, so overlapping same-pitch notes would kill re-strikes:
    # merge them in the sustained bed, re-articulate (shorten the earlier one) elsewhere
    def fix(ev, merge=False):
        ev = sorted(ev, key=lambda e: e[0]); out, last = [], {}
        for st, du, m, v in ev:
            j = last.get(m)
            if j is not None:
                pst, pdu, pm, pv = out[j]
                if st < pst + pdu:
                    if merge:
                        out[j] = (pst, max(pdu, st + du - pst), pm, pv); continue
                    out[j] = (pst, max(0.03, st - pst - 0.008), pm, pv)
            last[m] = len(out); out.append((st, du, m, v))
        return out
    ln, acc, pad, ctr = fix(ln), fix(acc), fix(pad, merge=True), fix(ctr)
    xl = render_layers(lead, ln, total)
    xa = render_layers([dict(prog=acc_prog)], acc, total)
    xp = render_layers([dict(prog=pad_prog)], pad, total)
    parts = [xl, xa, xp]
    if ctr:
        xc = render_layers([dict(prog=ctr_prog)], ctr, total); parts.append(xc)
    n = min(len(p) for p in parts)
    parts = [p[:n] for p in parts]
    rms = lambda v: np.sqrt(np.mean(v ** 2)) + 1e-12
    rl = rms(parts[0])
    x = parts[0] + parts[1] * (rl / rms(parts[1])) * 10 ** (acc_db / 20) + parts[2] * (rl / rms(parts[2])) * 10 ** (pad_db / 20)
    if ctr:
        x = x + parts[3] * (rl / rms(parts[3])) * 10 ** (ctr_db / 20)
    REV = dict(rt60=0.09, pd_ms=6, build_ms=4, tail_db=-30, tail_rt=1.5, lp=3000)
    TARGET = json.load(open(os.path.join(SP, "analiz", "tini.json")))["eq_curve"]
    y = Z.chain(x, wow_c=4.5, wet_db=-8, rev=REV)
    for _ in range(2):
        fir, _g = match_fir(y, [v for _, v in TARGET])
        y = apply(y, fir)
    y = ss.sosfilt(ss.butter(8, 5000, "lowpass", fs=SR, output="sos"), y, axis=0)
    y = y[: int(END_S * SR)]
    t = np.arange(len(y)) / SR
    y *= np.clip((END_S - t) / 0.06, 0, 1)[:, None]   # hold to a short cut like the original
    tmp = wav_path + ".tmp.wav"
    sf.write(tmp, y, SR, subtype="FLOAT")
    for _ in range(2):
        p = subprocess.run(["ffmpeg", "-nostats", "-hide_banner", "-i", tmp, "-af", "ebur128", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
        I = float(p[p.rfind("I:"):].split()[1])
        y = y * 10 ** ((-29.5 - I) / 20)
        sf.write(tmp, y, SR, subtype="FLOAT")
    sf.write(wav_path, y, SR, subtype="PCM_24")
    os.remove(tmp)
    return wav_path


def harness(wav, js, png):
    p = subprocess.run(["python3", os.path.join(SP, "olcum", "olcum.py"), wav, "--notalar", js, "--png", png],
                       capture_output=True, text=True)
    o = json.loads(p.stdout)
    json.dump(o, open(wav.replace(".wav", ".olcum.json"), "w"), indent=1, ensure_ascii=False)
    og = o["originality"]
    s = og.get("symbolic", {})
    mus = o["musical"]
    summ = {"verdict": o["originality_verdict"], "audio": og["audio_verdict"], "audio_warn": og["audio_warnings"],
            "chroma_tools": og["chroma_seq_sim"]["value"], "chroma_T": og["chroma_seq_sim_transposed"]["value"],
            "fingerprint": og["fingerprint_match"]["value"], "sym_verdict": s.get("verdict"), "sym_reasons": s.get("reasons"),
            "POV": s.get("offlimits", {}).get("POV"), "violations": s.get("offlimits", {}).get("violations"),
            "ngram3_metric": s.get("ngram3_metric", {}).get("share"), "ngram4_free": s.get("ngram4_free", {}).get("share"),
            "contour_bar": s.get("contour_bar_corr", {}).get("value"), "contour_phrase": s.get("contour_phrase_corr", {}).get("value"),
            "rhythm_distinct": s.get("rhythm_distinctive_same_bar"),
            "TIMBRE": o["TIMBRE_SCORE"], "tempo": mus["tempo_bpm"]["value"], "key": mus["key"]["value"],
            "c_minor_r": mus["key"].get("c_minor_r"), "rock_lag2": mus["harmonic_rocking"]["value"],
            "rock_lag1": mus["harmonic_rocking"].get("lag1bar"), "accent": o["timbre"]["accent_uaa"]["value"],
            "accent_level": o["timbre"]["accent_uaa"].get("level_from_dark_db"),
            "bar_levels": mus["bar_levels_db"]["value"], "first": o["technical"]["first_sound_s"]["value"],
            "last": o["technical"]["last_sound_s"]["value"], "LUFS": o["technical"]["lufs_integrated"]["value"],
            "checks_ok": o["technical_checks"].get("all_ok")}
    return summ, o
