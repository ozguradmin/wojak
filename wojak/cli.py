"""Komut satırı.

    python -m wojak render episodes/<bolum>            # video + kapak + paylaşım paketi
    python -m wojak render episodes/<bolum> --preview  # hızlı yarım çözünürlük
    python -m wojak render episodes/<bolum> --square   # 1080x1080 sürüm
    python -m wojak render episodes/<bolum> --dolgu    # siyah bantlar bulanık arka planla dolu (A/B testi)
    python -m wojak frames episodes/<bolum>            # her sahneden bir kare (kontrol için)
    python -m wojak check episodes/<bolum>             # YAML doğrulama + süre özeti
    python -m wojak new <bolum-id>                     # şablondan yeni bölüm klasörü
    python -m wojak paket episodes/<bolum>             # sadece paylaşım metinlerini yeniden yaz
    python -m wojak teslim episodes/<bolum>            # video + kapak + metinler -> teslim/<bolum>/ (onaya)
"""

from __future__ import annotations

import argparse
import shutil
import sys
import time

from PIL import Image

from . import config, denetim, episode, pack, render


def _summary(ep: episode.Episode) -> None:
    print(f"{ep.id}: {ep.duration:.1f} sn, {len(ep.scenes)} sahne")
    t = 0.0
    for i, s in enumerate(ep.scenes, 1):
        txt = (s.text or s.banner or ", ".join(p.name for p in s.images) or "").replace("\n", " ")
        print(f"  {i:2d}. {t:5.1f}s  {s.type:<8} {s.duration:4.1f}s  {txt[:70]}")
        t += s.duration


def _denetle(ep: episode.Episode) -> None:
    uyarilar = denetim.check(ep)
    for u in uyarilar:
        print(f"  ⚠ {u}")
    if ep.gundem:
        print("  GÜNDEM bölümü: yayından önce docs/GUNDEM.md > 5. Kontrol listesi (yayın yasağı kontrolü dahil).")


def cmd_check(a) -> None:
    ep = episode.load(a.episode)
    _summary(ep)
    _denetle(ep)
    if not 7 <= ep.duration <= 30:
        print(f"UYARI: süre {ep.duration:.1f} sn. 'Olay' formatında hedef 11-16 sn.")
    for i, s in enumerate(ep.scenes, 1):  # okuma süresi ≈ kelime/3 + 1 sn (KONSEPT §3)
        if s.type == "dialog" and s.text:
            need = len(s.text.split()) / 3 + 1
            if s.duration + 0.15 < need:
                print(f"UYARI: sahne {i} okunamayabilir: {len(s.text.split())} kelime için ~{need:.1f} sn gerekli, "
                      f"süre {s.duration:.1f} sn")


def cmd_render(a) -> None:
    ep = episode.load(a.episode)
    _summary(ep)
    _denetle(ep)
    out_dir = config.OUT / ep.id
    t0 = time.time()
    mp4 = render.render(ep, out_dir, square=a.square, preview=a.preview, fill=a.dolgu)
    print(f"video -> {mp4}  ({time.time() - t0:.1f} sn)")
    if not a.preview:
        cover_idx = next((i for i, s in enumerate(ep.scenes) if s.type == "dialog"), 0)
        name = "kapak_kare.jpg" if a.square else ("kapak_dolgu.jpg" if a.dolgu else "kapak.jpg")
        cover = render.still(ep, cover_idx, out_dir / name, at=0.9, square=a.square, fill=a.dolgu)
        print(f"kapak -> {cover}")
        if a.square or a.dolgu:  # metinler aynı; ana paketin üzerine yazma (teslim ek dosyaları kendisi alır)
            return
        print(f"paket -> {pack.write(ep, out_dir, mp4)}")
        for w in pack.warnings(pack.texts(ep), ep):
            print(f"  ⚠ {w}")


def cmd_frames(a) -> None:
    ep = episode.load(a.episode)
    out_dir = config.OUT / ep.id / "kareler"
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = [render.still(ep, i, out_dir / f"{i + 1:02d}.jpg", at=0.9, square=True)
             for i in range(len(ep.scenes))]
    # Hepsini tek bir şeritte birleştir (hızlı göz kontrolü için)
    ims = [Image.open(p) for p in paths]
    w = 360
    strip = Image.new("RGB", (w * len(ims), w), "black")
    for i, im in enumerate(ims):
        strip.paste(im.resize((w, w)), (i * w, 0))
    strip.save(out_dir / "serit.jpg", quality=88)
    print(f"-> {out_dir}/serit.jpg")


def cmd_paket(a) -> None:
    ep = episode.load(a.episode)
    out_dir = config.OUT / ep.id
    out_dir.mkdir(parents=True, exist_ok=True)
    mp4 = out_dir / f"{ep.id}.mp4"
    print(f"paket -> {pack.write(ep, out_dir, mp4 if mp4.exists() else None, denetim=denetim.check(ep))}")
    for w in pack.warnings(pack.texts(ep), ep):
        print(f"  ⚠ {w}")
    dst = config.ROOT / "teslim" / ep.id
    if dst.exists():  # teslim edilmiş bölümün metinlerini de güncelle (video gerekmez)
        (dst / "metinler").mkdir(exist_ok=True)
        for f in (out_dir / "metinler").glob("*.txt"):
            shutil.copy2(f, dst / "metinler" / f.name)
        shutil.copy2(out_dir / "paylasim.md", dst / "paylasim.md")
        print(f"teslim metinleri güncellendi -> {dst}")


def cmd_teslim(a) -> None:
    """Onaya gidecek her şeyi tek klasörde toplar (repoda kalır, hesap sahibi GitHub'dan da indirebilir)."""
    ep = episode.load(a.episode)
    src = config.OUT / ep.id
    mp4 = src / f"{ep.id}.mp4"
    if not mp4.exists() or not (src / "kapak.jpg").exists():
        sys.exit(f"Önce render: python -m wojak render {a.episode}")
    # Kapılar mevcut teslim/<id>/ silinmeden ÖNCE: engellenen bir deneme eski geçerli paketi bozmasın.
    uyarilar = denetim.check(ep)
    for u in uyarilar:
        print(f"  ⚠ {u}")
    if ep.gundem and uyarilar and not a.zorla:
        sys.exit("Güncel olay bölümünde denetim uyarıları var; düzelt ya da bilerek --zorla kullan.")
    sinir = pack.warnings(pack.texts(ep), ep)
    for w in sinir:
        print(f"  ⚠ {w}")
    if sinir and not a.zorla:
        sys.exit("Paket sınırları aşıldı ya da hikâye boş; düzelt ya da bilerek --zorla kullan.")
    yml = ep.dir / "episode.yaml"
    if yml.exists() and mp4.stat().st_mtime < yml.stat().st_mtime:
        print("  ⚠ video episode.yaml'dan eski: sahneler değiştiyse önce yeniden render et")
    pack.write(ep, src, mp4, denetim=uyarilar)
    dst = config.ROOT / "teslim" / ep.id
    if dst.exists():
        shutil.rmtree(dst)
    (dst / "metinler").mkdir(parents=True)
    shutil.copy2(mp4, dst / mp4.name)
    # kenarlık A/B testi sürümü varsa o da gider (KONSEPT §3)
    for name in ("kapak.jpg", "paylasim.md", f"{ep.id}_dolgu.mp4", "kapak_dolgu.jpg"):
        if (src / name).exists():
            shutil.copy2(src / name, dst / name)
    for f in (src / "metinler").glob("*.txt"):
        shutil.copy2(f, dst / "metinler" / f.name)
    print(f"teslim -> {dst}")
    for f in sorted(dst.rglob("*")):
        if f.is_file():
            n = f.stat().st_size
            print(f"  {f.relative_to(dst)}  ({n / 1e6:.1f} MB)" if n > 1e5 else f"  {f.relative_to(dst)}  ({n / 1e3:.1f} KB)")


def cmd_new(a) -> None:
    dst = config.ROOT / "episodes" / a.id
    if dst.exists():
        sys.exit(f"zaten var: {dst}")
    shutil.copytree(config.ROOT / "episodes" / "_sablon", dst)
    yml = dst / "episode.yaml"
    yml.write_text(yml.read_text(encoding="utf-8").replace("id: sablon", f"id: {a.id}"), encoding="utf-8")
    print(f"-> {dst}")


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(prog="wojak", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("render")
    p.add_argument("episode")
    p.add_argument("--square", action="store_true")
    p.add_argument("--preview", action="store_true")
    p.add_argument("--dolgu", action="store_true", help="üst/alt bantları karenin bulanık hâliyle doldur")
    p.set_defaults(fn=cmd_render)
    for name, fn in (("check", cmd_check), ("frames", cmd_frames), ("paket", cmd_paket)):
        p = sp.add_parser(name)
        p.add_argument("episode")
        p.set_defaults(fn=fn)
    p = sp.add_parser("teslim")
    p.add_argument("episode")
    p.add_argument("--zorla", action="store_true", help="denetim/sınır uyarılarına rağmen teslim et (bilerek)")
    p.set_defaults(fn=cmd_teslim)
    p = sp.add_parser("new")
    p.add_argument("id")
    p.set_defaults(fn=cmd_new)
    a = ap.parse_args(argv)
    try:
        a.fn(a)
    except episode.EpisodeError as e:
        sys.exit(f"HATA: {e}")


if __name__ == "__main__":
    main()
