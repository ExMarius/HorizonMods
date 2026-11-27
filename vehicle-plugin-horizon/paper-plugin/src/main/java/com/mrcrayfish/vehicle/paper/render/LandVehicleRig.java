package com.mrcrayfish.vehicle.paper.render;

import com.mrcrayfish.vehicle.paper.vehicle.FuelGauge;
import com.mrcrayfish.vehicle.paper.vehicle.LandVehicleSpec;
import io.papermc.paper.entity.TeleportFlag;
import org.bukkit.Bukkit;
import org.bukkit.Location;
import org.bukkit.Material;
import org.bukkit.NamespacedKey;
import org.bukkit.SoundCategory;
import org.bukkit.World;
import org.bukkit.attribute.Attribute;
import org.bukkit.attribute.AttributeInstance;
import org.bukkit.block.Block;
import org.bukkit.entity.Display;
import org.bukkit.entity.Entity;
import org.bukkit.entity.Horse;
import org.bukkit.entity.Interaction;
import org.bukkit.entity.ItemDisplay;
import org.bukkit.entity.Player;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.meta.ItemMeta;
import org.bukkit.util.Transformation;
import org.joml.Quaternionf;
import org.joml.Vector3f;

import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ThreadLocalRandom;

/** Multipart vanilla-display rig driven by a generated land-vehicle definition. */
public final class LandVehicleRig {
    /** BM: true numai pe durata in care vehiculul se roteste/se misca
     *  (A/D): serverul forteaza scaunul sa urmeze vehiculul. In repaus,
     *  campul ramane false si clientul detine rotatia (rider vanilla). */
    private boolean carryBody = false;

    public void setSeatBodyCarry(boolean carryBody) {
        this.carryBody = carryBody;
    }

    public static final String ENTITY_TAG = "mcv_plugin_vehicle";
    private static final int VANILLA_ENTITY_LERP_TICKS = 3;
    /* Ciclul BL: scaunul este un cal la scara minima, invizibil, fara saua:
     * acelasi rider pose + HUD de inimi, iar yaw-ul calareului este clamp-uit
     * vanilla la yaw-ul vehiculului (corp blocat, cap liber). Entitatile sunt
     * excluse din selectoarele /kill si sunt ejectate inainte de remove(), deci
     * bucla din cautarea vanilla a locului de demontare nu apare. */
    private static final double SEAT_CARRIER_SCALE = 0.0625D;
    // A 1.21.4 horse-dismount search can loop forever for tiny bounding boxes at
    // certain fractional Y coordinates. UTB has a different seat height, so keep
    // its invisible carrier at least 0.4 blocks high (0.25 * 1.6).
    private static final double UTB_SEAT_CARRIER_SCALE = 0.25D;
    private static final double SEAT_GAUGE_MAX_HEALTH = FuelGauge.MAX_HALF_HEARTS;

    private final UUID vehicleId;
    private final LandVehicleSpec spec;
    private final Interaction interaction;
    private final ItemDisplay body;
    private HorizonOffRoaderRig horizonRig;
    private HorizonGoKartRig kartRig;
    private DaciaHorizonWheels daciaWheels;
    private final ItemDisplay engine;
    private final ItemDisplay steering;
    private final ItemDisplay towBar;

    /** A vanilla ItemDisplay draws an item's local +Z axis pointing AWAY from the entity's
     * facing direction (items render 'into the screen'), i.e. turned 180 degrees versus
     * how Minecraft entity models face. Every vehicle part therefore receives this one
     * global yaw correction inside place(). */
    private static final Quaternionf ITEM_DISPLAY_YAW_CORRECTION =
            new Quaternionf().rotateY((float) Math.PI);

    /* THE tow bar math that burned the six failed nudge rounds, written down exactly:
     * tow_bar.json is AUTHORED pre-rotated - its drawbar arm already points at the car
     * when rendered with NO net yaw. But place() applies ITEM_DISPLAY_YAW_CORRECTION (+180 grade) to everything. To exempt the tow bar, its SOURCE rotation must
     * cancel that correction. The Part is created with rotationY = 180, and building the
     * source rotation from the Part's own angles (like every other part does) yields
     * rotateY(+pi); composed with the place() correction the net rotation is
     * rotateY(+pi). mul rotateY(+pi) = rotateY(2*pi) = IDENTITY. The old hand-written code reached the same identity by
     * stacking an unexplained second +pi, so any offset edit LOOKED like a no-op while we
     * were actually editing - wrong file (TRACTOR vs SMART_CAR) - but also fighting an
     * invisible double flip. From here on: ONE correction constant, ONE explicit source
     * rotation built from the Part angles, zero hidden flips. */
    private static final Quaternionf TOW_BAR_SOURCE_ROTATION = new Quaternionf()
            .rotateY((float) Math.PI); // == Part rotationY = 180; place() adds +180 again -> net 0
    private final List<PartDisplay> chassisParts;
    private final List<PartDisplay> forkParts;
    private final ItemDisplay storageChest;
    private final Interaction storageInteraction;
    private final List<WheelDisplay> wheels;
    private final List<SeatCarrier> seats;
    private final List<Entity> entities;
    /** New identity for each physical rig, even when the logical vehicle UUID is reused. */
    private final UUID spawnSessionId = UUID.randomUUID();
    private float seatGauge = 1.0F;
    // Prototype-only visual value; no player commands or loading logic use it yet.
    private double recoveryRampProgress;
    private boolean recoveryRootPivot;
    private final List<ItemDisplay> recoveryCableDisplays = new ArrayList<>();
    private List<com.mrcrayfish.vehicle.paper.recovery.RecoveryCable.Point> recoveryCable = List.of();
    private float propellerRotation;
    private float flapAngle;
    private float elevatorAngle;
    private float helicopterBladeRotation;
    private float helicopterJoystickForward;
    private float helicopterJoystickStrafe;
    private boolean removed;
    private int policeFlash = -1;
    private Integer policeColor;

    private LandVehicleRig(UUID vehicleId, LandVehicleSpec spec, Interaction interaction,
                           ItemDisplay body, ItemDisplay engine, ItemDisplay steering,
                           ItemDisplay towBar,
                           List<PartDisplay> chassisParts, List<PartDisplay> forkParts,
                           ItemDisplay storageChest, Interaction storageInteraction,
                           List<WheelDisplay> wheels, List<SeatCarrier> seats, List<Entity> entities) {
        this.vehicleId = vehicleId;
        this.spec = spec;
        this.interaction = interaction;
        this.body = body;
        this.engine = engine;
        this.steering = steering;
        this.towBar = towBar;
        this.chassisParts = chassisParts;
        this.forkParts = forkParts;
        this.storageChest = storageChest;
        this.storageInteraction = storageInteraction;
        this.wheels = wheels;
        this.seats = seats;
        this.entities = entities;
    }

    public static LandVehicleRig spawn(UUID vehicleId, LandVehicleSpec spec, Location location) {
        World world = location.getWorld();
        if (world == null) {
            throw new IllegalArgumentException("Cannot spawn a vehicle without a world");
        }

        List<Entity> all = new ArrayList<>();
        Interaction interaction = world.spawn(location, Interaction.class, hitbox -> {
            hitbox.setInteractionWidth(Math.max(2.2F, spec.entityWidth()));
            hitbox.setInteractionHeight(Math.max(1.1F, spec.entityHeight()));
            hitbox.setResponsive(true);
            hitbox.setPersistent(false);
        });
        mark(interaction, vehicleId);
        all.add(interaction);

        boolean horizon = "horizon_off_roader".equals(spec.id());
        boolean horizonKart = "horizon_go_kart".equals(spec.id());
        ItemDisplay body = display(world, location, (horizon || horizonKart) ? new ItemStack(Material.AIR) : model(spec.bodyModel()));
        mark(body, vehicleId);
        all.add(body);

        ItemDisplay engine = partDisplay(world, location, spec.engine(), vehicleId, all);
        ItemDisplay steering = partDisplay(world, location, spec.steering(), vehicleId, all);
        ItemDisplay towBar = spec.canTowTrailers() && !"utb_650".equals(spec.id())
                ? partDisplay(world, location, new LandVehicleSpec.Part(spec.towBarModel(),
                spec.towBarVisualCenter(), 1.0F, 0.0F, 180.0F, 0.0F), vehicleId, all)
                : null;

        List<PartDisplay> chassisParts = new ArrayList<>();
        for (LandVehicleSpec.Part part : spec.bodyParts()) {
            chassisParts.add(new PartDisplay(
                    partDisplay(world, location, part, vehicleId, all), part));
        }
        List<PartDisplay> forkParts = new ArrayList<>();
        ItemDisplay storageChest = null;
        Interaction storageInteraction = null;
        if (spec.mopedParts() != null) {
            for (LandVehicleSpec.Part part : spec.mopedParts().forkParts()) {
                forkParts.add(new PartDisplay(
                        partDisplay(world, location, part, vehicleId, all), part));
            }
            storageChest = display(world, location, new ItemStack(Material.CHEST));
            storageChest.setVisibleByDefault(false);
            mark(storageChest, vehicleId);
            all.add(storageChest);

            storageInteraction = world.spawn(location, Interaction.class, hitbox -> {
                hitbox.setInteractionWidth(0.8F);
                hitbox.setInteractionHeight(0.8F);
                hitbox.setResponsive(true);
                hitbox.setPersistent(false);
            });
            mark(storageInteraction, vehicleId);
            all.add(storageInteraction);
        }

        List<WheelDisplay> wheels = new ArrayList<>();
        for (LandVehicleSpec.Wheel properties : (horizon || horizonKart) ? List.<LandVehicleSpec.Wheel>of() : spec.wheels()) {
            ItemDisplay wheel = display(world, location, model(wheelModelFor(spec, properties, "standard_wheel")));
            mark(wheel, vehicleId);
            all.add(wheel);
            wheels.add(new WheelDisplay(wheel, properties));
        }

        List<SeatCarrier> seats = new ArrayList<>();
        boolean bodyAssigned = false;
        for (LandVehicleSpec.Seat seat : spec.seats()) {
            ItemDisplay anchor;
            if (seat.driver() && !bodyAssigned) {
                anchor = body;
                bodyAssigned = true;
            } else {
                anchor = display(world, location, new ItemStack(Material.AIR));
                mark(anchor, vehicleId);
                all.add(anchor);
            }
            seats.add(new SeatCarrier(anchor, seat));
        }
        if (!bodyAssigned) {
            throw new IllegalArgumentException("Land vehicle " + spec.id() + " has no driver seat");
        }

        LandVehicleRig rig = new LandVehicleRig(vehicleId, spec, interaction, body, engine, steering,
                towBar, Collections.unmodifiableList(chassisParts),
                Collections.unmodifiableList(forkParts), storageChest, storageInteraction,
                Collections.unmodifiableList(wheels), Collections.unmodifiableList(seats), all);
        if ("horizon_recovery_prototype".equals(spec.id())) {
            for (int i=0;i<2;i++) {
                ItemDisplay cableDisplay=display(world,location,model("horizon_service_cable"));
                cableDisplay.setVisibleByDefault(false);mark(cableDisplay,vehicleId);
                all.add(cableDisplay);rig.recoveryCableDisplays.add(cableDisplay);
            }
        }
        if (horizon) rig.horizonRig = new HorizonOffRoaderRig(location, vehicleId, all);
        if (horizonKart) rig.kartRig = new HorizonGoKartRig(location, vehicleId, all);
        if ("dacia_logan_police".equals(spec.id())) {
            rig.daciaWheels = new DaciaHorizonWheels(location, vehicleId, all, spec);
            rig.setWheelModel("standard_wheel");
        }
        for (Entity entity : all) rig.markSpawnSession(entity);
        rig.update(location, 0.0F, 0.0F, 0.0F, 0.0F, 0.0F, false, 0);
        return rig;
    }

    public UUID spawnSessionId() { return spawnSessionId; }

    private void markSpawnSession(Entity entity) {
        entity.addScoreboardTag("mcv_session_" + spawnSessionId);
    }

    private static ItemDisplay partDisplay(World world, Location location, LandVehicleSpec.Part part,
                                           UUID vehicleId, List<Entity> all) {
        if (part == null) {
            return null;
        }
        ItemDisplay display = display(world, location, model(part.model()));
        mark(display, vehicleId);
        all.add(display);
        return display;
    }

    private static ItemDisplay display(World world, Location location, ItemStack stack) {
        return world.spawn(location, ItemDisplay.class, display -> {
            display.setItemStack(stack);
            display.setItemDisplayTransform(ItemDisplay.ItemDisplayTransform.NONE);
            display.setInterpolationDelay(0);
            display.setInterpolationDuration(1);
            display.setTeleportDuration(VANILLA_ENTITY_LERP_TICKS);
            display.setInvulnerable(true);
            display.setPersistent(false);
            display.setShadowRadius(0.0F);
            display.setShadowStrength(0.0F);
        });
    }

    private static Horse seatCarrier(World world, Location location, UUID vehicleId, double carrierScale) {
        /* Ciclul BL (feedback user): scaun = cal FARA saua. Calul are clampa
         * vanilla de riding: yaw-ul calareului este legat de yaw-ul vehiculului,
         * deci corpul ramane blocat pe scaun si doar capul se roteste liber
         * (~45 grade), exact ca in mod. Fara saua entitatea NU este
         * "controllable" de catre client (era problema cu porcul cu saua:
         * clientul ii impunea rotatia dupa camera si se batea cap in cap cu
         * setRotation-ul server-ului -> corpul se invartea/oscila). */
        Horse seat = world.spawn(location, Horse.class, carrier -> {
            /* Ciclul BM (seattest a confirmat: varianta C tine corpul fix):
             * cal CU saua + tamed => vanilla activeaza clampa de riding
             * (yaw-ul calareului legat de yaw-ul monturii -> corp blocat,
             * cap liber stanga-dreapta). MOVEMENT_SPEED 0 => jucatorul nu
             * poate plimba montura cu WASD; rotatia prin mouse ramane. */
            carrier.setTamed(true);
            carrier.getInventory().setSaddle(new ItemStack(org.bukkit.Material.SADDLE));
            carrier.setAI(false);
            carrier.setGravity(false);
            carrier.setCollidable(false);
            carrier.setInvisible(true);
            carrier.setInvulnerable(true);
            carrier.setSilent(true);
            carrier.setPersistent(false);
            carrier.setRemoveWhenFarAway(false);
            AttributeInstance scale = carrier.getAttribute(Attribute.SCALE);
            if (scale != null) {
                scale.setBaseValue(carrierScale);
            }
            AttributeInstance speed = carrier.getAttribute(Attribute.MOVEMENT_SPEED);
            if (speed != null) {
                speed.setBaseValue(0.0D);
            }
            AttributeInstance maximumHealth = carrier.getAttribute(Attribute.MAX_HEALTH);
            if (maximumHealth != null) {
                maximumHealth.setBaseValue(SEAT_GAUGE_MAX_HEALTH);
            }
            carrier.setHealth(SEAT_GAUGE_MAX_HEALTH);
        });
        mark(seat, vehicleId);
        return seat;
    }

    private Horse createSeatMount(SeatCarrier carrier) {
        if (removed || !carrier.anchor.isValid()) {
            return null;
        }
        Location location = carrier.anchor.getLocation();
        Horse seat = seatCarrier(location.getWorld(), location, vehicleId, seatCarrierScale());
        markSpawnSession(seat);
        if (!carrier.anchor.addPassenger(seat)) {
            seat.remove();
            return null;
        }
        carrier.mount = seat;
        entities.add(seat);
        applySeatGauge(seat);
        return seat;
    }

    private void discardSeat(SeatCarrier carrier) {
        Horse seat = carrier.mount;
        carrier.mount = null;
        if (seat != null) {
            entities.remove(seat);
            seat.remove();
        }
    }

    private static ItemStack model(String name) {
        // Regresie dovedita live: stack-ul PAPER cu item_model nu mai randeaza pe
        // acest server (vehiculele nevopsite erau invizibile; vopsitele - carefolosesc
        // LEATHER_HORSE_ARMOR via coloredStack - apareau). Unificam pe materialul
        // dovedit-vizibil. Culoarea ALBA explicita pune dyed_color pe stack: clientul
        // tine din stack (calea dovedita la vopsire) si nu mai cade pe default-ul
        // definitiei, pe care clientii noi il interpreteaza ARGB cu alpha 0 (fetele
        // cu tintindex deveneau transparente - "gol la interior" la roti, body invizibil).
        ItemStack item = new ItemStack(Material.LEATHER_HORSE_ARMOR);
        ItemMeta meta = item.getItemMeta();
        meta.setItemModel(name.startsWith("dacia_police_body")
                ? new NamespacedKey("daciapolice", name.replace("dacia_police_body", "body")) : new NamespacedKey("vehicle", name));
        if (meta instanceof org.bukkit.inventory.meta.LeatherArmorMeta armor) {
            armor.setColor(org.bukkit.Color.fromRGB(0xF9FFFE));
        }
        item.setItemMeta(meta);
        return item;
    }

    private static void mark(Entity entity, UUID vehicleId) {
        entity.addScoreboardTag(ENTITY_TAG);
        entity.addScoreboardTag("mcv_" + vehicleId);
    }

    /** Isolated recovery test: pitch the complete rig around its root, not the wheelie axle.
     * This only changes rendering and does not validate tilted-body clearance. */
    public void updateRecoveryPose(Location root, float frontSpin, float rearSpin, float pitchDegrees, int tickCount) {
        if (!Float.isFinite(pitchDegrees) || Math.abs(pitchDegrees)>45F)
            throw new IllegalArgumentException("Invalid recovery pitch");
        recoveryRootPivot=true;
        try { update(root,0F,frontSpin,rearSpin,pitchDegrees,0F,false,tickCount); }
        finally { recoveryRootPivot=false; }
    }

    public void update(Location root, float renderSteeringAngle, float frontWheelRotation,
                       float rearWheelRotation, float wheelieAngle, float bodyRoll,
                       boolean engineRunning, int tickCount) {
        if (!valid()) {
            return;
        }

        float yaw = root.getYaw();
        Quaternionf chassisRotation = usesAircraftBodyRotation()
                ? SourceTransforms.aircraftRotation(wheelieAngle, bodyRoll)
                : SourceTransforms.chassisRotation(wheelieAngle, bodyRoll);
        Vector3f bodyOrigin = point(spec.bodyOrigin());
        Vector3f driverSeat = pigAnchor(chassis(driverSeatOffset(), wheelieAngle, bodyRoll));
        Location renderAnchor = local(root, driverSeat);

        interaction.teleport(root);
        interaction.setRotation(yaw, 0.0F);
        if (tickCount % 5 == 0) {
            updateBrightness(root);
        }

        Vector3f bodyCenter = chassis(bodyOrigin, wheelieAngle, bodyRoll);
        place(body, renderAnchor, relativeToSeat(bodyCenter, driverSeat), yaw, chassisRotation,
                new Vector3f(spec.bodyScale() * spec.modelScaleCorrection(spec.bodyModel())),
                new Quaternionf());
        if (horizonRig != null) {
            horizonRig.update(renderAnchor, driverSeat, chassisRotation, renderSteeringAngle,
                    frontWheelRotation, rearWheelRotation, wheelieAngle, bodyRoll, point(spec.wheeliePivot()));
        }

        if (kartRig != null) kartRig.update(renderAnchor, driverSeat, chassisRotation, renderSteeringAngle,
                frontWheelRotation, rearWheelRotation, wheelieAngle, bodyRoll, point(spec.wheeliePivot()),
                engineRunning, tickCount);

        if (engine != null) {
            LandVehicleSpec.Part part = spec.engine();
            Quaternionf shake = new Quaternionf();
            if (engineRunning && (tickCount & 1) == 1) {
                shake.rotateX(radians(0.5F)).rotateZ(radians(0.5F)).rotateY(radians(-0.5F));
            }
            Vector3f relative = point(part.center()).sub(bodyOrigin);
            shake.transform(relative);
            Vector3f center = chassis(new Vector3f(bodyOrigin).add(relative), wheelieAngle, bodyRoll);
            Quaternionf rotation = new Quaternionf(chassisRotation).mul(shake);
            Quaternionf sourceRotation = new Quaternionf()
                    .rotateX(radians(part.rotationX()))
                    .rotateY(radians(part.rotationY()))
                    .rotateZ(radians(part.rotationZ()));
            place(engine, renderAnchor, relativeToSeat(center, driverSeat), yaw, rotation,
                    new Vector3f(part.scale()), sourceRotation);
        }

        if (daciaWheels != null) daciaWheels.update(renderAnchor, driverSeat, chassisRotation,
                point(spec.wheeliePivot()), renderSteeringAngle, frontWheelRotation, rearWheelRotation,
                wheelieAngle, bodyRoll);

        float steeringRotation = renderSteeringAngle / spec.maxSteeringAngle()
                * spec.steeringVisualAngle();
        Quaternionf forkRotation = SourceTransforms.motorcycleSteering(spec.motorcycle(), steeringRotation);
        if (steering != null) {
            LandVehicleSpec.Part part = spec.steering();
            Vector3f unsteeredCenter = point(part.center()).add(point(spec.steeringDisplayOffset()));
            Vector3f center;
            Quaternionf rotation;
            if (spec.motorcycle() != null) {
                center = SourceTransforms.forkPoint(
                        unsteeredCenter, bodyOrigin, spec.motorcycle(), forkRotation);
                center = chassis(center, wheelieAngle, bodyRoll);
                rotation = new Quaternionf(chassisRotation).mul(forkRotation)
                        .rotateX(radians(part.rotationX()))
                        .rotateY(radians(part.rotationY()))
                        .rotateZ(radians(part.rotationZ()));
            } else {
                center = chassis(unsteeredCenter, wheelieAngle, bodyRoll);
                rotation = new Quaternionf(chassisRotation)
                        .rotateX(radians(part.rotationX()))
                        .rotateY(radians(part.rotationY() + steeringRotation))
                        .rotateZ(radians(part.rotationZ()));
            }
            place(steering, renderAnchor, relativeToSeat(center, driverSeat), yaw, rotation,
                    new Vector3f(part.scale()), new Quaternionf());
        }

        updateRecoveryCable(renderAnchor,driverSeat,yaw,wheelieAngle,bodyRoll);
        for (PartDisplay partDisplay : chassisParts) {
            placePropertyPart(partDisplay, renderAnchor, driverSeat,
                    yaw, wheelieAngle, bodyRoll, chassisRotation);
        }

        for (PartDisplay partDisplay : forkParts) {
            LandVehicleSpec.Part part = partDisplay.properties;
            Vector3f center = SourceTransforms.forkPoint(
                    point(part.center()), bodyOrigin, spec.motorcycle(), forkRotation);
            center = chassis(center, wheelieAngle, bodyRoll);
            Quaternionf rotation = new Quaternionf(chassisRotation).mul(forkRotation);
            Quaternionf sourceRotation = new Quaternionf()
                    .rotateX(radians(part.rotationX()))
                    .rotateY(radians(part.rotationY()))
                    .rotateZ(radians(part.rotationZ()));
            place(partDisplay.entity, renderAnchor, relativeToSeat(center, driverSeat), yaw, rotation,
                    new Vector3f(part.scale()), sourceRotation);
        }

        if (storageChest != null && spec.mopedParts() != null) {
            placePropertyPart(storageChest, spec.mopedParts().chest(), renderAnchor, driverSeat,
                    yaw, wheelieAngle, bodyRoll, chassisRotation);
            Vector3f interactionPoint = chassis(point(spec.mopedParts().chest().center()),
                    wheelieAngle, bodyRoll);
            storageInteraction.teleport(local(root, interactionPoint));
            storageInteraction.setRotation(yaw, 0.0F);
        }

        if (towBar != null) {
            /* AbstractLandVehicleRenderer renders the tow bar before applying the
             * axle/wheel translations and wheelie matrix. Keep its root-space
             * center and orientation fixed while the chassis wheelies. */
            Vector3f center = point(spec.towBarVisualCenter());
            place(towBar, renderAnchor, relativeToSeat(center, driverSeat), yaw, new Quaternionf(),
                    new Vector3f(1.0F), TOW_BAR_SOURCE_ROTATION);
        }

        for (WheelDisplay wheelDisplay : wheels) {
            LandVehicleSpec.Wheel wheel = wheelDisplay.properties;
            float spin = wheel.front() ? frontWheelRotation : rearWheelRotation;
            Vector3f center;
            Quaternionf rotation;
            Quaternionf sourceRotation;
            if (wheel.front() && spec.motorcycle() != null) {
                Vector3f unsteeredCenter = point(wheel.visualCenter());
                center = SourceTransforms.forkPoint(
                        unsteeredCenter, bodyOrigin, spec.motorcycle(), forkRotation);
                center = chassis(center, wheelieAngle, bodyRoll);
                rotation = new Quaternionf(chassisRotation).mul(forkRotation)
                        .rotateX(radians(-spin));
                sourceRotation = spec.motorcycle().frontWheelYaw180()
                        ? new Quaternionf().rotateY((float) Math.PI) : new Quaternionf();
            } else {
                float steeringAngle = wheel.front() ? renderSteeringAngle : 0.0F;
                float steerRadians = radians(steeringAngle);
                center = new Vector3f(
                        wheel.axleX() + wheel.halfWidthOffset() * (float) Math.cos(steerRadians),
                        wheel.centerY(),
                        wheel.axleZ() - wheel.halfWidthOffset() * (float) Math.sin(steerRadians)
                );
                center = chassis(center, wheelieAngle, bodyRoll);
                rotation = new Quaternionf(chassisRotation)
                        .rotateY(steerRadians)
                        .rotateX(radians(-spin));
                sourceRotation = wheel.side() > 0 && !"bmw_m6".equals(spec.id())
                        ? new Quaternionf().rotateY((float) Math.PI) : new Quaternionf();
            }
            place(wheelDisplay.entity, renderAnchor, relativeToSeat(center, driverSeat), yaw, rotation,
                    new Vector3f(wheel.scaleX(), wheel.scaleY(), wheel.scaleZ()), sourceRotation);
        }

        for (SeatCarrier carrier : seats) {
            if (carrier.anchor != body) {
                Vector3f seatPoint = pigAnchor(chassis(
                        seatOffset(carrier.properties), wheelieAngle, bodyRoll));
                Location seatLocation = local(root, seatPoint);
                carrier.anchor.teleport(seatLocation, TeleportFlag.EntityState.RETAIN_PASSENGERS);
                carrier.anchor.setRotation(yaw + carrier.properties.yawOffset(), 0.0F);
            }
            maintainSeat(carrier, yaw);
        }
    }

    /** Update visual cable only; the loading runtime must validate world obstacles. */
    private void updateRecoveryCable(Location anchor, Vector3f seat, float yaw, float wheelie, float roll) {
        for (int i=0;i<recoveryCableDisplays.size();i++) {
            ItemDisplay display=recoveryCableDisplays.get(i);
            boolean visible=i+1<recoveryCable.size();
            if (display.isVisibleByDefault()!=visible) display.setVisibleByDefault(visible);
            if (!visible) continue;
            var a=recoveryCable.get(i);var b=recoveryCable.get(i+1);
            // The legacy isolated rig used the opposite longitudinal convention.
            boolean corrected=spec.bodyParts().stream().anyMatch(p -> "horizon_service_ramp".equals(p.model()) && p.center().z()>0);
            float longitudinal=corrected ? 1F : -1F;
            Vector3f from=chassis(new Vector3f((float)-a.x(),(float)a.y(),longitudinal*(float)a.z()),wheelie,roll);
            Vector3f to=chassis(new Vector3f((float)-b.x(),(float)b.y(),longitudinal*(float)b.z()),wheelie,roll);
            Vector3f delta=new Vector3f(to).sub(from);float length=delta.length();
            if (length<1.0e-5F) {display.setVisibleByDefault(false);continue;}
            Vector3f center=new Vector3f(from).add(to).mul(.5F);
            Quaternionf rotation=new Quaternionf().rotationTo(new Vector3f(0,1,0),delta.div(length));
            place(display,anchor,relativeToSeat(center,seat),yaw,rotation,new Vector3f(4F,4F*length,4F),new Quaternionf());
        }
    }

    /** Test/internal hook: coordinates are in the authored truck frame, not world.
     * Calling this does not attach or move another vehicle, nor check obstacles. */
    public void setRecoveryCable(java.util.List<com.mrcrayfish.vehicle.paper.recovery.RecoveryCable.Point> points) {
        if (!"horizon_recovery_prototype".equals(spec.id())) throw new IllegalStateException("Not a recovery prototype");
        if (points==null || points.isEmpty()) {recoveryCable=List.of();return;}
        if (!com.mrcrayfish.vehicle.paper.recovery.RecoveryCable.clearsLevelBed(points,.18,5.35,.86,.018))
            throw new IllegalArgumentException("Cable geometry is unsafe for the prototype bed");
        recoveryCable=List.copyOf(points);
    }

    private void placePropertyPart(PartDisplay partDisplay,
                                   Location renderAnchor, Vector3f driverSeat, float yaw,
                                   float wheelieAngle, float bodyRoll, Quaternionf chassisRotation) {
        LandVehicleSpec.Part part = partDisplay.properties;
        Vector3f center = chassis(point(part.center()), wheelieAngle, bodyRoll);
        Quaternionf rotation = new Quaternionf(chassisRotation);
        if ("horizon_recovery_prototype".equals(spec.id()) && "horizon_service_ramp".equals(part.model())) {
            rotation.rotateX(com.mrcrayfish.vehicle.paper.recovery.RecoveryRampKinematics.paperOffsetRadians(recoveryRampProgress));
        }
        if (part.openable() != null) {
            float angle = radians(partDisplay.openAngle());
            switch (part.openable().axis()) {
                case X -> rotation.rotateX(angle);
                case Y -> rotation.rotateY(angle);
                case Z -> rotation.rotateZ(angle);
            }
        }
        applyPlanePartRotation(rotation, part.model());
        Quaternionf sourceRotation = new Quaternionf()
                .rotateX(radians(part.rotationX()))
                .rotateY(radians(part.rotationY()))
                .rotateZ(radians(part.rotationZ()));
        float visualScale = part.scale() * spec.modelScaleCorrection(part.model());
        place(partDisplay.entity, renderAnchor, relativeToSeat(center, driverSeat), yaw, rotation,
                new Vector3f(visualScale), sourceRotation);
    }

    /** Reproduces the actions in the original plane and helicopter complex-model files. */
    private void applyPlanePartRotation(Quaternionf rotation, String model) {
        switch (model) {
            case "sports_plane_propeller" -> rotation.rotateZ(radians(propellerRotation));
            case "sports_plane_left_aileron" -> rotation
                    .rotateY(radians(-5.0F))
                    .rotateX(radians(flapAngle * 0.5F))
                    .rotateY(radians(5.0F));
            case "sports_plane_right_aileron" -> rotation
                    .rotateY(radians(5.0F))
                    .rotateX(radians(flapAngle * -0.5F))
                    .rotateY(radians(-5.0F));
            case "sports_plane_elevator" -> rotation.rotateX(radians(elevatorAngle * 0.5F));
            case "sports_plane_joystick" -> rotation
                    .rotateX(radians(elevatorAngle * -0.25F))
                    .rotateZ(radians(flapAngle * -0.25F));
            case "compact_helicopter_blades", "sofacopter_blades" ->
                    rotation.rotateY(radians(helicopterBladeRotation));
            case "compact_helicopter_tail_rotor" -> rotation.rotateX(radians(helicopterBladeRotation));
            case "compact_helicopter_joystick" -> rotation
                    .rotateX(radians(helicopterJoystickForward * 10.0F))
                    .rotateZ(radians(helicopterJoystickStrafe * -10.0F));
            default -> {
            }
        }
    }

    public void setPlaneAnimations(float propellerRotation, float flapAngle, float elevatorAngle) {
        this.propellerRotation = propellerRotation;
        this.flapAngle = flapAngle;
        this.elevatorAngle = elevatorAngle;
    }

    public void setHelicopterAnimations(float bladeRotation, float joystickForward,
                                        float joystickStrafe) {
        this.helicopterBladeRotation = bladeRotation;
        this.helicopterJoystickForward = joystickForward;
        this.helicopterJoystickStrafe = joystickStrafe;
    }

    private void placePropertyPart(ItemDisplay display, LandVehicleSpec.Part part,
                                   Location renderAnchor, Vector3f driverSeat, float yaw,
                                   float wheelieAngle, float bodyRoll, Quaternionf chassisRotation) {
        if (display == null || part == null) {
            return;
        }
        Vector3f center = chassis(point(part.center()), wheelieAngle, bodyRoll);
        Quaternionf sourceRotation = new Quaternionf()
                .rotateX(radians(part.rotationX()))
                .rotateY(radians(part.rotationY()))
                .rotateZ(radians(part.rotationZ()));
        place(display, renderAnchor, relativeToSeat(center, driverSeat), yaw, chassisRotation,
                new Vector3f(part.scale()), sourceRotation);
    }

    private void maintainSeat(SeatCarrier carrier, float yaw) {
        float seatYaw = yaw + carrier.properties.yawOffset();
        Horse seat = carrier.mount;
        if (seat == null) {
            return;
        }
        if (!seat.isValid()) {
            UUID riderId = carrier.rider;
            entities.remove(seat);
            carrier.mount = null;
            if (!removed && riderId != null) {
                Player rider = Bukkit.getPlayer(riderId);
                if (rider != null && rider.isOnline() && !rider.isDead()) {
                    Horse replacement = createSeatMount(carrier);
                    if (replacement != null && replacement.addPassenger(rider)) {
                        carrier.rider = riderId;
                        replacement.setRotation(seatYaw, 0.0F);
                        return;
                    }
                    discardSeat(carrier);
                }
            }
            carrier.rider = null;
            return;
        }

        Player rider = seat.getPassengers().stream()
                .filter(Player.class::isInstance)
                .map(Player.class::cast)
                .findFirst().orElse(null);
        if (rider == null) {
            carrier.rider = null;
            discardSeat(carrier);
            return;
        }
        carrier.rider = rider.getUniqueId();
        /* BM: scaunul are rider; cat timp vehiculul NU vireaza/se misca,
         * rotatia ramane la client (clampa vanilla de riding blocheaza
         * corpul pe scaun si lasa capul liber). In timpul virajelor/mersului
         * serverul tine scaunul la yaw-ul vehiculului => corpul calatorul
         * se misca o data cu masina. */
        if (carryBody) {
            seat.setRotation(seatYaw, 0.0F);
        }
    }

    private void place(ItemDisplay display, Location renderAnchor, Vector3f translation, float yaw,
                       Quaternionf leftRotation, Vector3f scale, Quaternionf sourceRightRotation) {
        display.teleport(renderAnchor, TeleportFlag.EntityState.RETAIN_PASSENGERS);
        display.setRotation(yaw, 0.0F);
        Quaternionf itemDisplayCompensation = new Quaternionf(sourceRightRotation).mul(ITEM_DISPLAY_YAW_CORRECTION);
        display.setTransformation(new Transformation(translation, leftRotation, scale, itemDisplayCompensation));
    }

    public void refreshBrightness(Location root) {
        if (valid()) {
            updateBrightness(root);
        }
    }

    private void updateBrightness(Location root) {
        Block sample = root.clone().add(0.0D, spec.entityHeight() + 0.01D, 0.0D).getBlock();
        Display.Brightness brightness = new Display.Brightness(sample.getLightFromBlocks(), sample.getLightFromSky());
        for (Entity entity : entities) {
            if (entity instanceof ItemDisplay display && display.getType() != null
                    && !brightness.equals(display.getBrightness())) {
                display.setBrightness(brightness);
            }
        }
    }

    private Vector3f driverSeatOffset() {
        LandVehicleSpec.Seat seat = spec.seats().stream().filter(LandVehicleSpec.Seat::driver)
                .findFirst().orElseThrow();
        return seatOffset(seat);
    }

    private static Vector3f seatOffset(LandVehicleSpec.Seat seat) {
        return point(seat.sourceOffset()).add(0.0F, LandVehicleSpec.RIDER_HEIGHT_CORRECTION, 0.0F);
    }

    private double seatCarrierScale() {
        return "utb_650".equals(spec.id()) ? UTB_SEAT_CARRIER_SCALE : SEAT_CARRIER_SCALE;
    }

    private Vector3f pigAnchor(Vector3f seatPoint) {
        return new Vector3f(seatPoint).sub(0.0F, 0.7F * (float) seatCarrierScale(), 0.0F);
    }

    private Vector3f chassis(Vector3f sourcePoint, float wheelieAngle, float bodyRoll) {
        if (usesAircraftBodyRotation()) {
            return SourceTransforms.aircraftPoint(sourcePoint, wheelieAngle, bodyRoll);
        }
        return SourceTransforms.chassisPoint(
                sourcePoint, recoveryRootPivot ? new Vector3f() : point(spec.wheeliePivot()), wheelieAngle, bodyRoll);
    }

    private boolean usesAircraftBodyRotation() {
        return spec.motionType() == LandVehicleSpec.MotionType.AIR
                || spec.motionType() == LandVehicleSpec.MotionType.HELICOPTER;
    }

    private static Vector3f relativeToSeat(Vector3f point, Vector3f seat) {
        return new Vector3f(point).sub(seat);
    }

    private static Vector3f point(LandVehicleSpec.Point point) {
        return new Vector3f(point.x(), point.y(), point.z());
    }

    private static float radians(float degrees) {
        return (float) Math.toRadians(degrees);
    }

    private static Location local(Location root, Vector3f point) {
        double radians = Math.toRadians(root.getYaw());
        double sin = Math.sin(radians);
        double cos = Math.cos(radians);
        return root.clone().add(point.x * cos - point.z * sin, point.y, point.x * sin + point.z * cos);
    }

    public void setSeatGauge(float fraction) {
        seatGauge = Float.isFinite(fraction) ? Math.max(0.0F, Math.min(1.0F, fraction)) : 1.0F;
        for (SeatCarrier carrier : seats) {
            if (carrier.mount != null && carrier.mount.isValid()) {
                applySeatGauge(carrier.mount);
            }
        }
    }

    private void applySeatGauge(Horse seat) {
        double health = FuelGauge.mountHealth(seatGauge);
        if (Math.abs(seat.getHealth() - health) > 0.01D) {
            seat.setHealth(health);
        }
    }

    public void tickSeats(float yaw) {
        if (removed) {
            return;
        }
        for (SeatCarrier carrier : seats) {
            maintainSeat(carrier, yaw);
        }
    }

    public boolean mount(Player player) {
        if (removed || !valid()) {
            return false;
        }

        /* VehicleEntity/SeatTracker selects the closest available source seat,
         * rather than the first seat in declaration order. This is particularly
         * important for the Off Roader: approaching its rear selects one of the
         * two hanging rear positions without requiring the front seats to fill. */
        SeatCarrier closest = null;
        double closestDistance = Double.POSITIVE_INFINITY;
        double playerHalfHeight = player.getBoundingBox().getHeight() * 0.5D;
        Location playerLocation = player.getLocation();
        for (SeatCarrier carrier : seats) {
            Horse seat = carrier.mount;
            if (seat != null && seat.isValid() && !seat.getPassengers().isEmpty()) {
                continue;
            }
            // UTB's compact bench sits close to the driver. If the driver seat is
            // empty, select it first; otherwise a remount can silently choose the
            // rear bench and leave the tractor uncontrollable.
            if ("utb_650".equals(spec.id()) && carrier.properties.driver()) {
                closest = carrier;
                break;
            }
            Location seatLocation = carrier.anchor.getLocation();
            if (!seatLocation.getWorld().equals(playerLocation.getWorld())) {
                continue;
            }
            /* SeatTracker compares the player's feet against seatY minus half
             * the player's bounding-box height. Preserve that source equation. */
            seatLocation.subtract(0.0D, playerHalfHeight, 0.0D);
            double distance = seatLocation.distanceSquared(playerLocation);
            if (distance < closestDistance) {
                closest = carrier;
                closestDistance = distance;
            }
        }
        if (closest == null) {
            return false;
        }

        if (closest.mount != null) {
            discardSeat(closest);
        }
        Horse seat = createSeatMount(closest);
        if (seat != null && seat.addPassenger(player)) {
            closest.rider = player.getUniqueId();
            return true;
        }
        discardSeat(closest);
        return false;
    }

    public Entity driverSeat() {
        SeatCarrier driver = seats.stream().filter(seat -> seat.properties.driver())
                .findFirst().orElseThrow();
        return driver.mount != null && driver.mount.isValid() ? driver.mount : driver.anchor;
    }

    public List<Entity> seatCarriers() {
        return seats.stream()
                .map(SeatCarrier::seat)
                .filter(java.util.Objects::nonNull)
                .filter(Entity::isValid)
                .map(Entity.class::cast)
                .toList();
    }

    public List<Entity> entities() {
        return Collections.unmodifiableList(entities);
    }

    /** Advances source OpenableAction animations. Closing sounds fire when the part reaches zero. */
    public boolean tickOpenables(Location root) {
        boolean changed = false;
        for (PartDisplay part : chassisParts) {
            if (part.tick()) {
                changed = true;
                if (!part.open && part.animationTick == 0) {
                    playCustomSound(root, part.properties.openable().closeSound());
                }
            }
        }
        return changed;
    }

    /** Current prototype visual progress; not proof of an unobstructed path. */
    public double recoveryRampProgress() { return recoveryRampProgress; }

    /** Prototype-only display control. No collision or permission checks are implied. */
    public void setRecoveryRampProgress(double progress) {
        if (!"horizon_recovery_prototype".equals(spec.id())) throw new IllegalStateException("Not a recovery prototype");
        com.mrcrayfish.vehicle.paper.recovery.RecoveryRampKinematics.paperOffsetRadians(progress);
        recoveryRampProgress = progress;
    }

    public boolean toggleOpenable(String id, Location root) {
        for (PartDisplay part : chassisParts) {
            LandVehicleSpec.Openable openable = part.properties.openable();
            if (openable == null || !openable.id().equals(id)) {
                continue;
            }
            part.open = !part.open;
            if (part.open) {
                playCustomSound(root, openable.openSound());
            }
            return true;
        }
        return false;
    }

    public float openAngle(String id) {
        for (PartDisplay part : chassisParts) {
            LandVehicleSpec.Openable openable = part.properties.openable();
            if (openable != null && openable.id().equals(id)) {
                return part.openAngle();
            }
        }
        return 0.0F;
    }

    public Map<String, Boolean> openStates() {
        Map<String, Boolean> states = new LinkedHashMap<>();
        for (PartDisplay part : chassisParts) {
            if (part.properties.openable() != null) {
                states.put(part.properties.openable().id(), part.open);
            }
        }
        return states;
    }

    public void restoreOpenStates(Map<String, Boolean> states) {
        for (PartDisplay part : chassisParts) {
            LandVehicleSpec.Openable openable = part.properties.openable();
            if (openable == null) {
                continue;
            }
            part.open = states != null && Boolean.TRUE.equals(states.get(openable.id()));
            part.animationTick = part.open ? openable.animationLength() : 0;
        }
    }

    private static void playCustomSound(Location root, String sound) {
        if (root.getWorld() != null && sound != null && !sound.isBlank()) {
            float pitch = 0.8F + 0.2F * ThreadLocalRandom.current().nextFloat();
            root.getWorld().playSound(root, sound, SoundCategory.NEUTRAL, 1.0F, pitch);
        }
    }

    public boolean isStorageInteraction(Entity entity) {
        return storageInteraction != null && storageInteraction.getUniqueId().equals(entity.getUniqueId());
    }

    public void setStorageChestAttached(boolean attached) {
        if (storageChest != null && storageChest.isValid()) {
            storageChest.setVisibleByDefault(attached);
        }
    }

    public UUID vehicleId() {
        return vehicleId;
    }

    public boolean valid() {
        return interaction.isValid() && body.isValid()
                && (engine == null || engine.isValid())
                && (steering == null || steering.isValid())
                && (towBar == null || towBar.isValid())
                && chassisParts.stream().allMatch(part -> part.entity.isValid())
                && forkParts.stream().allMatch(part -> part.entity.isValid())
                && (storageChest == null || storageChest.isValid())
                && (storageInteraction == null || storageInteraction.isValid())
                && (horizonRig == null || horizonRig.valid())
                && (kartRig == null || kartRig.valid())
                && (daciaWheels == null || daciaWheels.valid())
                && wheels.stream().allMatch(wheel -> wheel.entity.isValid())
                && seats.stream().allMatch(seat -> seat.anchor.isValid());
    }

    public void remove() {
        removed = true;
        /* Detach riders synchronously while the living carrier is still valid.
         * Restoring an ordinary bounding box also keeps the fallback dismount
         * location independent of the carrier's minimum render scale. */
        for (SeatCarrier carrier : seats) {
            Horse seat = carrier.mount;
            if (seat == null || !seat.isValid() || seat.getPassengers().isEmpty()) {
                continue;
            }
            AttributeInstance scale = seat.getAttribute(Attribute.SCALE);
            if (scale != null) {
                scale.setBaseValue(1.0D);
            }
            seat.eject();
            if (!seat.getPassengers().isEmpty()) {
                /* Failing open is safer than deleting a still-ridden carrier. */
                entities.remove(seat);
                seat.setInvisible(false);
                seat.setInvulnerable(false);
                seat.setGravity(true);
            }
        }
        for (Entity entity : new ArrayList<>(entities)) {
            entity.remove();
        }
        entities.clear();
        for (SeatCarrier carrier : seats) {
            carrier.mount = null;
            carrier.rider = null;
        }
    }

    private record WheelDisplay(ItemDisplay entity, LandVehicleSpec.Wheel properties) {
    }

    private static final class PartDisplay {
        private final ItemDisplay entity;
        private final LandVehicleSpec.Part properties;
        private boolean open;
        private int animationTick;

        private PartDisplay(ItemDisplay entity, LandVehicleSpec.Part properties) {
            this.entity = entity;
            this.properties = properties;
        }

        private boolean tick() {
            LandVehicleSpec.Openable openable = properties.openable();
            if (openable == null) {
                return false;
            }
            int previous = animationTick;
            if (open && animationTick < openable.animationLength()) {
                animationTick++;
            } else if (!open && animationTick > 0) {
                animationTick--;
            }
            return previous != animationTick;
        }

        private float openAngle() {
            LandVehicleSpec.Openable openable = properties.openable();
            if (openable == null || animationTick == 0) {
                return 0.0F;
            }
            double progress = animationTick / (double) openable.animationLength();
            return (float) (openable.angle() * easeOutBack(progress));
        }
    }

    static double easeOutBack(double progress) {
        double c1 = 1.70158D;
        double c3 = c1 + 1.0D;
        return 1.0D + c3 * Math.pow(progress - 1.0D, 3.0D)
                + c1 * Math.pow(progress - 1.0D, 2.0D);
    }

    /* ===== Sistem mecanic: schimbare model roti + vopsea caroserie ============= */

    /** Cand slotul de motor e gol, piesa NU trebuie sa apara pe model (brief
     *  2026-10-24): stack gol = ItemDisplay complet invizibil. Re-montarea se face
     *  prin setEngineModel(...), care inlocuieste stack-ul - nu e nevoie de "show". */
    public void hideEngine() {
        if (kartRig != null) kartRig.hideEngine();
        if (!removed && engine != null && engine.isValid()) {
            engine.setItemStack(new org.bukkit.inventory.ItemStack(org.bukkit.Material.AIR));
        }
    }

    /** La fel ca motorul: rotile scoase din slot NU mai au voie sa apara pe model
     *  (nici in lume, nici in GUI) pana la re-montare. Inversul = setWheelModel. */
    public void hideWheels() {
        if (removed) {
            return;
        }
        if (horizonRig != null) horizonRig.hideWheels();
        if (kartRig != null) kartRig.hideWheels();
        if (daciaWheels != null) daciaWheels.hide();
        org.bukkit.inventory.ItemStack empty =
                new org.bukkit.inventory.ItemStack(org.bukkit.Material.AIR);
        for (WheelDisplay wheel : wheels) {
            if (wheel.entity != null && wheel.entity.isValid()) {
                wheel.entity.setItemStack(empty);
            }
        }
    }

    /** Schimba si PART-ul vizual al motorului la upgrade (ex. iron_small_engine ->
     *  diamond_small_engine), exact ca in mod, la schimbarea tier-ului. */
    public void setEngineModel(String modelName) {
        if (kartRig != null) kartRig.setEngine(modelName);
        if (!removed && engine != null && engine.isValid()) {
            engine.setItemStack(model(modelName));
        }
    }

    /** Leaps rotile pe noul model (STANDARD/SPORTS/OFF_ROAD - roti schimbate la mecanic). */
    public void setWheelModel(String modelName) {
        if (removed) {
            return;
        }
        if (horizonRig != null) horizonRig.setWheels(modelName);
        if (kartRig != null) kartRig.setWheels(modelName);
        if (daciaWheels != null) daciaWheels.setModel(modelName);
        ItemStack stack = daciaWheels != null && daciaWheels.handles(modelName)
                ? new ItemStack(Material.AIR) : model(modelName);
        for (WheelDisplay wheel : wheels) {
            if (wheel.entity != null && wheel.entity.isValid()) {
                // Keep front and rear UTB tires distinct and pivoted at their own hubs.
                String selectedModel = wheelModelFor(spec, wheel.properties, modelName);
                ItemStack selected = selectedModel.equals(modelName) ? stack : model(selectedModel);
                wheel.entity.setItemStack(selected);
            }
        }
    }

    static String wheelModelFor(LandVehicleSpec spec, LandVehicleSpec.Wheel wheel, String requested) {
        if ("horizon_recovery_prototype".equals(spec.id())) return "horizon_service_wheel";
        if ("bmw_m6".equals(spec.id())) return "horizon_coupe_wheel";
        return "utb_650".equals(spec.id()) && "standard_wheel".equals(requested)
                ? (wheel.front() ? "utb_650_wheel_front" : "utb_650_wheel_rear") : requested;
    }

    /** Vopsire cu spray can: caroseria trece pe un stack vopsibil (dyed_color) purtand
     *  acelasi model; tint-ul "dye" din definitia pack-ului recoloreaza fetele marcate.
     *  rgb null = revine la modelul nevopsit (paper, default alb). */
    public void applyColor(Integer rgb) {
        if (removed) {
            return;
        }
        if (horizonRig != null) horizonRig.applyColor(rgb);
        if (kartRig != null) kartRig.applyColor(rgb);
        if (horizonRig == null && kartRig == null && body != null && body.isValid()) {
            policeColor = rgb;
            body.setItemStack(coloredStack(policeBodyModel(), rgb));
        }
        // Modul inroseste TOATE partile caroseriei (capota/usile/acoperisul etc.), nu
        // doar corpul principal: replicam acelasi comportament ca sa nu ramana masina
        // vopsita "pe jumatate".
        for (PartDisplay part : chassisParts) {
            if (part.entity != null && part.entity.isValid()) {
                part.entity.setItemStack(coloredStack(part.properties.model(), rgb));
            }
        }
        for (PartDisplay part : forkParts) {
            if (part.entity != null && part.entity.isValid()) {
                part.entity.setItemStack(coloredStack(part.properties.model(), rgb));
            }
        }
    }

    private String policeBodyModel() {
        return "dacia_logan_police".equals(spec.id()) && policeFlash >= 0
                ? "dacia_police_body_flash_" + policeFlash : spec.bodyModel();
    }

    public void setPoliceFlash(int frame) {
        if (!"dacia_logan_police".equals(spec.id()) || removed || policeFlash == frame) return;
        policeFlash = frame;
        if (body.isValid()) body.setItemStack(coloredStack(policeBodyModel(), policeColor));
    }

    /** Stack vopsit (dyed_color) pentru un model de caroserie; stack normal cand rgb e
     *  null (nevopsit). Pack-ul are pentru modelele de caroserie definitie cu tint
     *  "dye" implicit alb, deci pe stack-uri nevopsite nu se schimba NIMIC vizual. */
    private static ItemStack coloredStack(String modelName, Integer rgb) {
        if (rgb == null) {
            return model(modelName);
        }
        ItemStack stack = new ItemStack(Material.LEATHER_HORSE_ARMOR);
        ItemMeta meta = stack.getItemMeta();
        if (meta instanceof org.bukkit.inventory.meta.LeatherArmorMeta armor) {
            armor.setItemModel(modelName.startsWith("dacia_police_body")
                    ? new NamespacedKey("daciapolice", modelName.replace("dacia_police_body", "body")) : new NamespacedKey("vehicle", modelName));
            armor.setColor(org.bukkit.Color.fromRGB(rgb));
        }
        stack.setItemMeta(meta);
        return stack;
    }

    private static final class SeatCarrier {
        private final ItemDisplay anchor;
        private final LandVehicleSpec.Seat properties;
        private Horse mount;
        private UUID rider;

        private SeatCarrier(ItemDisplay anchor, LandVehicleSpec.Seat properties) {
            this.anchor = anchor;
            this.properties = properties;
        }

        private Horse seat() {
            return mount;
        }
    }
}
