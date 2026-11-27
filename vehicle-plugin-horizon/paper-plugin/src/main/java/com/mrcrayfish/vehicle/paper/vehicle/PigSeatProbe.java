package com.mrcrayfish.vehicle.paper.vehicle;

import com.mrcrayfish.vehicle.paper.physics.VehicleCollisionMover;
import io.papermc.paper.entity.TeleportFlag;
import org.bukkit.Bukkit;
import org.bukkit.Color;
import org.bukkit.Location;
import org.bukkit.Material;
import org.bukkit.NamespacedKey;
import org.bukkit.World;
import org.bukkit.entity.Pig;
import org.bukkit.entity.Entity;
import org.bukkit.entity.EntityType;
import org.bukkit.entity.ItemDisplay;
import org.bukkit.entity.Player;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.meta.LeatherArmorMeta;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.scheduler.BukkitTask;
import org.bukkit.util.BoundingBox;
import org.bukkit.util.Vector;

import java.util.UUID;
import java.util.logging.Level;

/** Disposable in-game hierarchy probe, not a normal vehicle or production physics. */
final class PigSeatProbe {
    private final JavaPlugin plugin;
    private ItemDisplay root;
    private Pig pig;
    private UUID rider;
    private BukkitTask task;
    private int ticks;
    private boolean ending;

    PigSeatProbe(JavaPlugin plugin) { this.plugin = plugin; }
    boolean active() { return root != null; }

    void start(Player player) {
        if (!player.isOp() || active() || player.isInsideVehicle() || !player.isOnGround()) {
            player.sendMessage("[PorcTest] Necesită OP, un singur test activ și să fii pe sol, în afara altui vehicul.");
            return;
        }
        Location location = player.getLocation().clone();
        location.setPitch(0F);
        World world = location.getWorld();
        if (world == null || !floorSafe(location)) {
            player.sendMessage("[PorcTest] Alege o suprafață plană și solidă, într-o zonă liberă."); return;
        }
        try {
            ItemStack model = new ItemStack(Material.LEATHER_HORSE_ARMOR);
            LeatherArmorMeta meta = (LeatherArmorMeta) model.getItemMeta();
            meta.setColor(Color.fromRGB(0xF9FFFE));
            meta.setItemModel(new NamespacedKey("vehicle", "go_kart_body"));
            model.setItemMeta(meta);
            root = world.spawn(location, ItemDisplay.class, display -> {
                display.setItemStack(model);
                display.setItemDisplayTransform(ItemDisplay.ItemDisplayTransform.NONE);
                display.setPersistent(false); display.setInvulnerable(true);
                display.setTeleportDuration(3);
                display.addScoreboardTag("mcv_pig_probe");
            });
            Entity spawned = world.spawnEntity(location, EntityType.PIG);
            if (!(spawned instanceof Pig found)) { spawned.remove(); throw new IllegalStateException("Pig type unavailable"); }
            pig = found;
            pig.setPersistent(false); pig.setInvulnerable(true); pig.setSilent(true); pig.setGravity(false);
            pig.setInvisible(true); pig.setAI(false); pig.setCollidable(false);
            pig.addScoreboardTag("mcv_pig_probe");
            rider = player.getUniqueId(); ticks = 0; ending = false;
            if (!root.addPassenger(pig) || !pig.addPassenger(player)) throw new IllegalStateException("Passenger hierarchy refused");
            task = Bukkit.getScheduler().runTaskTimer(plugin, this::tick, 1L, 1L);
            player.sendMessage("[PorcTest] Prototip separat: scaun-porc invizibil. W/S mișcă lent; A/D virează numai în mers.");
            player.sendMessage("[PorcTest] Nu este o mașină normală. Shift sau /vehicle testporc oprit încheie testul; maxim 2 minute.");
        } catch (RuntimeException error) {
            plugin.getLogger().log(Level.WARNING, "[PorcTest] Could not start", error);
            player.sendMessage("[PorcTest] Nu am putut crea ierarhia; revin la starea normală.");
            end();
        }
    }

    void stop(Player actor) {
        if (!active()) { actor.sendMessage("[PorcTest] Nu există un test activ."); return; }
        ending = true;
        actor.sendMessage("[PorcTest] Oprire; dacă ești pe scaun, coboară cu Shift.");
        end();
    }

    void shutdown() { ending = true; end(); }

    private void tick() {
        try { tickSafely(); }
        catch (RuntimeException error) {
            plugin.getLogger().log(Level.WARNING, "[PorcTest] Test stopped", error);
            ending = true;
            end();
        }
    }

    private void tickSafely() {
        if (root == null || pig == null) { end(); return; }
        Player player = Bukkit.getPlayer(rider);
        if (++ticks > 20 * 120 || ending || !root.isValid() || !pig.isValid() || player == null
                || !player.isOnline() || !player.isOp() || player.isDead() || !pig.getPassengers().contains(player)
                || pig.getVehicle() != root) {
            ending = true; end(); return;
        }
        var input = player.getCurrentInput();
        int drive = (input.isForward() ? 1 : 0) - (input.isBackward() ? 1 : 0);
        int turn = (input.isRight() ? 1 : 0) - (input.isLeft() ? 1 : 0);
        float seatYaw = root.getLocation().getYaw();
        pig.setRotation(seatYaw, 0F);
        pig.setBodyYaw(seatYaw);
        if (drive == 0) return; // The prototype does not steer while stationary.
        Location from = root.getLocation();
        Location to = from.clone();
        if (drive != 0) to.setYaw(from.getYaw() + turn * drive * 2F);
        double radians = Math.toRadians(to.getYaw());
        Vector requested = new Vector(-Math.sin(radians) * drive * .055D, 0D, Math.cos(radians) * drive * .055D);
        World world = from.getWorld();
        if (world == null || !world.isChunkLoaded(to.getBlockX() >> 4, to.getBlockZ() >> 4)) return;
        var movement = VehicleCollisionMover.move(world, from, requested, true, 1.8D, 2.0D, 0D, false).movement();
        to.add(movement);
        BoundingBox area = new BoundingBox(Math.min(from.getX(), to.getX()) - 1, from.getY(), Math.min(from.getZ(), to.getZ()) - 1,
                Math.max(from.getX(), to.getX()) + 1, from.getY() + 2, Math.max(from.getZ(), to.getZ()) + 1);
        if (!floorSafe(to) || !world.getWorldBorder().isInside(to) || world.getNearbyEntities(area).stream()
                .anyMatch(e -> e.isValid() && e != root && e != pig && e != player)) return;
        if (!root.teleport(to, TeleportFlag.EntityState.RETAIN_PASSENGERS)) {
            ending = true; player.sendMessage("[PorcTest] Mutarea a fost refuzată; testul se încheie."); end();
        } else {
            pig.setRotation(to.getYaw(), 0F);
            pig.setBodyYaw(to.getYaw());
        }
    }

    private static boolean floorSafe(Location location) {
        World world = location.getWorld();
        if (world == null) return false;
        for (double dx : new double[]{-.9D, .9D}) for (double dz : new double[]{-.9D, .9D}) {
            Location p = location.clone().add(dx, -.05D, dz);
            if (!world.isChunkLoaded(p.getBlockX() >> 4, p.getBlockZ() >> 4)
                    || !p.getBlock().getType().isSolid()) return false;
        }
        return true;
    }

    private void end() {
        if (pig != null && pig.isValid() && !pig.getPassengers().isEmpty()) {
            // Never delete the rider's mount if Paper refuses a safe dismount.
            for (Entity passenger : pig.getPassengers()) if (passenger instanceof Player player && player.isOnline()) player.leaveVehicle();
            if (!pig.getPassengers().isEmpty()) {
                if (task == null && plugin.isEnabled()) task = Bukkit.getScheduler().runTaskTimer(plugin, this::tick, 20L, 20L);
                return;
            }
        }
        if (task != null) { task.cancel(); task = null; }
        if (pig != null) pig.remove();
        if (root != null) root.remove();
        pig = null; root = null; rider = null; ending = false;
    }
}
