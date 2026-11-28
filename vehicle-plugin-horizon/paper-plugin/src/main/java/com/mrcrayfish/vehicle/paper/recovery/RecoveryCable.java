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
                outlet.x() != 0 || roller.x() != 0 ||
                roller.z() <= outlet.z() || hook.z() <= outlet.z())
            throw new IllegalArgumentException("Unaligned or invalid cable geometry");
        if (hook.z() > roller.z()) {
            double t = (roller.z() - outlet.z()) / (hook.z() - outlet.z());
            double height = outlet.y() + (hook.y() - outlet.y()) * t;
            if (height < roller.y()) return List.of(outlet, roller, hook);
        }
        return List.of(outlet, hook);
    }
    /** Exact line-segment clearance over a level bed; not a world collision test. */
    public static boolean clearsLevelBed(List<Point> path,double bedStart,double bedEnd,double top,double radius) {
        if(path==null || path.size()<2 || path.size()>3 || !Double.isFinite(bedStart) || !Double.isFinite(bedEnd)
                || !Double.isFinite(top) || !Double.isFinite(radius) || bedEnd<=bedStart || radius<0) return false;
        for(int i=0;i<path.size();i++){
            Point p=path.get(i);
            // Visual prototype has no safe representation for huge or non-centred points.
            if(p==null || Math.abs(p.x())>2 || p.y()<radius || Math.abs(p.y())>64 || Math.abs(p.z())>64) return false;
            if(i==0)continue;
            Point a=path.get(i-1),b=p;
            if(b.z()<=a.z() || Math.hypot(b.y()-a.y(),b.z()-a.z())<1e-5) return false;
            double lo=Math.max(a.z(),bedStart),hi=Math.min(b.z(),bedEnd);
            if(lo>hi)continue;
            double y0=a.y()+(b.y()-a.y())*(lo-a.z())/(b.z()-a.z());
            double y1=a.y()+(b.y()-a.y())*(hi-a.z())/(b.z()-a.z());
            if(Math.min(y0,y1)-radius<top) return false;
        }
        return true;
    }

}
