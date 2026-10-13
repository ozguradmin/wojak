"""Uzun video animasyon denetimi (7. tur): kare kare, ölçerek hata avı.

Hesap sahibi (13.10): "animasyon güzel ama hatalar var". Bu araç teslimden önce videoyu 30 fps'de, öğe öğe tarar;
şüpheli anları zaman damgasıyla listeler (bakarak karar verilir: her bulgu hata değildir).

    # 1) videoyu çöz: kare farkı karoları (480x270 gri, 20x10 karo) + 160x90 küçük kareler
    python tools/uzun_animasyon_denetimi.py kareler out/<id>-uzun/<id>.mp4 /tmp/denetim
    # 2) motoru öğe öğe izle (render ile AYNI kod ve video.yaml olmalı): her C.bindir çağrısının yeri, boyu, opaklığı
    python tools/uzun_animasyon_denetimi.py oge uzun/<id> /tmp/denetim/oge.pkl --isci 3
    # 3) rapor: 1-2 karelik pop, geçişte flaş, öğe sıçraması, aniden belirme/kaybolma, kesmede yarı saydam kalma,
    #    kenar kırpılması, yazının yüze/yazıya binmesi (z-düzeni), kare başına hız (stroboskop)
    python tools/uzun_animasyon_denetimi.py rapor uzun/<id> /tmp/denetim [--oge /tmp/denetim/oge.pkl]
    # 4) şüpheli an: tam çözünürlük kare şeridi (k-a .. k+b), isteğe bağlı bölge
    python tools/uzun_animasyon_denetimi.py seri out/<id>-uzun/<id>.mp4 1567 2 2 --kutu 1200 300 1920 1080 -o s.png

Diskte yer: kareler 18.400 karelik (10 dk) videoda ~0,9 GB (küçük kareler); `--kucuk-yok` ile ~45 MB.
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import pickle
import subprocess
import sys
from collections import defaultdict, namedtuple
from pathlib import Path

import numpy as np

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK))

FPS = 30
TY, TX = 10, 20          # karo ızgarası (480x270'te 24x27 px karolar)


def zs(k: int) -> str:
    t = k / FPS
    return f"{int(t // 60)}:{t % 60:06.3f}"


# ================================================================ 1) kareler

def cmd_kareler(a) -> None:
    od = Path(a.cikti)
    od.mkdir(parents=True, exist_ok=True)
    W, H = 480, 270
    n = int(json.loads(subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v:0",
                                       "-show_entries", "stream=nb_read_packets", "-of", "json", a.mp4],
                                      capture_output=True, text=True, check=True).stdout)["streams"][0]["nb_read_packets"])
    p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-threads", "4", "-i", a.mp4, "-vf",
                          f"scale={W}:{H}:flags=area", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         stdout=subprocess.PIPE, bufsize=W * H * 3 * 8)
    kucuk = None if a.kucuk_yok else np.lib.format.open_memmap(od / "kucuk.npy", "w+", np.uint8, (n, 90, 160, 3))
    A, B, Cc = (np.zeros((n, TY, TX), np.float16) for _ in range(3))
    lum = np.zeros(n, np.float32)
    gecmis, k, fs = [], 0, W * H * 3
    agirlik = np.array([0.2126, 0.7152, 0.0722], np.float32)
    while k < n:
        buf = p.stdout.read(fs)
        if len(buf) < fs:
            break
        rgb = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        g = rgb.astype(np.float32) @ agirlik
        if kucuk is not None:
            kucuk[k] = rgb.reshape(90, 3, 160, 3, 3).mean(axis=(1, 3)).astype(np.uint8)
        lum[k] = g.mean()
        for arr, j in ((A, 1), (B, 2), (Cc, 3)):
            if len(gecmis) >= j:
                arr[k] = np.abs(g - gecmis[-j]).reshape(TY, H // TY, TX, W // TX).mean(axis=(1, 3)).astype(np.float16)
        gecmis = (gecmis + [g])[-3:]
        k += 1
    p.stdout.close()
    p.wait()
    for ad, x in (("A", A), ("B", B), ("C", Cc)):
        np.save(od / f"{ad}.npy", x[:k])
    np.save(od / "lum.npy", lum[:k])
    if kucuk is not None:
        kucuk.flush()
    print(f"{k} kare -> {od}")


# ================================================================ 2) öğe izleme

def cmd_oge(a) -> None:
    from wojak.uzun import cizim as C
    from wojak.uzun import render, spec, tts, zaman
    v = spec.yukle(a.yol)
    tts.sureleri_yukle(v)
    z = zaman.hesapla(v, tahmin=True)
    W, H = a.W, a.W * 9 // 16
    orijinal = C.bindir
    durum = {"kayit": None, "faz": "s", "idler": {}, "sira": 0}
    lut = [255 if x > 96 else 0 for x in range(256)]

    def bindir(dst, src, x, y, alfa=1.0):
        kay = durum["kayit"]
        if kay is not None and dst.size == (W, H) and alfa > 0.003:
            f = sys._getframe(1)
            while f is not None and f.f_code.co_filename.endswith("cizim.py"):   # bindir_alt vb. yardımcıları atla
                f = f.f_back
            self_ = f.f_locals.get("self") if f else None
            ids = durum["idler"]
            n = ids.setdefault(id(self_), len(ids))
            ad = f.f_code.co_name if f else "?"
            ek = ""
            if ad == "uygula" and "t0" in f.f_locals:
                ek = f":{round(float(f.f_locals['t0']), 3)}"
            if ad == "_ust_ogeler":
                ek = f":{f.f_locals.get('taraf')}"
            sinif = type(self_).__name__ if self_ is not None else "-"
            anahtar = f"{sinif}#{n}:{ad}:*{ek}" if sinif in ("UstKatman", "KoseGostergesi", "Damga", "Balon") \
                else f"{sinif}#{n}:{ad}:{f.f_lineno if f else 0}{ek}"
            kutu = src.getchannel("A").point(lut).getbbox() if src.mode == "RGBA" else (0, 0, src.width, src.height)
            durum["sira"] += 1
            kay.append((durum["faz"], anahtar, float(x), float(y), src.width, src.height, float(alfa), kutu,
                        durum["sira"]))
        return orijinal(dst, src, x, y, alfa)

    C.bindir = bindir

    def sahne_isle(i):
        s = z.sahneler[i]
        durum["idler"] = {}
        ku = render.KareUretici(v, z, i, W, H)
        out = []
        for cz, faz in ((ku.cz, "s"), (ku.onceki, "o")):
            if cz is None:
                continue
            ilk = cz.kare

            def sarili(t, ilk=ilk, faz=faz):
                durum["faz"] = faz
                return ilk(t)
            cz.kare = sarili
        for k in range(s.n_kare):
            durum["kayit"], durum["sira"] = [], 0
            ku.kare(k)
            out += [(s.bas_kare + k, i) + r for r in durum["kayit"]]
            durum["kayit"] = None
        return i, out

    sira = sorted(range(len(z.sahneler)), key=lambda i: -z.sahneler[i].n_kare)
    hepsi = {}
    with mp.get_context("fork").Pool(a.isci) as pool:
        for i, out in pool.imap_unordered(sahne_isle, sira):
            hepsi[i] = out
            print(f"  sahne {i} {z.sahneler[i].tip}: {len(out)} kayıt", flush=True)
    meta = [{"i": i, "tip": s.tip, "bas": s.bas_kare, "n": s.n_kare, "gecis": s.gecis, "gecis_kare": s.gecis_kare}
            for i, s in enumerate(z.sahneler)]
    with open(a.cikti, "wb") as f:
        pickle.dump({"meta": meta, "kayit": [r for i in sorted(hepsi) for r in hepsi[i]], "W": W, "H": H}, f)
    print(f"-> {a.cikti}")


# ================================================================ 3) rapor

YAZI = ("Damga", "UstKatman", "KoseGostergesi", "DaktiloEtiket", "Balon", "FotoCizici", "HaritaCizici",
        "SayacCizici", "MetinCizici", "ZamanCizelgesiCizici", "BolunmusCizici", "IzgaraCizici", "PanoCizici",
        "BitisCizici", "MarkaCizici", "BolumKartiCizici", "KapanisCizici")


def _kareler_raporu(z, d: Path) -> list[str]:
    A = np.load(d / "A.npy").astype(np.float32)
    B = np.load(d / "B.npy").astype(np.float32)
    Cc = np.load(d / "C.npy").astype(np.float32)
    N = len(A)
    sahne = np.zeros(N, int)
    for i, s in enumerate(z.sahneler):
        sahne[s.bas_kare:s.bas_kare + s.n_kare] = i
    out = []

    def gecis_ici(k):
        s = z.sahneler[sahne[k]]
        return s.gecis != "kesme" and k - s.bas_kare < s.gecis_kare + 2

    olaylar = defaultdict(list)
    for k in range(1, N - 1):
        m = np.minimum(A[k], A[k + 1])
        t = (m > 5.0) & (B[k + 1] < 0.4 * m)
        if t.any() and not gecis_ici(k):
            olaylar[(sahne[k], "1 karelik değişim")].append((k, int(t.sum()), float((m - B[k + 1])[t].max())))
    for k in range(1, N - 2):
        m = np.minimum(A[k], A[k + 2])
        t = (m > 5.0) & (Cc[k + 2] < 0.4 * m) & (A[k + 1] < m)
        if t.any() and not gecis_ici(k):
            olaylar[(sahne[k], "2 karelik değişim")].append((k, int(t.sum()), float((m - Cc[k + 2])[t].max())))
    for (i, tur), ks in sorted(olaylar.items()):
        s = z.sahneler[i]
        en = max(ks, key=lambda x: x[2])
        out.append(f"{zs(en[0]):>10} s{i:02d} {s.tip:<15} {tur}: {len(ks)} an, en güçlüsü k{en[0]} "
                   f"({en[1]} karo, skor {en[2]:.0f}) — sayaç/yüz değişimi/hızlı giriş olabilir: bak")
    g = A.mean(axis=(1, 2))
    for i, s in enumerate(z.sahneler):
        if s.gecis == "kesme" and not s.p.get("bindirme"):
            continue
        b = s.bas_kare
        seg = g[b:b + max(s.gecis_kare, 6) + 2]
        if len(seg) > 2 and seg[1] > 2.5 * max(seg[0], 1.0) and seg[1] > 15:
            out.append(f"{zs(b):>10} s{i:02d} {s.tip:<15} geçişin 2. karesinde ani sıçrama "
                       f"({seg[0]:.1f} -> {seg[1]:.1f}): flaş gibi görünebilir")
    return out


Kayit = namedtuple("Kayit", "k i faz an x y w h a kutu sira")


def _oge_raporu(d: dict, hiz_esik: float) -> list[str]:
    meta, W, H = d["meta"], d["W"], d["H"]
    kayit = [Kayit(*r) for r in d["kayit"]]
    gecis_son = {m["i"]: m["bas"] + (m["gecis_kare"] if m["gecis"] != "kesme" else 0) for m in meta}
    izler, kare = defaultdict(list), defaultdict(list)
    for r in kayit:
        if r.faz == "s" and r.kutu is not None:
            izler[(r.i, r.an)].append(r)
            kare[r.k].append(r)
    sinif = lambda an: an.split("#")[0]   # noqa: E731

    def kutu(r):   # görünen kutu, kare koordinatında
        return r.x + r.kutu[0], r.y + r.kutu[1], r.x + r.kutu[2], r.y + r.kutu[3]

    out = []
    hizli = defaultdict(list)
    for (i, an), rs in izler.items():
        m = meta[i]
        rs.sort(key=lambda r: r.k)
        ks = np.array([r.k for r in rs])
        son = m["bas"] + m["n"] - 1
        for p_ in np.split(np.arange(len(ks)), np.where(np.diff(ks) > 1)[0] + 1):
            k0, k1 = ks[p_[0]], ks[p_[-1]]
            if len(p_) <= 2 and k0 > gecis_son[i] and k1 < son:
                out.append(f"{zs(k0):>10} s{i:02d} {m['tip']:<15} POP: {an} {len(p_)} kare görünüp kayboldu")
            r1 = rs[p_[-1]]
            if k1 == son and 0.05 < r1.a < 0.95 and sinif(an) in ("UstKatman", "Damga"):
                out.append(f"{zs(k1):>10} s{i:02d} {m['tip']:<15} KESMEDE YARI SAYDAM: {an} (alfa {r1.a:.2f})")
            if son - k0 < 12 and k0 > m["bas"] + 2:
                out.append(f"{zs(k0):>10} s{i:02d} {m['tip']:<15} KISA KALIŞ: {an} kesmeden {(son - k0 + 1) / FPS:.2f} sn "
                           "önce belirdi (en az ~1 sn okunur kalsın)")
        for r0, r1 in zip(rs, rs[1:]):
            if r1.k - r0.k == 1:
                v = np.hypot((r1.x + r1.w / 2) - (r0.x + r0.w / 2), (r1.y + r1.h / 2) - (r0.y + r0.h / 2))
                if v > hiz_esik:
                    hizli[(i, an)].append(v)
        for j, r in enumerate(rs):
            L, T, R, Bt = kutu(r)
            sabit = 0 < j < len(rs) - 1 and abs(rs[j + 1].x - rs[j - 1].x) < 3 and abs(rs[j + 1].y - rs[j - 1].y) < 3
            if sabit and r.a >= 0.5 and sinif(an) in YAZI and (L < -2 or T < -2 or R > W + 2 or Bt > H + 2):
                out.append(f"{zs(r.k):>10} s{i:02d} {m['tip']:<15} KIRPILMA: {an} ({L:.0f},{T:.0f},{R:.0f},{Bt:.0f})")
                break
            if sabit and sinif(an) == "Karakter" and (T < -2 or L < -0.12 * W or R > 1.12 * W):
                out.append(f"{zs(r.k):>10} s{i:02d} {m['tip']:<15} KIRPILMA: karakter {an} ({L:.0f},{T:.0f},{R:.0f},"
                           f"{Bt:.0f}) üstten ya da yandan çok kesik")
                break
    for (i, an), vs in sorted(hizli.items()):
        out.append(f"{'':>10} s{i:02d} {meta[i]['tip']:<15} HIZ: {an} {len(vs)} karede > {hiz_esik:.0f} px/kare "
                   f"(en çok {max(vs):.0f}); hareket bulanıklığı açık mı?")
    cak = defaultdict(list)
    for k, rs in kare.items():
        kars = [r for r in rs if sinif(r.an) == "Karakter" and r.a > 0.5]
        yazis = [r for r in rs if sinif(r.an) in YAZI and r.a > 0.5]
        for y_ in yazis:
            A_ = kutu(y_)
            aA = max(1, (A_[2] - A_[0]) * (A_[3] - A_[1]))
            for c in kars:
                L, T, R, Bt = kutu(c)
                Kb = (L, T, R, T + 0.45 * (Bt - T))      # karakterin üst %45'i: baş
                ix = max(0, min(A_[2], Kb[2]) - max(A_[0], Kb[0]))
                iy = max(0, min(A_[3], Kb[3]) - max(A_[1], Kb[1]))
                if ix * iy > 0.12 * aA:
                    cak[(y_.i, y_.an, c.an, "yazı karakterin üst yarısında (yüz?)",
                         "üstte" if y_.sira > c.sira else "ARKADA")].append(k)
            for y2 in yazis:
                # aynı öğenin parçaları (foto + alt yazısı, satır + kelime) bilerek üst üste
                if y2.sira <= y_.sira or y2.an.split(":")[0] == y_.an.split(":")[0]:
                    continue
                Bb = kutu(y2)
                ix = max(0, min(A_[2], Bb[2]) - max(A_[0], Bb[0]))
                iy = max(0, min(A_[3], Bb[3]) - max(A_[1], Bb[1]))
                if ix * iy > 0.08 * min(aA, max(1, (Bb[2] - Bb[0]) * (Bb[3] - Bb[1]))):
                    cak[(y_.i, y_.an, y2.an, "yazı yazıya biniyor", "")].append(k)
    for (i, a_, b_, tur, ust), ks in sorted(cak.items(), key=lambda q: min(q[1])):
        if len(ks) >= 8:
            out.append(f"{zs(min(ks)):>10} s{i:02d} {meta[i]['tip']:<15} ÇAKIŞMA: {a_} / {b_}: {tur} {ust} "
                       f"({len(ks)} kare, {zs(min(ks))}-{zs(max(ks))})")
    return sorted(out)


def cmd_rapor(a) -> None:
    from wojak.uzun import spec, tts, zaman
    v = spec.yukle(a.yol)
    tts.sureleri_yukle(v)
    z = zaman.hesapla(v, tahmin=True)
    satirlar = []
    d = Path(a.klasor)
    if (d / "A.npy").exists():
        if len(np.load(d / "lum.npy", mmap_mode="r")) != z.toplam_kare:
            print("⚠ çözülen kare sayısı zaman çizelgesiyle aynı değil: video bu video.yaml'ın render'ı mı?")
        satirlar += ["## Kare farkı (videodan)"] + _kareler_raporu(z, d)
    if a.oge:
        satirlar += ["", "## Öğe izleri (motordan)"] + _oge_raporu(pickle.load(open(a.oge, "rb")), a.hiz)
    print("\n".join(satirlar))


# ================================================================ 4) seri

def cmd_seri(a) -> None:
    from PIL import Image, ImageDraw
    k0 = max(0, a.k - a.a)
    n = a.k + a.b - k0 + 1
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", f"{max((k0 - 0.2) / FPS, 0):.4f}", "-i", a.mp4,
                          "-frames:v", str(n), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    info = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                      "stream=width,height", "-of", "json", a.mp4], capture_output=True, text=True,
                                     check=True).stdout)["streams"][0]
    fr = np.frombuffer(raw, np.uint8).reshape(-1, info["height"], info["width"], 3)
    ims = []
    for i, f in enumerate(fr):
        im = Image.fromarray(f)
        if a.kutu:
            im = im.crop(tuple(a.kutu))
        w = a.s or min(im.width, 640)
        im = im.resize((int(w), int(im.height * w / im.width)), Image.LANCZOS)
        dr = ImageDraw.Draw(im)
        dr.rectangle((0, 0, 92, 22), fill=(0, 0, 0))
        dr.text((4, 4), f"{k0 + i}", fill=(255, 255, 0) if k0 + i == a.k else (255, 255, 255))
        ims.append(im)
    sut = a.sutun or min(len(ims), 5)
    w, h = ims[0].size
    out = Image.new("RGB", (sut * (w + 4), -(-len(ims) // sut) * (h + 4)), (40, 40, 40))
    for i, im in enumerate(ims):
        out.paste(im, ((i % sut) * (w + 4), (i // sut) * (h + 4)))
    out.save(a.o)
    print(a.o)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("kareler")
    p.add_argument("mp4")
    p.add_argument("cikti")
    p.add_argument("--kucuk-yok", action="store_true", help="160x90 küçük kareleri yazma (disk)")
    p.set_defaults(fn=cmd_kareler)
    p = sp.add_parser("oge")
    p.add_argument("yol")
    p.add_argument("cikti")
    p.add_argument("--isci", type=int, default=3)
    p.add_argument("--W", type=int, default=1920)
    p.set_defaults(fn=cmd_oge)
    p = sp.add_parser("rapor")
    p.add_argument("yol")
    p.add_argument("klasor")
    p.add_argument("--oge")
    p.add_argument("--hiz", type=float, default=60.0, help="px/kare: bunun üstü 'hızlı' sayılır")
    p.set_defaults(fn=cmd_rapor)
    p = sp.add_parser("seri")
    p.add_argument("mp4")
    p.add_argument("k", type=int)
    p.add_argument("a", type=int, nargs="?", default=2)
    p.add_argument("b", type=int, nargs="?", default=2)
    p.add_argument("--kutu", type=int, nargs=4)
    p.add_argument("-o", default="seri.png")
    p.add_argument("-s", type=float)
    p.add_argument("--sutun", type=int, default=0)
    p.set_defaults(fn=cmd_seri)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
