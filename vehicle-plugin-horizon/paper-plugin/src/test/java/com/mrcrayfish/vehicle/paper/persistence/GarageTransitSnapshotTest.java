package com.mrcrayfish.vehicle.paper.persistence;

import org.bukkit.configuration.file.YamlConfiguration;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.UUID;
import static org.junit.jupiter.api.Assertions.*;

class GarageTransitSnapshotTest {
    @TempDir Path dir;
    UUID truck=UUID.randomUUID(),car=UUID.randomUUID(),ownerA=UUID.randomUUID(),ownerB=UUID.randomUUID();
    YamlConfiguration snapshot() {
        var yaml=new YamlConfiguration();yaml.set("metadata", "keep");
        for(UUID id:List.of(truck,car)) {
            String p="vehicles."+id;yaml.set(p+".type","dacia_logan_police");
            yaml.set(p+".owner",(id.equals(truck)?ownerA:ownerB).toString());
            yaml.set(p+".storage.items",List.of("apple","stone"));
        }
        return yaml;
    }
    @Test void reservesBothThenRecoversWithoutDuplicatingOrReassigning() throws Exception {
        var yaml=snapshot(); GarageTransitSnapshot.reserve(yaml,truck,car);
        assertFalse(yaml.contains("vehicles."+truck));assertFalse(yaml.contains("vehicles."+car));
        assertEquals("OUT_TOWING",yaml.getString("garage."+truck+".recovery-transit"));
        assertEquals("TOWED",yaml.getString("garage."+car+".recovery-transit"));
        Path file=dir.resolve("vehicles.yml");yaml.save(file.toFile());
        assertEquals(2,GarageTransitSnapshot.recoverAtStartup(file));
        var restored=new YamlConfiguration();restored.load(file.toFile());
        assertEquals(ownerA.toString(),restored.getString("garage."+truck+".owner"));
        assertEquals(ownerB.toString(),restored.getString("garage."+car+".owner"));
        assertEquals(List.of("apple","stone"),restored.getStringList("garage."+car+".storage.items"));
        assertFalse(restored.contains("garage."+truck+".recovery-transit"));
        assertEquals("keep",restored.getString("metadata"));
        byte[] before=Files.readAllBytes(file);
        assertEquals(0,GarageTransitSnapshot.recoverAtStartup(file));assertArrayEquals(before,Files.readAllBytes(file));
    }
    @Test void invalidOwnerOrDuplicateNeverChangesInput() throws Exception {
        for(boolean duplicate:List.of(false,true)) {
            var yaml=snapshot();
            if(duplicate)yaml.set("garage."+car+".type","car");else yaml.set("vehicles."+car+".owner",null);
            String before=yaml.saveToString();
            assertThrows(IOException.class,()->GarageTransitSnapshot.reserve(yaml,truck,car));
            assertEquals(before,yaml.saveToString());
        }
    }
    @Test void startupRejectsDuplicateOrUnknownStatusWithoutWriting() throws Exception {
        for(boolean duplicate:List.of(false,true)) {
            var yaml=snapshot();GarageTransitSnapshot.reserve(yaml,truck,car);
            if(duplicate)yaml.set("vehicles."+car+".type","car");
            else yaml.set("garage."+car+".recovery-transit","UNKNOWN");
            Path file=dir.resolve("vehicles.yml");yaml.save(file.toFile());byte[] before=Files.readAllBytes(file);
            assertThrows(IOException.class,()->GarageTransitSnapshot.recoverAtStartup(file));
            assertArrayEquals(before,Files.readAllBytes(file));
        }
    }
}
