"""Uzun format komutları: python -m wojak uzun <komut> uzun/<id> [seçenekler]

    kontrol     spesifikasyon + zaman çizelgesi + hareket/bölüm/altyazı denetimi (ses yoksa süreler tahmini)
    seslendir   Cartesia TTS (önbellekli). --qa: Whisper ile isim denetimi; --yenile N: başarısızları N kez yeniden üret
    onizle      yarım çözünürlük (960x540) hızlı ön izleme; --bas 1:10 --bit 2:00 ile yalnız bir aralık
    render      1920x1080 30 fps, -14 LUFS; + .srt, anlatım izi, ölçümler (out/<id>/)
    kare        tek kare(ler): --t 12.5 --t 1:03
    kucukresim  1280x720 küçük resim varyantları
    paket       paylasim.md + .srt (out/<id>/)
    teslim      out/<id>/ -> teslim/<id>-uzun/ (video git'e girmez)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import time
from pathlib import Path

from .. import config
from . import FPS, altyazi, kucukresim, paket, render, ses, spec, tts, zaman
from .sahneler import vuruslar


def _t(s: str) -> float:
    """'75', '1:15', '0:01:15.5' -> saniye"""
    p = [float(x) for x in str(s).split(":")]
    t = 0.0
    for x in p:
        t = t * 60 + x
    return t


def _yukle(yol: str, tahmin: bool = True, log=print):
    v = spec.yukle(yol)
    eksik_dosya = spec.eksik_dosyalar(v)
    if eksik_dosya:
        raise spec.SpecHatasi("dosya yok:\n  " + "\n  ".join(eksik_dosya))
    eksik = tts.sureleri_yukle(v)
    if eksik and not tahmin:
        raise spec.SpecHatasi(f"{len(eksik)} satırın sesi yok (ilki: {eksik[0]}). Önce: python -m wojak uzun "
                              f"seslendir {yol}  (ya da --tahmini ile sessiz dene)")
    if eksik:
        log(f"not: {len(eksik)} satırın sesi yok, süreler metinden TAHMİN edildi")
    z = zaman.hesapla(v, tahmin=True)
    return v, z


def ozet(v, z, log=print) -> None:
    log(f"{v.id}: {zaman.zaman_str(z.sure)} ({z.sure:.1f} sn, {z.toplam_kare} kare), {len(z.sahneler)} sahne, "
        f"{len(v.bolumler)} bölüm, {sum(len(s.satirlar) for s in z.sahneler)} satır")
    bi = -1
    for s in z.sahneler:
        if s.bolum != bi:
            bi = s.bolum
            b = v.bolumler[bi]
            log(f"  ── {zaman.zaman_str(z.sahne_basi(s))}  BÖLÜM: {b.baslik}")
        ilk = s.satirlar[0].altyazi if s.satirlar else (s.p.get("baslik") or s.p.get("metin") or "")
        g = "" if s.gecis == "kesme" else f" [{s.gecis}]"
        log(f"     {zaman.zaman_str(z.sahne_basi(s), ms=True):>9}  {s.tip:<15} {s.sure_hesap:5.1f}s{g:<9} "
            f"{str(ilk)[:62]}")


def hareket_denetimi(v, z) -> list[str]:
    """Ekranda en geç max_bos sn'de bir yeni bir şey olmalı (UZUN_FORMAT §2)."""
    lim = v.zamanlama["max_bos"]
    anlar = []
    for s in z.sahneler:
        b = z.sahne_basi(s)
        anlar += [b + t for t in vuruslar(s)]
    anlar = sorted(set(round(a, 2) for a in anlar)) + [z.sure]
    out = []
    for a, b in zip(anlar, anlar[1:]):
        if b - a > lim:
            out.append(f"{zaman.zaman_str(a)}-{zaman.zaman_str(b)}: {b - a:.1f} sn ekranda yeni bir şey yok "
                       f"(sınır {lim:.0f} sn) — olay ekle (kelime, isim, yuz, balon...) ya da sahneyi böl")
    return out


def cmd_kontrol(a) -> None:
    v, z = _yukle(a.yol)
    ozet(v, z)
    u = hareket_denetimi(v, z) + paket.uyarilar(v, z) + altyazi.denetle(altyazi.parcalar(z))
    for x in u:
        print(f"  ⚠ {x}")
    print("bölümler:\n" + paket.bolum_metni(paket.bolum_damgalari(z)))
    if not u:
        print("denetim: sorun yok")


def cmd_seslendir(a) -> None:
    v = spec.yukle(a.yol)
    t0 = time.time()
    sonuc = tts.seslendir(v, yeniden=a.yeniden)
    yeni = sum(1 for r in sonuc if not r.onbellek)
    print(f"{len(sonuc)} satır ({yeni} yeni, {len(sonuc) - yeni} önbellekte), toplam ses "
          f"{sum(r.sure for r in sonuc):.1f} sn, {time.time() - t0:.1f} sn")
    if a.qa:
        print("Whisper denetimi (faster-whisper medium):")
        q = tts.qa(v, yenile=a.yenile)
        kotu = [x for x in q if x["durum"] != "tamam"]
        print(f"denetim: {len(q)} satır, {len(kotu)} kontrol gerektiriyor "
              f"(rapor: {tts.manifest_yolu(v)})")


def _ses_anahtari(v, z) -> str:
    d = {"s": [[round(sz.bas, 4), Path(sz.satir.wav).name if sz.satir.wav else None] for sz in z.satirlar()],
         "x": [[round(t, 4), x.ad, x.db] for t, x in zaman.tum_sfx(z)], "m": {k: str(x) for k, x in v.muzik.items()},
         "n": z.toplam_kare, "o": v.otomatik_sfx,
         "k": [s.otomatik_sfx for s in z.sahneler], "e": [list(e) for e in ses.otomatik_efektler(z)],
         "c": hashlib.sha1((Path(ses.__file__).read_bytes() + Path(ses.muzik.__file__).read_bytes())).hexdigest()}
    return hashlib.sha1(json.dumps(d, sort_keys=True, default=str).encode()).hexdigest()[:12]


def _ses(v, z, log=print) -> dict:
    klasor = config.OUT / v.id / "ses_miks"
    key = _ses_anahtari(v, z)
    bilgi_yol = klasor / f"bilgi_{key}.json"
    if bilgi_yol.exists():
        b = json.loads(bilgi_yol.read_text(encoding="utf-8"))
        if Path(b["ses"]).exists():
            log("ses: önbellekte")
            return b
    t0 = time.time()
    for f in klasor.glob("bilgi_*.json"):
        f.unlink()
    b = ses.miks(v, z, klasor, log)
    b["miks_sn"] = round(time.time() - t0, 1)
    bilgi_yol.write_text(json.dumps(b, ensure_ascii=False, indent=1), encoding="utf-8")
    log(f"ses: {b.get('son_lufs')} LUFS, tepe {b.get('son_tepe_dbtp')} dBTP, LRA {b.get('son_lra')} "
        f"(loudnorm {b.get('loudnorm_turu')}), {b['miks_sn']} sn")
    return b


def cmd_render(a, onizleme: bool = False) -> None:
    v, z = _yukle(a.yol, tahmin=a.tahmini)
    ozet(v, z)
    for x in hareket_denetimi(v, z) + paket.uyarilar(v, z):
        print(f"  ⚠ {x}")
    od = config.OUT / v.id
    W, H = (960, 540) if onizleme else (1920, 1080)
    aralik = None
    if onizleme and (a.bas or a.bit):
        aralik = (_t(a.bas or 0), min(_t(a.bit) if a.bit else z.sure, z.sure))
    sessiz = od / (f".{v.id}_onizleme_video.mp4" if onizleme else f".{v.id}_video.mp4")
    t0 = time.time()
    rb = render.video_render(v, z, sessiz, W, H, isci=a.isci, onizleme=onizleme, aralik=aralik,
                             preset=getattr(a, "preset", render.PRESET))
    t_video = time.time() - t0
    sb = _ses(v, z)
    cikti = od / (f"{v.id}_onizleme.mp4" if onizleme else f"{v.id}.mp4")
    if aralik:
        ilk = rb["ilk_kare"] / z.fps
        render.birlestir(sessiz, Path(sb["ses"]), cikti, ss_v=aralik[0] - ilk, ss_a=aralik[0],
                         sure=aralik[1] - aralik[0])
    elif onizleme:
        render.birlestir(sessiz, Path(sb["ses"]), cikti, ss_v=0, ss_a=0, sure=z.sure)
    else:
        render.birlestir(sessiz, Path(sb["ses"]), cikti)
    sessiz.unlink(missing_ok=True)
    d = render.dogrula(cikti, round((aralik[1] - aralik[0]) * z.fps) if aralik else z.toplam_kare, z.fps)
    toplam = time.time() - t0
    print(f"video -> {cikti}")
    print(f"  render: {rb['cizilen_kare']} kare çizildi, {rb['sure_sn']} sn"
          + (f" ({rb['kare_hizi']} kare/sn, {a.isci} işçi)" if rb["kare_hizi"] else "") + f"; toplam {toplam:.1f} sn")
    print(f"  senkron: video {d['video_basi']:.3f}/{d['video_sure']:.3f} sn, ses {d['ses_basi']:.3f}/"
          f"{d['ses_sure']:.3f} sn, fark {d['fark_sn'] * 1000:.1f} ms, kare {d['kare']}"
          + (f"/{d.get('beklenen_kare')}" if d.get("beklenen_kare") else "")
          + f" -> {'TAMAM' if d['senkron_ok'] and d.get('kare_ok', True) else 'SORUN'}")
    if onizleme:
        return
    srt = altyazi.yaz(z, od / f"{v.id}.srt")
    stem = od / f"{v.id}_anlatim.wav"
    shutil.copy2(sb["anlatim_izi"], stem)
    olcum = {**{k: sb.get(k) for k in ("son_lufs", "son_tepe_dbtp", "son_lra", "loudnorm_turu", "anlatim_lufs_ham",
                                       "muzik_lufs_ham", "efekt_sayisi")},
             **d, "render_kare_hizi": rb["kare_hizi"], "render_sn": rb["sure_sn"], "video_sn": round(t_video, 1),
             "toplam_sn": round(toplam, 1), "isci": a.isci}
    eski = od / "olcum.json"
    if rb["cizilen_kare"] == 0 and eski.exists():   # her şey önbellekteydi: son gerçek render hızını koru
        o = json.loads(eski.read_text(encoding="utf-8"))
        for k in ("render_kare_hizi", "render_sn", "video_sn", "isci"):
            olcum[k] = o.get(k)
        olcum["onbellekten"] = True
    eski.write_text(json.dumps(olcum, ensure_ascii=False, indent=1), encoding="utf-8")
    kr = sorted(od.glob("kucukresim_*.jpg"))
    pk = paket.yaz(v, z, od, cikti, srt, kr, olcum)
    print(f"  altyazı -> {srt}\n  anlatım izi -> {stem}\n  paket -> {pk}")


def cmd_onizle(a) -> None:
    cmd_render(a, onizleme=True)


def cmd_kare(a) -> None:
    v, z = _yukle(a.yol)
    od = config.OUT / v.id / "kareler"
    od.mkdir(parents=True, exist_ok=True)
    for t in a.t or ["0"]:
        sec = _t(t)
        im = render.tek_kare(v, z, sec)
        p = od / f"kare_{sec:07.2f}.png"
        im.save(p)
        print(p)


def cmd_kucukresim(a) -> None:
    v = spec.yukle(a.yol)
    if not v.kucukresimler:
        sys.exit("video.yaml'da 'kucukresimler' yok")
    for p, s in zip(kucukresim.hepsi(v, config.OUT / v.id), v.kucukresimler):
        print(f"-> {p} ({p.stat().st_size / 1e3:.0f} KB)" +
              ("  ⚠ telifli görsel içeriyor: teslim/ altına girerse repoya da girer" if kucukresim.telifli_mi(v, s) else ""))


def cmd_paket(a) -> None:
    v, z = _yukle(a.yol)
    od = config.OUT / v.id
    srt = altyazi.yaz(z, od / f"{v.id}.srt")
    mp4 = od / f"{v.id}.mp4"
    olcum = None
    if (od / "olcum.json").exists():
        olcum = json.loads((od / "olcum.json").read_text(encoding="utf-8"))
    p = paket.yaz(v, z, od, mp4 if mp4.exists() else None, srt, sorted(od.glob("kucukresim_*.jpg")), olcum)
    print(f"paket -> {p}\naltyazı -> {srt}")
    for x in paket.uyarilar(v, z):
        print(f"  ⚠ {x}")


def cmd_teslim(a) -> None:
    v, z = _yukle(a.yol, tahmin=False)
    od = config.OUT / v.id
    mp4 = od / f"{v.id}.mp4"
    if not mp4.exists():
        sys.exit(f"Önce render: python -m wojak uzun render {a.yol}")
    yml = v.dir / "video.yaml"
    if mp4.stat().st_mtime < yml.stat().st_mtime:
        print("  ⚠ video, video.yaml'dan eski: değiştiyse önce yeniden render et")
    u = paket.uyarilar(v, z)
    for x in u:
        print(f"  ⚠ {x}")
    if u and not a.zorla:
        sys.exit("Uyarılar var; düzelt ya da bilerek --zorla kullan.")
    kr = sorted(od.glob("kucukresim_*.jpg"))
    if not kr and v.kucukresimler:
        kr = kucukresim.hepsi(v, od)
    srt = altyazi.yaz(z, od / f"{v.id}.srt")
    olcum = json.loads((od / "olcum.json").read_text(encoding="utf-8")) if (od / "olcum.json").exists() else None
    paket.yaz(v, z, od, mp4, srt, kr, olcum)
    dst = config.ROOT / "teslim" / f"{v.id}-uzun"
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True)
    for f in [mp4, srt, od / "paylasim.md", *kr]:
        shutil.copy2(f, dst / f.name)
    for s in v.kucukresimler:
        if kucukresim.telifli_mi(v, s):
            print(f"  ⚠ kucukresim_{s.get('ad')}.jpg telifli görsel içeriyor (teslim/ repoya girer: kaldır ya da izin al)")
    print(f"teslim -> {dst}")
    for f in sorted(dst.iterdir()):
        n = f.stat().st_size
        print(f"  {f.name}  ({n / 1e6:.1f} MB)" if n > 1e5 else f"  {f.name}  ({n / 1e3:.1f} KB)")


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(prog="wojak uzun", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    for ad, fn in (("kontrol", cmd_kontrol), ("kucukresim", cmd_kucukresim), ("paket", cmd_paket)):
        p = sp.add_parser(ad)
        p.add_argument("yol")
        p.set_defaults(fn=fn)
    p = sp.add_parser("seslendir")
    p.add_argument("yol")
    p.add_argument("--qa", action="store_true", help="Whisper ile isim denetimi")
    p.add_argument("--yenile", type=int, default=0, help="denetimde başarısız satırı en fazla N kez yeniden üret")
    p.add_argument("--yeniden", action="store_true", help="önbelleği yok say, hepsini yeniden üret")
    p.set_defaults(fn=cmd_seslendir)
    for ad, fn in (("render", cmd_render), ("onizle", cmd_onizle)):
        p = sp.add_parser(ad)
        p.add_argument("yol")
        p.add_argument("--isci", type=int, default=3, help="paralel çizim süreci (vars. 3)")
        p.add_argument("--tahmini", action="store_true", help="ses yoksa tahmini sürelerle (sessiz) render et")
        p.add_argument("--preset", default=render.PRESET, help="x264 hız ayarı (vars. faster; kalite için medium)")
        if ad == "onizle":
            p.add_argument("--bas", help="başlangıç (sn ya da dk:sn)")
            p.add_argument("--bit", help="bitiş (sn ya da dk:sn)")
            p.set_defaults(tahmini=True)
        p.set_defaults(fn=fn)
    p = sp.add_parser("kare")
    p.add_argument("yol")
    p.add_argument("--t", action="append", help="an (sn ya da dk:sn); birden çok verilebilir")
    p.set_defaults(fn=cmd_kare)
    p = sp.add_parser("teslim")
    p.add_argument("yol")
    p.add_argument("--zorla", action="store_true")
    p.set_defaults(fn=cmd_teslim)
    a = ap.parse_args(argv)
    try:
        a.fn(a)
    except (spec.SpecHatasi, tts.TTSHatasi) as e:
        sys.exit(f"HATA: {e}")


if __name__ == "__main__":
    main()
