#!/usr/bin/env python3
"""@tarihselwojak YouTube kanalına video yükler (YouTube Data API v3).

Kimlik: YOUTUBE_TOKEN_JSON (OAuth "authorized_user" JSON'u; ortam değişkeni ya da ~/.config/wojak/secrets.env). Hiçbir
yere yazılmaz, hata mesajlarında gösterilmez. Kanal kimliği denetlenir: başka bir kanala yükleme yapılmaz.
Kota: günde 10.000 birim (başka kanallarla ortak), yükleme 1.600 birim -> bu kanal için günde en çok 3 yükleme.
Kural: hesap sahibi başlık/açıklama/gizlilik ayarını görüp "yükle" demeden yükleme yok; ilk yükleme private.

    python tools/yt_yukle.py --kontrol                       # yalnız kimlik + kanal denetimi (kota harcamaz sayılır: 1 birim)
    python tools/yt_yukle.py video.mp4 --title "..." --desc-file aciklama.txt [--tags a,b] [--privacy private] [--thumb kapak.jpg]

Kurulum: pip install google-api-python-client google-auth
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from wojak import config  # noqa: E402

CHANNEL_ID = "UCZqB6PyZKjono6d17xAgqvw"  # @tarihselwojak; başka kanala yükleme reddedilir


def youtube():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    config.load_secrets()
    raw = os.environ.get("YOUTUBE_TOKEN_JSON", "").strip()
    if not raw:
        sys.exit("YOUTUBE_TOKEN_JSON ortam değişkeni eksik")
    try:
        c = Credentials.from_authorized_user_info(json.loads(raw))
        c.refresh(Request())
    except Exception as e:  # içeriği değil yalnız türü göster
        sys.exit(f"kimlik yenilenemedi: {type(e).__name__} ({'invalid_grant: izin iptal edilmiş' if 'invalid_grant' in str(e) else 'ayrıntı gizli'})")
    yt = build("youtube", "v3", credentials=c, cache_discovery=False)
    ids = [i["id"] for i in yt.channels().list(part="id", mine=True).execute().get("items", [])]
    if CHANNEL_ID not in ids:
        sys.exit(f"yanlış kanal: {ids}")
    return yt


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video", nargs="?")
    ap.add_argument("--kontrol", action="store_true")
    ap.add_argument("--title")
    ap.add_argument("--desc-file")
    ap.add_argument("--tags", default="")
    ap.add_argument("--privacy", default="private", choices=["public", "unlisted", "private"])
    ap.add_argument("--thumb")
    ap.add_argument("--kategori", default="27", help="27 Eğitim, 24 Eğlence")
    a = ap.parse_args()
    yt = youtube()
    if a.kontrol:
        print(json.dumps({"kanal": CHANNEL_ID, "durum": "ok"}))
        return
    if not (a.video and a.title and a.desc_file):
        ap.error("video, --title ve --desc-file gerekli")
    from googleapiclient.http import MediaFileUpload
    body = {
        "snippet": {"title": a.title[:100], "description": Path(a.desc_file).read_text(encoding="utf-8")[:4900],
                    "tags": [t.strip() for t in a.tags.split(",") if t.strip()], "categoryId": a.kategori,
                    "defaultLanguage": "tr", "defaultAudioLanguage": "tr"},
        "status": {"privacyStatus": a.privacy, "selfDeclaredMadeForKids": False},
    }
    req = yt.videos().insert(part="snippet,status", body=body,
                             media_body=MediaFileUpload(a.video, chunksize=8 * 1024 * 1024, resumable=True))
    resp = None
    while resp is None:
        _, resp = req.next_chunk()
    vid = resp["id"]
    if a.thumb:
        try:
            yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(a.thumb)).execute()
        except Exception as e:  # Shorts özel kapağı yok sayar; doğrulanmamış kanal kapak koyamaz
            print("kapak atlandı:", type(e).__name__, file=sys.stderr)
    print(json.dumps({"id": vid, "url": f"https://youtube.com/shorts/{vid}", "privacy": resp["status"]["privacyStatus"]},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
