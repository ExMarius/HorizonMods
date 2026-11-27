package com.mrcrayfish.vehicle.paper.vehicle;

import com.mrcrayfish.vehicle.paper.recovery.RecoveryCable;
import com.mrcrayfish.vehicle.paper.recovery.RecoveryCableWorldCheck;
import com.mrcrayfish.vehicle.paper.recovery.RecoveryInterlock;
import com.mrcrayfish.vehicle.paper.recovery.RecoveryLoadingPath;
import com.mrcrayfish.vehicle.paper.recovery.RecoveryRearApproach;
import org.bukkit.Bukkit;
import org.bukkit.Location;

import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.UUID;

/** Disposable-server recovery experiment; NOT connected to commands or persistence.
 * Uses a caller-provided safety snapshot and authority, ideal flat terrain, and
 * approximate dimensions/hook point. Experimental transport has no full collision or crash protection. Do not deploy. */
public final class LiveRecoveryRoute {
    public enum State { LOADING, AT_DECK, TEST_DRIVING, PENDING_EVACUATION, UNLOADING, ON_GROUND, STOPPED, FINISHED, TEST_PARKED }
    private static final int STEPS=180;
    private static final double DECK=2.64, WHEELBASE=3.3;
    private final LiveRecoveryMotion motion;
    private final VehicleManager manager;
    private final LandVehicle carrier,target;
    private Location origin;
    private double sin,cos,startZ,lateral,groundOffset;
    private float cargoYaw;
    private final float cargoYawOffset;
    private final double pitchDirection;
    private State pausedState;
    private int step;
    private State state=State.LOADING;

    private LiveRecoveryRoute(VehicleManager manager,LiveRecoveryMotion motion,LandVehicle carrier,LandVehicle target) {
        this.manager=manager;this.motion=motion;this.carrier=carrier;this.target=target;origin=carrier.location().clone();
        double yaw=Math.toRadians(origin.getYaw());sin=Math.sin(yaw);cos=Math.cos(yaw);
        Location actual=target.location();double dx=actual.getX()-origin.getX(),dz=actual.getZ()-origin.getZ();
        startZ=-dx*sin+dz*cos;lateral=-dx*cos-dz*sin;
        groundOffset=actual.getY()-origin.getY()-RecoveryLoadingPath.pose(startZ,WHEELBASE).height();
        cargoYaw=actual.getYaw();
        cargoYawOffset=(float)Math.IEEEremainder(cargoYaw-origin.getYaw(),360D);
        pitchDirection=Math.cos(Math.toRadians(cargoYawOffset))<0?-1D:1D;
    }
    /** Common centred route for approved small/medium vehicles on level ground.
     * The shared wheelbase and tow-eye geometry are approximate for other models. */
    public static LiveRecoveryRoute begin(VehicleManager manager, LandVehicle carrier, LandVehicle target,
                                                org.bukkit.entity.Player player, LiveRecoveryMotion.Authority authority,
                                                RecoveryInterlock.Safety safety) {
        if(!Bukkit.isPrimaryThread()||manager==null||carrier==null||target==null
                || !com.mrcrayfish.vehicle.paper.recovery.RecoveryTargetPolicy.supports(target.spec())) return null;
        Location base=carrier.location(), start=target.location();
        if(base.getWorld()==null || !base.getWorld().equals(start.getWorld()))return null;
        var approach=RecoveryRearApproach.offset(start.getX()-base.getX(),start.getY()-base.getY(),
                start.getZ()-base.getZ(),base.getYaw());
        if(!RecoveryRearApproach.aligned(approach,start.getY()-base.getY(),
                start.getYaw()-base.getYaw())) return null;
        LiveRecoveryMotion motion=LiveRecoveryMotion.begin(manager,carrier,target,player,authority,safety);
        if(motion==null)return null;
        return new LiveRecoveryRoute(manager,motion,carrier,target);
    }
    public State state(){return state;}
    UUID lockToken(){return motion.lockToken();}
    boolean canReleaseOnGround(){return motion.canReleaseOnGround();}
    void abortUnmoved(){
        if(step!=0 || state!=State.LOADING)throw new IllegalStateException("Recovery already moved");
        motion.abortUnmoved();state=State.FINISHED;
    }
    /** Tests only: vehicle_trailer-like fixed transform, no durable restraints. */
    public boolean beginTestDrive() {
        if(!Bukkit.isPrimaryThread() || state!=State.AT_DECK)return false;
        carrier.rig().setRecoveryCable(List.of());carrier.rig().setRecoveryRampProgress(0);carrier.forceVisualSync();
        if(!motion.startTestDrive()) {carrier.rig().setRecoveryRampProgress(1);return false;}
        state=State.TEST_DRIVING;return true;
    }
    boolean canMoveCarrier(Location proposed) {
        return state!=State.TEST_DRIVING || motion.canFollowPose(proposed);
    }
    void syncMovedCarrier(Location pose) {
        if(state==State.TEST_DRIVING)motion.syncCarrierPose(pose);
    }
    public boolean tickTestDrive() {
        if(!Bukkit.isPrimaryThread()||state!=State.TEST_DRIVING)return false;
        if(!motion.followTestDrive()){pause();return false;}
        return true;
    }
    public boolean endTestDrive() {
        if(!Bukkit.isPrimaryThread()||state!=State.TEST_DRIVING||!motion.endTestDrive())return false;
        origin=carrier.location().clone();
        double yaw=Math.toRadians(origin.getYaw());sin=Math.sin(yaw);cos=Math.cos(yaw);
        lateral=0;groundOffset=0;cargoYaw=origin.getYaw()+cargoYawOffset;
        startZ=Math.max(startZ,9.55D);
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
            double from=loading?startZ:DECK,to=loading?DECK:startZ;
            double previousProgress=ease(step/(double)STEPS);
            var previous=RecoveryLoadingPath.sample(from,to,WHEELBASE,previousProgress);
            Location actual=target.location();
            double previousFactor=loading ? 1D-previousProgress : 0D;
            if(!origin.getWorld().equals(actual.getWorld()) || actual.distanceSquared(destination(previous,previousFactor))>1e-8
                    || Math.abs(Math.IEEEremainder(actual.getYaw()-cargoYaw,360D))>.01D) return stop();
            double nextProgress=ease((step+1D)/STEPS);
            var next=RecoveryLoadingPath.sample(from,to,WHEELBASE,nextProgress);
            double nextFactor=loading ? 1D-nextProgress : 0D;
            var cable=cable(next,lateral*nextFactor,groundOffset*nextFactor);
            if(!RecoveryCable.clearsLevelBed(cable,.18,5.35,.86,.018))return stop();
            Set<UUID> ignored=new HashSet<>();
            carrier.rig().entities().forEach(e -> ignored.add(e.getUniqueId()));
            target.rig().entities().forEach(e -> ignored.add(e.getUniqueId()));
            var worldCable=cable.stream().map(p -> new RecoveryCable.Point(
                    origin.getX()-p.x()*cos-p.z()*sin,origin.getY()+p.y(),origin.getZ()-p.x()*sin+p.z()*cos)).toList();
            if(!RecoveryCableWorldCheck.clear(origin.getWorld(),worldCable,.018,ignored))return stop();
            var delta=destination(next,nextFactor).toVector().subtract(target.location().toVector());
            if(!motion.step(delta,safety,-next.pitch()*pitchDirection))return stop();
            carrier.rig().setRecoveryCable(cable);carrier.forceVisualSync();
            if(++step==STEPS)state=loading?State.AT_DECK:State.ON_GROUND;
            return state;
        } catch(RuntimeException e) { return stop(); }
    }
    /** Test-only disconnect response; refuses if safe evacuation fails.
     * Not registered with live quit events and not crash-safe. */
    public boolean parkBothOnOwnerQuitForTest(UUID ownerId) {
        if(!Bukkit.isPrimaryThread() || ownerId==null || state==State.FINISHED || state==State.TEST_PARKED
                || !target.owner().map(ownerId::equals).orElse(false))return false;
        if(state==State.TEST_DRIVING || state==State.PENDING_EVACUATION) {
            state=State.PENDING_EVACUATION;
            if(!motion.evacuateTestDrive())return false;
        }
        if(!manager.parkRecoveryPairForTest(carrier,target))return false;
        state=State.TEST_PARKED;return true;
    }
    /** Only unlock on checked solid ground; a stopped suspended vehicle stays locked. */
    public boolean finishOnGround() {
        if(!Bukkit.isPrimaryThread()||(state!=State.ON_GROUND && state!=State.STOPPED)||!motion.releaseOnGround())return false;
        carrier.rig().setRecoveryCable(List.of());carrier.forceVisualSync();state=State.FINISHED;
        manager.returnOfflineRecoveredVehicle(target);
        return true;
    }
    private static double ease(double t){return t*t*(3D-2D*t);}
    void pause(){
        if(state==State.STOPPED)return;
        pausedState=state;motion.pause();state=State.STOPPED;
    }
    boolean resume(){
        if(state!=State.STOPPED || pausedState==null || !motion.resume())return false;
        state=pausedState;pausedState=null;return true;
    }
    private State stop(){pause();return state;}
    private boolean sameCarrierPose(){
        Location now=carrier.location();
        return origin.getWorld().equals(now.getWorld()) && origin.distanceSquared(now)<1e-8
                && Math.abs(Math.IEEEremainder(now.getYaw()-origin.getYaw(),360D))<.01F;
    }
    private Location destination(RecoveryLoadingPath.Pose pose,double factor){
        return origin.clone().add(-lateral*factor*cos-pose.centerZ()*sin,pose.height()+groundOffset*factor,-lateral*factor*sin+pose.centerZ()*cos);
    }
    private static List<RecoveryCable.Point> cable(RecoveryLoadingPath.Pose pose,double lateral,double groundOffset){
        double c=Math.cos(pose.pitch()),s=Math.sin(pose.pitch());
        double hookY=pose.height()+groundOffset+.005+.35*c+2.43*s, hookZ=pose.centerZ()+.35*s-2.43*c;
        return RecoveryCable.route(new RecoveryCable.Point(0,1.06,.18),new RecoveryCable.Point(0,.99,5.40),
                new RecoveryCable.Point(lateral,hookY,hookZ));
    }
}
