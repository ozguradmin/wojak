"""exploration only: python3 dene.py <variant> [...] -> var/<variant>.json + key reads over seeds in two engines
(b1's FluidR3 preview, b1lib.render_preview, seeds 1-3; motor/hibrit/render.py, seeds 1-4). Prints mean C-minor r,
mean G-major r and best key per seed, for the whole clip and for bars 6-9."""
import copy, json, os, subprocess, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SP = "/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2"
sys.path.insert(0, os.path.join(SP, "besteler", "b1", "py"))
sys.path.insert(0, HERE)
import b1lib as L, parca
import anahtar as K
import scipy.signal as ss, librosa
sys.path.insert(0, os.path.join(SP, "olcum"))
import olcum as O

VAR = os.path.join(HERE, "var")
os.makedirs(VAR, exist_ok=True)
BASE = parca.P["b1-4"]

V = {
    "orig": {},
    "A": dict(chords=["Cm", "Cm", "Ab/C Ab/C Cm", "Cm", "Ab/C Ab/C Cm", "Fm", "Ab/C Cm F#dim7/C", "F#dim7/C", "G7",
                      "Dm7b5/F G7 -", "Cm", "G7b9"],
              counter=["", "", "", "", "", "C5:3", "C5:2 Eb5:1", "Eb5:1.5 C5:1.5", "B4:3", "C5:1 D5:1 G4:1", "Eb4:3",
                       "F4:2.8"]),
}
# B: A + cadential 6/4 in bar 8 (melody D5 -> Eb5 on beat 2, counter 4-3 suspension C5 -> B4)
V["B"] = copy.deepcopy(V["A"])
V["B"]["chords"][8] = "Cm/G Cm/G G7"
V["B"]["counter"][7] = "Eb5:1.5 C5:3.5"
V["B"]["counter"][8] = "B4:1"
V["B"]["melody"] = list(BASE["melody"]); V["B"]["melody"][8] = "G5:t F5:t G5:t Eb5 F5"
# C: only fixes (a)+(c) with F#dim7/C, bars 2/4 untouched (to see what fix (b) costs the key read)
V["C"] = copy.deepcopy(V["A"])
V["C"]["chords"][2] = "Ab/C"; V["C"]["chords"][4] = "Ab/C"


def piece(name):
    P = copy.deepcopy(BASE)
    P.update(copy.deepcopy(V[name]))
    P["id"] = "var-" + name
    return P


def prof_of(wav, a=0.0, b=13.77):
    y = O.decode(wav)[: int(O.WIN_S * O.SR)]
    mid = (y[:, 0] + y[:, 1]) / 2
    ch = librosa.feature.chroma_cqt(y=ss.resample_poly(mid, 1, 2), sr=22050)
    t = np.arange(ch.shape[1]) * 512 / 22050
    return ch[:, (t >= a) & (t < b)].mean(1)


def reads(wav):
    out = {}
    for nm, (a, b) in (("all", (0, 13.77)), ("b6-9", (17 * K.BS, 29 * K.BS)), ("b1-5", (2 * K.BS, 17 * K.BS))):
        ks, d = K.rank(prof_of(wav, a, b))
        out[nm] = (d["C min"], d["G maj"], ks[0][1])
    return out


def main():
  for name in sys.argv[1:]:
    J = L.build(piece(name))
    jp = os.path.join(VAR, name + ".json")
    json.dump(J, open(jp, "w"), ensure_ascii=False, indent=1)
    res = {"prev": [], "hib": []}
    for s in (1, 2, 3):
        w = os.path.join(VAR, f"{name}_prev_s{s}.wav")
        L.render_preview(J, w, seed=s)
        res["prev"].append(reads(w))
    for s in (1, 2, 3, 4):
        w = os.path.join(VAR, f"{name}_hib_s{s}.wav")
        subprocess.run(["python3", os.path.join(SP, "motor", "hibrit", "render.py"), jp, w, "--seed", str(s)],
                       capture_output=True, text=True, check=True)
        res["hib"].append(reads(w))
    for eng, rr in res.items():
        line = f"{name:5s} {eng}: "
        for nm in ("all", "b6-9", "b1-5"):
            cm = np.mean([r[nm][0] for r in rr]); gm = np.mean([r[nm][1] for r in rr])
            line += f"[{nm} Cmin {cm:.2f} Gmaj {gm:.2f} best {','.join(r[nm][2] for r in rr)}]  "
        print(line, flush=True)


if __name__ == "__main__":
    main()
