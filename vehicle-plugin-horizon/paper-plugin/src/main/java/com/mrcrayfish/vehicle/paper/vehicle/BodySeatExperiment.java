package com.mrcrayfish.vehicle.paper.vehicle;

import org.bukkit.Bukkit;
import org.bukkit.entity.Player;

import java.util.UUID;

/** Opt-in visual seat experiment, scoped to one operator and vehicle only. */
final class BodySeatExperiment {
    private static final long DURATION_NANOS = 120_000_000_000L;
    private LandVehicle vehicle;
    private UUID driver;
    private long expires;

    boolean active() { return vehicle != null; }

    void start(Player player, LandVehicle target) {
        if (active()) { player.sendMessage("[CorpTest] Există deja un test activ."); return; }
        if (!Bukkit.isPrimaryThread() || !player.isOp() || target == null || target.recoveryLocked()
                || target.driver().filter(player::equals).isEmpty()) {
            player.sendMessage("[CorpTest] Intră la volan ca OP, fără tractare activă."); return;
        }
        vehicle = target;
        driver = player.getUniqueId();
        expires = System.nanoTime() + DURATION_NANOS;
        target.rig().setExperimentalDriverYaw(driver);
        player.sendMessage("[CorpTest] Activ pentru șoferul și vehiculul actual, maximum două minute.");
        player.sendMessage("[CorpTest] Încerc orientarea corpului pe server; F5 poate rămâne controlat de client.");
        player.sendMessage("[CorpTest] Nu controlează camera. Oprește cu /vehicle corptest oprit.");
    }

    void stop(Player actor) {
        if (!active()) { actor.sendMessage("[CorpTest] Nu există un test activ."); return; }
        UUID previous = driver;
        clear();
        actor.sendMessage("[CorpTest] Test dezactivat.");
        Player other = Bukkit.getPlayer(previous);
        if (other != null && other.isOnline() && !other.equals(actor)) other.sendMessage("[CorpTest] Test oprit de administrator.");
    }

    void clear() {
        if (vehicle != null) vehicle.rig().setExperimentalDriverYaw(null);
        vehicle = null; driver = null;
    }

    void tick(VehicleManager manager) {
        if (!active()) return;
        Player player = Bukkit.getPlayer(driver);
        if (player == null || !player.isOnline() || !player.isOp() || player.isDead()
                || manager.byId(vehicle.id()).orElse(null) != vehicle || vehicle.recoveryLocked()
                || vehicle.driver().filter(player::equals).isEmpty() || System.nanoTime() - expires >= 0L) {
            clear();
            if (player != null && player.isOnline()) player.sendMessage("[CorpTest] Test încheiat: expirare, coborâre sau schimbare vehicul.");
            return;
        }
        // Paper exposes the server-side body yaw; client rendering may ignore or overwrite it.
        // Do not change the player's head/view yaw or send teleport packets.
        float yaw = vehicle.location().getYaw();
        if (Float.isFinite(yaw)) player.setBodyYaw(yaw);
    }
}
