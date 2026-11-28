# Vizualizator GLB

`npm install && npm start` pornește portul 4189 pe `0.0.0.0`. Modelul GLB 2.0 (maximum 40 MB) este deschis local în browser; doar butonul explicit „Trimite modelul pentru analiză” salvează modelul și până la cinci capturi PNG în `downloads/glb-imports/<id>/`. Trimite calea afișată în chat pentru ca agentul să inspecteze fișierul și imaginile. Vederile rapide au axele +/− X și +/− Z; ce înseamnă „față” depinde de orientarea modelului importat.

Texturile trebuie încorporate în GLB. Exporturile cu extensii comprimate precum Draco sau KTX2 pot necesita conversie înainte de previzualizare. Este doar un vizualizator/import, nu convertește automat modelul GLB în cuburi Blockbench și nu modifică pluginul, pack-ul sau serverul Minecraft.
