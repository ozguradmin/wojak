"""FluidR3 render helper (analysis probes only)."""
import numpy as np, fluidsynth
SF='/usr/share/sounds/sf2/FluidR3_GM.sf2'
SR=44100
_cache={}
def render(layers,notes,total,tune_c=-23.0,sr=SR):
    """layers: list of dict(prog, gain_db=0, detune_c=0, bank=0, vel_scale=1)
       notes: list of (start_s, dur_s, midi, vel)
       returns mono float64"""
    fs=fluidsynth.Synth(gain=0.5,samplerate=float(sr),**{'synth.reverb.active':0,'synth.chorus.active':0,'synth.polyphony':256})
    sfid=fs.sfload(SF)
    for ch,L in enumerate(layers):
        fs.program_select(ch,sfid,L.get('bank',0),L['prog'])
        c=tune_c+L.get('detune_c',0.0)
        fs.pitch_bend(ch,int(round(c/200.0*8192)))
        fs.cc(ch,7,127); fs.cc(ch,11,127); fs.cc(ch,91,0); fs.cc(ch,93,0)
    ev=[]
    for st,du,m,v in notes:
        ev.append((st,1,m,v)); ev.append((st+du,0,m,v))
    ev.sort(key=lambda e:(e[0],e[1]))   # offs before ons at same time
    out=[]; t=0.0
    for et,on,m,v in ev:
        n=int(round((et-t)*sr))
        if n>0: out.append(np.array(fs.get_samples(n),dtype=np.float64)); t+=n/sr
        for ch,L in enumerate(layers):
            if on: fs.noteon(ch,m,int(np.clip(v*L.get('vel_scale',1.0),1,127)))
            else: fs.noteoff(ch,m)
    n=int(round((total-t)*sr))
    if n>0: out.append(np.array(fs.get_samples(n),dtype=np.float64))
    fs.delete()
    a=np.concatenate(out).reshape(-1,2)/32768.0
    # layer gains: render each layer separately would be cleaner; we apply gain via separate renders
    return a.mean(1)
def render_layers(layers,notes,total,tune_c=-23.0):
    out=None
    for L in layers:
        y=render([L],notes,total,tune_c)*10**(L.get('gain_db',0)/20)
        out=y if out is None else out[:len(y)]+y[:len(out)]
    return out
