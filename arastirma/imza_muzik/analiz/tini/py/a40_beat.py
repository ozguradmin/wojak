import numpy as np, sys, soundfile as sf
sys.path.insert(0,'/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/analiz/tini/py')
from fsr import render_layers
D='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/analiz/tini'
for p in [21,23,22,20]:
    x=render_layers([dict(prog=p)],[(0.05,3.0,72,100)],3.3)
    sf.write(D+f'/wav/dry_P{p}_C5.wav',x,44100)
