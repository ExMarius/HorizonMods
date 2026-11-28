package ro.horizon.vehiclepose.mixin;

import net.minecraft.client.model.PlayerModel;
import net.minecraft.client.renderer.entity.state.PlayerRenderState;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import ro.horizon.vehiclepose.SeatRendering;

@Mixin(PlayerModel.class)
public abstract class PlayerModelMixin {
    @Inject(method = "setupAnim(Lnet/minecraft/client/renderer/entity/state/PlayerRenderState;)V", at = @At("TAIL"))
    private void horizon$steeringPose(PlayerRenderState state, CallbackInfo ci) {
        SeatRendering.Seat seat = SeatRendering.seat(state);
        if (seat == null || !seat.driver() || state.isSpectator) return;
        PlayerModel model = (PlayerModel) (Object) this;
        // Starting poses based on MrCrayfish 1.16 renderers. The Paper models
        // have different wheel positions, so these require per-vehicle calibration.
        float pitch = switch (seat.vehicle()) {
            case "go_kart", "horizon_go_kart" -> -65F;
            case "tractor", "utb_650" -> -55F;
            default -> -75F;
        };
        float wheel = seat.steer() * 0.125F;
        model.rightArm.xRot = (float) Math.toRadians(pitch - wheel);
        model.leftArm.xRot = (float) Math.toRadians(pitch + wheel);
        model.rightArm.yRot = (float) Math.toRadians(-7F);
        model.leftArm.yRot = (float) Math.toRadians(7F);
        model.rightArm.zRot = 0F;
        model.leftArm.zRot = 0F;
    }
}
