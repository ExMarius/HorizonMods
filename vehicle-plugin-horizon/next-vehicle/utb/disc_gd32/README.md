# Grapă cu discuri GD-3.2 — preview and planned integration

`preview.html` is the last 3D preview discussed with the player. It requires
Three.js via the preview server import map and is not a Minecraft model. The
model uses 16 preview units per block, front -Z, 4 gangs of 8 discs, and a
transport axle. The player moved the transport wheels from x=±16,z=-3 to
x=±12,z=-1 to avoid overlap and asked for a foldable support when detached.

The geometry check exercises sampled blade/wheel separation and the previous
sketch's 23-unit / 18° versus endpoint mismatch. It is not a client-rendering,
physics, or protection test. No harrow item, commands, towing or world editing
is installed by this preview. Reproduce preview changes from this version;
do not silently replace the user's approved reference with a different design.

Before deploy: create actual Minecraft-compatible models (separate frame,
four animated disc shafts, two wheels, hitch and jack), independently test
towing over elevation changes and bends, implement a stateful safe work/road
mode, ensure ownership, permissions, protection-plugin compatibility, unloaded
chunk and restart safety, and test on a disposable Paper server. Save the
vehicle's active mode only if safe on load; always reset on detach.
