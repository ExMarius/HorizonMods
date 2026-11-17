# Horizon Vehicles pentru Paper — început, nu este gata de joc

Plugin separat pentru **Paper 1.21.4 / Java 21**. Acest director nu înlocuiește
modul Horizon. `/hvehicle list` enumeră vehiculele planificate, nu vehicule
jucabile. Nu există spawn, condus, scaune, resource pack sau rețete în acest
checkpoint. Nu instala pluginul vechi alături cu intenția că acest proiect i-a
înlocuit resursele sau funcțiile.

Codul pluginului Paper existent a fost copiat separat în
`../third_party/paper_vehicle_reference/` pentru a fi studiat și portat
selectiv. Nu este compilat în pluginul nou și nici nu sunt incluse modelele,
sunetele sau resource pack-ul lui. Vezi și `../docs/paper-transfer-plan-ro.md`
pentru licențe și starea fiecărui vehicul. Păstrează GPL și notificările
necesare când se adaptează cod. Modelele generate în `../content/` sunt surse
pentru port, nu sunt încă un resource pack valid pentru Paper.

## Build (într-un mediu cu acces la repository-urile Gradle și Paper)

```sh
./gradlew -p paper-vehicles build
```

Necesită Java 21, descărcarea Gradle și a Paper API. Acest mediu nu are Java și
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
