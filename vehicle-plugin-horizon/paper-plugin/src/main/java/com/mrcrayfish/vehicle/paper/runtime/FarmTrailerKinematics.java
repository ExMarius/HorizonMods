package com.mrcrayfish.vehicle.paper.runtime;

/** Horizontal geometry for a drawbar pivoting around the front axle.
 * Distances are measured from the trailer root, in blocks. */
final class FarmTrailerKinematics {
    static final double AXLE = 1.5D;
    static final double EYE = 1.835D;
    private FarmTrailerKinematics() {}

    static Result solve(double x, double z, float previousYaw, double hitchX, double hitchZ, float pullerYaw) {
        double dx = hitchX - x, dz = hitchZ - z;
        double desiredHeading = Math.hypot(dx, dz) < 1.0E-8 ? previousYaw : Math.toDegrees(Math.atan2(-dx, dz));
        float yaw = (float) (previousYaw + clamp(wrap(desiredHeading - previousYaw), -5.0, 5.0));
        double body = Math.toRadians(yaw);
        // The tongue follows the tractor's heading immediately, including slow
        // steering. The bed follows smoothly behind; the eye remains on its pin.
        float steering = (float) clamp(wrap(pullerYaw - yaw), -70.0, 70.0);
        double front = Math.toRadians(yaw + steering);
        // Reconstruct the root so the eye lands exactly on the hitch in X/Z.
        double rootX = hitchX + Math.sin(body) * AXLE + Math.sin(front) * EYE;
        double rootZ = hitchZ - Math.cos(body) * AXLE - Math.cos(front) * EYE;
        return new Result(rootX, rootZ, yaw, steering);
    }
    private static double wrap(double angle) { return ((angle + 540.0) % 360.0 + 360.0) % 360.0 - 180.0; }
    private static double clamp(double n, double min, double max) { return Math.max(min, Math.min(max, n)); }
    record Result(double x, double z, float yaw, float steering) {}
}
