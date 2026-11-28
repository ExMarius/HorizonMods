# Selected Paper 1.21.4 baseline

Source: ExMarius/MrCrayfishVehicleMod commit
`50583bb8618b8ad0b94e6e3aa5e28ea7dae761e5` (5 November), paper-plugin only.
Built and deployed through Actions run 45385265200; upload verified SHA-256
`8d45843ea6664415e5027d5b957dead70ac1d290e5c8abd67bfb9d70acc5bf59`.
The user confirmed this version was working, including `/vehicle creative`.
Do not treat the later `vehicle-plugin-1.21.4/` November 10 snapshot or the
`vehicle-plugin/` 26.3 snapshot as this baseline. No automatic deployment is
configured for this directory.

Before any update back up and verify the live JAR and all plugin data, build
against Paper 1.21.4/Java 21 and test on a disposable server. Preserve worlds,
existing data, config, colours and the existing server pack. A running server
can modify data after a live backup is taken; for a consistent recovery point,
stop it cleanly and back up again. Falix power API may require manual verification.
