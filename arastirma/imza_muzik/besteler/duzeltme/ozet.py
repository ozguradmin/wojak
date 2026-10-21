"""python3 ozet.py <olcum.json> [...]: one line of the numbers the melody judge used, per harness output"""
import json, sys

for p in sys.argv[1:]:
    o = json.load(open(p))
    m = o["musical"]; og = o["originality"]; s = og.get("symbolic", {}); ol = s.get("offlimits", {})
    k = m["key"]; a = o["timbre"]["accent_uaa"]; r = m["harmonic_rocking"]
    t = o["technical"]
    print(f"{p.rsplit('/', 1)[-1]:28s} {o['originality_verdict']:4s} audio={og['audio_verdict']} sym={s.get('verdict')} "
          f"viol={ol.get('violations')} POV={ol.get('POV')} chT={og['chroma_seq_sim_transposed']['value']:.3f} "
          f"chroma={og['chroma_seq_sim']['value']:.3f} fp={og['fingerprint_match']['value']:.4f} "
          f"cbar={s.get('contour_bar_corr', {}).get('value')} cphr={s.get('contour_phrase_corr', {}).get('value')} "
          f"rhy={s.get('rhythm_distinctive_same_bar')}")
    print(f"{'':28s} key={k['value']} r={k['r']} c_minor_r={k['c_minor_r']} | rock lag2={r['value']} lag1={r.get('lag1bar')} "
          f"| uaa tilt={[round(x, 1) for x in a['value']]} contrast={a.get('contrast_db'):.1f} "
          f"level={[round(x, 1) for x in a.get('level_from_dark_db') or []]} | TIMBRE={o['TIMBRE_SCORE']} "
          f"| first={t['first_sound_s']['value']} last={t['last_sound_s']['value']} LUFS={t['lufs_integrated']['value']} "
          f"checks_ok={o['technical_checks'].get('all_ok')}")
    if og.get("audio_reasons") or og.get("audio_warnings") or s.get("reasons"):
        print(f"{'':28s} reasons={og.get('audio_reasons')} warn={og.get('audio_warnings')} sym_reasons={s.get('reasons')}")
