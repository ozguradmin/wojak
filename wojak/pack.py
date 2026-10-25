"""Paylaşım paketi: hesap sahibinin kopyala-yapıştır yapacağı metinler + yükleme kontrol listesi.

Akış (2026-10): videoyu ben hazırlarım, hesap sahibi onaylar ve kendisi paylaşır.
  - Instagram Reels : açıklama = başlık + hikâyenin tamamı + atıf; hashtag YOK (hesap sahibinin düzeni, 13.10.2026)
  - YouTube Shorts  : açıklama = başlık + hikâyenin tamamı + atıf + en çok 3 hashtag (2 konu + #shorts); hikâye ayrıca
                      yorum olarak atılır, hesap sahibi sabitler (hesap sahibi 22.10: "açıklamaya da olayı yaz")
  - TikTok          : açıklama = Instagram ile aynı (sınır 4000)

Çıktı: out/<id>/paylasim.md (hepsi bir arada) ve out/<id>/metinler/*.txt (telefonda tek dokunuşla kopyalamak için).
"""

from __future__ import annotations

import re
from pathlib import Path

from . import censor, config
from .episode import Episode

DEFAULT_TAGS = config.KANALLAR["tr"]["default_tags"]
LIMITS = {"instagram": 2200, "instagram_tags": 5, "youtube_title": 100, "youtube_desc": 5000, "tiktok": 4000,
          "youtube_tags": 3}   # hesap sahibi (13.10.2026): YouTube'da 2-3 hashtag
BRAND_TAGS = config.KANALLAR["tr"]["brand_tags"]


def hashtags(ep: Episode, n: int = 8) -> str:
    tags = []
    for t in ep.hashtags + config.KANALLAR[ep.kanal]["default_tags"]:
        t = t if t.startswith("#") else f"#{t}"
        if t.lower() not in (x.lower() for x in tags):
            tags.append(t)
    return " ".join(tags[:n])  # IG: az ve alakalı hashtag daha iyi


def instagram_tags(ep: Episode) -> str:
    """Instagram gönderi başına en fazla 5 hashtag kabul ediyor (Aralık 2025'ten beri): 3 konu + 2 marka."""
    brand = config.KANALLAR[ep.kanal]["brand_tags"]
    own = [t for t in hashtags(ep, 20).split() if t.lower() not in brand]
    return " ".join(own[:LIMITS["instagram_tags"] - len(brand)] + brand)


def _plain_title(title: str) -> str:
    """'(Olayı yorumlara yazdım)' / '(story in the comments)' gibi yoruma yönlendiren ekleri atar."""
    return re.sub(r"\s*\([^)]*(?:yorum|comment)[^)]*\)", "", title, flags=re.IGNORECASE).strip()


def texts(ep: Episode) -> dict[str, str]:
    """Platform metinleri. Hassas kelimeler censor.metin ile (üslup; hukuki koruma değildir)."""
    k = config.KANALLAR[ep.kanal]
    title = censor.metin(ep.title.strip(), ep.kanal)
    story = censor.metin(ep.pinned_comment.strip(), ep.kanal)
    tags = hashtags(ep)
    head = _plain_title(title)
    credit = f"{k['credit']}: {ep.credits}" if ep.credits else ""  # CC BY atfı
    return {
        # Hesap Instagram'da hashtag kullanmıyor (sahibin düzeni, 13.10.2026): başlık + hikâye + atıf
        "instagram_aciklama": "\n\n".join(x for x in (head, story, credit) if x),
        "youtube_baslik": title,
        # 23.10: açıklama hikâyenin tamamını taşır; 'caption' ("tamamı sabit yorumda 👇") YouTube'a girmez
        "youtube_aciklama": "\n\n".join(x for x in (
            head, f"{k['uzun']}: {ep.uzun_video}" if ep.uzun_video else "", story, credit,
            hashtags(ep, LIMITS["youtube_tags"] - 1) + " #shorts") if x),   # 2 konu + #shorts (eskiden 8 + #shorts)
        "youtube_sabit_yorum": story,
        "tiktok_aciklama": "\n\n".join(x for x in (head, story, credit, tags) if x),
    }


def warnings(t: dict[str, str], ep: Episode | None = None) -> list[str]:
    w = []
    if len(t["instagram_aciklama"]) > LIMITS["instagram"]:
        w.append(f"Instagram açıklaması {len(t['instagram_aciklama'])} karakter (sınır 2200): hikâyeyi kısalt")
    n_tags = len(re.findall(r"(?<!\w)#\w+", t["instagram_aciklama"]))
    if n_tags > LIMITS["instagram_tags"]:
        w.append(f"Instagram açıklamasında {n_tags} hashtag (sınır 5)")
    if len(t["tiktok_aciklama"]) > LIMITS["tiktok"]:
        w.append(f"TikTok açıklaması {len(t['tiktok_aciklama'])} karakter (sınır 4000)")
    n_yt = len(re.findall(r"(?<!\w)#\w+", t["youtube_aciklama"]))
    if n_yt > LIMITS["youtube_tags"]:
        w.append(f"YouTube açıklamasında {n_yt} hashtag (hesap sahibinin kuralı: 2-3)")
    if len(t["youtube_aciklama"]) > LIMITS["youtube_desc"]:
        w.append(f"YouTube açıklaması {len(t['youtube_aciklama'])} karakter (sınır 5000): hikâyeyi kısalt")
    if len(t["youtube_baslik"]) > LIMITS["youtube_title"]:
        w.append(f"YouTube başlığı {len(t['youtube_baslik'])} karakter (sınır 100)")
    if not t["youtube_sabit_yorum"]:
        w.append("Hikâye metni (pinned_comment) boş")
    if ep is not None:
        bad = [h for h in ep.hashtags if censor.metin(h, ep.kanal) != h]
        if bad:
            w.append(f"Hassas kelimeli hashtag ({', '.join(bad)}): sansürlenemez, çıkar")
    return w


def _block(title: str, body: str, note: str = "") -> list[str]:
    return [f"### {title}" + (f" — {note}" if note else ""), "", "```", body or "(boş)", "```", ""]


def write(ep: Episode, out_dir: Path, video: Path | None = None, denetim: list[str] | None = None) -> Path:
    t = texts(ep)
    tdir = out_dir / "metinler"
    tdir.mkdir(parents=True, exist_ok=True)
    for name, body in t.items():
        (tdir / f"{name}.txt").write_text(body + "\n", encoding="utf-8")

    n = {k: len(v) for k, v in t.items()}
    lines = [f"# {ep.id} — paylaşım paketi", "",
             f"Süre: {ep.duration:.1f} sn · {len(ep.scenes)} sahne"
             + (f" · video: `{video.name}`" if video else "") + " · kapak: `kapak.jpg`", ""]
    for w in warnings(t, ep) + [f"Denetim: {d}" for d in (denetim or [])]:
        lines += [f"> ⚠️ {w}", ""]
    if (out_dir / f"{ep.id}_dolgu.mp4").exists():
        lines += [f"Ek: `{ep.id}_dolgu.mp4` + `kapak_dolgu.jpg`: siyah bantlar bulanık arka planla dolu sürüm. Kenarlık "
                  "A/B testi için Instagram'da **deneme reel** olarak paylaşılabilir (KONSEPT §3).", ""]
    lines += ["## Instagram Reels", ""]
    lines += _block("Açıklama (başlık + hikâye; hashtag yok, hesabın kendi düzeni)", t["instagram_aciklama"],
                    f"{n['instagram_aciklama']}/2200")
    lines += ["## YouTube Shorts", ""]
    lines += _block("Başlık", t["youtube_baslik"], f"{n['youtube_baslik']}/100")
    lines += _block("Açıklama", t["youtube_aciklama"])
    lines += _block("Sabit yorum (yayından hemen sonra yaz ve sabitle)", t["youtube_sabit_yorum"],
                    f"{n['youtube_sabit_yorum']} karakter")
    lines += ["## TikTok (isteğe bağlı)", ""]
    lines += _block("Açıklama", t["tiktok_aciklama"], f"{n['tiktok_aciklama']}/4000")
    ai = ("- [ ] **Yapay zekâ etiketi:** videoda fotogerçekçi yapay zekâ görseli var → Instagram'da "
          "\"Yapay zekâ etiketi ekle\", YouTube'da \"Değiştirilmiş veya yapay içerik: Evet\", TikTok'ta "
          "\"Yapay zekâ ile oluşturulan içerik\" açık") if ep.ai_generated else \
         ("- [ ] Yapay zekâ sorusu: \"Hayır\" (bu bölümde fotogerçekçi yapay zekâ görseli yok; wojak çizimi gerçekçi "
          "sayılmaz)")
    telifli = sorted({p.name for sc in ep.scenes for p in [sc.bg, *sc.images] if p and p.parent.name == "telifli"})
    lines += [
        "## Yükleme kontrol listesi", "",
        *([f"- [ ] **Lisans kararı senin:** " + (ep.telif_notu or
           f"şu görseller haber ajansı/gazete malı (telifli): {', '.join(f'`{n}`' for n in telifli)}. Kanal eskiden "
           "de böyle kullanıyordu; istemezsen serbest lisanslı yedekle değiştiririm (kaynaklar aşağıda)")]
          if telifli or ep.telif_notu else []),
        *(["- [ ] Saat: **20:00-20:15**, 2 günde 1 (Instagram altın döneminde 25/25 reel bu düzende)"]
          if ep.kanal == "tr" else
          ["- [ ] YouTube'u yayın botu yükler (wojak-en-ozel). Instagram: ABD akşamı (TR 01:00-04:00) önerilir"]),
        "- [ ] Instagram: Reels → videoyu seç → **Kapağı düzenle → Galeriden ekle → `kapak.jpg`** → açıklamayı yapıştır",
        "- [ ] Ses: videodaki kanalın imza müziği (orijinal ses). Ayrıca müzik ekleme",
        "- [ ] YouTube: Shorts yükle → başlık + açıklama → yayınlanınca **sabit yorumu yaz ve sabitle** (⋮ → Sabitle)",
        ai,
        "- [ ] İlk 1-2 saat: yorumlara cevap (özellikle \"ben oralıyım\" yorumları), hakaret/isim ifşası içerenleri sil",
        *([f"- [ ] **Uzun video bağlantısı:** YouTube Studio → bu Short → Düzenle → **İlgili video** → uzun videoyu seç "
            "(Short'u izleyen tek dokunuşla uzun videoya geçer). Açıklamadaki \"Uzun hali\" satırına uzun videonun "
            "linkini koy"] if ep.uzun_video else []),
        *[f"- [ ] {m}" for m in ep.ek_maddeler],
    ]
    if ep.gundem:
        lines.append("- [ ] **Güncel olay:** paylaşmadan hemen önce yayın yasağı yok mu? (RTÜK 'Mahkeme Yayın Yasakları')")
    lines += ["", "Metinler ayrıca tek tek: `metinler/` klasöründe (.txt)."]
    if ep.sources:
        lines += ["", "## Kaynaklar (doğrulama için, paylaşılmaz)", ""] + [f"- {s}" for s in ep.sources]
    p = out_dir / "paylasim.md"
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return p
