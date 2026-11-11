"""eskisehir-cinli-hamam: iki hazır karakter ve ters köşe yüz varyantı.

    python episodes/eskisehir-cinli-hamam/chars/uret.py

Kaynaklar (kaynak/ altında):
  adam_cok_terli.png, adam_terli.png  assets/kit/klasik (klasik "feels guy", çıplak gövde; ıslak/terli): A (sol),
                                      hamamdan kaçan adsız adam. Dosya sağa bakar.
  polis_ny.png                        wojakland "New York Cop Wojak" (new_york_cop_wojak.png,
                                      https://wojakland.com/gmedia/new_york_cop_wojak-png/), 843x831 kesilmiş;
                                      lacivert kasket ve üniforma. B (sağ), adsız polis memuru. Dosya sağa bakar.
Yapılanlar:
  - Polis PNG'leri göğüsten kesildi (y 745; uzun kasket, yüz büyüsün).
  - polis_sakin: kasket rozetindeki "000 777" numarası silindi (rozet altın rengine boyandı); başka değişiklik yok.
  - polis_sok: aynı kutu; alındaki kırışıklar ve kaşlar yerine iç uçları kalkık kalın kaşlar ve 4 düzensiz mavi
    soğuk ter çizgisi, iri yuvarlak gözler ve küçük göz bebekleri, "O" ağız, başın önünde (sağ) kontur dışında 3 damla.
  Tarif ve çizim yardımcıları yeralti-camii-karakoy/chars/uret.py'den.
Bakış yönü dosyanın kendisine göre kaydedilir (python -m wojak yon ...); episode.yaml'da faces: yok.
"""
from __future__ import annotations

import importlib.util
import shutil
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

ALTIN = (191, 138, 43)


def rozet_temizle(im):
    a = np.array(im).astype(np.int32)
    y0, y1, x0, x1 = 156, 179, 449, 539
    s = a[y0:y1, x0:x1]
    m = s[..., 3] > 0
    s[m, :3] = ALTIN
    a[y0:y1, x0:x1] = s
    return Image.fromarray(a.astype(np.uint8))


def gri_sil(im, pts):
    a = np.array(im).astype(np.int32)
    rgb = a[..., :3]
    m = yc.poly_mask(im.size, pts) & (rgb.min(-1) < 242) & ((rgb.max(-1) - rgb.min(-1)) < 30) & (a[..., 3] > 0)
    a[m, :3] = 255
    a[m, 3] = 255
    return Image.fromarray(a.astype(np.uint8))


def polis_sok(im):
    """polis_ny 843x831. Ölçülen hatlar (gerçek px): kasket alt kenarı y ~348-352; alın çizgileri (350-370 x 352-364),
    (450-462 x 368-388), (530-600 x 350-368), (535-539 x 375-400); sol göz 362-452 x 398-440; sağ göz 540-608 x
    404-452; ağız 425-556 x 592-620; yüz konturu sağda x ~645 (y 430), ~625 (y 545)."""
    # yalnız gri tonlu koyu çizgiler silinir (lacivert kasket kumaşı korunur); sağda kasket siperliği aşağı indiği
    # için çokgen x 540'tan sonra y 372'den başlar
    im = gri_sil(im, [(340, 357), (540, 357), (540, 372), (620, 372), (620, 402), (340, 402)])
    im = yc.sil_koyu(im, [(445, 365), (470, 365), (470, 392), (445, 392)])
    im = yc.sil(im, yc.kutu(356, 394, 458, 446), tol=-1)
    im = yc.sil(im, yc.kutu(534, 400, 614, 458), tol=-1)
    im = yc.sil(im, yc.kutu(420, 586, 562, 626), tol=-1)
    c = yc.Cizim(im, seed=7)
    W = yc.WHITE
    B = yc.BLACK
    # iri yuvarlak gözler, küçük göz bebekleri (sağa, dosyanın baktığı yöne)
    c.elips(406, 424, 33, 28, dolgu=W, w=5.0)
    c.elips(574, 432, 29, 26, dolgu=W, w=5.0)
    c.elips(418, 426, 6.5, 6.5, dolgu=B)
    c.elips(585, 434, 6.0, 6.0, dolgu=B)
    # iç uçları kalkık kalın kaşlar
    c.cizgi([(360, 388), (405, 380), (452, 362)], 6.0)
    c.cizgi([(536, 362), (578, 376), (614, 390)], 6.0)
    # "O" ağız
    c.elips(490, 606, 15, 20, dolgu=(60, 20, 20, 255), w=5.0)
    # alında 4 düzensiz mavi soğuk ter çizgisi (kaşların iç uçları arasında)
    MAVI = (70, 130, 230, 255)
    for x, y0, L, s in [(470, 360, 28, 1), (488, 357, 32, -1), (506, 357, 32, 1), (524, 360, 28, -1)]:
        c.cizgi([(x, y0), (x + 3 * s, y0 + L * 0.35), (x - 2 * s, y0 + L * 0.7), (x + 1.5 * s, y0 + L)], 4.2,
                renk=MAVI, titrek=0.6)
    # başın önünde (sağ), kontur dışında ~20 px uzakta 3 damla
    return yc.ter(c.im, [(674, 420, 13), (680, 480, 11), (664, 540, 10)])


if __name__ == "__main__":
    shutil.copy(KAYNAK / "adam_cok_terli.png", HERE / "adam_cok_terli.png")
    shutil.copy(KAYNAK / "adam_terli.png", HERE / "adam_terli.png")
    p = rozet_temizle(yc.kontur_sabitle(Image.open(KAYNAK / "polis_ny.png").convert("RGBA")))
    # uzun kasket: PNG göğüsten kesilir (y 745), yüz büyür; çene (y ~690) kadrajda kalır
    yc.kaydet(p.crop((0, 0, p.width, 745)), "polis_sakin")
    yc.kaydet(polis_sok(p.copy()).crop((0, 0, p.width, 745)), "polis_sok")
