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
- După restart/crash, vehiculele obișnuite din ultimul snapshot rămân în lume sau în stare hibernată încă 5 minute; la reconectarea proprietarului cronometrul se anulează. Temporizatorul continuă dacă un vehicul este hibernat/reactivat. La expirare se verifică proprietarul, ocupanții și legăturile și, dacă e sigur, vehiculul se mută în garaj. Vehiculele pe cric sau cu remorci legate și cele cu legături necunoscute sunt exceptate până pot fi tratate în siguranță. Timerul pornește de la zero la fiecare restart.
- Excepție: perechea tractată în tranzit revine direct în garaj după restart/crash, din snapshot-urile OUT_TOWING/TOWED; nu există încă restaurare sigură a perechii pe platformă cu un cronometru. Registrele incomplete de remorci nu se suprascriu cu o listă parțială. Salvarea periodică și lipsa fsync nu garantează păstrarea schimbărilor nesalvate la crash.

## Verificări în joc încă necesare
- Off-roader cu fața și cu spatele, urcare/coborâre, roți, caroserie și cablu; verificarea vizuală aparține utilizatorului.
- Cele două temporizatoare, anularea lor, descărcarea automată blocată și reluarea, revenirea proprietarului, trust revocat și quit al proprietarului platformei.
- Repornire normală și recuperare din stările de tranzit pe serverul de test; nu se presupune protecție completă împotriva crash-urilor.
