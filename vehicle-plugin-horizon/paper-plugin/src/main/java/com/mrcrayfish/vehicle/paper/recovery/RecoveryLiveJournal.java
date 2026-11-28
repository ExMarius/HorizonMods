package com.mrcrayfish.vehicle.paper.recovery;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.EOFException;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import java.util.zip.CRC32;

/** Durable recovery identity format for the future live coordinator. The
 * journal is not sufficient by itself: a complete snapshot must be durably saved
 * before an entry is acknowledged and any vehicle is moved. */
public final class RecoveryLiveJournal {
    private static final int MAGIC=0x48524c32, VERSION=1, MAX_ENTRIES=4096;
    private static final long MAX_BYTES=16L+64L*MAX_ENTRIES;
    private RecoveryLiveJournal() { }

    public record Entry(UUID carrier, UUID target, UUID carrierSession, UUID targetSession) {
        public Entry {
            if(carrier==null || target==null || carrier.equals(target) || carrierSession==null
                    || targetSession==null || carrierSession.equals(targetSession))
                throw new IllegalArgumentException("Invalid recovery identities");
        }
    }
    public static List<Entry> read(Path path) throws IOException {
        if(Files.notExists(path))return List.of();
        long size=Files.size(path);
        if(size<16 || size>MAX_BYTES)throw new IOException("Invalid live recovery journal size");
        byte[] data=Files.readAllBytes(path);
        int length=data.length-4; CRC32 crc=new CRC32();crc.update(data,0,length);
        if((int)crc.getValue()!=ByteBuffer.wrap(data,length,4).getInt())throw new IOException("Live recovery journal checksum mismatch");
        try(DataInputStream in=new DataInputStream(new ByteArrayInputStream(data,0,length))) {
            if(in.readInt()!=MAGIC || in.readInt()!=VERSION)throw new IOException("Unknown live recovery journal format");
            int count=in.readInt();
            if(count<0 || count>MAX_ENTRIES || length!=12L+64L*count)throw new IOException("Invalid live recovery count");
            var entries=new ArrayList<Entry>(count);
            for(int i=0;i<count;i++) {
                try {entries.add(new Entry(uuid(in),uuid(in),uuid(in),uuid(in)));}
                catch(IllegalArgumentException e){throw new IOException("Invalid live recovery identity",e);}
            }
            validate(entries);
            return List.copyOf(entries);
        } catch(EOFException e){throw new IOException("Truncated live recovery journal",e);}
    }
    public static byte[] encode(List<Entry> entries) throws IOException {
        validate(entries);
        var buffer=new ByteArrayOutputStream();
        try(var out=new DataOutputStream(buffer)) {
            out.writeInt(MAGIC);out.writeInt(VERSION);out.writeInt(entries.size());
            for(var entry:entries) {uuid(out,entry.carrier());uuid(out,entry.target());uuid(out,entry.carrierSession());uuid(out,entry.targetSession());}
        }
        byte[] payload=buffer.toByteArray();CRC32 crc=new CRC32();crc.update(payload);
        return ByteBuffer.allocate(payload.length+4).put(payload).putInt((int)crc.getValue()).array();
    }
    private static void validate(List<Entry> entries) throws IOException {
        if(entries==null || entries.size()>MAX_ENTRIES)throw new IOException("Invalid live recovery entries");
        Set<UUID> vehicles=new HashSet<>(),sessions=new HashSet<>();
        for(var e:entries) {
            if(e==null || !vehicles.add(e.carrier()) || !vehicles.add(e.target())
                    || !sessions.add(e.carrierSession()) || !sessions.add(e.targetSession()))
                throw new IOException("Duplicate live recovery identity");
        }
    }
    private static UUID uuid(DataInputStream in)throws IOException{return new UUID(in.readLong(),in.readLong());}
    private static void uuid(DataOutputStream out,UUID id)throws IOException{out.writeLong(id.getMostSignificantBits());out.writeLong(id.getLeastSignificantBits());}
}
