"""Sahne tipleri (1920x1080, hepsi easing'li animasyon) ve sahne üstü katmanlar.

Tipler: wojak, foto, manset, harita, sayac, bolum_karti, metin, zaman_cizelgesi (takma ad: liste).
Üst katmanlar (her sahnede): isim etiketi (lower third), vurgu kelimesi. Filigran render.py'de, geçişten
sonra eklenir (her karede sabit).

Her sahnenin varsayılan zamanlaması (ülkelerin yanma sırası, noktaların belirmesi, etiketin yazılması...)
bu dosyanın başındaki *_zamanlari() fonksiyonlarındadır: çizici, otomatik efektler (ses.py) ve hareket
denetimi (vuruslar) aynı zamanları kullanır.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps

from .. import facing
from . import cizim as C
from . import easing as E
from .spec import Olay, Sahne, Video
from .zaman import balon_olaylari


# ================================================================ zamanlama varsayılanları

def olaylar(sahne: Sahne, tip: str) -> list[Olay]:
    return sorted((o for o in sahne.olaylar if o.tip == tip), key=lambda o: o.zaman)


def basla_zamani(sahne: Sahne, varsayilan: float) -> float:
    b = olaylar(sahne, "basla")
    return b[0].zaman if b else varsayilan


def karakter_zamanlari(sahne: Sahne) -> dict[str, dict]:
    """id -> {giris: t|None, cikis: t|None, yuz: [(t, gorsel)]}"""
    out = {}
    for i, c in enumerate(sahne.p.get("karakterler", [])):
        g = c.get("giris", True)
        giris = None if g is False else (float(g) if isinstance(g, (int, float)) and g is not True else 0.05 + 0.22 * i)
        out[c["id"]] = {"giris": giris, "cikis": None, "yuz": []}
    for o in sahne.olaylar:
        k = o.p.get("karakter")
        if k not in out:
            continue
        if o.tip == "giris":
            out[k]["giris"] = o.zaman
        elif o.tip == "cikis":
            out[k]["cikis"] = o.zaman
        elif o.tip == "yuz":
            out[k]["yuz"].append((o.zaman, Path(o.p["gorsel"])))
    for v in out.values():
        v["yuz"].sort(key=lambda x: x[0])
    return out


def foto_zamanlari(sahne: Sahne) -> dict:
    inis = 0.12
    et = olaylar(sahne, "etiket")
    etiket = et[0].zaman if et else 0.95
    metin = str(sahne.p.get("etiket") or "")
    return {"inis": inis, "oturma": inis + 0.62, "etiket": etiket, "harf_hizi": DaktiloEtiket.HIZ,
            "etiket_metni": metin, "etiket_bitis": etiket + len(metin) / DaktiloEtiket.HIZ}


def etiket_zamani(sahne: Sahne, varsayilan: float) -> float | None:
    """wojak/manset/foto sahnelerindeki daktilo etiketinin başlama anı (etiket yoksa None)."""
    if not sahne.p.get("etiket"):
        return None
    et = olaylar(sahne, "etiket")
    return et[0].zaman if et else varsayilan


def manset_zamanlari(sahne: Sahne) -> list[float]:
    n = len(sahne.p.get("kutular") or [])
    ts = [0.8 + 1.1 * i for i in range(n)]
    for o in olaylar(sahne, "vurgula"):
        k = int(o.p["kutu"]) - 1
        if 0 <= k < n:
            ts[k] = o.zaman
    return ts


def harita_zamanlari(sahne: Sahne) -> tuple[list[tuple[str, float]], tuple[str, float] | None]:
    p = sahne.p
    kodlar = [str(k) for k in (p.get("ulkeler") or [])]
    dur = sahne.sure_hesap or 6.0
    bas = basla_zamani(sahne, 0.5)
    n = max(1, len(kodlar))
    aralik = float(p["aralik"]) if p.get("aralik") is not None else min(0.45, max(0.12, dur * 0.45 / n))
    ts = {k: bas + i * aralik for i, k in enumerate(kodlar)}
    vurgu = p.get("vurgu")
    vk = None
    if vurgu:
        vk = str(vurgu["kod"] if isinstance(vurgu, dict) else vurgu)
    vt = (bas + n * aralik + 0.6) if kodlar else bas
    for o in olaylar(sahne, "ulke"):
        k = str(o.p["kod"])
        if k == vk:
            vt = o.zaman
        elif k in ts:
            ts[k] = o.zaman
    return [(k, ts[k]) for k in kodlar], ((vk, vt) if vk else None)


def sayac_zamanlari(sahne: Sahne) -> tuple[float, float]:
    p = sahne.p
    bas = basla_zamani(sahne, 0.35)
    if p.get("yil"):
        a, b = p["yil"]
        sure = float(p.get("sure_say", max(1.0, 0.42 * abs(int(b) - int(a)))))
    else:
        sure = float(p.get("sure_say", 2.2))
    return bas, bas + sure


def zc_zamanlari(sahne: Sahne) -> list[float]:
    n = len(sahne.p["noktalar"])
    dur = sahne.sure_hesap or 6.0
    bas = basla_zamani(sahne, 0.75)
    ara = max(0.45, min(2.2, (dur - bas - 1.0) / max(n, 1)))
    ts = [bas + i * ara for i in range(n)]
    for o in olaylar(sahne, "nokta"):
        k = int(o.p["indeks"]) - 1
        if 0 <= k < n:
            ts[k] = o.zaman
    return ts


def metin_zamanlari(sahne: Sahne) -> dict:
    kel = str(sahne.p.get("metin", "")).split()
    bas = basla_zamani(sahne, 0.3)
    kt = [bas + 0.14 * i for i in range(len(kel))]
    cev = olaylar(sahne, "ceviri")
    ct = cev[0].zaman if cev else (float(sahne.p["ceviri_t"]) if sahne.p.get("ceviri_t") is not None
                                  else (kt[-1] if kt else bas) + 0.7)
    return {"kelimeler": kt, "ceviri": ct}


def vuruslar(sahne: Sahne) -> list[float]:
    """Sahnede ekrana yeni bir şey geldiği anlar (hareket denetimi için, sahne içi sn)."""
    t = [0.0]
    for o in sahne.olaylar:
        t.append(o.zaman)
    tip = sahne.tip
    if tip == "wojak":
        for v in karakter_zamanlari(sahne).values():
            t += [x for x in (v["giris"], v["cikis"]) if x is not None] + [y for y, _ in v["yuz"]]
        t += [o.zaman for o in balon_olaylari(sahne)]
        e = etiket_zamani(sahne, 0.6)
        t += [e] if e is not None else []
    elif tip == "foto":
        z = foto_zamanlari(sahne)
        t += [z["oturma"]] + ([z["etiket"]] if z["etiket_metni"] else [])
    elif tip == "manset":
        t += manset_zamanlari(sahne)
        e = etiket_zamani(sahne, 0.7)
        t += [e] if e is not None else []
    elif tip == "harita":
        u, v = harita_zamanlari(sahne)
        t += [x for _, x in u] + ([v[1]] if v else [])
    elif tip == "sayac":
        t += list(sayac_zamanlari(sahne))
    elif tip == "zaman_cizelgesi":
        t += zc_zamanlari(sahne)
    elif tip == "metin":
        z = metin_zamanlari(sahne)
        t += z["kelimeler"][:1] + ([z["ceviri"]] if sahne.p.get("ceviri") else [])
    elif tip == "bolum_karti":
        t += [0.4]
    return sorted(x for x in t if 0 <= x <= max(sahne.sure_hesap, 0.01))


# ================================================================ bağlam ve temel

class Baglam:
    def __init__(self, video: Video, W: int = 1920, H: int = 1080, fps: int = 30):
        self.v, self.W, self.H, self.fps = video, W, H, fps
        self.S = W / 1920


class Cizici:
    def __init__(self, sahne: Sahne, c: Baglam):
        self.sahne, self.c, self.p = sahne, c, sahne.p
        self.W, self.H, self.S = c.W, c.H, c.S
        self.dur = max(sahne.sure_hesap, 1 / c.fps)
        self.hazirla()
        self.katman = UstKatman(sahne, c)

    def hazirla(self):
        pass

    def ciz(self, t: float) -> Image.Image:
        raise NotImplementedError

    def kare(self, t: float) -> Image.Image:
        im = self.ciz(t)
        self.katman.uygula(im, t)
        return im

    def px(self, v: float) -> float:
        return v * self.S


def koyu_zemin(c: Baglam, arka=None, zm: float = 1.06, opak: float = 0.32, ic=(30, 34, 42), dis=(7, 8, 11)):
    """Koyu, hafif ışıklı zemin (zm katı büyüklükte, kamera için); istenirse bulanık bir fotoğrafla."""
    W, H = round(c.W * zm), round(c.H * zm)
    g = C.gradyan_zemin(W, H, ic, dis)
    if arka:
        ph = C.ayarla(C.kapla(C.yukle(arka).convert("RGB"), W, H), bulanik=24 * c.S, karart=0.45, doygunluk=0.5)
        g = Image.blend(g, ph, opak)
    return g


# ================================================================ üst katmanlar

class UstKatman:
    def __init__(self, sahne: Sahne, c: Baglam):
        self.c = c
        S = c.S
        self.isimler = []
        for o in olaylar(sahne, "isim"):
            konum = str(o.p.get("konum", "sol"))
            if o.p.get("karakter") is not None:   # adı verilen karakterin tarafına
                for c_ in sahne.p.get("karakterler", []):
                    if c_["id"] == str(o.p["karakter"]):
                        cx = float(c_["x"]) if c_.get("x") is not None else {"sol": 0.25, "sag": 0.75, "orta": 0.5}[c_["taraf"]]
                        konum = "sag" if cx > 0.5 else "sol"
            self.isimler.append((o.zaman, float(o.p.get("sure", 4.2)), self._isim(o.p["ad"], o.p.get("unvan")), konum))
        self.vurgular = []
        for o in olaylar(sahne, "kelime"):
            spr = C.yazi(str(o.p["metin"]), C.FONT_DIALOG, 92 * S, C.BEYAZ, stroke=7 * S, max_w=1500 * S,
                         max_lines=2, align="center", golge=(0, 5 * S, 9 * S, 0.55))
            self.vurgular.append((o.zaman, float(o.p.get("sure", 2.3)), spr, str(o.p.get("konum", "alt"))))

    def _isim(self, ad: str, unvan: str | None) -> Image.Image:
        S = self.c.S
        a = C.yazi(ad, C.FONT_BOLD, 46 * S, C.BEYAZ)
        u = C.yazi(unvan, C.FONT_BOLD, 27 * S, (206, 208, 214)) if unvan else None
        padx, pady, bar = 30 * S, 18 * S, 10 * S
        w = int(max(a.width, u.width if u else 0) + 2 * padx + bar)
        h = int(a.height + (u.height + 10 * S if u else 0) + 2 * pady)
        panel = C.yuvarlak_kutu(w, h, 6 * S, (10, 12, 16, 228))
        ImageDraw.Draw(panel).rectangle((0, 0, int(bar) - 1, h), fill=C.SARI + (255,))
        panel.alpha_composite(a, (int(bar + padx), int(pady)))
        if u:
            panel.alpha_composite(u, (int(bar + padx), int(pady + a.height + 10 * S)))
        spr, _, _ = C.golgeli(panel, 12 * S, 0.45, 0, 6 * S)
        return spr

    def uygula(self, im: Image.Image, t: float) -> None:
        S, W, H = self.c.S, self.c.W, self.c.H
        for t0, sure, spr, konum in self.isimler:
            u = t - t0
            if u < 0 or u > sure + 0.4:
                continue
            x_dur = 64 * S if konum == "sol" else W - 64 * S - spr.width
            git = (spr.width + x_dur + 20 * S) if konum == "sol" else -(W - x_dur + 20 * S)
            x = x_dur - (1 - E.out_cubic(u / 0.5)) * git - E.in_cubic((u - sure) / 0.38) * git
            C.bindir(im, spr, x, H - 92 * S - spr.height)
        for t0, sure, spr, konum in self.vurgular:
            u = t - t0
            if u < 0 or u > sure + 0.3:
                continue
            s = 0.6 + 0.4 * E.out_back(u / 0.26, 1.6)
            a = min(1.0, u / 0.08) * (1 - E.lineer((u - sure) / 0.3))
            cy = {"ust": 0.17, "orta": 0.5, "alt": 0.80}.get(konum, 0.80) * H
            if s != 1.0:
                spr2, x0, y0 = C.afin(spr, W / 2, cy, s, s)
                C.bindir(im, spr2, x0, y0, a)
            else:
                C.bindir(im, spr, W / 2 - spr.width / 2, cy - spr.height / 2, a)


# ================================================================ daktilo etiketi (yer / tarih / kaynak)

class DaktiloEtiket:
    """Sol altta, harf harf yazılan yer-tarih etiketi (koyu kutu, sarı çizgi, yanıp sönen imleç)."""
    HIZ = 20.0   # harf / sn

    def __init__(self, metin, c: Baglam, ol: list, varsayilan: float, kalis: float | None = 3.5):
        self.metin = str(metin) if metin else ""
        self.c = c
        self.t0 = ol[0].zaman if ol else varsayilan
        # yazı bittikten sonra kalma süresi (None: sahne sonuna kadar)
        self.bitis = None if kalis is None else self.t0 + len(self.metin) / self.HIZ + kalis
        self.f = C.font(C.FONT_MONO, 34 * c.S)
        self._cache: dict[int, Image.Image] = {}

    def _spr(self, n: int, imlec: bool) -> Image.Image:
        key = n * 2 + int(imlec)
        if key in self._cache:
            return self._cache[key]
        S, f = self.c.S, self.f
        asc, desc = f.getmetrics()
        padx, pady = 22 * S, 13 * S
        w, h = int(f.getlength(self.metin) + 2 * padx + 26 * S), int(asc + desc + 2 * pady)
        lay = C.yuvarlak_kutu(w, h, 4 * S, (8, 9, 12, 205))
        d = ImageDraw.Draw(lay)
        d.rectangle((0, 0, int(6 * S), h), fill=C.SARI + (255,))
        d.text((padx + 6 * S, pady), self.metin[:n], font=f, fill=(240, 238, 230, 255))
        if imlec:
            x = padx + 6 * S + f.getlength(self.metin[:n]) + 3 * S
            d.rectangle((x, pady + 4 * S, x + 15 * S, pady + asc + desc - 6 * S), fill=(240, 238, 230, 255))
        self._cache[key] = lay
        return lay

    def ciz(self, im: Image.Image, t: float) -> None:
        if not self.metin or t < self.t0 - 0.15 or (self.bitis is not None and t > self.bitis + 0.3):
            return
        S, H = self.c.S, self.c.H
        u = t - self.t0
        n = max(0, min(len(self.metin), int(u * self.HIZ) + 1)) if u >= 0 else 0
        imlec = (n < len(self.metin)) or (int(t * 2.2) % 2 == 0)
        spr = self._spr(n, imlec)
        a = E.out_cubic((u + 0.15) / 0.2)
        if self.bitis is not None and t > self.bitis:
            a *= 1 - E.in_cubic((t - self.bitis) / 0.3)
        C.bindir(im, spr, 70 * S - (1 - a) * 30 * S, H - 120 * S - spr.height, a)


# ================================================================ wojak

class Karakter:
    GIRIS = 0.75
    CIKIS = 0.45

    def __init__(self, spec: dict, zam: dict, c: Baglam, sira: int, konus: list[float]):
        S, W, H = c.S, c.W, c.H
        self.c = c
        yollar = [Path(spec["gorsel"])] + [p for _, p in zam["yuz"]]
        ims = [C.yukle(p).convert("RGBA") for p in yollar]
        if len({im.size for im in ims}) == 1:
            ims = C.kirp_alfa(ims)
        else:
            ims = [C.kirp_alfa([im])[0] for im in ims]
        taraf = spec.get("taraf", "sol")
        cxn = float(spec["x"]) if spec.get("x") is not None else {"sol": 0.25, "sag": 0.75, "orta": 0.5}[taraf]
        self.taraf = taraf if spec.get("x") is None else ("sol" if cxn < 0.42 else "sag" if cxn > 0.58 else "orta")
        bak = spec.get("bakis")
        faces, bilinen = facing.resolve(yollar[0], bak)
        flip = faces != "front" and facing.needs_flip(faces, cxn)
        if flip:
            ims = [ImageOps.mirror(im) for im in ims]
        boy = float(spec.get("boy", 0.66))
        th = boy * H
        self.ims = []
        for im in ims:
            w = max(1, round(im.width * th / im.height))
            self.ims.append(im.resize((w, round(th)), Image.LANCZOS))
        self.w, self.h = self.ims[0].size
        self.cx = cxn * W
        self.taban = H + float(spec.get("alt", 0.0)) * H + 0.04 * self.h
        self.giris, self.cikis = zam["giris"], zam["cikis"]
        self.yuz_t = [t for t, _ in zam["yuz"]]
        self.konus = konus
        self.faz = 1.7 * sira
        # baş: üst %18'lik bandın yatay merkezi
        a = np.asarray(self.ims[0].getchannel("A"))
        band = a[: max(2, int(self.h * 0.18))] > 60
        xs = np.where(band.any(axis=0))[0]
        self.bas_x = self.cx - self.w / 2 + (xs.mean() if len(xs) else self.w / 2)
        ys = np.where((a > 60).any(axis=1))[0]
        self.ust_y = self.taban - self.h + (ys[0] if len(ys) else 0)
        self.ic_yon = 1 if self.cx < W / 2 else -1   # kadrajın ortasına doğru
        self._onbellek: dict = {}

    def _mesafe(self) -> tuple[float, float]:
        W, H = self.c.W, self.c.H
        if self.taraf == "sol":
            return -(self.cx + self.w / 2 + 40 * self.c.S), 0.0
        if self.taraf == "sag":
            return W - self.cx + self.w / 2 + 40 * self.c.S, 0.0
        return 0.0, H * 0.75

    def gorunur(self, t: float) -> bool:
        if self.giris is not None and t < self.giris:
            return False
        if self.cikis is not None and t > self.cikis + self.CIKIS:
            return False
        return True

    def ciz(self, im: Image.Image, t: float) -> None:
        if not self.gorunur(t):
            return
        S = self.c.S
        mx, my = self._mesafe()
        dx = dy = 0.0
        if self.giris is not None:
            e = E.out_back((t - self.giris) / self.GIRIS, 1.1)
            dx += (1 - e) * mx
            dy += (1 - e) * my
        if self.cikis is not None and t > self.cikis:
            e = E.in_cubic((t - self.cikis) / self.CIKIS)
            dx += e * mx
            dy += e * my
        vi = sum(1 for ts in self.yuz_t if t >= ts)
        sx = sy = 1 + 0.01 * math.sin(2 * math.pi * 0.3 * t + self.faz)
        for ts in self.yuz_t:
            b = E.tumsek((t - ts + 0.13) / 0.26)
            if b:
                sy *= 1 - 0.075 * b
                sx *= 1 + 0.05 * b
        for tb in self.konus:
            b = E.tumsek((t - tb) / 0.32)
            if b:
                dy -= 9 * S * b
                sy *= 1 + 0.012 * b
        dy += 3 * S * math.sin(2 * math.pi * 0.21 * t + self.faz * 0.6)
        src = self.ims[vi]
        # ölçek 0.001 adımla nicemlenir ve önbelleğe alınır (nefes ±%1 = ~20 sprite; her karede yeniden
        # örneklemekten ~10 kat hızlı); 713 px boyda bir adım < 1 px, göz fark etmez
        key = (vi, round(sx * 1000), round(sy * 1000))
        spr = self._onbellek.get(key)
        if spr is None:
            w, h = max(1, round(src.width * key[1] / 1000)), max(1, round(src.height * key[2] / 1000))
            spr = src if (w, h) == src.size else src.resize((w, h), Image.BILINEAR)
            if len(self._onbellek) > 48:
                self._onbellek.pop(next(iter(self._onbellek)))
            self._onbellek[key] = spr
        C.bindir(im, spr, self.cx + dx - spr.width / 2, self.taban + dy - spr.height)


class Balon:
    """Konuşma balonu: yuvarlak, kuyruğu konuşana dönük, açılırken 'pop'."""

    def __init__(self, metin: str, k: Karakter, t0: float, sure: float, c: Baglam):
        S, W = c.S, c.W
        self.t0, self.sure, self.c = t0, sure, c
        yz = C.yazi(metin, C.FONT_DIALOG, 46 * S, (0, 0, 0), max_w=560 * S, max_lines=3, align="center",
                    satir=1.1)
        padx, pady = 36 * S, 24 * S
        bw, bh = int(yz.width + 2 * padx), int(yz.height + 2 * pady)
        kuyruk = 46 * S
        sw = 4.5 * S
        # uç (dünya koordinatı): konuşanın başının üstü, biraz içeri
        ux = k.bas_x + k.ic_yon * 0.10 * k.w
        uy = k.ust_y - 8 * S
        # balon dikdörtgeni: kuyruk tabanı balonun dış tarafına yakın
        rx0 = ux - (0.25 * bw if k.ic_yon > 0 else 0.75 * bw)
        rx0 = min(max(rx0, 40 * S), W - 40 * S - bw)
        ry0 = uy - kuyruk - bh
        if ry0 < 30 * S:
            ry0 = 30 * S
            uy = ry0 + bh + kuyruk
        # sprite (kenar payı = kontur)
        pad = int(sw * 2) + 2
        ss = 3
        SW_, SH_ = int(bw + 2 * pad), int(bh + kuyruk + 2 * pad)
        lay = Image.new("RGBA", (SW_ * ss, SH_ * ss), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        r = min(bh / 2, 38 * S)
        tbx = min(max(ux - rx0, r + 22 * S), bw - r - 22 * S)   # kuyruk tabanı (dikdörtgen içi x)
        tipx = ux - rx0
        tri = [(pad + tbx - 20 * S, pad + bh - 2 * S), (pad + tbx + 20 * S, pad + bh - 2 * S), (pad + tipx, pad + bh + kuyruk)]
        sc = lambda pts: [(x * ss, y * ss) for x, y in pts]
        siyah, beyaz = (0, 0, 0, 255), (255, 255, 255, 255)
        d.rounded_rectangle(((pad - sw) * ss, (pad - sw) * ss, (pad + bw + sw) * ss, (pad + bh + sw) * ss),
                            radius=int((r + sw) * ss), fill=siyah)
        d.polygon(sc(tri), fill=siyah, outline=siyah, width=int(sw * 2 * ss))
        d.rounded_rectangle((pad * ss, pad * ss, (pad + bw) * ss, (pad + bh) * ss), radius=int(r * ss), fill=beyaz)
        d.polygon(sc(tri), fill=beyaz)
        lay = lay.resize((SW_, SH_), Image.LANCZOS)
        lay.alpha_composite(yz, (int(pad + padx), int(pad + pady)))
        self.spr = lay
        self.ax, self.ay = pad + tipx, pad + bh + kuyruk     # sprite içindeki uç
        self.ux, self.uy = rx0 + tipx, ry0 + bh + kuyruk    # çerçevedeki uç

    def ciz(self, im: Image.Image, t: float) -> None:
        u = t - self.t0
        if u < 0 or u > self.sure + 0.16:
            return
        s = 0.3 + 0.7 * E.out_back(u / 0.24, 1.7)
        a = min(1.0, u / 0.06)
        if u > self.sure:
            q = (u - self.sure) / 0.16
            s *= 1 - 0.25 * q
            a *= 1 - q
        if abs(s - 1) < 1e-3:
            C.bindir(im, self.spr, self.ux - self.ax, self.uy - self.ay, a)
        else:
            spr, x0, y0 = C.afin(self.spr, self.ux, self.uy, s, s, 0, self.ax, self.ay)
            C.bindir(im, spr, x0, y0, a)


class WojakCizici(Cizici):
    def hazirla(self):
        p, S, W, H = self.p, self.S, self.W, self.H
        kam = p.get("kamera") or {}
        z = kam.get("zoom", [1.0, 1.07])
        z = [1.0, float(z)] if isinstance(z, (int, float)) else [float(z[0]), float(z[1])]
        m = kam.get("merkez", [[0.5, 0.5], [0.5, 0.46]])
        m = [m, m] if isinstance(m[0], (int, float)) else m
        self.z, self.m = z, [tuple(map(float, m[0])), tuple(map(float, m[1]))]
        zm = max(z) + 0.01
        bg = C.yukle(p["arka"]).convert("RGB")
        if p.get("kirp"):   # [x0, y0, x1, y1] (0..1): fotoğrafın istenmeyen kenarını at
            k = [float(v) for v in p["kirp"]]
            bg = bg.crop((round(k[0] * bg.width), round(k[1] * bg.height), round(k[2] * bg.width),
                          round(k[3] * bg.height)))
        bg = C.kapla(bg, round(W * zm), round(H * zm), tuple(p.get("odak", (0.5, 0.5))))
        self.bg = C.ayarla(bg, bulanik=float(p.get("bulanik", 1.6)) * S, karart=float(p.get("karart", 0.12)),
                           doygunluk=float(p.get("doygunluk", 0.85)))
        C.vinyet_uygula(self.bg, 0.42)   # kaynağa bir kez (her karede maske bindirmek pahalı)
        self.etiket = DaktiloEtiket(self.p.get("etiket"), self.c, olaylar(self.sahne, "etiket"), 0.6)
        zam = karakter_zamanlari(self.sahne)
        bal = balon_olaylari(self.sahne)
        self.karakterler = []
        kmap = {}
        for i, cs in enumerate(p.get("karakterler", [])):
            konus = [o.zaman for o in bal if o.p["karakter"] == cs["id"]]
            k = Karakter(cs, zam[cs["id"]], self.c, i, konus)
            self.karakterler.append(k)
            kmap[cs["id"]] = k
        self.balonlar = []
        for i, o in enumerate(bal):
            sure = float(o.p.get("sure") or 2.5)
            sonraki = [x.zaman for x in bal[i + 1:] if x.p["karakter"] == o.p["karakter"]]
            if sonraki:
                sure = min(sure, sonraki[0] - o.zaman - 0.05)
            self.balonlar.append(Balon(str(o.p["metin"]), kmap[o.p["karakter"]], o.zaman, sure, self.c))

    def ciz(self, t):
        u = E.in_out_sine(t / self.dur)
        z = E.karistir(self.z[0], self.z[1], u)
        m = (E.karistir(self.m[0][0], self.m[1][0], u), E.karistir(self.m[0][1], self.m[1][1], u))
        im = C.kamera(self.bg, self.W, self.H, z, m)
        for k in self.karakterler:
            k.ciz(im, t)
        for b in self.balonlar:
            b.ciz(im, t)
        self.etiket.ciz(im, t)
        return im


# ================================================================ foto

class FotoCizici(Cizici):
    def hazirla(self):
        p, S, W, H = self.p, self.S, self.W, self.H
        foto = C.yukle(p["gorsel"]).convert("RGB")
        arka = C.yukle(p["arka"]).convert("RGB") if p.get("arka") else foto
        self.arka = C.ayarla(C.kapla(arka, round(W * 1.1), round(H * 1.1)), bulanik=26 * S, karart=0.62,
                             doygunluk=0.55)
        boy = float(p.get("boy", 0.72))
        kenar = max(12 * S, min(28 * S, 0.026 * min(W * 0.78, H * boy)))
        ph = C.sigdir(foto, W * 0.78 - 2 * kenar, H * boy - 2 * kenar)
        b = int(round(kenar))
        pr = Image.new("RGBA", (ph.width + 2 * b, ph.height + 2 * b), (247, 245, 238, 255))
        pr.paste(ph, (b, b))
        ImageDraw.Draw(pr).rectangle((0, 0, pr.width - 1, pr.height - 1), outline=(214, 210, 200, 255),
                                     width=max(1, int(S)))
        self.spr, ox, oy = C.golgeli(pr, 22 * S, 0.62, 9 * S, 16 * S)
        self.ax, self.ay = ox + pr.width / 2, oy + pr.height / 2
        self.egim = float(p.get("egim", -2.2))
        self.giris = str(p.get("giris", "alt"))
        z = p.get("zoom", 1.05)
        self.zoom = float(z[1] if isinstance(z, list) else z)
        self.z = foto_zamanlari(self.sahne)
        self.etiket = DaktiloEtiket(p.get("etiket"), self.c, olaylar(self.sahne, "etiket"), self.z["etiket"], None)
        self.atif = C.yazi(str(p["atif"]), C.FONT_BOLD, 19 * S, (230, 230, 230)) if p.get("atif") else None

    def ciz(self, t):
        W, H, S = self.W, self.H, self.S
        im = C.kamera(self.arka, W, H, 1.0 + 0.06 * E.in_out_sine(t / self.dur), (0.5, 0.5))
        u = (t - self.z["inis"]) / 0.72
        e = E.out_back(u, 1.0)
        cx, cy = W / 2, H * 0.455
        yon = {"alt": (0, 1), "ust": (0, -1), "sag": (1, 0), "sol": (-1, 0)}.get(self.giris, (0, 1))
        cx += (1 - e) * yon[0] * W * 0.9
        cy += (1 - e) * yon[1] * H * 0.95
        aci = self.egim + (1 - E.out_cubic(u)) * (7.0 if yon[0] >= 0 else -7.0)
        s = (1.0 + 0.07 * (1 - E.out_cubic(u))) * (1 + (self.zoom - 1) * E.in_out_sine(t / self.dur))
        if u > 0:
            spr, x0, y0 = C.afin(self.spr, cx, cy, s, s, aci, self.ax, self.ay)
            C.bindir(im, spr, x0, y0)
        self.etiket.ciz(im, t)
        if self.atif is not None:
            C.bindir(im, self.atif, W - 70 * S - self.atif.width, H - 82 * S - self.atif.height, 0.65)
        return im


# ================================================================ manşet / belge

class MansetCizici(Cizici):
    def hazirla(self):
        p, S, W, H = self.p, self.S, self.W, self.H
        doc = C.yukle(p["gorsel"]).convert("RGB")
        z = p.get("zoom", 1.18)
        self.zson = float(z[1] if isinstance(z, list) else z)
        zm = max(self.zson, 1.0) + 0.02
        BW, BH = round(W * zm), round(H * zm)
        arka = C.yukle(p["arka"]).convert("RGB") if p.get("arka") else doc
        page = C.ayarla(C.kapla(arka, BW, BH), bulanik=30 * S, karart=0.78, doygunluk=0.4)
        boy = float(p.get("boy", 0.80))
        d = C.sigdir(doc, BW * 0.84, BH * boy)
        dl = d.convert("RGBA")
        spr, ox, oy = C.golgeli(dl, 26 * S, 0.7, 0, 14 * S)
        x0, y0 = (BW - d.width) // 2, (BH - d.height) // 2
        C.bindir(page, spr, x0 - ox, y0 - oy)
        C.vinyet_uygula(page, 0.3)
        self.page = page
        self.etiket = DaktiloEtiket(p.get("etiket"), self.c, olaylar(self.sahne, "etiket"), 0.7)
        self.BW, self.BH = BW, BH
        renk = tuple(p.get("renk", (255, 221, 40)))
        self.renk = np.array(renk, np.float32) / 255.0
        self.kutular = []
        for k in p.get("kutular") or []:
            k = [float(v) for v in k]
            if max(k) <= 1.0:
                bx = [k[0] * d.width, k[1] * d.height, k[2] * d.width, k[3] * d.height]
            else:
                r = d.width / doc.width
                bx = [v * r for v in k]
            padx, pady = 6 * S, 0.12 * (bx[3] - bx[1])
            bx = [x0 + bx[0] - padx, y0 + bx[1] - pady, x0 + bx[2] + padx, y0 + bx[3] + pady]
            bx = [int(round(v)) for v in bx]
            self.kutular.append((bx, self._kalem_maske(bx[2] - bx[0], bx[3] - bx[1], len(self.kutular))))
        self.ts = manset_zamanlari(self.sahne)
        # kamera: sırayla her kutunun merkezine doğru kayar (kalem nereden geçiyorsa oraya)
        self.hedefler = [((b[0] + b[2]) / 2 / BW, (b[1] + b[3]) / 2 / BH) for b, _ in self.kutular]

    def _kalem_maske(self, w: int, h: int, seed: int) -> np.ndarray:
        """Fosforlu kalem izi: uçları yuvarlak, kenarları hafif düzensiz, içi hafif dokulu (0..1)."""
        rng = np.random.default_rng(100 + seed)
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        ust = 0.06 * h + rng.normal(0, 0.015 * h, w).cumsum() * 0.05
        alt = 0.94 * h + rng.normal(0, 0.015 * h, w).cumsum() * 0.05
        m = ((yy >= ust[None, :]) & (yy <= alt[None, :])).astype(np.float32)
        r = h / 2
        for cx in (r, w - r):  # yuvarlak uçlar
            dx = np.abs(xx - cx)
            out = (dx > 0) & (((xx < r) & (cx == r)) | ((xx > w - r) & (cx == w - r)))
            m[out & (((xx - cx) ** 2 + (yy - r) ** 2) > r * r)] = 0
        doku = 0.86 + 0.1 * rng.random((1, w)).astype(np.float32).repeat(h, 0)
        return np.clip(m * doku, 0, 1)

    def ciz(self, t):
        pg = self.page.copy()
        for (bx, mask), t0 in zip(self.kutular, self.ts):
            pr = E.in_out_cubic((t - t0) / 0.6)
            if pr <= 0:
                continue
            w = bx[2] - bx[0]
            n = max(1, int(round(w * pr)))
            reg = (bx[0], bx[1], bx[0] + n, bx[3])
            a = np.asarray(pg.crop(reg), np.float32) / 255.0
            mk = mask[:, :n, None] * 0.82
            out = a * (1 - mk * (1 - self.renk[None, None, :]))
            pg.paste(Image.fromarray((out * 255).astype(np.uint8), "RGB"), reg[:2])
        u = E.in_out_sine(t / self.dur)
        m = (0.5, 0.5)
        for (hx, hy), t0 in zip(self.hedefler, self.ts):
            k = E.in_out_sine((t - t0 + 0.5) / 1.4)
            if k > 0:   # yalnız dikeyde izle: yatayda kaydırmak satırın öbür ucunu kadraj dışında bırakıyor
                m = (0.5, E.karistir(m[1], E.karistir(0.5, hy, 0.8), k))
        im = C.kamera(pg, self.W, self.H, 1.0 + (self.zson - 1.0) * u, m)
        self.etiket.ciz(im, t)
        return im


# ================================================================ harita

class HaritaCizici(Cizici):
    def hazirla(self):
        from .harita import BOLGELER, HaritaCizer
        p, S, W, H = self.p, self.S, self.W, self.H
        bolge = p.get("bolge", "avrupa")
        if isinstance(bolge, str) and bolge not in BOLGELER:
            raise ValueError(f"{self.sahne.yer}: bölge '{bolge}' yok ({', '.join(BOLGELER)}) ya da sözlük ver")
        r = p.get("cozunurluk") or ("110m" if bolge == "dunya" else "50m")
        z = p.get("zoom", [1.0, 1.06])
        self.z = [1.0, float(z)] if isinstance(z, (int, float)) else [float(z[0]), float(z[1])]
        zm = max(self.z) + 0.01
        BW, BH = round(W * zm), round(H * zm)
        self.BW, self.BH = BW, BH
        hc = HaritaCizer(bolge, BW, BH, r)
        self.taban = hc.taban()
        C.vinyet_uygula(self.taban, 0.38)
        renk = tuple(p.get("renk", (205, 62, 52)))
        self.renk = renk
        self.parlak = tuple(min(255, int(v * 1.35 + 40)) for v in renk)
        zam, vz = harita_zamanlari(self.sahne)
        etk = p.get("etiketler", False)
        self.ulkeler = []
        for kod, t0 in zam:
            mk = hc.maske(kod)
            if mk is None:
                continue
            mask, bbox = mk
            glow = self._parilti(mask, bbox, 14 * S)
            lab = None
            if etk is True or (isinstance(etk, list) and kod in [str(x) for x in etk]):
                pt = hc.etiket_noktasi(kod)
                if pt:
                    lab = (pt, C.yazi(hc.ulkeler[kod].ad_tr, C.FONT_BOLD, 25 * S, C.BEYAZ, stroke=3 * S,
                                      stroke_fill=(10, 12, 16)))
            self.ulkeler.append((kod, t0, mask, bbox, glow, lab))
        self.vurgu = None
        mrk = (0.5, 0.5)
        if vz:
            v = p["vurgu"] if isinstance(p["vurgu"], dict) else {"kod": vz[0]}
            mk = hc.maske(vz[0])
            if mk:
                mask, bbox = mk
                vr = tuple(v.get("renk", C.YESIL))
                halka = self._halka(mask, bbox, 5 * S)
                pt = hc.etiket_noktasi(vz[0]) or ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)
                ad = C.buyuk(str(v.get("ad", hc.ulkeler[vz[0]].ad_tr)))
                kutu = self._cagri(ad, v.get("etiket"), vr)
                self.vurgu = (vz[1], mask, bbox, vr, halka, pt, kutu)
                mrk = (E.karistir(0.5, pt[0] / BW, 0.35), E.karistir(0.5, pt[1] / BH, 0.35))
        self.merkez = mrk
        self.baslik = None
        if p.get("baslik"):
            self.baslik = C.yazi(str(p["baslik"]), C.FONT_DIALOG, 54 * S, C.BEYAZ, max_w=1100 * S, max_lines=2,
                                 golge=(0, 3 * S, 6 * S, 0.6))
        self.aciklama = None
        if p.get("aciklama"):
            yz = C.yazi(str(p["aciklama"]), C.FONT_BOLD, 26 * S, (226, 228, 232))
            sq = int(22 * S)
            w, h = int(sq + 14 * S + yz.width + 36 * S), int(max(sq, yz.height) + 24 * S)
            lay = C.yuvarlak_kutu(w, h, 5 * S, (8, 10, 14, 200))
            ImageDraw.Draw(lay).rectangle((int(18 * S), (h - sq) // 2, int(18 * S) + sq, (h - sq) // 2 + sq),
                                          fill=renk + (255,))
            lay.alpha_composite(yz, (int(18 * S + sq + 14 * S), (h - yz.height) // 2))
            self.aciklama = lay

    def _parilti(self, mask, bbox, r):
        pad = int(r * 3)
        m = Image.new("L", (mask.width + 2 * pad, mask.height + 2 * pad), 0)
        m.paste(mask, (pad, pad))
        return m.filter(ImageFilter.GaussianBlur(r)), (bbox[0] - pad, bbox[1] - pad)

    def _halka(self, mask, bbox, kal):
        pad = int(kal * 4)
        m = Image.new("L", (mask.width + 2 * pad, mask.height + 2 * pad), 0)
        m.paste(mask, (pad, pad))
        big = m.filter(ImageFilter.MaxFilter(int(kal) * 2 + 1)).filter(ImageFilter.GaussianBlur(kal * 0.6))
        halka = ImageChops.subtract(big, m)
        return halka, (bbox[0] - pad, bbox[1] - pad)

    def _cagri(self, ad: str, etiket, renk) -> Image.Image:
        S = self.S
        a = C.yazi(ad, C.FONT_BOLD, 34 * S, (10, 14, 12), aralik=0.06)
        b = C.yazi(str(etiket), C.FONT_DIALOG, 36 * S, (10, 14, 12)) if etiket else None
        padx, pady = 22 * S, 14 * S
        w = int(max(a.width, b.width if b else 0) + 2 * padx)
        h = int(a.height + (b.height + 6 * S if b else 0) + 2 * pady)
        lay = C.yuvarlak_kutu(w, h, 8 * S, tuple(renk) + (250,))
        lay.alpha_composite(a, (int(padx), int(pady)))
        if b:
            lay.alpha_composite(b, (int(padx), int(pady + a.height + 6 * S)))
        spr, _, _ = C.golgeli(lay, 14 * S, 0.55, 0, 6 * S)
        return spr

    @staticmethod
    def _renk_bas(dst, renk, xy, mask, a):
        if a <= 0.003:
            return
        m = mask if a >= 0.997 else mask.point(C._alfa_lut(int(a * 255)))
        x, y = int(xy[0]), int(xy[1])
        l, t_ = max(0, -x), max(0, -y)
        r, b = min(m.width, dst.width - x), min(m.height, dst.height - y)
        if r <= l or b <= t_:
            return
        if (l, t_, r, b) != (0, 0, m.width, m.height):
            m = m.crop((l, t_, r, b))
        dst.paste(tuple(renk), (x + l, y + t_, x + r, y + b), m)

    def _nokta(self, pt, zoom, merkez):
        sw, sh = self.BW, self.BH
        ww, wh = sw / zoom, sh / zoom
        cx = min(max(merkez[0] * sw, ww / 2), sw - ww / 2)
        cy = min(max(merkez[1] * sh, wh / 2), sh - wh / 2)
        return (pt[0] - (cx - ww / 2)) * self.W / ww, (pt[1] - (cy - wh / 2)) * self.H / wh

    def ciz(self, t):
        S, W, H = self.S, self.W, self.H
        # animasyonu bitmiş ülkeler bir kez tabana işlenir (zaman sırasıyla çizildiğinde her karede tekrar yok)
        if not hasattr(self, "_statik") or t < self._statik_t:
            self._statik, self._statik_t, self._bitti = self.taban.copy(), 0.0, set()
        for kod, t0, mask, bbox, glow, lab in self.ulkeler:
            if kod not in self._bitti and t - t0 > 1.05:
                self._renk_bas(self._statik, self.renk, bbox[:2], mask, 1.0)
                self._bitti.add(kod)
        self._statik_t = t
        base = self._statik.copy()
        for kod, t0, mask, bbox, glow, lab in self.ulkeler:
            u = t - t0
            if u < 0 or kod in self._bitti:
                continue
            a = E.out_cubic(u / 0.35)
            k = E.out_cubic(u / 0.7)
            renk = tuple(int(E.karistir(pa, ra, k)) for pa, ra in zip(self.parlak, self.renk))
            self._renk_bas(base, renk, bbox[:2], mask, a)
            if u < 1.0:
                gm, gxy = glow
                self._renk_bas(base, self.parlak, gxy, gm, 0.55 * (1 - E.out_cubic(u / 1.0)))
        if self.vurgu:
            t0, mask, bbox, vr, (halka, hxy), pt, kutu = self.vurgu
            u = t - t0
            if u >= 0:
                self._renk_bas(base, vr, bbox[:2], mask, E.out_cubic(u / 0.4))
                nab = 0.55 + 0.45 * math.sin(2 * math.pi * 1.1 * u) if u > 0.4 else E.out_cubic(u / 0.4)
                self._renk_bas(base, (235, 255, 240), hxy, halka, nab)
        uz = E.in_out_sine(t / self.dur)
        zoom = E.karistir(self.z[0], self.z[1], uz)
        im = C.kamera(base, W, H, zoom, self.merkez)
        for kod, t0, mask, bbox, glow, lab in self.ulkeler:
            if lab and t >= t0 + 0.1:
                (px, py), spr = lab
                x, y = self._nokta((px, py), zoom, self.merkez)
                a = E.out_cubic((t - t0 - 0.1) / 0.3)
                C.bindir(im, spr, x - spr.width / 2, y - spr.height / 2 + (1 - a) * 8 * S, a)
        if self.vurgu:
            t0, mask, bbox, vr, _, pt, kutu = self.vurgu
            u = t - t0 - 0.25
            if u >= 0:
                x, y = self._nokta(pt, zoom, self.merkez)
                a = E.out_cubic(u / 0.3)
                bx = min(x + 110 * S, W - kutu.width - 40 * S)
                by = max(y - 150 * S, 140 * S)
                d = ImageDraw.Draw(im)
                lu = E.out_cubic(u / 0.25)
                d.line((x, y, x + (bx + 12 * S - x) * lu, y + (by - y) * lu), fill=(245, 255, 248),
                       width=max(1, int(4 * S)))
                d.ellipse((x - 8 * S, y - 8 * S, x + 8 * S, y + 8 * S), fill=(245, 255, 248))
                s = 0.7 + 0.3 * E.out_back((u - 0.12) / 0.3, 1.5)
                if u > 0.12:
                    spr, x0, y0 = C.afin(kutu, bx, by, s, s, 0, 0, kutu.height * 0.5)
                    C.bindir(im, spr, x0, y0, a)
        a = E.out_cubic(t / 0.5)
        if self.baslik is not None:
            C.bindir(im, self.baslik, 80 * S, 64 * S - (1 - a) * 12 * S, a)
            ImageDraw.Draw(im).rectangle((80 * S, 64 * S + self.baslik.height + 12 * S,
                                          80 * S + 140 * S * E.out_cubic((t - 0.15) / 0.5),
                                          64 * S + self.baslik.height + 18 * S), fill=C.SARI)
        if self.aciklama is not None:
            C.bindir(im, self.aciklama, 80 * S, H - 110 * S - self.aciklama.height, a)
        return im


# ================================================================ sayaç

class SayacCizici(Cizici):
    def hazirla(self):
        p, S = self.p, self.S
        self.zem = koyu_zemin(self.c, p.get("arka"))
        self.yil = p.get("yil")
        self.t0, self.t1 = sayac_zamanlari(self.sahne)
        self.f = C.font(C.FONT_CARD, (300 if self.yil else 270) * S)
        self.hucre = max(self.f.getlength(str(d)) for d in range(10))
        tops, bots = zip(*[(self.f.getbbox(str(d))[1], self.f.getbbox(str(d))[3]) for d in range(10)])
        m = 0.07 * self.f.size
        self.bant = (min(tops) - m, max(bots) + m)          # rakamların görünür bandı (odometre penceresi)
        self.yuk = self.bant[1] - self.bant[0]
        self.onek = str(p.get("onek", ""))
        self.sonek = str(p.get("sonek", "+" if (p.get("deger") and not self.yil) else ""))
        self._rk: dict = {}
        self.etiket = C.yazi(str(p["etiket"]), C.FONT_DIALOG, 76 * S, C.SARI, max_w=1400 * S, max_lines=2,
                             align="center", golge=(0, 4 * S, 8 * S, 0.5)) if p.get("etiket") else None
        self.ust = C.yazi(C.buyuk(str(p["ust"])), C.FONT_BOLD, 32 * S, (196, 200, 208), aralik=0.22) \
            if p.get("ust") else None

    def _w(self, ch: str) -> float:
        return self.hucre if ch.isdigit() else self.f.getlength(ch)

    def _rakam(self, ch: str) -> Image.Image:
        """Tek karakter, rakam bandına kırpılmış (rakamlar sabit genişlikte hücrede ortalı)."""
        if ch not in self._rk:
            w = int(math.ceil(self._w(ch))) + 2
            lay = Image.new("RGBA", (w, int(math.ceil(self.yuk))), (0, 0, 0, 0))
            ImageDraw.Draw(lay).text(((w - self.f.getlength(ch)) / 2, -self.bant[0]), ch, font=self.f,
                                     fill=(255, 255, 255, 255))
            self._rk[ch] = lay
        return self._rk[ch]

    def _say_katmani(self, t: float) -> Image.Image:
        """O anki sayı; ortalı. Yıl modunda değişen basamaklar odometre gibi aşağıdan yukarı döner.
        Sonek ('+') için baştan yer ayrılır: belirdiğinde sayı yerinden kaymaz."""
        S = self.S
        u = (t - self.t0) / max(self.t1 - self.t0, 1e-3)
        if self.yil:
            a, b = int(self.yil[0]), int(self.yil[1])
            v = a + (b - a) * E.kirp(u)
            y0 = int(math.floor(v)) if v < b else b
            frac = E.in_out_cubic(min(1.0, (v - y0) * 1.6)) if y0 < b else 0.0
            s0, s1 = str(y0), str(min(y0 + 1, b))
        else:
            s0 = self.onek + C.say_bicimle(float(self.p["deger"]) * E.out_cubic(u))
            s1, frac = s0, 0.0
        son_w = self.f.getlength(self.sonek) if self.sonek else 0.0
        W = int(sum(self._w(ch) for ch in s0) + son_w) + 4
        Hh = int(math.ceil(self.yuk))
        lay = Image.new("RGBA", (W, Hh), (0, 0, 0, 0))
        x = 0.0
        for c0, c1 in zip(s0, s1):
            if c0 == c1 or frac <= 0:
                lay.alpha_composite(self._rakam(c0), (int(round(x)), 0))
            else:
                off = int(round(frac * Hh))
                hucre = Image.new("RGBA", self._rakam(c0).size, (0, 0, 0, 0))
                hucre.alpha_composite(self._rakam(c0), (0, -off))
                hucre.alpha_composite(self._rakam(c1), (0, Hh - off))
                lay.alpha_composite(hucre, (int(round(x)), 0))
            x += self._w(c0)
        if self.sonek and u >= 1.0:
            a = E.out_cubic((t - self.t1) / 0.25)
            sk = self._rakam(self.sonek)
            if a < 1:
                sk = sk.copy()
                sk.putalpha(sk.getchannel("A").point(C._alfa_lut(int(255 * a))))
            lay.alpha_composite(sk, (int(round(x)), int(-(1 - a) * 20 * S)) if a < 1 else (int(round(x)), 0))
        return lay

    def ciz(self, t):
        S, W, H = self.S, self.W, self.H
        im = C.kamera(self.zem, W, H, 1.0 + 0.05 * E.in_out_sine(t / self.dur), (0.5, 0.5))
        C.gren_uygula(im, t, 0.05)
        lay = self._say_katmani(t)
        bit = (t - self.t1)
        s = 1.0 + 0.06 * E.tumsek(bit / 0.3) if bit >= 0 else 0.94 + 0.06 * E.out_cubic(t / 0.45)
        a = E.out_cubic(t / 0.35)   # sayı sahne başında görünür (0 / başlangıç yılı), t0'da saymaya başlar
        cy = H * (0.45 if self.etiket else 0.5)
        spr, x0, y0 = C.afin(lay, W / 2, cy, s, s, 0)
        C.bindir(im, spr, x0, y0, a)
        if self.ust is not None:
            C.bindir(im, self.ust, W / 2 - self.ust.width / 2, cy - self.yuk / 2 - 40 * S - self.ust.height, a)
        if self.etiket is not None:
            ae = E.out_cubic((t - self.t0 - 0.35) / 0.45)
            C.bindir(im, self.etiket, W / 2 - self.etiket.width / 2, cy + self.yuk / 2 + 52 * S + (1 - ae) * 24 * S, ae)
        # bitişte sayının altında sarı çizgi
        if bit >= 0:
            lw = 260 * S * E.out_cubic(bit / 0.4)
            yl = cy + self.yuk / 2 + 22 * S
            ImageDraw.Draw(im).rectangle((W / 2 - lw, yl, W / 2 + lw, yl + 6 * S), fill=C.SARI)
        return im


# ================================================================ bölüm kartı

class BolumKartiCizici(Cizici):
    def hazirla(self):
        p, S, W, H = self.p, self.S, self.W, self.H
        self.zem = C.gradyan_zemin(W, H, (22, 23, 27), (2, 2, 3), (0.5, 0.5))
        ust = p.get("ust") or (f"BÖLÜM {p['numara']}" if p.get("numara") else "")
        self.ust = C.yazi(C.buyuk(str(ust)), C.FONT_BOLD, 36 * S, C.SARI, aralik=0.32) if ust else None
        self.baslik = C.yazi(str(p["baslik"]), C.FONT_DIALOG, 112 * S, C.BEYAZ, max_w=1500 * S, max_lines=2,
                             align="center", golge=(0, 5 * S, 10 * S, 0.6))

    def ciz(self, t):
        S, W, H = self.S, self.W, self.H
        im = self.zem.copy()
        C.gren_uygula(im, t, 0.07)
        cy = H * 0.5
        # çizgi ortadan dışa
        lw = (self.baslik.width / 2 + 40 * S) * E.out_cubic((t - 0.08) / 0.5)
        if lw > 1:
            ImageDraw.Draw(im).rectangle((W / 2 - lw, cy - 2 * S, W / 2 + lw, cy + 2 * S), fill=C.SARI)
        if self.ust is not None:
            a = E.out_cubic((t - 0.2) / 0.45)
            C.bindir(im, self.ust, W / 2 - self.ust.width / 2, cy - 30 * S - self.ust.height - (1 - a) * 18 * S, a)
        # başlık: soldan sağa silinerek açılır + hafif yükselir
        u = E.out_cubic((t - 0.32) / 0.65)
        if u > 0:
            b = self.baslik
            n = max(1, int(b.width * u))
            parca = b.crop((0, 0, n, b.height))
            C.bindir(im, parca, W / 2 - b.width / 2, cy + 26 * S + (1 - u) * 16 * S, min(1.0, u * 1.6))
        return im


# ================================================================ metin / alıntı

class MetinCizici(Cizici):
    def hazirla(self):
        p, S, W = self.p, self.S, self.W
        self.zem = koyu_zemin(self.c, p.get("arka"), ic=(38, 32, 30), dis=(9, 8, 8))
        self.f = C.font(C.FONT_DIALOG, 124 * S)
        metin = str(p["metin"])
        # kelime kelime yerleşim (en fazla 2 satır, ortalı)
        f = self.f
        maxw = 1560 * S
        while True:
            kel = metin.split()
            satirlar, cur = [], []
            for k in kel:
                if cur and f.getlength(" ".join(cur + [k])) > maxw:
                    satirlar.append(cur)
                    cur = [k]
                else:
                    cur.append(k)
            satirlar.append(cur)
            if len(satirlar) <= 3 or f.size < 60 * S:
                break
            f = C.font(C.FONT_DIALOG, f.size - 8)
        self.f = f
        asc, desc = f.getmetrics()
        lh = f.size * 1.12
        self.kelimeler = []
        top = -(len(satirlar) - 1) * lh / 2
        for si, s in enumerate(satirlar):
            sw = f.getlength(" ".join(s))
            x = -sw / 2
            for k in s:
                spr = C.yazi(k, C.FONT_DIALOG, f.size, C.BEYAZ, golge=(0, 5 * S, 10 * S, 0.55))
                self.kelimeler.append((spr, x, top + si * lh))
                x += f.getlength(k + " ")
        self.blok_h = len(satirlar) * lh
        self.z = metin_zamanlari(self.sahne)
        self.ceviri = C.yazi(str(p["ceviri"]), C.FONT_DIALOG, 84 * S, C.SARI, max_w=1500 * S, max_lines=2,
                             align="center", golge=(0, 4 * S, 8 * S, 0.5)) if p.get("ceviri") else None
        self.ust = C.yazi(C.buyuk(str(p["ust"])), C.FONT_BOLD, 30 * S, (190, 186, 180), aralik=0.22) \
            if p.get("ust") else None
        self.alt = C.yazi(str(p["alt"]), C.FONT_BOLD, 24 * S, (170, 166, 160)) if p.get("alt") else None
        self.tirnak = C.yazi("“", C.FONT_DIALOG, 420 * S, (255, 255, 255))

    def ciz(self, t):
        S, W, H = self.S, self.W, self.H
        im = C.kamera(self.zem, W, H, 1.0 + 0.05 * E.in_out_sine(t / self.dur), (0.5, 0.45))
        C.gren_uygula(im, t, 0.05)
        cy = H * (0.42 if self.ceviri else 0.5)
        C.bindir(im, self.tirnak, W / 2 - self.tirnak.width / 2, cy - self.blok_h / 2 - self.tirnak.height * 0.62,
                 0.07 * E.out_cubic(t / 0.6))
        if self.ust is not None:
            a = E.out_cubic(t / 0.45)
            C.bindir(im, self.ust, W / 2 - self.ust.width / 2, cy - self.blok_h / 2 - 40 * S - self.ust.height, a)
        for (spr, x, y), tk in zip(self.kelimeler, self.z["kelimeler"]):
            u = (t - tk) / 0.32
            if u <= 0:
                continue
            a = E.out_cubic(u)
            C.bindir(im, spr, W / 2 + x, cy + y - spr.height * 0.42 + (1 - a) * 26 * S, a)
        if self.ceviri is not None:
            u = (t - self.z["ceviri"]) / 0.45
            if u > 0:
                a = E.out_cubic(u)
                y = cy + self.blok_h / 2 + 60 * S
                cw = self.ceviri.width
                # altında fosforlu şerit
                lw = cw * E.in_out_cubic((t - self.z["ceviri"] - 0.2) / 0.5)
                if lw > 1:
                    ImageDraw.Draw(im).rectangle((W / 2 - cw / 2, y + self.ceviri.height - 4 * S,
                                                  W / 2 - cw / 2 + lw, y + self.ceviri.height + 6 * S), fill=C.SARI)
                C.bindir(im, self.ceviri, W / 2 - cw / 2, y + (1 - a) * 22 * S, a)
        if self.alt is not None:
            C.bindir(im, self.alt, W / 2 - self.alt.width / 2, H - 140 * S, 0.8 * E.out_cubic((t - 0.5) / 0.5))
        return im


# ================================================================ zaman çizelgesi

class ZamanCizelgesiCizici(Cizici):
    def hazirla(self):
        p, S, W, H = self.p, self.S, self.W, self.H
        self.zem = koyu_zemin(self.c, p.get("arka"))
        self.noktalar = p["noktalar"]
        n = len(self.noktalar)
        self.x0, self.x1 = 150 * S, W - 150 * S
        self.y = H * 0.53
        aralik = (self.x1 - self.x0) / n
        self.xs = [self.x0 + aralik * (i + 0.5) for i in range(n)]
        self.ts = zc_zamanlari(self.sahne)
        self.spr = []
        for nk in self.noktalar:
            tarih = C.yazi(str(nk["tarih"]), C.FONT_CARD, 66 * S, C.SARI, max_w=aralik - 20 * S, max_lines=2,
                           align="center", golge=(0, 3 * S, 6 * S, 0.5))
            yz = C.yazi(str(nk.get("metin", "")), C.FONT_BOLD, 36 * S, C.BEYAZ, max_w=aralik - 30 * S,
                        max_lines=3, align="center", satir=1.18, golge=(0, 3 * S, 6 * S, 0.5)) if nk.get("metin") else None
            self.spr.append((tarih, yz))
        self.baslik = C.yazi(str(p["baslik"]), C.FONT_DIALOG, 58 * S, C.BEYAZ, max_w=1500 * S, max_lines=1,
                             golge=(0, 3 * S, 6 * S, 0.6)) if p.get("baslik") else None
        self.cizgi_t = max(0.1, self.ts[0] - 0.6) if self.ts else 0.1

    def ciz(self, t):
        S, W, H = self.S, self.W, self.H
        im = C.kamera(self.zem, W, H, 1.0 + 0.04 * E.in_out_sine(t / self.dur), (0.45, 0.5))
        C.gren_uygula(im, t, 0.04)
        d = ImageDraw.Draw(im)
        # eksen
        lw = (self.x1 - self.x0) * E.in_out_cubic((t - self.cizgi_t) / 0.7)
        if lw > 0:
            d.rectangle((self.x0, self.y - 2 * S, self.x0 + lw, self.y + 2 * S), fill=(110, 116, 128))
        # ilerleme (sarı) çizgisi son beliren noktaya kadar
        gorunen = [i for i, tt in enumerate(self.ts) if t >= tt]
        if gorunen:
            i = gorunen[-1]
            tt = self.ts[i]
            xp0 = self.xs[i - 1] if i > 0 else self.x0
            xp = E.karistir(xp0, self.xs[i], E.out_cubic((t - tt) / 0.45))
            d.rectangle((self.x0, self.y - 3 * S, xp, self.y + 3 * S), fill=C.SARI)
        son = gorunen[-1] if gorunen else -1
        for i, (x, tt, (tarih, yz)) in enumerate(zip(self.xs, self.ts, self.spr)):
            u = t - tt
            if u < 0:
                continue
            aktif = i == son
            kis = 1.0 if aktif else 0.62
            r = 18 * S * (0.4 + 0.6 * E.out_back(u / 0.3, 2.0)) * (1.15 if aktif else 1.0)
            if aktif:
                rr = r + 10 * S * (0.5 + 0.5 * math.sin(2 * math.pi * 1.0 * u))
                d.ellipse((x - rr, self.y - rr, x + rr, self.y + rr), outline=C.SARI, width=max(1, int(3 * S)))
            d.ellipse((x - r, self.y - r, x + r, self.y + r), fill=C.BEYAZ if aktif else (170, 172, 178),
                      outline=C.SARI, width=max(1, int(4 * S)))
            a = E.out_cubic(u / 0.4) * kis
            C.bindir(im, tarih, x - tarih.width / 2, self.y - 44 * S - tarih.height - (1 - E.out_cubic(u / 0.4)) * 14 * S, a)
            if yz is not None:
                C.bindir(im, yz, x - yz.width / 2, self.y + 46 * S + (1 - E.out_cubic(u / 0.4)) * 14 * S, a)
        if self.baslik is not None:
            a = E.out_cubic(t / 0.5)
            C.bindir(im, self.baslik, 80 * S, 64 * S - (1 - a) * 12 * S, a)
            d.rectangle((80 * S, 64 * S + self.baslik.height + 12 * S, 80 * S + 140 * S * E.out_cubic((t - 0.15) / 0.5),
                         64 * S + self.baslik.height + 18 * S), fill=C.SARI)
        return im


CIZICILER = {"wojak": WojakCizici, "foto": FotoCizici, "manset": MansetCizici, "harita": HaritaCizici,
             "sayac": SayacCizici, "bolum_karti": BolumKartiCizici, "metin": MetinCizici,
             "zaman_cizelgesi": ZamanCizelgesiCizici}


def cizici(sahne: Sahne, c: Baglam) -> Cizici:
    return CIZICILER[sahne.tip](sahne, c)


# ================================================================ filigran

def filigran_katmani(metin: str, c: Baglam) -> tuple[Image.Image, int, int]:
    from .. import config, text as wtext
    S = c.S
    lay = wtext.text_block(metin, font_path=config.FONT_DIALOG, size=max(10, round(34 * S)), max_w=round(600 * S),
                           max_lines=1, stroke_ratio=0.09, pitch=1.1, shadow=False, shear=config.DIALOG_SHEAR)
    bb = lay.getchannel("A").getbbox()
    lay = lay.crop(bb) if bb else lay
    lay.putalpha(lay.getchannel("A").point(C._alfa_lut(int(255 * 0.9))))
    return lay, int(c.W - 34 * S - lay.width), int(c.H - 26 * S - lay.height)
