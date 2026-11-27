package com.mrcrayfish.vehicle.paper.recovery;

import com.mrcrayfish.vehicle.paper.render.LandVehicleRig;
import org.bukkit.Bukkit;
import org.bukkit.entity.Entity;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.world.EntitiesLoadEvent;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Set;
import java.util.UUID;

/** Live listener for retired rig sessions and exact old entity IDs, loaded before
 * vehicles spawn. Recovery transactions do not yet write these files. Never
 * expires IDs: entity.remove() alone doesn't prove the region was saved. A player
 * or an entity carrying passengers is never removed by this guard. */
public final class RecoveredEntityGuard implements Listener {
    private static final long MAX_FILE_SIZE = 16L * 100_000 + 16;
    private static final String SESSION_PREFIX = "mcv_session_";
    private final Set<UUID> retiredEntities;
    private final Set<UUID> retiredSessions;

    private RecoveredEntityGuard(Set<UUID> entities, Set<UUID> sessions) {
        this.retiredEntities = entities; this.retiredSessions = sessions;
    }

    public static RecoveredEntityGuard load(Path directory) throws IOException {
        return new RecoveredEntityGuard(read(directory.resolve("recovery-entities.dat")),
                read(directory.resolve("recovery-sessions.dat")));
    }
    private static Set<UUID> read(Path file) throws IOException {
        if (Files.notExists(file)) return Set.of();
        if (!Files.isRegularFile(file) || Files.size(file) > MAX_FILE_SIZE)
            throw new IOException("Invalid recovery identity registry: " + file.getFileName());
        return RecoveryEntityTombstones.decode(Files.readAllBytes(file));
    }

    @EventHandler
    public void onEntitiesLoad(EntitiesLoadEvent event) {
        for (Entity entity : event.getEntities()) removeIfRetired(entity);
    }

    /** Also cover entities already loaded before the listener is registered. */
    public void sweepLoaded() {
        if (!Bukkit.isPrimaryThread()) throw new IllegalStateException("Entity sweep requires main thread");
        for (var world : Bukkit.getWorlds()) for (Entity entity : world.getEntities()) removeIfRetired(entity);
    }

    private void removeIfRetired(Entity entity) {
        if (entity instanceof Player || !entity.getScoreboardTags().contains(LandVehicleRig.ENTITY_TAG)
                || !entity.getPassengers().isEmpty()) return;
        boolean retired = retiredEntities.contains(entity.getUniqueId());
        if (!retired) for (String tag : entity.getScoreboardTags()) {
            if (!tag.startsWith(SESSION_PREFIX)) continue;
            try {
                String value = tag.substring(SESSION_PREFIX.length());
                UUID session = UUID.fromString(value);
                if (session.toString().equals(value) && retiredSessions.contains(session)) { retired = true; break; }
            } catch (IllegalArgumentException ignored) { /* Unknown or malformed tag, leave it alone. */ }
        }
        if (retired) entity.remove();
    }
}
