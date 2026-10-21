#!/usr/bin/env python3
"""Repoya girmeyen özel dosyaları (lisanslı kanal fontu, ölçülen orijinal reel'ler) Telegram botundan indirip yerine koyar.

Yeni bir bulut oturumu repoyu temiz klonlar: `assets/fonts/ozel/` ve `referans/` boş gelir (herkese açık repoya
konamazlar). Bu dosyalar hesap sahibinin Telegram sohbetinde bot mesajı olarak durur; dosya kimlikleri (file_id) repoya
yazılmaz, hesap sahibinin yeni sohbete verdiği istemde gelir. İndirme için TELEGRAM_BOT_TOKEN gerekir (ortam
değişkeni ya da ~/.config/wojak/secrets.env; hiçbir yere yazılmaz). Bot API dosya başına en çok 20 MB indirir, bu
yüzden reel'ler 19 MB'lık 7-Zip parçalarıdır.

    python tools/ozel_indir.py '{"AvenirLTStd-BoldItalic-TR.otf": "<file_id>", "referans.7z.001": "<file_id>", ...}'
    python tools/ozel_indir.py --dosya kimlikler.json

Yerleşim: *.otf / *.ttf -> assets/fonts/ozel/, referans.7z.* -> açılıp referans/ altına, *.m4a / *.mp3 -> assets/music/ozel/.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from wojak import config  # noqa: E402

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"


def indir(tok: str, file_id: str, hedef: Path) -> None:
    import requests
    g = requests.get(f"https://api.telegram.org/bot{tok}/getFile", params={"file_id": file_id},
                     headers={"User-Agent": UA}, timeout=60).json()
    if not g.get("ok"):
        sys.exit(f"getFile başarısız ({hedef.name}): {g.get('description', '')}")
    yol = g["result"]["file_path"]
    r = requests.get(f"https://api.telegram.org/file/bot{tok}/{yol}", headers={"User-Agent": UA}, timeout=600)
    r.raise_for_status()
    hedef.parent.mkdir(parents=True, exist_ok=True)
    hedef.write_bytes(r.content)
    ad = hedef.relative_to(ROOT) if hedef.is_relative_to(ROOT) else hedef.name
    print(f"indirildi: {ad} ({len(r.content) / 1e6:.1f} MB)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("kimlikler", nargs="?", help="dosya adı -> file_id JSON metni")
    ap.add_argument("--dosya", type=Path, help="aynı JSON bir dosyada")
    a = ap.parse_args()
    veri = json.loads(a.dosya.read_text() if a.dosya else (a.kimlikler or "{}"))
    if not veri:
        ap.print_help()
        return
    config.load_secrets()
    tok = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not tok:
        sys.exit("TELEGRAM_BOT_TOKEN yok (ortam değişkeni ya da ~/.config/wojak/secrets.env)")
    with tempfile.TemporaryDirectory() as td:
        parcalar = []
        for ad, fid in veri.items():
            if ad.lower().endswith((".otf", ".ttf")):
                indir(tok, fid, ROOT / "assets" / "fonts" / "ozel" / ad)
            elif ad.lower().endswith((".m4a", ".mp3", ".wav")):
                indir(tok, fid, ROOT / "assets" / "music" / "ozel" / ad)
            elif ".7z." in ad:
                p = Path(td) / ad
                indir(tok, fid, p)
                parcalar.append(p)
            else:
                print(f"atlandı (bilinmeyen tür): {ad}")
        if parcalar:
            import multivolumefile
            import py7zr
            taban = sorted(parcalar)[0].with_suffix("")
            with multivolumefile.open(taban, mode="rb") as mv, py7zr.SevenZipFile(mv, "r") as z:
                z.extractall(ROOT)
            n = len(list((ROOT / "referans").glob("*.mp4")))
            print(f"açıldı: referans/ ({n} mp4)")


if __name__ == "__main__":
    main()
