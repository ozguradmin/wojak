"""Uzun video teslim paketi: paylasim.md (başlık alternatifleri, açıklama + bölüm zaman damgaları, kaynaklar,
görsel atıfları, etiketler, sabit yorum, yükleme kontrol listesi), .srt, küçük resimler.

YouTube bölüm kuralları (açıklamadaki zaman damgalarıyla otomatik bölümler): ilk damga 0:00, en az 3 bölüm,
her bölüm en az 10 sn, damgalar artan sırada.
"""

from __future__ import annotations

import math
from pathlib import Path

from .spec import Video
from .zaman import Zaman, zaman_str

BASLIK_MAX = 100
ETIKET_MAX = 500
ACIKLAMA_MAX = 5000


def bolum_damgalari(z: Zaman) -> list[tuple[int, str]]:
    """(saniye, ad): bölümün ilk sahnesinin başı, aşağı yuvarlanmış; ilki her zaman 0."""
    out = []
    for ad, t in z.bolum_baslari():
        s = 0 if not out else int(math.floor(t + 1e-6))
        out.append((s, ad))
    return out


def bolum_denetle(damgalar: list[tuple[int, str]], toplam: float) -> list[str]:
    u = []
    if not damgalar or damgalar[0][0] != 0:
        u.append("ilk bölüm 0:00'da başlamalı")
    if len(damgalar) < 3:
        u.append(f"YouTube otomatik bölüm için en az 3 bölüm ister ({len(damgalar)} var)")
    for i, (s, ad) in enumerate(damgalar):
        son = damgalar[i + 1][0] if i + 1 < len(damgalar) else toplam
        if son - s < 10:
            u.append(f"'{ad}' bölümü {son - s:.0f} sn: YouTube her bölüm için en az 10 sn ister")
        if i and s <= damgalar[i - 1][0]:
            u.append(f"'{ad}' damgası artan sırada değil")
    return u


def bolum_metni(damgalar: list[tuple[int, str]]) -> str:
    return "\n".join(f"{zaman_str(s)} {ad}" for s, ad in damgalar)


def aciklama(v: Video, z: Zaman) -> str:
    p = v.paket
    parcalar = []
    if p.get("aciklama"):
        parcalar.append(" ".join(str(p["aciklama"]).split("\n")).replace("  ", " ").strip())
    if p.get("short_url"):
        parcalar.append(f"Kısa hali (Short): {p['short_url']}")
    else:
        parcalar.append("Kısa hali (Short): [Short bağlantısı]")
    parcalar.append("Bölümler\n" + bolum_metni(bolum_damgalari(z)))
    if p.get("kaynaklar"):
        parcalar.append("Kaynaklar\n" + "\n".join(f"- {k}" for k in p["kaynaklar"]))
    if p.get("gorsel_atif"):
        parcalar.append("Görseller ve ses\n" + "\n".join(f"- {k}" for k in p["gorsel_atif"]))
    parcalar.append("Seslendirme yapay zekâ ile üretilmiştir (Cartesia). Karakterler canlandırmadır.")
    et = [str(e).replace(" ", "") for e in (p.get("etiketler") or [])][:3]
    if et:
        parcalar.append(" ".join(f"#{e}" for e in et))
    return "\n\n".join(parcalar)


def etiket_metni(v: Video) -> str:
    return ", ".join(str(e) for e in (v.paket.get("etiketler") or []))


def uyarilar(v: Video, z: Zaman) -> list[str]:
    u = bolum_denetle(bolum_damgalari(z), z.sure)
    for b in [v.baslik] + list(v.paket.get("baslik_alternatifleri") or []):
        if len(b) > BASLIK_MAX:
            u.append(f"başlık {len(b)} karakter (> {BASLIK_MAX}): {b[:50]}...")
    if len(etiket_metni(v)) > ETIKET_MAX:
        u.append(f"etiketler {len(etiket_metni(v))} karakter (> {ETIKET_MAX})")
    a = aciklama(v, z)
    if len(a) > ACIKLAMA_MAX:
        u.append(f"açıklama {len(a)} karakter (> {ACIKLAMA_MAX})")
    if "<" in a or ">" in a:
        u.append("açıklamada < ya da > var: YouTube kabul etmez")
    if z.sure < 25:
        u.append("video 25 sn'den kısa: bitiş ekranı eklenemez")
    if any(st.tahmini for s in z.sahneler for st in s.satirlar):
        u.append("bazı satır süreleri TAHMİNİ (seslendirme yok): zaman damgaları kesin değil")
    return u


def yaz(v: Video, z: Zaman, klasor: Path, mp4: Path | None, srt: Path | None, kucukresimler: list[Path],
        olcum: dict | None = None) -> Path:
    p = v.paket
    damgalar = bolum_damgalari(z)
    basliklar = [v.baslik] + [b for b in (p.get("baslik_alternatifleri") or []) if b != v.baslik]
    L = [f"# {v.baslik} — uzun video paketi", ""]
    L += [f"Süre: **{zaman_str(z.sure)}** ({z.sure:.1f} sn), {len(z.sahneler)} sahne, {len(v.bolumler)} bölüm."]
    if mp4:
        L.append(f"Video: `{mp4.name}` (1920x1080, 30 fps, H.264 + AAC 48 kHz)")
    if olcum:
        L.append(f"Ölçüm: {olcum.get('son_lufs')} LUFS, tepe {olcum.get('son_tepe_dbtp')} dBTP; "
                 f"senkron: {'tamam' if olcum.get('senkron_ok') else 'KONTROL ET'}")
    u = uyarilar(v, z)
    if u:
        L += ["", "**Uyarılar**", ""] + [f"- ⚠ {x}" for x in u]
    L += ["", "## Başlık alternatifleri", ""]
    L += [f"{i}. {b}  ({len(b)} karakter)" for i, b in enumerate(basliklar, 1)]
    L += ["", "## Açıklama (kopyala-yapıştır)", "", "```", aciklama(v, z), "```"]
    L += ["", "## Bölüm zaman damgaları", "", "```", bolum_metni(damgalar), "```"]
    L += ["", "## Etiketler", "", "```", etiket_metni(v), "```", f"({len(etiket_metni(v))}/{ETIKET_MAX} karakter)"]
    if p.get("sabit_yorum"):
        L += ["", "## Sabit yorum", "", "```", str(p["sabit_yorum"]).strip(), "```"]
    if kucukresimler:
        L += ["", "## Küçük resimler", ""] + [f"- `{k.name}`" for k in kucukresimler]
        L.append("- YouTube Studio > Küçük resim > **Test ve karşılaştır**: hepsini yükle, kazananı YouTube seçer.")
    if srt:
        L += ["", "## Altyazı", "", f"`{srt.name}` (Türkçe, zamanlamalı): Studio > Altyazılar > Türkçe > "
              "Altyazı ekle > Dosya yükle > *Zamanlamalı*."]
    L += ["", "## Yükleme kontrol listesi", ""]
    L += [
        "- [ ] Video yüklendi; başlık alternatiflerden seçildi (ilk 60 karakter arama sonucunda görünür)",
        "- [ ] Açıklama yapıştırıldı; bölümler oynatıcıda görünüyor (ilk damga 0:00, en az 3 bölüm, her biri >= 10 sn)",
        "- [ ] Küçük resim yüklendi; 'Test ve karşılaştır' ile diğer varyantlar eklendi",
        "- [ ] Altyazı (.srt) yüklendi, dil: Türkçe",
        "- [ ] Etiketler yapıştırıldı; kategori: Eğitim (ya da Kişiler ve Bloglar), dil: Türkçe",
        "- [ ] Kitle: 'Çocuklara özel değil'",
        "- [ ] Bitiş ekranı (son 20 sn): 'En son yüklenen' ya da ilgili video + Abone ol",
        "- [ ] **Shorts > İlgili video**: kısa sürümün (Short) Studio düzenleme sayfasında 'İlgili video' olarak "
        "BU uzun video seçildi (Short izleyicisini uzun videoya taşır)",
        "- [ ] Short'un açıklamasına 'Uzun hali kanalda' satırı eklendi; bu açıklamadaki [Short bağlantısı] dolduruldu",
        "- [ ] Sabit yorum yazıldı ve sabitlendi",
        "- [ ] 'Değiştirilmiş ya da yapay içerik' sorusu: gerçekçi bir kişi/olay taklidi yok; yapay zekâ "
        "seslendirmesi anlatım içindir (gerekirse 'Evet' seç)",
        "- [ ] Para kazanma: video 8 dk'yı geçiyorsa ara reklam yerleri (bölüm geçişlerine yakın) kontrol edildi",
        "- [ ] Görsel atıfları açıklamada (CC BY-SA görseller atıf ister); telifli görsellerin kullanım kararı verildi",
    ]
    if p.get("short_baglanti"):
        L += ["", f"Short: {p['short_baglanti']}"]
    klasor.mkdir(parents=True, exist_ok=True)
    out = klasor / "paylasim.md"
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    return out
