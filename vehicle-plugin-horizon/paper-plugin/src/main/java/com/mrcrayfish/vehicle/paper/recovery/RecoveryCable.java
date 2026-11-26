package com.mrcrayfish.vehicle.paper.recovery;

import java.util.List;

/** Local-space visual cable routing. Not a physics engine or obstacle query. */
public final class RecoveryCable {
    private RecoveryCable() { }
    public record Point(double x, double y, double z) {
        public Point {
            if (!Double.isFinite(x) || !Double.isFinite(y) || !Double.isFinite(z))
                throw new IllegalArgumentException("Non-finite point");
        }
    }

    /**
     * Uses the rear roller when a straight line would intersect its top. Requires
     * an aligned, level carrier and a target in front of the outlet in local +Z.
     * Does not check world blocks, target body, protection, or cable thickness.
     * The eventual runtime MUST independently validate those before movement.
     */
    public static List<Point> route(Point outlet, Point roller, Point hook) {
        if (outlet == null || roller == null || hook == null ||
                outlet.x() != 0 || roller.x() != 0 || hook.x() != 0 ||
                roller.z() <= outlet.z() || hook.z() <= outlet.z())
            throw new IllegalArgumentException("Unaligned or invalid cable geometry");
        if (hook.z() > roller.z()) {
            double t = (roller.z() - outlet.z()) / (hook.z() - outlet.z());
            double height = outlet.y() + (hook.y() - outlet.y()) * t;
            if (height < roller.y()) return List.of(outlet, roller, hook);
        }
        return List.of(outlet, hook);
    }
}
