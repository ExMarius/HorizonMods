package com.mrcrayfish.vehicle.paper.persistence;

import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.configuration.InvalidConfigurationException;
import org.bukkit.configuration.file.YamlConfiguration;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.AtomicMoveNotSupportedException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.nio.file.StandardOpenOption;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

/** Experimental snapshot writer, NOT connected to TrailerStore. The caller must
 * serialize all access and prove which IDs it actually owns. Deferred records
 * (including records unknown to the active runtime) remain untouched. A changed,
 * unreadable or malformed source must never be replaced. */
public final class TrailerSnapshotMerge {
    private TrailerSnapshotMerge() { }

    /** An absent file is represented by null; an empty existing file is distinct. */
    public static byte[] read(Path path) throws IOException {
        if (Files.notExists(path)) return null;
        return Files.readAllBytes(path);
    }

    /**
     * Replaces/deletes only explicitly managed IDs. Active entries must be a
     * subset of managed IDs; omitted managed IDs are explicit deletions. Values
     * are regular Bukkit YAML-serializable trailer fields. Expected is the exact
     * snapshot previously observed by the single serialized owner.
     */
    public static void write(Path file, byte[] expected, Set<UUID> managed,
                             Map<UUID, Map<String, Object>> active) throws IOException {
        if (file == null || managed == null || active == null || managed.stream().anyMatch(java.util.Objects::isNull)
                || active.keySet().stream().anyMatch(java.util.Objects::isNull) || !managed.containsAll(active.keySet()))
            throw new IOException("Invalid managed trailer set");
        Path target = file.toAbsolutePath();
        assertUnchanged(target, expected);
        YamlConfiguration yaml = new YamlConfiguration();
        try {
            if (expected != null) yaml.loadFromString(new String(expected, StandardCharsets.UTF_8));
        } catch (InvalidConfigurationException | IllegalArgumentException e) {
            throw new IOException("Malformed trailer snapshot", e);
        }
        if (yaml.contains("trailers") && !yaml.isConfigurationSection("trailers"))
            throw new IOException("Invalid trailers section");
        ConfigurationSection existing = yaml.getConfigurationSection("trailers");
        for (UUID id : managed) {
            String key = id.toString();
            // A managed-but-absent record is only allowed when it is newly active.
            if ((existing == null || !existing.contains(key)) && !active.containsKey(id))
                throw new IOException("Missing managed record " + id);
            if (existing != null && existing.contains(key) && !existing.isConfigurationSection(key))
                throw new IOException("Invalid managed record " + id);
        }
        for (UUID id : managed) {
            String key = "trailers." + id;
            Map<String, Object> fields = active.get(id);
            yaml.set(key, null);
            if (fields != null) {
                if (fields.isEmpty()) throw new IOException("Empty active trailer " + id);
                for (var entry : fields.entrySet()) {
                    if (entry.getKey() == null || entry.getKey().isBlank() || entry.getKey().contains("."))
                        throw new IOException("Invalid trailer field");
                    yaml.set(key + "." + entry.getKey(), entry.getValue());
                }
            } else if (active.containsKey(id)) throw new IOException("Null trailer record");
        }
        byte[] bytes = yaml.saveToString().getBytes(StandardCharsets.UTF_8);
        Path parent = target.getParent();
        if (parent == null) throw new IOException("Missing parent directory");
        Files.createDirectories(parent);
        Path temp = Files.createTempFile(parent, ".trailers-", ".tmp");
        try {
            try (FileChannel channel = FileChannel.open(temp, StandardOpenOption.WRITE, StandardOpenOption.TRUNCATE_EXISTING)) {
                ByteBuffer data = ByteBuffer.wrap(bytes);
                while (data.hasRemaining()) channel.write(data);
                channel.force(true);
            }
            assertUnchanged(target, expected);
            try {
                Files.move(temp, target, StandardCopyOption.ATOMIC_MOVE, StandardCopyOption.REPLACE_EXISTING);
            } catch (AtomicMoveNotSupportedException e) {
                throw new IOException("Atomic trailer snapshot update unavailable", e);
            }
            try (FileChannel directory = FileChannel.open(parent, StandardOpenOption.READ)) { directory.force(true); }
        } finally { Files.deleteIfExists(temp); }
    }

    private static void assertUnchanged(Path path, byte[] expected) throws IOException {
        if (!java.util.Arrays.equals(read(path), expected))
            throw new IOException("Trailer snapshot changed since it was read");
    }
}
