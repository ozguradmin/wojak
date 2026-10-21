"""detailed key metrics candidate vs original from olcum full JSON"""
import json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from olc import run
def show(o):
    T=o['timbre']; X=o['technical']; M=o['musical']
    def g(d,k,sub=None):
        v=d[k]; return v
    keys=['flatness','noise_floor','modulation','vibrato_rms_c','pitch_instability_c','partial_spread_c','texture_peaks_per_frame','stereo_lr_corr','reverb_ir_env_db','level_std_100ms_db','level_fast_fluct_db','crest_50ms_db','accent_uaa','centroid_hz','mfcc_dist','mel_env_dist_db']
    for k in keys:
        if k not in T: continue
        v=T[k]; extra={kk:vv for kk,vv in v.items() if kk not in ('value','original','desc')}
        val=v['value']; ori=v['original']
        if isinstance(val,list): val=[round(x,1) if isinstance(x,float) else x for x in val]
        if isinstance(ori,list): ori=[round(x,1) if isinstance(x,float) else x for x in ori]
        if isinstance(val,dict): val={a:round(b,2) for a,b in val.items()}
        if isinstance(ori,dict): ori={a:round(b,2) for a,b in ori.items()}
        ex=' '.join(f'{a}={json.dumps(b)[:60]}' for a,b in extra.items() if a!='diff_by_band_db')
        print(f'{k:24s} {json.dumps(val)[:110]}\n{"":24s} {json.dumps(ori)[:110]}   {ex[:200]}')
    for k in ['lra_lu','first_sound_s','last_sound_s','true_peak_dbtp']:
        print(k, X[k]['value'], X[k]['original'])
    for k in ['onsets_per_bar','legato_gap_fraction','tempo_bpm','key']:
        if k in M: print(k, M[k]['value'], M[k]['original'], {a:b for a,b in M[k].items() if a not in('value','original','desc')})
if __name__=='__main__':
    o=run(sys.argv[1], sys.argv[2] if len(sys.argv)>2 else None, full=True)
    s={k:v['score'] for k,v in o['timbre_subscores'].items()}
    print(f"TS {o['TIMBRE_SCORE']:5.1f} | "+" ".join(f"{k[:5]}={v:.0f}" for k,v in s.items()))
    show(o)
