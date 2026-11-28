# Vizualizator GLB și Blockbench

`npm install && npm start` pornește portul 4189 pe `0.0.0.0`. Modelul GLB 2.0 sau Blockbench `.bbmodel` (maximum 40 MB) este deschis local în browser; doar butonul explicit „Trimite modelul pentru analiză” salvează modelul și până la cinci capturi PNG în `downloads/glb-imports/<id>/`. Trimite calea afișată în chat pentru ca agentul să inspecteze fișierul și imaginile. Vederile rapide au axele +/− X și +/− Z; ce înseamnă „față” depinde de orientarea modelului importat.

Texturile trebuie încorporate în GLB. Exporturile cu extensii comprimate precum Draco sau KTX2 pot necesita conversie înainte de previzualizare. Este doar un vizualizator/import, nu convertește automat modelul GLB în cuburi Blockbench și nu modifică pluginul, pack-ul sau serverul Minecraft.

Un model deja trimis poate fi redeschis prin `/?model=<id>` folosind identificatorul primit la încărcare, cât timp fișierul se află în spațiul local.

Suportul `.bbmodel` afișează cuburi, mesh-uri poligonale, texturi încorporate și transformări de grup. Este un preview, nu Blockbench complet: animațiile Blockbench, unele tipuri de elemente, efecte și materialele speciale nu sunt implementate. Texturile externe nu sunt încărcate automat; aplicația arată un avertisment și o culoare de înlocuire. Salvează/încorporează texturile în proiect înainte de a-l trimite dacă vrei să ajungă și la agent. La trimitere se salvează `model.bbmodel` și capturi în același director ca GLB-urile.
