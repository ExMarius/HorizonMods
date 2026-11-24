package com.mrcrayfish.vehicle.paper.render;

import com.mrcrayfish.vehicle.paper.vehicle.LandVehicleSpec;
import org.junit.jupiter.api.Test;
import org.joml.Vector3f;
import org.joml.Quaternionf;
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
    @Test void assembledWheelGroupsMirrorTogetherWithoutLosingTheDiagonal() {
        Quaternionf diagonal = new Quaternionf().rotateX((float)Math.toRadians(67.5));
        Quaternionf mirror = new Quaternionf().rotateY((float)Math.PI);
        Vector3f source = new Vector3f(0.3F, 0.8F, 0.2F);
        Vector3f expected = new Quaternionf(mirror).mul(diagonal).transform(new Vector3f(source));
        Vector3f left = DaciaHorizonWheels.wheelGroupRotation(diagonal, -1).transform(new Vector3f(source));
        assertEquals(expected.x, left.x, .00001F);
        assertEquals(expected.y, left.y, .00001F);
        assertEquals(expected.z, left.z, .00001F);
        Vector3f right = DaciaHorizonWheels.wheelGroupRotation(diagonal, 1).transform(new Vector3f(source));
        Vector3f unmirrored = diagonal.transform(new Vector3f(source));
        assertEquals(unmirrored.x, right.x, .00001F);
        assertEquals(unmirrored.y, right.y, .00001F);
        assertEquals(unmirrored.z, right.z, .00001F);
    }
}
