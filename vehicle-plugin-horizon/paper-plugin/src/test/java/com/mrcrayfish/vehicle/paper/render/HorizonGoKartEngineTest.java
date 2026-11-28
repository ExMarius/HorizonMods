package com.mrcrayfish.vehicle.paper.render;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
class HorizonGoKartEngineTest {
    @Test void vibrationUsesSourceIdleAndMovingAmplitudesOnlyWhenRunning() {
        for (int tick=0; tick<100; tick++) {
            assertEquals(0F,HorizonGoKartRig.engineVibration(tick,false,false));
            assertEquals(0F,HorizonGoKartRig.engineVibration(tick,false,true));
            assertEquals((float)Math.sin(tick*.7F)*.0015F,HorizonGoKartRig.engineVibration(tick,true,false),1e-7F);
            assertEquals((float)Math.sin(tick*1.85F)*.004F,HorizonGoKartRig.engineVibration(tick,true,true),1e-7F);
        }
    }
}
