package com.mrcrayfish.vehicle.paper.recoveryprobe;

import com.mrcrayfish.vehicle.paper.VehiclePlugin;
import com.mrcrayfish.vehicle.paper.recovery.RecoveryTruckPrototype;
import com.mrcrayfish.vehicle.paper.vehicle.LandVehicle;
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
                getLogger().info("RECOVERY_PROBE_OK models="+counts+" both ramp transforms checked; seat definitions=2; visual/gameplay not tested");
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
