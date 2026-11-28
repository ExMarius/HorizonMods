package com.mrcrayfish.vehicle.paper.recovery;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.EOFException;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.file.AtomicMoveNotSupportedException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.nio.file.StandardOpenOption;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import java.util.zip.CRC32;

/**
 * Isolated crash-recovery journal. This is not connected to the Paper runtime.
 * An entry is a lock/identity record, never permission to move entities: after a
 * restart all in-progress operations require explicit reconciliation, and even
 * SECURED links require live revalidation. Call only from a serialized owner.
 */
public final class RecoveryJournal {
    private static final int MAGIC=0x48524331, VERSION=1, MAX_ENTRIES=4096, MAX_BYTES=1_000_000;
    public record Entry(UUID carrier, UUID target, UUID operator, RecoveryInterlock.Mode mode,
                        RecoveryInterlock.Phase phase) {
        public Entry {
            if (carrier==null || target==null || operator==null || carrier.equals(target)
                    || mode==null || phase==null || phase==RecoveryInterlock.Phase.IDLE)
                throw new IllegalArgumentException("Invalid active recovery entry");
        }
        /** True means a movement operation must not be resumed automatically. */
        public boolean needsOperatorReconciliation() { return true; }
    }
    private final Path file;
    public RecoveryJournal(Path file) { this.file = file.toAbsolutePath(); }

    public List<Entry> read() throws IOException {
        if (Files.notExists(file)) return List.of();
        long size=Files.size(file);
        if(size < 16 || size > MAX_BYTES) throw new IOException("Invalid recovery journal size");
        byte[] bytes=Files.readAllBytes(file);
        int n=bytes.length;
        CRC32 crc=new CRC32();crc.update(bytes,0,n-4);
        int expected=ByteBuffer.wrap(bytes,n-4,4).getInt();
        if((int)crc.getValue()!=expected)throw new IOException("Recovery journal checksum mismatch");
        try(DataInputStream in=new DataInputStream(new ByteArrayInputStream(bytes,0,n-4))){
            if(in.readInt()!=MAGIC || in.readInt()!=VERSION)throw new IOException("Unknown recovery journal format");
            int count=in.readInt();if(count<0||count>MAX_ENTRIES)throw new IOException("Invalid recovery count");
            List<Entry> result=new ArrayList<>(count);Set<UUID> used=new HashSet<>();
            for(int i=0;i<count;i++){
                UUID carrier=uuid(in),target=uuid(in),operator=uuid(in);
                int mode=in.readUnsignedByte(),phase=in.readUnsignedByte();
                if(mode>=RecoveryInterlock.Mode.values().length || phase>=RecoveryInterlock.Phase.values().length)
                    throw new IOException("Unknown recovery state");
                Entry entry;
                try{entry=new Entry(carrier,target,operator,RecoveryInterlock.Mode.values()[mode],RecoveryInterlock.Phase.values()[phase]);}
                catch(IllegalArgumentException e){throw new IOException("Invalid recovery entry",e);}
                if(!used.add(carrier)||!used.add(target))throw new IOException("Vehicle in multiple recovery entries");
                result.add(entry);
            }
            if(in.available()!=0)throw new IOException("Unexpected recovery journal data");
            return List.copyOf(result);
        } catch(EOFException e){throw new IOException("Truncated recovery journal",e);}
    }
    public void write(List<Entry> entries) throws IOException {
        // Do not destroy an unreadable or corrupted lock journal.
        read();
        ByteBuffer buffer=ByteBuffer.wrap(encode(entries));
        Path parent=file.getParent();if(parent==null)throw new IOException("Missing journal directory");
        Files.createDirectories(parent);
        Path tmp=Files.createTempFile(parent,".recovery-", ".tmp");
        try{
            try(FileChannel channel=FileChannel.open(tmp,StandardOpenOption.WRITE,StandardOpenOption.TRUNCATE_EXISTING)){
                while(buffer.hasRemaining())channel.write(buffer);
                channel.force(true);
            }
            // Never fall back to a non-atomic overwrite, which can lose the locks.
            try{Files.move(tmp,file,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING);}
            catch(AtomicMoveNotSupportedException e){throw new IOException("Atomic recovery journal update unavailable",e);}
            // Persist the directory entry as well as the file on supported platforms.
            try(FileChannel directory=FileChannel.open(parent,StandardOpenOption.READ)){directory.force(true);}
        } finally {Files.deleteIfExists(tmp);}
    }
    /** Make an immutable byte snapshot before submitting it to the ordered writer. */
    public static byte[] encode(List<Entry> entries) throws IOException {
        if(entries==null||entries.size()>MAX_ENTRIES)throw new IOException("Invalid recovery entries");
        Set<UUID> used=new HashSet<>();
        for(Entry e:entries){
            if(e==null||!used.add(e.carrier())||!used.add(e.target()))throw new IOException("Duplicate recovery vehicle");
        }
        ByteArrayOutputStream data=new ByteArrayOutputStream();
        try(DataOutputStream out=new DataOutputStream(data)){
            out.writeInt(MAGIC);out.writeInt(VERSION);out.writeInt(entries.size());
            for(Entry e:entries){uuid(out,e.carrier());uuid(out,e.target());uuid(out,e.operator());out.writeByte(e.mode().ordinal());out.writeByte(e.phase().ordinal());}
        }
        byte[] payload=data.toByteArray();CRC32 crc=new CRC32();crc.update(payload);
        return ByteBuffer.allocate(payload.length+4).put(payload).putInt((int)crc.getValue()).array();
    }
    private static UUID uuid(DataInputStream in)throws IOException{return new UUID(in.readLong(),in.readLong());}
    private static void uuid(DataOutputStream out,UUID id)throws IOException{out.writeLong(id.getMostSignificantBits());out.writeLong(id.getLeastSignificantBits());}
}
