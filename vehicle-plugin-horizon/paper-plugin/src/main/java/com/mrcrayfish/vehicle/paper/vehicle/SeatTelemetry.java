package com.mrcrayfish.vehicle.paper.vehicle;

import org.bukkit.Bukkit;
import org.bukkit.Location;
import org.bukkit.entity.Boat;
import org.bukkit.entity.Entity;
import org.bukkit.entity.Player;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.scheduler.BukkitTask;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.UUID;

/** One operator's opt-in server-side measurements; never changes vehicle state. */
final class SeatTelemetry {
    private static final long MAX_NANOS = 90_000_000_000L;
    private final JavaPlugin plugin;
    private final VehicleManager manager;
    private final List<String> samples = new ArrayList<>();
    private UUID rider;
    private BukkitTask task;
    private long started;
    private int ticks;
    private UUID lastVehicle;
    private Location previous;
    private LandVehicle cachedCar;

    SeatTelemetry(JavaPlugin plugin, VehicleManager manager) { this.plugin = plugin; this.manager = manager; }

    void start(Player player) {
        if (rider != null) { player.sendMessage("[Masurare] Există deja o măsurare activă."); return; }
        rider = player.getUniqueId(); started = System.nanoTime(); ticks = 0;
        samples.clear(); previous = null; lastVehicle = null; cachedCar = null;
        task = Bukkit.getScheduler().runTaskTimer(plugin, this::tick, 1L, 1L);
        player.sendMessage("[Masurare] Activă maximum 90 secunde, doar pentru tine. Datele ajung în logul serverului.");
        player.sendMessage("[Masurare] Condu bărci normale sau o mașină; oprește cu /vehicle masurare oprit.");
    }

    void stop(Player player) {
        if (rider == null) { player.sendMessage("[Masurare] Nu există o măsurare activă."); return; }
        if (!rider.equals(player.getUniqueId())) { player.sendMessage("[Masurare] Doar participantul poate opri măsurarea."); return; }
        finish("manual");
    }

    void shutdown() { if (rider != null) finish("shutdown"); }

    private void tick() {
        Player player = Bukkit.getPlayer(rider);
        if (player == null || !player.isOnline() || !player.isOp() || player.isDead()
                || System.nanoTime() - started >= MAX_NANOS || ticks >= 1800) {
            finish("timeout_or_exit"); return;
        }
        if (++ticks % 2 != 0) return;
        Entity seat = player.getVehicle();
        String type = null;
        UUID id = null;
        Location position = null;
        if (seat instanceof Boat boat && !boat.getPassengers().isEmpty() && boat.getPassengers().getFirst().equals(player)) {
            // Exclude the separate experimental hierarchy to keep this a vanilla reference.
            if (!boat.getScoreboardTags().contains("mcv_boat_probe")) {
                type = boat.getType().name(); id = boat.getUniqueId(); position = boat.getLocation();
            }
        } else if (seat != null) {
            if (cachedCar != null && cachedCar.driver().filter(player::equals).isEmpty()) cachedCar = null;
            if (cachedCar == null && ticks % 10 == 0) {
                cachedCar = manager.vehicles().stream()
                        .filter(car -> car.driver().filter(player::equals).isPresent()).findFirst().orElse(null);
            }
            LandVehicle car = cachedCar;
            if (car != null && manager.byId(car.id()).orElse(null) == car && car.driver().filter(player::equals).isPresent()) {
                type = "CAR"; id = car.id(); position = car.location();
            }
        }
        if (position == null) { previous = null; lastVehicle = null; return; }
        double distance = 0;
        if (id.equals(lastVehicle) && previous != null && previous.getWorld().equals(position.getWorld())) {
            distance = Math.sqrt(position.distanceSquared(previous));
        }
        previous = position.clone(); lastVehicle = id;
        var input = player.getCurrentInput();
        float yaw = position.getYaw();
        float view = player.getLocation().getYaw();
        float relative = ((view - yaw + 540F) % 360F + 360F) % 360F - 180F;
        samples.add(String.format(Locale.ROOT, "%d,%s,%.2f,%.2f,%.2f,%.2f,%.4f,%d%d%d%d",
                ticks, type, yaw, view, relative, player.getLocation().getPitch(), distance,
                input.isForward() ? 1 : 0, input.isBackward() ? 1 : 0,
                input.isLeft() ? 1 : 0, input.isRight() ? 1 : 0));
    }

    private void finish(String reason) {
        UUID previousRider = rider;
        rider = null;
        if (task != null) { task.cancel(); task = null; }
        plugin.getLogger().info("[SeatMeasure] BEGIN reason=" + reason + " samples=" + samples.size()
                + " columns=tick,type,vehicleYaw,playerYaw,relativeYaw,pitch,distancePerSample,W,S,A,D");
        for (int i = 0; i < samples.size(); i += 20) {
            plugin.getLogger().info("[SeatMeasure] " + String.join(";", samples.subList(i, Math.min(i + 20, samples.size()))));
        }
        plugin.getLogger().info("[SeatMeasure] END");
        samples.clear(); previous = null; lastVehicle = null; cachedCar = null;
        Player player = Bukkit.getPlayer(previousRider);
        if (player != null && player.isOnline()) player.sendMessage("[Masurare] Încheiată; datele anonimizate sunt în logul serverului.");
    }
}
