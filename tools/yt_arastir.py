#!/usr/bin/env python3
"""@tarihselwojak YouTube Shorts kopyasından performans verisi toplar.

Instagram bu sunucudan login istiyor; aynı videolar YouTube'da da yayınlandığı
için analiz YouTube üzerinden yapılır. Video dosyası indirilemiyor (YouTube
indirme linkleri IP'ye bağlı, buradaki çıkış IP'si her bağlantıda değişiyor),
ama şunlar alınabiliyor: izlenme/beğeni/yorum, tarih, süre, 1080x1920 kapak
karesi, storyboard (60 sn+ videolarda ~1 kare/sn), en iyi yorumlar ve
hesabın sabit "olay" yorumları.

Kurulum (bir kez):
    pip install "yt-dlp[default,curl-cffi]" bgutil-ytdlp-pot-provider
    # PO token sunucusu (YouTube bot korumasını aşmak için) — bkz. README > Araştırma

Komutlar:
    python tools/yt_arastir.py liste            # tüm shorts -> data/youtube_shorts.csv (hızlı)
    python tools/yt_arastir.py detay            # her video için tam metadata (yavaş, ~20 dk)
    python tools/yt_arastir.py kapak            # kapak kareleri -> .cache/yt/thumbs/
    python tools/yt_arastir.py yorum --top 45   # en çok izlenen N videonun yorumları
    python tools/yt_arastir.py rapor            # data/videos.csv + data/olay_metinleri.md
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / ".cache" / "yt"
CHANNEL = "https://www.youtube.com/@tarihselwojak/shorts"
ENV = {**os.environ, "PATH": f"{Path.home() / '.deno/bin'}:{os.environ.get('PATH', '')}"}


def ytdlp(*args: str, timeout: int = 150) -> subprocess.CompletedProcess:
    if shutil.which("yt-dlp", path=ENV["PATH"]) is None:
        raise SystemExit("yt-dlp yok: pip install 'yt-dlp[default,curl-cffi]'")
    return subprocess.run(["yt-dlp", *args], capture_output=True, text=True, timeout=timeout, env=ENV)


def cmd_liste(_a) -> None:
    r = ytdlp("--flat-playlist", "-J", CHANNEL, timeout=300)
    d = json.loads(r.stdout)
    CACHE.mkdir(parents=True, exist_ok=True)
    (CACHE / "flat.json").write_text(json.dumps(d, ensure_ascii=False))
    print(f"{d.get('channel_follower_count')} abone, {len(d['entries'])} short")


def _flat() -> list[dict]:
    p = CACHE / "flat.json"
    if not p.exists():
        raise SystemExit("Önce: python tools/yt_arastir.py liste")
    return json.loads(p.read_text())["entries"]


def cmd_detay(_a) -> None:
    out = CACHE / "meta"
    out.mkdir(parents=True, exist_ok=True)
    for e in _flat():
        p = out / f"{e['id']}.json"
        if p.exists() and p.stat().st_size > 0:
            continue
        r = ytdlp("--extractor-args", "youtube:player_client=mweb", "--skip-download", "-j",
                  f"https://www.youtube.com/shorts/{e['id']}")
        if r.returncode == 0 and r.stdout.strip():
            p.write_text(r.stdout)
            print("ok", e["id"])
        else:
            print("HATA", e["id"], r.stderr.strip()[-200:])
        time.sleep(2)


def cmd_kapak(_a) -> None:
    import requests
    out = CACHE / "thumbs"
    out.mkdir(parents=True, exist_ok=True)
    for e in _flat():
        p = out / f"{e['id']}.jpg"
        if not p.exists():
            r = requests.get(f"https://i.ytimg.com/vi/{e['id']}/oardefault.jpg", timeout=30)
            if r.ok:
                p.write_bytes(r.content)
    print(f"-> {out}")


def cmd_yorum(a) -> None:
    out = CACHE / "comments"
    out.mkdir(parents=True, exist_ok=True)
    es = sorted([e for e in _flat() if "#reklam" not in (e.get("title") or "")],
                key=lambda e: -(e.get("view_count") or 0))[:a.top]
    for e in es:
        if (out / f"{e['id']}.info.json").exists():
            continue
        ytdlp("--extractor-args", f"youtube:player_client=mweb;max_comments={a.adet},all,0,0;comment_sort=top",
              "--skip-download", "--write-comments", "-o", str(out / "%(id)s"),
              f"https://www.youtube.com/shorts/{e['id']}")
        print("ok", e["id"], e.get("title"))
        time.sleep(3)


def cmd_rapor(_a) -> None:
    flat = {e["id"]: e for e in _flat()}
    rows = []
    for vid, e in flat.items():
        m = {}
        p = CACHE / "meta" / f"{vid}.json"
        if p.exists() and p.stat().st_size:
            m = json.loads(p.read_text())
        rows.append({
            "id": vid,
            "url": f"https://www.youtube.com/shorts/{vid}",
            "upload_date": m.get("upload_date", ""),
            "duration": m.get("duration", ""),
            "views": m.get("view_count") or e.get("view_count") or "",
            "likes": m.get("like_count", ""),
            "comments": m.get("comment_count", ""),
            "title": m.get("title") or e.get("title"),
        })
    rows.sort(key=lambda r: r["upload_date"] or "0")
    with (ROOT / "data" / "videos.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"-> data/videos.csv ({len(rows)} video)")
    # Hesabın kendi sabit yorumları = olay metni örnekleri
    lines = ["# Hesabın sabit 'olay' yorumları (örnek metinler)", "",
             "YouTube yorumlarından toplandı. Yeni sabit yorum yazarken üslup referansı.", ""]
    cdir = CACHE / "comments"
    items = []
    for p in cdir.glob("*.info.json"):
        d = json.loads(p.read_text())
        own = [c for c in d.get("comments", []) if (c.get("author") or "").lower().lstrip("@") == "tarihselwojak"]
        if own:
            items.append((d.get("upload_date", ""), d, own[0]["text"]))
    for date, d, txt in sorted(items, key=lambda x: x[0]):
        lines += [f"## {d['title']}", "",
                  f"{date[:4]}-{date[4:6]}-{date[6:]} · {d.get('view_count', 0):,} izlenme · {d.get('duration')} sn".replace(",", "."),
                  "", txt.strip(), ""]
    (ROOT / "data" / "olay_metinleri.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"-> data/olay_metinleri.md ({len(items)} metin)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    for n, fn in (("liste", cmd_liste), ("detay", cmd_detay), ("kapak", cmd_kapak), ("rapor", cmd_rapor)):
        sp.add_parser(n).set_defaults(fn=fn)
    p = sp.add_parser("yorum")
    p.add_argument("--top", type=int, default=45)
    p.add_argument("--adet", type=int, default=40)
    p.set_defaults(fn=cmd_yorum)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
