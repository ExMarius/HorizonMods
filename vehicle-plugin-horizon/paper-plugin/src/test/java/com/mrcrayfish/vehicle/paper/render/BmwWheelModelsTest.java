package com.mrcrayfish.vehicle.paper.render;

import com.mrcrayfish.vehicle.paper.vehicle.LandVehicleSpec;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class BmwWheelModelsTest {
    @Test void allFourWheelsUseOriginalCoupeModel() {
        var wheels = LandVehicleSpec.BMW_M6.wheels();
        for (var wheel : wheels) {
            assertEquals("horizon_coupe_wheel", LandVehicleRig.wheelModelFor(LandVehicleSpec.BMW_M6, wheel, "standard_wheel"));
        }
    }
}
