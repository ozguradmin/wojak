"""python3 hibrit_anahtar.py <melody.json> [...]: render each through motor/hibrit/render.py (current version, default
recipe) at seeds 1-4 into duzeltme/hibrit/, and print the key read (olcum's method) per seed and on average."""
import os, subprocess, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SP = "/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2"
sys.path.insert(0, HERE)
from dene import reads

OUT = os.path.join(HERE, "hibrit")
os.makedirs(OUT, exist_ok=True)
for jp in sys.argv[1:]:
    pid = os.path.splitext(os.path.basename(jp))[0]
    rr = []
    for s in (1, 2, 3, 4):
        w = os.path.join(OUT, f"{pid}_s{s}.wav")
        subprocess.run(["python3", os.path.join(SP, "motor", "hibrit", "render.py"), jp, w, "--seed", str(s)],
                       capture_output=True, text=True, check=True)
        rr.append(reads(w))
    line = f"{pid:7s} hibrit s1-4: "
    for nm in ("all", "b6-9", "b1-5"):
        cm = np.mean([r[nm][0] for r in rr]); gm = np.mean([r[nm][1] for r in rr])
        line += f"[{nm} Cmin {cm:.2f} Gmaj {gm:.2f} best {','.join(r[nm][2] for r in rr)}]  "
    print(line, flush=True)
