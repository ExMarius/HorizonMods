package com.mrcrayfish.vehicle.paper.recovery;

import com.mrcrayfish.vehicle.paper.render.LandVehicleRig;
import com.mrcrayfish.vehicle.paper.persistence.RecoverySerializedWriter;
import org.bukkit.Bukkit;
import org.bukkit.entity.Entity;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.world.EntitiesLoadEvent;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashSet;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionException;
import java.util.concurrent.atomic.AtomicBoolean;

/** Live listener for retired rig sessions and exact old entity IDs, loaded before
 * vehicles spawn. Recovery transactions do not yet write these files. Never
 * expires IDs: entity.remove() alone doesn't prove the region was saved. A player
 * or an entity carrying passengers is never removed by this guard. */
public final class RecoveredEntityGuard implements Listener, AutoCloseable {
    private static final long MAX_FILE_SIZE = 16L * 100_000 + 16;
    private static final String SESSION_PREFIX = "mcv_session_";
    private final Set<UUID> retiredEntities;
    private final Set<UUID> retiredSessions;
    private final Set<UUID> pendingSessions;
    private final Path sessionFile;
    private final AtomicBoolean failed = new AtomicBoolean();
    private RecoverySerializedWriter writer;
    private boolean closed;

    private RecoveredEntityGuard(Set<UUID> entities, Set<UUID> sessions, Path sessionFile) {
        this.retiredEntities = entities;
        this.retiredSessions = new HashSet<>(sessions);
        this.pendingSessions = new HashSet<>(sessions);
        this.sessionFile = sessionFile;
    }

    public static RecoveredEntityGuard load(Path directory) throws IOException {
        return new RecoveredEntityGuard(read(directory.resolve("recovery-entities.dat")),
                read(directory.resolve("recovery-sessions.dat")), directory.resolve("recovery-sessions.dat"));
    }
    private static Set<UUID> read(Path file) throws IOException {
        if (Files.notExists(file)) return Set.of();
        if (!Files.isRegularFile(file) || Files.size(file) > MAX_FILE_SIZE)
            throw new IOException("Invalid recovery identity registry: " + file.getFileName());
        return RecoveryEntityTombstones.decode(Files.readAllBytes(file));
    }

    /** Queue the complete monotonic session set for durable storage. The future
     * transaction must persist its own recovery journal first, retain all vehicle
     * locks, and call Ticket.publish() on the main thread only after I/O succeeds.
     * No independent writer may modify this file while the guard is running. This
     * primitive is not itself a vehicle/garage transaction. */
    public Ticket prepareRetirement(Set<UUID> sessions) throws IOException {
        requireMain();
        if (closed || failed.get()) throw new IOException("Recovery session writer unavailable");
        if (sessions == null || sessions.isEmpty() || sessions.stream().anyMatch(java.util.Objects::isNull))
            throw new IOException("Missing recovery sessions");
        Set<UUID> snapshot = new HashSet<>(pendingSessions);
        snapshot.addAll(sessions);
        byte[] encoded = RecoveryEntityTombstones.encode(snapshot);
        if (writer == null) writer = new RecoverySerializedWriter(sessionFile);
        CompletableFuture<Void> write = writer.submit(encoded);
        write.whenComplete((unused, error) -> { if (error != null) failed.set(true); });
        pendingSessions.addAll(snapshot);
        return new Ticket(Set.copyOf(snapshot), write);
    }

    public final class Ticket {
        private final Set<UUID> snapshot;
        private final CompletableFuture<Void> write;
        private boolean published;
        private Ticket(Set<UUID> snapshot, CompletableFuture<Void> write) {
            this.snapshot = snapshot; this.write = write;
        }
        public boolean isDone() { return write.isDone(); }
        /** Returns false while the disk write is in flight; never blocks Paper. */
        public boolean publish() throws IOException {
            requireMain();
            if (closed || failed.get()) throw new IOException("Recovery session writer unavailable");
            if (published) return true;
            if (!write.isDone()) return false;
            try { write.join(); }
            catch (CompletionException e) { failed.set(true); throw new IOException("Recovery session write failed", e.getCause()); }
            retiredSessions.addAll(snapshot);
            published = true;
            return true;
        }
    }

    private static void requireMain() {
        if (!Bukkit.isPrimaryThread()) throw new IllegalStateException("Recovery session operation requires main thread");
    }

    /** Flush only during plugin shutdown; gameplay must poll tickets without blocking. */
    @Override public void close() throws IOException {
        requireMain();
        if (closed) return;
        closed = true;
        if (writer != null) writer.close();
    }

    @EventHandler
    public void onEntitiesLoad(EntitiesLoadEvent event) {
        for (Entity entity : event.getEntities()) removeIfRetired(entity);
    }

    /** Also cover entities already loaded before the listener is registered. */
    public void sweepLoaded() {
        if (!Bukkit.isPrimaryThread()) throw new IllegalStateException("Entity sweep requires main thread");
        for (var world : Bukkit.getWorlds()) for (Entity entity : world.getEntities()) removeIfRetired(entity);
    }

    private void removeIfRetired(Entity entity) {
        if (entity instanceof Player || !entity.getScoreboardTags().contains(LandVehicleRig.ENTITY_TAG)
                || !entity.getPassengers().isEmpty()) return;
        boolean retired = retiredEntities.contains(entity.getUniqueId());
        if (!retired) for (String tag : entity.getScoreboardTags()) {
            if (!tag.startsWith(SESSION_PREFIX)) continue;
            try {
                String value = tag.substring(SESSION_PREFIX.length());
                UUID session = UUID.fromString(value);
                if (session.toString().equals(value) && retiredSessions.contains(session)) { retired = true; break; }
            } catch (IllegalArgumentException ignored) { /* Unknown or malformed tag, leave it alone. */ }
        }
        if (retired) entity.remove();
    }
}
