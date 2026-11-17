package ro.exmarius.horizonvehicles.kart;

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import com.mrcrayfish.vehicle.paper.vehicle.LandVehicleSpec;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;
import org.bukkit.Color;
import org.bukkit.Location;
import org.bukkit.Material;
import org.bukkit.NamespacedKey;
import org.bukkit.entity.ItemDisplay;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.meta.LeatherArmorMeta;
import org.bukkit.plugin.java.JavaPlugin;
import org.bukkit.util.Transformation;
import org.joml.Quaternionf;
import org.joml.Vector3f;

/** Split-model renderer using the Paper source Go-Kart layout. */
public final class GoKartRig {
    private record Piece(ItemDisplay display, Vector3f offset, Quaternionf outerRotation, Quaternionf rotation, Vector3f scale) { }
    private final List<Piece> pieces = new ArrayList<>();

    private GoKartRig() { }

    public static GoKartRig spawn(JavaPlugin plugin, Location location) throws Exception {
        JsonObject descriptor = readDescriptor(plugin).getAsJsonObject("parts");
        GoKartRig rig = new GoKartRig();
        try {
            LandVehicleSpec spec = LandVehicleSpec.GO_KART;
            rig.add(descriptor, "go_kart_body", location, point(spec.bodyOrigin()),
                    new Vector3f(spec.bodyScale()), new Quaternionf());
            for (LandVehicleSpec.Wheel wheel : spec.wheels()) {
                Vector3f center = new Vector3f(wheel.axleX() + wheel.halfWidthOffset(),
                        wheel.centerY(), wheel.axleZ());
                Quaternionf orientation = new Quaternionf();
                if (wheel.side() > 0) orientation.rotateY((float) Math.PI);
                rig.add(descriptor, "wheel_standard", location, center,
                        new Vector3f(wheel.scaleX(), wheel.scaleY(), wheel.scaleZ()), orientation);
            }
            LandVehicleSpec.Part engine = spec.engine();
            rig.add(descriptor, "engine_iron", location, point(engine.center()),
                    new Vector3f(engine.scale()), rotation(engine));
            LandVehicleSpec.Part steering = spec.steering();
            rig.add(descriptor, "go_kart_steering_wheel", location, point(steering.center()),
                    new Vector3f(steering.scale()), rotation(steering));
            rig.move(location);
            return rig;
        } catch (Exception error) {
            rig.remove();
            throw error;
        }
    }

    private static JsonObject readDescriptor(JavaPlugin plugin) throws Exception {
        InputStream resource = plugin.getResource("resource-packs/go-kart-experimental.zip");
        if (resource == null) throw new IllegalStateException("Go-Kart pack missing from JAR");
        try (ZipInputStream zip = new ZipInputStream(resource)) {
            ZipEntry entry;
            while ((entry = zip.getNextEntry()) != null) {
                if (entry.getName().equals("go_kart_parts.json")) {
                    return JsonParser.parseReader(new InputStreamReader(zip, StandardCharsets.UTF_8)).getAsJsonObject();
                }
            }
        }
        throw new IllegalStateException("Go-Kart pack descriptor missing");
    }

    private static Vector3f point(LandVehicleSpec.Point point) {
        return new Vector3f(point.x(), point.y(), point.z());
    }

    private static Quaternionf rotation(LandVehicleSpec.Part part) {
        return new Quaternionf().rotateX((float) Math.toRadians(part.rotationX()))
                .rotateY((float) Math.toRadians(part.rotationY()))
                .rotateZ((float) Math.toRadians(part.rotationZ()));
    }

    private void add(JsonObject descriptor, String name, Location location, Vector3f offset,
                     Vector3f scale, Quaternionf outerRotation) {
        for (var element : descriptor.getAsJsonArray(name)) {
            JsonObject part = element.getAsJsonObject();
            String model = part.get("item_model").getAsString();
            Quaternionf rotation = new Quaternionf();
            Vector3f shift = new Vector3f();
            if (!part.get("rotation").isJsonNull()) {
                JsonObject r = part.getAsJsonObject("rotation");
                var origin = r.getAsJsonArray("origin");
                Vector3f pivot = new Vector3f(origin.get(0).getAsFloat() - 8, origin.get(1).getAsFloat() - 8, origin.get(2).getAsFloat() - 8).div(16);
                float angle = (float) Math.toRadians(r.get("angle").getAsFloat());
                switch (r.get("axis").getAsString()) {
                    case "x" -> rotation.rotateX(angle);
                    case "y" -> rotation.rotateY(angle);
                    case "z" -> rotation.rotateZ(angle);
                    default -> throw new IllegalArgumentException("Invalid model rotation axis");
                }
                shift.set(pivot).sub(rotation.transform(new Vector3f(pivot))).mul(scale);
            }
            outerRotation.transform(shift);
            ItemStack stack = new ItemStack(Material.LEATHER_HORSE_ARMOR);
            LeatherArmorMeta meta = (LeatherArmorMeta) stack.getItemMeta();
            meta.setItemModel(NamespacedKey.fromString(model));
            meta.setColor(Color.WHITE);
            stack.setItemMeta(meta);
            ItemDisplay display = location.getWorld().spawn(location, ItemDisplay.class, entity -> {
                entity.setItemStack(stack);
                entity.setItemDisplayTransform(ItemDisplay.ItemDisplayTransform.NONE);
                entity.setInterpolationDelay(0);
                entity.setInterpolationDuration(1);
                entity.setTeleportDuration(1);
                entity.setPersistent(false);
                entity.setInvulnerable(true);
                entity.setShadowRadius(0);
            });
            pieces.add(new Piece(display, new Vector3f(offset).add(shift), new Quaternionf(outerRotation), rotation, new Vector3f(scale)));
        }
    }

    /** Root location is the ground-level center; yaw follows Bukkit conventions. */
    public void move(Location root) {
        for (Piece piece : pieces) {
            piece.display().teleport(root);
            piece.display().setRotation(root.getYaw(), 0);
            // Vanilla item displays face opposite to the entity; compensate by 180 degrees.
            piece.display().setTransformation(new Transformation(piece.offset(), piece.outerRotation(), piece.scale(),
                    new Quaternionf(piece.rotation()).rotateY((float) Math.PI)));
        }
    }

    public void remove() {
        pieces.forEach(piece -> piece.display().remove());
        pieces.clear();
    }
}
