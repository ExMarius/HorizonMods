package com.mrcrayfish.vehicle.paper.runtime;

/** Pure hitch/axle kinematics for the GD-3.2 prototype. Caller must apply
 * collision resolution and synchronize the resulting render state. */
final class DiscHarrowKinematics {
    static final double AXLE_FORWARD = 1.0 / 16.0;
    static final double AXLE_Y = 5.5 / 16.0;
    static final double HORIZONTAL_LENGTH = 35.0 / 16.0;
    static final double EYE_DELTA_Y = 5.0 / 16.0;
    static final double DRAWBAR_LENGTH = Math.hypot(HORIZONTAL_LENGTH, EYE_DELTA_Y);
    private DiscHarrowKinematics() {}

    static Result solve(double x, double z, float yaw, double groundY,
                        double hitchX, double hitchY, double hitchZ) {
        double dy = Math.max(-DRAWBAR_LENGTH * .96, Math.min(DRAWBAR_LENGTH * .96,
                hitchY - groundY - AXLE_Y));
        double horizontal = Math.sqrt(DRAWBAR_LENGTH * DRAWBAR_LENGTH - dy * dy);
        double previous = Math.toRadians(yaw);
        double axleX = x - Math.sin(previous) * AXLE_FORWARD;
        double axleZ = z + Math.cos(previous) * AXLE_FORWARD;
        double dx = hitchX - axleX, dz = hitchZ - axleZ;
        float next = Math.hypot(dx, dz) < 1e-8 ? yaw : (float) Math.toDegrees(Math.atan2(-dx,dz));
        double heading = Math.toRadians(next);
        double pitch = Math.asin(dy / DRAWBAR_LENGTH) - Math.atan2(EYE_DELTA_Y,HORIZONTAL_LENGTH);
        return new Result(hitchX + Math.sin(heading) * (horizontal + AXLE_FORWARD),
                hitchZ - Math.cos(heading) * (horizontal + AXLE_FORWARD),
                next,(float)Math.toDegrees(pitch));
    }
    record Result(double x, double z, float yaw, float pitch) {}
}
