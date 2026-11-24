package com.mrcrayfish.vehicle.paper.render;

import org.bukkit.util.Transformation;
import org.joml.Quaternionf;
import org.joml.Vector3f;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertEquals;

class HorizonPartTransformTest {
    private static final float EPS = 1.0e-5F;

    @Test void rotationAboutOffsetPivotPrecedesNonUniformScale() {
        Vector3f centre = new Vector3f(0.0F, 0.69F, 0.0F);
        Vector3f scale = new Vector3f(1.42F, 1.38F, 1.42F);
        Vector3f pivotPixels = new Vector3f(8, 3.9F, 28.5F);
        Quaternionf group = new Quaternionf().rotateX((float)Math.toRadians(-18));
        Vector3f point = new Vector3f(.25F, -.3F, .8F);
        Vector3f pivot = new Vector3f(pivotPixels).sub(8, 8, 8).div(16);
        Vector3f expected = new Vector3f(point).sub(pivot);
        group.transform(expected);
        expected.add(pivot).mul(scale).add(centre);
        Transformation t = HorizonPartTransform.group(centre, scale, pivotPixels, group, new Quaternionf());
        assertVector(expected, apply(t, point));
    }

    @Test void parentRotationRotatesBothPivotCorrectionAndGeometry() {
        Vector3f centre = new Vector3f(1, 2, 3), scale = new Vector3f(2, 3, 4);
        Vector3f origin = new Vector3f(10, 12, 14), point = new Vector3f(.5F, .2F, -.7F);
        Quaternionf group = new Quaternionf().rotateZ(.6F);
        Quaternionf parent = new Quaternionf().rotateY(.9F);
        Vector3f pivot = new Vector3f(origin).sub(8,8,8).div(16);
        Vector3f expected = new Vector3f(point).sub(pivot);
        group.transform(expected);
        expected.add(pivot).mul(scale);
        parent.transform(expected);
        expected.add(centre);
        assertVector(expected, apply(HorizonPartTransform.group(centre, scale, origin, group, parent), point));
    }

    @Test void identityLeavesCentreAndScaleIntact() {
        Vector3f centre = new Vector3f(0, .69F, 0), scale = new Vector3f(1.42F,1.38F,1.42F);
        Vector3f point = new Vector3f(.1F,.2F,.3F);
        Vector3f expected = new Vector3f(point).mul(scale).add(centre);
        assertVector(expected, apply(HorizonPartTransform.group(centre, scale, new Vector3f(8,8,8),
                new Quaternionf(), new Quaternionf()), point));
    }

    private static Vector3f apply(Transformation t, Vector3f point) {
        Vector3f v = new Vector3f(point);
        t.getRightRotation().transform(v);
        v.mul(t.getScale());
        t.getLeftRotation().transform(v);
        return v.add(t.getTranslation());
    }
    private static void assertVector(Vector3f a, Vector3f b) {
        assertEquals(a.x, b.x, EPS); assertEquals(a.y, b.y, EPS); assertEquals(a.z, b.z, EPS);
    }
}
