"""karun-hazinesi-bros: arka plan ve kanıt görselleri (gerçek fotoğraf/belge; yapay zekâ yok).

    python episodes/karun-hazinesi-bros/gorsel.py

Ham dosyalar .cache/karun-hazinesi-bros/ altına iner (git'e girmez; Wikimedia istekleri arasında >= 12 sn).
Çıktılar:
  img/arka_muze.jpg                        diyalog arka planı (CC BY-SA 4.0, Canercangul)
  img/kanit_1_sahte_bros.jpg               kanıt 1: 2012'de Uşak Müzesi vitrinindeki SAHTE broş (CC BY-SA 4.0, Dosseman)
  img/telifli/kanit_2_milliyet_310506.jpg  kanıt 2: Milliyet 31.05.2006 birinci sayfa haberi (TELİFLİ, git'e girmez)
  img/telifli/kanit_yedek_milliyet_200406.jpg  yedek: Milliyet 20.04.2006 manşeti "KARUN HAZİNESİ SOYULDU" (TELİFLİ)
"""
from __future__ import annotations

import hashlib
import time
import urllib.parse
from pathlib import Path

import numpy as np
import requests
from PIL import Image, ImageEnhance

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CACHE = ROOT / ".cache" / "karun-hazinesi-bros"
IMG = HERE / "img"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}


def commons(ad: str) -> str:
    n = ad.replace(" ", "_")
    h = hashlib.md5(n.encode()).hexdigest()
    return f"https://upload.wikimedia.org/wikipedia/commons/{h[0]}/{h[:2]}/{urllib.parse.quote(n)}"


MILLIYET_API = "https://gazetearsivi-api.milliyet.com.tr/api/v1/NewspaperImage/Image/"
HAM = {
    "bursa_arkeoloji_muzesi_2.jpg": commons("Bursa Arkeoloji Müzesi (2).jpg"),
    "usak_sahte_bros_2303.jpg": commons("Uşak Winged Karun Treasure fake seahorse brooch 2303.jpg"),
    # Milliyet Gazete Arşivi (https://gazetearsivi.milliyet.com.tr/Arsiv/2006/05/31 ve /2006/04/20), 1. sayfa
    "milliyet_2006-05-31_s1.jpg": MILLIYET_API + "FqUXnf6KVM0l4SEDcULMJSOssIoBBBO7FvbHfaU_x2F_Yp4dyawZ8pWhrlEB94eND9F6Bt_x2B_CUE_x2B_To6jjZzgaYlXf0w_x3D__x3D_",
    "milliyet_2006-04-20_s1.jpg": MILLIYET_API + "FqUXnf6KVM0l4SEDcULMJf1_x2B_VQNr6uFxe_x2F_KWtQwraWDZ_x2F_0CAFsypGfTKRxdYlyLZUDpdpS5rXrX1Z3MiUj1nbQ_x3D__x3D_",
}


def ham(ad: str) -> Image.Image:
    p = CACHE / ad
    if not p.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        r = requests.get(HAM[ad], headers=UA, timeout=120)
        r.raise_for_status()
        p.write_bytes(r.content)
        time.sleep(12)
    return Image.open(p).convert("RGB")


def olc(im: Image.Image) -> tuple[float, float]:
    a = np.asarray(im.convert("RGB")).astype(float) / 255
    lum = (0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]).mean() * 255
    mx, mn = a.max(-1), a.min(-1)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0).mean()
    return lum, sat


def arka_plan():
    """Bursa Arkeoloji Müzesi salonu (2400x1600): ortada ışıklı cam vitrin, kırmızı ziyaretçi kordonu. 'Aynı türden
    yer' (Uşak Müzesi'nin serbest lisanslı geniş açı fotoğrafı yok). Kare kırpım vitrini ortalar (x 480-2080);
    karakterler iki yandaki heykel kaidelerini ve sol alttaki bankı örter."""
    im = ham("bursa_arkeoloji_muzesi_2.jpg").crop((480, 0, 2080, 1600)).resize((1080, 1080), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(0.45)
    im = ImageEnhance.Brightness(im).enhance(1.20)
    print("arka plan parlaklık/doygunluk:", ["%.2f" % v for v in olc(im)])
    im.save(IMG / "arka_muze.jpg", quality=92)


def kanit_1():
    """Commons 'Uşak Winged Karun Treasure fake seahorse brooch 2303.jpg' (1636x2564, 17.06.2012): yükleyenin
    notuna göre çekildiğinde vitrinde duran SAHTE broş. Broşun tamamı (kanat ucu - püskül uçları) y 195-2045.
    Renderer kanıtı kareye sığdırdığı için (yan siyah bant kalmasın, STIL §8: tam genişlik) broş 1080 yüksekliğe
    ölçeklenir (954 px); iki yandaki ~63 px, aynı fotoğrafın broşsuz sağ kenarındaki kumaş şeritleriyle doldurulur (ek yerinde
    8 px yumuşak geçiş): 1080x1080. Broşun piksellerine dokunulmaz."""
    im = ham("usak_sahte_bros_2303.jpg").crop((0, 195, 1636, 2045))
    im = im.resize((round(im.width * 1080 / im.height), 1080), Image.LANCZOS)
    sol_w = (1080 - im.width) // 2
    sag_w = 1080 - im.width - sol_w

    # dolgu: broşun hiç girmediği sağ kenar kumaşından düz (aynasız) şeritler; ek yerinde 8 px yumuşak geçiş
    def serit(x0, w):
        return im.crop((x0, 0, x0 + w, 1080))

    sol = serit(im.width - sol_w - 8, sol_w + 8)        # x >= ~885: broş ve gölgesi hiç yok
    sag = serit(im.width - sag_w - 8, sag_w + 8)
    out = Image.new("RGB", (1080, 1080))
    out.paste(sol, (0, 0))
    out.paste(sag, (1080 - sag.width, 0))
    m = Image.new("L", (im.width, 1080), 255)
    px = m.load()
    for x in range(8):
        for y in range(1080):
            px[x, y] = px[im.width - 1 - x, y] = int(255 * (x + 1) / 9)
    out.paste(im, (sol_w, 0), m)
    print("kanıt 1:", out.size, im.size, ["%.2f" % v for v in olc(out)])
    out.save(IMG / "kanit_1_sahte_bros.jpg", quality=92)


def kanit_2():
    """Milliyet 31.05.2006, 1. sayfa sol üst haber: üst başlık 'Karun soygunu dış basında', manşet 'DÜNYAYA REZİL
    OLDUK', broş fotoğrafı, spot ve kutu 'Bakan Koç: Hırsız evin içindeymiş'. Sayfa 1913x2743; kare kırpım
    (22, 1085)-(732, 1795): haberin krem kutusu + iki yandaki sayfa beyazı (renderer kanıtı kareye sığdırır; kare
    kırpım tam genişlik verir). 1080x1080. Piksellere başka dokunulmadı."""
    (IMG / "telifli").mkdir(parents=True, exist_ok=True)
    im = ham("milliyet_2006-05-31_s1.jpg").crop((22, 1085, 732, 1795)).resize((1080, 1080), Image.LANCZOS)
    print("kanıt 2:", im.size)
    im.save(IMG / "telifli" / "kanit_2_milliyet_310506.jpg", quality=93)


def yedek():
    """Milliyet 20.04.2006, 1. sayfa manşeti: 'SKANDAL: NE KORUMA VAR NE DE ALARM / KARUN HAZİNESİ SOYULDU' + spot
    ('... Kanatlı Denizatı Broşu'nu çaldılar, yerine sahtesini koydular'). Sayfa 1821x2672; kırpım (390, 697)-(1313,
    1560) -> 1080 genişlik. Videoda yok (hesap sahibi isterse kanıt 1 yerine)."""
    im = ham("milliyet_2006-04-20_s1.jpg").crop((390, 697, 1313, 1560))
    im = im.resize((1080, round(im.height * 1080 / im.width)), Image.LANCZOS)
    im.save(IMG / "telifli" / "kanit_yedek_milliyet_200406.jpg", quality=93)


if __name__ == "__main__":
    IMG.mkdir(exist_ok=True)
    arka_plan()
    kanit_1()
    kanit_2()
    yedek()
