#!/usr/bin/env python3
"""prenses_genc kitini kaynaktan yeniden üretir (Kız Kulesi bölümü; ayrıntı kit.json'da).

    python assets/kit/prenses_genc/uret.py

1. Kaynak: HF clayshoaf/Wojaks 5_Doomer_Girl/2481 ("Your Japanese girlfriend", 1467x2048; uzun siyah saç,
   yanak allığı, düz renk). C2P-JR7M4_4 (Kapalak kızı) reel'indeki siyah saçlı kızla aynı çizim ailesi.
   `tools/wojak_lib.py` önbelleğinden okunur (yoksa indirir).
2. Denizci üniforması silinir; yerine düz mor elbise + siyah kontur + altın yaka şeridi (Bizans) çizilir.
   Soldaki saç kütlesi elbisenin önünde kalır.
3. Başa küçük altın taç (stemma): tek bant, birkaç taş, iki yanda incili sarkıt (pendilia).
4. Büst kırpımı (yüz büyük kalsın diye boyun altı kısa).
5. sakin.png = taban (sola bakar). korku.png = aynı kutu: kalkık kaşlar, kocaman yuvarlak gözler + küçük
   gözbebekleri (C2P "Bekle, deprem mi oluyor?" bakışı), alnında mavi soğuk ter çizgileri, ter damlaları,
   açık ağız, allık büyük ölçüde silinmiş (bembeyaz yüz).
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
import wojak_lib  # noqa: E402
from wojak import facing  # noqa: E402

SRC_ID = "5_Doomer_Girl/2481"
CFG = json.loads((KIT / "kit.json").read_text(encoding="utf-8"))
P = CFG["parametreler"]
SS = 2  # çizimler için süper örnekleme

BLACK = (0, 0, 0, 255)
PURPLE = tuple(P["mor"]) + (255,)
GOLD = tuple(P["altin"]) + (255,)
GOLD_DK = tuple(P["altin_koyu"]) + (255,)
LW = P["cizgi"]  # kaynak çizgi kalınlığı (px)


def _lum(a):
    return 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]


def _dilate(m: np.ndarray, r: int) -> np.ndarray:
    im = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(2 * r + 1))
    return np.array(im) > 127


def _poly_mask(size, pts) -> np.ndarray:
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).polygon([tuple(p) for p in pts], fill=255)
    return np.array(m) > 127


def _curve(pts, n=24):
    """Catmull-Rom: elle verilen kontrol noktalarından yumuşak eğri."""
    pts = [np.array(p, float) for p in pts]
    pts = [pts[0]] + pts + [pts[-1]]
    out = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        for t in np.linspace(0, 1, n, endpoint=False):
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(pts[-2])
    return [tuple(map(float, p)) for p in out]


def _ss_layer(size):
    lay = Image.new("RGBA", (size[0] * SS, size[1] * SS), (0, 0, 0, 0))
    return lay, ImageDraw.Draw(lay)


def _s(pts):
    return [(x * SS, y * SS) for x, y in pts]


def _stroke(d: ImageDraw.ImageDraw, pts, width: float, fill) -> None:
    """Kalın, yuvarlak uçlu fırça çizgisi (PIL'in kalın çizgi eklem çıkıntıları olmadan): yol boyunca daire basar.
    pts süper örneklenmiş düzlemde."""
    r = width / 2
    step = max(1.0, r / 3)
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        n = max(1, int(np.hypot(x1 - x0, y1 - y0) / step))
        for t in np.linspace(0, 1, n + 1):
            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            d.ellipse([x - r, y - r, x + r, y + r], fill=fill)


def _down(lay, size):
    return lay.resize(size, Image.LANCZOS)


def kaynak() -> Image.Image:
    return wojak_lib.fetch(SRC_ID).convert("RGBA")


def govde(src: Image.Image) -> Image.Image:
    """Üniformayı siler, mor elbise + altın yaka çizer; sol saç önde kalır."""
    a = np.array(src).astype(np.int32)
    H, W = a.shape[:2]
    r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    lum = _lum(a)
    op = al > 0
    yy = np.mgrid[0:H, 0:W][0]
    skin = op & (r >= 254) & (g >= 254) & (b >= 254)
    hairfill = op & (lum >= 8) & (lum < 60) & (al > 200)
    xx = np.mgrid[0:H, 0:W][1]
    # sol saç kütlesi (boynun solu): elbisenin önünde kalır; saç dolgusu + kendi konturu
    sx = P["sol_sac_x"]
    # (çekirdek: çizgilerin kenar yumuşatması da 8-60 parlaklıkta olduğundan ince çizgiler 'saç' sayılmasın diye
    #  önce aşındırılır; denizci yakasının sol omuzdaki konturları böylece elbisenin altında kalır)
    core = ~_dilate(~(hairfill & (xx < sx)), 4)
    left_hair = _dilate(core, LW + 8) & op & (lum < 150) & (xx < sx + LW)
    # elbise bölgesi: omuz/yaka konturunun altı
    neck = _curve(P["yaka"])                      # soldan sağa: omuz - U yaka - omuz
    body_poly = [(-40, neck[0][1])] + neck + [(W + 40, neck[-1][1]), (W + 40, H + 40), (-40, H + 40)]
    body = _poly_mask((W, H), body_poly)
    # üniforma artıkları (yaka çizgisinin üstünde kalan gri gölge, açık dolgu, yeşil şerit) da silinir;
    # boyun konturu (tene bitişik siyah çizgi) korunur
    uni = op & ~skin & ~hairfill & (lum > 60) & (yy > P["uniforma_ust_y"])
    uni_lines = (op & (lum < 60) & ~hairfill & (yy > P["uniforma_ust_y"]) & _dilate(uni, LW + 2)
                 & ~_dilate(skin, LW + 6))
    sil = (body | uni | uni_lines) & ~left_hair
    a2 = a.copy()
    a2[..., 3] = np.where(sil, 0, a2[..., 3])
    head = Image.fromarray(a2.astype(np.uint8))

    # elbise katmanı (başın altında): düz mor + altın yaka şeridi (elbiseye kırpılır) + siyah kontur
    lay, d = _ss_layer((W, H))
    d.polygon(_s(body_poly), fill=PURPLE)
    trim, dt = _ss_layer((W, H))
    trim_w = P["yaka_serit"]
    path = _curve(P["yaka_serit_yol"])
    band = [(x, y - trim_w / 2) for x, y in path] + [(x, y + trim_w / 2) for x, y in path[::-1]]
    dt.polygon(_s(band), fill=GOLD)
    _stroke(dt, _s([(x, y + trim_w / 2) for x, y in path]), round(LW * 0.8 * SS), BLACK)
    for (x, y), col in zip(P["yaka_taslar"], P["yaka_tas_renk"]):
        rr = P["yaka_tas_r"]
        dt.ellipse([(x - rr) * SS, (y - rr) * SS, (x + rr) * SS, (y + rr) * SS], fill=tuple(col) + (255,),
                   outline=BLACK, width=round(P["tas_cizgi"] * SS))
    body_ss = Image.new("L", lay.size, 0)
    ImageDraw.Draw(body_ss).polygon(_s(body_poly), fill=255)
    trim.putalpha(Image.fromarray(np.minimum(np.array(trim.getchannel("A")), np.array(body_ss))))
    lay.alpha_composite(trim)
    d = ImageDraw.Draw(lay)
    _stroke(d, _s(neck), LW * SS, BLACK)
    for seg in P.get("elbise_kivrim", []):   # birkaç kumaş kıvrımı çizgisi (düz renk, gölge yok)
        _stroke(d, _s(_curve(seg)), round(LW * 0.75 * SS), BLACK)
    dress = _down(lay, (W, H))
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.alpha_composite(dress)
    out.alpha_composite(head)
    # sol saç elbisenin önünde
    hair_l = np.array(src).copy()
    hair_l[..., 3] = np.where(left_hair & (yy > P["uniforma_ust_y"]), hair_l[..., 3], 0)
    out.alpha_composite(Image.fromarray(hair_l))
    return out


def tac(im: Image.Image) -> Image.Image:
    """Küçük altın stemma: alın üstünde tek bant, taşlar, iki yanda incili sarkıt."""
    W, H = im.size
    lay, d = _ss_layer((W, H))
    t = P["tac"]
    top = _curve(t["ust"])
    bot = _curve(t["alt"])
    poly = top + bot[::-1]
    # sarkıtlar (önce: bandın altında kalsın)
    for chain in t["sarkit"]:
        x0, y0 = chain["bas"]
        d.line(_s([(x0, y0), (x0 + chain["dx"], y0 + chain["boy"])]), fill=GOLD_DK, width=round(5 * SS))
        for k in range(chain["inci"]):
            cy = y0 + chain["boy"] * (k + 1) / chain["inci"]
            cx = x0 + chain["dx"] * (k + 1) / chain["inci"]
            rr = chain["r"]
            d.ellipse([(cx - rr) * SS, (cy - rr) * SS, (cx + rr) * SS, (cy + rr) * SS], fill=(252, 250, 244, 255),
                      outline=BLACK, width=round(P["inci_cizgi"] * SS))
    for pk in t.get("sivri", []):            # bandın üstünde küçük yuvarlak uçlar
        d.polygon(_s(pk), fill=GOLD)
        _stroke(d, _s(pk + [pk[0]]), round(LW * 0.75 * SS), BLACK)
    d.polygon(_s(poly), fill=GOLD)
    _stroke(d, _s(poly + [poly[0]]), round(LW * 0.8 * SS), BLACK)
    for (x, y), col in zip(t["taslar"], t["tas_renk"]):
        rr = t["tas_r"]
        d.ellipse([(x - rr) * SS, (y - rr * 0.9) * SS, (x + rr) * SS, (y + rr * 0.9) * SS], fill=tuple(col) + (255,),
                  outline=BLACK, width=round(P["tas_cizgi"] * SS))
    for x, y in t.get("inciler", []):
        rr = t["inci_r"]
        d.ellipse([(x - rr) * SS, (y - rr) * SS, (x + rr) * SS, (y + rr) * SS], fill=(252, 250, 244, 255),
                  outline=BLACK, width=round(P["inci_cizgi"] * SS))
    out = im.copy()
    out.alpha_composite(_down(lay, (W, H)))
    return out


def kirp(im: Image.Image) -> Image.Image:
    x0, y0, x1, y1 = P["kirp"]
    out = im.crop((x0, y0, x1, y1))
    sx = P.get("yatay_olcek", 1.0)
    if sx != 1.0:
        out = out.resize((round(out.width * sx), out.height), Image.LANCZOS)
    return out


# --- yüz varyantı (koordinatlar kaynak düzleminde; kırpım/ölçek sonra uygulanır) -----------------------

def _beyaz_doldur(a: np.ndarray, mask: np.ndarray) -> None:
    a[mask, 0:3] = 255


def korku(im: Image.Image) -> Image.Image:
    """Ters köşe yüzü: kaşlar kalkar, gözler kocaman/yuvarlak, gözbebekleri küçük; mavi ter çizgileri,
    damlalar, açık ağız; allık büyük ölçüde silinir. Kaynak (kırpılmamış) düzlemde çalışır."""
    k = P["korku"]
    a = np.array(im).astype(np.int32)
    H, W = a.shape[:2]
    lum = _lum(a)
    # 1) allığı sil: yüzdeki açık pembe pikselleri beyaza çek, neredeyse beyaz teni tam beyaz yap (silinen göz/ağız
    #    alanlarıyla aynı ton olsun, hayalet halka kalmasın); çizgiler ve kenar yumuşatmaları (nötr gri) etkilenmez
    face_box = np.zeros((H, W), bool)
    fx0, fy0, fx1, fy1 = k["yuz_kutu"]
    face_box[fy0:fy1, fx0:fx1] = True
    vis = face_box & (a[..., 3] > 200)
    pinkish = vis & (lum > 150) & (a[..., 0] - a[..., 2] > 4) & (np.abs(a[..., 1] - a[..., 2]) < 30)
    t = k["allik_sil"]
    for c in range(3):
        a[..., c] = np.where(pinkish, np.round(a[..., c] + t * (255 - a[..., c])), a[..., c])
    near_white = vis & (_lum(a) > 238)
    a[near_white, 0:3] = 255
    # 2) kaşları yukarı taşı
    for (x0, y0, x1, y1), dy in zip(k["kas_kutulari"], k["kas_dy"]):
        reg = a[y0:y1, x0:x1].copy()
        dark = _lum(reg) < 235                        # kaş + kenar yumuşatması
        sub = a[y0:y1, x0:x1]
        sub[dark, 0:3] = 255                          # eski kaşı sil
        tgt = a[y0 - dy:y1 - dy, x0:x1]
        tgt[dark] = reg[dark]
    # kaynağın üst kapak + kirpik çizgileri (her gözün 'kesim' eğrisinin üstü) silmeden önce saklanır
    kapak_src = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    kapak_m = Image.new("L", (W * SS, H * SS), 0)
    dm = ImageDraw.Draw(kapak_m)
    for g in k["gozler"]:
        ks = _curve(g["kesim"], n=12)
        x0, x1 = ks[0][0] - 8, ks[-1][0] + 8
        dm.polygon(_s([(x0, k["kapak_ust_y"]), (x1, k["kapak_ust_y"]), (x1, ks[-1][1])] + ks[::-1]
                      + [(x0, ks[0][1])]), fill=255)
    kapak_m = kapak_m.resize((W, H), Image.LANCZOS)
    # 3) eski gözleri ve dudakları sil (ten beyazı), yüz konturuna dokunmadan
    for ex in k["goz_sil"] + [k["agiz_sil"]]:
        cx, cy, rx, ry = ex
        yy, xx = np.ogrid[0:H, 0:W]
        m = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1
        _beyaz_doldur(a, m & (a[..., 3] > 0))
    out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    sil, dsil = _ss_layer((W, H))                # eski alt kapak / iris artıkları (kesim eğrisinin altı) tamamen silinir
    for g in k["gozler"]:
        ks = _curve(g["kesim"], n=12)
        dsil.polygon(_s(ks + _curve(g["eski_sil"], n=12)[::-1]), fill=(255, 255, 255, 255))
    out.alpha_composite(_down(sil, (W, H)))
    # 4) aşağı doğru kocaman açılmış gözler: kaynağın kapağı aynen kalır, altı yeni alt kapak çizgisine kadar açılır;
    #    koyu gri halkalı iris + küçük gözbebeği (içe bakar), koyu gri göz altı çizgileri (C2P şok yüzü)
    eye, de = _ss_layer((W, H))
    torba = tuple(k["torba_renk"]) + (255,)
    for g in k["gozler"]:
        ks, al = _curve(g["kesim"], n=12), _curve(g["alt"], n=12)
        de.polygon(_s(ks + al[::-1]), fill=(255, 255, 255, 255))
        cx, cy = g["merkez"]
        px, py = cx + g["bebek_dx"], cy + g["bebek_dy"]
        (irx, iry), (icx, icy) = g["iris"], g["iris_ic"]
        iris_l, di = _ss_layer((W, H))
        di.ellipse([(px - irx) * SS, (py - iry) * SS, (px + irx) * SS, (py + iry) * SS],
                   fill=tuple(k["iris_renk"]) + (255,))
        di.ellipse([(px - icx) * SS, (py - icy) * SS, (px + icx) * SS, (py + icy) * SS], fill=(255, 255, 255, 255))
        pr = g["bebek_r"]
        di.ellipse([(px - pr) * SS, (py - pr) * SS, (px + pr) * SS, (py + pr) * SS], fill=BLACK)
        hx, hy, hr = g["isik"]
        di.ellipse([(px + hx - hr) * SS, (py + hy - hr) * SS, (px + hx + hr) * SS, (py + hy + hr) * SS],
                   fill=(255, 255, 255, 255))
        clip = Image.new("L", eye.size, 0)                 # iris göz açıklığına kırpılır
        ImageDraw.Draw(clip).polygon(_s(ks + al[::-1]), fill=255)
        iris_l.putalpha(Image.fromarray(np.minimum(np.array(iris_l.getchannel("A")), np.array(clip))))
        eye.alpha_composite(iris_l)
        de = ImageDraw.Draw(eye)
        _stroke(de, _s(al), round(k["goz_cizgi"] * SS), BLACK)
        for arc in g.get("torba", []):           # göz altı çizgileri
            _stroke(de, _s(_curve(arc)), round(k["torba_w"] * SS), torba)
    out.alpha_composite(_down(eye, (W, H)))
    kapak = kapak_src.copy()
    kapak.putalpha(Image.fromarray(np.minimum(np.array(kapak_src.getchannel("A")), np.array(kapak_m))))
    out.alpha_composite(kapak)
    lay, d = _ss_layer((W, H))
    for g in k["gozler"]:                        # göz köşeleri: kapak ile yeni alt kapak çizgisini birleştiren yuvarlak uç
        for x, y, r in g.get("koseler", []):
            d.ellipse([(x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS], fill=BLACK)
    # 5) açık ağız
    m = k["agiz"]
    pts = _curve(m["ust"]) + _curve(m["alt"])[::-1]
    d.polygon(_s(pts), fill=(70, 18, 28, 255))
    dil = _curve(m["dil"])
    d.polygon(_s(dil), fill=(214, 96, 110, 255))
    _stroke(d, _s(pts + [pts[0]]), round(LW * 0.8 * SS), BLACK)
    # 6) alında mavi soğuk ter çizgileri
    for ln in k["mavi_cizgiler"]:
        _stroke(d, _s(_curve(ln)), round(k["mavi_w"] * SS), tuple(k["mavi"]) + (255,))
    out.alpha_composite(_down(lay, (W, H)))
    # 7) ter damlaları (tools/kit_varyant.py ile aynı çizim)
    tmp = KIT / ".korku_tmp.png"
    out.save(tmp)
    kit_varyant.make(tmp, {"drops": k["damlalar"]}, tmp)
    out = Image.open(tmp).convert("RGBA")
    tmp.unlink()
    return out


def main() -> None:
    src = kaynak()
    base = tac(govde(src))
    sakin = kirp(base)
    sakin.save(KIT / "sakin.png", optimize=True)
    facing.register(KIT / "sakin.png", "left")
    kork = kirp(korku(base))
    kork.save(KIT / "korku.png", optimize=True)
    facing.register(KIT / "korku.png", "left")
    for f in ("sakin.png", "korku.png"):
        im = Image.open(KIT / f)
        print("->", (KIT / f).relative_to(ROOT), im.size)


if __name__ == "__main__":
    main()
