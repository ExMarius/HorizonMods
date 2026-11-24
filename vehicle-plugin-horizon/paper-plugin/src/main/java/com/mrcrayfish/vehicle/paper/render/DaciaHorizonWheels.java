package com.mrcrayfish.vehicle.paper.render;

import com.mrcrayfish.vehicle.paper.vehicle.LandVehicleSpec;
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

/** The exact multipart Horizon Off-Roader wheels, driven by the Dacia's own axles. */
final class DaciaHorizonWheels {
    private record Piece(ItemDisplay display, HorizonGroups.Group group, LandVehicleSpec.Wheel wheel) {}
    private final List<Piece> pieces = new ArrayList<>();
    private boolean visible = true;
    private String model = "wheel_sports";

    DaciaHorizonWheels(Location location, UUID id, List<Entity> all, LandVehicleSpec spec) {
        for (LandVehicleSpec.Wheel wheel : spec.wheels()) for (HorizonGroups.Group group : HorizonGroups.WHEEL_STANDARD) {
            ItemDisplay display = location.getWorld().spawn(location, ItemDisplay.class, d -> {
                d.setItemStack(stack(group.name().replace("wheel_standard", "wheel_sports")));
                d.setItemDisplayTransform(ItemDisplay.ItemDisplayTransform.NONE);
                d.setInterpolationDelay(0); d.setInterpolationDuration(1); d.setTeleportDuration(3);
                d.setInvulnerable(true); d.setPersistent(false); d.setShadowRadius(0); d.setShadowStrength(0);
            });
            display.addScoreboardTag(LandVehicleRig.ENTITY_TAG);
            display.addScoreboardTag("mcv_" + id); all.add(display);
            pieces.add(new Piece(display, group, wheel));
        }
    }
    private static ItemStack stack(String name) {
        ItemStack stack = new ItemStack(Material.LEATHER_HORSE_ARMOR);
        LeatherArmorMeta meta = (LeatherArmorMeta) stack.getItemMeta();
        meta.setItemModel(new NamespacedKey("horizonvehicles", name));
        meta.setColor(Color.fromRGB(0xFFFFFF)); stack.setItemMeta(meta); return stack;
    }
    void setModel(String name) {
        visible = "standard_wheel".equals(name) || "sports_wheel".equals(name);
        // Both stock and sports tires use the accepted Horizon Off-Roader look.
        model = "wheel_sports";
        refresh();
    }
    void hide() { visible = false; refresh(); }
    private void refresh() {
        for (Piece p : pieces) if (p.display().isValid()) {
            String name = p.group().name().replace("wheel_standard", model);
            p.display().setItemStack(visible ? stack(name) : new ItemStack(Material.AIR));
        }
    }
    boolean handles(String name) { return "standard_wheel".equals(name) || "sports_wheel".equals(name); }
    boolean valid() { return pieces.stream().allMatch(p -> p.display().isValid()); }
    static Vector3f visualCenter(LandVehicleSpec.Wheel w, float angle) {
        float visualOffset = w.halfWidthOffset();
        return new Vector3f(w.axleX() + visualOffset * (float)Math.cos(angle), w.centerY(),
                w.axleZ() - visualOffset * (float)Math.sin(angle));
    }
    // Mirror the assembled group, not each raw group before its rotation.
    // Otherwise the 67.5-degree tire segment turns the opposite way from the
    // baked 22.5/45-degree segments on one side and overlaps an existing spoke.
    static Quaternionf wheelGroupRotation(Quaternionf groupRotation, int side) {
        Quaternionf itemYaw = new Quaternionf();
        if (side < 0) itemYaw.rotateY((float)Math.PI);
        return itemYaw.mul(groupRotation);
    }
    void update(Location anchor, Vector3f driverSeat, Quaternionf chassis, Vector3f pivot,
                float steer, float frontSpin, float rearSpin, float wheelie, float roll) {
        for (Piece p : pieces) {
            LandVehicleSpec.Wheel w=p.wheel();
            float angle=(float)Math.toRadians(w.front() ? steer : 0.0F);
            Vector3f center=visualCenter(w, angle);
            center=SourceTransforms.chassisPoint(center, pivot, wheelie, roll).sub(driverSeat);
            Quaternionf animation=new Quaternionf(chassis).rotateY(angle)
                    .rotateX((float)Math.toRadians(-(w.front() ? frontSpin : rearSpin)));
            Transformation t=HorizonPartTransform.group(center,new Vector3f(w.scaleX(),w.scaleY(),w.scaleZ()),
                    p.group().origin(),p.group().rotation(),animation);
            Quaternionf right=wheelGroupRotation(t.getRightRotation(), w.side());
            p.display().teleport(anchor, TeleportFlag.EntityState.RETAIN_PASSENGERS);
            p.display().setRotation(anchor.getYaw(),0);
            p.display().setTransformation(new Transformation(t.getTranslation(),t.getLeftRotation(),t.getScale(),right));
        }
    }
}
