"""Diyalog arka planı (final tur 3): Kız Kulesi'nin kendisi, denizin ortasında (STIL §6: olayın gerçek yeri,
C2VH/C3dO gibi; Türk izleyici 1. saniyede tanısın, "denizin ortasına yılan gelemez" görsel olarak desteklensin).

    python episodes/kiz-kulesi-efsanesi/arkaplan.py

Kaynak: img/kiz_kulesi_sonse_kaynak.jpg = "Kız Kulesi, Maiden's Tower (52396926549).jpg", Sonse, 3 Ekim 2021,
CC BY 2.0 (Flickr 2048 px sürümü, değiştirilmemiş).
1. Kare kırpım: kenar = görsel yüksekliğinin %88'i, üstten; kule ekseni (kaynak x %34) karede x %43'te: sol karakterin
   başı (%13-35) ile sağ karakterin saçı (%50+) arasında kalır, iki tarafta da kule görünür. Bayrak yazının üstünde,
   külah yazının hemen altında, adacık ve deniz şeridi altta.
2. Ton: kanal diyalog karelerinin ölçüsüne (STIL §6: parlaklık medyanı 121, doygunluk 0,2) gama ile hafif
   karartma + hafif doygunluk azaltma. Karartma/gri ton yok; gün ışığı renkleri korunur.
Çıktı: img/arka_kiz_kulesi_sonse.jpg (renderer kendi 2,5 px yumuşatmasını uygular).
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance

EP = Path(__file__).resolve().parent
SRC = EP / "img" / "kiz_kulesi_sonse_kaynak.jpg"
OUT = EP / "img" / "arka_kiz_kulesi_sonse.jpg"
KENAR = 0.88        # kare kenarı / görsel yüksekliği
KULE_X = 0.340      # kule ekseni, kaynak genişliğine oranla
KULE_KARE_X = 0.43  # kule ekseninin karedeki yeri
GAMA = 1.35         # >1 orta tonları koyulaştırır (kaynak 146 -> ~124; kanal medyanı 121)
DOYGUNLUK = 0.88


def main() -> None:
    im = Image.open(SRC).convert("RGB")
    W, H = im.size
    s = round(KENAR * H)
    x0 = round(KULE_X * W - KULE_KARE_X * s)
    x0 = max(0, min(W - s, x0))
    sq = im.crop((x0, 0, x0 + s, s))
    a = np.asarray(sq).astype(np.float64) / 255.0
    a = a ** GAMA
    sq = Image.fromarray(np.clip(a * 255 + 0.5, 0, 255).astype(np.uint8))
    sq = ImageEnhance.Color(sq).enhance(DOYGUNLUK)
    sq.save(OUT, quality=93)
    print("->", OUT.relative_to(EP.parent.parent), sq.size, "kırpım", (x0, 0, x0 + s, s))


if __name__ == "__main__":
    main()
