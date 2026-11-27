package com.mrcrayfish.vehicle.paper.recovery;

/** Shared geometry for selecting a target behind a recovery carrier.
 * Coordinates use the same yaw convention as the live recovery route. */
public final class RecoveryRearApproach {
    public static final double MAX_DISTANCE = 10D;
    private RecoveryRearApproach() { }

    public record Offset(double longitudinal, double lateral, double distanceSquared) { }

    public static Offset offset(double dx, double dy, double dz, double yawDegrees) {
        if (!Double.isFinite(dx) || !Double.isFinite(dy) || !Double.isFinite(dz)
                || !Double.isFinite(yawDegrees)) throw new IllegalArgumentException("Non-finite approach");
        double radians=Math.toRadians(yawDegrees), sin=Math.sin(radians), cos=Math.cos(radians);
        return new Offset(-dx*sin+dz*cos, -dx*cos-dz*sin, dx*dx+dy*dy+dz*dz);
    }

    /** A candidate in the rear half-space and inside the spherical ten-block radius. */
    public static boolean selectable(Offset offset) {
        return offset != null && offset.longitudinal() > 0
                && offset.distanceSquared() <= MAX_DISTANCE*MAX_DISTANCE;
    }

    /** Straight, level approach using the common approximate wheelbase. */
    public static boolean aligned(Offset offset, double yDifference, double yawDifference) {
        if (!selectable(offset) || !Double.isFinite(yDifference) || !Double.isFinite(yawDifference)) return false;
        double z=offset.longitudinal();
        // Both axles start on ground, not suspended halfway up a ramp.
        double minZ=RecoveryLoadingPath.RAMP_END+3.3D/2D;
        return z >= minZ && Math.abs(offset.lateral()) <= .05D
                && Math.abs(yDifference) <= .05D
                && Math.abs(Math.IEEEremainder(yawDifference,360D)) <= 2D;
    }
}
