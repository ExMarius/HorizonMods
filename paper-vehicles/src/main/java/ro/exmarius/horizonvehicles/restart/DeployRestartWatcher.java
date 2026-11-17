package ro.exmarius.horizonvehicles.restart;

import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.Locale;
import java.util.logging.Level;
import org.bukkit.Bukkit;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.scheduler.BukkitTask;

/** Restart through the same console command as the upstream Paper plugin. */
public final class DeployRestartWatcher {
    private final JavaPlugin plugin;
    private final File marker;
    private final String loadedSha256;
    private BukkitTask poll;
    private boolean restartRequested;

    public DeployRestartWatcher(JavaPlugin plugin, String loadedSha256) {
        this.plugin = plugin;
        this.marker = new File(plugin.getDataFolder(), ".restart-request");
        this.loadedSha256 = loadedSha256.toLowerCase(Locale.ROOT);
    }

    public void start() {
        if (!plugin.getDataFolder().isDirectory() && !plugin.getDataFolder().mkdirs()) {
            plugin.getLogger().warning("Cannot create restart marker directory");
        }
        poll = Bukkit.getScheduler().runTaskTimer(plugin, this::check, 60L, 60L);
    }

    private void check() {
        if (restartRequested || !marker.isFile()) return;
        try {
            String requested = Files.readString(marker.toPath(), StandardCharsets.US_ASCII).trim().toLowerCase(Locale.ROOT);
            if (!requested.matches("[0-9a-f]{64}")) {
                plugin.getLogger().warning("Invalid restart request; ignoring marker.");
                return;
            }
            // A server that was already restarted is running the uploaded JAR.
            // Consume stale markers instead of causing a restart loop.
            if (requested.equals(loadedSha256)) {
                Files.deleteIfExists(marker.toPath());
                return;
            }
            restartRequested = true;
            Bukkit.broadcastMessage("§d[Horizon Vehicles] §fActualizare instalată. Serverul repornește în 5 secunde.");
            plugin.getLogger().info("Update detected; requesting server restart in 5 seconds.");
            Bukkit.getScheduler().runTaskLater(plugin, () -> {
                boolean accepted = Bukkit.dispatchCommand(Bukkit.getConsoleSender(), "restart");
                if (!accepted) plugin.getLogger().severe("Console restart command failed; marker retained for manual recovery.");
            }, 100L);
        } catch (IOException error) {
            plugin.getLogger().log(Level.WARNING, "Could not read restart marker", error);
        }
    }

    public void stop() { if (poll != null) poll.cancel(); }
}
