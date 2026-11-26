package com.mrcrayfish.vehicle.paper.recovery;

import com.mrcrayfish.vehicle.paper.vehicle.LandVehicleSpec;
import java.util.List;

/**
 * Development-only bridge from the authored item models to the existing Paper
 * land-vehicle rig. Deliberately NOT in the public vehicle catalog: the platform
 * has no safe loading runtime yet. No commands or server deployment are enabled.
 * The preview's front -Z maps to Paper's source front +Z after item yaw correction.
 */
public final class RecoveryTruckPrototype {
    public static final String ID="horizon_recovery_prototype";
    public static final float MODEL_SCALE=4F;
    private RecoveryTruckPrototype() { }
    private static LandVehicleSpec.Point p(float x,float y,float z){return new LandVehicleSpec.Point(x,y,z);}
    private static LandVehicleSpec.Part part(String model, float x,float y,float z,float rx){
        return new LandVehicleSpec.Part(model,p(x,y,z),MODEL_SCALE,rx,0F,0F);
    }
    private static LandVehicleSpec.Wheel wheel(int side,boolean front,float x,float y,float z,float scale){
        return new LandVehicleSpec.Wheel(side,front,x,y,z,0F,0F,scale,scale,scale);
    }
    /** These physics numbers are provisional; not a promise of roadworthiness. */
    public static LandVehicleSpec create() {
        return new LandVehicleSpec(
                ID,"Platformă auto (prototip)","horizon_service_cab",
                2.9F,2.5F,1.0F,
                MODEL_SCALE,0F,0F,
                8F,28F,1.56F,-3.92F,3F,
                15_000F,.3F,.7F,1.4F,"vehicle:entity.tractor.engine",
                false,p(0,0,0),null,null,null,null,
                List.of(
                        part("horizon_service_flatbed",0,0,0,0),
                        part("horizon_service_steering",0,0,0,0),
                        // Closed position, pivoted at the independently authored hinges.
                        part("horizon_service_ramp",-1.05F,.86F,-5.35F,90F),
                        part("horizon_service_ramp",1.05F,.86F,-5.35F,90F)),
                List.of(
                        wheel(-1,true,-1.02F,.45F,1.56F,MODEL_SCALE),
                        wheel(1,true,1.02F,.45F,1.56F,MODEL_SCALE),
                        wheel(-1,false,-1.20F,.35F,-3.92F,MODEL_SCALE*.35F/.45F),
                        wheel(1,false,1.20F,.35F,-3.92F,MODEL_SCALE*.35F/.45F)),
                List.of(new LandVehicleSpec.Seat(true,p(.43F,.70F,.94F),0F),
                        new LandVehicleSpec.Seat(false,p(-.43F,.70F,.94F),0F)),
                false,"tow_bar",p(0,0,0),p(0,0,0),null,null,List.of(),false);
    }
}
