# Horizon Off-Roader — integrare în versiunea aleasă

Baza de lucru este commitul `50583bb8618b8ad0b94e6e3aa5e28ea7dae761e5`,
nu variantele mai noi din alte directoare. Versiunea actuală are deja
`off_roader`, un model diferit cu patru scaune. Nu îl suprascriem: modelul
Horizon va avea ID separat `horizon_off_roader`.

Pachetul existent din `paper-vehicles/transfer/off-roader/` conține modelul
Horizon, texturi, transformări și indicații; testul structural al transferului
verifică toate cele 197 de elemente ale caroseriei. Nu este încă un vehicul
Paper funcțional. În baza aleasă, rendererul construiește item models în
namespace-ul `vehicle` și un model per piesă, deci nu poate folosi direct
pachetul transferat: forma Horizon are nevoie de mai multe grupuri/display-uri
cu transformări pentru rotațiile care nu se pot exprima în modelele vanilla.

Pași necesari înainte de livrare:
1. Extindere pack r39, nu înlocuire; namespace separat, texturi și definiții
   item complete; păstrarea modelelor, culorilor și mențiunilor existente.
2. Rig pentru toate grupurile, cu transformări verificate numeric; roți,
   direcție și componente animate din layoutul sursă. Teste de regresie pentru
   vehiculul deja existent și limite de entități/performanță.
3. Configurație proprie cu punctul șoferului din Horizon, fără a inventa locuri
   sau reutiliza geometria Off Roaderului actual. Fizica, coliziunile și
   sistemele de combustibil trebuie conectate și verificate separat.
4. Compilare, teste și server Paper temporar; backup verificat înainte de
   orice actualizare. Testele automate nu dovedesc randarea, camera sau
   poziționarea în joc. Compatibilitatea packului și modelul cer verificare
   reală în client vanilla.

Nicio schimbare de server sau în pack nu se face prin acest document.

## Progres pack

`tools/merge_horizon_pack.py` creează un pack candidat separat doar din r39 cu
hash verificat, păstrând conținutul fișierelor existente și adăugând namespace-ul
Horizon și licența; refuză coliziunile. Testele sunt în `tests/`, iar workflow-ul
`horizon-pack-integration.yml` verifică pe packul r39 real. Nu publică și nu
instalează packul: rigul vehiculului nu este încă implementat.
