# Boat synchronization investigation (Paper 1.21.4)

The current Go-Kart remains experimental: a real player reports that the body
separates from the occupied boat. Do not treat passing the offline protocol smoke
as proof that the visual problem is fixed.

## Evidence

The disposable Paper server sends the player **before** the armor-stand carrier
in the boat's passenger list after mounting. CI run 44272525643 deliberately
failed on that observation. The previous comment claiming the carrier reserves
control was incorrect. The smoke client only sends input packets; it does not
simulate the vanilla client's local boat movement, rendering or camera. Its
stationary-steering and server position checks cannot detect client prediction
or visual divergence.

The player being first is consistent with the observed problem: the vanilla
client may locally simulate its boat while the plugin separately calculates
motion and teleports the boat. This is a plausible cause, not yet a verified
root cause; passenger offsets, nested display transforms, interpolation and the
actually loaded server JAR also need checking in a real vanilla client.

## Next investigation

* Confirm the installed JAR/version, client version, pack and reproduce with a
  vanilla client; record first-person and third-person, including other viewers.
* Compare the client's predicted boat, server position and carrier/display
  positions while driving and steering. Test under latency as well as locally.
* Evaluate a client-side packet-only fake player as the first passenger, with
  the real player second, only in an isolated prototype. It could suppress local
  boat control but requires correct entity lifecycle, passenger ordering, player
  seat offsets and input delivery, and may introduce other visual artifacts.
* Alternatively use vanilla boat movement as the sole movement authority, which
  changes vehicle physics and likely conflicts with the requirement that A/D not
  rotate the boat independently. A client mod could provide custom rendering and
  prediction, but is a different deployment and needs user approval.
* Compare versions only after reproducing the relevant passenger-order and client
  prediction behavior on them. Older versions without display entities or the
  current item model format would also require a renderer/pack rewrite; no version
  change is presently supported by evidence as a fix.

No proposed alternative has yet passed a real vanilla-client visual test.

## Shared-carrier prototype (opt-in, not visually verified)

The plugin now has an isolated alternative hierarchy: marker armor stand ->
boat -> player, and the same stand -> kart ItemDisplays. It is enabled by default for the requested server trial. To revert to the original
rig, set `experiments.nested-boat-seat: false` in the plugin data directory's `config.yml` (nested YAML syntax) and restart. Use `/hvehicle spawn go_kart`
for the boat or `/hvehicle spawn go_kart_raft` for the bamboo raft.
The existing model and resource pack are unchanged. This option is experimental;
seat/model offsets, rotation, camera and prediction may still be wrong.

The disposable Paper 1.21.4 smoke enables the option, mounts a Mineflayer bot,
checks the passenger tree, moves and steers the server-side rig and dismounts.
A separate command-only experiment tests both oak boat and bamboo raft mounted
on a marker stand next to an item display. Both chains survive mounting and a
root movement according to the captured passenger packets. These checks do not
simulate client movement or render anything; they do not establish whether the
raft or boat stays visually aligned or which has the desired camera.

Relevant reference: Yarn 1.21.4 documents AbstractBoatEntity and its passenger
position and controller methods:
https://maven.fabricmc.net/docs/yarn-1.21.4+build.1/net/minecraft/entity/vehicle/AbstractBoatEntity.html
A community example of a boat mounted on a marker stand:
https://www.reddit.com/r/MinecraftCommands/comments/zpd8y7/fix_boats_position_so_it_cannot_be_pushed_by_a/
Neither reference proves the proposed rig works for a moving local rider.
