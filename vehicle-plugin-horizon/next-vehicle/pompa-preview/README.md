# Preview 3D: pompă roșie nouă

`npm install && npm start` pornește preview-ul pe portul 4185, accesibil pe `0.0.0.0`. Pompa, pistolul și furtunul sunt concepute de la zero în `app.js`; nu sunt modelele vechi din joc. Corpul are aproximativ 0,94 × 1,84 × 0,72 blocuri, afișaj, butoane, locaș lateral și pistol roșu cu țeavă metalică. Textul este desenat în browser, nu este încă un asset Minecraft.

Furtunul are 16 segmente; capătul de la pompă este fix, iar celălalt se calculează din transformarea conectorului pistolului. O curbă cu lăsare calculată aproximează greutatea furtunului. Aceasta este o demonstrație, nu un model fizic sau o implementare Paper. Jucătorul, mâna și perspectiva sunt schematice. Aspectul, punctele exacte de prindere, distanța și funcționarea trebuie confirmate de utilizator și apoi validate în Minecraft.

Nu modifică serverul. Pompa veche există deja în plugin, iar codul ei este marcat ca validat și înghețat; acest concept este separat. Nu se înlocuiesc pompele existente, datele sau resource pack-ul înainte de confirmarea designului și stabilirea compatibilității.
