package com.mrcrayfish.vehicle.paper.runtime;

import com.mrcrayfish.vehicle.paper.vehicle.TrailerSpec;
import org.bukkit.Material;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class UtbPloughTest {
    @Test void changesOnlyUncoveredVanillaTillableSoil() {
        assertTrue(PaperTrailer.tillable(Material.DIRT, Material.AIR));
        assertTrue(PaperTrailer.tillable(Material.GRASS_BLOCK, Material.AIR));
        assertTrue(PaperTrailer.tillable(Material.DIRT_PATH, Material.AIR));
        assertFalse(PaperTrailer.tillable(Material.DIRT, Material.WHEAT));
        assertFalse(PaperTrailer.tillable(Material.FARMLAND, Material.AIR));
        assertFalse(PaperTrailer.tillable(Material.CHEST, Material.AIR));
        assertFalse(PaperTrailer.tillable(Material.STONE, Material.AIR));
    }
    @Test void ploughIsIndependentOfExistingTrailerTypes() {
        assertEquals(TrailerSpec.UTB_PLOUGH, TrailerSpec.byId("utb_plough"));
        assertEquals(TrailerSpec.Kind.UTB_PLOUGH, TrailerSpec.UTB_PLOUGH.kind());
        assertEquals(TrailerSpec.Kind.SEEDER, TrailerSpec.SEEDER.kind());
        assertFalse(TrailerSpec.UTB_PLOUGH.canTowTrailers());
    }
}
