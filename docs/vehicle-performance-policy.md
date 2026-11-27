# Politică de performanță pentru vehicule

Acest document este un ghid pentru vehiculele viitoare, nu o certificare de capacitate. Performanța și comportamentul trebuie observate pe serverul real; nu există încă măsurători de sarcină pentru un server mare.

## Reguli pentru jucători
- Hibernarea este diferită de garaj: vehiculul rămâne asociat aceleiași poziții/identități și se reactivează la apropiere. Dacă proprietarul este online, hibernarea singură nu trebuie să pornească gararea offline. Regula separată de auto-garare în parcările marcate rămâne în vigoare.
- Un vehicul în folosință nu dispare sub ocupanți; trustul nu transferă proprietatea. Cronometrul offline și excepțiile de tractare/restart sunt definite în `vehicle-garage-recovery-policy.md`.
- Nu se încarcă chunk-uri doar pentru a muta în garaj un vehicul hibernat. Legăturile cu remorci, cricul, starea necunoscută și obiectele deschise se tratează conservator; nu se rup pentru optimizare.

## Implementat în managerul comun
- Vehiculele inactive, depărtate de jucători și fără legături de remorcă pot hiberna; identitatea și starea se salvează în colecția de vehicule în așteptare. Blocările recovery împiedică hibernarea. Reactivarea rămâne legată de apropierea jucătorilor și încărcarea chunk-ului.
- Temporizatoarele offline folosesc o singură verificare comună pe secundă, cu o coadă ordonată după termen: nu există un task Bukkit per vehicul și nu se parcurg toate termenele neexpirate la fiecare verificare. Indicele pe proprietar limitează căutarea la reconectare.
- La fiecare verificare periodică se procesează cel mult 4 termene expirate sau reîncercări, ca să nu se golească mii de cronometre într-un singur tick. În aglomerație gararea poate avea loc **după** cele 5 minute, niciodată intenționat înainte. Reconectarea verifică separat termenele acelui proprietar, inclusiv după pauza serverului gol.
- Pentru vehicule active, modificările din aceeași verificare periodică declanșează cel mult o salvare comună. Pentru cele hibernate se păstrează salvarea sincronă cu rollback înainte de expunerea în garaj; nu o înlocuiți cu o salvare în lot fără a proiecta atomicitatea și recuperarea la eroare.
- Persistența obișnuită coalescențează salvările asincrone; tranzitul recovery folosește în continuare propriile verificări și snapshot-uri. Nu se promite siguranță absolută la crash: ultimul snapshot poate fi vechi, iar scrierea existentă nu face fsync.

## Pentru modele noi și modificări viitoare
- Refolosiți `LandVehicle`/`VehicleManager`, inclusiv hibernarea și timerul comun; evitați task-uri, scanări globale și chunk tickets separate pentru fiecare model.
- Nu rulați fizică, scanări de coliziune, animații sau actualizări de display dacă vehiculul este efectiv inactiv; nu opriți însă verificările care asigură ocupanții, încărcătura și tranzițiile în siguranță. Nu presupuneți că orice vehicul poate fi hibernat în timpul unei manevre.
- Păstrați salvarea compatibilă cu datele existente; nu pierdeți inventar, owner, trust, combustibil sau conexiuni. Un vehicul recuperat trebuie să păstreze același UUID.
- Măsurați înainte de alte optimizări: MSPT/TPS, numărul vehiculelor active/hibernate, entități display, chunk tickets, durata colectării/scrierii snapshot-urilor și coada de expirări. Evitați promisiuni de capacitate fără măsurători; limitarea la 4 pe secundă poate crea cozi lungi.
- Identificări pentru lucru ulterior: indexarea spațială în locul scanărilor globale de apropiere, inventarierea costului remorcilor și platformelor, salvarea atomică în lot pentru vehicule hibernate și limite configurabile bazate pe date. Acestea nu sunt implementate aici.
