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
    @Test void wholeRigidFramePitchesAroundAxleAndEyeReachesHitch() {
        for (double height : new double[]{10.5/16.0 - 1,10.5/16.0,10.5/16.0 + 1}) {
            var r=DiscHarrowKinematics.solve(0,0,0,0,0,height,2.2);
            double pitch=Math.toRadians(r.pitch());
            double vertical=DiscHarrowKinematics.AXLE_Y
                    +DiscHarrowKinematics.HORIZONTAL_LENGTH*Math.sin(pitch)
                    +DiscHarrowKinematics.EYE_DELTA_Y*Math.cos(pitch);
            double horizontal=DiscHarrowKinematics.HORIZONTAL_LENGTH*Math.cos(pitch)
                    -DiscHarrowKinematics.EYE_DELTA_Y*Math.sin(pitch);
            assertEquals(height,vertical,1e-6);
            assertEquals(2.2,r.z()+DiscHarrowKinematics.AXLE_FORWARD+horizontal,1e-6);
            if(height>10.5/16.0) assertTrue(r.pitch()>0);
            if(height<10.5/16.0) assertTrue(r.pitch()<0);
        }
    }
    @Test void transportAndWorkEyeStayOnPinThroughLift() {
        for (double work : new double[]{0, .25, .5, .75, 1}) {
            double hitchY=10.5/16.0;
            var r=DiscHarrowKinematics.solve(0,0,0,0,0,hitchY,2.2,work);
            assertTrue(r.reachable());
            double pitch=Math.toRadians(r.pitch());
            double eyeHeight=DiscHarrowKinematics.EYE_DELTA_Y+4.5/16.0*(1-work);
            assertEquals(hitchY,DiscHarrowKinematics.AXLE_Y
                    +DiscHarrowKinematics.HORIZONTAL_LENGTH*Math.sin(pitch)
                    +eyeHeight*Math.cos(pitch),1e-6);
            double horizontal=DiscHarrowKinematics.HORIZONTAL_LENGTH*Math.cos(pitch)-eyeHeight*Math.sin(pitch);
            assertEquals(2.2,r.z()+DiscHarrowKinematics.AXLE_FORWARD+horizontal,1e-6);
        }
    }
    @Test void hitchIsReachedAfterCollisionOffsetAndLiftAtManyHeadings() {
        for (float yaw : new float[]{0, 45, 90, -90, 180}) {
            for (double work : new double[]{0, .5, 1}) for (double deltaY : new double[]{-1, 0, 1}) {
                double a=Math.toRadians(yaw);
                double hx=4-Math.sin(a)*2.1, hz=-7+Math.cos(a)*2.1;
                double hy=10.5/16.0+deltaY;
                var r=DiscHarrowKinematics.solve(4.1,-7.08,yaw,0,hx,hy,hz,work);
                assertTrue(r.reachable());
                double pitch=Math.toRadians(r.pitch());
                double eyeHeight=DiscHarrowKinematics.EYE_DELTA_Y+4.5/16.0*(1-work);
                double horizontal=DiscHarrowKinematics.AXLE_FORWARD
                        +DiscHarrowKinematics.HORIZONTAL_LENGTH*Math.cos(pitch)-eyeHeight*Math.sin(pitch);
                double heading=Math.toRadians(r.yaw());
                assertEquals(hx,r.x()-Math.sin(heading)*horizontal,1e-6);
                assertEquals(hz,r.z()+Math.cos(heading)*horizontal,1e-6);
                assertEquals(hy,DiscHarrowKinematics.AXLE_Y
                        +DiscHarrowKinematics.HORIZONTAL_LENGTH*Math.sin(pitch)+eyeHeight*Math.cos(pitch),1e-6);
            }
        }
    }
    @Test void impossibleClimbIsLimitedAndFinite() {
        var r=DiscHarrowKinematics.solve(0,0,0,0,1,100,2);
        assertTrue(Double.isFinite(r.x())&&Double.isFinite(r.z()));assertTrue(Float.isFinite(r.pitch()));
        assertFalse(r.reachable());
    }
}
