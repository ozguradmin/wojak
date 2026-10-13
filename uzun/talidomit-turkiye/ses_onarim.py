"""Önbellekteki TTS çekimlerinden kelime/hece düzeyinde ses onarımı (yeni Cartesia isteği YOK).

13.10.2026: Cartesia kotası bitti (HTTP 402 quota_exceeded; 3. hakem turunun başında yeniden denendi, yine 402).
Hakemlerin istediği yeni seslendirmeler alınamadığı için bu betik yalnız `out/talidomit-turkiye-uzun/ses/` içindeki
mevcut çekimlerle çalışır: onarılmış sesi `onarim_<ad>.wav` olarak yazar ve satırın önbellek anahtarını manifest
`secim`ine bağlar (motor o dosyayı çalar). Kesimler sessizlikte ya da kapantı (stop) boşluğunda, kısa eşit güçlü
çapraz geçişle; her sonuç Whisper ile (ipucusuz, iki farklı çözümleme) yeniden dinlenir ve manifeste yazılır.

Satırlar YERİNE göre değil METNİNE göre bulunur (sahne eklenip çıkınca "bölüm 5, sahne 2" kayıyordu). Metni
kısaltılan satırlarda (`eski`) kaynak çekim, satırın eski metninin önbellek anahtarından bulunur; yeni metnin
anahtarı onarım dosyasına bağlanır.

    python uzun/talidomit-turkiye/ses_onarim.py          # onar + dinle
    python uzun/talidomit-turkiye/ses_onarim.py --geri   # onarımları kaldır (secim eski çekimlere döner)

Onarımlar
- fda:       "…ilaç kurumu FDA, yeni bir uzmanı…": "FEFTA" duyulan çekim yerine virgüldeki sessizlikten kesilip "FDA"yı
             en net söyleyen 0. deneme + Kelsey'nin adını en iyi söyleyen 2. deneme (2. tur).
- recete:    "Reçetesiz bir uyku…": TTS'in başı yutuluyordu ("ve çetesiz"); "Re" hecesi aynı sözcüğü cümle başında
             söyleyen SA.4 çekiminden, "ç" kapantısında kesilip eklenir (2. tur).
- lenz:      "Lenz'i iftirayla": belirtme eki ile "iftira"nın i'si tek ünlüde birleşiyordu ("Lens iftirayla");
             ünlü ikilenir, araya 30 ms gırtlak boşluğu girer ("Lentsi | iftirayla") (2. tur).
- cuzzam1/2/3: "cüzzam" üç satırda "cüzdan / cüzlam / cüzağımın" duyuluyordu (3. tur, iki hakem). TTS ikiz zz'yi
             ~65-85 ms'lik zayıf tek bir z olarak söylüyor; z bölümü taneli örtüşmeli toplamla 2-2,2 kat uzatılır
             (perde değişmez; Türkçede ikiz ünsüz tekinin ~2 katı). "cüzzamın"da ünlüden sonra araya giren "ğı"
             hecesi (75 ms) de çıkarılır. Parametreler Whisper taramasıyla seçildi: komşu ayarlarda da "cüzzam".
- yil1962:   "1962 yazında hikâye…": "1962" "1960, iki" duyuluyordu (3. tur). Satır "Hikâye gazetelere düşüyor."
             olarak kesilir; tarih ekranda ("7 AĞUSTOS 1962 · BEYAZ SARAY").
- bilanco:   "Bilanço ağır. Dünyada…": "Blancho" duyuluyordu; ilk cümle sessizlikten atılır.
- ama_*:     dil hakemi 13 "Ama" ile başlayan cümlenin yarısını istiyordu: 6 cümlenin başındaki "Ama" kapantı
             boşluğundan atılır (1961 baharında, Arada bir boşluk, Asıl soru, Kaçak getirilen, Geri dönüşün, Bu kadarını).
- ustelik:   "Üstelik bu hikâye…": mantıksız bağlaç atılır ("Bu hikâye 1961'de bitmedi.").
- hiz_*:     hızlı okunan satırlar (dil hakemi: 8,4-9,3 hece/sn) rubberband ile perde/formant korunarak yavaşlatılır.
Kota yenilenince bu satırlar senaryo metniyle yeniden seslendirilmeli (uretici_raporu.md, "Kota gelince").
"""

from __future__ import annotations

import dataclasses
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

KOK = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(KOK))

from wojak.uzun import spec, tts  # noqa: E402

V = spec.yukle(Path(__file__).resolve().parent)
SK = tts.ses_klasoru(V)
HOP = 0.005


# ------------------------------------------------------------------------------------------------ satır / çekim
def satir(parca: str):
    """Görünen metninde `parca` geçen TEK satır."""
    bul = [(s, i, st) for s, i, st in tts._yer(V) if parca in st.altyazi]
    if len(bul) != 1:
        raise KeyError(f"'{parca}': {len(bul)} satır")
    return bul[0][2]


def yer(st) -> str:
    for s, i, x in tts._yer(V):
        if x is st:
            return f"{s.yer}, satır {i + 1}"
    return "?"


def eski_hali(st, eski: str | None):
    """Metni kısaltılmış satırın eski (seslendirilmiş) hâli: kaynak çekim bu metnin anahtarından bulunur."""
    return dataclasses.replace(st, metin=eski, tts=None) if eski else st


def cekim(st, deneme: int) -> tuple[str, Path]:
    k = tts.anahtar(V.model, V.ses_id(st.ses), V.transkript(st), st.hiz, st.duygu, V.dil, deneme)
    return k, SK / f"{k}.wav"


def secili(st) -> Path:
    k0, p0 = cekim(st, 0)
    man = tts._manifest(V)
    alt = man.get("secim", {}).get(k0)
    if alt and not alt.startswith("onarim_") and (SK / f"{alt}.wav").exists():
        return SK / f"{alt}.wav"
    if alt and alt.startswith("onarim_"):   # onarımdan önceki seçim manifestte saklı
        eski = man.get("onarim_oncesi", {}).get(k0)
        if eski and (SK / f"{eski}.wav").exists():
            return SK / f"{eski}.wav"
    return p0


# ------------------------------------------------------------------------------------------------ sinyal araçları
def zarf(x: np.ndarray, sr: int) -> np.ndarray:
    h = int(HOP * sr)
    n = len(x) // h
    return 20 * np.log10(np.sqrt((x[: n * h].reshape(n, h) ** 2).mean(1)) + 1e-9)


def en_dusuk(x, sr, a, b, yumusak: int = 1) -> float:
    """[a, b] sn aralığında zarfın (yumusak pencere ortalamalı) en düşük olduğu an (sn)."""
    z = zarf(x, sr)
    if yumusak > 1:
        z = np.convolve(z, np.ones(yumusak) / yumusak, mode="same")
    i0, i1 = int(a / HOP), int(b / HOP)
    return (i0 + int(np.argmin(z[i0:i1]))) * HOP + HOP / 2


def ilk_ustu(x, sr, a, b, esik=-45.0) -> float:
    z = zarf(x, sr)
    i0, i1 = int(a / HOP), int(b / HOP)
    idx = np.where(z[i0:i1] > esik)[0]
    return (i0 + int(idx[0])) * HOP if len(idx) else a


def son_ustu(x, sr, a, b, esik=-45.0) -> float:
    z = zarf(x, sr)
    i0, i1 = int(a / HOP), int(b / HOP)
    idx = np.where(z[i0:i1] > esik)[0]
    return (i0 + int(idx[-1]) + 1) * HOP if len(idx) else b


def ekle(a: np.ndarray, b: np.ndarray, sr: int, xf: float = 0.012) -> np.ndarray:
    """a'nın sonu ile b'nin başı eşit güçlü çapraz geçişle (xf sn) birleşir."""
    n = int(xf * sr)
    if n < 2 or len(a) < n or len(b) < n:
        return np.concatenate([a, b])
    q = np.linspace(0, 1, n, dtype=np.float32)
    orta = a[-n:] * np.cos(q * np.pi / 2) + b[:n] * np.sin(q * np.pi / 2)
    return np.concatenate([a[:-n], orta, b[n:]]).astype(np.float32)


def rms(x):
    return float(np.sqrt((x.astype(np.float64) ** 2).mean() + 1e-12))


def bastan_kes(x, sr, t, fade=0.008):
    """t'den önceki her şeyi atar (t bir kapantı/sessizlik çukurunda), kısa yumuşak giriş."""
    y = x[int(t * sr):].copy()
    n = int(fade * sr)
    y[:n] *= np.linspace(0, 1, n, dtype=np.float32)
    return y


def aradan_kes(x, sr, a, b, xf=0.008):
    """[a, b] aralığını çıkarır (iki uç sessizlikte/kapantıda)."""
    return ekle(x[: int(a * sr)], x[int(b * sr):], sr, xf)


def uzat(seg, sr, oran, tane=0.024, kaydir=0.008, seed=0):
    """Kısa bir parçayı (sürtünmeli ünsüz) taneli örtüşmeli toplamla `oran` kat uzatır (perde değişmez)."""
    n = len(seg)
    L = int(round(n * oran))
    g = min(int(tane * sr), n)
    h = int(kaydir * sr)
    w = np.hanning(g).astype(np.float32)
    out = np.zeros(L + g, np.float32)
    nrm = np.zeros(L + g, np.float32)
    rng = np.random.default_rng(seed)
    for o in range(0, L, h):
        src = int(o / max(L - 1, 1) * (n - g))
        src = int(np.clip(src + rng.integers(-h // 2, h // 2 + 1), 0, n - g))
        out[o:o + g] += seg[src:src + g] * w
        nrm[o:o + g] += w
    nrm[nrm < 1e-3] = 1
    return (out / nrm)[:L]


def degistir(x, sr, a, b, yeni, xf=0.006):
    """x[a:b] (sn) yerine `yeni` koyar, iki uçta kısa eşit güçlü çapraz geçiş."""
    i, j = int(a * sr), int(b * sr)
    n = int(xf * sr)
    sol, sag = x[:i + n], x[j - n:]
    q = np.linspace(0, 1, n, dtype=np.float32)
    yeni = yeni.astype(np.float32).copy()
    bas = sol[-n:] * np.cos(q * np.pi / 2) + yeni[:n] * np.sin(q * np.pi / 2)
    son = yeni[-n:] * np.cos(q * np.pi / 2) + sag[:n] * np.sin(q * np.pi / 2)
    return np.concatenate([sol[:-n], bas, yeni[n:-n], son, sag[n:]]).astype(np.float32)


def z_uzat(x, sr, a, b, oran):
    return degistir(x, sr, a, b, uzat(x[int(a * sr):int(b * sr)], sr, oran))


def sessizlik_kisalt(x, sr, en_fazla=0.5, esik=-42.0):
    """İç sessizliklerden en_fazla sn'yi aşanları kısaltır (ortasından)."""
    z = zarf(x, sr)
    sus = z < esik
    out, i, n = [], 0, len(z)
    kes = []
    while i < n:
        if sus[i]:
            j = i
            while j < n and sus[j]:
                j += 1
            if i > 0 and j < n and (j - i) * HOP > en_fazla:
                fazla = (j - i) * HOP - en_fazla
                m = (i + j) / 2 * HOP
                kes.append((m - fazla / 2, m + fazla / 2))
            i = j
        else:
            i += 1
    y = x
    for a, b in reversed(kes):
        y = aradan_kes(y, sr, a, b, 0.01)
    return y, [(round(a, 3), round(b, 3)) for a, b in kes]


def yavaslat(x, sr, tempo):
    """rubberband (ffmpeg) ile yavaşlatma: perde ve formant korunur."""
    with tempfile.TemporaryDirectory() as d:
        g, c = Path(d) / "g.wav", Path(d) / "c.wav"
        tts.wav_yaz(g, x, sr)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(g), "-af",
                        f"rubberband=tempo={tempo}:pitchq=quality:formant=preserved:detector=soft:smoothing=on",
                        "-ar", str(sr), "-ac", "1", "-c:a", "pcm_s16le", str(c)], check=True)
        y, _ = tts.wav_oku(c)
    return y


# ------------------------------------------------------------------------------------------------ 2. tur onarımları
def onar_fda(st):
    a, sr = tts.wav_oku(cekim(st, 0)[1])     # "FDA" en net (Whisper: FTA)
    b, _ = tts.wav_oku(cekim(st, 2)[1])      # Kelsey'nin adı en net (bugüne dek seçili çekim)
    a_son = son_ustu(a, sr, 2.6, 3.3)
    b_bas = ilk_ustu(b, sr, 3.3, 3.7)
    ka = min(a_son + 0.17, len(a) / sr)
    kb = max(b_bas - 0.12, 0.0)
    return ekle(a[: int(ka * sr)], b[int(kb * sr):], sr, 0.03), sr, {"a_kesim": round(ka, 3), "b_kesim": round(kb, 3)}


def onar_recete(st):
    kaynak = satir("1957. Batı Almanya. Reçetesiz satılan")
    t, sr = tts.wav_oku(secili(st))
    k, sr2 = tts.wav_oku(secili(kaynak))
    assert sr == sr2
    sus = en_dusuk(k, sr, 2.3, 2.9)
    k_bas = ilk_ustu(k, sr, sus, sus + 0.5)
    k_kap = en_dusuk(k, sr, k_bas + 0.06, k_bas + 0.13, yumusak=3)
    t_bas = ilk_ustu(t, sr, 0.0, 0.2)
    t_kap = en_dusuk(t, sr, t_bas + 0.07, t_bas + 0.15, yumusak=3)
    re = k[max(0, int((k_bas - 0.04) * sr)): int(k_kap * sr)].copy()
    g = rms(t[int(t_bas * sr): int(t_kap * sr)]) / max(rms(re), 1e-6)
    re *= float(np.clip(g, 0.5, 2.0))
    fi = int(0.006 * sr)
    re[:fi] *= np.linspace(0, 1, fi, dtype=np.float32)
    return ekle(re, t[int(t_kap * sr):], sr, 0.012), sr, {"kaynak_re": [round(k_bas, 3), round(k_kap, 3)],
                                                           "hedef_kap": round(t_kap, 3), "kazanc": round(float(g), 2)}


def onar_lenz(st):
    x, sr = tts.wav_oku(secili(st))
    z = zarf(x, sr)
    i0, i1 = int(1.66 / HOP), int(1.88 / HOP)
    ust = z[i0:i1] > -28
    en, bas, cur = 0, None, None
    for j, u in enumerate(ust):
        if u and cur is None:
            cur = j
        if (not u or j == len(ust) - 1) and cur is not None:
            L = (j if not u else j + 1) - cur
            if L > en:
                en, bas = L, cur
            cur = None
    v0, v1 = (i0 + bas) * HOP, (i0 + bas + en) * HOP
    vm = (v0 + v1) / 2
    on = x[: int(vm * sr)].copy()
    arka = x[int(v0 * sr):].copy()
    fo, fi = int(0.012 * sr), int(0.010 * sr)
    on[-fo:] *= np.linspace(1, 0, fo, dtype=np.float32)
    arka[:fi] *= np.linspace(0, 1, fi, dtype=np.float32)
    bosluk = np.zeros(int(0.03 * sr), np.float32)
    return np.concatenate([on, bosluk, arka]).astype(np.float32), sr, {"unlu": [round(v0, 3), round(v1, 3)]}


# ------------------------------------------------------------------------------------------------ 3. tur onarımları
def onar_cuzzam1(st):
    """B6.1: 0. deneme ("cüzdan"), z [4.10, 4.18] x2,2 -> "cüzzam"; "Kudüs."tan sonraki uzun sessizlik 0,5 sn'ye."""
    x, sr = tts.wav_oku(cekim(st, 0)[1])
    y = z_uzat(x, sr, 4.10, 4.18, 2.2)
    y, kes = sessizlik_kisalt(y, sr, 0.5)
    return y, sr, {"kaynak": "deneme 0", "z": [4.10, 4.18], "oran": 2.2, "sessizlik": kes}


def onar_cuzzam2(st):
    """B6.2: 2. deneme ("cüzağımın"), araya giren hece [2.29, 2.365] çıkar, z [2.15, 2.235] x2 -> "cüzzamın"."""
    x, sr = tts.wav_oku(cekim(st, 2)[1])
    y = aradan_kes(x, sr, 2.29, 2.365)
    y = z_uzat(y, sr, 2.15, 2.235, 2.0)
    return y, sr, {"kaynak": "deneme 2", "cikan": [2.29, 2.365], "z": [2.15, 2.235], "oran": 2.0}


def onar_cuzzam3(st):
    """B6.3 satır 2: tek çekim ("cüzdan"), z [0.725, 0.82] x2 -> "cüzzam" (komşu ayarlar da: r3 z_tara2)."""
    x, sr = tts.wav_oku(cekim(st, 0)[1])
    return z_uzat(x, sr, 0.725, 0.82, 2.0), sr, {"z": [0.725, 0.82], "oran": 2.0}


def bas_kes(eski, t, tempo=None):
    def fn(st):
        x, sr = tts.wav_oku(secili(eski_hali(st, eski)))
        y = bastan_kes(x, sr, t)
        bilgi = {"eski": eski, "kesim": t}
        if tempo:
            y = yavaslat(y, sr, tempo)
            bilgi["tempo"] = tempo
        return y, sr, bilgi
    return fn


def orta_kes(eski, a, b):
    def fn(st):
        x, sr = tts.wav_oku(secili(eski_hali(st, eski)))
        return aradan_kes(x, sr, a, b), sr, {"eski": eski, "cikan": [a, b]}
    return fn


def yavas(tempo):
    def fn(st):
        x, sr = tts.wav_oku(secili(st))
        return yavaslat(x, sr, tempo), sr, {"tempo": tempo}
    return fn


# ad -> (satırın ŞİMDİKİ metninden bir parça, işlev). Kesim noktaları zarf çukurlarında; her biri Whisper ile
# (ipucusuz) dinlenerek seçildi (scratchpad r3/kes_tara.py).
ONARIMLAR = {
    "fda": ("ilaç kurumu FDA", onar_fda),
    "recete": ("Reçetesiz bir uyku ve sakinleştirici", onar_recete),
    "lenz": ("Lenz'i iftirayla", onar_lenz),
    "cuzzam1": ("ağır bir cüzzam hastası", onar_cuzzam1),
    "cuzzam2": ("önce cüzzamın bir komplikasyonu", onar_cuzzam2),
    "cuzzam3": ("cüzzam tedavisinde kullanıldığı", onar_cuzzam3),
    "yil1962": ("Hikâye gazetelere düşüyor.", bas_kes("1962 yazında hikâye gazetelere düşüyor.", 1.788)),
    "bilanco": ("Dünyada on binden fazla bebek", bas_kes("Bilanço ağır. Dünyada on binden fazla bebek etkileniyor. "
                                                         "Bazı tahminler yirmi bini buluyor.", 1.177)),
    "ama_1961": ("1961 baharında vakalar", bas_kes("Ama 1961 baharında vakalar bini aşıyor.", 0.278)),
    "ama_arada": ("Arada bir boşluk var:", bas_kes("Ama arada bir boşluk var:", 0.238)),
    "ama_asil": ("Asıl soru hiç araştırılmamış", bas_kes("Ama asıl soru hiç araştırılmamış: Hamile bir kadın bu "
                                                         "ilacı alırsa, karnındaki bebeğe ne olur?", 0.46)),
    "ama_kacak": ("Kaçak getirilen ilaçla", orta_kes("Doğu Almanya da ilaca ruhsat vermemişti. Ama kaçak getirilen "
                                                    "ilaçla orada da vakalar görüldü.", 2.79, 3.125)),
    "ama_geri": ("Geri dönüşün bir bedeli", bas_kes("Ama geri dönüşün bir bedeli de oldu.", 0.273, tempo=0.92)),
    "ama_bu": ("Bu kadarını anlamak bile", bas_kes("Ama bu kadarını anlamak bile altmış yıldan uzun sürdü.", 0.238)),
    "ustelik": ("Bu hikâye 1961'de bitmedi.", bas_kes("Üstelik bu hikâye 1961'de bitmedi.", 0.448)),
    "hiz_pano": ("Şimdi elimizdekilere bakalım.", yavas(0.87)),
    "hiz_amerika": ("önce Amerika'ya bakmamız gerek", yavas(0.92)),
    "hiz_ingiltere": ("İngiltere'deki bir reklam ise", yavas(0.92)),
    "hiz_kapanis": ("Bir sonraki unutulmuş hikâyede", yavas(0.92)),
}


def dinle(yol: Path) -> tuple[str, str]:
    """İki çözümleme: ışın 5 (QA ile aynı) ve açgözlü (ışın 1); ikisi de ipucusuz."""
    a = tts.yaziya_dok(yol, V.dil)
    segs, _ = tts._model().transcribe(tts.wav_16k(yol), language=V.dil, beam_size=1, vad_filter=False,
                                      condition_on_previous_text=False)
    b = " ".join(s.text.strip() for s in segs).strip()
    return a, b


def main():
    man = tts._manifest(V)
    secim = man.setdefault("secim", {})
    once = man.setdefault("onarim_oncesi", {})
    secilen = [a for a in sys.argv[1:] if not a.startswith("--")] or list(ONARIMLAR)
    if "--geri" in sys.argv:
        for ad in secilen:
            k0, _ = cekim(satir(ONARIMLAR[ad][0]), 0)
            if k0 in once:
                if once[k0] == k0:
                    secim.pop(k0, None)
                else:
                    secim[k0] = once[k0]
                once.pop(k0)
        tts.manifest_yolu(V).write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding="utf-8")
        print("onarımlar kaldırıldı:", ", ".join(secilen))
        return
    rapor = man.get("onarim", {})
    for ad in secilen:
        parca, fn = ONARIMLAR[ad]
        st = satir(parca)
        k0, _ = cekim(st, 0)
        if k0 not in once:
            once[k0] = secim.get(k0, k0)
        y, sr, bilgi = fn(st)
        yol = SK / f"onarim_{ad}.wav"
        tts.wav_yaz(yol, y, sr)
        secim[k0] = f"onarim_{ad}"
        d5, d1 = dinle(yol)
        rapor[ad] = {"yer": yer(st), "metin": st.altyazi, "duyulan": d5, "duyulan_isin1": d1,
                     "sure": round(len(y) / sr, 3), **bilgi}
        print(f"{ad:13} {yer(st)}: {len(y) / sr:.2f} sn\n   metin:   {st.altyazi}\n   duyulan: {d5}\n   ışın 1:  {d1}",
              flush=True)
    man["onarim"] = rapor
    tts.manifest_yolu(V).write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
