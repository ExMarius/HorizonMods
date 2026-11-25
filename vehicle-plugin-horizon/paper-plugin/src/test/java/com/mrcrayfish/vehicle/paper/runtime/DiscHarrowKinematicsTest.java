package com.mrcrayfish.vehicle.paper.runtime;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class DiscHarrowKinematicsTest {
    @Test void straightAndStoppedDoNotFollowTractorYaw() {
        double hitchZ=DiscHarrowKinematics.HORIZONTAL_LENGTH+DiscHarrowKinematics.AXLE_FORWARD;
        var r=DiscHarrowKinematics.solve(0,0,0,0,0,10.5/16.0,hitchZ);
        assertEquals(0,r.x(),1e-7);assertEquals(0,r.z(),1e-7);assertEquals(0,r.yaw(),1e-7);assertEquals(0,r.pitch(),1e-7);
    }
    @Test void pinStaysAtHitchAcrossOneBlockStepAndSidewaysPull() {
        for(double y:new double[]{10.5/16.0,10.5/16.0+1,10.5/16.0-1}){
            var r=DiscHarrowKinematics.solve(0,0,0,0,.4,y,2.2);
            double dy=y-DiscHarrowKinematics.AXLE_Y;
            double horizontal=Math.sqrt(DiscHarrowKinematics.DRAWBAR_LENGTH*DiscHarrowKinematics.DRAWBAR_LENGTH-dy*dy);
            double a=Math.toRadians(r.yaw());
            assertEquals(.4,r.x()-Math.sin(a)*(horizontal+DiscHarrowKinematics.AXLE_FORWARD),1e-6);
            assertEquals(2.2,r.z()+Math.cos(a)*(horizontal+DiscHarrowKinematics.AXLE_FORWARD),1e-6);
        }
    }
    @Test void impossibleClimbIsLimitedAndFinite() {
        var r=DiscHarrowKinematics.solve(0,0,0,0,1,100,2);
        assertTrue(Double.isFinite(r.x())&&Double.isFinite(r.z()));assertTrue(Float.isFinite(r.pitch()));
    }
}
