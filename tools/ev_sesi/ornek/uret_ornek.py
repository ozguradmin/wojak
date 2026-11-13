#!/usr/bin/env python3
"""uret_ornek.py -- writes the minimal WORKING example JSONs of MOTOR_REHBERI.md into this folder.

These are ENGINE TEST PATTERNS (scale and arpeggio fragments written for this guide), not compositions: use them for
the format, never as a melody. Every file renders without error with ../render.py.

    python3 uret_ornek.py            # writes ornek/*.json
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def N(bar, beat, dur, midi, vel=90, **kw):
    d = {"bar": bar, "beat": beat, "dur_beats": dur, "midi": midi, "vel": vel}
    d.update(kw)
    return d


def CH(bar, midi, bass=None, beat=1, dur=None, **kw):
    d = {"bar": bar, "beat": beat, "midi": midi}
    if dur is not None:
        d["dur_beats"] = dur
    if bass is not None:
        d["bass"] = bass
    d.update(kw)
    return d


# chords as pitch-class sets written around C4 (the engine voices them itself)
Dm, Gm, A7, Bb, F, C7 = [62, 65, 69], [62, 67, 70], [61, 64, 67, 69], [62, 65, 70], [60, 65, 69], [60, 64, 67, 70]
G, D7, C, Em, Am, E7, Dm6 = [62, 67, 71], [60, 62, 66, 69], [60, 64, 67], [64, 67, 71], [60, 64, 69], [62, 64, 68, 71], [62, 65, 69, 71]

M3 = {"profile": "m3"}          # recommended for every new piece (start-tick fix + 4 ms fade-in)


def write(name, J):
    J = dict(J)
    J.setdefault("id", name)
    with open(os.path.join(HERE, name + ".json"), "w") as fh:
        json.dump(J, fh, indent=1, ensure_ascii=False)
    return name


def waltz(engine=None, accomp=None, perc=None, tempo=152, title="3/4 waltz, vamp 4 bars, lead from bar 5"):
    """3/4, D minor, 12 bars at 152 = 14.2 s (the engine's end fade cuts it at 13.74 s, like the CLASSIC)."""
    chords = [CH(b, Dm, 50) for b in (1, 2, 3, 4, 5)] + [CH(6, Gm, 55), CH(7, A7, 57), CH(8, Dm, 50), CH(9, Bb, 58),
                                                         CH(10, Gm, 55), CH(10, A7, 57, beat=3, dur=1), CH(11, Dm, 50),
                                                         CH(12, Dm, 50)]
    chords[9]["dur_beats"] = 2
    notes = [N(5, 1, 2, 81, 84), N(5, 3, 1, 79, 84),
             N(6, 1, 1, 82, 88), N(6, 2, 1, 81, 88), N(6, 3, 1, 79, 86),
             N(7, 1, 1, 76, 86), N(7, 2, 1, 81, 90), N(7, 3, 1, 79, 90),
             N(8, 1, 2, 77, 92), N(8, 3, 0.5, 79, 92), N(8, 3.5, 0.5, 81, 94),
             N(9, 1, 2, 86, 100), N(9, 3, 1, 84, 98),
             N(10, 1, 1, 82, 94), N(10, 2, 1, 79, 92), N(10, 3, 1, 76, 90),
             N(11, 1, 6, 74, 88)]
    J = {"title": title, "key": "D minor", "meter": "3/4", "tempo_bpm": tempo, "beats_per_bar": 3, "pickup_beats": 0,
         "notes": notes, "chords": chords, "accomp": accomp or {"pattern": "B C C"}, "engine": engine or dict(M3)}
    if perc:
        J["perc"] = perc
    return J


def polka(engine=None, accomp=None, perc=None, tempo=116):
    """2/4, G major, 13 bars at 116 = 13.45 s. Eighth-note oom-pah (subdiv 2), alternating bass, staccato lead."""
    prog = {1: (G, 55), 2: (G, 55), 3: (G, 55), 4: (D7, 50), 5: (G, 55), 6: (C, 48), 7: (D7, 50), 8: (G, 55),
            9: (Em, 52), 10: (C, 48), 11: (D7, 50), 12: (G, 55), 13: (G, 55)}
    chords = [CH(b, c, bs) for b, (c, bs) in prog.items()]
    st = {"art": "stacc"}
    notes = [N(5, 1, .5, 74, 86, **st), N(5, 1.5, .5, 71, 84, **st), N(5, 2, .5, 74, 86, **st), N(5, 2.5, .5, 79, 88, **st),
             N(6, 1, 1, 76, 90), N(6, 2, .5, 72, 86, **st), N(6, 2.5, .5, 76, 86, **st),
             N(7, 1, .5, 78, 88, **st), N(7, 1.5, .5, 74, 86, **st), N(7, 2, .5, 72, 86, **st), N(7, 2.5, .5, 69, 84, **st),
             N(8, 1, 1.5, 71, 88), N(8, 2.5, .5, 74, 88, **st),
             N(9, 1, .5, 76, 92, **st), N(9, 1.5, .5, 79, 94, **st), N(9, 2, 1, 83, 100),
             N(10, 1, 1.5, 84, 100), N(10, 2.5, .5, 79, 94, **st),
             N(11, 1, .5, 78, 92, **st), N(11, 1.5, .5, 76, 90, **st), N(11, 2, .5, 74, 90, **st), N(11, 2.5, .5, 72, 88, **st),
             N(12, 1, 4, 79, 90)]
    J = {"title": "2/4 polka, eighth-note oom-pah with alternating bass, vamp 4 bars", "key": "G major", "meter": "2/4",
         "tempo_bpm": tempo, "beats_per_bar": 2, "pickup_beats": 0, "notes": notes, "chords": chords,
         "accomp": accomp or {"pattern": "B C. F C.", "subdiv": 2, "pad": False},
         "engine": engine or dict(M3)}
    if perc:
        J["perc"] = perc
    return J


def march(engine=None, accomp=None, perc=None, tempo=120):
    """4/4, D minor, 7 bars at 120 = 14.0 s (cut at 13.74 s). Quarter-note oom-pah, vamp 2 bars."""
    prog = {1: (Dm, 50), 2: (Dm, 50), 3: (Dm, 50), 4: (Gm, 55), 5: (Bb, 58), 6: (A7, 57), 7: (Dm, 50)}
    chords = [CH(b, c, bs) for b, (c, bs) in prog.items()]
    notes = [N(3, 1, 1.5, 74, 88), N(3, 2.5, .5, 74, 86), N(3, 3, 1, 77, 90), N(3, 4, 1, 81, 92),
             N(4, 1, 2, 82, 94), N(4, 3, 1, 79, 90), N(4, 4, .5, 77, 88), N(4, 4.5, .5, 79, 90),
             N(5, 1, 3, 86, 102), N(5, 4, 1, 82, 96),
             N(6, 1, 1, 81, 94), N(6, 2, 1, 79, 92), N(6, 3, 1, 76, 90), N(6, 4, 1, 73, 88),
             N(7, 1, 4, 74, 90)]
    J = {"title": "4/4 march, oom-pah on the quarters with alternating bass, vamp 2 bars", "key": "D minor",
         "meter": "4/4", "tempo_bpm": tempo, "beats_per_bar": 4, "pickup_beats": 0, "notes": notes, "chords": chords,
         "accomp": accomp or {"pattern": "B C. F C.", "pad": True}, "engine": engine or dict(M3)}
    if perc:
        J["perc"] = perc
    return J


def sixeight(engine=None, accomp=None, perc=None, tempo=100):
    """6/8 written as 2 dotted-quarter beats per bar with 3 pattern slots per beat; A minor, 12 bars at 100 = 14.4 s."""
    prog = {1: (Am, 57), 2: (Am, 57), 3: (Am, 57), 4: (E7, 52), 5: (Am, 57), 6: (Dm, 50), 7: (E7, 52), 8: (Am, 57),
            9: (F, 53), 10: (Dm6, 50), 11: (Am, 57), 12: (Am, 57)}
    chords = [CH(b, c, bs) for b, (c, bs) in prog.items()]
    chords[9] = CH(10, Dm6, 50, dur=1)
    chords.insert(10, CH(10, E7, 52, beat=2, dur=1))
    t = 1 / 3
    notes = [N(5, 1, 2 * t, 76, 86), N(5, 1 + 2 * t, t, 77, 86), N(5, 2, 1, 76, 88),
             N(6, 1, 2 * t, 74, 88), N(6, 1 + 2 * t, t, 76, 88), N(6, 2, 2 * t, 77, 90), N(6, 2 + 2 * t, t, 81, 92),
             N(7, 1, 1, 80, 92), N(7, 2, 2 * t, 76, 90), N(7, 2 + 2 * t, t, 74, 88),
             N(8, 1, 1, 72, 88), N(8, 2, 2 * t, 76, 92), N(8, 2 + 2 * t, t, 81, 94),
             N(9, 1, 2, 84, 102),
             N(10, 1, 2 * t, 83, 96), N(10, 1 + 2 * t, t, 81, 94), N(10, 2, 2 * t, 80, 92), N(10, 2 + 2 * t, t, 76, 90),
             N(11, 1, 4, 81, 90)]
    for n in notes:
        n["beat"] = round(n["beat"], 4)
        n["dur_beats"] = round(n["dur_beats"], 4)
    J = {"title": "6/8 as 2 beats x 3 slots: bass - chord, fifth - chord; vamp 4 bars", "key": "A minor", "meter": "6/8",
         "tempo_bpm": tempo, "beats_per_bar": 2, "pickup_beats": 0, "notes": notes, "chords": chords,
         "accomp": accomp or {"pattern": "B - C. F - C.", "subdiv": 3}, "engine": engine or dict(M3)}
    if perc:
        J["perc"] = perc
    return J


def eng(**kw):
    d = dict(M3)
    d.update(kw)
    return d


def vamp_legato(J, last_vamp_bar, pattern):
    """per-chord pattern: the vamp-only bars play legato (no holes), the rest keeps the piece's own pattern"""
    for c in J["chords"]:
        if c["bar"] <= last_vamp_bar:
            c["pattern"] = pattern
    return J


VAMP = {"intro_bright_db": 3.0}        # vamp-only opening a little brighter (measured in MOTOR_REHBERI.md §7)

# lead recipes (measured scores: MOTOR_REHBERI.md §4)
R1 = [{"prog": 22}, {"prog": 22, "gain_db": -3, "detune": 20}]
R3 = [{"prog": 71}, {"prog": 71, "detune": 20}]
AKORDEON = [{"prog": 21}, {"prog": 22, "gain_db": -3, "detune": 14}]
HARMONYUM = [{"prog": 20}]
KUTU = [{"prog": 10, "kind": "struck", "ring_s": 1.2}]
KUTU_REED = [{"prog": 10, "kind": "struck", "ring_s": 1.2}, {"prog": 23, "gain_db": -4}]
CELESTA = [{"prog": 8, "kind": "struck", "ring_s": 1.0}]
MANDOLIN = [{"prog": 25, "bank": 16, "sf": "ms", "kind": "struck", "ring_s": 0.5, "trem_hz": 13}]
FAGOT = [{"prog": 70, "oct": -1}]
ISLIK = [{"prog": 78}]
ZURNA = [{"prog": 111}, {"prog": 111, "gain_db": -3, "detune": 14}]
TROMPET = [{"prog": 59}]
GAYDA = [{"prog": 109}]
HONKY = [{"prog": 3, "kind": "struck", "ring_s": 0.5}]
NO_BENDS = {"bends": None, "scoop_c": 0}       # struck / brass leads: no reed-style scoops


def lead(layers, **kw):
    d = {"layers": layers}
    d.update(kw)
    return d


def main():
    done = []
    A = lambda **kw: dict(VAMP, **kw)
    # ---- metres / accompaniment patterns (default lead R2)
    done.append(write("01_vals_3_4", waltz(engine=eng(accomp=A()))))
    done.append(write("02_polka_2_4", vamp_legato(polka(engine=eng(accomp=A()),
                                                        accomp={"pattern": "B C. F C.", "subdiv": 2, "pad": True}), 4, "B C F C")))
    done.append(write("03_mars_4_4", vamp_legato(march(engine=eng(accomp=A())), 2, "B C F C")))
    done.append(write("04_alti_sekiz_6_8", sixeight(engine=eng(accomp=A()))))
    done.append(write("05_vals_tutulan_akor", waltz(engine=eng(accomp=A()), accomp={"pattern": "B H H"},
                                                    title="3/4, held chords on beats 2-3 (B H H)")))
    Jw = vamp_legato(march(engine=eng(accomp=A(bass_fold=False)), accomp={"pattern": "B C. B C.", "pad": True}), 2, "B C B C")
    walks = {1: [50, 45], 2: [50, 45], 3: [50, 53], 4: [55, 58], 5: [58, 53], 6: [57, 52], 7: [50, 45]}
    for c in Jw["chords"]:
        c["bass"] = walks[c["bar"]]
    Jw["title"] = "4/4, walking bass: each chord carries a bass list, one note per B slot (bass_fold off = as written)"
    done.append(write("06_yuruyen_bas_4_4", Jw))
    Jp = polka(engine=eng())
    Jp["notes"] = [N(0, 2, .5, 74, 84, art="stacc"), N(0, 2.5, .5, 76, 84, art="stacc")] + \
                  [dict(n, bar=n["bar"] - 4) for n in Jp["notes"]]
    Jp["chords"] = [dict(c, bar=c["bar"] - 4) for c in Jp["chords"] if c["bar"] >= 5] + \
                   [CH(10, C, 48), CH(11, D7, 50), CH(12, G, 55), CH(13, G, 55)]
    Jp["notes"][-1] = N(8, 1, 2, 79, 90)
    Jp["notes"] += [N(9, 1, .5, 83, 92, art="stacc"), N(9, 1.5, .5, 81, 92, art="stacc"), N(9, 2, 1, 79, 92),
                    N(10, 1, 1.5, 76, 92), N(10, 2.5, .5, 79, 94, art="stacc"),
                    N(11, 1, .5, 78, 92, art="stacc"), N(11, 1.5, .5, 81, 94, art="stacc"), N(11, 2, 1, 86, 100),
                    N(12, 1, 4, 79, 90)]
    Jp["pickup_beats"] = 1
    Jp["title"] = "2/4 with a one-beat pickup (bar 0 beat 2) and no vamp: the first chord is extended back under it"
    done.append(write("07_auftakt_2_4", Jp))
    Jc = waltz(engine=eng(accomp=A()), title="3/4 with a counter line (second voice, P21, -6 dB) from bar 7")
    Jc["counter"] = [N(7, 1, 3, 73, 76), N(8, 1, 3, 74, 76), N(9, 1, 2, 77, 80), N(9, 3, 1, 74, 78), N(10, 1, 2, 70, 76),
                     N(10, 3, 1, 69, 76), N(11, 1, 3, 65, 74)]
    done.append(write("08_karsi_ezgi_3_4", Jc))
    # ---- lead recipes
    done.append(write("10_lead_R1_tremolo_harmonika", waltz(engine=eng(lead=lead(R1), accomp=A()))))
    done.append(write("11_lead_R3_klarnet_musette", waltz(engine=eng(lead=lead(R3), accomp=A()))))
    done.append(write("12_lead_akordeon_P21_P22", waltz(engine=eng(lead=lead(AKORDEON), accomp=A()))))
    done.append(write("13_lead_harmonyum_P20", waltz(engine=eng(lead=lead(HARMONYUM), accomp=A()))))
    done.append(write("14_lead_muzik_kutusu_6_8", sixeight(engine=eng(lead=lead(KUTU, **NO_BENDS), accomp=A()))))
    done.append(write("15_lead_kutu_arti_reed", waltz(engine=eng(lead=lead(KUTU_REED), accomp=A()))))
    done.append(write("16_lead_celesta_P8", waltz(engine=eng(lead=lead(CELESTA, **NO_BENDS), accomp=A()))))
    done.append(write("17_lead_mandolin_tremolo_6_8", sixeight(engine=eng(lead=lead(MANDOLIN, **NO_BENDS), accomp=A()))))
    done.append(write("18_lead_fagot_tuba_polka", vamp_legato(polka(
        engine=eng(lead=lead(FAGOT, **NO_BENDS), accomp=A(oom_layers=[{"prog": 58, "oct": -1}])),
        accomp={"pattern": "B C. F C.", "subdiv": 2, "pad": True}), 4, "B C F C")))
    done.append(write("19_lead_islik_polka", vamp_legato(polka(
        engine=eng(lead=lead(ISLIK, **NO_BENDS), accomp=A()),
        accomp={"pattern": "B C. F C.", "subdiv": 2, "pad": True}), 4, "B C F C")))
    done.append(write("20_lead_zurna_davul_2_4", vamp_legato(polka(
        engine=eng(lead=lead(ZURNA), accomp=A(), perc={"level_db": -9.0}), tempo=108,
        accomp={"pattern": "B C. F C.", "subdiv": 2, "pad": True},
        perc={"pattern": "D . x x D . x .", "subdiv": 4}), 4, "B C F C")))
    done.append(write("21_lead_trompet_trampet_mars", vamp_legato(march(
        engine=eng(lead=lead(TROMPET, **NO_BENDS), accomp=A(), perc={"level_db": -9.0}),
        perc={"pattern": "K . S . K . S s", "subdiv": 2, "from_bar": 1, "to_bar": 6}), 2, "B C F C")))
    done.append(write("22_lead_gayda_6_8", sixeight(engine=eng(lead=lead(GAYDA), accomp=A()))))
    done.append(write("23_lead_honkytonk_polka", vamp_legato(polka(
        engine=eng(lead=lead(HONKY, **NO_BENDS), accomp=A()),
        accomp={"pattern": "B C. F C.", "subdiv": 2, "pad": True}), 4, "B C F C")))
    # ---- percussion on a waltz, tempo and end time
    done.append(write("24_vurmali_tef_vals", waltz(engine=eng(accomp=A(), perc={"level_db": -9.0}), perc={"pattern": ". t t"})))
    Jf = waltz(engine=eng(accomp=A(), chain={"end_s": 13.9}), tempo=190,
               title="3/4 at 190 BPM, 16 bars, all sound ends at 13.9 s (chain.end_s)")
    Jf["notes"] = [n for n in Jf["notes"] if n["bar"] <= 10] + [dict(n, bar=n["bar"] + 6) for n in Jf["notes"] if 5 <= n["bar"] <= 8] \
        + [N(15, 1, 6, 74, 88)]
    Jf["chords"] = [c for c in Jf["chords"] if c["bar"] <= 10] + [dict(c, bar=c["bar"] + 6) for c in Jf["chords"] if 5 <= c["bar"] <= 8] \
        + [CH(15, Dm, 50), CH(16, Dm, 50)]
    done.append(write("25_tempo_190_son_13_9", Jf))
    Js = waltz(engine=eng(accomp=A(), chain={"end_s": 13.5}), tempo=96,
               title="3/4 at 96 BPM, 8 bars, vamp 2 bars, all sound ends at 13.5 s")
    Js["notes"] = [dict(n, bar=n["bar"] - 2) for n in Js["notes"] if n["bar"] <= 8] + [N(7, 1, 6, 74, 88)]
    Js["chords"] = [dict(c, bar=c["bar"] - 2) for c in Js["chords"] if 3 <= c["bar"] <= 8] + [CH(7, Dm, 50), CH(8, Dm, 50)]
    done.append(write("26_tempo_096_son_13_5", Js))
    json.dump(done, open(os.path.join(HERE, "liste.json"), "w"), indent=1)
    print("\n".join(done))


if __name__ == "__main__":
    main()
