package ro.horizon.vehiclepose;

import net.minecraft.client.Minecraft;
import net.minecraft.client.player.AbstractClientPlayer;
import net.minecraft.client.renderer.entity.state.PlayerRenderState;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.animal.Pig;
import net.minecraftforge.client.event.RenderPlayerEvent;

/** Client-only presentation. The marker is cosmetic metadata, not authorization. */
public final class SeatRendering {
    private static final String PREFIX = "horizon-seat-v1|";
    private SeatRendering() {}

    public record Seat(String vehicle, boolean driver, int steer) {}

    public static Seat seat(PlayerRenderState state) {
        Minecraft minecraft = Minecraft.getInstance();
        if (minecraft.level == null) return null;
        Entity entity = minecraft.level.getEntity(state.id);
        if (!(entity instanceof AbstractClientPlayer player) || !(player.getVehicle() instanceof Pig pig)) return null;
        var name = pig.getCustomName();
        if (name == null) return null;
        String value = name.getString();
        if (!value.startsWith(PREFIX)) return null;
        String[] fields = value.substring(PREFIX.length()).split("\\|", -1);
        if (fields.length != 3 || !fields[0].matches("[a-z0-9_]{1,64}")
                || !(fields[1].equals("d") || fields[1].equals("p"))) return null;
        try {
            int steer = Integer.parseInt(fields[2]);
            if (steer < -100 || steer > 100) return null;
            return new Seat(fields[0], fields[1].equals("d"), steer);
        } catch (NumberFormatException ignored) { return null; }
    }

    public static void beforeRender(RenderPlayerEvent.Pre event) {
        PlayerRenderState state = event.getState();
        if (seat(state) == null) return;
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null || !(mc.level.getEntity(state.id) instanceof AbstractClientPlayer player)
                || !(player.getVehicle() instanceof Pig pig)) return;
        float partial = mc.getDeltaTracker().getGameTimeDeltaPartialTick(false);
        float yaw = Mth.rotLerp(partial, pig.yRotO, pig.getYRot());
        float headYaw = Mth.rotLerp(partial, player.yHeadRotO, player.yHeadRot);
        state.bodyRot = yaw;
        // Preserve independent look without allowing the rendered neck to twist 360 degrees.
        // This does not change player yaw or camera movement.
        state.yRot = Mth.clamp(Mth.wrapDegrees(headYaw - yaw), -85F, 85F);
    }
}
