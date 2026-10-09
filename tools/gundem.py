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


# Her olayda geçebilen, tek başına "aynı olay" kanıtı olmayan özel isimler
GENERIC_PROPER = {"istan", "ankar", "izmir", "türki", "türk", "son", "dakik", "flaş", "vali", "bakan", "polis",
                  "jandarma", "afad", "emniy"}


def tr_lower(s: str) -> str:
    return s.replace("I", "ı").replace("İ", "i").lower()


def strip_html(s: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()


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


def fetch_feed(name: str, url: str) -> list[Item]:
    try:
        r = requests.get(url, headers=UA, timeout=25)
        r.raise_for_status()
        root = ET.fromstring(r.content)
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
        out.append(Item(title, link, source, pub, strip_html(_child(el, "description"))[:400], name))
    return out


def fetch_trends(url: str) -> list[dict]:
    try:
        r = requests.get(url, headers=UA, timeout=25)
        r.raise_for_status()
        root = ET.fromstring(r.content)
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
    jobs = [(f["name"], f["url"]) for f in cfg.get("feeds", [])]
    for q in list(cfg.get("searches", [])) + extra_queries:
        jobs.append((f"Google News: {q}", GNEWS_SEARCH.format(q=urllib.parse.quote(f"{q} when:2d"))))
    with ThreadPoolExecutor(8) as ex:
        results = list(ex.map(lambda j: fetch_feed(*j), jobs))
        trends_f = ex.submit(fetch_trends, cfg["trends"]) if cfg.get("trends") else None
    items = [i for rs in results for i in rs]
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


def cluster_items(items: list[Item], thr: float = 0.45, topic_words: set[str] | None = None) -> list[Cluster]:
    """Aynı olayı anlatan başlıkları kümeler.

    Benzerlik, ortak kelimelerin NADİRLİK ağırlıklı (IDF) toplamıdır; "çocuk", "ölü",
    "bulundu" gibi her habere geçen kelimeler alakasız olayları birleştiremez.
    Her başlık yalnızca kümenin ilk (tohum) başlığıyla karşılaştırılır.
    """
    stems = [{_stem(t) for t in i.toks} for i in items]
    df: dict[str, int] = {}
    for st in stems:
        for t in st:
            df[t] = df.get(t, 0) + 1
    n = max(1, len(items))
    idf = {t: math.log(n / c) for t, c in df.items()}
    proper = _proper_nouns(items) - GENERIC_PROPER

    topic = {_stem(tr_lower(w)) for w in (topic_words or set())}

    def anchored(shared: set[str]) -> bool:
        # "kayıp + çocuk + yaşındaki" gibi genel kelimeler tek başına yetmez: ortak bir özel isim
        # (Maltepe, Efe...) ya da nadir bir kelime (haberlerin %3'ünden azında geçen) şart.
        # Kategori/arama kelimeleri (kayıp, aranıyor...) bizim sorgularımız yüzünden sık
        # toplandığı için çapa sayılmaz.
        cand = shared - topic
        return any(t in proper and idf[t] > math.log(10) for t in cand) or \
            any(idf[t] > math.log(1 / 0.03) for t in cand)
    order = sorted(range(len(items)),
                   key=lambda k: items[k].published or datetime.min.replace(tzinfo=timezone.utc))
    clusters: list[tuple[set[str], float, Cluster]] = []
    seen = set()
    for k in order:
        it, st = items[k], stems[k]
        key = tr_lower(it.title)
        if not st:
            continue
        w_it = sum(idf[t] for t in st)
        best, best_sim = None, 0.0
        for seed, w_seed, c in clusters:
            shared = st & seed
            if len(shared) < 2:
                continue
            sim = sum(idf[t] for t in shared) / max(1e-9, min(w_it, w_seed))
            if sim > best_sim and anchored(shared):
                best, best_sim = c, sim
        if best is not None and best_sim >= thr:
            if key not in {tr_lower(x.title) for x in best.items} or it.source not in best.sources:
                best.items.append(it)
        elif key not in seen:
            clusters.append((st, w_it, Cluster(items=[it])))
        seen.add(key)
    return _merge_pass([c for _, _, c in clusters], idf, proper)


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


def _signature(c: Cluster, idf: dict[str, float], k: int = 6) -> list[str]:
    cnt: dict[str, int] = {}
    for i in c.items:
        for t in {_stem(x) for x in i.toks}:
            cnt[t] = cnt.get(t, 0) + 1
    return sorted(cnt, key=lambda t: -(cnt[t] * idf.get(t, 0)))[:k]


def _merge_pass(clusters: list[Cluster], idf: dict[str, float], proper: set[str]) -> list[Cluster]:
    """İkinci geçiş: aynı olayın farklı ifade edilmiş başlıklarını birleştirir
    (ör. "Maltepe'de bina çöktü" / "Maltepe'de çöken binada arama sürüyor").
    Koşul: imzalarda en az 2 ortak kelime ve bunlardan biri ortak bir özel isim
    (çok yaygın olanlar hariç: İstanbul, Türkiye...)."""
    common = math.log(10)  # haberlerin %10'undan fazlasında geçen özel isim "yaygın" sayılır
    changed = True
    while changed:
        changed = False
        sigs = [set(_signature(c, idf)) for c in clusters]
        for a in range(len(clusters)):
            for b in range(a + 1, len(clusters)):
                shared = sigs[a] & sigs[b]
                anchor = [t for t in shared if t in proper and idf.get(t, 0) > common]
                if len(shared) >= 2 and anchor:
                    clusters[a].items.extend(clusters[b].items)
                    del clusters[b]
                    changed = True
                    break
            if changed:
                break
    return clusters


def _match(text_tokens: list[str], text: str, roots: list[str]) -> list[str]:
    hits = []
    for r in roots:
        r = tr_lower(str(r))
        if " " in r:
            if r in text:
                hits.append(r)
        elif any(tok.startswith(r) for tok in text_tokens):
            hits.append(r)
    return hits


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
        out.append(w if sentence_start or not w[:1].isupper() else "")
    return " ".join(out)


def score(c: Cluster, cfg: dict, trends: list[dict]) -> None:
    text = tr_lower(" ".join(_content_text(f"{i.title}. {i.summary}") for i in c.items))
    toks = re.findall(r"[a-zçğıöşüâîû0-9]+", text)
    fit = 0.0
    strength = {}
    for name, cat in cfg["categories"].items():
        hits = _match(toks, text, cat["roots"])
        if hits:
            strength[name] = cat["weight"] * min(2, len(set(hits)))
            fit += strength[name]
    c.categories = sorted(strength, key=lambda k: -strength[k])
    excl = _match(toks, text, cfg["exclude"]["roots"])
    penalty = cfg["exclude"]["weight"] * min(2, len(set(excl))) if excl else 0.0
    for s in cfg.get("sensitive", []):
        if ("all" in s and all(_match(toks, text, [w]) for w in s["all"])) or \
           ("any" in s and _match(toks, text, s["any"])):
            c.flags.append(s["label"])
    n_src = len(c.sources)
    coverage = 3.0 * math.log2(1 + n_src)
    trend_bonus = 0.0
    ctoks = set(tokens(" ".join(i.title for i in c.items)))
    for t in trends:
        tt = set(tokens(t["term"]))
        if tt and len(tt & ctoks) >= max(1, math.ceil(len(tt) * 0.6)):
            traffic = int(re.sub(r"\D", "", t["traffic"] or "0") or 0)
            trend_bonus = max(trend_bonus, 2.0 + math.log10(1 + traffic))
            c.trend = f"{t['term']} ({t['traffic']})"
    fs = c.first_seen
    age_h = (datetime.now(timezone.utc) - fs).total_seconds() / 3600 if fs else 24
    recency = max(0.0, 2.0 - age_h / 24)
    c.parts = {"uygunluk": round(fit, 1), "kaynak": round(coverage, 1), "trend": round(trend_bonus, 1),
               "tazelik": round(recency, 1), "konu_dışı": round(penalty, 1)}
    c.score = round(fit + coverage + trend_bonus + recency + penalty, 1) if fit > 0 else round(penalty + coverage / 3, 1)


ANGLES = {
    "kayip": "Son masum an: kaybolan kişinin sıradan bir cümlesi (\"Birazdan dönerim anne\"). Kanıt: arama ekibi/afiş.",
    "kahramanlik": "Fedakârlık repliği: kahramanın tereddütsüz tek cümlesi (\"Önce çocuklar!\"). Kanıt: gerçek fotoğraf.",
    "mucize": "Mucize repliği: kurtarılan ya da kurtaranın kısa sözü. Kanıt: kurtarma anı fotoğrafı.",
    "gizem": "Merak repliği: keşfedenin şaşkın cümlesi (\"Bu duvarın arkasında ne var?\"). Kanıt: yer fotoğrafı.",
    "tarih": "Keşif repliği: kazı ekibinden kısa cümle. Kanıt: buluntu fotoğrafı. 'Tarihsel' seriye uygun.",
    "suc": "Dramatik ironi: kurbanın olaydan önceki sıradan cümlesi. Fail ürkütücü çizilir. Sadece kesinleşmiş bilgi.",
    "kaza": "Son an repliği (\"Toprak mı kayıyor?\"). Kanıt: olay yeri. Ancak insan hikâyesi varsa seç.",
    "hayvan": "Vefa repliği (hayvanın gözünden ya da sahibinden). Kanıt: gerçek fotoğraf.",
}


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
    tpl = tpl.replace("id: sablon", f"id: {slug}")
    tpl = tpl.replace('title: "<Olay adı> (Olayı yorumlara yazdım)"', f'title: "{c["headline"][:90]}"')
    srcs = "\n".join(f"  - {i['link']}  # {i['source']}: {i['title'][:80]}" for i in c["items"][:8])
    tpl = re.sub(r"sources:\n(  - .*\n?)+", f"sources:\n{srcs}\n", tpl)
    flags = f"DİKKAT: {', '.join(c['flags'])} — docs/GUNDEM.md kontrol listesi zorunlu.\n" if c["flags"] else ""
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
    topic_words = {w for cat in cfg["categories"].values() for r in cat["roots"] for w in str(r).split()}
    topic_words |= {w for q in cfg.get("searches", []) + a.sorgu for w in q.split()}
    clusters = cluster_items(items, topic_words=topic_words)
    for c in clusters:
        score(c, cfg, trends)
    if not a.hepsi:
        clusters = [c for c in clusters if c.parts.get("uygunluk", 0) > 0]
    clusters.sort(key=lambda c: -c.score)
    md, js = report(clusters, trends, a.ilk, a.saat)
    print(f"{len(clusters)} aday küme -> {md}")


if __name__ == "__main__":
    main()
