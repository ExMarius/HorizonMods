# Preview interactiv: pompa și furtunul

`npm install && npm start` pornește preview-ul pe portul 4185, accesibil pe `0.0.0.0`. Folosește modelele și texturile pompei și ale duzei din `vehicle-plugin/src/main/resources/assets/vehicle`, curba Hermite și opt segmente inspirate de `GasPumpRig`. Jucătorul este doar un model schematic; poziția mâinii, perspectiva, rotațiile item display și execuția în Minecraft nu sunt reprezentate cu fidelitate garantată. Nu modifică pompa sau serverul.

Modul actual Paper există deja: `/vehicle gaspump`, click pe partea de sus pentru a lua/depozita duza, alimentare gratuită a celui mai apropiat vehicul la 4 blocuri (în circa 15 secunde pentru gol-plin); distanța maximă implicită a furtunului este 10 blocuri. Nu are rezervor sau plată. Codul pompei este marcat în sursă ca înghețat și validat anterior, deci nu este modificat de acest preview. Cere confirmare pentru orice reproiectare a comportamentului sau modelului.
