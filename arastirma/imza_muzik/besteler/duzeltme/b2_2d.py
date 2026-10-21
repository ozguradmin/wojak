"""b2-2d: the melody judge's fixes applied to b2-2 "Musette des ombres" (YARGI.md §4, §5).

    python3 b2_2d.py [check|render|harness]      (default harness)

Built with b2's own toolkit (b2/b2lib.py, same bar notation and conventions as b2/pieces.py); writes b2/b2-2d.json,
renders b2's FluidR3 preview (b2lib.render, which carries the FluidSynth same-pitch note-off fix that the new
re-struck notes need) to b2/b2-2d.wav and runs olcum.py (b2/b2-2d.olcum.json, b2/b2-2d.png). b2's files are imported,
never edited.
"""
import copy, json, os, sys

SP = "/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2"
sys.path.insert(0, os.path.join(SP, "besteler", "b2"))
import b2lib as L
import pieces as PC

P = copy.deepcopy(PC.P2)
assert P["id"] == "b2-2"
P["id"] = "b2-2d"
P["title"] = "Musette des ombres (rev. d)"

# fix 1: bar 7 beat 3, B5 sat over iv for a full beat -> vii°7 (B-D-F-Ab) on that beat. Fm -> B°7 keeps F and Ab,
# moves C -> B under the melody's B5 and adds D; B°7 -> G7 in bar 8 then keeps B, D, F (Ab -> G). The bass stays F
# (no new um on beat 3), so the i <-> iv pendulum of bars 0-7 is kept bar for bar.
assert P["harm"][7] == "Fm/F"
P["harm"][7] = "Fm/F | b3 B07"

# fix 2: the "a" on beat 2. In the hook statement (bars 1-3) the limp (dotted quarter + eighth) stays exactly as it is;
# in the sequenced B-section pair (bars 5-6) the long note is re-struck on beat 2 (quarter + eighth + eighth), in the
# melody and in the second reed's parallel thirds, so the melody now attacks beat 2 in bars 4-7 (was 4 and 7 only).
assert P["mel"][5] == "Ab5:1.5 G5:.5 F5:1" and P["mel"][6] == "Bb5:1.5 A5:.5 G5:1"
P["mel"][5] = "Ab5:1 Ab5:.5 G5:.5 F5:1"
P["mel"][6] = "Bb5:1 Bb5:.5 A5:.5 G5:1"
assert P["counter"][5] == "F5:1.5 Eb5:.5 C5:1" and P["counter"][6] == "G5:1.5 F#5:.5 Eb5:1"
P["counter"][5] = "F5:1 F5:.5 Eb5:.5 C5:1"
P["counter"][6] = "G5:1 G5:.5 F#5:.5 Eb5:1"

P["notes_text"] = PC.P2["notes_text"] + (
    " Revision d (melody judge's fixes, YARGI.md): bar 7's last beat is now vii°7 (B-D-F-Ab over the F bass) under the "
    "leading tone B5, so the triplet run lands on the diminished seventh and moves to the cry over V7 by common tones; "
    "in the B-section sequence (bars 5-6) the lilt's long note is re-struck on beat 2 (Ab | Ab-G | F, Bb | Bb-A | G), "
    "melody and second reed together, so the waltz's bright 'a' on 2 is in the melody through the build-up. The hook "
    "statement in bars 1-3, the cry and the cadence are unchanged.")
REVISION = {
    "of": "b2-2",
    "by": "melody-judge fix pass (DUZELTME.md)",
    "changes": [
        "bar 7 beat 3: iv (Fm) -> vii°7 (B-D-F-Ab), bass F kept; B5 is now a chord tone instead of sitting over iv",
        "bars 5-6: melody Ab5:1.5 G5:.5 F5:1 | Bb5:1.5 A5:.5 G5:1 -> Ab5:1 Ab5:.5 G5:.5 F5:1 | Bb5:1 Bb5:.5 A5:.5 G5:1 "
        "(the long note re-struck on beat 2); the counter's parallel thirds get the same rhythm",
        "everything else (hook bars 1-3, the i <-> iv pendulum, the triplet run, the C6 cry, the cadence, the hold) unchanged",
    ],
}


def main(what):
    J = L.build(P)
    J["revision"] = REVISION
    base = os.path.join(L.OUT, P["id"])
    L.report_sym(J)
    if what in ("render", "harness"):
        json.dump(J, open(base + ".json", "w"), indent=1, ensure_ascii=False)
        print("   wrote", base + ".json")
        L.render(J, base + ".wav")
        print("   wrote", base + ".wav")
    if what == "harness":
        s, o = L.harness(base + ".wav", base + ".json", base + ".png")
        print("   HARNESS", json.dumps(s, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "harness")
