package ro.exmarius.horizonvehicles.kart;

/** Tick-based drivetrain model; world collision, entity movement and input are external. */
public final class GoKartMotion {
    public static final double CAPACITY = 100.0;
    private static final double MAX_FORWARD = 0.35;
    private static final double MAX_REVERSE = 0.14;
    private double speed;
    private double yawDegrees;
    private double fuel = CAPACITY;

    public record Step(double dx, double dz, double yawDegrees, double speed, double fuel) { }

    public GoKartMotion(double yawDegrees) {
        if (!Double.isFinite(yawDegrees)) throw new IllegalArgumentException("yaw must be finite");
        this.yawDegrees = yawDegrees;
    }

    /** Called once per server tick; input is normalized to -1, 0 or 1. */
    public Step tick(int throttle, int steering, boolean brake) {
        throttle = Integer.compare(throttle, 0);
        steering = Integer.compare(steering, 0);
        if (fuel > 0 && throttle != 0 && !brake) {
            speed += throttle * 0.018;
            fuel = Math.max(0, fuel - 0.004);
        } else {
            speed *= brake ? 0.65 : 0.96;
        }
        speed = Math.max(-MAX_REVERSE, Math.min(MAX_FORWARD, speed));
        if (Math.abs(speed) < 0.001) speed = 0;
        // Reverse steering changes direction as it would in a car.
        yawDegrees += steering * Math.max(-1, Math.min(1, speed / 0.10)) * 3.0;
        double radians = Math.toRadians(yawDegrees);
        return new Step(-Math.sin(radians) * speed, Math.cos(radians) * speed,
                yawDegrees, speed, fuel);
    }

    /** Stop after the caller rejects a move due to a collision. */
    public void stop() { speed = 0; }

    public void refuel(double amount) {
        if (!Double.isFinite(amount) || amount < 0) throw new IllegalArgumentException("invalid fuel amount");
        fuel = Math.min(CAPACITY, fuel + amount);
    }
}
