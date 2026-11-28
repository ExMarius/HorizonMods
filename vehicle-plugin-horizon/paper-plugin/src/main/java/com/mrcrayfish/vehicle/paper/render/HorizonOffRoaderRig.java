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
final class HorizonOffRoaderRig {
    private enum Kind { BODY, WHEEL, STEERING, SPARE }
    private record Piece(ItemDisplay display, HorizonGroups.Group group, Kind kind, int wheel) {}
    private static final float Z = 14.5F * 1.42F / 16F;
    private static final Quaternionf ITEM_YAW = new Quaternionf().rotateY((float)Math.PI);
    private final List<Piece> pieces = new ArrayList<>();
    private boolean wheelsVisible = true;
    private String wheelModel = "wheel_sports";

    HorizonOffRoaderRig(Location location, UUID id, List<Entity> entities) {
        add(location, id, entities, HorizonGroups.OFF_ROADER_BODY, Kind.BODY, -1);
        for (int i=0; i<4; i++) add(location, id, entities, HorizonGroups.WHEEL_SPORTS, Kind.WHEEL, i);
        add(location, id, entities, HorizonGroups.GO_KART_STEERING_WHEEL, Kind.STEERING, -1);
        add(location, id, entities, HorizonGroups.WHEEL_SPORTS, Kind.SPARE, -1);
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

    void update(Location anchor, Vector3f driverSeat, Quaternionf chassis, float steering,
                float frontSpin, float rearSpin, float wheelie, float roll, Vector3f pivot) {
        for (Piece p : pieces) {
            Vector3f center, scale;
            Quaternionf localRotation = new Quaternionf(chassis);
            switch (p.kind) {
                case BODY -> { center = new Vector3f(0, .69F, 0); scale = new Vector3f(1.42F, 1.38F, 1.42F); }
                case WHEEL -> {
                    boolean front = p.wheel < 2;
                    float x = (p.wheel % 2 == 0 ? 1 : -1) * 14.74F / 16F;
                    center = new Vector3f(x, .390F, front ? Z : -Z);
                    scale = new Vector3f(1.55F, 1.56F, 1.56F);
                    // In Paper the boost pitches the body: keep both axles on the
                    // same chassis transform so the wheels do not detach visually.
                    localRotation.rotateY((float)Math.toRadians(front ? steering : 0))
                            .rotateX((float)Math.toRadians(-(front ? frontSpin : rearSpin)));
                }
                case STEERING -> {
                    center = new Vector3f(6.816F / 16F, 17.30F / 16F, 4.45F / 16F);
                    scale = new Vector3f(1.16F);
                    localRotation.rotateX((float)Math.toRadians(32))
                            .rotateZ((float)Math.toRadians(-steering * 1.8F));
                }
                case SPARE -> {
                    center = new Vector3f(0, 14.8F / 16F, -34.6F / 16F);
                    scale = new Vector3f(1.24F, 1.32F, 1.32F);
                    localRotation.rotateY((float)Math.PI / 2);
                }
                default -> throw new IllegalStateException();
            }
            center = SourceTransforms.chassisPoint(center, pivot, wheelie, roll);
            center.sub(driverSeat);
            Transformation t = HorizonPartTransform.group(center, scale, p.group.origin(), p.group.rotation(), localRotation);
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
    private void refreshWheels() {
        for (Piece p : pieces) if ((p.kind == Kind.WHEEL || p.kind == Kind.SPARE) && p.display.isValid()) {
            String suffix = p.group.name().substring(p.group.name().lastIndexOf("_part_"));
            p.display.setItemStack(p.kind == Kind.SPARE || wheelsVisible ? model(wheelModel + suffix) : new ItemStack(Material.AIR));
        }
    }
}
