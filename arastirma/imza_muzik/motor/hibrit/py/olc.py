"""run olcum.py on a wav, print compact subscores (and save PNG)."""
import json, subprocess, sys, os
O="/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/olcum/olcum.py"
def run(wav, png=None, full=False):
    wav=os.path.abspath(wav); png=os.path.abspath(png) if png else None
    cmd=["python3",O,wav]+(["--png",png] if png else [])+([] if full else ["--ozet"])
    p=subprocess.run(cmd,capture_output=True,text=True,cwd=os.path.dirname(O))
    try: return json.loads(p.stdout)
    except Exception: print(p.stdout[-2000:],p.stderr[-2000:]); raise
def line(o):
    s=o.get("sub") or {k:v["score"] for k,v in o["timbre_subscores"].items()}
    return f"TS {o['TIMBRE_SCORE']:5.1f} | "+" ".join(f"{k[:5]}={v:.0f}" for k,v in s.items())
if __name__=="__main__":
    w=sys.argv[1]; png=sys.argv[2] if len(sys.argv)>2 else None
    o=run(w,png); print(line(o))
    if "--json" in sys.argv: print(json.dumps(o,indent=1)[:3000])
