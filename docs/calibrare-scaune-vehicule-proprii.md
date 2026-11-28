# Calibrarea scaunelor vehiculelor proprii — audit inițial

Situația după înlocuirea calului cu porcul: pozițiile pentru cele șase modele de mai jos au fost recalculate din geometria pernelor, dar nu au fost calibrate vizual. Nu se consideră confirmat că poziția corpului jucătorului coincide cu suprafața pernei. Paper, clientul și modelul pot introduce offseturi diferite; măsurarea trebuie făcută în Minecraft. Nu modifica simultan modelul și poziția scaunului: păstrează reperul vizual fix.

În `LandVehicleRig`, `seatOffset` adaugă `RIDER_HEIGHT_CORRECTION` (0,25 blocuri) la coordonata din `Seat.sourceOffset`. Se aplică apoi transformarea caroseriei și se scade `0,7 × scara porcului` din înălțimea ancorei. Ancora șoferului este display-ul caroseriei, iar poziția desenată a modelului este compensată relativ la ea; ancorele celorlalte locuri sunt display-uri separate. Prin urmare, corecțiile trebuie aplicate coordonatelor locurilor, fără a modifica această compensare a desenării sau originea fizică a vehiculului. Aceste coordonate sunt repere de montare, nu neapărat coordonatele șezutului jucătorului.

| Vehicul | Locuri existente și repere | Particularități de verificat |
|---|---|---|
| Horizon Go Kart | 1 șofer; `LandVehicleSpec.HORIZON_GO_KART`, coordonate adaptate modelului | Proba la scara 0,0625 inspirată de proiectul clasic nu a fost încă confirmată vizual; compară șezutul cu perna și mâinile cu volanul. |
| Horizon Off Roader | 1 șofer + 3 pasageri; `HORIZON_OFF_ROADER` | Scaunele față și bancheta spate au repere diferite; verifică fiecare rând și lateralele independent. |
| UTB 650 | 1 șofer + 2 pasageri; `UTB_650` | Modelul `next-vehicle/utb/assets/utb_650_body.json` are perne numite `seat cushion` și `rear bench cushion`. Șoferul avea deja o corecție de înălțime față de pernă pentru cal. Porcul folosește scara 0,25, nu scara implicită. Verifică separat banca din spate. |
| Platformă recovery | 1 șofer + 1 pasager; `RecoveryTruckSpec.create()` | Modelul este la scară 4 și rotit 180°; locurile au yaw 180°. Porcul are scara 1, deci ancora este coborâtă cu 0,7 blocuri. Nu presupune că această compensație echivalează cu cea a calului. Verifică și coborârea în spațiu liber, apoi lângă obstacole. |
| Dacia Logan Poliție | 1 șofer + 3 pasageri; `DACIA_LOGAN_POLICE` | Modelul are altă scară și transformare; verifică pernele față și bancheta spate, precum și partea volanului. |
| Horizon Coupe Sport (`bmw_m6`) | 1 șofer + 3 pasageri; `BMW_M6` | Modelul din `next-vehicle/horizon-coupe/build_model.py` definește explicit perne separate față și spate. Verifică fiecare rând și garda la plafon. |

## Procedură de calibrare în joc

1. Repornește după instalare și așază vehiculul pe teren plan, departe de blocuri. Fotografiază fiecare loc din lateral și din spate, în F5; ideal, un al doilea jucător observă și poziția din exterior.
2. Notează separat eroarea verticală, laterală și longitudinală față de pernă, nu față de sol. Verifică orientarea în repaus și în viraj, fără a considera că porcul controlează automat camera.
3. Schimbă numai locul afectat în spec, păstrând numărul locurilor și yaw-ul. Repetă pentru fiecare rând și verifică să nu intersecteze volanul, bordul sau plafonul.
4. Testează urcarea și coborârea, inclusiv pasageri; protecția de demontare cu mărirea scalei este experimentală și nu garantează siguranța tuturor căilor. Dacă apar blocări sau desincronizări, oprește testul.

## Prima poziționare din geometrie

Feedback în joc: scăderea suplimentară de 0,75 blocuri din prima încercare a pus personajul în podea; presupunerea privind poziția șoldului era greșită și a fost eliminată. După încercarea la suprafața pernei, utilizatorul a cerut puțin mai jos. S-a coborât reperul cu 0,15 blocuri față de versiunea anterioară, pe toate cele șase modele; în plus se scade 0,25, valoarea adăugată ulterior de `seatOffset`. Corecția 0,7 × scala porcului rămâne în rig, conform referinței clasice. Aceasta nu dovedește poziția finală a jucătorului: atașamentul pasagerului, animația și randarea clientului trebuie confirmate în joc.

- Platformă: cuburile 140 și 149, vârf y=12,26, centre (5,52/10,48; 4,8), cu origine 8 și 4 pixeli/bloc: suprafața este la y=1,065; `sourceOffset.y=0,665`.
- UTB: perna șoferului y=20,8 și bancheta y=19,2 pixeli după corecția de scară 2; `seat()` primește y=14,4 și respectiv 12,8 pixeli, după scăderea celor 4 pixeli și încă 2,4 pixeli (0,15 blocuri).
- Coupe: vârful pernelor y=12,3, centre x=5/11, z=4,2/-1,85 în modelul la scară 2; suprafața y=0,5375, `sourceOffset.y=0,1375`.
- Logan: pernele din modelul editat de utilizator au vârf y=2,85 față și 3,7 spate; transformarea este la scară 1,7 și `bodyOrigin.y=1,12625`. Centrele pe axa longitudinală sunt 7,725 și -1,2 pixeli. Rezultă înălțimile de suprafață 0,5790625/0,669375 și `sourceOffset.y=0,1790625/0,269375`.
- Horizon Go Kart: perna are centrul x=8, z=5,9 și vârful y=3,3, transformată cu centrul caroseriei y=0,57 și scara (1,18; 1,14; 1,18).
- Horizon Off Roader: pernele față au centrul x=12,825/3,175, z=5,6 și vârf y=6,7; bancheta are centrul z=-6,55 și vârful y=8,8. Se folosesc centrul caroseriei y=0,69 și scara (1,42; 1,38; 1,42).

Niciuna dintre pozițiile recalculate nu a fost validată în joc. Modul Forge 1.21.4 pentru corp/cameră/brațe este un proiect separat și încă nu este implementat.
