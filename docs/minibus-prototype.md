# Mini Bus prototype — not a playable vehicle

The first planned vehicle is an original Minecraft-style compact minibus,
inspired by the general category and proportions of the MrCrayfish Vehicle
Mod Mini Bus. No model, texture, or code from the reference mod is copied.
The other proposed vehicles are a dune buggy, a compact sports coupe and a
small pickup. Work on them has not started.

`prototype_minibus_body.json` is generated from `tools/generate_assets.py`.
It is deliberately not registered as a standalone model, item, creative-tab
entry, command or recipe: it has not passed in-game review and passenger seats
cannot yet be used. Four approximate cushion coordinates relative to the model
center are recorded in `PROTOTYPE_MINIBUS_SEATS_TEXELS`; they are not mount
positions, a synchronization mechanism or proof of player clearance.

Before this vehicle can be released: implement and validate authoritative
multi-seat mounting and positioning (see `passenger-seating.md`), player-size
clearance and dismounts, speed/fuel/step height, item/recipe/localization,
wheel/steering alignment, and a real two-client test. Current physics derives
acceleration and top speed primarily from the engine tier; it does not expose a
vehicle-mass parameter. Do not claim a mass simulation or 1-block climbing
works until implemented and verified in the game.

## Reference inspection

- [MrCrayfish Vehicle Mod: Mini Bus](https://github.com/MrCrayfish/MrCrayfishVehicleMod/blob/master/src/main/java/com/mrcrayfish/vehicle/entity/vehicle/EntityMiniBus.java) and [SeatTracker](https://github.com/MrCrayfish/MrCrayfishVehicleMod/blob/master/src/main/java/com/mrcrayfish/vehicle/common/SeatTracker.java): separate properties for vehicle and a server-synchronized UUID-to-seat mapping.
- [MTS Official Pack](https://github.com/DonBruce64/MTSOfficialPack): separate JSON definitions for vehicle parts and seats; viewed for the data-driven organization, not copied.
- [Ultimate Car Mod EntityVehicleBase](https://github.com/henkelmax/ultimate-car-mod/blob/master/src/main/java/de/maxhenkel/car/entity/car/base/EntityVehicleBase.java): the vehicle limits passengers and positions each rider relative to the vehicle; this depends on Minecraft/Forge entity APIs unavailable in the same form in our Horizon glue.

Reference inspection does not mean the multiplayer behavior has been ported.
