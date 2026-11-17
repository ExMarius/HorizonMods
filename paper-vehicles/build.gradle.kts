plugins { java }

group = "ro.exmarius"
version = "0.1.0-dev"

repositories {
    mavenCentral()
    maven("https://repo.papermc.io/repository/maven-public/")
    maven("https://jitpack.io")
}

dependencies {
    compileOnly("io.papermc.paper:paper-api:1.21.4-R0.1-SNAPSHOT")
    compileOnly("com.github.MilkBowl:VaultAPI:1.7.1")
    testImplementation("org.junit.jupiter:junit-jupiter:5.11.4")
    testRuntimeOnly("org.junit.platform:junit-platform-launcher")
}

tasks.test { useJUnitPlatform() }

java { toolchain.languageVersion.set(JavaLanguageVersion.of(21)) }
tasks.withType<JavaCompile>().configureEach {
    options.encoding = "UTF-8"
    options.release.set(21)
}
tasks.processResources {
    inputs.property("version", project.version)
    filesMatching("plugin.yml") { expand("version" to project.version) }
    from("LICENSE") { rename { "LICENSE.txt" } }
    from("THIRD-PARTY.md")
    // Bundle the MIT bus sources with the JAR; these are not yet a resource pack.
    from("asset-src/city_bus") {
        into("source-assets/city_bus")
        include("bus.obj", "bus_wheel.obj", "yellow_bus.png", "bus_wheel.png",
                "yellow_bus_frame.json", "LICENSE", "README.md")
    }
}
tasks.jar { archiveBaseName.set("HorizonVehiclesPaper") }
