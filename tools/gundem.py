#!/usr/bin/env python3
"""Gündem tarayıcı: Türkiye haber akışlarından kanala uygun GÜNCEL olayları bulur.

    python tools/gundem.py                    # son 48 saat -> out/gundem/<tarih>.md (+ .json)
    python tools/gundem.py --saat 24 --ilk 15 # son 24 saat, ilk 15 olay
    python tools/gundem.py --sorgu "maden"    # ek Google News araması
    python tools/gundem.py --taslak 3         # son raporun 3. olayı için episodes/gundem-... taslağı

Ne yapar:
  1. data/gundem_kaynaklar.yaml'daki RSS akışlarını, Google News aramalarını ve
     Google Trends TR'yi çeker.
  2. Aynı olayı anlatan haberleri başlık benzerliğiyle kümeler.
  3. Her kümeye puan verir: kanala uygunluk (gizem, kayıp, kahramanlık, mucize...)
     + kaç farklı kaynağın yazdığı (ülke çapında büyüklük) + Google Trends'te
     yükseliyor mu + tazelik − konu dışı (siyaset, ekonomi, spor, magazin).
  4. Hassas konuları (çocuk istismarı, intihar, terör, yayın yasağı...) DİKKAT diye işaretler.

Rapor bir KARAR DESTEK listesidir: hangi olayın yapılacağına ve nasıl anlatılacağına
docs/GUNDEM.md'deki kurallar ve kontrol listesiyle insan/Claude karar verir.
"""

from __future__ import annotations

import argparse
import email.utils
import html
import json
import math
import re
import statistics
import urllib.parse
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
import yaml

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "data" / "gundem_kaynaklar.yaml"
OUT = ROOT / "out" / "gundem"
TR = timezone(timedelta(hours=3))
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/140.0 Safari/537.36"}
GNEWS_SEARCH = "https://news.google.com/rss/search?q={q}&hl=tr&gl=TR&ceid=TR:tr"

STOP = set("""ve ile bir bu şu o da de ki mi mı mu mü için gibi kadar daha en çok az son yeni
olan oldu olarak sonra önce ise ya veya ama fakat ne neden nasıl her hiç tüm büyük küçük
iki üç dört beş yıl yılı gün saat dakika haber haberi video foto galeri canlı son dakika flaş
açıklama açıkladı dedi etti eden yaptı yapan oluyor olacak var yok""".split())


# İl adları: farklı olaylarda da geçtiği için tek başına "aynı olay" kanıtı sayılmaz (zincirleme birleşme yapar)
PROVINCES = """adana adıyaman afyonkarahisar afyon ağrı amasya ankara antalya artvin aydın balıkesir bilecik bingöl
bitlis bolu burdur bursa çanakkale çankırı çorum denizli diyarbakır edirne elazığ erzincan erzurum eskişehir
gaziantep antep giresun gümüşhane hakkari hatay ısparta mersin istanbul izmir kars kastamonu kayseri kırklareli
kırşehir kocaeli konya kütahya malatya manisa kahramanmaraş maraş mardin muğla muş nevşehir niğde ordu rize sakarya
samsun siirt sinop sivas tekirdağ tokat trabzon tunceli şanlıurfa urfa uşak van yozgat zonguldak aksaray bayburt
karaman kırıkkale batman şırnak bartın ardahan ığdır yalova karabük kilis osmaniye düzce kktc kıbrıs""".split()

# Her olayda geçebilen, tek başına "aynı olay" kanıtı olmayan özel isimler
GENERIC_PROPER = {"istan", "ankar", "izmir", "türki", "türk", "son", "dakik", "flaş", "vali", "bakan", "polis",
                  "jandarma", "afad", "emniy"}


def tr_lower(s: str) -> str:
    return s.replace("I", "ı").replace("İ", "i").lower()


def strip_html(s: str) -> str:
    # Haberler.com başlıkları çift kaçışlı ("Muş&amp;apos;ta"): iki kez çöz
    s = html.unescape(html.unescape(s or ""))
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)).strip()


def tokens(s: str) -> list[str]:
    return [t for t in re.findall(r"[a-zçğıöşüâîû0-9]+", tr_lower(s)) if t not in STOP and len(t) > 2]


@dataclass
class Item:
    title: str
    link: str
    source: str
    published: datetime | None
    summary: str = ""
    via: str = ""             # hangi akıştan geldi

    @property
    def toks(self) -> set[str]:
        return set(tokens(self.title))


@dataclass
class Cluster:
    items: list[Item] = field(default_factory=list)
    score: float = 0.0
    parts: dict = field(default_factory=dict)
    categories: list[str] = field(default_factory=list)
    flags: list[str] = field(default_factory=list)
    trend: str = ""
    ban_link: str = ""

    @property
    def sources(self) -> list[str]:
        return sorted({i.source for i in self.items if i.source})

    @property
    def first_seen(self) -> datetime | None:
        ds = [i.published for i in self.items if i.published]
        return min(ds) if ds else None

    @property
    def headline(self) -> str:
        # en çok kelime ortaklığı olan (temsilî) başlık
        best = max(self.items, key=lambda i: sum(len(i.toks & j.toks) for j in self.items))
        return best.title


# --- Çekme --------------------------------------------------------------------

def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _child(el: ET.Element, name: str) -> str:
    for c in el:
        if _local(c.tag) == name:
            return (c.text or "").strip()
    return ""


def _date(s: str) -> datetime | None:
    if not s:
        return None
    try:
        d = email.utils.parsedate_to_datetime(s)
    except (TypeError, ValueError):
        try:
            d = datetime.fromisoformat(s.replace("Z", "+00:00"))
        except ValueError:
            return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def _get_xml(url: str, tries: int = 3) -> ET.Element:
    last = None
    for _ in range(tries):
        try:
            r = requests.get(url, headers=UA, timeout=25)
            r.raise_for_status()
            # TRT gibi kaynaklarda yarım UTF-8 baytı var: katı ayrıştırıcıdan önce onar
            text = r.content.decode("utf-8", "replace")
            text = re.sub(r"^<\?xml[^>]*\?>", "", text.lstrip("\ufeff").lstrip())
            return ET.fromstring(text)
        except Exception as e:  # AA gibi aralıklı bağlantı kopmaları
            last = e
    raise last


def fetch_feed(name: str, url: str, tz_fix_hours: float = 0) -> list[Item]:
    try:
        root = _get_xml(url)
    except Exception as e:  # tek bir kaynak düşerse rapor yine çıksın
        print(f"  ! {name}: {type(e).__name__}: {str(e)[:80]}")
        return []
    out = []
    for el in root.iter():
        if _local(el.tag) not in ("item", "entry"):
            continue
        title = strip_html(_child(el, "title"))
        if not title:
            continue
        link = _child(el, "link")
        if not link:
            for c in el:
                if _local(c.tag) == "link" and c.get("href"):
                    link = c.get("href")
        source = _child(el, "source") or name
        # Google News başlıkları "Başlık - Kaynak" biçiminde
        if " - " in title and (name.startswith("Google") or source != name):
            head, tail = title.rsplit(" - ", 1)
            if len(tail) < 60:
                title, source = head.strip(), tail.strip()
        pub = _date(_child(el, "pubDate") or _child(el, "date") or _child(el, "published")
                    or _child(el, "updated"))
        if pub and tz_fix_hours:
            pub += timedelta(hours=tz_fix_hours)
        out.append(Item(title, link, source, pub, strip_html(_child(el, "description"))[:400], name))
    return out


def fetch_trends(url: str) -> list[dict]:
    try:
        root = _get_xml(url)
    except Exception as e:
        print(f"  ! Trends: {e}")
        return []
    trends = []
    for it in root.iter("item"):
        t = {"term": _child(it, "title"), "traffic": _child(it, "approx_traffic"), "news": []}
        for c in it:
            if _local(c.tag) == "news_item":
                t["news"].append({"title": _child(c, "news_item_title"),
                                  "url": _child(c, "news_item_url"),
                                  "source": _child(c, "news_item_source")})
        trends.append(t)
    return trends


def collect(cfg: dict, extra_queries: list[str], hours: int) -> tuple[list[Item], list[dict]]:
    jobs = [(f["name"], f["url"], f.get("tz_fix_hours", 0)) for f in cfg.get("feeds", [])]
    searches = [s if isinstance(s, dict) else {"q": s} for s in cfg.get("searches", [])]
    searches += [{"q": q, "when": "2d"} for q in extra_queries]
    for s in searches:
        q = f"{s['q']} when:{s.get('when', '2d')}"
        jobs.append((f"Google News: {s['q']}", GNEWS_SEARCH.format(q=urllib.parse.quote(q)), 0))
    with ThreadPoolExecutor(8) as ex:
        results = list(ex.map(lambda j: fetch_feed(*j), jobs))
        trends_f = ex.submit(fetch_trends, cfg["trends"]) if cfg.get("trends") else None
    items = [i for rs in results for i in rs]
    black = {b.lower() for b in cfg.get("source_blacklist", [])}
    items = [i for i in items if i.source.lower() not in black
             and not re.search(r"[\u0400-\u04FF]", i.source + i.title)]  # Kiril alfabeli kaynaklar
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    items = [i for i in items if i.published is None or i.published >= cutoff]
    trends = trends_f.result() if trends_f else []
    # Trends haber başlıklarını da öğe olarak ekle (kaynak sayısına katkı)
    for t in trends:
        for n in t["news"]:
            if n["title"]:
                items.append(Item(n["title"], n["url"], n["source"], None, "", "Google Trends"))
    print(f"{len(jobs)} akış, {len(items)} haber (son {hours} saat), {len(trends)} trend")
    return items, trends


# --- Kümeleme ve puanlama ------------------------------------------------------

def _stem(tok: str) -> str:
    return tok[:5]  # kaba Türkçe kök: "çöktü"/"çöken", "kaybolan"/"kayboldu" eşleşsin


def cluster_items(items: list[Item], topic_words: set[str] | None = None) -> list[Cluster]:
    """Aynı olayı anlatan başlıkları kümeler (union-find).

    İki haber birleşir:
      * kelime kökü kümelerinin Jaccard benzerliği >= 0.45 VE (>= 4 ortak kök YA DA ortak bir varlık), veya
      * ortak bir varlık (ilçe/kişi adı: Maltepe, Efe... — il adları sayılmaz) + >= 3 ortak kök + Jaccard >= 0.25.
    "Cinayet şüphelisi adliyeye sevk edildi" gibi genel başlıklar varlık şartı yüzünden birleşmez.
    Aday çiftler ters indeksle bulunur; 60'tan fazla haberde geçen kökler aday üretmez.
    """
    topic = {_stem(tr_lower(w)) for w in (topic_words or set())}
    stems = [{_stem(t) for t in i.toks} for i in items]
    provinces = {_stem(p) for p in PROVINCES}
    entities = _proper_nouns(items) - GENERIC_PROPER - topic - provinces
    index: dict[str, list[int]] = {}
    for k, st in enumerate(stems):
        for t in st:
            index.setdefault(t, []).append(k)
    parent = list(range(len(items)))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    seen_pairs: set[tuple[int, int]] = set()
    for t, ks in index.items():
        if len(ks) > 60:
            continue
        for x in range(len(ks)):
            for y in range(x + 1, len(ks)):
                a, b = ks[x], ks[y]
                if (a, b) in seen_pairs or find(a) == find(b):
                    continue
                seen_pairs.add((a, b))
                sa, sb = stems[a], stems[b]
                shared = sa & sb
                jac = len(shared) / len(sa | sb)
                ent = bool(shared & entities)
                if (jac >= 0.45 and (len(shared) >= 4 or ent)) or (ent and len(shared) >= 3 and jac >= 0.25):
                    parent[find(b)] = find(a)
    groups: dict[int, Cluster] = {}
    for k, it in enumerate(items):
        groups.setdefault(find(k), Cluster()).items.append(it)
    # aynı başlığın kopyalarını (aynı kaynak) tekilleştir
    for c in groups.values():
        uniq, seen = [], set()
        for it in c.items:
            key = (tr_lower(it.title), it.source)
            if key not in seen:
                seen.add(key)
                uniq.append(it)
        c.items = uniq
    return list(groups.values())


def _proper_nouns(items: list[Item]) -> set[str]:
    """Başlıklarda neredeyse hep büyük harfle geçen kelimeler (yer/kişi adları: Maltepe, Efe...)."""
    up: dict[str, int] = {}
    tot: dict[str, int] = {}
    for i in items:
        for w in re.findall(r"[A-Za-zÇĞİÖŞÜçğıöşüâîû]+", i.title):
            if len(w) < 3:
                continue
            t = _stem(tr_lower(w))
            tot[t] = tot.get(t, 0) + 1
            up[t] = up.get(t, 0) + (1 if w[0].isupper() else 0)
    return {t for t, n in tot.items() if n >= 2 and up[t] / n >= 0.85}


def _content_text(s: str) -> str:
    """Kategori eşleşmesi için metin: cümle ortasındaki özel isimleri (Ayla Aksu KAHRAMAN gibi
    soyadları, yer adları) çıkarır. Her kelimesi büyük harfle başlayan başlıklara dokunmaz."""
    # "Ayşe Kahraman", "Ayla Aksu Kahraman": ad + soyad olarak geçen Kahraman
    s = re.sub(r"\b([A-ZÇĞİÖŞÜ][a-zçğıöşü]+) Kahraman\b", r"\1", s)
    words = re.findall(r"\S+", s)
    caps = [w for w in words if w[:1].isupper()]
    if len(words) < 4 or len(caps) / len(words) > 0.6:
        return s
    out = []
    for n, w in enumerate(words):
        prev = words[n - 1] if n else ""
        sentence_start = n == 0 or prev[-1:] in ".!?:\"'“”‘’"
        acronym = len(w) >= 2 and w.isupper()
        out.append(w if sentence_start or acronym or not w[:1].isupper() else "")
    return " ".join(out)


_RX_CACHE: dict[str, re.Pattern] = {}


def _rx(pat: str) -> re.Pattern:
    """Kelime başından eşleşen regex (ekler serbest: 'kaybol' -> kayboldu, kaybolan)."""
    r = _RX_CACHE.get(pat)
    if r is None:
        r = _RX_CACHE[pat] = re.compile(r"(?<!\w)" + pat)
    return r


def _hits(text: str, groups: dict) -> dict[str, float]:
    """Her grup (kategori) metinde en az bir kalıpla eşleşirse ağırlığını döndürür."""
    return {name: g["weight"] for name, g in groups.items() if any(_rx(p).search(text) for p in g["patterns"])}


def _item_text(i: Item) -> str:
    return tr_lower(_content_text(f"{i.title}. {i.summary}"))


def score(c: Cluster, cfg: dict, trends: list[dict]) -> None:
    per_fit, per_pen, cat_count = [], [], {}
    for i in c.items:
        t = _item_text(i)
        h = _hits(t, cfg["categories"])
        for k in h:
            cat_count[k] = cat_count.get(k, 0) + 1
        per_fit.append(sum(h.values()))
        per_pen.append(sum(_hits(t, cfg["exclude"]).values()))
    # Medyan: kümeye yanlışlıkla karışmış tek bir haber puanı şişiremesin
    fit = statistics.median(per_fit) if per_fit else 0.0
    penalty = statistics.median(per_pen) if per_pen else 0.0
    w = {k: cfg["categories"][k]["weight"] for k in cat_count}
    c.categories = sorted(cat_count, key=lambda k: -(cat_count[k] * w[k]))
    alltext = " ".join(_item_text(i) for i in c.items)
    for s in cfg.get("sensitive", []):
        if any(_rx(p).search(alltext) for p in s["patterns"]):
            c.flags.append(s["label"])
    coverage = 2.0 * math.log2(1 + len(c.sources))
    trend_bonus = 0.0
    ctoks = set(tokens(" ".join(i.title for i in c.items)))
    for t in trends:
        tt = set(tokens(t["term"]))
        if tt and len(tt & ctoks) >= max(1, math.ceil(len(tt) * 0.6)):
            traffic = int(re.sub(r"\D", "", t["traffic"] or "0") or 0)
            trend_bonus = max(trend_bonus, 3.0 + math.log10(1 + traffic) / 2)
            c.trend = f"{t['term']} ({t['traffic']})"
    fs = c.first_seen
    age_h = (datetime.now(timezone.utc) - fs).total_seconds() / 3600 if fs else 24
    recency = max(0.0, 2.0 - age_h / 24)
    c.parts = {"uygunluk": round(fit, 1), "kaynak": round(coverage, 1), "trend": round(trend_bonus, 1),
               "tazelik": round(recency, 1), "konu_dışı": round(penalty, 1)}
    c.score = round(fit + coverage + trend_bonus + recency + penalty, 1)


ANGLES = {
    "kayip": "Son masum an: kaybolan kişinin sıradan bir cümlesi (\"Birazdan dönerim anne\"). Sonuç belli değilse bilgilendirme amaçlı.",
    "olum_gizem": "Merak repliği: keşfedenin şaşkın cümlesi. Resmi açıklama gelmeden 'cinayet' deme.",
    "kurtarma_kahramanlik": "Mucize/fedakârlık repliği: kurtaranın tereddütsüz ya da kurtulanın ilk sözü. Kanıt: kurtarma anı.",
    "efsane_tarih": "Keşif repliği: bulanın şaşkın cümlesi. 'Tarihsel' seriye uygun; stok video olarak da bekletilebilir.",
    "suc": "Odak kurbanın hayatı; kurbana uydurma 'son söz' koyma. Şüpheliye karakter/korkunç yüz verme, 'katil' deme (hüküm yoksa).",
    "felaket": "Son an repliği (\"Toprak mı kayıyor?\"). Felaketi değil içindeki bir insan hikâyesini anlat.",
    "duygu": "Haberdeki gerçek son söz/son mesaj varsa replik o olsun (kısaltılmış, tırnak içinde).",
}


def _ban_check(c: Cluster) -> None:
    """Olayla ilgili son 30 günde 'yayın yasağı' haberi var mı? (docs/GUNDEM.md > Hukuk)"""
    toks = [t for t in tokens(c.headline) if len(t) > 3][:4]
    if not toks:
        return
    q = " ".join(toks[:3]) + ' "yayın yasağı" when:30d'
    items = fetch_feed("Yayın yasağı kontrolü", GNEWS_SEARCH.format(q=urllib.parse.quote(q)))
    stems = {_stem(t) for t in toks}
    for it in items:
        t = tr_lower(it.title)
        if "yayın yasağı" in t and len(stems & {_stem(x) for x in tokens(it.title)}) >= 1:
            c.flags.insert(0, "🔴 YAYIN YASAĞI OLABİLİR")
            c.ban_link = it.link
            return


# --- Rapor ---------------------------------------------------------------------

def report(clusters: list[Cluster], trends: list[dict], top: int, hours: int) -> tuple[Path, Path]:
    OUT.mkdir(parents=True, exist_ok=True)
    now = datetime.now(TR)
    stem = now.strftime("%Y-%m-%d_%H%M")
    md, js = OUT / f"{stem}.md", OUT / f"{stem}.json"
    L = [f"# Gündem taraması — {now:%d.%m.%Y %H:%M} (son {hours} saat)", "",
         "Puan = uygunluk + kaynak sayısı + Google Trends + tazelik − konu dışı. "
         "**DİKKAT** işaretli olaylarda docs/GUNDEM.md kontrol listesi zorunlu.", ""]
    if trends:
        L += ["## Google Trends TR (şu an yükselenler)", ""]
        L += [f"- {t['term']} — {t['traffic']}" + (f" · {t['news'][0]['title']}" if t["news"] else "")
              for t in trends]
        L.append("")
    L += ["## Aday olaylar", ""]
    for n, c in enumerate(clusters[:top], 1):
        fs = c.first_seen.astimezone(TR).strftime("%d.%m %H:%M") if c.first_seen else "?"
        flag = f" ⚠️ **DİKKAT: {', '.join(c.flags)}**" if c.flags else ""
        L += [f"### {n}. {c.headline}{flag}", "",
              f"- **Puan {c.score}** {c.parts}",
              f"- Tür: {', '.join(c.categories) or '-'} · {len(c.sources)} kaynak · ilk görülme {fs}"
              + (f" · Trend: {c.trend}" if c.trend else ""),
              f"- Kaynaklar: {', '.join(c.sources[:8])}"]
        if c.categories:
            L.append(f"- Açı önerisi: {ANGLES.get(c.categories[0], '')}")
        if c.ban_link:
            L.append(f"- 🔴 Yayın yasağı haberi: {c.ban_link} — RTÜK 'Mahkeme Yayın Yasakları' sayfasından teyit et")
        for i in c.items[:4]:
            L.append(f"  - [{i.title}]({i.link}) — {i.source}")
        summ = next((i.summary for i in c.items if len(i.summary) > 60 and not i.summary.startswith("http")), "")
        if summ:
            L.append(f"  > {summ[:300]}")
        L.append("")
    md.write_text("\n".join(L), encoding="utf-8")
    data = [{**{k: v for k, v in asdict(c).items() if k != "items"}, "headline": c.headline,
             "sources": c.sources, "first_seen": c.first_seen.isoformat() if c.first_seen else None,
             "items": [{"title": i.title, "link": i.link, "source": i.source,
                        "published": i.published.isoformat() if i.published else None} for i in c.items]}
            for c in clusters[:top * 2]]
    js.write_text(json.dumps({"trends": trends, "clusters": data}, ensure_ascii=False, indent=1), encoding="utf-8")
    return md, js


def slugify(s: str) -> str:
    tr = str.maketrans("çğıöşüâîûÇĞİÖŞÜ", "cgiosuaiuCGIOSU")
    s = tr_lower(s).translate(tr)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:40].rstrip("-")


def draft_episode(report_json: Path, n: int) -> Path:
    """Gündem raporundaki n. olay için şablondan bölüm taslağı açar (kaynaklar dolu)."""
    data = json.loads(report_json.read_text(encoding="utf-8"))
    c = data["clusters"][n - 1]
    slug = "gundem-" + slugify(c["headline"])
    dst = ROOT / "episodes" / slug
    if dst.exists():
        raise SystemExit(f"zaten var: {dst}")
    (dst / "img").mkdir(parents=True)
    tpl = (ROOT / "episodes" / "_sablon" / "episode.yaml").read_text(encoding="utf-8")
    tpl = tpl.replace("id: sablon", f"id: {slug}\ngundem: true          # güncel olay: dil denetimi + docs/GUNDEM.md kontrol listesi\nkesin_hukum: false    # fail hakkında kesinleşmiş mahkûmiyet var mı?")
    tpl = tpl.replace("# top_text: \"1996, Manisa\"", "top_text: \"<gün ay yıl>, <yer> — resmi açıklamalara göre\"  # bağlam videonun İÇİNDE olmalı")
    tpl = tpl.replace('title: "<Olay adı> (Olayı yorumlara yazdım)"', f'title: "{c["headline"][:90]}"')
    srcs = "\n".join(f"  - {i['link']}  # {i['source']}: {i['title'][:80]}" for i in c["items"][:8])
    tpl = re.sub(r"sources:\n(  - .*\n?)+", f"sources:\n{srcs}\n", tpl)
    flags = f"DİKKAT: {', '.join(c['flags'])} — docs/GUNDEM.md kontrol listesi zorunlu.\n  " if c["flags"] else ""
    tpl += (f"\nnotes: |\n  GÜNDEM — ilk görülme {c['first_seen']}, {len(c['sources'])} kaynak, tür: "
            f"{', '.join(c['categories'])}.\n  {flags}  Yayından önce resmi açıklama ve yayın yasağı kontrolü yap.\n")
    (dst / "episode.yaml").write_text(tpl, encoding="utf-8")
    return dst


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--saat", type=int, default=48, help="kaç saat geriye bakılsın")
    ap.add_argument("--ilk", type=int, default=20, help="raporda kaç olay")
    ap.add_argument("--sorgu", action="append", default=[], help="ek Google News araması (tekrarlanabilir)")
    ap.add_argument("--hepsi", action="store_true", help="uygunluk puanı 0 olanları da göster")
    ap.add_argument("--taslak", type=int, metavar="N",
                    help="tarama yapmadan, en son raporun N. olayı için bölüm taslağı aç")
    a = ap.parse_args()
    if a.taslak:
        last = max(OUT.glob("*.json"), key=lambda p: p.stat().st_mtime, default=None)
        if last is None:
            raise SystemExit("Önce tarama yap: python tools/gundem.py")
        print(f"-> {draft_episode(last, a.taslak)}  (rapor: {last.name})")
        return
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    items, trends = collect(cfg, a.sorgu, a.saat)
    topic_words = {w for cat in cfg["categories"].values() for p in cat["patterns"]
                   for w in re.findall(r"[a-zçğıöşü]{3,}", p)}
    for sq in cfg.get("searches", []) + a.sorgu:
        topic_words |= set(re.findall(r"[a-zçğıöşü]{3,}", tr_lower(sq["q"] if isinstance(sq, dict) else sq)))
    clusters = cluster_items(items, topic_words=topic_words)
    for c in clusters:
        score(c, cfg, trends)
    if not a.hepsi:
        clusters = [c for c in clusters if c.parts.get("uygunluk", 0) >= 4]
    clusters.sort(key=lambda c: -c.score)
    with ThreadPoolExecutor(6) as ex:  # ilk adaylar için yayın yasağı kontrolü
        list(ex.map(_ban_check, clusters[:a.ilk]))
    md, js = report(clusters, trends, a.ilk, a.saat)
    print(f"{len(clusters)} aday küme -> {md}")


if __name__ == "__main__":
    main()
