"""Uzun video spesifikasyonu: uzun/<id>/video.yaml yükleme ve doğrulama.

Tüm alanların açıklamalı örneği: uzun/_sablon/video.yaml. Başvuru: docs/UZUN_MOTOR.md.
Hatalar SpecHatasi olarak, sahnenin yeriyle ("bölüm 2, sahne 3") birlikte bildirilir.
"""

from __future__ import annotations

import re
import zlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .. import config

VARSAYILAN_SESLER = {
    "murat": "5a31e4fb-f823-4359-aa91-82c0ae9a991c",
    "aylin": "bb2347fe-69e9-4810-873f-ffd759fe8420",
    "leyla": "fa7bfcdc-603c-4bf1-a600-a371400d2f8c",
    "azra": "0f95596c-09c4-4418-99fe-5c107e0713c0",
}

VARSAYILAN_ZAMANLAMA = {
    "bas": 0.35,        # sahne başı ile ilk satır arası (sn)
    "ara": 0.35,        # aynı sahnedeki iki satır arası
    "son": 0.55,        # son satırdan sonra sahnenin sürmesi
    "min_sahne": 2.0,   # satırlı sahnenin en kısa süresi
    "kart": 2.6,        # bölüm kartı süresi
    "sabit": 3.0,       # satırsız sahnenin varsayılan süresi
    "max_bos": 6.0,     # hareket denetimi: ekranda yeni bir şey olmadan geçebilecek en uzun süre
    "bindirme": 1.2,    # bindirme bölüm kartı (önceki karenin üstünde) süresi
}

# satırsız sahne tiplerinin varsayılan süresi (sn); satırlı sahnede alt sınır olarak da uygulanır (bitis)
TIP_SURESI = {"marka": 1.8}
TIP_MIN_SURE = {"bitis": 15.0, "kapanis": 10.0}

# 7. tur (animasyon): videonun hareket dili. Varsayılanlar her sahnede açık olanlar; paralaks ve doku bilerek kapalı
# (arka plandaki bir masaya "konmuş" nesne paralaksla kayar; gren her çizim stiline uymaz): sahne/video açar.
HAREKET_VARSAYILAN = {
    "bulaniklik": True,   # hızlı hareketlerde hareket bulanıklığı (giriş/çıkış, kayan etiket, fotoğraf, itme geçişi)
    "ikincil": True,      # girişte ikincil hareket: yandan girişte eğilip yaylanarak durma, alttan/üstten esneme
    "canli": True,        # karakter başına farklı nefes/salınım ritmi + çok hafif baş eğimi (tabandan)
    "paralaks": 0.0,      # wojak sahnesinde arka plan kamerayı daha az izler (0 = kapalı; öneri 0.3-0.45)
    "doku": False,        # wojak sahnesinde arka plana gren + toz (true | {gren: 0.035, toz: 18})
}

GECISLER = {"kesme": "kesme", "cut": "kesme", "gecis": "gecis", "crossfade": "gecis", "xfade": "gecis",
            "kaydir": "kaydir", "push": "kaydir", "itme": "kaydir", "karart": "karart", "dip": "karart"}
# 9. tur: karart = karanlıktan geçiş (önceki sahne koyuya söner, yenisi koyudan açılır; iki görüntü üst üste binmez:
# aynı karakterli sahneler arasında ve kâğıt/koyu parlaklık sıçramasında çapraz geçiş yerine)
GECIS_KARE = {"kesme": 0, "gecis": 8, "kaydir": 10, "karart": 10}

# sahne tipi -> izinli parametreler (ortak anahtarlar ayrıca)
ZEMIN_PARAM = {"zemin", "arka", "arka_opak", "karart"}   # "bilgi" sahnelerinin zemini (zemin.py); 9. tur: karart
# (0..1): zemin koyulaşır (kâğıt zeminli sahneye koyu sahneden kesmede parlaklık sıçramasın)
SAHNE_PARAMLARI: dict[str, set[str]] = {
    "wojak": {"arka", "kamera", "karakterler", "karart", "bulanik", "doygunluk", "kirp", "odak", "etiket", "vinyet",
              "doku"},
    "foto": {"gorsel", "etiket", "egim", "zoom", "atif", "boy", "giris", "arka", "odak", "x", "y"},
    "manset": {"gorsel", "kutular", "zoom", "arka", "renk", "boy", "etiket"},
    "harita": {"bolge", "ulkeler", "vurgu", "baslik", "aralik", "cozunurluk", "renk", "etiketler", "zoom",
               "aciklama", "aciklama_en"},   # 13. tur: aciklama_en (lejantın en geniş hali, px @1080p; aşarsa 2 satır)
    "sayac": {"deger", "yil", "etiket", "ust", "onek", "sonek", "sure_say", "renk", "olcek", "tut"} | ZEMIN_PARAM,
    "bolum_karti": {"numara", "baslik", "ust", "bindirme", "marka", "karart"},
    "metin": {"metin", "ceviri", "ust", "alt", "ceviri_t", "yazim", "renk", "tirnak"} | ZEMIN_PARAM,
    "zaman_cizelgesi": {"noktalar", "baslik", "olcek", "y", "x"} | ZEMIN_PARAM,   # 12. tur: olcek (yazı), y (eksen), x [x0, x1]
    "bolunmus": {"sol", "sag", "acik", "cizgi"},
    "izgara": {"n", "sutun", "ust", "etiket", "alt", "renk", "dolum", "say"} | ZEMIN_PARAM,
    "pano": {"kartlar", "ipler", "baslik", "zoom", "yakin", "doku", "cercevele"},
    "marka": {"bindirme", "karart", "wojak", "yuz", "yazi", "arka"},
    "bitis": {"arka", "bindirme", "karart", "bulanik", "baslik", "kutular", "abone", "duzen", "etiketler",
              "karakter"},
    # 7. tur: video kutusuz, hikâyeye bağlı kapanış çağrısı (soru + seçenek kartları + abone/zil/beğen + yorum balonu)
    "kapanis": {"arka", "bindirme", "karart", "bulanik", "ust", "soru", "secenekler", "yorum", "karakter",
                "dugmeler", "bos_alan", "renk"},
}
TIP_TAKMA = {"liste": "zaman_cizelgesi", "zaman": "zaman_cizelgesi", "kart": "bolum_karti", "fotograf": "foto",
             "belge": "manset", "sayi": "sayac", "bolunmus_ekran": "bolunmus", "split": "bolunmus",
             "nokta_izgarasi": "izgara", "sorusturma_panosu": "pano", "sting": "marka", "imza": "marka",
             "bitis_ekrani": "bitis", "cagri": "kapanis", "kapanis_cagrisi": "kapanis", "cta": "kapanis"}
ZORUNLU = {"wojak": ["arka"], "foto": ["gorsel"], "manset": ["gorsel"], "sayac": [], "bolum_karti": ["baslik"],
           "metin": ["metin"], "zaman_cizelgesi": ["noktalar"], "harita": [], "bolunmus": ["sol", "sag"],
           "izgara": [], "pano": ["kartlar"], "marka": [], "bitis": [], "kapanis": []}
ORTAK = {"tip", "satirlar", "olaylar", "sfx", "gecis", "gecis_kare", "sure", "min_sure", "bas", "ara", "son",
         "isim_etiketi", "kelime", "not", "otomatik_sfx", "kose", "muzik_db", "filigran", "muzik_mod", "konuk",
         "sfx_db"}
# sfx_db: bu sahnenin OTOMATİK efektlerine ek kazanç (dB, -24..+6; ör. sessiz altlıkta fosforlu kalem sesi -6)
# konuk: wojak dışındaki sahnelere (harita, sayaç, pano, belge...) köşeden/kenardan giren tepki karakteri (1-3; 10. tur: 3);
# `yuz` / `giris` / `cikis` olayları ve `isim {karakter}` konuk kimliğiyle her sahne tipinde kullanılabilir
KONUK_OLAYLARI = {"yuz", "giris", "cikis"}
ZEMINLER = ("koyu", "kagit", "foto")
KARAKTER_YONLERI = ("sol", "sag", "alt", "ust", "pop")
KAPANIS_DUGMELERI = ("abone", "zil", "begen", "yorum")
VURGU_STILLERI = ("kalem", "daire", "alt_cizgi")
KOSE_KONUM = ("sag_ust", "sol_ust", "sag_alt", "sol_alt")
PANEL_ANAHTAR = {"gorsel", "metin", "ceviri", "etiket", "alt", "arka", "odak", "zemin", "baslik", "zoom", "say",
                 "say_sure"}
KART_ANAHTAR = {"id", "metin", "alt", "x", "y", "en", "egim", "gorsel", "stil", "renk", "asili"}

# olay tipi -> izinli parametreler (çapa anahtarları satir/ofset/an/t ayrıca)
OLAY_TIPLERI: dict[str, set[str]] = {
    "yuz": {"karakter", "gorsel", "sik", "buyu"},   # 9. tur: buyu: true = yeni yüz eski görselin boyundan out_back ile
    #                                           büyüyerek oturur (doz şişesi tek karede 1,3 kat büyüyordu)     # yüz varyantına geç (kısa sıkışma efektiyle; 8. tur: sik: false =
    #                                           sıkışmasız: kapı kanadının ara kareleri gibi art arda geçişler)
    "balon": {"karakter", "metin", "sure", "agiz"},   # konuşma balonu (yalnız görsel); 9. tur: agiz = açık ağızlı
    #                                           yüz görseli: balon açıkken hecelerde ağız açılıp kapanır; 11. tur:
    #                                           [yarık, açık] listesi: kapalı -> yarık -> açık, en az 4 kare tutulur
    "kelime": {"metin", "sure", "konum", "y"},   # ekranda vurgu kelimesi (konum: ust | orta | alt; 13. tur: y 0..1 merkez)
    "isim": {"ad", "unvan", "sure", "konum", "karakter"},  # isim etiketi (lower third); konum: sol | sag
    "giris": {"karakter"},                    # karakter bu anda kayarak girer
    "cikis": {"karakter"},                    # karakter bu anda çıkar
    "vurgula": {"kutu", "stil", "renk"},      # manset: bu kutu vurgulanır (1'den); stil: kalem | daire | alt_cizgi
    "basla": {"sure"},                        # sayac/harita/zaman_cizelgesi: ana animasyon başlar (sayac: sure =
    #                                           ilk sayımın süresi, `sure_say` yerine; 10. tur)
    "nokta": {"indeks"},                      # zaman_cizelgesi: bu nokta belirir (1'den başlar)
    "ulke": {"kod"},                          # harita: bu ülke yanar (ISO3)
    "etiket": set(),                          # foto: yer-tarih etiketi yazılmaya başlar
    "ceviri": {"taraf"},                      # metin (bolunmus: taraf): çeviri satırı belirir
    # --- 2. tur
    "damga": {"metin", "renk", "x", "y", "aci", "boy", "sure", "kart", "inik", "kart_y", "kontur", "inis"},   # lastik damga (pano: kart'ın üstüne;
    # kart_y: kartın merkezine göre dikey yer, kart yüksekliği oranında (-0.5 üst .. 0.5 alt; görselli kartta
    # varsayılan görselin ortası, başlık okunur kalsın; görselsiz kartta 0.2)
    # inik: true = sahne başında zaten basılı, iniş ve ses yok: bölünmüş çekimin devamında)
    "kose": {"deger", "metin", "sure", "takili", "renk", "yil"},   # köşe göstergesi yeni değere döner (sayar / takılır)
    "muzik": {"db", "gecis"},                 # müzik seviyesi bu andan itibaren (dB, 0 = normal), gecis: rampa sn
    "deger": {"deger", "etiket", "renk", "sure", "onek", "sonek"},   # sayac: yeni değere sayar (etiket değişir)
    "panel": {"taraf"},                       # bolunmus: panel kayarak açılır (vars. sag)
    "soluk": {"taraf"},                       # bolunmus: panel soluklaşır
    "buyut": {"taraf"},                       # bolunmus: panel büyüyüp ekranı kaplar
    "kart": {"id"},                           # pano: kart iğnelenir
    "ip": {"a", "b"},                         # pano: iki kart arasına kırmızı ip gerilir
    "sondur": {"oran", "sure", "etiket"},     # izgara: noktaların bir oranı sessizce söner
    "ustunu_ciz": {"renk"},                   # metin: ana yazının üstü kırmızı çizgiyle çizilir
    # --- 7. tur
    "rota": {"a", "b", "renk", "sure", "kavis", "kesik", "etiket"},   # harita: a'dan b'ye çizilerek uzanan rota
    "tikla": {"hedef"},                       # kapanis: imleç bu anda hedefe tıklar (abone | zil | begen | yorum)
    "secenek": {"indeks"},                    # kapanis: seçenek kartı vurgulanır (1'den)
    # --- 8. tur
    "sarsinti": {"guc", "sure"},              # kamera sarsıntısı (kapı çarpması, darbe): guc px (1080p, vars. 7), sure sn (0.1)
    # --- 9. tur
    "it": {"guc", "sure", "x", "y"},          # wojak: kamera vurgu itmesi (zoom x(1+guc), vars. 0.08, sure 0.5 sn; x/y: hedef)
    #                                           12. tur: harita (x/y yoksa vurgu ülkesine) ve zaman_cizelgesi (x/y ekran oranı)
}
OLAY_ZORUNLU = {"yuz": ["karakter", "gorsel"], "balon": ["karakter", "metin"], "kelime": ["metin"],
                "isim": ["ad"], "giris": ["karakter"], "cikis": ["karakter"], "vurgula": ["kutu"],
                "nokta": ["indeks"], "ulke": ["kod"], "damga": ["metin"], "kose": ["deger"], "muzik": ["db"],
                "deger": ["deger"], "soluk": ["taraf"], "buyut": ["taraf"], "kart": ["id"], "ip": ["a", "b"],
                "sondur": ["oran"], "rota": ["a", "b"], "tikla": ["hedef"], "secenek": ["indeks"]}
# yalnız belirli sahne tiplerinde anlamı olan olaylar (diğerleri her sahnede)
OLAY_SAHNE = {"yuz": {"wojak"}, "balon": {"wojak"}, "giris": {"wojak"}, "cikis": {"wojak"},
              "vurgula": {"manset"}, "ulke": {"harita"}, "nokta": {"zaman_cizelgesi"},
              "ceviri": {"metin", "bolunmus"}, "deger": {"sayac"}, "panel": {"bolunmus"}, "soluk": {"bolunmus"},
              "buyut": {"bolunmus"}, "kart": {"pano"}, "ip": {"pano"}, "sondur": {"izgara"},
              "ustunu_ciz": {"metin"}, "rota": {"harita"}, "tikla": {"kapanis"}, "secenek": {"kapanis"},
              "it": {"wojak", "harita", "zaman_cizelgesi"}}   # 12. tur: it haritada ve zaman çizelgesinde de
CAPA = {"tip", "satir", "ofset", "an", "t"}

SFX_DIR = config.SFX
BREAK_RE = re.compile(r"<break\s+time=\"?([\d.]+)\s*(ms|s)\"?\s*/>", re.I)
TAG_RE = re.compile(r"<[^>]+>")


class SpecHatasi(ValueError):
    pass


# 14. tur (dil hakemi 13. tur S7): metindeki "¦" altyazı bloğunun İÇİNDE satırın nerede kırılacağını söyler ("\n" blok
# kırma ipucudur). İkisi de TTS metninden ve ekrandan çıkar: önbellek anahtarı değişmez.
SATIR_IPUCU = "¦"


def temiz_metin(s: str) -> str:
    """Altyazı/ekran metni: SSML benzeri etiketler (<break .../>), satır sonları ve altyazı satır ipuçları (¦) çıkar."""
    s = TAG_RE.sub(" ", s).replace("\n", " ").replace(SATIR_IPUCU, " ")
    s = re.sub(r"\s+", " ", s).strip()
    return re.sub(r"\s+([,.;:!?…])", r"\1", s)


def ara_sureleri(s: str) -> float:
    """Metindeki <break time="..."/> etiketlerinin toplam süresi (sn)."""
    tot = 0.0
    for v, unit in BREAK_RE.findall(s):
        tot += float(v) / (1000 if unit.lower() == "ms" else 1)
    return tot


@dataclass
class Satir:
    metin: str                   # ekranda/altyazıda görünen metin (etiketler altyazıdan çıkarılır)
    ses: str                     # ses adı (sesler anahtarı) ya da doğrudan Cartesia ses kimliği
    hiz: float = 1.0             # Gemini: sesin taban hızıyla çarpılır (atempo); Cartesia: generation_config.speed
    duygu: str | None = None
    tarz: str | None = None      # Gemini: bu satıra özel tavır tarifi (fısıltı, bağırma...); sesin tarzının yerine geçer
    once: float | None = None    # bu satırdan önce bekleme (sahnenin 'ara'sı yerine)
    sonra: float | None = None   # bu satırdan sonra ek bekleme
    tts: str | None = None       # TTS'e giden metin (verilmezse metin + telaffuz)
    balon: str | None = None     # karakter kimliği: satır o karakterin konuşma balonunda görünür
    konusan: str | None = None   # karakter kimliği: satır boyunca o karakter konuşur gibi seker (balonsuz)
    db: float = 0.0              # ortak seviyeye getirildikten sonra ek kazanç (dB; kulağa alçak gelen satır için)
    db_bas: tuple[float, float] | None = None   # (sn, dB): satırın ilk `sn`'sine ek kazanç (vurgulu giriş öbeği; Gemini
                                                # turu 2: "Bu arada bir ayrıntı:" komşularından +3,5 dB)
    # hesaplanan
    sure: float | None = None
    wav: Path | None = None
    t0: float = 0.0              # sahne içindeki başlangıç (sn)
    tahmini: bool = False

    @property
    def altyazi(self) -> str:
        return temiz_metin(self.metin)

    @property
    def t1(self) -> float:
        return self.t0 + (self.sure or 0.0)


@dataclass
class Olay:
    tip: str
    satir: int | None = None     # 1'den başlar; verilirse zaman o satıra göre
    ofset: float = 0.0
    an: str = "bas"              # bas | son (satırın başı/sonu)
    t: float | None = None       # satır yoksa sahne başına göre saniye
    p: dict = field(default_factory=dict)
    zaman: float = 0.0           # çözümlenmiş, sahne içi saniye


@dataclass
class Sfx:
    ad: str                      # assets/sfx/<ad>.wav ya da dosya yolu
    yol: Path
    satir: int | None = None
    ofset: float = 0.0
    an: str = "bas"
    t: float | None = None
    db: float = 0.0
    zaman: float = 0.0


@dataclass
class Sahne:
    tip: str
    p: dict
    satirlar: list[Satir] = field(default_factory=list)
    olaylar: list[Olay] = field(default_factory=list)
    sfx: list[Sfx] = field(default_factory=list)
    gecis: str = "kesme"         # bu sahneye GİRİŞ geçişi: kesme | gecis (crossfade) | kaydir (push)
    gecis_kare: int = 0
    sure: float | None = None
    min_sure: float | None = None
    bas: float | None = None
    ara: float | None = None
    son: float | None = None
    otomatik_sfx: bool = True
    kose: dict | None = None     # köşe göstergesi (sahne başındaki hâli)
    muzik_db: float = 0.0        # bu sahnede müzik seviyesi (dB, 0 = normal)
    muzik_mod: str | None = None  # bu sahneden itibaren müzik kipi (drone | nabiz | gerilim | major)
    filigran: bool = True        # False: bu sahnede filigran yok (ör. marka imzası)
    bolum: int = 0               # bölüm sırası (0'dan)
    yer: str = ""                # hata mesajları için "bölüm 2, sahne 3"
    # hesaplanan (zaman.py)
    no: int = 0
    sure_hesap: float = 0.0
    n_kare: int = 0
    bas_kare: int = 0


@dataclass
class Bolum:
    baslik: str
    kart: bool
    sahneler: list[Sahne]
    numara: int | None = None
    kart_sure: float = 2.6
    youtube: str | None = None   # açıklamadaki bölüm adı (verilmezse baslik)


@dataclass
class Video:
    id: str
    baslik: str
    dir: Path
    sesler: dict[str, Any]       # ad -> Cartesia ses kimliği (str) ya da Gemini {gemini, hiz, tarz}
    anlatici_ses: str
    anlatici_hiz: float
    model: str
    dil: str
    telaffuz: dict[str, str]
    muzik: dict
    zamanlama: dict
    gecis: str
    filigran: str | None
    otomatik_sfx: bool
    bolumler: list[Bolum]
    kucukresimler: list[dict]
    paket: dict
    qa_isimler: list[str]
    raw: dict
    # Gemini turu 2. hakem turu: Whisper'ın doğru okunuşu bile hep başka yazdığı kelimeler (ör. "Nejat" -> medium
    # "Necad", small "Nezat"): {kelime: [kabul edilen duyuş, ...]}. QA farkı saymaz; kulak kontrolü dinleme listesinde
    qa_duyulus: dict = field(default_factory=dict)
    hareket: dict = field(default_factory=lambda: dict(HAREKET_VARSAYILAN))

    @property
    def sahneler(self) -> list[Sahne]:
        return [s for b in self.bolumler for s in b.sahneler]

    @property
    def cikti(self) -> Path:
        """Çıktı klasörü: out/<id>-uzun/. Kısa reel aynı id'yi out/<id>/'de kullanır (episodes/<id>); ikisi aynı
        klasörü paylaşınca uzun videonun mp4'ü Short'un teslimine karışıyordu (talidomit-turkiye, 1. hakem turu)."""
        return config.OUT / f"{self.id}-uzun"

    def ses_id(self, ad: str) -> str:
        x = self.sesler.get(ad, ad)
        return x["gemini"] if isinstance(x, dict) else x

    def ses_ayari(self, ad: str) -> dict:
        """Gemini sesi: {gemini, hiz, tarz}; Cartesia sesi için boş sözlük."""
        x = self.sesler.get(ad)
        return dict(x) if isinstance(x, dict) else {}

    @property
    def saglayici(self) -> str:
        """'gemini' (model gemini-*: Google Cloud TTS) ya da 'cartesia' (sonic-*)."""
        return "gemini" if self.model.startswith("gemini") else "cartesia"

    def yol(self, p) -> Path:
        return yol_coz(p, self.dir)

    def transkript(self, satir: Satir) -> str:
        """TTS'e giden metin: telaffuz düzeltmeleri YALNIZ burada uygulanır (altyazıda değil)."""
        s = satir.tts if satir.tts is not None else satir.metin
        s = s.replace("\n", " ").replace(SATIR_IPUCU, " ")
        for yazim, okunus in self.telaffuz.items():
            s = re.sub(rf"(?<!\w){re.escape(yazim)}(?!\w)", okunus, s)
        return re.sub(r"[ \t]+", " ", s).strip()


def yol_coz(p, base: Path) -> Path:
    """Önce spesifikasyon klasörüne, sonra repo köküne göre çözer."""
    q = Path(str(p)).expanduser()
    if q.is_absolute():
        return q
    for b in (base, config.ROOT):
        if (b / q).exists():
            return (b / q).resolve()
    return (base / q).resolve()


def _hata(yer: str, msg: str):
    raise SpecHatasi(f"{yer}: {msg}" if yer else msg)


def _sayi(v, yer, ad, lo=None, hi=None) -> float:
    try:
        f = float(v)
    except (TypeError, ValueError):
        _hata(yer, f"'{ad}' sayı olmalı (verilen: {v!r})")
    if (lo is not None and f < lo) or (hi is not None and f > hi):
        _hata(yer, f"'{ad}' {lo}..{hi} aralığında olmalı (verilen: {f})")
    return f


def _bilinmeyen(d: dict, izinli: set[str], yer: str, ne: str) -> None:
    fazla = sorted(set(d) - izinli)
    if fazla:
        _hata(yer, f"bilinmeyen {ne} anahtarı: {', '.join(fazla)} (izinli: {', '.join(sorted(izinli))})")


def _gecis(v, yer) -> str:
    if v is None:
        return None
    g = GECISLER.get(str(v).lower())
    if g is None:
        _hata(yer, f"geçiş '{v}' bilinmiyor (kesme | gecis | kaydir | karart)")
    return g


def _capa(d: dict, yer: str, n_satir: int) -> dict:
    out = {}
    if "satir" in d and d["satir"] is not None:
        k = int(_sayi(d["satir"], yer, "satir"))
        if not 1 <= k <= max(n_satir, 0):
            _hata(yer, f"satir {k}: bu sahnede {n_satir} satır var (1'den başlar)")
        out["satir"] = k
    out["ofset"] = _sayi(d.get("ofset", 0.0), yer, "ofset")
    an = str(d.get("an", "bas"))
    if an not in ("bas", "son"):
        _hata(yer, f"an '{an}': bas | son olmalı")
    out["an"] = an
    if d.get("t") is not None:
        out["t"] = _sayi(d["t"], yer, "t", 0)
    return out


MUZIK_MODLARI = ("drone", "nabiz", "gerilim", "major")


def _muzik_mod(v, yer: str) -> str:
    m = str(v)
    if m not in MUZIK_MODLARI:
        _hata(yer, f"muzik_mod '{m}': {' | '.join(MUZIK_MODLARI)}")
    return m


def _satir(v, video_ses: str, video_hiz: float, sesler: dict, yer: str) -> Satir:
    if isinstance(v, str):
        if not v.strip():
            _hata(yer, "boş satır")
        return Satir(metin=v.strip(), ses=video_ses, hiz=video_hiz)
    if not isinstance(v, dict):
        _hata(yer, f"satır metin ya da sözlük olmalı: {v!r}")
    _bilinmeyen(v, {"metin", "ses", "duygu", "hiz", "once", "sonra", "tts", "balon", "konusan", "db", "tarz", "db_bas"},
                yer, "satır")
    db_bas = None
    if v.get("db_bas") is not None:
        x = v["db_bas"]
        if not (isinstance(x, (list, tuple)) and len(x) == 2):
            _hata(yer, "db_bas [sn, dB] olmalı (ör. [1.1, -3])")
        db_bas = (_sayi(x[0], yer, "db_bas sn", 0.05, 30), _sayi(x[1], yer, "db_bas dB", -9, 6))
    if not str(v.get("metin", "")).strip():
        _hata(yer, "satırda 'metin' yok")
    ses = str(v.get("ses", video_ses))
    if ses not in sesler and not re.fullmatch(r"[0-9a-f-]{36}", ses):
        _hata(yer, f"ses '{ses}' tanımlı değil (sesler: {', '.join(sesler)})")
    return Satir(metin=str(v["metin"]).strip(), ses=ses,
                 hiz=_sayi(v.get("hiz", video_hiz), yer, "hiz", 0.5, 2.0),
                 duygu=v.get("duygu"), tarz=None if v.get("tarz") is None else str(v["tarz"]), once=None if v.get("once") is None else _sayi(v["once"], yer, "once", 0),
                 sonra=None if v.get("sonra") is None else _sayi(v["sonra"], yer, "sonra", 0),
                 tts=v.get("tts"), balon=None if v.get("balon") is None else str(v["balon"]),
                 konusan=None if v.get("konusan") is None else str(v["konusan"]),
                 db=_sayi(v.get("db", 0.0), yer, "db", -6, 6), db_bas=db_bas)


def _olay(d, yer: str, n_satir: int) -> Olay:
    if not isinstance(d, dict) or "tip" not in d:
        _hata(yer, f"olay sözlük olmalı ve 'tip' içermeli: {d!r}")
    tip = str(d["tip"])
    if tip not in OLAY_TIPLERI:
        _hata(yer, f"olay tipi '{tip}' bilinmiyor ({', '.join(sorted(OLAY_TIPLERI))})")
    _bilinmeyen(d, OLAY_TIPLERI[tip] | CAPA, yer, f"'{tip}' olayı")
    for k in OLAY_ZORUNLU.get(tip, []):
        if d.get(k) in (None, ""):
            _hata(yer, f"'{tip}' olayında '{k}' zorunlu")
    p = {k: v for k, v in d.items() if k not in CAPA}
    return Olay(tip=tip, p=p, **_capa(d, yer, n_satir))


def _sfx(d, yer: str, n_satir: int, base: Path) -> Sfx:
    if isinstance(d, str):
        d = {"ad": d}
    if not isinstance(d, dict) or "ad" not in d:
        _hata(yer, f"sfx 'ad' içermeli: {d!r}")
    _bilinmeyen(d, {"ad", "db"} | CAPA - {"tip"}, yer, "sfx")
    ad = str(d["ad"])
    yol = SFX_DIR / f"{ad}.wav" if "/" not in ad and not ad.endswith(".wav") else yol_coz(ad, base)
    return Sfx(ad=ad, yol=yol, db=_sayi(d.get("db", 0.0), yer, "db", -60, 12), **_capa(d, yer, n_satir))


def _karakterler(lst, yer: str, base: Path, ne: str = "karakterler") -> list[dict]:
    out = []
    if lst is None:
        return out
    if isinstance(lst, dict) and ne == "konuk":
        lst = [lst]
    # 4. tur: 3 nesne + bir karakter (ör. molekül, cereblon, SALL4 + anlatıcı); 10. tur: konuk en çok 3 (iki karakter
    # ya da karakter + kapı + elindeki numune kutusu: talidomit-turkiye B5.4)
    en_cok = 3 if ne == "konuk" else 4
    if not isinstance(lst, list) or not 1 <= len(lst) <= en_cok:
        _hata(yer, f"{ne} 1-{en_cok} öğelik liste olmalı")
    for i, c in enumerate(lst):
        if isinstance(c, str):
            c = {"gorsel": c}
        _bilinmeyen(c, {"id", "gorsel", "taraf", "x", "boy", "giris", "bakis", "alt", "derinlik", "yon", "canli",
                        "golge"}, yer, "karakter")   # 8. tur: golge: true = havadaki nesneye yumuşak düşen gölge
        if c.get("yon") is not None and c["yon"] not in KARAKTER_YONLERI:
            _hata(yer, f"karakter yon '{c['yon']}': {' | '.join(KARAKTER_YONLERI)} (giriş/çıkış yönü; pop: yerinde "
                       f"büyüyerek belirir)")
        if "gorsel" not in c:
            _hata(yer, f"{i + 1}. karakterde 'gorsel' yok")
        c = dict(c)
        c.setdefault("id", chr(ord("a") + i))
        c["id"] = str(c["id"])
        taraf = c.get("taraf", ["sol", "sag", "orta", "orta"][i] if len(lst) > 1 else "sol")
        if taraf not in ("sol", "sag", "orta"):
            _hata(yer, f"taraf '{taraf}': sol | sag | orta")
        c["taraf"] = taraf
        if c.get("bakis") is True:  # YAML 'on' -> True
            c["bakis"] = "on"
        if c.get("derinlik") is not None:
            c["derinlik"] = _sayi(c["derinlik"], yer, "derinlik", 0, 1)
        out.append(c)
    ids = [c["id"] for c in out]
    if len(set(ids)) != len(ids):
        _hata(yer, f"karakter kimlikleri tekrar ediyor: {ids}")
    return out


def _kose(d, yer: str) -> dict:
    """Köşe göstergesi: {metin: "GÜN {} / 12", deger: 0, konum: sag_ust, renk, giris}."""
    if isinstance(d, (int, float, str)):
        d = {"deger": d}
    if not isinstance(d, dict):
        _hata(yer, f"kose sözlük olmalı: {d!r}")
    _bilinmeyen(d, {"metin", "deger", "konum", "renk", "giris", "yil"}, yer, "kose")
    d = dict(d)
    d.setdefault("metin", "{}")
    d.setdefault("deger", "")
    d.setdefault("konum", "sag_ust")
    if d["konum"] not in KOSE_KONUM:
        _hata(yer, f"kose konum '{d['konum']}': {' | '.join(KOSE_KONUM)}")
    if "{}" not in str(d["metin"]):
        d["metin"] = str(d["metin"]) + " {}"
    return d


def _panel(d, yer: str, base: Path) -> dict:
    """Bölünmüş ekran paneli: görsel (Ken Burns) ya da metin kartı (+ çeviri), üst etiket, alt not."""
    if isinstance(d, str):
        d = {"gorsel": d}
    if not isinstance(d, dict):
        _hata(yer, f"panel sözlük olmalı: {d!r}")
    _bilinmeyen(d, PANEL_ANAHTAR, yer, "panel")
    if not d.get("gorsel") and not d.get("metin"):
        _hata(yer, "panelde 'gorsel' ya da 'metin' gerekli")
    if d.get("zemin") is not None and d["zemin"] not in ZEMINLER:
        _hata(yer, f"zemin '{d['zemin']}': {' | '.join(ZEMINLER)}")
    d = dict(d)
    for k in ("gorsel", "arka"):
        if d.get(k):
            d[k] = yol_coz(d[k], base)
    return d


def _pano(p: dict, olaylar: list, yer: str, base: Path) -> None:
    kartlar = p["kartlar"]
    if not isinstance(kartlar, list) or not 1 <= len(kartlar) <= 12:
        _hata(yer, "pano kartlar 1-12 öğelik liste olmalı")
    out = []
    for i, k in enumerate(kartlar):
        if not isinstance(k, dict) or not k.get("metin"):
            _hata(yer, f"{i + 1}. kartta 'metin' yok")
        _bilinmeyen(k, KART_ANAHTAR, f"{yer}, kart {i + 1}", "kart")
        k = dict(k)
        k["id"] = str(k.get("id", i + 1))
        if k.get("stil", "kagit") not in ("kagit", "bos", "merkez", "foto"):
            _hata(yer, f"kart stil '{k['stil']}': kagit | bos | merkez | foto")
        if k.get("gorsel"):
            k["gorsel"] = yol_coz(k["gorsel"], base)
        out.append(k)
    ids = [k["id"] for k in out]
    if len(set(ids)) != len(ids):
        _hata(yer, f"kart kimlikleri tekrar ediyor: {ids}")
    p["kartlar"] = out
    ipler = []
    for j, ip in enumerate(p.get("ipler") or []):
        if isinstance(ip, dict):
            ip = [ip.get("a"), ip.get("b")]
        if not (isinstance(ip, list) and len(ip) == 2):
            _hata(yer, f"ip [a, b] olmalı: {ip!r}")
        ipler.append([str(ip[0]), str(ip[1])])
    for o in olaylar:
        if o.tip == "kart":
            o.p["id"] = str(o.p["id"])
        if o.tip == "ip":
            o.p["a"], o.p["b"] = str(o.p["a"]), str(o.p["b"])
            if [o.p["a"], o.p["b"]] not in ipler and [o.p["b"], o.p["a"]] not in ipler:
                ipler.append([o.p["a"], o.p["b"]])
        if o.tip == "damga" and o.p.get("kart") is not None:
            o.p["kart"] = str(o.p["kart"])
    for a, b in ipler:
        for x in (a, b):
            if x not in ids:
                _hata(yer, f"ip: kart '{x}' yok ({', '.join(ids)})")
    for o in olaylar:
        for x in ([o.p["id"]] if o.tip == "kart" else [o.p["kart"]] if o.tip == "damga" and o.p.get("kart") else []):
            if x not in ids:
                _hata(yer, f"olay '{o.tip}': kart '{x}' yok ({', '.join(ids)})")
    p["ipler"] = ipler


def _doku(v, yer: str):
    """wojak sahnesi arka plan dokusu: true | false | {gren: 0..0.2, toz: 0..60}."""
    if v is None or v is False:
        return False
    if v is True:
        return {"gren": 0.035, "toz": 18}
    if not isinstance(v, dict):
        _hata(yer, f"doku true | false | {{gren, toz}} olmalı: {v!r}")
    _bilinmeyen(v, {"gren", "toz"}, yer, "doku")
    return {"gren": _sayi(v.get("gren", 0.035), yer, "doku gren", 0, 0.2),
            "toz": int(_sayi(v.get("toz", 18), yer, "doku toz", 0, 60))}


def _kapanis(p: dict, olaylar: list, yer: str, base: Path) -> None:
    """Kapanış çağrısı: soru, 0-3 seçenek kartı, tıklayan karakter, düğmeler, yorum balonu."""
    sec = p.get("secenekler") or []
    if not isinstance(sec, list) or len(sec) > 3:
        _hata(yer, "kapanis secenekler 0-3 öğelik liste olmalı")
    out = []
    for i, s_ in enumerate(sec):
        if isinstance(s_, str):
            s_ = {"metin": s_}
        if not isinstance(s_, dict) or not s_.get("metin"):
            _hata(yer, f"{i + 1}. seçenekte 'metin' yok")
        _bilinmeyen(s_, {"metin", "alt", "gorsel", "harf", "bakis", "vurgu_gorsel", "damga", "hareket"},
                    f"{yer}, seçenek {i + 1}", "seçenek")
        s_ = dict(s_)
        for k_ in ("gorsel", "vurgu_gorsel"):
            if s_.get(k_):
                s_[k_] = yol_coz(s_[k_], base)
        # 11. tur (animasyon S9): vurguda kartın içindeki çizim de oynar: vurgu_gorsel (yüz değişir), damga (küçük
        # lastik damga iner: metin ya da {metin, renk}), hareket: yuvarlan (zar gibi döner ve seker) | sicra
        if s_.get("damga") is not None:
            d_ = s_["damga"]
            d_ = {"metin": d_} if isinstance(d_, str) else dict(d_)
            _bilinmeyen(d_, {"metin", "renk"}, f"{yer}, seçenek {i + 1}", "seçenek damgası")
            if not d_.get("metin"):
                _hata(yer, f"{i + 1}. seçeneğin damgasında 'metin' yok")
            s_["damga"] = d_
        if s_.get("hareket") not in (None, "yuvarlan", "sicra"):
            _hata(yer, f"{i + 1}. seçenek hareket: yuvarlan | sicra")
        out.append(s_)
    p["secenekler"] = out
    dug = p.get("dugmeler", list(KAPANIS_DUGMELERI))
    if not isinstance(dug, list) or any(d_ not in KAPANIS_DUGMELERI for d_ in dug):
        _hata(yer, f"kapanis dugmeler: {' | '.join(KAPANIS_DUGMELERI)} listesi")
    p["dugmeler"] = list(dug)
    if p.get("karakter") is not None:
        k = p["karakter"]
        k = {"gorsel": k} if isinstance(k, str) else dict(k)
        _bilinmeyen(k, {"gorsel", "yuz", "boy", "bakis", "taraf"}, yer, "kapanis karakteri")
        k["gorsel"] = yol_coz(k["gorsel"], base)
        if k.get("yuz"):
            k["yuz"] = yol_coz(k["yuz"], base)
        if k.get("taraf", "sol") not in ("sol", "sag"):
            _hata(yer, "kapanis karakter taraf: sol | sag")
        p["karakter"] = k
    if p.get("bos_alan") not in (None, False, True, "sag_ust", "sol_ust"):
        _hata(yer, "kapanis bos_alan: false | true (sağ üst) | sag_ust | sol_ust")
    for o in olaylar:
        if o.tip == "tikla" and o.p["hedef"] not in KAPANIS_DUGMELERI:
            _hata(yer, f"tikla hedef '{o.p['hedef']}': {' | '.join(KAPANIS_DUGMELERI)}")
        if o.tip == "tikla" and o.p["hedef"] not in p["dugmeler"]:
            _hata(yer, f"tikla hedef '{o.p['hedef']}' dugmeler listesinde yok")
        if o.tip == "secenek":
            k_ = int(_sayi(o.p["indeks"], yer, "secenek indeks", 1, max(1, len(out))))
            if not out:
                _hata(yer, "secenek olayı için secenekler gerekli")
            o.p["indeks"] = k_


def _hareket(v, yer: str = "hareket") -> dict:
    """Video düzeyi hareket dili (HAREKET_VARSAYILAN)."""
    out = dict(HAREKET_VARSAYILAN)
    if v is None:
        return out
    if not isinstance(v, dict):
        _hata(yer, f"hareket sözlük olmalı: {v!r}")
    _bilinmeyen(v, set(HAREKET_VARSAYILAN), yer, "hareket")
    for k in ("bulaniklik", "ikincil", "canli"):
        if k in v:
            out[k] = bool(v[k])
    if "paralaks" in v:
        out["paralaks"] = _sayi(v["paralaks"], yer, "paralaks", 0, 1)
    if "doku" in v:
        out["doku"] = _doku(v["doku"], yer)
    return out


def _sahne(d: dict, video_ctx: dict, yer: str, base: Path) -> Sahne:
    if not isinstance(d, dict) or "tip" not in d:
        _hata(yer, "sahne sözlük olmalı ve 'tip' içermeli")
    tip = TIP_TAKMA.get(str(d["tip"]), str(d["tip"]))
    if tip not in SAHNE_PARAMLARI:
        _hata(yer, f"sahne tipi '{d['tip']}' bilinmiyor ({', '.join(sorted(SAHNE_PARAMLARI))})")
    _bilinmeyen(d, SAHNE_PARAMLARI[tip] | ORTAK, yer, f"'{tip}' sahnesi")
    for k in ZORUNLU[tip]:
        if d.get(k) in (None, "", []):
            _hata(yer, f"'{tip}' sahnesinde '{k}' zorunlu")
    p = {k: v for k, v in d.items() if k not in ORTAK}
    if d.get("sfx_db") is not None:
        p["sfx_db"] = _sayi(d["sfx_db"], yer, "sfx_db", -24, 6)
    if d.get("konuk") is not None:
        if tip == "wojak":
            _hata(yer, "wojak sahnesinde konuk yok: karakterler listesini kullan")
        p["konuk"] = _karakterler(d["konuk"], yer, base, "konuk")
    satirlar = [_satir(v, video_ctx["ses"], video_ctx["hiz"], video_ctx["sesler"], f"{yer}, satır {i + 1}")
                for i, v in enumerate(d.get("satirlar") or [])]
    n = len(satirlar)
    olaylar = [_olay(o, f"{yer}, olay {i + 1}", n) for i, o in enumerate(d.get("olaylar") or [])]
    # kısayollar: isim_etiketi / kelime sahne anahtarı olarak da yazılabilir
    for anahtar, tip_o in (("isim_etiketi", "isim"), ("kelime", "kelime")):
        v = d.get(anahtar)
        if v:
            for j, o in enumerate(v if isinstance(v, list) else [v]):
                if isinstance(o, str):
                    o = {"metin": o}
                olaylar.append(_olay({"tip": tip_o, **o}, f"{yer}, {anahtar} {j + 1}", n))
    sfx = [_sfx(s, f"{yer}, sfx {i + 1}", n, base) for i, s in enumerate(d.get("sfx") or [])]
    sahne = Sahne(tip=tip, p=p, satirlar=satirlar, olaylar=olaylar, sfx=sfx, yer=yer,
                  otomatik_sfx=bool(d.get("otomatik_sfx", video_ctx["otomatik_sfx"])))
    for o in olaylar:
        izin = OLAY_SAHNE.get(o.tip)
        if izin and tip not in izin and not (o.tip in KONUK_OLAYLARI and p.get("konuk")):
            _hata(yer, f"'{o.tip}' olayı yalnız {' / '.join(sorted(izin))} sahnesinde (ya da konuklu sahnede) "
                       f"kullanılır")
    if d.get("kose") is not None:
        sahne.kose = _kose(d["kose"], yer)
    if d.get("muzik_db") is not None:
        sahne.muzik_db = _sayi(d["muzik_db"], yer, "muzik_db", -60, 12)
    if d.get("muzik_mod") is not None:
        sahne.muzik_mod = _muzik_mod(d["muzik_mod"], yer)
    if d.get("filigran") is not None:
        sahne.filigran = bool(d["filigran"])
    elif tip == "marka":
        sahne.filigran = False   # imza filigranın yerine konar; son karede filigranın yerine oturur
    for o in olaylar:
        if o.tip == "muzik":
            o.p["db"] = _sayi(o.p["db"], yer, "muzik db", -60, 12)
        if o.tip == "sondur":
            o.p["oran"] = _sayi(o.p["oran"], yer, "oran", 0, 1)
        if o.tip in ("panel", "soluk", "buyut", "ceviri") and o.p.get("taraf") is not None \
                and o.p["taraf"] not in ("sol", "sag"):
            _hata(yer, f"'{o.tip}' olayında taraf: sol | sag")
    g = _gecis(d.get("gecis"), yer) or video_ctx["gecis"]
    sahne.gecis = g
    sahne.gecis_kare = int(d.get("gecis_kare", GECIS_KARE[g]))
    for k in ("sure", "min_sure", "bas", "ara", "son"):
        if d.get(k) is not None:
            setattr(sahne, k, _sayi(d[k], yer, k, 0))
    # karakter / görsel parametreleri
    if tip == "wojak":
        p["karakterler"] = _karakterler(p.get("karakterler"), yer, base)
        ids = {c["id"] for c in p["karakterler"]}
        for o in olaylar:
            if "karakter" in o.p and str(o.p["karakter"]) not in ids:
                _hata(yer, f"olay '{o.tip}': karakter '{o.p['karakter']}' yok ({', '.join(sorted(ids))})")
            if "karakter" in o.p:
                o.p["karakter"] = str(o.p["karakter"])
        for s in satirlar:
            if s.balon is not None and s.balon not in ids:
                _hata(yer, f"satır balonu: karakter '{s.balon}' yok ({', '.join(sorted(ids))})")
            if s.konusan is not None and s.konusan not in ids:
                _hata(yer, f"satır konusan: karakter '{s.konusan}' yok ({', '.join(sorted(ids))})")
        kam = p.get("kamera") or {}
        if not isinstance(kam, dict):
            _hata(yer, "kamera sözlük olmalı: {zoom, merkez, it}")
        _bilinmeyen(kam, {"zoom", "merkez", "it", "odak", "paralaks"}, yer, "kamera")
        if kam.get("paralaks") is not None:
            kam["paralaks"] = _sayi(kam["paralaks"], yer, "kamera paralaks", 0, 1)
        if p.get("doku") is not None:
            p["doku"] = _doku(p["doku"], yer)
    else:
        for s in satirlar:
            if s.balon or s.konusan:
                _hata(yer, "satır balonu / konusan yalnız wojak sahnesinde kullanılır")
        kids = {c["id"] for c in p.get("konuk", [])}
        for o in olaylar:
            if "karakter" in o.p and o.p["karakter"] is not None:
                if str(o.p["karakter"]) not in kids:
                    _hata(yer, f"olay '{o.tip}': konuk '{o.p['karakter']}' yok ({', '.join(sorted(kids)) or 'konuk yok'})")
                o.p["karakter"] = str(o.p["karakter"])
    if tip == "zaman_cizelgesi":
        nk = p["noktalar"]
        if not isinstance(nk, list) or not 2 <= len(nk) <= 8:
            _hata(yer, "noktalar 2-8 öğelik liste olmalı (önerilen 3-6)")
        for i, n_ in enumerate(nk):
            if not isinstance(n_, dict) or "tarih" not in n_:
                _hata(yer, f"{i + 1}. noktada 'tarih' yok")
    if tip == "sayac" and p.get("deger") is None and p.get("yil") is None:
        _hata(yer, "sayac: 'deger' (ör. 10000, azalan: [60, 0]) ya da 'yil' ([1957, 1961]) gerekli")
    if tip == "sayac" and isinstance(p.get("deger"), list):
        if len(p["deger"]) != 2:
            _hata(yer, "sayac deger listesi [başlangıç, bitiş] olmalı (ör. [60, 0])")
        p["deger"] = [_sayi(x, yer, "deger") for x in p["deger"]]
    if p.get("zemin") is not None and p["zemin"] not in ZEMINLER:
        _hata(yer, f"zemin '{p['zemin']}': {' | '.join(ZEMINLER)}")
    if tip == "bolunmus":
        for taraf in ("sol", "sag"):
            p[taraf] = _panel(p[taraf], f"{yer}, {taraf} panel", base)
    if tip == "izgara":
        n_ = int(_sayi(p.get("n", 10000), yer, "n", 1, 40000))
        p["n"] = n_
    if tip == "pano":
        _pano(p, olaylar, yer, base)
    if tip == "bitis":
        p["kutular"] = int(_sayi(p.get("kutular", 2), yer, "kutular", 0, 2))
        if p.get("duzen", "yan_yana") not in ("yan_yana", "sag", "sol"):
            _hata(yer, "bitis duzen: yan_yana | sag | sol")
        if p.get("karakter") is not None:
            k = p["karakter"]
            k = {"gorsel": k} if isinstance(k, str) else dict(k)
            _bilinmeyen(k, {"gorsel", "taraf", "boy", "bakis"}, yer, "bitis karakteri")
            k["gorsel"] = yol_coz(k["gorsel"], base)
            p["karakter"] = k
    if tip == "kapanis":
        _kapanis(p, olaylar, yer, base)
    if tip == "manset":
        for o in olaylar:
            if o.tip == "vurgula" and o.p.get("stil") is not None and o.p["stil"] not in VURGU_STILLERI:
                _hata(yer, f"vurgula stil '{o.p['stil']}': {' | '.join(VURGU_STILLERI)}")
    if tip == "harita" and not (p.get("ulkeler") or p.get("vurgu")):
        _hata(yer, "harita: 'ulkeler' ya da 'vurgu' gerekli")
    if tip == "manset":
        kutular = p.get("kutular") or []
        if isinstance(kutular, list) and kutular and isinstance(kutular[0], (int, float)):
            kutular = [kutular]
        for k in kutular:
            if not (isinstance(k, list) and len(k) == 4):
                _hata(yer, f"manset kutusu [x0, y0, x1, y1] olmalı: {k!r}")
        p["kutular"] = kutular
    # dosya yolları
    for k in ("arka", "gorsel", "wojak", "yuz"):
        if p.get(k):
            p[k] = yol_coz(p[k], base)
    for c in p.get("karakterler", []) + p.get("konuk", []):
        c["gorsel"] = yol_coz(c["gorsel"], base)
    for o in olaylar:
        if o.tip == "yuz":
            o.p["gorsel"] = yol_coz(o.p["gorsel"], base)
        if o.tip == "balon" and o.p.get("agiz"):
            # 11. tur: agiz tek görsel ya da [yarık, açık] (kapalı -> yarık -> açık)
            ag = o.p["agiz"]
            if isinstance(ag, (list, tuple)):
                if not 1 <= len(ag) <= 2:
                    _hata(yer, f"balon agiz: tek görsel ya da [yarık, açık] olmalı: {ag!r}")
                o.p["agiz"] = [yol_coz(a, base) for a in ag]
            else:
                o.p["agiz"] = yol_coz(ag, base)
    return sahne


def yukle(yol) -> Video:
    """uzun/<id>/ klasörünü ya da video.yaml dosyasını yükler ve doğrular."""
    yol = Path(yol)
    if yol.is_dir():
        yol = yol / "video.yaml"
    if not yol.exists():
        raise SpecHatasi(f"bulunamadı: {yol}")
    try:
        raw = yaml.safe_load(yol.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as e:
        raise SpecHatasi(f"{yol}: YAML hatası: {e}") from e
    return yukle_sozluk(raw, yol.parent.resolve())


VIDEO_ANAHTARLARI = {"id", "baslik", "sesler", "anlatici", "model", "dil", "telaffuz", "muzik", "zamanlama",
                     "gecis", "filigran", "otomatik_sfx", "bolumler", "kucukresimler", "paket", "qa", "not",
                     "kart_bindirme", "hareket"}


def yukle_sozluk(raw: dict, base: Path) -> Video:
    _bilinmeyen(raw, VIDEO_ANAHTARLARI, "video.yaml", "üst düzey")
    for k in ("id", "baslik", "bolumler"):
        if not raw.get(k):
            raise SpecHatasi(f"video.yaml: '{k}' zorunlu")
    vid = str(raw["id"])
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", vid):
        raise SpecHatasi(f"id '{vid}': küçük harf, rakam, - ve _ kullan")
    sesler: dict[str, Any] = dict(VARSAYILAN_SESLER)
    for k, sv in (raw.get("sesler") or {}).items():
        if isinstance(sv, dict):   # Gemini sesi (UZUN_FORMAT §1.1): {gemini: Charon, hiz: 1.25, tarz: "..."}
            _bilinmeyen(sv, {"gemini", "hiz", "tarz"}, "sesler", f"'{k}' sesi")
            if not sv.get("gemini"):
                raise SpecHatasi(f"sesler.{k}: Gemini sesinde 'gemini' (ses adı, ör. Charon) zorunlu")
            sesler[str(k)] = {"gemini": str(sv["gemini"]), "hiz": _sayi(sv.get("hiz", 1.0), "sesler", f"{k}.hiz", 0.5, 2.0),
                              "tarz": str(sv.get("tarz") or "").strip()}
        else:
            sesler[str(k)] = str(sv)
    an = raw.get("anlatici") or {}
    an_ses = str(an.get("ses", "murat"))
    if an_ses not in sesler:
        raise SpecHatasi(f"anlatici.ses '{an_ses}' sesler içinde yok")
    an_hiz = _sayi(an.get("hiz", 0.95), "anlatici", "hiz", 0.5, 2.0)
    zam = dict(VARSAYILAN_ZAMANLAMA)
    for k, v in (raw.get("zamanlama") or {}).items():
        if k not in VARSAYILAN_ZAMANLAMA:
            raise SpecHatasi(f"zamanlama: bilinmeyen anahtar '{k}' ({', '.join(VARSAYILAN_ZAMANLAMA)})")
        zam[k] = _sayi(v, "zamanlama", k, 0)
    gecis = _gecis(raw.get("gecis", "kesme"), "video.yaml")
    muzik = raw.get("muzik")
    if muzik is None or muzik is True:
        muzik = {}
    if muzik is False:
        muzik = {"yok": True}
    if isinstance(muzik, str):
        muzik = {"dosya": muzik}
    muzik = dict(muzik)
    _bilinmeyen(muzik, {"uret", "dosya", "tohum", "seviye", "acik", "giris", "cikis", "yok", "baslangic", "mod"},
                "muzik", "müzik")
    if muzik.get("mod") is not None:
        _muzik_mod(muzik["mod"], "muzik")
    muzik.setdefault("tohum", zlib.crc32(vid.encode()) % 100000)
    if muzik.get("dosya"):
        muzik["dosya"] = yol_coz(muzik["dosya"], base)
    ctx = {"ses": an_ses, "hiz": an_hiz, "sesler": sesler, "gecis": gecis,
           "otomatik_sfx": bool(raw.get("otomatik_sfx", True))}
    bolumler: list[Bolum] = []
    kart_no = 0
    if not isinstance(raw["bolumler"], list):
        raise SpecHatasi("bolumler liste olmalı")
    for bi, b in enumerate(raw["bolumler"]):
        yer_b = f"bölüm {bi + 1}"
        if not isinstance(b, dict):
            raise SpecHatasi(f"{yer_b}: sözlük olmalı")
        _bilinmeyen(b, {"baslik", "kart", "numara", "sahneler", "kart_sure", "kart_ust", "kart_gecis",
                        "youtube", "not", "kart_bindirme", "kart_marka", "kart_muzik_db", "muzik_mod"}, yer_b, "bölüm")
        if not b.get("baslik"):
            raise SpecHatasi(f"{yer_b}: 'baslik' zorunlu")
        kart = bool(b.get("kart", bi > 0))
        sahneler = []
        numara = None
        if kart:
            kart_no += 1
            numara = int(b.get("numara", kart_no))
            bind = bool(b.get("kart_bindirme", raw.get("kart_bindirme", False)))
            ks = Sahne(tip="bolum_karti", p={"numara": numara, "baslik": str(b["baslik"]),
                                            "ust": b.get("kart_ust"), "bindirme": bind,
                                            "marka": bool(b.get("kart_marka", False))},
                       sure=_sayi(b.get("kart_sure", zam["bindirme"] if bind else zam["kart"]), yer_b, "kart_sure",
                                  0.5),
                       yer=f"{yer_b}, kart", otomatik_sfx=ctx["otomatik_sfx"])
            ks.gecis = _gecis(b.get("kart_gecis"), yer_b) or "kesme"
            ks.gecis_kare = GECIS_KARE[ks.gecis]
            if b.get("kart_muzik_db") is not None:   # kartta müzik kabarması (konuşma yok)
                ks.muzik_db = _sayi(b["kart_muzik_db"], yer_b, "kart_muzik_db", -60, 12)
            sahneler.append(ks)
        if not b.get("sahneler") and not kart:
            raise SpecHatasi(f"{yer_b}: 'sahneler' boş")
        for si, s in enumerate(b.get("sahneler") or []):
            sahneler.append(_sahne(s, ctx, f"{yer_b}, sahne {si + 1}", base))
        if b.get("muzik_mod") is not None and sahneler and sahneler[0].muzik_mod is None:
            sahneler[0].muzik_mod = _muzik_mod(b["muzik_mod"], yer_b)
        for s in sahneler:
            s.bolum = bi
        bolumler.append(Bolum(baslik=str(b["baslik"]), kart=kart, sahneler=sahneler, numara=numara,
                              kart_sure=float(sahneler[0].sure if kart else b.get("kart_sure", zam["kart"])),
                              youtube=b.get("youtube")))
    if bolumler and bolumler[0].sahneler:
        ilk = bolumler[0].sahneler[0]
        ilk.gecis, ilk.gecis_kare = "kesme", 0  # ilk sahnede önceki sahne yok
    tel = {str(k): str(v) for k, v in (raw.get("telaffuz") or {}).items()}
    qa = raw.get("qa") or {}
    v = Video(id=vid, baslik=str(raw["baslik"]), dir=base, sesler=sesler, anlatici_ses=an_ses,
              anlatici_hiz=an_hiz, model=str(raw.get("model", "sonic-3")), dil=str(raw.get("dil", "tr")),
              telaffuz=tel, muzik=muzik, zamanlama=zam, gecis=gecis,
              filigran=None if raw.get("filigran") is False else str(raw.get("filigran", config.WATERMARK)),
              otomatik_sfx=ctx["otomatik_sfx"], bolumler=bolumler,
              kucukresimler=list(raw.get("kucukresimler") or []), paket=dict(raw.get("paket") or {}),
              qa_isimler=[str(x) for x in (qa.get("isimler") or [])], raw=raw, hareket=_hareket(raw.get("hareket")),
              qa_duyulus={str(k): [str(x) for x in (vv if isinstance(vv, list) else [vv])]
                          for k, vv in (qa.get("duyulus") or {}).items()})
    for i, s in enumerate(v.sahneler):
        s.no = i
        if v.saglayici == "gemini":
            for j, st in enumerate(s.satirlar):
                if not v.ses_ayari(st.ses):
                    raise SpecHatasi(f"{s.yer}, satır {j + 1}: model {v.model} ama ses '{st.ses}' bir Gemini sesi değil "
                                     f"(sesler: {{{st.ses}: {{gemini: Charon, hiz: 1.25, tarz: ...}}}})")
    return v


def sahne_dosyalari(s: Sahne) -> list:
    """Sahnenin kullandığı bütün görsel dosyaları (önbellek imzası ve eksik dosya denetimi için)."""
    paths = [s.p.get(k) for k in ("arka", "gorsel", "wojak", "yuz")]
    paths += [c["gorsel"] for c in s.p.get("karakterler", []) + s.p.get("konuk", [])]
    for taraf in ("sol", "sag"):
        if isinstance(s.p.get(taraf), dict):
            paths += [s.p[taraf].get("gorsel"), s.p[taraf].get("arka")]
    paths += [k.get("gorsel") for k in s.p.get("kartlar", []) if isinstance(k, dict)]
    if isinstance(s.p.get("karakter"), dict):
        paths += [s.p["karakter"].get("gorsel"), s.p["karakter"].get("yuz")]
    paths += [x.get(k) for x in s.p.get("secenekler") or [] if isinstance(x, dict) for k in ("gorsel", "vurgu_gorsel")]
    paths += [o.p["gorsel"] for o in s.olaylar if o.tip == "yuz"]
    for o in s.olaylar:   # 11. tur: balon ağız görselleri de imzada (yeniden çizilince parça yenilensin)
        if o.tip == "balon" and o.p.get("agiz"):
            ag = o.p["agiz"]
            paths += list(ag) if isinstance(ag, (list, tuple)) else [ag]
    return [x for x in paths if x]


def eksik_dosyalar(v: Video) -> list[str]:
    """Var olmayan görsel/ses dosyaları (sahne yeriyle)."""
    out = []
    for s in v.sahneler:
        paths = sahne_dosyalari(s)
        paths += [x.yol for x in s.sfx]
        for p in paths:
            if p is not None and not Path(p).exists():
                out.append(f"{s.yer}: {p}")
    if v.muzik.get("dosya") and not Path(v.muzik["dosya"]).exists():
        out.append(f"muzik: {v.muzik['dosya']}")
    return out
