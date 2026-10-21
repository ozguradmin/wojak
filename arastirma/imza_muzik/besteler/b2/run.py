"""python3 run.py [check|render|harness] [ids...]"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b2lib as L
import importlib
import pieces as PC

what = sys.argv[1] if len(sys.argv) > 1 else "check"
ids = sys.argv[2:]
for P in PC.PIECES:
    if ids and P["id"] not in ids:
        continue
    J = L.build(P)
    base = os.path.join(L.OUT, P["id"])
    if what in ("check", "render", "harness"):
        L.report_sym(J)
    if what in ("render", "harness"):
        json.dump(J, open(base + ".json", "w"), indent=1, ensure_ascii=False)
        L.render(J, base + ".wav")
        print("   wrote", base + ".wav")
    if what == "harness":
        s, o = L.harness(base + ".wav", base + ".json", base + ".png")
        print("   HARNESS", json.dumps(s, ensure_ascii=False))
