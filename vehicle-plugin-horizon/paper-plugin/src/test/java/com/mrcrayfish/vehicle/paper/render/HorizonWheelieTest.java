package com.mrcrayfish.vehicle.paper.render;

import com.mrcrayfish.vehicle.paper.vehicle.LandVehicleSpec;
import org.joml.Vector3f;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class HorizonWheelieTest {
    @Test void boostRotatesFrontWheelAndChassisAroundSameRearPivot() {
        LandVehicleSpec spec = LandVehicleSpec.HORIZON_OFF_ROADER;
        var p = spec.wheeliePivot();
        Vector3f pivot = new Vector3f(p.x(), p.y(), p.z());
        Vector3f front = new Vector3f(14.74F / 16F, .390F, 14.5F * 1.42F / 16F);
        Vector3f nearbyBody = new Vector3f(.7F, .69F, 1.0F);
        Vector3f f = SourceTransforms.chassisPoint(front, pivot, -30, 0);
        Vector3f b = SourceTransforms.chassisPoint(nearbyBody, pivot, -30, 0);
        assertTrue(f.y > front.y, "front wheel rises on boost");
        assertEquals(front.distance(nearbyBody), f.distance(b), 1e-5F,
                "wheel and body remain rigidly related");
    }
}
