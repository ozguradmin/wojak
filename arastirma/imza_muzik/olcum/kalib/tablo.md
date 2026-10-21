| file | what | TIMBRE | chroma (tools) | chroma T+tempo | fingerprint | audio | symbolic | LUFS | TP | clicks | tempo | key | onsets/bar |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| orijinal | the original itself | 100.0 | 1.000 | 1.000 | 1.000 | FAIL | FAIL | -29.5 | -16.8 | 0 | 152.3 | C minor | 8.1 |
| kopya_aac128 | re-encode AAC-LC 128k | 98.9 | 0.995 | 0.995 | 0.839 | FAIL | - | -29.5 | -17.0 | 0 | 152.3 | C minor | 8.4 |
| kopya_mp3128 | re-encode MP3 128k | 98.3 | 0.995 | 0.995 | 0.823 | FAIL | - | -29.9 | -17.4 | 0 | 152.3 | C minor | 8.3 |
| kopya_tools | tools copy (orijinal_kopya.m4a) | 98.7 | 0.986 | 0.986 | 0.827 | FAIL | - | -31.5 | -18.7 | 0 | 152.3 | C minor | 8.1 |
| orijinal_p2 | original +2 semitones (rubberband) | 55.7 | 0.252 | 0.926 | 0.161 | FAIL | - | -30.3 | -18.0 | 0 | 152.2 | D minor | 5.0 |
| orijinal_m1 | original -1 semitone | 68.2 | 0.162 | 0.880 | 0.212 | FAIL | - | -30.7 | -17.8 | 0 | 152.3 | B minor | 4.8 |
| orijinal_tempo103 | original tempo +3 % | 79.6 | 0.628 | 0.907 | 0.048 | FAIL | - | -30.3 | -17.7 | 0 | 156.7 | C minor | 5.0 |
| orijinal_10klik | original + 10 clicks (-40..-22 dBFS) | 99.9 | 1.000 | 1.000 | 0.997 | FAIL | - | -29.5 | -16.8 | 10 | 152.3 | C minor | 8.2 |
| orijinal_hiss55 | original + hiss -55 dBFS | 86.8 | 0.988 | 0.988 | 0.716 | FAIL | - | -29.4 | -16.8 | 0 | 152.3 | C minor | 8.5 |
| red_imza | rejected imza_vals.m4a | 23.1 | 0.066 | 0.154 | 0.004 | PASS | PASS | -16.1 | -6.5 | 12 | 154.1 | C minor | 2.5 |
| red_ikinci | rejected imza_vals_ikinci.m4a | 24.8 | 0.104 | 0.133 | 0.004 | PASS | PASS | -16.2 | -7.3 | 7 | 154.1 | C minor | 2.6 |
| red_ucuncu | rejected imza_vals_ucuncu.m4a | 27.1 | 0.155 | 0.199 | 0.004 | PASS | PASS | -16.0 | -7.4 | 8 | 154.1 | C minor | 2.6 |
| ilgisiz_gece_vals | unrelated imza_gece_vals.mp3 | 9.8 | 0.139 | 0.190 | 0.005 | PASS | - | -14.8 | -4.0 | 4 | 132.0 | A minor | 3.1 |
| kapak_orijinal_fluid | COVER: original melody+harmony, FluidR3 + chain | 24.6 | 0.499 | 0.514 | 0.006 | FAIL | FAIL | -29.5 | -18.6 | 0 | 151.4 | C minor | 4.6 |
| red_imza_fluid | imza melody, FluidR3 + chain | 33.7 | 0.068 | 0.165 | 0.004 | PASS | PASS | -29.5 | -18.5 | 0 | 154.1 | G minor | 3.2 |
| red_ikinci_fluid | ikinci melody, FluidR3 + chain | 32.8 | 0.101 | 0.145 | 0.004 | PASS | PASS | -29.5 | -18.4 | 0 | 154.0 | C minor | 3.5 |
| red_ucuncu_fluid | ucuncu melody, FluidR3 + chain | 33.2 | 0.117 | 0.180 | 0.004 | PASS | PASS | -29.5 | -18.8 | 0 | 154.1 | G minor | 3.5 |
| rastgele0 | random melody 0, FluidR3 + chain (orig. harmony) | 23.9 | 0.281 | 0.290 | 0.003 | PASS | PASS | -29.5 | -17.3 | 0 | 151.9 | C minor | 3.8 |
| rastgele1 | random melody 1, FluidR3 + chain (orig. harmony) | 29.9 | 0.201 | 0.219 | 0.003 | PASS | PASS | -29.5 | -17.7 | 0 | 152.0 | G minor | 3.8 |
| rastgele2 | random melody 2, FluidR3 + chain (orig. harmony) | 24.4 | 0.231 | 0.235 | 0.003 | PASS | PASS | -29.5 | -16.2 | 0 | 152.1 | G major | 3.6 |
| rastgele3 | random melody 3, FluidR3 + chain (other harmony) | 31.5 | 0.145 | 0.171 | 0.003 | PASS | PASS | -29.5 | -18.4 | 0 | 152.0 | G major | 3.8 |
| rastgele4 | random melody 4, FluidR3 + chain (other harmony) | 30.4 | 0.095 | 0.155 | 0.003 | PASS | PASS | -29.5 | -17.0 | 0 | 152.0 | C minor | 4.1 |
| rastgele5 | random melody 5, FluidR3 + chain (other harmony) | 29.6 | 0.200 | 0.264 | 0.004 | PASS | PASS | -29.5 | -16.5 | 0 | 152.0 | C minor | 3.8 |

| file | ltas_db | mel_env_db | mfcc | band_shares | centroid | flatness | noise_floor | modulation | pitch | stereo | reverb | dynamics | accent |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| orijinal | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 |
| kopya_aac128 | 100 | 100 | 96 | 100 | 100 | 99 | 92 | 100 | 99 | 100 | 100 | 100 | 100 |
| kopya_mp3128 | 100 | 100 | 100 | 100 | 100 | 94 | 82 | 100 | 100 | 100 | 100 | 100 | 100 |
| kopya_tools | 100 | 100 | 96 | 100 | 100 | 99 | 91 | 100 | 98 | 100 | 100 | 100 | 100 |
| orijinal_p2 | 44 | 31 | 31 | 88 | 84 | 99 | 76 | 72 | 78 | 9 | 40 | 60 | 25 |
| orijinal_m1 | 65 | 42 | 55 | 87 | 79 | 93 | 91 | 80 | 87 | 19 | 37 | 65 | 76 |
| orijinal_tempo103 | 98 | 97 | 93 | 83 | 93 | 98 | 97 | 86 | 76 | 19 | 50 | 62 | 61 |
| orijinal_10klik | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 |
| orijinal_hiss55 | 96 | 71 | 43 | 100 | 100 | 61 | 50 | 100 | 98 | 100 | 99 | 99 | 89 |
| red_imza | 28 | 17 | 11 | 86 | 95 | 8 | 11 | 30 | 4 | 2 | 33 | 10 | 4 |
| red_ikinci | 22 | 19 | 11 | 99 | 98 | 7 | 11 | 44 | 4 | 2 | 31 | 12 | 4 |
| red_ucuncu | 34 | 19 | 12 | 97 | 100 | 8 | 11 | 44 | 5 | 2 | 34 | 10 | 8 |
| ilgisiz_gece_vals | 12 | 9 | 4 | 4 | 6 | 2 | 21 | 18 | 4 | 4 | 18 | 8 | 1 |
| kapak_orijinal_fluid | 30 | 39 | 22 | 60 | 70 | 7 | 9 | 11 | 9 | 26 | 56 | 19 | 5 |
| red_imza_fluid | 54 | 27 | 23 | 96 | 97 | 5 | 7 | 33 | 9 | 18 | 53 | 26 | 18 |
| red_ikinci_fluid | 54 | 35 | 26 | 82 | 94 | 5 | 8 | 26 | 9 | 23 | 55 | 33 | 8 |
| red_ucuncu_fluid | 58 | 29 | 24 | 83 | 94 | 5 | 7 | 31 | 8 | 19 | 55 | 29 | 12 |
| rastgele0 | 28 | 30 | 16 | 52 | 67 | 7 | 10 | 15 | 6 | 40 | 66 | 11 | 5 |
| rastgele1 | 29 | 30 | 18 | 60 | 65 | 6 | 9 | 20 | 6 | 45 | 60 | 70 | 9 |
| rastgele2 | 27 | 24 | 13 | 61 | 89 | 7 | 9 | 15 | 8 | 37 | 57 | 15 | 8 |
| rastgele3 | 54 | 28 | 22 | 98 | 99 | 7 | 8 | 26 | 7 | 18 | 52 | 21 | 6 |
| rastgele4 | 50 | 25 | 17 | 97 | 100 | 5 | 8 | 22 | 8 | 26 | 57 | 12 | 11 |
| rastgele5 | 60 | 36 | 26 | 75 | 91 | 6 | 8 | 14 | 8 | 24 | 56 | 6 | 7 |
