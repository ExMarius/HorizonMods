# Export experimental pentru Minecraft 1.21.4

Generatorul convertește cele două modele Blockbench existente (nu importă direct GLB-ul) în modele item și texturi, plus un manifest al pivoților:

```sh
python3 vehicle-plugin-horizon/next-vehicle/combina-moderna/minecraft/build_parts.py downloads/horizon-combina-moderna.bbmodel --variant cereale --output downloads/combina-cereale-parti.zip --manifest downloads/combina-cereale-manifest.json
python3 vehicle-plugin-horizon/next-vehicle/combina-moderna/minecraft/build_parts.py downloads/horizon-combina-moderna-porumb.bbmodel --variant porumb --output downloads/combina-porumb-parti.zip --manifest downloads/combina-porumb-manifest.json
```

Coordonatele fiecărui cub sunt localizate la pivot și împărțite la opt pentru a intra în limitele modelului item. Transformarea externă trebuie să restabilească scala opt și să aplice pivotul și rotația cubului plus toate transformările ierarhiei de bone-uri, în ordinea corectă. Cuburile cu aceeași rotație în același bone sunt regrupate la pivotul acelui bone prin translație calculată cu inversa rotației; asta păstrează poziția matematică originală fără rotunjirea unghiurilor. Unghiurile libere nu sunt rotunjite la unghiuri vanilla: sunt lăsate în manifest pentru viitoarele ItemDisplay. UUID-urile din manifest indică părinții fără a depinde de numele grupurilor. Texturile PNG originale sunt încorporate în pack.

**Nu instala aceste zip-uri peste pack-ul existent:** sunt pack-uri experimentale independente, fără restul resurselor serverului. Nu există încă un rig care să le folosească, logică de heder, recoltare, buncăr, descărcare ori remorcă. Fișierele nu au fost validate în client Minecraft. Cifrele actuale, 324 de părți pentru cereale și 182 pentru porumb (pentru întreaga combină), sunt prea mari pentru a le considera un design performant; trebuie reduse înainte de integrarea live. Cele mai costisitoare sunt melcul de cereale (132) și roțile (144); optimizarea lor necesită simplificare geometrică sau o altă reprezentare, nu doar grupare matematică. Geometria provine din modelele Blockbench actuale și nu este o conversie 1:1 a GLB-ului furnizat. Geamul și convențiile de transformare trebuie verificate în joc.
