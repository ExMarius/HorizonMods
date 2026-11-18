package ro.exmarius.horizonvehicles.kart;

import java.util.ArrayList;
import java.util.List;
import org.bukkit.Location;
import org.bukkit.Material;
import org.bukkit.entity.BlockDisplay;
import org.bukkit.util.Transformation;
import org.joml.Quaternionf;
import org.joml.Vector3f;

/** Optional cosmetic glove/forearm approximation, not the player's animated skin. */
final class GoKartHands {
    private record Segment(BlockDisplay entity, Vector3f translation, Quaternionf rotation, Vector3f scale) { }
    private final List<Segment> segments = new ArrayList<>();
    private boolean visible;

    static GoKartHands spawn(Location root) {
        GoKartHands hands = new GoKartHands();
        try {
            for (int side : new int[]{-1, 1}) {
                // Endpoints are in kart-local blocks; grip is beside the source wheel center.
                Vector3f shoulder = new Vector3f(side * .31f, 1.16f, -.09f);
                Vector3f wrist = new Vector3f(side * .19f, .71f, .42f);
                Vector3f grip = new Vector3f(side * .19f, .70f, .51f);
                hands.segment(root, shoulder, wrist, .105f, Material.BLUE_TERRACOTTA);
                hands.segment(root, wrist, grip, .12f, Material.ORANGE_TERRACOTTA);
            }
            hands.move(root);
            return hands;
        } catch (RuntimeException error) {
            hands.remove();
            throw error;
        }
    }

    private void segment(Location root, Vector3f start, Vector3f end, float width, Material material) {
        Vector3f delta = new Vector3f(end).sub(start);
        float length = delta.length();
        Quaternionf rotation = new Quaternionf().rotationTo(0, 1, 0, delta.x / length, delta.y / length, delta.z / length);
        // BlockDisplay renders a block from 0..1; center its width on the segment.
        Vector3f translation = new Vector3f(start).sub(rotation.transform(new Vector3f(width / 2, 0, width / 2)));
        BlockDisplay display = root.getWorld().spawn(root, BlockDisplay.class, entity -> {
            entity.setBlock(material.createBlockData());
            entity.setVisibleByDefault(false);
            entity.setInterpolationDelay(0);
            entity.setInterpolationDuration(1);
            entity.setTeleportDuration(1);
            entity.setPersistent(false);
            entity.setInvulnerable(true);
            entity.setShadowRadius(0);
        });
        segments.add(new Segment(display, translation, rotation, new Vector3f(width, length, width)));
    }

    void setOccupied(boolean occupied) {
        if (visible == occupied) return;
        visible = occupied;
        segments.forEach(segment -> segment.entity().setVisibleByDefault(occupied));
    }

    void move(Location root) {
        for (Segment segment : segments) {
            segment.entity().teleport(root);
            segment.entity().setRotation(root.getYaw(), 0);
            segment.entity().setTransformation(new Transformation(segment.translation(), segment.rotation(), segment.scale(), new Quaternionf()));
        }
    }

    void remove() { segments.forEach(segment -> segment.entity().remove()); segments.clear(); }
}
