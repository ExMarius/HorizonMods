# Horizon vehicle gallery

Interactive browser previews of **existing repository assets**:
`content/assets/gokart/models/block/{ambulance_body,smurd_body,fire_truck_body}.json`
and their `gokart:block` textures. They are not newly authored for this gallery,
not the Minecraft renderer, and not proof of installation or functional integration
in the active Paper server plugin. Wheel positions are approximate for display.

The browser renderer uses the source cuboids, rotations, face UV and texture files,
not a replacement low-poly mesh. It does not implement every Minecraft model option
and should not be used as proof of exact in-game appearance.

Run `npm ci && npm start` in this folder. The server listens on `0.0.0.0:4175`
(override with `PORT`). It needs the repository's `content/` directory alongside it.
