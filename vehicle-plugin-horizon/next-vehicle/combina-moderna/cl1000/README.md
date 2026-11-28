# CL1000 primit în format Blockbench

Sursa este fișierul `.bbmodel` trimis de utilizator, păstrat local în `downloads/glb-imports/cb7869cfffcd6e70/model.bbmodel`; nu se înlocuiește și nu este inclus în Git. Are 453 mesh-uri cuboidale, 481 de grupuri, două texturi PNG încorporate și nu are animații declarate.

## Pregătire experimentală

```sh
python3 vehicle-plugin-horizon/next-vehicle/combina-moderna/cl1000/convert_bbmodel.py downloads/glb-imports/cb7869cfffcd6e70/model.bbmodel downloads/combina-cl1000-bb-cuburi.bbmodel
# Requires numpy and scipy in a Python virtual environment.
.venv/bin/python vehicle-plugin-horizon/next-vehicle/combina-moderna/cl1000/flatten_parts.py downloads/combina-cl1000-bb-cuburi.bbmodel downloads/combina-cl1000-piese.bbmodel
python3 vehicle-plugin-horizon/next-vehicle/combina-moderna/minecraft/build_parts.py downloads/combina-cl1000-piese.bbmodel --variant cereale --output downloads/combina-cl1000-bb-piese.zip --manifest downloads/combina-cl1000-bb-piese-manifest.json
```

Primul pas reconstruiește cele 453 mesh-uri drept cuburi din aceleași vârfuri și texturi, păstrând grupurile și rotațiile din fișierul utilizatorului. Al doilea aplică transformările ierarhiei în fiecare cub, scalează lățimea totală la 4,8 blocuri (estimare) și le repartizează în grupuri de vehicul. Roțile, tubul, scaunul și rabatorul sunt identificate din numele grupurilor sursă; o parte a hederului este identificată spațial. Pivoții și împărțirea hederului sunt estimative, `intake_auger` este încă gol. Rezultă lungime totală aproximativă 8,50 blocuri și înălțime 3,72 blocuri; cerința de 4,8 blocuri se aplică lățimii totale, nu unei măsurători certificate a hederului.

Exportul experimental conține 96 părți ItemDisplay și 453 cuburi, nu este optimizat conform țintei anterioare de 250–300 elemente. Nu este un pack complet și nu trebuie instalat peste cel al serverului. Texturile, orientarea UV, transparența, ierarhia/pivoții și poziția jucătorului trebuie verificate în client. Nu sunt implementate în plugin rigul, animațiile, recoltarea, buncărul, descărcarea, transferul sau gararea acestui vehicul. Nu a fost efectuat niciun deploy pentru combină.
