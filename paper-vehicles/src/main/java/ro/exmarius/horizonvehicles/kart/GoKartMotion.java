package ro.exmarius.horizonvehicles.kart;

import com.mrcrayfish.vehicle.paper.vehicle.LandVehicleSpec;

/** Go-Kart subset of the GPL Paper LandVehicle drivetrain; charging/boost is not yet ported. */
public final class GoKartMotion {
    private static final LandVehicleSpec SPEC = LandVehicleSpec.GO_KART;
    public static final double CAPACITY = 100.0;
    private static final double SPEED_LIMIT = 18.0; // internal blocks/second, not blocks/tick
    private double vx, vz, yawDegrees, steeringAngle;
    private double traction = LandVehicleSpec.STANDARD_TRACTION;
    private double fuel = CAPACITY;

    public record Step(double dx, double dz, double yawDegrees, double speed, double fuel, double steering) { }

    public GoKartMotion(double yawDegrees) {
        if (!Double.isFinite(yawDegrees)) throw new IllegalArgumentException("yaw must be finite");
        this.yawDegrees = yawDegrees;
    }

    /** Steering: +1 left, -1 right, as in source VehicleInput. */
    public Step tick(int throttle, int steering, boolean brake, boolean onGround, double friction, double tractionFactor) {
        throttle = Integer.compare(throttle, 0);
        steering = Integer.compare(steering, 0);
        double target = SPEC.maxSteeringAngle() * steering;
        steeringAngle += (target - steeringAngle) * (steering == 0 ? .2 : .05);
        double radians = Math.toRadians(yawDegrees);
        double fx = -Math.sin(radians), fz = Math.cos(radians);
        double force = onGround && fuel > 0 && !brake ? SPEC.enginePower() * throttle : 0;
        if (throttle < 0) force *= .4;
        double speed = Math.hypot(vx, vz);
        if (speed < .05) { vx = 0; vz = 0; speed = 0; }
        double damping = Math.max(0, friction) * .05 + speed * .001 * .05 + (onGround && brake ? .05 : 0);
        double ax = fx * force * .05 - vx * damping;
        double az = fz * force * .05 - vz * damping;
        vx += ax; vz += az;
        speed = Math.hypot(vx, vz);
        if (speed > SPEED_LIMIT) { vx *= SPEED_LIMIT / speed; vz *= SPEED_LIMIT / speed; speed = SPEED_LIMIT; }
        double accel = Math.hypot(ax, az);
        if (brake) traction = .05;
        else {
            double desired = LandVehicleSpec.STANDARD_TRACTION * (accel > 0 ? Math.min(1, speed / accel) : 1);
            double side = speed < 1e-8 ? 1 : Math.max(0, 1 - Math.abs(vx / speed * fz - vz / speed * fx) / .3);
            traction += (desired - traction) * side * .15;
        }
        double steerRad = Math.toRadians(steeringAngle), cos = Math.cos(steerRad), sin = Math.sin(steerRad);
        double frontX = fx * SPEC.frontAxleOffset() + (vx * cos + vz * sin) * .05;
        double frontZ = fz * SPEC.frontAxleOffset() + (vz * cos - vx * sin) * .05;
        double rearX = fx * SPEC.rearAxleOffset() + vx * .05;
        double rearZ = fz * SPEC.rearAxleOffset() + vz * .05;
        double hx = frontX - rearX, hz = frontZ - rearZ, length = Math.hypot(hx, hz);
        if (length < 1e-8) { hx = fx; hz = fz; }
        else { hx /= length; hz /= length; }
        double dx = rearX - hx * SPEC.rearAxleOffset();
        double dz = rearZ - hz * SPEC.rearAxleOffset();
        double align = Math.max(0, Math.min(1, tractionFactor * traction));
        double targetSpeed = hx * vx + hz * vz > 0 ? speed : -Math.min(speed, SPEC.maxReverseSpeed());
        vx = vx * (1 - align) + hx * targetSpeed * align;
        vz = vz * (1 - align) + hz * targetSpeed * align;
        yawDegrees = Math.toDegrees(Math.atan2(hz, hx)) - 90;
        yawDegrees = ((yawDegrees + 180) % 360 + 360) % 360 - 180;
        if (throttle != 0 && fuel > 0) fuel = Math.max(0, fuel - SPEC.energyPerTick() / SPEC.energyCapacity() * CAPACITY);
        return new Step(dx, dz, yawDegrees, Math.hypot(vx, vz) * .05, fuel, steeringAngle);
    }

    public void stop() { vx = 0; vz = 0; }
    public void refuel(double amount) {
        if (!Double.isFinite(amount) || amount < 0) throw new IllegalArgumentException("invalid fuel amount");
        fuel = Math.min(CAPACITY, fuel + amount);
    }
}
