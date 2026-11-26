package com.mrcrayfish.vehicle.paper.recoveryprobe;

import com.mrcrayfish.vehicle.paper.VehiclePlugin;
import com.mrcrayfish.vehicle.paper.recovery.RecoveryTruckPrototype;
import com.mrcrayfish.vehicle.paper.vehicle.LandVehicle;
import com.mrcrayfish.vehicle.paper.vehicle.LandVehicleSpec;
import com.mrcrayfish.vehicle.paper.vehicle.PrototypeRecoveryMotion;
import com.mrcrayfish.vehicle.paper.recovery.RecoveryInterlock;
import org.bukkit.entity.ItemDisplay;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.player.PlayerJoinEvent;
import org.bukkit.plugin.java.JavaPlugin;
import java.util.HashMap;
import java.util.Map;

/** Disposable test-only plugin; never included in the production plugin jar. */
public final class RecoveryProbe extends JavaPlugin implements Listener {
    private boolean exercised;
    private final Map<java.util.UUID,LandVehicle> demoVehicles=new HashMap<>();
    @Override public boolean onCommand(org.bukkit.command.CommandSender sender, org.bukkit.command.Command cmd, String label, String[] args){
        if(!(sender instanceof org.bukkit.entity.Player player) || !player.hasPermission("recoveryprobe.use")) return true;
        var main=(VehiclePlugin)getServer().getPluginManager().getPlugin("MrCrayfishVehiclePlugin");
        if(main==null || args.length!=1) { sender.sendMessage("RECOVERY_DEMO_USAGE spawn|open|close|remove"); return true; }
        var vehicle=demoVehicles.get(player.getUniqueId());
        switch(args[0].toLowerCase(java.util.Locale.ROOT)) {
            case "spawn" -> {
                if(vehicle!=null){sender.sendMessage("RECOVERY_DEMO_ALREADY_EXISTS");break;}
                vehicle=main.vehicles().spawn(RecoveryTruckPrototype.create(),player.getLocation().clone().add(0,0,3));
                demoVehicles.put(player.getUniqueId(),vehicle);
                sender.sendMessage("RECOVERY_DEMO_SPAWNED");
                getLogger().info("RECOVERY_DEMO_SPAWNED");
            }
            case "open", "close" -> {
                if(vehicle==null || vehicle.occupied() || vehicle.horizontalSpeed()>.01D){sender.sendMessage("RECOVERY_DEMO_DENIED");break;}
                boolean open=args[0].equalsIgnoreCase("open");
                vehicle.rig().setRecoveryRampProgress(open?1D:0D);vehicle.forceVisualSync();
                sender.sendMessage(open?"RECOVERY_DEMO_OPEN":"RECOVERY_DEMO_CLOSE");
                getLogger().info(open?"RECOVERY_DEMO_OPEN":"RECOVERY_DEMO_CLOSE");
            }
            case "remove" -> {
                if(vehicle==null || !main.vehicles().remove(vehicle)){sender.sendMessage("RECOVERY_DEMO_DENIED");break;}
                demoVehicles.remove(player.getUniqueId());sender.sendMessage("RECOVERY_DEMO_REMOVED");getLogger().info("RECOVERY_DEMO_REMOVED");
            }
            default -> sender.sendMessage("RECOVERY_DEMO_USAGE spawn|open|close|remove");
        }
        return true;
    }
    @EventHandler public void quit(org.bukkit.event.player.PlayerQuitEvent event){ cleanupDemo(event.getPlayer().getUniqueId()); }
    @Override public void onDisable(){for(var id:java.util.List.copyOf(demoVehicles.keySet()))cleanupDemo(id);}
    private void cleanupDemo(java.util.UUID id){
        var main=(VehiclePlugin)getServer().getPluginManager().getPlugin("MrCrayfishVehiclePlugin");
        LandVehicle vehicle=demoVehicles.remove(id);
        if(main!=null && vehicle!=null) main.vehicles().remove(vehicle);
    }
    @Override public void onEnable(){getServer().getPluginManager().registerEvents(this,this);}
    @EventHandler public void join(PlayerJoinEvent event){
        if(exercised)return; exercised=true;
        getServer().getScheduler().runTaskLater(this,()->{
            LandVehicle v=null;
            try {
                VehiclePlugin main=(VehiclePlugin)getServer().getPluginManager().getPlugin("MrCrayfishVehiclePlugin");
                if(main==null||!main.isEnabled())throw new IllegalStateException("main plugin missing");
                v=main.vehicles().spawn(RecoveryTruckPrototype.create(),event.getPlayer().getLocation());
                v.forceVisualSync();
                if(!v.rig().valid())throw new IllegalStateException("invalid rig");
                Map<String,Integer> counts=new HashMap<>();
                for(var entity:v.rig().entities())if(entity instanceof ItemDisplay display){
                    var meta=display.getItemStack().getItemMeta();
                    if(meta!=null&&meta.getItemModel()!=null)counts.merge(meta.getItemModel().toString(),1,Integer::sum);
                }
                expect(counts,"vehicle:horizon_service_cab",1);
                expect(counts,"vehicle:horizon_service_flatbed",1);
                expect(counts,"vehicle:horizon_service_steering",1);
                expect(counts,"vehicle:horizon_service_wheel",4);
                expect(counts,"vehicle:horizon_service_ramp",2);
                expect(counts,"vehicle:horizon_service_cable",2);
                var cable=v.rig().entities().stream().filter(e->e instanceof ItemDisplay)
                    .map(e->(ItemDisplay)e).filter(d->d.getItemStack().getItemMeta()!=null
                        && new org.bukkit.NamespacedKey("vehicle","horizon_service_cable").equals(d.getItemStack().getItemMeta().getItemModel())).toList();
                if(cable.stream().anyMatch(ItemDisplay::isVisibleByDefault))throw new IllegalStateException("cable visible before attaching");
                var outlet=new com.mrcrayfish.vehicle.paper.recovery.RecoveryCable.Point(0,1.06,.18);
                var roller=new com.mrcrayfish.vehicle.paper.recovery.RecoveryCable.Point(0,.99,5.40);
                var hook=new com.mrcrayfish.vehicle.paper.recovery.RecoveryCable.Point(0,.35,7.37);
                v.rig().setRecoveryCable(com.mrcrayfish.vehicle.paper.recovery.RecoveryCable.route(outlet,roller,hook));
                v.forceVisualSync();
                if(cable.stream().anyMatch(d->!d.isVisibleByDefault()))throw new IllegalStateException("cable segments not visible");
                var t=cable.get(0).getTransformation();
                var actual=t.getLeftRotation().transform(new org.joml.Vector3f(0,1,0));
                var expected=new org.joml.Vector3f(0,-.07F,-5.22F).normalize();
                if(actual.dot(expected)<.999F || Math.abs(t.getScale().y-4F*(float)Math.hypot(.07,5.22))>.01F)
                    throw new IllegalStateException("cable alignment or length wrong");
                v.rig().setRecoveryCable(java.util.List.of());v.forceVisualSync();
                if(cable.stream().anyMatch(ItemDisplay::isVisibleByDefault))throw new IllegalStateException("cable not detached");
                // Exercise both real ItemDisplay transforms, then refold before cleanup.
                var ramps=v.rig().entities().stream().filter(e->e instanceof ItemDisplay)
                    .map(e->(ItemDisplay)e)
                    .filter(d->d.getItemStack().getItemMeta()!=null
                        && new org.bukkit.NamespacedKey("vehicle","horizon_service_ramp").equals(d.getItemStack().getItemMeta().getItemModel())).toList();
                var before=ramps.get(0).getTransformation().getLeftRotation();
                v.rig().setRecoveryRampProgress(1.0);v.forceVisualSync();
                for(var ramp:ramps){
                    var after=ramp.getTransformation().getLeftRotation();
                    if(Math.abs(before.dot(after))>.999F)throw new IllegalStateException("ramp did not animate");
                }
                v.rig().setRecoveryRampProgress(0);v.forceVisualSync();
                if(v.spec().seats().size()!=2)throw new IllegalStateException("seat count");
                // Exercise the actual player/horse seat path on disposable Paper.
                if(!v.mount(event.getPlayer())||!v.occupied()||v.rig().seatCarriers().size()!=1)
                    throw new IllegalStateException("player failed to mount prototype");
                // First dismount before testing a real, unoccupied target vehicle.
                var mount=event.getPlayer().getVehicle();
                if(mount instanceof org.bukkit.entity.Horse horse){
                    var scale=horse.getAttribute(org.bukkit.attribute.Attribute.SCALE);
                    if(scale!=null)scale.setBaseValue(1D);
                }
                event.getPlayer().leaveVehicle();
                LandVehicle target=main.vehicles().spawn(LandVehicleSpec.DACIA_LOGAN_POLICE,event.getPlayer().getLocation().clone().add(0,0,10));
                try {
                    v.rig().setRecoveryRampProgress(1);
                    var safety=new RecoveryInterlock.Safety(true,true,true,true,true,true,true,true,true,true,true,true,true,true,true,false,true,false,false,false);
                    target.setOwner(java.util.UUID.randomUUID());
                    if(PrototypeRecoveryMotion.begin(main.vehicles(),v,target,event.getPlayer(),(a,w,b)->true,safety)!=null)
                        throw new IllegalStateException("moved someone else's car");
                    target.setOwner(null);
                    // Test actual trailer graph entries, not a UI checkbox or Safety flag.
                    var tm=main.vehicles().trailers();
                    for(var spec:java.util.List.of(
                            com.mrcrayfish.vehicle.paper.vehicle.TrailerSpec.TRACTOR_TRAILER,
                            com.mrcrayfish.vehicle.paper.vehicle.TrailerSpec.UTB_PLOUGH,
                            com.mrcrayfish.vehicle.paper.vehicle.TrailerSpec.DISC_GD32)) {
                        var trailer=tm.spawn(spec, target.location().clone().add(12,0,0));
                        try {
                            trailer.attach(com.mrcrayfish.vehicle.paper.runtime.PaperTrailer.PullerType.VEHICLE,target.id());
                            if(!tm.referencesVehicle(target.id()) || PrototypeRecoveryMotion.begin(main.vehicles(),v,target,event.getPlayer(),(a,w,b)->true,safety)!=null)
                                throw new IllegalStateException("accepted attached "+spec.id());
                            trailer.detach(false);
                            if(tm.referencesVehicle(target.id()))throw new IllegalStateException("stale detached "+spec.id());
                        } finally {tm.remove(trailer);}
                    }
                    var vehicleTrailer=tm.spawn(com.mrcrayfish.vehicle.paper.vehicle.TrailerSpec.VEHICLE_TRAILER, target.location().clone().add(12,0,0));
                    try {
                        vehicleTrailer.setLoadedVehicleId(target.id());
                        if(!tm.referencesVehicle(target.id()) || PrototypeRecoveryMotion.begin(main.vehicles(),v,target,event.getPlayer(),(a,w,b)->true,safety)!=null)
                            throw new IllegalStateException("accepted vehicle already on a trailer");
                        vehicleTrailer.setLoadedVehicleId(null);
                    } finally {tm.remove(vehicleTrailer);}
                    var run=PrototypeRecoveryMotion.begin(main.vehicles(),v,target,event.getPlayer(),(a,w,b)->true,safety);
                    if(run==null)throw new IllegalStateException("recovery lock failed");
                    if(main.vehicles().pickUp(target)!=null || main.vehicles().remove(target)
                            || main.vehicles().park(target,event.getPlayer())!=com.mrcrayfish.vehicle.paper.vehicle.VehicleManager.ParkResult.OCCUPIED)
                        throw new IllegalStateException("locked vehicle can be picked up, removed or garaged");
                    var loc=target.location();var blocker=loc.clone().add(0,0,2.5).getBlock();var originalBlock=blocker.getBlockData();
                    blocker.setType(org.bukkit.Material.STONE,false);
                    try {
                        if(run.step(new org.bukkit.util.Vector(0,0,.05),safety))throw new IllegalStateException("moved through block");
                    } finally {blocker.setBlockData(originalBlock,false);}
                    if(run.step(new org.bukkit.util.Vector(0,0,.05),safety))throw new IllegalStateException("resumed automatically after blockage");
                    if(!run.releaseOnGround())throw new IllegalStateException("blocked run did not unlock");
                    run=PrototypeRecoveryMotion.begin(main.vehicles(),v,target,event.getPlayer(),(a,w,b)->true,safety);
                    if(run==null)throw new IllegalStateException("second recovery lock failed");
                    var start=target.location();
                    if(!run.step(new org.bukkit.util.Vector(0,0,.05),safety))throw new IllegalStateException("clear movement refused");
                    if(Math.abs(target.location().getZ()-start.getZ()-.05)>1e-6)throw new IllegalStateException("wrong movement");
                    if(!run.releaseOnGround())throw new IllegalStateException("clear run did not unlock");
                } finally {main.vehicles().remove(target);}
                // Exercise the same manager entry point used by the /vehicle disc coupling command.
                var permission=event.getPlayer().addAttachment(this,"vehicle.plough",true);
                var tractor=main.vehicles().spawn(LandVehicleSpec.UTB_650,event.getPlayer().getLocation().clone().add(2,0,0));
                var harrow=main.vehicles().trailers().spawn(com.mrcrayfish.vehicle.paper.vehicle.TrailerSpec.DISC_GD32,tractor.location());
                try {
                    var safety=new RecoveryInterlock.Safety(true,true,true,true,true,true,true,true,true,true,true,true,true,true,true,false,true,false,false,false);
                    var lock=PrototypeRecoveryMotion.begin(main.vehicles(),v,tractor,event.getPlayer(),(a,w,b)->true,safety);
                    if(lock==null)throw new IllegalStateException("tractor recovery lock failed");
                    main.vehicles().trailers().coupleHarrow(event.getPlayer());
                    if(harrow.pullerType()!=com.mrcrayfish.vehicle.paper.runtime.PaperTrailer.PullerType.NONE)
                        throw new IllegalStateException("harrow coupled during recovery lock");
                    if(!lock.releaseOnGround())throw new IllegalStateException("tractor lock cleanup failed");
                    main.vehicles().trailers().coupleHarrow(event.getPlayer());
                    if(harrow.pullerType()!=com.mrcrayfish.vehicle.paper.runtime.PaperTrailer.PullerType.VEHICLE || !tractor.id().equals(harrow.pullerId()))
                        throw new IllegalStateException("normal harrow coupling did not succeed");
                    if(PrototypeRecoveryMotion.begin(main.vehicles(),v,tractor,event.getPlayer(),(a,w,b)->true,safety)!=null)
                        throw new IllegalStateException("coupled tractor accepted for recovery");
                } finally {
                    main.vehicles().trailers().remove(harrow);
                    main.vehicles().remove(tractor);
                    event.getPlayer().removeAttachment(permission);
                }
                startTimedRoundTrip(main,event.getPlayer());
                // Offline bot only; the disposable plugin is never packaged into production.
                if(event.getPlayer().getName().equals("RecoveryProbeBot")) event.getPlayer().addAttachment(this,"recoveryprobe.use",true);
                getLogger().info("RECOVERY_PROBE_OK models="+counts+" both ramp transforms and cable display checked; seat, actual trailer graph, normal harrow coupling and guarded single vehicle movement checked; no full gameplay or visual test");
            } catch(Throwable e){ getLogger().severe("RECOVERY_PROBE_FAIL "+e); e.printStackTrace(); }
            finally{
                VehiclePlugin main=(VehiclePlugin)getServer().getPluginManager().getPlugin("MrCrayfishVehiclePlugin");
                if(v!=null&&main!=null)main.vehicles().remove(v);
            }
        },40L);
    }
    /** Test-only: ideal flat ground, fake claims adapter and no secured transport. */
    private void startTimedRoundTrip(VehiclePlugin main, org.bukkit.entity.Player player) {
        var home=player.getLocation();
        var truck=main.vehicles().spawn(RecoveryTruckPrototype.create(),home);
        truck.rig().setRecoveryRampProgress(1);
        var base=truck.location();
        double yaw=Math.toRadians(base.getYaw()),sin=Math.sin(yaw),cos=Math.cos(yaw);
        player.teleport(base.clone().add(10*cos,0,10*sin));
        // The authored +Z rear is mapped to Paper item-space -Z by the rig.
        var carStart=base.clone().add(9.8*sin,0,-9.8*cos);
        var car=main.vehicles().spawn(LandVehicleSpec.DACIA_LOGAN_POLICE,carStart);
        var safety=new RecoveryInterlock.Safety(true,true,true,true,true,true,true,true,true,true,true,true,true,true,true,false,true,false,false,false);
        var motion=PrototypeRecoveryMotion.begin(main.vehicles(),truck,car,player,(a,w,b)->true,safety);
        if(motion==null)throw new IllegalStateException("timed round trip lock failed");
        var ignored=new java.util.HashSet<java.util.UUID>();
        truck.rig().entities().forEach(e -> ignored.add(e.getUniqueId()));
        car.rig().entities().forEach(e -> ignored.add(e.getUniqueId()));
        var lineStart=new com.mrcrayfish.vehicle.paper.recovery.RecoveryCable.Point(base.getX()+12,base.getY()+1.5,base.getZ()+12);
        var lineEnd=new com.mrcrayfish.vehicle.paper.recovery.RecoveryCable.Point(base.getX()+15,base.getY()+1.5,base.getZ()+12);
        var obstruct=base.clone().add(13,1,12).getBlock();
        var old=obstruct.getBlockData();
        obstruct.setType(org.bukkit.Material.STONE,false);
        try {
            if(com.mrcrayfish.vehicle.paper.recovery.RecoveryCableWorldCheck.clear(base.getWorld(),java.util.List.of(lineStart,lineEnd),.018,ignored))
                throw new IllegalStateException("cable crossed a solid block");
        } finally { obstruct.setBlockData(old,false); }
        var body=car.rig().entities().stream().filter(e -> e instanceof ItemDisplay).map(e -> (ItemDisplay)e).findFirst().orElseThrow();
        var levelRotation=new org.joml.Quaternionf(body.getTransformation().getLeftRotation());
        new org.bukkit.scheduler.BukkitRunnable() {
            int ticks;
            boolean observedTilt;
            @Override public void run() {
                try {
                    ticks++;
                    int direction=ticks<=180?0:1;
                    int step=direction==0?ticks:ticks-180;
                    double from=direction==0?9.8:2.64,to=direction==0?2.64:9.8;
                    var pose=com.mrcrayfish.vehicle.paper.recovery.RecoveryLoadingPath.sample(from,to,3.3,step/180D);
                    var destination=base.clone().add(pose.centerZ()*sin,pose.height(),-pose.centerZ()*cos);
                    // Preview tow-eye, rotated about the car root using the same
                    // estimated pitch as the rig. It is not a measured in-game hook.
                    double c=Math.cos(pose.pitch()), sinPitch=Math.sin(pose.pitch());
                    double hookY=pose.height()+.005+.35*c+2.43*sinPitch;
                    double hookZ=pose.centerZ()+.35*sinPitch-2.43*c;
                    var cable=com.mrcrayfish.vehicle.paper.recovery.RecoveryCable.route(
                            new com.mrcrayfish.vehicle.paper.recovery.RecoveryCable.Point(0,1.06,.18),
                            new com.mrcrayfish.vehicle.paper.recovery.RecoveryCable.Point(0,.99,5.40),
                            new com.mrcrayfish.vehicle.paper.recovery.RecoveryCable.Point(0,hookY,hookZ));
                    if(!com.mrcrayfish.vehicle.paper.recovery.RecoveryCable.clearsLevelBed(cable,.18,5.35,.86,.018))
                        throw new IllegalStateException("cable intersects level bed at "+ticks);
                    // Model +Z rear maps to Paper -Z; transform each point to world.
                    var worldCable=cable.stream().map(p -> new com.mrcrayfish.vehicle.paper.recovery.RecoveryCable.Point(
                            base.getX()-p.x()*cos+p.z()*sin,base.getY()+p.y(),base.getZ()-p.x()*sin-p.z()*cos)).toList();
                    if(!com.mrcrayfish.vehicle.paper.recovery.RecoveryCableWorldCheck.clear(base.getWorld(),worldCable,.018,ignored))
                        throw new IllegalStateException("world obstructs cable at "+ticks);
                    truck.rig().setRecoveryCable(cable);truck.forceVisualSync();
                    var delta=destination.toVector().subtract(car.location().toVector());
                    if(!motion.step(delta,safety,pose.pitch()))throw new IllegalStateException("timed movement blocked at "+ticks);
                    if(pose.pitch()>.05 && Math.abs(levelRotation.dot(body.getTransformation().getLeftRotation()))<.9999F) observedTilt=true;
                    if(ticks==180 && Math.abs(car.location().getY()-base.getY()-.86)>1e-5)
                        throw new IllegalStateException("car did not reach deck height");
                    if(ticks==360) {
                        if(car.location().distance(carStart)>1e-5 || !motion.releaseOnGround())
                            throw new IllegalStateException("round trip did not return to ground");
                        if(!observedTilt)throw new IllegalStateException("vehicle rig did not pitch on ramp");
                        truck.rig().setRecoveryCable(java.util.List.of());
                        cancel();main.vehicles().remove(car);main.vehicles().remove(truck);player.teleport(home);
                        getLogger().info("RECOVERY_ROUND_TRIP_OK ticks="+ticks+" tilted rig and level-bed cable clearance checked");
                    }
                } catch(Throwable error) {
                    cancel();getLogger().severe("RECOVERY_PROBE_FAIL timed round trip: "+error);error.printStackTrace();
                    // Never forcibly release an unsafe mid-air lock, even in the fixture.
                    player.teleport(home);
                }
            }
        }.runTaskTimer(this,1L,1L);
    }
    private static void expect(Map<String,Integer> counts,String name,int count){
        if(counts.getOrDefault(name,0)!=count)throw new IllegalStateException(name+" count="+counts.getOrDefault(name,0));
    }
}
