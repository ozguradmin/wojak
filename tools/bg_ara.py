#!/usr/bin/env python3
"""Telifsiz (Creative Commons / CC0) arka plan görseli arar ve indirir — Openverse API.

    python tools/bg_ara.py "snowy forest night"                 # sonuçları listele
    python tools/bg_ara.py "abandoned village turkey" --indir 3 -d episodes/x/img
    python tools/bg_ara.py "istanbul street night" --sheet       # numaralı önizleme sayfası

Not: Olayın GERÇEK yeri/fotoğrafı (haber fotoğrafı) genelde daha etkili ama telifli
olabilir; bkz. docs/URETIM_REHBERI.md > Görseller. Wikimedia API'si bu sunucunun
paylaşılan IP'sini sık sık 429 ile engelliyor; Openverse sorunsuz çalışıyor.
"""

from __future__ import annotations

import argparse
import io
import re
from pathlib import Path

import requests
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
API = "https://api.openverse.org/v1/images/"
UA = {"User-Agent": "tarihselwojak-pipeline/0.1"}


def search(q: str, n: int = 20, commercial: bool = True) -> list[dict]:
    params = {"q": q, "page_size": n, "mature": "false"}
    if commercial:
        params["license_type"] = "commercial,modification"
    r = requests.get(API, params=params, headers=UA, timeout=60)
    r.raise_for_status()
    return [x for x in r.json().get("results", []) if (x.get("width") or 0) >= 800]


def download(item: dict, dst_dir: Path, idx: int) -> Path:
    r = requests.get(item["url"], headers=UA, timeout=120)
    r.raise_for_status()
    im = Image.open(io.BytesIO(r.content)).convert("RGB")
    slug = re.sub(r"[^a-z0-9]+", "_", item["title"].lower())[:40].strip("_") or "bg"
    p = dst_dir / f"{idx:02d}_{slug}.jpg"
    im.save(p, quality=92)
    return p


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sorgu", help="İngilizce arama daha çok sonuç verir")
    ap.add_argument("--indir", type=int, default=0, help="ilk N sonucu indir")
    ap.add_argument("-d", "--dizin", default="out/bg")
    ap.add_argument("--sheet", action="store_true")
    ap.add_argument("--hepsi", action="store_true", help="ticari olmayan lisansları da göster")
    a = ap.parse_args()
    res = search(a.sorgu, commercial=not a.hepsi)
    for i, x in enumerate(res):
        print(f"{i:2d} {x['width']}x{x['height']} {x['license']:<8} {x['source']:<10} {x['title'][:50]}  {x['url']}")
    d = ROOT / a.dizin
    if a.indir or a.sheet:
        d.mkdir(parents=True, exist_ok=True)
    for i, x in enumerate(res[:a.indir]):
        print("->", download(x, d, i))
    if a.sheet and res:
        tw, th, cols = 320, 320, 4
        sheet = Image.new("RGB", (cols * tw, ((len(res) + cols - 1) // cols) * (th + 20)), "white")
        dr = ImageDraw.Draw(sheet)
        for i, x in enumerate(res):
            try:
                r = requests.get(x.get("thumbnail") or x["url"], headers=UA, timeout=60)
                im = Image.open(io.BytesIO(r.content)).convert("RGB")
                im.thumbnail((tw - 6, th - 6))
                sheet.paste(im, ((i % cols) * tw + 3, (i // cols) * (th + 20) + 3))
            except Exception:
                pass
            dr.text(((i % cols) * tw + 4, (i // cols) * (th + 20) + th + 2), f"{i} {x['license']}", fill="black")
        p = d / "sheet.jpg"
        sheet.save(p, quality=85)
        print("->", p)


if __name__ == "__main__":
    main()
