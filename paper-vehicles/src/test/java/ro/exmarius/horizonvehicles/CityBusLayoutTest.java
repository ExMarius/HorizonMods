package ro.exmarius.horizonvehicles;

import java.io.ByteArrayInputStream;
import java.nio.charset.StandardCharsets;
import org.junit.jupiter.api.Test;
import ro.exmarius.horizonvehicles.vehicle.CityBusLayout;
import static org.junit.jupiter.api.Assertions.*;

class CityBusLayoutTest {
    @Test
    void upstreamBusLayoutHasOneDriverThirteenPassengersAndSixWheels() {
        var layout = CityBusLayout.readBundled();
        assertEquals(14, layout.seats().size());
        assertEquals(1, layout.seats().stream().filter(CityBusLayout.Seat::driver).count());
        assertEquals(new CityBusLayout.Vec3(12, 12, 58), layout.seats().getFirst().sourceTexels());
        assertEquals(6, layout.wheels().size());
        assertEquals(2, layout.wheels().stream().filter(w -> w.end().equals("front")).count());
        assertEquals(2, layout.wheels().stream().filter(w -> w.end().equals("back")).count());
        assertEquals(2, layout.wheels().stream().filter(w -> w.end().equals("none")).count());
        assertThrows(UnsupportedOperationException.class, () -> layout.seats().clear());
    }

    @Test
    void rejectsNonFiniteCoordinatesInsteadOfSpawningInvalidEntities() {
        String invalid = """
            {"display":{"driver_seat":[0,"NaN",0],"passenger_seats":[],"wheels":[]}}
            """;
        assertThrows(IllegalArgumentException.class,
            () -> CityBusLayout.read(new ByteArrayInputStream(invalid.getBytes(StandardCharsets.UTF_8))));
    }
}
