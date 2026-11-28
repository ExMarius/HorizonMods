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
        // A vehicle can wait at the ramp foot or partially at the start of it.
        // Both orientations are accepted: different models have opposite yaw conventions.
        double heading=Math.abs(Math.IEEEremainder(yawDifference,180D));
        return z >= 7.9D && Math.abs(offset.lateral()) <= 1.1D
                && Math.abs(yDifference) <= .25D && heading <= 25D;
    }
}
