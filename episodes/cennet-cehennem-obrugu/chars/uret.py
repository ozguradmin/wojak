"""cennet-cehennem-obrugu: iki hazır kıyafetli karakter ve ters köşe yüz varyantı.

    python episodes/cennet-cehennem-obrugu/chars/uret.py

Kaynaklar (kaynak/ altında, python tools/wojak_site.py get ile):
  hasirsapkali.png  wojakland "Farmer Wojak" (farmer_wojak.png, https://wojakland.com/gmedia/farmer_wojak-png/),
                    857x918; geniş kenarlı şapka, mavi gömlek, kirli sakal. A (sol), adsız köylü. Dosya sağa bakar.
  dede.png          wojakland "Grandpa Wojak" (grandpa_wojak.png), 996x947; gri saç, gözlük, bıyık, süveter yelek.
                    B (sağ), adsız yaşlı köylü. Dosya sağa bakar.
Kıyafete dokunulmaz. Yapılanlar:
  - koylu_sakin = hasirsapkali (kontur opak).
  - dede_sakin = dede (kontur opak).
  - dede_sok: aynı kutu; alın kırışıkları yerine 5 düzensiz mavi soğuk ter çizgisi, iç uçları kalkık kalın kaşlar,
    gözlük camlarının içinde iri yuvarlak gözler ve küçük göz bebekleri, bıyığın altında "O" ağız, başın önünde (sağ)
    kontur dışında 3 damla.
Çizim yardımcıları yeralti-camii-karakoy/chars/uret.py'den (Cizim, sil, sil_koyu, ter).
Bakış yönü dosyanın kendisine göre kaydedilir (python -m wojak yon ...); episode.yaml'da faces: yok.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
KAYNAK = HERE / "kaynak"

_spec = importlib.util.spec_from_file_location("yc", ROOT / "episodes/yeralti-camii-karakoy/chars/uret.py")
yc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(yc)
yc.HERE = HERE  # ter() geçici dosyasını bu klasöre yazsın

CAM = (241, 241, 241)


def cam_temizle(im, pts, esik=600):
    """Gözlük camının içindeki koyu çizgileri (göz, göz altı) cam rengine boyar; camın gri çerçevesine değmez."""
    a = np.array(im).astype(np.int32)
    m = yc.poly_mask(im.size, pts) & (a[..., :3].sum(-1) < esik) & (a[..., 3] > 0)
    a[m, :3] = CAM
    a[m, 3] = 255
    return Image.fromarray(a.astype(np.uint8))


def dede_sok(im):
    """Grandpa Wojak 996x947. Ölçülen hatlar (gerçek px): alın kırışıkları 455-745 x 160-255; sol cam iç kenarı
    ~478-622 x 290-408, sol göz 505-600 x 297-340, göz altı 528-600 x 352-360; sağ cam iç kenarı ~690-812 x 295-415,
    sağ göz 705-780 x 315-362, göz altı 705-770 x 358-378; bıyık 548-745 x 488-560; ağız (bıyık altı) 618-675 x
    570-588; yüz konturu sağda x ~826 (y 300-450)."""
    im = yc.sil_koyu(im, [(450, 150), (760, 150), (760, 258), (450, 258)])
    im = cam_temizle(im, [(484, 296), (600, 291), (620, 312), (616, 352), (588, 396), (530, 406), (492, 394),
                          (480, 350)])
    im = cam_temizle(im, [(694, 302), (798, 297), (808, 332), (800, 386), (768, 410), (722, 404), (698, 372),
                          (690, 332)])
    im = yc.sil(im, yc.kutu(612, 566, 682, 596), tol=-1)
    c = yc.Cizim(im, seed=5)
    W, B = yc.WHITE, yc.BLACK
    # camların içinde iri yuvarlak gözler, küçük göz bebekleri (sağa, dosyanın baktığı yöne)
    c.elips(548, 344, 36, 31, dolgu=W, w=5.0)
    c.elips(750, 348, 31, 29, dolgu=W, w=5.0)
    c.elips(557, 346, 6.5, 6.5, dolgu=B)
    c.elips(759, 350, 6.0, 6.0, dolgu=B)
    # iç uçları kalkık kalın kaşlar (camların üstünde)
    c.cizgi([(486, 258), (540, 248), (606, 222)], 7.0)
    c.cizgi([(694, 226), (742, 244), (792, 260)], 7.0)
    # "O" ağız, bıyığın altında
    c.elips(648, 588, 15, 16, dolgu=(60, 20, 20, 255), w=5.0)
    # alında 5 düzensiz mavi soğuk ter çizgisi
    MAVI = (70, 130, 230, 255)
    for x, y0, L, s in [(560, 168, 34, 1), (592, 162, 40, -1), (624, 160, 42, 1), (656, 162, 38, -1),
                        (688, 168, 30, 1)]:
        c.cizgi([(x, y0), (x + 3 * s, y0 + L * 0.35), (x - 2 * s, y0 + L * 0.7), (x + 1.5 * s, y0 + L)], 4.4,
                renk=MAVI, titrek=0.6)
    # başın önünde (sağ), kontur dışında ~25 px uzakta 3 damla
    return yc.ter(c.im, [(866, 300, 13), (874, 362, 11), (866, 424, 10)])


if __name__ == "__main__":
    yc.kaydet(yc.kontur_sabitle(Image.open(KAYNAK / "hasirsapkali.png").convert("RGBA")), "koylu_sakin")
    d = yc.kontur_sabitle(Image.open(KAYNAK / "dede.png").convert("RGBA"))
    yc.kaydet(d, "dede_sakin")
    yc.kaydet(dede_sok(d.copy()), "dede_sok")
