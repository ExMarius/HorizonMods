# Horizon Vehicles: Go-Kart, Quad Bike ATV & 4x4 Off-Roader (`gokart_native` v0.6.0)

Mod nativ complet de **Vehicule 3D (Go-Kart full-size & 4x4 Off-Roader)** pentru **Horizon 26.3 (Launcher `0.2.69+` / Nightly)**, inspirat din celebrul [MrCrayfish's Vehicle Mod](https://github.com/MrCrayfish/MrCrayfishVehicleMod) (implementare și design 100% originale, compatibile GPL-3.0).

Pachetul `dist/gokart_native.hnmod` este **100% autonom (un singur fișier)**: conține atât codul nativ Rust (fizică pe două punți la 20 TPS, drift, charge-boost, tracțiune 4x4 off-road, HUD cu vitezometru analogic + digital, Garaj interactiv de tuning, cameră inteligentă Chase + Free-Look și IK în timp real pentru mâinile șoferului pe volan), cât și pachetul de resurse încorporat (`gokart-content.hmod` cu modele 3D, texturi pixel-art originale, sunete OGG Vorbis sintetizate, rețete Survival și localizare completă în **Română `ro_ro`** și **Engleză `en_us`**).

---

## Caracteristici Principale / Features

### 1. Vehicule & Piese de Tuning (`gokart:*`)
- **Go-Kart (`gokart:go_kart`)** — Șasiu 3D **full-size** calibrat la proporțiile reale MrCrayfish (`~1.57–1.69` blocuri lățime la anvelope × `~2.24` blocuri lungime, scală `1.28×`), pontoni laterali vopsibili (`tintindex`), scaun tip scoică central în care șoferul stă fixat cu mâinile pe volanul cu 3 spițe (`32°`, IK dinamic sincronizat cu virajul), rezervor `2.000 mB` și motor posterior animat cu vibrație.
- **4x4 Off-Roader (`gokart:off_roader`)** — SUV off-road 4x4 original (`~2.14` blocuri lățime × `~3.05` blocuri lungime, scală `1.40×`, gardă la sol înaltă și urcare automată peste blocuri întregi `step_height = 1.05`!), bullbar din oțel cu proiectoare, roll-cage tubular cu 4 proiectoare pe plafon, roată de rezervă pe hayon, post de conducere pe partea stângă cu mâinile pe volan (IK dedicat), tracțiune superioară pe iarbă/pământ/nisip/noroi/zăpadă și rezervor dublu de `4.000 mB`!
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
| **4x4 Off-Roader** | `B G L` / `I E I` / `W I W` | `B` = Bloc de Fier, `G` = Sticlă, `L` = Piele, `I` = Fier, `E` = Motor Mic de Aur, `W` = Roată Sport |
| **Cheie Mecanică** | `I _ I` / `_ I _` / `_ R _` | `I` = Fier, `R` = Vopsea Roșie |
| **Canistră Combustibil** | `_ I R` / `I C I` / `I I I` | `I` = Fier, `R` = Vopsea Roșie, `C` = Cărbune |

---

## Comenzi Rapide

- `/gokart kit` *(OP / Singleplayer Cheats)* — Oferă pachetul complet de testare (**Go-Kart**, **4x4 Off-Roader**, motoare Aur/Diamant, roți Sport/Racing, Cheie Mecanică, Canistră plină și vopsele).
- `/gokart spawn` sau `/gokart spawn off_roader` *(OP)* — Spawnează instant un Go-Kart sau un 4x4 Off-Roader în fața jucătorului.
- `/gokart fuel` *(OP)* — Comută între consum normal de combustibil și **Combustibil Infinit**.
- `/gokart paint <culoare>` — Vopsește vehiculul curent/apropiat (`red`, `green`, `blue`, `yellow`, `orange`, `lime`, `cyan`, `black`, `white` etc.).

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
