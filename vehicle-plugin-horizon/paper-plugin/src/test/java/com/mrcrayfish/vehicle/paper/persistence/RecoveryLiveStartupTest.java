package com.mrcrayfish.vehicle.paper.persistence;

import com.mrcrayfish.vehicle.paper.recovery.RecoveryEntityTombstones;
import com.mrcrayfish.vehicle.paper.recovery.RecoveryLiveJournal;
import org.bukkit.configuration.file.YamlConfiguration;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import static org.junit.jupiter.api.Assertions.*;

class RecoveryLiveStartupTest {
    @TempDir Path dir;
    UUID truck=UUID.randomUUID(),car=UUID.randomUUID(),truckOwner=UUID.randomUUID(),carOwner=UUID.randomUUID();
    UUID oldTruck=UUID.randomUUID(),oldCar=UUID.randomUUID();
    private RecoveryLiveJournal.Entry entry(){return new RecoveryLiveJournal.Entry(truck,car,oldTruck,oldCar);}
    private String row(UUID id,UUID owner){return "  "+id+":\n    type: dacia_logan_police\n    owner: "+owner+"\n";}
    private void writeJournal()throws IOException{Files.write(dir.resolve("recovery-live-v2.journal"),RecoveryLiveJournal.encode(List.of(entry())));}
    private void assertGaraged()throws Exception{
        var yaml=new YamlConfiguration();yaml.load(dir.resolve("vehicles.yml").toFile());
        assertFalse(yaml.contains("vehicles."+truck));assertFalse(yaml.contains("vehicles."+car));
        assertEquals(truckOwner.toString(),yaml.getString("garage."+truck+".owner"));
        assertEquals(carOwner.toString(),yaml.getString("garage."+car+".owner"));
    }
    @Test void replayRecordsOldSessionsThenGaragesBothOwners()throws Exception{
        Files.writeString(dir.resolve("vehicles.yml"),"vehicles:\n"+row(truck,truckOwner)+row(car,carOwner));
        writeJournal();
        assertEquals(1,RecoveryLiveStartup.reconcile(dir));
        assertGaraged();
        assertEquals(Set.of(oldTruck,oldCar),RecoveryEntityTombstones.decode(Files.readAllBytes(dir.resolve("recovery-sessions.dat"))));
        assertTrue(RecoveryLiveJournal.read(dir.resolve("recovery-live-v2.journal")).isEmpty());
        assertEquals(0,RecoveryLiveStartup.reconcile(dir));
    }
    @Test void replayAfterSnapshotReplacementIsIdempotent()throws Exception{
        Files.writeString(dir.resolve("vehicles.yml"),"garage:\n"+row(truck,truckOwner)+row(car,carOwner));
        writeJournal();
        Files.write(dir.resolve("recovery-sessions.dat"),RecoveryEntityTombstones.encode(Set.of(oldTruck,oldCar)));
        assertEquals(1,RecoveryLiveStartup.reconcile(dir));assertGaraged();
        assertEquals(Set.of(oldTruck,oldCar),RecoveryEntityTombstones.decode(Files.readAllBytes(dir.resolve("recovery-sessions.dat"))));
    }
    @Test void missingVehicleKeepsJournalForRepairAndDoesNotAssignOwner()throws Exception{
        Files.writeString(dir.resolve("vehicles.yml"),"vehicles:\n"+row(truck,truckOwner));
        writeJournal();byte[] journal=Files.readAllBytes(dir.resolve("recovery-live-v2.journal"));
        assertThrows(IOException.class,()->RecoveryLiveStartup.reconcile(dir));
        assertArrayEquals(journal,Files.readAllBytes(dir.resolve("recovery-live-v2.journal")));
        assertEquals(Set.of(oldTruck,oldCar),RecoveryEntityTombstones.decode(Files.readAllBytes(dir.resolve("recovery-sessions.dat"))));
    }
    @Test void rejectsDuplicateAndCorruptJournalBeforeChangingAnything()throws Exception{
        assertThrows(IOException.class,()->RecoveryLiveJournal.encode(List.of(entry(),entry())));
        byte[] corrupt=RecoveryLiveJournal.encode(List.of(entry()));corrupt[12]^=1;
        Path file=dir.resolve("recovery-live-v2.journal");Files.write(file,corrupt);
        assertThrows(IOException.class,()->RecoveryLiveStartup.reconcile(dir));
        assertArrayEquals(corrupt,Files.readAllBytes(file));
        assertFalse(Files.exists(dir.resolve("recovery-sessions.dat")));
    }
}
