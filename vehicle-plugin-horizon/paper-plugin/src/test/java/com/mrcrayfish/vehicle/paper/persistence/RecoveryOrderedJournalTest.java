package com.mrcrayfish.vehicle.paper.persistence;

import com.mrcrayfish.vehicle.paper.recovery.RecoveryInterlock;
import com.mrcrayfish.vehicle.paper.recovery.RecoveryJournal;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import static org.junit.jupiter.api.Assertions.*;

class RecoveryOrderedJournalTest {
    @TempDir Path dir;
    @Test void queuedReservationsAreSnapshotsAndRemainOrdered() throws Exception {
        Path file = dir.resolve("journal");
        var entry = new RecoveryJournal.Entry(UUID.randomUUID(), UUID.randomUUID(), UUID.randomUUID(),
                RecoveryInterlock.Mode.WINCH, RecoveryInterlock.Phase.MOVING);
        var entries = new ArrayList<>(List.of(entry));
        try (var journal = new RecoveryOrderedJournal(file)) {
            assertTrue(journal.readAtStartup().isEmpty());
            var first = journal.write(entries);
            entries.clear();
            var second = journal.write(entries);
            first.get(5, TimeUnit.SECONDS); second.get(5, TimeUnit.SECONDS);
            assertThrows(IOException.class, journal::readAtStartup);
        }
        assertTrue(new RecoveryJournal(file).read().isEmpty());
        try (var journal = new RecoveryOrderedJournal(file)) {
            journal.write(List.of(entry)).get(5, TimeUnit.SECONDS);
        }
        assertEquals(List.of(entry), new RecoveryJournal(file).read());
    }
    @Test void refusesToOverwriteCorruptJournal() throws Exception {
        Path file = dir.resolve("journal"); byte[] corrupt = {1, 2, 3}; Files.write(file, corrupt);
        assertThrows(IOException.class, () -> new RecoveryOrderedJournal(file));
        assertArrayEquals(corrupt, Files.readAllBytes(file));
    }
}
