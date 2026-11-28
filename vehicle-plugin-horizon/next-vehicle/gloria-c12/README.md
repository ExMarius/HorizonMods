# Gloria C12 / C14U — concept editabil

Model: `downloads/horizon-gloria-c12.bbmodel`, format Blockbench `free`, texturi de culoare încorporate. Preview: `cd vehicle-plugin-horizon/next-vehicle/gloria-c12/preview && npm install && npm start` (portul 4187). Acesta este un concept construit din cuburi, nu un model original de fabrică, nici implementare în plugin sau resource pack Minecraft.

Scară 16 unități = 1 m/bloc, sol Y=0, față −Z. Cererea inițială avea intervalul Z −46..30 (4,75 m), incompatibil cu lungimea dorită 7,60 m. Pentru proporții mai potrivite lângă UTB și remorcă am multiplicat toate coordonatele Z specificate cu 1,6: −73,6..+48 = 121,6 unități/7,60 m. Lățimea hederului este 67,2 unități/4,20 m, înălțimea este 52 unități/3,25 m. Roțile motrice sunt centrate la X ±17, lățime anvelopă 6,5 unități, diametru 24,8; la aceste valori anvelopele sunt 40,5 unități peste lățime, iar detaliile butucilor se apropie de 42,4. Nu susținem că modelul este un releveu exact din fabrică.

Origini 1:1 (unități Blockbench): `body` [0,0,0], `wheel_fl` [-17,12.4,-16], `wheel_fr` [17,12.4,-16], `wheel_rl` [-13,6.8,33.6], `wheel_rr` [13,6.8,33.6], `header_assembly` [0,20,-28.8], `reel` [0,12,-62.4] în interiorul hederului, `unloading_auger` [-12,38,3.2], `seat_driver` [-3,26,-24]. Acestea sunt origini în spațiul modelului, nu coordonate deja implementate în plugin. Originea scaunului este un marker; poziția de ședere trebuie calibrată în joc la geometria reală a pernei și la mecanica scaunului.

Preview-ul arată animații demonstrative, nu fizică sau interacțiuni live. Geometria completă și rotațiile arbitrare pot necesita împărțire în modele/item displays și adaptare la limitele Minecraft: `.bbmodel` nu este un resource pack direct instalabil. Nu s-a schimbat pompa, serverul sau pluginul.

Referință vizuală: https://umas.ro/muzeu (fotografie Gloria CP12). Componente și culori conform cerinței utilizatorului; nu există documentație metrologică a exemplarului de referință în repository.
