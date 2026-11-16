#!/usr/bin/env python3
"""Deterministic asset generator for the Horizon Go-Kart mod (`gokart`).

Generates:
  - 16x16 RGBA pixel-art textures (items + 3D vehicle parts)
  - 3D standalone JSON models (`assets/gokart/models/block/*.json`)
  - Item models & Minecraft 26.3 item definitions (`assets/gokart/items/*.json`)
  - Synthesized 44.1 kHz OGG Vorbis sound effects (`assets/gokart/sounds/*.ogg`) + `sounds.json`
  - Survival crafting recipes (`data/gokart/recipe/*.json`)
  - Full English (`en_us.json`) and Romanian (`ro_ro.json`) localization files
"""

from __future__ import annotations

import json
import math
import os
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
ASSETS = CONTENT / "assets" / "gokart"
DATA = CONTENT / "data" / "gokart"


# ---------------------------------------------------------------------------
# Deterministic PNG writer (pure stdlib)
# ---------------------------------------------------------------------------

def write_png(path: Path, width: int, height: int, pixels: list[tuple[int, int, int, int]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = bytearray()
    for y in range(height):
        raw.append(0)  # Filter type 0 (None)
        row = pixels[y * width : (y + 1) * width]
        for r, g, b, a in row:
            raw.extend((r & 255, g & 255, b & 255, a & 255))

    def chunk(tag: bytes, payload: bytes) -> bytes:
        crc = zlib.crc32(tag + payload) & 0xFFFFFFFF
        return struct.pack(">I", len(payload)) + tag + payload + struct.pack(">I", crc)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    idat = zlib.compress(bytes(raw), level=9)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")
    path.write_bytes(png)


def grid_to_png(path: Path, art: list[str], palette: dict[str, tuple[int, int, int, int]]) -> None:
    h = len(art)
    w = len(art[0])
    pixels: list[tuple[int, int, int, int]] = []
    for row in art:
        assert len(row) == w, f"Row width mismatch in {path}: {len(row)} != {w}"
        for ch in row:
            pixels.append(palette[ch])
    write_png(path, w, h, pixels)


# ---------------------------------------------------------------------------
# Block / Vehicle surface textures (`assets/gokart/textures/block/*.png`)
# ---------------------------------------------------------------------------

def generate_vehicle_textures() -> None:
    bdir = ASSETS / "textures" / "block"

    # 1. `kart_body.png`: Neutral high-contrast metallic white/silver so `tintindex: 0`
    # multiplies cleanly with any of the 16 Minecraft dye RGB colors!
    pixels = []
    for y in range(16):
        for x in range(16):
            border = x in (0, 15) or y in (0, 15)
            highlight = y in (2, 3) and 2 <= x <= 13
            rivet = (x in (2, 13) and y in (2, 13))
            stripe = y in (7, 8)
            if border:
                v = 188
            elif rivet:
                v = 168
            elif highlight:
                v = 252
            elif stripe:
                v = 242
            else:
                v = 226 - ((x + y) % 3) * 4
            pixels.append((v, v, v, 255))
    write_png(bdir / "kart_body.png", 16, 16, pixels)

    # 2. `kart_frame.png`: Dark powder-coated tubular steel chassis & floorpan
    pixels = []
    for y in range(16):
        for x in range(16):
            edge = x in (0, 15) or y in (0, 15)
            tread = (x % 4 == 1 and y % 4 == 1) or (x % 4 == 3 and y % 4 == 3)
            if edge:
                c = (34, 37, 42, 255)
            elif tread:
                c = (68, 73, 82, 255)
            else:
                v = 48 + ((x * 3 + y * 5) % 7)
                c = (v, v + 2, v + 6, 255)
            pixels.append(c)
    write_png(bdir / "kart_frame.png", 16, 16, pixels)

    # 3. `kart_seat.png`: Racing bucket seat upholstery (dark red-stitched charcoal leather)
    pixels = []
    for y in range(16):
        for x in range(16):
            stitch = x in (2, 13) and (y % 2 == 0)
            rib = y in (4, 8, 12) and 3 <= x <= 12
            if stitch:
                c = (195, 52, 52, 255)
            elif rib:
                c = (26, 27, 31, 255)
            else:
                v = 36 + ((x + y) % 3) * 3
                c = (v, v, v + 4, 255)
            pixels.append(c)
    write_png(bdir / "kart_seat.png", 16, 16, pixels)

    # 4. `kart_chrome.png`: Brushed aluminum / chrome steering shaft, pedals & exhaust pipe
    pixels = []
    for y in range(16):
        for x in range(16):
            band = (x + y * 2) % 8
            if band in (0, 1):
                c = (235, 240, 246, 255)
            elif band in (2, 3):
                c = (192, 200, 210, 255)
            elif band in (4, 5):
                c = (150, 158, 170, 255)
            else:
                c = (210, 216, 225, 255)
            pixels.append(c)
    write_png(bdir / "kart_chrome.png", 16, 16, pixels)

    # 5. Wheel textures: `wheel_standard.png`, `wheel_sports.png`, `wheel_racing.png`
    wheel_configs = [
        ("wheel_standard.png", (38, 40, 44), (175, 182, 190), (110, 116, 124)),
        ("wheel_sports.png",   (30, 32, 36), (235, 185, 48),  (58, 138, 225)),
        ("wheel_racing.png",   (24, 25, 28), (230, 52, 52),   (242, 205, 62)),
    ]
    for fname, rubber, rim, accent in wheel_configs:
        pixels = []
        for y in range(16):
            for x in range(16):
                dx = x - 7.5
                dy = y - 7.5
                dist = math.hypot(dx, dy)
                if dist < 2.2:
                    c = (*accent, 255)
                elif dist < 4.7:
                    spoke = abs(dx) < 1.1 or abs(dy) < 1.1
                    c = (*rim, 255) if spoke else (rim[0] // 2, rim[1] // 2, rim[2] // 2, 255)
                else:
                    groove = ((x + y) % 3 == 0)
                    r = max(14, rubber[0] - (8 if groove else 0))
                    g = max(14, rubber[1] - (8 if groove else 0))
                    b = max(16, rubber[2] - (8 if groove else 0))
                    c = (r, g, b, 255)
                pixels.append(c)
        write_png(bdir / fname, 16, 16, pixels)

    # 6. Engine block textures: `engine_iron.png`, `engine_gold.png`, `engine_diamond.png`
    engine_configs = [
        ("engine_iron.png",    (158, 164, 172), (96, 102, 110), (212, 74, 56)),
        ("engine_gold.png",    (238, 192, 58),  (166, 118, 24), (225, 64, 48)),
        ("engine_diamond.png", (76, 224, 214),  (36, 138, 148), (245, 196, 54)),
    ]
    for fname, head_col, fin_col, cap_col in engine_configs:
        pixels = []
        for y in range(16):
            for x in range(16):
                if 5 <= x <= 10 and 1 <= y <= 3:
                    c = (*cap_col, 255)
                elif y % 2 == 0 and 2 <= x <= 13:
                    c = (*head_col, 255)
                elif x in (0, 15) or y in (0, 15):
                    c = (42, 45, 52, 255)
                else:
                    c = (*fin_col, 255)
                pixels.append(c)
        write_png(bdir / fname, 16, 16, pixels)


# ---------------------------------------------------------------------------
# 16x16 Crisp Pixel-Art Item Icons (`assets/gokart/textures/item/*.png`)
# ---------------------------------------------------------------------------

def generate_item_textures() -> None:
    idir = ASSETS / "textures" / "item"
    T = (0, 0, 0, 0)

    # 1. `go_kart.png` — Isometric/side iconic red racing Go-Kart!
    kart_pal = {
        ".": T,
        "K": (24, 26, 32, 255),     # Tire black outline
        "G": (64, 68, 76, 255),     # Tire tread / chassis dark
        "S": (186, 194, 206, 255),  # Silver rim / steering shaft / engine
        "R": (222, 48, 48, 255),    # Classic racing red body
        "H": (250, 106, 96, 255),   # Red highlight
        "D": (152, 26, 28, 255),    # Dark red shade
        "C": (48, 52, 60, 255),     # Bucket seat charcoal
        "Y": (246, 202, 56, 255),   # Racing number / cap accent
    }
    kart_art = [
        "................",
        "................",
        ".........KK.....",
        "....CC...KSK....",
        "...CCCC..S......",
        "..KSSCC..S.HHH..",
        "..SSGCCC.SRRRRR.",
        ".HRRRRRRRRRRRRH.",
        ".DRRRRRYYRRRRRD.",
        ".GGGGGGGGGGGGGG.",
        "..KKKK....KKKK..",
        ".KGGGGK..KGGGGK.",
        ".KGSSGK..KGSSGK.",
        ".KGGGGK..KGGGGK.",
        "..KKKK....KKKK..",
        "................",
    ]
    grid_to_png(idir / "go_kart.png", kart_art, kart_pal)

    # 2. Small Engines (`small_engine_iron.png`, `small_engine_gold.png`, `small_engine_diamond.png`)
    engine_tiers = [
        ("small_engine_iron.png",    (206, 212, 220, 255), (146, 154, 164, 255), (96, 102, 112, 255)),
        ("small_engine_gold.png",    (252, 224, 98, 255),  (228, 174, 42, 255),  (156, 106, 18, 255)),
        ("small_engine_diamond.png", (138, 248, 240, 255), (58, 206, 198, 255),  (28, 128, 136, 255)),
    ]
    for fname, hi, mid, lo in engine_tiers:
        pal = {
            ".": T,
            "K": (26, 28, 34, 255),
            "H": hi,
            "M": mid,
            "L": lo,
            "R": (222, 54, 48, 255),
            "G": (68, 72, 82, 255),
            "S": (232, 236, 242, 255),
        }
        art = [
            "................",
            "......KKKK......",
            ".....KRRRRK.....",
            "......KSSK......",
            "...KKKKKKKKKK...",
            "..KHHHHHHHHHHK..",
            "...KLLLLLLLLK...",
            "..KMMMMMMMMMMK..",
            "...KLLLLLLLLK...",
            "..KMMMMMMMMMMKK.",
            "..KGGGGGGGGGGSK.",
            "..KGGKSSSSKGGSK.",
            "..KGGKSSSSKGGKK.",
            "...KKKKKKKKKK...",
            "....KK....KK....",
            "................",
        ]
        grid_to_png(idir / fname, art, pal)

    # 3. Wheels (`standard_wheel.png`, `sports_wheel.png`, `racing_wheel.png`)
    wheel_items = [
        ("standard_wheel.png", (206, 212, 222, 255), (132, 138, 150, 255), (86, 92, 102, 255)),
        ("sports_wheel.png",   (248, 204, 68, 255),  (58, 146, 232, 255),  (184, 134, 28, 255)),
        ("racing_wheel.png",   (238, 62, 58, 255),   (250, 212, 64, 255),  (164, 32, 32, 255)),
    ]
    for fname, rim_hi, hub, rim_lo in wheel_items:
        pal = {
            ".": T,
            "K": (22, 24, 28, 255),
            "T": (48, 52, 58, 255),
            "G": (72, 76, 84, 255),
            "H": rim_hi,
            "L": rim_lo,
            "C": hub,
        }
        art = [
            "................",
            ".....KKKKKK.....",
            "...KKTTTTTTKK...",
            "..KTTGKKKKGTTK..",
            ".KTTKHHHHHHKTTK.",
            ".KTKHLLHHLLHKTK.",
            "KTKHLHCCCCHLHKTK",
            "KTKHHCCCCCCLHKTK",
            "KTKHLCCCCCCLHKTK",
            "KTKHLHCCCCHLHKTK",
            ".KTKHLLHHLLHKTK.",
            ".KTTKLLLLLLKTTK.",
            "..KTTGKKKKGTTK..",
            "...KKTTTTTTKK...",
            ".....KKKKKK.....",
            "................",
        ]
        grid_to_png(idir / fname, art, pal)

    # 4. `wrench.png` — Mechanic's open-end chrome vanadium wrench with red grip
    wrench_pal = {
        ".": T,
        "K": (28, 30, 36, 255),
        "S": (224, 230, 240, 255),
        "M": (162, 170, 184, 255),
        "D": (112, 120, 134, 255),
        "R": (218, 52, 48, 255),
        "H": (246, 98, 90, 255),
    }
    wrench_art = [
        "................",
        ".........KKKK...",
        "........KSSSSK..",
        "........KSS..KK.",
        "........KSSM..K.",
        "........KSSMMKK.",
        ".......KSSMMK...",
        "......KSSMMK....",
        ".....KSSMMK.....",
        "....KHRMMK......",
        "...KHRRMK.......",
        "..KHRRMK........",
        ".KHRRMK.........",
        ".KRRDK..........",
        "..KKK...........",
        "................",
    ]
    grid_to_png(idir / "wrench.png", wrench_art, wrench_pal)

    # 5. `jerry_can.png` — Classic red steel fuel Jerry Can with brass spout & X-emboss
    jerry_pal = {
        ".": T,
        "K": (28, 24, 24, 255),
        "R": (208, 44, 42, 255),
        "H": (244, 92, 84, 255),
        "D": (146, 26, 26, 255),
        "Y": (244, 198, 58, 255),
        "S": (186, 192, 202, 255),
    }
    jerry_art = [
        "................",
        "....KKK..KKKK...",
        "...KYYK.KSSSSK..",
        "....KKK.KSSKK...",
        "...KKKKKKKKKK...",
        "..KHRRRRRRRRHK..",
        "..KRRDRRRRDRRK..",
        "..KRRRDRRDRRRK..",
        "..KRRRRDDRRRRK..",
        "..KRRRRDDRRRRK..",
        "..KRRRDRRDRRRK..",
        "..KRRDRRRRDRRK..",
        "..KRRRRRRRRRRK..",
        "..KDDDDDDDDDDK..",
        "...KKKKKKKKKK...",
        "................",
    ]
    grid_to_png(idir / "jerry_can.png", jerry_art, jerry_pal)


# ---------------------------------------------------------------------------
# Standalone 3D JSON Vehicle Models (`assets/gokart/models/block/*.json`)
# ---------------------------------------------------------------------------

def box(from_xyz, to_xyz, tex: str, tint: bool = False) -> dict:
    dx = max(1.0, min(16.0, abs(to_xyz[0] - from_xyz[0])))
    dy = max(1.0, min(16.0, abs(to_xyz[1] - from_xyz[1])))
    dz = max(1.0, min(16.0, abs(to_xyz[2] - from_xyz[2])))
    uv_map = {
        "down": [0.0, 0.0, round(dx, 2), round(dz, 2)],
        "up": [0.0, 0.0, round(dx, 2), round(dz, 2)],
        "north": [0.0, 0.0, round(dx, 2), round(dy, 2)],
        "south": [0.0, 0.0, round(dx, 2), round(dy, 2)],
        "west": [0.0, 0.0, round(dz, 2), round(dy, 2)],
        "east": [0.0, 0.0, round(dz, 2), round(dy, 2)],
    }
    faces = {}
    for d in ("down", "up", "north", "south", "west", "east"):
        f = {"texture": tex, "uv": uv_map[d]}
        if tint:
            f["tintindex"] = 0
        faces[d] = f
    return {"from": from_xyz, "to": to_xyz, "faces": faces}


def generate_models() -> None:
    mdir = ASSETS / "models" / "block"
    mdir.mkdir(parents=True, exist_ok=True)

    # Coordinate convention:
    # Block model center is (8, 0, 8) at feet; +Z is forward (south), -Z is rear (north),
    # +X is left (east), -X is right (west), +Y is up.
    # Horizon allows standard Minecraft element coordinates [-16, 32], giving a crisp
    # 1.75-block long racing Go-Kart!

    # 1. `go_kart_body.json`
    body_elements = [
        # Main dark steel floorpan & side rails (no tintindex)
        box([2.5, 1.5, -7.0], [13.5, 2.8, 16.5], "#frame"),
        # Rear engine mounting deck
        box([3.0, 2.0, -13.5], [13.0, 3.5, -7.0], "#frame"),
        # Front axle crossbar & rear axle housing
        box([0.5, 2.0, 12.5], [15.5, 3.2, 14.5], "#frame"),
        box([0.5, 2.2, -10.5], [15.5, 3.6, -8.5], "#frame"),
        # Front tubular bumper + painted nose spoiler (`tint = True`)
        box([1.5, 2.0, 18.5], [14.5, 4.0, 20.5], "#frame"),
        box([2.5, 2.8, 15.0], [13.5, 5.4, 19.2], "#body", tint=True),
        # Sloped front nose cowling (`tint = True`)
        box([3.5, 4.8, 10.5], [12.5, 7.0, 16.0], "#body", tint=True),
        # Left & right painted aerodynamic side pods (`tint = True`)
        box([13.2, 2.2, -4.5], [15.8, 5.6, 10.5], "#body", tint=True),
        box([0.2, 2.2, -4.5], [2.8, 5.6, 10.5], "#body", tint=True),
        # Rear painted bumper cowling (`tint = True`) + steel crash bar
        box([2.0, 2.5, -15.2], [14.0, 4.6, -13.5], "#frame"),
        box([3.0, 3.5, -14.2], [13.0, 6.2, -12.2], "#body", tint=True),
        # Bucket racing seat (base cushion, side bolsters, high backrest)
        box([4.0, 2.8, -5.5], [12.0, 4.4, 2.5], "#seat"),
        box([3.5, 4.0, -5.5], [5.0, 7.5, 1.5], "#seat"),
        box([11.0, 4.0, -5.5], [12.5, 7.5, 1.5], "#seat"),
        box([4.0, 4.4, -6.8], [12.0, 11.2, -4.8], "#seat"),
        # Painted seat back shell (`tint = True`)
        box([4.5, 4.8, -7.4], [11.5, 10.6, -6.7], "#body", tint=True),
        # Steering column support & angled shaft
        box([6.8, 2.8, 9.8], [9.2, 8.2, 11.6], "#frame"),
        box([7.3, 7.2, 7.4], [8.7, 9.6, 10.8], "#chrome"),
        # Throttle & brake pedals at front of footwell
        box([4.5, 2.8, 14.5], [6.2, 5.2, 15.5], "#chrome"),
        box([9.8, 2.8, 14.5], [11.5, 5.2, 15.5], "#chrome"),
    ]
    (mdir / "go_kart_body.json").write_text(
        json.dumps(
            {
                "textures": {
                    "body": "gokart:block/kart_body",
                    "frame": "gokart:block/kart_frame",
                    "seat": "gokart:block/kart_seat",
                    "chrome": "gokart:block/kart_chrome",
                },
                "elements": body_elements,
            },
            indent=2,
        )
        + "\n"
    )

    # 2. `go_kart_steering_wheel.json` — Centered around (8, 8, 8) so rotating around
    # [0.5, 0.5, 0.5] spins cleanly along the steering column axis!
    sw_elements = [
        # Center hub
        box([6.8, 6.8, 7.2], [9.2, 9.2, 8.8], "#chrome"),
        # Outer grip ring (top, bottom, left, right)
        box([5.2, 10.2, 7.4], [10.8, 11.4, 8.6], "#seat"),
        box([5.2, 4.6, 7.4], [10.8, 5.8, 8.6], "#seat"),
        box([4.6, 5.2, 7.4], [5.8, 10.8, 8.6], "#seat"),
        box([10.2, 5.2, 7.4], [11.4, 10.8, 8.6], "#seat"),
        # Three spokes
        box([5.8, 7.5, 7.6], [10.2, 8.5, 8.4], "#chrome"),
        box([7.5, 5.8, 7.6], [8.5, 8.0, 8.4], "#chrome"),
    ]
    (mdir / "go_kart_steering_wheel.json").write_text(
        json.dumps(
            {
                "textures": {
                    "seat": "gokart:block/kart_seat",
                    "chrome": "gokart:block/kart_chrome",
                },
                "elements": sw_elements,
            },
            indent=2,
        )
        + "\n"
    )

    # 3. Wheel 3D models (`wheel_standard.json`, `wheel_sports.json`, `wheel_racing.json`)
    # Centered at (8, 8, 8), rolling around X axis, width along X [5.4..10.6], radius ~3.5 texels
    for wname, tex in [
        ("wheel_standard", "gokart:block/wheel_standard"),
        ("wheel_sports", "gokart:block/wheel_sports"),
        ("wheel_racing", "gokart:block/wheel_racing"),
    ]:
        # Octagonal-ish 2-box cross + hub profile so rotation around X is visibly crisp!
        w_elements = [
            box([5.5, 4.6, 5.4], [10.5, 11.4, 10.6], "#wheel"),
            box([5.5, 5.4, 4.6], [10.5, 10.6, 11.4], "#wheel"),
            box([5.2, 6.6, 6.6], [10.8, 9.4, 9.4], "#chrome"),
        ]
        (mdir / f"{wname}.json").write_text(
            json.dumps(
                {
                    "textures": {
                        "wheel": tex,
                        "chrome": "gokart:block/kart_chrome",
                    },
                    "elements": w_elements,
                },
                indent=2,
            )
            + "\n"
        )

    # 4. Rear Small Engine 3D models (`engine_iron.json`, `engine_gold.json`, `engine_diamond.json`)
    # Centered at (8, 8, 8)
    for ename, tex in [
        ("engine_iron", "gokart:block/engine_iron"),
        ("engine_gold", "gokart:block/engine_gold"),
        ("engine_diamond", "gokart:block/engine_diamond"),
    ]:
        e_elements = [
            # Crankcase & cylinder block with cooling fins
            box([4.8, 4.5, 5.0], [11.2, 9.8, 10.8], "#engine"),
            # Top air filter / fuel tank cap
            box([5.6, 9.8, 5.8], [10.4, 11.6, 9.6], "#frame"),
            # Twin chrome exhaust header & muffler pointing backward (-Z)
            box([9.5, 6.5, 1.2], [11.3, 8.3, 6.2], "#chrome"),
            box([9.8, 6.8, 0.2], [11.0, 8.0, 1.4], "#frame"),
        ]
        (mdir / f"{ename}.json").write_text(
            json.dumps(
                {
                    "textures": {
                        "engine": tex,
                        "frame": "gokart:block/kart_frame",
                        "chrome": "gokart:block/kart_chrome",
                    },
                    "elements": e_elements,
                },
                indent=2,
            )
            + "\n"
        )


# ---------------------------------------------------------------------------
# Item definitions (`assets/gokart/items/*.json`) & Item models
# ---------------------------------------------------------------------------

ITEMS = [
    "go_kart",
    "small_engine_iron",
    "small_engine_gold",
    "small_engine_diamond",
    "standard_wheel",
    "sports_wheel",
    "racing_wheel",
    "wrench",
    "jerry_can",
]


def generate_item_jsons() -> None:
    items_dir = ASSETS / "items"
    imodel_dir = ASSETS / "models" / "item"
    items_dir.mkdir(parents=True, exist_ok=True)
    imodel_dir.mkdir(parents=True, exist_ok=True)

    for name in ITEMS:
        (items_dir / f"{name}.json").write_text(
            json.dumps(
                {"model": {"type": "minecraft:model", "model": f"gokart:item/{name}"}},
                indent=2,
            )
            + "\n"
        )
        parent = "minecraft:item/handheld" if name == "wrench" else "minecraft:item/generated"
        (imodel_dir / f"{name}.json").write_text(
            json.dumps(
                {
                    "parent": parent,
                    "textures": {"layer0": f"gokart:item/{name}"},
                },
                indent=2,
            )
            + "\n"
        )


# ---------------------------------------------------------------------------
# Crafting Recipes (`data/gokart/recipe/*.json`)
# ---------------------------------------------------------------------------

def generate_recipes() -> None:
    rdir = DATA / "recipe"
    rdir.mkdir(parents=True, exist_ok=True)

    recipes = {
        # 1. Go-Kart (Iron Ingots + Seat Leather + Small Iron Engine + Standard Wheels)
        "go_kart": {
            "type": "minecraft:crafting_shaped",
            "category": "transportation",
            "pattern": [
                "I L",
                "III",
                "WEW",
            ],
            "key": {
                "I": "minecraft:iron_ingot",
                "L": "minecraft:leather",
                "W": "gokart:standard_wheel",
                "E": "gokart:small_engine_iron",
            },
            "result": {"id": "gokart:go_kart", "count": 1},
        },
        # 2. Small Iron Engine
        "small_engine_iron": {
            "type": "minecraft:crafting_shaped",
            "category": "misc",
            "pattern": [
                "III",
                "PFP",
                "IRI",
            ],
            "key": {
                "I": "minecraft:iron_ingot",
                "P": "minecraft:piston",
                "F": "minecraft:furnace",
                "R": "minecraft:redstone",
            },
            "result": {"id": "gokart:small_engine_iron", "count": 1},
        },
        # 3. Small Gold Engine (upgrade Iron Engine with Gold + Redstone)
        "small_engine_gold": {
            "type": "minecraft:crafting_shaped",
            "category": "misc",
            "pattern": [
                "GGG",
                "GEG",
                "RGR",
            ],
            "key": {
                "G": "minecraft:gold_ingot",
                "E": "gokart:small_engine_iron",
                "R": "minecraft:redstone",
            },
            "result": {"id": "gokart:small_engine_gold", "count": 1},
        },
        # 4. Small Diamond Engine (upgrade Gold Engine with Diamonds + Blaze Rod)
        "small_engine_diamond": {
            "type": "minecraft:crafting_shaped",
            "category": "misc",
            "pattern": [
                "DDD",
                "DED",
                "BDR",
            ],
            "key": {
                "D": "minecraft:diamond",
                "E": "gokart:small_engine_gold",
                "B": "minecraft:blaze_rod",
                "R": "minecraft:redstone_block",
            },
            "result": {"id": "gokart:small_engine_diamond", "count": 1},
        },
        # 5. Standard Wheel (makes 2 wheels per craft)
        "standard_wheel": {
            "type": "minecraft:crafting_shaped",
            "category": "misc",
            "pattern": [
                " W ",
                "WIW",
                " W ",
            ],
            "key": {
                "W": "minecraft:black_wool",
                "I": "minecraft:iron_ingot",
            },
            "result": {"id": "gokart:standard_wheel", "count": 2},
        },
        # 6. Sports Wheel
        "sports_wheel": {
            "type": "minecraft:crafting_shaped",
            "category": "misc",
            "pattern": [
                " L ",
                "GSG",
                " L ",
            ],
            "key": {
                "L": "minecraft:leather",
                "G": "minecraft:gold_ingot",
                "S": "gokart:standard_wheel",
            },
            "result": {"id": "gokart:sports_wheel", "count": 1},
        },
        # 7. Racing Slick Wheel
        "racing_wheel": {
            "type": "minecraft:crafting_shaped",
            "category": "misc",
            "pattern": [
                " D ",
                "RSR",
                " D ",
            ],
            "key": {
                "D": "minecraft:dried_kelp_block",
                "R": "minecraft:redstone",
                "S": "gokart:sports_wheel",
            },
            "result": {"id": "gokart:racing_wheel", "count": 1},
        },
        # 8. Vehicle Wrench
        "wrench": {
            "type": "minecraft:crafting_shaped",
            "category": "tools",
            "pattern": [
                "I I",
                " I ",
                " R ",
            ],
            "key": {
                "I": "minecraft:iron_ingot",
                "R": "minecraft:red_dye",
            },
            "result": {"id": "gokart:wrench", "count": 1},
        },
        # 9. Jerry Can (comes pre-filled with starter fuel!)
        "jerry_can": {
            "type": "minecraft:crafting_shaped",
            "category": "tools",
            "pattern": [
                " IR",
                "ICI",
                "III",
            ],
            "key": {
                "I": "minecraft:iron_ingot",
                "R": "minecraft:red_dye",
                "C": "minecraft:coal",
            },
            "result": {"id": "gokart:jerry_can", "count": 1},
        },
        # 10. Alternative Standard Wheel recipe using Dried Kelp (rubber feel!)
        "standard_wheel_kelp": {
            "type": "minecraft:crafting_shaped",
            "category": "misc",
            "pattern": [
                " K ",
                "KIK",
                " K ",
            ],
            "key": {
                "K": "minecraft:dried_kelp",
                "I": "minecraft:iron_ingot",
            },
            "result": {"id": "gokart:standard_wheel", "count": 2},
        },
    }

    for name, payload in recipes.items():
        (rdir / f"{name}.json").write_text(json.dumps(payload, indent=2) + "\n")


# ---------------------------------------------------------------------------
# Procedural Original OGG Vorbis Sounds (`assets/gokart/sounds/*.ogg`)
# ---------------------------------------------------------------------------

def generate_sounds() -> None:
    sdir = ASSETS / "sounds"
    sdir.mkdir(parents=True, exist_ok=True)

    # Write sounds.json
    sounds_json = {
        "engine.pulse": {
            "subtitle": "subtitles.gokart.engine",
            "sounds": [{"name": "gokart:engine_pulse", "attenuation_distance": 24, "stream": false_val()}]
            if False else [{"name": "gokart:engine_pulse", "attenuation_distance": 24, "stream": False}],
        },
        "horn": {
            "subtitle": "subtitles.gokart.horn",
            "sounds": [{"name": "gokart:horn", "attenuation_distance": 36, "stream": False}],
        },
        "drift": {
            "subtitle": "subtitles.gokart.drift",
            "sounds": [{"name": "gokart:drift", "attenuation_distance": 20, "stream": False}],
        },
        "boost": {
            "subtitle": "subtitles.gokart.boost",
            "sounds": [{"name": "gokart:boost", "attenuation_distance": 28, "stream": False}],
        },
        "wrench": {
            "subtitle": "subtitles.gokart.wrench",
            "sounds": [{"name": "gokart:wrench", "attenuation_distance": 12, "stream": False}],
        },
        "refuel": {
            "subtitle": "subtitles.gokart.refuel",
            "sounds": [{"name": "gokart:refuel", "attenuation_distance": 12, "stream": False}],
        },
    }
    (ASSETS / "sounds.json").write_text(json.dumps(sounds_json, indent=2) + "\n")

    # Skip re-encoding if all OGG files already exist unless `--force-sounds` is passed
    ogg_names = ["engine_pulse", "horn", "drift", "boost", "wrench", "refuel"]
    if "--force-sounds" not in sys.argv and all((sdir / f"{n}.ogg").exists() for n in ogg_names):
        return

    if "/tmp/pylibs" not in sys.path and os.path.isdir("/tmp/pylibs"):
        sys.path.insert(0, "/tmp/pylibs")

    import numpy as np
    import soundfile as sf

    rate = 44100
    rng = np.random.default_rng(20261116)

    def save_ogg(name: str, samples: np.ndarray) -> None:
        peak = float(np.max(np.abs(samples)))
        if peak > 1e-6:
            samples = (samples / peak) * 0.82
        sf.write(str(sdir / f"{name}.ogg"), samples.astype(np.float32), rate, format="OGG", subtype="VORBIS")

    # 1. `engine_pulse.ogg` — 2-stroke / 4-stroke single-cylinder kart motor pulse (0.32s seamless burst)
    t = np.linspace(0, 0.32, int(rate * 0.32), endpoint=False)
    f0 = 62.0
    saw = 2.0 * ((t * f0) % 1.0) - 1.0
    harm = 0.55 * np.sin(2 * np.pi * f0 * t) + 0.35 * np.sin(4 * np.pi * f0 * t) + 0.20 * saw
    chug = 0.72 + 0.28 * np.sin(2 * np.pi * 18.0 * t)
    env = np.minimum(t / 0.025, 1.0) * np.minimum((0.32 - t) / 0.04, 1.0)
    save_ogg("engine_pulse", harm * chug * env)

    # 2. `horn.ogg` — Classic cheerful dual-tone Go-Kart "BEEP-BEEP!" horn (0.38s)
    t = np.linspace(0, 0.38, int(rate * 0.38), endpoint=False)
    tone = (
        0.55 * np.sin(2 * np.pi * 440.0 * t)
        + 0.45 * np.sin(2 * np.pi * 554.37 * t)
        + 0.22 * np.sin(2 * np.pi * 880.0 * t)
        + 0.16 * np.sin(2 * np.pi * 1108.73 * t)
    )
    beep1 = (t >= 0.00) & (t < 0.15)
    beep2 = (t >= 0.19) & (t < 0.36)
    gate = np.where(beep1 | beep2, 1.0, 0.0)
    fade = np.minimum((0.38 - t) / 0.03, 1.0)
    save_ogg("horn", np.tanh(tone * 1.4) * gate * fade)

    # 3. `drift.ogg` — Tire rubber screech / asphalt skid (0.28s)
    n = int(rate * 0.28)
    t = np.linspace(0, 0.28, n, endpoint=False)
    noise = rng.standard_normal(n)
    # Band-limited tire squeal around 1150 Hz + 1680 Hz
    squeal = (
        0.45 * np.sin(2 * np.pi * (1120.0 + 90.0 * np.sin(2 * np.pi * 11.0 * t)) * t)
        + 0.25 * np.sin(2 * np.pi * 1690.0 * t)
        + 0.35 * noise
    )
    env = np.minimum(t / 0.02, 1.0) * np.minimum((0.28 - t) / 0.04, 1.0)
    save_ogg("drift", squeal * env)

    # 4. `boost.ogg` — Turbocharged kart launch roar (0.50s)
    n = int(rate * 0.50)
    t = np.linspace(0, 0.50, n, endpoint=False)
    freq = np.linspace(110.0, 340.0, n)
    phase = 2 * np.pi * np.cumsum(freq) / rate
    whoosh = 0.60 * np.sin(phase) + 0.30 * np.sin(2.0 * phase) + 0.25 * rng.standard_normal(n) * np.exp(-t * 5.0)
    env = np.minimum(t / 0.02, 1.0) * np.exp(-t * 3.2)
    save_ogg("boost", whoosh * env)

    # 5. `wrench.ogg` — Crisp mechanical ratchet clicks (0.26s)
    n = int(rate * 0.26)
    t = np.linspace(0, 0.26, n, endpoint=False)
    sig = np.zeros(n)
    for click_t in (0.01, 0.07, 0.13, 0.19):
        dt = np.maximum(t - click_t, 0.0)
        mask = t >= click_t
        sig += mask * np.sin(2 * np.pi * 2100.0 * dt) * np.exp(-dt * 120.0)
    save_ogg("wrench", sig)

    # 6. `refuel.ogg` — Liquid fuel glug-glug pour (0.42s)
    n = int(rate * 0.42)
    t = np.linspace(0, 0.42, n, endpoint=False)
    sig = np.zeros(n)
    for idx, gt in enumerate((0.02, 0.14, 0.26)):
        dt = np.maximum(t - gt, 0.0)
        mask = t >= gt
        f = 320.0 + idx * 55.0 + 180.0 * dt
        sig += mask * np.sin(2 * np.pi * f * dt) * np.exp(-dt * 26.0)
    save_ogg("refuel", sig)


# ---------------------------------------------------------------------------
# Bilingual Localization (`en_us.json` + `ro_ro.json`)
# ---------------------------------------------------------------------------

def generate_lang() -> None:
    ldir = ASSETS / "lang"
    ldir.mkdir(parents=True, exist_ok=True)

    en_us = {
        "gokart.mod.description": "Driveable 3D Go-Kart inspired by MrCrayfish's Vehicle Mod: Iron/Gold/Diamond engines, Standard/Sports/Racing wheels, 16-color dye painting, drift boost, fuel & tuning garage.",
        "item.gokart.go_kart": "Go-Kart",
        "item.gokart.small_engine_iron": "Small Iron Engine",
        "item.gokart.small_engine_gold": "Small Gold Engine",
        "item.gokart.small_engine_diamond": "Small Diamond Engine",
        "item.gokart.standard_wheel": "Standard Wheel",
        "item.gokart.sports_wheel": "Sports Wheel",
        "item.gokart.racing_wheel": "Racing Slick Wheel",
        "item.gokart.wrench": "Vehicle Wrench",
        "item.gokart.jerry_can": "Fuel Jerry Can",
        "subtitles.gokart.engine": "Go-Kart engine rumbles",
        "subtitles.gokart.horn": "Go-Kart horn honks",
        "subtitles.gokart.drift": "Go-Kart tires screech",
        "subtitles.gokart.boost": "Go-Kart turbo boost",
        "subtitles.gokart.wrench": "Wrench ratchets",
        "subtitles.gokart.refuel": "Go-Kart refuels",
        "gokart.engine.none": "No Engine",
        "gokart.engine.iron": "Iron Small Engine",
        "gokart.engine.gold": "Gold Small Engine",
        "gokart.engine.diamond": "Diamond Small Engine",
        "gokart.wheel.standard": "Standard Wheels",
        "gokart.wheel.sports": "Sports Wheels",
        "gokart.wheel.racing": "Racing Slick Wheels",
        "gokart.tooltip.engine": "Engine: %1$s",
        "gokart.tooltip.wheels": "Wheels: %1$s",
        "gokart.tooltip.paint": "Paint: %1$s",
        "gokart.tooltip.fuel": "Fuel: %1$s / %2$s mB (%3$s%%)",
        "gokart.tooltip.place_hint": "Right-click ground to deploy Go-Kart",
        "gokart.tooltip.wrench_hint": "Right-click Go-Kart: Tuning Garage | Sneak + Click: Pick up Kart",
        "gokart.tooltip.jerry_hint": "Right-click Go-Kart to refuel | Right-click Lava/Coal Block to refill",
        "gokart.tooltip.engine_iron": "Top Speed: 52 km/h | Balanced Torque",
        "gokart.tooltip.engine_gold": "Top Speed: 64 km/h | Snappy Acceleration",
        "gokart.tooltip.engine_diamond": "Top Speed: 76 km/h | Pro Racing Power & High Efficiency",
        "gokart.tooltip.wheel_standard": "Balanced grip on roads and dirt",
        "gokart.tooltip.wheel_sports": "Sharper steering & +12% drift boost charge",
        "gokart.tooltip.wheel_racing": "Maximum road speed & +25% drift boost charge",
        "gokart.hud.speed_kmh": "%1$s KM/H",
        "gokart.hud.speed_bps": "%1$s B/S",
        "gokart.hud.fuel": "FUEL",
        "gokart.hud.fuel_inf": "FUEL: INF",
        "gokart.hud.boost": "BOOST",
        "gokart.hud.drift": "DRIFT!",
        "gokart.hud.no_engine": "NO ENGINE!",
        "gokart.hud.no_fuel": "EMPTY FUEL!",
        "gokart.msg.placed": "Go-Kart deployed! Right-click to drive, Wrench to tune.",
        "gokart.msg.picked_up": "Go-Kart packed into inventory (all parts, paint & fuel saved).",
        "gokart.msg.painted": "Go-Kart painted %1$s!",
        "gokart.msg.engine_installed": "Installed %1$s!",
        "gokart.msg.engine_removed": "Removed %1$s from Go-Kart.",
        "gokart.msg.wheels_installed": "Fitted %1$s!",
        "gokart.msg.refueled": "Refueled Go-Kart (+%1$s mB -> %2$s%%).",
        "gokart.msg.tank_full": "Go-Kart fuel tank is already full!",
        "gokart.msg.jerry_refilled": "Jerry Can refilled (%1$s / %2$s mB).",
        "gokart.msg.fuel_mode_on": "Go-Kart fuel consumption: ENABLED",
        "gokart.msg.fuel_mode_off": "Go-Kart fuel consumption: INFINITE FUEL",
        "gokart.msg.kit_given": "Delivered complete Go-Kart Racing & Tuning Kit!",
        "gokart.ui.title": "GO-KART GARAGE & SETTINGS",
        "gokart.ui.subtitle": "MrCrayfish Vehicle Tribute • Horizon 26.3",
        "gokart.ui.no_kart": "No Go-Kart targeted nearby — showing Global Mod Settings",
        "gokart.ui.btn_pickup": "Pack Go-Kart to Item",
        "gokart.ui.btn_eject_engine": "Remove Engine",
        "gokart.ui.btn_refuel": "Refuel from Inventory",
        "gokart.ui.btn_fuel_toggle": "Require Fuel: %1$s",
        "gokart.ui.btn_cam_toggle": "Auto Third-Person (F5): %1$s",
        "gokart.ui.btn_unit_toggle": "Speedometer Unit: %1$s",
        "gokart.ui.btn_close": "Close [ESC]",
        "gokart.ui.on": "ON",
        "gokart.ui.off": "OFF",
        "gokart.ui.controls": "Controls: W/S Drive • A/D Steer • Space Drift / Charge Boost • H Horn • Shift Exit",
        "gokart.color.white": "Racing White",
        "gokart.color.orange": "Sunset Orange",
        "gokart.color.magenta": "Magenta",
        "gokart.color.light_blue": "Sky Blue",
        "gokart.color.yellow": "Grand Prix Yellow",
        "gokart.color.lime": "Acid Lime",
        "gokart.color.pink": "Hot Pink",
        "gokart.color.gray": "Gunmetal Gray",
        "gokart.color.light_gray": "Silver Metallic",
        "gokart.color.cyan": "Teal Cyan",
        "gokart.color.purple": "Royal Purple",
        "gokart.color.blue": "Cobalt Blue",
        "gokart.color.brown": "Bronze Brown",
        "gokart.color.green": "British Racing Green",
        "gokart.color.red": "Classic Rosso Red",
        "gokart.color.black": "Carbon Black",
    }

    ro_ro = {
        "gokart.mod.description": "Go-Kart 3D condus în timp real, inspirat din MrCrayfish's Vehicle Mod: motoare Fier/Aur/Diamant, roți Standard/Sport/Racing, vopsire în 16 culori, drift + boost, combustibil și garaj de tuning.",
        "item.gokart.go_kart": "Go-Kart",
        "item.gokart.small_engine_iron": "Motor Mic de Fier",
        "item.gokart.small_engine_gold": "Motor Mic de Aur",
        "item.gokart.small_engine_diamond": "Motor Mic de Diamant",
        "item.gokart.standard_wheel": "Roată Standard",
        "item.gokart.sports_wheel": "Roată Sport",
        "item.gokart.racing_wheel": "Roată Racing Slick",
        "item.gokart.wrench": "Cheie Mecanică (Vehicule)",
        "item.gokart.jerry_can": "Canistră de Combustibil",
        "subtitles.gokart.engine": "Motorul de Go-Kart toarce",
        "subtitles.gokart.horn": "Claxon de Go-Kart",
        "subtitles.gokart.drift": "Anvelopele de Go-Kart scârțâie",
        "subtitles.gokart.boost": "Boost turbo de Go-Kart",
        "subtitles.gokart.wrench": "Cheie mecanică în acțiune",
        "subtitles.gokart.refuel": "Alimentare Go-Kart",
        "gokart.engine.none": "Fără Motor",
        "gokart.engine.iron": "Motor Mic de Fier",
        "gokart.engine.gold": "Motor Mic de Aur",
        "gokart.engine.diamond": "Motor Mic de Diamant",
        "gokart.wheel.standard": "Roți Standard",
        "gokart.wheel.sports": "Roți Sport",
        "gokart.wheel.racing": "Roți Racing Slick",
        "gokart.tooltip.engine": "Motor: %1$s",
        "gokart.tooltip.wheels": "Roți: %1$s",
        "gokart.tooltip.paint": "Culoare: %1$s",
        "gokart.tooltip.fuel": "Combustibil: %1$s / %2$s mB (%3$s%%)",
        "gokart.tooltip.place_hint": "Click-dreapta pe sol pentru a plasa Go-Kartul",
        "gokart.tooltip.wrench_hint": "Click-dreapta pe Go-Kart: Garaj Tuning | Sneak + Click: Strânge Kartul",
        "gokart.tooltip.jerry_hint": "Click-dreapta pe Go-Kart: alimentează | Click-dreapta pe Lavă/Bloc de Cărbune: reumple",
        "gokart.tooltip.engine_iron": "Viteză max: 52 km/h | Cuplu echilibrat",
        "gokart.tooltip.engine_gold": "Viteză max: 64 km/h | Accelerație rapidă",
        "gokart.tooltip.engine_diamond": "Viteză max: 76 km/h | Putere maximă de curse & consum redus",
        "gokart.tooltip.wheel_standard": "Aderență echilibrată pe drum și pământ",
        "gokart.tooltip.wheel_sports": "Direcție precisă & +12% încărcare boost din drift",
        "gokart.tooltip.wheel_racing": "Viteză maximă pe asfalt/piatră & +25% boost din drift",
        "gokart.hud.speed_kmh": "%1$s KM/H",
        "gokart.hud.speed_bps": "%1$s B/S",
        "gokart.hud.fuel": "COMB.",
        "gokart.hud.fuel_inf": "COMB.: INF",
        "gokart.hud.boost": "BOOST",
        "gokart.hud.drift": "DRIFT!",
        "gokart.hud.no_engine": "FĂRĂ MOTOR!",
        "gokart.hud.no_fuel": "FĂRĂ COMBUSTIBIL!",
        "gokart.msg.placed": "Go-Kart plasat! Click-dreapta pentru a conduce, Cheie Mecanică pentru tuning.",
        "gokart.msg.picked_up": "Go-Kart strâns în inventar (piese, vopsea și combustibil păstrate).",
        "gokart.msg.painted": "Go-Kart vopsit în %1$s!",
        "gokart.msg.engine_installed": "Ai montat %1$s!",
        "gokart.msg.engine_removed": "Ai demontat %1$s de pe Go-Kart.",
        "gokart.msg.wheels_installed": "Ai echipat %1$s!",
        "gokart.msg.refueled": "Go-Kart alimentat (+%1$s mB -> %2$s%%).",
        "gokart.msg.tank_full": "Rezervorul Go-Kartului este deja plin!",
        "gokart.msg.jerry_refilled": "Canistră reumplută (%1$s / %2$s mB).",
        "gokart.msg.fuel_mode_on": "Consum combustibil Go-Kart: ACTIVAT",
        "gokart.msg.fuel_mode_off": "Consum combustibil Go-Kart: COMBUSTIBIL INFINIT",
        "gokart.msg.kit_given": "Ai primit pachetul complet Go-Kart Racing & Tuning!",
        "gokart.ui.title": "GARAJ GO-KART & SETĂRI",
        "gokart.ui.subtitle": "Tribut MrCrayfish Vehicle Mod • Horizon 26.3",
        "gokart.ui.no_kart": "Niciun Go-Kart selectat în apropiere — Setări Globale Mod",
        "gokart.ui.btn_pickup": "Strânge Go-Kartul în Item",
        "gokart.ui.btn_eject_engine": "Demontează Motorul",
        "gokart.ui.btn_refuel": "Alimentează din Inventar",
        "gokart.ui.btn_fuel_toggle": "Consum Combustibil: %1$s",
        "gokart.ui.btn_cam_toggle": "Cameră Automată F5: %1$s",
        "gokart.ui.btn_unit_toggle": "Unitate Vitezometru: %1$s",
        "gokart.ui.btn_close": "Închide [ESC]",
        "gokart.ui.on": "ACTIV",
        "gokart.ui.off": "OPRIT",
        "gokart.ui.controls": "Control: W/S Accelerație • A/D Viraj • Space Drift / Boost • H Claxon • Shift Coborâre",
        "gokart.color.white": "Alb Racing",
        "gokart.color.orange": "Portocaliu Sunset",
        "gokart.color.magenta": "Magenta",
        "gokart.color.light_blue": "Albastru Deschis",
        "gokart.color.yellow": "Galben Grand Prix",
        "gokart.color.lime": "Verde Lime",
        "gokart.color.pink": "Roz Electric",
        "gokart.color.gray": "Gri Gunmetal",
        "gokart.color.light_gray": "Argintiu Metalizat",
        "gokart.color.cyan": "Turcoaz",
        "gokart.color.purple": "Mov Imperial",
        "gokart.color.blue": "Albastru Cobalt",
        "gokart.color.brown": "Bronz Maro",
        "gokart.color.green": "Verde British Racing",
        "gokart.color.red": "Roșu Clasic Corsa",
        "gokart.color.black": "Negru Carbon",
    }

    (ldir / "en_us.json").write_text(json.dumps(en_us, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (ldir / "ro_ro.json").write_text(json.dumps(ro_ro, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def generate_mod_icon() -> None:
    # Render a crisp 128x128 badge icon at repo root (`icon.png`) for Horizon Launcher / Mod Browser
    kart_pal = {
        ".": None,
        "K": (24, 26, 32, 255),
        "G": (64, 68, 76, 255),
        "S": (186, 194, 206, 255),
        "R": (222, 48, 48, 255),
        "H": (250, 106, 96, 255),
        "D": (152, 26, 28, 255),
        "C": (48, 52, 60, 255),
        "Y": (246, 202, 56, 255),
    }
    kart_art = [
        "................",
        "................",
        ".........KK.....",
        "....CC...KSK....",
        "...CCCC..S......",
        "..KSSCC..S.HHH..",
        "..SSGCCC.SRRRRR.",
        ".HRRRRRRRRRRRRH.",
        ".DRRRRRYYRRRRRD.",
        ".GGGGGGGGGGGGGG.",
        "..KKKK....KKKK..",
        ".KGGGGK..KGGGGK.",
        ".KGSSGK..KGSSGK.",
        ".KGGGGK..KGGGGK.",
        "..KKKK....KKKK..",
        "................",
    ]
    size = 128
    pixels: list[tuple[int, int, int, int]] = []
    for y in range(size):
        for x in range(size):
            border = x < 4 or x >= size - 4 or y < 4 or y >= size - 4
            stripe = 96 <= y <= 104
            check = ((x // 16) + (y // 16)) % 2 == 0
            if border:
                bg = (224, 52, 48, 255)
            elif stripe:
                bg = (244, 246, 250, 255) if ((x // 8) % 2 == 0) else (28, 32, 40, 255)
            else:
                bg = (30, 35, 44, 255) if check else (24, 28, 36, 255)

            gx = (x - 16) // 6
            gy = (y - 14) // 6
            if 0 <= gx < 16 and 0 <= gy < 16 and (16 <= x < 112) and (14 <= y < 110):
                fg = kart_pal[kart_art[gy][gx]]
                pixels.append(fg if fg is not None else bg)
            else:
                pixels.append(bg)
    write_png(ROOT / "icon.png", size, size, pixels)


def main() -> None:
    generate_vehicle_textures()
    generate_item_textures()
    generate_models()
    generate_item_jsons()
    generate_recipes()
    generate_sounds()
    generate_lang()
    generate_mod_icon()
    print("Generated all Go-Kart assets, 3D models, OGG sounds, recipes, icon, and EN/RO translations.")


if __name__ == "__main__":
    main()
