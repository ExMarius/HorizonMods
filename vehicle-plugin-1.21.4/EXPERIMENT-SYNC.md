# Experiment de sincronizare, Paper 1.21.4

Sursa de bază `9222ad65a8308fd93ff7512078b3b79ec4688ba1` a fost compilată
și comparată cu JAR-ul de pe server: toate cele 138 clase aveau bytecode identic
înainte de experiment. Packul și modelele nu sunt schimbate.

Caroseria și roțile sunt ItemDisplay-uri independente cu interpolare de poziție
de 3 tickuri; scaunul este o entitate mutată separat. Această diferență poate
contribui la decalaj, dar nu dovedește cauza vizuală. Modul opțional
`/vehicle syncmode direct` setează interpolarea poziției și transformării la 0
pentru display-urile rigului și mută montura non-barca în fiecare tick la
ancoră, cu pasagerii păstrați. `/vehicle syncmode normal` restaurează 3/1
și comportamentul anterior. Doar OP/vehicle.admin, nu persistă peste restart.

Acesta este un test A/B, NU o soluție validată: poate accentua tremuratul,
funcționează cu entități încă separate și nu modifică fizica locală a bărcii,
libertatea capului sau camera. Trebuie verificat cu un client vanilla real,
drept, viraj, mers înapoi, urcare/coborâre, staționare și privit liber; cu un
al doilea observator dacă e posibil. Mineflayer și testele serverului nu
randază camera sau modelele. Nu se modifică automat serverul.
