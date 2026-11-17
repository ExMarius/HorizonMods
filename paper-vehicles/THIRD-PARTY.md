# Third-party notices — development build

## Paper plugin reference code

The Paper Java sources and `FuelGaugeTest` were copied from
[ExMarius/MrCrayfishVehicleMod](https://github.com/ExMarius/MrCrayfishVehicleMod),
revision `6ff2f1da494e7861d14c6772b2bdbcbc2a70ade0` (the test was copied at `f52426454e69407e7f16c7e8eb20ff5a511c318d`), under the source project's
GPLv3 license in `LICENSE`. The copied source code retains its existing package
and comments. The original plugin entrypoint is present for future adaptation but is not enabled; the active entrypoint remains the new scaffold. It is not wired into vehicle commands.
A wider reference snapshot is retained in `../third_party/paper_vehicle_reference`.

## Models, textures and sounds

This development plugin does not yet include or distribute a resource pack or
any models, textures or sounds from MrCrayfish's Vehicle Mod or Furniture Mod.
Future asset ports must identify their exact sources, version, license, credits
and dependency chain. Some source models say "All Rights Reserved" in their
credit field despite the repository's GPLv3 license: those assets remain out
until their reuse terms are clarified. Do not erase or replace the original
credit to work around this. Absence of that note is not, by itself, proof of
permission for each dependency. FoundationGames City Vehicles has a separate
MIT license; its bus is not currently included in this plugin or a resource pack.
