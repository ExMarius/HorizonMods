package com.mrcrayfish.vehicle.paper.persistence;

import com.mrcrayfish.vehicle.paper.recovery.RecoveryJournal;
import java.io.IOException;
import java.nio.file.Path;
import java.util.List;
import java.util.Objects;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.atomic.AtomicBoolean;

/** Ordered journal I/O for a future live recovery coordinator. All calls must
 * come from the owner thread; completion callbacks must not mutate Paper state.
 * No vehicle may move until its reservation AND full vehicle snapshot are known
 * durable. This class alone does not implement that multi-file transaction. */
public final class RecoveryOrderedJournal implements AutoCloseable {
    private final Thread owner = Thread.currentThread();
    private final RecoveryJournal reader;
    private final RecoverySerializedWriter writer;
    private final AtomicBoolean failed = new AtomicBoolean();
    private boolean closed, submitted;

    public RecoveryOrderedJournal(Path path) throws IOException {
        Objects.requireNonNull(path, "path");
        reader = new RecoveryJournal(path);
        reader.read(); // fail closed before a writer can overwrite a corrupt journal
        writer = new RecoverySerializedWriter(path);
    }
    public List<RecoveryJournal.Entry> readAtStartup() throws IOException {
        requireOwner();
        if (closed || submitted) throw new IOException("Recovery journal not in startup state");
        return reader.read();
    }
    public CompletableFuture<Void> write(List<RecoveryJournal.Entry> entries) throws IOException {
        requireOwner();
        if (closed || failed.get()) throw new IOException("Recovery journal unavailable");
        byte[] snapshot = RecoveryJournal.encode(entries);
        CompletableFuture<Void> result = writer.submit(snapshot);
        submitted = true;
        result.whenComplete((ignored, error) -> { if (error != null) failed.set(true); });
        return result;
    }
    private void requireOwner() {
        if (Thread.currentThread() != owner) throw new IllegalStateException("Wrong recovery journal owner thread");
    }
    @Override public void close() throws IOException {
        requireOwner();
        if (closed) return;
        closed = true;
        writer.close();
    }
}
