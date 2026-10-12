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

import json
import math
import subprocess
from functools import lru_cache
from pathlib import Path

import numpy as np

from .. import config
from . import muzik
from .sahneler import (foto_zamanlari, harita_zamanlari, karakter_zamanlari, manset_zamanlari, metin_zamanlari,
                       olaylar, sayac_zamanlari, zc_zamanlari)
from .spec import SFX_DIR, Video
from .zaman import Zaman, balon_olaylari, tum_sfx

SR = 48000
HEDEF_I, HEDEF_TP, HEDEF_LRA = -14.0, -1.0, 11.0


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
    af = (ek_filtre + "," if ek_filtre else "") + f"loudnorm=I={HEDEF_I}:TP={HEDEF_TP}:LRA={HEDEF_LRA}:print_format=json"
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(yol), "-af", af, "-f", "null", "-"],
                       capture_output=True, text=True)
    e = r.stderr
    return json.loads(e[e.rindex("{"):e.rindex("}") + 1])


def ebur128(yol: Path) -> dict:
    """Son ölçüm: entegre yükseklik (LUFS), gerçek tepe (dBTP), LRA."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(yol), "-af", "ebur128=peak=true",
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


# ---------------------------------------------------------------- efektler

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
        if s.gecis == "kaydir":
            out.append((max(0.0, b - 0.05), "whoosh_kisa", -7.0))
        if s.tip == "bolum_karti":
            out += [(b, "boom", -9.0), (max(0.0, b - 2.35), "riser", -20.0)]
        elif s.tip == "foto":
            fz = foto_zamanlari(s)
            out.append((b + fz["oturma"] - 0.04, "shutter", -8.0))
            for i in range(len(fz["etiket_metni"])):
                if fz["etiket_metni"][i] != " ":
                    out.append((b + fz["etiket"] + i / fz["harf_hizi"], "tus", float(rng.uniform(-19, -14))))
        elif s.tip == "manset":
            for t in manset_zamanlari(s)[: len(s.p.get("kutular") or [])]:
                out.append((b + t, "kalem", -9.0))
        elif s.tip == "harita":
            u, v = harita_zamanlari(s)
            for _, t in u:
                out.append((b + t, "blip", -17.0))
            if v:
                out += [(b + v[1], "pop", -8.0), (b + v[1], "hit", -14.0)]
        elif s.tip == "sayac":
            t0, t1 = sayac_zamanlari(s)
            if s.p.get("yil"):
                a, c = int(s.p["yil"][0]), int(s.p["yil"][1])
                n = abs(c - a)
                for k in range(1, n + 1):
                    out.append((b + t0 + (t1 - t0) * k / n - (t1 - t0) / n * 0.4, "tik", -10.0))
            else:
                # out_cubic sayımıyla yavaşlayan tıklar
                for k in range(1, 16):
                    q = k / 16
                    u = 1 - (1 - q) ** (1 / 3)   # out_cubic'in tersi
                    out.append((b + t0 + (t1 - t0) * u, "tik", -16.0))
            out.append((b + t1, "hit", -9.0))
        elif s.tip == "zaman_cizelgesi":
            for t in zc_zamanlari(s):
                out.append((b + t, "pop", -11.0))
        elif s.tip == "metin":
            mz = metin_zamanlari(s)
            if mz["kelimeler"]:
                out.append((b + mz["kelimeler"][0] - 0.1, "whoosh_kisa", -14.0))
            if s.p.get("ceviri"):
                out.append((b + mz["ceviri"], "pop", -10.0))
        elif s.tip == "wojak":
            for v in karakter_zamanlari(s).values():
                if v["giris"] is not None:
                    out.append((b + v["giris"], "whoosh_kisa", -16.0))
                if v["cikis"] is not None:
                    out.append((b + v["cikis"], "whoosh_kisa", -16.0))
            for o in balon_olaylari(s):
                out.append((b + o.zaman, "pop", -11.0))
        for o in olaylar(s, "isim"):
            out.append((b + o.zaman, "whoosh_kisa", -15.0))
        for o in olaylar(s, "kelime"):
            out.append((b + o.zaman, "pop", -12.0))
    return out


# ---------------------------------------------------------------- müzik ve kısma

def muzik_altligi(v: Video, sure: float, log=print) -> np.ndarray | None:
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
    yol = config.OUT / v.id / "muzik" / f"altlik_{m['tohum']}_{sure:.2f}.wav"
    if not yol.exists():
        log(f"müzik altlığı üretiliyor ({sure:.0f} sn, tohum {m['tohum']})...")
        wav_yaz(yol, muzik.uret(sure, int(m["tohum"])))
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
        x = x * satir_kazanci(x)   # her ses/satır aynı konuşma seviyesinde
        i = int(round(sz.bas * SR))
        j = min(n, i + len(x))
        if j > i:
            anlatim[i:j] += x[: j - i]
    if eksik:
        log(f"UYARI: {len(eksik)} satırın sesi yok (sessiz kalır); önce: python -m wojak uzun seslendir")
    ham_anlatim = klasor / "anlatim_ham.wav"
    wav_yaz(ham_anlatim, anlatim, float32=True)
    L_an = float(loudnorm_olc(ham_anlatim)["input_i"]) if anlatim.any() else -23.0
    if not math.isfinite(L_an):
        L_an = -23.0
    mix = np.repeat(anlatim[:, None], 2, axis=1)
    bilgi = {"anlatim_lufs_ham": round(L_an, 2)}
    mz = muzik_altligi(v, sure, log)
    if mz is not None:
        tmp = klasor / "muzik_ham.wav"
        wav_yaz(tmp, mz, float32=True)
        L_mz = float(loudnorm_olc(tmp)["input_i"])
        seviye = float(v.muzik.get("seviye", -22.0))
        acik = float(v.muzik.get("acik", -15.0))
        duk_db, acik_db = (L_an + seviye) - L_mz, (L_an + acik) - L_mz
        g = kisma_zarfi(anlatim, duk_db, acik_db)
        mix += mz * g[:, None]
        bilgi.update({"muzik_lufs_ham": round(L_mz, 2), "muzik_kisik_db": round(seviye, 1),
                      "muzik_acik_db": round(acik, 1)})
        tmp.unlink(missing_ok=True)
    efektler = [(t, _sfx_yolu(a), db) for t, a, db in (otomatik_efektler(z) if v.otomatik_sfx else [])]
    efektler += [(t, x.yol, x.db) for t, x in tum_sfx(z)]
    for t, yol, db in efektler:
        if not Path(yol).exists():
            log(f"UYARI: efekt yok: {yol}")
            continue
        x = oku(yol, 2) * (10 ** (db / 20))
        i = int(round(t * SR))
        j = min(n, i + len(x))
        if j > i >= 0:
            mix[i:j] += x[: j - i]
    bilgi["efekt_sayisi"] = len(efektler)
    ham = klasor / "miks_ham.wav"
    wav_yaz(ham, mix, float32=True)
    # iki geçişli normalizasyon: (1) ölç, kazanç + tepe sınırlayıcı; (2) ölç, doğrusal loudnorm
    m1 = loudnorm_olc(ham)
    on_kazanc = HEDEF_I - float(m1["input_i"])
    on = klasor / "miks_on.wav"
    limit = 0.74
    for _ in range(4):   # doğrusal loudnorm için: ölçülen tepe + kalan kazanç <= -1 dBTP olana dek sınırı indir
        sinir = f"volume={on_kazanc:.3f}dB,alimiter=limit={limit:.4f}:attack=4:release=60:level=0"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(ham), "-af", sinir, "-c:a", "pcm_f32le",
                        str(on)], check=True)
        m2 = loudnorm_olc(on)
        if float(m2["input_tp"]) + (HEDEF_I - float(m2["input_i"])) <= HEDEF_TP - 0.1:
            break
        limit *= 0.89
    bilgi["sinirlayici"] = round(20 * math.log10(limit), 2)
    son_af = (f"loudnorm=I={HEDEF_I}:TP={HEDEF_TP}:LRA={HEDEF_LRA}:measured_I={m2['input_i']}:"
              f"measured_TP={m2['input_tp']}:measured_LRA={m2['input_lra']}:measured_thresh={m2['input_thresh']}:"
              f"offset={m2['target_offset']}:linear=true:print_format=json")
    son = klasor / f"{v.id}_ses.wav"
    r = subprocess.run(["ffmpeg", "-y", "-hide_banner", "-nostats", "-i", str(on), "-af", son_af, "-ar", str(SR),
                        "-ac", "2", "-c:a", "pcm_s16le", str(son)], capture_output=True, text=True, check=True)
    e = r.stderr
    m3 = json.loads(e[e.rindex("{"):e.rindex("}") + 1])
    bilgi["loudnorm_turu"] = m3.get("normalization_type")
    lin_kazanc = HEDEF_I - float(m2["input_i"]) if m3.get("normalization_type") == "linear" else 0.0
    # anlatım izi: aynı toplam kazanç + aynı sınırlayıcı
    stem = klasor / f"{v.id}_anlatim.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(ham_anlatim), "-af",
                    f"volume={on_kazanc + lin_kazanc:.3f}dB,alimiter=limit=0.89:attack=4:release=60:level=0",
                    "-ar", str(SR), "-ac", "2", "-c:a", "pcm_s16le", str(stem)], check=True)
    for f in (ham, on, ham_anlatim):
        f.unlink(missing_ok=True)
    olcum = ebur128(son)
    bilgi.update({"son_lufs": olcum.get("I"), "son_tepe_dbtp": olcum.get("TP"), "son_lra": olcum.get("LRA"),
                  "ses": str(son), "anlatim_izi": str(stem), "ornek": n, "sure": sure})
    return bilgi
