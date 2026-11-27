# Investigație: montură de barcă virtuală (Paper 1.21.4)

Stare: **investigație, nu prototip funcțional**. Nu există comandă nouă și nu s-a schimbat clientul, fizica sau resource pack-ul. Sursa mașinii păstrează scaunul-cal real și fizica existentă. Nu presupunem că un pachet de entitate sau de pasager schimbă camera în mod identic cu o barcă reală.

## Ce știm

- O montură falsă locală implică faptul că serverul și clientul au grafuri de pasageri diferite. Protocolul conține pachete separate Set Passengers și Move Vehicle, iar comportamentul clientului depinde de montura percepută, nu de cea reală de pe server.
- Patch-ul Paper 1.21.4 pentru `ServerGamePacketListenerImpl.handleMoveVehicle` verifică montura rădăcină reală, pasagerul care o controlează și `lastVehicle`; valorile invalide pot duce la deconectare. A transmite pur și simplu o barcă falsă fără a gestiona pachetele de mișcare nu dovedește că montura reală va rămâne sigură sau sincronizată.
- Invizibilitatea pentru entități non-living precum bărcile nu este garantată de API-ul Bukkit; se începe cu model vizibil, fără a modifica resource pack-ul sau bărcile normale.
- ProtocolLib 5.4.0 anunță suport pentru 1.21.4. Proiectul actual nu depinde de ProtocolLib/PacketEvents. Listarea read-only nu a găsit JAR-uri cu numele acestor biblioteci în primele 100 intrări din `/plugins`; aceasta nu dovedește ce cod este încărcat efectiv.

## Condiții minime înainte de un test

1. Bibliotecă de pachete aleasă și versiune compatibilă, fără instalare peste alte pluginuri sau dependență obligatorie pentru mașinile normale.
2. Sesiune opt-in pentru un OP, un singur jucător, durată limitată; pentru început pe un vehicul de test, zonă sigură și fără pasageri adiționali. Fără aplicare generală.
3. Alocare ID fără coliziuni cu entitățile reale și virtuale, creare în ordinea corectă, proprietate explicită pentru pachetele monturii și evitarea eliminării altor pasageri. Pachetele trimise altor observatori rămân neschimbate la început.
4. Definirea comportamentului pentru pachetele `Move Vehicle`, input și ieșire ale clientului; nu se presupune că player input rămâne intact. Testarea va stabili dacă actualizările de poziție/yaw ale bărcii controlate local sunt acceptate și dacă camera urmează.
5. Restaurare verificabilă a monturii reale și ștergere a entității virtuale la stop, Shift, timeout, deconectare, moarte, schimbare lume, urmărirea entității, unload, disable și erori. La eșec sau stare incertă se oprește testul și nu se continuă spoofingul.
6. Experimentul nu pornește dacă alt test de cameră/scaun este activ; comportamentul implicit este neschimbat. Nu inventăm sau reutilizăm ID-uri de teleportare în afara gestiunii Paper.
7. Test în joc cu F5 și first person, tastatură/mouse, mers, viraje, oprire/coborâre și un observator. Nu se susține compatibilitate perfectă sau aplicare la pasageri înainte de aceste verificări.

Surse: Paper `ver/1.21.4` patch `paper-server/patches/sources/net/minecraft/server/network/ServerGamePacketListenerImpl.java.patch`; https://github.com/dmulloy2/ProtocolLib/releases/tag/5.4.0 ; https://wiki.vg/Protocol .
