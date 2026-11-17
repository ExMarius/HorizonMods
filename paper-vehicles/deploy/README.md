# Livrare SFTP controlată — versiune de dezvoltare

Workflow-ul `paper-deploy.yml` construiește și testează proiectul de pe branch,
verifică amprenta SSH **înainte** de autentificare, apoi încarcă exclusiv
`plugins/HorizonVehiclesPaper-dev.jar`. Verifică SHA-256 la upload, folosește
fișier temporar și nu șterge vechiul JAR dacă înlocuirea atomică nu este
suportată. Nu execută comenzi pe server, nu schimbă alte pluginuri, lumea sau
configurația și nu repornește serverul. JAR-ul este doar un schelet: nu există
încă vehicule jucabile.

Configurează **GitHub Actions repository secrets**, niciodată în chat sau în
repo:

- `HIDENCLOUD_SFTP_USERNAME`: utilizatorul SFTP din panel.
- `HIDENCLOUD_SFTP_PRIVATE_KEY`: cheia SSH **privată ED25519** (preferată);
  adaugă doar cheia publică în panel. Alternativ, `HIDENCLOUD_SFTP_PASSWORD`
  este parola SFTP. Dacă ambele există, este folosită doar cheia privată.
- `HIDENCLOUD_SFTP_HOST_KEY_SHA256`: amprenta SSH ED25519 în format `SHA256:…`,
  **confirmată independent de HidenCloud**. Rezultatul `ssh-keyscan` din
  workflow-ul de diagnostic este doar o observație, nu o sursă de încredere.
  Dacă nu există confirmare de la furnizor, nu seta valoarea și nu lansa deploy.

Odată configurate, declanșează `workflow_dispatch` pe branch; dacă GitHub nu
permite dispatch pentru un workflow absent pe branch-ul implicit, o schimbare
explicită în `paper-vehicles/deploy-request.txt` declanșează același job.
Workflow-ul nu rulează la orice push sau la pull request. Păstrează secretul
limitat la repo și rotește accesul compromis. Acest flux nu a fost încă testat
cu serverul real și poate eșua dacă SFTP nu permite citire/rename atomic sau
acces la directorul `plugins`.
