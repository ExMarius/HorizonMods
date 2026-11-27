package com.mrcrayfish.vehicle.paper.vehicle;

import com.mrcrayfish.vehicle.paper.VehiclePlugin;
import com.mrcrayfish.vehicle.paper.recovery.RecoveryTruckPrototype;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.player.PlayerJoinEvent;
import org.bukkit.event.player.PlayerQuitEvent;
import org.bukkit.plugin.java.JavaPlugin;
import java.nio.file.Files;
import java.util.UUID;

/** Disposable command integration probe, excluded from the production jar. */
public final class RecoveryCommandProbe extends JavaPlugin implements Listener {
    private LandVehicle carrier,target; private boolean started;
    private VehiclePlugin main(){return (VehiclePlugin)getServer().getPluginManager().getPlugin("MrCrayfishVehiclePlugin");}
    private java.nio.file.Path marker(){return getDataFolder().toPath().resolve("expected-pair.txt");}
    @Override public void onEnable(){getServer().getPluginManager().registerEvents(this,this);}
    @EventHandler public void join(PlayerJoinEvent event) {
        if(Files.exists(marker())) {
            getServer().getScheduler().runTaskLater(this,()->{
                try {
                    int index=event.getPlayer().getName().equals("RecoveryProbeBot")?0:event.getPlayer().getName().equals("RecoveryOwnerBot")?1:-1;
                    if(index<0)return;
                    UUID id=UUID.fromString(Files.readAllLines(marker()).get(index));var manager=main().vehicles();
                    if(manager.garagedOf(event.getPlayer()).stream().filter(v->v.id().equals(id)).count()!=1||manager.hasVehicleId(id))
                        throw new IllegalStateException("garage missing or duplicate");
                    event.getPlayer().teleport(event.getPlayer().getLocation().clone().add(index==0?12:-12,0,0));
                    if(!manager.retrieve(event.getPlayer(),id))throw new IllegalStateException("garage retrieval failed");
                    getLogger().info("RECOVERY_PAIR_RESTART_OK "+event.getPlayer().getName());
                } catch(Throwable error){fail(error);}
            },20L);
        } else if(!started && event.getPlayer().getName().equals("RecoveryProbeBot")) {
            started=true;getServer().getScheduler().runTaskLater(this,()->start(event.getPlayer()),40L);
        }
    }
    private void start(Player driver) {
        try {
            var owner=getServer().getPlayerExact("RecoveryOwnerBot");if(owner==null)throw new IllegalStateException("missing owner");
            driver.addAttachment(this,"vehicle.use",true);
            var manager=main().vehicles();var base=driver.getLocation();double yaw=Math.toRadians(base.getYaw());
            owner.teleport(base.clone().add(25,0,25));
            carrier=manager.spawn(RecoveryTruckPrototype.create(),base.clone());carrier.setOwner(driver.getUniqueId());
            target=manager.spawn(LandVehicleSpec.DACIA_LOGAN_POLICE,base.clone().add(9.8*Math.sin(yaw),0,-9.8*Math.cos(yaw)));
            target.setOwner(owner.getUniqueId());target.trust(driver.getUniqueId());
            driver.teleport(base.clone().add(10*Math.cos(yaw),0,10*Math.sin(yaw)));
            if(!driver.performCommand("vehicle tractare incarca"))throw new IllegalStateException("loading command failed");
            if(Boolean.getBoolean("horizon.recovery.commandcrash")) {
                getServer().getScheduler().runTaskLater(this,()->crashReady(base),60L);
            } else getServer().getScheduler().runTaskLater(this,()->loaded(driver),200L);
        } catch(Throwable error){fail(error);}
    }
    private void crashReady(org.bukkit.Location base) {
        try {
            double yaw=Math.toRadians(base.getYaw());
            var initial=base.clone().add(9.8*Math.sin(yaw),0,-9.8*Math.cos(yaw));
            if(!carrier.recoveryLocked() || !target.recoveryLocked() || target.location().distanceSquared(initial)<.1)
                throw new IllegalStateException("live command did not reach mid-loading");
            Files.createDirectories(getDataFolder().toPath());
            Files.writeString(marker(),carrier.id()+"\n"+target.id()+"\n");
            getLogger().info("RECOVERY_LIVE_COMMAND_CRASH_READY");
        } catch(Throwable error){fail(error);}
    }
    private void loaded(Player driver) {
        try {
            if(!target.recoveryLocked() || !carrier.recoveryLocked())throw new IllegalStateException("command did not reserve pair");
            var start=carrier.location();var current=target.location();double yaw=Math.toRadians(start.getYaw());
            if(current.distanceSquared(start.clone().add(2.64*Math.sin(yaw),.86,-2.64*Math.cos(yaw)))>.01)
                throw new IllegalStateException("command did not load target on deck");
            if(main().vehicles().retrieve(driver,carrier.id()))throw new IllegalStateException("transit garage retrieval allowed");
            if(!driver.performCommand("vehicle tractare descarca"))throw new IllegalStateException("unload command failed");
            getServer().getScheduler().runTaskLater(this,()->unloaded(driver),200L);
        } catch(Throwable error){fail(error);}
    }
    private void unloaded(Player driver) {
        try {
            if(target.recoveryLocked()||carrier.recoveryLocked())throw new IllegalStateException("command did not release pair after unloading");
            if(!main().vehicles().hasVehicleId(carrier.id())||!main().vehicles().hasVehicleId(target.id()))throw new IllegalStateException("vehicle lost after unload");
            Files.createDirectories(getDataFolder().toPath());Files.writeString(marker(),carrier.id()+"\n"+target.id()+"\n");
            getLogger().info("RECOVERY_COMMAND_ROUND_TRIP_OK");driver.sendMessage("RECOVERY_OWNER_CAN_QUIT");
        } catch(Throwable error){fail(error);}
    }
    @EventHandler public void quit(PlayerQuitEvent event) {
        if(target==null||!event.getPlayer().getName().equals("RecoveryOwnerBot"))return;
        getServer().getScheduler().runTaskLater(this,()->{
            try {if(main().vehicles().hasVehicleId(target.id()))throw new IllegalStateException("owner quit did not park target");
                getLogger().info("RECOVERY_PAIR_QUIT_OK");}catch(Throwable error){fail(error);}
        },20L);
    }
    private void fail(Throwable error){getLogger().severe("RECOVERY_PROBE_FAIL command: "+error);error.printStackTrace();}
}
