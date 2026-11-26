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
                getLogger().info("RECOVERY_PROBE_OK models="+counts+" both ramp transforms and cable display checked; seat, actual trailer graph and guarded single vehicle movement checked; no full gameplay or visual test");
            } catch(Throwable e){ getLogger().severe("RECOVERY_PROBE_FAIL "+e); e.printStackTrace(); }
            finally{
                VehiclePlugin main=(VehiclePlugin)getServer().getPluginManager().getPlugin("MrCrayfishVehiclePlugin");
                if(v!=null&&main!=null)main.vehicles().remove(v);
            }
        },40L);
    }
    private static void expect(Map<String,Integer> counts,String name,int count){
        if(counts.getOrDefault(name,0)!=count)throw new IllegalStateException(name+" count="+counts.getOrDefault(name,0));
    }
}
