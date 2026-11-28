package com.mrcrayfish.vehicle.paper.recovery;

import com.mrcrayfish.vehicle.paper.persistence.TrailerSnapshotMerge;
import org.bukkit.configuration.file.YamlConfiguration;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import static org.junit.jupiter.api.Assertions.*;

class TrailerSnapshotMergeTest {
    @TempDir Path dir;
    final UUID active = UUID.randomUUID(), deferred = UUID.randomUUID(), added = UUID.randomUUID();
    private Path original() throws IOException {
        Path path = dir.resolve("trailers.yml");
        Files.writeString(path, "meta: kept\ntrailers:\n  " + active + ":\n    type: old\n  " + deferred
                + ":\n    type: unknown_future_type\n    world: missing-world\n    arbitrary: preserved\n");
        return path;
    }
    @Test void updatesOnlyManagedRecordsAndPreservesDeferredData() throws Exception {
        Path path = original(); byte[] snapshot = TrailerSnapshotMerge.read(path);
        TrailerSnapshotMerge.write(path, snapshot, Set.of(active, added),
                Map.of(active, Map.of("type", "updated"), added, Map.of("type", "new")));
        YamlConfiguration result = new YamlConfiguration(); result.load(path.toFile());
        assertEquals("kept", result.getString("meta"));
        assertEquals("updated", result.getString("trailers." + active + ".type"));
        assertEquals("new", result.getString("trailers." + added + ".type"));
        assertEquals("unknown_future_type", result.getString("trailers." + deferred + ".type"));
        assertEquals("preserved", result.getString("trailers." + deferred + ".arbitrary"));
        TrailerSnapshotMerge.write(path, TrailerSnapshotMerge.read(path), Set.of(active), Map.of());
        result.load(path.toFile());
        assertFalse(result.contains("trailers." + active));
        assertTrue(result.contains("trailers." + deferred));
    }
    @Test void refusesStaleMalformedAndUnownedChangesWithoutModifyingFile() throws Exception {
        Path path = original(); byte[] old = TrailerSnapshotMerge.read(path);
        Files.writeString(path, "changed: true\n");
        assertThrows(IOException.class, () -> TrailerSnapshotMerge.write(path, old, Set.of(active), Map.of()));
        assertEquals("changed: true\n", Files.readString(path));
        Files.writeString(path, "trailers: [\n"); byte[] malformed = TrailerSnapshotMerge.read(path);
        assertThrows(IOException.class, () -> TrailerSnapshotMerge.write(path, malformed, Set.of(), Map.of()));
        assertArrayEquals(malformed, Files.readAllBytes(path));
        assertThrows(IOException.class, () -> TrailerSnapshotMerge.write(path, malformed, Set.of(), Map.of(active, Map.of("type", "x"))));
        assertArrayEquals(malformed, Files.readAllBytes(path));
    }
    @Test void detectsMissingManagedRecordAndHandlesAbsentFile() throws Exception {
        Path path = dir.resolve("new.yml");
        assertNull(TrailerSnapshotMerge.read(path));
        assertThrows(IOException.class, () -> TrailerSnapshotMerge.write(path, null, Set.of(active), Map.of()));
        assertFalse(Files.exists(path));
        TrailerSnapshotMerge.write(path, null, Set.of(active), Map.of(active, Map.of("type", "test")));
        assertTrue(Files.exists(path));
    }
}
