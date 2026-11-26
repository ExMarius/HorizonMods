package com.mrcrayfish.vehicle.paper.recovery;
import org.junit.jupiter.api.Test;
import java.util.List;
import static org.junit.jupiter.api.Assertions.*;
import static com.mrcrayfish.vehicle.paper.recovery.RecoveryCable.*;
class RecoveryCableTest {
    private static final Point OUTLET=new Point(0,1.06,.18), ROLLER=new Point(0,.99,5.4);
    @Test void rollerSupportsOnlyWhenTheTautLineNeedsIt(){
        Point low=new Point(0,.35,7.37),high=new Point(0,1.4,6),shortLine=new Point(0,1.2,3);
        assertEquals(List.of(OUTLET,ROLLER,low),route(OUTLET,ROLLER,low));
        assertEquals(List.of(OUTLET,high),route(OUTLET,ROLLER,high));
        assertEquals(List.of(OUTLET,shortLine),route(OUTLET,ROLLER,shortLine));
    }
    @Test void validatesTheEntireLineAndRefusesPenetrationOrOverflow(){
        var good=route(OUTLET,ROLLER,new Point(0,.35,7.37));
        assertTrue(clearsLevelBed(good,.18,5.35,.86,.018));
        assertFalse(clearsLevelBed(route(OUTLET,ROLLER,new Point(0,.2,3)),.18,5.35,.86,.018));
        assertFalse(clearsLevelBed(List.of(OUTLET,new Point(0,1.1,1e100)),.18,5.35,.86,.018));
        assertFalse(clearsLevelBed(List.of(OUTLET,OUTLET),.18,5.35,.86,.018));
        assertFalse(clearsLevelBed(route(OUTLET,ROLLER,new Point(0,-.2,8)),.18,5.35,.86,.018));
        assertFalse(clearsLevelBed(null,.18,5.35,.86,.018));
    }
    @Test void rejectsMissingOrUnalignedGeometry(){
        assertThrows(IllegalArgumentException.class,()->new Point(Double.NaN,0,0));
        assertThrows(IllegalArgumentException.class,()->route(null,ROLLER,OUTLET));
        assertThrows(IllegalArgumentException.class,()->route(OUTLET,ROLLER,new Point(.01,1,6)));
        assertThrows(IllegalArgumentException.class,()->route(OUTLET,ROLLER,new Point(0,1,.1)));
        assertThrows(IllegalArgumentException.class,()->route(ROLLER,OUTLET,new Point(0,1,6)));
    }
}
