package com.mrcrayfish.vehicle.paper.render;

import com.mrcrayfish.vehicle.paper.vehicle.LandVehicleSpec;
import com.mrcrayfish.vehicle.paper.vehicle.TrailerSpec;
import io.papermc.paper.entity.TeleportFlag;
import org.bukkit.Location;
import org.bukkit.Material;
import org.bukkit.NamespacedKey;
import org.bukkit.World;
import org.bukkit.block.Block;
import org.bukkit.block.data.BlockData;
import org.bukkit.entity.BlockDisplay;
import org.bukkit.entity.Display;
import org.bukkit.entity.Entity;
import org.bukkit.entity.Interaction;
import org.bukkit.entity.ItemDisplay;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.meta.ItemMeta;
import org.bukkit.util.Transformation;
import org.joml.Quaternionf;
import org.joml.Vector3f;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.UUID;

/** Multipart display rig for a source-compatible towable trailer. */
public final class TrailerRig {
    private static final int VANILLA_ENTITY_LERP_TICKS = 3;

    private final UUID trailerId;
    private final TrailerSpec spec;
    private final Interaction interaction;
    private final ItemDisplay body;
    private final List<WheelDisplay> wheels;
    private final List<ExtraDisplay> extras;
    private final List<InventoryDisplay> inventoryDisplays = new ArrayList<>();
    private final BlockDisplay fluid;
    private final List<Entity> entities;
    private int inventoryFingerprint = Integer.MIN_VALUE;

    private TrailerRig(UUID trailerId, TrailerSpec spec, Interaction interaction, ItemDisplay body,
                       List<WheelDisplay> wheels, List<ExtraDisplay> extras,
                       BlockDisplay fluid, List<Entity> entities) {
        this.trailerId = trailerId;
        this.spec = spec;
        this.interaction = interaction;
        this.body = body;
        this.wheels = wheels;
        this.extras = extras;
        this.fluid = fluid;
        this.entities = entities;
    }

    public static TrailerRig spawn(UUID trailerId, TrailerSpec spec, Location location,
                                   ItemStack[] inventoryContents) {
        World world = location.getWorld();
        if (world == null) {
            throw new IllegalArgumentException("Cannot spawn a trailer without a world");
        }
        List<Entity> all = new ArrayList<>();
        Interaction interaction = world.spawn(location, Interaction.class, entity -> {
            entity.setInteractionWidth(Math.max(1.5F, spec.entityWidth()));
            entity.setInteractionHeight(Math.max(1.0F, spec.entityHeight()));
            entity.setResponsive(true);
            entity.setPersistent(false);
        });
        mark(interaction, trailerId);
        all.add(interaction);

        ItemDisplay body = display(world, location, model(spec.bodyModel()));
        mark(body, trailerId);
        all.add(body);

        List<WheelDisplay> wheels = new ArrayList<>();
        for (int side : (spec.kind() == TrailerSpec.Kind.UTB_PLOUGH || spec.kind() == TrailerSpec.Kind.DISC_GD32) ? new int[0] : new int[]{-1, 1}) {
            float[] axles = spec.kind() == TrailerSpec.Kind.TRACTOR_TRAILER_MODERN ? new float[]{-1.45F, 1.5F} : new float[]{0.0F};
            for (float axle : axles) {
                ItemDisplay wheel = display(world, location, model(spec.isFarmTrailer() ? "utb_650_wheel_front" : "standard_wheel"));
                mark(wheel, trailerId);
                all.add(wheel);
                wheels.add(new WheelDisplay(wheel, side, axle));
            }
        }

        List<ExtraDisplay> extras = new ArrayList<>();
        if (spec.kind() == TrailerSpec.Kind.FERTILIZER) {
            /* FertilizerTrailerRenderer: body root, translate(0, -.5, -.4375),
             * rotate Z +90, then rotate X by wheel travel. */
            extra(world, location, trailerId, all, extras, "seed_spiker",
                    new Vector3f(spec.bodyPartX(0.0F), spec.bodyPartY(-0.5F),
                            spec.bodyPartZ(-0.4375F)),
                    new Vector3f(1.25F * spec.bodyScale()), true, 90.0F, 0.0F);
        } else if (spec.kind() == TrailerSpec.Kind.SEEDER) {
            /* SeederTrailerRenderer places seven independently spinning spikers
             * at source X offsets -12 through +12 model pixels. */
            for (int x = -12; x <= 12; x += 4) {
                extra(world, location, trailerId, all, extras, "seed_spiker",
                        new Vector3f(spec.bodyPartX(x * LandVehicleSpec.MODEL_UNIT),
                                spec.bodyPartY(-0.65F), spec.bodyPartZ(0.0F)),
                        new Vector3f(0.75F * spec.bodyScale()), true, 0.0F, 0.0F);
            }
        } else if (spec.kind() == TrailerSpec.Kind.STORAGE) {
            ItemDisplay chest = display(world, location, new ItemStack(Material.CHEST));
            mark(chest, trailerId);
            all.add(chest);
            /* StorageTrailerRenderer translates the closed chest -6 model pixels
             * inside the already transformed body matrix. */
            extras.add(new ExtraDisplay(chest,
                    new Vector3f(spec.bodyPartX(0.0F),
                            /* The source ChestModel is bottom-anchored after its
                             * -0.5 X/Z translation. A vanilla chest item model is
                             * center-anchored, so compensate by half a block. */
                            spec.storageChestCenterY(), spec.bodyPartZ(0.0F)),
                    new Vector3f(0.9F * spec.bodyScale()), false, 0.0F, 180.0F, false, false));
        }
        if (spec.kind() == TrailerSpec.Kind.TRACTOR_TRAILER_MODERN) {
            ItemDisplay axle = display(world, location, model("tractor_trailer_modern_axle"));
            mark(axle, trailerId);
            all.add(axle);
            extras.add(new ExtraDisplay(axle, new Vector3f(0.0F, 0.5F, 1.5F),
                    new Vector3f(2.0F), false, 0.0F, 0.0F, true, false));
            ItemDisplay drawbar = display(world, location, model("tractor_trailer_modern_drawbar"));
            mark(drawbar, trailerId);
            all.add(drawbar);
            extras.add(new ExtraDisplay(drawbar, new Vector3f(0.0F, 0.6F, 1.5F),
                    new Vector3f(2.0F), false, 0.0F, 0.0F, true, true));
        }
        if (spec.kind() == TrailerSpec.Kind.DISC_GD32) {
            // The arrays are ordered in pairs: carrier then rotating gang, front then rear.
            for (int front = 0; front < 2; front++) for (int side : new int[]{-1, 1}) {
                extra(world, location, trailerId, all, extras, "gd32_gang_frame",
                        new Vector3f(), new Vector3f(2), false, 0, 0);
                extra(world, location, trailerId, all, extras, front == 0 ? "gd32_gang_front" : "gd32_gang_rear",
                        new Vector3f(), new Vector3f(2), false, 0, 0);
            }
            for (int i=0; i<2; i++) extra(world, location, trailerId, all, extras, "gd32_wheel",
                    new Vector3f(), new Vector3f(2), false, 0, 0);
            extra(world, location, trailerId, all, extras, "gd32_axle", new Vector3f(), new Vector3f(2), false, 0, 0);
            extra(world, location, trailerId, all, extras, "gd32_jack", new Vector3f(), new Vector3f(2), false, 0, 0);
        }
        if (spec.canTowTrailers()) {
            LandVehicleSpec.Point tow = spec.towBarOffset();
            /* The common source renderer cancels bodyScale before drawing a tow
             * bar, so this transform intentionally does not use bodyPartY(). */
            extra(world, location, trailerId, all, extras, "tow_bar",
                    new Vector3f(tow.x() * spec.bodyScale() * LandVehicleSpec.MODEL_UNIT,
                            0.5F + tow.y() * spec.bodyScale() * LandVehicleSpec.MODEL_UNIT,
                            tow.z() * spec.bodyScale() * LandVehicleSpec.MODEL_UNIT),
                    new Vector3f(1.0F), false, 0.0F, 180.0F);
        }

        BlockDisplay fluid = null;
        if (spec.kind() == TrailerSpec.Kind.FLUID) {
            fluid = world.spawn(location, BlockDisplay.class, display -> {
                display.setBlock(Material.WATER.createBlockData());
                configure(display);
            });
            mark(fluid, trailerId);
            all.add(fluid);
        }

        TrailerRig rig = new TrailerRig(trailerId, spec, interaction, body,
                Collections.unmodifiableList(wheels), Collections.unmodifiableList(extras), fluid, all);
        rig.update(location, 0.0F, null, inventoryContents, 0);
        if (spec.kind() == TrailerSpec.Kind.DISC_GD32) rig.updateHarrow(location, 0, 0, 0, 0, false);
        return rig;
    }

    private static void extra(World world, Location location, UUID id, List<Entity> all,
                              List<ExtraDisplay> extras, String model, Vector3f center,
                              Vector3f scale, boolean spins, float preSpinZ, float sourceYaw) {
        ItemDisplay display = display(world, location, model(model));
        mark(display, id);
        all.add(display);
        extras.add(new ExtraDisplay(display, center, scale, spins, preSpinZ, sourceYaw, false, false));
    }

    private static ItemDisplay display(World world, Location location, ItemStack stack) {
        return world.spawn(location, ItemDisplay.class, display -> {
            display.setItemStack(stack);
            display.setItemDisplayTransform(ItemDisplay.ItemDisplayTransform.NONE);
            configure(display);
        });
    }

    private static void configure(Display display) {
        display.setInterpolationDelay(0);
        display.setInterpolationDuration(1);
        display.setTeleportDuration(VANILLA_ENTITY_LERP_TICKS);
        display.setInvulnerable(true);
        display.setPersistent(false);
        display.setShadowRadius(0.0F);
        display.setShadowStrength(0.0F);
    }

    private static ItemStack model(String name) {
        // PAPER + item_model nu mai randeaza pe server (regresie live - vehicule
        // nevopsite invizibile). LEATHER_HORSE_ARMOR + alb explicit: dyed_color pe
        // stack => tint din stack (opac pe orice client), aspect = albul din backup.
        ItemStack item = new ItemStack(Material.LEATHER_HORSE_ARMOR);
        ItemMeta meta = item.getItemMeta();
        meta.setItemModel(new NamespacedKey("vehicle", name));
        if (meta instanceof org.bukkit.inventory.meta.LeatherArmorMeta armor) {
            armor.setColor(org.bukkit.Color.fromRGB(0xF9FFFE));
        }
        item.setItemMeta(meta);
        return item;
    }

    private static void mark(Entity entity, UUID id) {
        entity.addScoreboardTag(LandVehicleRig.ENTITY_TAG);
        entity.addScoreboardTag("mcv_" + id);
    }

    public void update(Location root, float wheelRotation, FluidVisual fluidVisual,
                       ItemStack[] inventoryContents, int tickCount) {
        update(root, wheelRotation, fluidVisual, inventoryContents, tickCount, 0.0F, 0.0F);
    }

    public void update(Location root, float wheelRotation, FluidVisual fluidVisual,
                       ItemStack[] inventoryContents, int tickCount, float steering, float drawbarPitch) {
        if (!valid()) {
            return;
        }
        syncInventoryDisplays(root, inventoryContents);
        float yaw = root.getYaw();
        interaction.teleport(root);
        interaction.setRotation(yaw, 0.0F);

        if (spec.kind() == TrailerSpec.Kind.DISC_GD32) {
            if (tickCount % 5 == 0) updateBrightness(root);
            return;
        }

        place(body, root, new Vector3f(0.0F, spec.bodyOriginY(), 0.0F), new Quaternionf(),
                new Vector3f(spec.bodyScale()), new Quaternionf());

        float wheelX = spec.wheelX() * LandVehicleSpec.MODEL_UNIT * spec.bodyScale();
        float wheelZ = spec.wheelZ() * LandVehicleSpec.MODEL_UNIT * spec.bodyScale();
        for (WheelDisplay wheel : wheels) {
            float halfWidth = wheel.side * 4.0F * 0.5F * LandVehicleSpec.MODEL_UNIT * spec.bodyScale();
            boolean modern = spec.kind() == TrailerSpec.Kind.TRACTOR_TRAILER_MODERN;
            boolean farm = spec.isFarmTrailer();
            float steer = modern && wheel.axleZ > 0 ? radians(steering) : 0.0F;
            float x = modern ? wheel.side * 0.885F : wheel.side * 1.0F;
            Vector3f center = farm ? new Vector3f(x * (float) Math.cos(steer), modern ? 0.48F : 6.9F / 16.0F,
                    wheel.axleZ + x * (float) Math.sin(steer))
                    : new Vector3f(wheel.side * wheelX + halfWidth, spec.wheelCenterY(), wheelZ);
            Quaternionf rotation = new Quaternionf().rotateY(-steer).rotateX(radians(-wheelRotation));
            Quaternionf side = wheel.side > 0 ? new Quaternionf().rotateY((float) Math.PI) : new Quaternionf();
            Vector3f wheelScale = modern ? new Vector3f(1.28F, 1.113F, 1.113F) : farm ? new Vector3f(1.0F)
                    : new Vector3f(spec.bodyScale(), spec.bodyScale() * 1.25F, spec.bodyScale() * 1.25F);
            place(wheel.entity, root, center, rotation, wheelScale, side);
        }

        for (ExtraDisplay extra : extras) {
            /* Preserve source call order: the fertilizer roller's Z quarter-turn
             * is applied before its wheel-driven local X rotation. */
            Quaternionf rotation = extra.steering ? new Quaternionf().rotateY(-radians(steering))
                    : new Quaternionf().rotateZ(radians(extra.preSpinZ));
            if (extra.pitching) rotation.rotateX(-radians(drawbarPitch));
            if (extra.spins) {
                rotation.rotateX(radians(-wheelRotation));
            }
            place(extra.entity, root, extra.center, rotation, extra.scale,
                    new Quaternionf().rotateY(radians(extra.sourceYaw)));
        }

        for (InventoryDisplay inventoryDisplay : inventoryDisplays) {
            InventoryLayout layout = inventoryDisplay.layout;
            place(inventoryDisplay.entity, root, layout.center, layout.rotation, layout.scale,
                    new Quaternionf());
        }

        if (fluid != null) {
            updateFluid(root, fluidVisual);
        }
        if (tickCount % 5 == 0) {
            updateBrightness(root);
        }
    }

    /** Render the harrow as a rigid pitching frame around its wheel axle. */
    public void updateHarrow(Location root, float pitchDegrees, float wheelDegrees,
                             float discDegrees, double workPosition, boolean coupled) {
        if (spec.kind() != TrailerSpec.Kind.DISC_GD32 || !valid()) return;
        float lift=(float)(4.5 * (1.0-workPosition)/16.0);
        Quaternionf pitch=new Quaternionf().rotateX(-radians(pitchDegrees));
        Vector3f pivot=new Vector3f(0,5.5F/16F,1F/16F);
        Vector3f bodyCenter=new Vector3f(0,lift,0).sub(pivot);
        pitch.transform(bodyCenter); bodyCenter.add(pivot);
        place(body,root,bodyCenter,pitch,new Vector3f(2),new Quaternionf());
        for(int front=0;front<2;front++) for(int sideIndex=0;sideIndex<2;sideIndex++) {
            int side=sideIndex==0?-1:1, index=(front*2+sideIndex)*2;
            float sign=front==0 ? (side<0?1:-1) : (side<0?-1:1);
            float gangYaw=sign*18;
            Vector3f frameCenter=new Vector3f(-side*13.5F/16F, lift, (front==0?12.5F:-10.5F)/16F);
            Vector3f gangCenter=new Vector3f(frameCenter).add(0,4.2F/16F,0);
            for(Vector3f v : new Vector3f[]{frameCenter,gangCenter}) {v.sub(pivot);pitch.transform(v);v.add(pivot);}
            Quaternionf base=new Quaternionf(pitch).rotateY(radians(gangYaw));
            place(extras.get(index).entity,root,frameCenter,base,new Vector3f(2),new Quaternionf());
            place(extras.get(index+1).entity,root,gangCenter,new Quaternionf(base).rotateX(radians(discDegrees)),new Vector3f(2),new Quaternionf());
        }
        for(int sideIndex=0;sideIndex<2;sideIndex++) {
            int side=sideIndex==0?-1:1;
            Vector3f center=new Vector3f(side*12F/16F,5.5F/16F,1F/16F);
            place(extras.get(8+sideIndex).entity,root,center,
                    new Quaternionf(pitch).rotateX(radians(wheelDegrees)),new Vector3f(2),new Quaternionf());
        }
        place(extras.get(10).entity,root,pivot,pitch,new Vector3f(2),new Quaternionf());
        ItemDisplay jack=extras.get(11).entity;
        jack.setVisibleByDefault(!coupled);
        Vector3f jackCenter=new Vector3f(0,0,26F/16F);
        place(jack,root,jackCenter,pitch,new Vector3f(2),new Quaternionf());
    }

    private void syncInventoryDisplays(Location root, ItemStack[] contents) {
        if (spec.kind() != TrailerSpec.Kind.FERTILIZER && spec.kind() != TrailerSpec.Kind.SEEDER
                && !spec.isFarmTrailer()) {
            return;
        }
        int fingerprint = inventoryFingerprint(contents);
        if (fingerprint == inventoryFingerprint
                && inventoryDisplays.stream().allMatch(display -> display.entity.isValid())) {
            return;
        }
        inventoryFingerprint = fingerprint;

        World world = root.getWorld();
        if (world == null) {
            return;
        }
        List<InventoryLayout> desired = inventoryLayout(spec, contents);
        int shared = Math.min(inventoryDisplays.size(), desired.size());

        /* Consuming one seed or one bone meal changes ItemStack#hashCode every
         * work tick. Recreating the whole pile for that amount-only change made
         * fresh ItemDisplays interpolate from the moving trailer root, so the
         * cargo appeared to jump outside while planting/fertilizing. Reconcile
         * the existing entities in place and only add/remove displays when the
         * source renderer's visible pile count actually changes. */
        for (int index = 0; index < shared; index++) {
            InventoryDisplay current = inventoryDisplays.get(index);
            InventoryLayout layout = desired.get(index);
            ItemDisplay entity = current.entity;
            if (!entity.isValid()) {
                entities.remove(entity);
                entity.remove();
                entity = inventoryDisplay(world, root, layout);
            } else if (!entity.getItemStack().isSimilar(layout.stack)) {
                entity.setItemStack(visualStack(layout.stack));
            }
            inventoryDisplays.set(index, new InventoryDisplay(entity, layout));
        }
        for (int index = inventoryDisplays.size() - 1; index >= desired.size(); index--) {
            InventoryDisplay removed = inventoryDisplays.remove(index);
            entities.remove(removed.entity);
            removed.entity.remove();
        }
        for (int index = shared; index < desired.size(); index++) {
            InventoryLayout layout = desired.get(index);
            ItemDisplay entity = inventoryDisplay(world, root, layout);
            inventoryDisplays.add(new InventoryDisplay(entity, layout));
        }
    }

    private ItemDisplay inventoryDisplay(World world, Location root, InventoryLayout layout) {
        ItemDisplay entity = display(world, root, visualStack(layout.stack));
        mark(entity, trailerId);
        entities.add(entity);
        return entity;
    }

    private static ItemStack visualStack(ItemStack source) {
        ItemStack visual = source.clone();
        /* Stack count controls the number of rendered copies, not the appearance
         * of an individual source item. Keeping each display at amount one also
         * prevents amount-only metadata updates from reaching vanilla clients. */
        visual.setAmount(1);
        return visual;
    }

    /** Exact item-pile matrices from FertilizerTrailerRenderer and SeederTrailerRenderer. */
    static List<InventoryLayout> inventoryLayout(TrailerSpec spec, ItemStack[] contents) {
        if (contents == null) {
            return List.of();
        }
        int[] amounts = new int[contents.length];
        for (int slot = 0; slot < contents.length; slot++) {
            ItemStack stack = contents[slot];
            if (stack != null && !stack.getType().isAir()) {
                amounts[slot] = stack.getAmount();
            }
        }
        List<InventoryLayout> layouts = new ArrayList<>();
        boolean[] blocks = new boolean[contents.length];
        float[] fullness = new float[contents.length];
        for (int slot = 0; slot < contents.length; slot++) {
            ItemStack item = contents[slot];
            if (item != null && !item.getType().isAir()) {
                blocks[slot] = item.getType().isBlock();
                fullness[slot] = Math.min(1.0F, (float) item.getAmount() / Math.max(1, item.getMaxStackSize()));
            }
        }
        List<InventoryTransform> transforms = spec.isFarmTrailer()
                ? farmCargoTransforms(amounts, blocks, fullness) : inventoryTransforms(spec, amounts);
        for (InventoryTransform transform : transforms) {
            Vector3f center = new Vector3f(transform.center());
            if (spec.kind() == TrailerSpec.Kind.TRACTOR_TRAILER_MODERN) {
                center.z *= 1.6F;
                center.y = contents[transform.slot()].getType().isBlock() ? 1.31F
                        : 1.22F + (center.y - 0.66F) * 1.4F;
            }
            layouts.add(new InventoryLayout(contents[transform.slot()].clone(), center,
                    transform.scale(), transform.rotation()));
        }
        return List.copyOf(layouts);
    }

    /** A capped, shallow surface, not thousands of hidden entities under the load.
     * Each occupied slot contributes samples according to its fraction of a stack;
     * blocks stay at the bottom, loose items rise with the overall fill level. */
    static List<InventoryTransform> farmCargoTransforms(int[] amounts, boolean[] blocks, float[] fullness) {
        if (amounts == null || blocks == null || fullness == null) return List.of();
        int slots = Math.min(27, Math.min(amounts.length, Math.min(blocks.length, fullness.length)));
        float total = 0.0F;
        for (int i = 0; i < slots; i++) if (amounts[i] > 0) total += Math.max(0.0F, Math.min(1.0F, fullness[i]));
        float surface = 0.66F + 0.45F * Math.min(1.0F, total / 27.0F);
        List<InventoryTransform> result = new ArrayList<>();
        int looseIndex = 0, blockIndex = 0;
        for (int slot = 0; slot < slots; slot++) {
            if (amounts[slot] <= 0) continue;
            int count = blocks[slot] ? 1 : Math.max(1, (int) Math.ceil(Math.max(0, Math.min(1, fullness[slot])) * 3));
            for (int n = 0; n < count; n++) {
                int cell = blocks[slot] ? (blockIndex++ * 11) % 27 : (looseIndex++ * 37) % 81;
                int width = blocks[slot] ? 3 : 9;
                float x = ((cell % width) - (width - 1) / 2.0F) * (blocks[slot] ? 0.42F : 0.15F);
                float z = ((cell / width) - (blocks[slot] ? 4 : 4)) * (blocks[slot] ? 0.19F : 0.20F);
                float mound = blocks[slot] ? 0 : 0.035F * (1.0F - Math.min(1.0F, Math.abs(x) / 0.65F));
                float y = blocks[slot] ? 0.68F : surface + mound;
                float angle = (cell % 4) * (float) Math.PI / 2.0F;
                result.add(new InventoryTransform(slot, new Vector3f(x, y, z),
                        new Vector3f(blocks[slot] ? 0.30F : 0.32F),
                        blocks[slot] ? new Quaternionf() : new Quaternionf().rotateY(angle).rotateX(radians(90.0F))));
            }
        }
        return List.copyOf(result);
    }

    /** Pure source-matrix path, kept independent of Bukkit registry initialization for regression tests. */
    static List<InventoryTransform> inventoryTransforms(TrailerSpec spec, int... amounts) {
        if (amounts == null || (spec.kind() != TrailerSpec.Kind.FERTILIZER
                && spec.kind() != TrailerSpec.Kind.SEEDER)) {
            return List.of();
        }
        boolean fertilizer = spec.kind() == TrailerSpec.Kind.FERTILIZER;
        float baseX = (fertilizer ? -5.5F : -10.5F) * LandVehicleSpec.MODEL_UNIT;
        float baseY = -3.0F * LandVehicleSpec.MODEL_UNIT;
        float baseZ = (fertilizer ? -3.0F : -2.0F) * LandVehicleSpec.MODEL_UNIT;
        int divisor = fertilizer ? 32 : 16;
        int width = fertilizer ? 3 : 4;
        int maxLayerCount = fertilizer ? 6 : 8;
        float layerHeight = fertilizer ? 0.1F : 0.05F;
        float xSpacing = fertilizer ? 0.5F : 0.75F;
        float zSpacing = fertilizer ? 0.75F : 0.5F;
        float stagger = fertilizer ? 0.5F : 0.7F;
        float nestedScale = 0.45F;
        float worldScale = spec.bodyScale() * nestedScale;

        List<InventoryTransform> transforms = new ArrayList<>();
        int layer = 0;
        int index = 0;
        for (int slot = 0; slot < amounts.length; slot++) {
            if (amounts[slot] <= 0) {
                continue;
            }
            int count = Math.max(1, amounts[slot] / divisor);
            for (int j = 0; j < count; j++) {
                int layerIndex = index % maxLayerCount;
                float localX = (layerIndex % width) * xSpacing + stagger * (layer % 2);
                float localY = layer * layerHeight + (fertilizer ? j * 0.0625F : 0.0F);
                float localZ = (layerIndex / width) * zSpacing;
                Quaternionf rotation = new Quaternionf()
                        .rotateX(radians(90.0F))
                        .rotateZ(radians(47.0F * index))
                        .rotateX(radians(2.0F * layerIndex));
                Vector3f zFight = new Vector3f(layer * 0.001F, layer * 0.001F, layer * 0.001F);
                rotation.transform(zFight);
                localX += zFight.x;
                localY += zFight.y;
                localZ += zFight.z;

                Vector3f center = new Vector3f(
                        spec.bodyPartX(baseX + nestedScale * localX),
                        spec.bodyPartY(baseY + nestedScale * localY),
                        spec.bodyPartZ(baseZ + nestedScale * localZ));
                transforms.add(new InventoryTransform(slot, center,
                        new Vector3f(worldScale), rotation));
                index++;
                if (index % maxLayerCount == 0) {
                    layer++;
                }
            }
        }
        return List.copyOf(transforms);
    }

    private static int inventoryFingerprint(ItemStack[] contents) {
        int result = 1;
        if (contents != null) {
            for (ItemStack stack : contents) {
                result = 31 * result + (stack == null ? 0 : stack.hashCode());
            }
        }
        return result;
    }

    private void updateFluid(Location root, FluidVisual visual) {
        if (visual == null || visual.fraction() <= 0.0F) {
            fluid.setVisibleByDefault(false);
            return;
        }
        fluid.setVisibleByDefault(true);
        BlockData data = visual.material().createBlockData();
        if (!data.matches(fluid.getBlock())) {
            fluid.setBlock(data);
        }
        /* FluidTrailerRenderer#drawFluid source cuboid:
         * x=-.3875, y=-.1875, z=-.99, width=.7625, max height=9.9/16,
         * depth=1.67. It is drawn inside the common body transform. */
        float height = spec.bodyScale() * 9.9F * LandVehicleSpec.MODEL_UNIT
                * Math.min(1.0F, visual.fraction());
        fluid.teleport(root, TeleportFlag.EntityState.RETAIN_PASSENGERS);
        fluid.setRotation(root.getYaw(), 0.0F);
        fluid.setTransformation(new Transformation(
                new Vector3f(spec.bodyPartX(-0.3875F), spec.bodyPartY(-0.1875F),
                        spec.bodyPartZ(-0.99F)),
                new Quaternionf(),
                new Vector3f(spec.bodyScale() * 0.7625F, height,
                        spec.bodyScale() * 1.67F),
                new Quaternionf()));
    }

    private static void place(ItemDisplay display, Location root, Vector3f center,
                              Quaternionf leftRotation, Vector3f scale, Quaternionf rightRotation) {
        display.teleport(root, TeleportFlag.EntityState.RETAIN_PASSENGERS);
        display.setRotation(root.getYaw(), 0.0F);
        Quaternionf itemDisplayCompensation = new Quaternionf(rightRotation).rotateY((float) Math.PI);
        display.setTransformation(new Transformation(center, leftRotation, scale, itemDisplayCompensation));
    }

    private void updateBrightness(Location root) {
        Block sample = root.clone().add(0.0D, spec.entityHeight() + 0.01D, 0.0D).getBlock();
        Display.Brightness brightness = new Display.Brightness(sample.getLightFromBlocks(), sample.getLightFromSky());
        for (Entity entity : entities) {
            if (entity instanceof Display display && !brightness.equals(display.getBrightness())) {
                display.setBrightness(brightness);
            }
        }
    }

    public Interaction interaction() {
        return interaction;
    }

    public List<Entity> entities() {
        return Collections.unmodifiableList(entities);
    }

    public boolean valid() {
        return interaction.isValid() && body.isValid()
                && wheels.stream().allMatch(wheel -> wheel.entity.isValid())
                && extras.stream().allMatch(extra -> extra.entity.isValid())
                && (fluid == null || fluid.isValid());
    }

    public void remove() {
        entities.forEach(Entity::remove);
    }

    private static float radians(float value) {
        return (float) Math.toRadians(value);
    }

    private record WheelDisplay(ItemDisplay entity, int side, float axleZ) {
    }

    private record ExtraDisplay(ItemDisplay entity, Vector3f center, Vector3f scale,
                                boolean spins, float preSpinZ, float sourceYaw, boolean steering, boolean pitching) {
    }

    private record InventoryDisplay(ItemDisplay entity, InventoryLayout layout) {
    }

    record InventoryLayout(ItemStack stack, Vector3f center, Vector3f scale, Quaternionf rotation) {
    }

    record InventoryTransform(int slot, Vector3f center, Vector3f scale, Quaternionf rotation) {
    }

    public record FluidVisual(Material material, float fraction) {
    }
}
