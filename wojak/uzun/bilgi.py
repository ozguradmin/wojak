"""Bilgi sahneleri (2. tur): bölünmüş ekran, nokta ızgarası, soruşturma panosu.

bolunmus: iki panel yan yana. Sol panel baştan ekranı kaplar; `panel` olayıyla (taraf: sag) sağ panel kayarak
açılır ve ekran ikiye bölünür (`acik: true`: ikisi baştan açık). `soluk` bir paneli karartır, `buyut` bir paneli
büyütüp ekranı kaplatır. Panel: `gorsel` (Ken Burns) ya da `metin` (+ `ceviri`, kendi zemini), `etiket` (sol üst
kutu), `baslik` (üstte büyük), `alt` (küçük not).

izgara: n (vars. 10.000) küçük nokta satır satır dolar (`basla`, `dolum` sn); `sondur` olayı ({oran: 0.4}) rastgele
seçilmiş noktaların o oranını sessizce söndürür (silik iz kalır). `ust` başlık, `etiket` alt yazı, `say: true`
canlı sayı.

pano: mantar pano (kendi dokumuz), kartlar (`kartlar`: id, metin, alt, x, y, stil kagit|merkez|bos|foto, gorsel)
`kart` olayıyla iğnelenir, `ipler` ([a, b]) kırmızı iple bağlanır (`ip` olayı ya da iki kart da asılınca),
`damga` olayı `kart:` ile kartın üstüne basılır. Kamera yavaşça yaklaşır ve son iğnelenen karta kayar.
"""

from __future__ import annotations

import math
import re
from functools import lru_cache

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageEnhance

from . import cizim as C
from . import easing as E
from . import zemin as Z
from .sahneler import Cizici, basla_zamani, olaylar
from .ust import Damga, damga_olaylari


# ================================================================ bölünmüş ekran

def bolunmus_zamanlari(sahne) -> dict:
    """{'ac': {sol, sag}, 'soluk': {...}, 'buyut': {...}, 'ceviri': {...}} — her taraf için ilk olay anı."""
    out = {"ac": {}, "soluk": {}, "buyut": {}, "ceviri": {}}
    adlar = {"panel": "ac", "soluk": "soluk", "buyut": "buyut", "ceviri": "ceviri"}
    for o in sorted(sahne.olaylar, key=lambda o: o.zaman):
        if o.tip in adlar:
            taraf = str(o.p.get("taraf", "sag"))
            out[adlar[o.tip]].setdefault(taraf, o.zaman)
    out["ac"].setdefault("sol", 0.0)
    if sahne.p.get("acik"):
        out["ac"]["sag"] = 0.0
    else:
        out["ac"].setdefault("sag", 1.2)
    for taraf in ("sol", "sag"):   # metin paneli: çeviri vars. açılıştan 1,2 sn sonra
        if sahne.p[taraf].get("ceviri"):
            out["ceviri"].setdefault(taraf, out["ac"][taraf] + 1.2)
    return out


SAYI_RE = re.compile(r"\d{1,3}(?:\.\d{3})+|\d+")


def _hizali_sayi(son: str, deger: int) -> str:
    """deger'i son'un (ör. '1.267') rakam/ayraç düzenine sağdan hizalar; boş rakam hücresi U+2007, boş ayraç
    U+2008 (C.tabular_yazi ikisini de çizmeden genişliğiyle geçer): sayarken satır genişliği sabit kalır."""
    cs = C.say_bicimle(deger)
    out = []
    j = len(cs) - 1
    for ch in reversed(son):
        if j >= 0:
            out.append(cs[j])
            j -= 1
        else:
            out.append("\u2008" if ch == "." else "\u2007")
    return "".join(reversed(out))


class _Panel:
    def __init__(self, d: dict, c, tohum: int):
        S, W, H = c.S, c.W, c.H
        self.c, self.S, self.W, self.H = c, S, W, H
        self.d = d
        self.zm = float(d.get("zoom", 1.06))
        # 9. tur (izlenme S7): metin panelinin kendi itmesi (`zoom`: zemin daha çok yaklaşır, yazı bloğu hafifçe büyür)
        self.metin_zoom = float(d["zoom"]) if (d.get("zoom") and not d.get("gorsel")) else None
        self.odak = d.get("odak", (0.5, 0.5))
        self.odak = (float(self.odak[0]), float(self.odak[1])) if isinstance(self.odak, (list, tuple)) else (0.5, 0.5)
        if d.get("gorsel"):
            g = C.kapla(C.yukle(d["gorsel"]).convert("RGB"), round(W * self.zm), round(H * self.zm), self.odak)
            self.img = C.ayarla(g, karart=0.06, doygunluk=0.92)
            C.vinyet_uygula(self.img, 0.3)
            self.zemin = None
            pal = Z.KOYU
        else:
            self.img = None
            self.zemin = Z.Zemin(c, {"zemin": d.get("zemin"), "arka": d.get("arka")}, tohum=tohum,
                                 zm=max(1.08, self.metin_zoom or 1.08))
            pal = self.zemin.palet
        self.pal = pal
        self.metin = C.yazi(str(d["metin"]), C.FONT_DIALOG, 92 * S, pal.metin, max_w=0.40 * W, max_lines=4,
                            align="center", golge=pal.golge_t(S)) if d.get("metin") else None
        # 9. tur (izlenme S7): `say: true` -> metindeki sayılar panel açılınca 0'dan sayar (satırlar "\n" ile;
        # rakamlar sabit genişlikte, satır kaymaz)
        self.say = bool(d.get("say")) and bool(d.get("metin"))
        self.say_sure = float(d.get("say_sure", 1.5))
        self._say_cache: dict = {}
        if self.say:
            self.say_satirlar = [ln.strip() for ln in str(d["metin"]).split("\n") if ln.strip()]
            self.metin = self._say_katmani([1.0] * 16)
        self.ceviri = C.yazi(str(d["ceviri"]), C.FONT_DIALOG, 64 * S, C.SARI if pal.koyu else pal.metin,
                             max_w=0.40 * W, max_lines=3, align="center", golge=pal.golge_t(S, 4, 8)) \
            if d.get("ceviri") else None
        # 8. tur (izlenme hakemi N2): fotoğraflı koyu panelde sarı çeviri gri fotoğrafın üstünde silik kalıyordu:
        # arkasına koyu, yuvarlak bir bant
        if self.ceviri is not None and pal.koyu and d.get("arka"):
            px_, py_ = 26 * S, 10 * S
            bant = C.yuvarlak_kutu(int(self.ceviri.width + 2 * px_), int(self.ceviri.height + 2 * py_), 10 * S,
                                   (8, 9, 12, 196))
            bant.alpha_composite(self.ceviri, (int(px_), int(py_)))
            self.ceviri = bant
        self.ceviri_bant = self.ceviri is not None and pal.koyu and bool(d.get("arka"))
        self.etiket = _etiket_kutusu(str(d["etiket"]), S) if d.get("etiket") else None
        self.baslik = C.yazi(C.buyuk(str(d["baslik"])), C.FONT_CARD, 84 * S, C.BEYAZ if pal.koyu else pal.metin,
                             aralik=0.04, golge=(0, 4 * S, 10 * S, 0.7) if pal.koyu else None) \
            if d.get("baslik") else None
        # 5. tur (izlenme hakemi): 24 px alt yazı 1080p'de bile okunmuyordu: 40 px, koyu bant üstünde
        self.alt = _alt_kutusu(str(d["alt"]), S, 0.42 * W) if d.get("alt") else None

    def _say_katmani(self, kler: list[float]) -> Image.Image:
        """Satırlar alt alta, ortalı; her sayı kendi k (0..1) oranında."""
        S = self.S
        satirlar, j = [], 0
        for ln in self.say_satirlar:
            def deg(m):
                nonlocal j
                k = kler[min(j, len(kler) - 1)]
                j += 1
                son = m.group(0)
                return _hizali_sayi(son, int(round(int(son.replace(".", "")) * k)))
            satirlar.append(SAYI_RE.sub(deg, ln))
        key = tuple(satirlar)
        if key in self._say_cache:
            return self._say_cache[key]
        f_boy = 92 * S
        ims = [C.tabular_yazi(x, C.FONT_DIALOG, f_boy, self.pal.metin, golge=self.pal.golge_t(S)) for x in satirlar]
        lh = f_boy * 1.18
        w = max(im.width for im in ims)
        h = int(lh * (len(ims) - 1) + ims[-1].height)
        lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        for i, im in enumerate(ims):
            lay.alpha_composite(im, (int((w - im.width) / 2), int(i * lh)))
        if len(self._say_cache) > 96:
            self._say_cache.pop(next(iter(self._say_cache)))
        self._say_cache[key] = lay
        return lay

    def metin_katmani(self, u: float) -> Image.Image:
        """u: panel açılışından beri sn. Sayılar sırayla (0,45 sn arayla) out_cubic ile sayar."""
        if not self.say:
            return self.metin
        n = len(SAYI_RE.findall(" ".join(self.say_satirlar)))
        kler = [E.out_cubic((u - 0.2 - 0.45 * i) / self.say_sure) for i in range(n)]
        return self._say_katmani(kler or [1.0])

    def tam_kare(self, t: float, dur: float) -> Image.Image:
        """Panelin tam ekran (W x H) hâli; görünür pencere sonra kırpılır."""
        if self.img is not None:
            z = 1.0 + (self.zm - 1.0 - 0.01) * E.in_out_sine(t / max(dur, 1e-3))
            return C.kamera(self.img, self.W, self.H, z, self.odak)
        return self.zemin.ciz(t, dur)


def _alt_kutusu(metin: str, S: float, max_w: float) -> Image.Image:
    yz = C.yazi(metin, C.FONT_BOLD, 40 * S, (244, 242, 236), max_w=max_w, max_lines=2, satir=1.12)
    padx, pady, bar = 22 * S, 14 * S, 8 * S
    w, h = int(yz.width + 2 * padx + bar), int(yz.height + 2 * pady)
    lay = C.yuvarlak_kutu(w, h, 6 * S, (8, 9, 12, 225))
    ImageDraw.Draw(lay).rectangle((0, 0, int(bar) - 1, h), fill=C.SARI + (255,))
    lay.alpha_composite(yz, (int(bar + padx), int(pady)))
    spr, _, _ = C.golgeli(lay, 10 * S, 0.45, 0, 5 * S)
    return spr


def _etiket_kutusu(metin: str, S: float) -> Image.Image:
    yz = C.yazi(C.buyuk(metin), C.FONT_BOLD, 30 * S, (240, 238, 230), aralik=0.06, max_w=820 * S, max_lines=2)
    padx, pady, bar = 20 * S, 12 * S, 7 * S
    w, h = int(yz.width + 2 * padx + bar), int(yz.height + 2 * pady)
    lay = C.yuvarlak_kutu(w, h, 5 * S, (8, 9, 12, 215))
    ImageDraw.Draw(lay).rectangle((0, 0, int(bar) - 1, h), fill=C.SARI + (255,))
    lay.alpha_composite(yz, (int(bar + padx), int(pady)))
    spr, _, _ = C.golgeli(lay, 10 * S, 0.45, 0, 5 * S)
    return spr


class BolunmusCizici(Cizici):
    def hazirla(self):
        p = self.p
        self.paneller = {"sol": _Panel(p["sol"], self.c, 1), "sag": _Panel(p["sag"], self.c, 2)}
        self.z = bolunmus_zamanlari(self.sahne)
        self.cizgi = Z.renk(p.get("cizgi"), C.SARI)

    def genislik(self, t: float) -> float:
        """Sağ panelin genişliği (px)."""
        W = self.W
        z = self.z
        sag = W / 2 * E.out_cubic((t - z["ac"]["sag"]) / 0.6) if t >= z["ac"]["sag"] else 0.0
        if "sol" in z["ac"] and z["ac"]["sol"] > 0 and t < z["ac"]["sol"] + 0.6:   # sol da sonradan açılıyor
            sag = max(sag, W - W / 2 * E.out_cubic((t - z["ac"]["sol"]) / 0.6))
        if "sag" in z["buyut"]:
            sag += (W - sag) * E.in_out_cubic((t - z["buyut"]["sag"]) / 1.2)
        if "sol" in z["buyut"]:
            sag *= 1 - E.in_out_cubic((t - z["buyut"]["sol"]) / 1.2)
        return sag

    def ciz(self, t):
        S, W, H = self.S, self.W, self.H
        sw = int(round(self.genislik(t)))
        solw = W - sw
        im = Image.new("RGB", (W, H))
        for taraf, x0, pw in (("sol", 0, solw), ("sag", solw, sw)):
            if pw <= 0:
                continue
            pn = self.paneller[taraf]
            tam = pn.tam_kare(t, self.dur)
            fx = pn.odak[0] * W if pn.img is not None else W / 2
            kx = int(min(max(fx - pw / 2, 0), W - pw))
            parca = tam.crop((kx, 0, kx + pw, H))
            # soluklaşma
            ts = self.z["soluk"].get(taraf)
            if ts is not None and t > ts:
                q = E.in_out_sine((t - ts) / 0.6)
                parca = Image.blend(parca, ImageEnhance.Color(parca).enhance(0.25), q)
                parca = Image.blend(parca, Image.new("RGB", parca.size, (0, 0, 0)), 0.5 * q)
            im.paste(parca, (x0, 0))
            self._ust_ogeler(im, pn, taraf, x0, pw, t)
        if 0 < sw < W:   # ayraç
            x = solw
            d = ImageDraw.Draw(im)
            d.rectangle((x - 5 * S, 0, x + 5 * S, H), fill=(10, 10, 12))
            d.rectangle((x - 1.5 * S, 0, x + 1.5 * S, H), fill=self.cizgi)
        return im

    def _ust_ogeler(self, im, pn: _Panel, taraf: str, x0: int, pw: int, t: float) -> None:
        S, H = self.S, self.H
        if pw < 60 * S:
            return
        acilis = self.z["ac"][taraf]
        a = E.out_cubic((t - acilis - 0.15) / 0.4)
        cx = x0 + pw / 2
        if pn.metin is not None:
            yy = H * (0.44 if pn.ceviri is not None else 0.5) - pn.metin.height / 2 + Z.suzul(t, 1.1, 2.5) * S
            mk = pn.metin_katmani(t - acilis)
            sz = 1.0 + ((pn.metin_zoom - 1.0) * 0.5 * E.in_out_sine(t / max(self.dur, 1e-3)) if pn.metin_zoom else 0.0)
            if abs(sz - 1.0) > 1e-4:
                src = C.alt_piksel_hazirla(mk)
                spr, x0_, y0_ = C.alt_piksel(src, cx - mk.width * sz / 2,
                                             yy + mk.height * (1 - sz) / 2 + (1 - a) * 20 * S, sz, sz)
                C.bindir(im, spr, x0_, y0_, a)
            else:
                C.bindir_alt(im, mk, cx - mk.width / 2, yy + (1 - a) * 20 * S, a)
            tc = self.z["ceviri"].get(taraf)
            if pn.ceviri is not None and tc is not None and t >= tc:
                ac = E.out_cubic((t - tc) / 0.45)
                yc = yy + pn.metin.height + 40 * S
                lw = pn.ceviri.width * E.in_out_cubic((t - tc - 0.15) / 0.5)
                if lw > 1:
                    if pn.ceviri_bant:
                        pass   # koyu bant zaten çeviriyi taşıyor
                    elif pn.pal.koyu:
                        ImageDraw.Draw(im).rectangle((cx - pn.ceviri.width / 2, yc + pn.ceviri.height - 3 * S,
                                                      cx - pn.ceviri.width / 2 + lw, yc + pn.ceviri.height + 6 * S),
                                                     fill=C.SARI)
                    else:
                        isaret = Image.new("RGB", (int(lw + 20 * S), int(pn.ceviri.height * 0.6)), pn.pal.isaret)
                        C.bindir(im, isaret, cx - pn.ceviri.width / 2 - 10 * S, yc + pn.ceviri.height * 0.3, 0.8)
                C.bindir_alt(im, pn.ceviri, cx - pn.ceviri.width / 2, yc + (1 - ac) * 16 * S, ac)
        if pn.baslik is not None:
            C.bindir(im, pn.baslik, cx - pn.baslik.width / 2, 56 * S - (1 - a) * 14 * S, a)
        if pn.etiket is not None:
            ex = x0 + 40 * S if pn.baslik is None else x0 + 40 * S
            ey = 52 * S if pn.baslik is None else 56 * S + pn.baslik.height + 22 * S
            C.bindir(im, pn.etiket, ex - (1 - a) * 30 * S, ey, a)
        if pn.alt is not None:
            C.bindir(im, pn.alt, x0 + 36 * S, H - 84 * S - pn.alt.height, a)


# ================================================================ nokta ızgarası

def izgara_zamanlari(sahne) -> dict:
    p = sahne.p
    bas = basla_zamani(sahne, 0.4)
    dolum = float(p.get("dolum", 2.5))
    sondur = [(o.zaman, float(o.p["oran"]), float(o.p.get("sure", 1.6)), o.p.get("etiket"))
              for o in olaylar(sahne, "sondur")]
    return {"bas": bas, "bit": bas + dolum, "sondur": sondur}


def izgara_duzeni(n: int, aw: float, ah: float, sutun: int | None = None) -> tuple[int, int, float]:
    """(sütun, satır, aralık) — n nokta aw x ah alana en büyük aralıkla sığar."""
    cols = int(sutun) if sutun else max(1, round(math.sqrt(n * aw / ah)))
    rows = -(-n // cols)
    pitch = min(aw / cols, ah / rows)
    return cols, rows, pitch


class IzgaraCizici(Cizici):
    def hazirla(self):
        p, S, W, H = self.p, self.S, self.W, self.H
        self.zemin = Z.Zemin(self.c, p)
        pal = self.pal = self.zemin.palet
        self.n = n = int(p.get("n", 10000))
        self.zt = izgara_zamanlari(self.sahne)
        aw, ah = 1600 * S, 500 * S
        cols, rows, pitch = izgara_duzeni(n, aw, ah, p.get("sutun"))
        self.cols, self.rows, self.pitch = cols, rows, pitch
        gw, gh = cols * pitch, rows * pitch
        gx0, gy0 = (W - gw) / 2, H * 0.53 - gh / 2
        self.kutu = (int(gx0), int(gy0), int(math.ceil(gx0 + gw)), int(math.ceil(gy0 + gh)))
        x0, y0, x1, y1 = self.kutu
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32) + 0.5
        c_ = np.floor((xx - gx0) / pitch).astype(np.int32)
        r_ = np.floor((yy - gy0) / pitch).astype(np.int32)
        dx = xx - (gx0 + (c_ + 0.5) * pitch)
        dy = yy - (gy0 + (r_ + 0.5) * pitch)
        r = max(0.7, 0.36 * pitch)
        cov = np.clip(r + 0.5 - np.sqrt(dx * dx + dy * dy), 0, 1)
        idx = r_ * cols + c_
        gecerli = (c_ >= 0) & (c_ < cols) & (r_ >= 0) & (idx < n) & (cov > 0)
        self.idx = np.where(gecerli, idx, n).astype(np.int32)        # n = boş (alfa 0)
        self.cov = np.where(gecerli, cov, 0).astype(np.float32)[..., None]
        self.renk = np.array(Z.renk(p.get("renk"), (236, 232, 222) if pal.koyu else pal.metin), np.float32)
        k = np.arange(n, dtype=np.float32)
        self.t_gor = self.zt["bas"] + (self.zt["bit"] - self.zt["bas"]) * k / max(n, 1)
        # söndürme: her olay kalan yanık noktalardan oran * n tanesini rastgele seçer
        rng = np.random.default_rng(40)
        self.t_son = np.full(n, np.inf, np.float32)
        kalan = np.arange(n)
        for t0, oran, sure, _ in self.zt["sondur"]:
            m = min(len(kalan), int(round(oran * n)))
            sec = rng.choice(kalan, m, replace=False) if m else np.array([], int)
            self.t_son[sec] = t0 + sure * rng.random(m).astype(np.float32)
            kalan = np.setdiff1d(kalan, sec)
        cc, rr = k % cols, k // cols
        self.faz = (cc * 0.11 + rr * 0.17).astype(np.float32)
        self.ust = C.yazi(C.buyuk(str(p["ust"])), C.FONT_BOLD, 34 * S, pal.ikincil, aralik=0.2) if p.get("ust") else None
        self.etiket = C.yazi(str(p["etiket"]), C.FONT_DIALOG, 56 * S, pal.vurgu, max_w=1500 * S, max_lines=2,
                             align="center", golge=pal.golge_t(S, 4, 8)) if p.get("etiket") else None
        self.alt = C.yazi(str(p["alt"]), C.FONT_BOLD, 30 * S, pal.ikincil) if p.get("alt") else None   # 6. tur: 26 -> 30
        self.son_etiketler = [(t0, C.yazi(str(et), C.FONT_DIALOG, 56 * S, (226, 80, 70) if pal.koyu else pal.vurgu,
                                          max_w=1500 * S, max_lines=2, align="center", golge=pal.golge_t(S, 4, 8)))
                              for t0, _, _, et in self.zt["sondur"] if et]
        self.say = bool(p.get("say"))
        self._sayi: dict = {}

    def alfa(self, t: float) -> np.ndarray:
        a = np.clip((t - self.t_gor) / 0.12, 0, 1)
        son = np.clip((t - self.t_son) / 0.45, 0, 1)
        a = a * (1 - 0.84 * son)
        a = a * (0.93 + 0.07 * np.sin(self.faz + t * 1.4))   # yavaş ışıltı (boşta hareket)
        return np.concatenate([a, [0.0]]).astype(np.float32)

    def ciz(self, t):
        S, W, H = self.S, self.W, self.H
        im = self.zemin.ciz(t, self.dur)
        x0, y0, x1, y1 = self.kutu
        reg = np.asarray(im.crop(self.kutu), np.float32)
        a = self.cov * self.alfa(t)[self.idx][..., None]
        out = reg * (1 - a) + self.renk[None, None, :] * a
        im.paste(Image.fromarray(out.astype(np.uint8), "RGB"), (x0, y0))
        au = E.out_cubic(t / 0.4)
        if self.say:
            yanik = int(np.clip((t - self.zt["bas"]) / max(self.zt["bit"] - self.zt["bas"], 1e-3), 0, 1) * self.n)
            metin = C.say_bicimle(yanik)
            spr = self._sayi.get(metin)
            if spr is None:
                spr = C.yazi(metin, C.FONT_CARD, 96 * S, self.pal.metin, golge=self.pal.golge_t(S))
                self._sayi = {metin: spr}
            C.bindir(im, spr, x0, y0 - 26 * S - spr.height, au)
            if self.ust is not None:
                C.bindir(im, self.ust, x0 + spr.width + 24 * S, y0 - 40 * S - self.ust.height, au)
        elif self.ust is not None:
            C.bindir(im, self.ust, W / 2 - self.ust.width / 2, y0 - 42 * S - self.ust.height, au)
        ey = y1 + 40 * S
        if self.etiket is not None:
            ae = E.out_cubic((t - self.zt["bit"] + 0.4) / 0.5)
            for t0, _ in self.son_etiketler:   # söndürme etiketi gelince eski etiket kaybolur
                ae *= 1 - E.out_cubic((t - t0 - 0.2) / 0.3)
            C.bindir(im, self.etiket, W / 2 - self.etiket.width / 2, ey + (1 - min(ae, 1)) * 14 * S, ae)
        for t0, spr in self.son_etiketler:
            ae = E.out_cubic((t - t0 - 0.35) / 0.5)
            if ae > 0:
                C.bindir(im, spr, W / 2 - spr.width / 2, ey + (1 - ae) * 14 * S, ae)
        if self.alt is not None:
            C.bindir(im, self.alt, W / 2 - self.alt.width / 2, H - 120 * S, 0.85 * E.out_cubic((t - 0.6) / 0.5))
        return im


# ================================================================ soruşturma panosu

VARSAYILAN_YERLER = [(0.5, 0.40), (0.2, 0.28), (0.8, 0.28), (0.2, 0.72), (0.8, 0.72), (0.5, 0.80), (0.35, 0.56),
                     (0.65, 0.56), (0.08, 0.5), (0.92, 0.5), (0.35, 0.15), (0.65, 0.15)]


ASILI_T = -10.0   # `asili: true` kartın zamanı: sahne başında iğnelenmiş, ipi gerili


def pano_zamanlari(sahne) -> dict:
    """{'kartlar': {id: t}, 'ipler': [(a, b, t)], 'damgalar': [olay]}"""
    kartlar = sahne.p["kartlar"]
    acik = {o.p["id"]: o.zaman for o in olaylar(sahne, "kart")}
    out, sira = {}, 0
    for k in kartlar:
        if k.get("asili"):          # sahne başında zaten asılı (önceki pano çekiminden devam): düşme/ses yok
            out[k["id"]] = ASILI_T
        elif k["id"] in acik:
            out[k["id"]] = acik[k["id"]]
        else:
            out[k["id"]] = 0.45 + 0.9 * sira
            sira += 1
    ip_olay = {(o.p["a"], o.p["b"]): o.zaman for o in olaylar(sahne, "ip")}
    ipler = []
    for a, b in sahne.p.get("ipler") or []:
        t = ip_olay.get((a, b), ip_olay.get((b, a)))
        if t is None:
            t = max(out[a], out[b]) + 0.5
        ipler.append((a, b, t))
    return {"kartlar": out, "ipler": ipler}


@lru_cache(maxsize=4)
def mantar_dokusu(W: int, H: int, tohum: int = 21) -> Image.Image:
    """Mantar pano: sıcak kahve taban, çok ölçekli benek, koyu delikler, kenarda kararma (kendi dokumuz)."""
    S = W / 1920
    rng = np.random.default_rng(tohum)
    taban = np.array([168, 120, 74], np.float32)
    l1 = Z._gurultu(W, H, max(6, int(140 * S)), tohum)
    l2 = Z._gurultu(W, H, max(3, int(12 * S)), tohum + 1)
    l3 = rng.normal(0, 1, (H, W)).astype(np.float32)
    lum = 1 + 0.06 * l1 + 0.08 * l2 + 0.07 * l3
    arr = taban[None, None, :] * lum[..., None]
    delik = rng.random((H, W)) < 0.012
    arr[delik] *= 0.55
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / math.sqrt(2)
    arr *= (1 - 0.35 * np.clip((d - 0.5) / 0.5, 0, 1) ** 1.5)[..., None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")


@lru_cache(maxsize=2)
def kece_dokusu(W: int, H: int, tohum: int = 23) -> Image.Image:
    """Koyu mavi-gri keçe pano (kendi dokumuz): ince lif gürültüsü, hafif leke, kenarda kararma, ahşap çerçeve yok."""
    rng = np.random.default_rng(tohum)
    taban = np.array([78, 92, 112], np.float32)
    l1 = Z._gurultu(W, H, max(6, int(180 * W / 1920)), tohum)
    l3 = rng.normal(0, 1, (H, W)).astype(np.float32)
    lum = 1 + 0.07 * l1 + 0.05 * l3
    arr = taban[None, None, :] * lum[..., None]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / math.sqrt(2)
    arr *= (1 - 0.3 * np.clip((d - 0.5) / 0.5, 0, 1) ** 1.5)[..., None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")


def _raptiye(r: float) -> Image.Image:
    n = int(r * 2 + 8)
    ss = 3
    lay = Image.new("RGBA", (n * ss, n * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    o = 4 * ss
    d.ellipse((o + 2 * ss, o + 3 * ss, (n - 2) * ss, (n - 1) * ss), fill=(0, 0, 0, 90))   # gölge
    d.ellipse((o, o, (n - 4) * ss, (n - 4) * ss), fill=(196, 28, 32, 255), outline=(120, 10, 14, 255),
              width=max(1, int(ss * r * 0.12)))
    k = (n - 4 - 4) * ss
    d.ellipse((o + k * 0.22, o + k * 0.18, o + k * 0.48, o + k * 0.42), fill=(255, 190, 190, 200))
    return lay.resize((n, n), Image.LANCZOS)


class PanoCizici(Cizici):
    def hazirla(self):
        p, S, W, H = self.p, self.S, self.W, self.H
        # tuval kadrajdan geniş (kaydırma payı); kamera 1:1'den (zoom = zm) başlar, en çok %8 yaklaşır
        self.zm = float(p.get("zoom", 1.2))
        CW, CH = round(W * self.zm), round(H * self.zm)
        self.CW, self.CH = CW, CH
        # doku: mantar (vars.) | kece (koyu mavi-gri keçe: aynı mantar pano üçüncü kez görünmesin)
        self.taban = kece_dokusu(CW, CH) if p.get("doku") == "kece" else mantar_dokusu(CW, CH)
        self.zt = pano_zamanlari(self.sahne)
        self.raptiye = _raptiye(15 * S)
        self.canli_golge = bool((getattr(self.c.v, "hareket", None) or {}).get("ikincil", False))
        rng = np.random.default_rng(77)
        self.kartlar = {}
        for i, k in enumerate(p["kartlar"]):
            yer = VARSAYILAN_YERLER[i % len(VARSAYILAN_YERLER)]
            x = float(k.get("x", yer[0]))
            y = float(k.get("y", yer[1]))
            cx, cy = (x - 0.5) * W + CW / 2, (y - 0.5) * H + CH / 2
            egim = float(k.get("egim", rng.uniform(-4, 4)))
            spr, foto_y = self._kart(k)
            bb = spr.getchannel("A").point(lambda v: 255 if v > 160 else 0).getbbox() or (0, 0, spr.width, spr.height)
            govde = (cx - spr.width / 2 + bb[0], cy - spr.height / 2 + bb[1], cx - spr.width / 2 + bb[2],
                     cy - spr.height / 2 + bb[3])   # kartın kendisi (gölgesiz), tuval pikseli
            self.kartlar[k["id"]] = {"spr": spr, "cx": cx, "cy": cy, "egim": egim, "t": self.zt["kartlar"][k["id"]],
                                     "foto_y": foto_y, "govde": govde, "id": k["id"],
                                     "pin": (cx, cy - spr.height / 2 + 16 * S),
                                     "alt_pin": ((govde[0] + govde[2]) / 2, govde[3] - 16 * S)}
            if self.canli_golge:   # 7. tur: düşen kartın havadaki gölgesi (uzak, yumuşak; oturunca kaybolur)
                g, gx, gy = C.golge_katmani(spr, 16 * S, 0.5)
                self.kartlar[k["id"]]["golge"] = (g, gx, gy)
        self.damgalar = []
        for i, o in enumerate(damga_olaylari(self.sahne, kartli=True)):
            kt = self.kartlar[o.p["kart"]]
            dm = Damga(o, self.c, i)
            # kart_y: kart merkezine göre (yükseklik oranı). Varsayılan: görselli kartta görselin ortası (başlık
            # okunur kalsın; eskiden hep +0.2 idi ve görselli kartta tam başlığın üstüne düşüyordu), yoksa +0.2
            ky = o.p.get("kart_y")
            ky = float(ky) if ky is not None else (kt["foto_y"] if kt["foto_y"] is not None else 0.2)
            self.damgalar.append((dm, kt, ky))
        self.baslik = C.yazi(str(p["baslik"]), C.FONT_DIALOG, 54 * S, C.BEYAZ, max_w=1100 * S, max_lines=2,
                             golge=(0, 3 * S, 8 * S, 0.8)) if p.get("baslik") else None
        self.sira = sorted(self.kartlar.values(), key=lambda k: k["t"])
        # 10. tur (animasyon hakemi S6): ipin ucu. Raptiye kartın üstünde; öbür kart bu kartın ALTINDAysa ip üst
        # raptiyeden kartın kendi yazısının üstünden aşağı iniyordu ("KAYMAKÇALAN / kaynak: ..." okunmuyordu): o uç
        # kartın alt kenarındaki ikinci raptiyeye bağlanır
        self.ip_uclari = {}
        for a_, b_, _ in self.zt["ipler"]:
            self.ip_uclari[(a_, b_)] = (self._ip_ucu(a_, b_), self._ip_ucu(b_, a_))

    def _ip_ucu(self, a: str, b: str) -> tuple[tuple[float, float], bool]:
        """a kartında, b'ye giden ipin bağlandığı nokta ve alt raptiye mi."""
        ka, kb = self.kartlar[a], self.kartlar[b]
        x0, y0, x1, y1 = ka["govde"]
        px, py = ka["pin"]
        hx, hy = (kb["govde"][0] + kb["govde"][2]) / 2, (kb["govde"][1] + kb["govde"][3]) / 2
        if hy > y1 and hy - py > 1e-6:
            # üst raptiyeden b'nin ortasına giden doğru kartı alt kenarından mı terk ediyor (gövdeyi boydan geçer)
            xa = px + (hx - px) * (y1 - py) / (hy - py)
            if x0 <= xa <= x1:
                return ka["alt_pin"], True
        return ka["pin"], False

    def _kart(self, k: dict) -> Image.Image:
        S = self.S
        stil = k.get("stil", "kagit")
        en = float(k.get("en", 520 if stil == "merkez" else 420)) * S
        pad = 26 * S
        murekkep = (32, 28, 26)
        bas = C.yazi(str(k["metin"]), C.FONT_BOLD, (52 if stil == "merkez" else 40) * S,
                     (84, 76, 68) if stil == "bos" else murekkep, max_w=en - 2 * pad, max_lines=5, align="center",
                     satir=1.12)
        alt = C.yazi(str(k["alt"]), C.FONT_BOLD, 33 * S, (84, 74, 64), max_w=en - 2 * pad, max_lines=4,   # 8. tur: 28 -> 33 (telefon)
                     align="center", satir=1.15) if k.get("alt") else None
        foto = None
        if k.get("gorsel"):
            foto = C.sigdir(C.yukle(k["gorsel"]).convert("RGB"), en - 2 * pad, 0.62 * en)
        h = pad + (foto.height + 16 * S if foto else 0) + (36 * S if stil == "merkez" else 0) + bas.height \
            + (alt.height + 22 * S if alt else 0) + pad
        w, h = int(en), int(h)
        if stil == "bos":
            lay = Image.new("RGBA", (w, h), (246, 240, 226, 205))
            d = ImageDraw.Draw(lay)
            kc, kw = (92, 80, 68, 255), max(1, int(4 * S))
            for x in range(0, w, int(22 * S)):   # kesik çizgi çerçeve
                d.line((x, kw // 2, x + 12 * S, kw // 2), fill=kc, width=kw)
                d.line((x, h - 1 - kw // 2, x + 12 * S, h - 1 - kw // 2), fill=kc, width=kw)
            for y in range(0, h, int(22 * S)):
                d.line((kw // 2, y, kw // 2, y + 12 * S), fill=kc, width=kw)
                d.line((w - 1 - kw // 2, y, w - 1 - kw // 2, y + 12 * S), fill=kc, width=kw)
        else:
            doku = Z.kagit_dokusu(max(w, 64), max(h, 64)).crop((0, 0, w, h)).convert("RGBA")
            lay = doku
            d = ImageDraw.Draw(lay)
            if stil == "merkez":
                d.rectangle((0, 0, w, int(26 * S)), fill=(180, 34, 30, 255))
        y = pad + (36 * S if stil == "merkez" else 0)
        foto_y = None
        if foto is not None:
            fx = (w - foto.width) // 2
            lay.paste(foto, (fx, int(y)))
            foto_y = (y + foto.height / 2) / h - 0.5   # görselin ortası, kart merkezine göre (yükseklik oranı)
            y += foto.height + 16 * S
        lay.alpha_composite(bas, ((w - bas.width) // 2, int(y)))
        y += bas.height
        if alt is not None:
            y += 10 * S
            ImageDraw.Draw(lay).line((pad, y, w - pad, y), fill=(170, 156, 136, 255), width=max(1, int(2 * S)))
            y += 12 * S
            lay.alpha_composite(alt, ((w - alt.width) // 2, int(y)))
        spr, ox, oy = C.golgeli(lay, 12 * S, 0.55, 4 * S, 9 * S)
        if foto_y is not None:   # gölge payı sprite'ı büyütür: oranı sprite yüksekliğine çevir
            foto_y = (oy + (foto_y + 0.5) * h - spr.height / 2) / spr.height
        return spr, foto_y

    def _ip(self, d: ImageDraw.ImageDraw, a, b, q: float) -> None:
        S = self.S
        (x0, y0), (x1, y1) = a, b
        L = math.hypot(x1 - x0, y1 - y0)
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2 + 0.07 * L   # hafif sarkma
        n = 40
        pts = []
        for i in range(int(n * q) + 1):
            u = i / n
            pts.append(((1 - u) ** 2 * x0 + 2 * (1 - u) * u * mx + u * u * x1,
                        (1 - u) ** 2 * y0 + 2 * (1 - u) * u * my + u * u * y1))
        if len(pts) > 1:
            d.line([(x + 3 * S, y + 4 * S) for x, y in pts], fill=(60, 30, 18), width=max(1, int(4 * S)))
            d.line(pts, fill=(196, 26, 30), width=max(1, int(4.5 * S)))

    def _ip_ciz(self, cv: Image.Image, a: str, b: str, pa, pb, q: float, t: float) -> None:
        """10. tur (animasyon hakemi S6): ip, uçları olmayan kartların ALTINDAN geçer (üstten geçen ip "AYGÜN" kartının
        görselini ve başka kartların yazısını çiziyordu). İp ayrı katmanda çizilir; araya giren asılı kartların
        gövdesi (eğimiyle) katmandan silinir."""
        S = self.S
        xs, ys = [pa[0], pb[0]], [pa[1], pb[1] + 0.07 * math.hypot(pb[0] - pa[0], pb[1] - pa[1])]
        m = int(12 * S)
        X0, Y0 = int(min(xs)) - m, int(min(ys)) - m
        X1, Y1 = int(max(xs)) + m + 1, int(max(ys)) + m + 1
        lay = Image.new("RGBA", (max(1, X1 - X0), max(1, Y1 - Y0)), (0, 0, 0, 0))
        self._ip(ImageDraw.Draw(lay), (pa[0] - X0, pa[1] - Y0), (pb[0] - X0, pb[1] - Y0), q)
        aradaki = [k for k in self.sira if k["id"] not in (a, b) and t >= k["t"] + 0.4
                   and k["govde"][2] > X0 and k["govde"][0] < X1 and k["govde"][3] > Y0 and k["govde"][1] < Y1]
        if aradaki:
            maske = Image.new("L", lay.size, 0)
            dm = ImageDraw.Draw(maske)
            for k in aradaki:
                gx0, gy0, gx1, gy1 = k["govde"]
                cx, cy = (gx0 + gx1) / 2, (gy0 + gy1) / 2
                th = math.radians(k["egim"])
                c, s_ = math.cos(th), math.sin(th)
                w2, h2 = (gx1 - gx0) / 2, (gy1 - gy0) / 2
                dm.polygon([(c * dx + s_ * dy + cx - X0, -s_ * dx + c * dy + cy - Y0)
                            for dx, dy in ((-w2, -h2), (w2, -h2), (w2, h2), (-w2, h2))], fill=255)
            lay.putalpha(ImageChops.subtract(lay.getchannel("A"), maske))
        cv.paste(lay, (X0, Y0), lay)

    def ciz(self, t):
        S, W, H = self.S, self.W, self.H
        cv = self.taban.copy()
        # kartlar (iğnelenme sırasıyla)
        for k in self.sira:
            u = (t - k["t"]) / 0.4
            if u <= 0:
                continue
            s = 1.22 - 0.22 * E.out_back(u, 1.4)
            aci = k["egim"] + 7 * (1 - E.out_cubic(u))
            h = min(1.0, max(0.0, (s - 1) / 0.22))
            if h > 0.02 and "golge" in k:
                g, gx, gy = k["golge"]
                gs, x0, y0 = C.afin(g, k["cx"] + (10 + 34 * h) * S, k["cy"] + (14 + 50 * h) * S, s, s, aci,
                                    gx + k["spr"].width / 2, gy + k["spr"].height / 2)
                C.bindir(cv, gs, x0, y0, h * min(1.0, u * 2.5))
            spr, x0, y0 = C.afin(k["spr"], k["cx"], k["cy"], s, s, aci)
            C.bindir(cv, spr, x0, y0, min(1.0, u * 2.5))
        alt_pinler = []
        for a, b, t0 in self.zt["ipler"]:
            q = E.in_out_cubic((t - t0) / 0.55)
            if q > 0:
                (pa, alt_a), (pb, alt_b) = self.ip_uclari[(a, b)]
                self._ip_ciz(cv, a, b, pa, pb, q, t)
                alt_pinler += [(pa, t0)] if alt_a else []
                alt_pinler += [(pb, t0 + 0.4)] if alt_b else []
        for k in self.sira:   # raptiyeler ipin üstünde
            u = (t - k["t"] - 0.18) / 0.22
            if u > 0:
                s = 0.4 + 0.6 * E.out_back(u, 2.0)
                px, py = k["pin"]
                spr, x0, y0 = C.afin(self.raptiye, px, py, s, s)
                C.bindir(cv, spr, x0, y0)
        for (px, py), t0 in alt_pinler:   # ipin alt kenara bağlandığı ikinci raptiye, ip oraya varınca batar
            u = (t - t0) / 0.22
            if u > 0:
                s = 0.4 + 0.6 * E.out_back(u, 2.0)
                spr, x0, y0 = C.afin(self.raptiye, px, py, s, s)
                C.bindir(cv, spr, x0, y0)
        for dm, k, ky in self.damgalar:
            dm.ciz(cv, t, k["cx"], k["cy"] + ky * k["spr"].height)
        # kamera: 1:1'den yavaş yaklaşma + asılı kartların ağırlık merkezine kayma (yeni kart biraz daha ağır);
        # yalnız son karta gitmek üstteki kartları başlığın altına itiyordu
        # yakin > 1: kamera kartlara yaklaşır (pano iki çekime bölündüğünde ilk çekim; kartlar büyük okunur) ve
        # ağırlık merkezine daha çok kayar
        yakin = float(self.p.get("yakin", 1.0))
        z = self.zm * yakin * (1.0 + 0.06 * E.in_out_sine(t / self.dur))
        top = fx = fy = 0.0
        for k in self.sira:
            q = E.in_out_sine((t - k["t"]) / 1.1)
            if q <= 0:
                break
            w = q * (1.0 + math.exp(-(t - k["t"]) / 2.0))
            top += w
            fx += w * k["cx"] / self.CW
            fy += w * k["cy"] / self.CH
        mx, my = 0.5, 0.5
        if top > 0:
            g = (0.6 if yakin <= 1.0 else 0.95) * min(1.0, top)
            mx += (fx / top - 0.5) * g
            my += (fy / top - 0.5) * g
        im = C.kamera(cv, W, H, z, (mx, my))
        C.vinyet_uygula(im, 0.25)
        if self.baslik is not None:
            a = E.out_cubic(t / 0.5)
            C.bindir(im, self.baslik, 80 * S, 64 * S - (1 - a) * 12 * S, a)
            ImageDraw.Draw(im).rectangle((80 * S, 64 * S + self.baslik.height + 12 * S,
                                          80 * S + 140 * S * E.out_cubic((t - 0.15) / 0.5),
                                          64 * S + self.baslik.height + 18 * S), fill=C.SARI)
        return im


def vuruslar(sahne) -> list[float]:
    if sahne.tip == "bolunmus":
        z = bolunmus_zamanlari(sahne)
        return [x for d in z.values() for x in d.values()]
    if sahne.tip == "izgara":
        z = izgara_zamanlari(sahne)
        return [z["bas"], z["bit"]] + [t + s for t, _, s, _ in z["sondur"]]
    if sahne.tip == "pano":
        z = pano_zamanlari(sahne)
        return list(z["kartlar"].values()) + [t for _, _, t in z["ipler"]]
    return []
