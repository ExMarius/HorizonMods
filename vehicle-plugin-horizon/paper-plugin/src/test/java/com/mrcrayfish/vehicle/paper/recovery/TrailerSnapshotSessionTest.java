package com.mrcrayfish.vehicle.paper.recovery;

import com.mrcrayfish.vehicle.paper.persistence.TrailerSnapshotSession;
import org.bukkit.configuration.file.YamlConfiguration;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Map;
import java.util.UUID;
import static org.junit.jupiter.api.Assertions.*;

class TrailerSnapshotSessionTest {
    @TempDir Path dir;
    @Test void deferredRecordSurvivesMultipleSavesAndRestart() throws Exception {
        Path file = dir.resolve("trailers.yml");
        UUID loaded = UUID.randomUUID(), deferred = UUID.randomUUID(), created = UUID.randomUUID();
        Files.writeString(file, "trailers:\n  " + loaded + ":\n    type: old\n  " + deferred
                + ":\n    type: future\n    world: unavailable\n    opaque: do-not-lose\n");
        TrailerSnapshotSession first = new TrailerSnapshotSession(file);
        first.claimLoaded(loaded);
        assertThrows(IOException.class, () -> first.registerNew(deferred));
        first.registerNew(created);
        first.save(Map.of(loaded, Map.of("type", "updated"), created, Map.of("type", "new")));
        first.save(Map.of(created, Map.of("type", "newer")));
        TrailerSnapshotSession restart = new TrailerSnapshotSession(file);
        restart.claimLoaded(created);
        assertThrows(IOException.class, () -> restart.registerNew(deferred));
        restart.save(Map.of(created, Map.of("type", "after-restart")));
        YamlConfiguration result = new YamlConfiguration(); result.load(file.toFile());
        assertFalse(result.contains("trailers." + loaded));
        assertEquals("after-restart", result.getString("trailers." + created + ".type"));
        assertEquals("do-not-lose", result.getString("trailers." + deferred + ".opaque"));
    }
    @Test void failurePoisonsSessionAndDoesNotOverwriteExternalChanges() throws Exception {
        Path file = dir.resolve("trailers.yml"); UUID id = UUID.randomUUID();
        TrailerSnapshotSession session = new TrailerSnapshotSession(file);
        session.registerNew(id);
        Files.writeString(file, "external: data\n");
        assertThrows(IOException.class, () -> session.save(Map.of(id, Map.of("type", "new"))));
        assertThrows(IOException.class, () -> session.save(Map.of()));
        assertEquals("external: data\n", Files.readString(file));
    }
    @Test void removedBeforeFirstSaveNeedsNoTombstone() throws Exception {
        Path file = dir.resolve("trailers.yml"); UUID id = UUID.randomUUID();
        TrailerSnapshotSession session = new TrailerSnapshotSession(file);
        session.registerNew(id);
        session.save(Map.of());
        session.registerNew(id);
        session.save(Map.of(id, Map.of("type", "new")));
        assertTrue(Files.readString(file).contains(id.toString()));
    }
    @Test void unknownAndMalformedRecordsCannotBeClaimed() throws Exception {
        Path file = dir.resolve("trailers.yml"); UUID id = UUID.randomUUID();
        Files.writeString(file, "trailers:\n  " + id + ": not-a-record\n");
        TrailerSnapshotSession session = new TrailerSnapshotSession(file);
        assertThrows(IOException.class, () -> session.claimLoaded(id));
        assertThrows(IOException.class, () -> session.registerNew(id));
        assertThrows(IOException.class, () -> session.claimLoaded(UUID.randomUUID()));
        session.save(Map.of());
        assertTrue(Files.readString(file).contains("not-a-record"));
        Files.writeString(file, "trailers: [\n");
        assertThrows(IOException.class, () -> new TrailerSnapshotSession(file));
    }
}
