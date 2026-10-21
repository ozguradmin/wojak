"""The four b1 pieces in compact notation (see b1lib.py). bar 0 = 2-beat pickup (beats 2-3); bars 10-11 = tonic hold."""

P = {}

# ------------------------------------------------------------------------------------------------ b1-1
# Sigh-appoggiatura rocking: every hook downbeat is a dissonance on the soft "u" that resolves on the bright "a a".
P["b1-1"] = dict(
    id="b1-1", title="İç Çekiş (the sigh)", tempo_bpm=152,
    melody=[
        "F5 G5",                          # 0 pickup: stepwise run up into the first sigh
        "Ab5 G5 G5",                      # 1 b6 -> 5 over i
        "Eb5 D5 F5",                      # 2 b13 -> 5 over V6/5, F climbs the diminished triad back to Ab
        "Ab5 G5 G5",                      # 3
        "Eb5:t F5:t Eb5:t D5 D5",         # 4 spin 1: turn on the appoggiatura
        "Eb5 G5:t F5:t G5:t Ab5",         # 5 spin 2: lower-neighbour turn, climbing
        "F5 G5 F5:t Ab5:t B5:t",          # 6 rising diminished arpeggio F-Ab-B (augmented second Ab-B)
        "C6 B5 G5",                       # 7 CLIMAX: 4-3 sigh over V (C6 -> B5)
        "Ab5:t G5:t Ab5:t G5 Eb5",        # 8 spin 3: b6 shiver
        "Ab5 F5 Db5:2t C5:6.15",          # 9 Neapolitan arpeggio, Db -> C sigh, tonic one triplet early
        "", "",                           # 10-11 hold
    ],
    chords=["Cm", "Cm", "G7/B", "Cm", "G7/B", "Cm Cm Ab/C", "Fm/Ab - Bdim7/Ab", "Gsus4 G7 -", "Cm", "Db/F",
            "Cm", "G7"],
    counter=["", "", "", "", "", "", "C5:2 D5:1", "F5:3", "C5:3", "Ab4:3", "G4:3", "F4:2.8"],
    dyn={0: 74, 1: 76, 2: 74, 3: 78, 4: 80, 5: 90, 6: 94, 7: 102, 8: 92, 9: 86, 10: 82, 11: 78},
)

# ------------------------------------------------------------------------------------------------ b1-2
# Bell tower: a G5 bell rings on every "a a" while the "u" and the bass sink (lament bass C-Bb-Ab-G).
P["b1-2"] = dict(
    id="b1-2", title="Çan Kulesi (bell tower)", tempo_bpm=152,
    melody=[
        "G5 G5",                          # 0 pickup: the bell
        "G5 Eb5 G5",                      # 1 i: ding-dong-ding
        "G5 D5 G5",                       # 2 VII (G = added 6th): the inner voice sinks
        "G5 C5 Eb5",                      # 3 VI (G = major 7th): the bell falters
        "B4:t C5:t D5:t G5 F5",           # 4 V7, spin 1: rising lift on the 'u'
        "G5 Eb5 C5",                      # 5 i, the bell again, falling to the tonic
        "C5:t D5:t Eb5:t F5:t Eb5:t F5:t G5",   # 6 iv6, spin 2: a two-beat swirl climbing to the bell
        "Ab5 G5 F5",                      # 7 CLIMAX: the bell cracks: Ab5 (b9 over V7) -> G5
        "Eb5:t D5:t Eb5:t G5 G5",         # 8 spin 3: turn, last ring of the bell
        "F5 D5 B4:h C5:6.3",              # 9 iv(add6) -> V7, tonic an eighth early
        "", "",
    ],
    chords=["Cm", "Cm", "Bb", "Abmaj7", "G7", "Cm", "Fm/Ab", "G7b9", "Cm", "Fm6/Ab - G7", "Cm", "G7/B"],
    counter=["", "", "", "", "", "", "Ab4:3", "B4:1.5 D5:1.5", "C5:3", "Ab4:2 G4:1", "Eb4:3", "D4:2.8"],
    dyn={0: 74, 1: 76, 2: 76, 3: 78, 4: 82, 5: 90, 6: 94, 7: 102, 8: 92, 9: 86, 10: 82, 11: 78},
)

# ------------------------------------------------------------------------------------------------ b1-3
# Carousel: every hook bar starts with a chromatic lower-neighbour shiver (G-F#-G / F-E-F) over i <-> V7 (C-G bass).
P["b1-3"] = dict(
    id="b1-3", title="Atlıkarınca (carousel)", tempo_bpm=152,
    melody=[
        "Eb5 F5",                         # 0 pickup
        "G5:t F#5:t G5:t Eb5 G5",         # 1 i
        "F5:t E5:t F5:t D5 F5",           # 2 V7
        "G5:t F#5:t G5:t Eb5 G5",         # 3 i
        "F5:t E5:t F5:t D5 B4",           # 4 V7, opens down to the leading tone
        "C5:t Eb5:t F5:t G5:t F5:t Eb5:t D5",  # 5 two-beat swirl on beats 1-2 (rise then fall)
        "Eb5 G5 C5:t Db5:t F5:t",         # 6 Neapolitan arpeggio run (C-Db-F) ...
        "Ab5 G5:t F5:t G5:t F5",          # 7 CLIMAX: ... into Ab5 over N6, sigh to G5 as V7 arrives
        "G5:t F#5:t G5:t Eb5 C5",         # 8 the shiver returns over i
        "Eb5 F#5 D5:2t C5:6.15",          # 9 vii°7/V: augmented second Eb-F#, then V7, tonic a triplet early
        "", "",
    ],
    chords=["Cm", "Cm", "G7", "Cm", "G7", "Cm", "Cm Cm Db/F", "Db/F G7 -", "Cm", "F#dim7 - G7", "Cm", "Bdim7"],
    counter=["", "", "", "", "", "G4:3", "Bb4:2 Ab4:1", "F4:1 B4:2", "G4:3", "C5:2 G4:1", "G4:3", "Ab4:2.8"],
    dyn={0: 74, 1: 78, 2: 76, 3: 78, 4: 80, 5: 90, 6: 94, 7: 102, 8: 92, 9: 86, 10: 82, 11: 78},
)

# ------------------------------------------------------------------------------------------------ b1-4
# Shadow: a pedal 'u' on Eb5 under two falling sighs (G-F, Ab-G) over i <-> VI6 (tonic pedal); the cry is Bb5 -> A5
# over a "Hungarian" V7/V (b13), then a falling diminished arpeggio into the tonic.
P["b1-4"] = dict(
    id="b1-4", title="Gölge (shadow)", tempo_bpm=152,
    melody=[
        "G5 F5",                          # 0 pickup falls into the hook
        "Eb5 G5 F5",                      # 1 i
        "Eb5 Ab5 G5",                     # 2 VI6 over the C pedal
        "Eb5 G5 F5",                      # 3 i
        "Eb5:t D5:t Eb5:t Ab5 G5",        # 4 VI6, spin 1: turn on the pedal note
        "F5 G5:t Ab5:t G5:t F5",          # 5 iv, spin 2: upper-neighbour turn
        "Ab5 G5 F#5:t G5:t A5:t",         # 6 chromatic lift F#-G-A (V7/V) ...
        "Bb5 A5 F#5",                     # 7 CLIMAX: Bb5 (b13 over V7/V) -> A5
        "G5:t F5:t G5:t D5 F5",           # 8 V7, spin 3: lower-neighbour turn
        "Ab5 G5 F5:t D5:t C5:6.15",       # 9 last sigh Ab->G as V7 arrives, falling triplet F-D-C into the tonic
        "", "",
    ],
    chords=["Cm", "Cm", "Ab/C", "Cm", "Ab/C", "Fm", "Ab Ab D7/F#", "D7/F#", "G7", "Dm7b5/F G7 -", "Cm", "G7b9"],
    counter=["", "", "", "", "", "C5:3", "C5:2 D5:1", "D5:1.5 C5:1.5", "B4:3", "C5:1 D5:1 G4:1", "G4:3", "F4:2.8"],
    dyn={0: 74, 1: 76, 2: 78, 3: 76, 4: 80, 5: 88, 6: 94, 7: 102, 8: 92, 9: 86, 10: 82, 11: 78},
)

# ------------------------------------------------------------------------------------------------ texts
COMMON_FORM = {
    "bars": "0 pickup (beats 2-3) | 1-4 statement: 2-bar hook stated twice over a one-chord-per-bar rocking | "
            "5-8 intensification: triplet spins in 4/5/6 and 8, climax bar 7 (7.89 s = 57 %) | 9 cadence with a "
            "chromatic colour, tonic one triplet/eighth early | 10-11 tonic held over the continuing waltz, "
            "dominant-function chord under it in bar 11 so the reel's auto-loop resolves into the pickup",
    "dynamics": "bars 0-4 soft (vel 74-80), bars 5-8 +3..4 dB (vel 88-102, peak at the climax), bar 9 back -1..2 dB, "
                "hold softer; inside bars 1-9 beat 1 is written 7 velocity steps softer and beats 2-3 3 steps "
                "louder (the 'u a a'), except at the climax",
}
EXPR = [
    {"bar": 7, "beat": 1.0, "hint": "climax: may enter 40-80 ms early and scoop up into pitch (45-75 c over ~180 ms), "
                                     "as measured on the original's lead; no vibrato"},
    {"bar": 9, "beat": "last note", "hint": "tonic anticipation: keep it legato from the previous note; the held "
                                             "tonic may drift up to ~30-40 c sharp over its last second; hard stop "
                                             "by 13.75 s (fade 13.45-13.75)"},
    {"bar": "0-4", "hint": "the lead can be voiced as the top of the right-hand chords (struck together with the pa "
                           "chords); the full lead colour from bar 5"},
]
TEXT = {
"b1-1": "Emotional twin of the original's rocking opening, rebuilt on the appoggiatura sigh. Each hook downbeat is a "
        "dissonance on the soft, dark 'u' (Ab5 over the tonic, Eb5 over V6/5) that resolves by a semitone onto the "
        "bright 'a a' (G5 G5, then D5), so the followers' 'u a a' becomes sigh-and-answer. The harmony rocks one chord "
        "per bar between i and V6/5 over a C-B semitone bass: the whole texture sinks a semitone and comes back, a "
        "pendulum like the original's but not its C-D bass or its u-a-a cell. Bars 4-6 speed up with three new triplet "
        "shapes (a turn on beat 1, a lower-neighbour turn on beat 2, a rising diminished arpeggio F-Ab-B with the "
        "augmented second Ab-B) that carry the line by step to the one cry: C6 over V at 7.9 s (57 %), falling a "
        "semitone to B5 as a 4-3 suspension. The cadence is Phrygian: Neapolitan Db major, arpeggio Ab-F-Db, then the "
        "Db->C sigh; the tonic C5 arrives a triplet early (11.32 s) and is held while the waltz goes on, with V7 under "
        "it in the last bar so the auto-loop resolves into the pickup. Range C5-C6, wider than the brief's minor 7th "
        "because of the octave cry; 89 % of the notes sit inside Db5-Ab5.",
"b1-2": "A bell tower. A G5 bell rings on beats 1 and 3 ('ding-dong-ding') while the inner voice sinks Eb-D-C and the "
        "bass walks down the lament tetrachord C-Bb-Ab-G, so the same G changes colour underneath (fifth of i, added "
        "sixth over VII, major seventh over VI, root of V): eerie stillness over a falling floor. The 'a u a' contour "
        "keeps the original's quarter-note pulse, fused top voice and narrow register (B4-Ab5, 9 semitones, 92 % in "
        "C5-G5) but turns its rising u-a-a inside out. Spins: a rising lift B-C-D into V7 (bar 4), a two-beat swirl "
        "C-D-Eb | F-Eb-F climbing back to the bell (bar 6), a turn on the 'u' (bar 8). The cry is the bell cracking: "
        "at 7.9 s it rises a semitone to Ab5, the b9 over V7(b9), and falls straight back to G on the next beat "
        "(approached by step, not by a leap). Cadence: iv with added sixth (D against Ab) to V7, the tonic an eighth "
        "early, held over the waltz; V6/5 under it at the end for the loop.",
"b1-3": "A carousel, the most hummable of the four. Every hook bar opens with a chromatic lower-neighbour shiver on the "
        "soft beat 1 (G-F#-G over i, F-E-F over V7) followed by two plain quarters, so the bar sounds 'shiver-a-a': the "
        "original's pulse kept, with a new figure in the 'u'. The harmony is the most literal twin, i <-> V7 every "
        "bar, but over a root-position C-G oom (not C-D) and with G/Eb/F/D in the top line instead of the original's "
        "C/Eb/D/F u-a-a. Middle spins: a two-beat swirl C-Eb-F | G-F-Eb (bar 5), then a run C-Db-F through the "
        "Neapolitan chord into the cry, Ab5 at 7.9 s, which falls a semitone to G as V7 arrives (Ab->G over N6->V, "
        "reached from below by the arpeggio, not by the original's +8 leap). The shiver returns over the tonic "
        "(bar 8); the cadence uses vii°7/V with the melodic augmented second Eb-F# for the old-world colour, the "
        "tonic arrives a triplet early and is held over the waltz, with a diminished seventh under it at the end. "
        "Range B4-Ab5 (9 semitones), 96 % of the notes inside a fifth, 56 % triplets.",
"b1-4": "Shadow. A pedal 'u' on Eb5 under two falling sighs (Eb | G-F, then Eb | Ab-G) over a tonic pedal that rocks "
        "i <-> VI6, where only G<->Ab moves in the chord: the same semitone the melody sighs on, so the rocking is "
        "quieter and more hypnotic than the original's diminished pendulum. Spins: a turn on the pedal note (bar 4), "
        "an upper-neighbour turn (bar 5) and a chromatic lift F#-G-A (bar 6) into the cry: Bb5 over a 'Hungarian' "
        "V7/V (D7 with b13) at 7.9 s, falling a semitone to A5, the darkest and most Eastern-European colour of the "
        "four and a different cry note from the original's Ab. After a lower-neighbour turn over V7, the cadence "
        "gives one last Ab->G sigh as V7 arrives, then a falling triplet F-D into the tonic a triplet early, held "
        "over the waltz, with V7(b9) under it at the end for the loop. Range C5-Bb5 (a minor 7th), 95 % of the notes "
        "inside a fifth.",
}
for k in P:
    P[k]["notes_text"] = TEXT[k]
    P[k]["form"] = dict(COMMON_FORM)
    P[k]["expression"] = EXPR
