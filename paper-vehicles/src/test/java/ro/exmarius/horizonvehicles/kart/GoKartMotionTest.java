package ro.exmarius.horizonvehicles.kart;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class GoKartMotionTest {
    private GoKartMotion.Step step(GoKartMotion m, int throttle, int steering, boolean brake) {
        return m.tick(throttle, steering, brake, true, .99, 1);
    }
    @Test void acceleratesBrakesAndBurnsFuel() {
        GoKartMotion motion = new GoKartMotion(0);
        GoKartMotion.Step state = null;
        for (int i = 0; i < 100; i++) state = step(motion, 1, 0, false);
        assertTrue(state.speed() > 0);
        assertTrue(state.speed() <= .9 + 1e-8);
        assertEquals(0, state.dx(), 1e-8);
        assertTrue(state.fuel() < GoKartMotion.CAPACITY);
        double before = state.speed();
        for (int i = 0; i < 30; i++) state = step(motion, 0, 0, true);
        assertTrue(state.speed() < before);
    }
    @Test void reversingTurnsOppositeAndStopPreventsDrift() {
        GoKartMotion f = new GoKartMotion(0), r = new GoKartMotion(0);
        GoKartMotion.Step fs = null, rs = null;
        for (int i = 0; i < 20; i++) { fs = step(f, 1, 1, false); rs = step(r, -1, 1, false); }
        assertTrue(fs.yawDegrees() * rs.yawDegrees() < 0);
        f.stop();
        assertEquals(0, step(f, 0, 0, false).speed(), 1e-8);
    }
    @Test void noEngineForceInAirAndRefuelIsBounded() {
        GoKartMotion motion = new GoKartMotion(0);
        assertEquals(0, motion.tick(1, 0, false, false, 0, 1).speed(), 1e-8);
        assertThrows(IllegalArgumentException.class, () -> motion.refuel(Double.NaN));
        motion.refuel(1000);
        assertTrue(step(motion, 1, 0, false).speed() > 0);
    }
}
