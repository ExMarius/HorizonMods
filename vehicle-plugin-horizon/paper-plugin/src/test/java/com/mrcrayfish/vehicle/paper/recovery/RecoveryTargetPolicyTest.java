package com.mrcrayfish.vehicle.paper.recovery;

import com.mrcrayfish.vehicle.paper.vehicle.LandVehicleSpec;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class RecoveryTargetPolicyTest {
    @Test void admitsSmallAndMediumVehiclesButNotPlatformOrHeavyOrWatercraft() {
        for(String id : new String[]{"go_kart","horizon_go_kart","quad_bike","dune_buggy",
                "off_roader","horizon_off_roader","dacia_logan_police","bmw_m6","sports_car","atv","smart_car"}) {
            assertTrue(RecoveryTargetPolicy.supports(LandVehicleSpec.byId(id)),id);
        }
        for(String id : new String[]{"horizon_recovery_prototype","tractor","utb_650","mini_bus",
                "sports_plane","compact_helicopter","speed_boat","jet_ski"}) {
            assertFalse(RecoveryTargetPolicy.supports(LandVehicleSpec.byId(id)),id);
        }
        assertFalse(RecoveryTargetPolicy.supports(null));
    }
}
