package com.mrcrayfish.vehicle.paper.persistence;

import com.mrcrayfish.vehicle.paper.recovery.RecoveryEntityTombstones;
import com.mrcrayfish.vehicle.paper.recovery.RecoveryLiveJournal;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ExecutionException;

/** Boot-only replay before any vehicle/entity guard is loaded and before any
 * writer is active. Live movement does not yet create this journal. The caller
 * must ensure a full durable snapshot existed before every reservation and no
 * other process can write these files. A failure prevents vehicle startup. */
public final class RecoveryLiveStartup {
    private static final long MAX_SESSIONS_BYTES=16L*100_000+16;
    private RecoveryLiveStartup() { }

    public static int reconcile(Path directory) throws IOException {
        Path journalFile=directory.resolve("recovery-live-v2.journal");
        List<RecoveryLiveJournal.Entry> entries=RecoveryLiveJournal.read(journalFile);
        if(entries.isEmpty())return 0;
        Path sessionsFile=directory.resolve("recovery-sessions.dat");
        Set<UUID> sessions=new HashSet<>();
        if(!Files.notExists(sessionsFile)) {
            if(!Files.isRegularFile(sessionsFile) || Files.size(sessionsFile)>MAX_SESSIONS_BYTES)
                throw new IOException("Invalid retired-session registry");
            sessions.addAll(RecoveryEntityTombstones.decode(Files.readAllBytes(sessionsFile)));
        }
        for(var entry:entries) {sessions.add(entry.carrierSession());sessions.add(entry.targetSession());}
        // These tombstones must reach disk before any garage record is committed.
        write(sessionsFile,RecoveryEntityTombstones.encode(sessions));
        Path vehiclesFile=directory.resolve("vehicles.yml");
        for(var entry:entries)
            RecoveryGarageFallback.reconcile(vehiclesFile,entry.carrier(),entry.target());
        // Even an already-garaged snapshot must be durable before clearing the WAL.
        try(var file=java.nio.channels.FileChannel.open(vehiclesFile,java.nio.file.StandardOpenOption.WRITE)) {file.force(true);}
        try(var dir=java.nio.channels.FileChannel.open(directory,java.nio.file.StandardOpenOption.READ)) {dir.force(true);}
        // Replays are idempotent if interrupted after any previous step.
        write(journalFile,RecoveryLiveJournal.encode(List.of()));
        return entries.size();
    }
    private static void write(Path path,byte[] snapshot) throws IOException {
        try(var writer=new RecoverySerializedWriter(path)) {
            try {writer.submit(snapshot).get();}
            catch(InterruptedException e) {Thread.currentThread().interrupt();throw new IOException("Recovery startup interrupted",e);}
            catch(ExecutionException e) {throw new IOException("Recovery startup write failed",e.getCause());}
        }
    }
}
