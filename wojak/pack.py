"""Paylaşım paketi: başlık, açıklama, sabit yorum, hashtag ve yükleme kontrol listesi."""

from __future__ import annotations

from pathlib import Path

from . import censor
from .episode import Episode

DEFAULT_TAGS = ["#wojak", "#tarihselwojak", "#keşfet", "#olay", "#gizem"]


def hashtags(ep: Episode) -> str:
    tags = []
    for t in ep.hashtags + DEFAULT_TAGS:
        t = t if t.startswith("#") else f"#{t}"
        if t.lower() not in (x.lower() for x in tags):
            tags.append(t)
    return " ".join(tags[:8])  # IG: az ve alakalı hashtag daha iyi


def write(ep: Episode, out_dir: Path, video: Path | None = None) -> Path:
    title = censor.metin(ep.title)
    caption = censor.metin(ep.caption.strip())
    pinned = censor.metin(ep.pinned_comment.strip())
    tags = hashtags(ep)
    lines = [
        f"# {ep.id}",
        "",
        f"Süre: {ep.duration:.1f} sn · {len(ep.scenes)} sahne" + (f" · video: `{video.name}`" if video else ""),
        "",
        "## Başlık (YouTube Shorts başlığı / IG açıklamasının ilk satırı)",
        "",
        "```",
        title,
        "```",
        "",
        "## Instagram açıklaması",
        "",
        "```",
        (caption + "\n\n" if caption else "") + tags,
        "```",
        "",
        "## Sabit yorum (paylaşır paylaşmaz yaz ve sabitle)",
        "",
        "```",
        pinned or "(boş)",
        "```",
        "",
        "## Yükleme kontrol listesi",
        "",
        "- [ ] Kapak: `kapak.jpg` (Reels'te 'Kapağı düzenle' > galeriden ekle)",
        "- [ ] Ses: varsa Instagram içi trend sesi ekle; videodaki müziği %10-20'ye indir",
        "- [ ] Paylaştıktan sonra ilk 1 dakika içinde sabit yorumu yaz ve sabitle",
        "- [ ] YouTube Shorts'a da aynı başlıkla yükle; yorumu orada da sabitle",
        "- [ ] TikTok'a da aynı başlıkla yükle (aynı video, filigran yok)",
        "- [ ] Paylaşım saati: 17:00-21:00 (altın dönem verisi: 21:00 sonrası paylaşımlar ~%35 daha az izlendi)",
    ]
    if ep.sources:
        lines += ["", "## Kaynaklar (doğrulama için, paylaşılmaz)", ""] + [f"- {s}" for s in ep.sources]
    p = out_dir / "paylasim.md"
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return p
