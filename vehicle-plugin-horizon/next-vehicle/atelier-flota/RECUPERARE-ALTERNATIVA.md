# Soluție propusă: rezervare durabilă și garare reluabilă

Aceasta este o propunere, **nu o funcționalitate activă**. Nu garantează încă
siguranța platformei și nu trebuie instalată pe server ca mecanică live.

## Înainte de prima mișcare

- Se verifică proprietarii reali ai ambelor vehicule; fără proprietar valid,
  nu începe operația. Nu se atribuie vehiculele operatorului.
- Se blochează ambele ID-uri împotriva recuperării din garaj, vânzării,
  ridicării, cuplării, hibernării și oricărei alte modificări concurente.
- Un singur writer serializat golește salvările mai vechi și persistă durabil
  un snapshot complet al ambelor vehicule, inclusiv inventar, proprietari și
  stare relevantă. Apoi persistă jurnalul perechii; doar după confirmarea
  ambelor scrieri se permite mișcarea. Dacă o scriere eșuează, nu se pornește.
- Persistența trebuie să folosească înlocuire atomică și sincronizarea fișierelor
  și directoarelor pe platforme care le suportă. Eșecul sau suportul necunoscut
  închide mecanica. Scrierea sincronă de pe threadul principal poate provoca
  lag; o alternativă este pregătirea asincronă cu vehiculele blocate și aplicarea
  rezultatului pe threadul Paper, fără a lăsa un writer vechi să suprascrie.

## Deconectare și evacuare

- Oprire imediată, păstrarea rezervării și înregistrarea intenției de garare.
  Nu se așteaptă reconectarea proprietarului mașinii tractate.
- Șoferul și orice alt ocupant se evacuează doar într-un loc verificat ca sigur,
  în chunk încărcat, cu teleportarea confirmată. Dacă nu există loc sau
  teleportarea este refuzată, vehiculele rămân oprite și blocate, iar evacuarea
  se reîncearcă; nu se șterge vehiculul cu jucători atașați. Este necesar un
  mecanism verificat pentru situația în care șoferul se deconectează între timp.
- După evacuare, snapshotul este actualizat atomic cu ambele vehicule în
  garajele proprietarilor respectivi. Jurnalul se șterge doar după confirmarea
  durabilă a snapshotului și eliminarea sigură a entităților. Orice eșec lasă
  operația blocată și reluabilă; nu promite garare instantanee când nu există
  loc de evacuare sigur.

## Restart și întrerupere

- Înainte de încărcarea vehiculelor sau acceptarea comenzilor, se citesc
  jurnalul și snapshotul. Fiecare pereche se mută idempotent în garajele sale;
  intrări lipsă, duplicate, proprietari invalizi sau date corupte provoacă
  oprire închisă și intervenție administrativă, nu crearea unui vehicul nou.
- Curățarea entităților vechi trebuie să includă chunkuri/lumi încărcate mai
  târziu, fără a șterge o entitate nouă legitimă. Jurnalul nu poate fi șters
  până când această problemă și cazul jucătorilor salvați călare nu sunt
  rezolvate. Trebuie evaluată și ordinea salvărilor Minecraft față de jurnal.
- `RecoveryTestStartup` și `RecoveryGarageFallback` demonstrează doar
  reconcilierea unui snapshot pregătit offline. Testele acoperă rejucarea după
  înlocuirea snapshotului, eroare la o pereche ulterioară și jurnal corupt.
  Nu există încă un singur writer live, nici dovadă pentru crash în fiecare
  fereastră de scriere, lumi amânate, evacuare sau salvarea jucătorilor.

## Validare necesară

Injectare de erori înainte/după fiecare scriere și sincronizare, restart repetat,
întrerupere în toate fazele, scrieri concurente, server fără spațiu pe disc,
chunk/lume indisponibilă, mai mulți ocupanți, teleportare refuzată, reconectare,
inventare și proprietari distincți. Testare apoi pe Paper și în client real.
