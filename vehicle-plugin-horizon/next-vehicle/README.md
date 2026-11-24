# Următorul vehicul: Dacia Logan

Modelul ales este `vehicle/models/vehicle/dacialogan_body.json` din arhiva
`vehicle.rar` oferită de utilizator, cu permisiunea declarată pentru modele;
nu este un model generat procedural. Se păstrează creditul existent în copia
aprobată. Parametrii provin din `vehicle/vehicles/dacia_logan.json` din aceeași
arhivă: patru locuri, patru roți, scară caroserie 1.7 și motor large.
Coordonatele sunt în sistemul original al modului, nu poziții Paper validate.

`prepare_dacia.py` copiază cele 230 de elemente, UV, rotații, tinturi și
texturi într-un pack candidat separat; verifică formatul, limitele vanilla și
nu suprascrie resursele existente. Baza necesară este packul Horizon deja
publicat, verificat prin SHA-1. Rezultatul nu este instalat automat.

Mai trebuie: înregistrare ID separat și integrarea fizicii, a celor patru
scaune, roților, volanului și culorilor pe baza codului original MrCrayfish;
teste Paper, verificare în joc și abia apoi livrare. Geometria verificată
structural nu dovedește redarea sau poziția jucătorilor în client.

## Dacia Logan poliție

`prepare_police.py` folosește modelul și configurația distincte de poliție,
cele 268 de elemente și textura/sunetul din arhiva aprobată. Combină resursele
numai cu packul curent identificat prin SHA-1, refuză coliziunile și păstrează
intrările existente; testele automate nu confirmă aspectul în Minecraft. Sunetul
de sirenă este inclus ca resursă; integrarea și limitările sunt descrise mai jos.
Instalarea pe server depinde de verificarea și execuția workflowului de livrare.

### Integrare Paper

ID-ul este `dacia_logan_police`, separat de toate celelalte vehicule. Cele
patru locuri, dimensiunile și pozițiile roților, axele, caroseria și porturile
provin din configurația arhivei; offsetul roților este calculat după formula
modului. Fizica, dimensiunile hitboxului, modelul și poziția volanului sunt
adaptări Paper inițiale, nu valori de performanță documentate pentru Dacia.
Necesită verificare vizuală și de condus în clientul real.

Șoferul poate porni sau opri sirena cu F (în locul claxonului) sau cu
`/vehicle sirena`. F este interceptat fără a muta obiectele între mâini;
Q nu este folosit. Înregistrarea originală se repetă, iar cele două lentile de
pe plafon alternează culorile; sirena se oprește automat când nu mai este șofer.
Acestea sunt adaptări Paper, nu o reproducere demonstrată a efectelor originale.
Marcajele sunt din texturile Horizon, adăugate ca panouri fără schimbarea celor
268 de elemente originale ale caroseriei. Testele de protocol verifică F,
mâinile goale și ocupate, pasagerii și pachetele de oprire a sunetului, dar nu
demonstrează aspectul sau sunetul efectiv în client. Nu se promite iluminare
reală a blocurilor sau lentile emisive pe întuneric.

### Livrare 16 noiembrie 2026

Workflowul `45399405882` a trecut buildul, testele și smoke pe Paper pentru
Dacia și Horizon Off-Roader, a publicat packul și a verificat instalarea pe
Falix. JAR SHA-256 `69074d160c8f7b198a285a7ef2b820c7dd64808a83e36d84a1c1f07cb1473470`,
pack SHA-1 `4357e64281b5889d4c24d3e85faf35010e0d709e`. Backupul dinainte
este pe server cu prefix `mcv-before-horizon-45399405882-` (JAR, șase fișiere
de date plugin și server.properties), verificat; nu este backup de lume și a
fost făcut cât timp serverul era activ. Repornirea cerută automat a fost refuzată
de Falix cu HTTP 403 `verification_required`: este necesar restart manual, iar
procesul curent poate folosi versiunea veche până atunci.

### Actualizare culori și sirenă

Workflowul `45402788222` a trecut testele ambelor vehicule și a verificat backupul
și instalarea pe Falix: JAR SHA-256
`ec7995898e3ee4372a78fe33487ef9d183701be9e8f676210a97e6481148ba00`, pack
SHA-1 `162d4dd9ff52d0980d1eb4adbe9057f024b779c7`. Backup verificat cu prefix
`mcv-before-horizon-45402788222-`; este făcut online și nu include lumea.
Restartul automat a eșuat cu HTTP 403 `verification_required`, deci serverul
necesită restart manual și poate încă rula vechiul JAR. Culorile, poziționarea
marcajelor, efectul de girofar și sunetul trebuie verificate într-un client real.

### Reconstrucție după feedback vizual

Run `45406628530`: eliminate elementele textului original `POLICE`, marcajele
cu text ale versiunii precedente, panourile opace ale geamurilor laterale din
spate și vechea bară; păstrate restul elementelor sursei și forma caroseriei.
Scaunele folosesc textura închisă Horizon Off-Roader, iar modelul primește
marcaje fără text și o nouă bară cu faze alternante. Dacia folosește grupurile
roții sports Horizon la axele ei; când se montează alt tip de roată la mecanic,
roata off-road nativă rămâne disponibilă. Comenzile sirenei sunt neschimbate.

Testele au trecut pentru pack, patru călători, condus, salvare, F și Off-Roader;
nu înlocuiesc verificarea de randare în Minecraft. Falix a verificat backupul
`mcv-before-horizon-45406628530-` (online, fără backup de lume), instalarea JAR
SHA-256 `2943944c0db6bbd6ccf0d38f097f6e0af8721818ec4be21ddbb60221a8b212ec`
și pack SHA-1 `c4b0ccc2ec583a50e2a5f99d3e9a9d6601d66f4f`. Restartul automat a
fost refuzat HTTP 403: serverul trebuie repornit manual. Aspectul geamurilor,
scaunelor, roților și al barei necesită verificare în client după restart.

### Referință pentru noua caroserie

Am consultat fotografii cu Logan II facelift de poliție, de exemplu
https://commons.wikimedia.org/wiki/File:Romanian_Police_Dacia_Logan_II_Facelift_(2017)_1.jpg.
Fotografia este folosită ca referință vizuală, nu ca textură în pack. Adaptarea
își păstrează stilul Minecraft și cerința de a nu avea inscripția POLICE:
față și spate remodelate, grilă și faruri noi, capotă lărgită, patru panouri
de ușă, oglinzi noi și marcaje cu dungi/checker fără text. Structura cabinei și
părți din modelul utilizatorului sunt reutilizate, nu este o scanare fidelă a
modelului real. Pentru această versiune este necesară verificare în client.

Livrarea redesignului `45409075758` a verificat buildul, testele, ambele smoke
Paper și backupul anterior cu prefix `mcv-before-horizon-45409075758-` (online,
fără lume). JAR SHA-256 `2943944c0db6bbd6ccf0d38f097f6e0af8721818ec4be21ddbb60221a8b212ec`,
pack SHA-1 `8bd4d0043b7dde65dc761b87cfc667041acd8ec5`; perechea instalată a
fost verificată. Falix a refuzat repornirea automată cu HTTP 403
`verification_required`; este necesară repornirea manuală. Nu există încă o
validare vizuală reală a noii caroserii sau a alinierii elementelor în client.

### Caroserie nouă și interior

`custom_logan_body.py` înlocuiește toate elementele vechii caroserii Dacia cu
un model nou, desenat în coordonatele rigului existent, folosind texturile
Horizon și resursele deja aprobate. Include două scaune față independente,
banchetă, bord, consolă, schimbător, frână de mână și trei pedale **vizuale**;
acestea nu adaugă controale mecanice. Are deschideri pentru roți și geamuri,
girofar cu fazele sirenei existente și păstrează cele patru poziții de pasageri.
Testele verifică geometric elementele și resursele, dar nu pot confirma poziția
jucătorului sau aspectul în client; verificarea vizuală este obligatorie.

Livrarea caroseriei noi, run `45411366753`: testele structurale, buildul și
smoke pentru Dacia și Horizon Off-Roader au trecut. Backupul anterior a fost
verificat cu prefix `mcv-before-horizon-45411366753-` (online, fără lume).
Perechea instalată pe disc a fost verificată: JAR SHA-256
`2943944c0db6bbd6ccf0d38f097f6e0af8721818ec4be21ddbb60221a8b212ec`, pack
SHA-1 `0a0105a9f19d90d5cb37425265692a333012379b`. Falix a refuzat restartul
automat cu HTTP 403; este necesară repornirea manuală. Caroseria, scaunele,
interiorul și alinierea roților nu au fost verificate vizual în client.

### Reparații de geometrie în urma feedbackului

`repair_logan_body.py` elimină cele patru panouri de ușă duplicate, depărtează
liveria de suprafață, adaugă o podea continuă și înlocuiește panoul de capotă
care intra în bara din față cu secțiuni legate. Cele două scaune față sunt
separate, plasate după stâlpul dintre uși spre fața mașinii și redimensionate
la dimensiunile fizice ale scaunelor Horizon Off-Roader, ținând cont de scara
celor două modele. Pozițiile pasagerilor/condusul nu sunt modificate. Auditul
numeric pentru cuburi fără rotație reduce perechile de fețe coplanare suprapuse
de la 36 la 0; acesta nu dovedește că toate glitch-urile sau golurile au dispărut
în client. Este necesară o nouă verificare în joc.

Livrare reparație: workflow-ul `45415904672` a trecut build-ul și testele pe
servere temporare pentru ambele vehicule. A identificat și inclus `garages.yml`
în backupul verificat `mcv-before-horizon-45415904672-`, fără să îl modifice.
Instalarea JAR și configurației packului a fost verificată (JAR SHA-256
`2943944c0db6bbd6ccf0d38f097f6e0af8721818ec4be21ddbb60221a8b212ec`,
pack SHA-1 `9d73687b1be4272c02c7acd91ed8408e9f3faf02`). Falix a respins
restartul automat cu HTTP 403 `verification_required`; restartul din panoul
Falix și validarea vizuală/audio în client sunt necesare.

### Ajustarea Loganului după feedbackul final

`final_logan_body.py` scurtează doar fața dincolo de marginea pasajului roții,
păstrând axele, anvelopele și contururile pasajelor. Bancheta spate este
continuă și lată, spătarele față pornesc puțin în spatele stâlpului, iar bordul
este avansat spre capotă. Pardoseala, fețele interioare ale ușilor și antena
înclinată invers sunt incluse în toate fazele girofarului. Testele verifică
continuitatea și dimensiunile geometrice, dar nu înlocuiesc un test vizual cu
roțile și jucătorii în client.

Livrarea ajustării: `45418479212` a trecut testele geometrice, build-ul,
testele de protocol ale ambelor vehicule și verificarea că restul packului nu
s-a schimbat. Backupul `mcv-before-horizon-45418479212-` include datele
pluginului și `garages.yml`. Instalarea a fost verificată: JAR SHA-256
`2943944c0db6bbd6ccf0d38f097f6e0af8721818ec4be21ddbb60221a8b212ec`,
pack SHA-1 `566045f084e745bf4b76706435c573763ec07e74`. Restartul automat a
fost respins de Falix (HTTP 403 `verification_required`); este necesar restart
manual și verificare vizuală/audio în client.

### Reparații roți, aripi și față

`polish_logan_body.py` adaugă un perete la capătul compartimentului pedalelor,
leagă partea de sus a pasajelor de aripi și reduce lățimea traversei de sub
caroserie care intra în roți. Roțile Horizon sunt deplasate vizual lateral în
mod simetric (fără modificarea axelor fizice) pentru a lăsa spațiu banchetei;
poziția laterală urmează și unghiul de bracaj. Fața are grilă și detalii noi,
iar pe capotă și aripi sunt accente albastre fără scris. Testele geometrice
verifică spațiul în poziția statică; virajele și aspectul necesită verificare
în client, nu sunt demonstrate de randările schematice sau testele de protocol.

Livrare `45420871057`: build, teste geometrice, teste Paper pentru Dacia și
Off-Roader și verificarea celorlalte resurse au trecut. Backupul verificat este
`mcv-before-horizon-45420871057-`, inclusiv datele garajelor. JAR instalat
SHA-256 `6ddf2f509eebfca58a0686f0378da74b324e78b3b79d8953e3e5978a06ae37a6`,
pack SHA-1 `ba7b73145f5312aac04d4158d2340576da4afb9e`. Restartul automat a
fost respins de Falix cu HTTP 403 `verification_required`: trebuie restartat
manual și verificat efectul în client.

### Reamenajare interior și repoziționare roți

`refit_police_logan.py` readuce roțile la pozițiile vizuale originale ale
rigului, restrânge bancheta și podeaua doar în dreptul pasajelor spate și
adaugă căptușeli de pasaj și traverse dedesubt. Peretele de la pedale folosește
aceeași textură ca podeaua. Volanul are model dedicat cu coloană și păstrează
animația de direcție; grilajul din spatele scaunelor are goluri reale. Geamurile
laterale spate folosesc o textură fumurie cu pixeli transparenți alternanți
(pentru compatibilitate cu randarea vanilla cutout, nu transparență continuă).
Sunt verificate matematic dimensiunile statice, resursele, fazele sirenei și
pozițiile originale, dar roțile în viraj și aspectul real rămân de verificat
în client.

Livrare `45423974565`: testele de geometrie, build-ul și testele de protocol
pentru ambele vehicule au trecut; backupul verificat al pluginului, datelor
(inclusiv garaje) și server.properties are prefixul
`mcv-before-horizon-45423974565-`. Instalate și verificate: JAR SHA-256
`d412e636ee5b51f875fc7cec397dd8f661398acf36aa12ca41040291edd3cd0c`,
pack SHA-1 `0dc8d1a76098d8ab752a34366ab3c91fe1dcb010`. Restartul automat
Falix a fost refuzat HTTP 403 `verification_required`; trebuie restart manual
și verificare vizuală și audio în Minecraft.

### Finisarea interiorului

`finish_police_logan.py` înlocuiește volanul cu unul mai mic și rotunjit și
extinde coloana sa până la bord, scoate geamurile fumurii, uniformizează
podeaua de la pedale și mută grilajul până lângă spătarele din față. Deplasarea
este de 1,37 pixeli model (nu 4), deoarece 4 ar introduce grilajul în scaune;
prinderile ating spătarele. Un raft închide zona din spatele banchetei și
cotierele acoperă pasajele roților, păstrând roțile în pozițiile originale.
Testele sunt geometrice și de protocol, nu verificare vizuală în client.

Livrare `45426294538`: testele geometrice, build-ul, testele de protocol
pentru ambele vehicule și verificarea celorlalte resurse au trecut. Backupul
verificat (inclusiv garaje) are prefixul `mcv-before-horizon-45426294538-`.
JAR instalat SHA-256 `f57d6bece18145136b457e8198fdba1f2d72e8daaf071d7bc9f9ffeaa6100b3e`,
pack SHA-1 `e2df98516df738c740e1160c81ce8dc0cd870963`. Falix a respins
restartul automat HTTP 403 `verification_required`; este necesar restart
manual și o verificare vizuală și audio în client.

### Îmbinările banchetei și barele complete

`detail_police_logan.py` prelungește stâlpii existenți de la geamuri până la
podea pe conturul lor original, duce grilajul de la podea la acoperiș, extinde
capacul portbagajului cu un pixel și unește bancheta cu căptușelile pasajelor
și cotierele. Un perete de închidere acoperă partea dinspre portbagaj. Pentru
roata din stânga, compunerea rotațiilor este corectată: oglindirea se aplică
modelului asamblat, nu pieselor înainte de rotație. Pozițiile axelor rămân
neschimbate. Testele matematice verifică dimensiuni statice și transformări;
aspectul și spațiul la viraj trebuie verificate în client.

Livrare `45430636180`: build, teste geometrice, teste de transformare și teste
Paper pentru Dacia și Off-Roader au trecut. Backup verificat cu prefix
`mcv-before-horizon-45430636180-`, inclusiv datele garajelor. JAR instalat
SHA-256 `524fda2ba813a140622e2e2d23113ba0aec9163736177921c78295c4626f3771`,
pack SHA-1 `b2db5a9cec7d4d81eeaba9d3dcd77c3ca3efa235`. Falix a refuzat
restartul automat HTTP 403 `verification_required`; restart manual și
verificare vizuală/audio în client rămân necesare.

### Închiderea îmbinărilor și podeaua de dedesubt

`complete_police_logan.py` adaugă îmbinările inferioare spre stâlpii laterali
și extensii de spătar peste pasajele din spate. Aripile au elemente de tablă
între conturul în trepte și panoul de sus, cu pasajele roților lăsate deschise.
Dedesubt sunt panouri legate de caroserie și traversa centrală, cu decupaje
pentru roți; piesa izolată din spate care putea părea cârlig a fost eliminată.
Testele verifică modelul și spațiul geometric conservator în repaus/rotire;
nu înlocuiesc verificarea vizuală a virajului și a părții inferioare în joc.

Livrare `45433382850`: testele geometrice, build-ul, testele Paper ale ambelor
vehicule și verificarea celorlalte resurse au trecut. Backup verificat cu prefix
`mcv-before-horizon-45433382850-`, inclusiv garajele. JAR instalat SHA-256
`524fda2ba813a140622e2e2d23113ba0aec9163736177921c78295c4626f3771`,
pack SHA-1 `13521f225f298923a18b6cdc8dc6fd0f9330259b`. Restartul automat a
fost refuzat de Falix cu HTTP 403 `verification_required`: este necesar restart
manual și verificare vizuală în client.

### Roți Horizon complete și căptușeli de pasaj

`restore_police_wheels.py` reconstruiește anvelopa sports Horizon într-un singur
model vanilla per roată. Sunt păstrate toate cele 17 piese sursă; cele două la
67,5° sunt convertite geometric echivalent la -22,5° cu axe schimbate, pentru
ca întregul ansamblu să fie randat într-un singur ItemDisplay. Testele compară
colțurile tuturor pieselor cu geometria Horizon. Roțile nu sunt mutate în afară.
Au fost adăugate căptușeli de pasaj și un volan derivat din modelul Horizon,
cu coloană. Scuturile sunt verificate geometric în repaus; testarea virajelor,
aspectului și audio în client este în continuare necesară.

Livrare `45436491163`: testele geometrice ale tuturor pieselor roții, build-ul,
testele Paper pentru ambele vehicule și verificarea resurselor au trecut.
Backup verificat `mcv-before-horizon-45436491163-`, inclusiv garaje. JAR
instalat SHA-256 `01ea6f68ecea941d1b3af04b21a2e5134e6bb6c1fe5e16183b990778df6446f6`,
pack SHA-1 `9159951f45d8449c9e70f4e9a925f1d537df207b`. Falix a respins
restartul automat HTTP 403 `verification_required`; este necesar restart manual
și verificare vizuală/audio în client.

### Îmbinări și materialul de sub mașină

`seal_police_logan.py` schimbă textura de banchetă de pe placa vizibilă sub
șasiu și de pe fețele inferioare ale tapițeriei. Aliniază căptușelile
pasajelor cu cotierele și spătarele și segmentează piesele care se suprapuneau.
Testele verifică toate cele trei faze, perechile de fețe coplanare pentru
cuburile fără rotație și acoperirea eșantionată a plafonului pasajelor din
spate. Aceste verificări nu garantează lipsa tuturor golurilor în client sau
spațiul în orice unghi de virare; modelul trebuie inspectat și în joc.

Livrare `45439432075`: testele geometrice, build-ul, testele Paper pentru Dacia
și Off-Roader și verificarea celorlalte resurse au trecut. Backup verificat cu
prefix `mcv-before-horizon-45439432075-`, inclusiv garajele. JAR instalat
SHA-256 `01ea6f68ecea941d1b3af04b21a2e5134e6bb6c1fe5e16183b990778df6446f6`,
pack SHA-1 `c8a29468657a7a4b08c47bc657a372280073e924`. Falix a refuzat
restartul automat HTTP 403 `verification_required`; restart manual și
verificare vizuală în Minecraft sunt necesare.

### Închiderea pasajelor după fotografia din joc

`close_logan_wheelwells.py` extinde panourile interioare ale pasajelor până la
capetele deschiderilor și aliniază închiderea de lângă bancheta spate. Toate
fețele lor sunt închise la culoare. Testul eșantionează fiecare față interioară
pentru goluri, inclusiv extremitățile, și verifică cele trei faze de sirenă.
Coordonata longitudinală vizuală a roților a fost corectată în raport cu
rotația de 180° a caroseriei afișate: centrele corespund astfel pasajelor
autorate față/spate, în timp ce axele fizice rămân nemodificate. Testele
matematice și de protocol nu confirmă aspectul sau virarea în client.

Livrare `45442315730`: testele de eșantionare a panourilor, transformări,
build și smoke Paper pentru Dacia și Off-Roader au trecut. Backup verificat cu
prefix `mcv-before-horizon-45442315730-`, inclusiv garajele. JAR instalat
SHA-256 `a2c0d24b67862b72c871d980fb0e20337b4bf3ec23cd2c00dfae7f76020b4852`,
pack SHA-1 `2069088cc44c8c55157ed6baceba8eda16bcd9a0`. Falix a refuzat
restartul automat HTTP 403 `verification_required`; restart manual și verificare
vizuală a roților, inclusiv în viraj, sunt necesare.

### Repoziționare roți și oglinzi

În urma feedbackului, `DaciaHorizonWheels` revine la pozițiile vizuale de axă
anterioare inversării longitudinale. `connect_logan_mirrors.py` folosește panouri
închise la culoare în spatele roților pentru a ascunde interiorul, fără a
muta roțile în afară, cu spațiu suplimentar calculat pentru bracajul față.
Suporturile ating oglinzile laterale și caroseria; oglinda centrală este un
model decorativ, fără reflexie dinamică. Testele matematice și de protocol nu
înlocuiesc verificarea vizuală a roților în viraj și a montajului oglinzilor.

Încercarea `45444972812` a trecut build-ul, testele și publicarea, dar
instalatorul s-a oprit înainte de backup și modificări: Falix raporta serverul
într-o stare de tranziție. Inspecția read-only `45445936653` a raportat starea
`sleeping`. Nu presupune că serverul este oprit în siguranță; pornește-l din
panou și reia instalarea numai după ce starea devine `running` sau `offline`.

### Conturul roților spate și revenirea la pozițiile cerute

`fix_logan_rear_arch.py` pornește de la perechea instalată `45442315730` și
include modificările de oglinzi pregătite, dar neinstalate în `45444972812`.
Roțile vizuale revin la pozițiile vechi. Conturul și infill-ul aripilor spate
sunt recalculate față de centrul roții readuse, iar peretele și placa de sub
spate care intrau în volumul roții sunt retrase; sunt păstrate și panourile
întunecate din spatele roților. Testele verifică îmbinările și o limită
conservatoare statică; rezultatul trebuie inspectat în Minecraft.
