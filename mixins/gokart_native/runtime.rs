// Pure-Rust rules, physics, tuning, fuel, persistence, and network codecs for
// the Horizon Go-Kart mod (`gokart`), inspired by MrCrayfish's Vehicle Mod.
//
// This module intentionally depends only on `std` so it can be unit-tested
// standalone via `cargo test` as well as compiled directly into `horizon-client`
// as `crate::game::gokart`.

use std::collections::BTreeMap;

pub const ID: &str = "gokart";
pub const MIXIN_ID: &str = "gokart_native";
pub const VERSION: &str = "0.3.0";
pub const DESCRIPTION: &str = "Driveable 3D Go-Kart inspired by MrCrayfish's Vehicle Mod: Iron/Gold/Diamond engines, Standard/Sports/Racing wheels, 16-color dye painting, drift + turbo boost, fuel & tuning garage.";
pub const SAVE_DIR: &str = "gokart";
pub const SAVE_FILE: &str = "karts.txt";
pub const CLIENT_CONFIG_FILE: &str = "gokart-client.toml";
pub const SERVER_CONFIG_FILE: &str = "gokart-server.toml";

/// Entity tag attached to every summoned backing `minecraft:pig` that represents a Go-Kart.
pub const ENTITY_TAG: &str = "gokart_vehicle";

// Custom items
pub const ITEM_GO_KART: &str = "gokart:go_kart";
pub const ITEM_ENGINE_IRON: &str = "gokart:small_engine_iron";
pub const ITEM_ENGINE_GOLD: &str = "gokart:small_engine_gold";
pub const ITEM_ENGINE_DIAMOND: &str = "gokart:small_engine_diamond";
pub const ITEM_WHEEL_STANDARD: &str = "gokart:standard_wheel";
pub const ITEM_WHEEL_SPORTS: &str = "gokart:sports_wheel";
pub const ITEM_WHEEL_RACING: &str = "gokart:racing_wheel";
pub const ITEM_WRENCH: &str = "gokart:wrench";
pub const ITEM_JERRY_CAN: &str = "gokart:jerry_can";

// Custom item data components
pub const COMP_KART_DATA: &str = "gokart:kart_data";
pub const COMP_JERRY_FUEL: &str = "gokart:jerry_fuel";

// Standalone 3D block models baked via `native_standalone_models`
pub const MODEL_BODY: &str = "gokart:block/go_kart_body";
pub const MODEL_STEERING: &str = "gokart:block/go_kart_steering_wheel";
pub const MODEL_WHEEL_STANDARD: &str = "gokart:block/wheel_standard";
pub const MODEL_WHEEL_SPORTS: &str = "gokart:block/wheel_sports";
pub const MODEL_WHEEL_RACING: &str = "gokart:block/wheel_racing";
pub const MODEL_ENGINE_IRON: &str = "gokart:block/engine_iron";
pub const MODEL_ENGINE_GOLD: &str = "gokart:block/engine_gold";
pub const MODEL_ENGINE_DIAMOND: &str = "gokart:block/engine_diamond";

pub const STANDALONE_MODELS: [&str; 8] = [
    MODEL_BODY,
    MODEL_STEERING,
    MODEL_WHEEL_STANDARD,
    MODEL_WHEEL_SPORTS,
    MODEL_WHEEL_RACING,
    MODEL_ENGINE_IRON,
    MODEL_ENGINE_GOLD,
    MODEL_ENGINE_DIAMOND,
];

// Mod network channels
pub const CHAN_INPUT: &str = "gokart:input";
pub const CHAN_ACTION: &str = "gokart:action";
pub const CHAN_SYNC: &str = "gokart:sync";

// Fuel capacities (millibuckets)
pub const KART_MAX_FUEL_MB: u32 = 2_000;
pub const JERRY_MAX_FUEL_MB: u32 = 5_000;
pub const JERRY_DEFAULT_FUEL_MB: u32 = 2_500;

// Horizon Sprint Kart unified spatial geometry (in blocks; 16 texels = 1.0 block,
// origin (0, 0, 0) = road surface directly beneath entity center; +X left, +Y up, +Z forward)
pub const FRONT_AXLE_Z: f32 = 13.0 / 16.0;       // +0.8125 b
pub const REAR_AXLE_Z: f32 = -11.0 / 16.0;       // -0.6875 b
pub const WHEELBASE: f32 = FRONT_AXLE_Z - REAR_AXLE_Z; // 1.5000 b
pub const FRONT_TRACK_HALF_X: f32 = 10.5 / 16.0; // ±0.65625 b
pub const REAR_TRACK_HALF_X: f32 = 11.6 / 16.0;  // ±0.72500 b (staggered wider rear track!)
pub const FRONT_HUB_Y: f32 = 0.196_875;          // (3.5 / 16) * 0.90 -> tire bottom at Y = 0.000
pub const REAR_HUB_Y: f32 = 0.218_75;            // (3.5 / 16) * 1.00 -> tire bottom at Y = 0.000
pub const FRONT_WHEEL_SCALE: [f32; 3] = [0.88, 0.90, 0.90];
pub const REAR_WHEEL_SCALE: [f32; 3] = [1.16, 1.00, 1.00];
pub const STEER_PIVOT: [f32; 3] = [0.0, 9.1 / 16.0, 3.6 / 16.0];
pub const STEER_TILT_DEG: f32 = 35.0;
pub const STEER_SCALE: [f32; 3] = [0.86, 0.86, 0.86];
pub const ENGINE_PIVOT: [f32; 3] = [0.0, 7.6 / 16.0, -11.4 / 16.0];
pub const ENGINE_SCALE: [f32; 3] = [0.95, 0.95, 0.95];
pub const EXHAUST_OFFSET_Z: f32 = -18.5 / 16.0;
pub const EXHAUST_HEIGHT_Y: f32 = 0.48;
pub const SEAT_ATTACH_Y: f32 = 4.20 / 16.0;      // 0.2625 b (flush on bucket seat cushion!)
pub const SEAT_OFFSET_Z: f32 = -3.0 / 16.0;      // -0.1875 b (flush against contoured backrest!)
pub const MAX_STEER_DEG: f32 = 26.0;
pub const STEP_HEIGHT: f64 = 0.625;
pub const DEFAULT_CAMERA_DISTANCE: f32 = 4.0;

// Client -> Server action codes (`CHAN_ACTION`)
pub const ACT_HORN: u8 = 1;
pub const ACT_PICKUP_KART: u8 = 2;
pub const ACT_EJECT_ENGINE: u8 = 3;
pub const ACT_REFUEL_INV: u8 = 4;
pub const ACT_TOGGLE_FUEL_RULE: u8 = 5;

// ---------------------------------------------------------------------------
// Engine Tiers
// ---------------------------------------------------------------------------

#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub enum EngineTier {
    None,
    #[default]
    Iron,
    Gold,
    Diamond,
}

impl EngineTier {
    pub fn code(self) -> u8 {
        match self {
            Self::None => 0,
            Self::Iron => 1,
            Self::Gold => 2,
            Self::Diamond => 3,
        }
    }

    pub fn from_code(code: u8) -> Self {
        match code {
            0 => Self::None,
            2 => Self::Gold,
            3 => Self::Diamond,
            _ => Self::Iron,
        }
    }

    pub fn slug(self) -> &'static str {
        match self {
            Self::None => "none",
            Self::Iron => "iron",
            Self::Gold => "gold",
            Self::Diamond => "diamond",
        }
    }

    pub fn from_slug(s: &str) -> Self {
        match s.trim() {
            "none" => Self::None,
            "gold" => Self::Gold,
            "diamond" => Self::Diamond,
            _ => Self::Iron,
        }
    }

    pub fn from_item(item: &str) -> Option<Self> {
        match item {
            ITEM_ENGINE_IRON => Some(Self::Iron),
            ITEM_ENGINE_GOLD => Some(Self::Gold),
            ITEM_ENGINE_DIAMOND => Some(Self::Diamond),
            _ => None,
        }
    }

    pub fn item_id(self) -> Option<&'static str> {
        match self {
            Self::None => None,
            Self::Iron => Some(ITEM_ENGINE_IRON),
            Self::Gold => Some(ITEM_ENGINE_GOLD),
            Self::Diamond => Some(ITEM_ENGINE_DIAMOND),
        }
    }

    pub fn model_id(self) -> Option<&'static str> {
        match self {
            Self::None => None,
            Self::Iron => Some(MODEL_ENGINE_IRON),
            Self::Gold => Some(MODEL_ENGINE_GOLD),
            Self::Diamond => Some(MODEL_ENGINE_DIAMOND),
        }
    }

    pub fn lang_key(self) -> &'static str {
        match self {
            Self::None => "gokart.engine.none",
            Self::Iron => "gokart.engine.iron",
            Self::Gold => "gokart.engine.gold",
            Self::Diamond => "gokart.engine.diamond",
        }
    }

    /// Top speed on flat standard road in blocks/tick (20 ticks/sec).
    /// Iron = 14.5 m/s (52.2 km/h), Gold = 17.8 m/s (64.1 km/h), Diamond = 21.2 m/s (76.3 km/h).
    pub fn max_speed_bps(self) -> f32 {
        match self {
            Self::None => 0.0,
            Self::Iron => 0.725,
            Self::Gold => 0.890,
            Self::Diamond => 1.060,
        }
    }

    /// Base forward acceleration in blocks/tick^2.
    pub fn acceleration(self) -> f32 {
        match self {
            Self::None => 0.0,
            Self::Iron => 0.052,
            Self::Gold => 0.068,
            Self::Diamond => 0.082,
        }
    }

    /// Fuel consumed per powered tick (fractional millibuckets accumulated).
    pub fn fuel_burn_per_tick(self) -> f32 {
        match self {
            Self::None => 0.0,
            Self::Iron => 0.50,
            Self::Gold => 0.55,
            Self::Diamond => 0.42,
        }
    }

    /// Audio pitch range `(idle_pitch, redline_pitch)`.
    pub fn pitch_range(self) -> (f32, f32) {
        match self {
            Self::None => (0.85, 1.0),
            Self::Iron => (0.90, 1.75),
            Self::Gold => (0.96, 1.90),
            Self::Diamond => (1.02, 2.05),
        }
    }
}

// ---------------------------------------------------------------------------
// Wheel Types & Surface Grip
// ---------------------------------------------------------------------------

#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub enum WheelType {
    #[default]
    Standard,
    Sports,
    Racing,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum SurfaceKind {
    Road,
    Dirt,
    Loose,
    Ice,
}

impl SurfaceKind {
    pub fn from_block_name(block: &str) -> Self {
        let path = block.strip_prefix("minecraft:").unwrap_or(block);
        if path.contains("ice") {
            Self::Ice
        } else if path.contains("sand")
            || path.contains("gravel")
            || path.contains("snow")
            || path.contains("powder")
            || (path.contains("mud") && !path.contains("brick"))
        {
            Self::Loose
        } else if path.contains("concrete")
            || path.contains("stone")
            || path.contains("brick")
            || path.contains("deepslate")
            || path.contains("andesite")
            || path.contains("diorite")
            || path.contains("granite")
            || path.contains("quartz")
            || path.contains("basalt")
            || path.contains("terracotta")
            || path.contains("purpur")
            || path.contains("copper")
            || path.contains("iron_block")
        {
            Self::Road
        } else {
            Self::Dirt
        }
    }
}

impl WheelType {
    pub fn code(self) -> u8 {
        match self {
            Self::Standard => 0,
            Self::Sports => 1,
            Self::Racing => 2,
        }
    }

    pub fn from_code(code: u8) -> Self {
        match code {
            1 => Self::Sports,
            2 => Self::Racing,
            _ => Self::Standard,
        }
    }

    pub fn slug(self) -> &'static str {
        match self {
            Self::Standard => "standard",
            Self::Sports => "sports",
            Self::Racing => "racing",
        }
    }

    pub fn from_slug(s: &str) -> Self {
        match s.trim() {
            "sports" => Self::Sports,
            "racing" => Self::Racing,
            _ => Self::Standard,
        }
    }

    pub fn from_item(item: &str) -> Option<Self> {
        match item {
            ITEM_WHEEL_STANDARD => Some(Self::Standard),
            ITEM_WHEEL_SPORTS => Some(Self::Sports),
            ITEM_WHEEL_RACING => Some(Self::Racing),
            _ => None,
        }
    }

    pub fn item_id(self) -> &'static str {
        match self {
            Self::Standard => ITEM_WHEEL_STANDARD,
            Self::Sports => ITEM_WHEEL_SPORTS,
            Self::Racing => ITEM_WHEEL_RACING,
        }
    }

    pub fn model_id(self) -> &'static str {
        match self {
            Self::Standard => MODEL_WHEEL_STANDARD,
            Self::Sports => MODEL_WHEEL_SPORTS,
            Self::Racing => MODEL_WHEEL_RACING,
        }
    }

    pub fn lang_key(self) -> &'static str {
        match self {
            Self::Standard => "gokart.wheel.standard",
            Self::Sports => "gokart.wheel.sports",
            Self::Racing => "gokart.wheel.racing",
        }
    }

    /// Speed multiplier on a given surface.
    pub fn surface_speed_factor(self, surface: SurfaceKind) -> f32 {
        match (self, surface) {
            (Self::Standard, SurfaceKind::Road) => 1.00,
            (Self::Standard, SurfaceKind::Dirt) => 0.90,
            (Self::Standard, SurfaceKind::Loose) => 0.74,
            (Self::Standard, SurfaceKind::Ice) => 0.88,

            (Self::Sports, SurfaceKind::Road) => 1.05,
            (Self::Sports, SurfaceKind::Dirt) => 0.96,
            (Self::Sports, SurfaceKind::Loose) => 0.82,
            (Self::Sports, SurfaceKind::Ice) => 0.92,

            (Self::Racing, SurfaceKind::Road) => 1.12,
            (Self::Racing, SurfaceKind::Dirt) => 0.86,
            (Self::Racing, SurfaceKind::Loose) => 0.66,
            (Self::Racing, SurfaceKind::Ice) => 0.82,
        }
    }

    /// Lateral tire traction (`0.0` = pure ice slide, `1.0` = instant rail lock).
    pub fn lateral_grip(self, surface: SurfaceKind, drifting: bool) -> f32 {
        if surface == SurfaceKind::Ice {
            return if drifting { 0.04 } else { 0.12 };
        }
        if drifting {
            return match self {
                Self::Standard => 0.11,
                Self::Sports => 0.14,
                Self::Racing => 0.16,
            };
        }
        match (self, surface) {
            (Self::Standard, SurfaceKind::Loose) => 0.36,
            (Self::Standard, _) => 0.58,
            (Self::Sports, SurfaceKind::Loose) => 0.44,
            (Self::Sports, _) => 0.70,
            (Self::Racing, SurfaceKind::Road) => 0.82,
            (Self::Racing, SurfaceKind::Dirt) => 0.54,
            (Self::Racing, SurfaceKind::Loose) => 0.32,
            (_, SurfaceKind::Ice) => 0.12,
        }
    }

    pub fn steer_rate_deg(self) -> f32 {
        match self {
            Self::Standard => 4.2,
            Self::Sports => 5.0,
            Self::Racing => 5.6,
        }
    }

    pub fn boost_charge_multiplier(self) -> f32 {
        match self {
            Self::Standard => 1.00,
            Self::Sports => 1.12,
            Self::Racing => 1.25,
        }
    }
}

// ---------------------------------------------------------------------------
// 16 Minecraft Dye Paint Colors
// ---------------------------------------------------------------------------

#[derive(Clone, Copy, Debug, Default, PartialEq, Eq)]
pub enum PaintColor {
    White,
    Orange,
    Magenta,
    LightBlue,
    Yellow,
    Lime,
    Pink,
    Gray,
    LightGray,
    Cyan,
    Purple,
    Blue,
    Brown,
    Green,
    #[default]
    Red,
    Black,
}

impl PaintColor {
    pub const ALL: [Self; 16] = [
        Self::White,
        Self::Orange,
        Self::Magenta,
        Self::LightBlue,
        Self::Yellow,
        Self::Lime,
        Self::Pink,
        Self::Gray,
        Self::LightGray,
        Self::Cyan,
        Self::Purple,
        Self::Blue,
        Self::Brown,
        Self::Green,
        Self::Red,
        Self::Black,
    ];

    pub fn code(self) -> u8 {
        self as u8
    }

    pub fn from_code(code: u8) -> Self {
        Self::ALL.get(code as usize).copied().unwrap_or(Self::Red)
    }

    pub fn slug(self) -> &'static str {
        match self {
            Self::White => "white",
            Self::Orange => "orange",
            Self::Magenta => "magenta",
            Self::LightBlue => "light_blue",
            Self::Yellow => "yellow",
            Self::Lime => "lime",
            Self::Pink => "pink",
            Self::Gray => "gray",
            Self::LightGray => "light_gray",
            Self::Cyan => "cyan",
            Self::Purple => "purple",
            Self::Blue => "blue",
            Self::Brown => "brown",
            Self::Green => "green",
            Self::Red => "red",
            Self::Black => "black",
        }
    }

    pub fn from_slug(s: &str) -> Self {
        let clean = s.trim().to_ascii_lowercase();
        Self::ALL
            .into_iter()
            .find(|c| c.slug() == clean)
            .unwrap_or(Self::Red)
    }

    pub fn from_dye_item(item: &str) -> Option<Self> {
        let path = item.strip_prefix("minecraft:")?;
        let color = path.strip_suffix("_dye")?;
        Self::ALL.into_iter().find(|c| c.slug() == color)
    }

    pub fn rgb(self) -> u32 {
        match self {
            Self::White => 0xF4F6F8,
            Self::Orange => 0xF07618,
            Self::Magenta => 0xC846B8,
            Self::LightBlue => 0x3AAFD9,
            Self::Yellow => 0xF8C628,
            Self::Lime => 0x70C926,
            Self::Pink => 0xED80A6,
            Self::Gray => 0x464C54,
            Self::LightGray => 0xA2A8B0,
            Self::Cyan => 0x189C9D,
            Self::Purple => 0x8432B8,
            Self::Blue => 0x2E54C4,
            Self::Brown => 0x825232,
            Self::Green => 0x2E7D32,
            Self::Red => 0xE03430,
            Self::Black => 0x22252A,
        }
    }

    pub fn lang_key(self) -> &'static str {
        match self {
            Self::White => "gokart.color.white",
            Self::Orange => "gokart.color.orange",
            Self::Magenta => "gokart.color.magenta",
            Self::LightBlue => "gokart.color.light_blue",
            Self::Yellow => "gokart.color.yellow",
            Self::Lime => "gokart.color.lime",
            Self::Pink => "gokart.color.pink",
            Self::Gray => "gokart.color.gray",
            Self::LightGray => "gokart.color.light_gray",
            Self::Cyan => "gokart.color.cyan",
            Self::Purple => "gokart.color.purple",
            Self::Blue => "gokart.color.blue",
            Self::Brown => "gokart.color.brown",
            Self::Green => "gokart.color.green",
            Self::Red => "gokart.color.red",
            Self::Black => "gokart.color.black",
        }
    }
}

/// Direct emergency fuel items besides the Jerry Can (millibuckets restored).
pub fn direct_fuel_item_mb(item: &str) -> Option<(u32, Option<&'static str>)> {
    match item {
        "minecraft:coal" | "minecraft:charcoal" => Some((250, None)),
        "minecraft:blaze_powder" => Some((400, None)),
        "minecraft:blaze_rod" => Some((800, None)),
        "minecraft:coal_block" => Some((2_000, None)),
        "minecraft:lava_bucket" => Some((2_000, Some("minecraft:bucket"))),
        _ => None,
    }
}

/// Blocks that can refill a Jerry Can on right-click in the world.
pub fn world_refill_block_mb(block: &str) -> Option<u32> {
    match block {
        "minecraft:lava" => Some(JERRY_MAX_FUEL_MB),
        "minecraft:magma_block" => Some(1_000),
        "minecraft:coal_block" => Some(1_500),
        _ => None,
    }
}

// ---------------------------------------------------------------------------
// Go-Kart Persistent Specification & Item Component Serialization
// ---------------------------------------------------------------------------

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct KartSpec {
    pub engine: EngineTier,
    pub wheels: WheelType,
    pub paint: PaintColor,
    pub fuel_mb: u32,
}

impl Default for KartSpec {
    fn default() -> Self {
        Self {
            engine: EngineTier::Iron,
            wheels: WheelType::Standard,
            paint: PaintColor::Red,
            fuel_mb: KART_MAX_FUEL_MB,
        }
    }
}

impl KartSpec {
    pub fn fuel_percent(&self) -> u32 {
        ((self.fuel_mb.min(KART_MAX_FUEL_MB) * 100) + (KART_MAX_FUEL_MB / 2)) / KART_MAX_FUEL_MB
    }

    pub fn encode_component(&self) -> String {
        format!(
            "engine={};wheels={};paint={};fuel={}",
            self.engine.slug(),
            self.wheels.slug(),
            self.paint.slug(),
            self.fuel_mb.min(KART_MAX_FUEL_MB)
        )
    }

    pub fn decode_component(s: &str) -> Self {
        let mut spec = Self::default();
        for part in s.split(';') {
            let Some((k, v)) = part.split_once('=') else {
                continue;
            };
            match k.trim() {
                "engine" => spec.engine = EngineTier::from_slug(v),
                "wheels" => spec.wheels = WheelType::from_slug(v),
                "paint" => spec.paint = PaintColor::from_slug(v),
                "fuel" => {
                    if let Ok(mb) = v.trim().parse::<u32>() {
                        spec.fuel_mb = mb.min(KART_MAX_FUEL_MB);
                    }
                }
                _ => {}
            }
        }
        spec
    }
}

// ---------------------------------------------------------------------------
// Real-time Go-Kart Kinematics & MrCrayfish Drift/Boost State
// ---------------------------------------------------------------------------

#[derive(Clone, Copy, Debug, Default, PartialEq)]
pub struct DriveInput {
    /// `+1.0` forward (`W`), `-1.0` brake/reverse (`S`), `0.0` coast.
    pub throttle: f32,
    /// `+1.0` steer left (`A`), `-1.0` steer right (`D`), `0.0` straight.
    pub steer: f32,
    /// Handbrake / drift / stationary burnout charge (`Space`).
    pub handbrake: bool,
}

impl DriveInput {
    pub fn encode_packet(self) -> [u8; 3] {
        let t = (self.throttle.clamp(-1.0, 1.0) * 100.0).round() as i8;
        let s = (self.steer.clamp(-1.0, 1.0) * 100.0).round() as i8;
        let flags = u8::from(self.handbrake);
        [t as u8, s as u8, flags]
    }

    pub fn decode_packet(bytes: &[u8]) -> Option<Self> {
        if bytes.len() < 3 {
            return None;
        }
        let t = (bytes[0] as i8) as f32 / 100.0;
        let s = (bytes[1] as i8) as f32 / 100.0;
        let handbrake = (bytes[2] & 1) != 0;
        Some(Self {
            throttle: t.clamp(-1.0, 1.0),
            steer: s.clamp(-1.0, 1.0),
            handbrake,
        })
    }
}

#[derive(Clone, Debug)]
pub struct KartRuntime {
    pub uuid: u128,
    pub dimension: String,
    pub spec: KartSpec,
    /// Signed forward speed along chassis heading (blocks/tick).
    pub forward_speed: f32,
    /// Current world horizontal velocity `[vx, vz]` (blocks/tick).
    pub vel_xz: [f32; 2],
    /// Front wheel steering angle in degrees (`-MAX_STEER_DEG..=+MAX_STEER_DEG`, `+` = left).
    pub steer_deg: f32,
    /// Cumulative wheel rolling angle in degrees (wraps `[0, 360)`).
    pub wheel_rot_deg: f32,
    /// Drift / burnout boost charge (`0.0..=1.0`).
    pub boost_charge: f32,
    /// Active turbo boost ticks remaining (`0..=32`).
    pub boost_ticks: u16,
    /// Current turbo strength (`0.0..=1.0`).
    pub boost_power: f32,
    /// True while sliding in a handbrake drift.
    pub drifting: bool,
    /// True while holding Throttle + Handbrake stationary burnout!
    pub burnout: bool,
    /// Fractional millibucket accumulator for smooth sub-mB fuel drain.
    pub fuel_accum: f32,
    /// Tick counter for sound / exhaust cadence.
    pub tick_count: u64,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct StepOutcome {
    /// New entity yaw in degrees (Minecraft convention: `0` = +Z south, `-90` = +X east).
    pub yaw_deg: f32,
    /// New 3D velocity `[vx, vy, vz]` to apply via `native_entity_set_velocity`.
    pub velocity: [f64; 3],
    /// Speed in km/h (`|horizontal_speed| * 20 * 3.6`).
    pub speed_kmh: f32,
    /// True on the exact tick a charge-boost or drift-boost fires!
    pub boost_triggered: bool,
    /// Engine sound pitch (`None` if engine isn't running).
    pub engine_sound_pitch: Option<f32>,
    /// Emit tire smoke / exhaust particles this tick.
    pub tire_smoke: bool,
}

impl KartRuntime {
    pub fn new(uuid: u128, dimension: impl Into<String>, spec: KartSpec) -> Self {
        Self {
            uuid,
            dimension: dimension.into(),
            spec,
            forward_speed: 0.0,
            vel_xz: [0.0, 0.0],
            steer_deg: 0.0,
            wheel_rot_deg: 0.0,
            boost_charge: 0.0,
            boost_ticks: 0,
            boost_power: 0.0,
            drifting: false,
            burnout: false,
            fuel_accum: 0.0,
            tick_count: 0,
        }
    }

    pub fn has_fuel(&self, require_fuel: bool) -> bool {
        !require_fuel || self.spec.fuel_mb > 0
    }

    pub fn can_drive_powered(&self, require_fuel: bool) -> bool {
        self.spec.engine != EngineTier::None && self.has_fuel(require_fuel)
    }

    /// Advances Go-Kart physics by one 20-Hz server tick.
    pub fn step(
        &mut self,
        current_yaw_deg: f32,
        current_vel: [f64; 3],
        on_ground: bool,
        in_water: bool,
        surface: SurfaceKind,
        rider_present: bool,
        input: DriveInput,
        require_fuel: bool,
    ) -> StepOutcome {
        self.tick_count = self.tick_count.wrapping_add(1);
        let active_input = if rider_present {
            input
        } else {
            DriveInput::default()
        };

        // 1. Steering angle smoothing (speed-sensitive max angle for high-speed stability)
        let max_top = self.spec.engine.max_speed_bps().max(0.725);
        let speed_ratio = (self.forward_speed.abs() / max_top).clamp(0.0, 1.25);
        let dynamic_max_steer = MAX_STEER_DEG * (1.0 - 0.32 * speed_ratio.min(1.0));
        let target_steer = active_input.steer.clamp(-1.0, 1.0) * dynamic_max_steer;
        let steer_step = self.spec.wheels.steer_rate_deg();
        if (target_steer - self.steer_deg).abs() <= steer_step {
            self.steer_deg = target_steer;
        } else if target_steer > self.steer_deg {
            self.steer_deg += steer_step;
        } else {
            self.steer_deg -= steer_step;
        }

        let powered = rider_present && self.can_drive_powered(require_fuel);
        let mut boost_triggered = false;

        // 2. Stationary Burnout Charge-Boost (MrCrayfish signature mechanic: W + Space at rest!)
        let nearly_stopped = self.forward_speed.abs() < 0.09;
        if powered && active_input.handbrake && active_input.throttle > 0.25 && nearly_stopped && on_ground {
            self.burnout = true;
            self.drifting = false;
            self.forward_speed *= 0.5;
            self.vel_xz = [self.vel_xz[0] * 0.5, self.vel_xz[1] * 0.5];
            let charge_step = 0.036 * self.spec.wheels.boost_charge_multiplier();
            self.boost_charge = (self.boost_charge + charge_step).min(1.0);
            // Burn a tiny bit of fuel while revving burnout
            self.consume_fuel(require_fuel, 0.35);
        } else {
            // Did the driver just release Space from a burnout or charged drift while holding throttle?
            if (self.burnout || self.drifting)
                && !active_input.handbrake
                && active_input.throttle > 0.1
                && self.boost_charge >= 0.30
                && powered
            {
                self.boost_power = self.boost_charge;
                self.boost_ticks = (12.0 + 20.0 * self.boost_charge).round() as u16;
                self.boost_charge = 0.0;
                boost_triggered = true;
            } else if !active_input.handbrake {
                self.boost_charge = (self.boost_charge - 0.05).max(0.0);
            }
            self.burnout = false;
        }

        // 3. High-speed Handbrake Drift
        if !self.burnout
            && rider_present
            && active_input.handbrake
            && on_ground
            && self.forward_speed > 0.20
            && active_input.steer.abs() > 0.15
        {
            self.drifting = true;
            let charge_step = 0.022 * self.spec.wheels.boost_charge_multiplier();
            self.boost_charge = (self.boost_charge + charge_step).min(1.0);
        } else if !active_input.handbrake || self.forward_speed <= 0.12 {
            self.drifting = false;
        }

        // 4. Active Turbo Boost countdown
        let boost_mult = if self.boost_ticks > 0 {
            self.boost_ticks -= 1;
            1.0 + 0.36 * self.boost_power
        } else {
            self.boost_power = 0.0;
            1.0
        };

        // 5. Longitudinal Throttle / Brake / Reverse Acceleration
        let surf_factor = if in_water {
            0.42
        } else {
            self.spec.wheels.surface_speed_factor(surface)
        };
        let top_forward = self.spec.engine.max_speed_bps() * surf_factor * boost_mult;
        let top_reverse = top_forward * 0.38;
        let base_accel = self.spec.engine.acceleration()
            * (if self.boost_ticks > 0 { 1.85 } else { 1.0 })
            * (if in_water { 0.45 } else { 1.0 });

        if !self.burnout {
            if active_input.handbrake && !self.drifting {
                // Pure handbrake stop
                self.forward_speed *= 0.76;
                if self.forward_speed.abs() < 0.01 {
                    self.forward_speed = 0.0;
                }
            } else if active_input.throttle > 0.05 {
                if self.forward_speed < -0.02 {
                    // Braking while rolling backward
                    self.forward_speed = (self.forward_speed + 0.085).min(0.0);
                } else if powered {
                    let target = top_forward * active_input.throttle;
                    if self.forward_speed < target {
                        self.forward_speed = (self.forward_speed + base_accel * active_input.throttle).min(target);
                    } else {
                        self.forward_speed *= 0.96;
                    }
                    self.consume_fuel(require_fuel, active_input.throttle.abs());
                } else {
                    self.forward_speed *= 0.92;
                }
            } else if active_input.throttle < -0.05 {
                if self.forward_speed > 0.03 {
                    // Footbrake while moving forward
                    self.forward_speed = (self.forward_speed - 0.095 * active_input.throttle.abs()).max(0.0);
                } else if powered {
                    let target = -top_reverse * active_input.throttle.abs();
                    if self.forward_speed > target {
                        self.forward_speed =
                            (self.forward_speed - base_accel * 0.70 * active_input.throttle.abs()).max(target);
                    }
                    self.consume_fuel(require_fuel, 0.65 * active_input.throttle.abs());
                } else {
                    self.forward_speed *= 0.92;
                }
            } else {
                // Natural rolling resistance / engine braking
                let drag = if rider_present { 0.935 } else { 0.84 };
                self.forward_speed *= drag;
                if self.forward_speed.abs() < 0.004 {
                    self.forward_speed = 0.0;
                }
            }
        }

        // 6. Bicycle-Axle Heading Update
        // Minecraft entity yaw: 0 deg = +Z (south), 90 deg = -X (west), -90 deg = +X (east).
        // Therefore forward unit vector is `[-sin(yaw), +cos(yaw)]`.
        // Note: positive `steer_deg` (+left / counterclockwise from above) decreases Minecraft yaw!
        let mut yaw_deg = current_yaw_deg;
        if self.forward_speed.abs() > 0.006 && !self.burnout {
            let steer_rad = self.steer_deg.to_radians();
            let drift_yaw_bonus = if self.drifting { 1.38 } else { 1.0 };
            let angular_step_rad = (self.forward_speed / WHEELBASE) * steer_rad.tan() * drift_yaw_bonus;
            yaw_deg = wrap_degrees(yaw_deg - angular_step_rad.to_degrees());
        } else if self.burnout && active_input.steer.abs() > 0.1 {
            // Subtle burnout pivot so you can aim your launch!
            yaw_deg = wrap_degrees(yaw_deg - active_input.steer * 2.4);
        }

        let yaw_rad = yaw_deg.to_radians();
        let fwd_x = -yaw_rad.sin();
        let fwd_z = yaw_rad.cos();

        // 7. Lateral Tire Grip & Drift Slip Vector Blending
        let desired_vx = fwd_x * self.forward_speed;
        let desired_vz = fwd_z * self.forward_speed;
        let grip = self.spec.wheels.lateral_grip(surface, self.drifting);
        self.vel_xz[0] += (desired_vx - self.vel_xz[0]) * grip;
        self.vel_xz[1] += (desired_vz - self.vel_xz[1]) * grip;
        if self.forward_speed == 0.0 && self.vel_xz[0].hypot(self.vel_xz[1]) < 0.005 {
            self.vel_xz = [0.0, 0.0];
        }

        // 8. Exact No-Slip Wheel Rolling Kinematics
        let spin_deg = if self.burnout {
            42.0
        } else {
            let circumference = 2.0 * std::f32::consts::PI * REAR_HUB_Y;
            (self.forward_speed / circumference) * 360.0
        };
        self.wheel_rot_deg = (self.wheel_rot_deg + spin_deg).rem_euclid(360.0);

        // 9. Vertical Velocity (keep grounded cleanly on slopes while preserving fall gravity)
        let cur_vy = current_vel[1];
        let next_vy = if in_water {
            (cur_vy - 0.02).max(-0.12)
        } else if on_ground && cur_vy <= 0.0 {
            -0.06
        } else {
            ((cur_vy - 0.08) * 0.98).max(-3.0)
        };

        let horiz_speed = self.vel_xz[0].hypot(self.vel_xz[1]);
        let speed_kmh = horiz_speed * 20.0 * 3.6;

        let engine_sound_pitch = if powered {
            let (p_min, p_max) = self.spec.engine.pitch_range();
            let rev = if self.burnout {
                0.65 + 0.35 * self.boost_charge
            } else {
                (horiz_speed / top_forward.max(0.4)).clamp(0.0, 1.0)
            };
            Some(p_min + (p_max - p_min) * rev)
        } else {
            None
        };

        let tire_smoke = self.burnout || self.drifting || self.boost_ticks > 0;

        StepOutcome {
            yaw_deg,
            velocity: [
                f64::from(self.vel_xz[0]),
                next_vy,
                f64::from(self.vel_xz[1]),
            ],
            speed_kmh,
            boost_triggered,
            engine_sound_pitch,
            tire_smoke,
        }
    }

    fn consume_fuel(&mut self, require_fuel: bool, throttle_factor: f32) {
        if !require_fuel || self.spec.fuel_mb == 0 {
            return;
        }
        let burn = self.spec.engine.fuel_burn_per_tick() * throttle_factor.clamp(0.15, 1.2);
        self.fuel_accum += burn;
        if self.fuel_accum >= 1.0 {
            let whole = self.fuel_accum.floor() as u32;
            self.fuel_accum -= whole as f32;
            self.spec.fuel_mb = self.spec.fuel_mb.saturating_sub(whole);
        }
    }
}

pub fn wrap_degrees(deg: f32) -> f32 {
    let mut d = (deg + 180.0).rem_euclid(360.0) - 180.0;
    if d == -180.0 {
        d = 180.0;
    }
    d
}

// ---------------------------------------------------------------------------
// Compact Server -> Client Snapshot Codec (`CHAN_SYNC`)
// ---------------------------------------------------------------------------

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct ClientKartView {
    pub entity_id: u32,
    pub spec: KartSpec,
    pub steer_deg: f32,
    pub wheel_rot_deg: f32,
    pub speed_kmh: f32,
    pub boost_charge: f32,
    pub drifting: bool,
    pub burnout: bool,
    pub boosting: bool,
}

/// Encodes `require_fuel` + a slice of `ClientKartView` into a compact binary frame.
pub fn encode_sync_packet(require_fuel: bool, karts: &[ClientKartView]) -> Vec<u8> {
    let count = karts.len().min(255);
    let mut out = Vec::with_capacity(2 + count * 16);
    out.push(u8::from(require_fuel));
    out.push(count as u8);
    for k in karts.iter().take(count) {
        out.extend_from_slice(&k.entity_id.to_le_bytes());
        out.push(k.spec.engine.code());
        out.push(k.spec.wheels.code());
        out.push(k.spec.paint.code());
        out.extend_from_slice(&(k.spec.fuel_mb.min(u16::MAX as u32) as u16).to_le_bytes());
        let steer_i16 = (k.steer_deg.clamp(-45.0, 45.0) * 100.0).round() as i16;
        out.extend_from_slice(&steer_i16.to_le_bytes());
        let rot_u16 = (k.wheel_rot_deg.rem_euclid(360.0) * 100.0).round() as u16;
        out.extend_from_slice(&rot_u16.to_le_bytes());
        let kmh_u16 = (k.speed_kmh.clamp(0.0, 500.0) * 10.0).round() as u16;
        out.extend_from_slice(&kmh_u16.to_le_bytes());
        let charge_u8 = (k.boost_charge.clamp(0.0, 1.0) * 255.0).round() as u8;
        out.push(charge_u8);
        let flags = u8::from(k.drifting)
            | (u8::from(k.burnout) << 1)
            | (u8::from(k.boosting) << 2);
        out.push(flags);
    }
    out
}

pub fn decode_sync_packet(data: &[u8]) -> Option<(bool, Vec<ClientKartView>)> {
    if data.len() < 2 {
        return None;
    }
    let require_fuel = data[0] != 0;
    let count = data[1] as usize;
    let stride = 17;
    if data.len() < 2 + count * stride {
        return None;
    }
    let mut karts = Vec::with_capacity(count);
    for i in 0..count {
        let base = 2 + i * stride;
        let s = &data[base..base + stride];
        let entity_id = u32::from_le_bytes([s[0], s[1], s[2], s[3]]);
        let engine = EngineTier::from_code(s[4]);
        let wheels = WheelType::from_code(s[5]);
        let paint = PaintColor::from_code(s[6]);
        let fuel_mb = u16::from_le_bytes([s[7], s[8]]) as u32;
        let steer_deg = i16::from_le_bytes([s[9], s[10]]) as f32 / 100.0;
        let wheel_rot_deg = u16::from_le_bytes([s[11], s[12]]) as f32 / 100.0;
        let speed_kmh = u16::from_le_bytes([s[13], s[14]]) as f32 / 10.0;
        let boost_charge = s[15] as f32 / 255.0;
        let flags = s[16];
        karts.push(ClientKartView {
            entity_id,
            spec: KartSpec {
                engine,
                wheels,
                paint,
                fuel_mb,
            },
            steer_deg,
            wheel_rot_deg,
            speed_kmh,
            boost_charge,
            drifting: (flags & 1) != 0,
            burnout: (flags & 2) != 0,
            boosting: (flags & 4) != 0,
        });
    }
    Some((require_fuel, karts))
}

// ---------------------------------------------------------------------------
// World Save & Config Text Serialization (no external crates required)
// ---------------------------------------------------------------------------

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct SavedWorldData {
    pub require_fuel: bool,
    pub karts: BTreeMap<u128, (String, KartSpec)>,
}

impl Default for SavedWorldData {
    fn default() -> Self {
        Self {
            require_fuel: true,
            karts: BTreeMap::new(),
        }
    }
}

impl SavedWorldData {
    pub fn encode(&self) -> String {
        let mut out = String::new();
        out.push_str("# Horizon Go-Kart World State\n");
        out.push_str(&format!("require_fuel={}\n", self.require_fuel));
        for (&uuid, (dim, spec)) in &self.karts {
            out.push_str(&format!(
                "kart={uuid:032x}|{dim}|{}\n",
                spec.encode_component()
            ));
        }
        out
    }

    pub fn decode(text: &str) -> Self {
        let mut data = Self::default();
        for raw in text.lines() {
            let line = raw.trim();
            if line.is_empty() || line.starts_with('#') {
                continue;
            }
            if let Some(rest) = line.strip_prefix("require_fuel=") {
                data.require_fuel = matches!(rest.trim(), "true" | "1" | "yes" | "on");
            } else if let Some(rest) = line.strip_prefix("kart=") {
                let mut parts = rest.splitn(3, '|');
                let (Some(u_hex), Some(dim), Some(spec_str)) =
                    (parts.next(), parts.next(), parts.next())
                else {
                    continue;
                };
                if let Ok(uuid) = u128::from_str_radix(u_hex.trim(), 16) {
                    data.karts
                        .insert(uuid, (dim.trim().to_owned(), KartSpec::decode_component(spec_str)));
                }
            }
        }
        data
    }
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct ClientSettings {
    pub auto_third_person: bool,
    pub camera_distance: f32,
    pub speed_kmh: bool,
}

impl Default for ClientSettings {
    fn default() -> Self {
        Self {
            auto_third_person: true,
            camera_distance: DEFAULT_CAMERA_DISTANCE,
            speed_kmh: true,
        }
    }
}

impl ClientSettings {
    pub fn encode_toml(&self) -> String {
        format!(
            "# Horizon Go-Kart Client Settings\n\
             auto_third_person = {}\n\
             camera_distance = {:.1}\n\
             speed_kmh = {}\n",
            self.auto_third_person, self.camera_distance, self.speed_kmh
        )
    }

    pub fn decode_toml(text: &str) -> Self {
        let mut cfg = Self::default();
        for raw in text.lines() {
            let line = raw.split('#').next().unwrap_or("").trim();
            let Some((k, v)) = line.split_once('=') else {
                continue;
            };
            let val = v.trim().trim_matches('"');
            match k.trim() {
                "auto_third_person" => cfg.auto_third_person = matches!(val, "true" | "1" | "on"),
                "camera_distance" => {
                    if let Ok(d) = val.parse::<f32>() {
                        cfg.camera_distance = d.clamp(2.0, 10.0);
                    }
                }
                "speed_kmh" => cfg.speed_kmh = matches!(val, "true" | "1" | "on"),
                _ => {}
            }
        }
        cfg
    }
}

// ---------------------------------------------------------------------------
// Unit Tests (`cargo test`)
// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn engine_tiers_increase_top_speed_and_acceleration() {
        assert!(EngineTier::Diamond.max_speed_bps() > EngineTier::Gold.max_speed_bps());
        assert!(EngineTier::Gold.max_speed_bps() > EngineTier::Iron.max_speed_bps());
        assert!(EngineTier::Iron.max_speed_bps() > EngineTier::None.max_speed_bps());
        assert!(EngineTier::Diamond.acceleration() > EngineTier::Gold.acceleration());
        assert!(EngineTier::Gold.acceleration() > EngineTier::Iron.acceleration());
    }

    #[test]
    fn wheel_surface_factors_match_design() {
        let road = SurfaceKind::from_block_name("minecraft:gray_concrete");
        let sand = SurfaceKind::from_block_name("minecraft:sand");
        let ice = SurfaceKind::from_block_name("minecraft:packed_ice");
        assert_eq!(road, SurfaceKind::Road);
        assert_eq!(sand, SurfaceKind::Loose);
        assert_eq!(ice, SurfaceKind::Ice);

        assert!(
            WheelType::Racing.surface_speed_factor(road)
                > WheelType::Standard.surface_speed_factor(road)
        );
        assert!(
            WheelType::Sports.surface_speed_factor(sand)
                > WheelType::Racing.surface_speed_factor(sand)
        );
    }

    #[test]
    fn all_16_minecraft_dyes_map_to_distinct_paint_colors() {
        let dyes = [
            "minecraft:white_dye",
            "minecraft:orange_dye",
            "minecraft:magenta_dye",
            "minecraft:light_blue_dye",
            "minecraft:yellow_dye",
            "minecraft:lime_dye",
            "minecraft:pink_dye",
            "minecraft:gray_dye",
            "minecraft:light_gray_dye",
            "minecraft:cyan_dye",
            "minecraft:purple_dye",
            "minecraft:blue_dye",
            "minecraft:brown_dye",
            "minecraft:green_dye",
            "minecraft:red_dye",
            "minecraft:black_dye",
        ];
        for (idx, dye) in dyes.iter().enumerate() {
            let color = PaintColor::from_dye_item(dye).expect("dye mapped");
            assert_eq!(color.code() as usize, idx);
            assert_eq!(PaintColor::from_slug(color.slug()), color);
        }
    }

    #[test]
    fn kart_spec_component_round_trips() {
        let spec = KartSpec {
            engine: EngineTier::Diamond,
            wheels: WheelType::Racing,
            paint: PaintColor::Cyan,
            fuel_mb: 1_435,
        };
        let encoded = spec.encode_component();
        assert_eq!(KartSpec::decode_component(&encoded), spec);
    }

    #[test]
    fn forward_acceleration_steering_and_fuel_consumption_work() {
        let mut kart = KartRuntime::new(
            42,
            "minecraft:overworld",
            KartSpec {
                engine: EngineTier::Gold,
                wheels: WheelType::Sports,
                paint: PaintColor::Yellow,
                fuel_mb: 1_000,
            },
        );

        let mut yaw = 0.0;
        let mut vel = [0.0, 0.0, 0.0];
        for _ in 0..30 {
            let step = kart.step(
                yaw,
                vel,
                true,
                false,
                SurfaceKind::Road,
                true,
                DriveInput {
                    throttle: 1.0,
                    steer: 0.6,
                    handbrake: false,
                },
                true,
            );
            yaw = step.yaw_deg;
            vel = step.velocity;
        }

        assert!(kart.forward_speed > 0.65, "kart accelerated to cruising speed");
        assert!(yaw < -15.0, "left steer turned entity yaw counterclockwise");
        assert!(kart.spec.fuel_mb < 1_000, "fuel drained while driving");

        // Infinite fuel mode consumes zero fuel
        let saved_fuel = kart.spec.fuel_mb;
        kart.fuel_accum = 0.0;
        for _ in 0..25 {
            let step = kart.step(
                yaw,
                vel,
                true,
                false,
                SurfaceKind::Road,
                true,
                DriveInput {
                    throttle: 1.0,
                    steer: 0.0,
                    handbrake: false,
                },
                false,
            );
            yaw = step.yaw_deg;
            vel = step.velocity;
        }
        assert_eq!(kart.spec.fuel_mb, saved_fuel);
    }

    #[test]
    fn stationary_burnout_charges_and_triggers_turbo_boost() {
        let mut kart = KartRuntime::new(7, "minecraft:overworld", KartSpec::default());
        let mut yaw = 0.0;
        let mut vel = [0.0, 0.0, 0.0];

        // Hold W + Space at rest for 20 ticks to charge burnout boost
        for _ in 0..20 {
            let out = kart.step(
                yaw,
                vel,
                true,
                false,
                SurfaceKind::Road,
                true,
                DriveInput {
                    throttle: 1.0,
                    steer: 0.0,
                    handbrake: true,
                },
                false,
            );
            yaw = out.yaw_deg;
            vel = out.velocity;
            assert!(kart.burnout);
            assert!(out.speed_kmh < 2.0, "kart stays planted during burnout");
        }
        assert!(kart.boost_charge > 0.60);

        // Release Space while holding W -> turbo launch fires!
        let launch = kart.step(
            yaw,
            vel,
            true,
            false,
            SurfaceKind::Road,
            true,
            DriveInput {
                throttle: 1.0,
                steer: 0.0,
                handbrake: false,
            },
            false,
        );
        assert!(launch.boost_triggered);
        assert!(kart.boost_ticks >= 20);
    }

    #[test]
    fn sync_packet_and_world_save_round_trip() {
        let views = vec![ClientKartView {
            entity_id: 991,
            spec: KartSpec {
                engine: EngineTier::Diamond,
                wheels: WheelType::Racing,
                paint: PaintColor::Lime,
                fuel_mb: 1750,
            },
            steer_deg: -14.5,
            wheel_rot_deg: 212.25,
            speed_kmh: 72.4,
            boost_charge: 0.8,
            drifting: true,
            burnout: false,
            boosting: true,
        }];
        let bytes = encode_sync_packet(false, &views);
        let (req_fuel, decoded) = decode_sync_packet(&bytes).expect("valid packet");
        assert!(!req_fuel);
        assert_eq!(decoded.len(), 1);
        assert_eq!(decoded[0].entity_id, 991);
        assert_eq!(decoded[0].spec, views[0].spec);
        assert!((decoded[0].steer_deg - (-14.5)).abs() < 0.05);
        assert!(decoded[0].drifting && decoded[0].boosting && !decoded[0].burnout);

        let mut world = SavedWorldData {
            require_fuel: false,
            karts: BTreeMap::new(),
        };
        world.karts.insert(
            0x1234_5678_9abc_def0_1122_3344_5566_7788,
            ("minecraft:overworld".into(), views[0].spec),
        );
        let text = world.encode();
        assert_eq!(SavedWorldData::decode(&text), world);

        let cfg = ClientSettings {
            auto_third_person: false,
            camera_distance: 5.5,
            speed_kmh: false,
        };
        assert_eq!(ClientSettings::decode_toml(&cfg.encode_toml()), cfg);
    }

    #[test]
    fn kart_spatial_geometry_places_tires_on_ground_and_aligns_cockpit() {
        let model_wheel_radius = 3.5_f32 / 16.0;
        let front_bottom = FRONT_HUB_Y - model_wheel_radius * FRONT_WHEEL_SCALE[1];
        let rear_bottom = REAR_HUB_Y - model_wheel_radius * REAR_WHEEL_SCALE[1];
        assert!(front_bottom.abs() < 1e-6, "front tires rest flat on Y=0");
        assert!(rear_bottom.abs() < 1e-6, "rear tires rest flat on Y=0");
        assert!((WHEELBASE - 1.50).abs() < 1e-6);
        assert!(REAR_TRACK_HALF_X > FRONT_TRACK_HALF_X);
        assert!(STEER_PIVOT[2] > SEAT_OFFSET_Z && STEER_PIVOT[1] > SEAT_ATTACH_Y);
    }
}
