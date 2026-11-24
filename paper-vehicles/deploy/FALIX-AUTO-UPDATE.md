# Falix: actualizarea automată a pluginului

La un push pe branchul `arena/fb5f91ff-horizonmods` care modifică sursele sau
configurația de build din `vehicle-plugin/paper-plugin/`, workflow-ul
`falix-auto-update.yml` compilează și testează pentru Paper 1.21.4 / Java 21.
La succes se autentifică prin OIDC (fără parolă în repo), descarcă vechiul
JAR, salvează backup verificat prin SHA-256 în rădăcina serverului, încarcă
noul JAR, îl descarcă pentru verificare SHA-256 și cere restart doar dacă
serverul era și este încă pornit. Operațiile rulează serializat. Dacă serverul
este oprit, noul JAR se aplică la următoarea pornire, fără pornire automată.

O eroare de build, backup, transfer sau verificare oprește procedura și nu
cere restart. Dacă Falix respinge restartul (de exemplu verificarea planului
gratuit), workflow-ul raportează eroarea; JAR-ul poate fi deja actualizat,
dar trebuie repornit manual din panou. Un restart acceptat nu demonstrează
singur că pluginul a pornit, deci verifică și consola. Backup-urile rămân pe
server până sunt gestionate manual, nu sunt șterse automat.

Workflow-ul nu configurează packul și nu suprascrie `server.properties`. Dacă
configurația sursei încă indică packul 26.3-r41, acesta este dezactivat doar
în buildul pentru 1.21.4. Packul corect trebuie stabilit separat. Pe Falix,
configurația existentă a pluginului este păstrată și poate suprascrie implicitul
JAR-ului. Workflow-ul nu detectează încărcări manuale sau update-uri făcute pe
alt branch/repository: numai modificările împinse pe acest branch îl declanșează.

Testele `test_falix_auto_update.py` simulează verificarea backupului, a
transferului și ordinea restartului. Un ciclu complet real de update și restart
pe Falix încă necesită validare.
