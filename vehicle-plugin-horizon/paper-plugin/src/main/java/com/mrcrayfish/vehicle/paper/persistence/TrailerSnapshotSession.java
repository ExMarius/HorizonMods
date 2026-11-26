package com.mrcrayfish.vehicle.paper.persistence;

import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.configuration.InvalidConfigurationException;
import org.bukkit.configuration.file.YamlConfiguration;

import java.io.IOException;
import java.nio.file.Path;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

/** Experimental single-owner session for TrailerSnapshotMerge, not wired to the
 * live trailer manager. Ownership may be claimed only for successfully loaded
 * records. Unclaimed and unknown records survive every write. All calls must
 * run on the same serialized owner, with no independent writers. */
public final class TrailerSnapshotSession {
    private final Path path;
    private byte[] snapshot;
    private final Set<UUID> persisted = new HashSet<>();
    private final Set<UUID> claimable = new HashSet<>();
    private final Set<UUID> owned = new HashSet<>();
    private boolean failed;

    public TrailerSnapshotSession(Path path) throws IOException {
        if (path == null) throw new IOException("Missing snapshot path");
        this.path = path.toAbsolutePath();
        snapshot = TrailerSnapshotMerge.read(this.path);
        YamlConfiguration yaml = new YamlConfiguration();
        try {
            if (snapshot != null) yaml.loadFromString(TrailerSnapshotMerge.decode(snapshot));
            if (yaml.contains("trailers") && !yaml.isConfigurationSection("trailers"))
                throw new IOException("Invalid trailers section");
            ConfigurationSection section = yaml.getConfigurationSection("trailers");
            if (section != null) {
                for (String key : section.getKeys(false)) {
                    // Malformed/unknown records are retained but can never be claimed.
                    try {
                        UUID id = UUID.fromString(key);
                        if (!persisted.add(id)) throw new IOException("Duplicate trailer identity");
                        if (id.toString().equals(key) && section.isConfigurationSection(key)) claimable.add(id);
                    }
                    catch (IllegalArgumentException ignored) { }
                }
            }
        } catch (InvalidConfigurationException | IllegalArgumentException e) {
            throw new IOException("Malformed trailer snapshot", e);
        }
    }

    /** The caller must first have loaded and validated the entire record. */
    public void claimLoaded(UUID id) throws IOException {
        requireHealthy();
        if (id == null || !claimable.contains(id) || !owned.add(id))
            throw new IOException("Cannot claim trailer record");
    }

    /** Register a new entity, refusing collisions with even deferred records. */
    public void registerNew(UUID id) throws IOException {
        requireHealthy();
        if (id == null || persisted.contains(id) || !owned.add(id))
            throw new IOException("Trailer identity already exists or is invalid");
    }

    /** The map is the complete current live set. Missing previously owned IDs
     * are deleted explicitly. A failed write poisons the session: reconcile the
     * actual file and runtime before starting another one. */
    public void save(Map<UUID, Map<String, Object>> active) throws IOException {
        requireHealthy();
        if (active == null || !owned.containsAll(active.keySet()))
            throw new IOException("Active trailer is not owned");
        try {
            Set<UUID> changes = new HashSet<>(owned);
            // A newly created entity removed before its first save has no tombstone.
            changes.removeIf(id -> !persisted.contains(id) && !active.containsKey(id));
            TrailerSnapshotMerge.write(path, snapshot, changes, active);
            snapshot = TrailerSnapshotMerge.read(path);
            persisted.removeAll(owned);
            persisted.addAll(active.keySet());
            claimable.removeAll(owned);
            claimable.addAll(active.keySet());
            owned.retainAll(active.keySet());
        } catch (IOException | RuntimeException e) {
            failed = true;
            if (e instanceof IOException io) throw io;
            throw new IOException("Trailer snapshot serialization failed", e);
        }
    }

    private void requireHealthy() throws IOException {
        if (failed) throw new IOException("Trailer snapshot session requires reconciliation");
    }
}
