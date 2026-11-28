package com.mrcrayfish.vehicle.paper.persistence;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.file.AtomicMoveNotSupportedException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.nio.file.StandardOpenOption;
import java.util.Objects;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

/** Experimental ordered disk writer, NOT wired to gameplay. Construct and submit
 * only on the owning thread (Paper main thread in a future integration). Bytes
 * are copied before enqueueing; acknowledgement means file and directory force
 * succeeded. A failed write poisons the writer and all later writes fail closed.
 * This alone does not protect against other writers or ensure crash-safe gameplay. */
public final class RecoverySerializedWriter implements AutoCloseable {
    @FunctionalInterface interface Sink { void write(byte[] snapshot) throws IOException; }
    private final Thread owner = Thread.currentThread();
    private final ExecutorService executor = Executors.newSingleThreadExecutor();
    private final Sink sink;
    // Only accessed by the single worker, never by the owner thread.
    private IOException failure;
    private boolean closed;

    public RecoverySerializedWriter(Path file) {
        Objects.requireNonNull(file, "file");
        Path path = file.toAbsolutePath();
        this.sink = bytes -> writeAtomically(path, bytes);
    }
    RecoverySerializedWriter(Sink sink) { this.sink = Objects.requireNonNull(sink); }

    public CompletableFuture<Void> submit(byte[] snapshot) {
        requireOwner();
        if (closed) throw new IllegalStateException("Writer closed");
        byte[] copy = Objects.requireNonNull(snapshot, "snapshot").clone();
        CompletableFuture<Void> result = new CompletableFuture<>();
        executor.execute(() -> {
            if (failure != null) {
                result.completeExceptionally(new IOException("Prior recovery write failed", failure));
                return;
            }
            try {
                sink.write(copy);
                result.complete(null);
            } catch (IOException | RuntimeException error) {
                failure = error instanceof IOException io ? io : new IOException("Recovery write failed", error);
                result.completeExceptionally(failure);
            }
        });
        return result;
    }

    private static void writeAtomically(Path path, byte[] snapshot) throws IOException {
        Path parent = path.getParent();
        if (parent == null || !Files.isDirectory(parent)) throw new IOException("Missing snapshot directory");
        Path temp = Files.createTempFile(parent, ".recovery-write-", ".tmp");
        try {
            try (FileChannel channel = FileChannel.open(temp, StandardOpenOption.WRITE, StandardOpenOption.TRUNCATE_EXISTING)) {
                ByteBuffer bytes = ByteBuffer.wrap(snapshot);
                while (bytes.hasRemaining()) channel.write(bytes);
                channel.force(true);
            }
            try { Files.move(temp, path, StandardCopyOption.ATOMIC_MOVE, StandardCopyOption.REPLACE_EXISTING); }
            catch (AtomicMoveNotSupportedException e) { throw new IOException("Atomic recovery write unavailable", e); }
            try (FileChannel directory = FileChannel.open(parent, StandardOpenOption.READ)) { directory.force(true); }
        } finally { Files.deleteIfExists(temp); }
    }

    private void requireOwner() {
        if (Thread.currentThread() != owner) throw new IllegalStateException("Wrong recovery writer owner thread");
    }
    /** Waits for queued work. Do not call on the Paper thread during gameplay. */
    @Override public void close() throws IOException {
        requireOwner();
        if (closed) return;
        closed = true;
        executor.shutdown();
        try {
            if (!executor.awaitTermination(30, TimeUnit.SECONDS)) throw new IOException("Recovery writer did not stop");
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new IOException("Interrupted waiting for recovery writer", e);
        }
    }
}
