package com.mrcrayfish.vehicle.paper.render;

import org.joml.Quaternionf;
import org.joml.Vector3f;
import java.util.List;

/** Generated from resources/horizon/off_roader_parts.json; do not edit manually. */
final class HorizonGroups {
    record Group(String name, float x, float y, float z, char axis, float degrees) {
        Vector3f origin() { return new Vector3f(x, y, z); }
        Quaternionf rotation() {
            float r = (float)Math.toRadians(degrees);
            return switch (axis) {
                case 'x' -> new Quaternionf().rotateX(r);
                case 'y' -> new Quaternionf().rotateY(r);
                case 'z' -> new Quaternionf().rotateZ(r);
                default -> new Quaternionf();
            };
        }
    }
    static final List<Group> OFF_ROADER_BODY = List.of(
        new Group("off_roader_body_part_00", 8.0F, 8.0F, 8.0F, 'n', 0.0F),
        new Group("off_roader_body_part_01", 8.0F, 3.9F, 28.5F, 'x', -18.0F),
        new Group("off_roader_body_part_02", 8.0F, 8.25F, 9.6F, 'x', -12.0F),
        new Group("off_roader_body_part_03", 7.0F, 8.25F, 10.85F, 'x', -8.0F),
        new Group("off_roader_body_part_04", 8.0F, 10.05F, 24.95F, 'x', 35.0F),
        new Group("off_roader_body_part_05", 8.0F, 10.05F, 20.05F, 'x', -35.0F),
        new Group("off_roader_body_part_06", 8.0F, 10.05F, -4.05F, 'x', 35.0F),
        new Group("off_roader_body_part_07", 8.0F, 10.05F, -8.95F, 'x', -35.0F),
        new Group("off_roader_body_part_08", 12.8F, 12.54F, 11.13F, 'x', 32.0F),
        new Group("off_roader_body_part_09", 11.7F, 5.45F, 15.2F, 'x', -20.0F),
        new Group("off_roader_body_part_10", 13.9F, 5.45F, 15.2F, 'x', -20.0F),
        new Group("off_roader_body_part_11", 8.0F, 13.5F, 15.4F, 'x', -18.0F),
        new Group("off_roader_body_part_12", 9.2F, 13.7F, 16.18F, 'z', 4.0F),
        new Group("off_roader_body_part_13", 0.2F, 13.7F, 16.18F, 'z', 4.0F),
        new Group("off_roader_body_part_14", 18.7F, 13.0F, -12.0F, 'x', 32.0F),
        new Group("off_roader_body_part_15", -2.7F, 13.0F, -12.0F, 'x', 32.0F),
        new Group("off_roader_body_part_16", 12.8F, 6.72F, 2.4F, 'x', -8.0F),
        new Group("off_roader_body_part_17", 3.2F, 6.72F, 2.4F, 'x', -8.0F)
    );
    static final List<Group> WHEEL_SPORTS = List.of(
        new Group("wheel_sports_part_00", 8.0F, 8.0F, 8.0F, 'n', 0.0F),
        new Group("wheel_sports_part_01", 8.0F, 8.0F, 8.0F, 'x', 67.5F)
    );
    static final List<Group> WHEEL_STANDARD = List.of(
        new Group("wheel_standard_part_00", 8.0F, 8.0F, 8.0F, 'n', 0.0F),
        new Group("wheel_standard_part_01", 8.0F, 8.0F, 8.0F, 'x', 67.5F)
    );
    static final List<Group> GO_KART_STEERING_WHEEL = List.of(
        new Group("go_kart_steering_wheel_part_00", 8.0F, 8.0F, 8.0F, 'n', 0.0F),
        new Group("go_kart_steering_wheel_part_01", 8.0F, 8.0F, 8.0F, 'z', 12.0F),
        new Group("go_kart_steering_wheel_part_02", 8.0F, 8.0F, 8.0F, 'z', -12.0F)
    );
    private HorizonGroups() {}
}
