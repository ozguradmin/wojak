"""Sade, stilize dünya/Avrupa haritası (Natural Earth, kamu malı).

Veri: Natural Earth admin-0 ülkeleri (1:110m ve 1:50m), https://www.naturalearthdata.com — kamu malı.
`python -m wojak.uzun.harita indir` GeoJSON'u indirir, yalnız gerekli alanları (ADM0_A3, NAME, NAME_TR,
LABEL_X/Y) ve 3 ondalığa yuvarlanmış koordinatları tutup assets/harita/ altına .geojson.gz olarak yazar.

Projeksiyon: Avrupa ve bölgeler için Lambert azimut eşit alan (merkezli), dünya için Equal Earth.
"""

from __future__ import annotations

import gzip
import json
import math
import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from .. import config

VERI = config.ASSETS / "harita"
URL = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_{r}_admin_0_countries.geojson"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/126.0.0.0 Safari/537.36")

BOLGELER = {
    # merkez (lon, lat), sınır (lon0, lat0, lon1, lat1), projeksiyon
    "avrupa": {"merkez": (16.0, 50.0), "sinir": (-11.0, 34.0, 45.0, 66.0), "proj": "laea"},
    "bati_avrupa": {"merkez": (8.0, 50.0), "sinir": (-11.0, 35.0, 30.0, 63.0), "proj": "laea"},
    "akdeniz": {"merkez": (20.0, 39.0), "sinir": (-8.0, 29.0, 45.0, 48.0), "proj": "laea"},
    "turkiye": {"merkez": (35.0, 39.0), "sinir": (24.0, 34.0, 46.0, 43.5), "proj": "laea"},
    "dunya": {"merkez": (10.0, 0.0), "sinir": (-180.0, -58.0, 180.0, 84.0), "proj": "equal_earth"},
}


def dosya(r: str) -> Path:
    return VERI / f"ne_{r}_admin_0_countries.geojson.gz"


def indir(r: str = "50m", kaynak: str | None = None) -> Path:
    """GeoJSON'u indirir (ya da yerel `kaynak` dosyasından okur), sadeleştirip gzip'ler."""
    if kaynak:
        raw = json.loads(Path(kaynak).read_text(encoding="utf-8"))
    else:
        import requests
        resp = requests.get(URL.format(r=r), headers={"User-Agent": UA}, timeout=120)
        resp.raise_for_status()
        raw = resp.json()

    def yuvarla(c):
        if isinstance(c[0], (int, float)):
            return [round(c[0], 3), round(c[1], 3)]
        return [yuvarla(x) for x in c]

    feats = []
    for f in raw["features"]:
        p = f["properties"]
        feats.append({"type": "Feature", "properties": {
            "kod": p["ADM0_A3"], "ad": p["NAME"], "ad_tr": p.get("NAME_TR") or p["NAME"],
            "lx": p.get("LABEL_X"), "ly": p.get("LABEL_Y"), "kita": p.get("CONTINENT")},
            "geometry": {"type": f["geometry"]["type"], "coordinates": yuvarla(f["geometry"]["coordinates"])}})
    VERI.mkdir(parents=True, exist_ok=True)
    out = dosya(r)
    with gzip.open(out, "wt", encoding="utf-8") as fh:
        json.dump({"type": "FeatureCollection", "features": feats}, fh, ensure_ascii=False, separators=(",", ":"))
    lis = VERI / "LISANS.md"
    if not lis.exists():
        lis.write_text(LISANS, encoding="utf-8")
    return out


LISANS = """# Harita verisi

`ne_*_admin_0_countries.geojson.gz`: Natural Earth, Admin 0 – Countries (1:110m ve 1:50m), v5.
Kaynak: https://www.naturalearthdata.com/ (GeoJSON kopyası: https://github.com/nvkelso/natural-earth-vector).

**Lisans: kamu malı (public domain).** "All versions of Natural Earth raster + vector map data found on this
website are in the public domain. You may use the maps in any manner, including modifying the content and
design, electronic dissemination, and offset printing." (https://www.naturalearthdata.com/about/terms-of-use/)
Atıf gerekmez; açıklamada "Harita verisi: Natural Earth" yazmak iyi uygulamadır.

Değişiklik: yalnız ADM0_A3, NAME, NAME_TR, LABEL_X/Y, CONTINENT alanları tutuldu; koordinatlar 3 ondalığa
yuvarlandı (`python -m wojak.uzun.harita indir`). Not: sınırlar bugünkü sınırlardır (ör. 1957'nin Batı/Doğu
Almanya'sı ayrı değildir); tarihî harita gerekiyorsa anlatımda belirt.
"""


@dataclass
class Ulke:
    kod: str
    ad: str
    ad_tr: str
    etiket: tuple[float, float] | None
    halkalar: list[np.ndarray]   # dış halkalar, (n, 2) lon/lat
    kita: str | None = None


@lru_cache(maxsize=4)
def yukle(r: str = "50m") -> dict[str, Ulke]:
    p = dosya(r)
    if not p.exists():
        raise FileNotFoundError(f"{p} yok: python -m wojak.uzun.harita indir {r}")
    with gzip.open(p, "rt", encoding="utf-8") as fh:
        raw = json.load(fh)
    out: dict[str, Ulke] = {}
    for f in raw["features"]:
        pr, g = f["properties"], f["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        halkalar = [np.asarray(poly[0], dtype=np.float64) for poly in polys]
        lab = (pr["lx"], pr["ly"]) if pr.get("lx") is not None else None
        kod = pr["kod"]
        if kod in out:  # aynı kodlu parçalar (nadiren) birleşir
            out[kod].halkalar.extend(halkalar)
        else:
            out[kod] = Ulke(kod, pr["ad"], pr["ad_tr"], lab, halkalar, pr.get("kita"))
    return out


# ---------------------------------------------------------------- projeksiyonlar

def laea(lon, lat, lon0, lat0):
    lam, phi = np.radians(lon), np.radians(lat)
    l0, p0 = math.radians(lon0), math.radians(lat0)
    cosc = math.sin(p0) * np.sin(phi) + math.cos(p0) * np.cos(phi) * np.cos(lam - l0)
    k = np.sqrt(2.0 / np.maximum(1.0 + cosc, 1e-6))
    x = k * np.cos(phi) * np.sin(lam - l0)
    y = k * (math.cos(p0) * np.sin(phi) - math.sin(p0) * np.cos(phi) * np.cos(lam - l0))
    return x, y, cosc


def equal_earth(lon, lat, lon0=0.0, sar=True):
    A1, A2, A3, A4 = 1.340264, -0.081106, 0.000893, 0.003796
    d = np.asarray(lon) - lon0
    lam = np.radians(((d + 180) % 360) - 180 if sar else d)
    phi = np.radians(lat)
    th = np.arcsin(np.sqrt(3) / 2 * np.sin(phi))
    t2 = th * th
    t6 = t2 ** 3
    x = 2 * np.sqrt(3) * lam * np.cos(th) / (3 * (9 * A4 * t6 * t2 + 7 * A3 * t6 + 3 * A2 * t2 + A1))
    y = th * (A4 * t6 * t2 + A3 * t6 + A2 * t2 + A1)
    return x, y, np.ones_like(x)


class Projeksiyon:
    """lon/lat -> piksel (W x H çerçeveyi bölge sınırıyla dolduracak biçimde, en-boy korunur)."""

    def __init__(self, bolge, W: int, H: int):
        b = BOLGELER[bolge] if isinstance(bolge, str) else bolge
        self.b = b
        self.proj = b.get("proj", "laea")
        self.lon0, self.lat0 = b.get("merkez", (0.0, 0.0))
        lo0, la0, lo1, la1 = b["sinir"]
        # sınır kutusunun kenarlarını örnekleyip projeksiyondaki kapsayan kutuyu bul
        ts = np.linspace(0, 1, 60)
        lons = np.concatenate([lo0 + (lo1 - lo0) * ts, np.full(60, lo1), lo1 - (lo1 - lo0) * ts, np.full(60, lo0)])
        lats = np.concatenate([np.full(60, la0), la0 + (la1 - la0) * ts, np.full(60, la1), la1 - (la1 - la0) * ts])
        x, y, _ = self._ham(lons, lats)
        x0, x1, y0, y1 = x.min(), x.max(), y.min(), y.max()
        # bölgenin tamamı görünsün (contain); kalan alan bölgenin çevresiyle dolar
        s = min(W / (x1 - x0), H / (y1 - y0)) * float(b.get("yakin", 1.0))
        self.s = s
        self.cx, self.cy = (x0 + x1) / 2, (y0 + y1) / 2
        self.W, self.H = W, H

    def _ham(self, lon, lat, sar=True):
        if self.proj == "equal_earth":
            return equal_earth(lon, lat, self.lon0, sar)
        return laea(lon, lat, self.lon0, self.lat0)

    def __call__(self, lon, lat, sar=True):
        x, y, cosc = self._ham(np.asarray(lon, float), np.asarray(lat, float), sar)
        px = self.W / 2 + (x - self.cx) * self.s
        py = self.H / 2 - (y - self.cy) * self.s
        return px, py, cosc


def _cizilebilir(px, py, cosc, W, H, pay=0.6) -> bool:
    if np.any(cosc < -0.3):   # LAEA'da dünyanın arka yüzü
        return False
    return not (px.max() < -W * pay or px.min() > W * (1 + pay) or py.max() < -H * pay or py.min() > H * (1 + pay))


class HaritaCizer:
    """Taban harita (deniz + kara + sınırlar) ve vurgulanacak ülkelerin maskeleri, verilen boyutta."""

    def __init__(self, bolge, W: int, H: int, r: str = "50m", ss: int = 2, renk: dict | None = None):
        self.W, self.H = W, H
        self.ulkeler = yukle(r)
        self.proj = Projeksiyon(bolge, W, H)
        # 4. tur: deniz ve kara aydınlatıldı (eski deniz (13, 20, 30), kara (60, 66, 76): dünya haritası karelerinin
        # ortalama parlaklığı ~15-25/255'ti); kırmızı/yeşil/sarı vurgular okunur kalır
        self.renk = {"deniz": (36, 56, 84), "deniz2": (56, 84, 116), "kara": (118, 124, 136), "sinir": (66, 72, 84),
                     "izgara": (50, 72, 98)}
        self.renk.update(renk or {})
        self.ss = ss
        self._poli_cache: dict[str, list[list[tuple[float, float]]]] = {}

    def _poligonlar(self, kod: str, olcek: float) -> list[list[tuple[float, float]]]:
        key = f"{kod}@{olcek}"
        if key not in self._poli_cache:
            out = []
            for ring in self.ulkeler[kod].halkalar:
                px, py, cosc = self._yansit(ring)
                if len(px) < 3 or not _cizilebilir(px, py, cosc, self.W, self.H):
                    continue
                out.append(list(zip((px * olcek).tolist(), (py * olcek).tolist())))
            self._poli_cache[key] = out
        return self._poli_cache[key]

    def _yansit(self, ring: np.ndarray):
        """Halkayı projekte eder. Equal Earth'te kesim boylamını (merkez+180) aşan halka (ör. merkez 10 iken
        Çukotka, St. Lawrence adası) sarılınca haritayı boydan boya geçen bir şerit çiziyordu: böyle bir halka
        sarılmadan, tek parça olarak kenarın biraz dışına taşacak biçimde çizilir (Antarktika gibi tüm
        boylamları dolaşan halkalar olduğu gibi kalır)."""
        lon, lat = ring[:, 0], ring[:, 1]
        if self.proj.proj == "equal_earth" and len(lon) > 1:
            d = ((lon - self.proj.lon0 + 180) % 360) - 180
            if np.abs(np.diff(d)).max() > 180:
                du = np.degrees(np.unwrap(np.radians(d)))
                if np.ptp(du) < 270:
                    m = du.mean()
                    du = du - 360 if m > 180 else du + 360 if m < -180 else du
                    return self.proj(du + self.proj.lon0, lat, sar=False)
        return self.proj(lon, lat)

    def taban(self) -> Image.Image:
        ss = self.ss
        W2, H2 = self.W * ss, self.H * ss
        # deniz: hafif radyal ışık
        yy, xx = np.mgrid[0:self.H, 0:self.W].astype(np.float32)
        d = np.sqrt(((xx - self.W * 0.55) / self.W) ** 2 + ((yy - self.H * 0.45) / self.H) ** 2)
        k = np.clip(1 - d * 1.3, 0, 1)[..., None]
        c1, c2 = np.array(self.renk["deniz"], np.float32), np.array(self.renk["deniz2"], np.float32)
        deniz = Image.fromarray((c1 + (c2 - c1) * k).astype(np.uint8), "RGB").resize((W2, H2), Image.BILINEAR)
        dr = ImageDraw.Draw(deniz)
        # enlem/boylam ızgarası (çok silik)
        for lon in range(-180, 181, 10):
            lats = np.linspace(-80, 85, 120)
            px, py, cosc = self.proj(np.full_like(lats, lon), lats)
            pts = [(x * ss, y * ss) for x, y, c in zip(px, py, cosc) if c > -0.2]
            if len(pts) > 1:
                dr.line(pts, fill=self.renk["izgara"], width=ss)
        for lat in range(-80, 90, 10):
            lons = np.linspace(-180, 180, 240)
            px, py, cosc = self.proj(lons, np.full_like(lons, lat))
            pts = [(x * ss, y * ss) for x, y, c in zip(px, py, cosc) if c > -0.2]
            if len(pts) > 1:
                dr.line(pts, fill=self.renk["izgara"], width=ss)
        # kara + sınırlar
        for kod in self.ulkeler:
            for poly in self._poligonlar(kod, ss):
                dr.polygon(poly, fill=self.renk["kara"])
        for kod in self.ulkeler:
            for poly in self._poligonlar(kod, ss):
                dr.line(poly + [poly[0]], fill=self.renk["sinir"], width=max(1, round(1.4 * ss)), joint="curve")
        return deniz.resize((self.W, self.H), Image.LANCZOS)

    def maske(self, kod: str, asindir: int = 1) -> tuple[Image.Image, tuple[int, int, int, int]] | None:
        """Ülkenin yumuşak kenarlı maskesi (L) ve kutusu. asindir: sınır çizgisi görünsün diye kenardan px."""
        if kod not in self.ulkeler:
            raise KeyError(f"harita: ülke kodu '{kod}' yok (ADM0_A3, ör. DEU, GBR, TUR)")
        ss = self.ss
        m = Image.new("L", (self.W * ss, self.H * ss), 0)
        dr = ImageDraw.Draw(m)
        polys = self._poligonlar(kod, ss)
        if not polys:
            return None
        for poly in polys:
            dr.polygon(poly, fill=255)
        m = m.resize((self.W, self.H), Image.LANCZOS)
        if asindir:
            m = m.filter(ImageFilter.MinFilter(2 * asindir + 1))
        bbox = m.getbbox()
        if not bbox:
            return None
        return m.crop(bbox), bbox

    def etiket_noktasi(self, kod: str) -> tuple[float, float] | None:
        u = self.ulkeler[kod]
        if u.etiket:
            px, py, _ = self.proj(np.array([u.etiket[0]]), np.array([u.etiket[1]]))
            return float(px[0]), float(py[0])
        return None


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "indir":
        rs = [sys.argv[2]] if len(sys.argv) > 2 else ["110m", "50m"]
        kaynak = sys.argv[3] if len(sys.argv) > 3 else None
        for r in rs:
            print("->", indir(r, kaynak))
    else:
        print(__doc__)
