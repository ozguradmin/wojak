"""Yayın öncesi dil ve içerik denetimi (özellikle güncel olaylar için).

Kaynak: docs/GUNDEM.md > Hukuk. Sansürlü yazım (k4til, c!nayet) hukuki koruma SAĞLAMAZ; burada
kelimeler anlamına göre (maskelenmiş hâlleri dahil) denetlenir. Hukuki tavsiye değildir.
"""

from __future__ import annotations

import re

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
