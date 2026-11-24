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
