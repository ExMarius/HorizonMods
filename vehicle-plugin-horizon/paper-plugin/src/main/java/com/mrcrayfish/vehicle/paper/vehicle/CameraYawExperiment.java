package com.mrcrayfish.vehicle.paper.vehicle;

import org.bukkit.Bukkit;
import org.bukkit.entity.Player;
import org.bukkit.plugin.java.JavaPlugin;

import java.lang.reflect.Constructor;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.Set;
import java.util.UUID;
import java.util.logging.Level;

/** Explicitly enabled, single-driver Paper 1.21.4 experiment; never persistent.
 * NMS teleport acknowledgements and riding behaviour still require in-game validation. */
final class CameraYawExperiment {
    private static final long SESSION_NANOS = 120_000_000_000L;
    private static final long MIN_SEND_NANOS = 100_000_000L;
    private static final long MAX_ACK_WAIT_NANOS = 1_000_000_000L;
    private final JavaPlugin plugin;
    private Session session;

    private static final class Session {
        final UUID driver;
        final LandVehicle vehicle;
        final Object connection;
        final Field awaitingPosition;
        final Method teleport;
        final Constructor<?> movement;
        final Object zero;
        final Set<Object> flags;
        final long expires;
        float previousYaw;
        double accumulated;
        long lastSend, awaitingSince;
        Session(UUID driver, LandVehicle vehicle, Object connection, Field awaitingPosition, Method teleport,
                Constructor<?> movement, Object zero, Set<Object> flags) {
            this.driver = driver; this.vehicle = vehicle; this.connection = connection;
            this.awaitingPosition = awaitingPosition; this.teleport = teleport; this.movement = movement;
            this.zero = zero; this.flags = flags; this.previousYaw = vehicle.location().getYaw();
            this.expires = System.nanoTime() + SESSION_NANOS;
        }
    }

    CameraYawExperiment(JavaPlugin plugin) { this.plugin = plugin; }

    boolean start(Player player, LandVehicle vehicle) {
        if (!Bukkit.isPrimaryThread() || !player.isOp() || !"1.21.4".equals(Bukkit.getMinecraftVersion())
                || vehicle == null || vehicle.recoveryLocked()
                || vehicle.driver().filter(player::equals).isEmpty()) {
            player.sendMessage("[CameraTest] Necesită OP, Paper 1.21.4 și un vehicul condus, fără tractare activă.");
            return false;
        }
        if (session != null) {
            player.sendMessage("[CameraTest] Există deja un test activ. Folosește /vehicle cameratest oprit.");
            return false;
        }
        try {
            Object handle = player.getClass().getMethod("getHandle").invoke(player);
            Object connection = handle.getClass().getField("connection").get(handle);
            Class<?> listener = Class.forName("net.minecraft.server.network.ServerGamePacketListenerImpl");
            Class<?> vector = Class.forName("net.minecraft.world.phys.Vec3");
            Class<?> movement = Class.forName("net.minecraft.world.entity.PositionMoveRotation");
            Class<?> relative = Class.forName("net.minecraft.world.entity.Relative");
            Field awaiting = listener.getDeclaredField("awaitingPositionFromClient");
            awaiting.setAccessible(true);
            Set<Object> flags = Set.of(relative.getField("X").get(null), relative.getField("Y").get(null),
                    relative.getField("Z").get(null), relative.getField("Y_ROT").get(null),
                    relative.getField("X_ROT").get(null), relative.getField("DELTA_X").get(null),
                    relative.getField("DELTA_Y").get(null), relative.getField("DELTA_Z").get(null));
            session = new Session(player.getUniqueId(), vehicle, connection, awaiting,
                    listener.getMethod("internalTeleport", movement, Set.class),
                    movement.getConstructor(vector, vector, float.class, float.class),
                    vector.getField("ZERO").get(null), flags);
            player.sendMessage("[CameraTest] Activ doar pe acest vehicul, maximum 2 minute. Oprește cu /vehicle cameratest oprit.");
            player.sendMessage("[CameraTest] Dacă apar smucituri sau cobori din scaun, oprește imediat; nu este o variantă finală.");
            return true;
        } catch (ReflectiveOperationException | RuntimeException error) {
            plugin.getLogger().log(Level.WARNING, "[CameraTest] Paper 1.21.4 internals unavailable", error);
            player.sendMessage("[CameraTest] Nu pot activa prototipul pe această versiune; niciun pachet nu a fost trimis.");
            return false;
        }
    }

    void stop(Player actor) {
        if (session == null) { actor.sendMessage("[CameraTest] Nu există un test activ."); return; }
        Session old = session; session = null;
        actor.sendMessage("[CameraTest] Test dezactivat.");
        Player driver = Bukkit.getPlayer(old.driver);
        if (driver != null && !driver.equals(actor)) driver.sendMessage("[CameraTest] Test dezactivat de administrator.");
    }

    void clear() { session = null; }

    void tick(VehicleManager manager) {
        Session s = session;
        if (s == null) return;
        Player driver = Bukkit.getPlayer(s.driver);
        long now = System.nanoTime();
        if (driver == null || !driver.isOnline() || !driver.isOp() || driver.isDead()
                || manager.byId(s.vehicle.id()).orElse(null) != s.vehicle || s.vehicle.recoveryLocked()
                || s.vehicle.driver().filter(driver::equals).isEmpty() || now - s.expires >= 0L) {
            session = null;
            if (driver != null && driver.isOnline()) driver.sendMessage("[CameraTest] Test încheiat (coborâre, schimbare vehicul sau expirare).");
            return;
        }
        float yaw = s.vehicle.location().getYaw();
        double delta = Math.IEEEremainder(yaw - s.previousYaw, 360D);
        s.previousYaw = yaw;
        if (!Double.isFinite(delta) || Math.abs(delta) > 20D) {
            session = null; driver.sendMessage("[CameraTest] Oprit: schimbare bruscă de orientare."); return;
        }
        s.accumulated += delta;
        if (Math.abs(s.accumulated) > 20D) {
            session = null; driver.sendMessage("[CameraTest] Oprit: corecția acumulată a devenit prea mare."); return;
        }
        try {
            // Never overwrite an unacknowledged teleport, including one started by another plugin.
            if (s.awaitingPosition.get(s.connection) != null) {
                if (s.awaitingSince == 0L) s.awaitingSince = now;
                if (now - s.awaitingSince > MAX_ACK_WAIT_NANOS) {
                    session = null; driver.sendMessage("[CameraTest] Oprit: confirmarea de la client întârzie.");
                }
                return;
            }
            s.awaitingSince = 0L;
            if (Math.abs(s.accumulated) < .05D || now - s.lastSend < MIN_SEND_NANOS) return;
            Object change = s.movement.newInstance(s.zero, s.zero, (float) s.accumulated, 0F);
            // Let Paper allocate the teleport ID and update server-side state. No fabricated packet IDs.
            s.teleport.invoke(s.connection, change, s.flags);
            s.accumulated = 0D; s.lastSend = now; s.awaitingSince = now;
        } catch (ReflectiveOperationException | RuntimeException error) {
            session = null;
            plugin.getLogger().log(Level.WARNING, "[CameraTest] Experiment stopped", error);
            driver.sendMessage("[CameraTest] Oprit din cauza unei erori; sistemul normal rămâne activ.");
        }
    }
}
