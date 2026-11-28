package com.mrcrayfish.vehicle.paper.recovery;

import com.mrcrayfish.vehicle.paper.vehicle.LandVehicleSpec;
import java.util.Set;

/** Small and medium road vehicles supported by the common recovery deck pose.
 * The pose is shared and is not a model-specific fit or collision guarantee. */
public final class RecoveryTargetPolicy {
    private static final Set<String> ALLOWED=Set.of(
            "go_kart", "horizon_go_kart", "quad_bike", "dune_buggy",
            "off_roader", "horizon_off_roader", "dacia_logan_police", "bmw_m6",
            "sports_car", "golf_cart", "atv", "mini_bike", "smart_car",
            "dirt_bike", "moped", "bumper_car");
    private RecoveryTargetPolicy() { }
    public static boolean supports(LandVehicleSpec spec) {
        return spec!=null && spec.motionType()==LandVehicleSpec.MotionType.LAND && ALLOWED.contains(spec.id());
    }
}
