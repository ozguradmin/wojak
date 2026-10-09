#!/usr/bin/env python3
"""Instagram'a Reels yayınlama (Instagram API with Instagram Login — resmi Meta API'si).

Kurulum ve token alma: docs/arsiv/OTOMATIK_YAYIN.md > 2. Instagram yayın token'ı

Ortam değişkenleri (cloud environment ayarlarından; ASLA repoya/sohbete yazılmaz):
    IG_ACCESS_TOKEN   60 günlük Instagram kullanıcı token'ı (App Dashboard > Generate token)
    IG_USER_ID        (ops.) Instagram kullanıcı ID'si; yoksa /me'den alınır
    IG_API_VERSION    (ops.) varsayılan v26.0
    IG_API_HOST       (ops.) graph.instagram.com (Instagram Login, varsayılan) veya
                      graph.facebook.com (Facebook Login; doğrudan dosya yükleme destekli)
    R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET
                      (--r2 için) Cloudflare R2: videoyu geçici, imzalı bir HTTPS linkine koyar.
                      Kurulum: docs/arsiv/OTOMATIK_YAYIN.md > 2.8

Komutlar:
    python tools/ig_yayinla.py kontrol
        token geçerli mi, hesap tipi, günlük yayın kotası
    python tools/ig_yayinla.py yayinla episodes/derinkuyu --video-url https://.../derinkuyu.mp4 [--kapak-url URL]
        konteyner -> işlenmeyi bekle -> yayınla -> sabit yorum metnini yorum olarak yaz
    python tools/ig_yayinla.py yayinla episodes/derinkuyu --dosya out/derinkuyu/derinkuyu.mp4 --r2 \
            --kapak out/derinkuyu/kapak.jpg
        (ÖNERİLEN) mp4'ü R2'ye yükler, 2 saatlik imzalı linki Meta'ya verir, yayından sonra siler
    python tools/ig_yayinla.py yayinla episodes/derinkuyu --dosya out/derinkuyu/derinkuyu.mp4
        doğrudan dosya yükleme (resumable). Resmi olarak yalnızca Facebook Login yolunda var;
        Instagram Login'de büyük olasılıkla reddedilir -> --r2 kullan.
    python tools/ig_yayinla.py yayinla ... --trial
        "deneme reel": önce yalnızca takip etmeyenlere gösterilir (format A/B testi için)
    python tools/ig_yayinla.py yayinla ... --deneme
        hiçbir şey göndermeden ne yapılacağını gösterir
    python tools/ig_yayinla.py yenile [--goster]
        60 günlük token'ı yeniler (en az 24 saatlik ve süresi dolmamış olmalı). Dönen token farklıysa
        ortam değişkenini güncellemek gerekir (araç söyler).
    python tools/ig_yayinla.py yorum episodes/derinkuyu
        episode.yaml'daki (düzeltilmiş) sabit yorumu yeni yorum olarak yazar, eskisini siler
        (API yorum düzenlemeye izin vermiyor). Yeni yorumu telefondan yeniden sabitle.
    python tools/ig_yayinla.py yorumlar episodes/derinkuyu --kapat | --ac
        gönderinin yorumlarını kapatır/açar (linç, isim ifşası riski olan gündem videoları)

Notlar:
  * API ile yorum SABİTLENEMEZ (Meta API'sinde yok). Yorum otomatik yazılır; telefondan
    yoruma uzun bas (Android) / sola kaydır (iOS) -> raptiye.
  * Instagram Login yolunda video herkese açık bir HTTPS adresinde olmalı (Meta oradan indirir) -> --r2.
  * API ile gönderi silinemez ve açıklama düzenlenemez: yayın yasağı / aile talebinde telefondan kaldır.
  * Yayın bilgisi (medya ve yorum ID'leri) out/<bölüm>/yayin.json'a yazılır.
  * Instagram müzik kütüphanesinden ses eklemek (Audio API, audio_configuration) yalnızca Facebook
    Login yolunda var. Varsayılan: videoya gömülü imza müzik (orijinal ses).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from wojak import censor, denetim, episode, pack  # noqa: E402

VERSION = os.environ.get("IG_API_VERSION", "v26.0")
HOST = os.environ.get("IG_API_HOST", "graph.instagram.com")
BASE = f"https://{HOST}/{VERSION}"


def token() -> str:
    t = os.environ.get("IG_ACCESS_TOKEN")
    if not t:
        sys.exit("IG_ACCESS_TOKEN yok. Kurulum: docs/arsiv/OTOMATIK_YAYIN.md > 2. Instagram yayın token'ı")
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


def _r2():
    try:
        import boto3
        from botocore.config import Config
    except ImportError:
        sys.exit("--r2 için boto3 gerekli: pip install boto3")
    need = ["R2_ACCOUNT_ID", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY", "R2_BUCKET"]
    miss = [k for k in need if not os.environ.get(k)]
    if miss:
        sys.exit(f"R2 ortam değişkenleri eksik: {', '.join(miss)}. Kurulum: docs/arsiv/OTOMATIK_YAYIN.md > 2.8")
    s3 = boto3.client("s3", endpoint_url=f"https://{os.environ['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
                      aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
                      aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
                      region_name="auto", config=Config(signature_version="s3v4"))
    return s3, os.environ["R2_BUCKET"]


def _r2_put(path: Path, key: str, ctype: str) -> str:
    """Dosyayı R2'ye yükler, Meta'nın indirebileceği 2 saatlik imzalı GET linki döndürür."""
    s3, bucket = _r2()
    s3.upload_file(str(path), bucket, key, ExtraArgs={"ContentType": ctype})
    return s3.generate_presigned_url("get_object", Params={"Bucket": bucket, "Key": key}, ExpiresIn=7200)


def _r2_delete(keys: list[str]) -> None:
    s3, bucket = _r2()
    for k in keys:
        s3.delete_object(Bucket=bucket, Key=k)


def _kayit_yolu(ep: episode.Episode) -> Path:
    return ROOT / "out" / ep.id / "yayin.json"


def _kayit(ep: episode.Episode) -> dict:
    f = _kayit_yolu(ep)
    if not f.exists():
        sys.exit(f"{f} yok: bu bölüm bu araçla yayınlanmamış (medya ID'si bilinmiyor).")
    return json.loads(f.read_text(encoding="utf-8"))


def _kaydet(ep: episode.Episode, d: dict) -> None:
    f = _kayit_yolu(ep)
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


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
    if a.r2 and not a.dosya:
        sys.exit("--r2 için --dosya gerekli")
    for f in (a.dosya, a.kapak):
        if f and not Path(f).is_file():
            sys.exit(f"Dosya yok: {f}")
    if len(pinned) > 2200:
        print(f"  ⚠ sabit yorum {len(pinned)} karakter; Instagram yorum sınırı ~2200 (API'de belgelenmemiş)")
    params = {"media_type": "REELS", "caption": cap}
    if a.trial:  # deneme reel: önce yalnızca takip etmeyenlere gösterilir
        strat = "SS_PERFORMANCE" if a.trial == "otomatik" else "MANUAL"
        params["trial_params"] = json.dumps({"graduation_strategy": strat})
    else:
        params["share_to_feed"] = "true"
    if ep.ai_generated:  # fotogerçekçi yapay zekâ görseli: Meta etiket istiyor
        params["is_ai_generated"] = "true"
    uyarilar = denetim.check(ep)
    for u in uyarilar:
        print(f"  ⚠ {u}")
    if ep.gundem and uyarilar and not a.zorla:
        sys.exit("Güncel olay bölümünde denetim uyarıları var; düzelt ya da bilerek --zorla kullan.")
    if a.kapak_url:
        params["cover_url"] = a.kapak_url
    elif not (a.r2 and a.kapak):
        params["thumb_offset"] = str(int(a.kapak_ms))
    if a.video_url:
        params["video_url"] = a.video_url
    elif not a.r2:
        params["upload_type"] = "resumable"
    print(f"Bölüm: {ep.id} · {ep.duration:.1f} sn\nAçıklama ({len(cap)} karakter):\n{cap}\n")
    print(f"Sabit yorum ({len(pinned)} karakter): {pinned[:120]}...\n")
    if a.deneme:
        print("[deneme] gönderilecek parametreler:", {k: (v if k != "caption" else "...") for k, v in params.items()})
        return
    r2_keys: list[str] = []
    if a.r2:
        key = f"{ep.id}/{int(time.time())}"
        params["video_url"] = _r2_put(Path(a.dosya), key + ".mp4", "video/mp4")
        r2_keys.append(key + ".mp4")
        if a.kapak and not a.kapak_url:
            params["cover_url"] = _r2_put(Path(a.kapak), key + "_kapak.jpg", "image/jpeg")
            r2_keys.append(key + "_kapak.jpg")
        print("  R2'ye yüklendi (2 saatlik imzalı link)")
    uid = user_id()
    c = api("POST", f"{uid}/media", data=params)
    cid = c["id"]
    print(f"Konteyner: {cid}")
    if a.dosya and not a.r2:
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
    print(f"YAYINLANDI: {link}  (medya ID: {mid})")
    kayit = {"media_id": mid, "permalink": link, "yayin": time.strftime("%Y-%m-%d %H:%M"),
             "trial": a.trial or None, "comment_id": None}
    if r2_keys and not a.r2_sakla:
        _r2_delete(r2_keys)
    if pinned and not a.yorumsuz:
        com = api("POST", f"{mid}/comments", data={"message": pinned})
        kayit["comment_id"] = com.get("id")
        print(f"Yorum yazıldı ({com.get('id')}). ŞİMDİ telefondan sabitle: yoruma uzun bas (Android) / "
              "sola kaydır (iOS) -> raptiye.")
    _kaydet(ep, kayit)


def cmd_yorum(a) -> None:
    """Düzeltme/güncelleme: yeni yorumu yaz, sonra eskisini sil (önce silinirse ve yazma başarısız olursa
    hikâye tamamen kaybolur)."""
    ep = episode.load(a.bolum)
    k = _kayit(ep)
    text = censor.metin(ep.pinned_comment.strip())
    com = api("POST", f"{k['media_id']}/comments", data={"message": text})
    print(f"Yeni yorum yazıldı ({com.get('id')}).")
    if k.get("comment_id"):
        api("DELETE", k["comment_id"])
        print(f"Eski yorum silindi ({k['comment_id']}).")
    k["comment_id"] = com.get("id")
    _kaydet(ep, k)
    print("Telefondan yeni yorumu sabitle.")


def cmd_yorumlar(a) -> None:
    ep = episode.load(a.bolum)
    k = _kayit(ep)
    api("POST", k["media_id"], data={"comment_enabled": "false" if a.kapat else "true"})
    print(f"Yorumlar {'kapatıldı' if a.kapat else 'açıldı'}: {k.get('permalink')}")


def cmd_yenile(a) -> None:
    r = requests.get(f"https://{HOST}/refresh_access_token",
                     params={"grant_type": "ig_refresh_token", "access_token": token()}, timeout=60)
    d = r.json()
    if "access_token" not in d:
        raise SystemExit(f"Yenilenemedi: {d}")
    days = int(d.get("expires_in", 0)) // 86400
    print(f"Token yenilendi, {days} gün geçerli.")
    if d["access_token"] == token():
        print("Token dizesi aynı kaldı: ortam değişkeninde bir şey değiştirmen gerekmiyor.")
    elif a.goster:
        print("Token dizesi DEĞİŞTİ; IG_ACCESS_TOKEN ortam değişkenini bununla güncelle:")
        print(d["access_token"])
    else:
        print("Token dizesi DEĞİŞTİ: IG_ACCESS_TOKEN'ı güncellemek için --goster ile tekrar çalıştır "
              "(eski dize süresi dolunca çalışmaz).")


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
    p.add_argument("--zorla", action="store_true", help="güncel olay denetim uyarılarına rağmen yayınla")
    p.add_argument("--r2", action="store_true", help="--dosya'yı Cloudflare R2'ye yükleyip linkini kullan")
    p.add_argument("--r2-sakla", action="store_true", help="yayından sonra R2'deki dosyayı silme")
    p.add_argument("--kapak", help="yerel kapak JPEG'i (--r2 ile yüklenir)")
    p.add_argument("--trial", nargs="?", const="elle", choices=["elle", "otomatik"],
                   help="deneme reel: önce takip etmeyenlere; 'otomatik' iyi giderse takipçilere de açılır")
    p.set_defaults(fn=cmd_yayinla)
    p = sp.add_parser("yorum", help="sabit yorumu güncelle (yeni yaz, eskisini sil)")
    p.add_argument("bolum")
    p.set_defaults(fn=cmd_yorum)
    p = sp.add_parser("yorumlar", help="yorumları kapat/aç")
    p.add_argument("bolum")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--kapat", action="store_true")
    g.add_argument("--ac", action="store_true")
    p.set_defaults(fn=cmd_yorumlar)
    p = sp.add_parser("yenile")
    p.add_argument("--goster", action="store_true", help="yeni token'ı ekrana yaz")
    p.set_defaults(fn=cmd_yenile)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
