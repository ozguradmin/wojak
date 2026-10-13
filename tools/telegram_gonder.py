"""Teslim dosyalarını hesap sahibine Telegram botuyla gönderir (kalite kaybı yok: belge olarak).

Bot API tek dosyada en fazla 50 MB kabul eder. Daha büyük dosyalar (uzun video) sıkıştırmasız 7-Zip
parçalarına bölünür (`.7z.001`, `.7z.002` ...); hepsi aynı klasöre indirilip ilk parça açılınca tek dosya çıkar
(Windows: 7-Zip, Mac: Keka / The Unarchiver, Android: ZArchiver).

Gizli bilgiler: TELEGRAM_BOT_TOKEN ve TELEGRAM_CHAT_ID yalnız ortamdan ya da ~/.config/wojak/secrets.env'den
okunur; hiçbir yere yazılmaz, hata mesajlarında maskelenir.

    python tools/telegram_gonder.py --mesaj "Uzun video hazır"
    python tools/telegram_gonder.py teslim/<id>-uzun/<id>.mp4 teslim/<id>-uzun/kucukresim_k1.jpg --aciklama "..."
    python tools/telegram_gonder.py out/onizleme/x.mp4 --video      # 50 MB altı: Telegram'da oynatılabilir video
"""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from wojak import config  # noqa: E402

API = "https://api.telegram.org/bot{tok}/{yontem}"
SINIR = 49 * 1024 * 1024        # Bot API sınırı 50 MB; pay bırak
PARCA = 45 * 1024 * 1024
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"


def _kimlik() -> tuple[str, str]:
    config.load_secrets()
    tok = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not tok or not chat:
        sys.exit("TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID yok (ortam değişkeni ya da ~/.config/wojak/secrets.env)")
    return tok, chat


def _cagir(yontem: str, veri: dict, dosya: Path | None = None, alan: str = "document", deneme: int = 4) -> dict:
    import requests
    tok, _ = _kimlik()
    url = API.format(tok=tok, yontem=yontem)
    bekle = 3.0
    son = ""
    for i in range(deneme):
        try:
            if dosya:
                with open(dosya, "rb") as f:
                    r = requests.post(url, data=veri, files={alan: (dosya.name, f)}, timeout=600,
                                      headers={"User-Agent": UA})
            else:
                r = requests.post(url, data=veri, timeout=60, headers={"User-Agent": UA})
            d = r.json()
            if d.get("ok"):
                return d
            son = f"{r.status_code} {d.get('description', '')}"
            ra = (d.get("parameters") or {}).get("retry_after")
            if ra:
                bekle = max(bekle, float(ra) + 1)
            elif r.status_code < 500 and r.status_code != 429:
                break
        except Exception as e:  # ağ hatası
            son = type(e).__name__
        if i < deneme - 1:
            time.sleep(bekle)
            bekle = min(bekle * 2, 60)
    sys.exit(f"Telegram {yontem} başarısız: {son.replace(tok, '***')}")


def mesaj(metin: str) -> None:
    _, chat = _kimlik()
    for i in range(0, len(metin), 4000):  # mesaj sınırı 4096
        _cagir("sendMessage", {"chat_id": chat, "text": metin[i:i + 4000]})


def _parcala(p: Path, hedef: Path) -> list[Path]:
    import multivolumefile
    import py7zr
    taban = hedef / f"{p.name}.7z"
    with multivolumefile.open(taban, mode="wb", volume=PARCA) as mv:
        with py7zr.SevenZipFile(mv, "w", filters=[{"id": py7zr.FILTER_COPY}]) as z:
            z.write(p, arcname=p.name)
    # multivolumefile dört haneli yazar (.0001); 7-Zip/Keka'nın tanıdığı standart üç hane (.001)
    out = []
    for q in sorted(hedef.glob(f"{p.name}.7z.*")):
        yeni = q.with_name(f"{p.name}.7z.{int(q.suffix[1:]):03d}")
        q.rename(yeni)
        out.append(yeni)
    return out


def gonder(p: Path, aciklama: str = "", video: bool = False) -> None:
    _, chat = _kimlik()
    boyut = p.stat().st_size
    if boyut <= SINIR:
        if video and p.suffix.lower() == ".mp4":
            _cagir("sendVideo", {"chat_id": chat, "caption": aciklama[:1000], "supports_streaming": "true"}, p, "video")
        else:
            _cagir("sendDocument", {"chat_id": chat, "caption": aciklama[:1000]}, p)
        print(f"gönderildi: {p.name} ({boyut / 1e6:.1f} MB)")
        return
    with tempfile.TemporaryDirectory() as td:
        parcalar = _parcala(p, Path(td))
        n = len(parcalar)
        mesaj(f"{p.name} ({boyut / 1e6:.0f} MB) kalite kaybı olmadan {n} parça halinde geliyor. Hepsini aynı klasöre "
              f"indir, {parcalar[0].name} dosyasını aç: tek dosya çıkar (Windows: 7-Zip, Mac: Keka ya da The "
              "Unarchiver, Android: ZArchiver)." + (f"\n\n{aciklama}" if aciklama else ""))
        for i, q in enumerate(parcalar, 1):
            _cagir("sendDocument", {"chat_id": chat, "caption": f"{p.name}: parça {i}/{n}"}, q)
            print(f"gönderildi: {q.name} ({q.stat().st_size / 1e6:.1f} MB) [{i}/{n}]")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dosyalar", nargs="*", type=Path)
    ap.add_argument("--mesaj", help="önce gönderilecek metin")
    ap.add_argument("--aciklama", default="", help="dosya açıklaması (ilk dosyaya)")
    ap.add_argument("--video", action="store_true", help="50 MB altı mp4'ü oynatılabilir video olarak gönder")
    a = ap.parse_args()
    if a.mesaj:
        mesaj(a.mesaj)
    for i, p in enumerate(a.dosyalar):
        if not p.exists():
            sys.exit(f"yok: {p}")
        gonder(p, a.aciklama if i == 0 else "", a.video)
    if not a.mesaj and not a.dosyalar:
        ap.print_help()


if __name__ == "__main__":
    main()
