# Audit: evacuare, rejucare și entități (prototip)

Niciunul dintre cele trei puncte nu este complet integrat în gameplay. Nu
instala platforma în producție pe baza acestor probe.

## Evacuare

`PrototypeRecoveryMotion.findTestExit` verifică doar chunkuri încărcate,
podea solidă cu coliziune completă, două blocuri de aer la picioare și cap,
unele podele periculoase, limita lumii și entitățile din locul ales. Proba
Paper cu șofer verifică dezmontarea și aceste condiții de bază pe teren plat.
Aceasta nu dovedește că toate formele de coliziune sau pericolele sunt
tratate, nici că teleportarea anulată și mai mulți pasageri sunt sigure.

Lipsă critică: `evacuateTestDrive` îngheață platforma înainte de căutare;
în caz de eșec, `parkBothOnOwnerQuitForTest` trece în `STOPPED`. Nu există
retry înregistrat, notificare de așteptare sau interdicții live pentru
inventar/comenzi; un eșec după evacuarea parțială poate lăsa ocupanți în
stări diferite. Trebuie proiectată o stare de garare în așteptare, cu retry
sigur la fiecare pas, gestionarea deconectării/reconectării și testarea
comenzilor/inventarelor fără blocarea inutilă a jucătorilor deja evacuați.

## Jurnal

`RecoveryTestStartup` este exclusiv test și folosește un jurnal pregătit de
fixture. `RecoveryGarageFallback` verifică UUID-ul în snapshot: dacă fiecare
vehicul este deja exclusiv în garaj, rejucarea nu adaugă altul; dacă lipsește,
are proprietar invalid sau apare în ambele locuri, eșuează închis. Snapshotul
este scris atomic și sincronizat înainte de golirea jurnalului. Testele unitare
simulează reluarea după înlocuirea snapshotului, inclusiv o eroare la o a doua
pereche. Aceasta nu este o probă de double-SIGKILL la fiecare etapă, nici o
tranzacție live. Nu există un marcaj `COMPLETED` pe intrare: experimentul
șterge jurnalul integral după reconcilierea tuturor intrărilor. În producție
este necesară serializarea tuturor writerilor și împiedicarea oricărui snapshot
mai vechi de a suprascrie gararea, plus teste de cădere la fiecare frontieră.

## Entități și lumi amânate

Rigul obișnuit folosește tagul `mcv_<vehicle UUID>` și entități nepersistente;
UUID-ul vehiculului logic diferă de UUID-urile multiplelor entități din rig.
`VehicleChunkListener` face o curățare generică la `ChunkLoadEvent` folosind
acest tag și `hasVehicleId` (vehicule active sau așteptând lumea). Nu există
încă registru durabil de tombstone pentru recuperare și nici probă pentru
`EntitiesLoadEvent`, entități vechi persistente, lumi încărcate târziu sau
recuperarea ulterioară a aceluiași vehicul din garaj. O listă doar cu UUID-uri
de vehicul nu identifică direct entitățile Minecraft; o listă doar cu UUID-uri
de entități trebuie să includă *toate* piesele, să fie durabilă și să nu
șteargă un rig nou legitim. Pasagerii nu trebuie șterși. Persistența și
momentul colectării acelor identificatori trebuie demonstrate înaintea
ștergerii jurnalului. `RecoveryEntityTombstones` definește acum un format
experimental determinist, cu UUID-uri de entitate, limită de 100.000 de intrări
și checksum. Nu este încă un registru live sau listener. Nici ștergerea la
`EntitiesLoadEvent` nu dovedește singură că regiunea a fost salvată: un crash
între `entity.remove()` și salvarea lumii poate readuce entitatea. Prin urmare
nu eliminăm tombstone-ul la simpla primire a evenimentului și nici după un TTL;
este necesară dovada durabilă a salvării corecte a lumii sau păstrarea lui.

Un breadcrumb pentru evacuare este doar un candidat, nu o garanție: blocurile,
entitățile, lumea și chunk-ul se pot schimba între capturare și teleportare.
Trebuie reverificat în momentul utilizării, inclusiv teleportarea și pasagerii;
în lipsa unui loc sigur, rezervarea rămâne activă.

`RecoverySerializedWriter` este un experiment separat, nu writer-ul folosit de
`VehicleManager`. Salvarea curentă a garajului are încă o cale sincronă
`saveNow()` separată de coada asincronă; pentru o tranzacție nouă nu se poate
presupune că ordinea celor două este garantată. Viitoarea integrare trebuie să
centralizeze *toți* writerii relevanți, iar confirmările asincrone să revină pe
threadul principal înainte de a modifica starea Paper.

## Rust și Paper

Platforma experimentală și jurnalul descrise aici sunt cod Java în
`vehicle-plugin-horizon/paper-plugin`, rulat de Paper. Go-Kartul Rust din
`mixins/gokart_native` se conectează la API-ul nativ Horizon prin hook-uri;
este un runtime separat. Nu există în mecanica de recuperare verificată o
integrare Rust–Paper prin JNI/FFI sau protocol dedicat de rețea. Conceptul de
multi-proces nu trebuie presupus pentru această implementare. Orice viitoare
integrare ar necesita definirea proprietarului datelor, protocolului și
blocării între procese.
