package com.mrcrayfish.vehicle.paper.recovery;

import com.mrcrayfish.vehicle.paper.persistence.RecoveryGarageFallback;
import com.mrcrayfish.vehicle.paper.persistence.RecoveryTestStartup;
import org.bukkit.configuration.file.YamlConfiguration;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;

/** Offline fixture tests: not evidence that live vehicle saves are transactional. */
class RecoveryTestStartupTest {
    @TempDir Path dir;
    private final UUID truck = UUID.randomUUID(), car = UUID.randomUUID(), operator = UUID.randomUUID();
    private final UUID truckOwner = UUID.randomUUID(), carOwner = UUID.randomUUID();
    private RecoveryJournal journal() { return new RecoveryJournal(dir.resolve("recovery-test.journal")); }
    private RecoveryJournal.Entry entry(UUID a, UUID b) {
        return new RecoveryJournal.Entry(a, b, operator, RecoveryInterlock.Mode.WINCH, RecoveryInterlock.Phase.SECURED);
    }
    private String row(UUID id, UUID owner) {
        return "  " + id + ":\n    type: dacia_logan_police\n    owner: " + owner + "\n";
    }
    private void assertGaraged(UUID id, UUID owner) throws Exception {
        YamlConfiguration yaml = new YamlConfiguration();
        yaml.load(dir.resolve("vehicles.yml").toFile());
        assertFalse(yaml.contains("vehicles." + id));
        assertEquals(owner.toString(), yaml.getString("garage." + id + ".owner"));
    }

    @Test void interruptedAfterSnapshotReplacementReplaysBeforeClearingJournal() throws Exception {
        Files.writeString(dir.resolve("vehicles.yml"), "vehicles:\n" + row(truck, truckOwner) + row(car, carOwner));
        journal().write(List.of(entry(truck, car)));
        // Simulate crash after durable snapshot replacement, before clearing the journal.
        RecoveryGarageFallback.reconcile(dir.resolve("vehicles.yml"), truck, car);
        assertEquals(1, RecoveryTestStartup.reconcile(dir));
        assertGaraged(truck, truckOwner); assertGaraged(car, carOwner);
        assertTrue(journal().read().isEmpty());
        assertEquals(0, RecoveryTestStartup.reconcile(dir));
    }

    @Test void failureInLaterPairKeepsJournalAndAllowsRetryOfEarlierPair() throws Exception {
        UUID otherTruck = UUID.randomUUID(), otherCar = UUID.randomUUID();
        UUID otherTruckOwner = UUID.randomUUID(), otherCarOwner = UUID.randomUUID();
        Path snapshot = dir.resolve("vehicles.yml");
        Files.writeString(snapshot, "vehicles:\n" + row(truck, truckOwner) + row(car, carOwner) + row(otherTruck, otherTruckOwner));
        var entries = List.of(entry(truck, car), entry(otherTruck, otherCar));
        journal().write(entries);
        assertThrows(IOException.class, () -> RecoveryTestStartup.reconcile(dir));
        assertEquals(entries, journal().read());
        assertGaraged(truck, truckOwner); assertGaraged(car, carOwner);
        // Repair the missing record offline; the first pair must remain idempotent.
        YamlConfiguration yaml = new YamlConfiguration(); yaml.load(snapshot.toFile());
        yaml.set("vehicles." + otherCar + ".type", "dacia_logan_police");
        yaml.set("vehicles." + otherCar + ".owner", otherCarOwner.toString());
        yaml.save(snapshot.toFile());
        assertEquals(2, RecoveryTestStartup.reconcile(dir));
        for (UUID[] pair : List.of(new UUID[]{truck, truckOwner}, new UUID[]{car, carOwner},
                new UUID[]{otherTruck, otherTruckOwner}, new UUID[]{otherCar, otherCarOwner})) {
            assertGaraged(pair[0], pair[1]);
        }
        assertTrue(journal().read().isEmpty());
    }

    @Test void corruptJournalFailsClosedWithoutTouchingSnapshot() throws Exception {
        Path snapshot = dir.resolve("vehicles.yml");
        Files.writeString(snapshot, "vehicles:\n" + row(truck, truckOwner) + row(car, carOwner));
        byte[] before = Files.readAllBytes(snapshot);
        Files.write(dir.resolve("recovery-test.journal"), new byte[]{1, 2, 3});
        assertThrows(IOException.class, () -> RecoveryTestStartup.reconcile(dir));
        assertArrayEquals(before, Files.readAllBytes(snapshot));
    }
}
