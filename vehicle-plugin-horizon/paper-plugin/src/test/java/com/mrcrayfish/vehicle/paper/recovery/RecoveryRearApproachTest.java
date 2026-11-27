package com.mrcrayfish.vehicle.paper.recovery;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class RecoveryRearApproachTest {
    @Test void identifiesRearForAllFourDirections() {
        for (double yaw : new double[]{0, 90, 180, 270}) {
            double r=Math.toRadians(yaw);
            var rear=RecoveryRearApproach.offset(-9.6*Math.sin(r),0,9.6*Math.cos(r),yaw);
            var front=RecoveryRearApproach.offset(9.6*Math.sin(r),0,-9.6*Math.cos(r),yaw);
            assertTrue(RecoveryRearApproach.selectable(rear));
            assertTrue(RecoveryRearApproach.daciaAligned(rear,0,0));
            assertFalse(RecoveryRearApproach.selectable(front));
        }
    }
    @Test void tenBlockLimitAndRampSupportAreEnforced() {
        assertTrue(RecoveryRearApproach.selectable(RecoveryRearApproach.offset(0,0,10,0)));
        assertFalse(RecoveryRearApproach.selectable(RecoveryRearApproach.offset(0,0,10.001,0)));
        assertFalse(RecoveryRearApproach.selectable(RecoveryRearApproach.offset(0,1,10,0)));
        assertFalse(RecoveryRearApproach.daciaAligned(RecoveryRearApproach.offset(0,0,8,0),0,0));
        assertFalse(RecoveryRearApproach.daciaAligned(RecoveryRearApproach.offset(.2,0,9.6,0),0,0));
        assertFalse(RecoveryRearApproach.daciaAligned(RecoveryRearApproach.offset(0,0,9.6,0),.2,0));
        assertFalse(RecoveryRearApproach.daciaAligned(RecoveryRearApproach.offset(0,0,9.6,0),0,30));
        assertThrows(IllegalArgumentException.class,()->RecoveryRearApproach.offset(Double.NaN,0,0,0));
    }
}
