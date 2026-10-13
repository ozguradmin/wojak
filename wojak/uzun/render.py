"""Kare kare render (PIL/numpy), paralel parça kodlama, kayıpsız birleştirme, ses ekleme, senkron doğrulama.

Akış
1. Zaman çizelgesi (zaman.py) her sahneye kare aralığı verir. Sahneler en fazla PARCA_KARE karelik parçalara
   bölünür; her parça ayrı bir süreçte çizilip AYNI kodlayıcı ayarlarıyla (libx264, -bf 0, yuv420p, 30 fps,
   crf 18) ayrı bir mp4'e yazılır. Parçanın anahtarı (sahne içeriği + görsel dosya tarihleri + kod sürümü)
   değişmediyse yeniden çizilmez (önbellek: out/<id>/parca/).
2. Parçalar concat demuxer ile `-c copy` birleştirilir (yeniden kodlama yok).
3. Ses (ses.py) aynı zaman çizelgesinden kurulur; AAC 48 kHz ile eklenir; video ve ses 0.000'da başlar,
   süreler 1 kareden az farklı olmalı (dogrula()).

Geçişler yeni sahnenin ilk karelerinde olur (önceki sahne süresinin ötesinde çizilmeye devam eder):
kesme | gecis (8 kare crossfade) | kaydir (10 kare push). Filigran geçişten sonra eklenir.
"""

from __future__ import annotations

import concurrent.futures as cf
import hashlib
import json
import multiprocessing as mp
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from .. import config
from . import FPS, H as H_TAM, W as W_TAM
from . import easing as E
from .spec import Sahne, Video
from .zaman import Zaman

PARCA_KARE = 180
# x264 hız ayarı: 1080p'de 4 çekirdekte medium ~21 kare/sn, faster ~48 kare/sn (crf 18'de dosya boyu ve görüntü
# farkı küçük; YouTube zaten yeniden kodlar). Darboğaz kodlayıcı olmasın diye varsayılan 'faster'.
PRESET = "faster"
# Renk: RGB -> YUV dönüşümü BT.709 matrisiyle yapılır VE akış BT.709 olarak etiketlenir. Etiketsiz HD'yi YouTube
# ve tarayıcılar BT.709 diye çözer; swscale ise varsayılan olarak BT.601 ile dönüştürüyordu: Türkiye yeşili
# (60,255,140) (45,229,138), kırmızı (204,24,30) (219,42,28) görünüyordu. Bütün parçalarda aynı bayraklar:
# concat -c copy geçerli kalır.
RENK = ["-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p", "-colorspace", "bt709",
        "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv"]
KODLAYICI = [*RENK, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-bf", "0", "-profile:v", "high", "-g", "60",
             "-video_track_timescale", "15360"]


def kod_surumu() -> str:
    """Motor kodunun özeti: kod değişince parça önbelleği geçersizleşir."""
    h = hashlib.sha1()
    pk = Path(__file__).resolve().parent
    # yalnız görüntüyü etkileyen modüller (ses/TTS/paket değişince parçalar yeniden çizilmesin; zamanlama zaten
    # sahne imzasında)
    gorsel = ("sahneler.py", "cizim.py", "harita.py", "easing.py", "render.py", "__init__.py", "zemin.py", "ust.py",
              "bilgi.py", "kanal.py")
    for p in [pk / n for n in gorsel] + [pk.parent / n for n in ("text.py", "facing.py", "config.py")]:
        h.update(p.read_bytes())
    return h.hexdigest()[:12]


def _imza(o):
    if isinstance(o, Path):
        try:
            return f"{o}:{o.stat().st_mtime_ns}:{o.stat().st_size}"
        except OSError:
            return str(o)
    if isinstance(o, dict):
        return {str(k): _imza(v) for k, v in sorted(o.items(), key=lambda kv: str(kv[0]))}
    if isinstance(o, (list, tuple)):
        return [_imza(x) for x in o]
    if isinstance(o, float):
        return round(o, 5)
    return o


def sahne_imzasi(s: Sahne) -> dict:
    return _imza({"tip": s.tip, "p": s.p, "n": s.n_kare, "gecis": [s.gecis, s.gecis_kare],
                  "satirlar": [[st.metin, st.t0, st.sure, st.balon, st.konusan,
                                Path(st.wav).name if (st.wav and (st.balon or st.konusan)) else None]
                               for st in s.satirlar],
                  "olaylar": [[o.tip, o.zaman, o.p] for o in s.olaylar], "kose": s.kose, "f": s.filigran})


def bindirme_mi(s: Sahne) -> bool:
    """Önceki sahnenin son karesi üstüne çizilen sahne (bindirme bölüm kartı, marka, bitiş)."""
    return bool(s.p.get("bindirme")) and s.tip in ("bolum_karti", "marka", "bitis")


def onceki_imzasi(z: Zaman, i: int) -> list:
    """Bindirme sahnesinin bağlı olduğu önceki sahnelerin imzası (zincir: bindirme üstüne bindirme)."""
    out = []
    while i > 0 and bindirme_mi(z.sahneler[i]):
        i -= 1
        out.append(sahne_imzasi(z.sahneler[i]))
    return out


@dataclass
class Parca:
    no: int
    sahne_i: int
    k0: int
    k1: int
    anahtar: str
    yol: Path


def parcalar(v: Video, z: Zaman, klasor: Path, W: int, H: int, kod: dict, max_kare: int = PARCA_KARE,
             filigran: str | None = None) -> list[Parca]:
    ks = kod_surumu()
    out = []
    for i, s in enumerate(z.sahneler):
        n = s.n_kare
        k = max(1, -(-n // max_kare))
        sinirlar = [round(n * j / k) for j in range(k + 1)]
        imza = sahne_imzasi(s)
        onceki = sahne_imzasi(z.sahneler[i - 1]) if i > 0 and s.gecis != "kesme" else None
        bagli = onceki_imzasi(z, i)
        for a, b in zip(sinirlar, sinirlar[1:]):
            d = {"s": imza, "k": [a, b], "wh": [W, H], "fps": z.fps, "kod": kod, "ks": ks, "f": filigran,
                 "o": onceki if a < s.gecis_kare else None, "b": bagli}
            key = hashlib.sha1(json.dumps(d, sort_keys=True, ensure_ascii=False, default=str).encode()).hexdigest()[:16]
            out.append(Parca(len(out), i, a, b, key, klasor / f"{len(out):04d}_s{i:03d}_{key}.mp4"))
    return out


def gecis_uygula(tip: str, onceki: Image.Image, simdiki: Image.Image, j: int, k: int) -> Image.Image:
    p = (j + 1) / (k + 1)
    if tip == "gecis":
        return Image.blend(onceki, simdiki, E.in_out_sine(p))
    if tip == "kaydir":
        W, H = simdiki.size
        off = int(round(W * E.in_out_cubic(p)))
        out = Image.new("RGB", (W, H))
        out.paste(onceki, (-off, 0))
        out.paste(simdiki, (W - off, 0))
        return out
    return simdiki


def son_kare(v: Video, z: Zaman, i: int, W: int, H: int, derinlik: int = 0) -> Image.Image:
    """i. sahnenin son karesi (filigransız); bindirme sahnesi ise kendi öncülünü de çizer."""
    from .sahneler import Baglam, cizici
    c = Baglam(v, W, H, z.fps)
    s = z.sahneler[i]
    cz = cizici(s, c)
    if bindirme_mi(s) and i > 0 and derinlik < 4:
        cz.dondur(son_kare(v, z, i - 1, W, H, derinlik + 1))
    return cz.kare(s.sure_hesap - 1 / z.fps)


class KareUretici:
    """Bir sahnenin (geçiş ve filigran dahil) son karelerini üretir."""

    def __init__(self, v: Video, z: Zaman, i: int, W: int, H: int):
        from .sahneler import Baglam, cizici, filigran_katmani
        self.c = Baglam(v, W, H, z.fps)
        self.s = z.sahneler[i]
        self.cz = cizici(self.s, self.c)
        if bindirme_mi(self.s) and i > 0:
            self.cz.dondur(son_kare(v, z, i - 1, W, H))
        self.onceki = None
        if i > 0 and self.s.gecis != "kesme" and self.s.gecis_kare > 0:
            self.onceki_s = z.sahneler[i - 1]
            self.onceki = cizici(self.onceki_s, self.c)
            if bindirme_mi(self.onceki_s) and i > 1:
                self.onceki.dondur(son_kare(v, z, i - 2, W, H))
        self.wm = filigran_katmani(v.filigran, self.c) if (v.filigran and self.s.filigran) else None
        self.fps = z.fps

    def kare(self, k: int) -> Image.Image:
        t = k / self.fps
        im = self.cz.kare(t)
        if self.onceki is not None and k < self.s.gecis_kare:
            pim = self.onceki.kare(self.onceki_s.sure_hesap + k / self.fps)
            im = gecis_uygula(self.s.gecis, pim, im, k, self.s.gecis_kare)
        if self.wm is not None:
            lay, x, y = self.wm
            im.paste(lay, (x, y), lay)
        return im


def _parca_isle(args) -> tuple[int, int, float]:
    v, z, p, W, H, kod = args
    t0 = time.time()
    ku = KareUretici(v, z, p.sahne_i, W, H)
    tmp = p.yol.with_suffix(".tmp.mp4")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(z.fps), "-i", "-", *KODLAYICI, "-preset", kod["preset"], "-crf", str(kod["crf"]),
           "-r", str(z.fps), "-f", "mp4", str(tmp)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    try:
        for k in range(p.k0, p.k1):
            proc.stdin.write(ku.kare(k).tobytes())
    finally:
        proc.stdin.close()
        if proc.wait() != 0:
            raise RuntimeError(f"ffmpeg parça {p.no} kodlaması başarısız")
    tmp.replace(p.yol)
    return p.no, p.k1 - p.k0, time.time() - t0


def video_render(v: Video, z: Zaman, cikti: Path, W: int = W_TAM, H: int = H_TAM, isci: int = 3,
                 onizleme: bool = False, aralik: tuple[float, float] | None = None, preset: str = PRESET,
                 log=print) -> dict:
    """Sessiz videoyu üretir. aralik=(bas, bit) sn: yalnız o aralığa değen parçalar (ön izleme)."""
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg bulunamadı")
    kod = {"preset": "veryfast", "crf": 23} if onizleme else {"preset": preset, "crf": 18}
    klasor = v.cikti / ("parca_onizleme" if onizleme else "parca")
    klasor.mkdir(parents=True, exist_ok=True)
    ps = parcalar(v, z, klasor, W, H, kod, filigran=v.filigran)
    if aralik:
        a, b = aralik
        ps = [p for p in ps if (z.sahneler[p.sahne_i].bas_kare + p.k1) / z.fps > a and
              (z.sahneler[p.sahne_i].bas_kare + p.k0) / z.fps < b]
    gerekli = [p for p in ps if not p.yol.exists()]
    log(f"parça: {len(ps)} ({len(ps) - len(gerekli)} önbellekte), {W}x{H}, {isci} işçi")
    t0 = time.time()
    kare_say = 0
    if gerekli:
        sirali = sorted(gerekli, key=lambda p: -(p.k1 - p.k0))
        isler = [(v, z, p, W, H, kod) for p in sirali]
        if isci <= 1:
            sonuclar = map(_parca_isle, isler)
            for no, n, sn in sonuclar:
                kare_say += n
                log(f"  parça {no + 1}: {n} kare, {sn:.1f} sn ({n / max(sn, 1e-6):.1f} kare/sn)")
        else:
            with cf.ProcessPoolExecutor(max_workers=isci, mp_context=mp.get_context("fork")) as ex:
                for no, n, sn in ex.map(_parca_isle, isler):
                    kare_say += n
                    log(f"  parça {no + 1}: {n} kare, {sn:.1f} sn ({n / max(sn, 1e-6):.1f} kare/sn)")
    gecen = time.time() - t0
    # eski (artık kullanılmayan) parçaları temizle
    if not aralik:
        gecerli = {p.yol.name for p in parcalar(v, z, klasor, W, H, kod, filigran=v.filigran)}
        for f in klasor.glob("*.mp4"):
            if f.name not in gecerli:
                f.unlink()
    liste = klasor / "liste.txt"
    liste.write_text("".join(f"file '{p.yol.resolve()}'\n" for p in ps), encoding="utf-8")
    cikti.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(liste),
                    "-c", "copy", "-movflags", "+faststart", str(cikti)], check=True)
    ilk = z.sahneler[ps[0].sahne_i].bas_kare + ps[0].k0 if ps else 0
    return {"parca": len(ps), "cizilen_kare": kare_say, "sure_sn": round(gecen, 1),
            "kare_hizi": round(kare_say / gecen, 2) if gecen > 0 and kare_say else None, "ilk_kare": ilk}


def birlestir(video: Path, ses: Path, cikti: Path, ss_v: float | None = None, ss_a: float | None = None,
              sure: float | None = None) -> Path:
    """Videoya sesi ekler (AAC 48 kHz). ss_v/ss_a/sure verilirse (ön izleme aralığı) kırpılır, yeniden kodlanır."""
    if sure is None:
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-i", str(ses), "-map", "0:v", "-map", "1:a",
               "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-metadata:s:a:0", "language=tur",
               "-movflags", "+faststart", str(cikti)]
    else:   # kare/örnek hassasiyetinde kırp (-ss ile kayan kesirli kare başlangıcı olmasın)
        k0, nk = int(round((ss_v or 0) * FPS)), int(round(sure * FPS))
        a0, na = int(round((ss_a or 0) * 48000)), nk * 48000 // FPS
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-i", str(ses),
               "-filter_complex", f"[0:v]trim=start_frame={k0}:end_frame={k0 + nk},setpts=PTS-STARTPTS[v];"
                                  f"[1:a]atrim=start_sample={a0}:end_sample={a0 + na},asetpts=PTS-STARTPTS[a]",
               "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
               "-pix_fmt", "yuv420p", "-bf", "0", "-r", str(FPS), *RENK[2:],
               "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-movflags", "+faststart", str(cikti)]
    subprocess.run(cmd, check=True)
    return cikti


def dogrula(mp4: Path, beklenen_kare: int | None = None, fps: int = FPS) -> dict:
    """Video ve ses 0'da mı başlıyor, süreler 1 kareden az mı farklı?"""
    r = subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-show_entries",
                        "stream=codec_type,start_time,duration,nb_read_packets,sample_rate,width,height,r_frame_rate",
                        "-of", "json", str(mp4)], capture_output=True, text=True, check=True)
    d = {}
    for s in json.loads(r.stdout)["streams"]:
        d[s["codec_type"]] = s
    v, a = d.get("video", {}), d.get("audio", {})
    vd, ad = float(v.get("duration", 0)), float(a.get("duration", 0))
    out = {"video_basi": float(v.get("start_time", 0)), "ses_basi": float(a.get("start_time", 0)),
           "video_sure": vd, "ses_sure": ad, "fark_sn": round(ad - vd, 4), "kare": int(v.get("nb_read_packets", 0)),
           "boyut": f"{v.get('width')}x{v.get('height')}", "fps": v.get("r_frame_rate"),
           "ses_hz": a.get("sample_rate")}
    out["senkron_ok"] = (abs(out["video_basi"]) < 1e-3 and abs(out["ses_basi"]) < 1e-3 and abs(ad - vd) < 1 / fps)
    if beklenen_kare is not None:
        out["beklenen_kare"] = beklenen_kare
        out["kare_ok"] = out["kare"] == beklenen_kare
    return out


def tek_kare(v: Video, z: Zaman, t: float, W: int = W_TAM, H: int = H_TAM) -> Image.Image:
    """Mutlak t anının karesi (kontrol için)."""
    k = min(int(round(t * z.fps)), z.toplam_kare - 1)
    for i, s in enumerate(z.sahneler):
        if s.bas_kare <= k < s.bas_kare + s.n_kare:
            return KareUretici(v, z, i, W, H).kare(k - s.bas_kare)
    raise ValueError(t)
