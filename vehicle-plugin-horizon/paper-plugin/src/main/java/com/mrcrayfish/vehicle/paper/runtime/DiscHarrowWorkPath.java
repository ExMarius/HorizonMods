package com.mrcrayfish.vehicle.paper.runtime;

import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

/** Bounded swept footprint; produces candidates only, never accesses or changes a world.
 * The caller must check loaded chunks, soil, authorization and protection for every cell. */
final class DiscHarrowWorkPath {
    private static final double MAX_TICK_DISTANCE = 1.0;
    private static final double SPACING = 0.25;
    private static final double HALF_WIDTH = 1.6;
    private DiscHarrowWorkPath() {}

    static List<Cell> sample(double previousX, double previousZ, double x, double z, float yaw) {
        if (!Double.isFinite(previousX) || !Double.isFinite(previousZ) || !Double.isFinite(x)
                || !Double.isFinite(z) || !Float.isFinite(yaw)) return List.of();
        double dx=x-previousX, dz=z-previousZ, distance=Math.hypot(dx,dz);
        double angle=Math.toRadians(yaw), forwardX=-Math.sin(angle), forwardZ=Math.cos(angle);
        if (distance > MAX_TICK_DISTANCE || forwardX*dx+forwardZ*dz < .025) return List.of();
        double rightX=Math.cos(angle), rightZ=Math.sin(angle);
        int steps=(int)Math.ceil(distance/SPACING);
        int lanes=(int)Math.ceil(2*HALF_WIDTH/SPACING);
        Set<Cell> cells=new LinkedHashSet<>();
        for(int step=0;step<=steps;step++) {
            double t=(double)step/steps;
            for(int lane=0;lane<=lanes;lane++) {
                double side=-HALF_WIDTH+2*HALF_WIDTH*lane/lanes;
                double sx=previousX+dx*t+rightX*side, sz=previousZ+dz*t+rightZ*side;
                if (sx<Integer.MIN_VALUE || sx>=Integer.MAX_VALUE || sz<Integer.MIN_VALUE || sz>=Integer.MAX_VALUE)
                    return List.of();
                cells.add(new Cell((int)Math.floor(sx),(int)Math.floor(sz)));
            }
        }
        return List.copyOf(cells);
    }
    record Cell(int x, int z) {}
}
