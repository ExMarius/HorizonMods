package com.mrcrayfish.vehicle.paper.vehicle;

import com.mrcrayfish.vehicle.paper.VehiclePlugin;
import com.mrcrayfish.vehicle.paper.recovery.RecoveryTruckPrototype;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.player.PlayerJoinEvent;
import org.bukkit.event.player.PlayerQuitEvent;
import org.bukkit.entity.Player;
import org.bukkit.plugin.java.JavaPlugin;
import java.nio.file.Files;
import java.util.UUID;

/** Disposable Paper fixture: exercises live reservation and live quit listener.
 * Not included in the production JAR and not a full towing command. */
public final class RecoveryLiveProbe extends JavaPlugin implements Listener {
    private LandVehicle carrier, target;
    private UUID token;
    private boolean started;
    private org.bukkit.Location fallbackSpawn;
    private VehiclePlugin main() { return (VehiclePlugin)getServer().getPluginManager().getPlugin("MrCrayfishVehiclePlugin"); }
    private java.nio.file.Path marker(){return getDataFolder().toPath().resolve("expected-pair.txt");}
    @Override public void onEnable(){getServer().getPluginManager().registerEvents(this,this);}

    @EventHandler public void join(PlayerJoinEvent event) {
        if(Files.exists(marker())) {
            getServer().getScheduler().runTaskLater(this,()->{
                try {
                    int index=event.getPlayer().getName().equals("RecoveryProbeBot")?0:event.getPlayer().getName().equals("RecoveryOwnerBot")?1:-1;
                    if(index<0)return;
                    UUID id=UUID.fromString(Files.readAllLines(marker()).get(index));
                    var manager=main().vehicles();
                    if(manager.garagedOf(event.getPlayer()).stream().filter(v->v.id().equals(id)).count()!=1 || manager.hasVehicleId(id))
                        throw new IllegalStateException("recovered vehicle missing or duplicate");
                    event.getPlayer().teleport(event.getPlayer().getLocation().clone().add(index==0?12:-12,0,0));
                    if(!manager.retrieve(event.getPlayer(),id) || manager.byId(id).isEmpty())throw new IllegalStateException("retrieve failed");
                    getLogger().info("RECOVERY_PAIR_RESTART_OK "+event.getPlayer().getName());
                } catch(Throwable e){fail(e);}
            },20L);
        } else if(!started && event.getPlayer().getName().equals("RecoveryProbeBot")) {
            started=true;
            getServer().getScheduler().runTaskLater(this,()->start(event.getPlayer()),40L);
        }
    }
    private void start(Player driver) {
        try {
            var manager=main().vehicles();var owner=getServer().getPlayerExact("RecoveryOwnerBot");
            if(owner==null)throw new IllegalStateException("missing target owner");
            var origin=driver.getLocation(); owner.teleport(origin.clone().add(25,0,25));
            carrier=manager.spawn(RecoveryTruckPrototype.create(),origin.clone()); carrier.setOwner(driver.getUniqueId());
            target=manager.spawn(LandVehicleSpec.DACIA_LOGAN_POLICE,origin.clone().add(0,0,10));
            target.setOwner(owner.getUniqueId()); target.trust(driver.getUniqueId());
            token=UUID.randomUUID();
            if(!carrier.mount(driver))throw new IllegalStateException("driver mount failed");
            if(!(boolean)invoke(carrier,"beginRecoveryCarrier",new Class<?>[]{UUID.class,Player.class},token,driver)
                    || !(boolean)invoke(target,"beginRecoveryMotion",new Class<?>[]{UUID.class},token))throw new IllegalStateException("lock failed");
            if(!(boolean)invoke(manager,"reserveGarageTransit",new Class<?>[]{LandVehicle.class,LandVehicle.class,Player.class,UUID.class},carrier,target,driver,token))
                throw new IllegalStateException("live reservation refused");
            if(manager.retrieve(driver,carrier.id())||manager.retrieve(owner,target.id()))throw new IllegalStateException("reserved garage retrieval permitted");
            invoke(carrier,"startRecoveryTestDrive",new Class<?>[]{UUID.class},token);
            if(driver.getVehicle()==null)throw new IllegalStateException("driver was not retained during reservation");
            if(Boolean.getBoolean("horizon.recovery.fallbacktest")) {
                var world=origin.getWorld(); int x=origin.getBlockX(),y=origin.getBlockY(),z=origin.getBlockZ();
                fallbackSpawn=new org.bukkit.Location(world,x+40.5,y,z+.5);
                world.getChunkAt(fallbackSpawn).load();
                world.getBlockAt(x+40,y-1,z).setType(org.bukkit.Material.STONE,false);
                world.getBlockAt(x+40,y,z).setType(org.bukkit.Material.AIR,false);
                world.getBlockAt(x+40,y+1,z).setType(org.bukkit.Material.AIR,false);
                world.setSpawnLocation(fallbackSpawn);
                // Remove safe floors from every locally searched candidate height.
                for(int dx=-9;dx<=9;dx++)for(int dz=-9;dz<=9;dz++) {
                    int radius=Math.max(Math.abs(dx),Math.abs(dz));
                    if(radius<5 || radius>9)continue;
                    for(int dy=-3;dy<=-1;dy++)world.getBlockAt(x+dx,y+dy,z+dz).setType(org.bukkit.Material.LAVA,false);
                }
            }
            Files.createDirectories(getDataFolder().toPath());
            Files.writeString(marker(),carrier.id()+"\n"+target.id()+"\n");
            driver.sendMessage("RECOVERY_OWNER_CAN_QUIT");
        } catch(Throwable e){fail(e);}
    }
    @EventHandler public void quit(PlayerQuitEvent event) {
        if(carrier==null || !event.getPlayer().getName().equals("RecoveryOwnerBot"))return;
        getServer().getScheduler().runTaskLater(this,()->{
            try {
                var manager=main().vehicles(); var driver=getServer().getPlayerExact("RecoveryProbeBot");
                if(manager.hasVehicleId(carrier.id())||manager.hasVehicleId(target.id()) || driver==null || driver.getVehicle()!=null)
                    throw new IllegalStateException("live quit did not safely evacuate and park pair");
                var exit=driver.getLocation();
                if(!exit.clone().subtract(0,.1,0).getBlock().getType().isSolid() || !exit.getBlock().getType().isAir()
                        || !exit.clone().add(0,1,0).getBlock().getType().isAir())throw new IllegalStateException("unsafe driver exit");
                if(fallbackSpawn!=null) {
                    if(exit.getWorld()!=fallbackSpawn.getWorld() || exit.distanceSquared(fallbackSpawn)>1.0)
                        throw new IllegalStateException("driver did not reach validated world spawn");
                    getLogger().info("RECOVERY_LIVE_FALLBACK_OK");
                }
                getLogger().info("RECOVERY_PAIR_QUIT_OK");
            } catch(Throwable e){fail(e);}
        },fallbackSpawn==null?40L:140L);
    }
    private static Object invoke(Object instance,String name,Class<?>[] types,Object... args)throws Exception {
        var method=instance.getClass().getDeclaredMethod(name,types);
        method.setAccessible(true);
        try {return method.invoke(instance,args);}
        catch(java.lang.reflect.InvocationTargetException e) {
            if(e.getCause() instanceof Exception cause)throw cause;
            throw e;
        }
    }
    private void fail(Throwable error){getLogger().severe("RECOVERY_PROBE_FAIL live: "+error);error.printStackTrace();}
}
