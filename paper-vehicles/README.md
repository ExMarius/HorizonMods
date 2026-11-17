# Horizon Vehicles pentru Paper — început, nu este gata de joc

Plugin separat pentru **Paper 1.21.4 / Java 21**. Acest director nu înlocuiește
modul Horizon. `/hvehicle list` enumeră vehiculele planificate, nu vehicule
jucabile. Nu există spawn, condus, scaune funcționale, resource pack activ sau rețete în acest
checkpoint. Nu instala pluginul vechi alături cu intenția că acest proiect i-a
înlocuit resursele sau funcțiile.

Codul pluginului Paper existent a fost copiat separat în
`../third_party/paper_vehicle_reference/` pentru a fi studiat și portat
selectiv. Copia din `src/main/java` este inclusă în build, dar pluginul vechi
nu este activat și nu sunt incluse modelele, sunetele sau resource pack-ul lui. Vezi și `../docs/paper-transfer-plan-ro.md`
pentru licențe și starea fiecărui vehicul. Păstrează GPL și notificările
necesare când se adaptează cod. Modelele generate în `../content/` sunt surse
pentru port, nu sunt încă un resource pack valid pentru Paper.

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
JAR-ul de dezvoltare este disponibil 14 zile ca artifact al rulării. Este doar
scheletul descris mai sus, **nu un plugin cu vehicule funcționale**. Dacă
workflow-ul sau permisiunile repository-ului nu permit rularea, nu există un
build verificat până când eroarea nu este rezolvată.

## Importul codului

Codul Java al pluginului Paper și testul indicatorului de combustibil provin din pluginul Paper al lui ExMarius/MrCrayfish și sunt
incluse în build, dar nu sunt încă legate de un vehicul. Entrypoint-ul pluginului vechi nu este activat; nu se încarcă resource pack-ul lui. `LICENSE` conține
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
