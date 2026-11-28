package com.mrcrayfish.vehicle.paper.runtime;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class DiscHarrowStateTest {
    @Test void uncoupledIsSafeAndHitchStartsInTransport() {
        var s = new DiscHarrowState();
        assertTrue(s.standDeployed()); assertFalse(s.setWorking(true, true));
        s.couple(); assertFalse(s.standDeployed()); assertFalse(s.workRequested());
        assertEquals(0.0, s.position());
    }
    @Test void loweringTakesTimeAndNeverWorksInReverseOrWhileStopped() {
        var s = new DiscHarrowState();s.couple();assertTrue(s.setWorking(true,true));
        for(int i=0;i<19;i++)s.tick(true);
        assertFalse(s.canWork(true,true,.1));
        s.tick(true);assertTrue(s.canWork(true,true,.1));
        assertFalse(s.canWork(true,true,0)); assertFalse(s.canWork(true,true,-.1));
        assertFalse(s.canWork(true,false,.1)); assertFalse(s.canWork(false,true,.1));
    }
    @Test void detachDisablesWorkImmediatelyAndRaisesTheImplement() {
        var s=new DiscHarrowState();s.couple();s.setWorking(true,true);
        for(int i=0;i<20;i++)s.tick(true);
        s.detach();assertTrue(s.standDeployed());assertFalse(s.canWork(true,true,.1));
        for(int i=0;i<20;i++)s.tick(false);
        assertEquals(0.0,s.position(),1e-9);s.couple();assertFalse(s.workRequested());
    }
    @Test void missingOrUnauthorizedDriverCancelsWork() {
        var s=new DiscHarrowState();s.couple();assertFalse(s.setWorking(true,false));
        s.setWorking(true,true);s.tick(true);s.tick(false);
        assertFalse(s.workRequested());assertFalse(s.canWork(true,true,.1));
    }
}
