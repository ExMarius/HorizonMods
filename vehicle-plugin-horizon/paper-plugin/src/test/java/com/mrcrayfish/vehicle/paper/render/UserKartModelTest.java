package com.mrcrayfish.vehicle.paper.render;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
class UserKartModelTest {
    @Test void editedFinPivotsMatchUserModel() {
        var g=HorizonGroups.GO_KART_BODY;
        assertEquals(26.9F,g.get(3).z(),1e-5F);
        assertEquals(26.9F,g.get(4).z(),1e-5F);
        assertEquals(28F,g.get(6).z(),1e-5F);
        assertEquals(28F,g.get(7).z(),1e-5F);
        assertEquals(20F,g.get(3).degrees(),1e-5F);
        assertEquals(-20F,g.get(4).degrees(),1e-5F);
        assertEquals(18F,g.get(6).degrees(),1e-5F);
        assertEquals(-18F,g.get(7).degrees(),1e-5F);
    }
}
