"""Yapay zekâ ile wojak karakteri / arka plan üretimi (isteğe bağlı).

Sağlayıcılar (ortam değişkeniyle seçilir, anahtarlar ASLA repoya yazılmaz):
  - openai : OPENAI_API_KEY   varsayılan model gpt-image-2.5-flare (2026-10). Şeffaf PNG'yi
                              doğrudan verir (background=transparent).
  - gemini : GEMINI_API_KEY   varsayılan model gemini-nano-banana-2.1. Şeffaflık YOK -> düz yeşil
                              zeminde üretilir ve tools/cutout.py mantığıyla kesilir (beyaz zemin
                              kullanılmaz: wojak'ın yüzü de beyaz).

    WOJAK_IMG_PROVIDER=openai|gemini   (boşsa hangi anahtar varsa o)
    WOJAK_OPENAI_MODEL / WOJAK_GEMINI_MODEL   model adını değiştirmek için
    WOJAK_IMG_QUALITY=low|medium|high   (OpenAI; varsayılan medium — wojak çizimi için yeterli, ~4 kat ucuz)

Model durumu (2026-10-09): gpt-image-1 23.10.2026'da, gpt-image-1.5 01.12.2026'da kapanıyor;
gemini-2.5-flash-image kullanımdan kaldırıldı. Ayrıntı: docs/GEREKENLER.md > 3.

Komut satırı: python tools/gorsel_uret.py --help
"""

from __future__ import annotations

import base64
import io
import mimetypes
import os
import time
from pathlib import Path

import requests
from PIL import Image

OPENAI_MODEL = os.environ.get("WOJAK_OPENAI_MODEL", "gpt-image-2.5-flare")
GEMINI_MODEL = os.environ.get("WOJAK_GEMINI_MODEL", "gemini-nano-banana-2.1")
PROVIDERS = {"openai", "gemini"}

# --- Prompt şablonları -------------------------------------------------------

WOJAK_STYLE = (
    "A single Wojak meme character (the 'feels guy' internet meme) drawn in the classic "
    "MS Paint wojak style: bold uneven black outlines, flat fill colors, no gradients, "
    "pale white face with the iconic wojak features (heavy-lidded tired eyes, small "
    "wrinkles, tiny mouth). Bust portrait from the chest up, body cut off at the bottom "
    "edge, head fully visible, facing {facing}. {character}. Expression: {emotion}. "
    "No text, no letters, no watermark, no frame, no ground shadow, nothing else in the image."
)

BG_STYLE = (
    "A realistic photograph of {place}. {time}. {mood}. No people, no text, no watermark. "
    "Square composition, documentary news-photo look, natural light, slight film grain. "
    "Leave the lower-left and lower-right corners visually simple (a character will be "
    "placed there) and the upper-middle area calm (a caption will be placed there)."
)


def character_prompt(character: str, emotion: str = "worried", facing: str = "slightly to the left",
                     transparent: bool = True) -> str:
    p = WOJAK_STYLE.format(character=character.strip().rstrip("."), emotion=emotion, facing=facing)
    # Gemini şeffaf zemin veremiyor: düz yeşil zemin iste (beyaz yüzle karışmaz, kolay kesilir)
    p += " Transparent background." if transparent else " Plain flat pure green (#00FF00) background, no gradient."
    return p


def background_prompt(place: str, time: str = "Evening", mood: str = "Quiet, slightly eerie atmosphere") -> str:
    return BG_STYLE.format(place=place, time=time, mood=mood)


# --- Sağlayıcılar ------------------------------------------------------------

def _provider() -> str:
    p = os.environ.get("WOJAK_IMG_PROVIDER")
    if p:
        if p not in PROVIDERS:
            raise RuntimeError(f"WOJAK_IMG_PROVIDER geçersiz: {p} (geçerli: {sorted(PROVIDERS)})")
        return p
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    if os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"):
        return "gemini"
    raise RuntimeError("Görsel üretim anahtarı yok: OPENAI_API_KEY veya GEMINI_API_KEY tanımlayın "
                       "(cloud environment ayarlarından ortam değişkeni olarak). Bkz. docs/GEREKENLER.md")


def _post(url: str, *, tries: int = 4, **kw) -> requests.Response:
    """429/5xx'te üstel bekleyerek tekrar dener."""
    for k in range(tries):
        r = requests.post(url, timeout=300, **kw)
        if r.status_code not in (429, 500, 502, 503, 504) or k == tries - 1:
            return r
        time.sleep(2 ** (k + 1))
    return r


def _mime(p: Path) -> str:
    return mimetypes.guess_type(p.name)[0] or "image/png"


def _openai(prompt: str, *, size: str, transparent: bool, refs: list[Path]) -> Image.Image:
    key = os.environ["OPENAI_API_KEY"]
    common = {"model": OPENAI_MODEL, "prompt": prompt, "size": size, "n": 1,
              "quality": os.environ.get("WOJAK_IMG_QUALITY", "medium"),
              "output_format": "png", "background": "transparent" if transparent else "opaque"}
    headers = {"Authorization": f"Bearer {key}"}
    if refs:
        # Referans görsellerle (stil tutarlılığı için mevcut wojak PNG'leri) düzenleme uç noktası, en fazla 16
        files = [("image[]", (p.name, p.read_bytes(), _mime(p))) for p in refs[:16]]
        data = {k: str(v) for k, v in common.items()}
        r = _post("https://api.openai.com/v1/images/edits", headers=headers, data=data, files=files)
    else:
        r = _post("https://api.openai.com/v1/images/generations", headers=headers, json=common)
    if r.status_code == 403 and "verif" in r.text.lower():
        raise RuntimeError("OpenAI: kuruluş kimlik doğrulaması gerekli (Settings > Organization > General > "
                           "Verify Organization). Bkz. docs/GEREKENLER.md > 3.")
    if r.status_code != 200:
        raise RuntimeError(f"OpenAI hata {r.status_code}: {r.text[:500]}")
    d = r.json()
    if d.get("usage"):
        print(f"  [openai] {OPENAI_MODEL} kullanım: {d['usage']}")
    return Image.open(io.BytesIO(base64.b64decode(d["data"][0]["b64_json"])))


def _gemini(prompt: str, *, refs: list[Path], aspect: str = "1:1") -> Image.Image:
    key = os.environ.get("GEMINI_API_KEY") or os.environ["GOOGLE_API_KEY"]
    parts = [{"text": prompt}]
    for p in refs[:14]:
        parts.append({"inline_data": {"mime_type": _mime(p), "data": base64.b64encode(p.read_bytes()).decode()}})
    body = {"contents": [{"parts": parts}],
            "generationConfig": {"responseModalities": ["IMAGE"],
                                 "responseFormat": {"image": {"aspectRatio": aspect, "imageSize": "1K"}},
                                 "thinkingConfig": {"thinkingLevel": "MINIMAL"}}}
    r = _post(f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent",
              headers={"x-goog-api-key": key, "Content-Type": "application/json"}, json=body)
    if r.status_code != 200:
        raise RuntimeError(f"Gemini hata {r.status_code}: {r.text[:500]}")
    data = r.json()
    cands = data.get("candidates") or []
    if not cands:
        raise RuntimeError(f"Gemini görsel döndürmedi (güvenlik bloğu?): {data.get('promptFeedback')}")
    img = None
    for part in cands[0].get("content", {}).get("parts", []):
        if part.get("thought"):  # ara "düşünce" görselleri atlanır
            continue
        blob = part.get("inlineData") or part.get("inline_data")
        if blob:
            img = blob  # son (nihai) görsel kalsın
    if not img:
        raise RuntimeError(f"Gemini yanıtında görsel yok (finishReason={cands[0].get('finishReason')})")
    return Image.open(io.BytesIO(base64.b64decode(img["data"])))


def _cutout(im: Image.Image) -> Image.Image:
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "cutout", Path(__file__).resolve().parent.parent / "tools" / "cutout.py")
    cutout = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cutout)
    return cutout.flood_cutout(im, tol=40)


def generate_character(character: str, out: Path, *, emotion: str = "worried",
                       facing: str = "slightly to the left", refs: list[Path] | None = None) -> Path:
    """Şeffaf arka planlı wojak karakteri üretir ve out'a kaydeder."""
    refs = refs or []
    prov = _provider()
    transparent = prov == "openai"
    prompt = character_prompt(character, emotion, facing, transparent=transparent)
    if refs:
        prompt = "Match the exact drawing style of the reference wojak image(s). " + prompt
    if prov == "openai":
        im = _openai(prompt, size="1024x1536", transparent=True, refs=refs)
    else:
        im = _gemini(prompt, refs=refs, aspect="2:3")
    im = im.convert("RGBA")
    hist = im.getchannel("A").histogram()
    clear = sum(hist[:16]) / (im.width * im.height)
    if clear < 0.01:  # şeffaflık gelmediyse (Gemini ya da başarısız) düz zemini kes
        im = _cutout(im)
    bbox = im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
    if bbox:
        im = im.crop(bbox)
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out, optimize=True)
    return out


def generate_background(place: str, out: Path, *, time: str = "Evening",
                        mood: str = "Quiet, slightly eerie atmosphere") -> Path:
    prompt = background_prompt(place, time, mood)
    if _provider() == "openai":
        im = _openai(prompt, size="1088x1088", transparent=False, refs=[])
    else:
        im = _gemini(prompt, refs=[], aspect="1:1")
    out.parent.mkdir(parents=True, exist_ok=True)
    im.convert("RGB").save(out, quality=92)
    return out
