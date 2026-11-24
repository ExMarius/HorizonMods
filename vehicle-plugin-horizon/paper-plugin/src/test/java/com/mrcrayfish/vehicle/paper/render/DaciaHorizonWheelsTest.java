package com.mrcrayfish.vehicle.paper.render;

import com.mrcrayfish.vehicle.paper.vehicle.LandVehicleSpec;
import org.junit.jupiter.api.Test;
import org.joml.Vector3f;
import static org.junit.jupiter.api.Assertions.*;

class DaciaHorizonWheelsTest {
    @Test void wheelClearanceIsSymmetricAndRotatesAroundEachSteeringAxle() {
        var spec = LandVehicleSpec.DACIA_LOGAN_POLICE;
        float extra = 2.0F * spec.bodyScale() / 16.0F;
        for (var w : spec.wheels()) {
            Vector3f straight = DaciaHorizonWheels.visualCenter(w, 0, extra);
            assertEquals(w.axleX() + w.halfWidthOffset() + w.side() * extra, straight.x, 0.00001F);
            assertEquals(w.axleZ(), straight.z, 0.00001F);
            float angle = (float)Math.toRadians(35);
            Vector3f turned = DaciaHorizonWheels.visualCenter(w, angle, extra);
            float dx = turned.x - w.axleX(), dz = turned.z - w.axleZ();
            assertEquals(Math.abs(w.halfWidthOffset() + w.side() * extra),
                    Math.sqrt(dx * dx + dz * dz), 0.00001);
            assertEquals(w.centerY(), turned.y, 0.00001F);
        }
    }
}
