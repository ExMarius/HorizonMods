package com.mrcrayfish.vehicle.paper.recovery;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
class RecoveryRampKinematicsTest {
    @Test void endsMatchGroundAndFoldedState(){
        double a=RecoveryRampKinematics.deployedAngle();
        assertEquals(0,RecoveryRampKinematics.DECK_HEIGHT-RecoveryRampKinematics.LENGTH*Math.sin(a)-RecoveryRampKinematics.HALF_THICKNESS*Math.cos(a),1e-10);
        assertEquals(0,RecoveryRampKinematics.paperOffsetRadians(0),1e-7);
        assertEquals(-Math.PI/2-a,RecoveryRampKinematics.paperOffsetRadians(1),1e-6);
        double last=0;
        for(int i=0;i<=1000;i++){
            double angle=RecoveryRampKinematics.paperOffsetRadians(i/1000.0);
            assertTrue(angle<=last+1e-7);last=angle;
        }
        assertThrows(IllegalArgumentException.class,()->RecoveryRampKinematics.paperOffsetRadians(Double.NaN));
        assertThrows(IllegalArgumentException.class,()->RecoveryRampKinematics.paperOffsetRadians(1.01));
    }
}
