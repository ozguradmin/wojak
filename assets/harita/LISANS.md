# Harita verisi

`ne_*_admin_0_countries.geojson.gz`: Natural Earth, Admin 0 – Countries (1:110m ve 1:50m), v5.
Kaynak: https://www.naturalearthdata.com/ (GeoJSON kopyası: https://github.com/nvkelso/natural-earth-vector).

**Lisans: kamu malı (public domain).** "All versions of Natural Earth raster + vector map data found on this
website are in the public domain. You may use the maps in any manner, including modifying the content and
design, electronic dissemination, and offset printing." (https://www.naturalearthdata.com/about/terms-of-use/)
Atıf gerekmez; açıklamada "Harita verisi: Natural Earth" yazmak iyi uygulamadır.

Değişiklik: yalnız ADM0_A3, NAME, NAME_TR, LABEL_X/Y, CONTINENT alanları tutuldu; koordinatlar 3 ondalığa
yuvarlandı (`python -m wojak.uzun.harita indir`). Not: sınırlar bugünkü sınırlardır (ör. 1957'nin Batı/Doğu
Almanya'sı ayrı değildir); tarihî harita gerekiyorsa anlatımda belirt.
