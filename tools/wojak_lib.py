#!/usr/bin/env python3
"""Wojak karakter kütüphanesi (Hugging Face: clayshoaf/Wojaks — wojakparadise.net arşivi).

~10.000 şeffaf PNG, her birinin dönem/ülke/rol içeren İngilizce açıklaması var.

Komutlar:
    python tools/wojak_lib.py index                    # data/wojak_index.csv oluştur (bir kez)
    python tools/wojak_lib.py search doomer girl       # açıklamada geçen kelimelerle ara
    python tools/wojak_lib.py search police --cat NPC  # kategoriye göre süz
    python tools/wojak_lib.py sheet police officer     # sonuçların numaralı önizleme sayfası
    python tools/wojak_lib.py get 5_Doomer/13591 --name genc_erkek_uzgun
    python tools/wojak_lib.py cats                     # kategoriler ve sayıları

İndirilen karakterler assets/characters/<isim>.png olarak kaydedilir (kenarları
kırpılmış, en fazla 1400 px yükseklik) ve episode.yaml'da `img: <isim>` ile kullanılır.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
REPO = "clayshoaf/Wojaks"
API = f"https://huggingface.co/api/datasets/{REPO}/tree/main"
RAW = f"https://huggingface.co/datasets/{REPO}/resolve/main"
INDEX = ROOT / "data" / "wojak_index.csv"
CHARS = ROOT / "assets" / "characters"
CACHE = ROOT / ".cache" / "wojaks"

http = requests.Session()
http.headers["User-Agent"] = "tarihselwojak-pipeline/0.1"


def _list_dir(path: str) -> list[dict]:
    out, url = [], f"{API}/{urllib.parse.quote(path)}"
    while url:
        r = http.get(url, timeout=60)
        r.raise_for_status()
        out += r.json()
        nxt = re.search(r'<([^>]+)>;\s*rel="next"', r.headers.get("Link", ""))
        url = nxt.group(1) if nxt else None
    return out


def cmd_index(_a) -> None:
    top = http.get(API, timeout=60).json()
    cats = [e["path"] for e in top if e["type"] == "directory"]
    rows = []
    for c in cats:
        files = _list_dir(c)
        pngs = {f["path"]: f.get("size", 0) for f in files if f["path"].endswith(".png")}
        txts = [f["path"] for f in files if f["path"].endswith(".txt")]
        print(f"{c}: {len(pngs)} png", flush=True)

        def cap(p):
            try:
                return p, http.get(f"{RAW}/{urllib.parse.quote(p)}", timeout=60).text.strip()
            except Exception:
                return p, ""
        with ThreadPoolExecutor(16) as ex:
            caps = dict(ex.map(cap, txts))
        for png, size in pngs.items():
            key = png[:-4]
            rows.append({"id": key, "category": c.split("_", 1)[1], "caption": caps.get(key + ".txt", ""),
                         "bytes": size})
    INDEX.parent.mkdir(parents=True, exist_ok=True)
    with INDEX.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id", "category", "caption", "bytes"])
        w.writeheader()
        w.writerows(rows)
    print(f"-> {INDEX} ({len(rows)} karakter)")


def load_index() -> list[dict]:
    if not INDEX.exists():
        sys.exit("Önce: python tools/wojak_lib.py index")
    with INDEX.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def search(terms: list[str], cat: str | None = None, limit: int = 40) -> list[dict]:
    rows = load_index()
    terms = [t.lower() for t in terms]
    res = []
    for r in rows:
        if cat and cat.lower() not in r["category"].lower():
            continue
        hay = f"{r['category']} {r['caption']}".lower()
        if all(t in hay for t in terms):
            res.append(r)
    # Kısa açıklama = daha "genel" karakter; önce onları göster
    res.sort(key=lambda r: len(r["caption"]))
    return res[:limit]


def cmd_search(a) -> None:
    for i, r in enumerate(search(a.terms, a.cat, a.limit)):
        print(f"{i:3d}  {r['id']:<28} {r['caption'][:110]}")


def fetch(id_: str) -> Image.Image:
    CACHE.mkdir(parents=True, exist_ok=True)
    p = CACHE / (id_.replace("/", "_") + ".png")
    if not p.exists():
        r = http.get(f"{RAW}/{urllib.parse.quote(id_)}.png", timeout=120)
        r.raise_for_status()
        p.write_bytes(r.content)
    return Image.open(p)


def alpha_ratio(im: Image.Image) -> float:
    im = im.convert("RGBA")
    a = im.getchannel("A")
    hist = a.histogram()
    return sum(hist[:16]) / (im.width * im.height)


def cmd_get(a) -> None:
    im = fetch(a.id).convert("RGBA")
    ratio = alpha_ratio(im)
    if ratio < 0.03:
        print(f"UYARI: görsel neredeyse hiç şeffaf değil (%{ratio * 100:.1f}). "
              "Arka planı kaldırmak için: python tools/cutout.py <dosya>")
    bbox = im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
    if bbox:
        im = im.crop(bbox)
    if im.height > 1400:
        im = im.resize((round(im.width * 1400 / im.height), 1400), Image.LANCZOS)
    name = a.name or a.id.replace("/", "_")
    dest = Path(a.out_dir) if a.out_dir else CHARS  # bölüme özel karakterler: episodes/<id>/chars
    dest.mkdir(parents=True, exist_ok=True)
    out = dest / f"{name}.png"
    im.save(out, optimize=True)
    shown = out.resolve().relative_to(ROOT) if out.resolve().is_relative_to(ROOT) else out
    print(f"-> {shown}  ({im.width}x{im.height})")


def cmd_sheet(a) -> None:
    res = search(a.terms, a.cat, a.limit)
    if not res:
        sys.exit("sonuç yok")
    tw, th, cols = 240, 300, 6
    rows_n = (len(res) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows_n * (th + 40)), (200, 200, 200))
    d = ImageDraw.Draw(sheet)
    try:
        f = ImageFont.truetype(str(ROOT / "assets/fonts/Poppins-Bold.ttf"), 14)
    except OSError:
        f = ImageFont.load_default()

    def load(r):
        try:
            return r, fetch(r["id"]).convert("RGBA")
        except Exception:
            return r, None
    with ThreadPoolExecutor(8) as ex:
        items = list(ex.map(load, res))
    for i, (r, im) in enumerate(items):
        x, y = (i % cols) * tw, (i // cols) * (th + 40)
        if im is not None:
            im.thumbnail((tw - 10, th - 10))
            sheet.paste(im, (x + (tw - im.width) // 2, y + (th - im.height) // 2), im)
        d.text((x + 4, y + th + 2), f"{i} {r['id']}", fill="black", font=f)
        d.text((x + 4, y + th + 20), r["caption"][:34], fill=(60, 60, 60), font=f)
    out = ROOT / "out" / f"sheet_{'_'.join(a.terms) or a.cat}.jpg"
    out.parent.mkdir(exist_ok=True)
    sheet.save(out, quality=85)
    print(f"-> {out}")


def cmd_cats(_a) -> None:
    from collections import Counter
    for c, n in Counter(r["category"] for r in load_index()).most_common():
        print(f"{n:6d}  {c}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("index").set_defaults(fn=cmd_index)
    sp.add_parser("cats").set_defaults(fn=cmd_cats)
    for name, fn in (("search", cmd_search), ("sheet", cmd_sheet)):
        p = sp.add_parser(name)
        p.add_argument("terms", nargs="*")
        p.add_argument("--cat")
        p.add_argument("--limit", type=int, default=40 if name == "search" else 30)
        p.set_defaults(fn=fn)
    p = sp.add_parser("get")
    p.add_argument("id", help="örn. 5_Doomer/13591")
    p.add_argument("--name", help="kaydedilecek isim (assets/characters/<isim>.png)")
    p.add_argument("--out-dir", help="assets/characters yerine bu klasöre kaydet (ör. episodes/<id>/chars)")
    p.set_defaults(fn=cmd_get)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
