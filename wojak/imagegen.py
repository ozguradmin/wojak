"""Yapay zekâ ile wojak karakteri / arka plan üretimi (isteğe bağlı).

Sağlayıcılar (ortam değişkeniyle seçilir, anahtarlar ASLA repoya yazılmaz):
  - openai : OPENAI_API_KEY   (varsayılan model gpt-image-1.5; background=transparent destekler)
  - gemini : GEMINI_API_KEY   (varsayılan model gemini-2.5-flash-image; şeffaflık yok ->
                               beyaz zeminde üretip tools/cutout.py mantığıyla kesilir)

    WOJAK_IMG_PROVIDER=openai|gemini   (boşsa hangi anahtar varsa o)
    WOJAK_IMG_MODEL=<model adı>        (isteğe bağlı)

Komut satırı: python tools/gorsel_uret.py --help
"""

from __future__ import annotations

import base64
import io
import os
from pathlib import Path

import requests
from PIL import Image

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
    p += " Transparent background." if transparent else " Plain pure white (#FFFFFF) background."
    return p


def background_prompt(place: str, time: str = "Evening", mood: str = "Quiet, slightly eerie atmosphere") -> str:
    return BG_STYLE.format(place=place, time=time, mood=mood)


# --- Sağlayıcılar ------------------------------------------------------------

def _provider() -> str:
    p = os.environ.get("WOJAK_IMG_PROVIDER")
    if p:
        return p
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    if os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"):
        return "gemini"
    raise RuntimeError("Görsel üretim anahtarı yok: OPENAI_API_KEY veya GEMINI_API_KEY tanımlayın "
                       "(cloud environment ayarlarından ortam değişkeni olarak).")


def _openai(prompt: str, *, size: str, transparent: bool, refs: list[Path]) -> Image.Image:
    key = os.environ["OPENAI_API_KEY"]
    model = os.environ.get("WOJAK_IMG_MODEL", "gpt-image-1.5")
    common = {"model": model, "prompt": prompt, "size": size, "n": 1, "quality": "high",
              "output_format": "png", "background": "transparent" if transparent else "opaque"}
    headers = {"Authorization": f"Bearer {key}"}
    if refs:
        # Referans görsellerle (stil tutarlılığı için mevcut wojak PNG'leri) düzenleme uç noktası
        files = [("image[]", (p.name, p.read_bytes(), "image/png")) for p in refs]
        data = {k: str(v) for k, v in common.items()}
        r = requests.post("https://api.openai.com/v1/images/edits", headers=headers, data=data,
                          files=files, timeout=300)
    else:
        r = requests.post("https://api.openai.com/v1/images/generations", headers=headers,
                          json=common, timeout=300)
    if r.status_code != 200:
        raise RuntimeError(f"OpenAI hata {r.status_code}: {r.text[:500]}")
    return Image.open(io.BytesIO(base64.b64decode(r.json()["data"][0]["b64_json"])))


def _gemini(prompt: str, *, refs: list[Path]) -> Image.Image:
    key = os.environ.get("GEMINI_API_KEY") or os.environ["GOOGLE_API_KEY"]
    model = os.environ.get("WOJAK_IMG_MODEL", "gemini-2.5-flash-image")
    parts = [{"text": prompt}]
    for p in refs:
        parts.append({"inline_data": {"mime_type": "image/png", "data": base64.b64encode(p.read_bytes()).decode()}})
    r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                      headers={"x-goog-api-key": key, "Content-Type": "application/json"},
                      json={"contents": [{"parts": parts}],
                            "generationConfig": {"responseModalities": ["IMAGE"]}}, timeout=300)
    if r.status_code != 200:
        raise RuntimeError(f"Gemini hata {r.status_code}: {r.text[:500]}")
    for part in r.json()["candidates"][0]["content"]["parts"]:
        blob = part.get("inline_data") or part.get("inlineData")
        if blob:
            return Image.open(io.BytesIO(base64.b64decode(blob["data"])))
    raise RuntimeError("Gemini yanıtında görsel yok")


def generate_character(character: str, out: Path, *, emotion: str = "worried",
                       facing: str = "slightly to the left", refs: list[Path] | None = None) -> Path:
    """Şeffaf arka planlı wojak karakteri üretir ve out'a kaydeder."""
    refs = refs or []
    prov = _provider()
    if prov == "openai":
        prompt = character_prompt(character, emotion, facing, transparent=True)
        if refs:
            prompt = ("Match the exact drawing style of the reference wojak image(s). " + prompt)
        im = _openai(prompt, size="1024x1536", transparent=True, refs=refs)
    else:
        prompt = character_prompt(character, emotion, facing, transparent=False)
        if refs:
            prompt = ("Match the exact drawing style of the reference wojak image(s). " + prompt)
        im = _gemini(prompt, refs=refs)
    im = im.convert("RGBA")
    alpha_min = im.getchannel("A").getextrema()[0]
    if alpha_min == 255:  # şeffaflık gelmediyse beyaz zemini kes
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "cutout", Path(__file__).resolve().parent.parent / "tools" / "cutout.py")
        cutout = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cutout)
        im = cutout.flood_cutout(im, tol=30)
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
        im = _openai(prompt, size="1024x1024", transparent=False, refs=[])
    else:
        im = _gemini(prompt, refs=[])
    out.parent.mkdir(parents=True, exist_ok=True)
    im.convert("RGB").save(out, quality=92)
    return out
