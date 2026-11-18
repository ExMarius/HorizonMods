package ro.exmarius.horizonvehicles.kart;

import com.mrcrayfish.vehicle.paper.vehicle.LandVehicleSpec;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class GoKartSourceLayoutTest {
    @Test void paperReferenceHasOneDriverAndFourOriginalWheels() {
        var spec = LandVehicleSpec.GO_KART;
        assertEquals(1, spec.seats().size());
        assertTrue(spec.seats().getFirst().driver());
        assertEquals(4, spec.wheels().size());
        assertEquals(2, spec.wheels().stream().filter(LandVehicleSpec.Wheel::front).count());
        assertEquals(1.05, spec.stepHeight(), 1e-6);
        assertEquals(-45, spec.steering().rotationX(), 1e-6);
        assertEquals(180, spec.engine().rotationY(), 1e-6);
        var seat = spec.seats().getFirst().sourceOffset();
        assertEquals(-1.0 / 16, seat.z(), 1e-6);
        assertEquals((-3.0 - 1.0 + 3.2) / 16, seat.y(), 1e-6);
    }
}
