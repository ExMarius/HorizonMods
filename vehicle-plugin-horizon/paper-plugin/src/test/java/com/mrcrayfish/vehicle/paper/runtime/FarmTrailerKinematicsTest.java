package com.mrcrayfish.vehicle.paper.runtime;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class FarmTrailerKinematicsTest {
    private static final double TOL = 2.0E-6;

    @Test void eyeMeetsHitchEvenInSharpTurns() {
        for (double[] c : new double[][]{{0,0,0,0,3.335},{1,-2,0,1,1.335},{0,0,0,2,3},{-2,1,85,-5,1}}) {
            var r = FarmTrailerKinematics.solve(c[0],c[1],(float)c[2],c[3],c[4]);
            assertEye(r,c[3],c[4]);
        }
    }
    @Test void stationaryHitchKeepsTrailerStill() {
        var r=FarmTrailerKinematics.solve(0,0,0,0,3.335);
        assertEquals(0,r.x(),TOL); assertEquals(0,r.z(),TOL);
        assertEquals(0,r.yaw(),TOL); assertEquals(0,r.steering(),TOL);
    }
    @Test void sharpPullAndSidewaysDriftFollowHitchWithoutSidewaysRearAxleSlip() {
        double x=0,z=0,hx=0,hz=FarmTrailerKinematics.AXLE+FarmTrailerKinematics.EYE;
        float yaw=0, firstSteering=0, lastYaw=0;
        for (int tick=0;tick<90;tick++) {
            // Straight, then move the hitch sideways (skidding tractor), then
            // turn sharply: only the hitch trajectory matters, never tractor yaw.
            if (tick<20) hz+=0.08;
            else if (tick<45) { hx+=0.075; hz+=0.025; }
            else { hx+=0.02; hz-=0.075; }
            double oldYaw=Math.toRadians(yaw);
            double oldRearX=x+Math.sin(oldYaw)*FarmTrailerKinematics.REAR_AXLE;
            double oldRearZ=z-Math.cos(oldYaw)*FarmTrailerKinematics.REAR_AXLE;
            var r=FarmTrailerKinematics.solve(x,z,yaw,hx,hz);
            assertEye(r,hx,hz);
            double newYaw=Math.toRadians(r.yaw());
            double rearX=r.x()+Math.sin(newYaw)*FarmTrailerKinematics.REAR_AXLE;
            double rearZ=r.z()-Math.cos(newYaw)*FarmTrailerKinematics.REAR_AXLE;
            double lateral=(rearX-oldRearX)*Math.cos(newYaw)+(rearZ-oldRearZ)*Math.sin(newYaw);
            assertEquals(0,lateral,TOL,"rear axle must not slide sideways on clear ground");
            if(tick==23)firstSteering=r.steering();
            x=r.x();z=r.z();lastYaw=yaw;yaw=r.yaw();
            assertTrue(Double.isFinite(x) && Double.isFinite(z));
        }
        assertTrue(Math.abs(firstSteering)>1,"front axle should pivot when pulled sideways");
        assertTrue(Math.abs(yaw)>2,"the body must follow the changing path");
        assertTrue(Math.abs(yaw-lastYaw)<30,"successive small hitch movements must not cause a sudden spin");
    }
    private static void assertEye(FarmTrailerKinematics.Result r,double hx,double hz) {
        double body=Math.toRadians(r.yaw()),front=Math.toRadians(r.yaw()+r.steering());
        assertEquals(hx,r.x()-Math.sin(body)*FarmTrailerKinematics.AXLE-Math.sin(front)*FarmTrailerKinematics.EYE,TOL);
        assertEquals(hz,r.z()+Math.cos(body)*FarmTrailerKinematics.AXLE+Math.cos(front)*FarmTrailerKinematics.EYE,TOL);
    }
}
