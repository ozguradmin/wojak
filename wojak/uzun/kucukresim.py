"""YouTube küçük resmi (1280x720): arka plan + 1-2 wojak + 2-4 kelimelik dev yazı + isteğe bağlı ok/daire + küçük arşiv görseli.

Spesifikasyon (video.yaml > kucukresimler, her öğe bir varyant; YouTube "Test ve karşılaştır" için 2-3 varyant):
    - ad: a
      arka: img/mekan.jpg          # kaplar, kontrast/doygunluk artar, kenarlar kararır
      karart: 0.35
      karakterler: [{gorsel: chars/x.png, taraf: sol, boy: 0.95}]   # içeri bakar (wojak.facing), beyaz kontur
      yazi: "TÜRKİYE'YE GİREMEDİ"  # 2-4 kelime; en fazla 2 satır, büyük harf; yazi_y (0..1), yazi_bolge [x0, x1]
      vurgu_kelime: GİREMEDİ       # sarı yazılır
      ek: {gorsel: img/kanit.jpg, konum: sag_alt, boy: 0.32, egim: 4}
      ok: {bas: [0.5, 0.45], son: [0.72, 0.7]}        # 0..1 koordinat, kırmızı ok
      daire: {x: 0.8, y: 0.78, r: 0.16}              # kırmızı halka (r: yüksekliğe oran)
Dosya: out/<id>-uzun/kucukresim_<ad>.jpg (< 2 MB, YouTube sınırı).
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

from .. import config, facing
from . import cizim as C
from .spec import Video

KW, KH = 1280, 720
KIRMIZI = (230, 30, 36)


def _sticker(im: Image.Image, kalinlik: int = 7) -> Image.Image:
    """Karaktere beyaz dış kontur + yumuşak gölge."""
    pad = kalinlik * 3
    a = Image.new("L", (im.width + 2 * pad, im.height + 2 * pad), 0)
    a.paste(im.getchannel("A"), (pad, pad))
    kont = a.filter(ImageFilter.MaxFilter(kalinlik * 2 + 1)).filter(ImageFilter.GaussianBlur(1))
    out = Image.new("RGBA", a.size, (0, 0, 0, 0))
    gol = Image.new("RGBA", a.size, (0, 0, 0, 0))
    gol.putalpha(kont.filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * 0.6)))
    out.alpha_composite(gol, (6, 8))
    beyaz = Image.new("RGBA", a.size, (255, 255, 255, 0))
    beyaz.putalpha(kont)
    out.alpha_composite(beyaz)
    out.alpha_composite(im, (pad, pad))
    return out


def _yazi(metin: str, vurgu: str | None, max_w: float, max_h: float) -> Image.Image:
    """Dev, konturlu yazı (Anton, büyük harf). vurgu kelime(ler)i sarı."""
    metin = C.buyuk(metin)
    vurgu_k = set(C.buyuk(vurgu or "").split())
    kel = metin.split()
    for size in range(200, 60, -6):
        f = C.font(C.FONT_CARD, size)
        sw = max(4, size // 14)
        # 1 ya da 2 satır: en dengeli sığan kırım
        adaylar = [[kel]] + [[kel[:i], kel[i:]] for i in range(1, len(kel))]
        uygun = []
        for sat in adaylar:
            gen = [f.getlength(" ".join(s)) + 2 * sw for s in sat]
            yuk = len(sat) * size * 1.02
            if max(gen) <= max_w and yuk <= max_h:
                uygun.append((max(gen) - min(gen) + (0 if len(sat) == 2 else 40), sat))
        if uygun:
            sat = min(uygun, key=lambda x: x[0])[1]
            break
    lh = int(size * 1.0)
    W = int(max(f.getlength(" ".join(s)) for s in sat) + 4 * sw + 30)
    H = int(lh * len(sat) + size * 0.35 + 4 * sw + 30)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for i, s in enumerate(sat):
        x = (W - f.getlength(" ".join(s))) / 2
        y = 15 + i * lh
        for k in s:
            renk = (255, 214, 0) if k.strip("\"'“”„,.!?") in vurgu_k or k in vurgu_k else (255, 255, 255)
            d.text((x, y), k, font=f, fill=renk, stroke_width=sw, stroke_fill=(0, 0, 0))
            x += f.getlength(k + " ")
    gol = Image.new("RGBA", lay.size, (0, 0, 0, 0))
    gol.putalpha(lay.getchannel("A").filter(ImageFilter.GaussianBlur(8)).point(lambda v: int(v * 0.75)))
    out = Image.new("RGBA", lay.size, (0, 0, 0, 0))
    out.alpha_composite(gol, (0, 7))
    out.alpha_composite(lay)
    bb = out.getchannel("A").getbbox()
    return out.crop(bb) if bb else out


def _ok(d: ImageDraw.ImageDraw, a, b, kal: int, ss: int):
    ax, ay, bx, by = a[0] * ss, a[1] * ss, b[0] * ss, b[1] * ss
    ang = math.atan2(by - ay, bx - ax)
    bas = kal * 2.6 * ss
    gx, gy = bx - math.cos(ang) * bas * 0.9, by - math.sin(ang) * bas * 0.9
    uc = [(bx, by), (gx + math.cos(ang + math.pi / 2) * bas * 0.75, gy + math.sin(ang + math.pi / 2) * bas * 0.75),
          (gx - math.cos(ang + math.pi / 2) * bas * 0.75, gy - math.sin(ang + math.pi / 2) * bas * 0.75)]
    for renk, ek in (((0, 0, 0, 255), 6 * ss), (KIRMIZI + (255,), 0)):
        d.line((ax, ay, gx, gy), fill=renk, width=int(kal * ss + ek))
        d.polygon(uc, fill=renk, outline=renk, width=int(ek) if ek else 0)


def uret(v: Video, spec: dict, cikti: Path) -> Path:
    ss = 2
    arka = C.yukle(v.yol(spec["arka"])).convert("RGB")
    im = C.kapla(arka, KW, KH, tuple(spec.get("odak", (0.5, 0.5))))
    im = ImageEnhance.Contrast(im).enhance(1.12)
    im = ImageEnhance.Color(im).enhance(1.12)
    im = im.filter(ImageFilter.GaussianBlur(float(spec.get("bulanik", 1.5))))
    im = ImageEnhance.Brightness(im).enhance(1 - float(spec.get("karart", 0.3)))
    C.vinyet_uygula(im, 0.6)
    # küçük arşiv görseli
    ek = spec.get("ek")
    if ek:
        foto = C.yukle(v.yol(ek["gorsel"])).convert("RGB")
        boy = float(ek.get("boy", 0.32)) * KH
        foto = C.sigdir(foto, boy * 1.6, boy)
        b = 10
        pr = Image.new("RGBA", (foto.width + 2 * b, foto.height + 2 * b), (250, 248, 242, 255))
        pr.paste(foto, (b, b))
        spr, ox, oy = C.golgeli(pr, 12, 0.6, 5, 8)
        egim = float(ek.get("egim", 4 if "sag" in ek.get("konum", "sag_alt") else -4))
        spr = spr.rotate(egim, resample=Image.BICUBIC, expand=True)
        konum = ek.get("konum", "sag_alt")
        x = KW - spr.width - 30 if "sag" in konum else (30 if "sol" in konum else (KW - spr.width) // 2)
        y = KH - spr.height - 26 if "alt" in konum else 26
        im.paste(spr, (int(x), int(y)), spr)
    # karakterler
    kars = spec.get("karakterler") or []
    for i, c in enumerate(kars):
        p = v.yol(c["gorsel"])
        k = C.kirp_alfa([C.yukle(p).convert("RGBA")])[0]
        taraf = c.get("taraf", "sol" if i == 0 else "sag")
        cx = float(c.get("x", {"sol": 0.24, "sag": 0.76, "orta": 0.5}[taraf]))
        faces, _ = facing.resolve(p, c.get("bakis"))
        if faces != "front" and facing.needs_flip(faces, cx):
            k = ImageOps.mirror(k)
        h = float(c.get("boy", 0.95)) * KH
        k = k.resize((max(1, round(k.width * h / k.height)), round(h)), Image.LANCZOS)
        st = _sticker(k)
        pad = (st.width - k.width) // 2
        x = cx * KW - k.width / 2 - pad
        y = KH - k.height + 0.05 * k.height - pad
        im.paste(st, (int(x), int(y)), st)
    # halka / ok
    if spec.get("daire") or spec.get("ok"):
        lay = Image.new("RGBA", (KW * ss, KH * ss), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        if spec.get("daire"):
            dc = spec["daire"]
            cx, cy, r = float(dc["x"]) * KW * ss, float(dc["y"]) * KH * ss, float(dc.get("r", 0.15)) * KH * ss
            for renk, w in (((0, 0, 0, 255), 20), (KIRMIZI + (255,), 12)):
                d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=renk, width=w * ss)
        if spec.get("ok"):
            o = spec["ok"]
            _ok(d, (o["bas"][0] * KW, o["bas"][1] * KH), (o["son"][0] * KW, o["son"][1] * KH), 16, ss)
        lay = lay.resize((KW, KH), Image.LANCZOS)
        im.paste(lay, (0, 0), lay)
    # yazı
    if spec.get("yazi"):
        tek = len(kars) == 1
        sol = tek and kars[0].get("taraf", "sol") == "sol"
        sag = tek and not sol
        yb = [float(q) for q in (spec.get("yazi_bolge") or [])]
        if yb:   # [x0, x1] ya da [x0, x1, y0, y1] (0..1): yazının alanı (ör. karaktersiz haritada boş deniz)
            bolge = (KW * yb[0], KW * yb[1])
            max_h = KH * ((yb[3] - yb[2]) if len(yb) == 4 else 0.5)
        elif tek:
            bolge = (KW * 0.47, KW * 0.97) if sol else (KW * 0.03, KW * 0.53)
            max_h = KH * 0.62
        else:
            bolge = (KW * 0.05, KW * 0.95)
            max_h = KH * 0.42
        yz = _yazi(str(spec["yazi"]), spec.get("vurgu_kelime"), bolge[1] - bolge[0], max_h)
        x = (bolge[0] + bolge[1]) / 2 - yz.width / 2
        y = KH * (0.06 if not tek else 0.08)
        if spec.get("yazi_y") is not None:
            y = float(spec["yazi_y"]) * KH
        elif len(yb) == 4:   # alanın dikey ortası
            y = KH * (yb[2] + yb[3]) / 2 - yz.height / 2
        im.paste(yz, (int(x), int(y)), yz)
    # küçük filigran: sol altta (sağ alt köşe YouTube'un süre rozetinin altında kalıyor)
    wm = C.yazi(config.WATERMARK, C.FONT_DIALOG, 24, (255, 255, 255), stroke=2)
    im.paste(wm, (18, KH - wm.height - 12), wm)
    cikti.parent.mkdir(parents=True, exist_ok=True)
    q = 92
    while True:
        im.save(cikti, quality=q, optimize=True)
        if cikti.stat().st_size < 1.9e6 or q < 60:
            break
        q -= 6
    return cikti


def hepsi(v: Video, klasor: Path) -> list[Path]:
    out = []
    for i, s in enumerate(v.kucukresimler):
        ad = str(s.get("ad", chr(ord("a") + i)))
        out.append(uret(v, s, klasor / f"kucukresim_{ad}.jpg"))
    return out


def telifli_mi(v: Video, spec: dict) -> bool:
    yollar = [spec.get("arka")] + [c.get("gorsel") for c in spec.get("karakterler") or []] + \
        [(spec.get("ek") or {}).get("gorsel")]
    return any(p and "telifli" in str(p) for p in yollar)
