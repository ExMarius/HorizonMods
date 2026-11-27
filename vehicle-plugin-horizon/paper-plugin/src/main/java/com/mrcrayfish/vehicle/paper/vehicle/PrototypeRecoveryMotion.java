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
    private boolean closed, halted, testDriving, evacuationPending;
    private final Set<UUID> pendingEvacuees = new HashSet<>();

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
    /** Test-only carrier movement, not collision-safe or crash-safe for production. */
    boolean startTestDrive() {
        if(!Bukkit.isPrimaryThread()||closed||halted||testDriving || !carrier.recoveryMotionLockedBy(token)
                ||!target.recoveryMotionLockedBy(token)||target.recoveryHasPassengers()||carrier.recoveryHasPassengers()
                ||carrier.rig().recoveryRampProgress()!=0D)return false;
        carrier.startRecoveryTestDrive(token);testDriving=true;return true;
    }
    boolean followTestDrive() {
        if(!Bukkit.isPrimaryThread()||closed||halted||!testDriving || !operator.isOnline()
                ||!carrier.recoveryMotionLockedBy(token)||!target.recoveryMotionLockedBy(token)
                ||!carrier.rig().valid()||!target.rig().valid()||target.recoveryHasPassengers()
                ||manager.byId(carrier.id()).orElse(null)!=carrier || manager.byId(target.id()).orElse(null)!=target
                ||manager.trailers().referencesVehicle(carrier.id())||manager.trailers().referencesVehicle(target.id())
                ||carrier.location().getWorld()==null || !carrier.location().getWorld().equals(target.location().getWorld()))return false;
        Location carrierPose=carrier.location(), start=target.location();
        double yaw=Math.toRadians(carrierPose.getYaw());
        Location end=carrierPose.clone().add(2.64*Math.sin(yaw),.86,-2.64*Math.cos(yaw));
        Vector delta=end.toVector().subtract(start.toVector());
        double width=Math.max(5D,target.spec().entityWidth()),height=Math.max(2.5D,target.spec().entityHeight()),half=width/2;
        BoundingBox swept=new BoundingBox(start.getX()-half,start.getY(),start.getZ()-half,
                start.getX()+half,start.getY()+height,start.getZ()+half);
        swept.union(swept.clone().shift(delta));
        World world=start.getWorld();
        for(int x=((int)Math.floor(swept.getMinX()))>>4;x<=((int)Math.floor(swept.getMaxX()))>>4;x++)
            for(int z=((int)Math.floor(swept.getMinZ()))>>4;z<=((int)Math.floor(swept.getMaxZ()))>>4;z++)
                if(!world.isChunkLoaded(x,z))return false;
        Set<UUID> ignored=new HashSet<>();
        carrier.rig().entities().forEach(e -> {ignored.add(e.getUniqueId());e.getPassengers().forEach(p -> ignored.add(p.getUniqueId()));});
        target.rig().entities().forEach(e -> ignored.add(e.getUniqueId()));
        for(Entity entity:world.getNearbyEntities(swept))if(entity.isValid()&&!ignored.contains(entity.getUniqueId()))return false;
        if(delta.lengthSquared()>1e-12 && VehicleCollisionMover.move(world,start,delta,false,width,height,0D,false)
                .movement().distanceSquared(delta)>1e-10)return false;
        target.followRecoveryTestCarrier(token,carrierPose);return true;
    }
    boolean endTestDrive() {
        if(!Bukkit.isPrimaryThread()||!testDriving||carrier.recoveryHasPassengers()||!followTestDrive())return false;
        carrier.stopRecoveryTestDrive(token);testDriving=false;return true;
    }
    /** Stop the experimental carrier and evacuate players before garage fallback.
     * No forced ejection when no suitable location exists. Not production-safe. */
    boolean evacuateTestDrive() {
        if(!Bukkit.isPrimaryThread()||closed||(!testDriving&&!evacuationPending))return false;
        if(testDriving) {
            if(!followTestDrive())return false;
            carrier.freezeRecoveryTestDrive(token);testDriving=false;evacuationPending=true;
        }
        var technical=new HashSet<UUID>();
        carrier.rig().entities().forEach(e -> technical.add(e.getUniqueId()));
        target.rig().entities().forEach(e -> technical.add(e.getUniqueId()));
        for(Entity entity:carrier.rig().entities()) for(Entity passenger:entity.getPassengers()) {
            if(technical.contains(passenger.getUniqueId()))continue;
            if(!(passenger instanceof Player p)||!p.isOnline())return false;
            pendingEvacuees.add(p.getUniqueId());
        }
        var riders=new java.util.ArrayList<Player>();
        for(UUID id:pendingEvacuees) {
            Player player=Bukkit.getPlayer(id);
            if(player==null||!player.isOnline())return false;
            riders.add(player);
        }
        var destinations=new java.util.ArrayList<Location>();
        for(Player rider:riders) {
            Location safe=findTestExit(carrier.location(),technical,riders,destinations);
            if(safe==null)return false;
            destinations.add(safe);
        }
        for(int i=0;i<riders.size();i++) {
            Player rider=riders.get(i);
            Entity mount=rider.getVehicle();
            if(mount!=null && (!technical.contains(mount.getUniqueId()) || !rider.leaveVehicle()))return false;
            if(!rider.teleport(destinations.get(i)))return false;
            pendingEvacuees.remove(rider.getUniqueId());
        }
        if(carrier.recoveryHasPassengers())return false;
        evacuationPending=false;return true;
    }
    private Location findTestExit(Location base,Set<UUID> own,java.util.List<Player> riders,java.util.List<Location> chosen) {
        World world=base.getWorld();if(world==null)return null;
        for(int radius=5;radius<=9;radius++)for(int dx=-radius;dx<=radius;dx++)for(int dz=-radius;dz<=radius;dz++) {
            if(Math.max(Math.abs(dx),Math.abs(dz))!=radius)continue;
            int x=base.getBlockX()+dx,z=base.getBlockZ()+dz;
            if(!world.isChunkLoaded(x>>4,z>>4))continue;
            for(int dy=1;dy>=-2;dy--) {
                int y=base.getBlockY()+dy;
                if(y<=world.getMinHeight()||y+1>=world.getMaxHeight())continue;
                var floor=world.getBlockAt(x,y-1,z);var feet=world.getBlockAt(x,y,z);var head=world.getBlockAt(x,y+1,z);
                if(!floor.getType().isSolid() || !feet.getType().isAir() || !head.getType().isAir())continue;
                String type=floor.getType().name();
                if(type.contains("MAGMA")||type.contains("CAMPFIRE")||type.contains("CACTUS")||type.contains("BERRY")||type.contains("FIRE"))continue;
                boolean full=floor.getCollisionShape().getBoundingBoxes().stream().anyMatch(b -> b.getMinX()<=0 && b.getMinZ()<=0
                        && b.getMaxX()>=1 && b.getMaxZ()>=1 && b.getMaxY()>=1);
                if(!full)continue;
                Location place=new Location(world,x+.5,y,z+.5,base.getYaw(),0);
                if(!world.getWorldBorder().isInside(place))continue;
                if(chosen.stream().anyMatch(p -> p.distanceSquared(place)<4))continue;
                BoundingBox space=new BoundingBox(x+.2,y,z+.2,x+.8,y+1.9,z+.8);
                boolean blocked=world.getNearbyEntities(space).stream().anyMatch(e -> e.isValid()&&!own.contains(e.getUniqueId())
                        && riders.stream().noneMatch(p -> p.getUniqueId().equals(e.getUniqueId())));
                if(!blocked)return place;
            }
        }
        return null;
    }
    UUID lockToken() { return token; }

    /** The reservation caller uses this only if no movement was attempted and
     * the durable snapshot was not written. */
    void abortUnmoved() {
        if(!Bukkit.isPrimaryThread() || closed || testDriving || halted) throw new IllegalStateException("Cannot abort recovery lock");
        target.endRecoveryMotion(token); carrier.endRecoveryMotion(token); closed=true;
    }

    boolean canReleaseOnGround(){
        if(!Bukkit.isPrimaryThread()||closed||testDriving||!carrier.recoveryMotionLockedBy(token)||!target.recoveryMotionLockedBy(token))return false;
        Location where=target.location();
        if(where.getWorld()==null || target.recoveryHasPassengers() || carrier.recoveryHasPassengers()
                || Math.abs(target.recoveryPitchDegrees())>.1F || !groundSupportsFootprint(where))return false;
        BoundingBox point=new BoundingBox(where.getX()-.1,where.getY()-.1,where.getZ()-.1,where.getX()+.1,where.getY()+.1,where.getZ()+.1);
        return authority.allows(operator,where.getWorld(),point);
    }
    /** Test cleanup only: release both locks on solid ground. No secured transport. */
    public boolean releaseOnGround(){
        if(!canReleaseOnGround())return false;
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
