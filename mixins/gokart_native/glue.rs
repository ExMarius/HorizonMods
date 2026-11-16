// Horizon Go-Kart (`gokart`) integration glue (`crate::game::gokart_glue`).
// Connects pure-Rust vehicle physics/state (`crate::game::gokart`, runtime.rs)
// to Horizon Nightly's stable native hook points.

use crate::game::{Game, NativeBlockEdit, NativeBlockRun, gokart as rules, perspective::CameraType};
use horizon_client::{
    hud::HudBatch,
    items::ItemStack,
    lang,
    mobs::{Mob, anim::BodyPose, riders as mob_riders},
    mod_api::{
        BlockEntityDraw, Corners, KeyCode, NativeCommand, NativeMobRender, NativeMod,
        NativeScreenView, NativeServerPlayer, ParticleOptions, ParticleType, ServerTickPhase,
        WorldPhase, winit,
    },
    text::{self, Text},
};
use horizon_mods::content::{Item, Rarity};
use horizon_world::nbt::{Compound, JavaString, Tag};
use std::{
    any::Any,
    collections::{BTreeMap, BTreeSet, HashMap},
    fs,
    ops::ControlFlow,
    path::PathBuf,
    sync::{Arc, Mutex, MutexGuard},
    time::Instant,
};

const SOUND_PLAYERS: usize = 7;
const SOUND_NEUTRAL: usize = 6;
const SEAT_HEIGHT_PIG: f64 = 0.26875;
const SAVE_INTERVAL_TICKS: u64 = 100;

struct ServerState {
    dir: PathBuf,
    require_fuel: bool,
    dirty: bool,
    tick: u64,
    /// Active Go-Karts indexed by entity UUID (`u128`).
    by_uuid: HashMap<u128, rules::KartRuntime>,
    /// Fast map from current runtime `entity_id` (`u32`) to `uuid` (`u128`).
    id_to_uuid: HashMap<u32, u128>,
    /// Latest driving inputs received per player UUID (`u128`).
    inputs: HashMap<u128, rules::DriveInput>,
    /// Last Go-Kart entity targeted with a Wrench per player UUID.
    selected_kart: HashMap<u128, u32>,
    /// Position of each Go-Kart before `ai::tick` for wall-impact detection.
    pre_tick_pos: HashMap<u32, ([f64; 3], f32)>,
    /// Currently placed nighttime `minecraft:light` blocks `(dimension, [x, y, z])`.
    active_lights: BTreeSet<(String, [i32; 3])>,
}

#[derive(Default)]
struct ClientState {
    loaded_config: bool,
    settings: rules::ClientSettings,
    require_fuel: bool,
    karts: BTreeMap<u32, rules::ClientKartView>,
    smoothed_steer: BTreeMap<u32, f32>,
    local_input: rules::DriveInput,
    last_sent_input: rules::DriveInput,
    heartbeat: u8,
    was_riding_kart: bool,
    restored_first_person: bool,
    cam_kart_entity: Option<u32>,
    visual_kart_yaw: f32,
    last_seen_game_yaw: f32,
    last_mouse_move: Option<Instant>,
    last_frame_instant: Option<Instant>,
    pending_open_garage: bool,
    pending_close_garage: bool,
    pending_actions: Vec<Vec<u8>>,
    garage_target_entity: Option<u32>,
    horn_cooldown: u8,
}

static SERVER: Mutex<Option<ServerState>> = Mutex::new(None);
static CLIENT: Mutex<ClientState> = Mutex::new(ClientState {
    loaded_config: false,
    settings: rules::ClientSettings {
        auto_third_person: true,
        camera_distance: rules::DEFAULT_CAMERA_DISTANCE,
        speed_kmh: true,
    },
    require_fuel: true,
    karts: BTreeMap::new(),
    smoothed_steer: BTreeMap::new(),
    local_input: rules::DriveInput {
        throttle: 0.0,
        steer: 0.0,
        handbrake: false,
    },
    last_sent_input: rules::DriveInput {
        throttle: 0.0,
        steer: 0.0,
        handbrake: false,
    },
    heartbeat: 0,
    was_riding_kart: false,
    restored_first_person: false,
    cam_kart_entity: None,
    visual_kart_yaw: 0.0,
    last_seen_game_yaw: 0.0,
    last_mouse_move: None,
    last_frame_instant: None,
    pending_open_garage: false,
    pending_close_garage: false,
    pending_actions: Vec::new(),
    garage_target_entity: None,
    horn_cooldown: 0,
});

fn lock<T>(m: &'static Mutex<T>) -> MutexGuard<'static, T> {
    m.lock().unwrap_or_else(|e| e.into_inner())
}

// ---------------------------------------------------------------------------
// Localization & Item Helpers
// ---------------------------------------------------------------------------

fn tr(key: &str, fallback: &str) -> String {
    lang::get_or(key, fallback)
}

fn tr1(key: &str, fallback: &str, a1: &str) -> String {
    tr(key, fallback).replace("%1$s", a1)
}

fn tr3(key: &str, fallback: &str, a1: &str, a2: &str, a3: &str) -> String {
    tr(key, fallback)
        .replace("%1$s", a1)
        .replace("%2$s", a2)
        .replace("%3$s", a3)
}

fn stack_of(item: &str, count: u32) -> ItemStack {
    ItemStack {
        item: item.into(),
        count,
        damage: 0,
        extra: None,
    }
}

fn read_kart_spec(game: &Game<'_>, stack: &ItemStack) -> rules::KartSpec {
    let default_kind =
        rules::VehicleKind::from_item(&stack.item).unwrap_or(rules::VehicleKind::GoKart);
    if let Ok(Some(Tag::String(s))) = game.native_component(stack, rules::COMP_KART_DATA) {
        let mut spec = rules::KartSpec::decode_component_for_kind(default_kind, &s.to_string_lossy());
        spec.kind = default_kind;
        spec
    } else {
        rules::KartSpec::default_for_kind(default_kind)
    }
}

fn make_kart_item(game: &Game<'_>, spec: rules::KartSpec) -> ItemStack {
    let mut stack = stack_of(spec.kind.item_id(), 1);
    let _ = game.native_set_component(
        &mut stack,
        rules::COMP_KART_DATA,
        Tag::String(JavaString::from(spec.encode_component().as_str())),
    );
    stack
}

fn read_jerry_fuel(game: &Game<'_>, stack: &ItemStack) -> u32 {
    match game.native_component(stack, rules::COMP_JERRY_FUEL) {
        Ok(Some(Tag::Int(mb))) => (*mb).max(0) as u32,
        _ => rules::JERRY_DEFAULT_FUEL_MB,
    }
}

fn make_jerry_can(game: &Game<'_>, fuel_mb: u32) -> ItemStack {
    let mut stack = stack_of(rules::ITEM_JERRY_CAN, 1);
    let clamped = fuel_mb.min(rules::JERRY_MAX_FUEL_MB) as i32;
    let _ = game.native_set_component(&mut stack, rules::COMP_JERRY_FUEL, Tag::Int(clamped));
    stack
}

// ---------------------------------------------------------------------------
// World & Config Persistence
// ---------------------------------------------------------------------------

fn ensure_client_config(c: &mut ClientState) {
    if c.loaded_config {
        return;
    }
    c.loaded_config = true;
    if let Ok(dir) = Game::native_config_dir() {
        let file = dir.join(rules::CLIENT_CONFIG_FILE);
        if let Ok(text) = fs::read_to_string(&file) {
            c.settings = rules::ClientSettings::decode_toml(&text);
        } else {
            let _ = fs::create_dir_all(&dir);
            let _ = fs::write(&file, c.settings.encode_toml());
        }
    }
}

fn save_client_config(c: &ClientState) {
    if let Ok(dir) = Game::native_config_dir() {
        let _ = fs::create_dir_all(&dir);
        let _ = fs::write(dir.join(rules::CLIENT_CONFIG_FILE), c.settings.encode_toml());
    }
}

fn server_state(game: &Game<'_>) -> Option<MutexGuard<'static, Option<ServerState>>> {
    let dir = game.native_world_dir()?.join(rules::SAVE_DIR);
    let mut guard = lock(&SERVER);
    if guard.as_ref().is_none_or(|s| s.dir != dir) {
        let saved = fs::read_to_string(dir.join(rules::SAVE_FILE))
            .ok()
            .map(|t| rules::SavedWorldData::decode(&t))
            .unwrap_or_default();
        let mut by_uuid = HashMap::new();
        for (uuid, (dim, spec)) in saved.karts {
            by_uuid.insert(uuid, rules::KartRuntime::new(uuid, dim, spec));
        }
        let active_lights: BTreeSet<(String, [i32; 3])> = saved.lights.into_iter().collect();
        *guard = Some(ServerState {
            dir,
            require_fuel: saved.require_fuel,
            dirty: false,
            tick: 0,
            by_uuid,
            id_to_uuid: HashMap::new(),
            inputs: HashMap::new(),
            selected_kart: HashMap::new(),
            pre_tick_pos: HashMap::new(),
            active_lights,
        });
    }
    Some(guard)
}

fn flush_server_save(st: &mut ServerState) {
    if !st.dirty {
        return;
    }
    let mut data = rules::SavedWorldData {
        require_fuel: st.require_fuel,
        karts: Default::default(),
        lights: st.active_lights.iter().cloned().collect(),
    };
    for (&uuid, rt) in &st.by_uuid {
        data.karts.insert(uuid, (rt.dimension.clone(), rt.spec));
    }
    if fs::create_dir_all(&st.dir)
        .and_then(|()| fs::write(st.dir.join(rules::SAVE_FILE), data.encode()))
        .is_ok()
    {
        st.dirty = false;
    }
}

// ---------------------------------------------------------------------------
// Startup Registrations (Items, Components, Models, Mods Page, Commands)
// ---------------------------------------------------------------------------

pub(in crate::game) fn component_types(types: &mut Vec<String>) {
    types.push(rules::COMP_KART_DATA.into());
    types.push(rules::COMP_JERRY_FUEL.into());
}

pub(in crate::game) fn items(items: &mut Vec<Item>) {
    let push_item = |items: &mut Vec<Item>, id: &str, max_stack: u8, rarity: Rarity| {
        items.push(Item {
            id: id.into(),
            template: "minecraft:iron_ingot".into(),
            max_stack_size: Some(max_stack),
            rarity: Some(rarity),
            ..Default::default()
        });
    };
    push_item(items, rules::ITEM_GO_KART, 1, Rarity::Uncommon);
    push_item(items, rules::ITEM_OFF_ROADER, 1, Rarity::Rare);
    push_item(items, rules::ITEM_QUAD_BIKE, 1, Rarity::Uncommon);
    push_item(items, rules::ITEM_POLICE_CAR, 1, Rarity::Epic);
    push_item(items, rules::ITEM_ENGINE_IRON, 1, Rarity::Common);
    push_item(items, rules::ITEM_ENGINE_GOLD, 1, Rarity::Uncommon);
    push_item(items, rules::ITEM_ENGINE_DIAMOND, 1, Rarity::Rare);
    push_item(items, rules::ITEM_WHEEL_STANDARD, 16, Rarity::Common);
    push_item(items, rules::ITEM_WHEEL_SPORTS, 16, Rarity::Common);
    push_item(items, rules::ITEM_WHEEL_RACING, 16, Rarity::Uncommon);
    push_item(items, rules::ITEM_WRENCH, 1, Rarity::Common);
    push_item(items, rules::ITEM_JERRY_CAN, 1, Rarity::Common);
}

pub(in crate::game) fn standalone_models(models: &mut Vec<String>) {
    for m in rules::STANDALONE_MODELS {
        models.push(m.into());
    }
}

pub(in crate::game) fn listed(mods: &mut Vec<NativeMod>) {
    mods.push(NativeMod {
        id: rules::ID.into(),
        title: format!("Horizon Vehicles {}", rules::VERSION),
        description: tr("gokart.mod.description", rules::DESCRIPTION),
        keys: vec![
            [
                "horn".into(),
                "Vehicle Horn / Claxon".into(),
                "key.keyboard.h".into(),
            ],
            [
                "garage".into(),
                "Vehicle Garage & Paint Shop / Garaj".into(),
                "key.keyboard.k".into(),
            ],
        ],
    });
}

pub(in crate::game) fn commands(commands: &mut Vec<NativeCommand>) {
    commands.push(NativeCommand::new("vehicle"));
    commands.push(NativeCommand::new("vehicle remove [target:text]"));
    commands.push(NativeCommand::new("vehicle delete [target:text]"));
    commands.push(NativeCommand::new("vehicle clear"));
    commands.push(NativeCommand::new("vehicle pack"));
    commands.push(NativeCommand::new("vehicle paint <color:text>"));
    commands.push(NativeCommand::op("vehicle kit", 2));
    commands.push(NativeCommand::op("vehicle spawn [vehicle:text]", 2));
    commands.push(NativeCommand::op("vehicle fuel", 2));

    commands.push(NativeCommand::new("vehicel"));
    commands.push(NativeCommand::new("vehicel remove [target:text]"));
    commands.push(NativeCommand::new("vehicel delete [target:text]"));
    commands.push(NativeCommand::new("vehicel clear"));
    commands.push(NativeCommand::new("vehicel pack"));
    commands.push(NativeCommand::op("vehicel spawn [vehicle:text]", 2));

    commands.push(NativeCommand::new("gokart"));
    commands.push(NativeCommand::new("gokart remove [target:text]"));
    commands.push(NativeCommand::new("gokart clear"));
    commands.push(NativeCommand::new("gokart paint <color:text>"));
    commands.push(NativeCommand::op("gokart kit", 2));
    commands.push(NativeCommand::op("gokart spawn [vehicle:text]", 2));
    commands.push(NativeCommand::op("gokart fuel", 2));
}

// ---------------------------------------------------------------------------
// Backing Go-Kart & Off-Roader Entity Summoning & Identification
// ---------------------------------------------------------------------------

fn kart_summon_nbt(kind: rules::VehicleKind) -> Compound {
    let mut nbt = Compound::new();
    nbt.insert(JavaString::from("Silent"), Tag::Byte(1));
    nbt.insert(JavaString::from("Invulnerable"), Tag::Byte(1));
    nbt.insert(JavaString::from("PersistenceRequired"), Tag::Byte(1));
    nbt.insert(JavaString::from("Saddle"), Tag::Byte(1));
    let mut tags = vec![Tag::String(JavaString::from(rules::ENTITY_TAG))];
    match kind {
        rules::VehicleKind::OffRoader => {
            tags.push(Tag::String(JavaString::from(rules::ENTITY_TAG_OFF_ROADER)));
        }
        rules::VehicleKind::QuadBike => {
            tags.push(Tag::String(JavaString::from(rules::ENTITY_TAG_QUAD_BIKE)));
        }
        rules::VehicleKind::PoliceCar => {
            tags.push(Tag::String(JavaString::from(rules::ENTITY_TAG_POLICE_CAR)));
        }
        rules::VehicleKind::DaciaLoganPolice => {
            tags.push(Tag::String(JavaString::from(rules::ENTITY_TAG_DACIA_LOGAN)));
        }
        rules::VehicleKind::GoKart => {}
    }
    nbt.insert(JavaString::from("Tags"), Tag::List(tags));

    // Minecraft 26.3 saddle equipment slot so right-click mounts cleanly
    let mut saddle_item = Compound::new();
    saddle_item.insert(
        JavaString::from("id"),
        Tag::String(JavaString::from("minecraft:saddle")),
    );
    saddle_item.insert(JavaString::from("count"), Tag::Int(1));
    let mut equip = Compound::new();
    equip.insert(JavaString::from("saddle"), Tag::Compound(saddle_item));
    nbt.insert(JavaString::from("equipment"), Tag::Compound(equip));

    // Zero autonomous walk speed + vehicle step_height (0.625 kart / 1.05 4x4!) + knockback immunity
    let attr = |id: &str, base: f64| -> Tag {
        let mut c = Compound::new();
        c.insert(JavaString::from("id"), Tag::String(JavaString::from(id)));
        c.insert(JavaString::from("base"), Tag::Double(base.to_bits()));
        Tag::Compound(c)
    };
    nbt.insert(
        JavaString::from("attributes"),
        Tag::List(vec![
            attr("minecraft:movement_speed", 0.0),
            attr("minecraft:step_height", kind.layout().step_height),
            attr("minecraft:knockback_resistance", 1.0),
        ]),
    );
    nbt
}

fn prepare_kart_mob(game: &mut Game<'_>, entity_id: u32, yaw: f32, kind: rules::VehicleKind) {
    if let Some(m) = game.mobs.iter_mut().find(|m| m.id == entity_id) {
        m.ai.goals.clear();
        m.ai.targets.clear();
        m.extra.saddled = true;
        m.silent = true;
        m.invulnerable_flag = true;
        m.persistent = true;
        m.yaw = yaw;
        m.body_yaw = yaw;
        m.head_yaw = yaw;
    }
    if let Some(eref) = game.native_entity(entity_id) {
        game.native_entity_add_tag(eref, rules::ENTITY_TAG);
        match kind {
            rules::VehicleKind::OffRoader => {
                game.native_entity_add_tag(eref, rules::ENTITY_TAG_OFF_ROADER);
            }
            rules::VehicleKind::QuadBike => {
                game.native_entity_add_tag(eref, rules::ENTITY_TAG_QUAD_BIKE);
            }
            rules::VehicleKind::PoliceCar => {
                game.native_entity_add_tag(eref, rules::ENTITY_TAG_POLICE_CAR);
            }
            rules::VehicleKind::DaciaLoganPolice => {
                game.native_entity_add_tag(eref, rules::ENTITY_TAG_DACIA_LOGAN);
            }
            rules::VehicleKind::GoKart => {}
        }
        game.native_entity_set_rotation(eref, yaw, 0.0);
        game.native_entity_set_head_yaw(eref, yaw);
    }
}

fn spawn_kart(
    game: &mut Game<'_>,
    st: &mut ServerState,
    dimension: &str,
    pos: [f64; 3],
    yaw: f32,
    spec: rules::KartSpec,
) -> Option<u32> {
    let id = game.native_summon(dimension, "minecraft:pig", pos, kart_summon_nbt(spec.kind))?;
    prepare_kart_mob(game, id, yaw, spec.kind);
    let uuid = game
        .native_entity(id)
        .and_then(|e| game.native_entity_uuid(e))
        .unwrap_or_else(|| (u128::from(id) << 64) | 0x474f_4b41_5254_u128);
    st.id_to_uuid.insert(id, uuid);
    st.by_uuid
        .insert(uuid, rules::KartRuntime::new(uuid, dimension.to_owned(), spec));
    st.dirty = true;
    Some(id)
}

fn lookup_kart_uuid(
    game: &mut Game<'_>,
    st: &mut ServerState,
    dimension: &str,
    entity_id: u32,
) -> Option<u128> {
    if let Some(&u) = st.id_to_uuid.get(&entity_id) {
        if st.by_uuid.contains_key(&u) {
            return Some(u);
        }
        st.id_to_uuid.remove(&entity_id);
    }
    let eref = game.native_entity(entity_id)?;
    let uuid = game.native_entity_uuid(eref)?;
    if let Some(existing) = st.by_uuid.get(&uuid) {
        let k = existing.spec.kind;
        st.id_to_uuid.insert(entity_id, uuid);
        prepare_kart_mob(
            game,
            entity_id,
            game.native_entity_rotation(eref).map_or(0.0, |r| r[0]),
            k,
        );
        return Some(uuid);
    }
    // Recover any tagged Go-Kart / Off-Roader entity whose entry wasn't in karts.txt yet
    let tags = game.native_entity_tags(eref);
    if tags
        .as_ref()
        .is_some_and(|t| t.iter().any(|s| s == rules::ENTITY_TAG))
    {
        let default_spec = if tags
            .as_ref()
            .is_some_and(|t| t.iter().any(|s| s == rules::ENTITY_TAG_OFF_ROADER))
        {
            rules::KartSpec::default_off_roader()
        } else if tags
            .as_ref()
            .is_some_and(|t| t.iter().any(|s| s == rules::ENTITY_TAG_QUAD_BIKE))
        {
            rules::KartSpec::default_quad_bike()
        } else if tags
            .as_ref()
            .is_some_and(|t| t.iter().any(|s| s == rules::ENTITY_TAG_POLICE_CAR))
        {
            rules::KartSpec::default_police_car()
        } else if tags
            .as_ref()
            .is_some_and(|t| t.iter().any(|s| s == rules::ENTITY_TAG_DACIA_LOGAN))
        {
            rules::KartSpec::default_police_car()
        } else {
            rules::KartSpec::default()
        };
        st.id_to_uuid.insert(entity_id, uuid);
        st.by_uuid.insert(
            uuid,
            rules::KartRuntime::new(uuid, dimension.to_owned(), default_spec),
        );
        st.dirty = true;
        return Some(uuid);
    }
    None
}

fn pickup_kart_for_player(
    game: &mut Game<'_>,
    st: &mut ServerState,
    who: &NativeServerPlayer,
    entity_id: u32,
) -> bool {
    let Some(uuid) = lookup_kart_uuid(game, st, &who.dimension, entity_id) else {
        return false;
    };
    let Some(rt) = st.by_uuid.remove(&uuid) else {
        return false;
    };
    st.id_to_uuid.remove(&entity_id);
    st.pre_tick_pos.remove(&entity_id);
    st.dirty = true;

    let pos = game
        .native_entity(entity_id)
        .and_then(|e| game.native_entity_position(e))
        .unwrap_or(who.position);
    let _ = game.native_remove_mob(&rt.dimension, entity_id);
    if rt.dimension != who.dimension {
        let _ = game.native_remove_mob(&who.dimension, entity_id);
    }

    let item = make_kart_item(game, rt.spec);
    if let Some(leftover) = game.native_give_stack(who.uuid, item) {
        // Inventory full: drop item cleanly at the Go-Kart's position
        let drop_nbt: Compound = [(
            JavaString::from("Item"),
            Tag::Compound(
                [
                    (
                        JavaString::from("id"),
                        Tag::String(JavaString::from(leftover.item.as_ref())),
                    ),
                    (JavaString::from("count"), Tag::Int(1)),
                ]
                .into_iter()
                .collect(),
            ),
        )]
        .into_iter()
        .collect();
        let _ = game.native_summon(&rt.dimension, "minecraft:item", pos, drop_nbt);
    }

    game.native_play_sound_in_place("gokart:wrench", pos, SOUND_PLAYERS, 0.9, 1.05);
    let msg = tr(
        "gokart.msg.picked_up",
        "Go-Kart packed into inventory (all parts, paint & fuel saved).",
    );
    game.native_action_bar(who.uuid, Text::literal(msg).with_color(text::GREEN));
    broadcast_sync_now(game, st);
    true
}

// ---------------------------------------------------------------------------
// Player Block / Item / Entity Interactions & Commands
// ---------------------------------------------------------------------------

pub(in crate::game) fn use_item_on(
    game: &mut Game<'_>,
    stack: &ItemStack,
    pos: [i32; 3],
    face: [i32; 3],
    claimed: &mut bool,
) {
    if *claimed || !game.native_on(rules::ID) {
        return;
    }
    let item_id = &*stack.item;
    let is_vehicle_item = rules::VehicleKind::from_item(item_id).is_some();
    if !is_vehicle_item && item_id != rules::ITEM_JERRY_CAN {
        return;
    }
    let Some(who) = game.native_acting_player() else {
        return;
    };
    let Some(mut guard) = server_state(game) else {
        return;
    };
    let st = guard.as_mut().expect("server state");

    if is_vehicle_item {
        let spec = read_kart_spec(game, stack);
        let spawn_pos = [
            f64::from(pos[0] + face[0]) + 0.5,
            f64::from(pos[1] + face[1]) + 0.05,
            f64::from(pos[2] + face[2]) + 0.5,
        ];
        if spawn_kart(game, st, &who.dimension, spawn_pos, who.yaw, spec).is_some() {
            *claimed = true;
            if who.game_mode != 1 {
                game.native_take_items(item_id, 1);
            }
            game.native_play_sound_in_place("gokart:wrench", spawn_pos, SOUND_PLAYERS, 0.9, 0.95);
            let msg = match spec.kind {
                rules::VehicleKind::OffRoader => tr(
                    "gokart.msg.placed_off_roader",
                    "4x4 Off-Roader deployed! Right-click to drive, Wrench to tune.",
                ),
                rules::VehicleKind::QuadBike => tr(
                    "gokart.msg.placed_quad_bike",
                    "Quad Bike ATV deployed! Right-click to ride, Wrench to tune.",
                ),
                rules::VehicleKind::PoliceCar => tr(
                    "gokart.msg.placed_police_car",
                    "Poliția Română Patrol Car deployed! Press [H] while driving for Siren & Girofar.",
                ),
                rules::VehicleKind::DaciaLoganPolice => tr(
                    "gokart.msg.placed_dacia_logan",
                    "Dacia Logan Poliția Română deployed! Press [H] while driving for Siren & Girofar.",
                ),
                rules::VehicleKind::GoKart => tr(
                    "gokart.msg.placed",
                    "Go-Kart deployed! Right-click to drive, Wrench to tune.",
                ),
            };
            game.native_action_bar(who.uuid, Text::literal(msg).with_color(text::GREEN));
            broadcast_sync_now(game, st);
        }
        return;
    }

    // Jerry Can world refill on Lava / Magma Block / Coal Block
    let clicked_block = game.native_block(pos);
    let adj_block = game.native_block([pos[0] + face[0], pos[1] + face[1], pos[2] + face[2]]);
    let refill = rules::world_refill_block_mb(&clicked_block)
        .or_else(|| rules::world_refill_block_mb(&adj_block));
    if let Some(add_mb) = refill {
        let cur = read_jerry_fuel(game, stack);
        if cur < rules::JERRY_MAX_FUEL_MB {
            *claimed = true;
            let next = (cur + add_mb).min(rules::JERRY_MAX_FUEL_MB);
            game.native_take_items(rules::ITEM_JERRY_CAN, 1);
            let filled = make_jerry_can(game, next);
            let _ = game.native_give_stack(who.uuid, filled);
            game.native_play_sound_in_place("gokart:refuel", who.position, SOUND_PLAYERS, 0.9, 1.0);
            let msg = tr3(
                "gokart.msg.jerry_refilled",
                "Jerry Can refilled (%1$s / %2$s mB).",
                &next.to_string(),
                &rules::JERRY_MAX_FUEL_MB.to_string(),
                "",
            );
            game.native_action_bar(who.uuid, Text::literal(msg).with_color(text::GOLD));
        }
    }
}

pub(in crate::game) fn use_item(game: &mut Game<'_>, stack: &ItemStack, claimed: &mut bool) {
    if *claimed || !game.native_on(rules::ID) {
        return;
    }
    if &*stack.item == rules::ITEM_WRENCH && game.native_window() {
        *claimed = true;
        lock(&CLIENT).pending_open_garage = true;
    }
}

pub(in crate::game) fn interact_entity(
    game: &mut Game<'_>,
    entity: i32,
    kind: &str,
    stack: Option<&ItemStack>,
    claimed: &mut bool,
) {
    if *claimed || kind != "minecraft:pig" || !game.native_on(rules::ID) {
        return;
    }
    let Ok(entity_id) = u32::try_from(entity) else {
        return;
    };
    let Some(who) = game.native_acting_player() else {
        return;
    };
    let Some(mut guard) = server_state(game) else {
        return;
    };
    let st = guard.as_mut().expect("server state");
    let Some(kart_uuid) = lookup_kart_uuid(game, st, &who.dimension, entity_id) else {
        return;
    };

    st.selected_kart.insert(who.uuid, entity_id);
    let pos = game
        .native_entity(entity_id)
        .and_then(|e| game.native_entity_position(e))
        .unwrap_or(who.position);

    let Some(held) = stack else {
        // Bare hand: let vanilla saddled-pig mount logic seat the player into the Go-Kart!
        return;
    };
    let item_id = &*held.item;

    // 1. Wrench -> Open Garage UI (or if riding nothing & sneaking on client, Garage has 1-click Pack button!)
    if item_id == rules::ITEM_WRENCH {
        *claimed = true;
        game.native_play_sound_in_place("gokart:wrench", pos, SOUND_PLAYERS, 0.85, 1.1);
        broadcast_sync_now(game, st);
        // Signal client to open the Go-Kart Garage & Tuning GUI for `entity_id`
        let mut msg = vec![255_u8];
        msg.extend_from_slice(&entity_id.to_le_bytes());
        let _ = game.native_net_send_to_player(who.uuid, rules::CHAN_SYNC, &msg);
        return;
    }

    // 2. 16 Minecraft Dyes -> Paint the Go-Kart chassis!
    if let Some(paint) = rules::PaintColor::from_dye_item(item_id) {
        *claimed = true;
        if let Some(rt) = st.by_uuid.get_mut(&kart_uuid)
            && rt.spec.paint != paint
        {
            rt.spec.paint = paint;
            st.dirty = true;
            if who.game_mode != 1 {
                game.native_take_items(item_id, 1);
            }
            game.native_play_sound_in_place(
                "minecraft:item.dye.use",
                pos,
                SOUND_PLAYERS,
                0.9,
                1.1,
            );
            let cname = tr(paint.lang_key(), paint.slug());
            let txt = tr1("gokart.msg.painted", "Go-Kart painted %1$s!", &cname);
            game.native_action_bar(who.uuid, Text::literal(txt).with_color(paint.rgb()));
            broadcast_sync_now(game, st);
        }
        return;
    }

    // 3. Small Engines (Iron / Gold / Diamond) -> Upgrade or swap engine!
    if let Some(new_engine) = rules::EngineTier::from_item(item_id) {
        *claimed = true;
        let prev_engine = st
            .by_uuid
            .get(&kart_uuid)
            .map(|rt| rt.spec.engine)
            .unwrap_or(rules::EngineTier::None);
        if prev_engine != new_engine {
            if let Some(rt) = st.by_uuid.get_mut(&kart_uuid) {
                rt.spec.engine = new_engine;
            }
            st.dirty = true;
            if who.game_mode != 1 {
                game.native_take_items(item_id, 1);
                if let Some(old_item) = prev_engine.item_id() {
                    let _ = game.native_give_stack(who.uuid, stack_of(old_item, 1));
                }
            }
            game.native_play_sound_in_place("gokart:wrench", pos, SOUND_PLAYERS, 1.0, 1.0);
            let ename = tr(new_engine.lang_key(), new_engine.slug());
            let txt = tr1("gokart.msg.engine_installed", "Installed %1$s!", &ename);
            game.native_action_bar(who.uuid, Text::literal(txt).with_color(text::GOLD));
            broadcast_sync_now(game, st);
        }
        return;
    }

    // 4. Wheels (Standard / Sports / Racing) -> Swap wheel set!
    if let Some(new_wheels) = rules::WheelType::from_item(item_id) {
        *claimed = true;
        let prev_wheels = st
            .by_uuid
            .get(&kart_uuid)
            .map(|rt| rt.spec.wheels)
            .unwrap_or(rules::WheelType::Standard);
        if prev_wheels != new_wheels {
            if let Some(rt) = st.by_uuid.get_mut(&kart_uuid) {
                rt.spec.wheels = new_wheels;
            }
            st.dirty = true;
            if who.game_mode != 1 {
                game.native_take_items(item_id, 1);
                let _ = game.native_give_stack(who.uuid, stack_of(prev_wheels.item_id(), 1));
            }
            game.native_play_sound_in_place("gokart:wrench", pos, SOUND_PLAYERS, 1.0, 1.18);
            let wname = tr(new_wheels.lang_key(), new_wheels.slug());
            let txt = tr1("gokart.msg.wheels_installed", "Fitted %1$s!", &wname);
            game.native_action_bar(who.uuid, Text::literal(txt).with_color(text::AQUA));
            broadcast_sync_now(game, st);
        }
        return;
    }

    // 5. Jerry Can -> Pour fuel into vehicle tank!
    if item_id == rules::ITEM_JERRY_CAN {
        *claimed = true;
        let jerry_mb = read_jerry_fuel(game, held);
        let (cur_fuel, max_fuel) = st
            .by_uuid
            .get(&kart_uuid)
            .map_or((0, rules::KART_MAX_FUEL_MB), |rt| {
                (rt.spec.fuel_mb, rt.spec.max_fuel_mb())
            });
        let room = max_fuel.saturating_sub(cur_fuel);
        if room == 0 {
            let txt = tr("gokart.msg.tank_full", "Go-Kart fuel tank is already full!");
            game.native_action_bar(who.uuid, Text::literal(txt).with_color(text::YELLOW));
            return;
        }
        let transfer = room.min(jerry_mb).min(1_000);
        if transfer > 0 {
            let pct = if let Some(rt) = st.by_uuid.get_mut(&kart_uuid) {
                rt.spec.fuel_mb += transfer;
                rt.spec.fuel_percent()
            } else {
                0
            };
            st.dirty = true;
            if who.game_mode != 1 {
                game.native_take_items(rules::ITEM_JERRY_CAN, 1);
                let updated = make_jerry_can(game, jerry_mb.saturating_sub(transfer));
                let _ = game.native_give_stack(who.uuid, updated);
            }
            game.native_play_sound_in_place("gokart:refuel", pos, SOUND_PLAYERS, 1.0, 1.0);
            let txt = tr3(
                "gokart.msg.refueled",
                "Refueled Go-Kart (+%1$s mB -> %2$s%%).",
                &transfer.to_string(),
                &pct.to_string(),
                "",
            );
            game.native_action_bar(who.uuid, Text::literal(txt).with_color(text::GREEN));
            broadcast_sync_now(game, st);
        }
        return;
    }

    // 6. Direct emergency fuel items (Coal, Charcoal, Blaze Powder/Rod, Lava Bucket)
    if let Some((restore_mb, remainder)) = rules::direct_fuel_item_mb(item_id) {
        *claimed = true;
        let (cur_fuel, max_fuel) = st
            .by_uuid
            .get(&kart_uuid)
            .map_or((0, rules::KART_MAX_FUEL_MB), |rt| {
                (rt.spec.fuel_mb, rt.spec.max_fuel_mb())
            });
        if cur_fuel >= max_fuel {
            let txt = tr("gokart.msg.tank_full", "Go-Kart fuel tank is already full!");
            game.native_action_bar(who.uuid, Text::literal(txt).with_color(text::YELLOW));
            return;
        }
        let added = (cur_fuel + restore_mb).min(max_fuel) - cur_fuel;
        let pct = if let Some(rt) = st.by_uuid.get_mut(&kart_uuid) {
            rt.spec.fuel_mb += added;
            rt.spec.fuel_percent()
        } else {
            0
        };
        st.dirty = true;
        if who.game_mode != 1 {
            game.native_take_items(item_id, 1);
            if let Some(rem) = remainder {
                let _ = game.native_give_stack(who.uuid, stack_of(rem, 1));
            }
        }
        game.native_play_sound_in_place("gokart:refuel", pos, SOUND_PLAYERS, 0.9, 1.08);
        let txt = tr3(
            "gokart.msg.refueled",
            "Refueled Go-Kart (+%1$s mB -> %2$s%%).",
            &added.to_string(),
            &pct.to_string(),
            "",
        );
        game.native_action_bar(who.uuid, Text::literal(txt).with_color(text::GREEN));
        broadcast_sync_now(game, st);
        return;
    }

    // 7. Block shears, leads, carrot-on-a-stick, and pig food so vanilla never alters our backing pig!
    if matches!(
        item_id,
        "minecraft:shears"
            | "minecraft:lead"
            | "minecraft:carrot_on_a_stick"
            | "minecraft:carrot"
            | "minecraft:potato"
            | "minecraft:beetroot"
            | "minecraft:name_tag"
    ) {
        *claimed = true;
    }
}

pub(in crate::game) fn attack_entity(
    game: &mut Game<'_>,
    entity: i32,
    kind: &str,
    _pos: [f64; 3],
    canceled: &mut bool,
) {
    if *canceled || kind != "minecraft:pig" || !game.native_on(rules::ID) {
        return;
    }
    let Ok(entity_id) = u32::try_from(entity) else {
        return;
    };
    let Some(who) = game.native_acting_player() else {
        return;
    };
    let held_item = game.native_held().map(|(id, _, _)| id).unwrap_or_default();
    let Some(mut guard) = server_state(game) else {
        return;
    };
    let st = guard.as_mut().expect("server state");
    if lookup_kart_uuid(game, st, &who.dimension, entity_id).is_none() {
        return;
    }
    // Always protect Go-Kart from pig hurt/knockback; Wrench hit packs it cleanly into an item!
    *canceled = true;
    if held_item == rules::ITEM_WRENCH {
        pickup_kart_for_player(game, st, &who, entity_id);
    }
}

fn vehicle_kind_from_tags(tags: &[String]) -> Option<rules::VehicleKind> {
    let has_any = tags.iter().any(|t| {
        matches!(
            t.as_str(),
            rules::ENTITY_TAG
                | rules::ENTITY_TAG_OFF_ROADER
                | rules::ENTITY_TAG_QUAD_BIKE
                | rules::ENTITY_TAG_POLICE_CAR
                | rules::ENTITY_TAG_DACIA_LOGAN
        )
    });
    if !has_any {
        return None;
    }
    if tags.iter().any(|t| t == rules::ENTITY_TAG_OFF_ROADER) {
        Some(rules::VehicleKind::OffRoader)
    } else if tags.iter().any(|t| t == rules::ENTITY_TAG_QUAD_BIKE) {
        Some(rules::VehicleKind::QuadBike)
    } else if tags.iter().any(|t| t == rules::ENTITY_TAG_POLICE_CAR) {
        Some(rules::VehicleKind::PoliceCar)
    } else if tags.iter().any(|t| t == rules::ENTITY_TAG_DACIA_LOGAN) {
        Some(rules::VehicleKind::PoliceCar)
    } else {
        Some(rules::VehicleKind::GoKart)
    }
}

/// Discovers ALL vehicle mob IDs in `dimension` — both tracked in `st.id_to_uuid` AND any
/// orphaned `minecraft:pig` carrying `gokart_*` tags from earlier sessions!
fn discover_vehicle_mobs(
    game: &Game<'_>,
    st: &ServerState,
    dimension: &str,
) -> Vec<(u32, [f64; 3])> {
    let mut found: BTreeMap<u32, [f64; 3]> = BTreeMap::new();
    for (&eid, &uuid) in &st.id_to_uuid {
        if st
            .by_uuid
            .get(&uuid)
            .is_some_and(|rt| rt.dimension != dimension)
        {
            continue;
        }
        if let Some(eref) = game.native_entity(eid)
            && let Some(pos) = game.native_entity_position(eref)
        {
            found.insert(eid, pos);
        }
    }
    for mob in game.native_mobs(dimension) {
        if mob.kind != "minecraft:pig" || found.contains_key(&mob.id) {
            continue;
        }
        if let Some(eref) = game.native_entity(mob.id)
            && let Some(tags) = game.native_entity_tags(eref)
            && vehicle_kind_from_tags(&tags).is_some()
        {
            found.insert(mob.id, mob.pos);
        }
    }
    found.into_iter().collect()
}

fn delete_kart_entity(
    game: &mut Game<'_>,
    st: &mut ServerState,
    dimension: &str,
    entity_id: u32,
) -> Option<(rules::VehicleKind, [f64; 3])> {
    let pos = game
        .native_entity(entity_id)
        .and_then(|e| game.native_entity_position(e));
    let tag_kind = game
        .native_entity(entity_id)
        .and_then(|e| game.native_entity_tags(e))
        .and_then(|t| vehicle_kind_from_tags(&t));

    let tracked_uuid = lookup_kart_uuid(game, st, dimension, entity_id);
    let mut removed_kind = tag_kind;
    let mut target_dim = dimension.to_owned();

    if let Some(uuid) = tracked_uuid {
        if let Some(rt) = st.by_uuid.remove(&uuid) {
            removed_kind = Some(rt.spec.kind);
            target_dim = rt.dimension;
        }
    }
    st.id_to_uuid.remove(&entity_id);
    st.pre_tick_pos.remove(&entity_id);
    st.selected_kart.retain(|_, &mut v| v != entity_id);

    let killed_target = game.native_remove_mob(&target_dim, entity_id);
    let killed_here = if target_dim != dimension {
        game.native_remove_mob(dimension, entity_id)
    } else {
        false
    };
    let _ = game.native_remove_entity(&target_dim, entity_id);

    if killed_target || killed_here || removed_kind.is_some() {
        st.dirty = true;
        Some((
            removed_kind.unwrap_or(rules::VehicleKind::GoKart),
            pos.unwrap_or([0.0, 64.0, 0.0]),
        ))
    } else {
        None
    }
}

fn closest_kart_id(
    game: &Game<'_>,
    st: &ServerState,
    player: &NativeServerPlayer,
    max_dist: f64,
) -> Option<u32> {
    if let Some(rid) = game.riding
        && let Some(eref) = game.native_entity(rid)
        && (st.id_to_uuid.contains_key(&rid)
            || game
                .native_entity_tags(eref)
                .is_some_and(|t| vehicle_kind_from_tags(&t).is_some()))
    {
        return Some(rid);
    }
    let max_d2 = max_dist * max_dist;
    let mut best: Option<(u32, f64)> = None;
    for (eid, pos) in discover_vehicle_mobs(game, st, &player.dimension) {
        let dx = pos[0] - player.position[0];
        let dy = pos[1] - player.position[1];
        let dz = pos[2] - player.position[2];
        let d2 = dx * dx + dy * dy + dz * dz;
        if d2 <= max_d2 && best.is_none_or(|(_, b)| d2 < b) {
            best = Some((eid, d2));
        }
    }
    best.map(|(id, _)| id)
}

pub(in crate::game) fn perform_command(
    game: &mut Game<'_>,
    player: &NativeServerPlayer,
    command: &str,
    ran: &mut bool,
) {
    let trimmed = command.trim().trim_start_matches('/');
    let first = trimmed.split_whitespace().next().unwrap_or("");
    if *ran
        || !matches!(first, "vehicle" | "vehicel" | "gokart")
        || !game.native_on(rules::ID)
    {
        return;
    }
    *ran = true;
    let rest = trimmed.strip_prefix(first).unwrap_or("").trim();
    let Some(mut guard) = server_state(game) else {
        return;
    };
    let st = guard.as_mut().expect("server state");

    if rest == "clear"
        || rest == "remove"
        || rest.starts_with("remove ")
        || rest == "delete"
        || rest.starts_with("delete ")
        || rest == "rm"
        || rest.starts_with("rm ")
    {
        let sub_arg = if rest == "clear" {
            "all"
        } else {
            rest.split_once(char::is_whitespace)
                .map(|(_, a)| a.trim())
                .unwrap_or("")
        };
        if sub_arg.eq_ignore_ascii_case("all") || sub_arg == "*" {
            let candidates = discover_vehicle_mobs(game, st, &player.dimension);
            let mut removed_count = 0usize;
            for (eid, _) in candidates {
                if delete_kart_entity(game, st, &player.dimension, eid).is_some() {
                    removed_count += 1;
                }
            }
            // Also prune any stale saved UUIDs in this dimension whose mobs were unloaded/gone
            st.by_uuid.retain(|_, rt| rt.dimension != player.dimension);
            st.id_to_uuid.retain(|&id, _| game.native_entity(id).is_some());
            st.dirty = true;
            sync_headlight_blocks(game, st);
            flush_server_save(st);
            broadcast_sync_now(game, st);
            let msg = tr1(
                "gokart.msg.removed_many",
                "Removed %1$s vehicle(s) from the world.",
                &removed_count.to_string(),
            );
            game.native_tell(player.uuid, Text::literal(msg).with_color(text::GREEN));
            return;
        }
        if let Ok(radius) = sub_arg.parse::<f64>()
            && radius > 0.0
        {
            let r2 = radius * radius;
            let candidates = discover_vehicle_mobs(game, st, &player.dimension);
            let mut removed_count = 0usize;
            for (eid, pos) in candidates {
                let dx = pos[0] - player.position[0];
                let dy = pos[1] - player.position[1];
                let dz = pos[2] - player.position[2];
                if dx * dx + dy * dy + dz * dz <= r2
                    && delete_kart_entity(game, st, &player.dimension, eid).is_some()
                {
                    removed_count += 1;
                }
            }
            sync_headlight_blocks(game, st);
            flush_server_save(st);
            broadcast_sync_now(game, st);
            let msg = tr1(
                "gokart.msg.removed_many",
                "Removed %1$s vehicle(s) from the world.",
                &removed_count.to_string(),
            );
            game.native_tell(player.uuid, Text::literal(msg).with_color(text::GREEN));
            return;
        }
        if let Some(eid) = closest_kart_id(game, st, player, 16.0)
            && let Some((vkind, pos)) = delete_kart_entity(game, st, &player.dimension, eid)
        {
            game.native_play_sound_in_place("gokart:wrench", pos, SOUND_PLAYERS, 0.9, 0.95);
            sync_headlight_blocks(game, st);
            flush_server_save(st);
            broadcast_sync_now(game, st);
            let vname = tr(vkind.lang_key(), vkind.slug());
            let msg = tr1("gokart.msg.removed_one", "Removed %1$s!", &vname);
            game.native_tell(player.uuid, Text::literal(msg).with_color(text::GREEN));
        } else {
            let msg = tr(
                "gokart.msg.remove_none",
                "No vehicle nearby to remove (use /vehicle remove all to clear all).",
            );
            game.native_tell(player.uuid, Text::literal(msg).with_color(text::YELLOW));
        }
        return;
    }

    if rest == "pack" {
        if let Some(eid) = closest_kart_id(game, st, player, 8.0) {
            pickup_kart_for_player(game, st, player, eid);
        } else {
            let msg = tr("gokart.msg.remove_none", "No vehicle nearby.");
            game.native_tell(player.uuid, Text::literal(msg).with_color(text::YELLOW));
        }
        return;
    }

    if rest == "kit" {
        let items_to_give = [
            make_kart_item(game, rules::KartSpec::default()),
            make_kart_item(game, rules::KartSpec::default_quad_bike()),
            make_kart_item(game, rules::KartSpec::default_off_roader()),
            make_kart_item(game, rules::KartSpec::default_police_car()),
            stack_of(rules::ITEM_ENGINE_GOLD, 1),
            stack_of(rules::ITEM_ENGINE_DIAMOND, 1),
            stack_of(rules::ITEM_WHEEL_SPORTS, 1),
            stack_of(rules::ITEM_WHEEL_RACING, 1),
            stack_of(rules::ITEM_WRENCH, 1),
            make_jerry_can(game, rules::JERRY_MAX_FUEL_MB),
            stack_of("minecraft:blue_dye", 4),
            stack_of("minecraft:yellow_dye", 4),
            stack_of("minecraft:lime_dye", 4),
        ];
        for s in items_to_give {
            let _ = game.native_give_stack(player.uuid, s);
        }
        let msg = tr(
            "gokart.msg.kit_given",
            "Delivered complete Go-Kart, ATV, 4x4 & Poliția Română Kit!",
        );
        game.native_tell(player.uuid, Text::literal(msg).with_color(text::GOLD));
        return;
    }

    if rest == "spawn" || rest.starts_with("spawn ") {
        let arg = rest.strip_prefix("spawn").unwrap_or("").trim();
        let spec = if matches!(arg, "off_roader" | "offroader" | "4x4" | "jeep") {
            rules::KartSpec::default_off_roader()
        } else if matches!(arg, "quad_bike" | "quadbike" | "quad" | "atv") {
            rules::KartSpec::default_quad_bike()
        } else if matches!(arg, "police_car" | "policecar" | "police" | "politia" | "politie" | "bmw") {
            rules::KartSpec::default_police_car()
        } else {
            rules::KartSpec::default()
        };
        let yaw_rad = player.yaw.to_radians();
        let dist = match spec.kind {
            rules::VehicleKind::OffRoader
            | rules::VehicleKind::PoliceCar
            | rules::VehicleKind::DaciaLoganPolice => 3.2,
            rules::VehicleKind::QuadBike => 2.5,
            rules::VehicleKind::GoKart => 2.4,
        };
        let at = [
            player.position[0] - f64::from(yaw_rad.sin()) * dist,
            player.position[1] + 0.1,
            player.position[2] + f64::from(yaw_rad.cos()) * dist,
        ];
        if spawn_kart(game, st, &player.dimension, at, player.yaw, spec).is_some() {
            broadcast_sync_now(game, st);
            let msg = match spec.kind {
                rules::VehicleKind::OffRoader => {
                    tr("gokart.msg.placed_off_roader", "4x4 Off-Roader deployed!")
                }
                rules::VehicleKind::QuadBike => {
                    tr("gokart.msg.placed_quad_bike", "Quad Bike ATV deployed!")
                }
                rules::VehicleKind::PoliceCar => {
                    tr("gokart.msg.placed_police_car", "Poliția Română Patrol Car deployed!")
                }
                rules::VehicleKind::DaciaLoganPolice => {
                    tr("gokart.msg.placed_dacia_logan", "Dacia Logan Poliția Română deployed!")
                }
                rules::VehicleKind::GoKart => tr("gokart.msg.placed", "Go-Kart deployed!"),
            };
            game.native_tell(player.uuid, Text::literal(msg).with_color(text::GREEN));
        }
        return;
    }

    if rest == "fuel" {
        st.require_fuel = !st.require_fuel;
        st.dirty = true;
        broadcast_sync_now(game, st);
        let msg = if st.require_fuel {
            tr("gokart.msg.fuel_mode_on", "Go-Kart fuel consumption: ENABLED")
        } else {
            tr("gokart.msg.fuel_mode_off", "Go-Kart fuel consumption: INFINITE FUEL")
        };
        game.native_tell(player.uuid, Text::literal(msg).with_color(text::AQUA));
        return;
    }

    if let Some(color_arg) = rest.strip_prefix("paint ") {
        let paint = rules::PaintColor::from_slug(color_arg);
        if let Some(kart_id) = closest_kart_id(game, st, player, 8.0)
            && let Some(&u) = st.id_to_uuid.get(&kart_id)
            && let Some(rt) = st.by_uuid.get_mut(&u)
        {
            rt.spec.paint = paint;
            st.dirty = true;
            broadcast_sync_now(game, st);
            let cname = tr(paint.lang_key(), paint.slug());
            let txt = tr1("gokart.msg.painted", "Vehicle painted %1$s!", &cname);
            game.native_tell(player.uuid, Text::literal(txt).with_color(paint.rgb()));
        }
        return;
    }

    game.native_tell(
        player.uuid,
        Text::literal(
            "/vehicle [remove | remove all | clear | spawn [go_kart|quad_bike|off_roader|police] | pack | kit | fuel | paint <color>]",
        )
        .with_color(text::YELLOW),
    );
}

fn nearest_kart_id(
    game: &Game<'_>,
    st: &ServerState,
    player: &NativeServerPlayer,
    max_dist: f64,
) -> Option<u32> {
    if let Some(&sel) = st.selected_kart.get(&player.uuid)
        && let Some(eref) = game.native_entity(sel)
        && game
            .native_entity_distance_to_sqr(eref, player.position)
            .is_some_and(|d2| d2 <= max_dist * max_dist)
    {
        return Some(sel);
    }
    let mut best: Option<(u32, f64)> = None;
    for &id in st.id_to_uuid.keys() {
        let Some(eref) = game.native_entity(id) else {
            continue;
        };
        let Some(d2) = game.native_entity_distance_to_sqr(eref, player.position) else {
            continue;
        };
        if d2 <= max_dist * max_dist && best.is_none_or(|(_, b)| d2 < b) {
            best = Some((id, d2));
        }
    }
    best.map(|(id, _)| id)
}

// ---------------------------------------------------------------------------
// Server Entity Physics Tick & Network Synchronization
// ---------------------------------------------------------------------------

pub(in crate::game) fn entity_tick_listened(game: &mut Game<'_>, listened: &mut bool) {
    if game.native_on(rules::ID) {
        *listened = true;
    }
}

fn find_rider_uuid(
    game: &Game<'_>,
    players: &[NativeServerPlayer],
    entity_id: u32,
    kart_pos: [f64; 3],
) -> Option<u128> {
    if game.riding == Some(entity_id)
        && let Some(host) = players.first()
    {
        return Some(host.uuid);
    }
    let seat_y_pig = kart_pos[1] + SEAT_HEIGHT_PIG;
    let seat_y_kart = kart_pos[1] + f64::from(rules::SEAT_ATTACH_Y) - 0.6;
    let seat_y_off =
        kart_pos[1] + f64::from(rules::VehicleKind::OffRoader.layout().seat_attach[1]) - 0.6;
    let seat_y_quad =
        kart_pos[1] + f64::from(rules::VehicleKind::QuadBike.layout().seat_attach[1]) - 0.6;
    let seat_y_pol =
        kart_pos[1] + f64::from(rules::VehicleKind::PoliceCar.layout().seat_attach[1]) - 0.6;
    let seat_y_logan =
        kart_pos[1] + f64::from(rules::VehicleKind::DaciaLoganPolice.layout().seat_attach[1]) - 0.6;
    players.iter().find_map(|p| {
        let dx = p.position[0] - kart_pos[0];
        let dz = p.position[2] - kart_pos[2];
        let dy_ok = (p.position[1] - seat_y_kart).abs() < 0.55
            || (p.position[1] - seat_y_off).abs() < 0.55
            || (p.position[1] - seat_y_quad).abs() < 0.55
            || (p.position[1] - seat_y_pol).abs() < 0.55
            || (p.position[1] - seat_y_logan).abs() < 0.55
            || (p.position[1] - seat_y_pig).abs() < 0.55;
        (dx * dx + dz * dz < 1.15 && dy_ok).then_some(p.uuid)
    })
}

pub(in crate::game) fn entity_tick_pre(
    game: &mut Game<'_>,
    dimension: &str,
    entity: u32,
    kind: &str,
    _canceled: &mut bool,
) {
    if kind != "minecraft:pig" || !game.native_on(rules::ID) {
        return;
    }
    let Some(mut guard) = server_state(game) else {
        return;
    };
    let st = guard.as_mut().expect("server state");
    let Some(kart_uuid) = lookup_kart_uuid(game, st, dimension, entity) else {
        return;
    };

    // Keep vanilla pig AI completely inert while leaving `travel` enabled for collisions & step-up
    let mut on_ground = true;
    let mut in_water = false;
    if let Some(m) = game.mobs.iter_mut().find(|m| m.id == entity) {
        m.ai.goals.clear();
        m.ai.targets.clear();
        m.extra.saddled = true;
        m.silent = true;
        m.invulnerable_flag = true;
        on_ground = m.on_ground;
        in_water = m.fluids.in_water;
    }

    let Some(eref) = game.native_entity(entity) else {
        return;
    };
    let Some(pos) = game.native_entity_position(eref) else {
        return;
    };
    let cur_yaw = game.native_entity_rotation(eref).map_or(0.0, |r| r[0]);
    let cur_vel = game.native_entity_velocity(eref).unwrap_or([0.0, 0.0, 0.0]);

    let below_pos = [
        pos[0].floor() as i32,
        (pos[1] - 0.2).floor() as i32,
        pos[2].floor() as i32,
    ];
    let surface = rules::SurfaceKind::from_block_name(&game.native_block(below_pos));

    let players = game.native_server_players();
    let rider_uuid = find_rider_uuid(game, &players, entity, pos);
    if let Some(ruuid) = rider_uuid {
        st.selected_kart.insert(ruuid, entity);
    }
    let input = rider_uuid
        .and_then(|u| st.inputs.get(&u).copied())
        .unwrap_or_default();

    let require_fuel = st.require_fuel;
    let Some(rt) = st.by_uuid.get_mut(&kart_uuid) else {
        return;
    };
    rt.dimension = dimension.to_owned();
    let prev_fuel = rt.spec.fuel_mb;
    let outcome = rt.step(
        cur_yaw,
        cur_vel,
        on_ground,
        in_water,
        surface,
        rider_uuid.is_some(),
        input,
        require_fuel,
    );
    let vlay = rt.spec.kind.layout();
    let tick_count = rt.tick_count;
    let drifting = rt.drifting;
    let burnout = rt.burnout;
    let boosting = rt.boost_ticks > 0;
    let siren_active = rt.spec.kind.is_police() && rt.siren_on;
    let fuel_changed = rt.spec.fuel_mb != prev_fuel;
    if fuel_changed {
        st.dirty = true;
    }
    st.pre_tick_pos
        .insert(entity, (pos, outcome.yaw_deg));

    game.native_entity_set_rotation(eref, outcome.yaw_deg, 0.0);
    game.native_entity_set_head_yaw(eref, outcome.yaw_deg);
    game.native_entity_set_velocity(eref, outcome.velocity);

    if siren_active && tick_count.is_multiple_of(26) {
        game.native_play_sound_in_place("gokart:siren", pos, SOUND_PLAYERS, 0.95, 1.0);
    }

    // Exhaust, drift screech, engine rumble & turbo boost FX at exact 3D component coords!
    let yaw_rad = outcome.yaw_deg.to_radians();
    let fwd_x = f64::from(-yaw_rad.sin());
    let fwd_z = f64::from(yaw_rad.cos());
    let left_x = f64::from(yaw_rad.cos());
    let left_z = f64::from(yaw_rad.sin());

    let exh_z = f64::from(vlay.exhaust_offset_z);
    let exhaust_pos = [
        pos[0] + fwd_x * exh_z,
        pos[1] + f64::from(vlay.exhaust_height_y),
        pos[2] + fwd_z * exh_z,
    ];
    let rear_z = f64::from(vlay.rear_axle_z);
    let rear_x = f64::from(vlay.rear_track_half_x);
    let rear_left_patch = [
        pos[0] + fwd_x * rear_z + left_x * rear_x,
        pos[1] + 0.05,
        pos[2] + fwd_z * rear_z + left_z * rear_x,
    ];
    let rear_right_patch = [
        pos[0] + fwd_x * rear_z - left_x * rear_x,
        pos[1] + 0.05,
        pos[2] + fwd_z * rear_z - left_z * rear_x,
    ];

    if outcome.boost_triggered {
        game.native_play_sound_in_place("gokart:boost", pos, SOUND_NEUTRAL, 1.0, 1.05);
        let flame = ParticleOptions::simple(ParticleType::Flame);
        game.native_send_particles_in_place(
            &flame,
            None,
            exhaust_pos,
            [0.14, 0.06, 0.14],
            0.06,
            10,
        );
    }

    if let Some(pitch) = outcome.engine_sound_pitch
        && tick_count.is_multiple_of(5)
    {
        let vol = if rider_uuid.is_some() { 0.34 } else { 0.16 };
        game.native_play_sound_in_place("gokart:engine.pulse", pos, SOUND_NEUTRAL, vol, pitch);
        let smoke = ParticleOptions::simple(ParticleType::Smoke);
        game.native_send_particles_in_place(
            &smoke,
            None,
            exhaust_pos,
            [0.05, 0.03, 0.05],
            0.01,
            1,
        );
    }

    if outcome.tire_smoke && tick_count.is_multiple_of(2) {
        let smoke = ParticleOptions::simple(ParticleType::Smoke);
        let count = if burnout || boosting { 2 } else { 1 };
        for patch in [rear_left_patch, rear_right_patch] {
            game.native_send_particles_in_place(
                &smoke,
                None,
                patch,
                [0.10, 0.04, 0.10],
                0.015,
                count,
            );
        }
        if (drifting || burnout) && tick_count.is_multiple_of(6) {
            game.native_play_sound_in_place("gokart:drift", pos, SOUND_NEUTRAL, 0.42, 1.0);
        }
    }
}

pub(in crate::game) fn entity_tick_post(game: &mut Game<'_>, _dimension: &str, entity: u32, kind: &str) {
    if kind != "minecraft:pig" || !game.native_on(rules::ID) {
        return;
    }
    let Some(mut guard) = server_state(game) else {
        return;
    };
    let st = guard.as_mut().expect("server state");
    let Some(&(pre_pos, target_yaw)) = st.pre_tick_pos.get(&entity) else {
        return;
    };
    let Some(&uuid) = st.id_to_uuid.get(&entity) else {
        return;
    };

    // Keep body_yaw and yaw locked to Go-Kart chassis heading after `ai::tick`
    if let Some(m) = game.mobs.iter_mut().find(|m| m.id == entity) {
        m.yaw = target_yaw;
        m.body_yaw = target_yaw;
        m.head_yaw = target_yaw;
    }
    if let Some(eref) = game.native_entity(entity)
        && let Some(after_pos) = game.native_entity_position(eref)
        && let Some(rt) = st.by_uuid.get_mut(&uuid)
    {
        let moved_xz = (after_pos[0] - pre_pos[0]).hypot(after_pos[2] - pre_pos[2]) as f32;
        let expected_xz = rt.vel_xz[0].hypot(rt.vel_xz[1]);
        // Wall collision damping: if block collision stopped horizontal travel, damp momentum!
        if expected_xz > 0.14 && moved_xz < expected_xz * 0.35 {
            rt.forward_speed *= 0.30;
            rt.vel_xz = [rt.vel_xz[0] * 0.30, rt.vel_xz[1] * 0.30];
            if expected_xz > 0.38 {
                game.native_play_sound_in_place(
                    "minecraft:block.anvil.place",
                    after_pos,
                    SOUND_NEUTRAL,
                    0.35,
                    1.5,
                );
            }
        }
    }
}

fn sync_headlight_blocks(game: &mut Game<'_>, st: &mut ServerState) {
    // Minecraft dusk/night is 12,500..=23,500 ticks on the 24,000-tick day cycle!
    let tod = game.world.day_time.rem_euclid(24_000);
    let overworld_night = (12_500..=23_500).contains(&tod);

    let mut desired: BTreeSet<(String, [i32; 3])> = BTreeSet::new();
    for (&eid, &uuid) in &st.id_to_uuid {
        let Some(rt) = st.by_uuid.get(&uuid) else {
            continue;
        };
        let night_here = overworld_night || rt.dimension != "minecraft:overworld";
        if !night_here {
            continue;
        }
        let Some(eref) = game.native_entity(eid) else {
            continue;
        };
        let Some(pos) = game.native_entity_position(eref) else {
            continue;
        };
        let yaw = game.native_entity_rotation(eref).map_or(0.0, |r| r[0]);
        let yaw_rad = yaw.to_radians();
        let fwd_x = f64::from(-yaw_rad.sin());
        let fwd_z = f64::from(yaw_rad.cos());
        let nose = f64::from(rt.spec.kind.layout().nose_light_dist);

        // Project a real FiveM headlight cone (near bumper + road beam ahead)!
        for d in [nose, nose + 2.1] {
            let bx = (pos[0] + fwd_x * d).floor() as i32;
            let by = (pos[1] + 0.65).floor() as i32;
            let bz = (pos[2] + fwd_z * d).floor() as i32;
            desired.insert((rt.dimension.clone(), [bx, by, bz]));
        }
    }

    if desired == st.active_lights {
        return;
    }

    // 1. Remove stale `minecraft:light` blocks (strictly filtered by `only = "minecraft:light"`!)
    let mut to_clear: BTreeMap<String, Vec<NativeBlockRun>> = BTreeMap::new();
    for (dim, pos) in &st.active_lights {
        if !desired.contains(&(dim.clone(), *pos)) {
            to_clear.entry(dim.clone()).or_default().push(NativeBlockRun {
                x: pos[0],
                y: pos[1],
                z: pos[2],
                height: 1,
                surface: None,
                block: 0,
                only: Some(0),
            });
        }
    }
    for (dim, runs) in to_clear {
        let edit = NativeBlockEdit {
            palette: vec!["minecraft:air".into()],
            filters: vec!["minecraft:light".into()],
            runs,
            neighbour_updates: true,
            block_entities: Vec::new(),
        };
        let _ = game.native_edit_blocks(&dim, &edit);
    }

    // 2. Place new `minecraft:light[level=15]` blocks ONLY into `minecraft:air`!
    let mut to_place: BTreeMap<String, Vec<NativeBlockRun>> = BTreeMap::new();
    for (dim, pos) in &desired {
        if !st.active_lights.contains(&(dim.clone(), *pos)) {
            to_place.entry(dim.clone()).or_default().push(NativeBlockRun {
                x: pos[0],
                y: pos[1],
                z: pos[2],
                height: 1,
                surface: None,
                block: 0,
                only: Some(0),
            });
        }
    }
    for (dim, runs) in to_place {
        let edit = NativeBlockEdit {
            palette: vec!["minecraft:light[level=15]".into()],
            filters: vec!["minecraft:air".into()],
            runs,
            neighbour_updates: true,
            block_entities: Vec::new(),
        };
        let _ = game.native_edit_blocks(&dim, &edit);
    }

    st.active_lights = desired;
    st.dirty = true;
}

pub(in crate::game) fn server_tick(game: &mut Game<'_>, phase: ServerTickPhase) {
    if !matches!(phase, ServerTickPhase::ServerTickEnd { world_running: true })
        || !game.native_on(rules::ID)
    {
        return;
    }
    let Some(mut guard) = server_state(game) else {
        return;
    };
    let st = guard.as_mut().expect("server state");
    st.tick = st.tick.wrapping_add(1);

    // Prune stale entity IDs whose entities left loaded chunks
    st.id_to_uuid.retain(|&id, _| game.native_entity(id).is_some());

    if st.tick.is_multiple_of(2) {
        sync_headlight_blocks(game, st);
        broadcast_sync_now(game, st);
    }
    if st.tick.is_multiple_of(SAVE_INTERVAL_TICKS) {
        flush_server_save(st);
    }
}

fn broadcast_sync_now(game: &mut Game<'_>, st: &ServerState) {
    let mut views = Vec::with_capacity(st.id_to_uuid.len());
    for (&entity_id, &uuid) in &st.id_to_uuid {
        if let Some(rt) = st.by_uuid.get(&uuid) {
            let speed_kmh = rt.vel_xz[0].hypot(rt.vel_xz[1]) * 20.0 * 3.6;
            views.push(rules::ClientKartView {
                entity_id,
                spec: rt.spec,
                steer_deg: rt.steer_deg,
                wheel_rot_deg: rt.wheel_rot_deg,
                speed_kmh,
                boost_charge: rt.boost_charge,
                drifting: rt.drifting,
                burnout: rt.burnout,
                boosting: rt.boost_ticks > 0,
                siren_on: rt.siren_on,
            });
        }
    }
    let payload = rules::encode_sync_packet(st.require_fuel, &views);
    for p in game.native_server_players() {
        let _ = game.native_net_send_to_player(p.uuid, rules::CHAN_SYNC, &payload);
    }
}

pub(in crate::game) fn player_logged_in(game: &mut Game<'_>, player: u128) {
    if !game.native_on(rules::ID) {
        return;
    }
    let Some(mut guard) = server_state(game) else {
        return;
    };
    let st = guard.as_mut().expect("server state");
    let mut views = Vec::new();
    for (&entity_id, &uuid) in &st.id_to_uuid {
        if let Some(rt) = st.by_uuid.get(&uuid) {
            views.push(rules::ClientKartView {
                entity_id,
                spec: rt.spec,
                steer_deg: rt.steer_deg,
                wheel_rot_deg: rt.wheel_rot_deg,
                speed_kmh: 0.0,
                boost_charge: 0.0,
                drifting: false,
                burnout: false,
                boosting: false,
                siren_on: rt.siren_on,
            });
        }
    }
    let payload = rules::encode_sync_packet(st.require_fuel, &views);
    let _ = game.native_net_send_to_player(player, rules::CHAN_SYNC, &payload);
}

pub(in crate::game) fn world_lifecycle(phase: WorldPhase) {
    if matches!(phase, WorldPhase::WorldCloseFinal | WorldPhase::WorldCloseFailed) {
        if let Some(st) = lock(&SERVER).as_mut() {
            flush_server_save(st);
        }
        *lock(&SERVER) = None;
        let mut c = lock(&CLIENT);
        c.karts.clear();
        c.was_riding_kart = false;
        c.garage_target_entity = None;
    }
}

// ---------------------------------------------------------------------------
// Network Channels (`CHAN_INPUT`, `CHAN_ACTION`, `CHAN_SYNC`)
// ---------------------------------------------------------------------------

pub(in crate::game) fn net_from_client(
    game: &mut Game<'_>,
    player: u128,
    channel: &str,
    data: &[u8],
) {
    if !game.native_on(rules::ID) {
        return;
    }
    if channel == rules::CHAN_INPUT {
        if let Some(input) = rules::DriveInput::decode_packet(data)
            && let Some(mut guard) = server_state(game)
            && let Some(st) = guard.as_mut()
        {
            st.inputs.insert(player, input);
        }
        return;
    }
    if channel != rules::CHAN_ACTION || data.is_empty() {
        return;
    }

    let action = data[0];
    let target_arg = if data.len() >= 5 {
        Some(u32::from_le_bytes([data[1], data[2], data[3], data[4]]))
    } else {
        None
    };

    let Some(who) = game.native_server_players().into_iter().find(|p| p.uuid == player) else {
        return;
    };
    let Some(mut guard) = server_state(game) else {
        return;
    };
    let st = guard.as_mut().expect("server state");

    match action {
        rules::ACT_HORN => {
            let kart_id = target_arg.or_else(|| closest_kart_id(game, st, &who, 5.0));
            let sound_pos = kart_id
                .and_then(|id| game.native_entity(id))
                .and_then(|e| game.native_entity_position(e))
                .unwrap_or(who.position);
            if let Some(kid) = kart_id
                && let Some(&uuid) = st.id_to_uuid.get(&kid)
                && let Some(rt) = st.by_uuid.get_mut(&uuid)
                && rt.spec.kind.is_police()
            {
                rt.siren_on = !rt.siren_on;
                let now_on = rt.siren_on;
                if now_on {
                    game.native_play_sound_in_place(
                        "gokart:siren",
                        sound_pos,
                        SOUND_PLAYERS,
                        1.0,
                        1.0,
                    );
                    let txt = tr(
                        "gokart.msg.siren_on",
                        "Police Siren & Girofar: ON [H]",
                    );
                    game.native_action_bar(player, Text::literal(txt).with_color(text::AQUA));
                } else {
                    let txt = tr(
                        "gokart.msg.siren_off",
                        "Police Siren & Girofar: OFF",
                    );
                    game.native_action_bar(player, Text::literal(txt).with_color(text::GRAY));
                }
                broadcast_sync_now(game, st);
            } else {
                game.native_play_sound_in_place("gokart:horn", sound_pos, SOUND_PLAYERS, 1.15, 1.0);
            }
        }
        rules::ACT_PICKUP_KART => {
            if let Some(kart_id) = target_arg.or_else(|| nearest_kart_id(game, st, &who, 8.0)) {
                drop(guard);
                game.native_as_player(player, |g| {
                    if let Some(mut g2) = server_state(g)
                        && let Some(s2) = g2.as_mut()
                    {
                        pickup_kart_for_player(g, s2, &who, kart_id);
                        sync_headlight_blocks(g, s2);
                    }
                });
            }
        }
        rules::ACT_DELETE_KART => {
            if let Some(kart_id) = target_arg.or_else(|| closest_kart_id(game, st, &who, 10.0))
                && let Some((vkind, pos)) = delete_kart_entity(game, st, &who.dimension, kart_id)
            {
                game.native_play_sound_in_place("gokart:wrench", pos, SOUND_PLAYERS, 0.9, 0.95);
                sync_headlight_blocks(game, st);
                flush_server_save(st);
                broadcast_sync_now(game, st);
                let vname = tr(vkind.lang_key(), vkind.slug());
                let msg = tr1("gokart.msg.removed_one", "Removed %1$s!", &vname);
                game.native_action_bar(player, Text::literal(msg).with_color(text::GREEN));
            }
        }
        rules::ACT_EJECT_ENGINE => {
            if let Some(kart_id) = target_arg.or_else(|| nearest_kart_id(game, st, &who, 6.0))
                && let Some(&uuid) = st.id_to_uuid.get(&kart_id)
                && let Some(rt) = st.by_uuid.get_mut(&uuid)
                && let Some(engine_item) = rt.spec.engine.item_id()
            {
                let old = rt.spec.engine;
                rt.spec.engine = rules::EngineTier::None;
                st.dirty = true;
                let _ = game.native_give_stack(player, stack_of(engine_item, 1));
                game.native_play_sound_in_place("gokart:wrench", who.position, SOUND_PLAYERS, 0.9, 0.9);
                let ename = tr(old.lang_key(), old.slug());
                let txt = tr1("gokart.msg.engine_removed", "Removed %1$s from Go-Kart.", &ename);
                game.native_action_bar(player, Text::literal(txt).with_color(text::YELLOW));
                broadcast_sync_now(game, st);
            }
        }
        rules::ACT_REFUEL_INV => {
            let Some(kart_id) = target_arg.or_else(|| nearest_kart_id(game, st, &who, 6.0)) else {
                return;
            };
            let Some(&uuid) = st.id_to_uuid.get(&kart_id) else {
                return;
            };
            let (cur_fuel, max_fuel) = st
                .by_uuid
                .get(&uuid)
                .map_or((0, rules::KART_MAX_FUEL_MB), |rt| {
                    (rt.spec.fuel_mb, rt.spec.max_fuel_mb())
                });
            if cur_fuel >= max_fuel {
                let txt = tr("gokart.msg.tank_full", "Go-Kart fuel tank is already full!");
                game.native_action_bar(player, Text::literal(txt).with_color(text::YELLOW));
                return;
            }
            drop(guard);
            let mut added_mb = 0_u32;
            game.native_as_player(player, |g| {
                for (item_id, mb) in [
                    ("minecraft:coal", 250_u32),
                    ("minecraft:charcoal", 250_u32),
                    ("minecraft:blaze_powder", 400_u32),
                    ("minecraft:blaze_rod", 800_u32),
                ] {
                    if g.native_take_items(item_id, 1) > 0 {
                        added_mb = mb;
                        break;
                    }
                }
            });
            if added_mb > 0
                && let Some(mut g2) = server_state(game)
                && let Some(s2) = g2.as_mut()
                && let Some(rt) = s2.by_uuid.get_mut(&uuid)
            {
                let before = rt.spec.fuel_mb;
                let cap = rt.spec.max_fuel_mb();
                rt.spec.fuel_mb = (before + added_mb).min(cap);
                let actual = rt.spec.fuel_mb - before;
                let pct = rt.spec.fuel_percent();
                s2.dirty = true;
                game.native_play_sound_in_place("gokart:refuel", who.position, SOUND_PLAYERS, 1.0, 1.0);
                let txt = tr3(
                    "gokart.msg.refueled",
                    "Refueled Go-Kart (+%1$s mB -> %2$s%%).",
                    &actual.to_string(),
                    &pct.to_string(),
                    "",
                );
                game.native_action_bar(player, Text::literal(txt).with_color(text::GREEN));
                broadcast_sync_now(game, s2);
            }
        }
        rules::ACT_TOGGLE_FUEL_RULE => {
            if who.permission >= 2 || game.native_server_players().len() <= 1 {
                st.require_fuel = !st.require_fuel;
                st.dirty = true;
                let msg = if st.require_fuel {
                    tr("gokart.msg.fuel_mode_on", "Go-Kart fuel consumption: ENABLED")
                } else {
                    tr("gokart.msg.fuel_mode_off", "Go-Kart fuel consumption: INFINITE FUEL")
                };
                game.native_action_bar(player, Text::literal(msg).with_color(text::AQUA));
                broadcast_sync_now(game, st);
            }
        }
        code @ 20..=35 => {
            let paint = rules::PaintColor::from_code(code - 20);
            let Some(kart_id) = target_arg.or_else(|| nearest_kart_id(game, st, &who, 6.0)) else {
                return;
            };
            let Some(&uuid) = st.id_to_uuid.get(&kart_id) else {
                return;
            };
            let dye_id = format!("minecraft:{}_dye", paint.slug());
            let free_paint = who.game_mode == 1 || who.permission >= 2;
            drop(guard);
            let mut can_paint = free_paint;
            if !can_paint {
                game.native_as_player(player, |g| {
                    if g.native_take_items(&dye_id, 1) > 0 {
                        can_paint = true;
                    }
                });
            }
            if can_paint
                && let Some(mut g2) = server_state(game)
                && let Some(s2) = g2.as_mut()
                && let Some(rt) = s2.by_uuid.get_mut(&uuid)
            {
                rt.spec.paint = paint;
                s2.dirty = true;
                game.native_play_sound_in_place("gokart:wrench", who.position, SOUND_PLAYERS, 0.8, 1.25);
                let cname = tr(paint.lang_key(), paint.slug());
                let txt = tr1("gokart.msg.painted", "Painted %1$s!", &cname);
                game.native_action_bar(player, Text::literal(txt).with_color(paint.rgb()));
                broadcast_sync_now(game, s2);
            }
        }
        _ => {}
    }
}

pub(in crate::game) fn net_from_server(game: &mut Game<'_>, channel: &str, data: &[u8]) {
    if channel != rules::CHAN_SYNC || !game.native_window() {
        return;
    }
    let mut c = lock(&CLIENT);
    ensure_client_config(&mut c);

    // Special 5-byte Garage open signal `[255, id0, id1, id2, id3]`
    if data.len() == 5 && data[0] == 255 {
        let target = u32::from_le_bytes([data[1], data[2], data[3], data[4]]);
        c.garage_target_entity = Some(target);
        c.pending_open_garage = true;
        return;
    }

    if let Some((require_fuel, views)) = rules::decode_sync_packet(data) {
        c.require_fuel = require_fuel;
        c.karts.clear();
        for v in views {
            c.karts.insert(v.entity_id, v);
        }
    }
}

// ---------------------------------------------------------------------------
// Client Driving Input, Camera Pullback, Horn & 3D Rendering
// ---------------------------------------------------------------------------

fn client_ridden_kart(game: &Game<'_>, c: &ClientState) -> Option<rules::ClientKartView> {
    if let Some(id) = game.riding
        && let Some(&view) = c.karts.get(&id)
    {
        return Some(view);
    }
    // Fallback for remote server connections where `game.riding` may live in client state
    let eye = game.native_client_state()?.eye_position?;
    c.karts.values().copied().find(|v| {
        game.native_entity(v.entity_id)
            .and_then(|e| game.native_entity_position(e))
            .is_some_and(|kp| {
                let dx = eye[0] - kp[0];
                let dz = eye[2] - kp[2];
                let dy = eye[1] - kp[1];
                dx * dx + dz * dz < 0.36 && (0.8..2.4).contains(&dy)
            })
    })
}

pub(in crate::game) fn movement_input(
    game: &Game<'_>,
    forward: &mut f32,
    strafe: &mut f32,
    jump: &mut bool,
    _sneak: &mut bool,
) {
    if !game.native_window() || !game.native_on(rules::ID) {
        return;
    }
    let mut c = lock(&CLIENT);
    if client_ridden_kart(game, &c).is_some() {
        c.local_input = rules::DriveInput {
            throttle: (*forward).clamp(-1.0, 1.0),
            steer: (*strafe).clamp(-1.0, 1.0),
            handbrake: *jump,
        };
        // Consume jump while driving so Space acts purely as Handbrake / Drift / Boost!
        *jump = false;
    } else {
        c.local_input = rules::DriveInput::default();
    }
}

fn glfw_key_matches(spec: &str, code: KeyCode) -> bool {
    let suffix = spec.strip_prefix("key.keyboard.").unwrap_or(spec);
    matches!(
        (suffix, code),
        ("h", KeyCode::KeyH)
            | ("k", KeyCode::KeyK)
            | ("g", KeyCode::KeyG)
            | ("r", KeyCode::KeyR)
            | ("v", KeyCode::KeyV)
            | ("b", KeyCode::KeyB)
            | ("x", KeyCode::KeyX)
            | ("z", KeyCode::KeyZ)
            | ("c", KeyCode::KeyC)
    )
}

pub(in crate::game) fn input_key(game: &mut Game<'_>, event: &winit::event::KeyEvent) {
    if !game.native_window()
        || !game.native_on(rules::ID)
        || event.state != winit::event::ElementState::Pressed
        || event.repeat
    {
        return;
    }
    let Some(state) = game.native_client_state() else {
        return;
    };
    if state.screen != horizon_client::mod_api::NativeScreenKind::Playing {
        return;
    }
    let winit::keyboard::PhysicalKey::Code(code) = event.physical_key else {
        return;
    };

    let horn_bind = game.native_mod_key(rules::ID, "horn", "key.keyboard.h");
    let garage_bind = game.native_mod_key(rules::ID, "garage", "key.keyboard.k");

    let mut send_horn: Option<u32> = None;
    {
        let mut c = lock(&CLIENT);
        ensure_client_config(&mut c);
        if glfw_key_matches(&horn_bind, code) && c.horn_cooldown == 0 {
            if let Some(ridden) = client_ridden_kart(game, &c) {
                c.horn_cooldown = 8;
                send_horn = Some(ridden.entity_id);
            }
        } else if glfw_key_matches(&garage_bind, code) {
            c.garage_target_entity = client_ridden_kart(game, &c).map(|v| v.entity_id);
            c.pending_open_garage = true;
        }
    }

    if let Some(eid) = send_horn {
        let mut pkt = vec![rules::ACT_HORN];
        pkt.extend_from_slice(&eid.to_le_bytes());
        let _ = game.native_net_send_to_server(rules::CHAN_ACTION, &pkt);
    }
}

pub(in crate::game) fn frame(game: &mut Game<'_>) {
    if !game.native_window() || !game.native_on(rules::ID) {
        return;
    }

    let now = Instant::now();
    let (open_garage, close_garage, queued_actions, to_send_input, switch_cam, yaw_adjust) = {
        let mut c = lock(&CLIENT);
        ensure_client_config(&mut c);
        if c.horn_cooldown > 0 {
            c.horn_cooldown -= 1;
        }

        let dt = c
            .last_frame_instant
            .map(|prev| now.duration_since(prev).as_secs_f32().clamp(0.0005, 0.10))
            .unwrap_or(1.0 / 60.0);
        c.last_frame_instant = Some(now);

        // Smooth sub-tick steering angle at display refresh rate for both steering wheel & driver IK!
        let steer_blend = 1.0 - (-22.0 * dt).exp();
        {
            let ClientState {
                karts,
                smoothed_steer,
                ..
            } = &mut *c;
            smoothed_steer.retain(|id, _| karts.contains_key(id));
            for (&id, k) in karts.iter() {
                let entry = smoothed_steer.entry(id).or_insert(k.steer_deg);
                *entry += (k.steer_deg - *entry) * steer_blend;
            }
        }

        let ridden_view = client_ridden_kart(game, &c);
        let riding_now = ridden_view.is_some();
        let mut cam_change: Option<CameraType> = None;
        if riding_now && !c.was_riding_kart {
            c.was_riding_kart = true;
            if c.settings.auto_third_person && game.camera_type == CameraType::FirstPerson {
                c.restored_first_person = true;
                cam_change = Some(CameraType::ThirdPersonBack);
            } else {
                c.restored_first_person = false;
            }
        } else if !riding_now && c.was_riding_kart {
            c.was_riding_kart = false;
            c.cam_kart_entity = None;
            c.last_mouse_move = None;
            c.local_input = rules::DriveInput::default();
            if c.restored_first_person && game.camera_type == CameraType::ThirdPersonBack {
                cam_change = Some(CameraType::FirstPerson);
            }
            c.restored_first_person = false;
        }

        // Authentic Go-Kart camera follow:
        // - Free mouse look anytime you move the mouse (clamped comfortably within ±125 deg shoulder check)
        // - 1:1 smooth camera rotation as the Go-Kart turns corners
        // - Gentle auto-recenter behind the Go-Kart when driving and leaving the mouse untouched
        let mut cam_yaw_delta: f32 = 0.0;
        if let Some(kart_view) = ridden_view
            && let Some(m) = game
                .mobs
                .iter()
                .find(|m| m.id == kart_view.entity_id && !m.removed)
        {
            if c.cam_kart_entity != Some(kart_view.entity_id) {
                c.cam_kart_entity = Some(kart_view.entity_id);
                c.visual_kart_yaw = m.yaw;
                c.last_seen_game_yaw = game.yaw;
                c.last_mouse_move = None;
            } else {
                let mouse_moved = rules::wrap_degrees(game.yaw - c.last_seen_game_yaw).abs() > 0.03;
                if mouse_moved {
                    c.last_mouse_move = Some(now);
                }
                let yaw_step =
                    rules::wrap_degrees(m.yaw - c.visual_kart_yaw) * (1.0 - (-22.0 * dt).exp());
                c.visual_kart_yaw = rules::wrap_degrees(c.visual_kart_yaw + yaw_step);

                // 1. Rotate camera smoothly with the Go-Kart's turn
                cam_yaw_delta += yaw_step;
                let mut next_yaw = game.yaw + cam_yaw_delta;

                // 2. Smooth chase recenter when driving and mouse has been idle > 0.70 s
                let mouse_idle = c
                    .last_mouse_move
                    .is_none_or(|t| now.duration_since(t).as_secs_f32() > 0.70);
                let active_drive = kart_view.speed_kmh > 1.5
                    || c.local_input.throttle.abs() > 0.05
                    || c.local_input.steer.abs() > 0.05;
                if mouse_idle && active_drive {
                    let align_err = rules::wrap_degrees(c.visual_kart_yaw - next_yaw);
                    let recenter = align_err * (1.0 - (-4.2 * dt).exp());
                    cam_yaw_delta += recenter;
                    next_yaw += recenter;
                }

                // 3. Natural cockpit shoulder-look clamp (±125 deg relative to kart nose)
                let rel = rules::wrap_degrees(next_yaw - c.visual_kart_yaw);
                let clamp_fix = rel.clamp(-125.0, 125.0) - rel;
                cam_yaw_delta += clamp_fix;
                c.last_seen_game_yaw = game.yaw + cam_yaw_delta;
            }
        } else {
            c.cam_kart_entity = None;
        }

        c.heartbeat = c.heartbeat.wrapping_add(1);
        let send_pkt = if riding_now
            && (c.local_input != c.last_sent_input || c.heartbeat.is_multiple_of(4))
        {
            c.last_sent_input = c.local_input;
            Some(c.local_input.encode_packet())
        } else if !riding_now && c.last_sent_input != rules::DriveInput::default() {
            c.last_sent_input = rules::DriveInput::default();
            Some(rules::DriveInput::default().encode_packet())
        } else {
            None
        };

        let open = std::mem::replace(&mut c.pending_open_garage, false);
        let close = std::mem::replace(&mut c.pending_close_garage, false);
        let acts = std::mem::take(&mut c.pending_actions);
        (open, close, acts, send_pkt, cam_change, cam_yaw_delta)
    };

    if yaw_adjust.abs() > 1e-5 {
        game.yaw += yaw_adjust;
        game.rope_rot_old.0 += yaw_adjust;
    }
    if let Some(next_cam) = switch_cam {
        game.camera_type = next_cam;
    }
    if let Some(pkt) = to_send_input {
        let _ = game.native_net_send_to_server(rules::CHAN_INPUT, &pkt);
    }
    for act in queued_actions {
        let _ = game.native_net_send_to_server(rules::CHAN_ACTION, &act);
    }
    if close_garage {
        game.native_mod_screen_close(rules::ID);
    } else if open_garage {
        let _ = game.native_mod_screen_open(rules::ID);
    }
    tick_player_model_post(game);
}

pub(in crate::game) fn camera_distance(game: &Game<'_>, distance: &mut f32) {
    if !game.native_window() || !game.native_on(rules::ID) {
        return;
    }
    let c = lock(&CLIENT);
    if let Some(view) = client_ridden_kart(game, &c) {
        *distance = c
            .settings
            .camera_distance
            .max(view.spec.kind.layout().default_cam_dist);
    }
}

// ---------------------------------------------------------------------------
// 3D Go-Kart & 4x4 Off-Roader Renderer (`native_mob_submit`)
// ---------------------------------------------------------------------------

pub(in crate::game) fn mob_submit(
    game: &Game<'_>,
    mob: &NativeMobRender<'_>,
    draw: &mut BlockEntityDraw,
    drawn: &mut bool,
) {
    if *drawn || mob.kind != "minecraft:pig" || !game.native_on(rules::ID) {
        return;
    }
    let (view, smooth_steer) = {
        let c = lock(&CLIENT);
        (
            c.karts.get(&mob.id).copied(),
            c.smoothed_steer.get(&mob.id).copied(),
        )
    };
    let Some(kart) = view else {
        return;
    };
    let steer_deg = smooth_steer.unwrap_or(kart.steer_deg);
    let lay = kart.spec.kind.layout();

    // Claim rendering completely so the backing pig is never drawn!
    *drawn = true;

    let circumference = 2.0 * std::f32::consts::PI * lay.rear_hub_y;
    let bps = kart.speed_kmh / (20.0 * 3.6);
    let wheel_spin = kart.wheel_rot_deg
        + if kart.burnout {
            mob.partial * 42.0
        } else {
            mob.partial * (bps / circumference) * 360.0
        };

    // Helper that transforms any standalone model authored symmetrically around
    // texel center (8, 8, 8) (= [0.5, 0.5, 0.5] blocks) to exact vehicle pivot `pivot`
    // with zero eccentric scale shift and zero rotation wobble!
    let draw_part_at_pivot = |draw: &mut BlockEntityDraw,
                              model: &str,
                              pivot: [f32; 3],
                              rots: &[([f32; 3], f32)],
                              scale: [f32; 3],
                              tint: u32| {
        draw.push();
        draw.translate(pivot);
        for &(axis, deg) in rots {
            if deg.abs() > 0.001 {
                draw.rotate_about(axis, deg, [0.0, 0.0, 0.0]);
            }
        }
        draw.scale(scale);
        draw.translate([-0.5, -0.5, -0.5]);
        game.native_draw_model(draw, model, tint);
        draw.pop();
    };

    // 1. Four Articulated 16-Sided Wheels — planted flat on Y = 0.000 road surface!
    let wheel_model = kart.spec.wheels.model_id();
    let wheel_mounts: [([f32; 3], [f32; 3], bool); 4] = [
        (
            [lay.front_track_half_x, lay.front_hub_y, lay.front_axle_z],
            lay.front_wheel_scale,
            true,
        ),
        (
            [-lay.front_track_half_x, lay.front_hub_y, lay.front_axle_z],
            lay.front_wheel_scale,
            true,
        ),
        (
            [lay.rear_track_half_x, lay.rear_hub_y, lay.rear_axle_z],
            lay.rear_wheel_scale,
            false,
        ),
        (
            [-lay.rear_track_half_x, lay.rear_hub_y, lay.rear_axle_z],
            lay.rear_wheel_scale,
            false,
        ),
    ];

    for (pivot, wscale, is_front) in wheel_mounts {
        let spin_now = if is_front && kart.burnout {
            kart.wheel_rot_deg
        } else {
            wheel_spin
        };
        if is_front {
            draw_part_at_pivot(
                draw,
                wheel_model,
                pivot,
                &[([0.0, 1.0, 0.0], steer_deg), ([1.0, 0.0, 0.0], spin_now)],
                wscale,
                0xFFFFFF,
            );
        } else {
            draw_part_at_pivot(
                draw,
                wheel_model,
                pivot,
                &[([1.0, 0.0, 0.0], spin_now)],
                wscale,
                0xFFFFFF,
            );
        }
    }

    // 2. Sprung Chassis Assembly (4x4 long-travel suspension roll on Off-Roader, taut race roll on Go-Kart!)
    draw.push();
    let roll_mult = match kart.spec.kind {
        rules::VehicleKind::OffRoader => 1.75,
        rules::VehicleKind::QuadBike => 1.45,
        rules::VehicleKind::DaciaLoganPolice => 1.42,
        rules::VehicleKind::PoliceCar => 1.30,
        rules::VehicleKind::GoKart => 1.0,
    };
    let roll_deg = if kart.drifting {
        -steer_deg * 0.14 * roll_mult
    } else {
        -steer_deg * 0.05 * roll_mult * (kart.speed_kmh / 60.0).min(1.0)
    };
    let pitch_deg: f32 = if kart.boosting {
        -1.6 * roll_mult
    } else {
        0.0
    };
    let roll_center_y = match kart.spec.kind {
        rules::VehicleKind::OffRoader => 0.36,
        rules::VehicleKind::QuadBike => 0.30,
        rules::VehicleKind::DaciaLoganPolice => 0.30,
        rules::VehicleKind::PoliceCar => 0.28,
        rules::VehicleKind::GoKart => 0.18,
    };
    if roll_deg.abs() > 0.04 {
        draw.rotate_about([0.0, 0.0, 1.0], roll_deg, [0.0, roll_center_y, 0.0]);
    }
    if pitch_deg.abs() > 0.04 {
        draw.rotate_about(
            [1.0, 0.0, 0.0],
            pitch_deg,
            [0.0, roll_center_y, lay.rear_axle_z],
        );
    }

    // 2a. Full-Scale Chassis Body (Go-Kart 1.28x or Off-Roader 1.40x!)
    draw.push();
    draw.scale(lay.body_scale);
    draw.translate([-0.5, 0.0, -0.5]);
    game.native_draw_model(draw, lay.body_model, kart.spec.paint.rgb());
    draw.pop();

    // 2b. Coaxial Sport Steering Wheel (Go-Kart / 4x4) OR Dedicated ATV T-Handlebars (Quad Bike)!
    if kart.spec.kind == rules::VehicleKind::QuadBike {
        draw_part_at_pivot(
            draw,
            lay.steer_model,
            lay.steer_pivot,
            &[([0.0, 1.0, 0.0], steer_deg * rules::QUAD_HANDLEBAR_TURN_MULT)],
            lay.steer_scale,
            kart.spec.paint.rgb(),
        );
    } else {
        draw_part_at_pivot(
            draw,
            lay.steer_model,
            lay.steer_pivot,
            &[
                ([1.0, 0.0, 0.0], lay.steer_tilt_deg),
                ([0.0, 0.0, 1.0], -steer_deg * rules::STEER_WHEEL_TURN_MULT),
            ],
            lay.steer_scale,
            0xFFFFFF,
        );
    }

    // 2c. Exposed Rear Racing Small Engine on Go-Kart (Iron / Gold / Diamond)
    if let (Some(ep), Some(engine_model)) = (lay.engine_pivot, kart.spec.engine.model_id()) {
        let vib = if kart.speed_kmh > 0.5 || kart.burnout {
            (mob.age * 1.85).sin() * 0.004
        } else {
            (mob.age * 0.7).sin() * 0.0015
        };
        draw_part_at_pivot(
            draw,
            engine_model,
            [ep[0] + vib, ep[1], ep[2]],
            &[],
            lay.engine_scale,
            0xFFFFFF,
        );
    }

    // 2d. Tailgate-mounted Matching Spare Wheel on 4x4 Off-Roader (flush & dead straight on carrier!)
    if let Some(sp) = lay.spare_wheel_pivot {
        draw_part_at_pivot(
            draw,
            wheel_model,
            sp,
            &[([0.0, 1.0, 0.0], 90.0)],
            lay.spare_wheel_scale,
            0xFFFFFF,
        );
    }

    // 2e. FiveM Alternating Red & Blue Girofar + Grille Strobe Flashers on Romanian Police Cars!
    if kart.spec.kind.is_police() && kart.siren_on {
        let phase = ((mob.age * 0.65) as i32).rem_euclid(2) == 0;
        let (roof_x, roof_y, roof_z, grille_x, grille_y, grille_z) =
            if kart.spec.kind == rules::VehicleKind::DaciaLoganPolice {
                (5.8 / 16.0, 29.5 / 16.0, -1.6 / 16.0, 3.0 / 16.0, 10.6 / 16.0, 30.8 / 16.0)
            } else {
                (6.2 / 16.0, 28.6 / 16.0, -2.1 / 16.0, 3.4 / 16.0, 10.6 / 16.0, 32.8 / 16.0)
            };
        if phase {
            // Left BLUE roof dome + Right BLUE grille strobe
            draw_part_at_pivot(
                draw,
                rules::MODEL_SIREN_BLUE,
                [roof_x, roof_y, roof_z],
                &[],
                [1.42, 1.38, 1.42],
                0xFFFFFF,
            );
            draw_part_at_pivot(
                draw,
                rules::MODEL_SIREN_BLUE,
                [-grille_x, grille_y, grille_z],
                &[],
                [0.65, 0.55, 0.45],
                0xFFFFFF,
            );
        } else {
            // Right RED roof dome + Left RED grille strobe
            draw_part_at_pivot(
                draw,
                rules::MODEL_SIREN_RED,
                [-roof_x, roof_y, roof_z],
                &[],
                [1.42, 1.38, 1.42],
                0xFFFFFF,
            );
            draw_part_at_pivot(
                draw,
                rules::MODEL_SIREN_RED,
                [grille_x, grille_y, grille_z],
                &[],
                [0.65, 0.55, 0.45],
                0xFFFFFF,
            );
        }
    }

    draw.pop();
}

// ---------------------------------------------------------------------------
// Driver Seating, Torso Lock & Real-Time Hands-on-Steering-Wheel IK (`BodyPose`)
// ---------------------------------------------------------------------------

#[derive(Debug)]
struct KartDriverPose {
    entity_id: u32,
}

impl BodyPose for KartDriverPose {
    fn pose(&self, _age: f32, _at_rest: &[[f32; 9]; 6], poses: &mut [[f32; 9]; 6]) -> bool {
        let (kind, steer_deg) = {
            let c = lock(&CLIENT);
            let kview = c.karts.get(&self.entity_id).copied();
            let vkind = kview
                .map(|k| k.spec.kind)
                .unwrap_or(rules::VehicleKind::GoKart);
            let st = c
                .smoothed_steer
                .get(&self.entity_id)
                .copied()
                .or_else(|| kview.map(|k| k.steer_deg))
                .unwrap_or(0.0);
            (vkind, st)
        };
        let lay = kind.layout();
        let (right_arm, left_arm) = rules::compute_driver_ik_angles(kind, steer_deg);

        // 0: head — natural neck yaw range (±78 deg) while torso stays locked in the seat
        poses[0][4] = poses[0][4].clamp(-1.36, 1.36);

        // 1: body — planted squarely in the bucket seat with subtle cornering lean
        poses[1][3] = 0.0;
        poses[1][4] = 0.0;
        poses[1][5] = (-steer_deg * 0.12).to_radians();

        // 2: right_arm & 3: left_arm — gripping the steering wheel & rotating live with steer_deg!
        poses[2][3] = right_arm[0];
        poses[2][4] = right_arm[1];
        poses[2][5] = right_arm[2];
        poses[3][3] = left_arm[0];
        poses[3][4] = left_arm[1];
        poses[3][5] = left_arm[2];

        // 4: right_leg & 5: left_leg — tucked cleanly inside the footwell on the pedals!
        poses[4][3] = lay.leg_xrot;
        poses[4][4] = 0.07;
        poses[4][5] = 0.03;
        poses[5][3] = lay.leg_xrot;
        poses[5][4] = -0.07;
        poses[5][5] = -0.03;
        true
    }
}

fn ensure_driver_pose(m: &mut Mob, kart_id: u32) {
    let already = m.emote.as_ref().is_some_and(|p| {
        let any: &dyn Any = &**p;
        any.downcast_ref::<KartDriverPose>()
            .is_some_and(|k| k.entity_id == kart_id)
    });
    if !already {
        m.emote = Some(Arc::new(KartDriverPose { entity_id: kart_id }));
    }
}

fn clear_driver_pose(m: &mut Mob) {
    let ours = m.emote.as_ref().is_some_and(|p| {
        let any: &dyn Any = &**p;
        any.is::<KartDriverPose>()
    });
    if ours {
        m.emote = None;
    }
}

fn entity_vehicle_kind(game: &Game<'_>, entity_id: u32) -> Option<rules::VehicleKind> {
    {
        let c = lock(&CLIENT);
        if let Some(view) = c.karts.get(&entity_id) {
            return Some(view.spec.kind);
        }
    }
    let tags = game
        .native_entity(entity_id)
        .and_then(|e| game.native_entity_tags(e))?;
    vehicle_kind_from_tags(&tags)
}

fn is_kart_entity(game: &Game<'_>, entity_id: u32) -> bool {
    entity_vehicle_kind(game, entity_id).is_some()
}

pub(in crate::game) fn tick_player_model_post(game: &mut Game<'_>) {
    if !game.native_on(rules::ID) {
        if let Some(pm) = game.player_model.as_mut() {
            clear_driver_pose(pm);
        }
        return;
    }
    let kart_yaw = game.riding.and_then(|ride_id| {
        if !is_kart_entity(game, ride_id) {
            return None;
        }
        game.mobs
            .iter()
            .find(|m| m.id == ride_id && !m.removed)
            .map(|m| (ride_id, m.yaw, m.previous_yaw))
    });
    let Some(pm) = game.player_model.as_mut() else {
        return;
    };
    if let Some((ride_id, yaw, prev_yaw)) = kart_yaw {
        // Lock the seated driver's torso forward with the vehicle (exact Boat behavior!)
        pm.body_yaw = yaw;
        pm.previous_body_yaw = prev_yaw;
        ensure_driver_pose(pm, ride_id);
    } else {
        clear_driver_pose(pm);
    }
}

pub(in crate::game) fn position_rider(game: &mut Game<'_>) -> ControlFlow<()> {
    if !game.native_on(rules::ID) {
        return ControlFlow::Continue(());
    }
    let Some(ride_id) = game.riding else {
        return ControlFlow::Continue(());
    };
    let Some(vkind) = entity_vehicle_kind(game, ride_id) else {
        return ControlFlow::Continue(());
    };
    let Some(m) = game.mobs.iter().find(|m| m.id == ride_id && !m.removed) else {
        return ControlFlow::Continue(());
    };
    let sa = vkind.layout().seat_attach;
    let at = mob_riders::seat(
        [f64::from(sa[0]), f64::from(sa[1]), f64::from(sa[2])],
        f64::from(0.6_f32),
        m.position,
        m.yaw,
    );
    let first = game.posed_rider != game.riding;
    game.posed_rider = game.riding;
    if let Some(p) = game.player.as_mut() {
        game.previous_position = if first { at } else { p.position };
        p.position = at;
        p.velocity = horizon_core::geometry::Vec3::ZERO;
        p.fall_distance = 0.0;
    }
    ControlFlow::Break(())
}

pub(in crate::game) fn position_riders_post(game: &mut Game<'_>) {
    if !game.native_on(rules::ID) {
        for m in &mut game.mobs {
            clear_driver_pose(m);
        }
        return;
    }
    for i in 0..game.mobs.len() {
        let Some(v) = game.mobs[i].extra.mount else {
            clear_driver_pose(&mut game.mobs[i]);
            continue;
        };
        let Some(vkind) = entity_vehicle_kind(game, v) else {
            clear_driver_pose(&mut game.mobs[i]);
            continue;
        };
        let Some(v_idx) = game.mobs.iter().position(|m| m.id == v) else {
            clear_driver_pose(&mut game.mobs[i]);
            continue;
        };
        if v_idx == i {
            continue;
        }
        let sa = vkind.layout().seat_attach;
        let attach = [f64::from(sa[0]), f64::from(sa[1]), f64::from(sa[2])];
        let (pos, prev, yaw, prev_yaw, v_width) = {
            let veh = &game.mobs[v_idx];
            (
                veh.position,
                veh.previous,
                veh.yaw,
                veh.previous_yaw,
                veh.width(),
            )
        };
        let m = &mut game.mobs[i];
        let offset = mob_riders::vehicle_attachment(m, v_width);
        m.position = mob_riders::seat(attach, offset, pos, yaw);
        m.previous = mob_riders::seat(attach, offset, prev, prev_yaw);
        m.body_yaw = yaw;
        m.previous_body_yaw = prev_yaw;
        ensure_driver_pose(m, v);
    }
}

// ---------------------------------------------------------------------------
// Racing Speedometer / Fuel / Boost HUD (`native_hud`)
// ---------------------------------------------------------------------------

pub(in crate::game) fn hud(game: &mut Game<'_>, batch: &mut HudBatch, _corners: &mut Corners) {
    if !game.native_window() || !game.native_on(rules::ID) {
        return;
    }
    let Some(client) = game.native_client_state() else {
        return;
    };
    if client.gui_hidden || client.screen != horizon_client::mod_api::NativeScreenKind::Playing {
        return;
    }

    let (kart, settings, require_fuel) = {
        let c = lock(&CLIENT);
        let Some(k) = client_ridden_kart(game, &c) else {
            return;
        };
        (k, c.settings, c.require_fuel)
    };

    let [sw, sh] = client.gui_size;
    let pw = 136.0;
    let ph = 66.0;
    let px = (sw - pw - 10.0).max(6.0);
    let py = (sh - ph - 10.0).max(6.0);

    // Outer racing dashboard card + painted top accent stripe
    game.native_fill(batch, [px - 1.0, py - 1.0, pw + 2.0, ph + 2.0], 0xCC101318);
    game.native_fill(batch, [px, py, pw, ph], 0xD8181C24);
    game.native_fill(batch, [px, py, pw, 3.0], 0xFF00_0000 | kart.spec.paint.rgb());

    // Analog speedometer mini-arc + dynamic needle on the left of the card
    let cx = px + 24.0;
    let cy = py + 31.0;
    let r_in = 14.0_f32;
    let r_out = 18.0_f32;
    for seg in 0..8 {
        let a0 = (-210.0 + seg as f32 * 30.0).to_radians();
        let a1 = (-210.0 + (seg + 1) as f32 * 30.0).to_radians();
        let col = if seg >= 6 {
            0xFFE03430
        } else if seg >= 4 {
            0xFFF8C628
        } else {
            0xFF3AAFD9
        };
        let pts = [
            [cx + a0.cos() * r_out, cy + a0.sin() * r_out],
            [cx + a0.cos() * r_in, cy + a0.sin() * r_in],
            [cx + a1.cos() * r_in, cy + a1.sin() * r_in],
            [cx + a1.cos() * r_out, cy + a1.sin() * r_out],
        ];
        game.native_quad(batch, pts, col);
    }
    let ratio = (kart.speed_kmh / 80.0).clamp(0.0, 1.0);
    let needle_ang = (-210.0 + ratio * 240.0).to_radians();
    let nx = needle_ang.cos();
    let ny = needle_ang.sin();
    let px_n = -ny * 1.3;
    let py_n = nx * 1.3;
    game.native_quad(
        batch,
        [
            [cx + px_n, cy + py_n],
            [cx - px_n, cy - py_n],
            [cx + nx * 15.5 - px_n * 0.4, cy + ny * 15.5 - py_n * 0.4],
            [cx + nx * 15.5 + px_n * 0.4, cy + ny * 15.5 + py_n * 0.4],
        ],
        0xFFFF5252,
    );
    game.native_fill(batch, [cx - 2.0, cy - 2.0, 4.0, 4.0], 0xFFE8ECF2);

    // Digital speed readout
    let speed_str = if settings.speed_kmh {
        tr1(
            "gokart.hud.speed_kmh",
            "%1$s KM/H",
            &format!("{:.0}", kart.speed_kmh),
        )
    } else {
        let bps = kart.speed_kmh / 3.6;
        tr1(
            "gokart.hud.speed_bps",
            "%1$s B/S",
            &format!("{bps:.1}"),
        )
    };
    game.native_text(batch, &speed_str, [px + 48.0, py + 7.0], 0xFFFFFF, true);

    // Status badge (DRIFT! / NO ENGINE! / EMPTY FUEL!)
    if kart.spec.engine == rules::EngineTier::None {
        let s = tr("gokart.hud.no_engine", "NO ENGINE!");
        game.native_text(batch, &s, [px + 48.0, py + 18.0], 0xFF5555, true);
    } else if require_fuel && kart.spec.fuel_mb == 0 {
        let s = tr("gokart.hud.no_fuel", "EMPTY FUEL!");
        game.native_text(batch, &s, [px + 48.0, py + 18.0], 0xFF5555, true);
    } else if kart.drifting || kart.burnout || kart.boosting {
        let s = if kart.boosting {
            "TURBO!"
        } else {
            &tr("gokart.hud.drift", "DRIFT!")
        };
        game.native_text(batch, s, [px + 48.0, py + 18.0], 0x4CE0D6, true);
    }

    // Fuel gauge bar
    let bar_x = px + 48.0;
    let bar_w = 80.0;
    let fuel_y = py + 30.0;
    game.native_fill(batch, [bar_x, fuel_y, bar_w, 6.0], 0xFF2A303C);
    if require_fuel {
        let frac = (kart.spec.fuel_mb as f32 / kart.spec.max_fuel_mb() as f32).clamp(0.0, 1.0);
        let fcol = if frac < 0.2 {
            0xFFE03430
        } else if frac < 0.5 {
            0xFFF8C628
        } else {
            0xFF52D053
        };
        game.native_fill(batch, [bar_x, fuel_y, bar_w * frac, 6.0], fcol);
    } else {
        game.native_fill(batch, [bar_x, fuel_y, bar_w, 6.0], 0xFF3AAFD9);
    }

    // Boost charge bar
    let boost_y = py + 40.0;
    game.native_fill(batch, [bar_x, boost_y, bar_w, 5.0], 0xFF2A303C);
    let bfrac = if kart.boosting {
        1.0
    } else {
        kart.boost_charge.clamp(0.0, 1.0)
    };
    if bfrac > 0.01 {
        let bcol = if kart.boosting || bfrac >= 0.75 {
            0xFF4CE0D6
        } else {
            0xFFF07618
        };
        game.native_fill(batch, [bar_x, boost_y, bar_w * bfrac, 5.0], bcol);
    }

    // Footer: Engine + Wheel tier + Key hints
    let footer = format!(
        "{} • {}  [H/K]",
        kart.spec.engine.slug().to_ascii_uppercase(),
        kart.spec.wheels.slug().to_ascii_uppercase()
    );
    game.native_text(batch, &footer, [px + 6.0, py + 52.0], 0xAEB6C4, true);
}

// ---------------------------------------------------------------------------
// Interactive Go-Kart Garage & Tuning GUI (`native_screen_render_post` + mouse)
// ---------------------------------------------------------------------------

struct GarageButton {
    id: u8,
    rect: [f32; 4],
    label: String,
    accent: u32,
}

fn garage_layout(
    client_size: [f32; 2],
    c: &ClientState,
    target_kart: Option<rules::ClientKartView>,
) -> ([f32; 4], Vec<GarageButton>) {
    let pw = 264.0;
    let ph = if target_kart.is_some() { 236.0 } else { 188.0 };
    let px = ((client_size[0] - pw) * 0.5).max(8.0);
    let py = ((client_size[1] - ph) * 0.5).max(8.0);

    let on_txt = tr("gokart.ui.on", "ON");
    let off_txt = tr("gokart.ui.off", "OFF");
    let bx = px + 14.0;
    let bw = pw - 28.0;
    let mut btns = Vec::new();

    let mut y_cursor = py + 62.0;
    if target_kart.is_some() {
        let third_w = (bw - 8.0) / 3.0;
        btns.push(GarageButton {
            id: 1,
            rect: [bx, y_cursor, third_w, 18.0],
            label: tr("gokart.ui.btn_pickup", "Pack Item"),
            accent: 0xFF2E7D32,
        });
        btns.push(GarageButton {
            id: 2,
            rect: [bx + third_w + 4.0, y_cursor, third_w, 18.0],
            label: tr("gokart.ui.btn_eject_engine", "Eject Engine"),
            accent: 0xFFB86B1E,
        });
        btns.push(GarageButton {
            id: 8,
            rect: [bx + (third_w + 4.0) * 2.0, y_cursor, third_w, 18.0],
            label: tr("gokart.ui.btn_delete", "Delete"),
            accent: 0xFFC62828,
        });
        y_cursor += 22.0;
        btns.push(GarageButton {
            id: 3,
            rect: [bx, y_cursor, bw, 18.0],
            label: tr("gokart.ui.btn_refuel", "Refuel from Inventory"),
            accent: 0xFF2E54C4,
        });
        y_cursor += 22.0;
        // 16-color Quick Paint Shop swatches (2 rows x 8 colors, id = 100..115)
        let sw = (bw - 7.0 * 4.0) / 8.0;
        for code in 0_u8..16_u8 {
            let col = usize::from(code % 8);
            let row = usize::from(code / 8);
            let sx = bx + (col as f32) * (sw + 4.0);
            let sy = y_cursor + (row as f32) * 16.0;
            let rgb = rules::PaintColor::from_code(code).rgb();
            btns.push(GarageButton {
                id: 100 + u8::from(code),
                rect: [sx, sy, sw, 13.0],
                label: String::new(),
                accent: 0xFF00_0000 | rgb,
            });
        }
        y_cursor += 36.0;
    }

    let fuel_state = if c.require_fuel { &on_txt } else { &off_txt };
    btns.push(GarageButton {
        id: 4,
        rect: [bx, y_cursor, bw, 18.0],
        label: tr1("gokart.ui.btn_fuel_toggle", "Require Fuel: %1$s", fuel_state),
        accent: if c.require_fuel { 0xFF3A4454 } else { 0xFF189C9D },
    });
    y_cursor += 22.0;

    let cam_state = if c.settings.auto_third_person {
        &on_txt
    } else {
        &off_txt
    };
    btns.push(GarageButton {
        id: 5,
        rect: [bx, y_cursor, (bw - 6.0) * 0.5, 18.0],
        label: tr1("gokart.ui.btn_cam_toggle", "Auto F5: %1$s", cam_state),
        accent: 0xFF3A4454,
    });

    let unit_str = if c.settings.speed_kmh { "KM/H" } else { "B/S" };
    btns.push(GarageButton {
        id: 6,
        rect: [bx + (bw + 6.0) * 0.5, y_cursor, (bw - 6.0) * 0.5, 18.0],
        label: tr1("gokart.ui.btn_unit_toggle", "Unit: %1$s", unit_str),
        accent: 0xFF3A4454,
    });
    y_cursor += 22.0;

    btns.push(GarageButton {
        id: 7,
        rect: [bx, y_cursor, bw, 18.0],
        label: tr("gokart.ui.btn_close", "Close [ESC]"),
        accent: 0xFF562828,
    });

    ([px, py, pw, ph], btns)
}

pub(in crate::game) fn screen_render(
    game: &Game<'_>,
    batch: &mut HudBatch,
    screen: &NativeScreenView<'_>,
) {
    if game.native_mod_screen() != Some(rules::ID) {
        return;
    }
    let Some(client) = game.native_client_state() else {
        return;
    };

    let (panel, buttons, target_kart) = {
        let c = lock(&CLIENT);
        let target = c
            .garage_target_entity
            .and_then(|id| c.karts.get(&id).copied())
            .or_else(|| client_ridden_kart(game, &c));
        let (rect, btns) = garage_layout(client.gui_size, &c, target);
        (rect, btns, target)
    };

    let [px, py, pw, ph] = panel;
    game.native_fill(batch, [0.0, 0.0, client.gui_size[0], client.gui_size[1]], 0x88080A0E);
    game.native_fill(batch, [px - 2.0, py - 2.0, pw + 4.0, ph + 4.0], 0xFF0E1117);
    game.native_fill(batch, [px, py, pw, ph], 0xF2181D26);

    let header_rgb = target_kart
        .map(|k| k.spec.paint.rgb())
        .unwrap_or(0xE03430);
    game.native_fill(batch, [px, py, pw, 4.0], 0xFF00_0000 | header_rgb);

    let title = tr("gokart.ui.title", "GO-KART GARAGE & SETTINGS");
    let tw = game.native_text_width(&title);
    game.native_text(
        batch,
        &title,
        [px + (pw - tw) * 0.5, py + 10.0],
        0xFFFFFF,
        true,
    );

    if let Some(kart) = target_kart {
        let vname = tr(kart.spec.kind.lang_key(), kart.spec.kind.slug());
        let eng = tr(kart.spec.engine.lang_key(), kart.spec.engine.slug());
        let whl = tr(kart.spec.wheels.lang_key(), kart.spec.wheels.slug());
        let col = tr(kart.spec.paint.lang_key(), kart.spec.paint.slug());
        let line1 = format!("{vname}  •  {eng}  •  {whl}");
        let line2 = format!(
            "{col}  •  {} / {} mB ({}%)",
            kart.spec.fuel_mb,
            kart.spec.max_fuel_mb(),
            kart.spec.fuel_percent()
        );
        game.native_text(batch, &line1, [px + 14.0, py + 28.0], 0xFFD966, true);
        game.native_text(batch, &line2, [px + 14.0, py + 41.0], 0xB8C4D4, true);
    } else {
        let info = tr(
            "gokart.ui.no_kart",
            "No Go-Kart targeted nearby — showing Global Mod Settings",
        );
        game.native_text(batch, &info, [px + 14.0, py + 34.0], 0xB8C4D4, true);
    }

    let [mx, my] = screen.mouse;
    for b in &buttons {
        let [bx, by, bw, bh] = b.rect;
        let hovered = mx >= bx && mx <= bx + bw && my >= by && my <= by + bh;
        let bg = if hovered {
            b.accent.saturating_add(0x00181818)
        } else {
            b.accent
        };
        game.native_fill(batch, [bx - 1.0, by - 1.0, bw + 2.0, bh + 2.0], 0xFF0B0D12);
        game.native_fill(batch, [bx, by, bw, bh], bg);
        let lw = game.native_text_width(&b.label);
        game.native_text(
            batch,
            &b.label,
            [bx + (bw - lw) * 0.5, by + 5.0],
            0xFFFFFF,
            true,
        );
    }

    let hint = tr(
        "gokart.ui.controls",
        "W/S Drive • A/D Steer • Space Drift/Boost • H Horn • Shift Exit",
    );
    game.native_text(batch, &hint, [px + 10.0, py + ph - 11.0], 0x8A94A6, false);
}

pub(in crate::game) fn screen_mouse(
    game: &Game<'_>,
    screen: &NativeScreenView<'_>,
    button: i32,
    canceled: &mut bool,
) {
    if button != 0 || game.native_mod_screen() != Some(rules::ID) {
        return;
    }
    let Some(client) = game.native_client_state() else {
        return;
    };
    let [mx, my] = screen.mouse;

    let mut c = lock(&CLIENT);
    let target = c
        .garage_target_entity
        .and_then(|id| c.karts.get(&id).copied())
        .or_else(|| client_ridden_kart(game, &c));
    let (_, buttons) = garage_layout(client.gui_size, &c, target);
    let target_id = target.map(|k| k.entity_id).unwrap_or(0);

    for b in buttons {
        let [bx, by, bw, bh] = b.rect;
        if mx >= bx && mx <= bx + bw && my >= by && my <= by + bh {
            *canceled = true;
            match b.id {
                1 => {
                    let mut p = vec![rules::ACT_PICKUP_KART];
                    p.extend_from_slice(&target_id.to_le_bytes());
                    c.pending_actions.push(p);
                    c.pending_close_garage = true;
                }
                2 => {
                    let mut p = vec![rules::ACT_EJECT_ENGINE];
                    p.extend_from_slice(&target_id.to_le_bytes());
                    c.pending_actions.push(p);
                }
                3 => {
                    let mut p = vec![rules::ACT_REFUEL_INV];
                    p.extend_from_slice(&target_id.to_le_bytes());
                    c.pending_actions.push(p);
                }
                4 => {
                    c.pending_actions.push(vec![rules::ACT_TOGGLE_FUEL_RULE]);
                }
                5 => {
                    c.settings.auto_third_person = !c.settings.auto_third_person;
                    save_client_config(&c);
                }
                6 => {
                    c.settings.speed_kmh = !c.settings.speed_kmh;
                    save_client_config(&c);
                }
                7 => {
                    c.pending_close_garage = true;
                }
                8 => {
                    let mut p = vec![rules::ACT_DELETE_KART];
                    p.extend_from_slice(&target_id.to_le_bytes());
                    c.pending_actions.push(p);
                    c.pending_close_garage = true;
                }
                code @ 100..=115 => {
                    let mut p = vec![20 + (code - 100)];
                    p.extend_from_slice(&target_id.to_le_bytes());
                    c.pending_actions.push(p);
                }
                _ => {}
            }
            break;
        }
    }
}

// ---------------------------------------------------------------------------
// Dynamic Localized Item Tooltips & Durability/Fuel Bars
// ---------------------------------------------------------------------------

pub(in crate::game) fn tooltip(game: &Game<'_>, stack: &ItemStack, lines: &mut Vec<(Text, u32)>) {
    if !game.native_on(rules::ID) {
        return;
    }
    match &*stack.item {
        rules::ITEM_GO_KART
        | rules::ITEM_OFF_ROADER
        | rules::ITEM_QUAD_BIKE
        | rules::ITEM_POLICE_CAR
        | rules::ITEM_DACIA_LOGAN_POLICE => {
            let spec = read_kart_spec(game, stack);
            let eng = tr(spec.engine.lang_key(), spec.engine.slug());
            let whl = tr(spec.wheels.lang_key(), spec.wheels.slug());
            let col = tr(spec.paint.lang_key(), spec.paint.slug());
            lines.push((
                Text::literal(tr1("gokart.tooltip.engine", "Engine: %1$s", &eng)),
                0xFFD966,
            ));
            lines.push((
                Text::literal(tr1("gokart.tooltip.wheels", "Wheels: %1$s", &whl)),
                0x66D9EF,
            ));
            lines.push((
                Text::literal(tr1("gokart.tooltip.paint", "Paint: %1$s", &col)),
                spec.paint.rgb(),
            ));
            lines.push((
                Text::literal(tr3(
                    "gokart.tooltip.fuel",
                    "Fuel: %1$s / %2$s mB (%3$s%%)",
                    &spec.fuel_mb.to_string(),
                    &spec.max_fuel_mb().to_string(),
                    &spec.fuel_percent().to_string(),
                )),
                0x70C926,
            ));
            let hint = match spec.kind {
                rules::VehicleKind::OffRoader => tr(
                    "gokart.tooltip.place_off_roader",
                    "Right-click ground to deploy 4x4 Off-Roader (climbs 1-block terrain!)",
                ),
                rules::VehicleKind::QuadBike => tr(
                    "gokart.tooltip.place_quad_bike",
                    "Right-click ground to deploy Quad Bike ATV (nimble 1-block trail climber!)",
                ),
                rules::VehicleKind::PoliceCar => tr(
                    "gokart.tooltip.place_police_car",
                    "Right-click ground to deploy Poliția Română Patrol Car ([H] toggles Siren & Girofar!)",
                ),
                rules::VehicleKind::DaciaLoganPolice => tr(
                    "gokart.tooltip.place_dacia_logan",
                    "Right-click ground to deploy Dacia Logan Poliția Română ([H] toggles Siren & Girofar!)",
                ),
                rules::VehicleKind::GoKart => tr(
                    "gokart.tooltip.place_hint",
                    "Right-click ground to deploy Go-Kart",
                ),
            };
            lines.push((Text::literal(hint), 0x9AA4B2));
        }
        rules::ITEM_JERRY_CAN => {
            let mb = read_jerry_fuel(game, stack);
            let pct = (mb * 100) / rules::JERRY_MAX_FUEL_MB;
            lines.push((
                Text::literal(tr3(
                    "gokart.tooltip.fuel",
                    "Fuel: %1$s / %2$s mB (%3$s%%)",
                    &mb.to_string(),
                    &rules::JERRY_MAX_FUEL_MB.to_string(),
                    &pct.to_string(),
                )),
                0xF8C628,
            ));
            lines.push((
                Text::literal(tr(
                    "gokart.tooltip.jerry_hint",
                    "Right-click Go-Kart to refuel | Right-click Lava/Coal Block to refill",
                )),
                0x9AA4B2,
            ));
        }
        rules::ITEM_WRENCH => {
            lines.push((
                Text::literal(tr(
                    "gokart.tooltip.wrench_hint",
                    "Right-click Go-Kart: Tuning Garage | Left-click: Pack Go-Kart",
                )),
                0x9AA4B2,
            ));
        }
        rules::ITEM_ENGINE_IRON => {
            lines.push((
                Text::literal(tr(
                    "gokart.tooltip.engine_iron",
                    "Top Speed: 52 km/h | Balanced Torque",
                )),
                0xC8D0DC,
            ));
        }
        rules::ITEM_ENGINE_GOLD => {
            lines.push((
                Text::literal(tr(
                    "gokart.tooltip.engine_gold",
                    "Top Speed: 64 km/h | Snappy Acceleration",
                )),
                0xF8C628,
            ));
        }
        rules::ITEM_ENGINE_DIAMOND => {
            lines.push((
                Text::literal(tr(
                    "gokart.tooltip.engine_diamond",
                    "Top Speed: 76 km/h | Pro Racing Power & High Efficiency",
                )),
                0x4CE0D6,
            ));
        }
        rules::ITEM_WHEEL_STANDARD => {
            lines.push((
                Text::literal(tr(
                    "gokart.tooltip.wheel_standard",
                    "Balanced grip on roads and dirt",
                )),
                0xC8D0DC,
            ));
        }
        rules::ITEM_WHEEL_SPORTS => {
            lines.push((
                Text::literal(tr(
                    "gokart.tooltip.wheel_sports",
                    "Sharper steering & +12% drift boost charge",
                )),
                0x66D9EF,
            ));
        }
        rules::ITEM_WHEEL_RACING => {
            lines.push((
                Text::literal(tr(
                    "gokart.tooltip.wheel_racing",
                    "Maximum road speed & +25% drift boost charge",
                )),
                0xFF6B6B,
            ));
        }
        _ => {}
    }
}

pub(in crate::game) fn item_bar(
    game: &Game<'_>,
    stack: &ItemStack,
    bar: &mut Option<(i32, u32)>,
) {
    if !game.native_on(rules::ID) {
        return;
    }
    if &*stack.item == rules::ITEM_JERRY_CAN {
        let mb = read_jerry_fuel(game, stack);
        let fill = ((mb as f32 / rules::JERRY_MAX_FUEL_MB as f32) * 13.0).round() as i32;
        *bar = Some((fill.clamp(0, 13), 0xF8C628));
    } else if rules::VehicleKind::from_item(&stack.item).is_some() {
        let spec = read_kart_spec(game, stack);
        let cap = spec.max_fuel_mb();
        if spec.fuel_mb < cap {
            let fill = ((spec.fuel_mb as f32 / cap as f32) * 13.0).round() as i32;
            *bar = Some((fill.clamp(0, 13), 0x52D053));
        }
    }
}
