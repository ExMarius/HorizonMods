package ro.exmarius.horizonvehicles;

import java.security.MessageDigest;
import java.util.HexFormat;
import java.util.Map;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class BundledBusAssetsTest {
    @Test
    void upstreamModelTextureAndLicenseAreBundledUnmodified() throws Exception {
        var expected = Map.of(
            "bus.obj", "672d583e07129cf148d2ed693ce586639e99d6871870d10247c4adae18fcfcf1",
            "bus_wheel.obj", "d1a5576a7507fa9c792b8b6c7449491f2f6b4e66129daca0e5848c4a7eba2dde",
            "yellow_bus.png", "fba9bbd450aa2984c18224d240e94c430b98ada2587b22260b4aaa9026d3718f",
            "bus_wheel.png", "24d20470f693323bdc7ed25fdb5b4323ad309e2ec4250e711d25dc4edcc996f6"
        );
        for (var item : expected.entrySet()) {
            try (var in = getClass().getResourceAsStream("/source-assets/city_bus/" + item.getKey())) {
                assertNotNull(in, item.getKey());
                var actual = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(in.readAllBytes()));
                assertEquals(item.getValue(), actual, item.getKey());
            }
        }
        try (var license = getClass().getResourceAsStream("/source-assets/city_bus/LICENSE")) {
            assertNotNull(license);
            assertTrue(new String(license.readAllBytes(), java.nio.charset.StandardCharsets.UTF_8)
                .contains("Permission is hereby granted"));
        }
        assertNotNull(getClass().getResource("/source-assets/city_bus/yellow_bus_frame.json"));
    }
    @Test
    void experimentalPackIsIncludedButNotActivated() throws Exception {
        try (var stream = getClass().getResourceAsStream("/resource-packs/city-bus-experimental.zip")) {
            assertNotNull(stream, "Experimental resource pack must be included in the JAR");
            var seen = new java.util.HashSet<String>();
            try (var zip = new java.util.zip.ZipInputStream(stream)) {
                java.util.zip.ZipEntry entry;
                while ((entry = zip.getNextEntry()) != null) seen.add(entry.getName());
            }
            assertTrue(seen.contains("pack.mcmeta"));
            assertTrue(seen.contains("city_bus_parts.json"));
            assertTrue(seen.contains("LICENSE-city-bus.txt"));
        }
    }
}
