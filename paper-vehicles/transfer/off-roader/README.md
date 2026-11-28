# Off-Roader Horizon → plugin Paper: pachet de transfer

Acesta este **Off-Roaderul existent din HorizonMods**, nu modelul Off Roader
original MrCrayfish care există deja în pluginul tău. Nu înlocui automat
`off_roader`: adaugă-l separat, de exemplu `horizon_off_roader`, sau cere
confirmarea utilizatorului înainte de înlocuire. Pachetul este o bază de
integrare, **nu un vehicul Paper gata de jucat**.

## Conținut

* `source/models/` și `source/textures/`: modelele și texturile originale
  Horizon necesare; `source/runtime-layout.json` conține pozițiile extrase
  din implementarea Horizon. Sursele complete: HorizonMods commit
  `1ff4d573386ee3cde97503713cdb0047055b6fe6`,
  `content/assets/gokart/models/block/`, `mixins/gokart_native/runtime.rs`
  și `mixins/gokart_native/glue.rs`.
* `paper-resource-pack.zip`: pack **experimental pentru 1.21.4** (format 46),
  spațiu de nume `horizonvehicles`. Descriptorul `go_kart_parts.json` din pack
  conține cele patru modele împărțite în grupuri și rotațiile lor. Numele
  descriptorului este moștenit din convertor, nu înseamnă că modelul este kart.
* `LICENSE.txt`: GPL-3.0-or-later și nota de proveniență a acestui proiect.

## Pentru agentul care integrează

1. Nu suprascrie fișierele `vehicle:off_roader_body`, modelele, valorile sau
   ID-ul Off Roaderului existent. Integrează noul namespace și părțile în packul
   existent (inclusiv `items/`), fără să îl înlocuiești cu acest zip; păstrează
   `pack.mcmeta` al packului țintă. Ia toate texturile referite din pack.
2. `off_roader_body` are 197 de cuboizi; formele cu rotații nepermise de
   vanilla sunt separate după axă/unghi/pivot. Trebuie câte un ItemDisplay per
   grup, nu doar primul grup. Rotațiile legale rămân în model. Nu rotunji
   unghiurile la 22.5° și nu aplica transformarea grupului de două ori.
3. Pentru un ItemDisplay cu transform `NONE`, cu geometria centrată la (8,8,8),
   fie `p=(origin-[8,8,8])/16`, `R` rotația grupului, `S` scala părții și
   `O` poziția centrului modelului. Transformul local pe punctul modelului
   centrat `q` este `O + S * (p + R*(q-p))`. Echivalent: translație
   `O + S*(p-R*p)`, matrice liniară `S*R`. Ordinea este importantă la scala
   neuniformă: în JOML/Paper, o descompunere posibilă este
   `leftRotation=identitate`, `scale=S`, `rightRotation=R`. Compune apoi
   rotațiile de vehicul, viraj și rulare în ordinea sursei. Verifică numeric
   matricea completă și convențiile sistemului tău, nu copia semnele orbește.
4. Conform `glue.rs`, corpul Horizon are origine jos la nivelul vehiculului:
   pentru ItemDisplay centrat, `O=(0, 1.38/2, 0)`, `S=(1.42,1.38,1.42)`.
   Roțile, volanul și rezerva au pivotul la centrul modelului și datele din
   `source/runtime-layout.json`; +Z este fața în coordonatele sursei. Înainte
   de a folosi acestea în plugin verifică axele/yaw-ul rigului propriu.
5. Modelul Horizon este diferit ca proporții de `LandVehicleSpec.OFF_ROADER`
   din proiectul țintă. Nu reutiliza orbește scaunele, roțile, dimensiunile
   de coliziune, volanul, locurile spate sau fuel port-ul original. Avem doar
   coordonata șoferului din Horizon; locuri suplimentare nu sunt specificate
   aici. Seat attach este un punct Horizon, **nu** poziție garantată pentru o
   barcă sau un ArmorStand Paper. Camera și interacțiunea se testează separat.
6. Texture tint/paint în Horizon se aplică prin renderer; modelele sursă nu au
   `tintindex` pe fețe. Packul convertit nu promite vopsire identică. Nu colora
   tot modelul fără să verifici ce trebuie să rămână metal, geam sau cauciuc.
   `light_emission` a fost eliminat: farurile nu sunt emisive prin acest pack.
7. Testează toate grupurile, texturile/UV, roțile, rezerva, dimensiunea, direcția,
   așezarea jucătorului și mișcarea în Minecraft vanilla real. Testele automate
   de conversie verifică structura, nu redarea, performanța sau camera. Nu
   susține că modelul este verificat vizual până nu există capturi/test în joc.

Conversia este reprodusă prin `paper-vehicles/tools/build_off_roader_transfer.py`
în HorizonMods. Licența și atribuirile trebuie păstrate la distribuire.
