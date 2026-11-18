package ro.exmarius.horizonvehicles.kart;

import java.lang.reflect.Method;
import java.util.concurrent.CompletableFuture;
import org.bukkit.Bukkit;
import org.bukkit.Location;
import org.bukkit.command.CommandSender;
import org.bukkit.entity.Player;
import org.bukkit.plugin.Plugin;

/** Optional bridge to Apache-2.0 fakeplayer 0.3.13; never loads it implicitly. */
final class FakeSeatPilot {
    private final Object manager;
    private final Method spawn;
    private final Method remove;

    FakeSeatPilot() throws ReflectiveOperationException {
        Plugin provider = Bukkit.getPluginManager().getPlugin("fakeplayer");
        if (provider == null || !provider.isEnabled()) throw new IllegalStateException("Plugin fakeplayer indisponibil");
        ClassLoader loader = provider.getClass().getClassLoader();
        Class<?> main = Class.forName("io.github.hello09x.fakeplayer.core.Main", true, loader);
        Class<?> managerClass = Class.forName("io.github.hello09x.fakeplayer.core.manager.FakeplayerManager", true, loader);
        Object injector = main.getMethod("getInjector").invoke(null);
        // Invoke the public interface rather than a possibly package-private implementation.
        Class<?> injectorClass = Class.forName("com.google.inject.Injector", true, loader);
        manager = injectorClass.getMethod("getInstance", Class.class).invoke(injector, managerClass);
        spawn = managerClass.getMethod("spawnAsync", CommandSender.class, String.class, Location.class, long.class);
        remove = managerClass.getMethod("remove", String.class, String.class);
    }

    @SuppressWarnings("unchecked")
    CompletableFuture<Player> spawn(String name, Location where) throws ReflectiveOperationException {
        return (CompletableFuture<Player>) spawn.invoke(manager, Bukkit.getConsoleSender(), name, where, -1L);
    }

    void remove(String name) {
        try { remove.invoke(manager, name, "vehicle seat removed"); }
        catch (ReflectiveOperationException e) { Bukkit.getLogger().warning("Cannot remove fake seat pilot " + name + ": " + e); }
    }
}
