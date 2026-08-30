# Skien — kartdata for STORBY

3 × 2 km av Skien sentrum, brukt som verden i spillet.

## Rammen

EPSG:25833 (UTM33N) flyttet til origo, sentrert 400 m sør for Skien torg
(UTM 192365,6 / 6575315,6 — WGS84 ca. 59,2049 N 9,6090 Ø).

    spill-x =  E - E0     øst er +x      x ∈ [-1500, 1500]   -> CITY_W 3000
    spill-z = -(N - N0)   nord er -z     z ∈ [-1000, 1000]   -> CITY_D 2000

1 enhet = 1 meter. Torget ligger på (0, -400).

## Filer

| Fil | Innhold |
|---|---|
| `skien.json` | 2 706 veier, 6 695 bygninger med høyde, 64 vannflater, 127 grøntområder |
| `skien_terreng.bin` | høydemodell, uint16 little-endian, 600 × 400 à 5 m, radvis fra nordvest |
| `skien.osm.json` | rå Overpass-svar |
| `skien_dtm.tif` | rå DTM fra Kartverket, float32 GeoTIFF |
| `convert.py` | konverteringen — kjør på nytt for å endre utsnitt, veibredder eller høyder |
| `utm.py` | fram- og tilbakeprojeksjon WGS84 ↔ UTM33 |
| `query.overpass` | Overpass-spørringen |
| `forhandsvisning.png` | tegnet rett fra `skien.json`, for å se at data stemmer |

Høyde leses slik: `h = min_m + (u16 / 65535) * (maks_m - min_m)`, med `min_m`
og `maks_m` fra `meta.terreng` i `skien.json`.

## Nytt utsnitt

1. Endre `E0, N0` øverst i `convert.py`
2. Regn ut ny lat/lon-boks (bruk `utm332ll` på de fire hjørnene, legg på margin)
3. Oppdater boksen i `query.overpass`, last ned OSM på nytt
4. Last ned DTM på nytt via WCS 1.0.0 (`bbox=minE,minN,maxE,maxN`, `width`/`height`)
5. `python3 convert.py`

## Lisens

- Kartdata: © OpenStreetMap-bidragsytere, [ODbL](https://opendatacommons.org/licenses/odbl/)
- Terreng: Kartverket, DTM1 fra hoydedata.no, [NLOD](https://data.norge.no/nlod/no/)

Begge krever navngivelse. Spillet viser kilden i HUD-en (`#kildeline`) — den
linja må bli stående så lenge dataene brukes.
