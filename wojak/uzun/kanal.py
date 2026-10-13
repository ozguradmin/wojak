"""Kanal öğeleri: kanal imzası (sting, `marka`) ve YouTube bitiş ekranı (`bitis`).

marka (~1,8 sn; soğuk açılıştan sonra): koyu zemin (ya da `bindirme: true` ile donmuş, kararmış son kare);
sarı fosforlu şerit soldan geçerken `tarihselwojak` yazısı onun arkasından belirir, solda kanalın klasik
wojak'ı aşağıdan yükselir ve imza anında gülümser; sonunda yazı küçülüp filigranın yerine uçar (bir sonraki
sahnede filigran tam oradadır). Efekt: `marka` (whoosh + Do minör akor).

bitis (son 15-20 sn): bulanık-karartılmış arka plan (ya da donmuş son kare), üstte kapanış cümlesi, YouTube
Studio bitiş ekranı öğeleri için iki boş 16:9 kutu ve bir abone dairesi. Yerleşim YouTube'un 'kenarlardan uzak,
alt %10'u oynatıcı denetimlerine bırak' kuralına göre (BITIS_DUZENLERI). Kutular ve daire hafifçe nabız atar.
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

from .. import config, facing
from . import cizim as C
from . import easing as E
from . import zemin as Z
from .sahneler import Baglam, Cizici, filigran_katmani

MARKA_SURE = 1.8
VARSAYILAN_WOJAK = config.ASSETS / "kit" / "klasik" / "sakin.png"
VARSAYILAN_YUZ = config.ASSETS / "kit" / "klasik" / "mutlu.png"


def logotip(metin: str, c: Baglam, boy: float) -> Image.Image:
    """Kanal yazısı (filigranla aynı stil: kanal fontu, siyah kontur, italik), büyük boy, sıkı kırpılmış."""
    from .. import text as wtext
    S = c.S
    lay = wtext.text_block(metin, font_path=config.FONT_DIALOG, size=max(10, round(boy)), max_w=round(1750 * S),
                           max_lines=1, stroke_ratio=0.09, pitch=1.1, shadow=True, shear=config.DIALOG_SHEAR)
    bb = lay.getchannel("A").getbbox()
    return lay.crop(bb) if bb else lay


# ================================================================ marka imzası (sting)

def _rozet(im: Image.Image, cap: int, S: float, ayna: bool) -> Image.Image:
    """Yuvarlak kanal avatarı: koyu daire içinde wojak'ın başı ve omzu, sarı halka, gölge."""
    im = C.kirp_alfa([im])[0]
    if ayna:
        im = ImageOps.mirror(im)
    w = int(cap * 1.08)
    h = max(1, round(im.height * w / im.width))
    im = im.resize((w, h), Image.LANCZOS)
    ss = 3
    maske = Image.new("L", (cap * ss, cap * ss), 0)
    ImageDraw.Draw(maske).ellipse((0, 0, cap * ss - 1, cap * ss - 1), fill=255)
    maske = maske.resize((cap, cap), Image.LANCZOS)
    ic = Image.new("RGBA", (cap, cap), (36, 38, 46, 255))
    ic.alpha_composite(im, ((cap - w) // 2, int(0.12 * cap)))
    ic.putalpha(maske)
    halka = Image.new("RGBA", (cap * ss, cap * ss), (0, 0, 0, 0))
    k = int(0.045 * cap * ss)
    ImageDraw.Draw(halka).ellipse((k // 2, k // 2, cap * ss - 1 - k // 2, cap * ss - 1 - k // 2), outline=C.SARI + (255,),
                                  width=k)
    ic.alpha_composite(halka.resize((cap, cap), Image.LANCZOS))
    spr, _, _ = C.golgeli(ic, 14 * S, 0.55, 0, 6 * S)
    return spr


def marka_zamanlari(sahne) -> dict:
    """Animasyonun anları (sahne içi sn); süre 1,8 sn'den farklıysa orantılı."""
    k = (sahne.sure_hesap or MARKA_SURE) / MARKA_SURE
    return {"serit": 0.10 * k, "serit_son": 0.42 * k, "wojak": 0.22 * k, "gulumse": 0.72 * k,
            "ucus": 1.18 * k, "ucus_son": 1.70 * k, "k": k}


class MarkaCizici(Cizici):
    def hazirla(self):
        p, S, W, H = self.p, self.S, self.W, self.H
        self.bindirme = bool(p.get("bindirme"))
        self.karart = float(p.get("karart", 0.72))
        self.donuk = None
        metin = str(p.get("yazi") or self.c.v.filigran or config.WATERMARK)
        self.logo = logotip(metin, self.c, 150 * S)
        self.wm = filigran_katmani(metin, self.c)          # (katman, x, y): son karede tam bu konum
        self.zm = marka_zamanlari(self.sahne)
        if p.get("arka"):
            g = C.ayarla(C.kapla(C.yukle(p["arka"]).convert("RGB"), W, H), bulanik=16 * S, karart=0.6,
                         doygunluk=0.6)
            C.vinyet_uygula(g, 0.5)
            self.zem = g
        else:
            self.zem = C.gradyan_zemin(W, H, (30, 30, 36), (3, 3, 5), (0.5, 0.48))
        # wojak rozeti (solda, sağa bakar): yuvarlak kanal avatarı, imza anında gülümseyen yüze geçer
        yollar = [Path(p.get("wojak") or VARSAYILAN_WOJAK)]
        yuz = Path(p.get("yuz") or VARSAYILAN_YUZ) if (p.get("yuz") or not p.get("wojak")) else None
        if yuz is not None and yuz.exists():
            yollar.append(yuz)
        faces, _ = facing.resolve(yollar[0], None)
        ayna = faces != "front" and facing.needs_flip(faces, 0.3)
        lw, lh = self.logo.width, self.logo.height
        self.cap = int(1.8 * lh)
        self.rozetler = [_rozet(C.yukle(y).convert("RGBA"), self.cap, S, ayna) for y in yollar]
        bosluk = 0.14 * self.cap
        toplam = self.cap + bosluk + lw
        self.rx = W / 2 - toplam / 2 + self.cap / 2               # rozet merkezi
        self.lx = self.rx + self.cap / 2 + bosluk + lw / 2       # logo merkezi
        self.ly = self.ry = H * 0.5
        self.isik = Z._isik(int(900 * S)).point(C._alfa_lut(int(255 * 0.16)))

    def dondur(self, onceki: Image.Image) -> None:
        self.donuk = onceki.copy()
        k = C.ayarla(onceki, bulanik=10 * self.S, karart=C.donuk_karart(onceki, self.karart, 45), doygunluk=0.6)
        C.vinyet_uygula(k, 0.4)
        self.donuk_k = k

    def ciz(self, t):
        S = self.S
        z = self.zm
        k = z["k"]
        if self.bindirme and self.donuk is not None:
            a = E.out_cubic(t / 0.2)
            im = Image.blend(self.donuk, self.donuk_k, a) if a < 0.999 else self.donuk_k.copy()
        else:
            im = self.zem.copy()
        # imzanın arkasında açılan sıcak ışık
        ia = E.out_cubic((t - z["serit"]) / (0.4 * k)) * (1 - E.in_cubic((t - z["ucus"]) / (0.35 * k)))
        if ia > 0.01:
            cap = self.isik.width
            m = self.isik if ia > 0.99 else self.isik.point(C._alfa_lut(int(255 * ia)))
            im.paste((255, 214, 140), (int(self.lx - cap / 2), int(self.ly - cap / 2)), m)
        C.gren_uygula(im, t, 0.05)
        lg = self.logo
        ucus = E.in_out_cubic((t - z["ucus"]) / (z["ucus_son"] - z["ucus"]))
        # rozet: dönerek büyür, imzada gülümser (kısa sıkışma), uçuşta küçülüp kaybolur
        ru = E.out_back((t - z["wojak"]) / (0.38 * k), 1.6)
        if ru > 0.001:
            vi = 1 if (len(self.rozetler) > 1 and t >= z["gulumse"]) else 0
            b = E.tumsek((t - z["gulumse"] + 0.12) / 0.26) if len(self.rozetler) > 1 else 0.0
            kucul = 1 - E.in_cubic((t - z["ucus"]) / (0.32 * k))
            s = max(0.0, ru) * kucul
            if s > 0.01:
                spr, x0, y0 = C.afin(self.rozetler[vi], self.rx, self.ry + 3 * S * math.sin(2 * math.pi * 0.7 * t),
                                     s * (1 + 0.05 * b), s * (1 - 0.06 * b), -14 * (1 - min(1.0, ru)))
                C.bindir(im, spr, x0, y0, min(1.0, kucul * 1.5))
        # fosforlu şerit: soldan sağa geçer, sonra incelip alt çizgiye döner
        su = E.in_out_cubic((t - z["serit"]) / (z["serit_son"] - z["serit"]))
        x_bas = self.lx - lg.width / 2 - 16 * S
        x_kenar = x_bas + (lg.width + 32 * S) * su
        if su > 0:
            ince = E.in_out_cubic((t - z["serit_son"]) / (0.3 * k))
            sh = lg.height * (0.58 - 0.5 * ince)
            sy0 = self.ly - lg.height * 0.18 + ince * lg.height * 0.52
            sa = 1 - E.in_cubic((t - z["ucus"]) / (0.2 * k))
            if sa > 0.01:
                serit = Image.new("RGB", (max(1, int(x_kenar - x_bas)), max(1, int(sh))), C.SARI)
                C.bindir(im, serit, x_bas, sy0 - sh / 2, sa * 0.95)
        # imza: şeridin arkasından açılır, sonra filigranın yerine uçar
        if su > 0:
            wm, wx, wy = self.wm
            s_son = wm.width / lg.width
            s = E.karistir(1.0, s_son, ucus) * (1 + 0.025 * E.tumsek((t - z["serit_son"]) / 0.4))
            cx = E.karistir(self.lx, wx + wm.width / 2, ucus)
            cy = E.karistir(self.ly, wy + wm.height / 2, ucus)
            gorunur = lg
            if ucus <= 0:
                n = int(max(0, min(lg.width, x_kenar - (self.lx - lg.width / 2))))
                gorunur = lg.crop((0, 0, max(1, n), lg.height)) if n < lg.width else lg
                if n <= 0:
                    gorunur = None
            if gorunur is not None:
                son_a = 1 - E.lineer((t - (z["ucus_son"] - 0.1)) / 0.1)   # son anda gerçek filigranla değişir
                spr, x0, y0 = C.afin(gorunur, cx - (lg.width - gorunur.width) / 2 * s, cy, s, s)
                C.bindir(im, spr, x0, y0, son_a)
            if t >= z["ucus_son"] - 0.1:
                C.bindir(im, wm, wx, wy, E.lineer((t - (z["ucus_son"] - 0.1)) / 0.1) * 0.9)
        return im


# ================================================================ bitiş ekranı

# 1920x1080 ölçeğinde: (kutular [(x, y, w, h)], abone (cx, cy, çap), başlık (x, y, genişlik, hizalama))
BITIS_DUZENLERI = {
    "yan_yana": ([(176, 268, 736, 414), (1008, 268, 736, 414)], (960, 856, 216), (210, 92, 1500, "center")),
    "sag": ([(1096, 120, 704, 396), (1096, 564, 704, 396)], (520, 640, 280), (120, 150, 860, "left")),
    "sol": ([(120, 120, 704, 396), (120, 564, 704, 396)], (1400, 640, 280), (940, 150, 860, "left")),
}


def bitis_zamanlari(sahne) -> dict:
    n = int(sahne.p.get("kutular", 2))
    return {"baslik": 0.15, "kutular": [0.35 + 0.15 * i for i in range(n)], "abone": 0.35 + 0.15 * n,
            "karakter": 0.5 + 0.15 * n}


class BitisCizici(Cizici):
    def hazirla(self):
        p, S, W, H = self.p, self.S, self.W, self.H
        self.bindirme = bool(p.get("bindirme"))
        self.karart = float(p.get("karart", 0.62))
        self.donuk = None
        # zemin: bulanık-karartılmış fotoğraf (ya da koyu) + toz, gezinen ışık, süzülme (zemin.py)
        self.zemin = Z.Zemin(self.c, {"zemin": "foto" if p.get("arka") else "koyu", "arka": p.get("arka"),
                                      "arka_opak": 1 - self.karart, "bulanik": p.get("bulanik", 14)},
                             zm=1.07, ic=(34, 36, 44), dis=(6, 7, 9))
        self.z = bitis_zamanlari(self.sahne)
        duzen = p.get("duzen", "yan_yana")
        kutular, abone, bas = BITIS_DUZENLERI[duzen]
        n = int(p.get("kutular", 2))
        kt = list(kutular[:n])
        if n == 1:   # tek kutu: yan yana düzende yatay, yan düzenlerde dikey ortada
            x, y, w, h = kutular[0]
            kt = [((1920 - w) / 2, y, w, h)] if duzen == "yan_yana" else [(x, (1080 - h) / 2, w, h)]
        self.kutular = [tuple(v * S for v in k) for k in kt]
        self.abone = (abone[0] * S, abone[1] * S, abone[2] * S) if p.get("abone", True) else None
        etiketler = p.get("etiketler") or ["SIRADAKİ VİDEO", "BUNU DA İZLE"]
        self.kutu_spr = [self._kutu(w, h, str(etiketler[i]) if i < len(etiketler) else "")
                         for i, (x, y, w, h) in enumerate(self.kutular)]
        self.abone_spr = self._abone(self.abone[2]) if self.abone else None
        baslik = p.get("baslik")
        if baslik is None and self.sahne.satirlar:
            baslik = self.sahne.satirlar[0].altyazi
        self.baslik = None
        if baslik:
            bx, by, bw, hiza = bas
            self.baslik = (bx * S, by * S, bw * S, hiza,
                           C.yazi(str(baslik), C.FONT_DIALOG, 60 * S, C.BEYAZ, max_w=bw * S, max_lines=3,
                                  align="center" if hiza == "center" else "left", golge=(0, 4 * S, 9 * S, 0.6)))
        self.karakter = None
        if p.get("karakter"):
            kr = p["karakter"]
            im = C.kirp_alfa([C.yukle(kr["gorsel"]).convert("RGBA")])[0]
            sol = p.get("duzen", "yan_yana") != "sol"
            cxn = 0.1 if sol else 0.9
            faces, _ = facing.resolve(Path(kr["gorsel"]), kr.get("bakis"))
            if faces != "front" and facing.needs_flip(faces, cxn):
                im = ImageOps.mirror(im)
            h = float(kr.get("boy", 0.42)) * H
            im = im.resize((max(1, round(im.width * h / im.height)), round(h)), Image.LANCZOS)
            self.karakter = (im, cxn * W, H + 0.03 * h, 1 if sol else -1)

    def _kutu(self, w: float, h: float, etiket: str) -> Image.Image:
        S = self.S
        w, h = int(w), int(h)
        lay = C.yuvarlak_kutu(w, h, 14 * S, (8, 10, 14, 120), outline=(255, 255, 255, 235), width=4 * S)
        d = ImageDraw.Draw(lay)
        r = 0.11 * h   # oynat simgesi
        cx, cy = w / 2, h / 2 - 0.06 * h
        d.polygon([(cx - 0.7 * r, cy - r), (cx - 0.7 * r, cy + r), (cx + 1.0 * r, cy)], fill=(255, 255, 255, 110))
        if etiket:
            yz = C.yazi(C.buyuk(etiket), C.FONT_BOLD, 28 * S, (235, 236, 240), aralik=0.16)
            lay.alpha_composite(yz, (int((w - yz.width) / 2), int(h - yz.height - 0.1 * h)))
        spr, _, _ = C.golgeli(lay, 16 * S, 0.5, 0, 8 * S)
        return spr

    def _abone(self, cap: float) -> Image.Image:
        S = self.S
        n = int(cap)
        ss = 3
        lay = Image.new("RGBA", (n * ss, n * ss), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        d.ellipse((0, 0, n * ss - 1, n * ss - 1), fill=(204, 18, 24, 235), outline=(255, 255, 255, 255),
                  width=int(5 * S * ss))
        lay = lay.resize((n, n), Image.LANCZOS)
        yz = C.yazi("ABONE OL", C.FONT_BOLD, 34 * S, C.BEYAZ, aralik=0.06)
        lay.alpha_composite(yz, (int((n - yz.width) / 2), int((n - yz.height) / 2)))
        spr, _, _ = C.golgeli(lay, 14 * S, 0.5, 0, 6 * S)
        return spr

    def dondur(self, onceki: Image.Image) -> None:
        self.donuk = onceki.copy()
        k = C.ayarla(onceki, bulanik=12 * self.S, karart=C.donuk_karart(onceki, self.karart, 50), doygunluk=0.6)
        C.vinyet_uygula(k, 0.45)
        self.donuk_k = k

    def ciz(self, t):
        S, W, H = self.S, self.W, self.H
        if self.bindirme and self.donuk is not None:
            a = E.out_cubic(t / 0.35)
            im = Image.blend(self.donuk, self.donuk_k, a) if a < 0.999 else self.donuk_k.copy()
            zz = 1.0 + 0.03 * E.in_out_sine(t / self.dur)
            im = C.kamera(im, W, H, zz, (0.5, 0.5))
            C.gren_uygula(im, t, 0.04)
        else:
            im = self.zemin.ciz(t, self.dur)
        if self.baslik is not None:
            bx, by, bw, hiza, spr = self.baslik
            a = E.out_cubic((t - self.z["baslik"]) / 0.5)
            x = bx + (bw - spr.width) / 2 if hiza == "center" else bx
            C.bindir(im, spr, x, by - (1 - a) * 18 * S, a)
        for (x, y, w, h), spr, t0 in zip(self.kutular, self.kutu_spr, self.z["kutular"]):
            u = (t - t0) / 0.45
            if u <= 0:
                continue
            a = min(1.0, u * 2.2) * (0.82 + 0.18 * (0.5 + 0.5 * math.sin(2 * math.pi * 0.45 * t + y)))
            if u < 1.0:   # açılış: küçükten taşarak oturur
                s = 0.88 + 0.12 * E.out_back(u, 1.6)
                spr2, x0, y0 = C.afin(spr, x + w / 2, y + h / 2, s, s)
                C.bindir(im, spr2, x0, y0, a)
            else:         # sonra yerinde, kenarı hafifçe nabız atar
                C.bindir(im, spr, x + w / 2 - spr.width / 2, y + h / 2 - spr.height / 2, a)
        if self.abone is not None:
            cx, cy, cap = self.abone
            u = (t - self.z["abone"]) / 0.45
            if u > 0:
                # dışa yayılan halka (her 1,6 sn)
                q = ((t - self.z["abone"]) % 1.6) / 1.6
                rr = cap / 2 + 6 * S + 46 * S * E.out_cubic(q)
                ImageDraw.Draw(im).ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=(255, 255, 255),
                                           width=max(1, int(4 * S * (1 - q) + 1)))
                s = (0.7 + 0.3 * E.out_back(u, 1.8)) * (1 + 0.03 * E.tumsek(q / 0.35))
                spr2, x0, y0 = C.afin(self.abone_spr, cx, cy, s, s)
                C.bindir(im, spr2, x0, y0, min(1.0, u * 2.5))
        if self.karakter is not None:
            spr, cx, taban, yon = self.karakter
            u = E.out_back((t - self.z["karakter"]) / 0.7, 1.1)
            if u > 0.001:
                x = cx - (1 - u) * (spr.width + 80 * S) * yon
                dy = 3 * S * math.sin(2 * math.pi * 0.21 * t)
                C.bindir(im, spr, x - spr.width / 2, taban - spr.height + dy)
        return im


def vuruslar(sahne) -> list[float]:
    """Hareket denetimi için yeni öğe anları."""
    if sahne.tip == "marka":
        z = marka_zamanlari(sahne)
        return [z["serit"], z["wojak"], z["gulumse"], z["ucus"]]
    if sahne.tip == "bitis":
        z = bitis_zamanlari(sahne)
        dur = sahne.sure_hesap or 15.0
        nabiz = [z["abone"] + 1.6 * i for i in range(int(dur / 1.6) + 1)]   # abone halkası sürekli atar
        return [z["baslik"], *z["kutular"], z["abone"], z["karakter"], *nabiz]
    return []
