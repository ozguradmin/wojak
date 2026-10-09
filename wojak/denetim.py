"""Yayın öncesi dil ve içerik denetimi (özellikle güncel olaylar için).

Kaynak: docs/GUNDEM.md > Hukuk. Sansürlü yazım (k4til, c!nayet) hukuki koruma SAĞLAMAZ; burada
kelimeler anlamına göre (maskelenmiş hâlleri dahil) denetlenir. Hukuki tavsiye değildir.
"""

from __future__ import annotations

import re
from pathlib import Path

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
    if ep.gundem:
        if not ep.kesin_hukum:
            for w in _HUKUM:
                r = _rx(w)
                for where, txt in texts.items():
                    if r.search(txt or ""):
                        out.append(f"[masumiyet] '{w}' ({where}) — hüküm kesinleşmemiş: 'şüpheli', 'iddiaya göre' kullan")
        for w, why in _YASAK.items():
            r = _rx(w)
            if any(r.search(t or "") for t in texts.values()):
                out.append(f"[kırmızı çizgi] '{w}': {why}")
        if ep.duration > 17.5:
            out.append(f"[format] güncel olayda süre {ep.duration:.1f} sn; veriye göre 10-17 sn")
        if len(ep.title.split()) <= 3:
            out.append("[başlık] sadece isim/etiket gibi duruyor; 'kim + sıradan eylem + ters dönen son' kalıbı daha iyi")
        if not ep.top_text:
            out.append("[bağlam] güncel olayda üst yazıya tarih/yer bağlamı ekle (YouTube: bağlam videonun içinde olmalı)")
        if "Kaynak:" not in ep.pinned_comment and "açıklamasına göre" not in ep.pinned_comment:
            out.append("[kaynak] sabit yorumda resmi kaynak ve tarih yok ('X Valiliği'nin 12.10 14:30 açıklamasına göre...')")
    if re.search(r"(?<!\w)(?:[1-9]|1[0-7]) yaşındaki", " ".join(t for t in texts.values() if t)):
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
            if s.text and not re.search(r"sonra$", s.text.strip()):
                out.append(f"[stil] {tag}: kart yalnız ileri zaman atlaması olmalı ('Bir süre sonra', 'Birkaç saat sonra')")
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
    elif ep.music.file.resolve() not in (config.MUSIC_CHANNEL.resolve(), config.MUSIC_FALLBACK.resolve()):
        out.append("[stil] imza ses dışında bir müzik (music: kanal önerilir)")
    return out
