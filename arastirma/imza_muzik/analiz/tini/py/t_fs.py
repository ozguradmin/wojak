import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/analiz/tini/py')
from fsr import render_layers
import numpy as np
y=render_layers([dict(prog=21)],[(0.05,2.0,72,100)],2.5)
print(len(y),np.abs(y).max(),20*np.log10(np.sqrt(np.mean(y[4410:88200]**2))))
