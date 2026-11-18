package ro.exmarius.horizonvehicles;

import net.kyori.adventure.text.Component;
import org.bukkit.command.Command;
import org.bukkit.command.CommandExecutor;
import org.bukkit.command.CommandSender;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.player.PlayerJoinEvent;
import org.bukkit.plugin.java.JavaPlugin;
import ro.exmarius.horizonvehicles.kart.GoKartManager;
import ro.exmarius.horizonvehicles.restart.DeployRestartWatcher;
import java.nio.file.Files;
import java.io.File;
import java.io.InputStream;
import java.security.MessageDigest;
import java.util.HexFormat;
import java.util.UUID;

/** Entry point for the experimental Paper Go-Kart. */
public final class HorizonVehiclesPlugin extends JavaPlugin implements CommandExecutor, Listener {
    private static final String PACK_URL = "https://github.com/ExMarius/HorizonMods/raw/refs/heads/arena/fb5f91ff-horizonmods/paper-vehicles/public/go-kart.zip";
    private static final UUID PACK_ID = UUID.fromString("fc7756ca-6d5a-45be-9c32-caa85c873088");
    private GoKartManager karts;
    private String packHash;
    private DeployRestartWatcher restartWatcher;

    @Override public void onEnable() {
        try (InputStream stream = getResource("resource-packs/go-kart-experimental.zip")) {
            if (stream == null) throw new IllegalStateException("Go-Kart pack not bundled");
            packHash = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-1").digest(stream.readAllBytes()));
        } catch (Exception error) { throw new IllegalStateException("Cannot load Go-Kart pack", error); }
        try {
            // Paper remaps plugin JARs on startup, so getFile() may name a
            // remapped copy whose hash differs from the artifact uploaded by CI.
            File deployedJar = new File(getDataFolder().getParentFile(), "HorizonVehiclesPaper-dev.jar");
            File sourceJar = deployedJar.isFile() ? deployedJar : getFile();
            String loadedHash = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(Files.readAllBytes(sourceJar.toPath())));
            restartWatcher = new DeployRestartWatcher(this, loadedHash);
            restartWatcher.start();
        } catch (Exception error) {
            throw new IllegalStateException("Cannot enable deploy restart watcher", error);
        }
        karts = new GoKartManager(this);
        var command = getCommand("hvehicle");
        if (command == null) throw new IllegalStateException("Missing hvehicle command");
        command.setExecutor(this);
        getServer().getPluginManager().registerEvents(karts, this);
        getServer().getPluginManager().registerEvents(this, this);
        getServer().getScheduler().runTaskTimer(this, karts::tick, 1, 1);
        getLogger().warning("Go-Kart prototype: experimental and not yet validated in game; vehicles are not persistent.");
    }

    @Override public void onDisable() { if (restartWatcher != null) restartWatcher.stop(); if (karts != null) karts.removeAll(); }

    @EventHandler public void onJoin(PlayerJoinEvent event) {
        getServer().getScheduler().runTaskLater(this, () -> {
            if (event.getPlayer().isOnline()) sendPack(event.getPlayer());
        }, 40);
    }

    private void sendPack(Player player) {
        player.setResourcePack(PACK_ID, PACK_URL, packHash,
                Component.text("Acceptă pachetul pentru modelul Go-Kart."), false);
    }

    @Override public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {
        if (args.length == 1 && args[0].equalsIgnoreCase("list")) {
            sender.sendMessage("Go-Kart: prototip experimental. Alte vehicule sunt planificate:");
            for (var entry : VehicleCatalog.PLANNED) sender.sendMessage("- " + entry.id() + " — " + entry.name());
            return true;
        }
        if (!(sender instanceof Player player)) { sender.sendMessage("Comanda se folosește în joc."); return true; }
        if (args.length == 1 && args[0].equalsIgnoreCase("pack")) { sendPack(player); return true; }
        if (args.length == 1 && args[0].equalsIgnoreCase("remove")) {
            player.sendMessage(karts.removeNearest(player) ? "Go-Kart eliminat." : "Nu există un Go-Kart în apropiere."); return true;
        }
        if (args.length == 1 && args[0].equalsIgnoreCase("fuel")) {
            player.sendMessage(karts.refuelNearest(player) ? "Rezervor alimentat." : "Nu există un Go-Kart în apropiere."); return true;
        }
        if ((args.length == 1 && args[0].equalsIgnoreCase("spawn")) ||
                (args.length == 2 && args[0].equalsIgnoreCase("spawn") && args[1].equalsIgnoreCase("go_kart"))) {
            karts.spawn(player, false); return true;
        }
        if (args.length == 2 && args[0].equalsIgnoreCase("spawn") && args[1].equalsIgnoreCase("go_kart_raft")) {
            karts.spawn(player, true); return true;
        }
        return false;
    }
}
