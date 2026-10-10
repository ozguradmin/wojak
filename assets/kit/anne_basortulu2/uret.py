#!/usr/bin/env python3
"""anne_basortulu2 kitini kaynaktan yeniden üretir (kit.json'daki açıklamaya bakın).

    python assets/kit/anne_basortulu2/uret.py

1. Kaynak (anne): wojakland "Blushing Hijab Wojak" (458x538 RGBA, büyütme yok),
   `python tools/wojak_site.py get wl:blushing_hijab_wojak.png --out-dir episodes/van-depremi-azra-bebek/chars
   --name anne_hijab_kaynak` ile indirildi. Kanalın C3De/C2Fr kadınıyla aynı aile: yumuşak gölgeli, dökümlü
   açık başörtüsü, kirpikli anime gözler, görünen saç çizgisi, dişleri görünen aralık ağız.
2. Düzeltmeler: boyun zinciri (choker) ve asma kilitli kolye silinir; yanak allığı %80 azaltılır (gülümseme yok);
   pembe üst -> kahverengi örgü (#6B4A2E, C3De'deki hırka); başörtüsü ve gömlek hafif krem tona çekilir;
   büst kırpımı (göğüs altı kesilir).
   Yön: kaynak zaten 3/4 SAĞA dönük (burun yüz ortasının sağında, sağ göz sağ kontura yakın; kanalın
   C3De/C2Fr kadını da aynı açıda, solda durup içeri bakıyor) -> aynalanmaz, 'right' kaydedilir. Renderer
   sol tarafta aynalamaz; sağ tarafta kullanılırsa kendisi aynalar.
3. Kucaktaki bebek: beyaz kundak + küçük wojak yüzü (wojakland "Baby Face Wojak", emzik silindi), büstün iç
   (sağ) alt kenarında; üç varyantta da aynı yerde (kutu sabit).
4. tek_gozyasi: tools/kit_varyant.py ile (kit.json 'variants'); agliyor: iki gözden yaş + açık, titreyen ağız.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

KIT = Path(__file__).resolve().parent
ROOT = KIT.parent.parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))
import kit_varyant  # noqa: E402
from wojak import facing  # noqa: E402

CHARS = ROOT / "episodes" / "van-depremi-azra-bebek" / "chars"
SRC = CHARS / "anne_hijab_kaynak.png"      # wojakland blushing_hijab_wojak.png
BEBEK_SRC = CHARS / "bebek_yuz_kaynak.png"  # wojakland baby_face_wojak.png
CROP_H = 490                                # büst: bu satırın altı kesilir (alt kenar düz ve opak kalır)
BROWN = np.array((107, 74, 46), np.float32)  # #6B4A2E, C3De'deki kahverengi örgü
WARM = np.array((1.0, 0.975, 0.935), np.float32)  # başörtüsü/gömlek: soğuk gri -> krem (C3De/C2Fr)
DEBLUSH = 0.80
HAIR = np.array((78, 58, 46), np.float32)       # görünen saç (kaynakta düz gri)
SAC_TOHUM = (305, 40)                           # gri alanın içinden bir nokta


def _lum(a: np.ndarray) -> np.ndarray:
    return 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]


def _cene_y(x: int) -> float:
    """Çene çizgisinin beklenen y'si (kaynakta ölçüldü: (188,212) -> (240,262) -> (272,268))."""
    return 212 + (x - 188) * 50 / 52 if x <= 240 else 262 + (x - 240) * 6 / 32


def zincir_sil(a: np.ndarray) -> np.ndarray:
    """Boyundaki zincir: her sütunda çene çizgisinin altı ile boyun alt konturu arasında kalan gri halkalar
    beyaza boyanır (çene çizgisi, ağız, boyun konturu ve sağdaki dikey boyun çizgisi korunur)."""
    lum = _lum(a)
    for x in range(187, 274):
        col = lum[200:330, x]
        runs, y = [], 0
        while y < len(col):
            if col[y] < 80:
                y0 = y
                while y + 1 < len(col) and col[y + 1] < 80:
                    y += 1
                runs.append((y0, y))
            y += 1
        exp = _cene_y(x) - 200
        runs = [r for r in runs if abs(r[0] - exp) <= 9]
        if not runs:
            continue
        j1 = runs[0][1]
        # alttan yukarı: boyun konturu + başörtüsü (lum<240 kesintisiz koşu) başlangıcı
        t = len(col) - 1
        while t > j1 and col[t] < 240:
            t -= 1
        y0, y1 = 200 + j1 + 3, 200 + t - 1
        if y1 > y0:
            seg = a[y0:y1 + 1, x]
            m = _lum(seg) < 253
            seg[m, :3] = 253
    return a


def allik_azalt(a: np.ndarray) -> np.ndarray:
    """Yanak allığını %80 azaltır: yüz kutusunda pembe (R>G, G~B) piksellerin G/B'si R'ye doğru çekilir."""
    sub = a[120:225, 185:355]
    r, g, b = sub[..., 0], sub[..., 1], sub[..., 2]
    m = (r - g > 6) & (np.abs(g - b) < 9) & (sub[..., 3] > 0)
    sub[..., 1] = np.where(m, g + DEBLUSH * (r - g), g)
    sub[..., 2] = np.where(m, b + DEBLUSH * (r - b), b)
    return a


def _knit(h: int, w: int) -> np.ndarray:
    """Örgü dokusu çarpanı: dikey fitiller + her 26 px'de bir saç örgüsü (cable) sütunu, çok hafif."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    rib = 0.055 * np.cos(2 * np.pi * xx / 6.5)
    cx = (xx % 26) - 13
    cable_col = np.clip(1 - np.abs(cx) / 7.0, 0, 1)
    cable = 0.09 * cable_col * np.sin(2 * np.pi * (yy / 11.0) + np.sign(cx) * 1.3)
    return 1 + rib * (1 - cable_col) + cable


def ust_kahve(a: np.ndarray) -> np.ndarray:
    """Pembe üst -> kahverengi örgü; asma kilitli kolye üstle birlikte boyanır."""
    r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    pink = (r - g > 25) & (b - g > 8) & (yy > 400) & (al > 0)
    m = Image.fromarray((pink * 255).astype(np.uint8))
    closed = np.array(m.filter(ImageFilter.MaxFilter(31)).filter(ImageFilter.MinFilter(31))) > 0
    lum = _lum(a)
    sat = a[..., :3].max(-1) - a[..., :3].min(-1)
    kolye = (xx > 195) & (xx < 340) & (yy > 431)        # zincir + asma kilit bölgesi
    chain = closed & ~pink & (sat < 40) & (lum > 95) & kolye
    reg = pink | chain
    # düz dolgu; yalnız üstün sol/sağ siyah kenarındaki yumuşatma koyulaşır (kolye bölgesinde iz kalmaz)
    k = np.where((lum < 150) & ~(kolye & closed), np.clip(lum / 203.0, 0, 1.0), 1.0)
    tex = _knit(*a.shape[:2])
    col = BROWN[None, None, :] * (k * tex)[..., None]
    a[..., :3] = np.where(reg[..., None], np.clip(col, 0, 255), a[..., :3])
    return a


def sicak_ton(a: np.ndarray) -> np.ndarray:
    """Başörtüsü ve gömleğin soğuk grisini kreme çeker; yüzün saf beyazı (lum>=250) ve siyah çizgiler aynı kalır."""
    lum = _lum(a)
    sat = a[..., :3].max(-1) - a[..., :3].min(-1)
    m = (sat < 22) & (a[..., 3] > 0)
    t = (np.clip((lum - 60) / 60.0, 0, 1) * np.clip((250 - lum) / 8.0, 0, 1))[..., None]
    warm = a[..., :3] * (1 + t * (WARM[None, None, :] - 1))
    a[..., :3] = np.where(m[..., None], warm, a[..., :3])
    return a


def sac(a: np.ndarray) -> np.ndarray:
    """Alnın üstünde başörtüsünün altından görünen düz gri alan (saç) koyu kahve yapılır (C3De/C2Fr: koyu saç).
    Kenarda yumuşak geçiş: çekirdek maske hafif bulanıklaştırılıp karıştırılır."""
    lum = _lum(a)
    sat = a[..., :3].max(-1) - a[..., :3].min(-1)
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    grey = (np.abs(lum - 159) < 9) & (sat < 8) & (yy < 90) & (xx > 250) & (xx < 360) & (a[..., 3] > 200)
    m = Image.fromarray((grey * 255).astype(np.uint8)).copy()
    ImageDraw.floodfill(m, SAC_TOHUM, 128)            # yalnız ana gri alan (dış kenardaki gri pikseller değil)
    core = np.array(m) == 128
    soft = np.array(Image.fromarray((core * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8)))
    w = (np.maximum(soft / 255.0, core) * (lum < 236))[..., None]
    a[..., :3] = a[..., :3] * (1 - w) + HAIR[None, None, :] * w
    return a


def anne_taban() -> Image.Image:
    a = np.array(Image.open(SRC).convert("RGBA")).astype(np.float32)
    a = zincir_sil(a)
    a = allik_azalt(a)
    a = ust_kahve(a)
    a = sac(a)
    a = sicak_ton(a)
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return im.crop((0, 0, im.width, CROP_H))


# ---- kucaktaki bebek (kundak) -------------------------------------------------------------------------
BEBEK = {"cx": 352, "top": 362, "w": 96, "egim": 7}      # anne görselinde (kırpım sonrası) kundağın yeri, piksel
SS = 4


def bebek_yuz(w: int) -> Image.Image:
    """Baby Face Wojak: emzik silinir, küçük ağız çizilir, çizgiler küçültmeye göre kalınlaştırılır."""
    im = Image.open(BEBEK_SRC).convert("RGBA")
    d = ImageDraw.Draw(im)
    d.ellipse([132, 252, 222, 306], fill=(255, 255, 255, 255))           # emzik + dudak kenarları
    d.line([(160, 281), (174, 283), (188, 281)], fill=(0, 0, 0, 255), width=6, joint="curve")
    a = np.array(im)
    rgb = Image.fromarray(a[..., :3]).filter(ImageFilter.MinFilter(5))     # siyah çizgiler kalınlaşır
    out = Image.merge("RGBA", (*rgb.split(), im.getchannel("A")))
    h = round(out.height * w / out.width)
    return out.resize((w, h), Image.LANCZOS)


def _kundak_kontur(cx: float, top: float, w: float, bot: float) -> list[tuple[float, float]]:
    """Kundak silueti: üstte yarım elips kapüşon, yanlar aşağı doğru hafifçe genişler (yumuşak eğri)."""
    rx, ry = w / 2, w * 0.52
    cy = top + ry
    pts = [(cx + rx * np.cos(t), cy - ry * np.sin(t)) for t in np.linspace(np.pi, 0, 40)]
    right = [(cx + rx + 5 * (1 - np.cos(np.pi * u / 2)), cy + u * (bot - cy)) for u in np.linspace(0, 1, 12)[1:]]
    left = [(cx - rx - 5 * (1 - np.cos(np.pi * u / 2)), cy + u * (bot - cy)) for u in np.linspace(1, 0, 12)[:-1]]
    return pts + right + left


def bebek_katmani(size: tuple[int, int]) -> Image.Image:
    """Kundak: beyaz battaniye (yumuşak gri gölge, koyu ince kontur, çapraz sarma kıvrımları), kapüşon
    içinde küçük bebek yüzü. Annenin çizimindeki gibi yumuşak gölgeli; kontur kalınlığı yüz çizgileri kadar."""
    cx, top, w = BEBEK["cx"], BEBEK["top"], BEBEK["w"]
    W, H = size
    bot = H + 6
    S = lambda pts: [(x * SS, y * SS) for x, y in pts]  # noqa: E731
    line = (58, 52, 48, 255)
    body = _kundak_kontur(cx, top, w, bot)
    L = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    d.polygon(S(body), fill=(243, 244, 246, 255))
    # hacim: dış (sol) kenarda ve altta yumuşak gölge
    sh = Image.new("L", L.size, 0)
    ImageDraw.Draw(sh).polygon(S([(x - 14 if x < cx else x - 4, y + 10) for x, y in body]), fill=0)
    shade = Image.new("L", L.size, 0)
    ImageDraw.Draw(shade).polygon(S(body), fill=70)
    inner = Image.new("L", L.size, 0)
    ImageDraw.Draw(inner).polygon(S([(cx + (x - cx) * 0.80 + 6, top + (y - top) * 0.9 + 10) for x, y in body]),
                                  fill=255)
    shade = Image.fromarray(np.where(np.array(inner) > 0, 0, np.array(shade)).astype(np.uint8))
    shade = shade.filter(ImageFilter.GaussianBlur(7 * SS))
    body_m = Image.new("L", L.size, 0)
    ImageDraw.Draw(body_m).polygon(S(body), fill=255)
    shade = Image.fromarray(np.minimum(np.array(shade), np.array(body_m)))
    dark = Image.new("RGBA", L.size, (150, 146, 142, 255))
    dark.putalpha(shade)
    L.alpha_composite(dark)
    # kapüşon içi: yüz oyuğu (gölgeli kenar)
    fx0, fy0, fx1, fy1 = cx - 25, top + 13, cx + 27, top + 66
    d = ImageDraw.Draw(L)
    d.ellipse(S([(fx0 - 4, fy0 - 4), (fx1 + 4, fy1 + 4)]), fill=(206, 202, 198, 255))
    L = L.resize((W, H), Image.LANCZOS)
    face = bebek_yuz(round((fx1 - fx0) * 1.22))
    fl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fl.alpha_composite(face, (round(cx - face.width / 2 + 3), round(fy0 - face.height * 0.20)))
    mk = Image.new("L", (W * SS, H * SS), 0)
    ImageDraw.Draw(mk).ellipse(S([(fx0, fy0), (fx1, fy1)]), fill=255)
    mk = mk.resize((W, H), Image.LANCZOS)
    fl.putalpha(Image.fromarray(np.minimum(np.array(fl.getchannel("A")), np.array(mk))))
    L.alpha_composite(fl)
    # konturlar ve sarma kıvrımları
    K = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(K)
    d.line(S(body + body[:1]), fill=line, width=round(2.6 * SS), joint="curve")
    d.ellipse(S([(fx0 - 1, fy0 - 1), (fx1 + 1, fy1 + 1)]), outline=line, width=round(2.2 * SS))
    fold = (128, 122, 118, 255)
    x0, x1 = cx - w / 2, cx + w / 2
    # sarma: soldan sağa inen tek geniş kanat + karşı taraftan gelen kısa kanat (kundak)
    d.line(S([(x0 - 2, top + 78), (x0 + 24, top + 76), (cx + 10, top + 86), (x1 - 6, top + 104), (x1 + 4, top + 112)]),
           fill=fold, width=round(2.1 * SS), joint="curve")
    d.line(S([(x1 + 3, top + 72), (x1 - 12, top + 82), (cx + 2, top + 98)]),
           fill=fold, width=round(1.9 * SS), joint="curve")
    K = K.resize((W, H), Image.LANCZOS)
    L.alpha_composite(K)
    # bebek annenin göğsüne yaslı: üst kısım içe değil anneye doğru hafifçe yatık
    return L.rotate(BEBEK["egim"], resample=Image.BICUBIC, center=(cx, H))


def ile_bebek(im: Image.Image) -> Image.Image:
    out = im.copy()
    out.alpha_composite(bebek_katmani(im.size))
    out.putalpha(im.getchannel("A"))     # kutu sabit: kundak anne siluetinin içinde kalır
    return out


# ---- ağlayan ağız --------------------------------------------------------------------------------------
def acik_agiz(im: Image.Image, spec: dict) -> Image.Image:
    """Mevcut aralık ağzın yerine daha açık, titreyen (dalgalı) ağız; yalnız ağız bölgesi yeniden çizilir."""
    bx0, by0, bx1, by1 = spec["patch"]
    patch = im.crop((bx0, by0, bx1, by1))
    big = patch.resize((patch.width * SS, patch.height * SS), Image.LANCZOS)
    d = ImageDraw.Draw(big)
    P = lambda pts: [((x - bx0) * SS, (y - by0) * SS) for x, y in pts]  # noqa: E731
    x0, y0, x1, y1 = spec["cover"]
    d.ellipse(P([(x0, y0), (x1, y1)]), fill=tuple(spec["skin"]) + (255,))
    top, bot = P(spec["top"]), P(spec["bottom"])
    poly = top + bot[::-1]
    d.polygon(poly, fill=(70, 20, 26, 255))
    mask = Image.new("L", big.size, 0)
    ImageDraw.Draw(mask).polygon(poly, fill=255)
    teeth = [(x, y + 0.5 * SS) for x, y in top] + [(x, y + spec["teeth_h"] * SS) for x, y in top[::-1]]
    tl = Image.new("RGBA", big.size, (0, 0, 0, 0))
    ImageDraw.Draw(tl).polygon(teeth, fill=(250, 248, 244, 255))
    tl.putalpha(Image.fromarray(np.minimum(np.array(tl.getchannel("A")), np.array(mask))))
    big.alpha_composite(tl)
    d = ImageDraw.Draw(big)
    lw = round(spec["line"] * SS)
    d.line(top, fill=(16, 12, 12, 255), width=lw, joint="curve")
    d.line(bot, fill=(16, 12, 12, 255), width=lw, joint="curve")
    for p in (top[0], top[-1]):
        d.ellipse([p[0] - lw / 2, p[1] - lw / 2, p[0] + lw / 2, p[1] + lw / 2], fill=(16, 12, 12, 255))
    small = big.resize(patch.size, Image.LANCZOS)
    out = im.copy()
    out.paste(small, (bx0, by0))
    out.putalpha(im.getchannel("A"))
    return out


def main() -> None:
    cfg = json.loads((KIT / "kit.json").read_text(encoding="utf-8"))
    taban = anne_taban()
    sakin = ile_bebek(taban)
    sakin.save(KIT / "sakin.png", optimize=True)
    facing.register(KIT / "sakin.png", "right")
    for name, spec in cfg["variants"].items():
        kit_varyant.make(KIT / "sakin.png", spec, KIT / f"{name}.png")
        facing.register(KIT / f"{name}.png", "right")
    ag = cfg["agliyor"]
    tmp = KIT / ".agliyor_tmp.png"
    acik_agiz(sakin, ag["mouth"]).save(tmp)
    kit_varyant.make(tmp, {"tears": ag["tears"]}, KIT / "agliyor.png")
    tmp.unlink()
    facing.register(KIT / "agliyor.png", "right")
    for f in sorted(KIT.glob("*.png")):
        print("->", f.relative_to(ROOT), Image.open(f).size)


if __name__ == "__main__":
    main()
