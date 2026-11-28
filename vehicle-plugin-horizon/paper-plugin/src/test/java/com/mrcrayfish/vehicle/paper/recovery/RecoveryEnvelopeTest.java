package com.mrcrayfish.vehicle.paper.recovery;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import static com.mrcrayfish.vehicle.paper.recovery.RecoveryEnvelope.*;
class RecoveryEnvelopeTest {
    @Test void daciaPreviewEnvelopeFitsButLeavesLittleLongitudinalMargin(){
        // Bounds from the edited JSON at scale 1.7; tyre dimensions are approximate.
        Vehicle dacia=new Vehicle(23.0*1.7/16,46.8*1.7/16,2.06,2.06,.32);
        assertTrue(fits(dacia));
        assertTrue((DECK_END-REAR_RAMP_CLEARANCE-ROLLER_EXIT)-dacia.length()<.1);
    }
    @Test void refusesOversizeWrongTrackOrUnknown(){
        assertFalse(fits(null));
        assertFalse(fits(new Vehicle(2.61,4.9,2.06,2.06,.32)));
        assertFalse(fits(new Vehicle(2.4,5.05,2.06,2.06,.32)));
        assertFalse(fits(new Vehicle(2.4,4.9,1.2,2.06,.32)));
        assertFalse(fits(new Vehicle(2.4,4.9,2.06,2.06,.73)));
        assertThrows(IllegalArgumentException.class,()->new Vehicle(0,1,1,1,1));
        assertThrows(IllegalArgumentException.class,()->new Vehicle(Double.NaN,1,1,1,1));
        assertThrows(IllegalArgumentException.class,()->new Vehicle(1,Double.POSITIVE_INFINITY,1,1,1));
    }
}
