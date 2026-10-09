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

# Orijinal videolardaki yazı: DÜZ Poppins Bold, telefon editörü gibi ~7° eğdirilmiş (iki katlı "a";
# Poppins Bold Italic'te "a" tek katlı ve eğim 10°). Ölçüm: 223 altın dönem kapağı + 30 Instagram reel'i
# (docs/STIL.md). Boyut ~54 px, satır aralığı 1.1x, kontur ~%9.5, gölge yok, en fazla 2 satır.
# Kanalın gerçek fontu (hesap sahibi verdi): Avenir LT Std Bold Italic TR. Lisanslı olduğu için repoya
# KONMAZ (repo herkese açık): assets/fonts/ozel/ altında yerel durur (.gitignore). Yoksa en yakın eşdeğer
# kullanılır: düz Poppins Bold + 7° yapay eğim.
FONT_AVENIR = FONTS / "ozel" / "AvenirLTStd-BoldItalic-TR.otf"
HAS_AVENIR = FONT_AVENIR.exists()
FONT_DIALOG = FONT_AVENIR if HAS_AVENIR else FONTS / "Poppins-Bold.ttf"
FONT_BOLD = FONTS / "Poppins-Bold.ttf"
FONT_CARD = FONTS / "Anton-Regular.ttf"
DIALOG_SHEAR = 0.0 if HAS_AVENIR else 7.0   # derece (Avenir zaten italik)
DIALOG_SIZE = 55 if HAS_AVENIR else 52   # x-yüksekliği ~27 px (30 reel medyanı)
DIALOG_MIN_SIZE = 50
DIALOG_PITCH = 1.07         # satır aralığı / punto (59 px)
DIALOG_STROKE = 0.08        # kontur / punto (~4,4 px) + dış kenarda yumuşak geçiş
DIALOG_STROKE_SOFT = 1.5    # kontur dış kenarına Gauss (px), ofsetsiz
DIALOG_MAX_W = 860
DIALOG_MAX_LINES = 2
TEXT_HEAD_GAP = 55          # yazı bloğunun altı ile konuşanın başı arası (px, kare ölçeğinde)
TEXT_CENTER_RANGE = (0.32, 0.50)  # blok merkezinin kare içindeki izinli aralığı

# Ses: 27/30 reel'de AYNI parça (kanalın imza "orijinal ses"i, Do minör vals, 13,75 sn), efekt YOK,
# entegre -29,5 LUFS, gerçek tepe -17 dBTP, döngü yok. Parça hesabın kendi reel'lerinden çıkarılır
# (assets/music/ozel/, repoya girmez); yoksa sentez imza müziği kullanılır.
MUSIC_CHANNEL = MUSIC / "ozel" / "kanal_orijinal_ses.m4a"
MUSIC_FALLBACK = MUSIC / "imza_gece_vals.mp3"
LOUDNESS_LUFS = -29.5
LOUDNESS_TP = -17.0
MAX_DURATION = 14.0

WATERMARK = "tarihselwojak"
# Sahne etiketleri ("Gerçek fotoğraf · ...", "İddia · 1965") videoda gösterilmez: hesap sahibi istemiyor
# (2026-10-09) ve altın dönem videolarında yoktu. Atıf açıklamada (credits).
SHOW_LABELS = False
CHAR_HEIGHT = 0.48          # görünen yükseklik / kare (30 reel medyanı; izinli 0.42-0.55)
BG_BLUR = 2.5               # arka plan yumuşatma (px): kenar Laplace varyansı orijinallerle eşleşsin

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
