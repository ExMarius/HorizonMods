package com.mrcrayfish.vehicle.paper.runtime;

/** Vertical articulation about the front axle. The eye's position at level
 * ground is a little below the drawbar's pivot, as in the authored model. */
final class DrawbarPitch {
    static final double PIVOT_Y = 0.6D;
    static final double EYE_Y = 0.434375D;
    static final double EYE_DY = EYE_Y - PIVOT_Y;
    static final double LENGTH = Math.hypot(FarmTrailerKinematics.EYE, EYE_DY);
    private DrawbarPitch() {}

    static Result solve(double trailerGroundY, double hitchY) {
        double dy = Math.max(-LENGTH * 0.96D, Math.min(LENGTH * 0.96D,
                hitchY - trailerGroundY - PIVOT_Y));
        double angle = Math.asin(dy / LENGTH);
        double base = Math.atan2(EYE_DY, FarmTrailerKinematics.EYE);
        return new Result(LENGTH * Math.cos(angle), (float) Math.toDegrees(angle - base));
    }
    record Result(double horizontal, float pitchDegrees) {}
}
