"""Ses miksi: müzik + sahne efektleri (sfx) + isteğe bağlı seslendirme."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from . import config
from .episode import Episode


def _scene_starts(ep: Episode, fps: int) -> list[float]:
    starts, t = [], 0.0
    for s in ep.scenes:
        starts.append(t)
        t += max(1, round(s.duration * fps)) / fps
    return starts


def build(ep: Episode, out: Path, total: float, fps: int) -> Path:
    """Bölümün ses izini WAV olarak üretir. Hiç ses yoksa sessiz iz üretir
    (Instagram/YouTube ses izi olmayan videolarda sorun çıkarabiliyor)."""
    inputs: list[str] = []
    chains: list[str] = []
    labels: list[str] = []
    idx = 0

    if ep.music:
        m = ep.music
        inputs += (["-stream_loop", "-1"] if m.loop else []) + ["-ss", f"{m.start:.3f}", "-i", str(m.file)]
        f = [f"atrim=0:{total:.3f}", "asetpts=PTS-STARTPTS", f"volume={m.volume}"]
        if m.fade_in:
            f.append(f"afade=t=in:st=0:d={m.fade_in}")
        if m.fade_out:
            f.append(f"afade=t=out:st={max(0, total - m.fade_out):.3f}:d={m.fade_out}")
        chains.append(f"[{idx}:a]{','.join(f)}[a{idx}]")
        labels.append(f"[a{idx}]")
        idx += 1

    for start, sc in zip(_scene_starts(ep, fps), ep.scenes):
        events = [(s.file, start + s.at, s.volume) for s in sc.sfx]
        if sc.voice:
            events.append((sc.voice, start, 1.0))
        for path, at, vol in events:
            inputs += ["-i", str(path)]
            ms = max(0, round(at * 1000))
            chains.append(f"[{idx}:a]aresample=48000,volume={vol},adelay={ms}|{ms}[a{idx}]")
            labels.append(f"[a{idx}]")
            idx += 1

    if not labels:
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i",
               "anullsrc=r=48000:cl=stereo", "-t", f"{total:.3f}", str(out)]
    else:
        mix = (f"{''.join(labels)}amix=inputs={len(labels)}:duration=longest:normalize=0,"
               f"apad,atrim=0:{total:.3f}[out]")
        raw = out.with_name(out.stem + "_ham.wav")
        cmd = ["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex",
               ";".join(chains + [mix]), "-map", "[out]", "-ac", "2", "-ar", "48000", str(raw)]
        subprocess.run(cmd, check=True)
        _loudnorm(raw, out)
        raw.unlink(missing_ok=True)
        return out
    subprocess.run(cmd, check=True)
    return out


def _olc(src: Path) -> tuple[float, float]:
    """(entegre LUFS, gerçek tepe dBTP). loudnorm yalnız ÖLÇER: hedef TP ffmpeg'in izin verdiği -9..0 aralığına
    kırpılır (ölçülen değerler hedefe bağlı değil). Ölçülemezse ValueError."""
    tp = min(0.0, max(-9.0, config.LOUDNESS_TP))
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(src), "-af",
                        f"loudnorm=I={config.LOUDNESS_LUFS}:TP={tp}:LRA=7:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    err = r.stderr
    try:
        m = json.loads(err[err.rindex("{"):err.rindex("}") + 1])
        return float(m["input_i"]), float(m["input_tp"])
    except (ValueError, KeyError) as e:
        raise ValueError(f"loudnorm ölçümü okunamadı: {err.strip().splitlines()[-1:] or e}") from None


def _loudnorm(src: Path, dst: Path) -> None:
    """config.LOUDNESS_LUFS / LOUDNESS_TP'ye (31.10'dan beri -14 LUFS, -1,5 dBTP) ölçüp DOĞRUSAL kazanç (volume=dB)
    uygular. Limiter yok: tepe TP'yi aşacaksa kazanç tepeye göre kısılır (imza_v2_golge: -15,7 LUFS / -2,9 dBTP ->
    -14,3 LUFS / -1,5 dBTP) ve hedefin 1 LU'dan fazla altında kalırsa uyarılır.

    Eskiden loudnorm'a TP=-17 veriliyordu (orijinal reel'lerin -29,5 LUFS seviyesi); ffmpeg TP'yi -9..0 aralığında kabul
    ettiği için filtre hata veriyor, kod sessizce 'anull'a düşüyordu (kanuni-gizlenen-olum, 23.10). Ölçülemezse ses
    değiştirilmeden geçer ama bu artık sessiz değil, uyarılır."""
    I, TP = config.LOUDNESS_LUFS, config.LOUDNESS_TP
    try:
        li, ltp = _olc(src)
    except ValueError as e:
        print(f"  ⚠ ses normalize EDİLEMEDİ ({e}); video hedef {I} LUFS'tan farklı çıkar, ebur128 ile ölç")
        li = ltp = float("-inf")
    if li in (float("-inf"), float("inf")) or li != li:
        af = "anull"   # sessiz iz (ya da ölçülemedi): kazanç anlamsız
    else:
        gain = I - li
        if ltp + gain > TP:
            gain = TP - ltp
        if I - (li + gain) > 1.0:   # ±1 LU tolerans (notlardaki öneri); imza müziği ~0,3 LU altında kalır
            print(f"  ⚠ ses: tepe {ltp:.1f} dBTP, {I} LUFS'a çekilince {TP} dBTP'yi aşıyordu; kazanç tepeye göre "
                  f"kısıldı -> ~{li + gain:.1f} LUFS")
        af = f"volume={gain:.2f}dB"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-af", af,
                    "-ar", "48000", "-ac", "2", str(dst)], check=True)
