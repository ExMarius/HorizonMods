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

Pachetul relativ poate exprima intenția de a adăuga unghiul mașinii la privire, dar nu dovedește că mouse-ul rămâne complet liber și nici că mișcarea este lină. În Paper 1.21.4, `ServerGamePacketListenerImpl.internalTeleport` actualizează și starea jucătorului pe server, `awaitingTeleport`, poziția așteptată și abia apoi trimite pachetul. Tratarea confirmării include o deconectare pentru stare inconsistentă. Prin urmare, **nu trimite doar `ClientboundPlayerPositionPacket` cu un ID inventat**, chiar dacă folosești PacketEvents/ProtocolLib: transportul pachetului nu sincronizează automat starea serverului. Vezi https://github.com/PaperMC/Paper/blob/ver/1.21.4/paper-server/patches/sources/net/minecraft/server/network/ServerGamePacketListenerImpl.java.patch .

Nu există în build-ul curent al pluginului o dependență ProtocolLib sau PacketEvents; folosirea directă NMS ar depinde de versiune și necesită tratarea confirmărilor, a întreruperii, a altor teleportări, a călăririi, a diferenței de timp/ping și a posibilei rotații deja aplicate de montură. Invocarea `internalTeleport` nu demonstrează că acele cazuri sunt rezolvate. Pachetul de rotație a capului nu dovedește controlul trunchiului local. Fără verificări în client nu se pot afirma libertate 360°, fluiditate perfectă sau compatibilitate cu armele.

## Plan pentru prototip

1. Măsurăm întâi comportamentul existent într-un vehicul de test, în prima și a treia persoană, cu privirea în lateral și viraje lente/rapide; observăm din ambele perspective, șofer și alt jucător.
2. Cercetăm dacă orientarea monturii deja folosite poate îmbunătăți urmărirea fără teleportarea jucătorului; păstrăm un comutator temporar pentru revenire rapidă și nu atingem fizica, alte vehicule, protecțiile sau recovery.
3. Abia dacă este necesar și înțeles complet, investigăm un mecanism de pachete compatibil exact cu 1.21.4; nu îl activăm automat și nu promitem că serverul poate controla corpul local ca un mod client.
4. Verificăm separat compatibilitatea cu pluginul real de arme înainte să afirmăm că trasul din vehicul funcționează.

Checkpoint-ul proiectului și al pluginului creat înaintea experimentului este descris în `exports/checkpoints/README-revenire.md`.

## Prototip opt-in (Paper 1.21.4)

`/vehicle cameratest pornit` este disponibil doar OP, în timp ce conduce un vehicul care nu este blocat în tractare. Există maximum o sesiune, pentru acel șofer și acel vehicul, cu durată de două minute. `/vehicle cameratest oprit` o oprește; de asemenea se oprește la coborâre, deconectare, schimbarea vehiculului, tractare, eroare, schimbare bruscă a unghiului sau întârzierea confirmării. Implicit nu este activ pentru nimeni.

Cercetarea folosește prin reflecție metoda NMS `internalTeleport` a conexiunii, nu un pachet cu ID inventat. Sunt folosite coordonate și yaw/pitch relative zero în afară de delta-yaw, cu flag-uri de păstrare a vitezei; se așteaptă terminarea unui teleport anterior, se limitează frecvența la cel mult 10 pe secundă și se întrerupe dacă se acumulează o corecție excesivă. Metoda este internă, dependentă de versiune și nu reprezintă un API stabil sau o garanție de funcționare; se oprește dacă clasele ori câmpurile nu există. Folosește metoda internă fără eveniment Bukkit de teleport, deci alte pluginuri/anti-cheat pot reacționa diferit. Montura calului poate adăuga propria rotație și poate apărea supracorecție. Nu există dovezi că trunchiul local sau camera se vor comporta precum la barcă; numai utilizatorul poate evalua vizual. Un teleport deja trimis poate primi confirmarea chiar după oprirea experimentului.

La verificarea în joc: într-o zonă liberă, pe serverul de test, compară mersul fără comandă cu cel după activare, în F5 și prima persoană; rotește mouse-ul stânga/dreapta atât în linie dreaptă, cât și în viraje, verifică coborârea, kick-uri, desincronizări și poziția pentru un observator. Oprește imediat la probleme. Nu extinde la pasageri sau la celelalte vehicule fără validare.

## Prototip separat pentru corp

`/vehicle corptest pornit` (OP, la volan, fără recovery) menține orientarea calului-scaun al șoferului aliniată la vehicul și când acesta stă pe loc, în loc să o aplice numai la mers/viraj. Este un experiment distinct de `cameratest`, nu folosește pachete de teleport și nu permite rularea simultană a ambelor; dezactivare cu `/vehicle corptest oprit`, automat la coborâre, schimbarea vehiculului, recovery, dezactivare plugin sau după două minute. La mers codul existent deja aliniază montura, deci este posibil ca efectul să fie mic sau inexistent. Acesta **nu** este un control direct al `yBodyRot` pe client și nu garantează corp fix sau privire 360°. Comparația F5 la staționare și la mers trebuie făcută de utilizator înainte de orice adoptare generală.

## Prototip izolat cu barcă vizibilă

La cererea utilizatorului, se poate observa o alternativă tehnică folosind `/vehicle testbarca pornit`: un display cu model de go-kart este rădăcină, o barcă de stejar vizibilă este pasagerul lui, iar operatorul este pasagerul bărcii. `W/S` mișcă încet rădăcina cu verificări simple de obstacole și sol; `A/D` virează rădăcina doar când este apăsată și o comandă de mers. Cu doar A/D pe loc rădăcina nu virează, astfel încât rotația independentă a bărcii poate fi observată. Shift sau `/vehicle testbarca oprit` termină experimentul; este limitat la OP, o sesiune, două minute, fără persistență și nu se șterge montura dacă jucătorul nu poate coborî.

Acesta este un **machetă separată**: nu este un vehicul normal, nu are fizica, toate piesele, roțile, locurile sau comportamentul de garaj al pluginului. Nu schimbă rig-ul, mașinile normale ori resource pack-ul; barca de stejar și textura ei rămân vizibile. Rezultatele indică doar cum funcționează ierarhia în condițiile acestui experiment, nu garantează integrarea în mașinile reale, rotația 360°, lipsa glitch-urilor sau compatibilitatea cu armele. Se folosește pe serverul de test, pe suprafață plană, liberă, departe de margini și alte entități. Nu se extinde la sistemul normal fără o verificare vizuală și confirmarea utilizatorului.
