package com.mrcrayfish.vehicle.paper.persistence;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;
import static org.junit.jupiter.api.Assertions.*;

class RecoverySerializedWriterTest {
    @TempDir Path dir;
    private static byte[] bytes(String text) { return text.getBytes(StandardCharsets.UTF_8); }

    @Test void serializesCopiedSnapshotsInSubmissionOrder() throws Exception {
        var entered = new CountDownLatch(1); var release = new CountDownLatch(1);
        var writes = new ArrayList<String>();
        try (var writer = new RecoverySerializedWriter((RecoverySerializedWriter.Sink) data -> {
            if (writes.isEmpty()) {
                entered.countDown();
                try { if (!release.await(5, TimeUnit.SECONDS)) throw new IOException("timeout"); }
                catch (InterruptedException e) { Thread.currentThread().interrupt(); throw new IOException(e); }
            }
            writes.add(new String(data, StandardCharsets.UTF_8));
        })) {
            byte[] first = bytes("one");
            var a = writer.submit(first);
            assertTrue(entered.await(5, TimeUnit.SECONDS));
            var b = writer.submit(bytes("two"));
            first[0] = 'X';
            release.countDown(); a.get(5, TimeUnit.SECONDS); b.get(5, TimeUnit.SECONDS);
            assertEquals(List.of("one", "two"), writes);
        }
    }
    @Test void failurePreventsLaterSnapshotsFromBeingWritten() throws Exception {
        var calls = new ArrayList<String>();
        try (var writer = new RecoverySerializedWriter((RecoverySerializedWriter.Sink) data -> {
            calls.add(new String(data, StandardCharsets.UTF_8));
            throw new IOException("disk failure");
        })) {
            var first = writer.submit(bytes("first")); var second = writer.submit(bytes("second"));
            assertThrows(ExecutionException.class, () -> first.get(5, TimeUnit.SECONDS));
            assertThrows(ExecutionException.class, () -> second.get(5, TimeUnit.SECONDS));
            assertEquals(List.of("first"), calls);
        }
    }
    @Test void persistsIncreasingTombstoneSnapshotsInOrder() throws Exception {
        var first = java.util.UUID.randomUUID(); var second = java.util.UUID.randomUUID();
        Path file = dir.resolve("entity-tombstones");
        try (var writer = new RecoverySerializedWriter(file)) {
            var firstSave = writer.submit(com.mrcrayfish.vehicle.paper.recovery.RecoveryEntityTombstones.encode(java.util.Set.of(first)));
            var secondSave = writer.submit(com.mrcrayfish.vehicle.paper.recovery.RecoveryEntityTombstones.encode(java.util.Set.of(first, second)));
            firstSave.get(5, TimeUnit.SECONDS); secondSave.get(5, TimeUnit.SECONDS);
        }
        assertEquals(java.util.Set.of(first, second),
                com.mrcrayfish.vehicle.paper.recovery.RecoveryEntityTombstones.decode(Files.readAllBytes(file)));
    }
    @Test void atomicFileWriteAndOwnerEnforcement() throws Exception {
        Path file = dir.resolve("journal");
        try (var writer = new RecoverySerializedWriter(file)) {
            writer.submit(bytes("one")).get(5, TimeUnit.SECONDS);
            writer.submit(bytes("two")).get(5, TimeUnit.SECONDS);
            assertEquals("two", Files.readString(file));
            var thrown = new AtomicReference<Throwable>();
            Thread other = new Thread(() -> { try { writer.submit(bytes("wrong")); } catch (Throwable e) { thrown.set(e); } });
            other.start(); other.join();
            assertInstanceOf(IllegalStateException.class, thrown.get());
        }
        assertEquals("two", Files.readString(file));
    }
}
