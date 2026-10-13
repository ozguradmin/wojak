"""Çizim yardımcıları: yazı, gölge, yuvarlak kutu, alt-piksel afin yerleştirme, Ken Burns, gren, vinyet.

Kareler RGB tutulur; RGBA katmanlar `paste(..., mask=alfa)` ile bindirilir (opak zeminde 'over' ile aynı,
alpha_composite'ten hızlı). Tüm ölçüler 1920x1080 içindir; ön izlemede S = W/1920 ile ölçeklenir.
"""

from __future__ import annotations

import math
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

from .. import config
from .. import text as wtext

FONT_DIALOG = config.FONT_DIALOG          # kanalın yazısı (Avenir Bold Italic, yoksa Poppins Bold)
FONT_BOLD = config.FONT_BOLD              # Poppins Bold
FONT_CARD = config.FONT_CARD              # Anton (büyük sayılar)
FONT_MONO = config.FONTS / "LiberationMono-Bold.ttf"   # daktilo etiketi (OFL)

SARI = (242, 190, 58)
KIRMIZI = (214, 58, 50)
YESIL = (70, 196, 118)
BEYAZ = (255, 255, 255)
KOYU = (11, 13, 17)


def buyuk(s: str) -> str:
    """Türkçe büyük harf (i -> İ, ı -> I)."""
    return s.replace("i", "İ").replace("ı", "I").upper()


def font(path, size: int):
    return wtext.font(str(path), max(6, int(round(size))))


# ---------------------------------------------------------------- yazı

def yazi(metin: str, path=FONT_BOLD, size: float = 40, fill=BEYAZ, stroke: float = 0, stroke_fill=(0, 0, 0),
         max_w: float | None = None, max_lines: int = 3, align: str = "left", satir: float = 1.12,
         aralik: float = 0.0, golge: tuple | None = None, min_size: float | None = None,
         dikey_kirp: bool = True) -> Image.Image:
    """Çok satırlı yazı katmanı (RGBA, sıkı kutu). aralik: harf aralığı (punto oranı, ör. 0.25).
    golge: (dx, dy, bulanıklık, opaklık). max_w verilirse dengeli kırılır, sığmazsa punto küçülür.
    dikey_kirp=False: yalnız yatayda kırpılır, yükseklik satır yüksekliği kalır (kelime kelime dizilen yazıda taban
    çizgisi ortak: "ne" gibi çıkıntısız kelime yukarı kaymaz)."""
    size = max(6, int(round(size)))
    sw = int(round(stroke))
    if max_w:
        f, lines, _ = wtext.fit_text(metin, path, size, int(max_w), max_lines, stroke_ratio=sw / max(size, 1),
                                     min_size=int(min_size or max(10, size * 0.6)))
        sw = int(round(stroke * f.size / size))
    else:
        f = font(path, size)
        lines = metin.split("\n")
    asc, desc = f.getmetrics()
    lh = round(f.size * satir)

    def gen(ln):
        if not aralik:
            l, _, r, _ = f.getbbox(ln, stroke_width=sw)
            return r - l, l
        w = 0.0
        for ch in ln:
            w += f.getlength(ch) + aralik * f.size
        return int(w - aralik * f.size) + 2 * sw, 0

    ws = [gen(ln) for ln in lines]
    pad = sw + 4 + (int(golge[2] * 2 + abs(golge[0]) + abs(golge[1])) if golge else 0)
    W = max(w for w, _ in ws) + 2 * pad
    Ht = lh * (len(lines) - 1) + asc + desc + 2 * pad
    lay = Image.new("RGBA", (W, Ht), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for i, (ln, (w, l0)) in enumerate(zip(lines, ws)):
        x = pad + (W - 2 * pad - w) / 2 if align == "center" else (W - pad - w if align == "right" else pad)
        y = pad + i * lh
        if not aralik:
            d.text((x - l0, y), ln, font=f, fill=fill, stroke_width=sw, stroke_fill=stroke_fill)
        else:
            cx = x + sw
            for ch in ln:
                d.text((cx, y), ch, font=f, fill=fill, stroke_width=sw, stroke_fill=stroke_fill)
                cx += f.getlength(ch) + aralik * f.size
    if golge:
        dx, dy, bl, op = golge
        sh = Image.new("RGBA", lay.size, (0, 0, 0, 0))
        a = lay.getchannel("A").filter(ImageFilter.GaussianBlur(bl)) if bl else lay.getchannel("A")
        sh.putalpha(a.point(lambda v: int(v * op)))
        out = Image.new("RGBA", lay.size, (0, 0, 0, 0))
        out.alpha_composite(sh, (int(dx), int(dy)))
        out.alpha_composite(lay)
        lay = out
    bb = lay.getchannel("A").getbbox()
    if bb and not dikey_kirp:
        bb = (bb[0], 0, bb[2], lay.height)
    return lay.crop(bb) if bb else lay


# ---------------------------------------------------------------- şekiller

def yuvarlak_kutu(w: int, h: int, r: float, fill, outline=None, width: float = 0, ss: int = 3) -> Image.Image:
    w, h = max(1, int(w)), max(1, int(h))
    im = Image.new("RGBA", (w * ss, h * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w * ss - 1, h * ss - 1), radius=int(r * ss), fill=fill,
                        outline=outline, width=int(round(width * ss)) if outline else 0)
    return im.resize((w, h), Image.LANCZOS)


def golgeli(lay: Image.Image, bulaniklik: float, opaklik: float, dx: float, dy: float,
            renk=(0, 0, 0)) -> tuple[Image.Image, int, int]:
    """Katmanın altına yumuşak gölge ekler. (yeni katman, orijinalin yeni katmandaki x, y'si)."""
    pad = int(bulaniklik * 2.5 + max(abs(dx), abs(dy))) + 2
    W, H = lay.width + 2 * pad, lay.height + 2 * pad
    a = Image.new("L", (W, H), 0)
    a.paste(lay.getchannel("A"), (pad + int(dx), pad + int(dy)))
    if bulaniklik:
        a = a.filter(ImageFilter.GaussianBlur(bulaniklik))
    sh = Image.new("RGBA", (W, H), renk + (0,))
    sh.putalpha(a.point(lambda v: int(v * opaklik)))
    sh.alpha_composite(lay, (pad, pad))
    return sh, pad, pad


def golge_katmani(lay: Image.Image, bulaniklik: float, opaklik: float, renk=(0, 0, 0)) -> tuple[Image.Image, int, int]:
    """Yalnız gölge (katmanın kendisi yok): (gölge katmanı, katmanın gölge içindeki x, y'si). Kalkan/inen kâğıdın
    gölgesi ayrı çizilsin diye (7. tur)."""
    pad = int(bulaniklik * 2.5) + 2
    a = Image.new("L", (lay.width + 2 * pad, lay.height + 2 * pad), 0)
    a.paste(lay.getchannel("A"), (pad, pad))
    if bulaniklik:
        a = a.filter(ImageFilter.GaussianBlur(bulaniklik))
    sh = Image.new("RGBA", a.size, tuple(renk) + (0,))
    sh.putalpha(a.point(lambda v: int(v * opaklik)))
    return sh, pad, pad


# ---------------------------------------------------------------- görsel yükleme / sığdırma

@lru_cache(maxsize=48)
def _yukle(path: str, mtime: float) -> Image.Image:
    im = Image.open(path)
    im = ImageOps.exif_transpose(im)
    return im.convert("RGBA") if im.mode in ("RGBA", "LA", "P", "PA") else im.convert("RGB")


def yukle(path) -> Image.Image:
    p = Path(path)
    return _yukle(str(p), p.stat().st_mtime).copy()


def kapla(im: Image.Image, w: int, h: int, odak=(0.5, 0.5)) -> Image.Image:
    return ImageOps.fit(im, (int(w), int(h)), Image.LANCZOS, centering=tuple(odak))


def sigdir(im: Image.Image, w: float, h: float, buyut: bool = True) -> Image.Image:
    r = min(w / im.width, h / im.height)
    if r > 1 and not buyut:
        return im.copy()
    return im.resize((max(1, round(im.width * r)), max(1, round(im.height * r))), Image.LANCZOS)


def kirp_alfa(ims: list[Image.Image]) -> list[Image.Image]:
    """Aynı tuvaldeki varyantları ortak (birleşik) alfa kutusuna kırpar: yüz değişiminde hizalama bozulmaz."""
    box = None
    for im in ims:
        b = im.getchannel("A").point(lambda a: 255 if a > 8 else 0).getbbox()
        if b:
            box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3]))
    if box is None:
        return ims
    return [im.crop(box) for im in ims]


def ayarla(im: Image.Image, bulanik: float = 0, karart: float = 0, doygunluk: float = 1.0,
           kontrast: float = 1.0) -> Image.Image:
    if doygunluk != 1.0:
        im = ImageEnhance.Color(im).enhance(doygunluk)
    if kontrast != 1.0:
        im = ImageEnhance.Contrast(im).enhance(kontrast)
    if bulanik:
        im = im.filter(ImageFilter.GaussianBlur(bulanik))
    if karart:
        im = ImageEnhance.Brightness(im).enhance(1 - karart)
    return im


# ---------------------------------------------------------------- yerleştirme

def bindir(dst: Image.Image, src: Image.Image, x: float, y: float, alfa: float = 1.0) -> None:
    """RGBA src'yi RGB dst üzerine (x, y) sol üstten bindirir; taşanı kırpar; alfa ile saydamlaştırır."""
    if alfa <= 0.003:
        return
    x, y = int(round(x)), int(round(y))
    l, t = max(0, -x), max(0, -y)
    r, b = min(src.width, dst.width - x), min(src.height, dst.height - y)
    if r <= l or b <= t:
        return
    if (l, t, r, b) != (0, 0, src.width, src.height):
        src = src.crop((l, t, r, b))
    if src.mode != "RGBA":
        if alfa >= 0.997:
            dst.paste(src, (x + l, y + t))
        else:
            dst.paste(src, (x + l, y + t), Image.new("L", src.size, int(255 * alfa)))
        return
    m = src.getchannel("A")
    if alfa < 0.997:
        m = m.point(_alfa_lut(int(alfa * 255)))
    dst.paste(src, (x + l, y + t), m)


@lru_cache(maxsize=256)
def _alfa_lut(a255: int):
    return [v * a255 // 255 for v in range(256)]


def afin(src: Image.Image, cx: float, cy: float, sx: float = 1.0, sy: float | None = None, aci: float = 0.0,
         ax: float | None = None, ay: float | None = None, resample=Image.BILINEAR) -> tuple[Image.Image, int, int]:
    """src'nin (ax, ay) noktası çerçevede (cx, cy)'ye (alt piksel) gelecek biçimde ölçek/döndürme uygular.
    Dönen: (dönüştürülmüş katman, çerçevedeki sol üst x, y — tam sayı). aci derece, saat yönünün tersi +."""
    sy = sx if sy is None else sy
    ax = src.width / 2 if ax is None else ax
    ay = src.height / 2 if ay is None else ay
    th = math.radians(aci)
    c, s = math.cos(th), math.sin(th)
    # ileri: p' = R S (p - a) + C ; R = [[c, s], [-s, c]] (ekranda y aşağı)
    m00, m01, m10, m11 = c * sx, s * sy, -s * sx, c * sy
    xs, ys = [], []
    for px, py in ((0, 0), (src.width, 0), (0, src.height), (src.width, src.height)):
        dx, dy = px - ax, py - ay
        xs.append(m00 * dx + m01 * dy + cx)
        ys.append(m10 * dx + m11 * dy + cy)
    x0, y0 = math.floor(min(xs)) - 1, math.floor(min(ys)) - 1
    w, h = math.ceil(max(xs)) - x0 + 1, math.ceil(max(ys)) - y0 + 1
    det = m00 * m11 - m01 * m10
    i00, i01, i10, i11 = m11 / det, -m01 / det, -m10 / det, m00 / det
    ox, oy = x0 - cx, y0 - cy
    a, b_, c_ = i00, i01, i00 * ox + i01 * oy + ax
    d, e, f = i10, i11, i10 * ox + i11 * oy + ay
    out = src.transform((w, h), Image.AFFINE, (a, b_, c_, d, e, f), resample=resample)
    return out, x0, y0


ALT_PAY = 4   # alt piksel yerleştirme için sprite çevresindeki saydam pay (px)


def alt_piksel_hazirla(src: Image.Image) -> Image.Image:
    """Sprite'ı alt piksel yerleştirmeye hazırlar: önceden çarpılmış alfa (RGBa) + ALT_PAY saydam kenar."""
    out = Image.new("RGBa", (src.width + 2 * ALT_PAY, src.height + 2 * ALT_PAY))
    out.paste(src.convert("RGBa"), (ALT_PAY, ALT_PAY))
    return out


def alt_piksel(src: Image.Image, x: float, y: float, sx: float, sy: float) -> tuple[Image.Image, int, int]:
    """alt_piksel_hazirla()'dan geçmiş sprite'ı, sol üst köşesi (x, y) (kesirli) ve ölçeği (sx, sy) olacak
    biçimde örnekler. Dönen: (RGBA katman, tam sayı sol üst). `resize(box=...)` ayrılabilir örnekleme kullanır:
    afin dönüşümden ~2 kat hızlı (713 px boyda ~9 ms)."""
    P = ALT_PAY
    w0, h0 = src.width - 2 * P, src.height - 2 * P
    x0, y0 = math.floor(x), math.floor(y)
    fx, fy = x - x0, y - y0
    wo, ho = math.ceil(w0 * sx + fx) + 1, math.ceil(h0 * sy + fy) + 1
    bx, by = P - fx / sx, P - fy / sy
    if bx < 0 or by < 0:   # 8. tur: çok küçük ölçekte (pop girişinin ilk kareleri) kutu eksiye düşüyordu: afin
        out, ax0, ay0 = afin(src, x, y, sx, sy, 0.0, P, P)
        return out.convert("RGBA"), ax0, ay0
    out = src.resize((wo, ho), Image.BILINEAR, box=(bx, by, bx + wo / sx, by + ho / sy))
    return out.convert("RGBA"), x0, y0


def bindir_alt(dst: Image.Image, src: Image.Image, x: float, y: float, alfa: float = 1.0) -> None:
    """Alt piksel bindirme (7. tur): kesirli konum yeniden örneklenerek yerleşir. Yavaş süzülen yazı ve kamerayla
    kayan etiket eskiden tam piksele yuvarlanıyordu: 124 pt yazı 0,3-0,4 sn'de bir 1 px zıplıyor, harita etiketleri
    altlarındaki (alt pikselde kayan) haritaya göre titriyordu."""
    if alfa <= 0.003:
        return
    fx, fy = x - math.floor(x), y - math.floor(y)
    if src.mode != "RGBA" or ((fx < 0.03 or fx > 0.97) and (fy < 0.03 or fy > 0.97)):
        bindir(dst, src, round(x), round(y), alfa)
        return
    spr, x0, y0 = alt_piksel(alt_piksel_hazirla(src), x, y, 1.0, 1.0)
    bindir(dst, spr, x0, y0, alfa)


def afin_pm(src_pm: Image.Image, cx: float, cy: float, sx: float, sy: float, aci: float, ax: float,
            ay: float) -> tuple[Image.Image, int, int]:
    """Önceden çarpılmış alfa (RGBa) kaynakla afin (döndürme + ölçek): saydam kenarda koyu saçak olmaz.
    Dönen katman RGBA."""
    out, x0, y0 = afin(src_pm, cx, cy, sx, sy, aci, ax, ay)
    return out.convert("RGBA"), x0, y0


IZ_EN_COK = 40.0     # px (1080p): hareket izinin en uzun hâli (8. tur)
IZ_OPAKLIK = 0.6     # izin (keskin sprite'ın ALTINDA kalan bulanık kopyanın) opaklığı


def hareket_izi(src: Image.Image, dx: float, dy: float, pay: float = 0.5, en_cok: float | None = IZ_EN_COK,
                alta: bool = True, iz_opak: float = IZ_OPAKLIK) -> tuple[Image.Image, int, int]:
    """Hareket bulanıklığı: katman son karede (dx, dy) px yer değiştirdiyse, hareketin tersine `pay` (obtüratör,
    0.5 = 180°) kadar iz bırakır. Kutu çekirdeği ikiye katlanan kaydırmalarla (L/2, L/4, ...) kurulur: log2(L)
    toplama, eşit aralıklı en çok ~1,5 px'lik örnekler.
    8. tur (animasyon hakemi M1): bulanık kopya artık katmanın YERİNE değil, keskin ve tam opak katmanın ALTINA
    çizilir (`alta`): yüzün çizgileri bulanıp yarı saydam "hayalet"e dönmüyor (0:15'te anlatıcı kafatası gibi
    görünüyordu; giren karakterin arkasından raflar görünüyordu). İz `en_cok` px ile sınırlı (vars. 40 px; 1080p
    dışında çağıran ölçekler), opaklığı `iz_opak`. `alta=False`: eski davranış (bütün katman bulanır).
    Dönen (katman, ox, oy): yeni katmanın sol üstü, eskisinin sol üstüne göre (ox, oy)."""
    vx, vy = -dx * pay, -dy * pay
    L = math.hypot(vx, vy)
    if en_cok is not None and L > en_cok:
        vx, vy, L = vx * en_cok / L, vy * en_cok / L, en_cok
    if L < 1.5 or src.mode != "RGBA":
        return src, 0, 0
    keskin = np.asarray(src.convert("RGBa"), np.float32)
    a = keskin
    ox = oy = 0
    gecis = min(8, max(1, math.ceil(math.log2(L / 1.5))))
    for p in range(gecis):
        f = 0.5 ** (p + 1)
        sx, sy = int(round(vx * f)), int(round(vy * f))
        if sx == 0 and sy == 0:
            continue
        h, w = a.shape[:2]
        b = np.zeros((h + abs(sy), w + abs(sx), 4), np.float32)
        x0, y0 = max(0, -sx), max(0, -sy)
        b[y0:y0 + h, x0:x0 + w] += a
        b[y0 + sy:y0 + sy + h, x0 + sx:x0 + sx + w] += a
        a = b * 0.5
        ox -= x0
        oy -= y0
    if alta:
        # önceden çarpılmış alfa: keskin ÜSTTE (tam opak), iz altta: out = K + iz * opak * (1 - K_a)
        a = a * iz_opak
        h, w = keskin.shape[:2]
        x0, y0 = -ox, -oy
        bolge = a[y0:y0 + h, x0:x0 + w]
        ka = keskin[..., 3:4] / 255.0
        a[y0:y0 + h, x0:x0 + w] = keskin + bolge * (1.0 - ka)
    out = Image.fromarray(np.clip(a + 0.5, 0, 255).astype(np.uint8), "RGBa").convert("RGBA")
    return out, ox, oy


def yatay_bulanik(im: Image.Image, L: float) -> Image.Image:
    """Bütün karede yatay kutu bulanıklığı (itme geçişi: kamera 'savrulması'). L px."""
    n = int(round(L))
    if n < 2:
        return im
    a = np.asarray(im, np.float32)
    pad = np.pad(a, ((0, 0), (n // 2 + 1, n - n // 2), (0, 0)), mode="edge")
    c = np.cumsum(pad, axis=1)
    out = (c[:, n:n + a.shape[1]] - c[:, :a.shape[1]]) / n
    return Image.fromarray(np.clip(out + 0.5, 0, 255).astype(np.uint8), "RGB")


def tabular_yazi(metin: str, path, size: float, fill, rakam_en: float | None = None,
                 golge: tuple | None = None) -> Image.Image:
    """Rakamları sabit genişlikte (tabular) yazar: sayan gösterge kutusu ve yazısı her rakamda genişleyip
    daralmaz (7. tur: köşe göstergesi sayarken kutusu 9 px titriyordu). '?' de rakam hücresine oturur."""
    f = font(path, size)
    hucre = rakam_en or max(f.getlength(str(d)) for d in range(10))
    asc, desc = f.getmetrics()
    pad = 4 + (int(golge[2] * 2 + abs(golge[0]) + abs(golge[1])) if golge else 0)
    # 9. tur: U+2007 = boş rakam hücresi, U+2008 = boş ayraç ('.') genişliği (sayan panel metni sabit genişlikte)
    def gen(ch):
        if ch.isdigit() or ch in "?\u2007":
            return hucre
        return f.getlength("." if ch == "\u2008" else ch)
    w = sum(gen(ch) for ch in metin)
    lay = Image.new("RGBA", (int(math.ceil(w)) + 2 * pad, asc + desc + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    x = float(pad)
    for ch in metin:
        if ch in "\u2007\u2008":
            x += gen(ch)
        elif ch.isdigit() or ch == "?":
            d.text((x + (hucre - f.getlength(ch)) / 2, pad), ch, font=f, fill=fill)
            x += hucre
        else:
            d.text((x, pad), ch, font=f, fill=fill)
            x += f.getlength(ch)
    if golge:
        dx, dy, bl, op = golge
        sh = Image.new("RGBA", lay.size, (0, 0, 0, 0))
        al = lay.getchannel("A").filter(ImageFilter.GaussianBlur(bl)) if bl else lay.getchannel("A")
        sh.putalpha(al.point(lambda v: int(v * op)))
        out = Image.new("RGBA", lay.size, (0, 0, 0, 0))
        out.alpha_composite(sh, (int(dx), int(dy)))
        out.alpha_composite(lay)
        lay = out
    return lay


def cizgi_katmani(x0: float, y0: float, x1: float, y1: float, kalinlik: float, renk, nokta: float = 0.0,
                  ss: int = 3) -> tuple[Image.Image, float, float]:
    """Kenarı yumuşatılmış çizgi (+ başında yuvarlak nokta) katmanı ve kesirli sol üstü: bindir_alt ile yerleşir
    (harita çağrı çizgisi kamerayla kayarken basamaklanmasın)."""
    pad = kalinlik + nokta + 2
    L, T = min(x0, x1) - pad, min(y0, y1) - pad
    w, h = int(math.ceil(abs(x1 - x0) + 2 * pad)) + 1, int(math.ceil(abs(y1 - y0) + 2 * pad)) + 1
    lay = Image.new("RGBA", (w * ss, h * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    p0 = ((x0 - L) * ss, (y0 - T) * ss)
    p1 = ((x1 - L) * ss, (y1 - T) * ss)
    d.line((p0, p1), fill=tuple(renk) + (255,), width=max(1, int(round(kalinlik * ss))))
    if nokta:
        r = nokta * ss
        d.ellipse((p0[0] - r, p0[1] - r, p0[0] + r, p0[1] + r), fill=tuple(renk) + (255,))
    return lay.resize((w, h), Image.LANCZOS), L, T


def kamera(src: Image.Image, W: int, H: int, zoom: float, merkez=(0.5, 0.5),
           resample=Image.BILINEAR) -> Image.Image:
    """Ken Burns: src (W*zmax x H*zmax) içinden 1/zoom'luk pencereyi (merkez, 0..1) W x H'ye örnekler.
    zoom=1 -> src'nin tamamına göre en geniş pencere: src'nin en-boyu çerçeveyle aynı olmalı."""
    sw, sh = src.size
    # pencere: src'nin 1/zoom'u (en geniş = tam src)
    zoom = max(zoom, 1e-3)
    ww = sw / zoom
    wh = sh / zoom
    cx = min(max(merkez[0] * sw, ww / 2), sw - ww / 2)
    cy = min(max(merkez[1] * sh, wh / 2), sh - wh / 2)
    box = (cx - ww / 2, cy - wh / 2, cx + ww / 2, cy + wh / 2)
    return src.resize((W, H), resample, box=box)


# ---------------------------------------------------------------- doku

@lru_cache(maxsize=8)
def vinyet(W: int, H: int, guc: float = 0.55, yumusak: float = 0.75) -> Image.Image:
    """Kenarlara doğru koyulaşan maske (L: 255 = tam karart)."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / math.sqrt(2)
    v = np.clip((d - (1 - yumusak)) / yumusak, 0, 1) ** 1.6 * guc
    return Image.fromarray((v * 255).astype(np.uint8), "L")


def vinyet_uygula(im: Image.Image, guc: float = 0.55) -> None:
    im.paste((0, 0, 0), (0, 0, im.width, im.height), vinyet(im.width, im.height, guc))


@lru_cache(maxsize=4)
def _gren(W: int, H: int, n: int, seed: int = 7) -> tuple[Image.Image, ...]:
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n):
        g = rng.normal(0, 1, (H // 2 + 1, W // 2 + 1)).astype(np.float32)
        a = np.clip(np.abs(g) * 60, 0, 255).astype(np.uint8)
        im = Image.fromarray(a, "L").resize((W, H), Image.NEAREST)
        out.append(im)
    return tuple(out)


def gren_uygula(im: Image.Image, t: float, guc: float = 0.06, fps: int = 30, renk=(255, 255, 255)) -> None:
    """Hafif film greni (vars. açık noktalar; kâğıtta koyu renk ver). guc: 0..1."""
    if guc <= 0:
        return
    frames = _gren(im.width, im.height, 6)
    m = frames[int(t * fps) % len(frames)].point(_alfa_lut(int(guc * 255)))
    im.paste(tuple(renk), (0, 0, im.width, im.height), m)


def gradyan_zemin(W: int, H: int, ic=(30, 34, 42), dis=(8, 9, 12), merkez=(0.5, 0.42)) -> Image.Image:
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W * merkez[0]) / W) ** 2 + ((yy - H * merkez[1]) / H * 0.8) ** 2)
    k = np.clip(d / 0.75, 0, 1)[..., None] ** 1.2
    a, b = np.array(ic, np.float32), np.array(dis, np.float32)
    return Image.fromarray((a + (b - a) * k).astype(np.uint8), "RGB")


def donuk_karart(im: Image.Image, karart: float, hedef: float = 58.0) -> float:
    """Bindirme sahnelerinde donmuş karenin karartma oranı: en az `karart`; açık renkli karede (kâğıt, gökyüzü)
    ortalama parlaklık `hedef`in altına inecek kadar (üstteki beyaz/sarı yazı okunsun)."""
    ort = float(np.asarray(im.convert("L").resize((64, 36))).mean())
    return min(0.9, max(karart, 1.0 - hedef / max(ort, 1.0)))


def say_bicimle(n: float, ondalik: int = 0) -> str:
    """Türkçe sayı biçimi: 10.000 / 2,5"""
    if ondalik:
        s = f"{n:,.{ondalik}f}"
        return s.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{int(round(n)):,}".replace(",", ".")
