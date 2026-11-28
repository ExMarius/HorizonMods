# Concept: pompă dublă benzină / motorină

Preview separat de implementarea Paper. Pornim de la modelul și geometria pompei existente; al doilea pistol și latura sa sunt o adaptare, nu o copie validată în Minecraft.

- Benzină: pistol verde; motorină: pistol negru. Etichetele trebuie să indice și tipul combustibilului, nu doar culoarea.
- Un singur pistol activ pe pompă la un moment dat; un jucător poate ține cel mult un pistol. Alegerea trebuie să folosească click-ul pe partea corespunzătoare, inclusiv după rotirea pompei. Când titularul depune, pleacă sau depășește lungimea, pistolul revine la loc.
- Fiecare parte are propriul furtun și preț global/litru, configurabil în fișier și printr-o comandă administrativă. Afișajul trebuie să arate tipul, litrii livrați și suma sesiunii.
- Se folosește Vault cu un furnizor de economie; lipsa sau eroarea furnizorului trebuie să oprească alimentarea cu plată, fără combustibil gratuit. Încasarea și livrarea trebuie coordonate astfel încât să nu factureze combustibil nelivrat sau să ofere combustibil neplătit; fracțiile și prețul în schimbare necesită reguli explicite.
- Stocarea actuală a vehiculelor are un singur rezervor numeric, fără tip benzină/motorină. Nu presupunem compatibilitate diesel sau conversia în litri reali fără o regulă explicită și păstrarea datelor existente. O propunere compatibilă este 1000 de unități interne per litru; se va confirma înainte de a aplica facturarea.
- Pompele deja plasate trebuie păstrate prin adaptarea datelor existente. Pistoalele, furtunurile, hitboxurile și citirea afișajului trebuie validate vizual în Minecraft înainte de a considera designul finalizat.
- Vault și EssentialsX au fost încărcate pe server, dar furnizorul efectiv și pornirea lor după restart nu sunt încă verificate. EssentialsX poate schimba comenzi și comportamente ale serverului.
