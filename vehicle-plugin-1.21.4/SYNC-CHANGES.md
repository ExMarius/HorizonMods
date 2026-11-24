# Sincronizare scaun și roți — Paper 1.21.4

Baza este versiunea 10 noiembrie verificată la nivel de bytecode (138 clase),
cu resource packul și modelele neschimbate. Display-urile caroseriei, roților
și ancorei scaunului folosesc interpolare de poziție și transformare zero și
primesc datele aceluiași tick. Montura liberă este actualizată la ancora de
scaun în fiecare tick, păstrând pasagerii; barca nu mai primește suplimentar
poziția tickului precedent. Nu se forțează rotația camerei jucătorului.

Această abordare elimină întârzierea intenționată de 3 tickuri a display-urilor,
dar nu dovedește că entitățile separate sunt redate simultan pe client. Poate
produce tremur și nu elimină controlul local al bărcii sau alte efecte ale
Minecraft vanilla. Testele de server verifică pornirea și persistența, nu
redarea, camera, sau sincronizarea vizuală în mers. Dacă apar probleme, se
poate restaura JAR-ul 10 noiembrie din backupul de pe server.
