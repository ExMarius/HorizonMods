# Combină modernă 1:1 — model separat

Model editabil: `downloads/horizon-combina-moderna.bbmodel`. Preview: `cd vehicle-plugin-horizon/next-vehicle/combina-moderna/preview && npm install && npm start` (port 4188). Nu modifică modelul Gloria, pluginul, resource pack-ul sau serverul. Modelul este un concept cuboid inspirat de combine moderne, nu o reproducere certificată a unui model comercial.

Scară 16 unități = 1 bloc/metru, fața −Z, sol Y=0. După cererea de scurtare a spatelui, modelul are limite statice Z −70..+46: 116 unități / 7,25 m, nu 8,20 m. Hederul măsoară 4,80 m; înălțimea maximă 3,65 m.

Pivoți în unități Blockbench: `body` [0,0,0], `seat_driver` [0,26,-18], `header_assembly` [0,21,-20], `reel` [0,11,-57.5], `intake_auger` [0,6.5,-47.5], `unloading_auger` [-13,44,0], roți față [±18,14,-12], roți spate [±14,8.4,25]. Grupurile principale își păstrează UUID-urile, iar `reel`, `intake_auger` și `cutter_bar` rămân copii ai hederului. Markerul scaunului trebuie calibrat în Minecraft.

Preview-ul demonstrează oprirea la −6° prin încetinirea rabatorului și snecului. Convenția afișată „−16° sus” se traduce în rotație geometrică +16° pe axa X; cuțitul se ridică aproximativ 0,81 m față de poziția jos. Cilindrii sunt decorativi și nu se telescopiează automat.

Nu există recoltare, plată, detecție de culturi sau transfer în RM-2 în acest preview. Integrarea necesită dezvoltare separată și validare în Minecraft, inclusiv protecții pentru modificarea culturilor și siguranța inventarului. Desenele au cuburi rotite la unghiuri arbitrare și un număr mare de elemente; conversia pentru ItemDisplay trebuie făcută pe componente, nu presupusă ca export direct într-un singur model vanilla.

Revizia alb-perlat / roșu: hederul are plăci de pivot pe corp și o ramă de cuplare suprapusă peste gât și jgheab; cuțitul este la Y=0 în poziția de lucru. Puntea spate `rear_steering_axle` include pivot central, grindă, fuzete, brațe, bară și cilindru de direcție; grupurile `wheel_rl` și `wheel_rr` sunt copii ai punții, cu origini neschimbate. Sliderul rotește vizual ambele roți în jurul pivoturilor, dar nu este un sistem dinamic Ackermann și nu animează cinematica barei sau cilindrului. Nu a fost verificată evitarea tuturor intersectărilor la ridicare/direcție în Minecraft.

Revizia hederului: fața este −Z; rabatorul este mai jos și mai aproape de cuțit decât melcul, iar sensul rotației de jos duce plantele spre +Z. Melcul este reprezentat prin tambur poligonal, spirale detaliate din segmente, flanșe și degete. Punctele de pe laturi ale rabatorului se prind de brațe fixate pe heder; nu se garantează funcționarea fizică sau lipsa intersecțiilor până la validare.

Crampoanele au poziții și rotații individuale distribuite pe fiecare roată, nu depind de rotirea grupurilor intermediare. Hederul, rabatorul și melcul au revenit la geometria precedentă, mai detaliată; aceasta include numeroase rotații de cuburi. Toate intrările de textură din fișierul anterior au fost păstrate; paleta roșu/alb/antracit nu a fost schimbată. Conversia completă pentru Minecraft și aspectul vizual nu sunt încă validate.

## Heder de porumb — prototip vizual

`python3 build_model.py --corn` creează separat `downloads/horizon-combina-moderna-porumb.bbmodel`, folosind aceleași texturi și același pivot de heder. Preview-ul permite comutarea între fișiere. Hederul de porumb este o aproximare cu opt canale, nu o copie 1:1 a GLB-ului. Este doar vizual, fără recoltare sau integrare Minecraft. Hederul de cereale trebuie în continuare adaptat după referință.
