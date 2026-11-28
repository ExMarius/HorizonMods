# Propunere: recoltare și descărcare CL1000

Acesta este un plan, nu o funcție instalată. În preview, culturile, tractorul și remorca sunt schematice; capacitatea și cantitățile afișate nu sunt stabilite pentru server.

## Recoltare

- Hederul de cereale și rabatorul lucrează în fața combinei, în timp ce aceasta înaintează. Încep cu grâul Minecraft ajuns la maturitate; plantele imature rămân intacte.
- Grâul matur produce grâu (`WHEAT`) și semințe (`WHEAT_SEEDS`), în cantități provenite din loot-ul Minecraft, nu generate în mod fix ca în preview. Se colectează în buncăr pe tipuri distincte. În Minecraft, un balot de fân (`HAY_BLOCK`) nu este același lucru cu grâul; transformarea automată în baloți sau recoltarea ierbii ca fân necesită confirmare.
- Cu hederul ridicat la/peste −6° sau treieratul oprit, rabatorul încetinește treptat și recoltarea se oprește. Cu buncărul plin, combina nu distruge plantele a căror recoltă nu încape. Porumbul rămâne neimplementat.

## Transfer în remorcă, inclusiv în mers

- Tubul trebuie deschis spre exterior; tractorul poate trage o remorcă agricolă compatibilă în paralel, fără să fie decuplată. Conținutul intră în inventarul efectiv al remorcii, nu în obiecte fizice aruncate pe jos. În codul actual `TRACTOR_TRAILER` și `TRACTOR_TRAILER_MODERN` au inventar de 27 sloturi; alegerea exactă a remorcii RM-2 și a volumului benei trebuie legată de modelul din joc.
- La fiecare actualizare, transformăm poziția gurii tubului în coordonatele locale ale benei, ținând cont de poziția și yaw-ul actual al ambelor vehicule. Transferul este permis doar dacă gura este deasupra deschiderii benei, la o înălțime adecvată. Asta funcționează și când ambele se deplasează; dacă ies din aliniere, se oprește imediat.
- Transferul mută numai cantitatea care încape, scăzând exact ce s-a acceptat în inventarul remorcii. Se întrerupe la remorcă plină, buncăr gol, tub închis, remorcă dispărută/hibernată sau distanță nepotrivită. Datele buncărului trebuie persistate; transferul în memorie nu este o garanție de siguranță la crash, care necesită proiectare separată.
- Fluxul vizual de boabe/semințe este decorativ și este afișat numai cât transferul are loc; nu produce iteme Minecraft care pot fi culese sau duplicate. Poate folosi particule sau afișaje temporare limitate ca număr. Clientul vede să cadă în benă, în timp ce inventarul se actualizează pe server.

## Sisteme complementare

- Indicator de umplere și tipuri din buncăr; notificări la buncăr/remorcă plină sau tub nealiniat, fără spam.
- Mișcarea rabatorului, a roților și a tubului; sunete și particule limitate; feedback când hederul este ridicat. Fără logici pentru porumb până la o etapă ulterioară.
- Persistență pentru conținut și starea relevantă, restaurare după garare/restart; descărcarea activă se oprește la dispariția unui vehicul. Compatibilitate cu inventarele existente, fără un jurnal tranzacțional nou în această etapă.
- Folosim mecanismele de evenimente ale serverului pentru recoltare și păstrăm protecțiile suplimentare amânate. Nu încărcăm chunk-uri doar ca să căutăm remorci; căutarea și particulele se limitează la vehiculele apropiate și active.
