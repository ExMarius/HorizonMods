# Export experimental pentru Minecraft 1.21.4

Generatorul convertește cele două modele Blockbench existente (nu importă direct GLB-ul) în modele item și texturi, plus un manifest al pivoților:

```sh
python3 vehicle-plugin-horizon/next-vehicle/combina-moderna/minecraft/build_parts.py downloads/horizon-combina-moderna.bbmodel --variant cereale --output downloads/combina-cereale-parti.zip --manifest downloads/combina-cereale-manifest.json
python3 vehicle-plugin-horizon/next-vehicle/combina-moderna/minecraft/build_parts.py downloads/horizon-combina-moderna-porumb.bbmodel --variant porumb --output downloads/combina-porumb-parti.zip --manifest downloads/combina-porumb-manifest.json
```

Coordonatele fiecărui cub sunt localizate la pivot și împărțite la opt pentru a intra în limitele modelului item. Transformarea externă trebuie să restabilească scala opt și să aplice pivotul și rotația cubului plus toate transformările ierarhiei de bone-uri, în ordinea corectă. Cuburile cu aceeași rotație în același bone sunt regrupate la pivotul acelui bone prin translație calculată cu inversa rotației; asta păstrează poziția matematică originală fără rotunjirea unghiurilor. Unghiurile libere nu sunt rotunjite la unghiuri vanilla: sunt lăsate în manifest pentru viitoarele ItemDisplay. UUID-urile din manifest indică părinții fără a depinde de numele grupurilor. Texturile PNG originale sunt încorporate în pack.

**Nu instala aceste zip-uri peste pack-ul existent:** sunt pack-uri experimentale independente, fără restul resurselor serverului. Nu există încă un rig care să le folosească, logică de heder, recoltare, buncăr, descărcare ori remorcă. Fișierele nu au fost validate în client Minecraft. Cifrele actuale, 324 de părți pentru cereale și 182 pentru porumb (pentru întreaga combină), sunt prea mari pentru a le considera un design performant; trebuie reduse înainte de integrarea live. Cele mai costisitoare sunt melcul de cereale (132) și roțile (144); optimizarea lor necesită simplificare geometrică sau o altă reprezentare, nu doar grupare matematică. Geometria provine din modelele Blockbench actuale și nu este o conversie 1:1 a GLB-ului furnizat. Geamul și convențiile de transformare trebuie verificate în joc.

## Importul fidel al GLB-ului trimis

`import_glb_mesh.py` separă cele trei poziții cunoscute din GLB-ul primit și exportă triunghiurile transformate în fișiere `.bbmodel` (JSON Blockbench free cu mesh-uri). Necesită `numpy` și `trimesh`; rulează, de exemplu, cu un mediu Python virtual. Scara este uniformă, dar dimensiunea totală de 3,65 blocuri pe înălțime este o presupunere, nu o măsurătoare a sursei. Importul păstrează geometria triunghiulară și culorile de bază ale materialelor, nu și toate proprietățile PBR. Aceste fișiere mesh **nu sunt modele JSON item Minecraft** și nu au pivoți de animație sau gameplay. Separarea este specifică aranjamentului spațial al GLB-ului trimis; nu folosi scriptul pentru alte scene fără adaptare. Modelele generate din GLB-ul furnizat de utilizator rămân locale.

## Cuburi JSON extrase din GLB

`convert_glb_items.py` prelucrează direct GLB-ul furnizat: voxelizează suprafețele fiecărui mesh, apoi grupează cuburile alăturate de aceeași culoare în elemente Minecraft. Rulează cu `.venv/bin/python convert_glb_items.py <model.glb> --output <pack.zip> --manifest <manifest.json>` (dependințe `numpy`, `scipy`, `trimesh`). Parametrul `--pitch` controlează compromisul detaliu/performanță; implicit 8 unități sursă. Rezultatul este o aproximare geometrică, nu identic cu mesh-ul. Înălțimea implicită 3,65 blocuri este estimată. Materialele PBR sunt înlocuite cu culori plate; transparența și iluminarea necesită verificare.

Pack-ul rezultat este experimental și conține modele item statice separate pentru cele trei poziții. Valorile de la pitch 8 necesită regenerare după corectarea etichetării. Nu există separare în bone-uri sau animație, rig, joc ori test client; nu se instalează peste pack-ul existent. Această geometrie este costisitoare și trebuie optimizată înainte de utilizare. `build_glb_preview.py <pack.zip> <director>` generează JSON-uri intermediare pentru comparația vizuală din preview; nu sunt resource-pack. Generarea derivatelor din GLB rămâne locală.

Conversia detaliată locală a fost construită cu `--pitch 5`: cereale 5.106 cuburi, porumb 5.899 cuburi; este mai fină decât cea la pitch 8, dar mult mai costisitoare și nu este un model gata de utilizare live. Preview-ul grupează cuburile după culoare strict pentru randarea în browser; asta nu reduce numărul cuburilor în JSON-ul Minecraft. Comenzile de animație sunt dezactivate pentru aceste modele statice.

### Corecție identificare și bone-uri provizorii

Anterior, modelul din dreapta, fără heder, era etichetat greșit drept cereale. Modelul de cereale este cel din mijloc: `cereale` X≈29, `porumb` X≈−585, `fara_heder` X≈561. S-au regenerat modelele detaliate și preview-ul.

`rig_glb_boxes.py <pack> <manifest> <director>` separă aproximativ cuburile convertite în grupuri Blockbench pentru caroserie, heder și patru roți, folosind regiuni spațiale și pivoți estimați. Clasificarea poate include accidental cuburi ale caroseriei în roți/heder și trebuie inspectată vizual; rabatorul, melcul și tubul nu sunt separate în mod fiabil. Nu este încă un model realizat manual, optimizat sau un rig Minecraft funcțional.

## Cuburile utilizatorului, fără redesenare

`merge_voxel_boxes.py <input.bbmodel> <output.bbmodel>` încearcă reunirea cuburilor adiacente cu aceleași fețe/textură în interiorul fiecărui bone, fără modificarea volumului sau a culorilor. Pentru cele două fișiere curente, conversia inițială făcuse deja aceste reuniri: rezultatul rămâne la 5.106 cuburi pentru cereale și 5.899 pentru porumb. Exportul `build_parts.py` le grupează în câte șase modele/ItemDisplay, dar fiecare model conține în continuare mii de cuburi: șase display-uri nu înseamnă un model performant sau cu sub 300 de elemente.

Fișierele `glb-*-optimizat.bbmodel` și copiile `horizon-combina-glb-*-bucati.bbmodel` păstrează geometria voxelizată, nu reconstrucția desenată separat. Gruparea actuală în roți și heder este estimată spațial, nu identificată sigur din sursă, și poate include cuburi greșite; melcii și rabatorul nu sunt separați. Preview-ul grupează cuburile după bone/culoare doar pentru afișare rapidă, fără a reduce complexitatea resursei din joc. Nu există încă integrare sau verificare Minecraft. Atingerea limitei de 250–300 de cuburi va necesita înlocuirea formelor prin aproximări, nu o reunire exactă.
