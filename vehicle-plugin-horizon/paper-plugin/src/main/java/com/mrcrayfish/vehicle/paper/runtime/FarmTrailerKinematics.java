package com.mrcrayfish.vehicle.paper.runtime;

/** Two-link drawbar trailer. Positions are in world X/Z blocks, yaw in degrees. */
final class FarmTrailerKinematics {
    static final double AXLE = 1.5D;
    static final double REAR_AXLE = 1.45D;
    static final double EYE = 1.835D;
    private FarmTrailerKinematics() {}

    static Result solve(double x, double z, float previousYaw, double hitchX, double hitchZ) {
        double oldBody = Math.toRadians(previousYaw);
        double oldFrontX = x - Math.sin(oldBody) * AXLE;
        double oldFrontZ = z + Math.cos(oldBody) * AXLE;
        double oldRearX = x + Math.sin(oldBody) * REAR_AXLE;
        double oldRearZ = z - Math.cos(oldBody) * REAR_AXLE;

        // The drawbar pivots freely towards the moving hitch; its direction is
        // determined by the pull, not by the tractor's body heading during a skid.
        double hx = hitchX - oldFrontX, hz = hitchZ - oldFrontZ;
        double frontYaw = Math.hypot(hx, hz) < 1.0E-8
                ? previousYaw : Math.toDegrees(Math.atan2(-hx, hz));
        double front = Math.toRadians(frontYaw);
        double frontX = hitchX + Math.sin(front) * EYE;
        double frontZ = hitchZ - Math.cos(front) * EYE;

        // The rear axle follows the front axle without imposing sideways travel.
        double dx = frontX - oldRearX, dz = frontZ - oldRearZ;
        float yaw = (float) (Math.hypot(dx, dz) < 1.0E-8
                ? previousYaw : Math.toDegrees(Math.atan2(-dx, dz)));
        double body = Math.toRadians(yaw);
        float steering = (float) wrap(frontYaw - yaw);
        double rootX = frontX + Math.sin(body) * AXLE;
        double rootZ = frontZ - Math.cos(body) * AXLE;
        return new Result(rootX, rootZ, yaw, steering);
    }
    private static double wrap(double angle) { return ((angle + 540.0) % 360.0 + 360.0) % 360.0 - 180.0; }
    record Result(double x, double z, float yaw, float steering) {}
}
