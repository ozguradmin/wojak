"""Kare kare render + ffmpeg ile kodlama."""

from __future__ import annotations

import math
import random
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageFilter

from . import audio, compose, config
from .episode import Episode, Scene


def ease_in_out(t: float) -> float:
    return 0.5 - 0.5 * math.cos(math.pi * max(0.0, min(1.0, t)))


def ease_out_back(t: float, k: float = 1.6) -> float:
    t = max(0.0, min(1.0, t)) - 1
    return 1 + (k + 1) * t ** 3 + k * t ** 2


class SceneRenderer:
    POP_SEC = 0.22
    SHAKE_SEC = 0.45
    FLASH_SEC = 0.18

    def __init__(self, ep: Episode, scene: Scene, box: int, fps: int, seed: int = 0):
        self.scene = scene
        self.box = box
        self.fps = fps
        self.layers = compose.build_layers(ep, scene, box)
        self.n = max(1, round(scene.duration * fps))
        self.rng = random.Random(seed)
        self._static = None
        self._pop_cache: dict[tuple[int, int], Image.Image] = {}

    def _bg(self, t: float) -> Image.Image:
        z = 1 + (self.scene.zoom - 1) * ease_in_out(t)
        if abs(z - 1) < 1e-4:
            return self.layers.bg.copy()
        b = self.box
        w = b / z
        px, py = self.scene.pan
        cx = b / 2 + px * (b - w) / 2
        cy = b / 2 + py * (b - w) / 2
        region = (cx - w / 2, cy - w / 2, cx + w / 2, cy + w / 2)
        return self.layers.bg.resize((b, b), Image.BILINEAR, box=region)

    def frame(self, i: int) -> Image.Image:
        sc = self.scene
        sec = i / self.fps
        t = i / max(1, self.n - 1)
        animated = (sc.zoom != 1.0) or (sec < self.POP_SEC and any(c.pop for c in self.layers.chars)) \
            or (sc.shake and sec < self.SHAKE_SEC) or (sc.flash and sec < self.FLASH_SEC)
        if not animated and self._static is not None:
            return self._static
        im = self._bg(t)
        for ci, c in enumerate(self.layers.chars):
            if c.pop and sec < self.POP_SEC:
                s = 0.82 + 0.18 * ease_out_back(sec / self.POP_SEC)
                key = (ci, round(s * 200))
                ch = self._pop_cache.get(key)
                if ch is None:
                    ch = c.image.resize((max(1, round(c.image.width * s)), max(1, round(c.image.height * s))),
                                        Image.BILINEAR)
                    self._pop_cache[key] = ch
                x = c.x + (c.image.width - ch.width) // 2
                y = c.y + (c.image.height - ch.height)
                compose.paste_rgba(im, ch, x, y)
            else:
                compose.paste_rgba(im, c.image, c.x, c.y)
        if self.layers.overlay is not None:
            im.alpha_composite(self.layers.overlay)
        if sc.shake and sec < self.SHAKE_SEC:
            amp = sc.shake * (1 - sec / self.SHAKE_SEC)
            dx, dy = self.rng.uniform(-amp, amp), self.rng.uniform(-amp, amp)
            shaken = Image.new("RGBA", im.size, (0, 0, 0, 255))
            z = 1 + 2 * sc.shake / self.box  # kenar boşluğu görünmesin
            big = im.resize((round(self.box * z),) * 2, Image.BILINEAR)
            off = (big.width - self.box) // 2
            shaken.paste(big, (round(-off + dx), round(-off + dy)))
            im = shaken
        if sc.flash and sec < self.FLASH_SEC:
            a = int(255 * (1 - sec / self.FLASH_SEC))
            im = Image.alpha_composite(im, Image.new("RGBA", im.size, (255, 255, 255, a)))
        if not animated:
            self._static = im
        return im


def _fill_bg(box_img: Image.Image) -> Image.Image:
    """Siyah bant yerine karenin bulanık, karartılmış büyütmesi (kenarlık testi için 'dolgu' sürümü)."""
    small = box_img.convert("RGB").resize((96, 96), Image.BILINEAR).filter(ImageFilter.GaussianBlur(3))
    big = small.resize((config.CANVAS_H, config.CANVAS_H), Image.BICUBIC)
    x = (config.CANVAS_H - config.CANVAS_W) // 2
    big = big.crop((x, 0, x + config.CANVAS_W, config.CANVAS_H))
    return Image.blend(big, Image.new("RGB", big.size, (0, 0, 0)), 0.55)


def _canvas_frame(box_img: Image.Image, top: Image.Image | None, square: bool, fill: bool = False) -> bytes:
    if square:
        return box_img.convert("RGB").tobytes()
    canvas = _fill_bg(box_img) if fill else Image.new("RGB", (config.CANVAS_W, config.CANVAS_H), (0, 0, 0))
    canvas.paste(box_img.convert("RGB"), (0, config.BOX_Y))
    if top is not None:
        canvas.paste(top, ((config.CANVAS_W - top.width) // 2, (config.BOX_Y - top.height) // 2), top)
    return canvas.tobytes()


def render(ep: Episode, out_dir: Path | None = None, *, square: bool = False, fps: int = config.FPS,
           crf: int = 18, preset: str = "medium", preview: bool = False, fill: bool = False) -> Path:
    """Bölümü render eder ve mp4 yolunu döndürür.

    square=True -> 1080x1080 (IG akış/gönderi); aksi halde 1080x1920 (Reels/Shorts).
    preview=True -> yarım çözünürlük, hızlı ön izleme.
    fill=True -> üst/alt siyah bantlar karenin bulanık hâliyle dolar (kenarlık A/B testi).
    """
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg bulunamadı (apt install ffmpeg)")
    out_dir = Path(out_dir or config.OUT / ep.id)
    out_dir.mkdir(parents=True, exist_ok=True)
    suffix = "_kare" if square else ("_dolgu" if fill else "")
    suffix += "_onizleme" if preview else ""
    silent = out_dir / f".{ep.id}{suffix}_video.mp4"
    final = out_dir / f"{ep.id}{suffix}.mp4"

    W, H = (config.BOX, config.BOX) if square else (config.CANVAS_W, config.CANVAS_H)
    top = compose.top_text_layer(ep.top_text) if (ep.top_text and not square) else None
    scale = ["-vf", f"scale={W // 2}:{H // 2}:flags=bilinear"] if preview else []
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(fps), "-i", "-", *scale,
           "-c:v", "libx264", "-preset", "veryfast" if preview else preset,
           "-crf", str(crf + (6 if preview else 0)), "-pix_fmt", "yuv420p",
           "-profile:v", "high", "-movflags", "+faststart", str(silent)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    try:
        for si, sc in enumerate(ep.scenes):
            sr = SceneRenderer(ep, sc, config.BOX, fps, seed=si)
            for i in range(sr.n):
                proc.stdin.write(_canvas_frame(sr.frame(i), top, square, fill))
    finally:
        proc.stdin.close()
        if proc.wait() != 0:
            raise RuntimeError("ffmpeg video kodlaması başarısız")

    total = sum(max(1, round(s.duration * fps)) for s in ep.scenes) / fps
    wav = audio.build(ep, out_dir / f".{ep.id}{suffix}_audio.wav", total, fps)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(silent), "-i", str(wav),
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
                    "-ar", "48000", "-shortest", "-use_editlist", "0", "-movflags", "+faststart", str(final)], check=True)
    silent.unlink(missing_ok=True)
    wav.unlink(missing_ok=True)
    return final


def still(ep: Episode, scene_index: int, out: Path, at: float = 0.6, square: bool = False,
          fill: bool = False) -> Path:
    """Tek bir sahneden kare (kapak/ön izleme) çıkarır."""
    sc = ep.scenes[scene_index]
    sr = SceneRenderer(ep, sc, config.BOX, config.FPS)
    i = min(sr.n - 1, round(at * sr.n))
    top = compose.top_text_layer(ep.top_text) if (ep.top_text and not square) else None
    W, H = (config.BOX, config.BOX) if square else (config.CANVAS_W, config.CANVAS_H)
    Image.frombytes("RGB", (W, H), _canvas_frame(sr.frame(i), top, square, fill)).save(out, quality=92)
    return out
