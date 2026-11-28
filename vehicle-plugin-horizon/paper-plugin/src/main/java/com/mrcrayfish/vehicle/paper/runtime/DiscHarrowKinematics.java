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
        return solve(x, z, yaw, groundY, hitchX, hitchY, hitchZ, 1.0);
    }

    /** Work position 1 is level at the authored model origin; transport position
     * 0 raises the frame 4.5 pixels above the same axle. Empty means the pin
     * cannot be reached: callers must not silently render a disconnected eye. */
    static Result solve(double x, double z, float yaw, double groundY,
                        double hitchX, double hitchY, double hitchZ, double workPosition) {
        if (!Double.isFinite(workPosition) || workPosition < 0 || workPosition > 1)
            throw new IllegalArgumentException("workPosition must be in [0,1]");
        double eyeHeight = EYE_DELTA_Y + 4.5 / 16.0 * (1.0 - workPosition);
        double length = Math.hypot(HORIZONTAL_LENGTH, eyeHeight);
        double rawDy = hitchY - groundY - AXLE_Y;
        boolean reachable = Double.isFinite(rawDy) && Math.abs(rawDy) <= length * .96;
        double dy = Math.max(-length * .96, Math.min(length * .96, rawDy));
        double horizontal = Math.sqrt(length * length - dy * dy);
        double previous = Math.toRadians(yaw);
        double axleX = x - Math.sin(previous) * AXLE_FORWARD;
        double axleZ = z + Math.cos(previous) * AXLE_FORWARD;
        double dx = hitchX - axleX, dz = hitchZ - axleZ;
        float next = Math.hypot(dx, dz) < 1e-8 ? yaw : (float) Math.toDegrees(Math.atan2(-dx,dz));
        double heading = Math.toRadians(next);
        double pitch = Math.asin(dy / length) - Math.atan2(eyeHeight,HORIZONTAL_LENGTH);
        return new Result(hitchX + Math.sin(heading) * (horizontal + AXLE_FORWARD),
                hitchZ - Math.cos(heading) * (horizontal + AXLE_FORWARD),
                next,(float)Math.toDegrees(pitch), reachable);
    }
    record Result(double x, double z, float yaw, float pitch, boolean reachable) {}
}
