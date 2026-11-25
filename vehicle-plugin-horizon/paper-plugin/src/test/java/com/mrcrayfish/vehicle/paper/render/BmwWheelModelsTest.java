package com.mrcrayfish.vehicle.paper.render;

import com.mrcrayfish.vehicle.paper.vehicle.LandVehicleSpec;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class BmwWheelModelsTest {
    @Test void sourceRearBecomesSteeringAxleAfterBodyRotation() {
        var wheels = LandVehicleSpec.BMW_M6.wheels();
        assertEquals("bmw_m6_rear_right", LandVehicleRig.wheelModelFor(LandVehicleSpec.BMW_M6,wheels.get(0),"standard_wheel"));
        assertEquals("bmw_m6_rear_left", LandVehicleRig.wheelModelFor(LandVehicleSpec.BMW_M6,wheels.get(1),"standard_wheel"));
        assertEquals("bmw_m6_front_right", LandVehicleRig.wheelModelFor(LandVehicleSpec.BMW_M6,wheels.get(2),"standard_wheel"));
        assertEquals("bmw_m6_front_left", LandVehicleRig.wheelModelFor(LandVehicleSpec.BMW_M6,wheels.get(3),"standard_wheel"));
    }
}
