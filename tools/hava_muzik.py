#!/usr/bin/env python3
"""Hava müzikleri v2: besteleri (tools/hava_besteler.py) ev sesi motorundan geçirip assets/music/hava/ altına yazar.

    python tools/hava_muzik.py --hepsi                 # beş parça: JSON -> ev sesi -> assets/music/hava/<ad>.m4a
    python tools/hava_muzik.py gizem_a [--tohum 1]     # tek parça
    python tools/hava_muzik.py --liste
    python tools/hava_muzik.py --onizleme plan.json cikti.mp4 [--teslim /yol/wojak-ozel/teslim] [--boy 1280]

Zincir: tools/ev_sesi/render.py (Gölge'yi yapan motor: FluidR3 örnekleri + klasik sesten ölçülen lo-fi zincir, çıktı
-29,5 LUFS) -> tools/ev_sesi/master.py (düz kazançla -15 LUFS, tepe <= -2 dBTP, AAC 192k). Aynı JSON + tohum = aynı
dosya. Ara dosyalar out/hava/ altında. Kurulum: apt-get install fluidsynth fluid-soundfont-gm; pip install
pyfluidsynth soundfile scipy numpy.

--onizleme: hesap sahibi için dinleme videosu. Her parça GERÇEK bir yayınlanmış videonun altında çalar
(wojak-ozel/teslim/<bolum>/<bolum>.mp4), üstte numara ve etiket; ses videodaki kurala göre -14 LUFS, tepe <= -1,5.
plan.json: [{"no": 1, "etiket": "GİZEM · Fısıltı", "ses": "assets/music/hava/gizem_a.m4a", "bolum": "<id>"}, ...]
Yayınlanmaz; çıktı out/ altına yazılır (repoya video girmez).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MOTOR = ROOT / "tools" / "ev_sesi"
CIKTI = ROOT / "assets" / "music" / "hava"
CALISMA = ROOT / "out" / "hava"
YAZI = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def uret(ad: str, beste: dict, tohum: int = 1) -> dict:
    CALISMA.mkdir(parents=True, exist_ok=True)
    CIKTI.mkdir(parents=True, exist_ok=True)
    js, wav, m4a = CALISMA / f"{ad}.json", CALISMA / f"{ad}.wav", CIKTI / f"{ad}.m4a"
    js.write_text(json.dumps(beste, indent=1, ensure_ascii=False), encoding="utf-8")
    r = subprocess.run([sys.executable, str(MOTOR / "render.py"), str(js), str(wav), "--seed", str(tohum)],
                       capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"{ad}: render hatası: {r.stderr.strip().splitlines()[-1] if r.stderr.strip() else '?'}")
    bilgi = json.loads(r.stdout)
    m = subprocess.run([sys.executable, str(MOTOR / "master.py"), str(wav), str(m4a)], capture_output=True, text=True)
    if m.returncode:
        raise SystemExit(f"{ad}: master hatası: {m.stderr.strip().splitlines()[-1] if m.stderr.strip() else '?'}")
    son = json.loads(m.stdout.strip().splitlines()[-1])
    (CALISMA / f"{ad}.olcum.json").write_text(json.dumps({"render": bilgi, "master": son}, indent=1), encoding="utf-8")
    return {"ad": ad, "bpm": bilgi["bpm"], "son_s": bilgi["end_s"], "lufs": son["out_lufs"], "tp": son["out_tp"],
            "giris_s": (bilgi.get("sections") or {}).get("lead_in_s"), "dosya": str(m4a.relative_to(ROOT))}


def _olc(p: Path) -> tuple[float, float]:
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(p), "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    i = [s for s in r.splitlines() if s.strip().startswith("I:")][-1].split()[1]
    t = [s for s in r.splitlines() if s.strip().startswith("Peak:")][-1].split()[1]
    return float(i), float(t)


def onizleme(plan_yolu: Path, cikti: Path, teslim: Path, boy: int = 1280) -> Path:
    plan = json.loads(plan_yolu.read_text(encoding="utf-8"))
    en = boy * 9 // 16
    cikti.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as d:
        parcalar = []
        for m in plan:
            v = teslim / m["bolum"] / f"{m['bolum']}.mp4"
            ses = Path(m["ses"]) if Path(m["ses"]).is_absolute() else ROOT / m["ses"]
            if not v.exists() or not ses.exists():
                raise SystemExit(f"yok: {v if not v.exists() else ses}")
            lufs, tp = _olc(ses)
            kazanc = min(-14.0 - lufs, -1.5 - tp)
            sure = float(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                         "stream=duration", "-of", "csv=p=0", str(v)],
                                        capture_output=True, text=True).stdout.strip() or 14.0)
            etiket = f"{m['no']}  {m['etiket']}".replace(":", "\\:").replace("'", "")
            vf = (f"scale={en}:{boy},drawbox=x=0:y=0:w=iw:h={boy // 14}:color=black@0.75:t=fill,"
                  f"drawtext=fontfile={YAZI}:text='{etiket}':fontcolor=0xF0C850:fontsize={boy // 28}:"
                  f"x=(w-text_w)/2:y={boy // 56}")
            p = Path(d) / f"{int(m['no']):02d}.mp4"
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(v), "-i", str(ses), "-filter_complex",
                            f"[0:v]{vf}[v];[1:a]volume={kazanc:.2f}dB,apad=whole_dur={sure:.3f},atrim=0:{sure:.3f}[a]",
                            "-map", "[v]", "-map", "[a]", "-t", f"{sure:.3f}", "-r", "30", "-c:v", "libx264",
                            "-crf", "25", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
                            "-ar", "44100", "-ac", "2", str(p)], check=True)
            parcalar.append(p)
            print(f"{m['no']:>2} {m['etiket']:<26} {m['bolum']:<30} {lufs:6.1f} LUFS -> {kazanc:+.1f} dB")
        liste = Path(d) / "liste.txt"
        liste.write_text("".join(f"file '{p}'\n" for p in parcalar))
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(liste), "-c", "copy",
                        str(cikti)], check=True)
    return cikti


def main() -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import hava_besteler
    besteler = hava_besteler.BESTELER
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("adlar", nargs="*")
    ap.add_argument("--hepsi", action="store_true")
    ap.add_argument("--liste", action="store_true")
    ap.add_argument("--tohum", type=int, default=1)
    ap.add_argument("--onizleme", nargs=2, metavar=("PLAN", "CIKTI"))
    ap.add_argument("--teslim", type=Path, default=Path("/home/user/wojak-ozel/teslim"))
    ap.add_argument("--boy", type=int, default=1280)
    a = ap.parse_args()
    if a.liste:
        for ad, f in besteler.items():
            b = f()
            print(f"{ad:<12} {b['title']:<11} {b['key']:<26} {b['tempo_bpm']:>4} BPM  {hava_besteler.KONU.get(ad, '')}")
        return
    if a.onizleme:
        print("->", onizleme(Path(a.onizleme[0]), Path(a.onizleme[1]), a.teslim, a.boy))
        return
    for ad in (list(besteler) if a.hepsi else a.adlar):
        o = uret(ad, besteler[ad](), a.tohum)
        print(f"{o['ad']:<12} {o['bpm']:5.0f} BPM  ezgi {o['giris_s']} sn  son {o['son_s']} sn  {o['lufs']:6.1f} LUFS  "
              f"tepe {o['tp']:5.1f} dBTP  -> {o['dosya']}")


if __name__ == "__main__":
    main()
