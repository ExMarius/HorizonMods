# Referință pentru cele două hedere

Referință: GLB-ul furnizat în conversație (`downloads/glb-imports/4e62101cc2953521/model.glb`), împreună cu capturile din același director. Fișierul conține trei reprezentări ale combinei: cu heder de porumb, cu heder de cereale și fără heder. Capturile sunt relativ îndepărtate, așa că detaliile fine trebuie inspectate la zoom înainte de reproducere. Nu presupunem că avem dreptul de redistribuire a fișierului: rămâne în spațiul local, nu este inclus aici în Git.

## Direcție vizuală

- O singură combină și două hedere distincte, schimbabile la același cuplaj frontal; nu trei combine separate în joc.
- Cereale: după modelul central, cu platformă lată, rabator transversal și grilă de gheare, păstrând funcțiile de ridicare și treierat planificate.
- Porumb: după modelul cu separatoare roșii conice, repetate pe lățime, și structură întunecată în spatele lor. Variantă vizuală separată pentru început; nu adăugăm și nu promitem recoltarea porumbului încă.
- Păstrăm paleta roșu/alb/antracit și texturile modelului modern existent. Forma și proporțiile sunt inspirate de referință, fără a presupune că datele din GLB sunt deja la scară Minecraft.

## Observații tehnice

GLB-ul primit are 271 mesh-uri, 529 noduri și nu declară animații. Numele nodurilor sunt generice (`Cube...`), nu o ierarhie clară de heder, roți sau pivoți funcționali. Importul ca mesh nu creează automat cuburi Blockbench, resource-pack valid, pivoți ori comportament Minecraft. Separarea pieselor, reconstrucția adaptată și verificarea vizuală rămân de făcut; niciunul dintre hedere nu este implementat pe baza acestei referințe încă.
