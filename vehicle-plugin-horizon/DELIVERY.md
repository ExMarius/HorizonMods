# Horizon Off-Roader — livrare Paper 1.21.4

Sursă de bază 5 noiembrie: `50583bb8618b8ad0b94e6e3aa5e28ea7dae761e5`.
Modelul Horizon are ID separat `horizon_off_roader`; `off_roader` original
este păstrat. Driverul este singurul loc definit în layoutul Horizon.

Livrare: Actions run 45392102009; pre-release
`horizon-offroader-45392102009`. JAR SHA-256
`3d45d95a43ccd4875dd019510b70d8a5124f18aa257d3db98b41469c848d596f`;
pack SHA-1 `ca0413462ebbbc2fde1b8c2f1cfaf43620709661`.
Fișierele, configurația packului și hashurile au fost verificate pe Falix.
Packul r39 a fost extins cu namespace-ul Horizon, iar conținutul vechilor
fișiere a fost comparat cu originalul. Șase fișiere de date, JAR și
server.properties au backup verificat cu prefix `mcv-before-horizon-45392102009-`.
Backupul a fost efectuat cu serverul pornit și nu este instantaneu atomic al
lumii. API-ul de restart a returnat `403 verification_required`; încărcarea
în procesul serverului depinde de restart manual în panou.

Testele Java/Python au trecut. Pe Paper temporar, clientul de protocol a creat
vehiculul, urcat, condus, salvat și verificat încărcarea din garaj la restart;
a verificat un singur pack la intrare și niciunul la spawn. Aceste teste nu
randază modelul și nu validează camera, scaunul, culorile sau sincronizarea
vizuală. Fizica Paper este o adaptare provizorie, nu fidelitate demonstrată;
roțile off-road folosesc vizualul standard Horizon. Aplicarea culorii urmează
tintul integral aplicat de rendererul Horizon caroseriei, dar trebuie verificată
în joc. Nu afirma validare vizuală înainte de feedbackul unui client real.
