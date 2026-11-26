package com.mrcrayfish.vehicle.paper.render;

import com.mrcrayfish.vehicle.paper.recovery.RecoveryTruckPrototype;
import com.mrcrayfish.vehicle.paper.vehicle.LandVehicleSpec;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class RecoveryTruckPrototypeTest {
    @Test void isolatedPrototypeHasCorrectModelsPivotsAndIsNotSpawnable() {
        var spec=RecoveryTruckPrototype.create();
        assertNull(LandVehicleSpec.byId(spec.id()),"must not enter public catalog before safety integration");
        assertEquals("horizon_service_cab",spec.bodyModel());
        assertEquals(4F,spec.bodyScale());
        assertEquals(new LandVehicleSpec.Point(0,0,0),spec.bodyOrigin());
        assertEquals(4,spec.wheels().size());
        assertEquals("horizon_service_wheel",LandVehicleRig.wheelModelFor(spec,spec.firstFrontWheel(),"standard_wheel"));
        assertEquals("horizon_service_wheel",LandVehicleRig.wheelModelFor(spec,spec.firstRearWheel(),"standard_wheel"));
        assertEquals(2,spec.seats().size());
        assertEquals(2,spec.bodyParts().stream().filter(p->p.model().equals("horizon_service_ramp")).count());
        for(var ramp:spec.bodyParts().stream().filter(p->p.model().equals("horizon_service_ramp")).toList()){
            assertEquals(.86F,ramp.center().y());assertEquals(-5.35F,ramp.center().z());
            assertEquals(4F,ramp.scale());assertEquals(90F,ramp.rotationX());
        }
        assertFalse(spec.canTowTrailers());
    }
    @Test void closedRampGoesUpFromTheHingeAfterItemYawCompensation(){
        var rotation=new org.joml.Quaternionf().rotateX((float)Math.toRadians(90)).rotateY((float)Math.PI);
        var tip=rotation.transform(new org.joml.Vector3f(0,0,2.48F));
        assertEquals(0F,tip.x,1e-5F);assertEquals(2.48F,tip.y,1e-5F);assertEquals(0F,tip.z,1e-5F);
    }
    @Test void existingWheelSelectionRemainsUnchanged(){
        assertEquals("standard_wheel",LandVehicleRig.wheelModelFor(LandVehicleSpec.TRACTOR,LandVehicleSpec.TRACTOR.firstFrontWheel(),"standard_wheel"));
    }
}
