"""python3 olustur.py b1-1 [...]: build JSON, render the FluidR3 preview wav, run olcum.py (+png), print a summary"""
import sys, json, os, subprocess, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b1lib as L, parca
OL = os.path.join(L.SP, 'olcum', 'olcum.py')
for pid in sys.argv[1:]:
    t0 = time.time()
    J = L.build(parca.P[pid])
    s, ol, cc = L.symcheck(J)
    jp = L.save(J)
    wav = os.path.join(L.OUT, pid + '.wav')
    _, I = L.render_preview(J, wav, lead_layers=parca.P[pid].get('lead_layers'))
    png = os.path.join(L.OUT, pid + '.png')
    r = subprocess.run(['python3', OL, wav, '--notalar', jp, '--png', png], capture_output=True, text=True)
    out = json.loads(r.stdout)
    json.dump(out, open(os.path.join(L.OUT, pid + '_olcum.json'), 'w'), indent=1, ensure_ascii=False)
    og = out['originality']; sy = og.get('symbolic', {})
    print(pid, 'render+measure %.0fs' % (time.time() - t0), 'LUFS', round(I, 1))
    print('  VERDICT', out['originality_verdict'], '| audio', og['audio_verdict'], og['audio_reasons'], og['audio_warnings'],
          '| symbolic', sy.get('verdict'), sy.get('reasons'))
    print('  chroma(tools) %.3f  chroma_T %.3f  fingerprint %.4f' % (og['chroma_seq_sim']['value'], og['chroma_seq_sim_transposed']['value'], og['fingerprint_match']['value']))
    print('  POV', sy['offlimits']['POV'], 'viol', sy['offlimits']['violations'], 'ng3m', sy['ngram3_metric']['share'], 'ng4f', sy['ngram4_free']['share'],
          'cbar', sy['contour_bar_corr']['value'], 'cphr', sy['contour_phrase_corr']['value'], 'rhy', sy['rhythm_distinctive_same_bar'])
    print('  TIMBRE', out['TIMBRE_SCORE'], {k: v['score'] for k, v in out['timbre_subscores'].items()})
    print('  tech', out['technical_checks'])
