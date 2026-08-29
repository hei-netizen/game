# STORBY v3

Prosedural by på **3 × 2 km** med PBR-materialer, fotoskannede gate-props og multiplayer.

**Live:** https://hei-netizen.github.io/game/storby/
**Repo:** `hei-netizen/game`, mappe `storby/` (klonet lokalt i `~/sol-city-online`)

## Kjøre lokalt

⚠️ **Kan ikke lenger dobbeltklikkes.** Spillet bruker ES-moduler og laster `.glb`-filer,
og nettleseren blokkerer begge deler på `file://`. Start en lokal server:

```bash
cd "creative-workspace/exports/game (jona og simon)"
python3 -m http.server 8000
# åpne http://localhost:8000
```

Eller bare bruk den live lenken over.

## Kontroller

| Tast | Handling |
|---|---|
| `W A S D` | gå · `Shift` løp · `Space` hopp |
| `F` | fly-modus (`Space`/`Ctrl` opp/ned) |
| `N` | natt/dag — vinduene tennes |
| `T` | skygger av/på (skru av hvis det henger) |
| `R` | ny by — **kun verten** i multiplayer |
| `Esc` | slipp musepekeren |

Du kan gå på hustakene.

## Innhold (målt kjøring)

- **3 657 bygninger** i 425 kvartaler, 44 gater
- **1 710 props** fra Poly Haven, 16 ulike modeller
- Høyeste tårn 187 m · 5 bydeler · 280 biler i trafikk

## Hva som gjør at det ser ekte ut

```
PBR-materialer     Hver fasade genererer 4 kart på canvas: albedo, høydekart
                   → normalkart (Sobel), ruhet/metall (grønn/blå kanal), og
                   emissive for nattlys. Vinduer får ruhet 0.06 + metall 0.88,
                   vegg 0.9/0.0 — derfor speiler glasset og pussen ikke.

Miljøkart          Himmelen rendres til en PMREM-tekstur som settes som
                   scene.environment. Det er dette som gjør at glassfasadene
                   faktisk reflekterer omgivelsene i stedet for å være malt blå.

Gateplan           Egen tekstur for de nederste 5,4 m: butikkvinduer med varer,
                   markiser, skiltbånd, inngangsdører, granittsokkel. Dette er
                   den største enkeltforskjellen mellom "boks med vinduer" og
                   noe som ser ut som en gate.

Bygningsformer     Rett volum, podium+tårn, L-form, saltak i boligstrøk,
                   tilbakespring på høyhus, gesims rundt alle takkanter.
                   Per-bygg fargetone via vertex colors.

Heltalls UV        Fasadeteksturen repeteres et helt antall ganger per vegg,
                   så et vindu blir aldri kuttet på midten. Vindusstørrelsen
                   varierer litt mellom bygg — som også gir variasjon gratis.
```

## Poly Haven-props

16 fotoskannede CC0-modeller. Rå er de ubrukelige på web — **5,5 MB hver**.
Pipeline som fikser det:

```bash
python3 fetch_ph.py fire_hydrant          # laster gltf + bin + teksturer
npx @gltf-transform/cli@4 optimize src/fire_hydrant/fire_hydrant.gltf opt/fire_hydrant.glb \
  --texture-size 512 --texture-compress webp --compress quantize \
  --simplify true --simplify-ratio 0.12 --simplify-error 0.004
# 5,52 MB → 277 KB
```

Scriptene ligger i scratchpad; kopier dem hit hvis du vil legge til flere.
Hele `hidden_alley`-samlingen har 39 assets — vi bruker 16.

Props instanseres per romlig rute (5×4) slik at frustum culling virker.
Vil du ha tettere gater: øk tallene i `PROP_DEF` øverst i prop-seksjonen.
Jeg testet 2 600 props og programvare-rendereren knakk — på ekte GPU tåler
den sannsynligvis mer, men det må testes på faktisk maskinvare.

## Multiplayer

WebRTC via PeerJS, stjernetopologi. Første som åpner lenken blir vert,
resten kobler seg på automatisk. Ingen server, ingen romkode.
Verten eier `SEED`, så alle står i samme by. `?rom=NAVN` gir eget rom.

## Kjente mangler

- Props har **ingen kollisjon** — du går tvers gjennom gatelys og benker
- Ingen fotgjengere
- Ingen kjørbar bil (bilene er trafikk-kulisser)
- Ingen interiører — dører er tekstur, ikke ganger
- Glassfasadene har synlig rutemønster på avstand

## Lisens

Koden er din. three.js: MIT. Poly Haven-modeller: CC0. PeerJS: MIT.
