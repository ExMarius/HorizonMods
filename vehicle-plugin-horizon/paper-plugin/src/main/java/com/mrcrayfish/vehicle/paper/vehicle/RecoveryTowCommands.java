package com.mrcrayfish.vehicle.paper.vehicle;

import com.mrcrayfish.vehicle.paper.VehiclePlugin;
import com.mrcrayfish.vehicle.paper.recovery.RecoveryInterlock;
import com.mrcrayfish.vehicle.paper.recovery.RecoveryRearApproach;
import com.mrcrayfish.vehicle.paper.recovery.RecoveryTargetPolicy;
import org.bukkit.Bukkit;
import org.bukkit.Location;
import org.bukkit.entity.Player;
import org.bukkit.scheduler.BukkitTask;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/** Command-driven recovery. Geometry, crash handling and full road collision safety
 * still require validation on a disposable server before production use. */
public final class RecoveryTowCommands {
    private final VehiclePlugin plugin;
    private final VehicleManager manager;
    private final Map<UUID,Operation> operations=new HashMap<>();
    private static final RecoveryInterlock.Safety SAFETY = new RecoveryInterlock.Safety(
            true,true,true,true,true,true,true,true,true,true,true,true,true,true,true,false,true,false,false,false);
    public RecoveryTowCommands(VehiclePlugin plugin,VehicleManager manager){this.plugin=plugin;this.manager=manager;}

    public void execute(Player player,String action) {
        if(!player.hasPermission("vehicle.use")) {player.sendMessage("Nu ai permisiunea vehicle.use.");return;}
        LandVehicle carrier=manager.vehicles().stream()
                .filter(v -> "horizon_recovery_prototype".equals(v.spec().id()) && canOperateCarrier(v,player))
                .filter(v -> v.location().getWorld()!=null && v.location().getWorld().equals(player.getWorld()))
                .filter(v -> v.driver().filter(player::equals).isPresent() || v.location().distanceSquared(player.getLocation())<=16*16)
                .min(java.util.Comparator.<LandVehicle>comparingInt(v -> v.driver().filter(player::equals).isPresent()?0:1)
                        .thenComparingDouble(v -> v.location().distanceSquared(player.getLocation()))).orElse(null);
        if(carrier==null){
            boolean nearby=manager.vehicles().stream().anyMatch(v -> "horizon_recovery_prototype".equals(v.spec().id())
                    && player.getWorld().equals(v.location().getWorld()) && v.location().distanceSquared(player.getLocation())<=16*16);
            player.sendMessage(nearby ? "Nu ai permisiune pentru platforma din apropiere."
                    : "Nu găsesc o platformă activă în această lume la maximum 16 blocuri.");
            return;
        }
        // The winch requires an empty carrier for collision and evacuation safety.
        if(carrier.driver().filter(player::equals).isPresent()) {
            if(carrier.horizontalSpeed()>.01 || !player.leaveVehicle()) {
                player.sendMessage("Oprește platforma pentru a coborî înainte de manevră.");return;
            }
            player.sendMessage("Ai coborât din platformă pentru manevra troliului.");
        }
        if(action.equalsIgnoreCase("incarca")) start(player,carrier);
        else if(action.equalsIgnoreCase("descarca")) unload(player,carrier);
        else player.sendMessage("Utilizare: /vehicle tractare incarca|descarca");
    }
    static boolean canOperateCarrier(LandVehicle carrier,Player player) {
        return player.isOp() || carrier.canDrive(player);
    }
    private void start(Player player,LandVehicle carrier) {
        if(operations.containsKey(carrier.id()) || carrier.occupied() || carrier.horizontalSpeed()>.01) {
            player.sendMessage("Oprește platforma, coboară și încheie transportul anterior.");return;
        }
        Location base=carrier.location();
        LandVehicle target=manager.vehicles().stream().filter(v -> v!=carrier && RecoveryTargetPolicy.supports(v.spec()))
                .filter(v -> v.location().getWorld()!=null && v.location().getWorld().equals(base.getWorld()))
                .filter(v -> {
                    Location at=v.location();
                    return RecoveryRearApproach.selectable(RecoveryRearApproach.offset(
                            at.getX()-base.getX(),at.getY()-base.getY(),at.getZ()-base.getZ(),base.getYaw()));
                })
                .min(java.util.Comparator.comparingDouble(v -> v.location().distanceSquared(base))).orElse(null);
        if(target==null){player.sendMessage("Nu există niciun vehicul mic sau mediu compatibil în spatele platformei la maximum 10 blocuri.");return;}
        if(!target.canDrive(player) && !player.isOp()) {
            player.sendMessage("Nu ai drepturi asupra celui mai apropiat vehicul.");return;
        }
        carrier.rig().setRecoveryRampProgress(1);carrier.forceVisualSync();
        var route=LiveRecoveryRoute.begin(manager,carrier,target,player,(actor,world,box)->actor.isOnline(),SAFETY);
        if(route==null) {carrier.rig().setRecoveryRampProgress(0);carrier.forceVisualSync();player.sendMessage("Vehicul găsit, dar traseul verificat cere aliniere dreaptă pe sol în spatele rampelor, aproape de limita de 10 blocuri. Verifică și ocupanții/cuplajele.");return;}
        try {
            if(!manager.reserveGarageTransit(carrier,target,player,route.lockToken())) {
                route.abortUnmoved();carrier.rig().setRecoveryRampProgress(0);carrier.forceVisualSync();
                player.sendMessage("Rezervarea în garaj a fost refuzată.");return;
            }
        } catch(IOException error) {
            // The rename outcome may be uncertain; do not unlock or overwrite.
            player.sendMessage("Eroare la salvare: vehiculele rămân blocate pentru siguranță.");
            plugin.getLogger().severe("[Recovery] Reservation failed: "+error.getMessage());return;
        }
        Operation operation=new Operation(carrier,target,route,player);
        operations.put(carrier.id(),operation);
        operation.task=Bukkit.getScheduler().runTaskTimer(plugin,operation::tick,1L,1L);
        player.sendMessage("Troliul a început încărcarea.");
    }
    private void unload(Player player,LandVehicle carrier) {
        Operation operation=operations.get(carrier.id());
        if(operation==null || operation.route.state()!=LiveRecoveryRoute.State.TEST_DRIVING) {player.sendMessage("Nu există o mașină fixată pe această platformă.");return;}
        if((!operation.target.canDrive(player) && !player.isOp()) || carrier.occupied() || carrier.horizontalSpeed()>.01) {
            player.sendMessage("Oprește platforma, coboară și verifică drepturile asupra mașinii.");return;
        }
        if(!operation.route.endTestDrive() || !operation.route.beginUnload()) {player.sendMessage("Descărcarea a fost refuzată; verifică zona.");return;}
        player.sendMessage("Troliul a început descărcarea.");
    }
    private final class Operation {
        final LandVehicle carrier,target;final LiveRecoveryRoute route;final Player operator;BukkitTask task;
        Operation(LandVehicle carrier,LandVehicle target,LiveRecoveryRoute route,Player operator) {
            this.carrier=carrier;this.target=target;this.route=route;this.operator=operator;
        }
        void tick() {
            try {
                if(!manager.recoveryPairActive(carrier.id())) {finishTask();return;}
                var state=route.state();
                if(state==LiveRecoveryRoute.State.LOADING || state==LiveRecoveryRoute.State.UNLOADING) {
                    state=route.tick(SAFETY);
                    if(state==LiveRecoveryRoute.State.AT_DECK) {
                        if(!route.beginTestDrive()) {stop();return;}
                        operator.sendMessage("Mașina este fixată; poți conduce platforma.");
                    } else if(state==LiveRecoveryRoute.State.ON_GROUND) {
                        if(!route.canReleaseOnGround() || !manager.commitRecoveryUnload(carrier,target,route.lockToken())) {stop();return;}
                        if(!route.finishOnGround())throw new IllegalStateException("Recovery release failed after commit");
                        operator.sendMessage("Mașina a fost descărcată.");finishTask();
                    } else if(state==LiveRecoveryRoute.State.STOPPED) stop();
                } else if(state==LiveRecoveryRoute.State.TEST_DRIVING && !route.tickTestDrive()) stop();
            } catch(Exception error) {
                plugin.getLogger().warning("[Recovery] Manevra oprită: "+error.getMessage());stop();
            }
        }
        void stop() {
            operator.sendMessage("Manevra s-a oprit; vehiculele sunt trimise în garaj în siguranță.");
            manager.recoveryOwnerQuit(carrier.owner().orElse(operator.getUniqueId()));finishTask();
        }
        void finishTask(){if(task!=null)task.cancel();operations.remove(carrier.id(),this);}
    }
}
