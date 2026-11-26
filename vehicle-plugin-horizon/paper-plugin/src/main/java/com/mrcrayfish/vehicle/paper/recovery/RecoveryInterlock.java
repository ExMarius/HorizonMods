package com.mrcrayfish.vehicle.paper.recovery;

import java.util.UUID;

/**
 * Isolated, fail-closed state controller for future recovery-truck integration.
 * It moves no entities and grants no permissions. Callers must query live server
 * state and apply its decisions on the Paper main thread; no caller is wired yet.
 */
public final class RecoveryInterlock {
    public enum Mode { DRIVEN, WINCH }
    public enum Phase { IDLE, RAMPS_OPEN, READY, MOVING, PAUSED, POSITIONED, SECURED }
    public enum Denial {
        NONE, INVALID_PHASE, MISSING_ENTITY, UNAUTHORIZED, PROTECTION_UNAVAILABLE,
        PROHIBITED_AREA, TRUCK_MOVING, UNKNOWN_COUPLING, TRAILER_ATTACHED,
        ALREADY_TRANSPORTED, UNKNOWN_GEOMETRY, DOES_NOT_FIT, PATH_UNCHECKED,
        PATH_BLOCKED, WRONG_OCCUPANTS, CABLE_NOT_ATTACHED, CABLE_STILL_ATTACHED,
        NOT_CENTERED, RAMPS_NOT_OPEN, RAMPS_NOT_CLOSED, NOT_SECURED
    }

    /** Every 'known/checked' flag is separate from its value: unknown is not safe. */
    public record Safety(boolean entitiesPresent, boolean operatorAuthorized,
                         boolean protectionChecked, boolean areaAllowed,
                         boolean truckStationary, boolean couplingKnown,
                         boolean attachmentFree, boolean targetFree,
                         boolean geometryKnown, boolean fits,
                         boolean pathChecked, boolean pathClear,
                         boolean driverAuthorizedAndAlone, boolean targetEmpty,
                         boolean cableAttached, boolean centered,
                         boolean rampsOpen, boolean rampsClosed, boolean strapsConfirmed) { }

    private Phase phase = Phase.IDLE;
    private Phase pausedFrom;
    private Mode mode;
    private UUID carrier, target, operator;

    public Phase phase() { return phase; }
    public UUID carrier() { return carrier; }
    public UUID target() { return target; }
    public UUID operator() { return operator; }
    public Mode mode() { return mode; }
    public boolean locked() { return phase != Phase.IDLE; }
    public boolean mayDriveCarrier() { return phase == Phase.IDLE || phase == Phase.SECURED; }

    public Denial openRamps(UUID carrier, UUID target, UUID operator, Mode mode, Safety safety) {
        if (phase != Phase.IDLE) return Denial.INVALID_PHASE;
        if (carrier == null || target == null || operator == null || carrier.equals(target) || mode == null || safety == null)
            return Denial.MISSING_ENTITY;
        Denial denial = validate(safety, mode, false);
        if (denial != Denial.NONE) return denial;
        this.carrier = carrier; this.target = target; this.operator = operator; this.mode = mode;
        phase = Phase.RAMPS_OPEN;
        return Denial.NONE;
    }

    /** Called only after real ramp animation/collision checks have completed. */
    public Denial rampsReady(Safety safety) {
        if (phase != Phase.RAMPS_OPEN) return Denial.INVALID_PHASE;
        Denial d = validate(safety, mode, false);
        if (d != Denial.NONE) return d;
        if (!safety.rampsOpen()) return Denial.RAMPS_NOT_OPEN;
        phase = Phase.READY;
        return Denial.NONE;
    }

    public Denial startMovement(Safety safety) {
        if (phase != Phase.READY) return Denial.INVALID_PHASE;
        Denial d = validate(safety, mode, true);
        if (d != Denial.NONE) return d;
        phase = Phase.MOVING;
        return Denial.NONE;
    }

    /** Re-evaluate live conditions before EVERY movement update; never auto-resume. */
    public Denial checkMovement(Safety safety) {
        if (phase != Phase.MOVING) return Denial.INVALID_PHASE;
        Denial d = validate(safety, mode, true);
        if (d != Denial.NONE) { pausedFrom = Phase.MOVING; phase = Phase.PAUSED; }
        return d;
    }

    public Denial resume(Safety safety) {
        if (phase != Phase.PAUSED || pausedFrom != Phase.MOVING) return Denial.INVALID_PHASE;
        Denial d = validate(safety, mode, true);
        if (d != Denial.NONE) return d;
        pausedFrom = null; phase = Phase.MOVING;
        return Denial.NONE;
    }

    public Denial finishMovement(Safety safety) {
        if (phase != Phase.MOVING) return Denial.INVALID_PHASE;
        Denial d = checkMovement(safety);
        if (d != Denial.NONE) return d;
        if (!safety.centered()) return Denial.NOT_CENTERED;
        phase = Phase.POSITIONED;
        return Denial.NONE;
    }

    /** Attaching straps and closing ramps are real-world operations, not performed here. */
    public Denial secure(Safety safety) {
        if (phase != Phase.POSITIONED) return Denial.INVALID_PHASE;
        if (safety == null || !safety.entitiesPresent()) return Denial.MISSING_ENTITY;
        if (!safety.operatorAuthorized()) return Denial.UNAUTHORIZED;
        if (!safety.protectionChecked()) return Denial.PROTECTION_UNAVAILABLE;
        if (!safety.areaAllowed()) return Denial.PROHIBITED_AREA;
        if (!safety.truckStationary()) return Denial.TRUCK_MOVING;
        if (!safety.couplingKnown()) return Denial.UNKNOWN_COUPLING;
        if (!safety.attachmentFree()) return Denial.TRAILER_ATTACHED;
        if (!safety.targetFree()) return Denial.ALREADY_TRANSPORTED;
        if (!safety.geometryKnown()) return Denial.UNKNOWN_GEOMETRY;
        if (!safety.fits()) return Denial.DOES_NOT_FIT;
        if (!safety.targetEmpty()) return Denial.WRONG_OCCUPANTS;
        if (!safety.centered()) return Denial.NOT_CENTERED;
        if (safety.cableAttached()) return Denial.CABLE_STILL_ATTACHED;
        if (!safety.rampsClosed() || safety.rampsOpen()) return Denial.RAMPS_NOT_CLOSED;
        if (!safety.strapsConfirmed()) return Denial.NOT_SECURED;
        phase = Phase.SECURED;
        return Denial.NONE;
    }

    /** Never discard an active operation or a secured vehicle through a generic reset. */
    public Denial resetIfEmptyAndSafe(boolean explicitlyEmpty, boolean rampsClosed, boolean cableDetached) {
        if (phase == Phase.SECURED || !explicitlyEmpty || !rampsClosed || !cableDetached) return Denial.INVALID_PHASE;
        phase = Phase.IDLE; pausedFrom = null; carrier = target = operator = null; mode = null;
        return Denial.NONE;
    }

    private static Denial validate(Safety s, Mode mode, boolean moving) {
        if (s == null || mode == null || !s.entitiesPresent()) return Denial.MISSING_ENTITY;
        if (!s.operatorAuthorized()) return Denial.UNAUTHORIZED;
        if (!s.protectionChecked()) return Denial.PROTECTION_UNAVAILABLE;
        if (!s.areaAllowed()) return Denial.PROHIBITED_AREA;
        if (!s.truckStationary()) return Denial.TRUCK_MOVING;
        if (!s.couplingKnown()) return Denial.UNKNOWN_COUPLING;
        if (!s.attachmentFree()) return Denial.TRAILER_ATTACHED;
        if (!s.targetFree()) return Denial.ALREADY_TRANSPORTED;
        if (!s.geometryKnown()) return Denial.UNKNOWN_GEOMETRY;
        if (!s.fits()) return Denial.DOES_NOT_FIT;
        if (!s.pathChecked()) return Denial.PATH_UNCHECKED;
        if (!s.pathClear()) return Denial.PATH_BLOCKED;
        if (mode == Mode.WINCH && !s.targetEmpty()) return Denial.WRONG_OCCUPANTS;
        if (moving && !s.rampsOpen()) return Denial.RAMPS_NOT_OPEN;
        if (moving && mode == Mode.DRIVEN && !s.driverAuthorizedAndAlone()) return Denial.WRONG_OCCUPANTS;
        if (moving && mode == Mode.WINCH && !s.cableAttached()) return Denial.CABLE_NOT_ATTACHED;
        if (mode == Mode.DRIVEN && s.cableAttached()) return Denial.CABLE_STILL_ATTACHED;
        return Denial.NONE;
    }
}
