package com.mrcrayfish.vehicle.paper.runtime;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class DrawbarPitchTest {
    @Test void levelClimbAndDescentReachThePin() {
        for(double height : new double[]{0,1,-1,0.5,-0.5}) {
            var r=DrawbarPitch.solve(0,DrawbarPitch.EYE_Y+height);
            double angle=Math.toRadians(r.pitchDegrees());
            double forward=FarmTrailerKinematics.EYE*Math.cos(angle)-DrawbarPitch.EYE_DY*Math.sin(angle);
            double vertical=FarmTrailerKinematics.EYE*Math.sin(angle)+DrawbarPitch.EYE_DY*Math.cos(angle);
            assertEquals(r.horizontal(),forward,1.0E-6);
            assertEquals(DrawbarPitch.EYE_Y+height,DrawbarPitch.PIVOT_Y+vertical,1.0E-6);
        }
        assertEquals(0,DrawbarPitch.solve(0,DrawbarPitch.EYE_Y).pitchDegrees(),1.0E-6);
        assertTrue(DrawbarPitch.solve(0,DrawbarPitch.EYE_Y+1).pitchDegrees()>0);
        assertTrue(DrawbarPitch.solve(0,DrawbarPitch.EYE_Y-1).pitchDegrees()<0);
    }
    @Test void extremeHeightIsClampedAndFinite() {
        var r=DrawbarPitch.solve(0,100);
        assertTrue(Double.isFinite(r.horizontal()));assertTrue(Float.isFinite(r.pitchDegrees()));
        assertTrue(r.horizontal()>0);
    }
    @Test void projectedEyeStillMeetsHitchInTurn() {
        var pitch=DrawbarPitch.solve(0,DrawbarPitch.EYE_Y+1);
        var r=FarmTrailerKinematics.solve(0,0,0,0.7,3.0,pitch.horizontal());
        double body=Math.toRadians(r.yaw()), front=Math.toRadians(r.yaw()+r.steering());
        assertEquals(0.7,r.x()-Math.sin(body)*FarmTrailerKinematics.AXLE-Math.sin(front)*pitch.horizontal(),1e-6);
        assertEquals(3.0,r.z()+Math.cos(body)*FarmTrailerKinematics.AXLE+Math.cos(front)*pitch.horizontal(),1e-6);
    }
}
