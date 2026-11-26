package com.mrcrayfish.vehicle.paper.vehicle;

import com.mrcrayfish.vehicle.paper.physics.VehicleCollisionMover;
import com.mrcrayfish.vehicle.paper.recovery.RecoveryInterlock;
import com.mrcrayfish.vehicle.paper.recovery.RecoveryTruckPrototype;
import org.bukkit.Bukkit;
import org.bukkit.Location;
import org.bukkit.World;
import org.bukkit.entity.Entity;
import org.bukkit.entity.Player;
import org.bukkit.util.BoundingBox;
import org.bukkit.util.Vector;

import java.util.HashSet;
import java.util.Set;
import java.util.UUID;

/**
 * Disposable-server prototype ONLY, never registered as a command. Moves a real
 * LandVehicle by small collision-checked increments; it is not ready for live
 * operation because the authority and complete linkage adapters, path planner,
 * crash recovery and safe release are not connected. No autonomous driver.
 */
public final class PrototypeRecoveryMotion {
    /** Implementations must fail closed for unverified claims and regions. */
    @FunctionalInterface public interface Authority { boolean allows(Player operator, World world, BoundingBox swept); }
    private final VehicleManager manager;
    private final LandVehicle carrier,target;
    private final Player operator;
    private final Authority authority;
    private final UUID token=UUID.randomUUID();
    private final RecoveryInterlock interlock=new RecoveryInterlock();
    private boolean closed, halted;

    private PrototypeRecoveryMotion(VehicleManager manager,LandVehicle carrier,LandVehicle target,Player operator,Authority authority){
        this.manager=manager;this.carrier=carrier;this.target=target;this.operator=operator;this.authority=authority;
    }
    /** SAFETY is a snapshot supplied by the test harness; production adapter does not yet exist. */
    public static PrototypeRecoveryMotion begin(VehicleManager manager,LandVehicle carrier,LandVehicle target,
                                                 Player operator,Authority authority,RecoveryInterlock.Safety safety){
        if(!Bukkit.isPrimaryThread()||manager==null||carrier==null||target==null||operator==null||authority==null||safety==null
                ||!RecoveryTruckPrototype.ID.equals(carrier.spec().id()) || carrier==target
                ||manager.byId(carrier.id()).orElse(null)!=carrier || manager.byId(target.id()).orElse(null)!=target
                ||!carrier.rig().valid() || !target.rig().valid()
                ||target.recoveryHasPassengers() || carrier.recoveryHasPassengers()
                ||!operator.isOnline() || !carrier.canDrive(operator) || !target.canDrive(operator)
                ||carrier.rig().recoveryRampProgress()!=1D || carrier.horizontalSpeed()>.01D
                ||carrier.location().getWorld()==null || !carrier.location().getWorld().equals(target.location().getWorld())
                ||!manager.trailers().recoveryLinksKnown()
                ||manager.trailers().referencesVehicle(target.id()) || manager.trailers().referencesVehicle(carrier.id())) return null;
        PrototypeRecoveryMotion run=new PrototypeRecoveryMotion(manager,carrier,target,operator,authority);
        if(run.interlock.openRamps(carrier.id(),target.id(),operator.getUniqueId(),RecoveryInterlock.Mode.WINCH,safety)!=RecoveryInterlock.Denial.NONE
                ||run.interlock.rampsReady(safety)!=RecoveryInterlock.Denial.NONE
                ||run.interlock.startMovement(safety)!=RecoveryInterlock.Denial.NONE) return null;
        if(!carrier.beginRecoveryMotion(run.token))return null;
        if(!target.beginRecoveryMotion(run.token)){carrier.endRecoveryMotion(run.token);return null;}
        return run;
    }
    /** One step, zero on any denial. The caller must re-supply all live safety checks. */
    public boolean step(Vector delta,RecoveryInterlock.Safety safety){
        return step(delta,safety,0D);
    }
    /** Visual pitch only. The caller must independently check the full tilted body. */
    public boolean step(Vector delta,RecoveryInterlock.Safety safety,double pitchRadians){
        if(halted || closed)return false;
        boolean accepted;
        try { accepted=checkedStep(delta,safety,pitchRadians); }
        catch (RuntimeException ex) { halted=true; return false; }
        if(!accepted)halted=true; // explicit intervention required, never auto-resume
        return accepted;
    }
    private boolean checkedStep(Vector delta,RecoveryInterlock.Safety safety,double pitchRadians){
        if(!Double.isFinite(pitchRadians)||Math.abs(pitchRadians)>Math.PI/4
                ||!Bukkit.isPrimaryThread()||closed||delta==null||!Double.isFinite(delta.getX())||!Double.isFinite(delta.getY())||!Double.isFinite(delta.getZ())
                ||delta.lengthSquared()<1e-12 ||delta.lengthSquared()>.08D*.08D || !operator.isOnline()
                || !carrier.canDrive(operator) || !target.canDrive(operator)
                ||!carrier.rig().valid() || !target.rig().valid()
                ||!carrier.recoveryMotionLockedBy(token)||!target.recoveryMotionLockedBy(token)
                ||manager.byId(carrier.id()).orElse(null)!=carrier||manager.byId(target.id()).orElse(null)!=target
                ||!manager.trailers().recoveryLinksKnown()
                ||manager.trailers().referencesVehicle(carrier.id())||manager.trailers().referencesVehicle(target.id())
                ||carrier.rig().recoveryRampProgress()!=1D||target.recoveryHasPassengers()||carrier.recoveryHasPassengers()
                ||target.onJack()||target.jackId()!=null||carrier.onJack()||carrier.jackId()!=null
                ||interlock.checkMovement(safety)!=RecoveryInterlock.Denial.NONE) return false;
        Location start=target.location();World world=start.getWorld();
        if(world==null||!world.equals(carrier.location().getWorld()))return false;
        // Conservative square footprint: body length/width must be independently measured.
        double width=Math.max(5D,target.spec().entityWidth()),height=Math.max(2.5D,target.spec().entityHeight());
        double half=width/2;
        BoundingBox startBox=new BoundingBox(start.getX()-half,start.getY(),start.getZ()-half,
                start.getX()+half,start.getY()+height,start.getZ()+half);
        BoundingBox endBox=startBox.clone().shift(delta);
        BoundingBox swept=startBox.clone().union(endBox);
        int minX=((int)Math.floor(swept.getMinX()))>>4,maxX=((int)Math.floor(swept.getMaxX()))>>4;
        int minZ=((int)Math.floor(swept.getMinZ()))>>4,maxZ=((int)Math.floor(swept.getMaxZ()))>>4;
        for(int x=minX;x<=maxX;x++)for(int z=minZ;z<=maxZ;z++)if(!world.isChunkLoaded(x,z))return false;
        if(!authority.allows(operator,world,swept.clone()))return false;
        Set<UUID> own=new HashSet<>();target.rig().entities().forEach(e->own.add(e.getUniqueId()));
        carrier.rig().entities().forEach(e->own.add(e.getUniqueId()));
        for(Entity e:world.getNearbyEntities(swept))if(e.isValid()&&!own.contains(e.getUniqueId()))return false;
        var moved=VehicleCollisionMover.move(world,start,delta,false,width,height,0D,false).movement();
        if(moved.distanceSquared(delta)>1e-10)return false;
        target.applyRecoveryMotion(token,delta,(float)-Math.toDegrees(pitchRadians));return true;
    }
    /** Test cleanup only: release both locks on solid ground. No secured transport. */
    public boolean releaseOnGround(){
        if(!Bukkit.isPrimaryThread()||closed||!carrier.recoveryMotionLockedBy(token)||!target.recoveryMotionLockedBy(token))return false;
        Location where=target.location();
        if(where.getWorld()==null || target.recoveryHasPassengers() || carrier.recoveryHasPassengers()
                || Math.abs(target.recoveryPitchDegrees())>.1F || !groundSupportsFootprint(where))return false;
        BoundingBox point=new BoundingBox(where.getX()-.1,where.getY()-.1,where.getZ()-.1,where.getX()+.1,where.getY()+.1,where.getZ()+.1);
        if(!authority.allows(operator,where.getWorld(),point))return false;
        target.endRecoveryMotion(token);carrier.endRecoveryMotion(token);closed=true;return true;
    }
    /** Conservative support under centre and four corners, with no chunk loads.
     * This is still only an experimental release check, not terrain physics. */
    private boolean groundSupportsFootprint(Location location) {
        World world=location.getWorld();
        if(world==null)return false;
        double half=Math.max(5D,target.spec().entityWidth())/2-.1;
        for(double[] offset:new double[][]{{0,0},{-half,-half},{-half,half},{half,-half},{half,half}}) {
            double x=location.getX()+offset[0],z=location.getZ()+offset[1],y=location.getY();
            int bx=(int)Math.floor(x),bz=(int)Math.floor(z),by=(int)Math.floor(y-.001);
            if(by<world.getMinHeight()||by>=world.getMaxHeight()||!world.isChunkLoaded(bx>>4,bz>>4))return false;
            var block=world.getBlockAt(bx,by,bz);
            boolean supported=false;
            for(var shape:block.getCollisionShape().getBoundingBoxes()) {
                var box=shape.clone().shift(bx,by,bz);
                if(x>=box.getMinX()&&x<=box.getMaxX()&&z>=box.getMinZ()&&z<=box.getMaxZ()
                        && box.getMaxY()>=y-.05 && box.getMaxY()<=y+.001) {supported=true;break;}
            }
            if(!supported)return false;
        }
        return true;
    }
}
