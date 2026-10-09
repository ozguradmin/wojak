"""Hassas kelime sansürü.

Hesap, 'olay' dönemindeki başlık/ekran yazısı/sabit yorumlarda hassas kelimeleri
harf değiştirerek yazıyordu (c*n4yet, *ldürüldü, t3c4v*z, *leceğim...). Amaç
platformların otomatik kısıtlamasına (erişim düşürme, yaş sınırı) takılmamak.

İki seviye:
  - "ekran": video üstü yazılar için hafif (sadece en riskli kökler)
  - "metin": başlık/açıklama/sabit yorum için daha kapsamlı

Bu bir ÜSLUP aracıdır, hukuki koruma DEĞİLDİR: "k4til" yazmak hukuken "katil" demektir.
Güncel olaylarda kelime seçimi wojak.denetim.check() ile ayrıca denetlenir (docs/GUNDEM.md §7).
"""

from __future__ import annotations

import re

# (kök regex, değiştirme): kelime BAŞINDA eşleşir ((?<!\w)), ek korunur. Kelime başı şartı olmadan
# "Bakanlığı", "Gölü", "bölüm", "savuran" gibi sıradan kelimeler bozuluyordu.
W = r"(?<!\w)"
_EKRAN = [
    (W + r"öld[üu]r", "*ldür"),
    (W + r"öl(?=[üemdsiıyl])", "*l"),
    (W + r"cinayet", "c!nayet"),
    (W + r"tecav[üu]z", "t3c4v*z"),
    (W + r"intihar", "1nt1h4r"),
    (W + r"ceset", "c3s3t"),
    (W + r"cesed", "c3s3d"),
    (W + r"kan(?!\w)", "k*n"),
    (W + r"kanl(?=[ıi])", "k*nl"),
    (W + r"taciz", "t4c*z"),
]
_METIN = _EKRAN + [
    (W + r"katlet", "k4tlet"),
    # ı/i katlaması kapalı: "katıldı" / "KATILIM" katil değildir
    (W + r"(?-i:[kK][aA][tT][iİ][lL])", "k4til"),
    (W + r"b[ıi]çak", "b*çak"),
    (W + r"silah", "s!lah"),
    (W + r"vur(?=ul|du|an)", "v*r"),
    (W + r"bo[ğg]arak", "b*ğarak"),
    (W + r"bo[ğg]ul", "b*ğul"),
    (W + r"uyu[şs]turucu", "uyu$turucu"),
    (W + r"istismar", "1st1smar"),
    (W + r"pedofil", "p3d0f1l"),
    (W + r"terör", "t3rör"),
    (W + r"bomba", "b0mba"),
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
