#!/usr/bin/env python3
"""Aynı wojak yüzünden duygu varyantları üretir (ter damlası, gözyaşı).

Altın dönem videolarında ana karakter sahneden sahneye AYNI çizimdir; sadece yüzüne ter damlaları,
gözyaşı eklenir ya da son sahnede korku yüzüne döner. Bu araç bir taban PNG'ye bu katmanları çizer.

    python tools/kit_varyant.py assets/kit/klasik/sakin.png --kit klasik

Koordinatlar taban görselin piksel düzlemindedir (assets/kit/<kit>/kit.json içinde, elle ayarlanır).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

SS = 3  # süper örnekleme (yumuşak kenar)
SWEAT_FILL, SWEAT_LINE = (170, 220, 255, 255), (40, 120, 200, 255)
TEAR_FILL = (120, 190, 250, 235)


def _drop(d: ImageDraw.ImageDraw, x: float, y: float, s: float) -> None:
    """Damla: üstü sivri, altı yuvarlak. (x, y) alt dairenin merkezi, s yarıçap."""
    x, y, s = x * SS, y * SS, s * SS
    lw = max(2, round(s * 0.22))
    pts = [(x, y - s * 2.6), (x - s * 0.95, y - s * 0.35), (x + s * 0.95, y - s * 0.35)]
    d.polygon(pts, fill=SWEAT_FILL)
    d.ellipse([x - s, y - s, x + s, y + s], fill=SWEAT_FILL)
    d.line([pts[0], pts[1]], fill=SWEAT_LINE, width=lw)
    d.line([pts[0], pts[2]], fill=SWEAT_LINE, width=lw)
    d.arc([x - s, y - s, x + s, y + s], start=-15, end=195, fill=SWEAT_LINE, width=lw)


def _tear(d: ImageDraw.ImageDraw, pts: list[list[float]], w: float) -> None:
    p = [(x * SS, y * SS) for x, y in pts]
    d.line(p, fill=TEAR_FILL, width=round(w * SS), joint="curve")
    for x, y in p[:1] + p[-1:]:
        r = w * SS / 2
        d.ellipse([x - r, y - r, x + r, y + r], fill=TEAR_FILL)


def make(base: Path, spec: dict, out: Path) -> Path:
    im = Image.open(base).convert("RGBA")
    layer = Image.new("RGBA", (im.width * SS, im.height * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for t in spec.get("tears", []):
        _tear(d, t["path"], t.get("w", 14))
    for x, y, s in spec.get("drops", []):
        _drop(d, x, y, s)
    layer = layer.resize(im.size, Image.LANCZOS)
    out.parent.mkdir(parents=True, exist_ok=True)
    Image.alpha_composite(im, layer).save(out, optimize=True)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("base")
    ap.add_argument("--kit", required=True, help="assets/kit/<kit>/kit.json içindeki 'variants' kullanılır")
    a = ap.parse_args()
    kit = ROOT / "assets" / "kit" / a.kit
    cfg = json.loads((kit / "kit.json").read_text(encoding="utf-8"))
    from wojak import facing
    faces = facing.registered(Path(a.base))
    for name, spec in cfg["variants"].items():
        out = make(Path(a.base), spec, kit / f"{name}.png")
        if faces:
            facing.register(out, faces)
        print(f"-> {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
