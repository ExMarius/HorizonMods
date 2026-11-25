package com.mrcrayfish.vehicle.paper.runtime;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class DiscHarrowWorkPathTest {
    @Test void sweepsFullWidthWithoutDuplicates() {
        var cells=DiscHarrowWorkPath.sample(0,0,0,.8,0);
        assertTrue(cells.contains(new DiscHarrowWorkPath.Cell(-2,0)));
        assertTrue(cells.contains(new DiscHarrowWorkPath.Cell(1,0)));
        assertEquals(cells.size(),new java.util.HashSet<>(cells).size());
    }
    @Test void headingAndNegativeCoordinates() {
        var cells=DiscHarrowWorkPath.sample(-.1,-.1,-.8,-.1,90);
        assertTrue(cells.contains(new DiscHarrowWorkPath.Cell(-1,-2)));
        assertTrue(cells.contains(new DiscHarrowWorkPath.Cell(-1,1)));
    }
    @Test void rejectStoppedReverseTeleportsAndNonFinitePositions() {
        assertTrue(DiscHarrowWorkPath.sample(0,0,0,0,0).isEmpty());
        assertTrue(DiscHarrowWorkPath.sample(0,0,0,-.1,0).isEmpty());
        assertTrue(DiscHarrowWorkPath.sample(0,0,0,1.01,0).isEmpty());
        assertTrue(DiscHarrowWorkPath.sample(0,0,Double.NaN,1,0).isEmpty());
        assertTrue(DiscHarrowWorkPath.sample(0,0,0,.1,Float.NaN).isEmpty());
    }
}
