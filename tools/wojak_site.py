#!/usr/bin/env python3
"""Ek wojak kaynakları: wojaksparadise.com (wp, ~110 görsel) ve wojakland.com (wl, ~5.900 görsel).

tools/wojak_lib.py (HF clayshoaf/Wojaks) ile aynı kullanım. Başlıklar/etiketler İngilizce.

    python tools/wojak_site.py index                       # data/wojak_site_index.csv (bir kez, ~4 dk)
    python tools/wojak_site.py search crying wojak         # başlık/etiket/kategoride geçen kelimeler (VE)
    python tools/wojak_site.py search "soldier|army" turkish --site wl
    python tools/wojak_site.py sheet doomer girl           # numaralı önizleme sayfası (out/*.jpg)
    python tools/wojak_site.py get wl:feels_wojak.png --name sakin_wojak --yon on
    python tools/wojak_site.py get https://wojaksparadise.com/image/dr-zoomer.D1l --name doktor

`get` orijinali indirir (.cache/wojak_site), RGBA'ya çevirir, düz (beyaz vb.) zeminliyse
tools/cutout.py flood_cutout ile keser, şeffaf kenarı kırpar, en fazla 1400 px yüksekliğe indirir ve
assets/characters/<isim>.png (ya da --out-dir) olarak kaydeder. Kaynak adresi PNG'nin içine yazılır.

Nezaket: siteye en fazla ~1 istek/sn, tanıtıcı User-Agent, indirilenler önbellekte.
Hassas (siyasi figür, aşırılıkçı, cinsel, etnik karikatür) görseller aramada varsayılan olarak gizli
(--hepsi ile görünür). Lisans: wp'de yükleyen hak sahibi, yeniden kullanım izni verilmiyor; wl'de şart
sayfası yok (topluluk memeleri). Sadece kanal videolarında karakter olarak kullan.
"""

from __future__ import annotations

import argparse
import csv
import html
import io
import json
import re
import sys
import time
import urllib.parse
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont
from PIL.PngImagePlugin import PngInfo

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "data" / "wojak_site_index.csv"
CHARS = ROOT / "assets" / "characters"
CACHE = ROOT / ".cache" / "wojak_site"
DIMS = CACHE / "dims.json"
FIELDS = ["id", "site", "title", "tags", "date", "width", "height", "ext", "url", "preview", "page", "by"]

WP = "https://wojaksparadise.com"
WL = "https://wojakland.com"
WL_IMG = WL + "/wp-content/grand-media/image/"
MIN_GAP = 1.1  # aynı siteye iki istek arası en az bu kadar saniye

http = requests.Session()
http.headers.update({
    "User-Agent": "Mozilla/5.0 (compatible; tarihselwojak-asset-fetcher/0.1; "
                  "personal meme-video pipeline; max 1 req/s)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.8",
})
# wojaksparadise'ın 18+ onay kapısı: /?agree-consent ziyaretinin koyduğu çerezin aynısı
http.cookies.set("AGREE_CONSENT", "1", domain="wojaksparadise.com", path="/")
_last: dict[str, float] = {}

# Elle bakılıp elenenler (2026-10-09 taraması) + başlık kalıpları
SENSITIVE_IDS = {f"wp:{x}" for x in (
    "vTI 73j tGS aS3 ifp ium iht arV 3lQ DLd1 DL9K D8L6 GH2 D94k 8E1 bjp D9MD DGi3 D35S UOH Dijl "
    "Di2P hMz NVv cns OAd").split()} | {"wl:erdogan_turkey_wojak.png", "wl:greek_and_turk_civil_war_wojaks.png"}
SENSITIVE_RE = re.compile(
    r"\b(chud\w*|happy merchant|amerimutt|mutt|nazi\w*|hitler|austrian painter|swastika|reich|waffen|ss|kkk|"
    r"isis|jihad\w*|bomber|terror\w*|osama|bin laden|taliban|al qaeda|hamas|hezbollah|pkk|gulen|falange|"
    r"reconquista|maga|erdogan|putin|trump|biden|obama|kamala|zelensky|netanyahu|macron|orban|xi jinping|"
    r"kim jong\w*|mosley|feelsley|milei|lula|starmer|epstein|naked|nude|nsfw|porn\w*|fap\w*|hentai|sex\w*)\b")


# ---------------------------------------------------------------- HTTP

class Blocked(RuntimeError):
    """Site isteği reddetti (403/406)."""


def _req(method: str, url: str, **kw) -> requests.Response:
    host = urllib.parse.urlsplit(url).netloc
    timeout = kw.pop("timeout", 90)
    for attempt in range(3):
        wait = MIN_GAP - (time.time() - _last.get(host, 0.0))
        if wait > 0:
            time.sleep(wait)
        try:
            r = http.request(method, url, timeout=timeout, **kw)
        except requests.RequestException as e:
            _last[host] = time.time()
            if attempt == 2:
                raise
            print(f"   ağ hatası ({e.__class__.__name__}), tekrar deneniyor...", file=sys.stderr)
            time.sleep(3 * (attempt + 1))
            continue
        _last[host] = time.time()
        if r.status_code in (429, 503) and attempt < 2:
            time.sleep(10 * (attempt + 1))
            continue
        if r.status_code in (403, 406):
            raise Blocked(f"{host} isteği reddetti (HTTP {r.status_code}): {url}\n"
                          "Site bot korumasını açmış olabilir; bir süre sonra tekrar dene.")
        return r
    return r


def get_text(url: str) -> str:
    r = _req("GET", url)
    r.raise_for_status()
    return r.text


def get_bytes(url: str) -> bytes | None:
    r = _req("GET", url, timeout=180)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return r.content


def _cache_file(sub: str, name: str) -> Path:
    p = CACHE / sub / re.sub(r"[^A-Za-z0-9._-]+", "_", name)[-180:]
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def _key(r: dict, url: str) -> str:
    base = urllib.parse.unquote(url.rsplit("/", 1)[-1])
    return r["id"] if r["id"].endswith(base) else f"{r['id']}_{base}"


def cached_bytes(sub: str, name: str, urls: list[str]) -> tuple[bytes, str]:
    """İlk çalışan adresten indirir; sonraki çağrılarda önbellekten verir."""
    p = _cache_file(sub, name)
    src = p.with_name(p.name + ".src")
    if p.exists() and p.stat().st_size:
        return p.read_bytes(), (src.read_text().strip() if src.exists() else "")
    for u in [u for u in urls if u]:
        data = get_bytes(u)
        if data:
            p.write_bytes(data)
            src.write_text(u)
            return data, u
    raise FileNotFoundError(" | ".join(u for u in urls if u))


# ---------------------------------------------------------------- index

def _attr(tag: str, name: str) -> str | None:
    m = re.search(name + r'="([^"]*)"', tag) or re.search(name + r"='([^']*)'", tag)
    return html.unescape(m.group(1)) if m else None


def wp_parse_list(page: str) -> list[dict]:
    out = []
    for tag in re.findall(r'<div class="list-item [^>]*>', page):
        obj = _attr(tag, "data-object")
        if not obj or _attr(tag, "data-flag") != "safe" or _attr(tag, "data-type") != "image":
            continue
        try:
            out.append(json.loads(urllib.parse.unquote(obj)))
        except ValueError:
            pass
    return out


def wp_details(viewer: str, id_: str, refresh: bool) -> dict:
    p = _cache_file("wp_pages", id_ + ".html")
    if refresh or not p.exists():
        p.write_text(get_text(viewer), encoding="utf-8")
    h = p.read_text(encoding="utf-8")
    tags = {urllib.parse.unquote(t).replace("+", " ") for t in re.findall(r'href="(?:https://wojaksparadise\.com)?/tag/([^"/?#]+)', h)}
    album = re.search(r'href="https://wojaksparadise\.com/album/([^"/]+)\.[A-Za-z0-9]+"', h)  # .../album/Full-Body-Wojak.ch
    return {"tags": sorted(html.unescape(t) for t in tags),
            "album": urllib.parse.unquote(album.group(1)).replace("-", " ") if album else ""}


def index_wp(details: bool, refresh: bool) -> list[dict]:
    home = get_text(WP + "/")
    tok = re.search(r'auth_token\s*=\s*"([0-9a-f]+)"', home)
    if not tok:
        sys.exit("wojaksparadise: auth_token bulunamadı (site yapısı değişmiş olabilir)")
    items, seen, seek, page = [], set(), None, 1
    while True:
        data = {"action": "list", "list": "images", "sort": "date_desc", "page": str(page),
                "auth_token": tok.group(1), "params_hidden[route]": "index",
                "params_hidden[hide_empty]": "1", "params_hidden[hide_banned]": "1"}
        if seek:
            data["seek"] = seek
        r = _req("POST", WP + "/json", data=data,
                 headers={"X-Requested-With": "XMLHttpRequest", "Referer": WP + "/"})
        r.raise_for_status()
        j = r.json()
        new = [d for d in wp_parse_list(j.get("html", "")) if d["id_encoded"] not in seen]
        seen.update(d["id_encoded"] for d in new)
        items += new
        print(f"  wp sayfa {page}: +{len(new)} (toplam {len(items)})", flush=True)
        if not new or not j.get("seekEnd"):
            break
        seek, page = j["seekEnd"], page + 1
    rows = []
    for i, d in enumerate(items):
        url = d.get("url") or d["image"]["url"]
        det = {"tags": [], "album": ""}
        if details:
            det = wp_details(d["url_viewer"], d["id_encoded"], refresh)
            if (i + 1) % 20 == 0:
                print(f"  wp ayrıntı {i + 1}/{len(items)}", flush=True)
        m = re.search(r"/images/(\d{4})/(\d{2})/(\d{2})/", url)
        rows.append({
            "id": "wp:" + d["id_encoded"], "site": "wp", "title": html.unescape(d.get("title", "")),
            "tags": "|".join(det["tags"] + ([f"album {det['album']}"] if det["album"] else [])),
            "date": "-".join(m.groups()) if m else "", "width": d.get("width", ""), "height": d.get("height", ""),
            "ext": d.get("extension", ""), "url": url,
            "preview": (d.get("medium") or {}).get("url") or (d.get("thumb") or {}).get("url") or url,
            "page": d.get("url_viewer", ""), "by": (d.get("user") or {}).get("username", ""),
        })
    return rows


WL_ITEM = re.compile(
    r'<div class="gmPhantom_ThumbContainer[^"]*" data-id="(\d+)"[^>]*?data-ext="(\w+)"[^>]*>\s*'
    r'<a href="([^"]+)"[^>]*>\s*<img[^>]*?alt="([^"]*)"', re.S)


def wl_slug(file: str) -> str:
    return file.lower().replace(".", "-")


def index_wl() -> list[dict]:
    pages = json.loads(get_text(WL + "/wp-json/wp/v2/pages?per_page=100&_fields=slug,link"))
    items: dict[str, dict] = {}
    for p in pages:
        if p["slug"] in ("privacy-policy", "categories"):
            continue
        todo, seen = [p["link"]], set()
        while todo:
            u = todo.pop(0)
            seen.add(u)
            b = get_text(u)
            found = WL_ITEM.findall(b)
            for gid, ext, web, alt in found:
                file = urllib.parse.unquote(web.rsplit("/", 1)[1])
                r = items.setdefault(file, {"title": html.unescape(alt).strip(), "ext": ext, "cats": set()})
                r["cats"].add(p["slug"])
            for m in re.findall(r'<a href="(https://wojakland\.com/[^"]+/\d+/)" class="post-page-numbers"', b):
                if m not in seen and m not in todo:
                    todo.append(m)
            print(f"  wl {u}: {len(found)} (toplam {len(items)})", flush=True)
    # Site haritaları: yükleme tarihleri + hiçbir kategoride olmayan görseller
    idx = get_text(WL + "/sitemap_index.xml")
    dates: dict[str, str] = {}
    for sm in re.findall(r"<loc>(https://wojakland\.com/gmedia-sitemap\d*\.xml)</loc>", idx):
        x = get_text(sm)
        for loc, mod in re.findall(r"<loc>https://wojakland\.com/gmedia/([^<]+?)/</loc>\s*<lastmod>([^<]+)</lastmod>", x):
            dates[loc] = mod[:10]
        print(f"  wl {sm}: {len(dates)} tarih", flush=True)
    rows, known = [], set()
    for file, r in items.items():
        s = wl_slug(file)
        known.add(s)
        rows.append({
            "id": "wl:" + file, "site": "wl", "title": r["title"], "tags": "|".join(sorted(r["cats"])),
            "date": dates.get(s, ""), "width": "", "height": "", "ext": r["ext"],
            "url": WL_IMG + "original/" + urllib.parse.quote(file), "preview": WL_IMG + "thumb/" + urllib.parse.quote(file),
            "page": f"{WL}/gmedia/{s}/", "by": "",
        })
    for s, d in dates.items():
        m = re.fullmatch(r"(.+)-(png|webp|jpe?g|gif)", s)
        if s in known or not m:
            continue
        # Kategorisiz görsel: dosya adının büyük/küçük harfi bilinmiyor; get sırasında sayfadan çözülür
        rows.append({
            "id": f"wl:{m.group(1)}.{m.group(2)}", "site": "wl",
            "title": re.sub(r"[_-]+", " ", m.group(1)).strip().title(), "tags": "kategorisiz", "date": d,
            "width": "", "height": "", "ext": m.group(2), "url": "", "preview": "", "page": f"{WL}/gmedia/{s}/", "by": "",
        })
    return rows


def cmd_index(a) -> None:
    old: dict[str, list] = {}
    for r in load_index(quiet=True):
        old.setdefault(r["site"], []).append(r)
    rows = []
    for site in ("wp", "wl"):
        if a.site and a.site != site:
            rows += old.get(site, [])
            continue
        print(f"{site} taranıyor...", flush=True)
        rows += index_wp(not a.hizli, a.yenile) if site == "wp" else index_wl()
    INDEX.parent.mkdir(parents=True, exist_ok=True)
    with INDEX.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    n = {s: sum(r["site"] == s for r in rows) for s in ("wp", "wl")}
    print(f"-> {INDEX.relative_to(ROOT)} (wp {n['wp']}, wl {n['wl']})")


def load_index(quiet: bool = False) -> list[dict]:
    if not INDEX.exists():
        if quiet:
            return []
        sys.exit("Önce: python tools/wojak_site.py index")
    with INDEX.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ---------------------------------------------------------------- search

def _dims() -> dict:
    try:
        return json.loads(DIMS.read_text())
    except (OSError, ValueError):
        return {}


def _save_dims(d: dict) -> None:
    DIMS.parent.mkdir(parents=True, exist_ok=True)
    DIMS.write_text(json.dumps(d, indent=0, sort_keys=True))


def size_of(r: dict, dims: dict) -> tuple[int, int] | None:
    if r["width"] and r["height"]:
        return int(r["width"]), int(r["height"])
    v = dims.get(r["id"])
    return (v[0], v[1]) if v else None


def is_sensitive(r: dict) -> bool:
    if r["id"] in SENSITIVE_IDS:
        return True
    hay = re.sub(r"[_\-.]+", " ", f"{r['title']} {r['tags']} {r['id']}").lower()
    return bool(SENSITIVE_RE.search(hay))


def search(terms: list[str], site: str | None = None, limit: int = 40,
           show_all: bool = False) -> tuple[list[dict], int]:
    rows = load_index()
    groups = [[t for t in term.lower().split("|") if t] for term in terms]
    res, hidden = [], 0
    for r in rows:
        if site and r["site"] != site:
            continue
        title = re.sub(r"[_\-]+", " ", r["title"]).lower()
        hay = re.sub(r"[_\-/|.]+", " ", f"{title} {r['tags']} {r['id']} {r['url'].rsplit('/', 1)[-1]}").lower()
        flat = hay.replace(" ", "")  # "tradwife" = "trad wife"
        if not all(any(t in hay or t.replace(" ", "") in flat for t in g) for g in groups):
            continue
        if not show_all and is_sensitive(r):
            hidden += 1
            continue
        # başlıkta tam kelime olarak geçen terimler önce; sonra kısa (= daha genel) başlık
        score = sum(max((2 if re.search(rf"\b{re.escape(t)}\b", title) else 1 if t in title else 0) for t in g)
                    for g in groups)
        res.append((-score, len(r["title"]), r))
    res.sort(key=lambda x: x[:2])
    return [r for *_, r in res[:limit]], hidden


def print_rows(res: list[dict], show_flag: bool) -> None:
    dims = _dims()
    for i, r in enumerate(res):
        sz = size_of(r, dims)
        sz = f"{sz[0]}x{sz[1]}" if sz else "?"
        flag = " [hassas]" if show_flag and is_sensitive(r) else ""
        print(f"{i:3d}  {r['id']:<44} {sz:>9}  {r['date']:<10}  {r['title'][:60]}{flag}  {r['url'] or r['page']}")


def cmd_search(a) -> None:
    res, hidden = search(a.terms, a.site, a.limit, a.hepsi)
    print_rows(res, a.hepsi)
    if hidden:
        print(f"({hidden} hassas sonuç gizlendi; görmek için --hepsi)")
    if not res:
        print("sonuç yok")


# ---------------------------------------------------------------- download / process

def measure_remote(url: str) -> tuple[int, int] | None:
    """Orijinali indirmeden ölçü: ilk 64 KB yeter (PNG/WebP/JPEG başlığı)."""
    try:
        r = _req("GET", url, headers={"Range": "bytes=0-65535"}, timeout=60)
        if r.status_code not in (200, 206):
            return None
        b = r.content
        if b[:4] == b"RIFF" and b[8:12] == b"WEBP":  # Pillow WebP'yi yarım veriyle açamıyor
            if b[12:16] == b"VP8X":
                return 1 + int.from_bytes(b[24:27], "little"), 1 + int.from_bytes(b[27:30], "little")
            if b[12:16] == b"VP8L":
                bits = int.from_bytes(b[21:25], "little")
                return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
            if b[12:16] == b"VP8 ":
                return int.from_bytes(b[26:28], "little") & 0x3FFF, int.from_bytes(b[28:30], "little") & 0x3FFF
        return Image.open(io.BytesIO(b)).size
    except Exception:
        return None


def wl_resolve(r: dict) -> dict:
    """Kategorisiz wl görselinin gerçek dosya adresini öğe sayfasının og:image'inden bulur."""
    if r.get("url"):
        return r
    h = get_text(r["page"])
    m = re.search(r'<meta property="og:image" content="([^"]+)"', h)
    if not m:
        sys.exit(f"görsel adresi bulunamadı: {r['page']}")
    web = html.unescape(m.group(1))
    file = urllib.parse.unquote(web.rsplit("/", 1)[1])
    t = re.search(r'<meta property="og:title" content="([^"]+)"', h)
    return {**r, "url": WL_IMG + "original/" + urllib.parse.quote(file), "preview": WL_IMG + "thumb/" + urllib.parse.quote(file),
            "title": html.unescape(t.group(1)).split(" - ")[0].strip() if t else r["title"]}


def fallbacks(r: dict) -> list[str]:
    if r["site"] == "wl":
        return [r["url"], r["url"].replace("/image/original/", "/image/")]
    return [r["url"], r["preview"]]


def resolve(ref: str) -> dict:
    rows = load_index()
    by_id = {r["id"]: r for r in rows}
    ref = ref.strip()
    if ref in by_id:
        return by_id[ref]
    for pre in ("wp:", "wl:"):
        if pre + ref in by_id:
            return by_id[pre + ref]
    if not ref.startswith("http"):
        low = {k.lower(): v for k, v in by_id.items()}
        for k in (ref.lower(), "wl:" + ref.lower()):
            if k in low:
                return low[k]
        sys.exit(f"bulunamadı: {ref}  (önce: python tools/wojak_site.py search ...)")
    u = urllib.parse.urlsplit(ref)
    path = urllib.parse.unquote(u.path)
    if u.netloc.endswith("wojaksparadise.com"):
        m = re.match(r"/image/(?:.*\.)?([A-Za-z0-9]+)/?$", path)
        if m and "wp:" + m.group(1) in by_id:
            return by_id["wp:" + m.group(1)]
        for r in rows:
            if r["site"] == "wp" and (r["url"] == ref or r["preview"] == ref):
                return r
        if m:  # dizinde yok (yeni yüklenmiş): sayfadan çöz
            h = get_text(ref)
            og = re.search(r'<meta property="og:image" content="([^"]+)"', h)
            t = re.search(r'<meta property="og:title" content="([^"]+)"', h)
            if og:
                url = html.unescape(og.group(1))
                return {"id": "wp:" + m.group(1), "site": "wp", "title": html.unescape(t.group(1)) if t else m.group(1),
                        "url": url, "preview": url, "page": ref, "by": "", "width": "", "height": "", "tags": "", "date": ""}
        if path.startswith("/images/"):
            return {"id": "wp:" + Path(path).stem, "site": "wp", "title": Path(path).stem, "url": ref, "preview": ref,
                    "page": ref, "by": "", "width": "", "height": "", "tags": "", "date": ""}
    if u.netloc.endswith("wojakland.com"):
        m = re.match(r"/wp-content/grand-media/image/(?:original/|thumb/)?([^/]+)$", path)
        if m:
            k = "wl:" + m.group(1)
            if k in by_id:
                return by_id[k]
            return {"id": k, "site": "wl", "title": Path(m.group(1)).stem, "url": WL_IMG + "original/" + urllib.parse.quote(m.group(1)),
                    "preview": "", "page": ref, "by": "", "width": "", "height": "", "tags": "", "date": ""}
        m = re.match(r"/gmedia/([^/]+)/?$", path)
        if m:
            for r in rows:
                if r["page"].rstrip("/").endswith("/gmedia/" + m.group(1)):
                    return r
            return {"id": "wl:" + m.group(1), "site": "wl", "title": m.group(1), "url": "", "preview": "",
                    "page": f"{WL}/gmedia/{m.group(1)}/", "by": "", "width": "", "height": "", "tags": "", "date": ""}
    sys.exit(f"desteklenmeyen adres: {ref} (sadece wojaksparadise.com / wojakland.com)")


def alpha_ratio(im: Image.Image) -> float:
    return sum(im.getchannel("A").histogram()[:16]) / (im.width * im.height)


def border_flat(im: Image.Image, tol: int = 38) -> tuple[bool, tuple]:
    """Kenar piksellerinin çoğu tek renkse (düz zemin) True."""
    small = im.convert("RGB")
    small.thumbnail((600, 600))
    w, h = small.size
    px = small.load()
    sides = [[px[x, 0] for x in range(w)], [px[x, h - 1] for x in range(w)],
             [px[0, y] for y in range(h)], [px[w - 1, y] for y in range(h)]]
    border = [c for side in sides for c in side]
    med = tuple(sorted(c[i] for c in border)[len(border) // 2] for i in range(3))

    def share(px_list):
        return sum(max(abs(c[i] - med[i]) for i in range(3)) <= tol for c in px_list) / len(px_list)
    # büst/boy görsellerinde gövde alt kenara değer: 3 kenar zemin rengindeyse yeter
    return share(border) >= 0.85 or sorted(map(share, sides))[1] >= 0.9, med


def seal_edges(im: Image.Image, bg: tuple) -> Image.Image | None:
    """Kenara değen gövdeyi kapat: konturun bir kenara değdiği ilk ve son nokta arası koyu çizgiyle
    mühürlenir (beyaz zeminde boynu alt kenara değen beyaz yüzlü wojak'ta flood fill yüzün içine sızmasın).
    Görsel 1 px zemin rengiyle çerçevelenir ki cutout'un zemin rengi tahmini bozulmasın; köşelere değen
    çizgiler (ekran görüntüsü kenarı vb.) sayılmaz. Mühürlenecek kenar yoksa None."""
    import numpy as np
    a = np.asarray(im.convert("RGB"))
    dark = a.max(axis=2) < 110
    h, w = dark.shape
    out = np.empty((h + 2, w + 2, 3), np.uint8)
    out[:] = bg
    out[1:-1, 1:-1] = a
    changed = False
    for hits, n, sl in ((dark[:2].any(0), w, lambda i, j: (slice(1, 3), slice(i + 1, j + 1))),
                        (dark[h - 2:].any(0), w, lambda i, j: (slice(h - 1, h + 1), slice(i + 1, j + 1))),
                        (dark[:, :2].any(1), h, lambda i, j: (slice(i + 1, j + 1), slice(1, 3))),
                        (dark[:, w - 2:].any(1), h, lambda i, j: (slice(i + 1, j + 1), slice(w - 1, w + 1)))):
        m = max(4, n // 50)
        idx = np.flatnonzero(hits[m:n - m]) + m
        if len(idx) >= 2:
            out[sl(int(idx[0]), int(idx[-1]) + 1)] = 0
            changed = True
    return Image.fromarray(out) if changed else None


def bbox_fill(im: Image.Image) -> float:
    """Opak piksellerin kendi sınır kutusundaki payı. Wojak figürü ~0,55+; yüzü silinmiş çizgi ~0,1."""
    a = im.getchannel("A").point(lambda v: 255 if v > 128 else 0)
    bb = a.getbbox()
    if not bb:
        return 0.0
    c = a.crop(bb)
    return c.histogram()[255] / (c.width * c.height)


def smart_cutout(im: Image.Image, tol: int, bg: tuple) -> tuple[Image.Image | None, str]:
    """cutout.flood_cutout; kontur kenara değiyorsa bir de kenarları mühürlü dener. Sonuç yalnız çizgiye
    inmişse (açık konturdan yüzün içine sızmış) kesimi reddeder: (None, sebep)."""
    sys.path.insert(0, str(ROOT / "tools"))
    from cutout import flood_cutout
    note = ""
    d_white = 255 - min(bg)
    if 0 < d_white < 2 * tol and min(bg) > 150:  # açık gri zemin: beyaz wojak teni zeminle karışmasın
        tol, note = max(6, d_white // 2), f"; beyaz tenden ayırmak için tol {max(6, d_white // 2)}"
    work = im
    if max(work.size) > 1800:  # saf Python flood fill; büyük görselde önce küçült
        work = work.copy()
        work.thumbnail((1800, 1800), Image.LANCZOS)
    best = flood_cutout(work, tol)
    sealed_in = seal_edges(work, bg)
    if sealed_in is not None:
        sealed = work.copy()
        sealed.putalpha(flood_cutout(sealed_in, tol).getchannel("A").crop((1, 1, work.width + 1, work.height + 1)))
        if alpha_ratio(best) - alpha_ratio(sealed) > 0.08 or (bbox_fill(best) < 0.3 <= bbox_fill(sealed)):
            best, note = sealed, note + "; kenara değen gövde korundu"
    if bbox_fill(best) < 0.3:
        return None, f"kesim yüzün/gövdenin içine sızdı (kalan dolu alan %{bbox_fill(best) * 100:.0f})"
    return best, note


def cmd_get(a) -> None:
    r = resolve(a.id)
    if r["site"] == "wl":
        r = wl_resolve(r)
    data, src = cached_bytes("orig", _key(r, r["url"]), fallbacks(r))
    im = Image.open(io.BytesIO(data))
    frames = getattr(im, "n_frames", 1)
    if frames > 1:
        im.seek(0)
        print(f"not: hareketli görsel ({frames} kare); ilk kare alındı")
    im = im.convert("RGBA")
    w0, h0 = im.size
    dims = _dims()
    if r["site"] == "wl" and src == r["url"] and dims.get(r["id"]) != [w0, h0]:
        dims[r["id"]] = [w0, h0]
        _save_dims(dims)
    ratio = alpha_ratio(im)
    cut = ""
    if ratio < 0.03 and not a.no_cutout:
        flat, bg = border_flat(im, a.tol)
        if flat:
            out, how = smart_cutout(im, a.tol, bg)
            if out is not None and 0.03 <= alpha_ratio(out) <= 0.97:
                im, cut = out, f"düz zemin {bg} kesildi (cutout.py flood_cutout{how})"
            else:
                print(f"UYARI: otomatik kesim yapılmadı: {how or 'sonuç boş/tam dolu'}. Görsel zeminiyle "
                      f"kaydedildi. Elle: python tools/cutout.py {_cache_file('orig', _key(r, r['url']))} --rembg")
        else:
            print("UYARI: zemin düz değil (fotoğraf/sahne). Elle: "
                  f"python tools/cutout.py {_cache_file('orig', _key(r, r['url']))} --rembg")
    bbox = im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
    if bbox:
        im = im.crop(bbox)
    if im.height > 1400:
        im = im.resize((round(im.width * 1400 / im.height), 1400), Image.LANCZOS)
    name = a.name or re.sub(r"[^A-Za-z0-9_-]+", "_", Path(r["id"].split(":", 1)[1]).stem).strip("_").lower()
    dest = Path(a.out_dir) if a.out_dir else CHARS
    dest.mkdir(parents=True, exist_ok=True)
    out = dest / f"{name}.png"
    meta = PngInfo()
    meta.add_text("Source", r["page"] or src)
    meta.add_text("Title", r["title"])
    im.save(out, optimize=True, pnginfo=meta)
    shown = out.resolve().relative_to(ROOT) if out.resolve().is_relative_to(ROOT) else out
    print(f"-> {shown}  ({im.width}x{im.height}, orijinal {w0}x{h0}, şeffaf %{alpha_ratio(im) * 100:.0f})")
    print(f"   {r['title']} | kaynak: {r['page'] or src}" + (f" | yükleyen: {r['by']}" if r.get("by") else ""))
    if cut:
        print(f"   {cut}")
    if src and src != r["url"]:
        print(f"   not: orijinal yoktu, küçük kopya kullanıldı: {src}")
    if is_sensitive(r):
        print("   UYARI: bu görsel hassas listede (siyasi/aşırılıkçı/cinsel içerik); kullanmadan önce bak")
    sys.path.insert(0, str(ROOT))
    from wojak import facing
    if a.yon:  # gözle bakılan yön kaydedilir; sahnede karakter otomatik içeri çevrilir
        print(f"   bakış yönü kaydedildi: {facing.register(out, a.yon)}")
    else:
        print(f"   bakış yönü kayıtlı değil (tahmin: {facing.guess(out)[0]}); görsele bakıp: "
              f"python -m wojak yon {shown} --yon sag|sol|on")


# ---------------------------------------------------------------- sheet

def _checker(w: int, h: int, s: int = 12) -> Image.Image:
    im = Image.new("RGB", (w, h), (236, 236, 236))
    d = ImageDraw.Draw(im)
    for y in range(0, h, s):
        for x in range((y // s) % 2 * s, w, 2 * s):
            d.rectangle((x, y, x + s - 1, y + s - 1), fill=(206, 206, 206))
    return im


def cmd_sheet(a) -> None:
    res, hidden = search(a.terms, a.site, a.limit, a.hepsi)
    if not res:
        sys.exit("sonuç yok")
    dims = _dims()
    tw, th, cols = 240, 300, 6
    rows_n = (len(res) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows_n * (th + 58)), (255, 255, 255))
    d = ImageDraw.Draw(sheet)
    try:
        f = ImageFont.truetype(str(ROOT / "assets/fonts/Poppins-Bold.ttf"), 13)
    except OSError:
        f = ImageFont.load_default()
    print(f"{len(res)} önizleme indiriliyor (önbellekte olmayanlar ~1 sn/adet)...", flush=True)
    for i, r in enumerate(res):
        x, y = (i % cols) * tw, (i // cols) * (th + 58)
        sheet.paste(_checker(tw - 6, th - 6), (x + 3, y + 3))
        try:
            if r["site"] == "wl" and not r["url"]:
                r = wl_resolve(r)
            data, _ = cached_bytes("prev", _key(r, r["preview"]), [r["preview"], r["url"]])
            im = Image.open(io.BytesIO(data))
            im.seek(0)
            im = im.convert("RGBA")
            im.thumbnail((tw - 14, th - 14))
            sheet.paste(im, (x + (tw - im.width) // 2, y + (th - im.height) // 2), im)
        except Exception as e:  # önizleme yoksa kutu boş kalır
            d.text((x + 10, y + 10), f"önizleme yok: {e.__class__.__name__}", fill="red", font=f)
        sz = size_of(r, dims)
        if sz is None and r["site"] == "wl" and r["url"] and not a.olcme:
            sz = measure_remote(r["url"])
            if sz:
                dims[r["id"]] = list(sz)
                _save_dims(dims)
        d.text((x + 4, y + th + 1), f"{i} {r['id']}"[:30], fill="black", font=f)
        d.text((x + 4, y + th + 19), r["title"][:32], fill=(60, 60, 60), font=f)
        info = f"{sz[0]}x{sz[1]}" if sz else "?"
        d.text((x + 4, y + th + 37), f"{info}  {r['date']}", fill=(150, 0, 0) if sz and max(sz) < 600 else (0, 90, 0),
               font=f)
    print_rows(res, a.hepsi)  # sayfadaki numaraların tam kimlikleri (get için)
    out = ROOT / "out" / f"sheet_site_{'_'.join(re.sub(r'[^A-Za-z0-9]+', '-', t) for t in a.terms) or 'hepsi'}.jpg"
    out.parent.mkdir(exist_ok=True)
    sheet.save(out, quality=85)
    print(f"-> {out}" + (f"  ({hidden} hassas sonuç gizli)" if hidden else ""))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("index", help="iki sitenin kataloğunu data/wojak_site_index.csv'ye yaz")
    p.add_argument("--site", choices=["wp", "wl"], help="sadece bu siteyi yeniden tara")
    p.add_argument("--hizli", action="store_true", help="wp görsel sayfalarını (etiketler) atla")
    p.add_argument("--yenile", action="store_true", help="önbellekteki wp sayfalarını da yeniden indir")
    p.set_defaults(fn=cmd_index)
    for name, fn in (("search", cmd_search), ("sheet", cmd_sheet)):
        p = sp.add_parser(name)
        p.add_argument("terms", nargs="*", help='kelimeler (hepsi geçmeli); "a|b" = a veya b')
        p.add_argument("--site", choices=["wp", "wl"])
        p.add_argument("--limit", type=int, default=40 if name == "search" else 30)
        p.add_argument("--hepsi", action="store_true", help="hassas sonuçları da göster")
        if name == "sheet":
            p.add_argument("--olcme", action="store_true", help="wl orijinal ölçüsünü sorma (daha hızlı)")
        p.set_defaults(fn=fn)
    p = sp.add_parser("get")
    p.add_argument("id", help="örn. wl:feels_wojak.png, wp:D1l ya da sayfa/dosya adresi")
    p.add_argument("--name", help="kaydedilecek isim (assets/characters/<isim>.png)")
    p.add_argument("--out-dir", help="assets/characters yerine bu klasöre kaydet (ör. episodes/<id>/chars)")
    p.add_argument("--yon", choices=["sag", "sol", "on"], help="görselin baktığı yön (gözle bakıp ver)")
    p.add_argument("--no-cutout", action="store_true", help="opak zeminde bile otomatik kesme yapma")
    p.add_argument("--tol", type=int, default=38, help="kesim için zemin renk toleransı (0-255)")
    p.set_defaults(fn=cmd_get)
    a = ap.parse_args()
    try:
        a.fn(a)
    except (Blocked, requests.RequestException, FileNotFoundError) as e:
        sys.exit(f"HATA: {e}")


if __name__ == "__main__":
    main()
