package ro.exmarius.horizonvehicles.kart;

import io.papermc.paper.entity.TeleportFlag;
import com.mrcrayfish.vehicle.paper.physics.VehicleCollisionMover;
import com.mrcrayfish.vehicle.paper.vehicle.LandVehicleSpec;
import org.bukkit.attribute.Attribute;
import org.bukkit.util.Vector;
import net.kyori.adventure.text.Component;
import org.bukkit.Location;
import org.bukkit.World;
import org.bukkit.entity.ArmorStand;
import org.bukkit.entity.Interaction;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.player.PlayerInteractEntityEvent;
import org.bukkit.plugin.java.JavaPlugin;
import java.util.ArrayList;
import java.util.List;

/** Temporary single-seat prototype. Vehicles are removed on plugin shutdown. */
public final class GoKartManager implements Listener {
    private final JavaPlugin plugin;
    private final List<Kart> karts = new ArrayList<>();
    public GoKartManager(JavaPlugin plugin) { this.plugin = plugin; }

    public boolean spawn(Player player) {
        Location root = player.getLocation().clone();
        root.add(root.getDirection().setY(0).normalize().multiply(2.5));
        if (!clear(root)) { player.sendMessage("Nu este loc liber pentru Go-Kart."); return false; }
        GoKartRig rig = null;
        ArmorStand seat = null;
        Interaction hitbox = null;
        try {
            rig = GoKartRig.spawn(plugin, root);
            seat = root.getWorld().spawn(seatLocation(root), ArmorStand.class, entity -> {
                entity.setInvisible(true); entity.setSmall(true); entity.setGravity(false);
                entity.setInvulnerable(true); entity.setSilent(true); entity.setPersistent(false);
                entity.setRemoveWhenFarAway(false);
                var scale = entity.getAttribute(Attribute.SCALE);
                if (scale != null) scale.setBaseValue(0.0625);
            });
            hitbox = root.getWorld().spawn(root, Interaction.class, entity -> {
                entity.setInteractionWidth(1.8f); entity.setInteractionHeight(1.3f);
                entity.setResponsive(true); entity.setPersistent(false);
            });
            karts.add(new Kart(root, rig, seat, hitbox));
            player.sendMessage("Go-Kart experimental creat. Click dreapta pentru a urca; Shift pentru a cobori.");
            return true;
        } catch (Exception error) {
            if (rig != null) rig.remove();
            if (seat != null) seat.remove();
            if (hitbox != null) hitbox.remove();
            plugin.getLogger().warning("Go-Kart spawn failed: " + error);
            player.sendMessage("Nu am putut crea Go-Kart-ul; verifică logul serverului.");
            return false;
        }
    }

    @EventHandler(ignoreCancelled = true)
    public void onInteract(PlayerInteractEntityEvent event) {
        for (Kart kart : karts) {
            if (event.getRightClicked().equals(kart.hitbox) || event.getRightClicked().equals(kart.seat)) {
                event.setCancelled(true);
                if (!kart.seat.getPassengers().isEmpty()) { event.getPlayer().sendMessage("Scaunul este ocupat."); return; }
                if (!kart.seat.addPassenger(event.getPlayer())) event.getPlayer().sendMessage("Nu te-ai putut urca.");
                return;
            }
        }
    }

    public boolean removeNearest(Player player) {
        Kart nearest = null; double distance = 36;
        for (Kart kart : karts) {
            if (!kart.root.getWorld().equals(player.getWorld())) continue;
            double d = kart.root.distanceSquared(player.getLocation());
            if (d < distance) { nearest = kart; distance = d; }
        }
        if (nearest == null) return false;
        nearest.remove(); karts.remove(nearest); return true;
    }

    public boolean refuelNearest(Player player) {
        for (Kart kart : karts) {
            if (kart.root.getWorld().equals(player.getWorld()) && kart.root.distanceSquared(player.getLocation()) < 36) {
                kart.motion.refuel(GoKartMotion.CAPACITY); return true;
            }
        }
        return false;
    }

    public void tick() {
        for (Kart kart : new ArrayList<>(karts)) {
            if (!kart.seat.isValid() || !kart.hitbox.isValid()) { kart.remove(); karts.remove(kart); continue; }
            kart.tick();
        }
    }
    public void removeAll() { karts.forEach(Kart::remove); karts.clear(); }

    private static Location seatLocation(Location root) {
        LandVehicleSpec.Point p = LandVehicleSpec.GO_KART.seats().stream()
                .filter(LandVehicleSpec.Seat::driver).findFirst().orElseThrow().sourceOffset();
        double angle = Math.toRadians(root.getYaw());
        return root.clone().add(p.x() * Math.cos(angle) - p.z() * Math.sin(angle),
                p.y() + LandVehicleSpec.RIDER_HEIGHT_CORRECTION - 0.7 * 0.0625,
                p.x() * Math.sin(angle) + p.z() * Math.cos(angle));
    }

    /** Coarse conservative occupancy check; refuses unloaded chunks and blocks other than passable ones. */
    private static boolean clear(Location location) {
        World world = location.getWorld();
        for (double x : new double[]{-.72, 0, .72}) for (double z : new double[]{-.72, 0, .72}) {
            for (double y : new double[]{.08, .9, 1.65}) {
                Location p = location.clone().add(x, y, z);
                if (p.getBlockY() < world.getMinHeight() || p.getBlockY() >= world.getMaxHeight()
                        || !world.isChunkLoaded(p.getBlockX() >> 4, p.getBlockZ() >> 4)
                        || !p.getBlock().isPassable()) return false;
            }
        }
        return true;
    }

    private static final class Kart {
        Location root; final GoKartRig rig; final ArmorStand seat; final Interaction hitbox;
        final GoKartMotion motion; double fallVelocity; boolean onGround = true;
        Kart(Location root, GoKartRig rig, ArmorStand seat, Interaction hitbox) {
            this.root = root.clone(); this.rig = rig; this.seat = seat; this.hitbox = hitbox;
            this.motion = new GoKartMotion(root.getYaw());
        }
        void tick() {
            Player driver = seat.getPassengers().stream().filter(Player.class::isInstance).map(Player.class::cast).findFirst().orElse(null);
            var input = driver == null ? null : driver.getCurrentInput();
            int throttle = input == null ? 0 : (input.isForward() ? 1 : 0) - (input.isBackward() ? 1 : 0);
            int steering = input == null ? 0 : (input.isRight() ? 1 : 0) - (input.isLeft() ? 1 : 0);
            var step = motion.tick(throttle, steering, input != null && input.isJump());
            LandVehicleSpec spec = LandVehicleSpec.GO_KART;
            fallVelocity = Math.max(-0.45, fallVelocity - .04);
            Vector requested = new Vector(step.dx(), fallVelocity, step.dz());
            // Never cause chunk loads from collision sampling at a chunk boundary.
            Location end = root.clone().add(requested);
            for (double x : new double[]{-2, 2}) for (double z : new double[]{-2, 2}) {
                Location p = end.clone().add(x, 0, z);
                if (!root.getWorld().isChunkLoaded(p.getBlockX() >> 4, p.getBlockZ() >> 4)) {
                    motion.stop(); return;
                }
            }
            var result = VehicleCollisionMover.move(root.getWorld(), root, requested, onGround,
                    spec.entityWidth(), spec.entityHeight(), spec.stepHeight(), false);
            Vector actual = result.movement();
            Location next = root.clone().add(actual);
            next.setYaw((float) step.yawDegrees());
            onGround = result.onGround();
            if (result.verticalCollision()) fallVelocity = 0;
            if (Math.abs(actual.getX() - requested.getX()) > 0.001
                    || Math.abs(actual.getZ() - requested.getZ()) > 0.001) motion.stop();
            Location seatTarget = seatLocation(next);
            if (!seat.teleport(seatTarget, TeleportFlag.EntityState.RETAIN_PASSENGERS)) { motion.stop(); return; }
            root = next; hitbox.teleport(root); rig.move(root);
            if (driver != null && driver.getTicksLived() % 20 == 0)
                driver.sendActionBar(Component.text(String.format("Go-Kart | Combustibil: %.0f%%", step.fuel())));
        }
        void remove() { seat.eject(); seat.remove(); hitbox.remove(); rig.remove(); }
    }
}
