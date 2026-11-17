# Multi-seat and stretcher implementation notes

Status: **not integrated**. The current release still mounts only the driver.
`SeatReservations` in `runtime.rs` is standalone bookkeeping, not a mount system.
It must not be used as evidence that passengers or the stretcher work.

## Constraints verified in Horizon revision `9f42064`

- The current vehicle is a saddled pig; the existing client positioning and driver
  input logic assume one rider. Additional player links must not be mapped to the
  driver's seat or allowed to steer.
- `native_mount` resolves only boats, minecarts and living mobs as vehicles, even
  though Horizon's internal forced `/ride` path also supports static entities.
  A static-entity seat cannot simply be passed to that helper.
- `native_move_entity` can move a kept entity, but multiplayer tracking,
  interpolation and rider positioning during movement must be verified, not
  assumed. Teleporting a player to follow the vehicle removes them from their
  mount and is not a safe substitute.
- The acting-player context and the server tick see different players. Don't use
  proximity to infer which player controls a vehicle. Driver selection and
  passenger occupancy must come from authoritative mount links.

## Required integration before enabling this feature

1. Define per-vehicle seat identities and poses against the actual scaled models,
   including a distinct stretcher pose for ambulance/SMURD. Validate clearance
   and Minecraft player dimensions in game; a rendered cushion is not proof of
   space for a player.
2. Create addressable seat entities, with safe reach and explicit choice of seat;
   link an acting player to the requested empty seat through a supported mount
   path. Reserve only after a successful mount; report failures to the player.
3. Synchronize seat identity, parent and pose to every client; update positions
   and yaw as the vehicle moves, including late join, reconnect, chunk reload,
   interpolation and dimension changes. Separate driver inputs from passengers.
4. Implement the stretcher's lying pose and visible restraints only while occupied,
   and allow a patient to get off safely. Verify that pose and restraints are
   visible to both the patient and other clients.
5. Release and safely dismount on sneak, death, logout, removal, vehicle packing,
   unload, failed mount and server shutdown; clean up orphan seat entities.
6. Run Horizon integration tests plus an in-game two-client test: fill seats,
   deny duplicate occupancy, drive and turn, dismount, remove the vehicle,
   reconnect and reload the world. Also test collisions and obstructed exits.
