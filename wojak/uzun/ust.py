"""Her sahnede kullanılabilen üst katmanlar (2. tur): lastik damga ve köşe göstergesi.

- `damga` olayı: kırmızı (ya da yeşil/mavi) lastik damga, ekrana 'çarparak' iner (büyükten küçüğe, 0,14 sn),
  mürekkep dokulu, çift çerçeveli. `x`, `y` (0..1, merkez), `aci` (derece), `boy` (punto, 1920 ölçeğinde),
  `sure` (verilmezse sahne sonuna kadar kalır). Otomatik efekt: `damga`.
- Köşe göstergesi: sahnenin `kose` anahtarı (başlangıç hâli, ör. {metin: "GÜN {} / 12", deger: 0}) ve `kose`
  olayları ({deger: 5}). Sayı -> sayı geçişi sayarak, metin -> metin geçişi yuvarlanarak olur; `takili: true`
  ile basamaklar karışıp takılı kalır (ara ara titrer: "1961 -> ????"). `yil: true`: binlik ayırıcı yok.
  Birden çok sahneye yayılan sayaç (GÜN 0/12 ... 12/12) için her sahne kendi başlangıç değerini yazar.
"""

from __future__ import annotations

import numpy as np
from PIL import Image, ImageDraw

from . import cizim as C
from . import easing as E
from .zemin import renk as renk_coz

KIRMIZI_DAMGA = (196, 34, 38)


# ---------------------------------------------------------------- damga

INIS_OLCEK = 1.85   # damganın iniş başlangıç ölçeği (varsayılan)


def damga_sprite(metin: str, renk, boy: float, S: float, tohum: int = 0, kontur=None) -> Image.Image:
    """Lastik damga katmanı (RGBA): büyük harf Anton, çift çerçeve, mürekkep boşlukları.
    `kontur` (renk): harflerin ve çerçevenin çevresine ince dolu kenar (koyu/renkli zeminde okunurluk; 5. tur)."""
    renk = tuple(renk)
    yz = C.yazi(C.buyuk(metin), C.FONT_CARD, boy, renk, max_w=1300 * S, max_lines=2, align="center",
                aralik=0.05, satir=1.0)
    k1, k2, ara = max(2, round(0.075 * boy)), max(1, round(0.03 * boy)), round(0.07 * boy)
    padx, pady = round(0.36 * boy), round(0.2 * boy)
    w, h = yz.width + 2 * (padx + k1 + ara + k2), yz.height + 2 * (pady + k1 + ara + k2)
    ss = 2
    lay = Image.new("RGBA", (w * ss, h * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    r = 0.12 * boy * ss
    d.rounded_rectangle((0, 0, w * ss - 1, h * ss - 1), radius=r, outline=renk + (255,), width=k1 * ss)
    o = (k1 + ara) * ss
    d.rounded_rectangle((o, o, w * ss - 1 - o, h * ss - 1 - o), radius=max(1, r * 0.6), outline=renk + (255,),
                        width=k2 * ss)
    lay = lay.resize((w, h), Image.LANCZOS)
    lay.alpha_composite(yz, ((w - yz.width) // 2, (h - yz.height) // 2))
    # mürekkep dokusu: lekeli opaklık + küçük boşluklar
    rng = np.random.default_rng(1234 + tohum)
    a = np.asarray(lay.getchannel("A"), np.float32)
    g1 = np.asarray(Image.fromarray((rng.random((h // 6 + 2, w // 6 + 2)) * 255).astype(np.uint8), "L")
                    .resize((w, h), Image.BICUBIC), np.float32) / 255
    g2 = rng.random((h, w)).astype(np.float32)
    doku = np.clip(0.62 + 0.55 * g1, 0, 1) * np.where(g2 < 0.06, 0.35, 1.0)
    doku[g1 < 0.16] *= 0.25
    lay.putalpha(Image.fromarray(np.clip(a * doku * 0.94, 0, 255).astype(np.uint8), "L"))
    if kontur is not None:
        from PIL import ImageFilter
        kal = max(3, int(round(0.07 * boy)) | 1)
        pay = kal
        tuval = Image.new("RGBA", (w + 2 * pay, h + 2 * pay), (0, 0, 0, 0))
        maske = Image.new("L", tuval.size, 0)
        maske.paste(Image.fromarray(a.astype(np.uint8), "L"), (pay, pay))
        maske = maske.filter(ImageFilter.MaxFilter(kal)).filter(ImageFilter.GaussianBlur(0.6 * S))
        kenar = Image.new("RGBA", tuval.size, tuple(kontur) + (0,))
        kenar.putalpha(maske.point(lambda v: int(v * 0.92)))
        tuval.alpha_composite(kenar)
        # 13. tur (izlenme: mantar panodaki kırmızı damgalar telefonda soluk): kenar dolgusu harflerin ALTINI da
        # dolduruyordu, mürekkep boşluklarından beyaz görünüyordu (kırmızı yazı pembe-beyaz benekli). Harf ve çerçeve
        # izinin altına önce mürekkebin kendi rengi (%72): boşluklar açık mürekkep tonu, kenar yalnız dışta halka
        alt = Image.new("RGBA", (w, h), renk + (0,))
        alt.putalpha(Image.fromarray((a * 0.72).astype(np.uint8), "L"))
        tuval.alpha_composite(alt, (pay, pay))
        tuval.alpha_composite(lay, (pay, pay))
        return tuval
    return lay


class Damga:
    INIS = 0.14
    INIS_A = 0.3   # kontrol: inişte bu opaklıktan sonra yüze binen damga bildirilir

    def __init__(self, o, c, tohum: int = 0):
        S = c.S
        p = o.p
        self.c, self.t0 = c, (-10.0 if p.get("inik") else o.zaman)   # inik: önceki çekimden basılı gelir
        self.metin = str(p["metin"])
        self.sure = None if p.get("sure") is None else float(p["sure"])
        if p.get("inik") and self.sure is not None:   # 11. tur: inik + sure: sahne başından `sure` sn sonra söner
            self.sure -= self.t0                       # (eskiden t0 = -10'a göre sayılıp hiç çizilmiyordu)
        kontur = p.get("kontur")
        if kontur is True:
            kontur = C.BEYAZ
        self.spr = damga_sprite(str(p["metin"]), renk_coz(p.get("renk"), KIRMIZI_DAMGA), float(p.get("boy", 84)) * S,
                                S, tohum, renk_coz(kontur, C.BEYAZ) if kontur else None)
        self.x, self.y = float(p.get("x", 0.5)) * c.W, float(p.get("y", 0.5)) * c.H
        self.aci = float(p.get("aci", -8))
        # Gemini turu 2. hakem turu (animasyon S5): damga 1,85 kattan iner; yüzün yanına basılan damga ilk 3 karede
        # yüzü süpürüyordu (B6.6, B5.3b). `inis`: iniş başlangıç ölçeği (1,0-1,85); kontrol bunu ölçer
        self.inis = min(1.85, max(1.0, float(p.get("inis", INIS_OLCEK))))

    def olcek(self, u: float) -> float:
        """İnişin u (sn) anındaki ölçeği (tümsek dahil)."""
        s = self.inis - (self.inis - 1.0) * E.in_cubic(u / self.INIS)
        return s * (1 - 0.035 * E.tumsek((u - self.INIS) / 0.14))

    def ciz(self, im: Image.Image, t: float, x: float | None = None, y: float | None = None, olcek: float = 1.0):
        u = t - self.t0
        if u < 0:
            return
        a = 1.0
        if self.sure is not None:
            if u > self.sure + 0.25:
                return
            a = 1 - E.in_cubic((u - self.sure) / 0.25)
        s = self.olcek(u)
        a *= min(1.0, u / (self.INIS * 0.6))
        spr, x0, y0 = C.afin(self.spr, self.x if x is None else x, self.y if y is None else y, s * olcek, s * olcek,
                             self.aci)
        C.bindir(im, spr, x0, y0, a)


# ---------------------------------------------------------------- köşe göstergesi

def _sayi_mi(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _bicim(v, yil: bool) -> str:
    if _sayi_mi(v):
        if yil:
            return str(int(round(v)))
        return C.say_bicimle(v, 0 if float(v).is_integer() or abs(v) >= 100 else 1)
    return str(v)


class KoseGostergesi:
    """Köşede küçük sayaç kutusu: değer değişimlerini sayarak / yuvarlanarak / takılarak gösterir."""

    def __init__(self, sahne, c, olaylar):
        S = c.S
        self.c = c
        bas = sahne.kose
        evs = sorted(olaylar, key=lambda o: o.zaman)
        if bas is None:
            ilk = evs[0].p if evs else {}
            bas = {"metin": ilk.get("metin", "{}"), "deger": None, "konum": "sag_ust", "renk": None,
                   "giris": True, "yil": ilk.get("yil", False)}
            self.goster_t = evs[0].zaman if evs else 0.0
            self.giris = True
        else:
            self.goster_t = 0.0
            self.giris = bool(bas.get("giris", False))
        self.konum = bas.get("konum", "sag_ust")
        # sol üstte sahne başlığı olan tiplerde (harita, zaman çizelgesi, pano) başlığın altına in
        self.ust_y = 170 if (self.konum == "sol_ust" and sahne.p.get("baslik")
                             and sahne.tip in ("harita", "zaman_cizelgesi", "pano")) else 50
        # durumlar: (t, metin_sablonu, eski, yeni, sure, takili, renk, yil)
        self.durumlar = []
        metin, deger = str(bas.get("metin", "{}")), bas.get("deger")
        rk, yil = renk_coz(bas.get("renk"), C.BEYAZ), bool(bas.get("yil", False))
        self.durumlar.append((-1.0, metin, deger, deger, 0.0, False, rk, yil))
        for o in evs:
            p = o.p
            metin = str(p.get("metin", metin))
            if "{}" not in metin:
                metin += " {}"
            rk = renk_coz(p.get("renk"), rk) if p.get("renk") is not None else rk
            yil = bool(p.get("yil", yil))
            takili = bool(p.get("takili", False))
            sure = float(p.get("sure", 0.8 if takili else 0.6))
            yeni = p["deger"]
            # 14. tur (animasyon hakemi 13. tur M1, 5:20): şablon değişirken ("GÜN {}" -> "{}") ya da değerlerden biri
            # sayı değilken ("1961" yazı) şablon olay anında değişiyor, eski değer ise sürenin yarısı boyunca yeni
            # şablonla çiziliyordu: 9 kare çıplak "0", sonra "1961". Bu durumda şablon ve değer aynı karede birlikte
            # değişir (nabız vuruşuyla); sayı -> sayı aynı şablonda sayarak geçmeye devam eder
            if not takili and (metin != self.durumlar[-1][1] or not (_sayi_mi(deger) and _sayi_mi(yeni))):
                sure = 0.0
            self.durumlar.append((o.zaman, metin, deger, yeni, sure, takili, rk, yil))
            deger = yeni
        self.f_boy = 58 * S   # 8. tur (izlenme hakemi N2): 52 telefonda küçüktü
        self._cache: dict = {}
        # 7. tur: rakamlar sabit genişlikte (tabular) ve kutu genişliği bütün durumların en genişine sabit: sayarken
        # ("GÜN 3 / 12" -> "GÜN 11 / 12") ya da takılınca kutu her karede 5-9 px genişleyip daralıyordu (titreme)
        f = C.font(C.FONT_CARD, self.f_boy)
        self.rakam_en = max(f.getlength(str(d)) for d in range(10)) * 1.03
        self._dikey = None
        metinler = []
        for _, sablon, eski, yeni, _, takili, _, yil in self.durumlar:
            metinler += [sablon.replace("{}", _bicim(v, yil)) for v in (eski, yeni) if v is not None]
            if takili:
                metinler.append(sablon.replace("{}", "0000"))
        en, ust, alt = 0.0, 10 ** 9, -1
        for m in metinler or ["0"]:
            yz = self._yazi(m, C.BEYAZ)
            en = max(en, yz.width)
            bb = yz.getchannel("A").getbbox()
            if bb:
                ust, alt = min(ust, bb[1]), max(alt, bb[3])
        self.min_w = en
        self._dikey = (ust, alt) if alt > ust else None

    def _metin(self, t: float) -> tuple[str, tuple, float]:
        """(gösterilecek yazı, renk, nabız 0..1)."""
        d = self.durumlar[0]
        for x in self.durumlar:
            if x[0] <= t:
                d = x
        t0, sablon, eski, yeni, sure, takili, rk, yil = d
        u = (t - t0) / sure if sure > 0 else 1.0
        nabiz = E.tumsek((t - t0) / 0.32) if t0 >= 0 else 0.0
        if takili and yil and _sayi_mi(eski):
            # 9. tur (izlenme S1): yıl göstergesi takılırken geriye gitmez: eski yıldan ileri doğru hızla akar ("1961 ->
            # 20??" altında 1948 ve 1987 görünüp zamanda geri gidiyor gibi okunuyordu), sonra takılır; titreşimde de
            # yalnız eski yıldan sonraki yıllar
            rng = np.random.default_rng(int(t * 30) + 7)
            yeni_s = _bicim(yeni, yil)
            e0 = int(round(eski))
            if len(yeni_s) == 4 and yeni_s[:2].isdigit():
                ust_y = int(yeni_s[:2]) * 100
                if ust_y <= e0:
                    ust_y = e0 + 40
            else:
                ust_y = e0 + 45
            if u < 1.0:
                yv = int(e0 + (ust_y - e0) * E.out_cubic(max(0.0, u)))
                return sablon.replace("{}", str(yv)), rk, nabiz
            faz = (t - t0 - sure) % 1.35
            if faz < 0.12:
                lo = ust_y if ust_y > e0 + 1 and len(yeni_s) == 4 and yeni_s[:2].isdigit() else e0 + 1
                hi = lo + 19 if lo == ust_y else ust_y
                return sablon.replace("{}", str(int(rng.integers(lo, max(lo + 1, hi + 1))))), rk, 0.0
            return sablon.replace("{}", yeni_s), rk, nabiz
        if takili:
            rng = np.random.default_rng(int(t * 30) + 7)
            ornek = _bicim(eski, yil) if eski is not None else "0000"
            ornek = ornek.ljust(4, "0")
            # yıl göstergesinde yüzyıl basamakları sabit kalır, yalnız son iki basamak karışır ("19??" / "20??");
            # 5. tur: tam karışım "1781", "5940" gibi anlamsız yıllar gösteriyordu
            yeni_s = _bicim(yeni, yil)
            sabit = 2 if yil and len(ornek) == 4 else 0
            if sabit and u >= 0.5 and len(yeni_s) == 4 and yeni_s[:2].isdigit():
                ornek = yeni_s[:2] + ornek[2:]
            kar = "".join(ch if j < sabit else (str(rng.integers(10)) if ch.isdigit() or ch == "?" else ch)
                          for j, ch in enumerate(ornek))
            if sabit and kar[:2] == "20":   # gelecek yıl görünmesin ("2076"): 2000-2019
                kar = kar[:2] + str(rng.integers(2)) + kar[3:]
            if u < 1.0:
                return sablon.replace("{}", kar), rk, nabiz
            # takılı kaldı: ara ara 0,12 sn titrer
            faz = (t - t0 - sure) % 1.35
            if faz < 0.12:
                return sablon.replace("{}", kar), rk, 0.0
            return sablon.replace("{}", yeni_s), rk, nabiz
        if u >= 1.0 or eski is None:
            return sablon.replace("{}", _bicim(yeni, yil) if yeni is not None else ""), rk, nabiz
        if _sayi_mi(eski) and _sayi_mi(yeni):
            v = eski + (yeni - eski) * E.out_cubic(u)
            v = round(v) if float(eski).is_integer() and float(yeni).is_integer() else v
            return sablon.replace("{}", _bicim(v, yil)), rk, nabiz
        return sablon.replace("{}", _bicim(yeni if u > 0.5 else eski, yil)), rk, nabiz

    def _yazi(self, metin: str, rk) -> Image.Image:
        yz = C.tabular_yazi(metin, C.FONT_CARD, self.f_boy, tuple(rk) + (255,), rakam_en=self.rakam_en)
        bb = yz.getchannel("A").getbbox()
        if bb:   # yükseklik sabit kalsın (yazı kutusu: yalnız yatayda sıkı)
            yz = yz.crop((bb[0], 0, bb[2], yz.height))
        return yz

    def _kutu(self, metin: str, rk) -> Image.Image:
        key = (metin, rk)
        spr = self._cache.get(key)
        if spr is None:
            S = self.c.S
            yz = self._yazi(metin, rk)
            bb = yz.getchannel("A").getbbox() or (0, 0, yz.width, yz.height)
            yz = yz.crop((0, bb[1], yz.width, bb[3])) if self._dikey is None else \
                yz.crop((0, self._dikey[0], yz.width, self._dikey[1]))
            padx, pady, bar = 22 * S, 12 * S, 8 * S
            w, h = int(max(yz.width, getattr(self, "min_w", 0)) + 2 * padx + bar), int(yz.height + 2 * pady)
            lay = C.yuvarlak_kutu(w, h, 6 * S, (10, 12, 16, 222))
            ImageDraw.Draw(lay).rectangle((0, 0, int(bar) - 1, h), fill=C.SARI + (255,))
            lay.alpha_composite(yz, (int(bar + padx), int(pady)))
            spr, _, _ = C.golgeli(lay, 10 * S, 0.45, 0, 5 * S)
            if len(self._cache) > 64:
                self._cache.pop(next(iter(self._cache)))
            self._cache[key] = spr
        return spr

    def kutu(self, t: float) -> tuple[float, float, float, float]:
        """10. tur (yerleşim denetimi): oturmuş kutunun ekran kutusu (gölgesiz)."""
        S, W, H = self.c.S, self.c.W, self.c.H
        metin, rk, _ = self._metin(t)
        spr = self._kutu(metin, rk)
        bb = spr.getchannel("A").point(lambda v: 255 if v > 160 else 0).getbbox() or (0, 0, spr.width, spr.height)
        x = W - 54 * S - spr.width if self.konum.startswith("sag") else 54 * S
        y = self.ust_y * S if self.konum.endswith("ust") else H - 118 * S - spr.height
        return x + bb[0], y + bb[1], x + bb[2], y + bb[3]

    def ciz(self, im: Image.Image, t: float) -> None:
        if t < self.goster_t:
            return
        S, W, H = self.c.S, self.c.W, self.c.H
        metin, rk, nabiz = self._metin(t)
        spr = self._kutu(metin, rk)
        sag = self.konum.startswith("sag")
        ust = self.konum.endswith("ust")
        x = W - 54 * S - spr.width if sag else 54 * S
        y = self.ust_y * S if ust else H - 118 * S - spr.height
        a = 1.0
        if self.giris:
            e = E.out_back((t - self.goster_t) / 0.45, 1.3)
            x += (1 - e) * (spr.width + 80 * S) * (1 if sag else -1)
            a = E.out_cubic((t - self.goster_t) / 0.25)
        s = 1 + 0.09 * nabiz
        if s > 1.001:
            spr2, x0, y0 = C.afin(spr, x + spr.width / 2, y + spr.height / 2, s, s)
            C.bindir(im, spr2, x0, y0, a)
        else:
            C.bindir(im, spr, x, y, a)


def kose_olaylari(sahne) -> list:
    return sorted((o for o in sahne.olaylar if o.tip == "kose"), key=lambda o: o.zaman)


def damga_olaylari(sahne, kartli: bool = False) -> list:
    return sorted((o for o in sahne.olaylar if o.tip == "damga" and bool(o.p.get("kart")) == kartli),
                  key=lambda o: o.zaman)
