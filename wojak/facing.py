"""Karakterin bakış yönü: sahnede HER ZAMAN içeri (kadrajın ortasına) bakmalı.

Solda duran karakter sağa, sağda duran sola bakar; dışarı bakan karakter "videonun dışına bakıyor"
gibi durur (hesap sahibinin geri bildirimi, 2026-10-09). Görselin hangi yöne baktığı bir kez gözle
belirlenip data/karakter_yon.json'a yazılır (anahtar: dosya içeriğinin sha1'i, dosya kopyalansa da
geçerli). Renderer bu kayda göre gerekirse aynalar; kayıt yoksa sezgisel tahmin kullanılır ve
`python -m wojak check` uyarır.

    python -m wojak yon <png> [<png>...]            # kayıt + tahmin
    python -m wojak yon <png> sag|sol|on            # gözle bakıp kaydet
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

from . import config

REGISTRY = config.ROOT / "data" / "karakter_yon.json"
ALIASES = {"sag": "right", "sağ": "right", "right": "right", "r": "right",
           "sol": "left", "left": "left", "l": "left",
           "on": "front", "ön": "front", "front": "front", "f": "front"}


def _sha1(path: Path) -> str:
    return hashlib.sha1(Path(path).read_bytes()).hexdigest()


def _load() -> dict:
    try:
        return json.loads(REGISTRY.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def register(path: Path, faces: str) -> str:
    faces = ALIASES[faces.lower()]
    reg = _load()
    p = Path(path).resolve()
    rel = str(p.relative_to(config.ROOT)) if p.is_relative_to(config.ROOT) else str(p)
    reg[_sha1(p)] = {"faces": faces, "file": rel}
    REGISTRY.write_text(json.dumps(reg, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return faces


def registered(path: Path) -> str | None:
    rec = _load().get(_sha1(path))
    return rec["faces"] if rec else None


def guess(path: Path) -> tuple[str, float]:
    """Sezgisel tahmin (13 elle etiketli karakterde ~%75 isabet; tek başına güvenme).
    Başın üst %55'inde, açık renkli yüz alanının içindeki koyu çizgilerin (göz, burun, ağız) yüz
    merkezine göre kayması: 3/4 profilde yüz hatları bakılan tarafa toplanır."""
    a = np.asarray(Image.open(path).convert("RGBA")).astype(float)
    m = a[..., 3] > 128
    if m.sum() < 100:
        return "front", 0.0
    ys, _ = np.where(m)
    y0, y1 = ys.min(), ys.max()
    hb = y0 + int((y1 - y0) * 0.55)
    lum = 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]
    light, dark = m & (lum > 185), m & (lum < 95)

    def sh(arr, dy, dx):
        out = np.zeros_like(arr)
        H, W = arr.shape
        out[max(dy, 0):H + min(dy, 0), max(dx, 0):W + min(dx, 0)] = \
            arr[max(-dy, 0):H + min(-dy, 0), max(-dx, 0):W + min(-dx, 0)]
        return out

    k = 5
    inner = dark & ((sh(light, 0, k) & sh(light, 0, -k)) | (sh(light, k, 0) & sh(light, -k, 0)))
    band = np.zeros_like(m)
    band[y0:hb] = True
    inner &= band
    lb = light & band
    if inner.sum() < 30 or lb.sum() < 100:
        return "front", 0.0
    lx = np.where(lb)[1]
    lo, hi = np.percentile(lx, 5), np.percentile(lx, 95)
    s = (np.where(inner)[1].mean() - (lo + hi) / 2) / max(hi - lo, 1)
    return ("right" if s > 0.07 else "left" if s < -0.04 else "front"), float(s)


def resolve(path: Path, override: str | None = None) -> tuple[str, bool]:
    """(yön, kayıtlı_mı). Öncelik: sahnedeki 'faces' > kayıt > tahmin."""
    if override:
        return ALIASES[override.lower()], True
    r = registered(path)
    if r:
        return r, True
    return guess(path)[0], False


def needs_flip(faces: str, center_x: float) -> bool:
    """Karakter kadrajın solundaysa sağa, sağındaysa sola baksın."""
    if faces == "front" or abs(center_x - 0.5) < 0.08:
        return False
    want = "right" if center_x < 0.5 else "left"
    return faces != want
