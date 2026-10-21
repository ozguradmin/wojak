"""python3 kontrol.py b1-1 [b1-2 ...] : build JSON, print stats + symbolic checks (no audio)"""
import sys, json, importlib
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import b1lib as L, parca
importlib.reload(parca)
for pid in sys.argv[1:]:
    J = L.build(parca.P[pid])
    s, ol, cc = L.symcheck(J)
    print(pid, json.dumps(L.stats(J)))
    print('  ', json.dumps(L.brief(s, ol, cc), default=str))
    print('   bars:', ' | '.join(f"{n['bar']}.{n['beat']:g}:{n['midi']}" for n in J['notes'])[:600])
    if '--save' in sys.argv[0:] or True:
        L.save(J)
