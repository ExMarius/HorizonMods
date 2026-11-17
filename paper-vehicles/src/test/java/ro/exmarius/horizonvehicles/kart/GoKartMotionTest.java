package ro.exmarius.horizonvehicles.kart;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class GoKartMotionTest {
    @Test void acceleratesAndBrakesWithinLimits() {
        GoKartMotion motion = new GoKartMotion(0);
        GoKartMotion.Step step = null;
        for (int i = 0; i < 100; i++) step = motion.tick(1, 0, false);
        assertEquals(0.35, step.speed(), 1e-9);
        assertEquals(0, step.dx(), 1e-9);
        assertTrue(step.fuel() < GoKartMotion.CAPACITY);
        for (int i = 0; i < 30; i++) step = motion.tick(0, 0, true);
        assertEquals(0, step.speed(), 1e-9);
    }

    @Test void reverseChangesSteeringDirectionAndStopPreventsDrift() {
        GoKartMotion forward = new GoKartMotion(0), reverse = new GoKartMotion(0);
        assertTrue(forward.tick(1, 1, false).yawDegrees() > 0);
        assertTrue(reverse.tick(-1, 1, false).yawDegrees() < 0);
        forward.stop();
        assertEquals(0, forward.tick(0, 0, false).speed());
    }

    @Test void emptyTankCannotAccelerateAndRefuelIsBounded() {
        GoKartMotion motion = new GoKartMotion(0);
        for (int i = 0; i < 25001; i++) motion.tick(1, 0, false);
        motion.stop();
        assertEquals(0, motion.tick(1, 0, false).speed());
        assertThrows(IllegalArgumentException.class, () -> motion.refuel(Double.NaN));
        motion.refuel(1000);
        assertTrue(motion.tick(1, 0, false).speed() > 0);
    }
}
