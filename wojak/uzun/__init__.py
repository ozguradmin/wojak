"""Uzun format (YouTube, 8-10 dk, 1920x1080) video motoru.

Karar belgesi: docs/UZUN_FORMAT.md. Kullanım ve spesifikasyon: docs/UZUN_MOTOR.md.

    python -m wojak uzun kontrol     uzun/<id>   # spesifikasyon + zaman çizelgesi + hareket denetimi
    python -m wojak uzun seslendir   uzun/<id>   # Gemini/Cartesia TTS (önbellekli), --qa ile isim denetimi
    python -m wojak uzun onizle      uzun/<id>   # yarım çözünürlük hızlı ön izleme (--bas/--bit)
    python -m wojak uzun render      uzun/<id>   # 1920x1080 30 fps, -14 LUFS
    python -m wojak uzun kucukresim  uzun/<id>   # 1280x720 küçük resim varyantları
    python -m wojak uzun paket       uzun/<id>   # paylasim.md + .srt
    python -m wojak uzun teslim      uzun/<id>   # teslim/<id>-uzun/

Modüller: spec (YAML), zaman (zaman çizelgesi), tts, sahneler (+cizim, harita), render, ses (+muzik),
altyazi, kucukresim, paket, cli.
"""

W, H = 1920, 1080
FPS = 30
