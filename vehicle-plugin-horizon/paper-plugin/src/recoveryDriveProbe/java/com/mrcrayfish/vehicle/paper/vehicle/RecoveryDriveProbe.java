package com.mrcrayfish.vehicle.paper.vehicle;

import com.mrcrayfish.vehicle.paper.VehiclePlugin;
import com.mrcrayfish.vehicle.paper.recovery.RecoveryTruckSpec;
import org.bukkit.GameMode;
import org.bukkit.Location;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.player.PlayerJoinEvent;
import org.bukkit.plugin.java.JavaPlugin;

/** Disposable Paper control check; excluded from the production plugin. */
public final class RecoveryDriveProbe extends JavaPlugin implements Listener {
    private boolean started;
    @Override public void onEnable(){getServer().getPluginManager().registerEvents(this,this);}
    @EventHandler public void join(PlayerJoinEvent event){
        if(started)return;started=true;
        getServer().getScheduler().runTaskLater(this,()->run(event.getPlayer()),40L);
    }
    private void run(Player player){
        try {
            var plugin=(VehiclePlugin)getServer().getPluginManager().getPlugin("MrCrayfishVehiclePlugin");
            var origin=player.getLocation().clone();origin.setYaw(0);origin.setPitch(0);
            player.setGameMode(GameMode.CREATIVE);
            var carrier=plugin.vehicles().spawn(RecoveryTruckSpec.create(),origin);
            carrier.setOwner(player.getUniqueId());carrier.setEngineInstalled(true);carrier.setWheelsInstalled(true);
            if(!carrier.mount(player))throw new IllegalStateException("Cannot mount test driver");
            getServer().getScheduler().runTaskLater(this,()->{
                var before=carrier.location().clone();
                player.sendMessage("RECOVERY_DRIVE_FORWARD");
                getServer().getScheduler().runTaskLater(this,()->{
                    try {
                        Location end=carrier.location();
                        if(end.getZ()-before.getZ()>=-.20)throw new IllegalStateException("W did not move toward visible front: "+(end.getZ()-before.getZ()));
                        getLogger().info("RECOVERY_FORWARD_OK");
                        player.sendMessage("RECOVERY_DRIVE_TURN");
                        getServer().getScheduler().runTaskLater(this,()->{
                            try {
                                if(Math.abs(Math.IEEEremainder(carrier.location().getYaw()-end.getYaw(),360D))<1)
                                    throw new IllegalStateException("Steering did not change vehicle heading");
                                getLogger().info("RECOVERY_TURN_OK");player.sendMessage("RECOVERY_DRIVE_DONE");
                            } catch(Throwable e){fail(e);}
                        },50L);
                    } catch(Throwable e){fail(e);}
                },50L);
            },20L);
        } catch(Throwable e){fail(e);}
    }
    private void fail(Throwable e){getLogger().severe("RECOVERY_PROBE_FAIL drive: "+e);e.printStackTrace();}
}
