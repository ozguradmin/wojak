"""Yayın öncesi dil ve içerik denetimi (özellikle güncel olaylar için).

Kaynak: docs/GUNDEM.md > Hukuk. Sansürlü yazım (k4til, c!nayet) hukuki koruma SAĞLAMAZ; burada
kelimeler anlamına göre (maskelenmiş hâlleri dahil) denetlenir. Hukuki tavsiye değildir.
"""

from __future__ import annotations

import re
from pathlib import Path

from . import config
from .episode import Episode

# Maskelenmiş yazımları da yakalamak için: harf yerine gelebilecek karakterler
_MASK = {"a": "[a4@*]", "e": "[e3*]", "i": "[iı1!*]", "ı": "[ıi1!*]", "o": "[o0ø*]", "ö": "[öo0ø*]",
         "u": "[uü*]", "ü": "[üu*]", "s": "[s$5*]", "ş": "[şs$*]", "g": "[gğ*]", "ğ": "[ğg*]", "c": "[cç*]",
         "ç": "[çc*]", "t": "[t7*]", "l": "[l1!*|]"}


def _rx(word: str) -> re.Pattern:
    return re.compile(r"(?<!\w)" + "".join(_MASK.get(ch, re.escape(ch)) for ch in word), re.IGNORECASE)


# Hüküm kesinleşmeden kullanılmaz (masumiyet karinesi, TCK 285/5, 126; Basın Meslek İlkeleri md. 9)
_HUKUM = ["katil", "cani", "sapık", "itiraf", "canavar", "vahşi", "şeytan", "suçlu"]
# Hiç işlenmez
_YASAK = {"intihar": "intihar olayları işlenmez (DSÖ rehberi; yöntem/mekân verilmez)",
          "tecavüz": "cinsel suç konusu işlenmez",
          "istismar": "istismar konusu işlenmez"}
# İngilizce kanal (kanal: en): aynı kurallar, İngilizce kelimelerle
_HUKUM_EN = ["killer", "murderer", "guilty", "monster", "psycho", "confessed", "evil"]
_YASAK_EN = {"suicide": "intihar olayları işlenmez (DSÖ rehberi; yöntem/mekân verilmez)",
             "rape": "cinsel suç konusu işlenmez",
             "abuse": "istismar konusu işlenmez"}
_DIL = {
    "tr": {"hukum": _HUKUM, "yasak": _YASAK, "cocuk": r"(?<!\w)(?:[1-9]|1[0-7]) yaşındaki",
           "kaynak": ("Kaynak:", "açıklamasına göre"), "kart": r"sonra$"},
    "en": {"hukum": _HUKUM_EN, "yasak": _YASAK_EN, "cocuk": r"(?<!\w)(?:[1-9]|1[0-7])-year-old",
           "kaynak": ("Source:", "according to"), "kart": r"later$"},
}


def _texts(ep: Episode) -> dict[str, str]:
    t = {"başlık": ep.title, "açıklama": ep.caption, "sabit yorum": ep.pinned_comment}
    for i, s in enumerate(ep.scenes, 1):
        for k in ("text", "banner", "label"):
            v = getattr(s, k)
            if v:
                t[f"sahne {i} {k}"] = v
    if ep.top_text:
        t["üst yazı"] = ep.top_text
    if ep.hashtags:  # açıklamalara olduğu gibi gider (sansürsüz)
        t["hashtag"] = " ".join(ep.hashtags)
    return t


def check(ep: Episode) -> list[str]:
    """Uyarı listesi döndürür (boş = sorun bulunmadı)."""
    out: list[str] = []
    texts = _texts(ep)
    dil = _DIL[ep.kanal]
    if ep.gundem:
        if not ep.kesin_hukum:
            for w in dil["hukum"]:
                r = _rx(w)
                for where, txt in texts.items():
                    if r.search(txt or ""):
                        out.append(f"[masumiyet] '{w}' ({where}) — hüküm kesinleşmemiş: 'şüpheli', 'iddiaya göre' kullan")
        for w, why in dil["yasak"].items():
            r = _rx(w)
            if any(r.search(t or "") for t in texts.values()):
                out.append(f"[kırmızı çizgi] '{w}': {why}")
        if ep.duration > 17.5:
            out.append(f"[format] güncel olayda süre {ep.duration:.1f} sn; veriye göre 10-17 sn")
        if len(ep.title.split()) <= 3:
            out.append("[başlık] sadece isim/etiket gibi duruyor; 'kim + sıradan eylem + ters dönen son' kalıbı daha iyi")
        if not ep.top_text:
            out.append("[bağlam] güncel olayda üst yazıya tarih/yer bağlamı ekle (YouTube: bağlam videonun içinde olmalı)")
        if not any(k in ep.pinned_comment for k in dil["kaynak"]):
            out.append("[kaynak] sabit yorumda resmi kaynak ve tarih yok ('X Valiliği'nin 12.10 14:30 açıklamasına göre...')")
    if re.search(dil["cocuk"], " ".join(t for t in texts.values() if t), re.IGNORECASE):
        out.append("[çocuk] 18 yaş altı kişi geçiyor: isim, yüz, okul, mahalle, ebeveyn adı olmamalı")
    return out


# --- Stil denetimi (docs/STIL.md: 30 orijinal reel'in ölçüleri) -------------------------------

def _speaker(img: Path) -> str:
    """Aynı karakterin yüz varyantları (assets/kit/<kit>/...) tek konuşmacı sayılır."""
    p = Path(img)
    return f"kit:{p.parent.name}" if p.parent.parent.name == "kit" else str(p)


def stil(ep: Episode) -> list[str]:
    import re
    from . import config
    out: list[str] = []
    seen_evidence = False
    sides: dict[str, str] = {}
    bgs = []
    for i, s in enumerate(ep.scenes, 1):
        tag = f"sahne {i}"
        if s.type == "evidence":
            seen_evidence = True
            if len(s.images) > 1:
                out.append(f"[stil] {tag}: kanıtta tek görsel (gerekirse hazır kolaj); ızgara orijinallerde yok")
            if not 1.0 <= s.duration <= 2.5:
                out.append(f"[stil] {tag}: kanıt süresi {s.duration} sn (orijinal ~1,5 sn)")
        elif seen_evidence:
            out.append(f"[stil] {tag}: kanıttan sonra {s.type} var; orijinallerde video kanıtla biter (0/30)")
        if s.type == "card":
            if s.text and not re.search(_DIL[ep.kanal]["kart"], s.text.strip(), re.IGNORECASE):
                ornek = "'Bir süre sonra', 'Birkaç saat sonra'" if ep.kanal == "tr" else "'A while later', 'A few hours later'"
                out.append(f"[stil] {tag}: kart yalnız ileri zaman atlaması olmalı ({ornek})")
            if not 1.4 <= s.duration <= 2.0:
                out.append(f"[stil] {tag}: kart süresi {s.duration} sn (orijinal 1,5)")
        if s.type == "dialog":
            if len(s.chars) != 1:
                out.append(f"[stil] {tag}: diyalog sahnesinde {len(s.chars)} karakter; her sahnede tam 1 konuşan olmalı")
            for c in s.chars:
                k = _speaker(c.img)
                if k in sides and sides[k] != c.side:
                    out.append(f"[stil] {tag}: aynı karakter taraf değiştirdi ({sides[k]} -> {c.side}); A hep sol, B hep sağ")
                sides.setdefault(k, c.side)
                if not 0.42 <= c.height <= 0.55:
                    out.append(f"[stil] {tag}: karakter boyu {c.height} (orijinal 0,42-0,55, medyan 0,48)")
            if s.bg:
                bgs.append(str(s.bg))
            if not 2.0 <= s.duration <= 3.05:
                out.append(f"[stil] {tag}: diyalog süresi {s.duration} sn (orijinal 2,0-3,0; çoğu 2,5)")
            t = (s.text or "").strip()
            if t:
                if re.search(r"(\.\.|…)", t) or t.endswith("."):
                    out.append(f"[stil] {tag}: replikte nokta/üç nokta var; orijinallerde 0/121")
                if len(t.split()) > 11:
                    out.append(f"[stil] {tag}: replik {len(t.split())} kelime (en fazla 11, medyan 5)")
        if abs(s.duration * 2 - round(s.duration * 2)) > 0.04:
            out.append(f"[stil] {tag}: süre {s.duration} sn; orijinallerde kesmeler 0,5 sn ızgarasında")
        for k, bad in (("zoom", s.zoom != 1.0), ("shake", bool(s.shake)), ("flash", s.flash), ("darken", bool(s.darken)),
                       ("grayscale", s.grayscale), ("label", bool(s.label)), ("banner", bool(s.banner)), ("sfx", bool(s.sfx))):
            if bad:
                out.append(f"[stil] {tag}: '{k}' kullanılmış; orijinallerde yok (hareket/efekt/etiket 0/30)")
        if any(c.pop for c in s.chars):
            out.append(f"[stil] {tag}: pop-in var; orijinallerde yok")
    if len(set(bgs)) > 2:
        out.append(f"[stil] {len(set(bgs))} farklı diyalog arka planı; orijinallerde 1 (en fazla 2, ikincisi karttan sonra)")
    if not seen_evidence:
        out.append("[stil] kanıt sahnesi yok (25/30 reel kanıtla biter; yoksa son replik güçlü bir ters köşe olmalı)")
    if ep.duration > config.MAX_DURATION + 0.05:
        out.append(f"[stil] toplam {ep.duration:.1f} sn; imza ses 13,75 sn, en fazla 14,0 sn")
    if ep.music is None:
        out.append("[stil] müzik yok; orijinallerin 27/30'u kanalın imza sesini kullanıyor (music: kanal)")
    elif ep.music.file.resolve() not in (config.MUSIC_CHANNEL.resolve(), config.MUSIC_FALLBACK.resolve(),
                                      *(p.resolve() for p in config.MUSIC_IMZA_VARYANT)):
        out.append("[stil] imza ses dışında bir müzik (music: kanal önerilir)")
    return out


# --- Hakem öncesi ön kontrol (docs/OGRENILENLER.md "Ek dersler": hakemlerin tekrar tekrar MUST verdiği kusurlar) ---
# Yalnız uyarı: teslimi durdurmaz. Eşikler notlardaki ölçümlerden; yayınlanan bölümlerde (episodes/*) kalibre edildi.

KANIT_MIN = 537          # kanıtın kısa kenarı (px, 1080 kare); 482 px'lik kırpım hakemde MUST (Lady Be Good, 25.10)
KANIT_MAX_H = 816        # yatay kanıt yüksekliği (STIL §8: 537-816); 820'lik kupür düzeltildi (Göbeklitepe, 24.10)
KANIT_BUYUTME = 1.5      # kaynağı bundan fazla büyütülen kanıt bulanık okunur (560 -> 1080, 1,93x: MUST)
LAPLAS_ALT = 2.5         # kenar Laplace varyansı (720 ölçeği): düz gökyüzü ~2 "gradyan, gerçek yer değil" (25.10);
LAPLAS_UST = 60.0        #   Kanuni (bu ölçümle 2,8) kabul. Orijinal medyan 22, IQR 11-47 (STIL); servi 143 keskin (24.10)
DOYGUNLUK_UST = 0.45     # orijinal medyan 0,20; 0,57 (D.B. Cooper) ve 0,60 (Violet) reddedildi; kabul edilen
                         #   Dakhla (Lady Be Good) bu ölçümle 0,42. Hedef yine <= 0,35
BASLIK_ORTAK = 0.5       # başlık, son repliğin anahtar kelimelerinin en az yarısını (ve 2 kelime) taşıyorsa


def _satirlar(s) -> list[str] | None:
    """Rendererın (compose.dialog_text) kıracağı satırlar; elle kırılmış ('\\n') ya da baloncuk yazı için None."""
    from . import text
    if s.type != "dialog" or not s.text or "\n" in s.text or s.text_style != "outline":
        return None
    _, lines, _ = text.fit_text(s.text, config.FONT_DIALOG, s.text_size, config.DIALOG_MAX_W, config.DIALOG_MAX_LINES,
                                config.DIALOG_STROKE, config.DIALOG_MIN_SIZE, "greedy")
    return lines


def yetim(ep: Episode) -> list[str]:
    """Satır sonu yetim kelime ve bölünen özel ad. 55 px'te satır ~26-27 karakterde kırılıyor; Göbeklitepe'de üç
    replikte, Lusitania'da ("for / Saturday") ve Mona Lisa'da ("Seriously?") hakem MUST verdi. "Türk Hava / Yolları"
    okunmadı (Tahran, 26.10). Çözüm: virgülde elle kırım ('\\n') ya da kısaltma."""
    out = []
    for i, s in enumerate(ep.scenes, 1):
        lines = _satirlar(s)
        if not lines or len(lines) < 2:
            continue
        if len(lines[-1].split()) == 1:
            out.append(f"[yetim] sahne {i}: son satırda tek kelime kalıyor ('{lines[-1]}'); virgülde elle kır (\\n) "
                       f"ya da kısalt")
        for a, b in zip(lines, lines[1:]):
            son, ilk = a.split()[-1], b.split()[0]
            if (son[:1].isupper() and ilk[:1].isupper() and son[-1].isalnum() and "'" not in son
                    and "’" not in son and ilk not in ("I", "I'm", "I'll", "I've")):
                out.append(f"[yetim] sahne {i}: özel ad iki satıra bölünüyor ('{son} / {ilk}'); elle kır ya da kısalt")
    return out


_NOKTALAMA = "\"'“”‘’.,;:?()«»"
_SANSURLU = re.compile(r"\w+[*!]+\w+|(?<![\w*])\*+\w+")   # kelime İÇİNDE * ya da ! ("d*ed", "S!lahdar", "*lüm"); "Dur!" değil


def sansur_izi(ep: Episode) -> list[str]:
    """Sansürün bozduğu kelimeler. censor.metin başlık ve hikâyede "died"ı "d*ed", "Silahdar"ı "S!lahdar" yapıyor;
    hakem ve izleyici bunu yazım hatası okuyor (Lady Be Good, Lusitania, Violet Jessop, Mona Lisa; Kanuni). Ekrandaki
    yazı sansürlenmez: orada görülen yıldız elle yazılmıştır. TR'de kasıtlı maskeleme varsa (öl-, cinayet) bilerek geç."""
    from . import censor
    out = []
    ekran = {f"sahne {i} yazı": s.text for i, s in enumerate(ep.scenes, 1) if s.text}
    if ep.top_text:
        ekran["üst yazı"] = ep.top_text
    for where, t in ekran.items():
        bad = sorted(set(_SANSURLU.findall(t)))
        if bad:
            out.append(f"[sansür] {where}: ekranda sansürlü yazım ({', '.join(bad)}); izleyici yazım hatası okur")
    for where, t in (("başlık", ep.title), ("hikâye/açıklama", ep.pinned_comment)):
        ham = (t or "").split()
        if len(ham) != len(censor.metin(t or "", ep.kanal).split()):
            continue
        degisen = []
        for a, b in zip(ham, censor.metin(t or "", ep.kanal).split()):
            a, b = a.strip(_NOKTALAMA), b.strip(_NOKTALAMA)
            if a != b and f"{a} -> {b}" not in degisen:
                degisen.append(f"{a} -> {b}")
        if degisen:
            ek = "" if len(degisen) <= 5 else f" (+{len(degisen) - 5})"
            oneri = "'passed away', 'did not survive', 'body'" if ep.kanal == "en" else "'vefat', 'hayatını kaybetti'"
            out.append(f"[sansür] {where}: {', '.join(degisen[:5])}{ek}; kasıtlı değilse karşılık kullan ({oneri})")
    return out


def _kanit_boyu(p: Path, box: int = config.BOX) -> tuple[int, int, float]:
    """compose.contain_fit'in vereceği ölçü (dosyayı çözmeden) ve büyütme oranı."""
    from PIL import Image
    with Image.open(p) as im:
        w, h = im.size
        if im.getexif().get(0x0112) in (5, 6, 7, 8):   # load_rgba exif_transpose uygular
            w, h = h, w
    r = min(box / w, box / h)
    return round(w * r), round(h * r), r


def kanit_boyu(ep: Episode) -> list[str]:
    """Kanıt görseli 1080 karede çok küçük (kısa kenar < 537), yatayda 816'dan yüksek ya da fazla büyütülmüş mü."""
    out = []
    for i, s in enumerate(ep.scenes, 1):
        if s.type != "evidence" or len(s.images) != 1:
            continue
        w, h, r = _kanit_boyu(s.images[0])
        ad = s.images[0].name
        if min(w, h) < KANIT_MIN:
            out.append(f"[kanıt] sahne {i}: {ad} karede {w}x{h}; kısa kenar {KANIT_MIN} px altı, hakem küçük buluyor")
        elif w >= h and h > KANIT_MAX_H:
            out.append(f"[kanıt] sahne {i}: {ad} karede {w}x{h}; yatay/kare kanıt en fazla {KANIT_MAX_H} px yüksek "
                       f"(STIL §8: 537-816), kırp")
        if r > KANIT_BUYUTME:
            out.append(f"[kanıt] sahne {i}: {ad} {r:.2f}x büyütülüyor (bulanık); büyütmesiz, tam genişlikte görsel seç")
    return out


def arka_plan_olcu(s) -> tuple[float, float, float]:
    """(kenar Laplace varyansı, doygunluk, parlaklık): rendererın kırpıp yumuşattığı arka plan, 720 ölçeğinde.
    Laplace üst şerit + iki yan şeritte (yazı ve karakter dışı; notlardaki ölçümle aynı), doygunluk HSV ortalaması."""
    import numpy as np
    from PIL import Image, ImageFilter
    from .compose import cover_fit
    with Image.open(s.bg) as im:
        bg = cover_fit(im.convert("RGB"), config.BOX, config.BOX, s.focus)
    if s.blur:
        bg = bg.filter(ImageFilter.GaussianBlur(s.blur))
    bg = bg.resize((720, 720), Image.LANCZOS)
    g = np.asarray(bg.convert("L"), dtype=float)

    def lap(a):
        return (a[:-2, 1:-1] + a[2:, 1:-1] + a[1:-1, :-2] + a[1:-1, 2:] - 4 * a[1:-1, 1:-1]).var()

    lv = float(np.mean([lap(g[:150]), lap(g[:, :150]), lap(g[:, 570:])]))
    sat = float(np.asarray(bg.convert("HSV"))[..., 1].mean() / 255)
    return lv, sat, float(g.mean())


def arka_plan(ep: Episode) -> list[str]:
    """Diyalog arka planı altın dönem aralığında mı: doygun (kartpostal/gün batımı) ya da düz/aşırı keskin."""
    out, gor = [], set()
    for i, s in enumerate(ep.scenes, 1):
        if s.type != "dialog" or not s.bg or s.grayscale or (s.bg, s.blur, s.focus) in gor:
            continue
        gor.add((s.bg, s.blur, s.focus))
        lv, sat, br = arka_plan_olcu(s)
        olcu = f"Laplace {lv:.1f}, doygunluk {sat:.2f}, parlaklık {br:.0f}"
        if sat > DOYGUNLUK_UST:
            out.append(f"[arka plan] sahne {i}: {s.bg.name} çok doygun ({olcu}); orijinal ~0,20: "
                       f"ImageEnhance.Color(0.6) gibi indir, değişikliği credits'e yaz")
        if lv < LAPLAS_ALT:
            out.append(f"[arka plan] sahne {i}: {s.bg.name} düz/çok yumuşak ({olcu}); orijinal medyan 22: "
                       f"blur'u düşür ya da dokulu kırpım seç")
        elif lv > LAPLAS_UST:
            out.append(f"[arka plan] sahne {i}: {s.bg.name} çok keskin ({olcu}); orijinal medyan 22: blur'u artır")
    return out


_DURAK = set("""bu şu o bir ve ile da de mi mı mu mü ne neden niye nasıl nereden nerede nereye kim kime hangi gibi için
kadar daha çok en ki ya bekle usta hocam efendi paşam sizin bizim benim senin onun bana sana bize size ben sen biz siz
onlar var yok mi bile hep şimdi zaten acaba the a an this that these those is are was were be been it its wait what why
where who how my your his her our their to of in on at for with and or but did do does you i we they he she me us
them so still just now then there here oh hey sir""".split())
_OLUMSUZ = re.compile(r"(?:m[ae]d[ıi]|m[ae]m[ıi]ş|m[ae]z|yok|değil|hiç|n't|^no|^not|^never|^nothing|^none|^without)$")


def _kelimeler(t: str) -> list[str]:
    t = (t or "").replace("I", "ı").replace("İ", "i").lower()
    return re.findall(r"[^\W\d_]+(?:['’][^\W\d_]+)?", t)


def _taban(w: str) -> str:
    """Kesme işaretinden önceki kısım: "Almanya'da" -> "almanya", "where's" -> "where"."""
    return re.split(r"['’]", w)[0]


def _kok(w: str) -> str:
    """Kaba kök: tabanın ilk 5 harfi (Türkçe ekleri ve İngilizce çoğulları yutar)."""
    return _taban(w)[:5]


def baslik_ters_kose(ep: Episode) -> list[str]:
    """Başlık ters köşeyi söylüyor mu: son repliğin anahtar kelimeleri başlıkta. Midas'ta "...içinden tek bir altın
    çıkmadı" başlığı son repliği ("neden hiç altın yok?") önceden cevapladı, ilk turdaki tek MUST (25.10).
    İki kural: (1) başlık son repliğin anahtar kelimelerinin yarısını (en az 2) taşıyor ve biri önceki repliklerde
    geçmeyen YENİ kelime (ters köşenin kendisi; Orban'daki "dev top" kurulumdur); (2) başlık olumsuz (çıkmadı, yok,
    never) ve son replikle ortak bir cins ad var (özel ad kurulumdur, sayılmaz). Yaygın kelimeler (bekle, wait) atılır."""
    diyalog = [s.text for s in ep.scenes if s.type == "dialog" and s.text]
    if not diyalog or not ep.title:
        return []
    son = diyalog[-1]
    kelime = {}   # kök -> son replikteki ilk yazılışı
    adlar = set()
    for w in re.findall(r"[^\W\d_]+(?:['’][^\W\d_]+)?", son):
        k = _kelimeler(w)
        if not k or _taban(k[0]) in _DURAK or len(k[0]) <= 2:
            continue
        kelime.setdefault(_kok(k[0]), w)
        if w[:1].isupper():
            adlar.add(_kok(k[0]))
    once = {_kok(w) for t in diyalog[:-1] for w in _kelimeler(t)}
    baslik = _kelimeler(ep.title)
    ortak = set(kelime) & {_kok(w) for w in baslik if _taban(w) not in _DURAK}
    olumsuz = any(_OLUMSUZ.search(w) for w in baslik)
    if ((len(ortak) >= 2 and len(ortak) / len(kelime) >= BASLIK_ORTAK and ortak - once)
            or (olumsuz and ortak - adlar)):
        return [f"[başlık] başlık son repliğin cevabını veriyor olabilir (ortak: "
                f"{', '.join(sorted(kelime[k] for k in ortak))}); başlık kanca + somut ayrıntı olsun, ters köşe videoda kalsın"]
    return []


BASLIK_EN_COK = 60


def baslik_uzun(ep: Episode) -> list[str]:
    """Başlık 60 karakteri aşıyor mu. En çok izlenen TR başlıkları 43-57 karakter, en az izlenenler 69-88 (31.10 verisi:
    kasikci-elmasi 54, midas-mezari-altin 57; pera-palas-anahtar-1979 88, ankara-elci-vagonlari 85)."""
    n = len((ep.title or "").strip())
    if n > BASLIK_EN_COK:
        return [f"[başlık] başlık {n} karakter (en çok {BASLIK_EN_COK}); kısalt, ünlü çapayı koru (el kitabı §5)"]
    return []


def hakem_oncesi(ep: Episode) -> list[str]:
    """Hakemden önce yakalanabilen kusurlar (uyarı). Biri hata verirse (eksik dosya vb.) diğerleri yine çalışır."""
    out: list[str] = []
    for fn in (yetim, sansur_izi, kanit_boyu, arka_plan, baslik_ters_kose, baslik_uzun):
        try:
            out += fn(ep)
        except (OSError, ValueError) as e:
            out.append(f"[ön kontrol] {fn.__name__} çalışmadı: {e}")
    return out
