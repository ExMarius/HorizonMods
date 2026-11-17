package ro.exmarius.horizonvehicles;

import org.bukkit.command.Command;
import org.bukkit.command.CommandExecutor;
import org.bukkit.command.CommandSender;
import org.bukkit.plugin.java.JavaPlugin;

/** Safe starting point: no original plugin resources and no premature spawning. */
public final class HorizonVehiclesPlugin extends JavaPlugin implements CommandExecutor {
    @Override
    public void onEnable() {
        var command = getCommand("hvehicle");
        if (command == null) {
            throw new IllegalStateException("Missing hvehicle command in plugin.yml");
        }
        command.setExecutor(this);
        getLogger().warning("Development scaffold only: vehicles cannot be spawned yet.");
    }

    @Override
    public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {
        if (args.length != 1 || !args[0].equalsIgnoreCase("list")) {
            return false;
        }
        sender.sendMessage("Vehicule planificate (nu pot fi spawnate inca):");
        for (var entry : VehicleCatalog.PLANNED) {
            sender.sendMessage("- " + entry.id() + " — " + entry.name());
        }
        return true;
    }
}
