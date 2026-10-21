"""b1-4d: the melody judge's fixes applied to b1-4 "Gölge" (YARGI.md §4, §5).

    python3 b1_4d.py [--no-render]

Builds the piece with b1's own toolkit (b1/py/b1lib.py, same notation and conventions as b1/py/parca.py), saves
b1/b1-4d.json, renders the same FluidR3 preview b1 used (b1lib.render_preview) to b1/b1-4d.wav and runs olcum.py
(b1/b1-4d_olcum.json, b1/b1-4d.png). b1's files are imported, never edited.
"""
import copy, json, os, subprocess, sys, time

SP = "/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2"
sys.path.insert(0, os.path.join(SP, "besteler", "b1", "py"))
import b1lib as L, parca

P = copy.deepcopy(parca.P["b1-4"])
P["id"] = "b1-4d"
P["title"] = "Gölge (shadow), rev. d"

# melody: one note changes (bar 8 beat 2 D5 -> Eb5, for the cadential 6/4); the judge's three slips are fixed in the
# harmony / bass / counter
assert P["melody"][6] == "Ab5 G5 F#5:t G5:t A5:t" and P["melody"][7] == "Bb5 A5 F#5"
assert P["melody"][8] == "G5:t F5:t G5:t D5 F5"
P["melody"][8] = "G5:t F5:t G5:t Eb5 F5"   # 8  Eb (the hook's 'u' note) over i6/4; Eb F | Ab G recalls the hook

P["chords"] = [
    "Cm", "Cm",
    "Ab/C Ab/C Cm",          # 2  fix (b): beat 3 -> i, so the sigh's G5 lands on a chord tone (was G5 over Ab4)
    "Cm",
    "Ab/C Ab/C Cm",          # 4  fix (b), same
    "Fm",                    # 5
    "Ab/C Cm F#dim7/C",      # 6  fix (a): VI6 over the C pedal (no F5/F2 -> Ab5/Ab2 octaves); beat 2 -> i under G5
                             #    (the same G-over-Ab rub as (b)); beat 3: vii°7/V over the C pedal instead of D7/F#
    "F#dim7/C",              # 7  fix (c) + key: the cry Bb5 -> A5 over the diminished seventh on the tonic pedal;
                             #    no F# in the bass, no D-major triad
    "Cm/G Cm/G G7",          # 8  key: cadential 6/4 -> V7 (vii°7/V -> i6/4 -> V7), 2 fewer beats of G7
    "Dm7b5/F G7 -",          # 9
    "Cm", "G7b9",            # 10-11 hold, unchanged
]
P["counter"] = [
    "", "", "", "", "",
    "C5:3",                  # 5
    "C5:2 Eb5:1",            # 6  Eb (chord tone of the diminished seventh) instead of D
    "Eb5:1.5 C5:3.5",        # 7  Eb -> C over the diminished; C held over the bar line as the 6/4's fourth ...
    "B4:1",                  # 8  ... and resolved to B when V7 arrives (4-3)
    "C5:1 D5:1 G4:1",        # 9
    "Eb4:3",                 # 10 the tonic's minor third under the held C5 (was G4)
    "F4:2.8",                # 11
]

P["notes_text"] = parca.TEXT["b1-4"].replace(
    "and a chromatic lift F#-G-A (bar 6) into the cry: Bb5 over a 'Hungarian' V7/V (D7 with b13) at 7.9 s, falling a "
    "semitone to A5",
    "and a chromatic lift F#-G-A (bar 6) into the cry: Bb5 over the diminished seventh F#-A-C-Eb on the tonic pedal "
    "at 7.9 s, falling a semitone to A5").replace(
    "After a lower-neighbour turn over V7,", "After a lower-neighbour turn over the cadential 6/4 and V7,") + (
    " Revision d (melody judge's fixes, YARGI.md): the chord now sighs with the melody (VI6 -> i under Ab -> G in bars "
    "2, 4 and 6); the C pedal stays under bars 6-7, so the climax's diminished seventh (vii°7/V, a rootless D7b9) "
    "sits on the tonic and resolves straight to V7 in bar 8; the counter takes Eb instead of D in bars 6-7 and under "
    "the held tonic; bar 8 is a cadential 6/4 (Eb5 in the melody, the hook's 'u' note) before V7.")
P["revision"] = {
    "of": "b1-4",
    "by": "melody-judge fix pass (DUZELTME.md)",
    "changes": [
        "bars 2 and 4, beat 3: VI6 -> i (C-Eb-G), so the hook's G5 is a chord tone on the bright beat (was G5 against Ab4)",
        "bar 6: Ab (Ab2 bass) -> Ab/C (C bass); removes the outer-voice octaves F5/F2 -> Ab5/Ab2 on the bar 5->6 downbeats",
        "bar 6 beat 2: Ab -> Cm under G5 (the same G-against-Ab rub as bars 2/4)",
        "bar 6 beat 3 + bar 7: D7/F# (V7/V 6/5) -> F#dim7/C (vii°7/V over the tonic pedal); the F#2 bass that the melody "
        "doubled into G is gone, and the D-major sonority that tonicised G is replaced by C and Eb",
        "bar 8: G7 -> Cm/G (beats 1-2, cadential 6/4) + G7 (beat 3); melody bar 8 beat 2 D5 -> Eb5 (the only melody "
        "change); the counter holds C5 over the bar line and resolves it to B4 on beat 3 (4-3)",
        "counter bars 6-7: D5 -> Eb5 (chord tone of the new diminished seventh); bar 10: G4 -> Eb4 under the held C5",
    ],
}


def main(render=True):
    t0 = time.time()
    J = L.build(P)
    J["revision"] = P["revision"]
    s, ol, cc = L.symcheck(J)
    print("stats", json.dumps(L.stats(J)))
    print("sym  ", json.dumps(L.brief(s, ol, cc), default=str))
    jp = L.save(J)
    print("saved", jp)
    if not render:
        return
    wav = os.path.join(L.OUT, "b1-4d.wav")
    _, I = L.render_preview(J, wav, lead_layers=P.get("lead_layers"))
    png = os.path.join(L.OUT, "b1-4d.png")
    r = subprocess.run(["python3", os.path.join(SP, "olcum", "olcum.py"), wav, "--notalar", jp, "--png", png],
                       capture_output=True, text=True)
    out = json.loads(r.stdout)
    json.dump(out, open(os.path.join(L.OUT, "b1-4d_olcum.json"), "w"), indent=1, ensure_ascii=False)
    print("render+measure %.0f s, LUFS %.1f" % (time.time() - t0, I))
    print("wav", wav, "png", png)


if __name__ == "__main__":
    main(render="--no-render" not in sys.argv)
