package ro.exmarius.horizonvehicles;

import java.util.List;

/** Planned ports, not a list of vehicles currently available to spawn. */
public final class VehicleCatalog {
    private VehicleCatalog() {}

    public record Entry(String id, String name, String sourceModel) {}

    public static final List<Entry> PLANNED = List.of(
        new Entry("go_kart", "Go-Kart", "go_kart_body"),
        new Entry("off_roader", "Off-Roader", "off_roader_body"),
        new Entry("quad_bike", "Quad Bike", "quad_bike_body"),
        new Entry("atv", "ATV", "atv_body"),
        new Entry("police_car", "Politia Romana Pursuit Sedan", "police_car_body"),
        new Entry("ambulance", "Ambulanta", "ambulance_body"),
        new Entry("smurd", "SMURD", "smurd_body"),
        new Entry("fire_truck", "Pompieri", "fire_truck_body"),
        new Entry("street_coupe", "Street Coupe", "street_coupe_body"),
        new Entry("muscle_car", "Muscle Car", "muscle_car_body"),
        new Entry("supercar", "Supercar", "supercar_body"),
        new Entry("city_suv", "City SUV", "city_suv_body"),
        new Entry("taxi", "Taxi", "taxi_body"),
        new Entry("city_bus", "City Bus (prototip)", "prototype_minibus_body")
    );
}
