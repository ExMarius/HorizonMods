package ro.exmarius.horizonvehicles.vehicle;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

/**
 * Immutable source-space bus layout, loaded from the licensed upstream frame.
 * Coordinates are Automobility texels, NOT calibrated Paper rider positions.
 * Parsing the layout does not spawn or mount any entity.
 */
public record CityBusLayout(List<Seat> seats, List<Wheel> wheels) {
    public record Vec3(double x, double y, double z) {}
    public record Seat(boolean driver, Vec3 sourceTexels) {}
    public record Wheel(String end, String side, double forward, double right, double yaw, double scale) {}

    public CityBusLayout {
        seats = List.copyOf(seats);
        wheels = List.copyOf(wheels);
        if (seats.isEmpty() || seats.stream().filter(Seat::driver).count() != 1) {
            throw new IllegalArgumentException("Exactly one driver seat is required");
        }
        if (wheels.isEmpty()) throw new IllegalArgumentException("At least one wheel is required");
    }

    public static CityBusLayout readBundled() {
        InputStream stream = CityBusLayout.class.getResourceAsStream("/source-assets/city_bus/yellow_bus_frame.json");
        if (stream == null) throw new IllegalStateException("Bundled bus frame is missing");
        try (stream) {
            return read(stream);
        } catch (java.io.IOException exception) {
            throw new IllegalStateException("Unable to close bus frame", exception);
        }
    }

    public static CityBusLayout read(InputStream stream) {
        Objects.requireNonNull(stream, "stream");
        JsonObject root = JsonParser.parseReader(new InputStreamReader(stream, StandardCharsets.UTF_8)).getAsJsonObject();
        JsonObject display = root.getAsJsonObject("display");
        List<Seat> seats = new ArrayList<>();
        seats.add(new Seat(true, vector(display.getAsJsonArray("driver_seat"))));
        for (JsonElement entry : display.getAsJsonArray("passenger_seats")) {
            seats.add(new Seat(false, vector(entry.getAsJsonArray())));
        }
        List<Wheel> wheels = new ArrayList<>();
        for (JsonElement entry : display.getAsJsonArray("wheels")) {
            JsonObject wheel = entry.getAsJsonObject();
            String end = wheel.get("end").getAsString();
            String side = wheel.get("side").getAsString();
            if (!List.of("front", "back", "none").contains(end) || !List.of("left", "right").contains(side)) {
                throw new IllegalArgumentException("Invalid bus wheel placement");
            }
            double scale = finite(wheel.get("scale"));
            if (scale <= 0) throw new IllegalArgumentException("Wheel scale must be positive");
            wheels.add(new Wheel(end, side, finite(wheel.get("forward")), finite(wheel.get("right")),
                    finite(wheel.get("yaw")), scale));
        }
        return new CityBusLayout(seats, wheels);
    }

    private static Vec3 vector(JsonArray values) {
        if (values == null || values.size() != 3) throw new IllegalArgumentException("Expected a 3D position");
        return new Vec3(finite(values.get(0)), finite(values.get(1)), finite(values.get(2)));
    }

    private static double finite(JsonElement value) {
        double number = value.getAsDouble();
        if (!Double.isFinite(number)) throw new IllegalArgumentException("Non-finite bus coordinate");
        return number;
    }
}
