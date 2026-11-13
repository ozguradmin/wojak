"""Bölüm (episode) YAML şeması ve yükleyicisi.

Örnek ve tüm alanların açıklaması: episodes/_sablon/episode.yaml
"""

from __future__ import annotations

import zlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from . import config

SCENE_TYPES = {"dialog", "card", "evidence", "image"}
TEXT_STYLES = {"outline", "bubble", "bubble_dark", "none"}


class EpisodeError(ValueError):
    pass


@dataclass
class Character:
    img: Path
    side: str = "right"          # left | right | center
    height: float = config.CHAR_HEIGHT  # kare yüksekliğine oranı (altın dönem medyanı %48)
    x: float | None = None       # 0..1, verilirse side yerine kullanılır (karakterin merkezi)
    y_offset: float = 0.0        # + aşağı, - yukarı (kare oranı)
    flip: bool = False           # yalnızca bakış yönü bilinmiyorsa ya da karakter ortadaysa kullanılır
    faces: str | None = None     # PNG'nin KENDİ baktığı yön (right/left/front; sag/sol/on), olması gereken yön değil;
                                 # data/karakter_yon.json'da kayıt varsa kayıt geçerli (kısa reel)
    pop: bool = False            # sahne başında "pop-in" (altın dönemde YOK: sabit görüntü, sert kesme)


@dataclass
class Sfx:
    file: Path
    at: float = 0.0              # sahne başına göre saniye
    volume: float = 1.0


@dataclass
class Scene:
    type: str
    duration: float
    bg: Path | None = None
    images: list[Path] = field(default_factory=list)
    chars: list[Character] = field(default_factory=list)
    text: str | None = None
    text_style: str = "outline"
    text_y: float | None = None  # yazı bloğunun merkezi (kare oranı); None = konuşanın başının hemen üstü
    text_size: int = config.DIALOG_SIZE
    zoom: float = 1.0            # Ken Burns (altın dönemde YOK; >1 verilirse sahne boyunca yakınlaşır)
    pan: tuple[float, float] = (0.0, 0.0)  # zoom sırasında kayma yönü (-1..1)
    focus: tuple[float, float] = (0.5, 0.5)  # arka plan kare kırpılırken odak (0..1, 0..1)
    darken: float = 0.0          # 0..1 arka planı karart
    blur: float = config.BG_BLUR  # arka plan yumuşatma (px; altın dönem fotoğrafları yumuşak, karakter keskin)
    grayscale: bool = False
    shake: float = 0.0           # 0 = yok; 6-14 px dramatik sarsıntı
    flash: bool = False          # sahne başında beyaz flaş
    banner: str | None = None    # kanıt sahnesi haber bandı
    label: str | None = None     # küçük etiket (örn. "Gerçek fotoğraf")
    sfx: list[Sfx] = field(default_factory=list)
    voice: Path | None = None    # isteğe bağlı seslendirme dosyası


@dataclass
class Music:
    file: Path
    start: float = 0.0
    volume: float = 1.0          # son miks zaten LOUDNESS_LUFS'a normalize edilir
    fade_in: float = 0.0
    fade_out: float = 0.0        # orijinallerde parça kesilerek biter
    loop: bool = False           # orijinallerde döngü yok
    ad: str | None = None        # kısa ad (kanal, klasik, gizem...): muzik_dosyasi(); dosya yoluysa None


@dataclass
class Episode:
    id: str
    dir: Path
    title: str
    scenes: list[Scene]
    layout: str = "square"       # square | full
    watermark: str | None = config.WATERMARK
    top_text: str | None = None
    music: Music | None = None
    caption: str = ""
    pinned_comment: str = ""
    hashtags: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    notes: str = ""
    gundem: bool = False         # güncel olay: docs/GUNDEM.md kuralları ve dil denetimi uygulanır
    kesin_hukum: bool = False    # failin mahkûmiyeti kesinleşmiş mi (değilse "katil" vb. yasak)
    yasak_sorgu: str = ""        # gündem: yayın yasağı aramasının 2-3 ayırt edici kelimesi (isim, yer); bot 14 gün arar
    olay_yeri: str = ""          # gündem: ilçe ve il ("Gebze, Kocaeli"); bot RTÜK listesinde bu yerin mahkemesine bakar
    ai_generated: bool = False   # fotogerçekçi yapay zekâ görseli var mı (platformlarda etiket zorunlu)
    credits: str = ""            # görsel atfı (CC BY lisansı şart koşar); açıklamalara 'Görseller: ...' olarak eklenir
    cover_scene: int | None = None  # kapak sahnesi (1'den başlar); yoksa ilk diyalog sahnesi
    cover_at: float = 0.9        # kapak karesinin sahne içindeki yeri (0-1)
    telif_notu: str = ""         # telifli görseller için hesap sahibine özel lisans notu (paylaşım paketinde)
    ek_maddeler: list[str] = field(default_factory=list)  # paylaşım kontrol listesine bölüme özel maddeler
    uzun_video: str = ""         # aynı konunun uzun YouTube videosu (bağlantı ya da "yakında"); Shorts açıklamasına eklenir
    kanal: str = "tr"            # kanal profili (config.KANALLAR): tr = Tarihsel Wojak, en = Wojak Past Files

    @property
    def duration(self) -> float:
        return sum(s.duration for s in self.scenes)


_TR_ASCII = str.maketrans("ıİüÜşŞçÇöÖğĞ", "iIuUsScCoOgG")


def _muzik_adi(ad: str) -> str:
    """Kısa adlar Türkçe harfle de yazılabilir: destansı -> destansi, hüzün -> huzun."""
    sade = ad.strip().translate(_TR_ASCII).lower()
    return sade if sade in ("kanal", "imza", "huzun", "klasik", "orijinal", *config.HAVALAR) else ad


def muzik_dosyasi(ad: str, bolum_id: str) -> Path | None:
    """`music:` kısa adını dosyaya çevirir; kısa ad değilse None (o zaman dosya yolu olarak aranır). 12.11.2026:

    kanal | imza | huzun       -> imza vals Gölge (hüzün, trajedi; klasik sırası değilse kararsızken bu)
    klasik | orijinal          -> eski kanal sesi (özel depodan, tools/hazirla.sh kopyalar); yoksa imza ve `check` uyarır
    gizem | merak | ironik | destansi | masal
                               -> o havanın parçalarından biri, bölüm kimliğine göre SABİT seçilir (yeniden render aynı
                                  parçayı verir; bölümden bölüme parça değişir)
    gizem_a, merak_b ...       -> o parça (assets/music/hava/<ad>.m4a)
    """
    imza = config.MUSIC_IMZA if config.MUSIC_IMZA.exists() else config.MUSIC_FALLBACK
    if ad in ("kanal", "imza", "huzun"):
        return imza
    if ad in ("klasik", "orijinal"):
        return config.MUSIC_CHANNEL if config.MUSIC_CHANNEL.exists() else imza
    if ad in config.HAVALAR:
        secenek = sorted(config.MUSIC_HAVA.glob(f"{ad}_*.m4a"))
        if not secenek:
            raise EpisodeError(f"music: {ad}: {config.MUSIC_HAVA}/{ad}_*.m4a yok")
        return secenek[zlib.crc32(bolum_id.encode("utf-8")) % len(secenek)]
    if "/" not in ad and "." not in ad:
        tam = config.MUSIC_HAVA / f"{ad}.m4a"
        if tam.is_file():
            return tam
    return None


def _resolve(base: Path, p: str | None, kind: str = "file") -> Path | None:
    if p is None:
        return None
    p = str(p)
    candidates = [base / p, config.ROOT / p]
    if kind == "char":
        candidates += [config.CHARACTERS / p, config.CHARACTERS / f"{p}.png"]
    if kind == "sfx":
        candidates += [config.SFX / p, config.SFX / f"{p}.wav", config.SFX / f"{p}.mp3"]
    if kind == "music":
        candidates += [config.MUSIC / p, config.SFX / p]  # sfx/drone.wav altlık olarak kullanılabilir
    for c in candidates:
        if c.is_file():
            return c.resolve()
    raise EpisodeError(f"Dosya bulunamadı ({kind}): {p}  (aranan: {[str(c) for c in candidates]})")


def _char(base: Path, d: Any) -> Character:
    if isinstance(d, str):
        d = {"img": d}
    d = dict(d)
    d["img"] = _resolve(base, d["img"], "char")
    return Character(**d)


def _sfx(base: Path, d: Any) -> Sfx:
    if isinstance(d, str):
        d = {"file": d}
    d = dict(d)
    d["file"] = _resolve(base, d["file"], "sfx")
    return Sfx(**d)


def _scene(base: Path, i: int, d: dict) -> Scene:
    d = dict(d)
    t = d.get("type", "dialog")
    if t not in SCENE_TYPES:
        raise EpisodeError(f"Sahne {i + 1}: bilinmeyen type '{t}' (geçerli: {sorted(SCENE_TYPES)})")
    if "duration" not in d:
        raise EpisodeError(f"Sahne {i + 1}: duration zorunlu")
    if d.get("text_style", "outline") not in TEXT_STYLES:
        raise EpisodeError(f"Sahne {i + 1}: text_style geçersiz")
    if "bg" in d:
        d["bg"] = _resolve(base, d["bg"])
    imgs = d.pop("images", None) or ([d.pop("image")] if "image" in d else [])
    d["images"] = [_resolve(base, p) for p in imgs]
    d["chars"] = [_char(base, c) for c in d.pop("chars", None) or []]
    d["sfx"] = [_sfx(base, s) for s in d.pop("sfx", None) or []]
    if d.get("voice"):
        d["voice"] = _resolve(base, d["voice"])
    for k in ("pan", "focus"):
        if k in d:
            d[k] = tuple(d[k])
    if t == "dialog" and d.get("bg") is None:
        raise EpisodeError(f"Sahne {i + 1}: dialog sahnesi için bg (arka plan görseli) gerekli")
    if t == "evidence" and not d["images"]:
        raise EpisodeError(f"Sahne {i + 1}: evidence sahnesi için images gerekli")
    known = set(Scene.__dataclass_fields__)
    extra = set(d) - known
    if extra:
        raise EpisodeError(f"Sahne {i + 1}: bilinmeyen alan(lar): {sorted(extra)}")
    return Scene(**d)


def load(path: str | Path) -> Episode:
    path = Path(path)
    if path.is_dir():
        path = path / "episode.yaml"
    base = path.parent.resolve()
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not raw.get("scenes"):
        raise EpisodeError("scenes boş olamaz")
    scenes = [_scene(base, i, s) for i, s in enumerate(raw["scenes"])]
    music = None
    if raw.get("music"):
        m = raw["music"]
        if isinstance(m, str):
            m = {"file": m}
        m = dict(m)
        ad = _muzik_adi(str(m["file"]))
        kisa = muzik_dosyasi(ad, str(raw.get("id") or base.name))
        if kisa is not None:
            m["ad"], m["file"] = ad, str(kisa)
        m["file"] = _resolve(base, m["file"], "music")
        music = Music(**m)
    kanal = str(raw.get("kanal") or "tr")
    if kanal not in config.KANALLAR:
        raise EpisodeError(f"bilinmeyen kanal '{kanal}' (geçerli: {sorted(config.KANALLAR)})")
    return Episode(
        id=raw.get("id") or base.name,
        dir=base,
        title=raw.get("title", base.name),
        scenes=scenes,
        layout=raw.get("layout", "square"),
        watermark=raw.get("watermark", config.KANALLAR[kanal]["watermark"]),
        top_text=raw.get("top_text"),
        music=music,
        caption=raw.get("caption", "") or "",
        pinned_comment=raw.get("pinned_comment", "") or "",
        hashtags=list(raw.get("hashtags") or []),
        sources=list(raw.get("sources") or []),
        notes=raw.get("notes", "") or "",
        gundem=bool(raw.get("gundem", False)),
        kesin_hukum=bool(raw.get("kesin_hukum", False)),
        yasak_sorgu=str(raw.get("yasak_sorgu") or "").strip(),
        olay_yeri=str(raw.get("olay_yeri") or "").strip(),
        ai_generated=bool(raw.get("ai_generated", False)),
        credits=str(raw.get("credits") or "").strip(),
        cover_scene=raw.get("cover_scene"),
        cover_at=float(raw.get("cover_at", 0.9)),
        telif_notu=str(raw.get("telif_notu") or "").strip(),
        ek_maddeler=[str(x) for x in raw.get("ek_maddeler") or []],
        uzun_video=str(raw.get("uzun_video") or "").strip(),
        kanal=kanal,
    )
