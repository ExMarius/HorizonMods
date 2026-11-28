package com.mrcrayfish.vehicle.paper.runtime;

import com.mrcrayfish.vehicle.paper.render.LandVehicleRig;
import net.kyori.adventure.key.Key;
import net.kyori.adventure.sound.Sound;
import net.kyori.adventure.sound.SoundStop;
import org.bukkit.Bukkit;
import org.bukkit.Location;
import org.bukkit.entity.Player;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

/** Per-vehicle toggle and independently stoppable moving sound. Server main thread only. */
public final class PoliceSiren {
    private static final boolean[] SLOTS = new boolean[16];
    private static final double RANGE_SQUARED = 48.0D * 48.0D;
    // 1,124,352 samples at 44,100 Hz = 25.4955 seconds.
    private static final int SAMPLE_TICKS = 510;
    private final LandVehicleRig rig;
    private final Map<UUID, Integer> listeners = new HashMap<>();
    private int slot = -1;
    public PoliceSiren(LandVehicleRig rig) { this.rig = rig; }
    public boolean enabled() { return slot >= 0; }
    public boolean enable() {
        if (enabled()) return true;
        for (int i=0; i<SLOTS.length; i++) if (!SLOTS[i]) {
            SLOTS[i]=true; slot=i; return true;
        }
        return false;
    }
    private Key key() { return Key.key("daciapolice:sirena_" + slot); }
    public void tick(Location location, int tick, boolean hasDriver) {
        if (!enabled()) return;
        if (!hasDriver || location.getWorld() == null || !rig.valid()) { stop(); return; }
        rig.setPoliceFlash((tick / 4) % 2);
        Set<UUID> nearby = new HashSet<>();
        for (Player player : location.getWorld().getPlayers()) {
            if (player.getLocation().distanceSquared(location) > RANGE_SQUARED) continue;
            UUID id=player.getUniqueId(); nearby.add(id);
            Integer next=listeners.get(id);
            if (next == null || tick - next >= 0) {
                player.playSound(Sound.sound(key(), Sound.Source.NEUTRAL, 1.0F, 1.0F), rig.driverSeat());
                listeners.put(id, tick + SAMPLE_TICKS);
            }
        }
        for (UUID id : new HashSet<>(listeners.keySet())) if (!nearby.contains(id)) {
            Player player=Bukkit.getPlayer(id);
            if (player != null) player.stopSound(SoundStop.namedOnSource(key(), Sound.Source.NEUTRAL));
            listeners.remove(id);
        }
    }
    public void stop() {
        if (!enabled()) return;
        SoundStop stop=SoundStop.namedOnSource(key(), Sound.Source.NEUTRAL);
        for (UUID id : listeners.keySet()) {
            Player player=Bukkit.getPlayer(id);
            if (player != null) player.stopSound(stop);
        }
        listeners.clear(); SLOTS[slot]=false; slot=-1; rig.setPoliceFlash(-1);
    }
}
