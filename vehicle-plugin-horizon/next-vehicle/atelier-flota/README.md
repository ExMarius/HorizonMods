# Atelier Horizon — două concepte originale

Galerie 3D cu platformă auto și atelier mobil, desenate de la zero în
`design.js` ca ansambluri de piese cu poziții explicite. Ambele folosesc
aceeași cabină și șasiu, iar suprastructurile sunt diferite. Cabina are deschideri cu geamuri semitransparente, scaune, bord și volan; platforma are troliu și
rampe, puncte de fixare, marcaje laterale și cutie de scule; atelierul are
obloane, închideri, treaptă spate și suport pentru echipamente.

Este o previzualizare Three.js, nu un model Blockbench sau un model de resource
pack. Există un export candidat Minecraft, dar nu există încă mecanici în joc sau instalare pe server.
Roțile sunt aproximări poligonale în browser, nu geometrie Minecraft validată.

Pornește cu `npm ci && npm start` (portul 4176, sau `PORT` pentru alt port).

## Export pentru modelul Minecraft

`node minecraft/export.mjs` convertește piesele amplasate manual din `design.js`
în șase modele de item: cabină/șasiu, platformă, atelier, volan, roată și rampă.
Modelul este normalizat pentru un `ItemDisplay` la scala 4. Fișierele sunt în
`minecraft/assets/`; `conversion-report.json` consemnează înclinările rotunjite
la unghiurile permise de format. Roțile și volanul din browser sunt aproximări cu cuboizi în export.
Scara roților spate este diferită pentru a rămâne sub podea; transparența
geamurilor trebuie verificată în clientul Minecraft.
Comutatorul „Arată JSON Minecraft” afișează geometria JSON aproximativ, nu
simulează fidel rendererul Minecraft.

`python3 minecraft/build_pack.py BASE.zip CANDIDAT.zip --expected-sha1 HASH`
construiește numai local un pachet separat, după verificarea SHA-1, formatului și
absenței coliziunilor; nu modifică pachetul de intrare și nu instalează pe server.
Funcționalitatea, coliziunile, scaunele, șofatul, troliul și rampele nu sunt
implementate în plugin; doar piesele vizuale sunt pregătite.

## Simularea de încărcare

Butoanele „Urcă pe roți” și „Trage cu troliul” arată două variante ale
aceleiași animații, cu modelul Dacia Poliție editat în proiect. „Descarcă”
arată coborârea. Roțile Daciei sunt aproximative, iar cablul este vizual.
Platforma măsoară 5,50 × 2,90 blocuri, iar rampele sunt piese articulate
separate. Simularea nu implementează controlul de către un jucător, troliul,
coliziuni, ancorare sau transport în Minecraft; acestea necesită implementare
și testare separate în plugin. Nu este instalată pe server.

Verificări locale: `node test-design.mjs`, `node test-loading.mjs` și
`cd minecraft && python3 -m unittest -v test_minecraft`.

### Siguranța la încărcare

În demonstrație, bifa „Simulează vehicul cu remorcă / utilaj cuplat” blochează
ambele variante de încărcare și cere decuplarea. Aceasta este o stare de test
din browser, nu citește remorcile din joc. Când încărcarea va fi implementată
în plugin, trebuie verificată starea reală de cuplare pentru orice vehicul
candidat atât la pornire, cât și pe parcurs, în ambele moduri; cuplarea trebuie
refuzată în timpul manevrei. Regulile nu sunt încă implementate pe server.
