package ro.horizon.vehiclepose;

import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.fml.common.Mod;

@Mod("horizonvehiclepose")
public final class HorizonVehiclePose {
    public HorizonVehiclePose() {
        MinecraftForge.EVENT_BUS.addListener(SeatRendering::beforeRender);
    }
}
