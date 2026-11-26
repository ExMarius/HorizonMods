package com.mrcrayfish.vehicle.paper.persistence;

import com.mrcrayfish.vehicle.paper.recovery.RecoveryJournal;
import java.io.IOException;
import java.nio.file.Path;
import java.util.List;

/** Disposable-server-only boot experiment. Never enabled by normal plugin config.
 * Call before loading vehicles and with no concurrent writer. A real production
 * implementation still needs durable write ordering before EVERY operation. */
public final class RecoveryTestStartup {
    private RecoveryTestStartup() { }
    public static int reconcile(Path directory) throws IOException {
        var journal=new RecoveryJournal(directory.resolve("recovery-test.journal"));
        var entries=journal.read();
        for(var entry:entries) RecoveryGarageFallback.reconcile(directory.resolve("vehicles.yml"),entry.carrier(),entry.target());
        if(!entries.isEmpty())journal.write(List.of());
        return entries.size();
    }
}
