# Politica vehiculelor, trustului și tractării

Decizii discutate cu utilizatorul; comportamentul este supus verificării în Minecraft. Nu considerați prezenta listă dovadă că toate cazurile sunt deja implementate sau complet sigure la crash.

## Vehicule obișnuite
- Proprietarul rămâne proprietar și numai garajul lui primește vehiculul; trustul oferă drept de condus, nu proprietate.
- Când proprietarul iese, vehiculele obișnuite neconduse rămân afară 5 minute înainte de a fi garate în siguranță; întoarcerea lui anulează așteptarea. Nu se aplică perechii rezervate pe platformă, care are regula specială de mai jos.
- Dacă proprietarul pleacă în timp ce un șofer autorizat conduce, șoferul își poate termina cursa. Când coboară, dacă proprietarul este offline, începe o perioadă de 5 minute. Reintrarea proprietarului sau urcarea unei persoane anulează temporizatorul. Nu se scoate vehiculul de sub ocupanți sau în mișcare.
- Excepțiile existente pentru vehicule pe cric, vitrine și legături cu remorci trebuie păstrate în siguranță. După expirare se așteaptă dacă situația nu permite gararea.

## Platforma de tractare
- Vehicule mici/medii, încărcare din spate; nu se începe cu pasageri în vehiculele manevrate. Drepturi necesare pe ambele vehicule; nu există protecții WorldGuard/GriefPrevention în această etapă.
- Dacă proprietarul cargo pleacă, cargo rămâne pe platformă. Dacă el este offline și nu mai este șofer în platformă timp de 5 minute, se pornește descărcarea verificată, numai cu platforma oprită și goală; obstacolele blochează mișcarea până când este sigur. După descărcarea automată cargo intră imediat în garaj dacă proprietarul încă e offline.
- La descărcare manuală cargo stă pe sol 5 minute înainte de a fi garat dacă proprietarul este offline. Întoarcerea proprietarului sau urcarea anulează temporizatorul. Retragerea trustului păstrează procedura specială: oprire, coborâre și descărcare sigură, apoi garare dacă proprietarul e offline.
- La quit al proprietarului platformei se păstrează regula deja confirmată: evacuare sigură și gararea ambelor vehicule, fiecare la proprietarul lui. Dacă aceeași persoană deține ambele, se aplică regula platformei. Nu se pornește un cronometru de 5 minute pentru acest caz: evităm să rămână o pereche rezervată fără proprietarul platformei.
- La restart/crash perechea în tranzit are în mod normal snapshot-uri în garaj (OUT_TOWING/TOWED); temporizatoarele nu se păstrează. La pornire, mașinile obișnuite deținute din ultimul snapshot sunt mutate în garajele proprietarilor înainte de reactivare, cu excepții de siguranță: vehiculele pe cric, legate la remorci, fără proprietar valid sau cu date de remorcă insuficient cunoscute nu sunt mutate automat. Dacă snapshot-ul de pornire nu poate fi salvat, activarea eșuează în loc să expună o recuperare nesalvată. Registrele de remorci incomplete nu se suprascriu cu o listă parțială. Salvarea periodică existentă și lipsa fsync nu oferă o garanție absolută contra tuturor crash-urilor; schimbările nesalvate pot fi pierdute.

## Verificări în joc încă necesare
- Off-roader cu fața și cu spatele, urcare/coborâre, roți, caroserie și cablu; verificarea vizuală aparține utilizatorului.
- Cele două temporizatoare, anularea lor, descărcarea automată blocată și reluarea, revenirea proprietarului, trust revocat și quit al proprietarului platformei.
- Repornire normală și recuperare din stările de tranzit pe serverul de test; nu se presupune protecție completă împotriva crash-urilor.
