package com.mrcrayfish.vehicle.paper.vehicle;

import com.mrcrayfish.vehicle.paper.recovery.RecoveryCable;
import com.mrcrayfish.vehicle.paper.recovery.RecoveryCableWorldCheck;
import com.mrcrayfish.vehicle.paper.recovery.RecoveryInterlock;
import com.mrcrayfish.vehicle.paper.recovery.RecoveryLoadingPath;
import org.bukkit.Bukkit;
import org.bukkit.Location;

import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.UUID;

/** Disposable-server recovery experiment; NOT connected to commands or persistence.
 * Uses a caller-provided safety snapshot and authority, ideal flat terrain, and
 * approximate dimensions/hook point. Experimental transport has no full collision or crash protection. Do not deploy. */
public final class PrototypeRecoveryRoute {
    public enum State { LOADING, AT_DECK, TEST_DRIVING, UNLOADING, ON_GROUND, STOPPED, FINISHED }
    private static final int STEPS=180;
    private static final double START=9.8, DECK=2.64, WHEELBASE=3.3;
    private final PrototypeRecoveryMotion motion;
    private final VehicleManager manager;
    private final LandVehicle carrier,target;
    private Location origin;
    private double sin,cos;
    private int step;
    private State state=State.LOADING;

    private PrototypeRecoveryRoute(VehicleManager manager,PrototypeRecoveryMotion motion,LandVehicle carrier,LandVehicle target) {
        this.manager=manager;this.motion=motion;this.carrier=carrier;this.target=target;origin=carrier.location().clone();
        double yaw=Math.toRadians(origin.getYaw());sin=Math.sin(yaw);cos=Math.cos(yaw);
    }
    /** Only the Dacia example geometry on a level approach is modelled. The
     * caller is responsible for proving those dimensions and all permissions. */
    public static PrototypeRecoveryRoute begin(VehicleManager manager, LandVehicle carrier, LandVehicle target,
                                                org.bukkit.entity.Player player, PrototypeRecoveryMotion.Authority authority,
                                                RecoveryInterlock.Safety safety) {
        if(!Bukkit.isPrimaryThread()||manager==null||carrier==null||target==null
                || !"dacia_logan_police".equals(target.spec().id())) return null;
        Location base=carrier.location(), start=target.location();
        if(base.getWorld()==null || !base.getWorld().equals(start.getWorld()))return null;
        double yaw=Math.toRadians(base.getYaw());
        Location expected=base.clone().add(START*Math.sin(yaw),0,-START*Math.cos(yaw));
        if(expected.distanceSquared(start)>1e-8 || Math.abs(Math.IEEEremainder(start.getYaw()-base.getYaw(),360D))>.01F) return null;
        PrototypeRecoveryMotion motion=PrototypeRecoveryMotion.begin(manager,carrier,target,player,authority,safety);
        if(motion==null)return null;
        return new PrototypeRecoveryRoute(manager,motion,carrier,target);
    }
    public State state(){return state;}
    /** Tests only: vehicle_trailer-like fixed transform, no durable restraints. */
    public boolean beginTestDrive() {
        if(!Bukkit.isPrimaryThread() || state!=State.AT_DECK)return false;
        carrier.rig().setRecoveryCable(List.of());carrier.rig().setRecoveryRampProgress(0);carrier.forceVisualSync();
        if(!motion.startTestDrive()) {carrier.rig().setRecoveryRampProgress(1);return false;}
        state=State.TEST_DRIVING;return true;
    }
    public boolean tickTestDrive() {
        if(!Bukkit.isPrimaryThread()||state!=State.TEST_DRIVING)return false;
        if(!motion.followTestDrive()){state=State.STOPPED;return false;}
        return true;
    }
    public boolean endTestDrive() {
        if(!Bukkit.isPrimaryThread()||state!=State.TEST_DRIVING||!motion.endTestDrive())return false;
        origin=carrier.location().clone();
        double yaw=Math.toRadians(origin.getYaw());sin=Math.sin(yaw);cos=Math.cos(yaw);
        carrier.rig().setRecoveryRampProgress(1);carrier.forceVisualSync();
        state=State.AT_DECK;return true;
    }
    /** Explicit operator action after the carrier is stationary. */
    public boolean beginUnload() {
        if(!Bukkit.isPrimaryThread()||state!=State.AT_DECK)return false;
        step=0;state=State.UNLOADING;return true;
    }
    /** One tick on the main thread. Any failed check halts and cannot auto-resume. */
    public State tick(RecoveryInterlock.Safety safety) {
        if(!Bukkit.isPrimaryThread() || (state!=State.LOADING && state!=State.UNLOADING)) return state;
        try {
            if (!sameCarrierPose()) return stop();
            boolean loading=state==State.LOADING;
            double from=loading?START:DECK,to=loading?DECK:START;
            var previous=RecoveryLoadingPath.sample(from,to,WHEELBASE,step/(double)STEPS);
            Location actual=target.location();
            if(!origin.getWorld().equals(actual.getWorld()) || actual.distanceSquared(destination(previous))>1e-8
                    || Math.abs(Math.IEEEremainder(actual.getYaw()-origin.getYaw(),360D))>.01D) return stop();
            var next=RecoveryLoadingPath.sample(from,to,WHEELBASE,(step+1D)/STEPS);
            var cable=cable(next);
            if(!RecoveryCable.clearsLevelBed(cable,.18,5.35,.86,.018))return stop();
            Set<UUID> ignored=new HashSet<>();
            carrier.rig().entities().forEach(e -> ignored.add(e.getUniqueId()));
            target.rig().entities().forEach(e -> ignored.add(e.getUniqueId()));
            var worldCable=cable.stream().map(p -> new RecoveryCable.Point(
                    origin.getX()-p.x()*cos+p.z()*sin,origin.getY()+p.y(),origin.getZ()-p.x()*sin-p.z()*cos)).toList();
            if(!RecoveryCableWorldCheck.clear(origin.getWorld(),worldCable,.018,ignored))return stop();
            var delta=destination(next).toVector().subtract(target.location().toVector());
            if(!motion.step(delta,safety,next.pitch()))return stop();
            carrier.rig().setRecoveryCable(cable);carrier.forceVisualSync();
            if(++step==STEPS)state=loading?State.AT_DECK:State.ON_GROUND;
            return state;
        } catch(RuntimeException e) { return stop(); }
    }
    /** Only unlock on checked solid ground; a stopped suspended vehicle stays locked. */
    public boolean finishOnGround() {
        if(!Bukkit.isPrimaryThread()||(state!=State.ON_GROUND && state!=State.STOPPED)||!motion.releaseOnGround())return false;
        carrier.rig().setRecoveryCable(List.of());carrier.forceVisualSync();state=State.FINISHED;
        manager.returnOfflineRecoveredVehicle(target);
        return true;
    }
    private State stop(){state=State.STOPPED;return state;}
    private boolean sameCarrierPose(){
        Location now=carrier.location();
        return origin.getWorld().equals(now.getWorld()) && origin.distanceSquared(now)<1e-8
                && Math.abs(Math.IEEEremainder(now.getYaw()-origin.getYaw(),360D))<.01F;
    }
    private Location destination(RecoveryLoadingPath.Pose pose){
        return origin.clone().add(pose.centerZ()*sin,pose.height(),-pose.centerZ()*cos);
    }
    private static List<RecoveryCable.Point> cable(RecoveryLoadingPath.Pose pose){
        double c=Math.cos(pose.pitch()),s=Math.sin(pose.pitch());
        double hookY=pose.height()+.005+.35*c+2.43*s, hookZ=pose.centerZ()+.35*s-2.43*c;
        return RecoveryCable.route(new RecoveryCable.Point(0,1.06,.18),new RecoveryCable.Point(0,.99,5.40),
                new RecoveryCable.Point(0,hookY,hookZ));
    }
}
