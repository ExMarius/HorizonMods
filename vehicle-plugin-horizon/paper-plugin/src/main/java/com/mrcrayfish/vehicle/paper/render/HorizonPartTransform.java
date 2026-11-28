package com.mrcrayfish.vehicle.paper.render;

import org.bukkit.util.Transformation;
import org.joml.Quaternionf;
import org.joml.Vector3f;

/** Pivot-correct item-group transforms; does not itself spawn entities. */
final class HorizonPartTransform {
    private HorizonPartTransform() {}

    /**
     * Coordinates are model pixels, with item centre at (8,8,8). The caller
     * supplies the centre and animation rotation in its own coordinate system.
     * For point q the local result is centre + S*(p + R*(q-p)).
     */
    static Transformation group(Vector3f centre, Vector3f scale, Vector3f originPixels,
                                Quaternionf groupRotation, Quaternionf animationRotation) {
        Vector3f pivot = new Vector3f(originPixels).sub(8.0F, 8.0F, 8.0F).div(16.0F);
        Vector3f rotatedPivot = new Quaternionf(groupRotation).transform(new Vector3f(pivot));
        Vector3f localOffset = pivot.sub(rotatedPivot).mul(scale);
        Vector3f position = new Quaternionf(animationRotation).transform(localOffset).add(centre);
        return new Transformation(position, new Quaternionf(animationRotation), new Vector3f(scale),
                new Quaternionf(groupRotation));
    }
}
