import json, numpy as np
D='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/analiz'; T=D+'/tini'
lt=json.load(open(T+'/ltas.json')); singles=json.load(open(T+'/singles.json')); combos=json.load(open(T+'/combos.json'))
rec=json.load(open(T+'/recipes.json')); orig=json.load(open(T+'/orig_feat.json')); rev=json.load(open(T+'/revfit3.json'))[0]
bands=lt['bands']
eq=[[b,round(v,1)] for b,v in zip(bands,lt['ltas_rel'])]
floor=[[b,round(v,1)] for b,v in zip(bands,lt['floor_p10_dbfs']) if v>-199]
def rank(rows):
    out=[]
    for r in rows:
        dcen=abs(np.log2(r['centroid']/orig['centroid']))*12
        out.append(dict(id=r['id'],name=r.get('name',r['id']),score=round(r['score'],2),score_with_brightness=round(r['score']+0.5*dcen,2),
                        env_resid_db=round(r['env_rms'],2),odd_even_db=round(r['oe'],1),am_std_db=round(r['am'],2),fm_std_c=round(r['fm'],1),centroid_hz=round(r['centroid'])))
    return sorted(out,key=lambda x:x['score_with_brightness'])
sr=rank(singles); cr=rank(combos)
PNG=lambda n: f'{T}/png/{n}'
J=dict(
 source=dict(file='/home/user/wojak/assets/music/ozel/kanal_orijinal_ses.m4a',codec='HE-AAC v1 (SBR) 70 kb/s stereo 44.1 kHz',
   note='content above ~5 kHz is SBR-reconstructed (noise-like, no harmonic peaks); valleys above 4 kHz quantised to <= -108 dBFS; side channel below ~120 Hz is zero (mono LF)',
   start='sound already present at 0.000 s (excerpt starts mid-sound, -42 dB RMS in first 10 ms)', end='hard cut at 13.735 s (-41.9 -> -58 dB within 10 ms), no free decay',
   tuning=dict(a4_hz=434.5,offset_cents=-21,detail='C5 516.3 Hz (-23 c), C4 258.2 (-23 c), G4 387-389 (-14..-20 c), D5 583 (-12 c), Eb5 618 (-11 c), Ab5 818 (-27 c); consistent with old A=435 pitch')),
 eq_curve=eq, eq_curve_note='1/3-octave LTAS of the mid channel, dB re loudest band (1.6 kHz). This is a TARGET LTAS for a >=1/3-oct match EQ on the full arrangement, not a filter. Peaks 630 Hz and 1.6-2 kHz, dip 0.8-1.25 kHz; 250->200 Hz band drops 12.5 dB; above 2.5 kHz falls ~-24 dB/oct to 4 kHz then ~-30 dB/oct; 8-20 kHz is codec SBR.',
 eq_curve_dbfs=[[b,round(v,1)] for b,v in zip(bands,lt['ltas_dbfs'])],
 noise_floor=dict(per_band_upper_bound_dbfs=floor,
   note='10th-percentile inter-harmonic valley power per 1/3-oct band (dBFS, sine-referenced). In 250-3150 Hz this is an UPPER BOUND (valleys are filled by accompaniment partials and room), not hiss. Above 4 kHz valleys are <= -108 dBFS (codec), so no broadband hiss is measurable.',
   hiss='not detectable; upper bound about -64 dBFS per 1/3-oct band in 250-3150 Hz; recommend <= -80 dBFS (sine-ref RMS, 250-4500 Hz) or none',
   hum=dict(lines_hz_dbfs_peak=[[100.0,-70.4],[150.0,-78.3],[200.0,-83.5],[250.0,-83.5],[50.0,-87.3]],stable='100.0 Hz constant within 0.5 Hz over the clip, level -69..-72 dBFS in 2 s windows (added after any speed effect)'),
   rumble=dict(band_hz=[1,25],rms_dbfs=-55.7,dominant_hz=7.6,mono=True,lr_corr=0.994,correlated_with_music=False),
   crackle=dict(clicks_per_s=0.0,kurtosis_4p5_11k=4.3,note='no impulsive clicks (LPC residual max z 7.8)'),
   level_dbfs_sine_ref=dict(music_250_4000=-31.7,lf_30_90=-69.2,band_100hz=-67.9,infrasonic=-55.7)),
 vibrato=dict(rate_hz=None,depth_cents=0,delay_s=None,detail='no periodic vibrato. Held C5 (11.75-12.70 s): FM std 7.5 c with a weak 4.5 Hz component (peak/median 3.0); other notes FM std 10-12 c without a peak. This includes ~4.4 c common wow and interference from accompaniment.'),
 pitch_inflections=[dict(t=[4.95,5.20],from_hz=640,to_hz=612,cents=-77,kind='falling scoop into Eb5'),dict(t=[8.45,8.65],from_hz=815,to_hz=848,cents=+69,kind='rising glide on the Ab5 climax, then held at 846-850 Hz'),dict(t=[12.6,12.9],from_hz=516,to_hz=529,cents=+44,kind='held tonic C5 drifts sharp')],
 tremolo=dict(am_std_db_held_C5=round(orig['am'],2),note='amplitude fluctuation of lead harmonics ~4-6 dB std (heterodyne, 60 Hz band). The chain alone (wow+room) gives only ~1 dB on a steady sample, so the modulation is in the source: it comes from beating (see beating), not from a tremolo LFO.'),
 beating=dict(model='two voices detuned (musette / tremolo reed)',held_C5=dict(beat_hz_fundamental=6.7,detune_cents=22,evidence='AM peaks h1 7.0, h3 20, h4 26.7, h5 33.4 Hz = k x 6.7 Hz'),Ab5=dict(beat_hz_fundamental=8.3,detune_cents=17,evidence='AM peaks h1 9.0, h3 24.7, h4 31.9 Hz'),
   confidence='moderate (clean on 2 of 5 notes; others masked by polyphony)',fluidR3_reference='P23 tango accordion sample is a 2-reed musette with ~15 c (4.5-4.8 Hz at C5); P21 accordion ~16 c with deeper beats (AM 8.4 dB)'),
 attack_release=dict(lead_entrance_rise_ms=45,legato='no level dip at melody note changes (median -2.8 dB vs -2.9 dB at random times) -> fully legato in the dense texture',
   pah_bursts=dict(attack_ms_median=48,attack_ms_range=[16,72],decay_to_minus10_ms_median=55,decay_range=[19,76],width_ms=[120,150],rise_over_background_db=[15,18]),end='hard cut'),
 inharmonicity='none measurable (harmonics at k*f0 within 0.4 %)',
 breath_bellows_noise='not separable from accompaniment; no evidence of broadband breath noise',
 formants=dict(fixed_peaks_hz=[630,1600,2000,2500],dip_hz=[800,1250],source_filter='a fixed-frequency envelope and a harmonic-number term (odd>even by 5-11 dB) both explain the data (resid 4.9 / 4.8 dB alone, 3.9 dB jointly)',
   u_a_a='"u a a" = rhythm/brightness, not a sung vowel: beat 1 centroid ~1070 Hz, beats 2-3 centroid ~1610 Hz and +8.3 dB'),
 odd_even=dict(index_db_mean=round(orig['oe'],1),per_note={k:round(v,1) for k,v in dict(C5=11.2,D5=10.8,Eb5=6.3,Ab5=5.1).items()},note='mean(h1,h3,h5,h7) - mean(h2,h4,h6,h8) after the chain; h3 is the strongest harmonic on D5/Eb5'),
 reverb=dict(type='short room / ambience, stereo-decorrelated, with a faint long tail',rt60_early_s=0.09,rt60_range_s=[0.08,0.15],predelay_ms=6,build_ms=4,late_tail=dict(level_db=-30,rt60_s=1.5),wet_db=-8,wet_band_hz=[150,4000],
   measured=dict(side_ir_db_vs_ms={'10':-3.8,'20':-0.7,'35':-5.6,'50':-15.7,'75':-24.6,'100':-26.8,'150':-28.2,'200':-27.9,'300':-35.2},side_lag_ms=25),
   fit_quality=dict(model_side_mid_db=[round(rev['stats'][k],1) for k in ('sm_250','sm_500','sm_1000','sm_2000')],orig_side_mid_db=[-8.1,-5.3,-6.1,-9.6],model_coh=[round(rev['stats'][k],2) for k in ('coh_250','coh_500','coh_1000','coh_2000')],orig_coh=[0.66,0.58,0.57,0.73]),
   note='system-identified from side vs mid (Welch cross-spectrum, 0.74 s); the late tail estimate is near the estimation floor'),
 saturation=dict(clipping=False,sample_peak_dbfs=[-18.0,-16.9],true_peak_dbtp=-16.8,crest_db=16.3,crest_50ms_median_db=9.9,estimate='none detectable; harmonic distortion cannot be separated from instrument harmonics -> use none or very mild'),
 stereo=dict(lr_corr=0.64,side_minus_mid_db=-6.6,per_band_side_mid_db={'20-250':-11.2,'250-500':-8.1,'500-1000':-5.3,'1000-2000':-6.1,'2000-4000':-9.6},coherence={'250-500':0.66,'500-1000':0.58,'1000-2000':0.57,'2000-4000':0.73},mono_below_hz=130,balance_db=[-1.6,1.4],
   interpretation='mono dry source + decorrelated stereo room; side lags mid by ~25 ms; side is -13 dB under mid at accents and -4 dB between them'),
 wow_flutter=dict(common_rms_cents=4.4,band_hz=[0.8,5.0],periodic=False,evidence='slow pitch deviations of simultaneous non-harmonically related partials correlate r=0.33 mean (0.42 median, n=255) vs r=0.00 null (n=6466); per-partial slow deviation 7.1 c std'),
 dynamics=dict(integrated_lufs=-29.5,lra_lu=3.6,rms_dbfs=dict(intro_0_4p6=-36.7,melody_4p9_11p5=-33.3,final_hold=-35.1),per_bar_rms_dbfs=[-37.0,-36.2,-38.0,-36.1,-32.2,-36.8,-32.8,-33.6,-33.1,-33.7,-34.4,-36.9],short_term_100ms_std_db=4.0,p10_p90_db=9.9),
 time_varying_filter='none found beyond the accent brightness changes (no sweep/wah)',
 layers=[
  dict(name='lead melody',when='4.94 s to end (bars 5-12); absent in bars 1-4',register='C5-Ab5, fundamentals 516-850 Hz',rhythm='legato, long notes (median partial track 0.26 s, longest ~1 s; final C5 held ~2 s)',timbre='free reed, 2 detuned voices (17-22 c), odd>even harmonics 5-11 dB, h3 strongest on D5/Eb5, centroid ~1.9 kHz',level='about +1 to +6 dB over the accompaniment (energy)',expression='pitch scoops/glides of 45-75 c on 3 long notes; no vibrato'),
  dict(name='accompaniment oom (beat 1)',register='visible partials 240-450 Hz (C4-A4); any fundamental below 250 Hz is removed by the EQ',rhythm='beat 1, ~0.3 s',timbre='dark: centroid ~1.07 kHz; 240-330 Hz band +5..+7 dB at downbeats'),
  dict(name='accompaniment pah-pah (beats 2-3)',register='chord tones C4-F5; tops C5/Eb5 and D5/F5 in bars 1-4',rhythm='staccato 120-150 ms swells, attack ~48 ms, decay ~55 ms',timbre='bright (3rd harmonics at 1.5-1.9 kHz rise 15-18 dB), +8.3 dB over beat 1',note='this is the "a a" of "u a a"'),
  dict(name='inner sustained tones',register='D4, F4, G4',rhythm='occasional holds 0.5-1.5 s (D4 1.05-2.1 s, G4 9.3-10.9 s)',timbre='same reed family'),
  dict(name='absent',items=['bass below 250 Hz (only hum/rumble there)','drums/percussion','pads/strings','voice','sfx'])],
 best_patches=sr[:14], best_combos=cr,
 best_recipes=[
  dict(rank=1,name='R1 tremolo harmonica (2 x FluidR3 P22)',layers=[dict(prog=22,gain_db=0,detune_c=0),dict(prog=22,gain_db=-3,detune_c=20)],tuning_cents=-23,
       metrics=dict(score=round(rec['R1_tremolo_harmonica']['score'],2),env_resid_db=round(rec['R1_tremolo_harmonica']['env_rms'],2),odd_even_db=round(rec['R1_tremolo_harmonica']['oe'],1),am_std_db=round(rec['R1_tremolo_harmonica']['am'],2),centroid_hz=round(rec['R1_tremolo_harmonica']['centroid'])),
       patch_eq_db=[[round(f),round(g,1)] for f,g in rec['R1_tremolo_harmonica']['eq_corr']]),
  dict(rank=2,name='R2 tango accordion + tremolo harmonica (P23 + P22)',layers=[dict(prog=23,gain_db=0,detune_c=0),dict(prog=22,gain_db=-2,detune_c=14)],tuning_cents=-23,
       metrics=dict(score=round(rec['R2_tango_plus_harmonica']['score'],2),env_resid_db=round(rec['R2_tango_plus_harmonica']['env_rms'],2),odd_even_db=round(rec['R2_tango_plus_harmonica']['oe'],1),am_std_db=round(rec['R2_tango_plus_harmonica']['am'],2),centroid_hz=round(rec['R2_tango_plus_harmonica']['centroid'])),
       patch_eq_db=[[round(f),round(g,1)] for f,g in rec['R2_tango_plus_harmonica']['eq_corr']]),
  dict(rank=3,name='R3 clarinet musette (2 x FluidR3 P71)',layers=[dict(prog=71,gain_db=0,detune_c=0),dict(prog=71,gain_db=0,detune_c=20)],tuning_cents=-23,
       metrics=dict(score=round(rec['R3_clarinet_musette']['score'],2),env_resid_db=round(rec['R3_clarinet_musette']['env_rms'],2),odd_even_db=round(rec['R3_clarinet_musette']['oe'],1),am_std_db=round(rec['R3_clarinet_musette']['am'],2),centroid_hz=round(rec['R3_clarinet_musette']['centroid'])),
       patch_eq_db=[[round(f),round(g,1)] for f,g in rec['R3_clarinet_musette']['eq_corr']])],
 accompaniment_patch=dict(prog=23,alt=21,oom=dict(dur_s=0.30,vel=85),pah=dict(dur_s=[0.08,0.12],vel=85,note='P23 0.08 s chord: attack 34 ms, decay 39 ms; P21 0.12 s: 74/72 ms; plucked/struck patches (piano 9 ms, guitar 8 ms, harp 18 ms attacks) do not match'),level_db_re_lead=[-6,-1],evidence='HNR at the held C5 is 19-20 dB in the original; R1 lead + accompaniment at -6 dB gives 21-24 dB, at -10 dB 25-28 dB'),
 chain=dict(order=['render dry mono (FluidR3, reverb/chorus off, -23 c pitch bend)','per-note 40-50 ms raised-cosine attack, overlap next note 30-60 ms','wow: band-limited noise 0.5-5 Hz, 4.5 c RMS, variable delay','stereo room IR (rt60 0.09 s, predelay 6 ms, build 4 ms, tail -30 dB/1.5 s, wet band 150-4000 Hz, wet -8 dB)','patch EQ (patch_eq_db) then 1/3-oct LTAS match to eq_curve on the full arrangement, boost cap +12 dB, 2-3 passes','steep LPF ~5 kHz (>=48 dB/oct) to mimic the codec cliff','hum 100 Hz -70 dBFS peak (+150 Hz -78, 200 Hz -83.5) and optional 4-20 Hz rumble -56 dBFS RMS','level to -29.5 LUFS, true peak <= -17 dBTP, no limiter','end: short fade so all sound stops by 13.75 s'],
   code=dict(chain=T+'/py/zincir.py',render=T+'/py/fsr.py',features=T+'/py/ozellik.py',evaluate=T+'/py/aday.py',ltas_match=T+'/py/eslestir.py')),
 audio=dict(recipes_held_C5=[T+f'/wav/{k}_heldC5.wav' for k in rec],recipes_phrase=[T+f'/wav/{k}_phrase.wav' for k in rec],full_probe=[T+'/wav/fullprobe_R1.wav',T+'/wav/fullprobe_R2.wav'],note='probe phrase is a scale fragment C5-D5-Eb5, not a candidate melody'),
 spectrograms=dict(overview=PNG('01_overview.png'),fullband=PNG('02_fullband.png'),cqt_zoom=[PNG('04_cqt_zoom1.png'),PNG('04_cqt_zoom2.png'),PNG('04_cqt_zoom3.png')],narrowband=PNG('05_narrowband.png'),band_envelopes=PNG('06_band_envelopes.png'),intro_zoom=PNG('07_zoom_0_2p5.png'),head_tail=PNG('08_head_tail.png'),end_zoom=[PNG('09_zoom_end.png'),PNG('11_end_lowlin.png'),PNG('12_end_hilin.png')],partial_tracks=PNG('13_tracks.png'),
   held_C5_heterodyne=PNG('14_het_C5.png'),am_spectra=[PNG('15_am_C5.png'),PNG('15c_am_Ab5b.png')],ab5_glide=[PNG('18_ab5_low.png'),PNG('33_glide_check.png')],dominant_f0=PNG('20_f0_dominant.png'),bursts=PNG('21_burst_shapes.png'),ltas=PNG('23_ltas.png'),low_freq=PNG('24_lowfreq.png'),infrasonic=PNG('25_infrasonic.png'),stereo=PNG('26_stereo.png'),
   hf_harmonics=PNG('27_hf_harmonics.png'),source_filter=PNG('28_source_filter.png'),reverb_sysid=PNG('29_sysid_orig.png'),wow=PNG('30_wow.png'),oom=PNG('34_oom_check.png'),recipes_vs_original=PNG('35_recipes_vs_original.png'),fullprobe_vs_original=PNG('36_fullprobe_vs_original.png')),
 caveats=['Nobody listened; all claims are measurements or looked-at images.','Lead identity: measurements fit a free reed with two detuned voices; the 45-75 c glides fit a mouth-blown reed (harmonica/melodica) better than an accordion. Exact instrument unknown.','Lead harmonic profiles of the original include accompaniment leakage; the residual floor for every candidate is ~4 dB.','Reverb tail estimate below -28 dB is near the identification floor.','Hiss level is an upper bound only.','The ranking score is ad hoc: env_resid + 0.5*|odd-even diff| + |AM diff| + 0.5*|FM diff|/3 (+0.5*centroid diff in semitones for score_with_brightness).'])
json.dump(J,open(D+'/tini.json','w'),indent=1,ensure_ascii=False)
print('written'); print(json.dumps(sr[:10],indent=0)[:3000]); print([ (c['id'],c['score_with_brightness']) for c in cr][:8])
