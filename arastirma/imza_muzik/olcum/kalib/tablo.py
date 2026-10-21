import json, os, sys
K=os.path.dirname(os.path.abspath(__file__))
rows=[('orijinal','the original itself'),('kopya_aac128','re-encode AAC-LC 128k'),('kopya_mp3128','re-encode MP3 128k'),('kopya_tools','tools copy (orijinal_kopya.m4a)'),
('orijinal_p2','original +2 semitones (rubberband)'),('orijinal_m1','original -1 semitone'),('orijinal_tempo103','original tempo +3 %'),
('orijinal_10klik','original + 10 clicks (-40..-22 dBFS)'),('orijinal_hiss55','original + hiss -55 dBFS'),
('red_imza','rejected imza_vals.m4a'),('red_ikinci','rejected imza_vals_ikinci.m4a'),('red_ucuncu','rejected imza_vals_ucuncu.m4a'),
('ilgisiz_gece_vals','unrelated imza_gece_vals.mp3'),('kapak_orijinal_fluid','COVER: original melody+harmony, FluidR3 + chain'),
('red_imza_fluid','imza melody, FluidR3 + chain'),('red_ikinci_fluid','ikinci melody, FluidR3 + chain'),('red_ucuncu_fluid','ucuncu melody, FluidR3 + chain')]+[(f'rastgele{i}',f'random melody {i}, FluidR3 + chain ('+('orig. harmony' if i<3 else 'other harmony')+')') for i in range(6)]
print('| file | what | TIMBRE | chroma (tools) | chroma T+tempo | fingerprint | audio | symbolic | LUFS | TP | clicks | tempo | key | onsets/bar |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
for n,w in rows:
    p=os.path.join(K,'sonuc',n+'.json')
    if not os.path.exists(p): continue
    j=json.load(open(p)); o=j['originality']; t=j['technical']; m=j['musical']
    sym=o.get('symbolic',{}).get('verdict','-')
    print(f"| {n} | {w} | {j['TIMBRE_SCORE']:.1f} | {o['chroma_seq_sim']['value']:.3f} | {o['chroma_seq_sim_transposed']['value']:.3f} | {o['fingerprint_match']['value']:.3f} | {o['audio_verdict']} | {sym} | {t['lufs_integrated']['value']} | {t['true_peak_dbtp']['value']} | {t['clicks']['value']} | {m['tempo_bpm']['value']} | {m['key']['value']} | {m['onsets_per_bar']['value']:.1f} |")
print()
keys=list(json.load(open(os.path.join(K,'sonuc','orijinal.json')))['timbre_subscores'])
print('| file | '+' | '.join(keys)+' |'); print('|---|'+'---|'*len(keys))
for n,w in rows:
    p=os.path.join(K,'sonuc',n+'.json')
    if not os.path.exists(p): continue
    j=json.load(open(p)); s=j['timbre_subscores']
    print(f"| {n} | "+' | '.join(f"{s[k]['score']:.0f}" for k in keys)+' |')
