package com.mrcrayfish.vehicle.paper.persistence;

import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.configuration.InvalidConfigurationException;
import org.bukkit.configuration.file.YamlConfiguration;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.AtomicMoveNotSupportedException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.nio.file.StandardOpenOption;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.UUID;

/** Experimental OFFLINE startup reconciliation, not wired to the server.
 * Both vehicle snapshots are moved to their respective owners' garages in a
 * single atomic vehicles.yml replacement. The caller must stop all writers and
 * remove/disable world entities before calling this; it is not a live operation.
 * A separate durable journal must establish which IDs need reconciliation. */
public final class RecoveryGarageFallback {
    private RecoveryGarageFallback() { }
    public enum Outcome { MOVED, ALREADY_GARAGED }

    public static Outcome reconcile(Path file, UUID carrier, UUID target) throws IOException {
        if(file==null || carrier==null || target==null || carrier.equals(target))throw new IOException("Invalid recovery identities");
        Path path=file.toAbsolutePath();byte[] expected=TrailerSnapshotMerge.read(path);
        if(expected==null)throw new IOException("Missing vehicle snapshot");
        YamlConfiguration yaml=new YamlConfiguration();
        try { yaml.loadFromString(TrailerSnapshotMerge.decode(expected)); }
        catch(InvalidConfigurationException | IllegalArgumentException e) {throw new IOException("Invalid vehicle snapshot",e);}
        if((yaml.contains("vehicles")&&!yaml.isConfigurationSection("vehicles"))
                ||(yaml.contains("garage")&&!yaml.isConfigurationSection("garage")))throw new IOException("Invalid snapshot sections");
        boolean changed=false;
        for(UUID id:new UUID[]{carrier,target}) {
            String active="vehicles."+id, garaged="garage."+id;
            boolean inWorld=yaml.contains(active), inGarage=yaml.contains(garaged);
            if(inWorld==inGarage)throw new IOException("Vehicle missing or duplicated: "+id);
            ConfigurationSection record=yaml.getConfigurationSection(inWorld?active:garaged);
            if(record==null || record.getString("type", "").isBlank())throw new IOException("Invalid vehicle record: "+id);
            try { UUID.fromString(record.getString("owner", "")); }
            catch(IllegalArgumentException e) {throw new IOException("Unknown vehicle owner: "+id,e);}
            if(inWorld) {
                Map<String,Object> copy=copy(record);
                yaml.set(garaged,copy);yaml.set(active,null);changed=true;
            }
        }
        if(!changed)return Outcome.ALREADY_GARAGED;
        byte[] result=yaml.saveToString().getBytes(StandardCharsets.UTF_8);
        Path parent=path.getParent();if(parent==null)throw new IOException("Missing snapshot directory");
        Path temp=Files.createTempFile(parent,".recovery-garage-", ".tmp");
        try {
            try(FileChannel channel=FileChannel.open(temp,StandardOpenOption.WRITE,StandardOpenOption.TRUNCATE_EXISTING)) {
                ByteBuffer bytes=ByteBuffer.wrap(result);while(bytes.hasRemaining())channel.write(bytes);channel.force(true);
            }
            if(!java.util.Arrays.equals(expected,TrailerSnapshotMerge.read(path)))throw new IOException("Vehicle snapshot changed");
            try {Files.move(temp,path,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);}
            catch(AtomicMoveNotSupportedException e){throw new IOException("Atomic vehicle snapshot update unavailable",e);}
            try(FileChannel directory=FileChannel.open(parent,StandardOpenOption.READ)){directory.force(true);}
        } finally {Files.deleteIfExists(temp);}
        return Outcome.MOVED;
    }
    private static Map<String,Object> copy(ConfigurationSection section) {
        Map<String,Object> result=new LinkedHashMap<>();
        for(var entry:section.getValues(false).entrySet())
            result.put(entry.getKey(),entry.getValue() instanceof ConfigurationSection child?copy(child):entry.getValue());
        return result;
    }
}
