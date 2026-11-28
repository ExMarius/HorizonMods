package com.mrcrayfish.vehicle.paper.recovery;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import static com.mrcrayfish.vehicle.paper.recovery.RecoveryLoadingPath.*;

class RecoveryLoadingPathTest {
    @Test void surfaceIsContinuousAndSlopeIsMonotonic() {
        assertEquals(.86, surfaceHeight(RecoveryEnvelope.DECK_END), 1e-12);
        assertEquals(0, surfaceHeight(RAMP_END), 1e-12);
        assertEquals(.43, surfaceHeight((RecoveryEnvelope.DECK_END + RAMP_END) / 2), 1e-12);
        double previous = .86;
        for (int i = 0; i <= 1000; i++) {
            double h = surfaceHeight(RecoveryEnvelope.DECK_END + RAMP_RUN * i / 1000);
            assertTrue(h <= previous + 1e-12 && h >= 0);
            previous = h;
        }
    }

    @Test void loadingAndUnloadingAreTheSamePathInReverse() {
        for (int i = 0; i <= 100; i++) {
            double t = i / 100.0;
            Pose loading = sample(9.8, 2.64, 3.3, t);
            Pose unloading = sample(2.64, 9.8, 3.3, 1 - t);
            assertEquals(loading.centerZ(), unloading.centerZ(), 1e-12);
            assertEquals(loading.height(), unloading.height(), 1e-12);
            assertEquals(loading.pitch(), unloading.pitch(), 1e-12);
            assertTrue(loading.height() >= 0 && loading.height() <= .86);
            assertTrue(loading.pitch() >= 0);
        }
        assertEquals(0, pose(9.8, 3.3).height(), 1e-12);
        assertEquals(.86, pose(2.64, 3.3).height(), 1e-12);
        assertEquals(0, pose(2.64, 3.3).pitch(), 1e-12);
    }

    @Test void invalidSamplesFailClosed() {
        assertThrows(IllegalArgumentException.class, () -> pose(1, 0));
        assertThrows(IllegalArgumentException.class, () -> pose(1, Double.NaN));
        assertThrows(IllegalArgumentException.class, () -> pose(Double.MAX_VALUE, Double.MAX_VALUE));
        assertThrows(IllegalArgumentException.class, () -> surfaceHeight(Double.NaN));
        assertThrows(IllegalArgumentException.class, () -> sample(1, 2, 3, -0.1));
        assertThrows(IllegalArgumentException.class, () -> sample(1, 2, 3, Double.NaN));
    }
}
