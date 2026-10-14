"""Kapanış çağrısı (7. tur, `kapanis`): video kutusuz, hikâyeye bağlı bitiş sahnesi (~8-12 sn).

Hesap sahibi (13.10): "Bitişteki iki 'sıradaki video' kutusu gereksiz (kanalda henüz 2 uzun video yok); abone / beğen /
yorum çağrısı düz değil, hikâyeye bağlı ve ilgi çekici olsun." Bu sahne:

- Üstte hikâyenin açık kalan sorusu (`soru`; yoksa ilk satır), kelime kelime belirir; isteğe bağlı küçük üst yazı
  (`ust`, ör. "SON SORU").
- Ortada 0-3 **seçenek kartı** (`secenekler`: metin, alt, gorsel, harf): her kart bir wojak (ya da görsel), altında
  sarı ad plakası, köşesinde A/B/C rozeti. Kartlar sırayla zıplayarak gelir; `secenek` olayı (ya da varsayılan sıra)
  kartı vurgular (sarı çerçeve, büyüme, içindeki karakter sıçrar). Kartlar birbirine bağlanmaz (ip/ok yok): tartışmalı
  kişiler aynı karede ama ayrı seçenek olarak durur (OGRENILENLER §2.7 dramatizasyon sınırı).
- Altta kanalın kendi düğmeleri (`dugmeler`: abone, zil, begen, yorum; YouTube logosu yok): solda çağrıyı yapan wojak
  (`karakter`: gorsel, yuz) aşağıdan yükselir; elinden çıkan imleç ABONE OL'a gider ve tıklar (düğme basılır, griye
  döner: "ABONE OLUNDU" + tik işareti, wojak gülümser), sonra zile (zil sallanır, çınlama çizgileri), sonra BEĞEN'e
  (başparmak dolar, kıvılcım). Yorum balonunda soru daktiloyla yazılır (`yorum`).
- `bos_alan: true` (ya da sag_ust / sol_ust): YouTube Studio'nun kendi "Abone ol" öğesi için o köşede ~280x280 px boş
  alan kalır (soru o yana taşmaz). Varsayılan kapalı: sahnenin kendi düğmeleri çağrıyı zaten yapar.

Zamanlama (sahne içi sn; 10 sn'den kısa sahnede orantılı sıkışır): soru 0,2; kartlar 0,8 + 0,18·i; karakter 1,7;
düğmeler 2,0; imleç 2,4; tıklar abone 3,1 / zil 3,9 / begen 4,7; yorum yazımı son tıktan 0,5 sn sonra; seçenek
vurguları yazım bitince 0,6 sn arayla. `tikla {hedef}` ve `secenek {indeks}` olayları bu anları satıra çapalar.
Efektler (ses.py): soru whoosh, kart pop, karakter whoosh, tık (klik), abone pop, zil (zil), beğen pop, yazım tuşları,
vurgu blip.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageOps

from .. import config, facing
from . import cizim as C
from . import easing as E
from . import zemin as Z
from .sahneler import Cizici

VARSAYILAN_KARAKTER = config.ASSETS / "kit" / "klasik" / "sakin.png"
VARSAYILAN_YUZ = config.ASSETS / "kit" / "klasik" / "mutlu.png"
YORUM_HIZI = 24.0   # harf / sn
GRI = (64, 66, 74)
KOYU_DUGME = (24, 26, 32)
KIRMIZI_DUGME = (204, 18, 24)


def kapanis_zamanlari(sahne) -> dict:
    """Bütün anlar (sahne içi sn): soru, kartlar [..], karakter, dugmeler [..], imlec, tik {hedef: t}, yorum,
    yorum_bitis, vurgu [(t, indeks)], k (sıkıştırma)."""
    p = sahne.p
    dur = sahne.sure_hesap or 10.0
    k = min(1.0, dur / 10.0)
    n = len(p.get("secenekler") or [])
    dug = list(p.get("dugmeler") or ["abone", "zil", "begen", "yorum"])
    tik_sira = [d for d in ("abone", "zil", "begen") if d in dug]
    tik = {d: (3.1 + 0.8 * i) * k for i, d in enumerate(tik_sira)}
    for o in sorted((o for o in sahne.olaylar if o.tip == "tikla"), key=lambda o: o.zaman):
        tik[o.p["hedef"]] = o.zaman
    son_tik = max(tik.values()) if tik else 2.6 * k
    yorum = son_tik + 0.5 * k
    metin = str(p.get("yorum") or varsayilan_yorum(n))
    yorum_bitis = yorum + len(metin) / YORUM_HIZI
    # 8. tur (animasyon hakemi S1): kartlar 0,5 sn arayla tek tek vurgulanır, sonra ÜÇÜ BİRDEN nabız gibi atar ve
    # eşit, hafif vurguda kalır. Eskiden son vurgu (C, ŞANS) son karede hâlâ sarı ve büyüktü: cevap gibi okunuyordu.
    ara = 0.5
    bas = min(yorum_bitis + 0.35, dur - 0.75 - ara * n)
    vurgu = [(max(0.0, bas + ara * i), i + 1) for i in range(n)]
    ev = sorted((o for o in sahne.olaylar if o.tip == "secenek"), key=lambda o: o.zaman)
    if ev:
        vurgu = [(o.zaman, int(o.p["indeks"])) for o in ev]
    hepsi = (vurgu[-1][0] + ara) if (vurgu and n >= 2) else None
    if hepsi is not None and hepsi > dur - 0.4:
        hepsi = None
    return {"soru": 0.2 * k, "kartlar": [(0.8 + 0.18 * i) * k for i in range(n)], "karakter": 1.7 * k,
            "dugmeler": [(2.0 + 0.1 * j) * k for j in range(len(dug))], "imlec": 2.4 * k, "tik": tik,
            "yorum": yorum, "yorum_bitis": yorum_bitis, "vurgu": vurgu, "hepsi": hepsi, "k": k, "metin": metin,
            "dugme_sira": dug}


def varsayilan_yorum(n: int) -> str:
    """'A mı, B mi, yoksa C mi? Yorumlara yaz' (soru eki harfin okunuşuna uyar: A -> mı, B/C -> mi)."""
    ek = {"A": "mı"}
    harfler = ["A", "B", "C"][:n]
    if n >= 2:
        parca = [f"{h} {ek.get(h, 'mi')}" for h in harfler]
        bas = ", ".join(parca[:-1])
        return f"{bas}{', yoksa ' if n > 2 else ', '}{parca[-1]}?\nCevabını yorumlara yaz"
    return "Sence?\nCevabını yorumlara yaz"


def vuruslar(sahne) -> list[float]:
    z = kapanis_zamanlari(sahne)
    return ([z["soru"], z["karakter"], z["imlec"], z["yorum"]] + z["kartlar"] + z["dugmeler"]
            + list(z["tik"].values()) + [t for t, _ in z["vurgu"]] + ([z["hepsi"]] if z.get("hepsi") else []))


def efektler(sahne, b: float) -> list[tuple[float, str, float]]:
    """Otomatik efektler (ses.py _ek_efektler çağırır): (mutlak sn, ad, dB)."""
    z = kapanis_zamanlari(sahne)
    out = [(b + max(0.0, z["soru"] - 0.1), "whoosh_kisa", -16.0)]
    out += [(b + t, "pop", -13.0) for t in z["kartlar"]]
    out.append((b + max(0.0, z["karakter"] - 0.12), "whoosh_kisa", -18.0))
    out += [(b + t, "pop", -20.0) for t in z["dugmeler"]]
    for hedef, t in z["tik"].items():
        out.append((b + t, "klik", -9.0))
        if hedef == "abone":
            out.append((b + t + 0.05, "pop", -12.0))
        elif hedef == "zil":
            out.append((b + t + 0.03, "zil", -12.0))
        elif hedef == "begen":
            out.append((b + t + 0.04, "pop", -11.0))
    harfler = [i for i, ch in enumerate(z["metin"]) if ch != " "]
    out += [(b + z["yorum"] + i / YORUM_HIZI, "tus", -25.0) for i in harfler[::3]]
    out += [(b + t, "blip", -15.0) for t, _ in z["vurgu"]]
    # 11. tur: kartın tepkisi (ilk vurgusunda): damga iner, zar döner
    sec = sahne.p.get("secenekler") or []
    ilk = {}
    for t, idx in z["vurgu"]:
        ilk.setdefault(idx, t)
    for idx, t in ilk.items():
        s_ = sec[idx - 1] if 0 < idx <= len(sec) else {}
        if s_.get("damga"):
            out.append((b + t + 0.15 + 0.14, "damga", -13.0))
        if s_.get("hareket") == "yuvarlan":
            out.append((b + t + 0.05, "whoosh_kisa", -20.0))
            out.append((b + t + 0.55, "tik", -14.0))
    if z.get("hepsi") is not None:
        out.append((b + z["hepsi"], "pop", -14.0))
    return out


# ---------------------------------------------------------------- simgeler (kendi çizimimiz; marka logosu yok)

def imlec_spr(boy: float) -> Image.Image:
    """Ok imleç: beyaz dolgu, siyah kontur, hafif gölge. Ucu (0, 0)'da: sprite içindeki uç = (pad, pad)."""
    ss = 4
    pts = [(0, 0), (0, 0.78), (0.2, 0.6), (0.33, 0.92), (0.45, 0.87), (0.32, 0.56), (0.58, 0.56)]
    pad = 6
    w, h = int(boy * 0.62) + 2 * pad, int(boy) + 2 * pad
    lay = Image.new("RGBA", (w * ss, h * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    P = [((pad + x * boy) * ss, (pad + y * boy) * ss) for x, y in pts]
    d.polygon(P, fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=max(2, int(boy * 0.055 * ss)))
    lay = lay.resize((w, h), Image.LANCZOS)
    spr, ox, oy = C.golgeli(lay, boy * 0.06, 0.45, boy * 0.03, boy * 0.06)
    spr.info["uc"] = (ox + pad, oy + pad)
    return spr


def basparmak(boy: float, renk, kontur=(0, 0, 0)) -> Image.Image:
    """Başparmak yukarı simgesi (dolu)."""
    ss = 4
    n = int(boy * ss)
    lay = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    k = int(boy * 0.07 * ss)
    rk, kr = tuple(renk) + (255,), tuple(kontur) + (255,)
    # el (avuç): yuvarlak dikdörtgen + bilek
    d.rounded_rectangle((0.06 * n, 0.44 * n, 0.26 * n, 0.94 * n), radius=0.05 * n, fill=rk, outline=kr, width=k)
    avuc = [(0.32 * n, 0.46 * n), (0.5 * n, 0.12 * n), (0.6 * n, 0.08 * n), (0.66 * n, 0.2 * n), (0.6 * n, 0.4 * n),
            (0.88 * n, 0.4 * n), (0.95 * n, 0.5 * n), (0.88 * n, 0.92 * n), (0.32 * n, 0.92 * n)]
    d.polygon(avuc, fill=rk, outline=kr, width=k)
    d.line([(avuc[-1][0], avuc[0][1]), (avuc[-1][0], avuc[-1][1])], fill=kr, width=k)
    return lay.resize((int(boy), int(boy)), Image.LANCZOS)


def zil(boy: float, renk, kontur=(0, 0, 0)) -> Image.Image:
    """Zil simgesi (dolu); sallanma için pivot üst orta."""
    ss = 4
    n = int(boy * ss)
    lay = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    k = int(boy * 0.065 * ss)
    rk, kr = tuple(renk) + (255,), tuple(kontur) + (255,)
    govde = [(0.5 * n, 0.12 * n)]
    for i in range(0, 21):
        a = math.pi * i / 20
        govde.append((0.5 * n - 0.3 * n * math.cos(a), 0.42 * n - 0.28 * n * math.sin(a)))
    govde = [(0.18 * n, 0.72 * n), (0.2 * n, 0.42 * n)] + govde[1:] + [(0.8 * n, 0.42 * n), (0.82 * n, 0.72 * n),
                                                                       (0.92 * n, 0.8 * n), (0.08 * n, 0.8 * n)]
    d.polygon(govde, fill=rk, outline=kr, width=k)
    d.ellipse((0.4 * n, 0.8 * n, 0.6 * n, 0.95 * n), fill=rk, outline=kr, width=k)
    d.ellipse((0.45 * n, 0.04 * n, 0.55 * n, 0.15 * n), fill=rk, outline=kr, width=k)
    return lay.resize((int(boy), int(boy)), Image.LANCZOS)


def tik_isareti(boy: float, renk) -> Image.Image:
    ss = 4
    n = int(boy * ss)
    lay = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    ImageDraw.Draw(lay).line([(0.12 * n, 0.55 * n), (0.4 * n, 0.82 * n), (0.88 * n, 0.2 * n)],
                             fill=tuple(renk) + (255,), width=int(0.16 * n), joint="curve")
    return lay.resize((int(boy), int(boy)), Image.LANCZOS)


def _ust_uste(dst: Image.Image, src: Image.Image, x: int, y: int) -> None:
    """RGBA üstüne RGBA (alfa birleşimi), taşan kısım kırpılır."""
    l, t = max(0, -x), max(0, -y)
    r, b = min(src.width, dst.width - x), min(src.height, dst.height - y)
    if r <= l or b <= t:
        return
    dst.alpha_composite(src.crop((l, t, r, b)), (x + l, y + t))


# ---------------------------------------------------------------- sahne

class KapanisCizici(Cizici):
    def hazirla(self):
        p, S, W = self.p, self.S, self.W
        self.bindirme = bool(p.get("bindirme"))
        self.karart = float(p.get("karart", 0.6))
        self.donuk = None
        self.vurgu_renk = Z.renk(p.get("renk"), C.SARI)
        self.zemin = Z.Zemin(self.c, {"zemin": "foto" if p.get("arka") else "koyu", "arka": p.get("arka"),
                                      "arka_opak": 1 - self.karart, "bulanik": p.get("bulanik", 14)},
                             zm=1.07, ic=(34, 36, 44), dis=(6, 7, 9))
        self.z = kapanis_zamanlari(self.sahne)
        bos = p.get("bos_alan")
        self.bos = None if not bos else ("sag_ust" if bos is True else str(bos))
        # --- soru (üst)
        soru = p.get("soru")
        if soru is None and self.sahne.satirlar:
            soru = self.sahne.satirlar[0].altyazi
        self.soru_bolge = (80 * S, W - 80 * S) if not self.bos else \
            ((80 * S, W - 400 * S) if self.bos == "sag_ust" else (400 * S, W - 80 * S))
        self.kelimeler = []
        if soru:
            self._soru_hazirla(str(soru))
        self.ust = C.yazi(C.buyuk(str(p["ust"])), C.FONT_BOLD, 32 * S, self.vurgu_renk, aralik=0.24) \
            if p.get("ust") else None
        # --- tıklayan karakter (10. tur: kartlardan önce: kart sırası onun kutusundan kaçar)
        self.kar = self._karakter(p.get("karakter") or {})
        # --- seçenek kartları
        self.kartlar = []
        sec = p.get("secenekler") or []
        n = len(sec)
        if n:
            kw, kh = 400 * S, 420 * S
            ara = 80 * S if n < 3 else 64 * S
            top = (350 if self.bos else 300) * S
            x0 = W / 2 - (n * kw + (n - 1) * ara) / 2
            x0, kw, ara = self._kartlar_karakterden_kac(x0, top, n, kw, kh, ara)
            for i, s_ in enumerate(sec):
                self.kartlar.append(self._kart(s_, i, x0 + i * (kw + ara), top, kw, kh))
        # --- düğmeler
        self.dugmeler = {}
        self._dugmeler_hazirla()
        self.imlec = imlec_spr(58 * S)
        self.yorum_metin = self.z["metin"]
        self._yorum_cache: dict = {}
        self._yorum_satir = None

    # ---------------------------------------------------------------- hazırlık

    def _soru_hazirla(self, soru: str):
        S = self.S
        x0, x1 = self.soru_bolge
        maxw = x1 - x0
        boy = 78 * S
        while True:
            f = C.font(C.FONT_DIALOG, boy)
            kel = soru.split()
            satirlar, cur = [], []
            for k in kel:
                if cur and f.getlength(" ".join(cur + [k])) > maxw:
                    satirlar.append(cur)
                    cur = [k]
                else:
                    cur.append(k)
            satirlar.append(cur)
            if len(satirlar) <= 2 or boy < 50 * S:
                break
            boy -= 6 * S
        lh = boy * 1.14
        cx = (x0 + x1) / 2
        y_ilk = (120 if self.p.get("ust") else 90) * S
        i = 0
        for si, s_ in enumerate(satirlar):
            sw = f.getlength(" ".join(s_))
            x = cx - sw / 2
            for k in s_:
                spr = C.yazi(k, C.FONT_DIALOG, boy, C.BEYAZ, stroke=6 * S, golge=(0, 5 * S, 9 * S, 0.55),
                             dikey_kirp=False)
                self.kelimeler.append((spr, x, y_ilk + si * lh, i))
                x += f.getlength(k + " ")
                i += 1
        self.soru_alt = y_ilk + len(satirlar) * lh
        self.soru_cx = cx
        self.soru_w = max(f.getlength(" ".join(s_)) for s_ in satirlar)

    def _kartlar_karakterden_kac(self, x0: float, top: float, n: int, kw: float, kh: float,
                                 ara: float) -> tuple[float, float, float]:
        """10. tur (animasyon hakemi S8): kart sırası karakterin alfa kutusundan (+ sıçrama/onay payı 28 px) uzak
        dursun: anlatıcının başı A kartının sol alt köşesine ~40 px biniyordu. Önce sıra karakterden öteye kayar
        (en az kaydırma; kenarda 60 px kalır), yetmezse kart arası, sonra kart eni daralır."""
        S, W = self.S, self.W
        k = self.kar
        if not k or k.get("kutu") is None:
            return x0, kw, ara
        kx0, ky0, kx1, _ = k["kutu"]
        pay, kenar = 28 * S, 60 * S
        if ky0 - pay >= top + kh:          # karakter kartların altında kalıyor
            return x0, kw, ara
        if not k["sag"]:
            sol, sag = max(x0, kx1 + pay), W - kenar
        else:
            sol, sag = kenar, min(x0 + n * kw + (n - 1) * ara, kx0 - pay)
        if sol <= x0 and x0 + n * kw + (n - 1) * ara <= sag:
            return x0, kw, ara
        alan = sag - sol
        top_w = n * kw + (n - 1) * ara
        if top_w > alan:                    # sığmıyor: önce ara (en az 28 px), sonra kart eni (en az 300 px)
            ara = max(28 * S, (alan - n * kw) / max(n - 1, 1)) if n > 1 else ara
            top_w = n * kw + (n - 1) * ara
            if top_w > alan:
                kw = max(300 * S, (alan - (n - 1) * ara) / n)
                top_w = n * kw + (n - 1) * ara
        # en az kaydırma: sıra eski yerine en yakın, boşluğun içinde
        return min(max(x0, sol), sag - top_w), kw, ara

    def _kart(self, s_: dict, i: int, x: float, y: float, kw: float, kh: float) -> dict:
        S = self.S
        w, h = int(kw), int(kh)
        r = 22 * S
        pad = 12 * S
        plaka_h = (122 if s_.get("alt") else 78) * S   # 11. tur (animasyon S9): alt yazı 24 -> 34 px (telefonda okunmuyordu)
        ic_h = h - plaka_h - 2 * pad
        # iç görsel (kartın üst bölümü, yuvarlak köşeli pencere)
        ic = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        zemin = C.yuvarlak_kutu(w, h, r, (16, 18, 24, 228))
        ic.alpha_composite(zemin)
        kar = kar2 = None
        if s_.get("gorsel"):
            g = C.yukle(s_["gorsel"]).convert("RGBA")
            g2 = C.yukle(s_["vurgu_gorsel"]).convert("RGBA") if s_.get("vurgu_gorsel") else None
            if g2 is not None and g2.size == g.size:   # aynı tuval: ortak kırpım (yüz değişiminde zıplamaz)
                g, g2 = C.kirp_alfa([g, g2])
            else:
                g = C.kirp_alfa([g])[0]
                g2 = C.kirp_alfa([g2])[0] if g2 is not None else None
            seffaf = np.asarray(g.getchannel("A")).min() < 250
            if seffaf:   # karakter: büstü pencerenin altına oturur, içeri bakar
                faces, _ = facing.resolve(Path(s_["gorsel"]), s_.get("bakis"))
                cxn = (x + kw / 2) / self.W
                ayna = faces != "front" and facing.needs_flip(faces, cxn)
                hh = ic_h * 0.98

                def _sig(g):
                    if ayna:
                        g = ImageOps.mirror(g)
                    g = g.resize((max(1, round(g.width * hh / g.height)), round(hh)), Image.LANCZOS)
                    if g.width > w - 2 * pad:
                        ww = w - 2 * pad
                        g = g.resize((int(ww), max(1, round(g.height * ww / g.width))), Image.LANCZOS)
                    return g
                kar = _sig(g)
                kar2 = _sig(g2) if g2 is not None else None
            else:
                g = C.sigdir(g.convert("RGB"), w - 2 * pad, ic_h).convert("RGBA")
                ic.alpha_composite(g, (int((w - g.width) / 2), int(pad + (ic_h - g.height) / 2)))
        # plaka
        plaka = C.yuvarlak_kutu(int(w - 2 * pad), int(plaka_h), 12 * S, tuple(self.vurgu_renk) + (255,))
        ad = C.yazi(C.buyuk(str(s_["metin"])), C.FONT_BOLD, 40 * S, (14, 14, 16), max_w=w - 4 * pad, max_lines=1,
                    aralik=0.04)
        yy = (plaka_h - ad.height - ((30 * S) if s_.get("alt") else 0)) / 2
        plaka.alpha_composite(ad, (int((plaka.width - ad.width) / 2), int(yy)))
        if s_.get("alt"):
            alt = C.yazi(str(s_["alt"]), C.FONT_BOLD, 34 * S, (40, 34, 20), max_w=w - 3 * pad, max_lines=1,
                         min_size=28 * S)
            plaka.alpha_composite(alt, (int((plaka.width - alt.width) / 2), int(yy + ad.height + 8 * S)))
        # harf rozeti
        harf = str(s_.get("harf") or "ABC"[i])
        rz = int(84 * S)
        roz = Image.new("RGBA", (rz * 3, rz * 3), (0, 0, 0, 0))
        ImageDraw.Draw(roz).ellipse((6, 6, rz * 3 - 7, rz * 3 - 7), fill=tuple(self.vurgu_renk) + (255,),
                                    outline=(14, 14, 16, 255), width=int(5 * S * 3))
        roz = roz.resize((rz, rz), Image.LANCZOS)
        hz = C.yazi(harf, C.FONT_CARD, 56 * S, (14, 14, 16))
        roz.alpha_composite(hz, (int((rz - hz.width) / 2), int((rz - hz.height) / 2)))
        # 11. tur (animasyon S9): vurguda içerideki çizim de oynar: küçük lastik damga iner (kartın görselinin
        # ortasına, hafif eğik), yüz değişir (vurgu_gorsel), zar gibi döner (hareket: yuvarlan)
        dmg = None
        if s_.get("damga"):
            from .ust import damga_sprite
            d_ = s_["damga"]
            renk = Z.renk(d_.get("renk"), (176, 14, 30))
            dmg = damga_sprite(str(d_["metin"]), renk, (36 if kar is not None else 50) * S, S, tohum=7 + i,
                               kontur=(255, 255, 255))
        return {"x": x, "y": y, "w": w, "h": h, "ic": ic, "kar": kar, "pad": pad, "ic_h": ic_h, "plaka": plaka,
                "kar_pm": C.alt_piksel_hazirla(kar) if kar is not None else None,
                "kar2_pm": C.alt_piksel_hazirla(kar2) if kar2 is not None else None,
                "damga": dmg, "hareket": s_.get("hareket"),
                "plaka_h": plaka_h, "roz": roz, "r": r, "faz": 1.3 * i}

    def _karakter(self, kr: dict) -> dict:
        W, H = self.W, self.H
        yol = Path(kr.get("gorsel") or VARSAYILAN_KARAKTER)
        yuz = kr.get("yuz") or (VARSAYILAN_YUZ if not kr.get("gorsel") else None)
        yollar = [yol] + ([Path(yuz)] if yuz and Path(yuz).exists() else [])
        ims = [C.yukle(y_).convert("RGBA") for y_ in yollar]
        ims = C.kirp_alfa(ims) if len({im.size for im in ims}) == 1 else [C.kirp_alfa([im])[0] for im in ims]
        sag = kr.get("taraf", "sol") == "sag"
        cxn = 0.88 if sag else 0.12
        faces, _ = facing.resolve(yol, kr.get("bakis"))
        if faces != "front" and facing.needs_flip(faces, cxn):
            ims = [ImageOps.mirror(im) for im in ims]
        h = float(kr.get("boy", 0.34)) * H
        ims = [im.resize((max(1, round(im.width * h / im.height)), round(h)), Image.LANCZOS) for im in ims]
        w = ims[0].width
        cx = max(cxn * W, w * 0.42) if not sag else min(cxn * W, W - w * 0.42)
        taban = H + 0.04 * h
        # imlecin çıktığı yer: göğsünün önü (9. tur, animasyon S12: omuzdaki boşlukta beliriyordu, karakterle bağı
        # yoktu); imleç orada küçükten büyüyerek doğar ve oradan yola çıkar
        el = (cx + (0.2 if not sag else -0.2) * w, taban - 0.34 * h)
        bb = ims[0].getchannel("A").point(lambda v: 255 if v > 40 else 0).getbbox()
        kutu = (cx - w / 2 + bb[0], taban - h + bb[1], cx - w / 2 + bb[2], taban - h + bb[3]) if bb else None
        return {"ims": [C.alt_piksel_hazirla(im) for im in ims], "w": w, "h": h, "cx": cx, "taban": taban,
                "el": el, "sag": sag, "kutu": kutu}

    def _dugme(self, w: float, h: float, dolgu, kontur, simge, yazi: str | None, yazi_renk=C.BEYAZ) -> Image.Image:
        S = self.S
        w, h = int(w), int(h)
        lay = C.yuvarlak_kutu(w, h, h / 2, tuple(dolgu) + (255,), outline=tuple(kontur) + (255,), width=4 * S)
        x = 30 * S if yazi else (w - (simge.width if simge else 0)) / 2
        if simge is not None:
            lay.alpha_composite(simge, (int(x), int((h - simge.height) / 2)))
            x += simge.width + 14 * S
        if yazi:
            yz = C.yazi(yazi, C.FONT_BOLD, 38 * S, yazi_renk, aralik=0.03)
            lay.alpha_composite(yz, (int(x), int((h - yz.height) / 2)))
        spr, ox, oy = C.golgeli(lay, 14 * S, 0.5, 0, 6 * S)
        spr.info["o"] = (ox, oy)
        return spr

    def _dugmeler_hazirla(self):
        S, W = self.S, self.W
        bh = 96 * S
        sira = self.z["dugme_sira"]
        ol = {}
        sb = 46 * S
        if "abone" in sira:
            ab_w = max(C.yazi("ABONE OLUNDU", C.FONT_BOLD, 38 * S).width + sb + 84 * S,
                       C.yazi("ABONE OL", C.FONT_BOLD, 38 * S).width + 64 * S)
            ol["abone"] = {"w": ab_w,
                           "spr": [self._dugme(ab_w, bh, KIRMIZI_DUGME, C.BEYAZ, None, "ABONE OL"),
                                   self._dugme(ab_w, bh, GRI, (200, 202, 208), tik_isareti(sb, C.BEYAZ),
                                               "ABONE OLUNDU", (236, 236, 240))]}
            # "ABONE OL" yazısı ortada dursun
            yz = C.yazi("ABONE OL", C.FONT_BOLD, 38 * S, C.BEYAZ, aralik=0.03)
            lay = C.yuvarlak_kutu(int(ab_w), int(bh), bh / 2, KIRMIZI_DUGME + (255,), outline=C.BEYAZ + (255,),
                                  width=4 * S)
            lay.alpha_composite(yz, (int((ab_w - yz.width) / 2), int((bh - yz.height) / 2)))
            spr, ox, oy = C.golgeli(lay, 14 * S, 0.5, 0, 6 * S)
            spr.info["o"] = (ox, oy)
            ol["abone"]["spr"][0] = spr
        if "zil" in sira:
            ol["zil"] = {"w": bh, "spr": [self._dugme(bh, bh, KOYU_DUGME, C.BEYAZ, None, None)],
                         "simge": [zil(56 * S, C.BEYAZ), zil(56 * S, self.vurgu_renk)]}
        if "begen" in sira:
            bw = C.yazi("BEĞEN", C.FONT_BOLD, 38 * S).width + 56 * S + 30 * S + 14 * S + 30 * S
            ol["begen"] = {"w": bw, "spr": [self._dugme(bw, bh, KOYU_DUGME, C.BEYAZ, basparmak(56 * S, C.BEYAZ), "BEĞEN"),
                                           self._dugme(bw, bh, KOYU_DUGME, self.vurgu_renk,
                                                       basparmak(56 * S, self.vurgu_renk), "BEĞEN", self.vurgu_renk)]}
        if "yorum" in sira:
            ol["yorum"] = {"w": 600 * S}
        # yerleşim: karakterin yanından sağa, ortalı
        # karakterin yanından (8. tur: büyük karakterde düğmeler omzuna binmesin)
        k_ = self.kar
        sol = max(420 * S, k_["cx"] + 0.5 * k_["w"] + 24 * S) if (k_ and not k_["sag"]) else 90 * S
        sag = min(W - 420 * S, k_["cx"] - 0.5 * k_["w"] - 24 * S) if (k_ and k_["sag"]) else W - 90 * S
        ara = 24 * S
        top = sum(ol[d]["w"] for d in sira) + ara * (len(sira) - 1)
        if top > sag - sol and "yorum" in ol:
            ol["yorum"]["w"] = max(360 * S, ol["yorum"]["w"] - (top - (sag - sol)))
            top = sum(ol[d]["w"] for d in sira) + ara * (len(sira) - 1)
        x = sol + max(0.0, (sag - sol - top) / 2)
        cy = 862 * S
        for d in sira:
            ol[d]["x"], ol[d]["cy"] = x, cy
            x += ol[d]["w"] + ara
        self.dugmeler = ol
        self.dugme_h = bh

    # ---------------------------------------------------------------- çizim yardımcıları

    def dondur(self, onceki: Image.Image) -> None:
        self.donuk = onceki.copy()
        k = C.ayarla(onceki, bulanik=12 * self.S, karart=C.donuk_karart(onceki, self.karart, 50), doygunluk=0.6)
        C.vinyet_uygula(k, 0.45)
        self.donuk_k = k

    def _bas(self, hedef: str, t: float) -> float:
        """Düğmenin basılma çarpanı (tık anında 0,93'e iner, out_back ile döner)."""
        tt = self.z["tik"].get(hedef)
        if tt is None or t < tt:
            return 1.0
        u = t - tt
        if u < 0.08:
            return 1 - 0.07 * E.out_cubic(u / 0.08)
        return 0.93 + 0.07 * E.out_back((u - 0.08) / 0.35, 2.2)

    def _imlec_yeri(self, t: float) -> tuple[float, float, float] | None:
        """(x, y, alfa) imlecin ucu; yoksa None."""
        z = self.z
        if t < z["imlec"] or not self.kar:
            return None
        hedefler = [(tt, self._hedef_noktasi(h)) for h, tt in sorted(z["tik"].items(), key=lambda q: q[1])]
        if not hedefler:
            return None
        bas = self.kar["el"]
        a = E.out_cubic((t - z["imlec"]) / 0.25)
        onceki_t, onceki_p = z["imlec"], bas
        for tt, p in hedefler:
            git = min(0.65 * z["k"] + 0.1, max(0.2, tt - 0.05 - onceki_t))
            if t < tt - 0.05:
                u = E.in_out_cubic((t - (tt - 0.05 - git)) / git)
                # hafif yay: ortada yukarı
                mx, my = (onceki_p[0] + p[0]) / 2, min(onceki_p[1], p[1]) - 90 * self.S
                x = (1 - u) ** 2 * onceki_p[0] + 2 * (1 - u) * u * mx + u * u * p[0]
                y = (1 - u) ** 2 * onceki_p[1] + 2 * (1 - u) * u * my + u * u * p[1]
                return x, y, a
            onceki_t, onceki_p = tt, p
        # son tıktan sonra yorum balonunun yanına süzülüp söner
        son_t = hedefler[-1][0]
        u = E.in_out_sine((t - son_t - 0.3) / 0.8)
        hedef = onceki_p
        if "yorum" in self.dugmeler:
            yb = self.dugmeler["yorum"]
            hedef = (yb["x"] + 40 * self.S, yb["cy"] + 40 * self.S)
        x = onceki_p[0] + (hedef[0] - onceki_p[0]) * u
        y = onceki_p[1] + (hedef[1] - onceki_p[1]) * u
        sonme = 1 - E.in_out_sine((t - son_t - 1.6) / 0.5)
        return x, y, a * sonme

    def _hedef_noktasi(self, hedef: str) -> tuple[float, float]:
        d = self.dugmeler[hedef]
        return d["x"] + d["w"] * (0.5 if hedef != "abone" else 0.62), d["cy"] + 8 * self.S

    # ---------------------------------------------------------------- kare

    def ciz(self, t):
        S, W, H = self.S, self.W, self.H
        z = self.z
        if self.bindirme and self.donuk is not None:
            a = E.in_out_sine(t / 0.35)
            im = Image.blend(self.donuk, self.donuk_k, a) if a < 0.999 else self.donuk_k.copy()
            zz = 1.0 + 0.03 * E.in_out_sine(t / self.dur)
            im = C.kamera(im, W, H, zz, (0.5, 0.5))
            C.gren_uygula(im, t, 0.04)
        else:
            im = self.zemin.ciz(t, self.dur)
        self._soru(im, t)
        for i, k in enumerate(self.kartlar):
            self._kart_ciz(im, t, i, k)
        self._karakter_ciz(im, t)
        self._dugmeler_ciz(im, t)
        ip = self._imlec_yeri(t)
        if ip is not None:
            x, y, a = ip
            bas = 1.0
            for tt in z["tik"].values():
                if 0 <= t - tt < 0.16:
                    bas = 1 - 0.15 * E.tumsek((t - tt) / 0.16)
                if 0 <= t - tt < 0.45:   # tık halkası
                    q = (t - tt) / 0.45
                    rr = (10 + 46 * E.out_cubic(q)) * S
                    lay = Image.new("RGBA", (int(2 * rr + 8), int(2 * rr + 8)), (0, 0, 0, 0))
                    ImageDraw.Draw(lay).ellipse((4, 4, 4 + 2 * rr, 4 + 2 * rr), outline=(255, 255, 255, 255),
                                                width=max(1, int(5 * S * (1 - q) + 1)))
                    C.bindir_alt(im, lay, x - rr - 4, y - rr - 4, (1 - q) * 0.9)
            ux, uy = self.imlec.info["uc"]
            dog = (t - z["imlec"]) / 0.3
            if dog < 1:   # 9. tur: imleç karakterin önünde küçükten büyüyerek doğar
                bas *= 0.35 + 0.65 * max(0.0, E.out_back(dog, 1.8))
            if abs(bas - 1) > 1e-3:
                spr, x0, y0 = C.afin(self.imlec, x, y, bas, bas, 0, ux, uy)
                C.bindir(im, spr, x0, y0, a)
            else:
                C.bindir_alt(im, self.imlec, x - ux, y - uy, a)
        # 9. tur (animasyon S12): son ~1,8 sn durağan değil: bütün kare hafifçe yaklaşır (son müzik vuruşuyla)
        q = (t - (self.dur - 1.8)) / 1.8
        if q > 0:
            im = C.kamera(im, W, H, 1.0 + 0.035 * E.in_out_sine(min(1.0, q)), (0.5, 0.52))
        return im

    def _soru(self, im, t):
        S = self.S
        z = self.z
        if self.ust is not None:
            a = E.out_cubic((t - z["soru"] + 0.1) / 0.4)
            C.bindir_alt(im, self.ust, self.soru_cx - self.ust.width / 2, 62 * S - (1 - a) * 10 * S, a)
        for spr, x, y, i in self.kelimeler:
            u = (t - z["soru"] - 0.09 * i) / 0.32
            if u <= 0:
                continue
            a = E.out_cubic(u)
            yy = y + Z.suzul(t, 0.7, 2.0) * S + (1 - a) * 26 * S
            C.bindir_alt(im, spr, x, yy, a)
        if self.kelimeler:
            son = z["soru"] + 0.09 * len(self.kelimeler) + 0.1
            lw = (self.soru_w / 2 + 30 * S) * E.out_cubic((t - son) / 0.5)
            if lw > 1:
                y = self.soru_alt + 14 * S + Z.suzul(t, 0.7, 2.0) * S
                bar = Image.new("RGBA", (int(2 * lw), max(1, int(6 * S))), tuple(self.vurgu_renk) + (255,))
                C.bindir_alt(im, bar, self.soru_cx - lw, y)

    def _vurgu(self, t: float, i: int) -> float:
        """Kartın vurgu düzeyi (0..1): vurgu anından itibaren; bir sonraki vurguda söner, sonuncusu 0,9 sn sonra
        (sahne hiçbir seçeneği 'doğru cevap' gibi işaretli bırakmaz)."""
        v = 0.0
        vs = self.z["vurgu"]
        hepsi = self.z.get("hepsi")
        for j, (tt, idx) in enumerate(vs):
            if idx - 1 != i or t < tt:
                continue
            son = vs[j + 1][0] if j + 1 < len(vs) else (hepsi if hepsi is not None else tt + 0.9)
            v = E.out_cubic((t - tt) / 0.2) * (1 - E.in_out_sine((t - son) / 0.3))
        if hepsi is not None and t >= hepsi:   # üçü birden: nabız, sonra eşit ve hafif vurguda kalır
            vh = E.out_cubic((t - hepsi) / 0.2) * (1 - 0.6 * E.in_out_sine((t - hepsi - 0.3) / 0.45))
            v = max(v, vh)
        return v

    def _kart_ciz(self, im, t, i, k):
        S = self.S
        t0 = self.z["kartlar"][i]
        u = (t - t0) / 0.45
        if u <= 0:
            return
        a = min(1.0, u * 2.5)
        s = 0.82 + 0.18 * E.out_back(u, 1.6)
        v = self._vurgu(t, i)
        ilk_vurgu = next((tt for tt, idx in self.z["vurgu"] if idx - 1 == i and t >= tt), None)
        zip_ = E.tumsek((t - ilk_vurgu) / 0.35) if ilk_vurgu is not None else 0.0
        if self.z.get("hepsi") is not None and t >= self.z["hepsi"]:
            zip_ = max(zip_, E.tumsek((t - self.z["hepsi"]) / 0.35))
        s *= 1 + 0.05 * v + 0.03 * zip_
        dy = (1 - E.out_cubic(u)) * 40 * S + Z.suzul(t, k["faz"], 3.0) * S
        lay = k["ic"].copy()
        tepki = (t - ilk_vurgu) if ilk_vurgu is not None else None   # 11. tur: kartın ilk vurgusundan beri (sn)
        if k["kar"] is not None:   # karakter pencerede, altı plakanın arkasında; vurguda sıçrar
            g = k["kar"]
            pm = k["kar2_pm"] if (k["kar2_pm"] is not None and tepki is not None and tepki >= 0.06) else k["kar_pm"]
            nefes = 1 + 0.008 * math.sin(2 * math.pi * 0.3 * t + k["faz"])
            sq = E.tumsek((tepki - 0.06 + 0.13) / 0.26) if (tepki is not None and k["kar2_pm"] is not None) else 0.0
            gx = (k["w"] - g.width) / 2
            # büstün kesik alt kenarı plakanın arkasında kalır
            gy = 2 * k["pad"] + k["ic_h"] + 14 * S - g.height * nefes - 18 * S * zip_
            pencere = Image.new("RGBA", lay.size, (0, 0, 0, 0))
            if k["hareket"] == "yuvarlan" and tepki is not None and tepki < 0.75:
                # zar gibi: bir tur döner, sekerek oturur (pivot ortası)
                q = tepki / 0.75
                aci = -360 * E.out_cubic(q)
                hop = 34 * S * E.tumsek(q / 0.7)
                w0, h0 = pm.width - 2 * C.ALT_PAY, pm.height - 2 * C.ALT_PAY
                spr, x0, y0 = C.afin_pm(pm, gx + w0 / 2, gy + h0 * nefes / 2 - hop, 1.0, nefes, aci,
                                        C.ALT_PAY + w0 / 2, C.ALT_PAY + h0 / 2)
            else:
                spr, x0, y0 = C.alt_piksel(pm, gx - g.width * 0.02 * sq, gy + g.height * 0.06 * sq,
                                           1.0 + 0.04 * sq, nefes * (1 - 0.06 * sq))
            _ust_uste(pencere, spr, x0, y0)
            maske = C.yuvarlak_kutu(k["w"], k["h"], k["r"], (255, 255, 255, 255)).getchannel("A")
            pencere.putalpha(Image.fromarray(np.minimum(np.asarray(pencere.getchannel("A")),
                                                        np.asarray(maske)), "L"))
            lay.alpha_composite(pencere)
        if k["damga"] is not None and tepki is not None and tepki >= 0.15:
            # lastik damga görselin ortasına iner (ust.Damga gibi: büyükten 0,14 sn'de çarpar, sonra kalır)
            q = (tepki - 0.15) / 0.14
            ds = 1.0 + 0.7 * (1 - E.out_cubic(min(1.0, q)))
            da = min(1.0, q * 1.6)
            dm = k["damga"]
            # karakterli kartta yüze/ağza değil başın yanındaki boşluğa (sol üst; yüz değişimi görünsün, gerçek kişinin
            # yüzü ya da ağzı damgalanmaz), belgede ortaya
            if k["kar"] is not None:
                dcx, dcy = k["w"] * 0.22, k["pad"] + k["ic_h"] * 0.2
            else:
                dcx, dcy = k["w"] / 2, k["pad"] + k["ic_h"] * 0.72   # belgenin başlığı (1928) açık kalsın
            out_d, dx0, dy0 = C.afin(dm, dcx, dcy, ds, ds, -7, dm.width / 2, dm.height / 2)
            out_d = out_d.copy()
            if da < 1:
                out_d.putalpha(out_d.getchannel("A").point(lambda v: int(v * da)))
            _ust_uste(lay, out_d, dx0, dy0)
        lay.alpha_composite(k["plaka"], (int(k["pad"]), int(k["h"] - k["pad"] - k["plaka_h"])))
        # çerçeve: beyaz; vurguda kalın sarı
        kal = (4 + 5 * v) * S
        renk = tuple(int(E.karistir(255, c_, v)) for c_ in self.vurgu_renk)
        cer = C.yuvarlak_kutu(k["w"], k["h"], k["r"], (0, 0, 0, 0), outline=renk + (255,), width=kal)
        lay.alpha_composite(cer)
        spr, gx_, gy_ = C.golgeli(lay, 18 * S, 0.55, 0, 10 * S)
        cx, cy = k["x"] + k["w"] / 2, k["y"] + k["h"] / 2 + dy
        out, x0, y0 = C.afin(spr, cx, cy, s, s, 0, gx_ + k["w"] / 2, gy_ + k["h"] / 2)
        C.bindir(im, out, x0, y0, a)
        # harf rozeti: kartın sol üst köşesinde, kartla birlikte; vurguda zıplar
        rs = s * (1 + 0.15 * zip_)
        rx = cx - k["w"] / 2 * s + 6 * S
        ry = cy - k["h"] / 2 * s + 6 * S - 10 * S * zip_
        ro, rx0, ry0 = C.afin(k["roz"], rx, ry, rs, rs, -8 * (1 - E.out_cubic(u)))
        C.bindir(im, ro, rx0, ry0, a)

    def _karakter_ciz(self, im, t):
        kr = self.kar
        if not kr:
            return
        S = self.S
        t0 = self.z["karakter"]
        u = (t - t0) / 0.7
        if u <= 0:
            return
        e = E.out_back(u, 1.2)
        dy = (1 - e) * (kr["h"] * 1.06 + 40 * S)
        hop = 0.0
        for tt in self.z["tik"].values():
            hop = max(hop, E.tumsek((t - tt + 0.02) / 0.3))
        abone_t = self.z["tik"].get("abone")
        vi = 1 if (len(kr["ims"]) > 1 and abone_t is not None and t >= abone_t + 0.05) else 0
        sq = E.tumsek((t - (abone_t or -9) - 0.05 + 0.13) / 0.26) if len(kr["ims"]) > 1 else 0.0
        nefes = 1 + 0.01 * math.sin(2 * math.pi * 0.3 * t)
        sy, sx = nefes * (1 - 0.06 * sq), nefes * (1 + 0.04 * sq)
        dy += -12 * S * hop + 3 * S * math.sin(2 * math.pi * 0.21 * t)
        src = kr["ims"][vi]
        w0, h0 = src.width - 2 * C.ALT_PAY, src.height - 2 * C.ALT_PAY
        # 8. tur (animasyon hakemi S1): anlatıcı edilgen kalmasın: yorum balonu yazılırken ona doğru eğilir (en çok
        # 5°), her seçenek vurgusunda başıyla küçük bir onay verir
        z = self.z
        yon = -1.0 if not kr["sag"] else 1.0            # solda duran sağa (balona) eğilir: saat yönü (-)
        egil = E.in_out_sine((t - z["yorum"] + 0.2) / 0.5) * (1 - E.in_out_sine((t - z["yorum_bitis"] - 0.2) / 0.6))
        aci = 5.0 * yon * egil
        for tt, _ in z["vurgu"]:
            aci += 2.2 * yon * E.tumsek((t - tt) / 0.32)
        if z.get("hepsi") is not None:
            aci += 2.5 * yon * E.tumsek((t - z["hepsi"]) / 0.4)
        if abs(aci) < 0.02:
            spr, x0, y0 = C.alt_piksel(src, kr["cx"] - w0 * sx / 2, kr["taban"] + dy - h0 * sy, sx, sy)
        else:
            spr, x0, y0 = C.afin_pm(src, kr["cx"], kr["taban"] + dy, sx, sy, aci, C.ALT_PAY + w0 / 2, C.ALT_PAY + h0)
        C.bindir(im, spr, x0, y0)

    def _dugmeler_ciz(self, im, t):
        S = self.S
        z = self.z
        for j, ad in enumerate(z["dugme_sira"]):
            d = self.dugmeler[ad]
            t0 = z["dugmeler"][j]
            u = (t - t0) / 0.4
            if u <= 0:
                continue
            a = min(1.0, u * 2.5)
            gy = (1 - E.out_back(u, 1.4)) * 70 * S
            if ad == "yorum":
                self._yorum_ciz(im, t, d, gy, a)
                continue
            tt = z["tik"].get(ad)
            durum = 1 if (tt is not None and t >= tt + 0.04) else 0
            sprs = d["spr"]
            spr = sprs[min(durum, len(sprs) - 1)]
            ox, oy = spr.info.get("o", (0, 0))
            s = self._bas(ad, t)
            if ad == "begen" and tt is not None and t >= tt:
                s *= 1 + 0.08 * E.tumsek((t - tt - 0.05) / 0.3)
            cx, cy = d["x"] + d["w"] / 2, d["cy"] + gy
            out, x0, y0 = C.afin(spr, cx, cy, s, s, 0, ox + d["w"] / 2, oy + self.dugme_h / 2)
            C.bindir(im, out, x0, y0, a)
            if ad == "zil":   # simge: tıkta sallanır (sönümlü), çınlama çizgileri
                simge = d["simge"][durum]
                aci = 0.0
                if tt is not None and t >= tt:
                    q = t - tt
                    aci = 24 * math.exp(-q / 0.32) * math.sin(2 * math.pi * 4.2 * q)
                sp, sx0, sy0 = C.afin(simge, cx, cy - 22 * S * s, s, s, aci, simge.width / 2, 0.08 * simge.height)
                C.bindir(im, sp, sx0, sy0, a)
                if tt is not None and 0 <= t - tt < 0.9:
                    q = (t - tt) / 0.9
                    lay = Image.new("RGBA", (int(d["w"] * 2), int(d["w"] * 2)), (0, 0, 0, 0))
                    dr = ImageDraw.Draw(lay)
                    c0 = d["w"]
                    for k_, yon in ((0, -1), (1, -1), (0, 1), (1, 1)):
                        r = (0.55 + 0.12 * k_ + 0.25 * q) * d["w"]
                        bas = 200 if yon < 0 else -20
                        dr.arc((c0 - r, c0 - r, c0 + r, c0 + r), bas, bas + 40, fill=tuple(self.vurgu_renk) + (255,),
                               width=max(1, int(5 * S)))
                    C.bindir(im, lay, cx - c0, cy - c0, (1 - q) * a)
            if ad == "begen" and tt is not None and 0 <= t - tt < 0.6:   # kıvılcım
                q = (t - tt) / 0.6
                lay = Image.new("RGBA", (int(320 * S), int(320 * S)), (0, 0, 0, 0))
                dr = ImageDraw.Draw(lay)
                c0 = 160 * S
                bx = d["x"] + 30 * S + 28 * S - cx
                for k_ in range(8):
                    ang = 2 * math.pi * k_ / 8 + 0.3
                    r0, r1 = (40 + 70 * E.out_cubic(q)) * S, (52 + 96 * E.out_cubic(q)) * S
                    dr.line((c0 + bx + r0 * math.cos(ang), c0 + r0 * math.sin(ang), c0 + bx + r1 * math.cos(ang),
                             c0 + r1 * math.sin(ang)), fill=tuple(self.vurgu_renk) + (255,), width=max(1, int(6 * S)))
                C.bindir(im, lay, cx - c0, cy - c0, (1 - q) * a)

    def _yorum_ciz(self, im, t, d, gy, a):
        """Yorum balonu: beyaz konuşma balonu, kuyruğu sol altta; soru daktiloyla yazılır."""
        S = self.S
        z = self.z
        n = 0
        if t >= z["yorum"]:
            n = min(len(self.yorum_metin), int((t - z["yorum"]) * YORUM_HIZI) + 1)
        imlec = n < len(self.yorum_metin) or int(t * 2.2) % 2 == 0
        key = (n, imlec and t >= z["yorum"] - 0.3)
        spr = self._yorum_cache.get(key)
        if spr is None:
            w = int(d["w"])
            h = int(118 * S)
            kuyruk = 26 * S
            ss = 3
            lay = Image.new("RGBA", (w * ss, int((h + kuyruk) * ss)), (0, 0, 0, 0))
            dr = ImageDraw.Draw(lay)
            k = int(4.5 * S * ss)
            dr.rounded_rectangle((0, 0, w * ss - 1, h * ss - 1), radius=int(28 * S * ss), fill=(0, 0, 0, 255))
            tri = [(40 * S * ss, (h - 4 * S) * ss), (96 * S * ss, (h - 4 * S) * ss), (34 * S * ss, (h + kuyruk) * ss)]
            dr.polygon(tri, fill=(0, 0, 0, 255))
            dr.rounded_rectangle((k, k, w * ss - 1 - k, h * ss - 1 - k), radius=int(24 * S * ss), fill=(255, 255, 255, 255))
            tri2 = [(48 * S * ss, (h - 9 * S) * ss), (88 * S * ss, (h - 9 * S) * ss), (40 * S * ss, (h + kuyruk - 8 * S) * ss)]
            dr.polygon(tri2, fill=(255, 255, 255, 255))
            lay = lay.resize((w, int(h + kuyruk)), Image.LANCZOS)
            # satırlar tam metne göre bir kez kırılır (yazılırken kelime satır değiştirmez)
            if self._yorum_satir is None:
                from .. import text as wtext
                if "\n" in self.yorum_metin:   # elle kırılmış: en uzun satır sığana dek küçült
                    satirlar = self.yorum_metin.split("\n")[:2]
                    boy = int(38 * S)
                    f = C.font(C.FONT_DIALOG, boy)
                    while boy > 22 * S and max(f.getlength(x) for x in satirlar) > w - 60 * S:
                        boy -= 2
                        f = C.font(C.FONT_DIALOG, boy)
                else:
                    f, satirlar, _ = wtext.fit_text(self.yorum_metin, C.FONT_DIALOG, int(38 * S), int(w - 60 * S), 2,
                                                    min_size=int(26 * S))
                self._yorum_satir = (f, satirlar)
            f, satirlar = self._yorum_satir
            dr2 = ImageDraw.Draw(lay)
            asc, desc = f.getmetrics()
            lh = f.size * 1.12
            y0 = (h - (lh * (len(satirlar) - 1) + asc + desc)) / 2
            kalan = n
            cx_, cy_ = 28 * S, y0
            if n == 0:   # yer tutucu: YouTube yorum kutusu gibi soluk "Yorum ekle..."
                dr2.text((28 * S, (h - asc - desc) / 2), "Yorum ekle…", font=f, fill=(150, 152, 158, 255))
            for i_, sat in enumerate(satirlar):
                if kalan <= 0:
                    break
                parca = sat[:kalan]
                dr2.text((28 * S, y0 + i_ * lh), parca, font=f, fill=(14, 14, 16, 255))
                cx_, cy_ = 28 * S + f.getlength(parca) + 4 * S, y0 + i_ * lh
                kalan -= len(sat) + 1
            if key[1] and n > 0:
                dr2.rectangle((cx_, cy_ + 4 * S, cx_ + 4 * S, cy_ + asc + desc * 0.3), fill=(14, 14, 16, 255))
            spr, ox, oy = C.golgeli(lay, 14 * S, 0.45, 0, 6 * S)
            spr.info["o"] = (ox, oy)
            if len(self._yorum_cache) > 8:
                self._yorum_cache.clear()
            self._yorum_cache[key] = spr
        ox, oy = spr.info["o"]
        C.bindir(im, spr, d["x"] - ox, d["cy"] - 59 * S + gy - oy, a)
