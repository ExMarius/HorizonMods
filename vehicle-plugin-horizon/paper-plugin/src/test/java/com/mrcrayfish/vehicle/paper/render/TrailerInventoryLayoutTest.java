package com.mrcrayfish.vehicle.paper.render;

import com.mrcrayfish.vehicle.paper.vehicle.TrailerSpec;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

class TrailerInventoryLayoutTest {
    private static final float EPSILON = 1.0E-6F;

    @Test
    void fertilizerCargoUsesSourceBaseSpacingCountAndScale() {
        List<TrailerRig.InventoryTransform> transforms = TrailerRig.inventoryTransforms(
                TrailerSpec.FERTILIZER, 64);

        assertEquals(2, transforms.size());
        assertTransform(transforms.getFirst(), -0.378125F, 0.653125F, -0.20625F, 0.495F);
        assertTransform(transforms.getLast(), -0.130625F, 0.6840625F, -0.20625F, 0.495F);
        assertEquals(0, transforms.getFirst().slot());
    }

    @Test
    void seederCargoUsesFourDisplaysForAFullStackAndSourceGrid() {
        List<TrailerRig.InventoryTransform> transforms = TrailerRig.inventoryTransforms(
                TrailerSpec.SEEDER, 64);

        assertEquals(4, transforms.size());
        assertTransform(transforms.getFirst(), -0.721875F, 0.653125F, -0.1375F, 0.495F);
        assertTransform(transforms.get(1), -0.350625F, 0.653125F, -0.1375F, 0.495F);
        assertTrue(Math.abs(transforms.get(1).rotation().z) > EPSILON);
    }

    @Test
    void emptySlotsRetainTheirSourceInventoryIndex() {
        List<TrailerRig.InventoryTransform> transforms = TrailerRig.inventoryTransforms(
                TrailerSpec.SEEDER, 0, 16);

        assertEquals(1, transforms.size());
        assertEquals(1, transforms.getFirst().slot());
    }

    @Test
    void amountOnlyConsumptionKeepsExistingCargoTransformsStable() {
        assertEquals(
                TrailerRig.inventoryTransforms(TrailerSpec.FERTILIZER, 63),
                TrailerRig.inventoryTransforms(TrailerSpec.FERTILIZER, 62));
        assertEquals(
                TrailerRig.inventoryTransforms(TrailerSpec.SEEDER, 63),
                TrailerRig.inventoryTransforms(TrailerSpec.SEEDER, 62));
    }

    @Test
    void sourcePileThresholdOnlyRemovesTheTrailingDisplay() {
        List<TrailerRig.InventoryTransform> full = TrailerRig.inventoryTransforms(
                TrailerSpec.SEEDER, 64);
        List<TrailerRig.InventoryTransform> consumed = TrailerRig.inventoryTransforms(
                TrailerSpec.SEEDER, 63);

        assertEquals(4, full.size());
        assertEquals(3, consumed.size());
        assertEquals(full.subList(0, 3), consumed);
    }

    @Test
    void farmTrailerShowsEveryOccupiedSlotInsideBoundedBed() {
        int[] amounts = new int[27]; java.util.Arrays.fill(amounts, 64);
        var all = TrailerRig.inventoryTransforms(TrailerSpec.TRACTOR_TRAILER, amounts);
        assertEquals(27, all.size());
        for (int slot = 0; slot < 27; slot++) {
            var t = all.get(slot);
            assertEquals(slot, t.slot());
            assertTrue(Math.abs(t.center().x) <= 0.48F + EPSILON);
            assertTrue(Math.abs(t.center().z) <= 0.62F + EPSILON);
            assertTrue(t.center().y >= 0.78F && t.center().y <= 1.10F + EPSILON);
            assertEquals(0.28F, t.scale().x, EPSILON);
        }
        amounts[0] = 0; amounts[1] = 1;
        var reduced = TrailerRig.inventoryTransforms(TrailerSpec.TRACTOR_TRAILER, amounts);
        assertEquals(26, reduced.size());
        assertEquals(all.get(1), reduced.getFirst());
        assertTrue(TrailerRig.inventoryTransforms(TrailerSpec.TRACTOR_TRAILER).isEmpty());
    }

    @Test
    void trailersWithoutSourceCargoRenderingProduceNoTransforms() {
        assertTrue(TrailerRig.inventoryTransforms(TrailerSpec.STORAGE_TRAILER, 64).isEmpty());
    }

    private static void assertTransform(TrailerRig.InventoryTransform transform,
                                        float x, float y, float z, float scale) {
        assertEquals(x, transform.center().x, EPSILON);
        assertEquals(y, transform.center().y, EPSILON);
        assertEquals(z, transform.center().z, EPSILON);
        assertEquals(scale, transform.scale().x, EPSILON);
        assertEquals(scale, transform.scale().y, EPSILON);
        assertEquals(scale, transform.scale().z, EPSILON);
    }
}
