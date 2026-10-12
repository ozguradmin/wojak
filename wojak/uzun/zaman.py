"""Zaman çizelgesi: satır sesleri + aralar -> sahne süreleri (kare ızgarasında) -> mutlak zamanlar.

Kurallar
- Sahne içi: `bas` bekle, satır 1, `ara`, satır 2, ..., son satır, `son` bekle (sahne/video ayarı).
  Satırın `once`'si o satırdan önceki arayı, `sonra`'sı satırdan sonra ek beklemeyi belirler.
- Sahne süresi = max(satırlar + aralar, min_sure, sure). Satırsız sahne: `sure` (yoksa tipin varsayılanı).
- Süre kareye yuvarlanır (n_kare = round(süre * fps)); sahne başları tam kare sınırındadır, satır sesleri
  örnek hassasiyetinde (sahne_başı + t0) yerleştirilir. Böylece görüntü ve ses kayma yapmaz.
- Geçiş (gecis/kaydir) yeni sahnenin ilk karelerinde olur, toplam süreyi değiştirmez.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import FPS
from .spec import Olay, Sahne, Satir, Sfx, Video, ara_sureleri, temiz_metin

TR_HIZ = 14.5   # sn başına harf (boşluk dahil), hız 1.0'da: Cartesia Türkçe anlatıcı ölçümü (~)


def tahmini_sure(metin: str, hiz: float = 1.0) -> float:
    """TTS yokken satır süresi tahmini (ön izleme / test için)."""
    t = temiz_metin(metin)
    return round(len(t) / TR_HIZ / max(hiz, 0.1) + ara_sureleri(metin) + 0.2, 3)


def _capa_zamani(sahne: Sahne, satir: int | None, an: str, t: float | None, ofset: float) -> float:
    if satir is not None:
        s = sahne.satirlar[satir - 1]
        base = s.t1 if an == "son" else s.t0
    else:
        base = t or 0.0
    return base + ofset


def sahne_zamanla(sahne: Sahne, zam: dict, fps: int = FPS) -> None:
    """Satırların sahne içi başlangıçlarını, olay/sfx zamanlarını ve sahne süresini hesaplar."""
    bas = zam["bas"] if sahne.bas is None else sahne.bas
    ara = zam["ara"] if sahne.ara is None else sahne.ara
    son = zam["son"] if sahne.son is None else sahne.son
    t = bas
    for i, s in enumerate(sahne.satirlar):
        if s.sure is None:
            raise ValueError(f"{sahne.yer}: satır {i + 1} süresi yok (önce seslendir ya da tahmin kullan)")
        if i > 0:
            t += ara if s.once is None else s.once
        elif s.once is not None:
            t = s.once
        s.t0 = round(t, 4)
        t += s.sure + (s.sonra or 0.0)
    if sahne.satirlar:
        dur = t + son
        dur = max(dur, zam["min_sahne"] if sahne.min_sure is None else sahne.min_sure)
        if sahne.sure is not None:
            dur = max(dur, sahne.sure)
    else:
        dur = sahne.sure if sahne.sure is not None else (zam["kart"] if sahne.tip == "bolum_karti" else zam["sabit"])
        if sahne.min_sure is not None:
            dur = max(dur, sahne.min_sure)
    sahne.n_kare = max(1, round(dur * fps))
    sahne.sure_hesap = sahne.n_kare / fps
    son_t = sahne.sure_hesap
    for o in sahne.olaylar:
        o.zaman = min(max(0.0, _capa_zamani(sahne, o.satir, o.an, o.t, o.ofset)), son_t)
    for x in sahne.sfx:
        x.zaman = min(max(0.0, _capa_zamani(sahne, x.satir, x.an, x.t, x.ofset)), son_t)


def balon_olaylari(sahne: Sahne) -> list[Olay]:
    """Satıra bağlı balonlar (satir.balon) -> balon olayları; açık 'balon' olaylarıyla birlikte."""
    out = [o for o in sahne.olaylar if o.tip == "balon"]
    for i, s in enumerate(sahne.satirlar):
        if s.balon:
            o = Olay(tip="balon", satir=i + 1, ofset=-0.08,
                     p={"karakter": s.balon, "metin": s.altyazi, "sure": (s.sure or 0) + 0.35})
            o.zaman = max(0.0, s.t0 - 0.08)
            out.append(o)
    out.sort(key=lambda o: o.zaman)
    return out


@dataclass
class SatirZamani:
    sahne: Sahne
    satir: Satir
    bas: float   # mutlak (sn)
    son: float


@dataclass
class Zaman:
    video: Video
    sahneler: list[Sahne]
    fps: int
    toplam_kare: int

    @property
    def sure(self) -> float:
        return self.toplam_kare / self.fps

    def sahne_basi(self, s: Sahne) -> float:
        return s.bas_kare / self.fps

    def satirlar(self) -> list[SatirZamani]:
        out = []
        for s in self.sahneler:
            b = self.sahne_basi(s)
            for st in s.satirlar:
                out.append(SatirZamani(s, st, b + st.t0, b + st.t1))
        return out

    def bolum_baslari(self) -> list[tuple[str, float]]:
        """(bölüm adı, mutlak başlangıç sn) — bölümün ilk sahnesinin (kart dahil) başı."""
        out = []
        for b in self.video.bolumler:
            if b.sahneler:
                out.append((b.youtube or b.baslik, self.sahne_basi(b.sahneler[0])))
        return out

    def sahne_at(self, t: float) -> tuple[Sahne, float]:
        """Mutlak t anındaki sahne ve sahne içi zaman."""
        k = int(t * self.fps)
        for s in self.sahneler:
            if s.bas_kare <= k < s.bas_kare + s.n_kare:
                return s, t - self.sahne_basi(s)
        s = self.sahneler[-1]
        return s, s.sure_hesap - 1 / self.fps


def hesapla(video: Video, fps: int = FPS, tahmin: bool = False) -> Zaman:
    """Bütün videonun zaman çizelgesi. tahmin=True: süresi bilinmeyen satırlar için metinden tahmin."""
    k = 0
    for s in video.sahneler:
        for st in s.satirlar:
            if st.sure is None and tahmin:
                st.sure, st.tahmini = tahmini_sure(st.metin, st.hiz), True
        sahne_zamanla(s, video.zamanlama, fps)
        s.bas_kare = k
        k += s.n_kare
    return Zaman(video=video, sahneler=video.sahneler, fps=fps, toplam_kare=k)


def tum_sfx(z: Zaman) -> list[tuple[float, Sfx]]:
    """Spesifikasyondaki açık sfx'ler, mutlak zamanlarıyla."""
    return [(z.sahne_basi(s) + x.zaman, x) for s in z.sahneler for x in s.sfx]


def zaman_str(t: float, ms: bool = False) -> str:
    t = max(0.0, t)
    m, s = divmod(t, 60)
    h, m = divmod(int(m), 60)
    if ms:
        return f"{h:d}:{m:02d}:{s:06.3f}" if h else f"{m:d}:{s:06.3f}"
    s = int(s)
    return f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:d}:{s:02d}"
