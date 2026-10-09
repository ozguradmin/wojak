#!/usr/bin/env python3
"""Instagram'a Reels yayınlama (Instagram API with Instagram Login — resmi Meta API'si).

Kurulum ve token alma: docs/GEREKENLER.md > 2. Instagram yayın token'ı

Ortam değişkenleri (cloud environment ayarlarından; ASLA repoya/sohbete yazılmaz):
    IG_ACCESS_TOKEN   60 günlük Instagram kullanıcı token'ı (App Dashboard > Generate token)
    IG_USER_ID        (ops.) Instagram kullanıcı ID'si; yoksa /me'den alınır
    IG_API_VERSION    (ops.) varsayılan v26.0
    IG_API_HOST       (ops.) graph.instagram.com (Instagram Login, varsayılan) veya
                      graph.facebook.com (Facebook Login; doğrudan dosya yükleme destekli)

Komutlar:
    python tools/ig_yayinla.py kontrol
        token geçerli mi, hesap tipi, günlük yayın kotası
    python tools/ig_yayinla.py yayinla episodes/derinkuyu --video-url https://.../derinkuyu.mp4 [--kapak-url URL]
        konteyner -> işlenmeyi bekle -> yayınla -> sabit yorum metnini yorum olarak yaz
    python tools/ig_yayinla.py yayinla episodes/derinkuyu --dosya out/derinkuyu/derinkuyu.mp4
        doğrudan dosya yükleme (resumable). Resmi olarak yalnızca Facebook Login yolunda var;
        Instagram Login'de denenir, olmazsa --video-url gerekir.
    python tools/ig_yayinla.py yayinla ... --deneme
        hiçbir şey göndermeden ne yapılacağını gösterir
    python tools/ig_yayinla.py yenile [--goster]
        60 günlük token'ı yeniler (en az 24 saatlik ve süresi dolmamış olmalı). Yeni token'ı
        ortam değişkenine kaydetmeyi unutma.

Notlar:
  * API ile yorum SABİTLENEMEZ (Meta API'sinde yok). Yorum otomatik yazılır; telefondan
    yoruma uzun bas (Android) / sola kaydır (iOS) -> raptiye.
  * Instagram Login yolunda video herkese açık bir HTTPS adresinde olmalı (Meta oradan indirir).
  * Instagram müzik kütüphanesinden ses eklemek (Audio API, audio_configuration) yalnızca Facebook
    Login yolunda var. Varsayılan: videoya gömülü imza müzik (orijinal ses).
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from wojak import censor, episode, pack  # noqa: E402

VERSION = os.environ.get("IG_API_VERSION", "v26.0")
HOST = os.environ.get("IG_API_HOST", "graph.instagram.com")
BASE = f"https://{HOST}/{VERSION}"


def token() -> str:
    t = os.environ.get("IG_ACCESS_TOKEN")
    if not t:
        sys.exit("IG_ACCESS_TOKEN yok. Kurulum: docs/GEREKENLER.md > 2. Instagram yayın token'ı")
    return t


def api(method: str, path: str, **kw) -> dict:
    url = path if path.startswith("http") else f"{BASE}/{path.lstrip('/')}"
    r = requests.request(method, url, headers={"Authorization": f"Bearer {token()}"}, timeout=120, **kw)
    try:
        d = r.json()
    except ValueError:
        d = {"raw": r.text[:300]}
    if r.status_code >= 400 or "error" in d:
        err = d.get("error", d)
        raise SystemExit(f"API hatası ({r.status_code}) {path}: {err.get('message', err)} "
                         f"[kod {err.get('code')}/{err.get('error_subcode')}]\n"
                         "Sık hatalar: 190=token geçersiz/süresi dolmuş, 2207052=video URL'den indirilemedi, "
                         "2207026=video formatı, 2207042=günlük limit.")
    return d


def user_id() -> str:
    return os.environ.get("IG_USER_ID") or api("GET", "me", params={"fields": "user_id,username"})["user_id"]


def cmd_kontrol(_a) -> None:
    me = api("GET", "me", params={"fields": "user_id,username,account_type"})
    print(f"Hesap: @{me.get('username')} · tip: {me.get('account_type')} · user_id: {me.get('user_id')}")
    q = api("GET", f"{me['user_id']}/content_publishing_limit", params={"fields": "config,quota_usage"})
    data = (q.get("data") or [{}])[0]
    print(f"Son 24 saatte API ile yayın: {data.get('quota_usage')} / {data.get('config', {}).get('quota_total')}")


def _caption(ep: episode.Episode) -> str:
    title = censor.metin(ep.title)
    body = censor.metin(ep.caption.strip())
    parts = [title] + ([body] if body and body.splitlines()[0].strip() != title else []) + [pack.hashtags(ep)]
    cap = "\n\n".join(p for p in parts if p)
    if len(cap) > 2200:
        sys.exit(f"Açıklama 2200 karakteri aşıyor ({len(cap)})")
    return cap


def _wait(cid: str, limit_s: int = 600) -> None:
    t0 = time.time()
    while True:
        st = api("GET", cid, params={"fields": "status_code,status"})
        code = st.get("status_code")
        print(f"  durum: {code} {st.get('status', '')}")
        if code == "FINISHED":
            return
        if code in ("ERROR", "EXPIRED"):
            raise SystemExit(f"Video işlenemedi: {st}")
        if time.time() - t0 > limit_s:
            raise SystemExit("Video 10 dakikada işlenmedi; daha sonra 'durum' ile tekrar dene.")
        time.sleep(20)


def cmd_yayinla(a) -> None:
    ep = episode.load(a.bolum)
    cap = _caption(ep)
    pinned = censor.metin(ep.pinned_comment.strip())
    if not (a.video_url or a.dosya):
        sys.exit("--video-url (herkese açık HTTPS adresi) veya --dosya gerekli")
    params = {"media_type": "REELS", "caption": cap, "share_to_feed": "true"}
    if a.kapak_url:
        params["cover_url"] = a.kapak_url
    else:
        params["thumb_offset"] = str(int(a.kapak_ms))
    if a.video_url:
        params["video_url"] = a.video_url
    else:
        params["upload_type"] = "resumable"
    print(f"Bölüm: {ep.id} · {ep.duration:.1f} sn\nAçıklama ({len(cap)} karakter):\n{cap}\n")
    print(f"Sabit yorum ({len(pinned)} karakter): {pinned[:120]}...\n")
    if a.deneme:
        print("[deneme] gönderilecek parametreler:", {k: (v if k != "caption" else "...") for k, v in params.items()})
        return
    uid = user_id()
    c = api("POST", f"{uid}/media", data=params)
    cid = c["id"]
    print(f"Konteyner: {cid}")
    if a.dosya:
        f = Path(a.dosya)
        uri = c.get("uri") or f"https://rupload.facebook.com/ig-api-upload/{VERSION}/{cid}"
        r = requests.post(uri, headers={"Authorization": f"OAuth {token()}", "offset": "0",
                                        "file_size": str(f.stat().st_size)}, data=f.read_bytes(), timeout=600)
        if r.status_code >= 400:
            raise SystemExit(f"Dosya yüklenemedi ({r.status_code}): {r.text[:300]}\n"
                             "Instagram Login yolunda doğrudan yükleme desteklenmiyor olabilir: --video-url kullan.")
        print("  dosya yüklendi")
    _wait(cid)
    media = api("POST", f"{uid}/media_publish", data={"creation_id": cid})
    mid = media["id"]
    link = api("GET", mid, params={"fields": "permalink"}).get("permalink")
    print(f"YAYINLANDI: {link}")
    if pinned and not a.yorumsuz:
        com = api("POST", f"{mid}/comments", data={"message": pinned})
        print(f"Yorum yazıldı ({com.get('id')}). ŞİMDİ telefondan sabitle: yoruma uzun bas (Android) / "
              "sola kaydır (iOS) -> raptiye.")


def cmd_yenile(a) -> None:
    r = requests.get(f"https://{HOST}/refresh_access_token",
                     params={"grant_type": "ig_refresh_token", "access_token": token()}, timeout=60)
    d = r.json()
    if "access_token" not in d:
        raise SystemExit(f"Yenilenemedi: {d}")
    days = int(d.get("expires_in", 0)) // 86400
    print(f"Token yenilendi, {days} gün geçerli.")
    if a.goster:
        print(d["access_token"])
    else:
        print("Yeni token'ı görmek ve ortam değişkenini güncellemek için: --goster")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("kontrol").set_defaults(fn=cmd_kontrol)
    p = sp.add_parser("yayinla")
    p.add_argument("bolum", help="episodes/<id> (başlık, açıklama, sabit yorum buradan)")
    p.add_argument("--video-url", help="mp4'ün herkese açık HTTPS adresi")
    p.add_argument("--dosya", help="yerel mp4 (resumable yükleme dener)")
    p.add_argument("--kapak-url", help="kapak JPEG'inin herkese açık adresi")
    p.add_argument("--kapak-ms", type=float, default=900, help="kapak karesi (ms), kapak-url yoksa")
    p.add_argument("--yorumsuz", action="store_true", help="sabit yorum metnini yorum olarak yazma")
    p.add_argument("--deneme", action="store_true", help="hiçbir şey göndermeden göster")
    p.set_defaults(fn=cmd_yayinla)
    p = sp.add_parser("yenile")
    p.add_argument("--goster", action="store_true", help="yeni token'ı ekrana yaz")
    p.set_defaults(fn=cmd_yenile)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
