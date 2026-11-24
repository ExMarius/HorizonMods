package com.mrcrayfish.vehicle.paper.render;

/** Reversible experiment: remove visual interpolation rather than changing geometry. */
public enum VehicleSyncMode {
    NORMAL(3, 1),
    DIRECT(0, 0);

    private final int teleportTicks;
    private final int transformTicks;

    VehicleSyncMode(int teleportTicks, int transformTicks) {
        this.teleportTicks = teleportTicks;
        this.transformTicks = transformTicks;
    }

    public int teleportTicks() { return teleportTicks; }
    public int transformTicks() { return transformTicks; }
}
