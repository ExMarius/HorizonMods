# Platformă auto — specificație roleplay pentru integrare

Prioritatea este platforma; atelierul mobil nu intră în integrarea curentă.
Acesta este un plan, nu o funcționalitate deja disponibilă în plugin.

## Scenariu de joc

1. Operatorul parchează platforma stabil, lângă vehicul, cu spatele și rampele
   aliniate spre acesta. Nu poate pleca în timpul manevrei. Verifică să fie loc
   pentru rampe și zona de lucru, apoi le deschide.
2. Operatorul selectează vehiculul din apropiere, cu permisiunile și acordul
   necesare. Dacă are remorcă **sau orice utilaj cuplat**, încărcarea se refuză
   până la decuplare. Se refuză și un vehicul deja transportat, prins de un alt
   sistem, prea mare, cu traseul blocat sau într-o zonă unde nu e permisă acțiunea.
3. **Urcare condusă:** un șofer urcă lent pe rampe, iar operatorul nu mută
   automat mașina. **Troliu:** operatorul prinde cablul de un punct de remorcare
   valid și controlează tragerea lentă; pentru siguranță, mișcarea automată se
   face doar cu vehiculul neocupat. Nu tragem prin blocuri, jucători sau alte
   vehicule. Absența permisiunii nu se ocolește prin troliu.
4. Când vehiculul este centrat și încape complet pe platformă, operatorul
   detașează cablul, îl asigură cu chingi și ridică rampele. Numai atunci se
   permite deplasarea platformei. În previzualizare chingile nu sunt implementate.
5. La destinație: oprește, deschide rampele, scoate chingile și descarcă în
   spațiul liber, cu șoferul sau cu un mecanism controlat; nu eliberează
   vehiculul în aer sau în interiorul unui obstacol.

## Reguli și calcule de implementat pe server

- Măsoară fiecare vehicul eligibil din geometria/coliziunile sale reale, cu
  orientare, roți, ampatament, gardă la sol și toleranțe. Nu presupune că toate
  vehiculele au dimensiunile Daciei. Platforma concept are 5,50 × 2,90 blocuri;
  asta nu înseamnă că toate vehiculele care încap în dreptunghi pot urca: trebuie
  probate și rampele, gabaritul, înălțimea, terenul și traiectoria completă.
- Detectează orice remorcă/utilaj atât în starea de cuplare a vehiculului, cât și
  în legăturile persistate. Nu permite cuplarea în timpul încărcării sau cât timp
  vehiculul este ancorat; verifică din nou la fiecare tranziție și întrerupe
  sigur la pierderea condițiilor. Nu modifica alte sisteme de remorcare.
- Troliul are puncte valide la tambur, ghidaj și vehicul; traseul vizual urmărește
  ghidajele, nu traversează platforma sau caroseria. În joc sunt necesare teste
  reale de obstacole pe traseul cablului și al vehiculului, nu doar animație.
  Dacă o geometrie sau o permisiune nu poate fi verificată, manevra se refuză.
- Limitele de viteză, distanță, pantă, capacitate și sarcină se stabilesc din
  testele vehiculelor existente și se fac configurabile; nu inventăm greutăți
  sau forțe fizice. Nu simulăm o frânghie elastică ori un troliu fizic real.
- Cuplarea, chingile și transportul trebuie să supraviețuiască descărcării
  chunk-urilor și restartului fără duplicare sau pierdere. Dacă ținta/operatorul
  dispare sau apare un obstacol, oprește, păstrează legătura într-o stare sigură
  și oferă o metodă de recuperare. Fără teleportare prin obstacole.
- Protecțiile de teren, permisiunile, proprietatea, pasagerii și vehiculele
  celorlalți jucători necesită validare în serverul real. Nu considera protecțiile
  compatibile până nu sunt testate efectiv.

## De validat înainte de instalare

Teste pe server Paper temporar: ambele moduri, refuz cu remorci/utilaje,
încărcare pe teren denivelat, obiecte/blocuri în cale, doi jucători simultan,
permisiuni, spațiu insuficient, deconectare, chunk unload, restart, resetare și
transport. Test vizual pe client pentru geamuri, roți, rampe și cablu. Instalarea
necesită separat un build verificat, backup și confirmarea utilizatorului.
