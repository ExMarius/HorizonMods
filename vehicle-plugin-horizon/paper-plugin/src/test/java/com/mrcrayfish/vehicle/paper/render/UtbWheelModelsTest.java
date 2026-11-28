package com.mrcrayfish.vehicle.paper.render;

import com.mrcrayfish.vehicle.paper.vehicle.LandVehicleSpec;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertEquals;

class UtbWheelModelsTest {
    @Test void frontAndRearUseIndependentModelsAtSpawnAndRestore() {
        var utb = LandVehicleSpec.UTB_650;
        assertEquals("utb_650_wheel_front", LandVehicleRig.wheelModelFor(utb, utb.firstFrontWheel(), "standard_wheel"));
        assertEquals("utb_650_wheel_rear", LandVehicleRig.wheelModelFor(utb, utb.firstRearWheel(), "standard_wheel"));
        assertEquals("sports_wheel", LandVehicleRig.wheelModelFor(utb, utb.firstRearWheel(), "sports_wheel"));
        assertEquals("standard_wheel", LandVehicleRig.wheelModelFor(LandVehicleSpec.TRACTOR, LandVehicleSpec.TRACTOR.firstFrontWheel(), "standard_wheel"));
    }
}
