# Horizon Vehicles pentru Paper — Go-Kart experimental

Plugin separat pentru Paper 1.21.4 / Java 21. Comenzile OP sunt
`/hvehicle spawn go_kart`, `/hvehicle remove`, `/hvehicle fuel`, `/hvehicle pack`
și `/hvehicle list` (aliasuri `/vehicle` și `/vehicel` dacă nu sunt ocupate de alt plugin). Click dreapta pentru urcare, WASD pentru condus, spațiu
pentru frână, Shift pentru coborâre. Resource pack-ul Go-Kart este inclus în JAR
și este oferit clienților prin URL-ul public al acestui branch; acceptarea este
necesară pentru a vedea modelul. Vehiculele sunt temporare și sunt eliminate la
oprirea pluginului. Acesta este un prototip, **netestat încă în joc**: scaunul,
modelul, mișcarea, coliziunile și livrarea pack-ului necesită validare. Nu sunt
implementate rețeta, obiectul, salvarea, localizarea sau restul vehiculelor.

Codul pluginului Paper existent a fost copiat separat în
`../third_party/paper_vehicle_reference/` pentru a fi studiat și portat
selectiv. Copia din `src/main/java` este inclusă în build, dar pluginul vechi
nu este activat și nu sunt incluse modelele, sunetele sau resource pack-ul lui. Vezi și `../docs/paper-transfer-plan-ro.md`
pentru licențe și starea fiecărui vehicul. Păstrează GPL și notificările
necesare când se adaptează cod. Modelele generate în `../content/` sunt surse
pentru port; pack-ul experimental Go-Kart este generat în timpul build-ului.

## Build (într-un mediu cu acces la repository-urile Gradle și Paper)

```sh
./gradlew -p paper-vehicles build
```

Necesită Java 21, Python 3 cu Pillow 11.3.0, descărcarea Gradle și a Paper API. Acest mediu nu are Java și
nu poate accesa gazdele Gradle/Paper, deci build-ul și rularea Paper nu au fost
validate aici. Urmează conversia geometriei și a texturilor la un resource pack
vanilla 1.21.4 și integrarea în rig-ul de afișare; JSON-urile Horizon folosesc
unghiuri de rotație neacceptate în mod normal de modelele vanilla, iar autobuzul
este OBJ, deci simpla copiere ar produce resurse invalide sau lipsă. Vehiculele
vor fi portate pe rând, cu teste pentru model, mișcare și scaune multiplayer.

## Build automat pe GitHub

Workflow-ul `.github/workflows/paper-vehicles.yml` instalează Java 21, verifică
catalogul și încearcă să construiască JAR-ul pe GitHub Actions. Dacă reușește,
JAR-ul de dezvoltare este disponibil 14 zile ca artifact al rulării. Este un prototip netestat în joc. Dacă
workflow-ul sau permisiunile repository-ului nu permit rularea, nu există un
build verificat până când eroarea nu este rezolvată.

## Importul codului

Codul Java al pluginului Paper și testul indicatorului de combustibil provin din pluginul Paper al lui ExMarius/MrCrayfish și sunt
incluse în build; componentele de coliziune și specificația Go-Kart sunt folosite de prototip. Entrypoint-ul pluginului vechi nu este activat; nu se încarcă resource pack-ul lui. `LICENSE` conține
textul complet GPLv3; `THIRD-PARTY.md` documentează sursa și excepțiile. Testele rămase și generatorul de pack sunt păstrate ca referință, fără a le
activa și fără resursele originale. Nu rulăm generatorul original nefiltrat:
el include și vehicule/componente cu mențiune ARR și trimite la resurse externe.

## Primul model: City Bus

Modelul și texturile sursă MIT sunt copiate în `asset-src/city_bus/` și
împachetate în JAR la `source-assets/city_bus/`, împreună cu licența. Aceste
surse nu sunt încă un resource pack și nu sunt redate în joc. Formatul OBJ nu este
acceptat direct de un client vanilla Paper 1.21.4; portul necesită o conversie
reală și testare vizuală, nu redenumirea fișierului.

Analiza offline `python3 paper-vehicles/tools/audit_bus_mesh.py` inventariază
geometria originală: corpul conține 379 fețe, iar roata conține 64; acestea nu
pot fi importate ca OBJ în pack-ul vanilla 1.21.4. Cifrele nu dovedesc că toate
fețele se pot converti fără pierderi. Fișierul original de proprietăți pentru
bus (`yellow_bus_frame.json`) descrie șase roți și 13 poziții de pasager, plus
șofer, în coordonatele Automobility. Ele nu sunt încă adaptate la Paper, montate
sau testate și nu garantează că jucătorii încap în aceste locuri.

`CityBusLayout` citește acum automat datele originale din JAR și le validează;
rezultatul este exclusiv în coordonate sursă, încă necalibrat și neconectat
la sistemul de montare. Faptul că datele se citesc nu face scaunele funcționale.

### Conversie experimentală

`tools/compile_city_bus.py` convertește suprafețele OBJ în modele vanilla
plane cu texturi coapte din UV-urile originale, grupate după orientare. Build-ul
include zip-ul experimental și licența MIT în JAR, dar **nu îl trimite
clienților și nu instanțiază modelele**. Sunt 31 grupuri pentru corp și 21
pentru fiecare roată: folosirea lor brută poate fi costisitoare pentru server.
Texturile sunt resample la 48×48 per față, nu o conversie pixel-perfect.
Geometria, UV-urile, transparența, animația și performanța trebuie verificate
în Paper înainte de activare; nu este un produs final sau vehicul condus.

Livrarea opțională prin GitHub Actions este documentată în
`deploy/README.md`: este dezactivată până la o cerere explicită și configurarea
secretelor și a amprentei confirmate de HidenCloud. Nu repornește serverul.

## Go-Kart: prima portare

`tools/compile_go_kart.py` construiește un pack experimental din modelele și
texturile proprii Horizon: caroserie, roți, volan și motor. Cuburile cu unghiuri
neacceptate de Minecraft 1.21.4 sunt separate pe pivoti; datele lor precise
sunt păstrate în `go_kart_parts.json`, fără rotunjirea unghiurilor. Pack-ul e în JAR. Rendererul, scaunul și fizica de bază sunt conectate experimental, dar încă nu au fost validate în joc. Emisia luminii nu este implementată de formatul vanilla folosit.

### Integrare în curs

`GoKartRig` este un renderer experimental pentru grupurile din pack, cu rotații
în jurul pivotului sursă. `GoKartMotion` modelează separat accelerația, frâna,
virarea și consumul. Aceste componente sunt legate experimental de comenzi, scaun,
coliziuni aproximative și livrarea pack-ului, dar nu au fost verificate în joc.

### Preluare din proiectul Paper existent

Prototipul folosește `LandVehicleSpec.GO_KART` din proiectul Paper pentru
poziția scaunului și parametrii fizici, precum și `VehicleCollisionMover` pentru
coliziuni și urcarea treptelor. Pentru modelul Horizon am restaurat aranjarea
anterioară a caroseriei, roților, volanului și motorului, care necesită verificare vizuală;
nu este încă rig-ul sau motorul complet `LandVehicle` al proiectului sursă.
Condusul folosește o adaptare selectivă a formulelor din `LandVehicle`, inclusiv frecare, tracțiune și virare pe osii; boost-ul și unele detalii ale rezervorului rămân neportate. Aceste modificări
nu au fost încă verificate în joc.

### Restart la actualizări

Livrarea scrie un marker SHA-256 după upload, iar watcherul pluginului anunță și
execută `restart` după 5 secunde. Vezi `deploy/README.md` pentru condiția de
primă activare și limitările serverului.

Testul automat pornește un server Paper 1.21.4 separat și un client offline:
verifică spawnul, urcarea, deplasarea orizontală și declanșarea scriptului de
restart. Nu verifică fidelitatea vizuală, multiplayer, terenuri complexe sau
comportamentul serverului real.

### Scaun barcă și pachetul de resurse

Kartul folosește experimental o barcă vanilla pentru poziția de șezut. Un suport
invizibil ocupă primul loc al bărcii, pentru ca A/D să controleze kartul și nu
barca independent; jucătorul stă direct pe celălalt loc. Poziția, aspectul și
caroseria și restul grupurilor modelului sunt pasageri ai suportului invizibil,
formând ierarhia barcă → suport → model; nu mai sunt teleportate ca entități
independente. Jucătorul rămâne pasager direct al bărcii. Testul automat verifică
ierarhia și deplasarea, dar nu dovedește cum se văd modelul și camera într-un
client real. Barca poate fi vizibilă în model. Mâinile cosmetice au fost eliminate. Pachetul este trimis automat doar la intrare, nu
la spawn; `/hvehicle pack` rămâne disponibil la cerere.
