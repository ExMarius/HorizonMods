package com.mrcrayfish.vehicle.paper.recovery;

import com.mrcrayfish.vehicle.paper.persistence.TrailerRecoveryAudit;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import java.nio.file.Files;
import java.nio.file.Path;
import static org.junit.jupiter.api.Assertions.*;

class TrailerRecoveryAuditTest {
    @TempDir Path temp;
    private int audit(String yaml) throws Exception {
        Path file = temp.resolve("trailers.yml");
        Files.writeString(file, yaml);
        return TrailerRecoveryAudit.countTrustedRecords(file.toFile());
    }
    private static final String ID = "11111111-1111-1111-1111-111111111111";
    private static final String WORLD = "22222222-2222-2222-2222-222222222222";
    private static final String VEHICLE = "33333333-3333-3333-3333-333333333333";
    private static String record(String links) {
        return "trailers:\n  " + ID + ":\n    type: trailer\n    world: " + WORLD + "\n" + links;
    }
    @Test void validatesEveryPersistedLink() throws Exception {
        assertEquals(0, TrailerRecoveryAudit.countTrustedRecords(temp.resolve("absent.yml").toFile()));
        assertEquals(0, audit("{}\n"));
        assertEquals(1, audit(record("    puller-type: NONE\n")));
        assertEquals(1, audit(record("    puller-type: VEHICLE\n    puller-id: " + VEHICLE + "\n    loaded-vehicle-id: " + ID + "\n")));
        assertEquals(-1, audit(record("    puller-type: VEHICLE\n")));
        assertEquals(-1, audit(record("    puller-type: NONE\n    puller-id: " + VEHICLE + "\n")));
        assertEquals(-1, audit(record("    puller-type: UNKNOWN\n")));
        assertEquals(-1, audit(record("    puller-type: NONE\n    loaded-vehicle-id: broken\n")));
        assertEquals(-1, audit("trailers: [\n"));
        assertEquals(-1, audit("trailers: wrong\n"));
        assertEquals(-1, audit("wrong-key: true\n"));
    }
}
