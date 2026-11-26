package com.mrcrayfish.vehicle.paper.recovery;

import org.bukkit.util.BoundingBox;
import org.bukkit.util.Vector;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class RecoveryCableWorldCheckTest {
    @Test void detectsCrossingTouchingContainedAndParallelCases() {
        var box=new BoundingBox(0,0,0,1,1,1);
        assertTrue(RecoveryCableWorldCheck.intersects(new Vector(-1,.5,.5),new Vector(2,.5,.5),box));
        assertTrue(RecoveryCableWorldCheck.intersects(new Vector(-1,1,.5),new Vector(2,1,.5),box));
        assertTrue(RecoveryCableWorldCheck.intersects(new Vector(.5,.5,.5),new Vector(.6,.5,.5),box));
        assertFalse(RecoveryCableWorldCheck.intersects(new Vector(-1,1.01,.5),new Vector(2,1.01,.5),box));
        assertFalse(RecoveryCableWorldCheck.intersects(new Vector(-2,.5,.5),new Vector(-1,.5,.5),box));
        assertFalse(RecoveryCableWorldCheck.intersects(new Vector(.5,-1,2),new Vector(.5,2,2),box));
    }
}
