package com.mrcrayfish.vehicle.paper.render;

import org.bukkit.util.Transformation;
import org.joml.Quaternionf;
import org.joml.Vector3f;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class HorizonGoKartNoseTest {
    @Test void finsAreTheOnlyMovedGroupsAndOriginAccountsForItemYaw() {
        for (var group : HorizonGroups.GO_KART_BODY) {
            boolean expected = group.name().endsWith("_03") || group.name().endsWith("_04")
                    || group.name().endsWith("_06") || group.name().endsWith("_07");
            assertEquals(expected, HorizonGoKartRig.isNoseFin(group.name()));
            if (!expected) continue;
            Vector3f origin=group.origin(), corrected=HorizonGoKartRig.noseFinOrigin(origin);
            assertEquals(16-origin.x, corrected.x, 0.00001F);
            assertEquals(origin.y, corrected.y, 0.00001F);
            assertEquals(16-origin.z, corrected.z, 0.00001F);
        }
        assertEquals(2F * 1.18F / 16F, HorizonGoKartRig.NOSE_FIN_FORWARD, 0.00001F);
    }

    @Test void finBoundsClearConservativeWheelSweepOnBothSides() {
        // Original source cuboids (17,18,20,21), transformed by the actual
        // split model and item yaw, including the two-pixel nose adjustment.
        int[] idx={3,4,6,7};
        float[][] bounds={{14.8F,20.2F,25F,26.8F},{-4.2F,1.2F,25F,26.8F},
                {13.8F,20.2F,24.6F,27.6F},{-4.2F,2.2F,24.6F,27.6F}};
        float bodyScale=1.18F;
        float rearAxle=-11.4F*bodyScale/16F;
        // Bounding rectangle includes the wider rear tire at max 25 degree yaw.
        float radius=(4F*1.28F*(float)Math.cos(Math.toRadians(25))
                + 2.4F*1.34F*(float)Math.sin(Math.toRadians(25)))/16F;
        float safeZ=rearAxle-radius;
        for (int i=0;i<idx.length;i++) {
            var group=HorizonGroups.GO_KART_BODY.get(idx[i]);
            var center=new Vector3f(0,.57F,-HorizonGoKartRig.NOSE_FIN_FORWARD);
            var t=HorizonPartTransform.group(center,new Vector3f(bodyScale,1.14F,bodyScale),
                    HorizonGoKartRig.noseFinOrigin(group.origin()),group.rotation(),new Quaternionf());
            var right=new Quaternionf(t.getRightRotation()).rotateY((float)Math.PI);
            for(float x:new float[]{bounds[i][0],bounds[i][1]}) for(float z:new float[]{bounds[i][2],bounds[i][3]}) {
                var point=new Vector3f((x-8)/16F,0,(z-8)/16F);
                right.transform(point);point.mul(t.getScale());t.getLeftRotation().transform(point);point.add(t.getTranslation());
                assertTrue(point.z < safeZ, group.name()+" z="+point.z+" safety boundary="+safeZ);
            }
        }
    }
}
