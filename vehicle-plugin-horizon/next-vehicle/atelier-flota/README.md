# Atelier Horizon — două concepte originale

Galerie 3D cu platformă auto și atelier mobil, desenate de la zero în
`design.js` ca ansambluri de piese cu poziții explicite. Ambele folosesc
aceeași cabină și șasiu, iar suprastructurile sunt diferite. Cabina are
geamuri semitransparente, locuri, bord și volan; platforma are troliu și
rampe, iar atelierul are obloane și suport pentru echipamente.

Este o previzualizare Three.js, nu un model Blockbench sau un model de resource
pack. Nu există încă mecanici, conversie Minecraft ori instalare pe server.
Roțile sunt aproximări poligonale în browser, nu geometrie Minecraft validată.

Pornește cu `npm ci && npm start` (portul 4176, sau `PORT` pentru alt port).

## Export pentru modelul Minecraft

`node minecraft/export.mjs` convertește piesele amplasate manual din `design.js`
în cinci modele de item: cabină/șasiu, platformă, atelier, volan și roată.
Modelul este normalizat pentru un `ItemDisplay` la scala 4. Fișierele sunt în
`minecraft/assets/`; `conversion-report.json` consemnează înclinările rotunjite
la unghiurile permise de format. Roțile și volanul din browser sunt aproximate
cu cuboizi în export, iar alfa geamurilor trebuie verificată pe clientul jocului.
Comutatorul „Arată JSON Minecraft” afișează geometria JSON aproximativ, nu
simulează fidel rendererul Minecraft.

`python3 minecraft/build_pack.py BASE.zip CANDIDAT.zip --expected-sha1 HASH`
construiește numai local un pachet separat, după verificarea SHA-1, formatului și
absenței coliziunilor; nu modifică pachetul de intrare și nu instalează pe server.
Funcționalitatea, coliziunile, scaunele, șofatul, troliul și rampele nu sunt
implementate în plugin; doar piesele vizuale sunt pregătite.
