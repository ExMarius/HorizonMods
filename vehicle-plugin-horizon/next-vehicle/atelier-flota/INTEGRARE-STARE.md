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
  orientarea trebuie validate vizual, iar rampele încă nu sunt animate în joc.
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
