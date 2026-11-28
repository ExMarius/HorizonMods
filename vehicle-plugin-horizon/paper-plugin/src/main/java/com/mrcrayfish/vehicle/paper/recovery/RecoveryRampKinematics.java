package com.mrcrayfish.vehicle.paper.recovery;

/** Visual-only hinged ramp math for the isolated truck prototype, not gameplay. */
public final class RecoveryRampKinematics {
    public static final double DECK_HEIGHT=.86, LENGTH=2.48, HALF_THICKNESS=.05;
    private RecoveryRampKinematics() { }
    public static double deployedAngle(){
        return Math.asin(DECK_HEIGHT/Math.hypot(LENGTH,HALF_THICKNESS))-Math.atan2(HALF_THICKNESS,LENGTH);
    }
    /** Relative to the authored +90° folded Paper display. */
    public static float paperOffsetRadians(double progress){
        if(!Double.isFinite(progress)||progress<0||progress>1)throw new IllegalArgumentException("Invalid ramp progress");
        double eased=progress*progress*(3-2*progress);
        return (float)(-(Math.PI/2+deployedAngle())*eased);
    }
}
