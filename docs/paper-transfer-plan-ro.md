# Predare: Horizon Vehicles → plugin Paper

## Stare și decizie de arhivare

Proiectul Horizon/Rust rămâne pe branch-ul `arena/fb5f91ff-horizonmods`; nu îl ștergem și nu înlocuim pachetele sale cu pluginul. Ultimul cod al prototipului înainte de acest document este `4be481b`. Pluginul Paper este o aplicație separată: nu încarcă fișierele `.hnmod` sau codul Rust Horizon. Transferul înseamnă portare/adaptare, nu simpla copiere a modului.

Repo-ul indicat pentru plugin este [ExMarius/MrCrayfishVehicleMod](https://github.com/ExMarius/MrCrayfishVehicleMod/tree/arena%2F2f9f7b9e-mrcrayfishvehiclemod), branch `arena/2f9f7b9e-mrcrayfishvehiclemod`. La revizia `6ff2f1da494e7861d14c6772b2bdbcbc2a70ade0`, `paper-plugin/README.md` descrie Paper 1.21.4, resource pack și mai multe vehicule cu pasageri. Aceste afirmații nu au fost verificate pe un server în această sesiune. Portul nu poate fi rulat direct pe Horizon 26.3; alegerea Paper înseamnă server Paper compatibil și adaptarea clienților/resource pack-ului.

## Vehicule de luat în considerare

- Go-Kart, Off-Roader, Quad Bike și ATV distinct.
- Pursuit Sedan Poliția Română, Ambulance, SMURD și Fire Truck; nu crea un Logan separat.
- Street Coupe, Muscle Car, Supercar, City SUV și Taxi. Aceste modele au fost respinse vizual de utilizator și necesită rework, nu trebuie prezentate ca modele finalizate.
- Autobuzul City Vehicles este doar prototip, neînregistrat și nejucabil; cele șase roți sunt statice, scaunele nu sunt integrate. Utilizatorului i-a plăcut direcția vizuală. Transferă-l doar însoțit de licența MIT și atribuirea upstream; verifică adaptarea la Paper.

Aceste nume sunt lista de lucru, nu o promisiune că modelele curente sau comportamentul sunt gata. Dacă pluginul existent are deja un vehicul cu nume similar, decide explicit dacă este o variantă separată sau înlocuire; nu îl suprascrie accidental.

## Proveniență și drepturi

- `LICENSE` declară codul și resursele create pentru acest proiect ca GPL-3.0-or-later, cu excepțiile din `third_party/`. Păstrează licența și notificările aplicabile când copiezi sau adaptezi; verifică proveniența fiecărui asset înainte de distribuire.
- Autobuz: FoundationGames City Vehicles, MIT, sursă și licență în `third_party/city_vehicles/`. Este permisă reutilizarea cu păstrarea notificării MIT; nu este un model original al acestui repo.
- Supercar: Quaternius, CC0 conform `third_party/quaternius/README.md`; utilizatorul a respins aspectul neminecraft. Nu îl confunda cu un model al proiectului.
- MrCrayfish: fișierele Mini Bus originale au credit „All Rights Reserved”, deși repo-ul conține licență GPL pentru mod. Drepturile asupra asseturilor sunt neclare; nu le copia/distribui fără clarificare. Pluginul existent folosește, conform README-ului său, modele originale: simpla adăugare a vehiculelor proprii nu elimină această problemă. Licența codului și drepturile pentru modele, texturi și sunete trebuie verificate separat.
- Chiar și resursele originale ale proiectului au drepturi de autor; obiectivul realist este folosirea resurselor pentru care avem drepturi clare și respectarea licențelor, nu „fără copyright”. Un plugin nou nu garantează automat acest lucru.

## Plan după alegerea utilizatorului

1. Alege explicit între extinderea pluginului existent (păstrează și mașinile vechi) sau un plugin nou cu numai vehiculele noastre/licențiate clar. Nu șterge sau modifica proiectul existent fără acord.
2. Auditează licențele pentru cod, modele, texturi și sunete, inclusiv dependențe și output-ul resource pack-ului. Dacă se pornește de la pluginul existent, scoaterea modelelor nu transformă automat codul într-un proiect independent de licența sa.
3. Portează și testează **câte un vehicul**, pornind cu autobuzul dacă utilizatorul confirmă, fără a pretinde că modelele actuale sunt terminate. Exportul din Horizon și folosirea OBJ/JSON necesită un flux compatibil cu Paper/resource pack; păstrează UV, materiale, scaune și transformări corecte.
4. Pentru fiecare: model îngrijit și interior, roți fără goluri, luminile, fizică/rezervor/treaptă, toate scaunele ocupabile multiplayer, item/rețetă/traduceri și teste. Ambulanțele au nevoie de targă funcțională cu player culcat și legat vizibil; pompierii rămân un vehicul distinct cu echipamente decorative. Păstrează comanda de eliminare și evită coliziunile de nume cu pluginul.
5. Testează build, conectarea a doi clienți, sincronizarea scaunelor, ieșirea/intrarea, deconectarea, coliziunile, treapta de un bloc, persistența și aspectul în joc. Distinge testele automate de testele efective pe server.
