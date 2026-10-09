"""Paylaşım paketi: hesap sahibinin kopyala-yapıştır yapacağı metinler + yükleme kontrol listesi.

Akış (2026-10): videoyu ben hazırlarım, hesap sahibi onaylar ve kendisi paylaşır.
  - Instagram Reels : açıklama = başlık + hikâyenin tamamı + hashtag (hikâye açıklamada, yorumda değil)
  - YouTube Shorts  : başlık + kısa açıklama; hikâye SABİT YORUMDA (hesap sahibi yazar ve sabitler)
  - TikTok          : açıklama = Instagram ile aynı (sınır 4000)

Çıktı: out/<id>/paylasim.md (hepsi bir arada) ve out/<id>/metinler/*.txt (telefonda tek dokunuşla kopyalamak için).
"""

from __future__ import annotations

import re
from pathlib import Path

from . import censor
from .episode import Episode

DEFAULT_TAGS = ["#wojak", "#tarihselwojak", "#keşfet", "#olay", "#gizem"]
LIMITS = {"instagram": 2200, "youtube_title": 100, "youtube_desc": 5000, "tiktok": 4000}


def hashtags(ep: Episode, n: int = 8) -> str:
    tags = []
    for t in ep.hashtags + DEFAULT_TAGS:
        t = t if t.startswith("#") else f"#{t}"
        if t.lower() not in (x.lower() for x in tags):
            tags.append(t)
    return " ".join(tags[:n])  # IG: az ve alakalı hashtag daha iyi


def _plain_title(title: str) -> str:
    """'(Olayı yorumlara yazdım)' gibi yoruma yönlendiren ekleri atar (Instagram'da hikâye açıklamada)."""
    return re.sub(r"\s*\([^)]*yorum[^)]*\)", "", title).strip()


def texts(ep: Episode) -> dict[str, str]:
    """Platform metinleri. Hassas kelimeler censor.metin ile (üslup; hukuki koruma değildir)."""
    title = censor.metin(ep.title.strip())
    story = censor.metin(ep.pinned_comment.strip())
    caption = censor.metin(ep.caption.strip())
    tags = hashtags(ep)
    head = _plain_title(title)
    long_cap = "\n\n".join(x for x in (head, story, tags) if x)
    yt_desc = "\n\n".join(x for x in (caption, tags + " #shorts") if x)
    return {
        "instagram_aciklama": long_cap,
        "youtube_baslik": title,
        "youtube_aciklama": yt_desc,
        "youtube_sabit_yorum": story,
        "tiktok_aciklama": long_cap,
    }


def warnings(t: dict[str, str]) -> list[str]:
    w = []
    if len(t["instagram_aciklama"]) > LIMITS["instagram"]:
        w.append(f"Instagram açıklaması {len(t['instagram_aciklama'])} karakter (sınır 2200): hikâyeyi kısalt")
    if len(t["youtube_baslik"]) > LIMITS["youtube_title"]:
        w.append(f"YouTube başlığı {len(t['youtube_baslik'])} karakter (sınır 100)")
    if not t["youtube_sabit_yorum"]:
        w.append("Hikâye metni (pinned_comment) boş")
    return w


def _block(title: str, body: str, note: str = "") -> list[str]:
    return [f"### {title}" + (f" — {note}" if note else ""), "", "```", body or "(boş)", "```", ""]


def write(ep: Episode, out_dir: Path, video: Path | None = None) -> Path:
    t = texts(ep)
    tdir = out_dir / "metinler"
    tdir.mkdir(parents=True, exist_ok=True)
    for name, body in t.items():
        (tdir / f"{name}.txt").write_text(body + "\n", encoding="utf-8")

    n = {k: len(v) for k, v in t.items()}
    lines = [f"# {ep.id} — paylaşım paketi", "",
             f"Süre: {ep.duration:.1f} sn · {len(ep.scenes)} sahne"
             + (f" · video: `{video.name}`" if video else "") + " · kapak: `kapak.jpg`", ""]
    for w in warnings(t):
        lines += [f"> ⚠️ {w}", ""]
    lines += ["## Instagram Reels", ""]
    lines += _block("Açıklama (başlık + hikâye + hashtag)", t["instagram_aciklama"], f"{n['instagram_aciklama']}/2200")
    lines += ["## YouTube Shorts", ""]
    lines += _block("Başlık", t["youtube_baslik"], f"{n['youtube_baslik']}/100")
    lines += _block("Açıklama", t["youtube_aciklama"])
    lines += _block("Sabit yorum (yayından hemen sonra yaz ve sabitle)", t["youtube_sabit_yorum"],
                    f"{n['youtube_sabit_yorum']} karakter")
    lines += ["## TikTok (isteğe bağlı)", ""]
    lines += _block("Açıklama", t["tiktok_aciklama"], f"{n['tiktok_aciklama']}/4000")
    ai = ("- [ ] **Yapay zekâ etiketi:** videoda fotogerçekçi yapay zekâ görseli var → Instagram'da "
          "\"Yapay zekâ etiketi ekle\", YouTube'da \"Değiştirilmiş veya yapay içerik: Evet\"") if ep.ai_generated else \
         "- [ ] Yapay zekâ sorusu: \"Hayır\" (wojak çizimi gerçekçi değil; gerçek fotoğraflar gerçek)"
    lines += [
        "## Yükleme kontrol listesi", "",
        "- [ ] Saat: **17:00-21:00** (altın dönemde 21:00 sonrası paylaşımlar ~%35 daha az izlendi)",
        "- [ ] Instagram: Reels → videoyu seç → **Kapağı düzenle → Galeriden ekle → `kapak.jpg`** → açıklamayı yapıştır",
        "- [ ] Ses: videodaki kanalın imza müziği (orijinal ses). Ayrıca müzik ekleme",
        "- [ ] YouTube: Shorts yükle → başlık + açıklama → yayınlanınca **sabit yorumu yaz ve sabitle** (⋮ → Sabitle)",
        ai,
        "- [ ] İlk 1-2 saat: yorumlara cevap (özellikle \"ben oralıyım\" yorumları), hakaret/isim ifşası içerenleri sil",
    ]
    if ep.gundem:
        lines.append("- [ ] **Güncel olay:** paylaşmadan hemen önce yayın yasağı yok mu? (RTÜK 'Mahkeme Yayın Yasakları')")
    lines += ["", "Metinler ayrıca tek tek: `metinler/` klasöründe (.txt)."]
    if ep.sources:
        lines += ["", "## Kaynaklar (doğrulama için, paylaşılmaz)", ""] + [f"- {s}" for s in ep.sources]
    p = out_dir / "paylasim.md"
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return p
