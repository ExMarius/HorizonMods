package com.mrcrayfish.vehicle.paper.recovery;

/** Conservative concept measurements; these alone do not prove that a path is safe. */
public final class RecoveryEnvelope {
    private RecoveryEnvelope() { }
    // Browser-authored geometry, local metres/blocks. Front is negative Z.
    public static final double DECK_WIDTH = 2.90;
    public static final double DECK_START = -.15;
    public static final double DECK_END = 5.35;
    public static final double ROLLER_EXIT = .18;
    public static final double REAR_RAMP_CLEARANCE = .13;
    public static final double SIDE_CLEARANCE = .15;
    public static final double RAMP_CENTER = 1.05;
    public static final double RAMP_WIDTH = .72;

    /** Width and length must be measured from the *complete* actual model,
     * including protrusions. No hard-coded fallback for an unknown vehicle. */
    public record Vehicle(double width, double length, double frontTrack,
                          double rearTrack, double tireWidth) {
        public Vehicle {
            if (!positive(width) || !positive(length) || !positive(frontTrack)
                    || !positive(rearTrack) || !positive(tireWidth))
                throw new IllegalArgumentException("Unknown or non-positive vehicle dimensions");
        }
    }
    private static boolean positive(double value) { return Double.isFinite(value) && value > 0; }
    public static boolean fits(Vehicle v) {
        if (v == null) return false;
        double usableWidth=DECK_WIDTH-2*SIDE_CLEARANCE;
        double usableLength=DECK_END-REAR_RAMP_CLEARANCE-ROLLER_EXIT;
        return v.width()<=usableWidth && v.length()<=usableLength
                && axleFits(v.frontTrack(),v.tireWidth()) && axleFits(v.rearTrack(),v.tireWidth());
    }
    private static boolean axleFits(double track, double tireWidth) {
        // Track is centre-to-centre across the vehicle; one symmetric lane per tyre.
        return Math.abs(track/2-RAMP_CENTER)+tireWidth/2<=RAMP_WIDTH/2;
    }
}
