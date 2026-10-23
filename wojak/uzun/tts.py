"""Seslendirme: Google Gemini TTS (23.10.2026'dan beri) ya da Cartesia sonic-3; önbellek, yeniden deneme, sessizlik
kırpma, isteğe bağlı Whisper denetimi.

Sağlayıcı video.yaml'daki `model`den: `gemini-*` -> Gemini (UZUN_FORMAT §1.1), `sonic-*` -> Cartesia.
- Gemini: Cloud Text-to-Speech v1 `text:synthesize` (`voice.modelName` = model, `input.prompt` = tarz tarifi).
  Kimlik HIKAYE_GCP_CREDENTIALS (authorized_user JSON) ortamdan ya da ~/.config/wojak/secrets.env'den; proje
  HIKAYE_GCP_PROJECT (yoksa kimliğin gördüğü ilk etkin proje bulunur). Hız parametresi yok: ses tablosundaki taban
  hız × satırın `hiz`ı, üretimden sonra ffmpeg `atempo` ile (ton değişmez). `<break .../>` etiketleri Gemini'ye
  noktalama olarak gider ("..." ya da virgül). Ham yanıt ham/ klasöründe saklanır.
- Cartesia: POST https://api.cartesia.ai/tts/bytes, başlıklar X-API-Key + Cartesia-Version: 2025-11-04.
- Anahtarlar YALNIZ ortamdan / ~/.config/wojak/secrets.env'den (config.load_secrets) okunur; hiçbir yere
  yazılmaz, loglanmaz, hata mesajına konmaz.
- Önbellek: out/<id>-uzun/ses/ham/<anahtar>.wav (API'nin ham çıktısı) ve out/<id>-uzun/ses/<anahtar>.wav (işlenmiş).
  Anahtar = sha1(sağlayıcı, model, ses, transkript, hız, duygu/tarz, dil, sürüm). Metin değişmedikçe yeniden istek atılmaz.
- Kırpma: tüm satırlarda aynı kural (eşik + sabit ön/arka pay + kısa yumuşatma), böylece aralar tutarlı.
- Denetim (--qa): faster-whisper "medium"; sesi ffmpeg ile 16 kHz float diziye kendimiz çözeriz
  (faster_whisper'ın kendi çözücüsü kurulu PyAV ile bozuk). Listelenen isimleri duyamadığı satırları
  raporlar; döngüye girmez (en fazla --yenile kez yeniden üretir).
"""

from __future__ import annotations

import difflib
import hashlib
import json
import os
import re
import subprocess
import sys
import threading
import time
import wave
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .. import config
from .spec import Satir, Video

URL = "https://api.cartesia.ai/tts/bytes"
API_VERSION = "2025-11-04"
SR = 44100
# Genel tarayıcı kimliği (gizlilik: e-posta/kanal adı/kişisel bilgi başlıklara girmez)
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/126.0.0.0 Safari/537.36")
KIRPMA = {"esik_db": -42.0, "on_pay": 0.04, "arka_pay": 0.10, "fade_in": 0.006, "fade_out": 0.025}
SURUM = 1   # kırpma/istek biçimi değişirse artır (önbelleği geçersiz kılar)


class TTSHatasi(RuntimeError):
    pass


def ses_klasoru(v: Video) -> Path:
    return v.cikti / "ses"


def anahtar(model: str, ses_id: str, transkript: str, hiz: float, duygu: str | None, dil: str,
            deneme: int = 0) -> str:
    d = {"m": model, "v": ses_id, "t": transkript, "s": round(float(hiz), 3), "e": duygu or None, "l": dil,
         "k": KIRPMA, "r": SURUM}
    if deneme:
        d["deneme"] = deneme
    return hashlib.sha1(json.dumps(d, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:20]


# ---------------------------------------------------------------- Gemini (Google Cloud Text-to-Speech)

GEMINI_URL = "https://texttospeech.googleapis.com/v1/text:synthesize"
GEMINI_SR = 48000
GEMINI_SURUM = 1   # Gemini isteği/işleme biçimi değişirse artır
DUYGU_TARZI = {"content": "Hoşnut, kendinden emin ve güven veren bir tonla söyle."}
_GCP: dict = {}
_GCP_KILIT = threading.Lock()


_BIRLER = ["", "bir", "iki", "üç", "dört", "beş", "altı", "yedi", "sekiz", "dokuz"]
_ONLAR = ["", "on", "yirmi", "otuz", "kırk", "elli", "altmış", "yetmiş", "seksen", "doksan"]


def sayi_yazi(n: int) -> str:
    """Türkçe okunuş: 1957 -> 'bin dokuz yüz elli yedi', 10000 -> 'on bin' (0 <= n < 10^9)."""
    if n == 0:
        return "sıfır"

    def uc(k):   # 0-999
        y, r = divmod(k, 100)
        o, b = divmod(r, 10)
        return " ".join(x for x in ((("" if y == 1 else _BIRLER[y] + " ") + "yüz") if y else "", _ONLAR[o],
                                    _BIRLER[b]) if x)
    parcalar = []
    for bolen, ad in ((10 ** 6, "milyon"), (1000, "bin")):
        q, n = divmod(n, bolen)
        if q:
            parcalar.append("bin" if (q == 1 and ad == "bin") else f"{uc(q)} {ad}")
    if n:
        parcalar.append(uc(n))
    return " ".join(parcalar)


def sayilari_yaziya(s: str) -> str:
    """Rakamları yazıya çevirir, kesme işaretli eki bitiştirir: 1957'de -> 'bin dokuz yüz elli yedide', 10.000'den ->
    'on binden' (yazılı ek zaten okunuşa uyumlu). UZUN_FORMAT §1.1: sayılar yazıyla."""
    def cevir(m):
        return sayi_yazi(int(m.group(1).replace(".", ""))) + (m.group(2) or "")
    s = re.sub(r"%\s?(\d+)", lambda m: "yüzde " + m.group(1), s)
    return re.sub(r"(?<![\w.,])(\d{1,3}(?:\.\d{3})+|\d+)(?![.,]\d)(?:['’](\w+))?", cevir, s)


def gemini_metni(s: str) -> str:
    """Cartesia'nın <break time="..."/> etiketleri Gemini'de sesli okunabilir: noktalamaya çevrilir
    (>= 250 ms "...", daha kısası virgül; UZUN_FORMAT §1.1: durak için "..." ya da virgül)."""
    from .spec import BREAK_RE

    def cevir(m):
        sn = float(m.group(1)) / (1000 if m.group(2).lower() == "ms" else 1)
        return " ... " if sn >= 0.25 else ", "
    s = sayilari_yaziya(BREAK_RE.sub(cevir, s))
    s = re.sub(r"\s*([,.:;!?])\s*(\.\.\.|,)\s*", lambda m: m.group(1) + (" ... " if m.group(2) == "..." else " "), s)
    return re.sub(r"\s+,", ",", re.sub(r"[ \t]+", " ", s)).strip()


def gemini_ayari(v: Video, satir: Satir) -> dict:
    """İsteği ve işlemeyi tanımlayan her şey (önbellek anahtarı bundan): ses, tarz, tempo, metin."""
    ay = v.ses_ayari(satir.ses)
    tarz = satir.tarz if satir.tarz is not None else ay.get("tarz", "")
    if satir.duygu and satir.tarz is None:
        tarz = (tarz + " " + DUYGU_TARZI.get(str(satir.duygu), f"Duygu: {satir.duygu}.")).strip()
    return {"model": v.model, "ses": ay["gemini"], "tarz": tarz, "metin": gemini_metni(v.transkript(satir)),
            "tempo": round(float(ay.get("hiz", 1.0)) * float(satir.hiz), 4), "dil": "tr-TR" if v.dil == "tr" else v.dil}


def _gcp_kimligi() -> tuple[str, str]:
    """(erişim jetonu, proje). Jeton ~1 saat geçerli; 50 dk'da bir yenilenir. Kimlik/jeton hiçbir yere yazılmaz."""
    import requests
    with _GCP_KILIT:
        if _GCP.get("jeton") and time.time() < _GCP.get("bitis", 0):
            return _GCP["jeton"], _GCP["proje"]
        config.load_secrets()
        raw = os.environ.get("HIKAYE_GCP_CREDENTIALS", "").strip()
        if not raw:
            raise TTSHatasi("HIKAYE_GCP_CREDENTIALS yok (ortam değişkeni ya da ~/.config/wojak/secrets.env)")
        try:
            c = json.loads(raw)
            r = requests.post("https://oauth2.googleapis.com/token", timeout=60, data={
                "client_id": c["client_id"], "client_secret": c["client_secret"],
                "refresh_token": c["refresh_token"], "grant_type": "refresh_token"})
            jeton = r.json()["access_token"]
        except Exception as e:  # içerik değil yalnız tür
            raise TTSHatasi(f"Google kimliği yenilenemedi: {type(e).__name__}") from None
        proje = os.environ.get("HIKAYE_GCP_PROJECT", "").strip() or _GCP.get("proje", "")
        if not proje:
            r = requests.get("https://cloudresourcemanager.googleapis.com/v1/projects", timeout=60,
                             headers={"Authorization": f"Bearer {jeton}"}, params={"filter": "lifecycleState:ACTIVE"})
            ps = [x["projectId"] for x in r.json().get("projects", [])] if r.ok else []
            if not ps:
                raise TTSHatasi("Google projesi bulunamadı: HIKAYE_GCP_PROJECT ortam değişkenini ver")
            proje = ps[0]
        _GCP.update(jeton=jeton, proje=proje, bitis=time.time() + 50 * 60)
        return jeton, proje


def gemini_istek(ay: dict, deneme_sayisi: int = 6) -> bytes:
    """Ham WAV (LINEAR16, 48 kHz mono). 429/5xx'te üstel bekleme."""
    import base64
    import requests
    govde = {"input": {"text": ay["metin"], **({"prompt": ay["tarz"]} if ay["tarz"] else {})},
             "voice": {"languageCode": ay["dil"], "name": ay["ses"], "modelName": ay["model"]},
             "audioConfig": {"audioEncoding": "LINEAR16", "sampleRateHertz": GEMINI_SR}}
    bekle, son = 3.0, ""
    for i in range(deneme_sayisi):
        jeton, proje = _gcp_kimligi()
        try:
            r = requests.post(GEMINI_URL, json=govde, timeout=300, headers={
                "Authorization": f"Bearer {jeton}", "x-goog-user-project": proje, "User-Agent": UA})
        except requests.RequestException as e:
            son = type(e).__name__
        else:
            if r.status_code == 200:
                data = base64.b64decode(r.json()["audioContent"])
                if data[:4] == b"RIFF":
                    return data
                son = "yanıt WAV değil"
            else:
                try:
                    msg = r.json().get("error", {}).get("message", "")[:200]
                except ValueError:
                    msg = r.text[:200]
                son = f"HTTP {r.status_code}: {msg.replace(jeton, '***')}"
                if r.status_code == 401:
                    _GCP.clear()
                elif r.status_code not in (408, 409, 425, 429, 500, 502, 503, 504):
                    raise TTSHatasi(f"Gemini TTS isteği başarısız: {son}")
        if i < deneme_sayisi - 1:
            time.sleep(bekle)
            bekle = min(bekle * 2, 60)
    raise TTSHatasi(f"Gemini TTS isteği başarısız: {son}")


def tempo_uygula(x: np.ndarray, sr: int, tempo: float) -> np.ndarray:
    """ffmpeg atempo (perde korunur); 0.5-2.0 arası tek süzgeç."""
    if abs(tempo - 1.0) < 1e-3:
        return x
    pcm = (np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes()
    out = subprocess.run(["ffmpeg", "-v", "error", "-f", "s16le", "-ar", str(sr), "-ac", "1", "-i", "-",
                          "-af", f"atempo={tempo:.4f}", "-f", "s16le", "-ar", str(sr), "-ac", "1", "-"],
                         input=pcm, capture_output=True, check=True).stdout
    return np.frombuffer(out, np.int16).astype(np.float32) / 32768


def istek_govdesi(v: Video, satir: Satir) -> dict:
    gc = {"speed": round(float(satir.hiz), 3)}
    if satir.duygu:
        gc["emotion"] = str(satir.duygu)
    return {"model_id": v.model, "transcript": v.transkript(satir),
            "voice": {"mode": "id", "id": v.ses_id(satir.ses)}, "language": v.dil,
            "output_format": {"container": "wav", "encoding": "pcm_s16le", "sample_rate": SR},
            "generation_config": gc}


def _api_anahtarlari() -> list[str]:
    """CARTESIA_API_KEY, sonra CARTESIA_API_KEY_2 ... _9 (kota dolunca sıradakine geçilir)."""
    config.load_secrets()
    adlar = ["CARTESIA_API_KEY"] + [f"CARTESIA_API_KEY_{i}" for i in range(2, 10)]
    ks = []
    for a in adlar:
        k = os.environ.get(a, "").strip()
        if k and k not in ks:
            ks.append(k)
    if not ks:
        raise TTSHatasi("CARTESIA_API_KEY yok (ortam değişkeni ya da ~/.config/wojak/secrets.env)")
    return ks


_KOTASI_DOLAN: set[str] = set()  # bu süreçte 402 dönen anahtarlar (tekrar denenmez)


def _api_anahtari() -> str:
    return _api_anahtarlari()[0]


def _maskele(metin: str, anahtarlar: list[str]) -> str:
    for k in anahtarlar:
        metin = metin.replace(k, "***")
    return metin


def _istek(govde: dict, deneme_sayisi: int = 5) -> bytes:
    import requests
    anahtarlar = _api_anahtarlari()
    son_hata = ""
    for key in [k for k in anahtarlar if k not in _KOTASI_DOLAN]:
        headers = {"X-API-Key": key, "Cartesia-Version": API_VERSION, "Content-Type": "application/json",
                   "User-Agent": UA}
        bekle = 2.0
        for i in range(deneme_sayisi):
            try:
                r = requests.post(URL, headers=headers, json=govde, timeout=120)
            except requests.RequestException as e:
                son_hata = type(e).__name__
            else:
                if r.status_code == 200 and r.content[:4] == b"RIFF":
                    return r.content
                son_hata = f"HTTP {r.status_code}: {r.text[:200]}"
                if r.status_code == 402:  # kota doldu: sıradaki anahtara geç
                    _KOTASI_DOLAN.add(key)
                    break
                if r.status_code not in (408, 409, 425, 429, 500, 502, 503, 504):
                    raise TTSHatasi(f"Cartesia isteği başarısız: {_maskele(son_hata, anahtarlar)}")
                ra = r.headers.get("Retry-After")
                if ra and ra.replace(".", "", 1).isdigit():
                    bekle = max(bekle, float(ra))
            if i < deneme_sayisi - 1:
                time.sleep(bekle)
                bekle = min(bekle * 2, 30)
        else:
            break  # geçici hatalar tükendi: başka anahtarı harcamaya gerek yok
    # anahtar mesaja girmesin
    raise TTSHatasi(f"Cartesia isteği başarısız: {_maskele(son_hata, anahtarlar)}")


def wav_oku(p: Path) -> tuple[np.ndarray, int]:
    with wave.open(str(p), "rb") as w:
        sr, ch, sw = w.getframerate(), w.getnchannels(), w.getsampwidth()
        raw = w.readframes(w.getnframes())
    if sw != 2:
        raise TTSHatasi(f"{p}: 16 bit PCM bekleniyordu")
    x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    if ch > 1:
        x = x.reshape(-1, ch).mean(axis=1)
    return x, sr


def wav_yaz(p: Path, x: np.ndarray, sr: int) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    pcm = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    tmp = p.with_suffix(".tmp.wav")
    with wave.open(str(tmp), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())
    tmp.replace(p)


def sessizlik_kirp(x: np.ndarray, sr: int, k: dict = KIRPMA) -> tuple[np.ndarray, float, float]:
    """Baştaki/sondaki sessizliği tutarlı biçimde kırpar. (kırpılmış, baştan atılan sn, sondan atılan sn)."""
    if len(x) == 0:
        return x, 0.0, 0.0
    hop = int(sr * 0.01)
    n = len(x) // hop
    if n < 3:
        return x, 0.0, 0.0
    fr = x[: n * hop].reshape(n, hop)
    rms_db = 20 * np.log10(np.sqrt((fr ** 2).mean(axis=1)) + 1e-9)
    esik = max(k["esik_db"], rms_db.max() - 45)
    akt = np.where(rms_db > esik)[0]
    if len(akt) == 0:
        return x, 0.0, 0.0
    a = max(0, akt[0] * hop - int(k["on_pay"] * sr))
    b = min(len(x), (akt[-1] + 1) * hop + int(k["arka_pay"] * sr))
    y = x[a:b].copy()
    fi, fo = int(k["fade_in"] * sr), int(k["fade_out"] * sr)
    if fi and len(y) > fi:
        y[:fi] *= np.linspace(0, 1, fi, dtype=np.float32)
    if fo and len(y) > fo:
        y[-fo:] *= np.linspace(1, 0, fo, dtype=np.float32)
    return y, a / sr, (len(x) - b) / sr


@dataclass
class Sonuc:
    satir: Satir
    yer: str
    anahtar: str
    wav: Path
    sure: float
    onbellek: bool


def _yer(v: Video):
    for s in v.sahneler:
        for i, st in enumerate(s.satirlar):
            yield s, i, st


def satir_anahtari(v: Video, satir: Satir, deneme: int = 0) -> str:
    if v.saglayici == "gemini":
        d = {"g": gemini_ayari(v, satir), "k": KIRPMA, "r": GEMINI_SURUM}
        if deneme:
            d["deneme"] = deneme
        return "g" + hashlib.sha1(json.dumps(d, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:19]
    return anahtar(v.model, v.ses_id(satir.ses), v.transkript(satir), satir.hiz, satir.duygu, v.dil, deneme)


def satir_wav(v: Video, satir: Satir, deneme: int = 0) -> tuple[str, Path]:
    k = satir_anahtari(v, satir, deneme)
    return k, ses_klasoru(v) / f"{k}.wav"


def ham_uret(v: Video, satir: Satir) -> bytes:
    """Sağlayıcıdan ham WAV (önbelleğe ham/ altında yazılır)."""
    if v.saglayici == "gemini":
        return gemini_istek(gemini_ayari(v, satir))
    return _istek(istek_govdesi(v, satir))


def ham_isle(v: Video, satir: Satir, ham: Path, hedef: Path) -> None:
    """Ham çekim -> (Gemini: atempo) -> tutarlı sessizlik kırpma -> hedef wav."""
    x, sr = wav_oku(ham)
    if v.saglayici == "gemini":
        x = tempo_uygula(x, sr, gemini_ayari(v, satir)["tempo"])
    wav_yaz(hedef, sessizlik_kirp(x, sr)[0], sr)


def tekrarlar(v: Video) -> tuple[list[list[str]], list[str]]:
    """Aynı kaydı paylaşan satır grupları ve uyarılar.

    Aynı ses + aynı TTS metni + aynı hız/duygu = aynı önbellek anahtarı = AYNI dosya: ikinci satır yeniden
    seslendirilmez, birebir aynı kayıt çalar (ör. 'Tamamen zehirsiz.' açılışta ve sonda). Görünen metni ve sesi
    aynı ama ayarı (hiz, duygu, tts) farklı satırlar ayrı kayıt olur: uyarı verilir."""
    gruplar: dict[str, list[str]] = {}
    metinler: dict[tuple[str, str], list[tuple[str, str]]] = {}
    for s, i, st in _yer(v):
        k, _ = satir_wav(v, st)
        yer = f"{s.yer}, satır {i + 1}"
        gruplar.setdefault(k, []).append(yer)
        metinler.setdefault((st.ses, st.altyazi), []).append((k, yer))
    tekrar = [y for y in gruplar.values() if len(y) > 1]
    uyari = []
    for (ses, metin), lst in metinler.items():
        if len({k for k, _ in lst}) > 1:
            uyari.append(f"'{metin[:40]}' ({ses}) {len(lst)} kez ama farklı ayarla (hiz/duygu/tts): aynı kayıt "
                         f"çalmaz — {'; '.join(y for _, y in lst)}")
    return tekrar, uyari


def manifest_yolu(v: Video) -> Path:
    return ses_klasoru(v) / "manifest.json"


def _manifest(v: Video) -> dict:
    try:
        return json.loads(manifest_yolu(v).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def sureleri_yukle(v: Video, zorunlu: bool = True) -> list[str]:
    """Önbellekteki seslerle satır sürelerini doldurur. Eksik satırların yerlerini döndürür.
    Manifest'te QA sonrası yeniden üretilmiş (deneme>0) bir sürüm varsa o kullanılır."""
    man = _manifest(v)
    eksik = []
    for s, i, st in _yer(v):
        k0, p0 = satir_wav(v, st)
        p = p0
        alt = man.get("secim", {}).get(k0)
        if alt and (ses_klasoru(v) / f"{alt}.wav").exists():
            p = ses_klasoru(v) / f"{alt}.wav"
        if p.exists():
            st.wav = p
            with wave.open(str(p), "rb") as w:
                st.sure = w.getnframes() / w.getframerate()
            st.tahmini = False
        else:
            eksik.append(f"{s.yer}, satır {i + 1}")
    return eksik


def seslendir(v: Video, yeniden: bool = False, log=print, paralel: int | None = None) -> list[Sonuc]:
    """Bütün satırları seslendirir (önbellekte olanlar atlanır). Gemini'de ham çekimler `paralel` (varsayılan 4)
    eşzamanlı istekle alınır; Cartesia sırayla."""
    out = []
    ham = ses_klasoru(v) / "ham"
    ham.mkdir(parents=True, exist_ok=True)
    man = _manifest(v)
    secim = man.get("secim", {})
    toplam = sum(1 for _ in _yer(v))
    plan = []
    for n, (s, i, st) in enumerate(_yer(v), 1):
        k, p = satir_wav(v, st)
        if secim.get(k) and not yeniden:
            k2 = secim[k]
            p2 = ses_klasoru(v) / f"{k2}.wav"
            if p2.exists():
                k, p = k2, p2
        plan.append((n, s, i, st, k, p))
    gerek = {}   # ham dosya -> (n, yer, satir): aynı anahtarı paylaşan satırlar tek istek
    for n, s, i, st, k, p in plan:
        hp = ham / f"{k}.wav"
        if (not p.exists() or yeniden) and (not hp.exists() or yeniden):
            gerek.setdefault(hp, (n, f"{s.yer}, satır {i + 1}", st))

    def al(item):
        hp, (n, yer, st) = item
        t0 = time.time()
        hp.write_bytes(ham_uret(v, st))
        log(f"  [{n}/{toplam}] {yer}: {st.ses} {time.time() - t0:.1f} sn  «{st.altyazi[:60]}»")
        if v.saglayici != "gemini":
            time.sleep(0.2)
    isci = (paralel or 4) if v.saglayici == "gemini" else 1
    if isci > 1 and len(gerek) > 1:
        with ThreadPoolExecutor(isci) as ex:
            list(ex.map(al, gerek.items()))
    else:
        for it in gerek.items():
            al(it)
    for n, s, i, st, k, p in plan:
        yer = f"{s.yer}, satır {i + 1}"
        onb = p.exists() and not yeniden and (ham / f"{k}.wav") not in gerek
        if not p.exists() or yeniden:
            ham_isle(v, st, ham / f"{k}.wav", p)
        with wave.open(str(p), "rb") as w:
            sure = w.getnframes() / w.getframerate()
        st.wav, st.sure, st.tahmini = p, sure, False
        out.append(Sonuc(st, yer, k, p, sure, onb))
    man["satirlar"] = [{"yer": r.yer, "anahtar": r.anahtar, "ses": r.satir.ses, "sure": round(r.sure, 3),
                        "metin": r.satir.altyazi, "transkript": v.transkript(r.satir)} for r in out]
    man["secim"] = secim
    manifest_yolu(v).write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


# ---------------------------------------------------------------- QA (faster-whisper)

def tr_norm(s: str) -> str:
    s = s.replace("İ", "i").replace("I", "ı").lower()
    s = re.sub(r"[^\w\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def ascii_kat(s: str) -> str:
    return s.translate(str.maketrans("çğıöşüâîû", "cgiosuaiu"))


def isim_duyuldu_mu(isim: str, duyulan: str, okunus: str | None = None, esik: float = 0.72) -> tuple[bool, float]:
    """isim (ya da TTS okunuşu) duyulan metinde benzer bir kelime öbeği olarak geçiyor mu?"""
    hedefler = [ascii_kat(tr_norm(isim))] + ([ascii_kat(tr_norm(okunus))] if okunus else [])
    kel = ascii_kat(tr_norm(duyulan)).split()
    en_iyi = 0.0
    for h in hedefler:
        n = max(1, len(h.split()))
        for L in {n, n + 1, max(1, n - 1)}:
            for i in range(0, max(1, len(kel) - L + 1)):
                parca = " ".join(kel[i:i + L])
                # ekler (Aygün'ün -> aygunun) ve bitişik yazım (vido kindlentz) eşleşmeyi bozmasın:
                # hedef uzunluğunda önek ve sonek de dene
                for aday in (parca, parca[: len(h) + 1], parca[: len(h)], parca[-len(h):], parca[-len(h) - 1:]):
                    r = difflib.SequenceMatcher(None, h, aday).ratio()
                    en_iyi = max(en_iyi, r)
    return en_iyi >= esik, round(en_iyi, 3)


SAYI_KOKLERI = ("bir", "iki", "uc", "dort", "bes", "alti", "yedi", "sekiz", "dokuz", "on", "yirmi", "otuz", "kirk",
                "elli", "altmis", "yetmis", "seksen", "doksan", "yuz", "bin", "milyon", "milyar")


def _sayi_kelimesi(k: str) -> bool:
    """'kırk', 'binden', 'kırkı', 'yirmi' gibi yazıyla sayı (Whisper bunları rakamla yazar)."""
    return any(k == r or (k.startswith(r) and len(k) - len(r) <= 3 and r not in ("bir", "on", "uc", "yuz"))
               for r in SAYI_KOKLERI)


def _sayisiz(s: str) -> list[str]:
    """Karşılaştırma için kelimeler: kesme işareti birleşir (Fakültesi'nden -> fakultesinden), rakamlı ve yazıyla
    sayı kelimeleri atılır (Whisper sayıları rakamla yazar, metin yazıyla)."""
    s = re.sub(r"['’`]", "", s)
    return [k for k in ascii_kat(tr_norm(s)).split() if not any(ch.isdigit() for ch in k) and not _sayi_kelimesi(k)]


def kelime_farklari(beklenen: str, duyulan: str, esik: float = 0.96, haric: list[str] | None = None) -> list[str]:
    """Beklenen metinde olup duyulanda benzeri (>= esik) bulunmayan kelimeler (isimler `haric`te: ayrıca puanlanır).
    Eşik 0.96: tek harflik kayıplar da yakalanır ('denenmiyor' -> 'denemiyor' 0.95, 'çalışanının' -> 'çalışanın'
    0.90, 'cüzzam' -> 'cüzdan'); kısa kelimeler (< 4 harf) ve rakamlı kelimeler atlanır. Whisper'ın kendi
    yanlışları da işaretlenebilir: rapor dinleyip karar vermek içindir."""
    duy = _sayisiz(duyulan)
    bitisik = "".join(ascii_kat(tr_norm(re.sub(r"['’`]", "", duyulan))).split())   # 'bir çoğunda' / 'Sıkanlatılan'
    ad = set()
    for h in haric or []:
        ad |= set(_sayisiz(h))
    out = []
    for k in _sayisiz(beklenen):
        if len(k) < 4 or k in ad or any(k.startswith(a if len(a) < 5 else a[:5]) for a in ad if len(a) >= 3):
            continue
        if k in bitisik:
            continue
        en = max((difflib.SequenceMatcher(None, k, d).ratio() for d in duy), default=0.0)
        if en < esik:
            out.append(k)
    return out


def satirdaki_isimler(v: Video, satir: Satir) -> list[str]:
    adaylar = list(dict.fromkeys(v.qa_isimler + list(v.telaffuz)))
    m = tr_norm(satir.altyazi)
    return [a for a in adaylar if tr_norm(a) and tr_norm(a) in m]


def wav_16k(p: Path) -> np.ndarray:
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(p), "-ac", "1", "-ar", "16000",
                                   "-f", "f32le", "-"])
    return np.frombuffer(raw, np.float32).copy()


_MODEL = None


def _model():
    global _MODEL
    if _MODEL is None:
        from faster_whisper import WhisperModel
        _MODEL = WhisperModel("medium", device="cpu", compute_type="int8")
    return _MODEL


def yaziya_dok(p: Path, dil: str = "tr", ipucu: str | None = None) -> str:
    segs, _ = _model().transcribe(wav_16k(p), language=dil, beam_size=5, vad_filter=False,
                                  condition_on_previous_text=False)
    return " ".join(s.text.strip() for s in segs).strip()


def qa(v: Video, yenile: int = 0, log=print, tum: bool = False) -> list[dict]:
    """İsim geçen satırları (tum=True: bütün satırları) Whisper ile dinler; duyulmayan isimleri ve isim dışı
    kelime farklarını (kelime_farklari) raporlar: ikisinden biri varsa "KONTROL ET".
    yenile>0: başarısız satırları en fazla o kadar kez yeniden üretir (önbellek anahtarına deneme no eklenir),
    en iyi sonucu seçer (manifest 'secim'). Asla sonsuz döngüye girmez."""
    sonuc = []
    man = _manifest(v)
    secim = man.setdefault("secim", {})
    for s, i, st in _yer(v):
        isimler = satirdaki_isimler(v, st)
        if not isimler and not tum:
            continue
        k0, p0 = satir_wav(v, st)
        aday = secim.get(k0, k0)
        p = ses_klasoru(v) / f"{aday}.wav"
        if not p.exists():
            p, aday = p0, k0
        if not p.exists():
            sonuc.append({"yer": f"{s.yer}, satır {i + 1}", "durum": "ses yok", "isimler": isimler})
            continue

        def puanla(path):
            duy = yaziya_dok(path, v.dil)
            r = [(a, *isim_duyuldu_mu(a, duy, v.telaffuz.get(a))) for a in isimler]
            return duy, r

        duy, r = puanla(p)
        deneme = 0
        while not all(ok for _, ok, _ in r) and deneme < yenile:
            deneme += 1
            k2, p2 = satir_wav(v, st, deneme)
            if not p2.exists():
                hp = ses_klasoru(v) / "ham" / f"{k2}.wav"
                if not hp.exists():
                    hp.write_bytes(ham_uret(v, st))
                ham_isle(v, st, hp, p2)
            duy2, r2 = puanla(p2)
            if sum(ok for _, ok, _ in r2) > sum(ok for _, ok, _ in r) or \
                    (sum(ok for _, ok, _ in r2) == sum(ok for _, ok, _ in r) and
                     sum(x for _, _, x in r2) > sum(x for _, _, x in r)):
                duy, r, aday = duy2, r2, k2
                secim[k0] = k2
        fark = kelime_farklari(st.altyazi, duy, haric=isimler + [v.telaffuz.get(a, a) for a in isimler])
        durum = "tamam" if all(ok for _, ok, _ in r) and not fark else "KONTROL ET"
        kayit = {"yer": f"{s.yer}, satır {i + 1}", "durum": durum, "metin": st.altyazi, "duyulan": duy,
                 "isimler": [{"isim": a, "duyuldu": ok, "benzerlik": x} for a, ok, x in r],
                 "kelime_farki": fark, "anahtar": aday, "deneme": deneme}
        sonuc.append(kayit)
        log(f"  {durum:<10} {kayit['yer']}: " + ", ".join(f"{a} {'✓' if ok else '✗'}{x:.2f}" for a, ok, x in r)
            + (f" fark: {', '.join(fark)}" if fark else "") + f"  | duyulan: {duy[:90]}")
    man["qa"] = sonuc
    manifest_yolu(v).write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding="utf-8")
    return sonuc


if __name__ == "__main__":  # küçük deneme: python -m wojak.uzun.tts "metin"
    from .spec import yukle_sozluk
    vv = yukle_sozluk({"id": "deneme", "baslik": "d", "bolumler": [{"baslik": "a", "sahneler": [
        {"tip": "bolum_karti", "baslik": "x", "satirlar": [sys.argv[1] if len(sys.argv) > 1 else "Merhaba."]}]}]},
        config.ROOT)
    for r in seslendir(vv):
        print(r.wav, round(r.sure, 2))
