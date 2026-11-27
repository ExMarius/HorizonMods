package com.mrcrayfish.vehicle.paper.recovery;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.EOFException;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.util.Collections;
import java.util.HashSet;
import java.util.Set;
import java.util.UUID;
import java.util.zip.CRC32;

/** Experimental durable-format codec for entity UUID tombstones. Not connected
 * to Paper events. IDs must be captured from the old rig before it is removed;
 * they are Minecraft entity IDs, not logical vehicle IDs or player IDs. The
 * caller must durably save the union before allowing recovery to proceed.
 * There is deliberately no expiry or automatic acknowledgement/removal. */
public final class RecoveryEntityTombstones {
    private static final int MAGIC = 0x48455431, VERSION = 1, MAX_ENTRIES = 100_000;
    private static final long MAX_BYTES = 16L * MAX_ENTRIES + 16;
    private RecoveryEntityTombstones() { }

    public static byte[] encode(Set<UUID> ids) throws IOException {
        if (ids == null || ids.size() > MAX_ENTRIES || ids.stream().anyMatch(java.util.Objects::isNull)) throw new IOException("Invalid tombstone set");
        var sorted = ids.stream().sorted().toList();
        ByteArrayOutputStream buffer = new ByteArrayOutputStream();
        try (DataOutputStream out = new DataOutputStream(buffer)) {
            out.writeInt(MAGIC); out.writeInt(VERSION); out.writeInt(sorted.size());
            for (UUID id : sorted) { out.writeLong(id.getMostSignificantBits()); out.writeLong(id.getLeastSignificantBits()); }
        }
        byte[] payload = buffer.toByteArray();
        CRC32 crc = new CRC32(); crc.update(payload);
        return ByteBuffer.allocate(payload.length + 4).put(payload).putInt((int) crc.getValue()).array();
    }

    public static Set<UUID> decode(byte[] data) throws IOException {
        if (data == null || data.length < 16 || data.length > MAX_BYTES) throw new IOException("Invalid tombstone size");
        int payloadLength = data.length - 4;
        CRC32 crc = new CRC32(); crc.update(data, 0, payloadLength);
        if ((int) crc.getValue() != ByteBuffer.wrap(data, payloadLength, 4).getInt()) throw new IOException("Tombstone checksum mismatch");
        try (DataInputStream in = new DataInputStream(new ByteArrayInputStream(data, 0, payloadLength))) {
            if (in.readInt() != MAGIC || in.readInt() != VERSION) throw new IOException("Unknown tombstone format");
            int count = in.readInt();
            if (count < 0 || count > MAX_ENTRIES || payloadLength != 12L + 16L * count) throw new IOException("Invalid tombstone count");
            Set<UUID> ids = new HashSet<>();
            for (int i = 0; i < count; i++) {
                UUID id = new UUID(in.readLong(), in.readLong());
                if (!ids.add(id)) throw new IOException("Duplicate tombstone identity");
            }
            return Collections.unmodifiableSet(ids);
        } catch (EOFException e) { throw new IOException("Truncated tombstones", e); }
    }
}
