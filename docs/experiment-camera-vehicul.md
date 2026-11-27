# Experiment: privire relativă la vehicul, client vanilla

## Obiectiv

Fără mod pe client și fără barcă ascunsă: corpul să urmărească vehiculul, privirea schimbată cu mouse-ul să păstreze aproximativ același unghi relativ în viraje, iar pasagerul să rămână în scaun. Nu există garanție de lipsă a tremuratului; verificarea vizuală se face de utilizator în joc. Nicio schimbare nu se aplică tuturor vehiculelor înainte de acceptarea experimentului.

## Ce există

`paper/render/LandVehicleRig.java` folosește deja un cal invizibil ca montură a unui display; acesta este creat numai pentru un loc ocupat și eliminat după coborâre. Scaunele sunt aliniate la yaw în condițiile `carryBody`. Display-urile au interpolare la teleport. Implementarea lui MrCrayfish din `vehicle-plugin/src/main/java/.../entity/VehicleEntity.java` are `clampYaw` client-side (±120°), urmărește opțional orientarea și utilizează `CameraHelper` client-side; nu poate fi transpusă direct într-un plugin pentru client vanilla.

## Atenție la propunerea cu teleport relativ

Pe ramura Paper `ver/1.21.4`, `paper-api/.../TeleportFlag.java` documentează că flag-urile `Relative` expuse în API sunt pentru **viteză**, nu pentru poziția sau yaw-ul relativ al camerei. `Relative.YAW` și `PITCH` sunt aliasuri deprecated pentru `VELOCITY_ROTATION`, nu un delta de privire. `CraftPlayer.teleport` folosește coordonate/yaw absolute, emite eveniment de teleport și poate demonta jucătorul dacă lipsește `EntityState.RETAIN_VEHICLE`. Prin urmare, rețeta propusă pentru `player.teleport` nu implementează ce susține și nu trebuie aplicată per tick.

Referințe:
- https://github.com/PaperMC/Paper/blob/ver/1.21.4/paper-api/src/main/java/io/papermc/paper/entity/TeleportFlag.java
- https://github.com/PaperMC/Paper/blob/ver/1.21.4/paper-server/src/main/java/org/bukkit/craftbukkit/entity/CraftPlayer.java

Pachetele vanilla/NMS nu se reduc la un singur flag API: trebuie analizate confirmările de teleport și starea serverului și clientului; trimiterea manuală nesincronizată poate produce desincronizare, demontare sau alte efecte. Pachetul de rotație a capului nu dovedește controlul trunchiului local. Fără teste în client nu se pot afirma libertate 360°, fluiditate perfectă sau compatibilitate cu armele.

## Plan pentru prototip

1. Măsurăm întâi comportamentul existent într-un vehicul de test, în prima și a treia persoană, cu privirea în lateral și viraje lente/rapide; observăm din ambele perspective, șofer și alt jucător.
2. Cercetăm dacă orientarea monturii deja folosite poate îmbunătăți urmărirea fără teleportarea jucătorului; păstrăm un comutator temporar pentru revenire rapidă și nu atingem fizica, alte vehicule, protecțiile sau recovery.
3. Abia dacă este necesar și înțeles complet, investigăm un mecanism de pachete compatibil exact cu 1.21.4; nu îl activăm automat și nu promitem că serverul poate controla corpul local ca un mod client.
4. Verificăm separat compatibilitatea cu pluginul real de arme înainte să afirmăm că trasul din vehicul funcționează.

Checkpoint-ul proiectului și al pluginului creat înaintea experimentului este descris în `exports/checkpoints/README-revenire.md`.
