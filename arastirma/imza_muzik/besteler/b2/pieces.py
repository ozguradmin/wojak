"""The four b2 pieces (bar notation: see b2lib.py). Bar 0 = 2-beat pickup."""

DYN_STD = {0: 0, 1: 0, 2: 0, 3: 0, 4: 2.5, 5: 3, 6: 3.5, 7: 4, 8: 3, 9: 1.5, 10: 1.5, 11: 1}

ACC = ("waltz um-pa-pa with an inverted accent: beat 1 = soft dark bass + octave (the 'u'), beats 2-3 = bright close-triad "
       "swells in the C4-C5 octave (the 'a a'), over a very soft sustained chord bed so nothing gaps")

# ----------------------------------------------------------------------------------------------------------- b2-1
P1 = dict(
    id="b2-1", title="Kurmalı Kutu (the wind-up box)", tempo=152,
    harm={0: "Cm+/C", 1: "B07/C", 2: "Cm+/C", 3: "B07/C", 4: "Cm+/C", 5: "B07/C", 6: "Cm+/C", 7: "B07/C",
          8: "Fm+/Ab", 9: "Cm64/G | b2 G7", 10: "Cm+/C", 11: "Cm+/C | b2 B07"},
    mel={0: "@2 C6:1 Ab5:1",
         1: "B5:1 [C6 B5 Ab5] B5:1",
         2: "C6:2 G5:1",
         3: "Ab5:1 [B5 Ab5 G5] F5:1",
         4: "G5:1 [Ab5 G5 F5] G5:1",
         5: "Ab5:1 B5:1 D6:1",
         6: "C6:2 [B5 C6 D6]",
         7: "Eb6:1 D6:2",
         8: "C6:1 [Bb5 Ab5 G5] F5:1",
         9: "G5:1 Ab5:1 B5:.667 C6:hold"},
    counter={1: "C5:3", 2: "C5:3", 3: "C5:3", 4: "Eb5:3", 5: "D5:3", 6: "C5:3", 7: "B4:3", 8: "C5:3", 9: "B4:2 D5:1", 10: "Eb5:3", 11: "Eb5:1 D5:hold"},
    dyn=DYN_STD, accomp_text=ACC + "; bass is a C pedal for bars 0-7 (music-box drone), then Ab-G-G-C",
    counter_text="inner sustained reed line (like the original's held inner tones): Eb-D-C-B under the climb to the climax, "
                 "in contrary motion to the melody, then back to Eb/D under the held tonic",
    instruments={"lead": "tremolo-reed lead (tini R1/R2: harmonica pair or tango accordion + harmonica); preview: FluidR3 accordion P21 + harmonica P22 +16 c",
                 "accomp": "accordion/harmonium pa swells (preview P21) + reed organ bed (P20)", "counter": "soft second reed (preview P23)"},
    notes_text="A music box being wound in a dark room. KEPT from the original: C minor, 3/4 at 152, the inverted um-pa-pa, a one-bar harmonic pendulum (tonic <-> leading-tone chord), a narrow childlike line, triplet 'spins', one cry near the golden section, an early tonic frozen over the still-turning pulse, and the leading-tone chord returning under the held tonic so the reel's loop resolves into bar 0. CHANGED: the pendulum is the full vii°7 (B-D-F-Ab) over a C pedal (no C-D bass), so every second bar carries the Ab-B augmented second, a hicaz colour from Turkish music that already lives inside C harmonic minor. The melody sits in the upper tetrachord G-Ab-B-C, not the original's C-D-Eb-F. HOOK (bars 0-2): 'do le | ti (do-ti-le) ti | do - sol'. The pickup jumps an augmented second up to the leading tone, a music-box turn ornaments it, and it resolves to C6 and drops to G. Bars 3-4 answer a third lower in the same ornament language. Bars 5-7 wind upward: B°7 arpeggio Ab-B-D, C6, then a rising triplet B-C-D into the single cry Eb6 at 57 %. Eb6 is a b13 over the dominant-function chord, a minor ninth against its D, and it sighs a semitone to D6 on the next beat. Bars 8-9 fall by step to F5 and wind back up G-Ab-B. C6 arrives a triplet early and is held over the pedal. The inner counter doubles the C pedal and then creeps Eb-D-C-B in contrary motion under the climb.")

# ----------------------------------------------------------------------------------------------------------- b2-2
P2 = dict(
    id="b2-2", title="Musette des ombres", tempo=152,
    harm={0: "Cm/C", 1: "Fm/F", 2: "Cm/C", 3: "Fm/F", 4: "Cm/C", 5: "Fm/F", 6: "Cm/C", 7: "Fm/F",
          8: "G7/G", 9: "Fm6/Ab | b2 G7/G", 10: "Cm+/C", 11: "Cm+/C | b2 Fm+"},
    mel={0: "@2 Eb5:1 G5:1",
         1: "F5:1.5 E5:.5 Ab5:1",
         2: "G5:1.5 F#5:.5 Eb5:1",
         3: "F5:1.5 E5:.5 Ab5:1",
         4: "G5:1 [F#5 G5 Ab5] Bb5:1",
         5: "Ab5:1.5 G5:.5 F5:1",
         6: "Bb5:1.5 A5:.5 G5:1",
         7: "Ab5:1 [G5 Ab5 Bb5] B5:1",
         8: "C6:1.5 B5:.5 [Ab5 G5 F5]",
         9: "Ab5:1.5 G5:.5 B5:.5 C6:hold"},
    counter={5: "F5:1.5 Eb5:.5 C5:1", 6: "G5:1.5 F#5:.5 Eb5:1", 7: "F5:1 [Eb5 F5 G5] Ab5:1",
             8: "Ab5:1.5 G5:.5 [F5 Eb5 D5]", 9: "F5:1.5 Eb5:.5 D5:.5 Eb5:hold"},
    dyn=DYN_STD, accomp_text=ACC + "; bass rocks C-F (i-iv, a fourth) instead of a neighbour step",
    counter_text="musette duo: a second reed in parallel thirds below the melody in bars 5-9 (the B-section lift), "
                 "ending on Eb5 under the held C6",
    instruments={"lead": "musette accordion (two detuned reeds; tini R2)", "accomp": "accordion bass/chords (P21) + reed bed (P20)",
                 "counter": "second musette reed (P23)"},
    notes_text="An old-European musette waltz heard from the next room. KEPT: C minor 3/4 at 152, inverted um-pa-pa, a strict one-bar pendulum, a narrow line, a cry at bar 8, an early held tonic. CHANGED: the pendulum is plagal, i <-> iv (Cm <-> Fm), with the bass leaping C-F. It is just as hypnotic, but it is not the original's dominant rocking. HOOK: a limping musette lilt, dotted quarter + eighth + quarter, with chromatic lower neighbours: 'fa. mi-natural le | sol. fi mi'. E-natural and F# are the classic musette appoggiaturas. F#->Eb is an augmented second, and the up-a-fourth (E->Ab) / down-a-third answer gives the cell a shape you can hum ('daa-di DAA | daa-di da'). It is stated twice (bars 1-3). B section: the lilt climbs a step at a time (G, Ab, Bb with an A-natural neighbour), and a rising triplet run G-Ab-Bb plus B leads into the cry C6 at bar 8. C6 is a fourth suspended over V7 and resolves a semitone to B5 on the half-beat, then falls through a triplet Ab-G-F. The cadence restates the lilt (Ab. G), and the leading tone resolves an eighth early to C6, held. A second reed plays the melody in parallel thirds in bars 5-9 (the musette duo), which gives the B section its lift. Under the held tonic, iv returns as a plagal ghost that resolves into the loop.")

# ----------------------------------------------------------------------------------------------------------- b2-3
P3 = dict(
    id="b2-3", title="Çingene Dansı (danse macabre)", tempo=152,
    harm={0: "Cm/C", 1: "Ger6/C", 2: "Cm/C", 3: "Ger6/C", 4: "Cm/C", 5: "Ger6/C", 6: "Cm/C", 7: "Ger6/C | b3 G7/G",
          8: "G7/G", 9: "Cm64/G | b2 G7", 10: "Cm/C", 11: "Cm/C | b2 Ger6"},
    mel={0: "@2 Eb5:1 F#5:1",
         1: "Ab5:1 [G5 F#5 G5] Ab5:1",
         2: "G5:1 Eb5:1 C5:1",
         3: "Eb5:1 [F#5 G5 F#5] Ab5:1",
         4: "G5:1 Eb5:1 C5:1",
         5: "C5:1 [Eb5 F#5 Ab5] F#5:1",
         6: "G5:1 Eb5:1 [F#5 G5 Ab5]",
         7: "B5:1 Ab5:1 G5:1",
         8: "Ab5:1 [G5 F5 Eb5] D5:1",
         9: "Eb5:1 F5:1 D5:.5 C5:hold"},
    counter={1: "Ab4:3", 2: "G4:3", 3: "F#4:3", 4: "G4:3", 5: "Ab4:3", 6: "G4:3", 7: "Ab4:2 G4:1", 8: "B4:3", 9: "B4:3",
             10: "C5:3", 11: "C5:hold"},
    dyn=DYN_STD, accomp_text=ACC + "; bass is a C pedal (hurdy-gurdy drone) under the i <-> German-sixth (Ab-C-Eb-F#) rocking, then G-G-C",
    counter_text="inner reed voice that spells the German-sixth split: G4 on tonic bars, Ab4 / F#4 on alternate sixth bars (G splits into its two neighbours), then the leading tone B4 under the cadence and C5 under the hold",
    instruments={"lead": "tremolo harmonica / musette reed (tini R1/R2)", "accomp": "accordion (P21) + reed bed (P20)",
                 "counter": "soft reed drone (P23)"},
    notes_text="A danse macabre with a gypsy fiddler. KEPT: C minor 3/4 at 152, inverted um-pa-pa, a one-bar pendulum over a fixed bass, triplet spins, one cry at 57 %, an anticipated held tonic, the pendulum chord under the hold. CHANGED: the mode is Hungarian (gypsy) minor, C D Eb F# G Ab B, with two augmented seconds. The pendulum is i <-> German sixth over a C pedal (Ab-C-Eb-F#): every second bar the tonic's G splits into its two chromatic neighbours, Ab and F#, an eerie shimmer, and an inner reed voice spells that split (G-Ab-G-F#-G). HOOK: 'mi fi | le (sol-fi-sol) le | sol mi do'. An augmented-second pickup leads into a gypsy turn around G, then a falling tonic arpeggio plants C every other bar. Bar 3 varies the turn on F#. Bar 5 spins up the diminished shape C-Eb-F#-Ab, and bar 6 spins F#-G-Ab into the cry. The melody leaps the augmented second Ab->B5 (B against the German sixth, a sob), falls back the augmented second to Ab and sighs a semitone to G as V7 arrives. It then descends by step Ab-G-F-Eb-D to C5, an eighth early, held. The German sixth returns under the held C. (An earlier nikriz version, C D Eb F# G A Bb, was dropped: its pitch set is G harmonic minor's, and the key estimator heard it in G minor, not C minor.)")

# ----------------------------------------------------------------------------------------------------------- b2-4
P4 = dict(
    id="b2-4", title="Kürdi Ninni (the sinking lullaby)", tempo=152,
    harm={0: "Cm/C", 1: "Cm/C", 2: "Db/Db", 3: "Cm/C", 4: "Db/Db", 5: "Cm/C", 6: "Db/Db",
          7: "F7/F | b2 Fm/F", 8: "G7/G", 9: "Db+/F | b2 G7/G", 10: "Cm/C", 11: "Cm/C | b2 Db"},
    mel={0: "@2 Eb5:1 F5:1",
         1: "G5:2 [Ab5 G5 Eb5]",
         2: "F5:2 [G5 F5 Db5]",
         3: "Eb5:2 [F5 Eb5 C5]",
         4: "Db5:1 F5:1 Ab5:1",
         5: "G5:2 [Eb5 F5 G5]",
         6: "F5:1 [Ab5 F5 Db5] Eb5:1",
         7: "A5:1 Ab5:1 [G5 F5 Eb5]",
         8: "D5:1 [Eb5 F5 Eb5] D5:1",
         9: "Db5:2 B4:.667 C5:hold"},
    counter={5: "C5:3", 6: "Db5:3", 7: "Eb5:1 C5:2", 8: "B4:3", 9: "Ab4:2 G4:1", 10: "G4:3", 11: "G4:1 Ab4:hold"},
    dyn=DYN_STD, accomp_text=ACC + "; bass rocks C-Db (a semitone 'creak', Phrygian i <-> bII) from bar 1, then F-G-F/G-C",
    counter_text="inner reed line Eb-F-Eb/C-B-Ab/G-G under the B section and cadence; Ab4 (in the bII chord) under the held tonic",
    instruments={"lead": "tremolo reed (tini R1)", "accomp": "accordion (P21) + reed bed (P20)", "counter": "reed (P23)"},
    notes_text="A cradle song that sinks (kurdi/Phrygian lullaby). KEPT: C minor 3/4 at 152, inverted um-pa-pa, a one-bar pendulum, a narrow line, triplet motion, one cry at 57 %, an early held tonic, the pendulum chord under the hold. CHANGED: the pendulum is Phrygian, i <-> bII (Cm <-> Db), with the bass creaking a semitone C-Db like a cradle. HOOK: the cradle rhythm, a long note then a triplet that rocks up and falls: 'sol - (le-sol-mi) | fa - (sol-fa-reb) | mi - (fa-mi-do)'. The long notes walk down the kurdi pentachord G-F-Eb-Db: a lullaby falling asleep. Bars 4-6 wake: a rising Db arpeggio and rising triplets, then the single cry, a tritone leap Eb5->A5 onto a 'wrong', bright A natural over F7 (Dorian IV7). It darkens a semitone to Ab on the next beat as the chord turns to Fm (IV->iv, the lullaby's last light going out). The line then falls by step through G-F-Eb-D to the Neapolitan cadence Db-B-C (b2 -> 7 -> 1), with the tonic a triplet early and held. Db returns under the held C, so the loop restarts on the creak.")

PIECES = [P1, P2, P3, P4]
