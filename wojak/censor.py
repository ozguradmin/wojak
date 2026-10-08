"""Hassas kelime sansürü.

Hesap, 'olay' dönemindeki başlık/ekran yazısı/sabit yorumlarda hassas kelimeleri
harf değiştirerek yazıyordu (c*n4yet, *ldürüldü, t3c4v*z, *leceğim...). Amaç
platformların otomatik kısıtlamasına (erişim düşürme, yaş sınırı) takılmamak.

İki seviye:
  - "ekran": video üstü yazılar için hafif (sadece en riskli kökler)
  - "metin": başlık/açıklama/sabit yorum için daha kapsamlı
"""

from __future__ import annotations

import re

# (kök regex, değiştirme) — kelimenin başını yakalar, eki korur.
_EKRAN = [
    (r"öld[üu]r", "*ldür"),
    (r"öl(?=[üemdsiıyl])", "*l"),
    (r"cinayet", "c!nayet"),
    (r"tecav[üu]z", "t3c4v*z"),
    (r"intihar", "1nt1h4r"),
    (r"ceset", "c3s3t"),
    (r"cesed", "c3s3d"),
    (r"\bkan\b", "k*n"),
    (r"kanl[ıi]", "k*nl"),
    (r"taciz", "t4c*z"),
]
_METIN = _EKRAN + [
    (r"katlet", "k4tlet"),
    (r"katil", "k4til"),
    (r"b[ıi]çak", "b*çak"),
    (r"silah", "s!lah"),
    (r"vur(?=ul|du|an)", "v*r"),
    (r"bo[ğg]arak", "b*ğarak"),
    (r"bo[ğg]ul", "b*ğul"),
    (r"uyu[şs]turucu", "uyu$turucu"),
    (r"istismar", "1st1smar"),
    (r"pedofil", "p3d0f1l"),
    (r"terör", "t3rör"),
    (r"bomba", "b0mba"),
]


def _apply(text: str, rules) -> str:
    for pat, rep in rules:
        def sub(m, rep=rep):
            s = m.group(0)
            return rep[0].upper() + rep[1:] if s[:1].isupper() and rep[0].isalpha() else rep
        text = re.sub(pat, sub, text, flags=re.IGNORECASE)
    return text


def ekran(text: str) -> str:
    return _apply(text, _EKRAN)


def metin(text: str) -> str:
    return _apply(text, _METIN)
