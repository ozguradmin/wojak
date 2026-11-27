from __future__ import annotations
"""en-project-a119 gorselleri:  python episodes/en-project-a119/gorsel.py

Kaynaklar:
  arka.jpg  <- img/kaynak/ay_gunduz_londra.jpg (Commons "Daytime moon over London, England.jpg", Acabashi, CC BY-SA 4.0; 1920 px):
               ay diskini kapsayan 1100x1100 kirpim (450,440) 1080'e kucultulur, renk 0,35 / parlaklik 0,92 (doygunluk ~0,26, parlaklik ~120).
  ev_1.jpg  <- "A Study of Lunar Research Flights" Vol I kapagi (rapor PDF sayfa 3, 300 dpi tarama; Commons PDF, {{PD-USGov-Military-Air Force}};
               DTIC AD0425380; NSA EBB 479): baslik + armali kalkan + damga; her kenarda bosluk; kagit tonu (saf beyaz yok).
  ev_2.jpg  <- ayni raporun kunye sayfasi (PDF sayfa 5): "With contributions by" listesi (C. E. Sagan dahil); kagit tonu.
PDF yolu: /tmp/rapor.pdf (kamu mali; depoya konmaz; Commons: File:A_Study_of_Lunar_Research_Flights.pdf).
"""
import subprocess
from pathlib import Path
from PIL import Image, ImageEnhance

HERE = Path(__file__).resolve().parent
IMG = HERE / "img"
PDF = "/tmp/rapor.pdf"
KAGIT = (238, 233, 220)   # kagit tonu (tarama saf beyazdi)


def sayfa(n: int) -> Image.Image:
    out = f"/tmp/a119_p{n}"
    subprocess.run(["pdftoppm", "-r", "300", "-f", str(n), "-l", str(n), "-gray", "-png", PDF, out], check=True)
    f = sorted(Path("/tmp").glob(f"a119_p{n}*.png"))[0]
    return Image.open(f).convert("L")


def kagitla(g: Image.Image, kutu, pay: int, pay_y: int | None = None, genislik=1080) -> Image.Image:
    """Kirpar, her kenara `pay` px bosluk ekler (kagit tonunda), 1080 genislige olcekler, beyazi kagit tonuna cevirir."""
    k = g.crop(kutu)
    py = pay if pay_y is None else pay_y
    c = Image.new("L", (k.width + 2 * pay, k.height + 2 * py), 255)
    c.paste(k, (pay, py))
    c = c.resize((genislik, round(genislik * c.height / c.width)), Image.LANCZOS)
    rgb = Image.merge("RGB", [c.point(lambda v, t=t: round(v * t / 255)) for t in KAGIT])
    return rgb


ay = Image.open(IMG / "kaynak/ay_gunduz_londra.jpg").convert("RGB").crop((450, 440, 1550, 1540)).resize((1080, 1080), Image.LANCZOS)
ay = ImageEnhance.Brightness(ImageEnhance.Color(ay).enhance(0.35)).enhance(0.92)
ay.save(IMG / "arka.jpg", quality=93)

# kapak: siyah cilt cubugunun sagindan (x>=412) damganin alt ucuna (y 2060) kadar; ust 455
kagitla(sayfa(3), (412, 455, 2480, 2060), 120, 40).save(IMG / "ev_1.jpg", quality=95)
# kunye: "With contributions by" -> "19 June 1959" (L. Reiffel satiri disarida)
kagitla(sayfa(5), (900, 812, 1840, 1335), 50).save(IMG / "ev_2.jpg", quality=95)
