package com.mrcrayfish.vehicle.paper.runtime;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class FarmTrailerKinematicsTest {
    @Test void eyeMeetsHitchStraightAndInTurns() {
        for (double[] c : new double[][]{{0,0,0,0,3.335},{1,-2,0,1,1.335},{0,0,0,2,3},{-2,1,85,-5,1}}) {
            var result = FarmTrailerKinematics.solve(c[0],c[1],(float)c[2],c[3],c[4],(float)(c[2]+25));
            double body=Math.toRadians(result.yaw()),front=Math.toRadians(result.yaw()+result.steering());
            assertEquals(c[3],result.x()-Math.sin(body)*FarmTrailerKinematics.AXLE-Math.sin(front)*FarmTrailerKinematics.EYE,1e-8);
            assertEquals(c[4],result.z()+Math.cos(body)*FarmTrailerKinematics.AXLE+Math.cos(front)*FarmTrailerKinematics.EYE,1e-8);
            assertTrue(Math.abs(result.steering())<=70.0);
        }
    }
    @Test void changesHeadingSmoothly() {
        var r=FarmTrailerKinematics.solve(0,0,0,3,3,30);
        assertTrue(Math.abs(r.yaw())<=5.0);
        assertTrue(Math.abs(r.steering())>1.0);
    }
    @Test void frontAxleAndBodyRespondToGentleTurnWithoutCollision() {
        double x=0,z=0,hx=0,hz=FarmTrailerKinematics.AXLE+FarmTrailerKinematics.EYE;
        float yaw=0, firstTurnYaw=0;
        for (int tick=1; tick<=30; tick++) {
            float tractorYaw=tick;
            hx-=Math.sin(Math.toRadians(tractorYaw))*0.08;
            hz+=Math.cos(Math.toRadians(tractorYaw))*0.08;
            var r=FarmTrailerKinematics.solve(x,z,yaw,hx,hz,tractorYaw);
            assertTrue(Math.abs(r.yaw()-yaw)<=5.001F);
            if(tick==10) firstTurnYaw=r.yaw();
            x=r.x();z=r.z();yaw=r.yaw();
        }
        assertTrue(firstTurnYaw>0.5F,"body must start following the curve before hitting an obstacle");
        assertTrue(yaw>firstTurnYaw,"body should continue turning smoothly");
    }
}
