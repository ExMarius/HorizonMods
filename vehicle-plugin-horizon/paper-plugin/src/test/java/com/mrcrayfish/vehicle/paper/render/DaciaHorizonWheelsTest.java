package com.mrcrayfish.vehicle.paper.render;

import com.mrcrayfish.vehicle.paper.vehicle.LandVehicleSpec;
import org.junit.jupiter.api.Test;
import org.joml.Vector3f;
import static org.junit.jupiter.api.Assertions.*;

class DaciaHorizonWheelsTest {
    @Test void originalWheelOffsetsRotateAroundEachSteeringAxle() {
        var spec = LandVehicleSpec.DACIA_LOGAN_POLICE;
        for (var w : spec.wheels()) {
            Vector3f straight = DaciaHorizonWheels.visualCenter(w, 0);
            assertEquals(w.axleX() + w.halfWidthOffset(), straight.x, 0.00001F);
            assertEquals(w.axleZ(), straight.z, 0.00001F);
            float angle = (float)Math.toRadians(35);
            Vector3f turned = DaciaHorizonWheels.visualCenter(w, angle);
            float dx = turned.x - w.axleX(), dz = turned.z - w.axleZ();
            assertEquals(Math.abs(w.halfWidthOffset()),
                    Math.sqrt(dx * dx + dz * dz), 0.00001);
            assertEquals(w.centerY(), turned.y, 0.00001F);
        }
    }
}
