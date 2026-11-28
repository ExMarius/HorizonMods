package com.mrcrayfish.vehicle.paper.runtime;

/** Safe transition controller for a towed disc harrow. Position 0 is road
 * transport, 1 is the working position. This class does not edit the world;
 * callers must independently check permissions and terrain protection. */
final class DiscHarrowState {
    private static final double STEP = 1.0D / 20.0D;
    private boolean coupled;
    private boolean requestedWork;
    private double position;

    void couple() {
        coupled = true;
        requestedWork = false; // hitching always starts in the safe transport state
    }

    void detach() {
        coupled = false;
        requestedWork = false;
    }

    boolean setWorking(boolean working, boolean authorizedDriver) {
        if (working && (!coupled || !authorizedDriver)) return false;
        requestedWork = working;
        return true;
    }

    void tick(boolean authorizedDriver) {
        if (!coupled || !authorizedDriver) requestedWork = false;
        double target = requestedWork ? 1.0D : 0.0D;
        if (position < target) position = Math.min(target, position + STEP);
        else if (position > target) position = Math.max(target, position - STEP);
    }

    boolean canWork(boolean authorizedDriver, boolean onGround, double forwardDistance) {
        return coupled && authorizedDriver && requestedWork && position >= 1.0D
                && onGround && forwardDistance >= .025D;
    }

    boolean standDeployed() { return !coupled; }
    boolean workRequested() { return requestedWork; }
    double position() { return position; }
}
