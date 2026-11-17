# Livrare și restart automat — plugin Paper experimental

La cerere, workflow-ul `paper-deploy.yml` construiește și testează pluginul,
verifică amprenta SFTP și încarcă JAR-ul verificat în `plugins/`. La fiecare
livrare reușită, publică în folderul pluginului o cerere cu SHA-256-ul JAR-ului.
Watcherul din plugin anunță jucătorii și execută comanda de consolă `restart`
după 5 secunde, ca în proiectul Paper original. O cerere pentru JAR-ul deja
încărcat este consumată fără restart, pentru a preveni buclele. Dacă comanda
nu este disponibilă sau serverul nu repornește automat după oprire, este nevoie
de intervenție în panel. **Prima activare necesită un restart inițial** dacă
versiunea care rulează nu are watcherul: SFTP nu poate executa comenzi la distanță.
Un marker scris la prima instalare este consumat la pornire, fără un al doilea restart.

Înlocuirea se face atomic unde este disponibilă. În caz contrar, JAR-ul vechi
este redenumit într-un backup `.bak`, apoi JAR-ul nou este instalat; la eșec se
încearcă revenirea. Există un scurt interval între cele două redenumiri; nu
reporni serverul în timpul uploadului. O copie backup este păstrată pe server.

Autentificarea folosește secretele GitHub Actions `HIDENCLOUD_SFTP_USERNAME`
și `HIDENCLOUD_SFTP_PRIVATE_KEY` sau `HIDENCLOUD_SFTP_PASSWORD`. Amprenta hostului
este fixată pe baza valorii observate (TOFU), nu confirmată independent. Nu pune
secrete în repo. Livrarea atinge doar JAR-ul, backup-ul și markerul acestui plugin.
