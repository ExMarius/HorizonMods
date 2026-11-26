package com.mrcrayfish.vehicle.paper.recovery;

/**
 * Geometric preview of a centred, straight, two-axle loading path, in the
 * truck's local coordinate system (front is negative Z). This does not move a
 * vehicle, check its body or cable for collisions, or grant permission.
 * The actual tyre footprint, pitch rendering and terrain must be checked before
 * this approximation can be used for gameplay.
 */
public final class RecoveryLoadingPath {
    private RecoveryLoadingPath() { }

    public static final double RAMP_RUN = RecoveryRampKinematics.LENGTH
            * Math.cos(RecoveryRampKinematics.deployedAngle());
    public static final double RAMP_END = RecoveryEnvelope.DECK_END + RAMP_RUN;

    public record Pose(double centerZ, double height, double pitch,
                       double frontHeight, double rearHeight) { }

    /** Height of the idealised supporting surface relative to level ground. */
    public static double surfaceHeight(double z) {
        if (!Double.isFinite(z)) throw new IllegalArgumentException("Non-finite position");
        if (z <= RecoveryEnvelope.DECK_END) return RecoveryRampKinematics.DECK_HEIGHT;
        if (z >= RAMP_END) return 0;
        return RecoveryRampKinematics.DECK_HEIGHT * (RAMP_END - z) / RAMP_RUN;
    }

    /** Estimate pitch from the axle heights. Only valid for a level, centred approach. */
    public static Pose pose(double centerZ, double wheelbase) {
        if (!Double.isFinite(centerZ) || !Double.isFinite(wheelbase) || wheelbase <= 0)
            throw new IllegalArgumentException("Invalid position or wheelbase");
        double frontZ = centerZ - wheelbase / 2;
        double rearZ = centerZ + wheelbase / 2;
        if (!Double.isFinite(frontZ) || !Double.isFinite(rearZ))
            throw new IllegalArgumentException("Position overflow");
        double front = surfaceHeight(frontZ), rear = surfaceHeight(rearZ);
        return new Pose(centerZ, (front + rear) / 2, Math.atan2(front - rear, wheelbase), front, rear);
    }

    /** Linear path sample; progress 0 and 1 reproduce the supplied endpoints. */
    public static Pose sample(double startZ, double endZ, double wheelbase, double progress) {
        if (!Double.isFinite(startZ) || !Double.isFinite(endZ)
                || !Double.isFinite(progress) || progress < 0 || progress > 1)
            throw new IllegalArgumentException("Invalid path sample");
        // Avoid a subtraction overflow for large but finite endpoints.
        double z = startZ * (1 - progress) + endZ * progress;
        return pose(z, wheelbase);
    }
}
