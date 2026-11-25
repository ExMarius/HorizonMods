package com.mrcrayfish.vehicle.paper.render;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertEquals;

class DiscHarrowOrientationTest {
    @Test void entireVisualAssemblyIsHalfTurnedRelativeToPhysicsRoot() {
        for (float yaw : new float[]{0, 45, 90, -90, 180}) {
            double a=Math.toRadians(yaw), b=Math.toRadians(TrailerRig.harrowVisualYaw(yaw));
            assertEquals(-Math.cos(a), Math.cos(b), 1e-6);
            assertEquals(-Math.sin(a), Math.sin(b), 1e-6);
        }
    }
}
