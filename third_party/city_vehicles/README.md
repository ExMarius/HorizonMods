# City Vehicles example bus model

Source: FoundationGames, [City Vehicles Example Addon for Automobility](https://github.com/FoundationGames/City-Vehicles-Example-Addon), revision `15bb7cd8ebbc940d241c90027420f2baccd887b8`.

The source assets here are the original Blockbench-exported Minecraft bus body,
wheel, and textures from `assets/cityvehicles/models/entity/bus*`. They are
provided under the upstream MIT license in `LICENSE`. The car frame properties
are upstream `data/cityvehicles/automobility/automobile_frame/yellow_bus.json`.

`tools/import_city_bus.py` rescales the original bus body and changes its material
references for the Horizon OBJ loader; it does not modify the shapes or UVs.
The upstream six-wheel model is retained for reference; the WIP prototype is
not registered or playable because this mod currently animates only four wheels
and has no passenger-seat integration. No claim of in-game compatibility.
