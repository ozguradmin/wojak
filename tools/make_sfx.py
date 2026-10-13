#!/usr/bin/env python3
"""Telifsiz ses efektlerini ffmpeg ile sentezler -> assets/sfx/*.wav

    python tools/make_sfx.py              # hepsi
    python tools/make_sfx.py pop tus      # yalnız adı verilenler (var olanlara dokunmaz)

Hepsi matematiksel olarak üretildiği için telif sorunu yoktur. Daha kaliteli
efekt/müzik için assets/music/README.md'ye bakın.
"""

import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "sfx"

SFX = {
    # sinematik "boom": düşen frekanslı sinüs + gürültü darbesi
    "boom": ("aevalsrc='0.9*sin(2*PI*(60-30*t)*t)*exp(-3.2*t)+0.25*(random(0)-0.5)*exp(-18*t)':d=2.2:s=48000",
             "lowpass=f=900,volume=1.4"),
    # kısa sert vuruş (kesme anları için)
    "hit": ("aevalsrc='0.8*sin(2*PI*90*t)*exp(-9*t)+0.5*(random(0)-0.5)*exp(-30*t)':d=0.9:s=48000",
            "lowpass=f=2500,volume=1.3"),
    # geçiş "whoosh"u
    "whoosh": ("anoisesrc=c=pink:d=0.8:a=0.6:r=48000",
               "bandpass=f=900:w=1.4,afade=t=in:d=0.45:curve=exp,afade=t=out:st=0.45:d=0.35,volume=9"),
    # gerilim yükselişi
    "riser": ("aevalsrc='0.35*sin(2*PI*(180+500*t*t/2.5)*t)*(t/2.5)+0.25*(random(0)-0.5)*(t/2.5)':d=2.5:s=48000",
              "highpass=f=120,afade=t=out:st=2.35:d=0.15"),
    # kalp atışı (2 vuruş)
    "heartbeat": ("aevalsrc='0.9*sin(2*PI*50*t)*exp(-25*t)+0.7*sin(2*PI*45*(t-0.28))*exp(-25*(t-0.28))*gte(t,0.28)':d=1.0:s=48000",
                  "lowpass=f=400,volume=1.6"),
    # cızırtı / statik
    "static": ("anoisesrc=c=white:d=0.6:a=0.4:r=48000", "bandpass=f=3000:w=1.2,afade=t=out:st=0.45:d=0.15,volume=3.5"),
    # fotoğraf makinesi deklanşörü (kanıt fotoğrafları için)
    "shutter": ("aevalsrc='(random(0)-0.5)*(exp(-120*t)+0.7*exp(-120*(t-0.07))*gte(t,0.07))':d=0.25:s=48000",
                "highpass=f=1500,volume=2.5"),
    # --- uzun format (wojak/uzun) için ---
    # balon/ikon "pop"u: perdesi hızla düşen kısa ton
    "pop": ("aevalsrc='0.7*sin(2*PI*(420+900*exp(-35*t))*t)*exp(-26*t)+0.15*(random(0)-0.5)*exp(-300*t)':d=0.2:s=48000",
            "highpass=f=180,afade=t=out:st=0.15:d=0.05,volume=1.2"),
    # daktilo tuşu (etiket yazılırken harf başına)
    "tus": ("aevalsrc='(random(0)-0.5)*exp(-170*t)+0.35*sin(2*PI*1700*t)*exp(-110*t)+0.2*sin(2*PI*230*t)*exp(-60*t)':d=0.07:s=48000",
            "highpass=f=400,volume=1.6"),
    # fosforlu kalem sürtünmesi
    "kalem": ("aevalsrc='(random(0)-0.5)*(0.55+0.45*sin(2*PI*19*t))':d=0.6:s=48000",
              "bandpass=f=2600:w=1.3,afade=t=in:d=0.06,afade=t=out:st=0.45:d=0.15,volume=2.2"),
    # sayaç tıkı
    "tik": ("aevalsrc='0.8*sin(2*PI*2400*t)*exp(-280*t)+0.3*(random(0)-0.5)*exp(-500*t)':d=0.04:s=48000",
            "highpass=f=800,volume=1.0"),
    # haritada ülke yanarken yumuşak ton
    "blip": ("aevalsrc='0.45*sin(2*PI*660*t)*exp(-12*t)+0.2*sin(2*PI*990*t)*exp(-18*t)':d=0.4:s=48000",
             "afade=t=in:d=0.004,volume=1.0"),
    # kısa geçiş hışırtısı (itme geçişi, isim etiketi)
    "whoosh_kisa": ("anoisesrc=c=pink:d=0.45:a=0.6:r=48000",
                    "bandpass=f=1300:w=1.2,afade=t=in:d=0.2:curve=exp,afade=t=out:st=0.2:d=0.25,volume=8"),
    # karanlık ambiyans altlığı (müzik yoksa kullanılabilir, 30 sn, döngüye uygun)
    "drone": ("aevalsrc='0.22*sin(2*PI*55*t)*(0.75+0.25*sin(2*PI*0.2*t))+0.12*sin(2*PI*82.4*t)+0.07*sin(2*PI*110.3*t)*(0.5+0.5*sin(2*PI*0.13*t))':d=30:s=48000",
              "lowpass=f=600,aecho=0.8:0.7:120|300:0.3|0.2,volume=1.3"),
}


# ---------------------------------------------------------------- numpy ile sentez (uzun format, 2. tur)
# Süpürmeli filtre, nota dizisi ve yankı gerektiren efektler ffmpeg lavfi ile yazılamıyor; bunlar numpy ile
# üretilir (müzik altlığıyla aynı tını ve yankı: wojak/uzun/muzik.py). Hepsi 48 kHz stereo.

SR = 48000


def _np():
    import numpy as np
    return np


def _zaman(sure: float):
    np = _np()
    return np.arange(int(sure * SR), dtype=np.float32) / SR


def _yanki(x, sure: float = 1.6, rt60: float = 1.4, islak: float = 0.35, tohum: int = 3):
    """Mono x -> stereo (kuru + sentetik oda yankısı)."""
    np = _np()
    from wojak.uzun import muzik
    rng = np.random.default_rng(tohum)
    ir = muzik._yanki_ir(sure, rng, rt60=rt60)
    y = muzik._evris(np.concatenate([x, np.zeros(len(ir), np.float32)]), ir)
    kuru = np.concatenate([x, np.zeros(len(ir), np.float32)])
    return kuru[:, None] * (1 - islak) + y * islak


def _supurme(sure: float, fc, bw_okt: float, tohum: int):
    """Merkez frekansı zamanla değişen (fc(u), u 0..1) bant geçiren gürültü (STFT ile şekillendirilmiş)."""
    np = _np()
    n = int(sure * SR)
    rng = np.random.default_rng(tohum)
    gur = rng.normal(0, 1, n + 2048)
    win, hop = 1024, 256
    w = np.hanning(win)
    f = np.maximum(np.fft.rfftfreq(win, 1 / SR), 1.0)
    out = np.zeros(n + win)
    for i in range(0, n, hop):
        X = np.fft.rfft(gur[i:i + win] * w)
        u = min(1.0, (i + win / 2) / n)
        g = np.exp(-0.5 * (np.log2(f / fc(u)) / bw_okt) ** 2)
        out[i:i + win] += np.fft.irfft(X * g, win) * w
    out = out[:n]
    return (out / (np.abs(out).max() + 1e-9)).astype(np.float32)


def sfx_gecis():
    """Geçiş 'whoosh'u: merkez frekansı 400 -> 2600 -> 900 Hz süpürülen gürültü, tepe 0,36 sn'de, soldan sağa
    geçer (itme geçişi ve bölüm kartı). Altında hafif hava gövdesi."""
    np = _np()
    sure, tepe = 0.95, 0.36
    t = _zaman(sure)
    fc = lambda u: 400 * (2600 / 400) ** (u / 0.38) if u < 0.38 else 2600 * (900 / 2600) ** ((u - 0.38) / 0.62)
    x = _supurme(sure, fc, 0.75, 11) + 0.45 * _supurme(sure, lambda u: 170.0, 0.6, 12)
    env = np.where(t < tepe, (t / tepe) ** 2.2, np.exp(-(t - tepe) * 5.0)).astype(np.float32)
    env[-int(0.04 * SR):] *= np.linspace(1, 0, int(0.04 * SR), dtype=np.float32)
    x = x * env
    p = np.clip((t - 0.08) / 0.62, 0, 1)
    L, R = 0.55 + 0.45 * np.cos(p * np.pi / 2), 0.55 + 0.45 * np.sin(p * np.pi / 2)
    st = np.stack([x * L, x * R], axis=1)
    return st / (np.abs(st).max() + 1e-9) * 0.85


def _motif(notalar, aralik: float, sure: float, parlak: bool):
    np = _np()
    from wojak.uzun import muzik
    n = int(sure * SR)
    x = np.zeros(n, np.float32)
    for k, m in enumerate(notalar):
        i = int(k * aralik * SR)
        v = 0.75 if k < len(notalar) - 1 else 0.95
        sig = muzik.piyano(muzik.hz(m), sure - k * aralik, v)
        sig = sig + muzik.muzik_kutusu(muzik.hz(m + 12), sure - k * aralik, v * (0.55 if parlak else 0.3))
        j = min(n, i + len(sig))
        x[i:j] += sig[: j - i]
    st = _yanki(x, 2.0, 1.8, 0.42)[:n]
    fo = int(0.3 * SR)
    st[-fo:] *= np.linspace(1, 0, fo, dtype=np.float32)[:, None]
    return st / (np.abs(st).max() + 1e-9) * 0.8


def sfx_turkiye():
    """Türkiye ses motifi (minör): Sol4 - Do5 - Mi bemol5, müzik altlığıyla aynı Do minör, piyano + müzik kutusu."""
    return _motif([67, 72, 75], 0.17, 2.2, False)


def sfx_turkiye_major():
    """Türkiye motifinin majör (çözülen) hâli: Do5 - Mi5 - Sol5 (2004 ruhsatı gibi 'kapı açıldı' anları)."""
    return _motif([72, 76, 79], 0.15, 2.2, True)


def sfx_kapi():
    """İki tok kapı vuruşu (ahşap): 0 ve 0,27 sn."""
    np = _np()
    t = _zaman(0.6)
    rng = np.random.default_rng(5)

    def vurus(t0, g):
        u = np.maximum(t - t0, 0) * (t >= t0)
        govde = 0.8 * np.sin(2 * np.pi * 105 * u) * np.exp(-34 * u) + 0.5 * np.sin(2 * np.pi * 410 * u) * np.exp(-48 * u)
        tik = (rng.normal(0, 1, len(t)) * np.exp(-140 * u)) * 0.35
        return g * (govde + tik) * (t >= t0)
    x = (vurus(0.0, 1.0) + vurus(0.27, 0.9)).astype(np.float32)
    st = _yanki(x, 0.5, 0.35, 0.25)[: len(t)]
    return st / (np.abs(st).max() + 1e-9) * 0.85


def sfx_damga():
    """Lastik damga: kâğıda inen tok gövde + kısa kâğıt şaplağı."""
    np = _np()
    t = _zaman(0.45)
    rng = np.random.default_rng(8)
    govde = 0.9 * np.sin(2 * np.pi * 72 * t) * np.exp(-20 * t) + 0.45 * np.sin(2 * np.pi * 150 * t) * np.exp(-34 * t)
    sap = rng.normal(0, 1, len(t)) * np.exp(-75 * t)
    sap = np.diff(np.concatenate([[0], sap])) * 0.9     # basit yüksek geçiren: parlak şaplak
    x = (govde + 0.5 * sap).astype(np.float32)
    st = _yanki(x, 0.4, 0.3, 0.18)[: len(t)]
    return st / (np.abs(st).max() + 1e-9) * 0.9


def sfx_geri_sarma():
    """Bant geri sarma: perdesi hızla yükselen titrek ton + hışırtı, sonunda tık."""
    np = _np()
    sure = 0.8
    t = _zaman(sure)
    f = 220 * (2400 / 220) ** (t / sure) * (1 + 0.06 * np.sin(2 * np.pi * 23 * t))
    faz = 2 * np.pi * np.cumsum(f) / SR
    ton = 0.5 * np.sign(np.sin(faz)) * 0.3 + 0.5 * np.sin(faz)
    rng = np.random.default_rng(4)
    gur = _supurme(sure, lambda u: 600 + 3000 * u, 0.8, 9) * 0.5
    env = np.minimum(1, t / 0.05) * np.where(t > sure - 0.06, (sure - t) / 0.06, 1)
    x = (ton * 0.55 + gur) * env * 0.6
    tik = np.zeros_like(t)
    i = int((sure - 0.03) * SR)
    tik[i:] = rng.normal(0, 1, len(t) - i) * np.exp(-300 * (t[i:] - t[i]))
    x = (x + 0.6 * tik).astype(np.float32)
    st = np.stack([x, x], axis=1)
    return st / (np.abs(st).max() + 1e-9) * 0.75


def sfx_raptiye():
    """Raptiye/iğne panoya batar: kuru tık + küçük metal çınlaması."""
    np = _np()
    t = _zaman(0.18)
    rng = np.random.default_rng(6)
    tik = rng.normal(0, 1, len(t)) * np.exp(-420 * t)
    tik = np.diff(np.concatenate([[0], tik]))
    cin = 0.35 * np.sin(2 * np.pi * 3300 * t) * np.exp(-55 * t) + 0.2 * np.sin(2 * np.pi * 5100 * t) * np.exp(-80 * t)
    tok = 0.5 * np.sin(2 * np.pi * 190 * t) * np.exp(-60 * t)
    x = (tik + cin + tok).astype(np.float32)
    st = np.stack([x, x], axis=1)
    return st / (np.abs(st).max() + 1e-9) * 0.8


def sfx_telefon():
    """Eski telefon zili: iki çan tonu, 20 Hz çekiç vuruşu, bir çalış (1,1 sn)."""
    np = _np()
    t = _zaman(1.25)
    zil = np.sin(2 * np.pi * 1020 * t) + 0.7 * np.sin(2 * np.pi * 1290 * t) + 0.3 * np.sin(2 * np.pi * 2550 * t)
    cekic = 0.55 + 0.45 * np.sign(np.sin(2 * np.pi * 20 * t))
    env = np.minimum(1, t / 0.01) * np.where(t < 1.0, 1.0, np.exp(-(t - 1.0) * 14))
    x = (zil * cekic * env * 0.3).astype(np.float32)
    st = _yanki(x, 0.6, 0.5, 0.2)[: len(t)]
    return st / (np.abs(st).max() + 1e-9) * 0.7


def sfx_marka():
    """Kanal imzası (sting): kısa whoosh -> Do minör piyano akoru + müzik kutusu pırıltısı + alçak boom (~2,6 sn)."""
    np = _np()
    from wojak.uzun import muzik
    sure = 2.6
    n = int(sure * SR)
    st = np.zeros((n, 2), np.float32)
    w = sfx_gecis() * 0.55
    st[: len(w)] += w[:n]
    i0 = int(0.30 * SR)
    akor = np.zeros(n - i0, np.float32)
    for m, v in ((48, 0.55), (55, 0.45), (60, 0.6), (63, 0.55), (67, 0.5)):
        sig = muzik.piyano(muzik.hz(m), sure - 0.3, v)
        akor[: len(sig)] += sig[: len(akor)]
    for k, m in enumerate((75, 79, 84)):
        sig = muzik.muzik_kutusu(muzik.hz(m), 1.8, 0.35)
        j = int((0.06 + 0.09 * k) * SR)
        akor[j:j + len(sig)] += sig[: len(akor) - j]
    tb = np.arange(len(akor), dtype=np.float32) / SR
    akor += 0.7 * np.sin(2 * np.pi * (58 - 18 * tb) * tb) * np.exp(-4.5 * tb)
    st[i0:] += _yanki(akor, 2.2, 2.0, 0.4)[: n - i0]
    fo = int(0.35 * SR)
    st[-fo:] *= np.linspace(1, 0, fo, dtype=np.float32)[:, None]
    return st / (np.abs(st).max() + 1e-9) * 0.85


def sfx_klik():
    """Fare tıkı (kapanış çağrısı, 7. tur): basma + bırakma, iki kuru plastik tık (0 ve 0,07 sn)."""
    np = _np()
    t = _zaman(0.16)
    rng = np.random.default_rng(11)
    x = np.zeros(len(t))
    for t0, g, f in ((0.0, 1.0, 3800), (0.07, 0.55, 3100)):
        u = np.clip(t - t0, 0, None) * (t >= t0)
        gur = rng.normal(0, 1, len(t)) * np.exp(-900 * u) * (t >= t0)
        ton = np.sin(2 * np.pi * f * u) * np.exp(-260 * u) * (t >= t0)
        x += g * (0.7 * np.diff(np.concatenate([[0], gur])) + 0.35 * ton)
    x = x.astype(np.float32)
    st = np.stack([x, x], axis=1)
    return st / (np.abs(st).max() + 1e-9) * 0.75


def sfx_zil():
    """Bildirim zili (kapanış çağrısı, 7. tur): küçük çan, uyumsuz kısmi tonlar (1 : 2,76 : 5,4), yumuşak sönüm."""
    np = _np()
    t = _zaman(1.4)
    f0 = 1318.5   # Mi6
    x = (np.sin(2 * np.pi * f0 * t) * np.exp(-3.2 * t) + 0.45 * np.sin(2 * np.pi * f0 * 2.76 * t) * np.exp(-6 * t)
         + 0.22 * np.sin(2 * np.pi * f0 * 5.4 * t) * np.exp(-11 * t))
    # ikinci, daha alçak vuruş (zil sallanınca): 0,16 sn
    u = np.clip(t - 0.16, 0, None)
    x += 0.5 * (t >= 0.16) * (np.sin(2 * np.pi * f0 * 0.75 * u) * np.exp(-4 * u)
                             + 0.4 * np.sin(2 * np.pi * f0 * 0.75 * 2.76 * u) * np.exp(-7 * u))
    x *= np.minimum(1, t / 0.004)
    st = _yanki(x.astype(np.float32), 1.0, 0.9, 0.25)[: len(t)]
    return st / (np.abs(st).max() + 1e-9) * 0.7


NP_SFX = {"gecis": sfx_gecis, "turkiye": sfx_turkiye, "turkiye_major": sfx_turkiye_major, "kapi": sfx_kapi,
          "damga": sfx_damga, "geri_sarma": sfx_geri_sarma, "raptiye": sfx_raptiye, "telefon": sfx_telefon,
          "marka": sfx_marka, "klik": sfx_klik, "zil": sfx_zil}


def _wav_yaz(yol: Path, st) -> None:
    import wave
    np = _np()
    st = np.asarray(st, np.float32)
    if st.ndim == 1:
        st = np.stack([st, st], axis=1)
    pcm = (np.clip(st, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(yol), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def main() -> None:
    import sys
    sys.path.insert(0, str(OUT.parent.parent))   # wojak paketi (müzik tınıları) için repo kökü
    OUT.mkdir(parents=True, exist_ok=True)
    hepsi = list(SFX) + list(NP_SFX)
    secili = sys.argv[1:] or hepsi
    for name in secili:
        if name not in SFX and name not in NP_SFX:
            sys.exit(f"bilinmeyen efekt: {name} ({', '.join(hepsi)})")
    for name in secili:
        out = OUT / f"{name}.wav"
        if name in NP_SFX:
            _wav_yaz(out, NP_SFX[name]())
        else:
            src, flt = SFX[name]
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", src, "-af", flt,
                            "-ac", "2", "-ar", "48000", str(out)], check=True)
        print(f"-> {out.name}")


if __name__ == "__main__":
    main()
