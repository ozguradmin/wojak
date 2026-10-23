"""Ses: anlatım zaman çizelgesi + müzik altlığı (yan zincirli kısma) + efektler -> -14 LUFS / -1 dBTP.

- Anlatım: her satırın kırpılmış sesi, zaman çizelgesindeki mutlak başlangıcına örnek hassasiyetinde konur.
- Müzik: `muzik.dosya` ya da kendi sentezimiz (muzik.py, videonun süresi kadar, tohumlu). Seviye anlatımın
  ölçülen yüksekliğine göre ayarlanır: konuşma varken `seviye` (vars. -22 dB), konuşma yokken `acik`
  (vars. -15 dB). Kısma anahtarı anlatım izinin kendisidir (20 ms RMS, eşik, 0,35 sn tutma, 0,12 sn atak,
  0,7 sn bırakma) — gerçek yan zincir.
- Efektler: spesifikasyondaki `sfx` + sahne tipine göre otomatik efektler (otomatik_sfx: false ile kapanır).
- Son: iki geçişli loudnorm (ölç -> kazanç + tepe sınırlayıcı -> ölç -> doğrusal loudnorm), hedef -14 LUFS,
  -1 dBTP. Yalnız anlatım izi (stem) aynı toplam kazançla ayrıca yazılır.
"""

from __future__ import annotations

import hashlib
import json
import math
import subprocess
from functools import lru_cache
from pathlib import Path

import numpy as np

from .. import config
from . import muzik
from .sahneler import (foto_zamanlari, harita_zamanlari, karakter_zamanlari, manset_zamanlari, metin_zamanlari,
                       olaylar, rota_zamanlari, sayac_bolumleri, zc_zamanlari)
from .spec import SFX_DIR, Video
from .ust import Damga
from .zaman import Zaman, balon_olaylari, tum_sfx

SR = 48000
HEDEF_I, HEDEF_TP, HEDEF_LRA = -14.0, -1.0, 11.0
# AAC kodlaması gerçek tepeyi iki yöne de ~0,5-1 dB oynatabiliyor (talidomit-turkiye: WAV -1,5 -> mp4 -0,9 dBTP);
# teslim edilen mp4'ün de <= HEDEF_TP kalması için WAV bu pay kadar aşağıda tutulur
KODEK_PAYI = 1.0
WAV_TP = HEDEF_TP - KODEK_PAYI


@lru_cache(maxsize=64)
def _oku(yol: str, mtime: float, kanal: int) -> np.ndarray:
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", yol, "-ac", str(kanal), "-ar", str(SR),
                                   "-f", "f32le", "-"])
    x = np.frombuffer(raw, np.float32)
    return x.reshape(-1, kanal) if kanal > 1 else x


def oku(yol, kanal: int = 1) -> np.ndarray:
    p = Path(yol)
    return _oku(str(p), p.stat().st_mtime, kanal)


def wav_yaz(yol: Path, x: np.ndarray, float32: bool = False) -> Path:
    yol.parent.mkdir(parents=True, exist_ok=True)
    x = np.asarray(x, np.float32)
    ch = 1 if x.ndim == 1 else x.shape[1]
    fmt = ["-c:a", "pcm_f32le"] if float32 else ["-c:a", "pcm_s16le"]
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "f32le", "-ar", str(SR), "-ac", str(ch), "-i", "-",
                    *fmt, str(yol)], input=x.tobytes(), check=True)
    return yol


def loudnorm_olc(yol: Path, ek_filtre: str = "") -> dict:
    af = (ek_filtre + "," if ek_filtre else "") + f"loudnorm=I={HEDEF_I}:TP={WAV_TP}:LRA={HEDEF_LRA}:print_format=json"
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(yol), "-af", af, "-f", "null", "-"],
                       capture_output=True, text=True)
    e = r.stderr
    return json.loads(e[e.rindex("{"):e.rindex("}") + 1])


def ebur128(yol: Path) -> dict:
    """Son ölçüm: entegre yükseklik (LUFS), gerçek tepe (dBTP), LRA."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(yol), "-vn", "-af", "ebur128=peak=true",
                        "-f", "null", "-"], capture_output=True, text=True)
    e = r.stderr[r.stderr.rfind("Summary:"):]
    out = {}
    for ln in e.splitlines():
        ln = ln.strip()
        for k, key in (("I:", "I"), ("LRA:", "LRA"), ("Peak:", "TP")):
            if ln.startswith(k):
                try:
                    out[key] = float(ln.split()[1])
                except (IndexError, ValueError):
                    pass
    return out


# ---------------------------------------------------------------- satır seviyesi

SATIR_HEDEF_DB = -18.0   # konuşulan bölümün RMS hedefi (dBFS): sesler arası fark (Aylin ~6 dB daha yüksek) kapanır
# konuşma sürerken efekt veriyolu anlatımın en az bu kadar altında kalır (talidomit-turkiye 1. hakem turu: Türkiye
# motifi, harita pop+hit ve damgalar tam da vurgulanan kelimenin üstüne düşüp onu örtüyordu)
EFEKT_PAYI_DB = 9.0
TUS_ADIMI = 2   # daktilo metninde (metin sahnesi, yazim: daktilo) her 2 harfte bir tuş sesi
ETIKET_TUS_ADIMI = 4   # fotoğraf etiketinde her 4 harfte bir, daha alçak (6. tur, izlenme hakemi S9: anlatımın altında
                       # saniyede ~10 tık; ilk dakikada ~67 efekt)


def aktif_rms_db(x: np.ndarray) -> float:
    """Konuşulan pencerelerin (en yükseğin 30 dB altına kadar) RMS'i, dBFS."""
    hop = int(0.02 * SR)
    n = len(x) // hop
    if n < 1:
        return SATIR_HEDEF_DB
    r = np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(axis=1) + 1e-12)
    db = 20 * np.log10(r)
    akt = db > db.max() - 30
    return float(20 * np.log10(np.sqrt((r[akt] ** 2).mean())))


def satir_kazanci(x: np.ndarray) -> float:
    """Satırı ortak seviyeye getiren doğrusal kazanç (±12 dB ile sınırlı)."""
    return float(10 ** (np.clip(SATIR_HEDEF_DB - aktif_rms_db(x), -12, 12) / 20))


# 14. tur (teknik hakem M1: 11 tık): rubberband'le yavaşlatılmış onarım kliplerinin son 5-9 ms'i tam bantlı bir
# patlamaydı ve ardından sayısal sessizlik geliyordu. Motor artık (1) yerleştirdiği her anlatım klibinin sonunu
# KLIP_SONU sn'de yükseltilmiş kosinüsle söndürür (klibin kendisi ne olursa olsun basamaklı bitiş kalmaz) ve
# (2) `kontrol`/`render`'da son KUYRUK_SON sn'si önceki KUYRUK_ONCE sn'den KUYRUK_DB'den fazla yüksek klibi bildirir
# (söndürme 8 ms'lik patlamanın ilk yarısını bırakır: asıl düzeltme klibin kendisinde).
KLIP_SONU = 0.008
KUYRUK_SON, KUYRUK_ONCE, KUYRUK_DB = 0.020, 0.045, 20.0
KUYRUK_TABAN_DB = -45.0   # son pencere klibin tepesinin bu kadar altındaysa (sessizlik üstünde gürültü) sayılmaz


def bas_kazanci(x: np.ndarray, sn: float, db: float, rampa: float = 0.06, sr: int = SR) -> np.ndarray:
    """Satırın ilk `sn` saniyesine `db` ek kazanç; sınırda `rampa` sn'lik yumuşak geçiş (kopya döner). Gemini turu 2.
    hakem turu (izlenme S4): vurgulu giriş öbeği ("Bu arada bir ayrıntı:") komşularından +3,5 dB, sonra 4,4 dB düşüş;
    sınır öbekler arasındaki sessizliğe konur."""
    y = np.array(x, np.float32, copy=True)
    n = min(len(y), int(round(sn * sr)))
    r = min(n, int(round(rampa * sr)))
    g = np.ones(len(y), np.float32)
    k = np.float32(10 ** (db / 20))
    g[: n - r] = k
    if r:
        g[n - r: n] = np.linspace(k, 1.0, r, dtype=np.float32)
    return y * g


def klip_sondur(x: np.ndarray, sure: float = KLIP_SONU, sr: int = SR) -> np.ndarray:
    """Klibin son `sure` sn'sini yükseltilmiş kosinüsle sıfıra indirir (kopya döner)."""
    n = min(int(round(sure * sr)), len(x))
    if n < 2:
        return x
    y = np.array(x, np.float32, copy=True)
    y[-n:] *= (0.5 + 0.5 * np.cos(np.linspace(0.0, np.pi, n))).astype(np.float32)
    return y


# 14. tur (son tarama): Cartesia `<break>` aralarını sayısal sıfırla dolduruyor ve konuşmayı sönümsüz kesip sönümsüz
# başlatıyor (ör. 8:11 "…bir söz var: | ‘Etkilenmeyen…": -12 dBFS'ten sıfıra, sıfırdan -9 dBFS'e tek örnekte; teslim
# karışımında 7 yer). Motor her klibin İÇİNDEKİ en az IC_SIFIR_MIN sn'lik tam sıfır aralıklarının iki kenarını da
# IC_KENAR sn'de yükseltilmiş kosinüsle yumuşatır (klip boyu ve zamanlama aynı).
IC_KENAR = 0.005
IC_SIFIR_MIN = 0.003


def sifir_araliklari(x: np.ndarray, sr: int = SR, en_az: float = IC_SIFIR_MIN) -> list[tuple[int, int]]:
    """Klipteki tam sıfır (|x| < 1e-7) aralıkları [(i0, i1)], en az `en_az` sn; klibin başı ve sonu dahil."""
    z = np.abs(np.asarray(x)) < 1e-7
    if not z.any():
        return []
    d = np.diff(np.concatenate([[0], z.astype(np.int8), [0]]))
    bas, son = np.nonzero(d == 1)[0], np.nonzero(d == -1)[0]
    m = int(round(en_az * sr))
    return [(int(a), int(b)) for a, b in zip(bas, son) if b - a >= m]


def ic_kenar_yumusat(x: np.ndarray, sure: float = IC_KENAR, sr: int = SR) -> tuple[np.ndarray, int]:
    """(kopya, yumuşatılan kenar sayısı): sıfır aralığından önceki `sure` sn söner, sonraki `sure` sn açılır; klip
    sıfırsız başlıyorsa baş da açılır."""
    y = np.array(x, np.float32, copy=True)
    n = int(round(sure * sr))
    if n < 2 or len(y) < 2 * n:
        return y, 0
    w = (0.5 - 0.5 * np.cos(np.linspace(0.0, np.pi, n))).astype(np.float32)   # 0 -> 1
    k = 0
    for a, b in sifir_araliklari(y, sr):
        if a > 0:
            a0 = max(0, a - n)
            y[a0:a] *= w[::-1][n - (a - a0):]
            k += 1
        if b < len(y):
            b1 = min(len(y), b + n)
            y[b:b1] *= w[: b1 - b]
            k += 1
    if abs(float(y[0])) >= 1e-7:   # sıfırsız başlangıç
        y[:n] *= w
        k += 1
    return y, k


def kuyruk_farki(x: np.ndarray, sr: int = SR, son: float = KUYRUK_SON, once: float = KUYRUK_ONCE) -> tuple[float, float]:
    """(fark_db, son_tepeye_db): klibin son `son` sn'sindeki en yüksek 1 ms RMS'in, ondan önceki `once` sn'nin RMS'ine
    göre farkı; ve o son pencerenin klibin örnek tepesine göre düzeyi. Tık/patlama ölçüsü (teknik hakemin ölçütü)."""
    w = max(1, sr // 1000)
    n = len(x) // w
    ns, no = int(round(son * 1000)), int(round(once * 1000))
    if n < ns + no + 1:
        return 0.0, -120.0
    e = np.sqrt((np.asarray(x[: n * w], np.float64).reshape(n, w) ** 2).mean(axis=1))
    son_db = 20 * math.log10(max(float(e[n - ns:].max()), 1e-9))
    once_db = 20 * math.log10(max(float(np.sqrt((e[n - ns - no:n - ns] ** 2).mean())), 1e-9))
    tepe_db = 20 * math.log10(max(float(np.abs(x).max()), 1e-9))
    return son_db - once_db, son_db - tepe_db


def klip_denetimi(z: Zaman) -> list[str]:
    """Anlatım kliplerinden sonu patlayanlar (kontrol ve render uyarısı). Her dosya bir kez ölçülür."""
    from .zaman import zaman_str
    out, gor = [], set()
    for sz in z.satirlar():
        p = sz.satir.wav
        if p is None or not Path(p).exists() or str(p) in gor:
            continue
        gor.add(str(p))
        fark, duzey = kuyruk_farki(oku(p, 1))
        if fark > KUYRUK_DB and duzey > KUYRUK_TABAN_DB:
            out.append(f"{zaman_str(sz.bas + float(sz.satir.sure or 0), True)}: anlatım klibi {Path(p).name} ({sz.sahne.yer}) "
                       f"patlamayla bitiyor: son {KUYRUK_SON * 1000:.0f} ms önceki {KUYRUK_ONCE * 1000:.0f} ms'den "
                       f"{fark:.0f} dB yüksek (tık) — klibin sonunu düzelt (yavaşlatmada sona sessizlik ekleyip kes, "
                       f"ya da söndür)")
    return out


# ---------------------------------------------------------------- efektler

def efekt_kismasi(anlatim: np.ndarray, efekt: np.ndarray, pay_db: float = EFEKT_PAYI_DB, esik_db: float = -42.0,
                  on_tut: float = 0.06, arka_tut: float = 0.18) -> np.ndarray:
    """Efekt veriyolu için yan zincirli kısma (örnek başına doğrusal kazanç). Anlatım konuşurken (eşik üstü,
    `on_tut` sn önce / `arka_tut` sn sonra dahil) efektlerin 10 ms RMS'i satır seviyesinin (`SATIR_HEDEF_DB`)
    `pay_db` altına sınırlanır; konuşma yokken efekt olduğu gibi kalır. Böylece hiçbir efekt bir kelimeyi
    örtemez; vurgu efekti cümle bitince tam sesiyle duyulur."""
    hop = int(0.01 * SR)
    n = len(anlatim) // hop + 1
    def rms_db(x):
        pad = np.zeros((n * hop,) + x.shape[1:], np.float32)
        pad[: len(x)] = x
        e = (pad.reshape(n, hop, *x.shape[1:]) ** 2).mean(axis=1)
        if e.ndim > 1:
            e = e.mean(axis=1)
        return 10 * np.log10(e + 1e-12)
    v = rms_db(anlatim)
    e = rms_db(efekt)
    aktif = v > esik_db
    a0, a1 = int(round(on_tut / 0.01)), int(round(arka_tut / 0.01))
    if aktif.any():
        idx = np.where(aktif)[0]
        m = np.zeros(n, bool)
        for i in idx:   # n ~ 60k pencere (10 dk); seyrek değil ama hızlı
            m[max(0, i - a0): i + a1 + 1] = True
        aktif = m
    sinir = SATIR_HEDEF_DB - pay_db
    g_db = np.where(aktif, np.minimum(0.0, sinir - e), 0.0)
    # ileri bakış + tutma: komşu pencerelerin en kötüsü (geçici sesin başı kaçmasın), sonra yumuşat
    k = 3
    gp = np.pad(g_db, (k, k), constant_values=0.0)
    g_db = np.min(np.stack([gp[i:i + n] for i in range(2 * k + 1)]), axis=0)
    ker = np.hanning(9)
    ker /= ker.sum()
    g_db = np.convolve(g_db, ker, mode="same")
    t_pen = (np.arange(n) + 0.5) * hop
    gs = np.interp(np.arange(len(anlatim)), t_pen, g_db)
    return (10 ** (gs / 20)).astype(np.float32)


def _sfx_yolu(ad: str) -> Path:
    return SFX_DIR / f"{ad}.wav"


def otomatik_efektler(z: Zaman) -> list[tuple[float, str, float]]:
    """(mutlak sn, efekt adı, dB) — sahne tiplerine ve olaylara göre."""
    out: list[tuple[float, str, float]] = []
    rng = np.random.default_rng(7)
    for s in z.sahneler:
        if not s.otomatik_sfx:
            continue
        b = z.sahne_basi(s)
        n0 = len(out)
        if s.gecis == "kaydir":   # itme geçişi: tepe noktası geçişin ortasına denk gelen whoosh
            out.append((max(0.0, b - 0.22), "gecis", -10.0))
        if s.tip == "bolum_karti":
            out += [(max(0.0, b - 0.24), "gecis", -9.0), (b + 0.05, "boom", -9.0)]
            if not s.p.get("bindirme"):
                out.append((max(0.0, b - 2.35), "riser", -20.0))
        elif s.tip == "foto":
            fz = foto_zamanlari(s)
            # 7. tur: deklanşör baskının ilk değdiği an (out_back(u, 1.0) u = 0,5'te hedefe varır); eskiden oturma
            # anında (0,22 sn geç) çalıyordu
            out.append((b + fz["inis"] + 0.36, "shutter", -8.0))
            # daktilo tuşu her harfte değil, her ETIKET_TUS_ADIMI harfte bir (uzun etikette 40+ tık yorucu)
            harfler = [i for i, ch in enumerate(fz["etiket_metni"]) if ch != " "]
            for i in harfler[::ETIKET_TUS_ADIMI]:
                out.append((b + fz["etiket"] + i / fz["harf_hizi"], "tus", float(rng.uniform(-27, -22))))
        elif s.tip == "manset":
            for t in manset_zamanlari(s)[: len(s.p.get("kutular") or [])]:
                out.append((b + t, "kalem", -9.0))
        elif s.tip == "harita":
            u, v = harita_zamanlari(s)
            for _, t in u:
                out.append((b + t, "blip", -17.0))
            if v:
                out += [(b + v[1], "pop", -8.0), (b + v[1], "hit", -14.0)]
            for t0, sure, _ in rota_zamanlari(s):   # 7. tur: rota çizilirken hafif whoosh, varışta blip
                out += [(max(0.0, b + t0 - 0.05), "whoosh_kisa", -19.0), (b + t0 + sure, "blip", -13.0)]
        elif s.tip == "sayac":
            for bl in sayac_bolumleri(s):
                t0, t1 = bl["t0"], bl["t1"]
                if bl["yil"]:
                    n = abs(int(bl["b"]) - int(bl["a"]))
                    for k in range(1, n + 1):
                        out.append((b + t0 + (t1 - t0) * k / n - (t1 - t0) / n * 0.4, "tik", -10.0))
                elif t1 - t0 < 0.15:      # anlık değişim (deger olayı sure: 0): tık yok, yalnız vuruş
                    pass
                elif bl["b"] < bl["a"]:   # azalan (geri sayım): eşit aralıklı tıklar
                    n = int(min(abs(bl["a"] - bl["b"]), 20))
                    for k in range(1, n + 1):
                        out.append((b + t0 + (t1 - t0) * k / n, "tik", -14.0))
                else:
                    # out_cubic sayımıyla yavaşlayan tıklar
                    for k in range(1, 16):
                        q = k / 16
                        u = 1 - (1 - q) ** (1 / 3)   # out_cubic'in tersi
                        out.append((b + t0 + (t1 - t0) * u, "tik", -16.0))
                out.append((b + bl.get("varis", t1), "hit", -9.0))   # 10. tur: anlıkta yuvarlanan sayı oturunca
        elif s.tip == "zaman_cizelgesi":
            for t in zc_zamanlari(s):
                out.append((b + t, "pop", -11.0))
        elif s.tip == "metin":
            mz = metin_zamanlari(s)
            if mz["daktilo"]:
                bas, hiz = mz["daktilo"]
                harfler = [i for i, ch in enumerate(mz["metin"]) if ch != " "]
                for i in harfler[::TUS_ADIMI]:
                    out.append((b + bas + i / hiz, "tus", float(rng.uniform(-19, -14))))
            elif mz["kelimeler"]:
                out.append((b + mz["kelimeler"][0] - 0.1, "whoosh_kisa", -14.0))
            if s.p.get("ceviri"):
                out.append((b + mz["ceviri"], "pop", -10.0))
            for o in olaylar(s, "ustunu_ciz"):
                out.append((b + o.zaman, "kalem", -7.0))
        elif s.tip == "wojak":
            out += _karakter_efektleri(s, b, -16.0)
            for o in balon_olaylari(s):
                out.append((b + o.zaman, "pop", -11.0))
        elif s.tip in ("bolunmus", "izgara", "pano", "marka", "bitis", "kapanis"):
            out += _ek_efektler(s, b)
        if s.tip != "wojak" and s.p.get("konuk"):   # konuk karakterin girişi/çıkışı (wojak sahnesindeki gibi)
            out += _karakter_efektleri(s, b, -18.0)
        for o in olaylar(s, "isim"):   # whoosh tepesi (0,22 sn) etiketin en hızlı kaydığı ilk kareye
            out.append((max(0.0, b + o.zaman - WHOOSH_TEPE + 0.08), "whoosh_kisa", -15.0))
        for o in olaylar(s, "kelime"):
            out.append((b + o.zaman, "pop", -12.0))
        for o in olaylar(s, "damga"):
            if not o.p.get("inik"):   # damga.wav'ın vuruşu 0 ms'de: damganın kâğıda değdiği an (Damga.INIS)
                out.append((b + o.zaman + Damga.INIS, "damga", -5.0))
        for o in olaylar(s, "kose"):
            out.append((b + o.zaman, "static" if o.p.get("takili") else "tik", -18.0 if o.p.get("takili") else -12.0))
        ek = float(s.p.get("sfx_db") or 0.0)
        if ek:
            out[n0:] = [(t, ad, db + ek) for t, ad, db in out[n0:]]
    return out


WHOOSH_TEPE = 0.22   # whoosh_kisa.wav'ın tepe anı (sn)


def _karakter_efektleri(s, b: float, db: float) -> list[tuple[float, str, float]]:
    """Karakter giriş/çıkış efektleri (7. tur: ses ile görüntünün en hızlı anı aynı karede). Giriş out_back: en hızlı
    ilk karelerde -> whoosh tepesi girişin ~0,1 sn sonrasına; çıkış in_cubic: en hızlı sonda -> tepe ~0,35 sn'ye.
    `yon: pop` girişi kayma değil büyüme: 'pop'."""
    out = []
    yonler = {c["id"]: c.get("yon") for c in s.p.get("karakterler", []) + s.p.get("konuk", [])}
    for kid, v in karakter_zamanlari(s).items():
        if v["giris"] is not None:
            if yonler.get(kid) == "pop":
                out.append((b + v["giris"], "pop", db + 4.0))
            else:
                out.append((max(0.0, b + v["giris"] + 0.1 - WHOOSH_TEPE), "whoosh_kisa", db))
        if v["cikis"] is not None:
            out.append((b + v["cikis"] + 0.35 - WHOOSH_TEPE, "whoosh_kisa", db))
    return out


def _ek_efektler(s, b: float) -> list[tuple[float, str, float]]:
    """2. tur sahne tiplerinin otomatik efektleri."""
    out: list[tuple[float, str, float]] = []
    if s.tip == "bolunmus":
        from .bilgi import bolunmus_zamanlari
        z = bolunmus_zamanlari(s)
        for taraf, t in z["ac"].items():
            if t > 0.01:
                out.append((b + t - 0.08, "whoosh_kisa", -10.0))
        for t in z["buyut"].values():
            out.append((b + t, "whoosh", -16.0))
        for t in z["ceviri"].values():
            out.append((b + t, "pop", -12.0))
    elif s.tip == "pano":
        from .bilgi import pano_zamanlari
        z = pano_zamanlari(s)
        for t in z["kartlar"].values():
            if t >= 0:   # asılı kart (önceki çekimden devam) ses çıkarmaz
                out += [(b + t, "whoosh_kisa", -19.0), (b + t + 0.18, "raptiye", -6.0)]
        for _, _, t in z["ipler"]:
            if t >= 0:
                out.append((b + t, "whoosh_kisa", -21.0))
    elif s.tip == "marka":
        out.append((b, "marka", -6.0))
    elif s.tip == "bitis":
        from .kanal import bitis_zamanlari
        z = bitis_zamanlari(s)
        for t in z["kutular"] + [z["abone"]]:
            out.append((b + t, "pop", -14.0))
    elif s.tip == "kapanis":
        from .kapanis import efektler
        out += efektler(s, b)
    # izgara: bilerek sessiz (noktalar sessizce dolar ve söner)
    return out


def muzik_egrisi(z: Zaman) -> list[tuple[float, float, float]]:
    """Müzik seviyesi değişimleri: (mutlak sn, dB, rampa sn). Sahne `muzik_db` (sahne başında) ve `muzik` olayları
    ({db, gecis}); 0 dB = normal (kısma zarfı ayrıca uygulanır)."""
    out: list[tuple[float, float, float]] = []
    son = 0.0

    def rampa(r: float, eski: float, yeni: float) -> float:
        # 7. tur: bir an sessizlikten (<= -30 dB) dönen müzik 0,6 sn'de 40 dB yükselince "patlayarak" geliyordu;
        # dönüş en az SESSIZLIK_DONUS sn
        return max(r, SESSIZLIK_DONUS) if eski <= -30 and yeni - eski >= 20 else r

    for s in z.sahneler:
        b = z.sahne_basi(s)
        if abs(s.muzik_db - son) > 1e-6:
            out.append((b, s.muzik_db, rampa(0.6, son, s.muzik_db)))
            son = s.muzik_db
        for o in olaylar(s, "muzik"):
            db = float(o.p["db"])
            out.append((b + o.zaman, db, rampa(float(o.p.get("gecis", 0.5)), son, db)))
            son = db
    return out


SESSIZLIK_DONUS = 1.6


def muzik_kazanci(egri: list[tuple[float, float, float]], n: int) -> np.ndarray | None:
    """Eğriden örnek başına doğrusal kazanç (yoksa None)."""
    if not egri:
        return None
    ts, vs = [0.0], [0.0]
    for t, db, r in sorted(egri, key=lambda x: x[0]):
        if t <= 1e-6 and len(ts) == 1:   # videonun başında: rampa yok, o seviyeden başlar
            vs[0] = db
            continue
        t = max(t, ts[-1])
        ts += [t, t + max(r, 0.01)]
        vs += [vs[-1], db]
    tt = np.arange(n, dtype=np.float64) / SR
    g = np.interp(tt, np.asarray(ts), np.asarray(vs))
    return (10 ** (g / 20)).astype(np.float32)


# ---------------------------------------------------------------- müzik ve kısma

def muzik_kipleri(z: Zaman) -> list[tuple[float, str]]:
    """Müzik kipi değişimleri [(mutlak sn, kip)]: video `muzik.mod` (vars. drone) + sahne/bölüm `muzik_mod`."""
    cur = str(z.video.muzik.get("mod", "drone"))
    out = [(0.0, cur)]
    for s in z.sahneler:
        if s.muzik_mod and s.muzik_mod != cur:
            cur = s.muzik_mod
            out.append((round(z.sahne_basi(s), 3), cur))
    return out


def muzik_altligi(v: Video, sure: float, log=print, kipler: list[tuple[float, str]] | None = None) -> np.ndarray | None:
    m = v.muzik
    if m.get("yok"):
        return None
    n = int(round(sure * SR))
    if m.get("dosya"):
        x = oku(m["dosya"], 2)
        bas = int(float(m.get("baslangic", 0)) * SR)
        x = x[bas:]
        if len(x) < n:   # kısa parça: çapraz geçişli döngü
            parcalar, xf = [x], int(2.0 * SR)
            top = len(x)
            while top < n:
                parcalar.append(x)
                top += len(x) - xf
            y = parcalar[0].copy()
            for p in parcalar[1:]:
                r = np.linspace(0, 1, xf, dtype=np.float32)[:, None]
                y[-xf:] = y[-xf:] * (1 - r) + p[:xf] * r
                y = np.concatenate([y, p[xf:]])
            x = y
        x = x[:n].copy()
        fo = int(3.0 * SR)
        x[-fo:] *= np.linspace(1, 0, fo, dtype=np.float32)[:, None]
        return x
    kipler = kipler or [(0.0, str(m.get("mod", "drone")))]
    imza = "" if kipler == [(0.0, "drone")] else "_" + hashlib.sha1(json.dumps(kipler).encode()).hexdigest()[:8]
    yol = v.cikti / "muzik" / f"altlik_{m['tohum']}_{sure:.2f}{imza}.wav"
    if not yol.exists():
        log(f"müzik altlığı üretiliyor ({sure:.0f} sn, tohum {m['tohum']}, {len(kipler)} kip bölümü)...")
        x = (muzik.uret(sure, int(m["tohum"]), mod=kipler[0][1]) if len(kipler) == 1
             else muzik.uret_bolumlu(sure, int(m["tohum"]), kipler))
        wav_yaz(yol, x)
    x = oku(yol, 2)
    if len(x) < n:
        x = np.concatenate([x, np.zeros((n - len(x), 2), np.float32)])
    return x[:n].copy()


def kisma_zarfi(anlatim: np.ndarray, duk_db: float, acik_db: float, esik_db: float = -42.0, tut: float = 0.35,
                atak: float = 0.12, birak: float = 0.7) -> np.ndarray:
    """Anlatım izinden (yan zincir) müzik kazancı (doğrusal, örnek başına)."""
    hop = int(0.02 * SR)
    n = len(anlatim) // hop + 1
    pad = np.zeros(n * hop, np.float32)
    pad[: len(anlatim)] = anlatim
    rms = np.sqrt((pad.reshape(n, hop) ** 2).mean(axis=1) + 1e-12)
    aktif = 20 * np.log10(rms) > esik_db
    # tutma: aktif pencereden sonra `tut` sn daha aktif say
    k = int(tut / 0.02)
    if k > 0:
        idx = np.where(aktif)[0]
        tut_m = np.zeros(n, bool)
        for i in idx:   # seyrek değil ama n küçük (10 dk = 30k pencere)
            tut_m[i:i + k + 1] = True
        aktif = tut_m
    hedef = np.where(aktif, duk_db, acik_db).astype(np.float64)
    a_at, a_bi = math.exp(-0.02 / atak), math.exp(-0.02 / birak)
    g = np.empty(n)
    cur = hedef[0]
    for i in range(n):
        h = hedef[i]
        c = a_at if h < cur else a_bi
        cur = h + (cur - h) * c
        g[i] = cur
    t_pen = (np.arange(n) + 0.5) * hop
    gs = np.interp(np.arange(len(anlatim)), t_pen, g)
    return (10 ** (gs / 20)).astype(np.float32)


TEPE_PAYI_DB = 2.0   # altlığın (müzik + efekt) 100 ms RMS'i medyan konuşma seviyesini en çok bu kadar aşar


def tepe_siniri(anlatim: np.ndarray, altlik: np.ndarray, pay_db: float = TEPE_PAYI_DB, pencere: float = 0.1,
                esik_db: float = -40.0) -> tuple[np.ndarray, dict]:
    """Altlık (müzik + efekt) için geçici tepe sınırı (örnek başına doğrusal kazanç). Bölüm kartı boom/whoosh'u,
    kanal imzası, damga ve doruk boom'u 100 ms pencerede medyan konuşma seviyesinin `pay_db` üstüne çıkmasın
    (talidomit-turkiye 3. hakem turu: kartlarda +7,5-8,7 dB, kulaklıkta sıçratıyordu). Medyan konuşma seviyesi
    anlatım izinin konuşulan 100 ms pencerelerinden (> esik_db) ölçülür; konuşma yoksa sınır uygulanmaz."""
    hop = int(0.01 * SR)
    n = len(anlatim) // hop + 1
    k = max(1, int(round(pencere / 0.01)))

    def e100(x):
        pad = np.zeros((n * hop,) + x.shape[1:], np.float32)
        pad[: len(x)] = x
        e = (pad.reshape(n, hop, *x.shape[1:]).astype(np.float64) ** 2).mean(axis=1)
        if e.ndim > 1:
            e = e.mean(axis=1)
        c = np.convolve(e, np.ones(k) / k, mode="same")   # 100 ms kayan pencere
        return 10 * np.log10(c + 1e-12)

    va = e100(anlatim)
    konusma = va > esik_db
    if not konusma.any():
        return np.ones(len(anlatim), np.float32), {}
    ref = float(np.median(va[konusma]))
    ea = e100(altlik)
    g_db = np.minimum(0.0, ref + pay_db - ea)
    # ileri bakış + tutma (pencerenin tamamı), sonra yumuşat
    gp = np.pad(g_db, (k, k), constant_values=0.0)
    g_db = np.min(np.stack([gp[i:i + n] for i in range(2 * k + 1)]), axis=0)
    ker = np.hanning(11)
    ker /= ker.sum()
    g_db = np.convolve(g_db, ker, mode="same")
    t_pen = (np.arange(n) + 0.5) * hop
    gs = np.interp(np.arange(len(anlatim)), t_pen, g_db)
    bilgi = {"konusma_medyan_100ms_db": round(ref, 2), "tepe_payi_db": pay_db,
             "tepe_siniri_en_cok_db": round(float(g_db.min()), 1),
             "altlik_en_yuksek_ustu_db": round(float(ea.max() - ref), 1)}
    return (10 ** (gs / 20)).astype(np.float32), bilgi


# ---------------------------------------------------------------- ana miks

def miks(v: Video, z: Zaman, klasor: Path, log=print) -> dict:
    """Sesleri kurar; son WAV'ı, anlatım izini ve ölçümleri döndürür."""
    klasor.mkdir(parents=True, exist_ok=True)
    n = z.toplam_kare * SR // z.fps
    sure = n / SR
    anlatim = np.zeros(n, np.float32)
    eksik = []
    for sz in z.satirlar():
        if sz.satir.wav is None or not Path(sz.satir.wav).exists():
            eksik.append(sz.sahne.yer)
            continue
        x = oku(sz.satir.wav, 1)
        x = x * satir_kazanci(x) * (10 ** (sz.satir.db / 20))   # her ses/satır aynı konuşma seviyesinde (+ satır db)
        if sz.satir.db_bas:
            x = bas_kazanci(x, *sz.satir.db_bas)
        i = int(round(sz.bas * SR))
        j = min(n, i + len(x))
        if j > i:
            # 14. tur: basamaklı bitiş (tık) ve klip içindeki sönümsüz kesme/başlangıçlar (Cartesia break) kalmasın
            anlatim[i:j] += klip_sondur(ic_kenar_yumusat(x[: j - i])[0])
    if eksik:
        log(f"UYARI: {len(eksik)} satırın sesi yok (sessiz kalır); önce: python -m wojak uzun seslendir")
    ham_anlatim = klasor / "anlatim_ham.wav"
    wav_yaz(ham_anlatim, anlatim, float32=True)
    L_an = float(loudnorm_olc(ham_anlatim)["input_i"]) if anlatim.any() else -23.0
    if not math.isfinite(L_an):
        L_an = -23.0
    mix = np.repeat(anlatim[:, None], 2, axis=1)
    altlik = np.zeros_like(mix)   # müzik + efekt (anlatımsız): ölçüm izi
    bilgi = {"anlatim_lufs_ham": round(L_an, 2)}
    mz = muzik_altligi(v, sure, log, muzik_kipleri(z))
    if mz is not None:
        tmp = klasor / "muzik_ham.wav"
        wav_yaz(tmp, mz, float32=True)
        L_mz = float(loudnorm_olc(tmp)["input_i"])
        seviye = float(v.muzik.get("seviye", -22.0))
        acik = float(v.muzik.get("acik", -15.0))
        duk_db, acik_db = (L_an + seviye) - L_mz, (L_an + acik) - L_mz
        g = kisma_zarfi(anlatim, duk_db, acik_db)
        gm = muzik_kazanci(muzik_egrisi(z), n)
        if gm is not None:
            g = g * gm
            bilgi["muzik_egrisi"] = len(muzik_egrisi(z))
        altlik += mz * g[:, None]
        bilgi.update({"muzik_lufs_ham": round(L_mz, 2), "muzik_kisik_db": round(seviye, 1),
                      "muzik_acik_db": round(acik, 1)})
        tmp.unlink(missing_ok=True)
    efektler = [(t, _sfx_yolu(a), db) for t, a, db in (otomatik_efektler(z) if v.otomatik_sfx else [])]
    efektler += [(t, x.yol, x.db) for t, x in tum_sfx(z)]
    bus = np.zeros((n, 2), np.float32)
    for t, yol, db in efektler:
        if not Path(yol).exists():
            log(f"UYARI: efekt yok: {yol}")
            continue
        x = oku(yol, 2) * (10 ** (db / 20))
        i = int(round(t * SR))
        j = min(n, i + len(x))
        if j > i >= 0:
            bus[i:j] += x[: j - i]
    ge = efekt_kismasi(anlatim, bus)
    altlik += bus * ge[:, None]
    gt, tb = tepe_siniri(anlatim, altlik)
    altlik *= gt[:, None]
    bilgi.update(tb)
    mix += altlik
    bilgi["efekt_sayisi"] = len(efektler)
    bilgi["efekt_kisma_en_cok_db"] = round(float(20 * np.log10(ge.min() + 1e-9)), 1)
    ham = klasor / "miks_ham.wav"
    wav_yaz(ham, mix, float32=True)
    # iki geçişli normalizasyon: (1) ölç, kazanç + tepe sınırlayıcı; (2) ölç, doğrusal loudnorm
    m1 = loudnorm_olc(ham)
    on_kazanc = HEDEF_I - float(m1["input_i"])
    on = klasor / "miks_on.wav"
    limit = 0.74
    # doğrusal loudnorm için: ölçülen tepe + kalan kazanç <= WAV_TP olana dek sınırı indir. 4 deneme yetmeyebiliyor
    # (talidomit-turkiye 3. tur: müzik -18 dB'ye çıkınca 4 adımda koşul sağlanmadı, loudnorm dinamik kipe düştü)
    for _ in range(10):
        # latency=1: sınırlayıcının ileri bakış gecikmesi telafi edilir (yoksa ses 4 ms geride kalıyordu).
        # 4x örnekleme: alimiter örnek tepesine bakar; 48 kHz'de gerçek (örnekler arası) tepe sınırın ~3 dB üstüne
        # çıkıyordu, döngü de sınırı -9,7 dBFS'e indirip sesin ~4,6 LU'sunu sınırlayıcıda eziyordu (4. tur ölçümü:
        # 100 ms pencerelerde medyan 2,9 dB kazanç düşümü). 192 kHz'de sınırlanınca tepe sınırda kalır, ezilme ~1 LU.
        sinir = (f"volume={on_kazanc:.3f}dB,aresample={4 * SR},alimiter=limit={limit:.4f}:attack=4:release=60:level=0:"
                 f"latency=1,aresample={SR}")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(ham), "-af", sinir, "-c:a", "pcm_f32le",
                        str(on)], check=True)
        m2 = loudnorm_olc(on)
        if float(m2["input_tp"]) + (HEDEF_I - float(m2["input_i"])) <= WAV_TP - 0.1:
            break
        limit *= 0.89
    bilgi["sinirlayici"] = round(20 * math.log10(limit), 2)
    son_af = (f"loudnorm=I={HEDEF_I}:TP={WAV_TP}:LRA={HEDEF_LRA}:measured_I={m2['input_i']}:"
              f"measured_TP={m2['input_tp']}:measured_LRA={m2['input_lra']}:measured_thresh={m2['input_thresh']}:"
              f"offset={m2['target_offset']}:linear=true:print_format=json")
    son = klasor / f"{v.id}_ses.wav"
    r = subprocess.run(["ffmpeg", "-y", "-hide_banner", "-nostats", "-i", str(on), "-af", son_af, "-ar", str(SR),
                        "-ac", "2", "-c:a", "pcm_s16le", str(son)], capture_output=True, text=True, check=True)
    e = r.stderr
    m3 = json.loads(e[e.rindex("{"):e.rindex("}") + 1])
    bilgi["loudnorm_turu"] = m3.get("normalization_type")
    lin_kazanc = HEDEF_I - float(m2["input_i"]) if m3.get("normalization_type") == "linear" else 0.0
    # anlatım izi ve altlık izi (müzik + efekt): aynı toplam kazanç, sınırlayıcı yok (32 bit kayan nokta; 0 dBFS'yi
    # aşabilir). Anlatım / altlık oranı bu ikisinden ölçülür: "miks - anlatım" farkı, miksin sınırlayıcısının sesin
    # tepelerinden kestiği kısmı da altlık sanar (talidomit-turkiye: gerçek oran medyan ~23 dB iken fark yöntemi ~8 dB).
    stem = klasor / f"{v.id}_anlatim.wav"
    toplam = on_kazanc + lin_kazanc
    # mono -> stereo AYNI seviyede (pan): `-ac 2` merkez karışımında -3 dB uyguluyordu (teknik hakem, 3. tur: iz
    # miksteki anlatımdan 3,01 dB alçaktı; izlerden ölçülen anlatım/altlık oranı 3 dB eksik çıkıyordu)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(ham_anlatim), "-af",
                    f"volume={toplam:.3f}dB,pan=stereo|c0=c0|c1=c0", "-ar", str(SR), "-c:a", "pcm_f32le", str(stem)],
                   check=True)
    ham_altlik = klasor / "altlik_ham.wav"
    wav_yaz(ham_altlik, altlik, float32=True)
    altlik_izi = klasor / f"{v.id}_altlik.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(ham_altlik), "-af", f"volume={toplam:.3f}dB",
                    "-ar", str(SR), "-ac", "2", "-c:a", "pcm_f32le", str(altlik_izi)], check=True)
    for f in (ham, on, ham_anlatim, ham_altlik):
        f.unlink(missing_ok=True)
    olcum = ebur128(son)
    bilgi.update({"son_lufs": olcum.get("I"), "son_tepe_dbtp": olcum.get("TP"), "son_lra": olcum.get("LRA"),
                  "ses": str(son), "anlatim_izi": str(stem), "altlik_izi": str(altlik_izi), "ornek": n, "sure": sure})
    return bilgi
