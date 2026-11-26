# Platforma auto — pregătire pentru integrare

**Nu este gata de instalare.** Nu există încă un camion funcțional, comenzi,
încărcare reală sau un release pentru server. În această sesiune nu se deployează
și nu se atinge serverul. `recovery/RecoveryInterlock` și `RecoveryCable` sunt
componente izolate, fără conexiune la runtime, fără efect în joc.

## Auditul mecanicii existente

- `TrailerManager.referencesVehicle` inspectează legături din remorcile
  încărcate în memorie; `hasVehicleChild` este privat. Datele remorcilor din lumi
  indisponibile sunt amânate la pornire (`start`), deci o interogare exclusiv în
  memorie nu demonstrează că nu există o legătură persistentă. Pentru încărcare
  trebuie un index complet și rezultat explicit «necunoscut» când nu poate fi
  stabilit. Nu schimba semantica grapplei sau remorcilor existente.
- `positionLoadedVehicle` și `LandVehicle.placeOnTrailer` fixează instant poziția
  și opresc fizica; nu implementează urcarea pe rampe, detectarea obstacolelor,
  autorizarea și nici o platformă autopropulsată. Nu trebuie reutilizate ca și
  cum ar implementa manevra cerută.
- `LandVehicle.occupied()` și `canDrive()` oferă verificări de pasageri și owner /
  trusted drivers, dar nu sunt suficiente pentru protecțiile terenului, dreptul
  de a muta vehiculul, acord și siguranța căii. Nu deduce permisiuni din ele.
- Vehiculele și remorcile au persistență diferită; ordinea de încărcare, zonele
  indisponibile și chunk-urile inactive trebuie tratate explicit, fără să se
  piardă o mașină, să se dubleze sau să se elibereze într-un loc nesigur.

## Ce este pregătit

- Modelul candidat, exportul separat și constructorul de resource pack care
  verifică hash-ul bazei și coliziunile. `RecoveryTruckPrototype` leagă cabina,
  platforma, volanul, roțile și rampele în poziție pliată de structurile rig-ului
  Paper. **Nu este în catalog** și nu se poate spawna; poziția, scaunele și
  orientarea trebuie validate vizual. Există control vizual pentru ambele rampe
  și cablu în până la două segmente; acestea nu mișcă niciun vehicul și nu au
  comenzi sau verificări de coliziune pentru jucători.
- `RecoveryInterlock`: controlor izolat pentru stările încărcării și validarea
  repetată fail-closed; condițiile sunt furnizate de viitorul adaptor Paper.
  Refuză și starea necunoscută, nu doar o remorcă detectată. Nu salvează date,
  nu impune singur drepturi și nu mișcă vehicule.
- `RecoveryJournal`: jurnal separat, cu checksum și înlocuire atomică, care
  păstrează identitățile manevrelor. După restart cere reconciliere explicită;
  nu este conectat la runtime și nu validează singur existența vehiculelor.
- `RecoveryEnvelope`: calcule conservative pentru spațiul de pe platforma
  plană și alinierea roților pe rampe; nu validează obstacole sau urcarea reală.
  Cu rezervele actuale rămân aproximativ 5,04 × 2,60 blocuri pentru vehicul;
  Dacia demonstrată are aproximativ 4,97 × 2,44 blocuri. Dimensiunile și roțile
  sunt orientative și nu se extrapolează la vehicule necunoscute.
- `RecoveryCable`: calcule locale ale liniei și ghidajului, doar pentru vehicule
  aliniate și platformă plană. Nu verifică obstacole, mașini sau teren; ochiul
  Daciei în browser este orientativ. Testele și randarea nu demonstrează protecție
  sau coliziuni în joc.
- `ROLEPLAY-PLATFORMA.md` conține regulile, gabaritele și scenariile de validare.

## Lucru obligatoriu înainte de candidat și instalare

1. Rig, catalog, comenzi, scaune și cinematica mașinii-platformă. Adaptor real
   pentru axe, poziția rampelor, roți, platformă înclinată și cablu. Trebuie
   comparate în client cu JSON-ul; geamurile și orientarea nu sunt validate.
2. Surse de adevăr pentru proprietate, permisiuni, protecții, obstacole și toate
   legăturile/remorcile, inclusiv cele persistate și neîncărcate. Necunoscut sau
   refuzat = stop; nu începe încărcarea dacă nu se pot verifica.
3. Implementarea efectivă a urcării conduse și a troliului, cu verificarea căii
   înainte și pe fiecare tick; oprire sigură, acordul șoferului, stări și blocări
   atomice pentru doi jucători și interzicerea cuplării în timpul manevrei.
4. Prindere cu chingi, transport și descărcare, persistență atomică și reconciliere
   după restart/chunk unload; fără mutări prin pereți, pierderi sau duplicare.
5. Teste automate complete și smoke pe server Paper temporar cu jucători, obstacole,
   remorci, permisiuni, deconectare/restart, plus validare vizuală în client real.
6. Abia după succes: candidat JAR/pack, compararea hash-urilor, backup verificat,
   apoi confirmare expresă înainte de upload/install; restart manual dacă e necesar.

Nu prezenta verificările componentelor izolate ca dovadă de funcționare în joc.

Build-ul și testele pluginului au trecut în CI pentru commitul `132d420`;
smoke-ul din același workflow testează grapa existentă, nu platforma auto.

Sesiunea de integrare: nu s-a instalat pe server. Jurnalul este o componentă
izolată și trebuie conectat tranzacțional la stările efective din joc înainte
de a putea revendica persistența în caz de restart.

Pe serverul Paper temporar, workflow-ul `45889715106` a creat rig-ul, a
verificat ID-urile pieselor, transformarea ambelor rampe și urcarea unui
jucător pe scaun; prototipul a fost apoi eliminat. Nu a testat condusul,
încărcarea, troliul, persistența platformei sau randarea într-un client real.

Workflow-ul `45890606178` a testat în Paper temporar inclusiv direcția,
lungimea și ascunderea celor două segmente de cablu; calculele verifică
intersecția cu puntea plană și solul. Nu a testat cablul în client, în alte
configurații de teren sau împotriva obiectelor din lume.

Workflow-ul `45891664762` a compilat experimentul de mișcare și a rulat
proba Paper izolată, inclusiv blocarea unor operații concurente. Mișcarea nu
este expusă jucătorilor: protecțiile, traseul real și persistența nu sunt legate.
`RecoveryLoadingPath` adaugă doar o aproximare matematică pentru înălțime și
înclinare, reversibilă pentru descărcare; nu reprezintă o cale verificată de
coliziuni și nu trebuie folosită ca autorizație de deplasare. Lipsesc suprafața
reală, coordonatele vehiculului în joc și verificarea caroseriei și a cablului.

Experimentul de mișcare refuză acum dacă inventarul de remorci de la pornire
nu poate fi verificat complet, inclusiv când o lume sau un tip este indisponibil;
verifică și legăturile active la fiecare pas. Aceasta nu rezolvă încă o problemă
existentă a stocării remorcilor: salvarea obișnuită poate omite înregistrări
amânate, iar după restart nu se mai poate deduce că au existat. Nu activa
recuperarea în producție până când stocarea și reconcilierea nu păstrează și
verifică toate înregistrările, inclusiv cele neîncărcate.

`TrailerSnapshotMerge` este un experiment separat de `TrailerStore`: combină
înregistrările administrate explicit cu cele amânate, respinge fișierele
modificate sau corupte și folosește înlocuire atomică. Nu este încă utilizat în
runtime. Pentru integrare trebuie inventariate toate căile de creare/ștergere,
serializate scrierile și testate restartul, lumile indisponibile și eșecurile
I/O; verificarea versiunii fișierului nu este un lock pentru scriitori externi.

`TrailerSnapshotSession` este un al doilea experiment izolat: gestionează explicit
înregistrările preluate, adăugate și șterse și păstrează înregistrările amânate
între salvări și o repornire simulată. După o eroare de scriere, cere reconciliere
în loc să continue. Nu este integrat în TrailerManager și nu schimbă comportamentul
serverului; funcționarea lui presupune un singur responsabil serializat pentru fișier.

Proba izolată `45901024002` rulează încărcarea/descărcarea Daciei pe 360 de
bifări prin `PrototypeRecoveryRoute`, cu verificare a segmentelor de cablu
față de formele de coliziune ale blocurilor și față de entități, plus refuz în
chunk-uri neîncărcate. Un obstacol în cablu oprește traseul fără reluare
automată; deblocarea la sol necesită sprijin sub centru și patru puncte. Aceste
verificări folosesc geometrie aproximativă, un teren ideal și un adaptor de
permisiuni furnizat de proba de test. Nu verifică volumul măturat de cablu între
bifări, caroseria înclinată, propriile modele sau toate pluginurile de protecție.
Traseul rămâne nepublic: lipsesc chingile și transportul efectiv, persistența și
reconcilierea, sursa reală a permisiunilor, precum și validarea în client.

Domeniu simplificat la cererea utilizatorului: doar troliu, fără ocupanți;
mașina nu trebuie mutată în garaj cât este blocată în recuperare. După
descărcare în siguranță, dacă proprietarul e offline, prototipul încearcă să
trimită doar acea mașină în garajul lui. În proba Paper `45902777546` s-au
verificat refuzul cu jucător pe scaun, apelul de garare la deconectare simulat
în timpul blocării și întoarcerea în garaj după descărcare pentru un proprietar
offline. Nu s-a testat deconectarea reală a doi jucători sau crash/restart în
mijlocul manevrei; salvarea obișnuită a garajului este asincronă și nu asigură
încă o tranzacție de recuperare. Transportul pe platformă în mers și comenzile
reale pentru jucători nu sunt implementate. Nu instala prototipul în producție.

Proba Paper `45903847091` a legat Dacia de platformă după urcare, folosind o
poziție relativă actualizată după vehiculul purtător, precum `vehicle_trailer`.
Un client automat a condus și a virat; proba a verificat că Dacia rămâne la
poziția relativă a platformei, apoi a descărcat-o la noua poziție. Este o probă
izolată, fără validare grafică, chingi persistente, reconectare după restart,
coliziuni sau protecții complete pentru vehiculul transportat. Nu este expusă
jucătorilor și nu trebuie instalată pe server.

Proba Paper `45904692219` folosește doi clienți offline: proprietarul Daciei
se deconectează în timpul urcării, mașina rămâne în lume, operatorul conduce
platforma, apoi o descarcă. Dacia intră în garajul proprietarului, iar după o
oprire și repornire controlate ale Paper apare o singură dată în garaj și nu
în lumea activă. Nu este test de crash/restart în timpul transportului: legătura
încă nu este persistată și restaurată în acea situație.
