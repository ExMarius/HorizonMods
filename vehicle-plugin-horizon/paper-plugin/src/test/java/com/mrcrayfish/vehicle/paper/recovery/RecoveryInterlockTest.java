package com.mrcrayfish.vehicle.paper.recovery;

import org.junit.jupiter.api.Test;
import java.util.UUID;
import static org.junit.jupiter.api.Assertions.*;
import static com.mrcrayfish.vehicle.paper.recovery.RecoveryInterlock.*;

class RecoveryInterlockTest {
    private static final UUID CARRIER=UUID.randomUUID(), TARGET=UUID.randomUUID(), OPERATOR=UUID.randomUUID();
    // Independent switches keep it easy to exercise missing and bad information.
    private static Safety safety(boolean... bad) {
        boolean[] v = new boolean[20]; java.util.Arrays.fill(v,true);
        // cable is absent until explicitly requested.
        v[14]=false; v[17]=false; v[18]=false; v[19]=false;
        for(int i=0;i<bad.length;i++)if(bad[i])v[i]=!v[i];
        return new Safety(v[0],v[1],v[2],v[3],v[4],v[5],v[6],v[7],v[8],v[9],v[10],v[11],v[12],v[13],v[14],v[15],v[16],v[17],v[18],v[19]);
    }
    private static Safety flip(int... indexes){boolean[] bad=new boolean[20];for(int i:indexes)bad[i]=true;return safety(bad);}
    private static void opened(RecoveryInterlock m, Mode mode){assertEquals(Denial.NONE,m.openRamps(CARRIER,TARGET,OPERATOR,mode,safety()));assertEquals(Denial.NONE,m.rampsReady(safety()));}
    @Test void rejectsUnknownSafetyConditionsAndCoupledVehicles(){
        Denial[] expected={Denial.MISSING_ENTITY,Denial.UNAUTHORIZED,Denial.PROTECTION_UNAVAILABLE,Denial.PROHIBITED_AREA,
            Denial.TRUCK_MOVING,Denial.UNKNOWN_COUPLING,Denial.TRAILER_ATTACHED,Denial.ALREADY_TRANSPORTED,
            Denial.UNKNOWN_GEOMETRY,Denial.DOES_NOT_FIT,Denial.PATH_UNCHECKED,Denial.PATH_BLOCKED};
        for(int i=0;i<expected.length;i++){var s=new RecoveryInterlock();assertEquals(expected[i],s.openRamps(CARRIER,TARGET,OPERATOR,Mode.WINCH,flip(i)));assertEquals(Phase.IDLE,s.phase());}
        var s=new RecoveryInterlock();assertEquals(Denial.MISSING_ENTITY,s.openRamps(CARRIER,CARRIER,OPERATOR,Mode.WINCH,safety()));
        assertEquals(Denial.WRONG_OCCUPANTS,s.openRamps(CARRIER,TARGET,OPERATOR,Mode.WINCH,flip(13)));
    }
    @Test void winchRequiresEmptyTargetCableAndDeployedRamps(){
        var s=new RecoveryInterlock();opened(s,Mode.WINCH);
        assertEquals(Denial.CABLE_NOT_ATTACHED,s.startMovement(safety()));
        assertEquals(Denial.RAMPS_NOT_OPEN,s.startMovement(flip(14,16)));
        assertEquals(Denial.NONE,s.startMovement(flip(14)));
        assertFalse(s.mayDriveCarrier(null));
        assertEquals(Denial.TRAILER_ATTACHED,s.checkMovement(flip(6,14)));
        assertEquals(Phase.PAUSED,s.phase());
        assertEquals(Denial.INVALID_PHASE,s.checkMovement(flip(14)));
        assertEquals(Denial.NONE,s.resume(flip(14)));
    }
    @Test void drivenRequiresAuthorizedDriverAndCannotLoadWithCable(){
        var s=new RecoveryInterlock();opened(s,Mode.DRIVEN);
        assertEquals(Denial.WRONG_OCCUPANTS,s.startMovement(flip(12)));
        assertEquals(Denial.CABLE_STILL_ATTACHED,s.startMovement(flip(14)));
        assertEquals(Denial.NONE,s.startMovement(safety()));
        assertEquals(Denial.PATH_BLOCKED,s.checkMovement(flip(11)));
        assertEquals(Denial.PATH_UNCHECKED,s.resume(flip(10)));
        assertEquals(Phase.PAUSED,s.phase());
        assertEquals(Denial.NONE,s.resume(safety()));
    }
    @Test void securingRequiresEmptyCenteredDetachedClosedAndStrapped(){
        var s=new RecoveryInterlock();opened(s,Mode.WINCH);assertEquals(Denial.NONE,s.startMovement(flip(14)));
        assertEquals(Denial.NOT_CENTERED,s.finishMovement(flip(14,15)));
        assertEquals(Denial.NONE,s.finishMovement(flip(14)));
        assertEquals(Denial.WRONG_OCCUPANTS,s.secure(flip(13,16,17,18)));
        assertEquals(Denial.CABLE_STILL_ATTACHED,s.secure(flip(14,16,17,18)));
        assertEquals(Denial.RAMPS_NOT_CLOSED,s.secure(flip(16,18)));
        assertEquals(Denial.NOT_SECURED,s.secure(flip(16,17)));
        assertEquals(Denial.NONE,s.secure(flip(16,17,18,19)));assertFalse(s.mayDriveCarrier(null)); assertTrue(s.mayDriveCarrier(flip(16,17,18,19)));
        assertFalse(s.mayDriveCarrier(flip(16,17,18)));
        assertEquals(Denial.INVALID_PHASE,s.resetIfEmptyAndSafe(true,true,true));
    }
    @Test void cannotEraseAnActiveVehicleOrGuessAtMissingState(){
        var s=new RecoveryInterlock();opened(s,Mode.DRIVEN);
        assertEquals(Denial.INVALID_PHASE,s.resetIfEmptyAndSafe(false,true,true));
        assertEquals(Denial.INVALID_PHASE,s.resetIfEmptyAndSafe(true,false,true));
        assertEquals(Denial.INVALID_PHASE,s.resetIfEmptyAndSafe(true,true,false));
        assertEquals(Denial.NONE,s.resetIfEmptyAndSafe(true,true,true));
        assertNull(s.target());assertTrue(s.mayDriveCarrier(null));
        assertEquals(Denial.MISSING_ENTITY,s.openRamps(CARRIER,TARGET,OPERATOR,Mode.DRIVEN,null));
    }
}
