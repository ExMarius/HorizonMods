package com.mrcrayfish.vehicle.paper.render;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertEquals;

class VehicleSyncModeTest {
    @Test void stableModeRetainsPreviousInterpolation() {
        assertEquals(3, VehicleSyncMode.NORMAL.teleportTicks());
        assertEquals(1, VehicleSyncMode.NORMAL.transformTicks());
    }
    @Test void directModeUsesNoDisplayInterpolation() {
        assertEquals(0, VehicleSyncMode.DIRECT.teleportTicks());
        assertEquals(0, VehicleSyncMode.DIRECT.transformTicks());
    }
}
