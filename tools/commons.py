#!/usr/bin/env python3
"""Wikimedia Commons: ara, lisans + atıf oku, 429'a takılmadan indir. Internet Archive araması.

    python tools/commons.py ara "Hagia Sophia runic inscription" [-n 10]
    python tools/commons.py bilgi "File:Harbor in Moudros, Lemnos Greece.jpg"     # lisans + atıf satırı
    python tools/commons.py indir "File:..." episodes/<id>/img/kaynak.jpg [--genislik 1280]
    python tools/commons.py ia-ara "Lusitania warning 1915" [-n 10]

Her oturum bu yardımcıyı /tmp altında yeniden yazıyordu (docs/OGRENILENLER.md, 21-28.10.2026); dersler burada:
- Küçük resim yalnız STANDART genişlikte (960/1280/1920): Commons onları önbellekten verir. Başka bir `iiurlwidth`
  (790/1800/2400) ya da özgünden büyük/eşit genişlik `thumbnail_unscaled` özgün yolu döndürüyor ve 429'da kalıyor
  (goeben-fes-1914 / pera-palas, 28.10). Küçük resim inmezse md5 özgün yoluna düşülür (21-25.10'da çalışan yol).
- İstekler arası en az ~3 sn; 429/503'te Retry-After'a uy, yoksa 15/30/60 sn geri çekil, en fazla 4 deneme.
- User-Agent aracı tanıtır ama e-posta ya da kişisel tanımlayıcı TAŞIMAZ (bir hakem e-posta koymuştu, §3.10).
- Lisans extmetadata'dan (LicenseShortName, Artist, Credit, UsageTerms, DateTimeOriginal). Kabul: kamu malı, CC0,
  CC BY, CC BY-SA. Red: NC, ND, fair use, bilinmeyen. `bilgi` ham sayfadaki (`action=raw`) lisans şablonlarını da
  gösterir: API'nin "Public domain" kısa adı tek başına yetmez (kanuni-gizlenen-olum, 23.10).
"""

from __future__ import annotations

import argparse
import email.utils
import hashlib
import html
import re
import sys
import time
from pathlib import Path
from urllib.parse import quote, unquote

API = "https://commons.wikimedia.org/w/api.php"
INDEX = "https://commons.wikimedia.org/w/index.php"
UPLOAD = "https://upload.wikimedia.org/wikipedia/commons"
IA_ARA = "https://archive.org/advancedsearch.php"
UA = "TarihselWojakAraclari/1.0 (tools/commons.py; Commons lisans ve gorsel indirici) python-requests"
STANDART = (960, 1280, 1920)
ARALIK = 3.0          # istekler arası en az (sn); 28.10'da ~3 sn arayla 4. aramada 429 görüldü -> geri çekilme şart
DENEME = 4
GERI_CEKIL = 15.0     # 15, 30, 60 sn
META = ("LicenseShortName", "LicenseUrl", "Artist", "Credit", "UsageTerms", "DateTimeOriginal", "ImageDescription",
        "Copyrighted", "AttributionRequired")

_bekle = time.sleep   # testlerde değiştirilir
_son = 0.0
_oturum = None


class CommonsHatasi(RuntimeError):
    pass


def _session():
    global _oturum
    if _oturum is None:
        import requests
        _oturum = requests.Session()
        _oturum.headers["User-Agent"] = UA
    return _oturum


def _retry_after(deger: str | None) -> float | None:
    """Retry-After: saniye ya da HTTP tarihi."""
    if not deger:
        return None
    if deger.strip().isdigit():
        return float(deger)
    try:
        return max(0.0, email.utils.parsedate_to_datetime(deger).timestamp() - time.time())
    except (TypeError, ValueError):
        return None


def _get(url: str, params: dict | None = None, timeout: float = 60):
    """Kibar GET: istekler arası ARALIK, 429/503'te Retry-After ya da üstel geri çekilme, en fazla DENEME kez."""
    global _son
    son_hata = ""
    for k in range(DENEME):
        bekle = _son + ARALIK - time.monotonic()
        if bekle > 0:
            _bekle(bekle)
        _son = time.monotonic()
        oturum = _session()
        try:
            r = oturum.get(url, params=params, timeout=timeout)
        except Exception as e:  # ağ kesintisi, zaman aşımı
            son_hata = f"{type(e).__name__}: {e}"
            r = None
        if r is not None and r.status_code == 200:
            return r
        if r is not None and r.status_code not in (429, 500, 502, 503, 504):
            raise CommonsHatasi(f"HTTP {r.status_code}: {url}")
        if r is not None:
            son_hata = f"HTTP {r.status_code}"
        if k + 1 < DENEME:
            ra = _retry_after(r.headers.get("Retry-After")) if r is not None else None
            _bekle(min(ra if ra is not None else GERI_CEKIL * 2 ** k, 180))
    raise CommonsHatasi(f"{DENEME} denemede olmadı ({son_hata}): {url}")


def _api(**params) -> dict:
    params = {"action": "query", "format": "json", "formatversion": "2", **params}
    return _get(API, params).json()


# --- Saf yardımcılar (ağsız; testli) -----------------------------------------------------------------------------

def dosya_adi(baslik: str) -> str:
    """'File:Harbor in X.jpg' (ya da dosya sayfası adresi) -> 'Harbor_in_X.jpg': Commons'un depoladığı ad
    (ilk harf büyük, boşluk alt çizgi)."""
    if "/wiki/" in baslik:
        baslik = unquote(baslik.split("/wiki/", 1)[1])
    ad = re.sub(r"^(?:File|Dosya|Image):", "", baslik.strip(), flags=re.IGNORECASE).strip().replace(" ", "_")
    return ad[:1].upper() + ad[1:]


def md5_url(baslik: str) -> str:
    """Özgün dosyanın upload yolu: /<md5[0]>/<md5[:2]>/<ad>. API'ye uğramadan iner."""
    ad = dosya_adi(baslik)
    h = hashlib.md5(ad.encode("utf-8")).hexdigest()
    return f"{UPLOAD}/{h[0]}/{h[:2]}/{quote(ad)}"


def thumb_url(baslik: str, genislik: int) -> str:
    """Standart genişlikte küçük resim yolu (önbellekte). Standart dışı genişlik istenmez."""
    if genislik not in STANDART:
        raise ValueError(f"standart dışı genişlik {genislik}; yalnız {STANDART} (başkası 429'da kalıyor)")
    ad = dosya_adi(baslik)
    h = hashlib.md5(ad.encode("utf-8")).hexdigest()
    q = quote(ad)
    uzanti = ad.rsplit(".", 1)[-1].lower()
    if uzanti == "svg":
        son = f"{genislik}px-{q}.png"
    elif uzanti in ("tif", "tiff"):
        son = f"lossy-page1-{genislik}px-{q}.jpg"
    elif uzanti in ("pdf", "djvu"):
        son = f"page1-{genislik}px-{q}.jpg"
    else:
        son = f"{genislik}px-{q}"
    return f"{UPLOAD}/thumb/{h[0]}/{h[:2]}/{q}/{son}"


def genislik_sec(istenen: int, ozgun: int) -> int | None:
    """İstenen genişliğe en yakın STANDART genişlik; özgünden KÜÇÜK olmalı (eşit/büyükse Commons özgün yolu verir,
    o da 429). Hiçbiri uymuyorsa None: özgün dosya zaten küçük, md5 yolundan in."""
    adaylar = [w for w in STANDART if w < ozgun]
    if not adaylar:
        return None
    ustu = [w for w in adaylar if w >= istenen]
    return min(ustu) if ustu else max(adaylar)


def gecerli_thumb(url: str) -> bool:
    """API'nin döndürdüğü thumburl gerçekten önbellek yolu mu (`thumbnail_unscaled` = özgün yol, 429)."""
    return bool(url) and "thumbnail_unscaled" not in url and "/thumb/" in url


def duz_metin(s: str | None) -> str:
    """extmetadata HTML'ini düz metne çevirir."""
    s = re.sub(r"<[^>]+>", " ", s or "")
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


_RED = [(r"\bnc\b|non-?commercial", "ticari olmayan (NC)"), (r"\bnd\b|no-?deriv", "türetme yasak (ND)"),
        (r"fair[ _-]?use|non-?free|all rights reserved", "adil kullanım / telifli")]
_KABUL = [(r"\bcc0\b|cc-zero|public domain|^pd\b|^pd-|\bpdm\b|no restrictions|no known copyright", "kamu malı / CC0"),
          (r"\bcc[ -]by[ -]sa\b|\bcc-by-sa", "CC BY-SA"), (r"\bcc[ -]by\b|\bcc-by|^attribution\b", "CC BY")]


def lisans_sinifi(kisa_ad: str | None, kullanim: str | None = "") -> tuple[bool, str]:
    """(kabul, neden). Önce red (NC/ND/fair use), sonra kabul (PD/CC0/CC BY/CC BY-SA); gerisi bilinmeyen = red."""
    t = f"{duz_metin(kisa_ad)} | {duz_metin(kullanim)}".lower().strip(" |")
    if not t:
        return False, "lisans bilgisi yok"
    for rx, neden in _RED:
        if re.search(rx, t):
            return False, neden
    for rx, neden in _KABUL:
        if re.search(rx, t):
            return True, neden
    return False, f"bilinmeyen lisans ({duz_metin(kisa_ad) or duz_metin(kullanim)})"


def _yil(tarih: str) -> str:
    m = re.search(r"\b(1[5-9]\d\d|20\d\d)\b", duz_metin(tarih))
    return m.group(1) if m else ""


def atif(bilgi: dict) -> dict[str, str]:
    """episode.yaml `credits` için hazır satırlar (en: Wojak Past Files kalıbı, tr: Tarihsel Wojak kalıbı)."""
    baslik = re.sub(r"\.[a-z0-9]+$", "", bilgi["ad"].replace("_", " "), flags=re.IGNORECASE)
    yazar = bilgi.get("yazar") or "yazarı bilinmiyor"
    yil = bilgi.get("yil")
    lis = bilgi.get("lisans") or ""
    pd = bilgi.get("neden") == "kamu malı / CC0" and "cc0" not in lis.lower()
    en_lis = "public domain" if pd else (f"{lis} ({bilgi['lisans_url']})" if bilgi.get("lisans_url") else lis)
    tr_lis = "kamu malı" if pd else lis
    en = f"{baslik}, by {yazar}{', ' + yil if yil else ''}, {en_lis}, via Wikimedia Commons ({bilgi['sayfa']})"
    tr = f"{yazar} ({baslik}{', ' + yil if yil else ''}, {tr_lis}), Wikimedia Commons"
    return {"en": en, "tr": tr}


def _ozet(sayfa: dict) -> dict:
    ii = (sayfa.get("imageinfo") or [{}])[0]
    m = {k: (v or {}).get("value", "") for k, v in (ii.get("extmetadata") or {}).items()}
    kabul, neden = lisans_sinifi(m.get("LicenseShortName"), m.get("UsageTerms"))
    return {"baslik": sayfa.get("title", ""), "ad": dosya_adi(sayfa.get("title", "")),
            "genislik": ii.get("width", 0), "yukseklik": ii.get("height", 0), "url": ii.get("url", ""),
            "sayfa": ii.get("descriptionurl", ""), "kisa": ii.get("descriptionshorturl", ""),
            "lisans": duz_metin(m.get("LicenseShortName")), "lisans_url": duz_metin(m.get("LicenseUrl")),
            "yazar": duz_metin(m.get("Artist")), "kredi": duz_metin(m.get("Credit")),
            "kullanim": duz_metin(m.get("UsageTerms")), "tarih": duz_metin(m.get("DateTimeOriginal")),
            "yil": _yil(m.get("DateTimeOriginal", "")), "kabul": kabul, "neden": neden,
            "index": sayfa.get("index", 0)}


# --- Ağ komutları --------------------------------------------------------------------------------------------------

def _ii(**ek) -> dict:
    return {"prop": "imageinfo", "iiprop": "url|size|mime|extmetadata", "iiextmetadatafilter": "|".join(META), **ek}


def ara(sorgu: str, n: int = 10) -> list[dict]:
    """Dosya ad alanında tek istekle arama + lisans (generator=search)."""
    d = _api(generator="search", gsrsearch=sorgu, gsrnamespace=6, gsrlimit=n, **_ii())
    return sorted((_ozet(p) for p in d.get("query", {}).get("pages", []) if p.get("imageinfo")),
                  key=lambda x: x["index"])


def bilgi(baslik: str) -> dict:
    t = "File:" + dosya_adi(baslik).replace("_", " ")
    sayfalar = _api(titles=t, **_ii()).get("query", {}).get("pages", [])
    if not sayfalar or sayfalar[0].get("missing") or not sayfalar[0].get("imageinfo"):
        raise CommonsHatasi(f"dosya bulunamadı: {t}")
    return _ozet(sayfalar[0])


def ham_lisans(baslik: str) -> list[str]:
    """Dosya sayfasının ham metnindeki lisans şablonları ({{PD-Art|...}}, {{cc-by-sa-4.0}}); 28.10'da 429 vermedi."""
    t = "File:" + dosya_adi(baslik).replace("_", " ")
    metin = _get(INDEX, {"title": t, "action": "raw"}).text
    return sorted(set(re.findall(r"\{\{\s*((?:PD|CC|Cc|cc|pd|Self|self|GFDL|FAL|Attribution|Licen)[^{}\n]{0,80})\}\}",
                                 metin)))


def _gorsel_mi(icerik: bytes) -> bool:
    return icerik[:3] == b"\xff\xd8\xff" or icerik[:8] == b"\x89PNG\r\n\x1a\n" or icerik[:4] in (b"GIF8", b"RIFF") \
        or icerik[:4] in (b"II*\x00", b"MM\x00*")


def indir(baslik: str, hedef: Path, genislik: int = 1280, b: dict | None = None) -> tuple[Path, str]:
    """Standart küçük resim; inmezse md5 özgün yol (gerekirse standart genişliğe küçültülür). (yol, kullanılan url)."""
    b = b or bilgi(baslik)
    w = genislik_sec(genislik, b["genislik"] or 10 ** 6)
    adaylar = ([thumb_url(baslik, w)] if w else []) + [md5_url(baslik)]
    hata = ""
    for url in adaylar:
        try:
            r = _get(url, timeout=180)
        except CommonsHatasi as e:
            hata = str(e)
            print(f"  ! {e}; sıradaki yol deneniyor", file=sys.stderr)
            continue
        if not _gorsel_mi(r.content):
            hata = f"görsel değil ({r.headers.get('Content-Type')}): {url}"
            continue
        hedef = Path(hedef)
        hedef.parent.mkdir(parents=True, exist_ok=True)
        _kaydet(r.content, hedef, w if url == adaylar[-1] else None)
        return hedef, url
    raise CommonsHatasi(f"indirilemedi: {hata}")


def _kaydet(icerik: bytes, hedef: Path, genislik: int | None) -> None:
    """Biçim hedefin uzantısıyla aynıysa ve küçültme gerekmiyorsa baytlar olduğu gibi yazılır (yeniden sıkıştırma yok)."""
    import io
    from PIL import Image
    im = Image.open(io.BytesIO(icerik))
    bicim = {"jpg": "JPEG", "jpeg": "JPEG", "png": "PNG", "webp": "WEBP"}.get(hedef.suffix.lower().lstrip("."), "JPEG")
    if im.format == bicim and not (genislik and im.width > genislik):
        hedef.write_bytes(icerik)
        return
    if genislik and im.width > genislik:
        im = im.resize((genislik, round(im.height * genislik / im.width)), Image.LANCZOS)
    if bicim == "JPEG" and im.mode not in ("RGB", "L"):
        im = im.convert("RGB")
    im.save(hedef, bicim, **({"quality": 95} if bicim == "JPEG" else {}))


def ia_ara(sorgu: str, n: int = 10) -> list[dict]:
    """Internet Archive advancedsearch (kitap, gazete taraması; kamu malı son kare kaynağı)."""
    params = [("q", sorgu), ("rows", n), ("output", "json")] + \
        [("fl[]", f) for f in ("identifier", "title", "year", "licenseurl", "rights", "mediatype")]
    docs = _get(IA_ARA, params).json().get("response", {}).get("docs", [])
    return [{"id": d.get("identifier", ""), "baslik": d.get("title", ""), "yil": str(d.get("year", "") or ""),
             "lisans": d.get("licenseurl") or (d.get("rights") if isinstance(d.get("rights"), str)
                                               else "; ".join(d.get("rights") or [])) or "-",
             "tur": d.get("mediatype", "")} for d in docs]


# --- Komut satırı -------------------------------------------------------------------------------------------------

def _satir(x: dict) -> str:
    isaret = "KABUL" if x["kabul"] else "red  "
    return (f"{isaret} {x['genislik']:>5}x{x['yukseklik']:<5} {x['lisans'][:16]:<16} {x['baslik'][5:][:60]:<60} "
            f"{x['kisa'] or x['sayfa']}")


def main(argv=None) -> None:
    global ARALIK
    try:
        sys.stdout.reconfigure(errors="replace")
    except (AttributeError, ValueError):
        pass
    ap = argparse.ArgumentParser(prog="commons", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--aralik", type=float, default=ARALIK, help=f"istekler arası en az sn (varsayılan {ARALIK})")
    sp = ap.add_subparsers(dest="komut", required=True)
    p = sp.add_parser("ara", help="dosya ara (tek satır: kabul, boyut, lisans, ad, kısa url)")
    p.add_argument("sorgu")
    p.add_argument("-n", type=int, default=10)
    p = sp.add_parser("bilgi", help="lisans, yazar ve credits'e hazır atıf satırı")
    p.add_argument("dosya")
    p.add_argument("--ham", action="store_true", help="ham sayfadaki lisans şablonlarını da getir (1 istek daha)")
    p = sp.add_parser("indir", help="standart genişlikte indir; olmazsa md5 özgün yol")
    p.add_argument("dosya")
    p.add_argument("hedef")
    p.add_argument("--genislik", type=int, choices=STANDART, default=1280)
    p.add_argument("--zorla", action="store_true", help="lisans kabul değilse de indir (telifli/ klasörü için)")
    p = sp.add_parser("ia-ara", help="Internet Archive araması (kimlik, yıl, lisans/haklar, başlık)")
    p.add_argument("sorgu")
    p.add_argument("-n", type=int, default=10)
    a = ap.parse_args(argv)
    ARALIK = a.aralik
    try:
        if a.komut == "ara":
            for x in ara(a.sorgu, a.n):
                print(_satir(x))
        elif a.komut == "bilgi":
            b = bilgi(a.dosya)
            print(_satir(b))
            print(f"lisans : {b['lisans']} {b['lisans_url']}  -> {'KABUL' if b['kabul'] else 'RED'} ({b['neden']})")
            print(f"yazar  : {b['yazar'] or '-'} | kredi: {b['kredi'][:100] or '-'} | tarih: {b['tarih'][:40] or '-'}")
            if a.ham:
                print(f"şablon : {', '.join(ham_lisans(a.dosya)) or '-'}")
            for k, v in atif(b).items():
                print(f"atıf {k}: {v}")
        elif a.komut == "indir":
            b = bilgi(a.dosya)
            if not b["kabul"] and not a.zorla:
                sys.exit(f"lisans kabul değil ({b['neden']}): {b['lisans'] or '-'}. Bilerek indirmek için --zorla")
            yol, url = indir(a.dosya, Path(a.hedef), a.genislik, b)
            print(f"-> {yol}  ({url.split('/')[-1][:60]}; {b['lisans']}, {'KABUL' if b['kabul'] else 'RED'})")
            print(f"atıf: {atif(b)['en']}")
        elif a.komut == "ia-ara":
            for x in ia_ara(a.sorgu, a.n):
                print(f"{x['id'][:40]:<40} {x['yil']:<5} {x['lisans'][:40]:<40} {x['baslik'][:60]}  "
                      f"https://archive.org/details/{x['id']}")
    except CommonsHatasi as e:
        sys.exit(f"HATA: {e}")


if __name__ == "__main__":
    main()
