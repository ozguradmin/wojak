# Görsel üretim promptları

`tools/gorsel_uret.py` bu şablonları otomatik kullanır. Elle bir arayüzde (ChatGPT, Gemini,
Midjourney vb.) üretmek gerekirse aşağıdakileri kopyala. **İngilizce prompt daha tutarlı sonuç verir.**

## Hangi model?

| Model | Şeffaf PNG | Not |
|---|---|---|
| OpenAI `gpt-image-1.5` / `gpt-image-1` | **Evet** (`background=transparent`) | En pratik. Referans görselle stil kopyalama iyi. |
| Ideogram 3.0 | Evet (ayrı uç nokta) | Alternatif. |
| Gemini "Nano Banana" (`gemini-2.5-flash-image`) | Hayır | Beyaz zeminde üretilir, `tools/cutout.py` ile kesilir (wojak'ın siyah konturu sayesinde temiz). |
| Flux (Replicate/fal) + wojak LoRA | Hayır | `fal/Wojak-Kontext-Dev-LoRA`, `marckohlbrugge/flux-wojak-v2` — stil en sadık; sonra arka plan kesimi. |

Anahtar tanımı: cloud environment ayarlarına `OPENAI_API_KEY` veya `GEMINI_API_KEY` ortam değişkeni.
**Anahtarı sohbete ya da repoya yazma.**

## Karakter şablonu

```
A single Wojak meme character (the 'feels guy' internet meme) drawn in the classic MS Paint
wojak style: bold uneven black outlines, flat fill colors, no gradients, pale white face with
the iconic wojak features (heavy-lidded tired eyes, small wrinkles, tiny mouth). Bust portrait
from the chest up, body cut off at the bottom edge, head fully visible, facing {YÖN}.
{KARAKTER TARİFİ}. Expression: {DUYGU}. No text, no letters, no watermark, no frame,
no ground shadow, nothing else in the image. Transparent background.
```

İpuçları:
- **Referans ver:** kütüphaneden benzer bir wojak PNG'sini referans olarak eklemek stili sabitler
  (`--ref assets/characters/x.png`). Prompt başına: *"Match the exact drawing style of the reference wojak image."*
- **Bakış yönü:** karakter sağda duracaksa `facing slightly to the left` (sahnenin içine baksın).
- **Benzerlik:** saç rengi/uzunluğu, sakal/bıyık, gözlük, yaş, dönem kıyafeti, meslek üniforması.
- **Kötü karakter:** `menacing grin, dark sunken eyes, shadowed face` veya `face completely black with
  white glowing eyes` (kanalın kötü karakter dili).
- **Gerçek kişi:** yüz benzetme değil, *rol + kıyafet + saç* ile çağrışım yap. Gerçek kişinin yüzünü
  birebir kopyalamaya çalışma.

### Hazır karakter tarifleri

| Rol | Tarif (KARAKTER TARİFİ yerine) | Duygu |
|---|---|---|
| Köy imamı | a Turkish village imam in his 60s, white turban, short grey beard, black robe over a white shirt | calm, slightly suspicious |
| Jandarma | a Turkish gendarmerie officer, olive green uniform and cap, short mustache | serious, shocked |
| Polis | a Turkish police officer, dark navy uniform, police cap with badge | tired, alarmed |
| Taksici | a Turkish taxi driver in his 40s, short black hair, mustache, grey jacket over a checkered shirt | kind, tired smile |
| Anadolu annesi | an Anatolian village mother in her 50s, white headscarf, floral cardigan | worried, teary eyes |
| Öğrenci kız | a Turkish schoolgirl around 12, black school uniform with white collar, two braids | innocent, curious |
| Çoban | an old Anatolian shepherd, flat cap, thick mustache, brown wool coat | wary |
| Lokanta sahibi (kötü) | a middle-aged restaurant cook, white apron with dark stains, bald, thick mustache | menacing grin, dark sunken eyes |
| Kapüşonlu şüpheli | a mysterious figure in a dark hooded coat, face in shadow, only a pale chin visible | unreadable |
| Pilot | an airline pilot in the 1970s, navy uniform, captain hat, headset around neck | panicked |
| Asker (Osmanlı/WW1) | an Ottoman soldier from WW1, kabalak cloth helmet, khaki uniform, ammunition belt | determined |
| Madenci | a Turkish miner, orange high-visibility vest, white helmet with lamp, dusty face | exhausted |
| AFAD kurtarmacı | a Turkish rescue worker, orange AFAD uniform, helmet, dust on face | determined, sad |
| Doktor | a doctor in a white coat, stethoscope, glasses | grave |

## Arka plan şablonu

```
A realistic photograph of {YER}. {ZAMAN}. {ATMOSFER}. No people, no text, no watermark.
Square composition, documentary news-photo look, natural light, slight film grain.
Leave the lower-left and lower-right corners visually simple (a character will be placed there)
and the upper-middle area calm (a caption will be placed there).
```

Örnek YER'ler: `an old Ottoman-era village cemetery in the Black Sea region with mossy tombstones`,
`the empty corridor of a 1990s Turkish primary school, green painted walls`,
`a small Anatolian kebab restaurant kitchen in the 1990s, fluorescent light`,
`a dark cave entrance on a rocky hillside in western Turkey`.

Not: **gerçek mekânın gerçek fotoğrafı her zaman daha iyi.** Üretim sadece bulunamadığında.
