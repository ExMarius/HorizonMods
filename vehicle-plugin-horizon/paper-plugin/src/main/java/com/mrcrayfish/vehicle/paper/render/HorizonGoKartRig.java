package com.mrcrayfish.vehicle.paper.render;

import io.papermc.paper.entity.TeleportFlag;
import org.bukkit.Color;
import org.bukkit.Location;
import org.bukkit.Material;
import org.bukkit.NamespacedKey;
import org.bukkit.entity.Entity;
import org.bukkit.entity.ItemDisplay;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.meta.LeatherArmorMeta;
import org.bukkit.util.Transformation;
import org.joml.Quaternionf;
import org.joml.Vector3f;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/** Display groups for the Horizon model only; normal vehicle rigs are unaffected. */
final class HorizonGoKartRig {
    private enum Kind { BODY, WHEEL, STEERING, ENGINE }
    private record Piece(ItemDisplay display, HorizonGroups.Group group, Kind kind, int wheel) {}
    private static final float FRONT_Z = 11.2F * 1.18F / 16F;
    private static final float REAR_Z = -11.4F * 1.18F / 16F;
    private static final Quaternionf ITEM_YAW = new Quaternionf().rotateY((float)Math.PI);
    private final List<Piece> pieces = new ArrayList<>();
    private boolean wheelsVisible = true;
    private String wheelModel = "wheel_standard";
    private String engineModel = "engine_iron";
    private boolean engineVisible = true;

    HorizonGoKartRig(Location location, UUID id, List<Entity> entities) {
        add(location, id, entities, HorizonGroups.GO_KART_BODY, Kind.BODY, -1);
        for (int i=0; i<4; i++) add(location, id, entities, HorizonGroups.WHEEL_STANDARD, Kind.WHEEL, i);
        add(location, id, entities, HorizonGroups.GO_KART_STEERING_WHEEL, Kind.STEERING, -1);
        add(location, id, entities, HorizonGroups.ENGINE_IRON, Kind.ENGINE, -1);
    }

    private void add(Location at, UUID id, List<Entity> all, List<HorizonGroups.Group> groups, Kind kind, int wheel) {
        for (HorizonGroups.Group group : groups) {
            ItemDisplay d = at.getWorld().spawn(at, ItemDisplay.class, e -> {
                e.setItemStack(model(group.name()));
                e.setItemDisplayTransform(ItemDisplay.ItemDisplayTransform.NONE);
                e.setInterpolationDelay(0);
                e.setInterpolationDuration(1);
                e.setTeleportDuration(3);
                e.setInvulnerable(true);
                e.setPersistent(false);
                e.setShadowRadius(0);
                e.setShadowStrength(0);
            });
            d.addScoreboardTag(LandVehicleRig.ENTITY_TAG);
            d.addScoreboardTag("mcv_" + id);
            all.add(d);
            pieces.add(new Piece(d, group, kind, wheel));
        }
    }

    private static ItemStack model(String name) { return model(name, null); }
    private static ItemStack model(String name, Integer rgb) {
        ItemStack stack = new ItemStack(Material.LEATHER_HORSE_ARMOR);
        LeatherArmorMeta meta = (LeatherArmorMeta) stack.getItemMeta();
        meta.setItemModel(new NamespacedKey("horizonvehicles", name));
        meta.setColor(Color.fromRGB(rgb == null ? 0xFFFFFF : rgb));
        stack.setItemMeta(meta);
        return stack;
    }

    // These four groups form the two white nose fins and their dark backing.
    // Move them together toward the nose, leaving every wheel centre unchanged.
    static boolean isNoseFin(String name) {
        return name.equals("go_kart_body_part_03") || name.equals("go_kart_body_part_04")
                || name.equals("go_kart_body_part_06") || name.equals("go_kart_body_part_07");
    }
    static Vector3f noseFinOrigin(Vector3f sourceOrigin) {
        // Item-display yaw mirrors both X and Z before the group rotation.
        return new Vector3f(16F - sourceOrigin.x, sourceOrigin.y, 16F - sourceOrigin.z);
    }
    static final float NOSE_FIN_FORWARD = 2F * 1.18F / 16F;

    void update(Location anchor, Vector3f driverSeat, Quaternionf chassis, float steering,
                float frontSpin, float rearSpin, float wheelie, float roll, Vector3f pivot) {
        for (Piece p : pieces) {
            Vector3f center, scale;
            Quaternionf localRotation = new Quaternionf(chassis);
            switch (p.kind) {
                case BODY -> {
                    center = new Vector3f(0, .57F, isNoseFin(p.group.name()) ? -NOSE_FIN_FORWARD : 0F);
                    scale = new Vector3f(1.18F, 1.14F, 1.18F);
                }
                case WHEEL -> {
                    boolean front = p.wheel < 2;
                    float x = (p.wheel % 2 == 0 ? 1 : -1) * (front ? 11.64F : 12.16F) / 16F;
                    center = new Vector3f(x, front ? .295F : .320F, front ? FRONT_Z : REAR_Z);
                    scale = front ? new Vector3f(1.15F, 1.18F, 1.18F) : new Vector3f(1.34F, 1.28F, 1.28F);
                    // In Paper the boost pitches the body: keep both axles on the
                    // same chassis transform so the wheels do not detach visually.
                    localRotation.rotateY((float)Math.toRadians(front ? steering : 0))
                            .rotateX((float)Math.toRadians(-(front ? frontSpin : rearSpin)));
                }
                case STEERING -> {
                    center = new Vector3f(0, 10.50F * 1.14F / 16F, 2.95F * 1.18F / 16F);
                    scale = new Vector3f(1.14F);
                    localRotation.rotateX((float)Math.toRadians(30))
                            .rotateZ((float)Math.toRadians(-steering * 1.8F));
                }
                case ENGINE -> {
                    center = new Vector3f(0, 6.5F * 1.14F / 16F, -11.6F * 1.18F / 16F);
                    scale = new Vector3f(1.18F);
                }
                default -> throw new IllegalStateException();
            }
            center = SourceTransforms.chassisPoint(center, pivot, wheelie, roll);
            center.sub(driverSeat);
            Vector3f groupOrigin = p.kind == Kind.BODY && isNoseFin(p.group.name())
                    ? noseFinOrigin(p.group.origin()) : p.group.origin();
            Transformation t = HorizonPartTransform.group(center, scale, groupOrigin, p.group.rotation(), localRotation);
            Quaternionf right = new Quaternionf(t.getRightRotation()).mul(ITEM_YAW);
            p.display.teleport(anchor, TeleportFlag.EntityState.RETAIN_PASSENGERS);
            p.display.setRotation(anchor.getYaw(), 0);
            p.display.setTransformation(new Transformation(t.getTranslation(), t.getLeftRotation(), t.getScale(), right));
        }
    }

    boolean valid() { return pieces.stream().allMatch(p -> p.display.isValid()); }
    void applyColor(Integer rgb) {
        for (Piece p : pieces) if (p.kind == Kind.BODY && p.display.isValid()) {
            p.display.setItemStack(model(p.group.name(), rgb));
        }
    }
    void hideWheels() { wheelsVisible = false; refreshWheels(); }
    void setWheels(String name) {
        wheelsVisible = true;
        // Transfer contains sports and standard wheels; no invented off-road asset.
        wheelModel = "sports_wheel".equals(name) ? "wheel_sports" : "wheel_standard";
        refreshWheels();
    }
    void hideEngine() { engineVisible = false; refreshEngine(); }
    void setEngine(String name) {
        engineModel = name.startsWith("gold_") ? "engine_gold" :
                (name.startsWith("diamond_") || name.startsWith("netherite_")) ? "engine_diamond" : "engine_iron";
        engineVisible = true; refreshEngine();
    }
    private void refreshEngine() {
        for (Piece p : pieces) if (p.kind == Kind.ENGINE && p.display.isValid()) {
            String suffix = p.group.name().substring(p.group.name().lastIndexOf("_part_"));
            p.display.setItemStack(engineVisible ? model(engineModel + suffix) : new ItemStack(Material.AIR));
        }
    }
    private void refreshWheels() {
        for (Piece p : pieces) if ((p.kind == Kind.WHEEL) && p.display.isValid()) {
            String suffix = p.group.name().substring(p.group.name().lastIndexOf("_part_"));
            p.display.setItemStack(wheelsVisible ? model(wheelModel + suffix) : new ItemStack(Material.AIR));
        }
    }
}
