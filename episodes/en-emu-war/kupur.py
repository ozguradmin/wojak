"""en-emu-war: son kare için telifsiz, gerçekçi 1930'lar basılı sayfa kupürü (kendi tasarımımız).

    python episodes/en-emu-war/kupur.py        # -> img/kanit_2_kupur.jpg (1080x800, siyah zemin, kupürün kendisi)

Gobeklitepe kupürünün kâğıt/mürekkep yöntemi (episodes/gobeklitepe-mezar-tasi/kupur.py); üç sütunlu sayfa, siyah zemin.
Metinler gerçek kaynaktan: Parliament of Australia, House of Representatives, Hansard, 9 Kasım 1932 (historichansard.net),
"Destruction of Emus" cevabı (Mr Lyons, for Mr Francis) ve aynı sayfadaki öncesi (emeklilik ve "Air Mail Contracts" maddeleri).
Yalnız bariz OCR yapışıklıkları düzeltildi (settlera -> settlers, wore -> were, existingair -> existing air...).
Son cümle ("The machine guns have since been returned to Perth.") bütün olarak ve büyük puntoyla; cevabın geri kalanı küçük
puntoyla önünde, aynı paragrafın devamı. Yayın logosu/adı/düzeni taklit edilmez; sayfa üstünde "HOUSE OF REPRESENTATIVES" ve
tarih satırı (basılı sayfa başlığı) kaynağı gösterir; kareye ek etiket yok.
Fontlar SIL OFL (karun-hazinesi-bros/fonts): Source Serif 4, Libre Franklin.
"""
from __future__ import annotations
import math
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "episodes" / "gobeklitepe-mezar-tasi"))
import kupur as K  # noqa: E402

K.RNG = np.random.default_rng(1932)
RNG = K.RNG
OUT = HERE / "img" / "kanit_2_kupur.jpg"
SS = 2
PW, PH = 1050, 790
W, H = 1080, 800

SOL = ("unemployed food relief, any amounts received as old-age pension are not taken into account, nor is the pensioner "
       "included in the family for the purpose of arriving at the family income. In all other cases amounts received from all "
       "sources, including invalid pensions, are taken into account when calculating the income of applicants. It is the policy "
       "of the Government that in all cases where pensioners have children who, having due regard to their other "
       "responsibilities, are in a position to maintain their parents and do not do so, they shall make such a contribution to "
       "the revenue as their means will permit, and thus reduce the burden of the pension on the ordinary taxpayer. Recent "
       "amendments to the invalid and old-age pensions law were made to this effect. The Government is not aware that it is the "
       "intention of the New South Wales Government to force pensioners to keep their children.")
AIR_H = "Air Mail Contracts."
AIR = ("Mr Lyons (for Mr Francis). - Yesterday the honorable member for Newcastle (Mr. Watkins) asked to be furnished with the "
       "dates upon which the existing air mail contracts will expire. I am now in a position to inform the honorable member "
       "that the existing air mail contracts will expire on the following dates:")
BASLIK = "Destruction of Emus."
GOVDE = ("I am now in a position to inform the honorable member that a deputation of soldier settlers on the fringe of the wheat "
         "belt in Western Australia waited on the Minister for Defence recently, and pointed out that, owing to the dry spell "
         "inland, thousands of emus were damaging rabbit-proof fences and devastating crops by rolling on them. The settlers "
         "pointed out that ordinary firearms were useless to stop the inroad of the emus, as the birds quickly dispersed when "
         "attacked, and only a few of them were destroyed. They suggested that Lewis guns would be more effective, and the "
         "Minister agreed to several machine guns, with the requisite personnel, being made available, on the understanding "
         "that the cost thereof would be borne by the State and the settlers jointly.")
SATIRLAR = ["The machine guns have", "since been returned", "to Perth."]
BAS_UST = "HOUSE OF REPRESENTATIVES"
BAS_TARIH = "9 NOVEMBER 1932"


def serif(boy, agirlik=420, opsz=12):
    return K.font("SourceSerif4-opsz-wght.ttf", boy, agirlik, opsz)


def satirlara_bol(metin, f, genislik, d):
    kel, satirlar, cur = metin.split(), [], []
    for k in kel:
        deneme = " ".join(cur + [k])
        if d.textlength(deneme, font=f) / SS <= genislik or not cur:
            cur.append(k)
        else:
            satirlar.append(cur)
            cur = [k]
    if cur:
        satirlar.append(cur)
    return satirlar


def yaz_blok(d, metin, f, x, y, genislik, satir_h, son_satir_yok=False, max_h=None):
    """İki yana yaslı küçük punto blok; döndürür: bitiş y."""
    satirlar = satirlara_bol(metin, f, genislik, d)
    for i, kel in enumerate(satirlar):
        if max_h is not None and y - 0 > max_h:
            break
        son = i == len(satirlar) - 1
        toplam = sum(d.textlength(k, font=f) / SS for k in kel)
        bosluk = (genislik - toplam) / max(1, len(kel) - 1) if not son and len(kel) > 1 else d.textlength(" ", font=f) / SS
        bosluk = min(bosluk, 14)
        cx = x
        for k in kel:
            d.text((cx * SS, y * SS), k, font=f, fill=255, anchor="ls")
            cx += d.textlength(k, font=f) / SS + bosluk
        y += satir_h
    return y


def sayfa():
    p = K.kagit(PW, PH)
    pa = np.asarray(p).astype(np.float32) * np.array([0.97, 0.95, 0.88])
    p = Image.fromarray(np.clip(pa, 0, 255).astype(np.uint8))
    m = Image.new("L", (PW * SS, PH * SS), 0)
    d = ImageDraw.Draw(m)
    c1x0, c1x1 = 34, 332
    c2x0, c2x1 = 366, PW - 34
    # sütun çizgisi
    d.rectangle([(c1x1 + 15) * SS, 30 * SS, (c1x1 + 16) * SS + 1, (PH - 14) * SS], fill=255)
    fs = serif(22, 440, 10)
    fb = serif(24, 800, 14)
    # sayfa başlığı (basılı üst satır)
    fh = K.font("SourceSerif4-opsz-wght.ttf", 18, 700, 14)
    d.text((c1x0 * SS, 40 * SS), BAS_UST, font=fh, fill=255, anchor="ls")
    d.text(((PW - 34) * SS, 40 * SS), BAS_TARIH, font=fh, fill=255, anchor="rs")
    d.rectangle([c1x0 * SS, 50 * SS, (PW - 34) * SS, 51 * SS], fill=255)
    # sol sütun: emeklilik metni (gerçek), Air Mail maddesi
    y = yaz_blok(d, SOL, fs, c1x0, 82, c1x1 - c1x0, 27)
    y += 14
    d.text((c1x0 * SS, y * SS), AIR_H, font=fb, fill=255, anchor="ls")
    y += 30
    yaz_blok(d, AIR, fs, c1x0, y, c1x1 - c1x0, 27)
    # sağ geniş alan: başlık, küçük punto cevap, büyük son cümle
    bas = K.font("SourceSerif4-opsz-wght.ttf", 70, 900, 60)
    d.text((c2x0 * SS, 132 * SS), BASLIK, font=bas, fill=255, anchor="ls")
    d.rectangle([c2x0 * SS, 148 * SS, c2x1 * SS, 151 * SS], fill=255)
    d.rectangle([c2x0 * SS, 156 * SS, c2x1 * SS, 157 * SS], fill=255)
    y2 = yaz_blok(d, GOVDE, fs, c2x0, 188, c2x1 - c2x0, 27)
    gov = K.font("SourceSerif4-opsz-wght.ttf", 56, 640, 40)
    y2 += 30
    for i, s in enumerate(SATIRLAR):
        d.text((c2x0 * SS, (y2 + i * 68) * SS), s, font=gov, fill=255, anchor="ls")
    m = m.resize((PW, PH), Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.55))   # mürekkep yayılması
    ink = K.murekkep(m)
    lay = Image.new("RGB", (PW, PH), (32, 31, 29))
    return Image.composite(lay, p, ink)


def main():
    p = sayfa()
    alfa = K.kenar_alfa(PW, PH)
    # dört kenar da düzensiz: sağ/sol kenarı da aşındır
    yy, xx = np.mgrid[0:PH, 0:PW].astype(np.float32)
    kivrim = 1.05 - 0.05 * (xx / PW) - 0.07 * (yy / PH) - 0.05 * np.clip((PW * 0.1 - xx) / (PW * 0.1), 0, 1) ** 2
    pa = np.asarray(p).astype(np.float32) * kivrim[..., None]
    # tarama gürültüsü + hafif kontrast
    pa += RNG.normal(0, 3.0, pa.shape[:2])[..., None]
    pa = (pa - 128) * 1.08 + 128
    p = Image.fromarray(np.clip(pa, 0, 255).astype(np.uint8))
    rgba = p.convert("RGBA")
    rgba.putalpha(alfa)
    rgba = rgba.rotate(-0.8, resample=Image.BICUBIC, expand=True)
    z = Image.new("RGB", (W, H), (0, 0, 0))
    ox, oy = (W - rgba.width) // 2, 4
    z.paste(rgba, (ox, oy), rgba)
    z = z.filter(ImageFilter.GaussianBlur(0.45))
    z.save(OUT, quality=92)
    print("->", OUT.relative_to(ROOT), z.size, "kağıt", rgba.size)


if __name__ == "__main__":
    main()
