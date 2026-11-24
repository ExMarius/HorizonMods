# Următorul vehicul: Dacia Logan

Modelul ales este `vehicle/models/vehicle/dacialogan_body.json` din arhiva
`vehicle.rar` oferită de utilizator, cu permisiunea declarată pentru modele;
nu este un model generat procedural. Se păstrează creditul existent în copia
aprobată. Parametrii provin din `vehicle/vehicles/dacia_logan.json` din aceeași
arhivă: patru locuri, patru roți, scară caroserie 1.7 și motor large.
Coordonatele sunt în sistemul original al modului, nu poziții Paper validate.

`prepare_dacia.py` copiază cele 230 de elemente, UV, rotații, tinturi și
texturi într-un pack candidat separat; verifică formatul, limitele vanilla și
nu suprascrie resursele existente. Baza necesară este packul Horizon deja
publicat, verificat prin SHA-1. Rezultatul nu este instalat automat.

Mai trebuie: înregistrare ID separat și integrarea fizicii, a celor patru
scaune, roților, volanului și culorilor pe baza codului original MrCrayfish;
teste Paper, verificare în joc și abia apoi livrare. Geometria verificată
structural nu dovedește redarea sau poziția jucătorilor în client.

## Dacia Logan poliție — în lucru

`prepare_police.py` folosește modelul și configurația distincte de poliție,
cele 268 de elemente și textura/sunetul din arhiva aprobată. Combină resursele
numai cu packul curent identificat prin SHA-1, refuză coliziunile și păstrează
intrările existente; testele automate nu confirmă aspectul în Minecraft. Sunetul
de sirenă este inclus ca resursă, dar comanda/comportamentul nu sunt implementate.
Nu este încă înregistrată ca vehicul și nu este instalată pe server.
