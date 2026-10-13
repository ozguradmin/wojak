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
KISA_URL_PAYI = 45   # "[Short bağlantısı]" yerine gelecek https://youtube.com/shorts/... bağlantısının ek baytı


def yukari(t: float) -> int:
    """Saniyeyi yukarı yuvarlar (kayan nokta payıyla: 181.0000001 -> 181)."""
    return int(math.ceil(t - 1e-3))


def bolum_damgalari(z: Zaman) -> list[tuple[int, str]]:
    """(saniye, ad): bölümün ilk sahnesinin (kart dahil) başı, YUKARI yuvarlanmış; ilki her zaman 0.

    Yukarı: damga bölüm kartının içine düşer. Aşağı yuvarlanınca (talidomit-turkiye 3. hakem turu) 3:00.9'da başlayan
    kartın damgası 3:00 oluyor, bölüme tıklayan izleyici önceki bölümün son cümlesinin ortasına düşüyordu.

    Kartsız bölümde (ilk sahnesi bölüm kartı değil) AŞAĞI yuvarlanır: yukarı yuvarlanınca ilk kelime kesiliyordu
    (talidomit-turkiye 4. tur, teknik hakem: "Kapanış" 9:36'ya düştü, konuşma 9:35,53'te başlıyordu; "Peki" kırpıldı).
    Aradaki kesir önceki sahnenin son sessiz payına düşer."""
    import math
    out = []
    kartli = [b.sahneler[0].tip == "bolum_karti" for b in z.video.bolumler if b.sahneler]
    for (ad, t), k in zip(z.bolum_baslari(), kartli):
        s = 0 if not out else (yukari(t) if k else int(math.floor(t + 1e-6)))
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
    nb = len(a.encode("utf-8")) + (0 if v.paket.get("short_url") else KISA_URL_PAYI)
    if nb > ACIKLAMA_MAX:   # YouTube API bayt sayar (Studio karakter): Türkçe harfler 2 bayt
        u.append(f"açıklama {len(a.encode('utf-8'))} bayt (+ Short bağlantısı ~{KISA_URL_PAYI}): API sınırı "
                 f"{ACIKLAMA_MAX} bayt; kısalt")
    if "<" in a or ">" in a:
        u.append("açıklamada < ya da > var: YouTube kabul etmez")
    if z.sure < 25:
        u.append("video 25 sn'den kısa: bitiş ekranı eklenemez")
    u += bitis_denetle(z)
    if any(st.tahmini for s in z.sahneler for st in s.satirlar):
        u.append("bazı satır süreleri TAHMİNİ (seslendirme yok): zaman damgaları kesin değil")
    return u


def bitis_denetle(z: Zaman) -> list[str]:
    """YouTube bitiş ekranı: son 5-20 sn'ye konabilir; `bitis` sahnesi videonun son sahnesi olmalı."""
    u = []
    bitisler = [s for s in z.sahneler if s.tip == "bitis"]
    if not bitisler:
        return u
    if z.sahneler[-1].tip != "bitis":
        u.append("bitis sahnesi videonun son sahnesi olmalı (YouTube bitiş ekranı son 5-20 sn'de)")
    if len(bitisler) > 1:
        u.append(f"{len(bitisler)} bitis sahnesi var: bir tane yeter")
    s = bitisler[-1]
    if not 5.0 <= s.sure_hesap <= 20.0 + 1e-6:
        u.append(f"bitis sahnesi {s.sure_hesap:.1f} sn: YouTube bitiş ekranı 5-20 sn (önerilen 15-20)")
    return u


def ara_reklam_yerleri(v: Video, z: Zaman) -> list[str]:
    """paket.ara_reklam: sayı = o numaralı bölüm kartının İÇİNDE ilk tam saniye (zaman çizelgesinden; süre değişince
    kayar), metin olduğu gibi. Studio ara reklamı tam saniyeye koyar: kartın başı aşağı yuvarlanınca reklam önceki
    cümleyi kesiyordu (talidomit-turkiye 3. hakem turu: kart 5:49.97, reklam 5:49 'unutul-du'nun ortasında)."""
    out = []
    for x in v.paket.get("ara_reklam") or []:
        if isinstance(x, int):
            b = next((b for b in v.bolumler if b.numara == x), None)
            if b and b.sahneler:
                k = b.sahneler[0]
                t0 = z.sahne_basi(k)
                t1 = t0 + k.sure_hesap
                s = yukari(t0)
                if s < t1:
                    out.append(f"{zaman_str(s)} ({x}. bölüm kartı: {zaman_str(t0, ms=True)}–{zaman_str(t1, ms=True)})")
                else:
                    out.append(f"{zaman_str(t0, ms=True)} ({x}. bölüm kartı; kartta tam saniye yok: kartı uzat)")
                continue
        out.append(str(x))
    return out


def dinlenecekler(v: Video, z: Zaman) -> list[str]:
    """paket.dinle: [{ara: 'satırda geçen metin', not: '...'}] -> 'm:ss «satır» — not' (satırın başı zaman
    çizelgesinden; süre değişince kayar). Bulunamayan arama da yazılır (elle bakılsın)."""
    out = []   # (sıralama anı, satır): 4. tur: hesap sahibi videoyu baştan sona dinlerken sırayla gitsin
    satirlar = z.satirlar()
    for d in v.paket.get("dinle") or []:
        d = d if isinstance(d, dict) else {"ara": str(d)}
        ara = str(d.get("ara", "")).strip()
        bul = [sz for sz in satirlar if ara and ara.casefold() in sz.satir.altyazi.casefold()]
        notu = f" — {d['not']}" if d.get("not") else ""
        if not bul:
            out.append((-1.0, f"'{ara}' (satır bulunamadı){notu}"))
            continue
        for sz in bul:
            m = sz.satir.altyazi
            i = m.casefold().find(ara.casefold())
            a, b = max(0, i - 28), min(len(m), i + len(ara) + 28)
            if a > 0:                       # kelime sınırından başla/bitir (yarım kelime gösterme)
                a = m.find(" ", a) + 1 if m.find(" ", a) != -1 and m.find(" ", a) < i else i
            if b < len(m):
                j = m.rfind(" ", i + len(ara), b)
                b = j if j != -1 else b
            parca = ("…" if a else "") + m[a:b] + ("…" if b < len(m) else "")
            out.append((sz.bas, f"{zaman_str(sz.bas)} «{parca}»{notu}"))
    return [x for _, x in sorted(out, key=lambda x: x[0])]


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
        lufs = olcum.get("mp4_lufs", olcum.get("son_lufs"))
        tepe = olcum.get("mp4_tepe_dbtp", olcum.get("son_tepe_dbtp"))
        L.append(f"Ölçüm (mp4): {lufs} LUFS, tepe {tepe} dBTP; "
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
        (f"- [ ] Bitiş ekranı (son ~{z.sure - yukari(z.sahne_basi([s for s in z.sahneler if s.tip == 'bitis'][-1])):.0f} sn)"
         if any(s.tip == "bitis" for s in z.sahneler) else "- [ ] Bitiş ekranı (son 5-20 sn)")
        + ": 'En son yüklenen' ya da ilgili video + Abone ol"
        + (f" — öğeleri **{zaman_str(yukari(z.sahne_basi([s for s in z.sahneler if s.tip == 'bitis'][-1])))}**'ten "
           "itibaren videodaki iki boş kutunun İKİSİNİ DE ve dairenin üstüne yerleştir, kutuyu tam örtecek kadar "
           "büyüt (boş kalan kutu yer tutucu gibi görünür; daha erken başlarsa kapanış sahnesinin üstüne biner)"
           if any(s.tip == "bitis" for s in z.sahneler) else ""),
        "- [ ] **Shorts > İlgili video**: kısa sürümün (Short) Studio düzenleme sayfasında 'İlgili video' olarak "
        "BU uzun video seçildi (Short izleyicisini uzun videoya taşır)",
        "- [ ] Short'un açıklamasına 'Uzun hali kanalda' satırı eklendi; bu açıklamadaki [Short bağlantısı] dolduruldu",
        "- [ ] Short henüz yayımlanmadıysa açıklamadaki 'Kısa hali (Short): [Short bağlantısı]' satırı silindi"
        if not p.get("short_url") else "- [ ] Short bağlantısı açıklamada doğru",
        "- [ ] Sabit yorum yazıldı ve sabitlendi",
        "- [ ] 'Değiştirilmiş ya da yapay içerik' sorusu: "
        + str(p.get("yapay_icerik") or "gerçekçi bir kişi/olay taklidi yok; yapay zekâ seslendirmesi anlatım "
                                         "içindir (gerekirse 'Evet' seç)"),
        "- [ ] Para kazanma: video 8 dk'yı geçiyorsa ara reklam yerleri "
        + (f"elle yerleştirildi: **{', '.join(ara_reklam_yerleri(v, z))}** (otomatik ara reklam kapalı)"
           if p.get("ara_reklam") else "(bölüm geçişlerine yakın) kontrol edildi"),
        "- [ ] Görsel atıfları açıklamada (CC BY-SA görseller atıf ister); telif kararları verildi (aşağıdaki "
        "'Telif notu' bölümü)" if p.get("telif_notu") else
        "- [ ] Görsel atıfları açıklamada (CC BY-SA görseller atıf ister); telifli görsellerin kullanım kararı verildi",
    ]
    dn = dinlenecekler(v, z)
    if dn:
        L.append("- [ ] **Yayından önce kulakla dinle** (yapay zekâ seslendirmesi; satırın başladığı an). Kabul "
                 "edilemeyen varsa yayımlama, bildir:")
        L += [f"  - {x}" for x in dn]
    L += [f"- [ ] {x}" for x in (p.get("ek_maddeler") or [])]
    if p.get("telif_notu"):
        tn = p["telif_notu"]
        L += ["", "## Telif notu / lisans kararları (hesap sahibi karar verir)", ""]
        if isinstance(tn, list):   # liste içindeki liste: bir önceki maddenin alt maddeleri (5. tur)
            for x in tn:
                L += [f"  - {y}" for y in x] if isinstance(x, list) else [f"- {x}"]
        else:
            L += [str(tn).strip()]
    if p.get("short_baglanti"):
        L += ["", f"Short: {p['short_baglanti']}"]
    klasor.mkdir(parents=True, exist_ok=True)
    out = klasor / "paylasim.md"
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    return out
