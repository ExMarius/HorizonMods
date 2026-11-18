package ro.exmarius.horizonvehicles.kart;

import io.papermc.paper.entity.TeleportFlag;
import com.mrcrayfish.vehicle.paper.physics.VehicleCollisionMover;
import com.mrcrayfish.vehicle.paper.physics.SurfaceProfile;
import com.mrcrayfish.vehicle.paper.mechanic.WheelType;
import com.mrcrayfish.vehicle.paper.vehicle.LandVehicleSpec;
import org.bukkit.util.Vector;
import net.kyori.adventure.text.Component;
import org.bukkit.Location;
import org.bukkit.World;
import org.bukkit.entity.ArmorStand;
import org.bukkit.entity.Boat;
import org.bukkit.entity.EntityType;
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
        Boat seat = null;
        ArmorStand blocker = null;
        Interaction hitbox = null;
        boolean nested = plugin.getConfig().getBoolean("experiments.nested-boat-seat", false);
        try {
            rig = GoKartRig.spawn(plugin, root);
            seat = (Boat) root.getWorld().spawnEntity(seatLocation(root), EntityType.OAK_BOAT);
            seat.setGravity(false); seat.setInvulnerable(true); seat.setSilent(true); seat.setPersistent(false);
            // Carrier for the model. Paper 1.21.4 promotes a player ahead of
            // this non-player passenger, so it does NOT reserve boat control.
            // A vanilla client can still predict boat movement independently.
            blocker = root.getWorld().spawn(seatLocation(root), ArmorStand.class, entity -> {
                entity.setInvisible(true); entity.setMarker(true); entity.setSmall(true);
                entity.setGravity(false); entity.setInvulnerable(true); entity.setSilent(true);
                entity.setPersistent(false); entity.setRemoveWhenFarAway(false);
            });
            if (nested) {
                // Experimental inverted hierarchy: carrier -> boat -> player,
                // and carrier -> model displays. Not yet visually validated.
                if (!blocker.addPassenger(seat)) throw new IllegalStateException("Unable to attach boat to carrier");
            } else if (!seat.addPassenger(blocker)) {
                throw new IllegalStateException("Unable to attach model carrier to boat");
            }
            rig.attach(blocker, root);
            hitbox = root.getWorld().spawn(root, Interaction.class, entity -> {
                entity.setInteractionWidth(1.8f); entity.setInteractionHeight(1.3f);
                entity.setResponsive(true); entity.setPersistent(false);
            });
            karts.add(new Kart(root, rig, seat, blocker, hitbox, nested));
            player.sendMessage("Go-Kart experimental creat. Click dreapta pentru a urca; Shift pentru a cobori.");
            return true;
        } catch (Exception error) {
            if (rig != null) rig.remove();
            if (seat != null) seat.remove();
            if (blocker != null) blocker.remove();
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
                if (kart.seat.getPassengers().stream().anyMatch(Player.class::isInstance)) {
                    event.getPlayer().sendMessage("Scaunul este ocupat."); return;
                }
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
            if (!kart.seat.isValid() || !kart.hitbox.isValid()
                    || !(kart.nested ? kart.blocker.equals(kart.seat.getVehicle()) : kart.seat.equals(kart.blocker.getVehicle()))
                    || !kart.rig.isAttached(kart.blocker)) {
                kart.remove(); karts.remove(kart); continue;
            }
            kart.tick();
        }
    }
    public void removeAll() { karts.forEach(Kart::remove); karts.clear(); }

    private static Location seatLocation(Location root) {
        LandVehicleSpec.Point p = LandVehicleSpec.GO_KART.seats().stream()
                .filter(LandVehicleSpec.Seat::driver).findFirst().orElseThrow().sourceOffset();
        double angle = Math.toRadians(root.getYaw());
        Location target = root.clone().add(p.x() * Math.cos(angle) - p.z() * Math.sin(angle),
                p.y() + LandVehicleSpec.RIDER_HEIGHT_CORRECTION - 0.7 * 0.0625,
                p.x() * Math.sin(angle) + p.z() * Math.cos(angle));
        target.setPitch(0);
        return target;
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
        Location root; final GoKartRig rig; final Boat seat; final ArmorStand blocker; final Interaction hitbox;
        final GoKartMotion motion; final boolean nested; double fallVelocity; boolean onGround = true;
        Kart(Location root, GoKartRig rig, Boat seat, ArmorStand blocker, Interaction hitbox, boolean nested) {
            this.root = root.clone(); this.rig = rig; this.seat = seat; this.blocker = blocker; this.hitbox = hitbox;
            this.motion = new GoKartMotion(root.getYaw()); this.nested = nested;
        }
        void tick() {
            Player driver = seat.getPassengers().stream().filter(Player.class::isInstance).map(Player.class::cast).findFirst().orElse(null);
            var input = driver == null ? null : driver.getCurrentInput();
            int throttle = input == null ? 0 : (input.isForward() ? 1 : 0) - (input.isBackward() ? 1 : 0);
            int steering = input == null ? 0 : (input.isLeft() ? 1 : 0) - (input.isRight() ? 1 : 0);
            double friction = 0, traction = 0;
            int contacts = 0;
            double yaw = Math.toRadians(root.getYaw());
            for (LandVehicleSpec.Wheel wheel : LandVehicleSpec.GO_KART.wheels()) {
                double x = wheel.contactX() * Math.cos(yaw) - wheel.contactZ() * Math.sin(yaw);
                double z = wheel.contactX() * Math.sin(yaw) + wheel.contactZ() * Math.cos(yaw);
                Location contact = root.clone().add(x, wheel.contactY() - .2, z);
                if (!root.getWorld().isChunkLoaded(contact.getBlockX() >> 4, contact.getBlockZ() >> 4)) { motion.stop(); return; }
                SurfaceProfile surface = SurfaceProfile.at(contact.getBlock());
                if (surface.friction() == 0) continue;
                friction += surface.friction() * WheelType.STANDARD.surfaceModifier(surface.category());
                traction += surface.tractionFactor(); contacts++;
            }
            if (contacts == 0) traction = 1;
            else { friction /= contacts; traction /= contacts; }
            var step = motion.tick(throttle, steering, input != null && input.isJump(), onGround, friction, traction);
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
            // Move only the root of the chosen hierarchy, retaining passengers.
            // Client rendering and local boat prediction still need visual tests.
            seat.setVelocity(new Vector(0, 0, 0));
            if (nested) {
                blocker.setVelocity(new Vector(0, 0, 0));
                if (!blocker.teleport(seatTarget, TeleportFlag.EntityState.RETAIN_PASSENGERS)) { motion.stop(); return; }
            } else if (!seat.teleport(seatTarget, TeleportFlag.EntityState.RETAIN_PASSENGERS)) {
                motion.stop(); return;
            }
            seat.setRotation(seatTarget.getYaw(), 0);
            root = next;
            hitbox.teleport(root);
            rig.updateAttached(root, blocker);
            if (driver != null && driver.getTicksLived() % 20 == 0)
                driver.sendActionBar(Component.text(String.format("Go-Kart | Combustibil: %.0f%%", step.fuel())));
        }
        void remove() { seat.eject(); blocker.remove(); seat.remove(); hitbox.remove(); rig.remove(); }
    }
}
