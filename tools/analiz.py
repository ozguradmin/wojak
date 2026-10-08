#!/usr/bin/env python3
"""YouTube metadata'sından dönem/format/süre/saat analizleri (markdown tablolar).

    python tools/yt_arastir.py liste && python tools/yt_arastir.py detay   # önce veri
    python tools/analiz.py > /tmp/analiz.md

Dönem sınırları kapak karelerinin elle incelenmesiyle belirlendi (docs/ANALIZ.md).
"""

from __future__ import annotations

import csv
import json
import statistics as st
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / ".cache" / "yt"
TR = timezone(timedelta(hours=3))

ERAS = [  # (başlangıç dahil, ad)
    ("20231019", "1-Tarihsel (WW2/Çanakkale wojak)"),
    ("20231025", "2-Viral repost/meme (Low Budget Stories, split-screen)"),
    ("20231210", "3-OLAY altın dönem"),
    ("20240307", "4-Dağılma (gerçek video, reaction, 'vs' meme, reklam)"),
    ("20250101", "5-Olay'a dönüş (uzun yazı, AI sahne, seyrek)"),
]


def era(date: str) -> str:
    name = ERAS[0][1]
    for start, n in ERAS:
        if date >= start:
            name = n
    return name


def load() -> list[dict]:
    flat = json.loads((CACHE / "flat.json").read_text())["entries"]
    rows = []
    for e in flat:
        p = CACHE / "meta" / f"{e['id']}.json"
        if not p.exists() or not p.stat().st_size:
            continue
        m = json.loads(p.read_text())
        ts = m.get("timestamp")
        dt = datetime.fromtimestamp(ts, TR) if ts else None
        title = m.get("title") or ""
        rows.append({
            "id": m["id"], "date": m["upload_date"], "dt": dt,
            "hour": dt.hour if dt else None, "weekday": dt.weekday() if dt else None,
            "dur": m.get("duration") or 0, "views": m.get("view_count") or 0,
            "likes": m.get("like_count") or 0, "comments": m.get("comment_count") or 0,
            "title": title, "era": era(m["upload_date"]),
            "ad": "#reklam" in title,
            "olay_tag": any(k in title.lower() for k in ("yorumlara yazdım", "yorumlarda", "yorum kısmına",
                                                         "yorumlar kısmında", "olayı bilenler")),
        })
    rows.sort(key=lambda r: r["date"])
    return rows


def fmt(n: float) -> str:
    if n >= 1e6:
        return f"{n / 1e6:.2f}M"
    if n >= 1e3:
        return f"{n / 1e3:.0f}K"
    return f"{n:.0f}"


def table(groups: dict[str, list[dict]], label: str) -> str:
    out = [f"| {label} | Video | Medyan izlenme | Ortalama | ≥500K oranı | Medyan süre | Beğeni/izlenme |",
           "|---|---:|---:|---:|---:|---:|---:|"]
    for k, rs in groups.items():
        if not rs:
            continue
        v = [r["views"] for r in rs]
        lr = st.median([r["likes"] / r["views"] for r in rs if r["views"]]) * 100
        out.append(f"| {k} | {len(rs)} | {fmt(st.median(v))} | {fmt(st.mean(v))} | "
                   f"%{100 * sum(x >= 500_000 for x in v) / len(v):.0f} | {st.median(r['dur'] for r in rs):.0f} sn | %{lr:.1f} |")
    return "\n".join(out)


def main() -> None:
    rows = [r for r in load() if not r["ad"]]
    print(f"Analiz edilen video: {len(rows)} (reklamlar hariç)\n")

    print("## Dönemler\n")
    g = defaultdict(list)
    for r in rows:
        g[r["era"]].append(r)
    print(table(dict(sorted(g.items())), "Dönem"))

    print("\n### Paylaşım sıklığı (dönem içi)\n")
    print("| Dönem | İlk | Son | Video | Video/hafta |\n|---|---|---|---:|---:|")
    for k, rs in sorted(g.items()):
        d0 = datetime.strptime(rs[0]["date"], "%Y%m%d")
        d1 = datetime.strptime(rs[-1]["date"], "%Y%m%d")
        weeks = max(1, (d1 - d0).days / 7)
        print(f"| {k} | {d0:%Y-%m-%d} | {d1:%Y-%m-%d} | {len(rs)} | {len(rs) / weeks:.1f} |")

    print("\n## Süre (tüm dönemler)\n")
    b = defaultdict(list)
    for r in rows:
        d = r["dur"]
        key = "≤10 sn" if d <= 10 else "11-15 sn" if d <= 15 else "16-30 sn" if d <= 30 else "31-60 sn"
        b[key].append(r)
    print(table({k: b[k] for k in ("≤10 sn", "11-15 sn", "16-30 sn", "31-60 sn")}, "Süre"))

    print("\n## Süre — sadece 2024-03 sonrası (format karışık dönem)\n")
    b = defaultdict(list)
    for r in rows:
        if r["date"] < "20240307":
            continue
        d = r["dur"]
        key = "≤15 sn" if d <= 15 else "16-30 sn" if d <= 30 else "31-60 sn"
        b[key].append(r)
    print(table({k: b[k] for k in ("≤15 sn", "16-30 sn", "31-60 sn")}, "Süre"))

    print("\n## Başlıkta 'olayı yorumlara yazdım' tipi ibare\n")
    b = {"Var": [r for r in rows if r["olay_tag"]], "Yok (aynı dönem 2023-11-25..2024-03-06)":
         [r for r in rows if not r["olay_tag"] and "20231125" <= r["date"] <= "20240306"]}
    print(table(b, "İbare"))

    print("\n## Paylaşım saati (TR saati, tüm dönemler)\n")
    b = defaultdict(list)
    for r in rows:
        if r["hour"] is None:
            continue
        h = r["hour"]
        key = "00-06" if h < 6 else "06-12" if h < 12 else "12-17" if h < 17 else "17-21" if h < 21 else "21-24"
        b[key].append(r)
    print(table({k: b[k] for k in ("00-06", "06-12", "12-17", "17-21", "21-24") if k in b}, "Saat"))

    for era_key, label in (("3-", "altın dönem"), ("4-", "dağılma dönemi")):
        print(f"\n## Paylaşım saati — sadece {label}\n")
        b = defaultdict(list)
        for r in rows:
            if r["hour"] is None or not r["era"].startswith(era_key):
                continue
            h = r["hour"]
            key = "00-17" if h < 17 else "17-19" if h < 19 else "19-21" if h < 21 else "21-24"
            b[key].append(r)
        print(table({k: b[k] for k in ("00-17", "17-19", "19-21", "21-24") if k in b}, "Saat"))

    print("\n## En çok izlenen 25\n")
    print("| # | Tarih | Süre | İzlenme | Beğeni | Dönem | Başlık |\n|---:|---|---:|---:|---:|---|---|")
    for i, r in enumerate(sorted(rows, key=lambda r: -r["views"])[:25], 1):
        print(f"| {i} | {r['date'][:4]}-{r['date'][4:6]}-{r['date'][6:]} | {r['dur']} | {fmt(r['views'])} | "
              f"{fmt(r['likes'])} | {r['era'][0]} | {r['title'][:70]} |")

    print("\n## Son 15 video\n")
    print("| Tarih | Süre | İzlenme | Başlık |\n|---|---:|---:|---|")
    for r in rows[-15:]:
        print(f"| {r['date'][:4]}-{r['date'][4:6]}-{r['date'][6:]} | {r['dur']} | {fmt(r['views'])} | {r['title'][:70]} |")

    with (ROOT / "data" / "videos.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "url", "tarih", "saat_tr", "sure_sn", "izlenme", "begeni", "yorum", "donem", "baslik"])
        for r in load():
            w.writerow([r["id"], f"https://www.youtube.com/shorts/{r['id']}", r["date"],
                        r["dt"].strftime("%H:%M") if r["dt"] else "", r["dur"], r["views"], r["likes"],
                        r["comments"], r["era"].split("-")[0], r["title"]])


if __name__ == "__main__":
    main()
