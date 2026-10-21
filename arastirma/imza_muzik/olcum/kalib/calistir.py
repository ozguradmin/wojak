#!/usr/bin/env python3
"""Run olcum.py on the calibration set (4 in parallel) -> kalib/sonuc/<name>.json, ../png/<name>.png; print a table."""
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

K = os.path.dirname(os.path.abspath(__file__))
O = os.path.dirname(K)
SCR = os.path.abspath(os.path.join(O, "..", ".."))
A = os.path.join(K, "audio")
MUS = "/home/user/wojak/assets/music"
SET = [
    ("orijinal", os.path.join(SCR, "muzik", "orijinal.wav"), "notalar_orijinal.json"),
    ("kopya_aac128", os.path.join(A, "kopya_aac128.m4a"), None),
    ("kopya_mp3128", os.path.join(A, "kopya_mp3128.mp3"), None),
    ("kopya_tools", os.path.join(SCR, "muzik", "orijinal_kopya.m4a"), None),
    ("orijinal_p2", os.path.join(A, "orijinal_p2.wav"), None),
    ("orijinal_m1", os.path.join(A, "orijinal_m1.wav"), None),
    ("orijinal_tempo103", os.path.join(A, "orijinal_tempo103.wav"), None),
    ("orijinal_10klik", os.path.join(A, "orijinal_10klik.wav"), None),
    ("orijinal_hiss55", os.path.join(A, "orijinal_hiss55.wav"), None),
    ("red_imza", os.path.join(MUS, "imza_vals.m4a"), "notalar_imza.json"),
    ("red_ikinci", os.path.join(MUS, "imza_vals_ikinci.m4a"), "notalar_ikinci.json"),
    ("red_ucuncu", os.path.join(MUS, "imza_vals_ucuncu.m4a"), "notalar_ucuncu.json"),
    ("ilgisiz_gece_vals", os.path.join(MUS, "imza_gece_vals.mp3"), None),
    ("kapak_orijinal_fluid", os.path.join(A, "kapak_orijinal_besteyle_fluid.wav"), "notalar_orijinal.json"),
    ("red_imza_fluid", os.path.join(A, "red_imza_fluid.wav"), "notalar_imza.json"),
    ("red_ikinci_fluid", os.path.join(A, "red_ikinci_fluid.wav"), "notalar_ikinci.json"),
    ("red_ucuncu_fluid", os.path.join(A, "red_ucuncu_fluid.wav"), "notalar_ucuncu.json"),
] + [(f"rastgele{i}", os.path.join(A, f"rastgele{i}_{'origarmoni' if i < 3 else 'baskaarmoni'}.wav"),
      f"notalar_rastgele{i}.json") for i in range(6)]


def run(item):
    name, path, nj = item
    out = os.path.join(K, "sonuc", name + ".json")
    cmd = [sys.executable, os.path.join(O, "olcum.py"), path, "--png", os.path.join(O, "png", name + ".png")]
    if nj:
        cmd += ["--notalar", os.path.join(K, nj)]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode:
        return name, None, p.stderr[-2000:]
    open(out, "w").write(p.stdout)
    return name, json.loads(p.stdout), None


if __name__ == "__main__":
    os.makedirs(os.path.join(K, "sonuc"), exist_ok=True)
    only = set(sys.argv[1:])
    items = [s for s in SET if not only or s[0] in only]
    res = {}
    first = [s for s in items if s[0] == "orijinal"]
    for s in first:                      # builds the reference cache once
        n, j, e = run(s); res[n] = j
        if e:
            print(n, e)
    with ThreadPoolExecutor(4) as ex:
        for n, j, e in ex.map(run, [s for s in items if s[0] != "orijinal"]):
            res[n] = j
            if e:
                print(n, "ERROR", e)
    for n, j in res.items():
        if j:
            print(f"{n:22s} T={j['TIMBRE_SCORE']:5.1f} chroma={j['originality']['chroma_seq_sim']['value']:.3f} "
                  f"chromaT={j['originality']['chroma_seq_sim_transposed']['value']:.3f} fp={j['originality']['fingerprint_match']['value']:.3f} "
                  f"{j['originality_verdict'][:4]} {j['elapsed_s']}s")
