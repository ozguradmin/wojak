"""Ankara elçi vagonları: arka plan ve kanıt görselleri (kaynaklar img/ ve img/kaynak/ altında, hepsi serbest lisanslı).

arka_angora_1922.jpg : Gadmer, 'Turquie, Angora, Mosquée Hadji Baïram et Ambassade Afghane - A36980' (24.12.1922, CC BY-SA 4.0).
                       Kare kırpım, cam plaka tozları (gökyüzündeki koyu benekler) yerel medyanla temizlendi, renk/parlaklık.
kanit_1_nyt_1926.jpg : The New York Times Magazine, 30.5.1926, s. 23 (ABD'de kamu malı), sol sütundaki paragraf.
kanit_2_ankara_bugun.jpg : Alexkom000, '2025-05-02 A view of Ankara from Anıtkabir 2' (CC BY 4.0).
Çalıştır: python episodes/ankara-elci-vagonlari/gorsel.py
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

D = Path(__file__).parent / "img"


def olc(im):
    a = np.asarray(im.convert("RGB").resize((720, 720))).astype(float) / 255
    mx, mn = a.max(2), a.min(2)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0).mean()
    g = np.asarray(im.convert("L").resize((720, 720))).astype(float)
    lap = (np.roll(g, 1, 0) + np.roll(g, -1, 0) + np.roll(g, 1, 1) + np.roll(g, -1, 1) - 4 * g).var()
    return round(g.mean(), 1), round(float(sat), 3), round(float(lap), 1)


def arka():
    # tur 3: Hacı Bayram sokağı ve Afgan elçiliği (24.12.1922); cam plaka kenarları dışarıda
    im = Image.open(D / "r2_bg_angora_1922_sokak_afgan_elcilik.jpg").convert("RGB").crop((360, 40, 1700, 1380))
    # gökyüzündeki toz/benekleri temizle: yerel medyandan belirgin koyu pikseller medyanla değişir (yalnız üst %40)
    a = np.asarray(im).astype(int)
    med = np.asarray(im.filter(ImageFilter.MedianFilter(25))).astype(int)
    fark = med.mean(2) - a.mean(2)
    yy = np.arange(a.shape[0])[:, None]
    m = (fark > 9) & (yy < int(a.shape[0] * 0.40))
    m = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(7))) > 0
    a[m] = med[m]
    a = np.asarray(ImageOps.autocontrast(Image.fromarray(a.astype(np.uint8)), cutoff=0.5, preserve_tone=True)).astype(float)
    # beyaz dengesi: otokromun mor-mavi gökyüzü (B-R ~56) -> B-R ~18
    gok = a[: int(a.shape[0] * 0.25)].reshape(-1, 3).mean(0)
    hedef = gok.mean()
    k = np.array([hedef / gok[0], hedef / gok[1], (hedef + 4) / gok[2]])
    a = np.clip(a * k, 0, 255)
    im = Image.fromarray(a.astype(np.uint8)).resize((1080, 1080), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(2.9)
    im = ImageEnhance.Brightness(im).enhance(0.76)
    im.save(D / "arka_angora_1922.jpg", quality=93)
    b = np.asarray(im).astype(int)[:270].reshape(-1, 3).mean(0)
    print("arka (parlaklık, doygunluk, laplace):", olc(im), "gökyüzü RGB", b.round(), "B-R", round(b[2] - b[0]))


def kanit1():
    im = Image.open(D / "kaynak" / "nyt_1926-05-30_s23_w4000.jpg").convert("RGB")
    # paragraf + sağda sütun çizgisi ve komşu sütunun ilk harfleri; kâğıt tonu korunur (beyaza çekilmez)
    c = im.crop((300, 1394, 1000, 1744))
    c = c.resize((1080, round(1080 * c.height / c.width)), Image.LANCZOS)
    c.save(D / "kanit_1_nyt_1926.jpg", quality=93)
    print("kanit1", c.size)


def kanit2():
    im = Image.open(D / "r2_kanit_bugun_ankara_anitkabir.jpg").convert("RGB")
    c = im.crop((0, 200, 1920, 1250)).resize((1080, 591), Image.LANCZOS)   # gökyüzü azaltıldı
    c.save(D / "kanit_2_ankara_bugun.jpg", quality=93)
    print("kanit2", c.size)


if __name__ == "__main__":
    arka()
    kanit1()
    kanit2()
