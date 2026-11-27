package com.mrcrayfish.vehicle.paper.recovery;

import com.mrcrayfish.vehicle.paper.vehicle.LandVehicleSpec;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class RecoveryTruckSpecTest {
    @Test void liveOffsetsUseCorrectedLongitudinalAxis() {
        var spec=LandVehicleSpec.byId(RecoveryTruckSpec.ID);
        assertNotNull(spec);
        assertEquals(-1.56F,spec.wheels().get(0).axleZ());
        assertEquals(-1.56F,spec.wheels().get(1).axleZ());
        assertEquals(3.92F,spec.wheels().get(2).axleZ());
        assertEquals(3.92F,spec.wheels().get(3).axleZ());
        var ramps=spec.bodyParts().stream().filter(p->p.model().equals("horizon_service_ramp")).toList();
        assertEquals(2,ramps.size());
        ramps.forEach(ramp->assertEquals(5.35F,ramp.center().z()));
        spec.seats().forEach(seat->assertEquals(-.94F,seat.sourceOffset().z()));
    }
}
