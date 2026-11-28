package com.mrcrayfish.vehicle.paper.recovery;

import com.mrcrayfish.vehicle.paper.persistence.RecoveryGarageFallback;
import org.bukkit.configuration.file.YamlConfiguration;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.UUID;
import static org.junit.jupiter.api.Assertions.*;

class RecoveryGarageFallbackTest {
    @TempDir Path dir;
    private final UUID truck=UUID.randomUUID(), car=UUID.randomUUID(), firstOwner=UUID.randomUUID(), secondOwner=UUID.randomUUID();
    private Path input(String text)throws IOException {Path p=dir.resolve("vehicles.yml");Files.writeString(p,text);return p;}
    private String row(UUID id, UUID owner) {
        return "  "+id+":\n    type: dacia_logan_police\n    owner: "+owner+"\n    fuel: 42.0\n    storage:\n      compartments:\n        trunk: [apple, stone]\n";
    }
    @Test void sendsBothSnapshotsToTheirOwnGaragesAndIsIdempotent() throws Exception {
        Path path=input("metadata: preserved\nvehicles:\n"+row(truck,firstOwner)+row(car,secondOwner));
        assertEquals(RecoveryGarageFallback.Outcome.MOVED,RecoveryGarageFallback.reconcile(path,truck,car));
        YamlConfiguration yaml=new YamlConfiguration();yaml.load(path.toFile());
        assertEquals("preserved",yaml.getString("metadata"));
        assertFalse(yaml.contains("vehicles."+truck));assertFalse(yaml.contains("vehicles."+car));
        assertEquals(firstOwner.toString(),yaml.getString("garage."+truck+".owner"));
        assertEquals(secondOwner.toString(),yaml.getString("garage."+car+".owner"));
        assertEquals(42,yaml.getDouble("garage."+car+".fuel"));
        assertEquals(java.util.List.of("apple","stone"),yaml.getStringList("garage."+car+".storage.compartments.trunk"));
        byte[] before=Files.readAllBytes(path);
        assertEquals(RecoveryGarageFallback.Outcome.ALREADY_GARAGED,RecoveryGarageFallback.reconcile(path,truck,car));
        assertArrayEquals(before,Files.readAllBytes(path));
    }
    @Test void refusesMissingUnknownOwnerOrDuplicateWithoutPartialWrites() throws Exception {
        for(String text:new String[]{
                "vehicles:\n"+row(truck,firstOwner),
                "vehicles:\n"+row(truck,firstOwner)+"  "+car+":\n    type: car\n",
                "vehicles:\n"+row(truck,firstOwner)+row(car,secondOwner)+"garage:\n"+row(truck,firstOwner),
                "vehicles: [broken\n"}) {
            Path path=input(text);byte[] before=Files.readAllBytes(path);
            assertThrows(IOException.class,()->RecoveryGarageFallback.reconcile(path,truck,car));
            assertArrayEquals(before,Files.readAllBytes(path));
        }
    }
    @Test void completesInterruptedRecoveryWhenOneIsAlreadyGaraged() throws Exception {
        Path path=input("vehicles:\n"+row(car,secondOwner)+"garage:\n"+row(truck,firstOwner));
        assertEquals(RecoveryGarageFallback.Outcome.MOVED,RecoveryGarageFallback.reconcile(path,truck,car));
        YamlConfiguration yaml=new YamlConfiguration();yaml.load(path.toFile());
        assertTrue(yaml.contains("garage."+truck));assertTrue(yaml.contains("garage."+car));
        assertFalse(yaml.contains("vehicles."+car));
    }
}
