"""Sabitler: tuval ölçüleri, fontlar, renkler.

Ölçüler hesabın 2023-12 / 2024-03 "olay" dönemindeki videolardan ölçüldü:
1080x1920 siyah tuval, ortada 1080x1080 kare görsel alanı (y=420..1500).
"""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
FONTS = ASSETS / "fonts"
CHARACTERS = ASSETS / "characters"
SFX = ASSETS / "sfx"
MUSIC = ASSETS / "music"
OUT = ROOT / "out"

CANVAS_W = 1080
CANVAS_H = 1920
BOX = 1080                      # kare görsel alanı kenarı
BOX_Y = (CANVAS_H - BOX) // 2   # 420
FPS = 30

# Orijinal videolardaki yazı tipi Poppins Bold Italic ile birebir eşleşiyor.
FONT_DIALOG = FONTS / "Poppins-BoldItalic.ttf"
FONT_BOLD = FONTS / "Poppins-Bold.ttf"
FONT_CARD = FONTS / "Anton-Regular.ttf"

WATERMARK = "tarihselwojak"

WHITE = (255, 255, 255, 255)
BLACK = (0, 0, 0, 255)


# Gizli bilgiler repoya yazılmaz. Önce ortam değişkenleri (cloud environment ayarları), yoksa repo
# DIŞINDAKİ bu dosya okunur (satır başına AD=değer; chmod 600). Yol WOJAK_SECRETS ile değiştirilebilir.
SECRETS_FILE = Path(os.environ.get("WOJAK_SECRETS", Path.home() / ".config" / "wojak" / "secrets.env"))


def load_secrets() -> None:
    """SECRETS_FILE'daki değerleri, ortamda tanımlı değilse os.environ'a ekler."""
    try:
        lines = SECRETS_FILE.read_text(encoding="utf-8").splitlines()
    except OSError:
        return
    for line in lines:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
