#!/usr/bin/env python3
"""Hesap sahibinin metin+görsel ağ geçidine (OpenAI uyumlu, SOL_API_KEY) soru sorar; dosya eklenebilir.

Anahtar: SOL_API_KEY ortam değişkeni ya da repo DIŞINDAKİ ~/.config/wojak/secrets.env (wojak/config.py).
Uç nokta: SOL_BASE_URL (varsayılan https://sol.ozgurguler.tech/v1), model: SOL_MODEL.

Örnekler:
    python tools/sol_sor.py "Sadece OK yaz."                       # bağlantı testi
    python tools/sol_sor.py "Bu wojak çizimi MS Paint tarzında mı? Yüzde metin var mı?" karakter.png
    python tools/sol_sor.py "Bu sesi kelimesi kelimesine yaz" ses.mp3
    python tools/sol_sor.py --durum                                  # ağ geçidi sağlık durumu

Sınırlar (ağ geçidi rehberi): istek başına 12 dosya, dosya başına 48 MB, toplam 70 MB; uzak URL kabul
edilmez. Videonun içindeki ses yazıya dökülmez: önce ffmpeg ile sesi ayır
(ffmpeg -i v.mp4 -vn -ac 1 -ar 16000 -b:a 64k ses.mp3) ve sesi gönder.
"""

from __future__ import annotations

import argparse
import base64
import mimetypes
import os
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from wojak import config  # noqa: E402

config.load_secrets()
BASE = os.environ.get("SOL_BASE_URL", "https://sol.ozgurguler.tech/v1").rstrip("/")
MODEL = os.environ.get("SOL_MODEL", "gpt-5.6-sol-web")


def ask(prompt: str, files: list[Path] | None = None, timeout: int = 400) -> str:
    key = os.environ.get("SOL_API_KEY")
    if not key:
        raise SystemExit("SOL_API_KEY yok (ortam değişkeni ya da ~/.config/wojak/secrets.env)")
    body: dict = {"model": MODEL, "messages": [{"role": "user", "content": prompt}]}
    if files:
        body["files"] = [{"filename": f.name, "mime_type": mimetypes.guess_type(f.name)[0] or "application/octet-stream",
                          "data_base64": base64.b64encode(f.read_bytes()).decode()} for f in files]
    r = requests.post(f"{BASE}/chat/completions", headers={"Authorization": f"Bearer {key}"},
                      json=body, timeout=timeout)
    if r.status_code != 200:
        raise SystemExit(f"Hata {r.status_code}: {r.text[:300]}")
    return r.json()["choices"][0]["message"]["content"]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("soru", nargs="?")
    ap.add_argument("dosyalar", nargs="*", type=Path)
    ap.add_argument("--durum", action="store_true", help="ağ geçidinin /health çıktısı")
    a = ap.parse_args()
    if a.durum:
        print(requests.get(BASE.rsplit("/v1", 1)[0] + "/health", timeout=30).text)
        return
    if not a.soru:
        ap.error("soru gerekli")
    for f in a.dosyalar:
        if not f.is_file():
            raise SystemExit(f"Dosya yok: {f}")
    print(ask(a.soru, a.dosyalar))


if __name__ == "__main__":
    main()
