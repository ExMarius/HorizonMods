package com.mrcrayfish.vehicle.paper.persistence;

import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.configuration.InvalidConfigurationException;
import org.bukkit.configuration.file.YamlConfiguration;

import java.io.File;
import java.io.IOException;
import java.util.UUID;

/** Strict, read-only sanity check for recovery operations, not a trailer loader.
 * The ordinary loader tolerates bad records; recovery must instead fail closed. */
public final class TrailerRecoveryAudit {
    private TrailerRecoveryAudit() { }

    /** Return the number of records, or -1 when link state cannot be trusted. */
    public static int countTrustedRecords(File file) {
        if (java.nio.file.Files.notExists(file.toPath())) return 0;
        if (!file.isFile()) return -1;
        YamlConfiguration yaml = new YamlConfiguration();
        try {
            yaml.load(file);
            if (!yaml.contains("trailers")) return yaml.getKeys(false).isEmpty() ? 0 : -1;
            ConfigurationSection root = yaml.getConfigurationSection("trailers");
            if (root == null) return -1;
            for (String key : root.getKeys(false)) {
                UUID.fromString(key);
                ConfigurationSection entry = root.getConfigurationSection(key);
                if (entry == null || entry.getString("type", "").isBlank()) return -1;
                UUID.fromString(entry.getString("world", ""));
                String type = entry.getString("puller-type", "");
                String puller = entry.getString("puller-id");
                String loaded = entry.getString("loaded-vehicle-id");
                if (!type.equals("NONE") && !type.equals("PLAYER")
                        && !type.equals("VEHICLE") && !type.equals("TRAILER")) return -1;
                if (type.equals("NONE")) {
                    if (puller != null && !puller.isBlank()) return -1;
                } else {
                    if (puller == null || puller.isBlank()) return -1;
                    UUID.fromString(puller);
                }
                if (loaded != null && !loaded.isBlank()) UUID.fromString(loaded);
            }
            return root.getKeys(false).size();
        } catch (IOException | InvalidConfigurationException | IllegalArgumentException e) {
            return -1;
        }
    }
}
