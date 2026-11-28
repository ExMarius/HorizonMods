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

/** Single-snapshot recovery scheme for future tow operations. NOT wired to
 * live towing. The caller must stop competing writers and lock both vehicles;
 * persist and acknowledge this entire snapshot before changing world entities.
 * Temporary rigs alone cannot enforce garage exclusivity or preserve live edits. */
public final class GarageTransitSnapshot {
    private static final String MARKER="recovery-transit";
    private GarageTransitSnapshot() { }

    /** Move both active records to the garage in one in-memory snapshot.
     * Validation completes before the input is modified. */
    public static void reserve(YamlConfiguration yaml, UUID carrier, UUID target) throws IOException {
        if(yaml==null || carrier==null || target==null || carrier.equals(target))throw new IOException("Invalid transit identities");
        checkSections(yaml);
        Map<UUID,Map<String,Object>> records=new LinkedHashMap<>();
        for(UUID id:new UUID[]{carrier,target}) {
            String active="vehicles."+id, garage="garage."+id;
            if(!yaml.contains(active) || yaml.contains(garage))throw new IOException("Vehicle missing or duplicated: "+id);
            var record=yaml.getConfigurationSection(active);
            validateRecord(record,id);
            if(record.contains(MARKER))throw new IOException("Unexpected transit marker: "+id);
            records.put(id,copy(record));
        }
        for(UUID id:new UUID[]{carrier,target}) {
            String garage="garage."+id;
            ConfigurationSection section=yaml.createSection(garage,records.get(id));
            section.set(MARKER,id.equals(carrier)?"OUT_TOWING":"TOWED");
            yaml.set("vehicles."+id,null);
        }
    }

    /** Offline startup only, before any writer or vehicle spawn. All marked
     * records become ordinary garage entries. Refuses duplicates or bad owners. */
    public static int recoverAtStartup(Path file) throws IOException {
        byte[] expected=TrailerSnapshotMerge.read(file);
        if(expected==null)return 0;
        YamlConfiguration yaml=new YamlConfiguration();
        try {yaml.loadFromString(TrailerSnapshotMerge.decode(expected));}
        catch(InvalidConfigurationException | IllegalArgumentException e){throw new IOException("Invalid vehicle snapshot",e);}
        checkSections(yaml);
        var garage=yaml.getConfigurationSection("garage");
        if(garage==null)return 0;
        int changed=0;
        for(String key:garage.getKeys(false)) {
            var record=garage.getConfigurationSection(key);
            if(record==null || !record.contains(MARKER))continue;
            UUID id;
            try {id=UUID.fromString(key);if(!id.toString().equals(key))throw new IllegalArgumentException();}
            catch(IllegalArgumentException e){throw new IOException("Invalid transit vehicle id",e);}
            String state=record.getString(MARKER,"");
            if(!state.equals("TOWED")&&!state.equals("OUT_TOWING"))throw new IOException("Unknown transit state: "+id);
            validateRecord(record,id);
            if(yaml.contains("vehicles."+id))throw new IOException("Duplicated transit vehicle: "+id);
            record.set(MARKER,null);changed++;
        }
        if(changed==0)return 0;
        byte[] result=yaml.saveToString().getBytes(StandardCharsets.UTF_8);
        Path path=file.toAbsolutePath(), parent=path.getParent();
        if(parent==null)throw new IOException("Missing vehicle snapshot directory");
        Path temp=Files.createTempFile(parent,".transit-recover-", ".tmp");
        try {
            try(FileChannel channel=FileChannel.open(temp,StandardOpenOption.WRITE,StandardOpenOption.TRUNCATE_EXISTING)) {
                ByteBuffer bytes=ByteBuffer.wrap(result);while(bytes.hasRemaining())channel.write(bytes);channel.force(true);
            }
            if(!java.util.Arrays.equals(expected,TrailerSnapshotMerge.read(path)))throw new IOException("Vehicle snapshot changed");
            try {Files.move(temp,path,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);}
            catch(AtomicMoveNotSupportedException e){throw new IOException("Atomic vehicle update unavailable",e);}
            try(FileChannel directory=FileChannel.open(parent,StandardOpenOption.READ)){directory.force(true);}
        } finally {Files.deleteIfExists(temp);}
        return changed;
    }
    private static void checkSections(YamlConfiguration yaml)throws IOException {
        if((yaml.contains("vehicles")&&!yaml.isConfigurationSection("vehicles")) ||
                (yaml.contains("garage")&&!yaml.isConfigurationSection("garage")))throw new IOException("Invalid vehicle sections");
    }
    private static void validateRecord(ConfigurationSection record,UUID id)throws IOException {
        if(record==null || record.getString("type","").isBlank())throw new IOException("Invalid vehicle record: "+id);
        try {UUID.fromString(record.getString("owner",""));}
        catch(IllegalArgumentException e){throw new IOException("Unknown vehicle owner: "+id,e);}
    }
    private static Map<String,Object> copy(ConfigurationSection section) {
        Map<String,Object> result=new LinkedHashMap<>();
        for(var e:section.getValues(false).entrySet())result.put(e.getKey(),e.getValue() instanceof ConfigurationSection child?copy(child):e.getValue());
        return result;
    }
}
