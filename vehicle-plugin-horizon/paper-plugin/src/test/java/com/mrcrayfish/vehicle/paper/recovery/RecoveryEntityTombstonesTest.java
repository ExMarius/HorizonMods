package com.mrcrayfish.vehicle.paper.recovery;

import org.junit.jupiter.api.Test;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.util.HashSet;
import java.util.Set;
import java.util.UUID;
import java.util.zip.CRC32;
import static org.junit.jupiter.api.Assertions.*;

class RecoveryEntityTombstonesTest {
    @Test void roundTripIsDeterministicAndImmutable() throws Exception {
        UUID first = UUID.randomUUID(), second = UUID.randomUUID();
        Set<UUID> a = new HashSet<>(); a.add(first); a.add(second);
        Set<UUID> b = new HashSet<>(); b.add(second); b.add(first);
        byte[] encoded = RecoveryEntityTombstones.encode(a);
        assertArrayEquals(encoded, RecoveryEntityTombstones.encode(b));
        Set<UUID> decoded = RecoveryEntityTombstones.decode(encoded);
        assertEquals(a, decoded);
        assertThrows(UnsupportedOperationException.class, () -> decoded.add(UUID.randomUUID()));
        assertEquals(Set.of(), RecoveryEntityTombstones.decode(RecoveryEntityTombstones.encode(Set.of())));
    }
    @Test void rejectsTruncatedCorruptedUnknownAndDuplicateEntries() throws Exception {
        UUID id = UUID.randomUUID();
        byte[] original = RecoveryEntityTombstones.encode(Set.of(id));
        byte[] corrupt = original.clone(); corrupt[12] ^= 1;
        assertThrows(IOException.class, () -> RecoveryEntityTombstones.decode(corrupt));
        assertThrows(IOException.class, () -> RecoveryEntityTombstones.decode(java.util.Arrays.copyOf(original, original.length - 1)));
        byte[] version = original.clone(); ByteBuffer.wrap(version).putInt(4, 99); checksum(version);
        assertThrows(IOException.class, () -> RecoveryEntityTombstones.decode(version));
        byte[] duplicate = ByteBuffer.allocate(48).putInt(0x48455431).putInt(1).putInt(2)
                .putLong(id.getMostSignificantBits()).putLong(id.getLeastSignificantBits())
                .putLong(id.getMostSignificantBits()).putLong(id.getLeastSignificantBits()).putInt(0).array();
        checksum(duplicate);
        assertThrows(IOException.class, () -> RecoveryEntityTombstones.decode(duplicate));
    }
    @Test void refusesInvalidInput() {
        assertThrows(IOException.class, () -> RecoveryEntityTombstones.encode(null));
        Set<UUID> withNull = new HashSet<>(); withNull.add(null);
        assertThrows(IOException.class, () -> RecoveryEntityTombstones.encode(withNull));
        assertThrows(IOException.class, () -> RecoveryEntityTombstones.decode(null));
    }
    private static void checksum(byte[] data) {
        CRC32 crc = new CRC32(); crc.update(data, 0, data.length - 4);
        ByteBuffer.wrap(data).putInt(data.length - 4, (int)crc.getValue());
    }
}
