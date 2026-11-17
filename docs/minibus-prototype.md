# Bus prototype — not yet a playable vehicle

The first vehicle is being developed using the Minecraft Blockbench bus from
FoundationGames' [City Vehicles Example Addon](https://github.com/FoundationGames/City-Vehicles-Example-Addon),
licensed MIT (see `third_party/city_vehicles/`). It is a large three-axle bus,
not an exact replica of the MrCrayfish minibus. The source OBJ geometry and
texture are retained; `tools/import_city_bus.py` uniformly resizes and rotates the body and places the original six wheels
at upstream axle positions in a single static Horizon OBJ model. This replaces
the previous procedurally created prototype. The wheels do not animate yet.

This model remains unregistered: it cannot be crafted or spawned yet. It has
not been checked in game. Further work is needed to match all six animated
wheels and all intended seats to the adapted model, to implement multiplayer
mounts, add physically accurate lighting, driver visibility, item, recipe,
translations, fuel and driving characteristics, and to test block steps and
multiplayer. `SeatReservations` is not an actual mounting system. A mass
parameter is not yet present in the current physics.

The [MrCrayfish Mini Bus model](https://github.com/MrCrayfish/MrCrayfishVehicleMod/blob/918cefe5f1e49168ac329efbca103f39070a0323/src/main/resources/assets/vehicle/models/vehicle/mini_bus/body.json)
explicitly says "All Rights Reserved" in its model credit even though the mod's
code is GPL; it was inspected but its model and textures were not copied.
