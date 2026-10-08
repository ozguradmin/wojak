"""Ses miksi: müzik + sahne efektleri (sfx) + isteğe bağlı seslendirme."""

from __future__ import annotations

import subprocess
from pathlib import Path

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
        inputs += ["-stream_loop", "-1", "-ss", f"{m.start:.3f}", "-i", str(m.file)]
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
               f"apad,atrim=0:{total:.3f},alimiter=limit=0.95[out]")
        cmd = ["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex",
               ";".join(chains + [mix]), "-map", "[out]", "-ac", "2", "-ar", "48000", str(out)]
    subprocess.run(cmd, check=True)
    return out
