# Horizon Vehicles: Go-Kart, ATV Quad Bike, ATV utilitar, 4x4 Off-Roader, Poliția Română (`gokart_native` v0.13.0)

Mod nativ **FiveM-style de Vehicule 3D** pentru **Horizon 26.3 (Launcher `0.2.69+` / Nightly)**: **Go-Kart**, **ATV Quad Bike**, **ATV utilitar**, **Off-Roader 4x4**, **Autospecială Poliția Română (Pursuit Sedan)** — cu aripi 3D poligonale curbate în 5 segmente pe conturul roții + contra-aripi interioare și praguri continue de la roți la roți, girofar Red/Blue dinamic + sirenă pe tasta `[H]`, faruri emisive (`light_emission: 15`) + blocuri reale `minecraft:light` noaptea, categorie dedicată **Horizon Vehicles** în Creative Inventory și modele 3D verificate fără z-fighting.

Pachetul `dist/gokart_native.hnmod` este **100% autonom (un singur fișier)**: conține atât codul nativ Rust (fizică pe două punți la 20 TPS, drift, charge-boost, tracțiune 4x4 off-road, HUD cu vitezometru analogic + digital, Garaj interactiv de tuning, cameră inteligentă Chase + Free-Look și IK în timp real pentru mâinile șoferului pe volan), cât și pachetul de resurse încorporat (`gokart-content.hmod` cu modele 3D, texturi pixel-art originale, sunete OGG Vorbis sintetizate, rețete Survival și localizare completă în **Română `ro_ro`** și **Engleză `en_us`**).

---

## Caracteristici Principale / Features

### 1. Cele 5 Vehicule & Piese de Tuning (`gokart:*`)
- **Go-Kart (`gokart:go_kart`)** — Șasiu 3D **full-size** calibrat la proporțiile reale MrCrayfish (`~1.57–1.69` blocuri lățime × `~2.24` blocuri lungime, scală `1.28×`), pontoni laterali vopsibili, scaun tip scoică central cu IK dinamic pe volan, rezervor `2.000 mB` și motor posterior animat cu vibrație.
- **ATV Quad Bike (`gokart:quad_bike`)** — ATV agil de traseu cu ghidon articulat `quad_handlebars` + handguards, șa centrală, suspensie vizibilă cu arcuri elicoidale, portbagaje tubulare deschise față/spate, apărători de noroi și margini ranforsate și urcare peste blocuri întregi (`step_height = 1.05`, rezervor `2.800 mB`).
- **ATV utilitar (`gokart:atv`)** — model separat inspirat de ATV-ul din modul original, cu apărătoare frontală, aripi late și portbagaj spate.
- **4x4 Off-Roader (`gokart:off_roader`)** — SUV off-road 4x4 (`~2.14` blocuri lățime × `~3.05` blocuri lungime, `step_height = 1.05`), aripi trapezoidale 3D evazate cu contra-aripi + praguri rock-slider continue de la roată la roată, bullbar îngust central cu troliu, roll-cage cu 4 proiectoare pe plafon, roată de rezervă pe hayon și rezervor `4.000 mB`.
- **Ambulanță Română (`gokart:ambulance`)** — autospecială albă inspirată de Renault Master, cu bandă portocalie, geamuri ample, grilă distinctă și girofar albastru.
- **Autospecială de pompieri (`gokart:fire_truck`)** — cabină de echipaj, compartimente cu rulouri, scară și echipament de pompă modelate vizual; `[H]` activează sirena. Scara, furtunurile și pompa sunt statice și nu sting incendii.
- **Ambulanță SMURD (`gokart:smurd`)** — autospecială roșie inspirată de Sprinter SMURD, cu marcaje POMPIERII, bandă galbenă, grilă distinctă și girofar albastru. Ambele folosesc `[H]` pentru sirenă.
  - Compartimentul medical include targă, dulapuri, monitor, oxigen, scaun și geamuri decupate. Aceste detalii sunt statice: ușile nu se deschid, iar targa nu poate fi folosită pentru transportul unui jucător.
- **Autospecială Poliția Română — Pursuit Sedan (`gokart:police_car`)** — Sedan sportiv de intervenție cu grilă dublă și stroboscoape integrate, aripi curbate în 5 segmente cu contra-aripi + praguri aero și linie mediană continuă de la roți la roți, plafon conectat cu antenă shark-fin, colantare Battenberg albastru/galben-neon `POLIȚIA`, plăcuțe `RO`, laptop MDT în bord și **girofar aerodinamic Red/Blue + sirenă pe `[H]`** (`4.500 mB`).
- **3 Motoare (`Engine Tiers`)**:
  - `gokart:small_engine_iron` — **Motor Mic de Fier**: `52 km/h` pe Go-Kart (`47 km/h` pe Off-Roader), cuplu echilibrat.
  - `gokart:small_engine_gold` — **Motor Mic de Aur**: `64 km/h` pe Go-Kart (`58 km/h` pe Off-Roader), accelerație rapidă.
  - `gokart:small_engine_diamond` — **Motor Mic de Diamant**: `76 km/h` pe Go-Kart (`69 km/h` pe Off-Roader), putere maximă & eficiență ridicată.
- **3 Tipuri de Roți (`Wheels`)**:
  - `gokart:standard_wheel` — **Roți Standard**: aderență echilibrată pe piatră, drum și pământ.
  - `gokart:sports_wheel` — **Roți Sport**: direcție mai rapidă, aderență excelentă off-road și `+12%` încărcare boost din drift.
  - `gokart:racing_wheel` — **Roți Racing Slick**: `+12%` viteză maximă pe asfalt/piatră/beton și `+25%` încărcare boost din drift.
- **Vopsire în 16 Culori (`Minecraft Dyes`)** — Click-dreapta pe Go-Kart sau Off-Roader cu oricare dintre cele 16 vopsele vanilla (`minecraft:*_dye`) pentru a vopsi instant caroseria.
- **Cheie Mecanică (`gokart:wrench`)**:
  - **Click-dreapta pe vehicul**: deschide **Garajul Vehicul & Setări** (demontare motor, alimentare din inventar, împachetare vehicul, comutare *Combustibil Infinit*, *Cameră F5 Automată*, *KM/H vs B/S*).
  - **Click-stânga cu Cheia pe vehicul** (sau butonul din Garaj): strânge Go-Kartul sau Off-Roaderul înapoi în item (`gokart:go_kart` / `gokart:off_roader`), păstrând intacte motorul, roțile, culoarea și nivelul de combustibil!
- **Sistem de Combustibil & Canistră (`gokart:jerry_can`)**:
  - Capacitate Canistră: `5.000 mB` (rezervor Go-Kart: `2.000 mB`; rezervor 4x4 Off-Roader: `4.000 mB` — ambele vin cu **rezervorul plin** la craft/spawn!).
  - Click-dreapta pe vehicul cu Canistra (sau direct cu Cărbune, Cărbune de Lemn, Blaze Powder, Blaze Rod ori Găleată cu Lavă) pentru a alimenta.
  - Click-dreapta cu Canistra pe **Lavă**, **Magma Block** sau **Bloc de Cărbune** în lume pentru a reumple canistra.
  - **Mod Combustibil Infinit**: poate fi activat/dezactivat oricând din panoul Garaj (`[K]`) sau prin comanda `/gokart fuel`.

### 2. Fizică pe Două Punți, Controale & Cameră
- **Geometrie pe două punți (Bicycle-Axle Kinematics)** cu urcare peste dale (`step_height = 0.625` la Go-Kart) și peste **blocuri întregi de 1m** (`step_height = 1.05` la 4x4 Off-Roader!).
- **Controale clasice**:
  - `W` / `S` — Accelerație / Frână & Marșarier
  - `A` / `D` — Viraj stânga / dreapta
  - `Space` (în mers + viraj) — **Frână de mână / Drift** cu scârțâit de anvelope, fum și încărcare Mini-Turbo
  - `W` + `Space` (pe loc) — **Burnout Charge-Boost** (roțile spate patinează pe loc și încarcă bara `BOOST`; eliberarea tastei `Space` lansează vehiculul cu turbo!)
  - `H` — **Claxon** (`gokart:horn`, reconfigurabil în *Options > Mods > Go-Kart*)
  - `K` — **Panou Garaj & Setări** (reconfigurabil în *Options > Mods > Go-Kart*)
  - `Shift` — Coborâre din vehicul (camera revine automat la First-Person)
- **Cameră de condus inteligentă (Chase + Free-Look)**: comută automat în F5 la urcarea în vehicul (`4.0` blocuri pentru Go-Kart, `5.8` blocuri pentru 4x4 Off-Roader), permite rotirea liberă a camerei cu mouse-ul și urmărește lin direcția vehiculului când lași mouse-ul nemișcat.

---

## Rețete de Crafting (Survival)

| Obiect | Model 3x3 | Ingrediente |
|---|---|---|
| **Roată Standard (x2)** | `_ W _` / `W I W` / `_ W _` | `W` = Lână Neagră *(sau Kelp Uscat)*, `I` = Lingou de Fier |
| **Roată Sport** | `_ L _` / `G S G` / `_ L _` | `L` = Piele, `G` = Lingou de Aur, `S` = Roată Standard |
| **Roată Racing Slick** | `_ D _` / `R S R` / `_ D _` | `D` = Bloc de Kelp Uscat, `R` = Redstone, `S` = Roată Sport |
| **Motor Mic de Fier** | `I I I` / `P F P` / `I R I` | `I` = Fier, `P` = Piston, `F` = Cuptor, `R` = Redstone |
| **Motor Mic de Aur** | `G G G` / `G E G` / `R G R` | `G` = Aur, `E` = Motor Mic de Fier, `R` = Redstone |
| **Motor Mic de Diamant** | `D D D` / `D E D` / `B D R` | `D` = Diamant, `E` = Motor Mic de Aur, `B` = Blaze Rod, `R` = Bloc Redstone |
| **Go-Kart** | `I _ L` / `I I I` / `W E W` | `I` = Fier, `L` = Piele, `W` = Roată Standard, `E` = Motor Mic de Fier |
| **ATV Quad Bike** | `B L B` / `I E I` / `W _ W` | `B` = Grilaj Fier, `L` = Piele, `I` = Fier, `E` = Motor Mic de Fier, `W` = Roată Sport |
| **ATV utilitar** | `B L B` / `I E I` / `W _ W` | `B` = Fier, `L` = Piele, `I` = Grilaj Fier, `E` = Motor Mic de Aur, `W` = Roată Sport |
| **4x4 Off-Roader** | `L G L` / `I B I` / `W E W` | `L` = Piele, `G` = Geam, `I` = Fier, `B` = Bloc de Fier, `W` = Roată Sport, `E` = Motor Mic de Aur |
| **Autospecială Poliția Română** | `R L B` / `I I I` / `W E W` | `R` = Redstone, `L` = Piele, `B` = Lapis Lazuli, `I` = Fier, `W` = Roată Racing, `E` = Motor Diamant |
| **Cheie Mecanică** | `I _ I` / `_ I _` / `_ R _` | `I` = Fier, `R` = Vopsea Roșie |
| **Canistră Combustibil** | `_ I R` / `I C I` / `I I I` | `I` = Fier, `R` = Vopsea Roșie, `C` = Cărbune |

---

## Comenzi Rapide (`/vehicle`, `/vehicel` sau `/gokart`)

- `/vehicle kit` *(OP / Singleplayer Cheats)* — Oferă pachetul complet (**Go-Kart**, **ATV Quad Bike**, **ATV utilitar**, **4x4 Off-Roader**, **Autospecială Poliția Română**, **Ambulanță**, **SMURD**, **Pompieri**, motoare Aur/Diamant, roți Sport/Racing, Cheie Mecanică, Canistră plină și vopsele).
- `/vehicle spawn [go_kart | quad_bike | atv | off_roader | police | ambulance | smurd | fire_truck]` *(OP)* — Spawnează instant vehiculul dorit în fața jucătorului.
- `/vehicle remove`, `/vehicle remove <rază>` sau `/vehicle remove all` *(aliasuri: `/vehicel remove [all]`, `/vehicle clear`, `/vehicle delete`, plus butonul **Șterge Definitiv** în Garajul `[K]`)* — Șterge garantat din lume (`native_remove_mob`) atât vehiculele active, cât și vehiculele vechi rămase din sesiuni anterioare, curățând instant și blocurile de lumină.
- `/vehicle fuel` *(OP)* — Comută între consum normal de combustibil și **Combustibil Infinit**.
- `/vehicle paint <culoare>` — Vopsește vehiculul curent/apropiat (`red`, `green`, `blue`, `yellow`, `orange`, `lime`, `cyan`, `black`, `white` etc.).

---

## Instalare & Compilare

### Instalare în Horizon Launcher (`0.2.69+`, canal Nightly)
1. Folosește fișierul pre-împachetat `dist/gokart_native.hnmod` (conține automat și resursele `.hmod` încorporate).
2. În Horizon Launcher, construiește/instalează bundle-ul nativ:
   ```bash
   horizon-launcher native-build dist/gokart_native.hnmod --trust-native-code
   ```
   *(Alternativ, direct din directorul sursă al mixin-ului: `horizon-launcher native-build mixins/gokart_native --trust-native-code`.)*

### Dezvoltare & Testare Locală
```bash
# Rulează testele unitare pentru fizică, drift/boost, pachete rețea și persistență + împachetează determinist .hmod și .hnmod
./tools/build.sh

# Doar regenerare resurse (modele 3D, texturi PNG, sunete OGG Vorbis, traduceri EN/RO) + împachetare în dist/
./tools/build.sh package
```

---

## Structura Proiectului

- `mixins/gokart_native/runtime.rs` — Fizica pură Rust a Go-Kartului (cinematică pe două punți, aderență pe suprafețe, drift, burnout charge-boost, consum combustibil, serializare rețea/disc și teste unitare `cargo test`).
- `mixins/gokart_native/glue.rs` & helperii `*.rs` — Integrarea cu hook-urile native Horizon Nightly (`NATIVE_HOOKS_API` >= 379 / verificat pe `415`).
- `content/` — Modele 3D standalone (`models/block/*.json`), texturi pixel-art (`textures/`), efecte audio OGG Vorbis (`sounds/`), rețete (`data/gokart/recipe/`) și localizări (`lang/en_us.json`, `lang/ro_ro.json`).
- `tools/generate_assets.py` & `tools/build.sh` — Pipeline determinist de generare a resurselor și împachetare `.hmod` / `.hnmod`.
- `dist/gokart_native.hnmod` & `dist/gokart-content.hmod` — Pachetele gata de instalare.

## Licență

Distribuit sub **GNU General Public License v3.0 (`GPL-3.0-or-later`)**. Inspirat de [MrCrayfish's Vehicle Mod](https://github.com/MrCrayfish/MrCrayfishVehicleMod) (GPL-3.0).
