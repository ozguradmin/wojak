#!/usr/bin/env python3
"""@tarihselwojak Instagram reel'lerini istatistikleriyle indirir.

Gereken ortam değişkeni (cloud environment ayarlarından eklenir, ASLA repoya
yazılmaz): IG_SESSIONID  (opsiyonel: IG_CSRFTOKEN, IG_DS_USER_ID)

Ana hesabın değil ikincil bir hesabın cookie'si kullanılmalı.

Kullanım:
    python tools/ig_fetch.py                 # sadece istatistik -> data/instagram_posts.csv
    python tools/ig_fetch.py --download 30   # en çok izlenen 30 reel'i referans/ içine indir
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from wojak import config  # noqa: E402

config.load_secrets()  # IG_* ortamda yoksa repo dışındaki ~/.config/wojak/secrets.env
USER = "tarihselwojak"
APP_ID = "936619743392459"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")


def session() -> requests.Session:
    sid = os.environ.get("IG_SESSIONID")
    if not sid:
        sys.exit("IG_SESSIONID ortam değişkeni yok. Cloud environment ayarlarından ekleyin.")
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "X-IG-App-ID": APP_ID, "Accept": "*/*",
                      "Referer": f"https://www.instagram.com/{USER}/"})
    s.cookies.set("sessionid", sid, domain=".instagram.com")
    if os.environ.get("IG_CSRFTOKEN"):
        s.cookies.set("csrftoken", os.environ["IG_CSRFTOKEN"], domain=".instagram.com")
        s.headers["X-CSRFToken"] = os.environ["IG_CSRFTOKEN"]
    if os.environ.get("IG_DS_USER_ID"):
        s.cookies.set("ds_user_id", os.environ["IG_DS_USER_ID"], domain=".instagram.com")
    return s


def user_id(s: requests.Session) -> str:
    r = s.get("https://www.instagram.com/api/v1/users/web_profile_info/", params={"username": USER})
    r.raise_for_status()
    u = r.json()["data"]["user"]
    print(f"{u['full_name']}: {u['edge_followed_by']['count']} takipçi, "
          f"{u['edge_owner_to_timeline_media']['count']} gönderi")
    return u["id"]


def all_posts(s: requests.Session, uid: str) -> list[dict]:
    items, max_id = [], None
    while True:
        params = {"count": 33}
        if max_id:
            params["max_id"] = max_id
        r = s.get(f"https://www.instagram.com/api/v1/feed/user/{uid}/", params=params)
        if r.status_code == 429:
            print("429 — 60 sn bekleniyor"); time.sleep(60); continue
        r.raise_for_status()
        d = r.json()
        items += d.get("items", [])
        print(f"  {len(items)} gönderi alındı")
        if not d.get("more_available"):
            return items
        max_id = d.get("next_max_id")
        time.sleep(2)


def row(it: dict) -> dict:
    cap = (it.get("caption") or {}).get("text", "")
    vids = it.get("video_versions") or []
    return {
        "code": it.get("code"),
        "url": f"https://www.instagram.com/reel/{it.get('code')}/",
        "taken_at": time.strftime("%Y-%m-%d", time.gmtime(it.get("taken_at", 0))),
        "media_type": it.get("media_type"),
        "duration": round(it.get("video_duration") or 0, 1),
        "plays": it.get("play_count") or it.get("ig_play_count") or it.get("view_count") or "",
        "likes": it.get("like_count"),
        "comments": it.get("comment_count"),
        "width": it.get("original_width"),
        "height": it.get("original_height"),
        "audio": json.dumps((it.get("clips_metadata") or {}).get("music_info") or
                            (it.get("clips_metadata") or {}).get("original_sound_info") or {},
                            ensure_ascii=False)[:500],
        "caption": cap.replace("\n", " ")[:1000],
        "video_url": vids[0]["url"] if vids else "",
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--download", type=int, default=0, help="en çok izlenen N reel'i indir")
    a = ap.parse_args()
    s = session()
    uid = user_id(s)
    rows = [row(it) for it in all_posts(s, uid)]
    out = ROOT / "data" / "instagram_posts.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[k for k in rows[0] if k != "video_url"], extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(f"-> {out}")
    if a.download:
        ref = ROOT / "referans"
        ref.mkdir(exist_ok=True)
        top = sorted([r for r in rows if r["video_url"]], key=lambda r: -(r["plays"] or 0))[:a.download]
        for r in top:
            p = ref / f"{r['taken_at']}_{r['code']}.mp4"
            if p.exists():
                continue
            with s.get(r["video_url"], stream=True) as resp:
                resp.raise_for_status()
                with p.open("wb") as fh:
                    for chunk in resp.iter_content(1 << 16):
                        fh.write(chunk)
            print(f"  indirildi: {p.name} ({r['plays']} izlenme)")
            time.sleep(1.5)


if __name__ == "__main__":
    main()
