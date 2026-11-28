package com.mrcrayfish.vehicle.paper.recovery;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.UUID;
import static org.junit.jupiter.api.Assertions.*;
import static com.mrcrayfish.vehicle.paper.recovery.RecoveryInterlock.*;
class RecoveryJournalTest {
    @TempDir Path temp;
    private static RecoveryJournal.Entry entry(Phase p){return new RecoveryJournal.Entry(UUID.randomUUID(),UUID.randomUUID(),UUID.randomUUID(),Mode.WINCH,p);}
    @Test void roundTripAndRestartAreFailClosed()throws Exception{
        var journal=new RecoveryJournal(temp.resolve("journal.dat"));assertEquals(List.of(),journal.read());
        var moving=entry(Phase.MOVING);var secured=entry(Phase.SECURED);
        journal.write(List.of(moving,secured));var loaded=journal.read();assertEquals(List.of(moving,secured),loaded);
        assertTrue(loaded.get(0).needsOperatorReconciliation());assertTrue(loaded.get(1).needsOperatorReconciliation());
        journal.write(List.of(secured));assertEquals(List.of(secured),journal.read());
    }
    @Test void corruptOrTruncatedFileFailsRatherThanClearingLocks()throws Exception{
        Path path=temp.resolve("journal.dat");var journal=new RecoveryJournal(path);journal.write(List.of(entry(Phase.PAUSED)));
        byte[] data=Files.readAllBytes(path);data[15]^=0x40;Files.write(path,data);
        assertThrows(IOException.class,journal::read);
        assertThrows(IOException.class,()->journal.write(List.of()));
        assertArrayEquals(data,Files.readAllBytes(path));
        Files.write(path,new byte[]{1,2,3});assertThrows(IOException.class,journal::read);
    }
    @Test void duplicatedOrInvalidVehicleEntriesAreRejectedBeforeOverwriting()throws Exception{
        Path path=temp.resolve("journal.dat");var journal=new RecoveryJournal(path);var first=entry(Phase.READY);
        journal.write(List.of(first));
        var duplicate=new RecoveryJournal.Entry(UUID.randomUUID(),first.target(),UUID.randomUUID(),Mode.DRIVEN,Phase.MOVING);
        assertThrows(IOException.class,()->journal.write(List.of(first,duplicate)));
        assertEquals(List.of(first),journal.read());
        assertThrows(IllegalArgumentException.class,()->new RecoveryJournal.Entry(first.carrier(),first.carrier(),first.operator(),Mode.WINCH,Phase.READY));
        assertThrows(IllegalArgumentException.class,()->new RecoveryJournal.Entry(first.carrier(),first.target(),first.operator(),Mode.WINCH,Phase.IDLE));
    }
}
