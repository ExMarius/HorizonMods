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

    # 5. `kart_tire.png`: Vulcanized dark racing rubber with subtle tread channels
    pixels = []
    for y in range(16):
        for x in range(16):
            channel = x in (3, 12)
            sipe = ((y + (x // 4)) % 4 == 0) and (4 <= x <= 11)
            base = 24 if channel else (30 if sipe else 35)
            grain = ((x * 5 + y * 3) % 3) - 1
            v = max(16, base + grain)
            pixels.append((v, v + 1, v + 3, 255))
    write_png(bdir / "kart_tire.png", 16, 16, pixels)

    # 6. Wheel Alloy Rim textures: `wheel_standard.png`, `wheel_sports.png`, `wheel_racing.png`
    # Full 16x16 centered alloy rim discs (mapped [0,0,16,16] onto West/East wheel rim faces)
    wheel_configs = [
        ("wheel_standard.png", (196, 204, 214), (122, 130, 142), (70, 76, 86)),
        ("wheel_sports.png",   (246, 198, 56),  (54, 142, 232),  (44, 52, 68)),
        ("wheel_racing.png",   (236, 52, 50),   (248, 208, 62),  (38, 40, 48)),
    ]
    for fname, rim_hi, accent, recess in wheel_configs:
        pixels = []
        for y in range(16):
            for x in range(16):
                dx = x - 7.5
                dy = y - 7.5
                dist = math.hypot(dx, dy)
                if dist < 2.4:
                    c = (*accent, 255)
                elif dist > 6.4:
                    c = (*rim_hi, 255)
                else:
                    spoke = abs(dx) < 1.35 or abs(dy) < 1.35 or abs(abs(dx) - abs(dy)) < 1.15
                    c = (*rim_hi, 255) if spoke else (*recess, 255)
                pixels.append(c)
        write_png(bdir / fname, 16, 16, pixels)

    # 7. Engine block textures: `engine_iron.png`, `engine_gold.png`, `engine_diamond.png`
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

    # 1b. `off_roader.png` — Rugged 4x4 Emerald/Forest Off-Roader with Rollbar & Roof Lights!
    off_pal = {
        ".": T,
        "K": (22, 24, 30, 255),     # Tire / outline black
        "G": (62, 66, 74, 255),     # Heavy tread / bullbar / rollcage
        "S": (196, 204, 214, 255),  # Alloy rim / chrome bullbar
        "E": (42, 152, 72, 255),    # Forest emerald 4x4 body
        "H": (88, 206, 112, 255),   # Body highlight
        "D": (24, 98, 46, 255),     # Body shadow
        "Y": (252, 214, 68, 255),   # Roof KC spotlights / headlights
        "C": (48, 52, 60, 255),     # Seats
    }
    off_art = [
        "................",
        ".....GGGGGG.....",
        "....GYYGGYYG....",
        "....G..CC..G..K.",
        "...GGCCCCCCGSKK.",
        "..HHHHHHHHHHHHK.",
        ".GEEEEEEEEEEEEYS",
        "GGDEEEEEEEEEEDGG",
        ".GGGGGGGGGGGGGG.",
        "..KKKK....KKKK..",
        ".KGGGGK..KGGGGK.",
        ".KGSSGK..KGSSGK.",
        ".KGGGGK..KGGGGK.",
        "..KKKK....KKKK..",
        "................",
        "................",
    ]
    grid_to_png(idir / "off_roader.png", off_art, off_pal)

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

def box(
    from_xyz,
    to_xyz,
    tex: str,
    tint: bool = False,
    rot=None,
    full_uv_faces=(),
) -> dict:
    dx = max(0.5, min(16.0, abs(to_xyz[0] - from_xyz[0])))
    dy = max(0.5, min(16.0, abs(to_xyz[1] - from_xyz[1])))
    dz = max(0.5, min(16.0, abs(to_xyz[2] - from_xyz[2])))

    def centered_uv(w: float, h: float) -> list:
        u0 = round(max(0.0, 8.0 - w * 0.5), 2)
        v0 = round(max(0.0, 8.0 - h * 0.5), 2)
        u1 = round(min(16.0, u0 + w), 2)
        v1 = round(min(16.0, v0 + h), 2)
        return [u0, v0, u1, v1]

    uv_map = {
        "down": centered_uv(dx, dz),
        "up": centered_uv(dx, dz),
        "north": centered_uv(dx, dy),
        "south": centered_uv(dx, dy),
        "west": centered_uv(dz, dy),
        "east": centered_uv(dz, dy),
    }
    for d in full_uv_faces:
        uv_map[d] = [0.0, 0.0, 16.0, 16.0]

    faces = {}
    for d in ("down", "up", "north", "south", "west", "east"):
        f = {"texture": tex, "uv": uv_map[d]}
        if tint:
            f["tintindex"] = 0
        faces[d] = f
    elem = {"from": [round(v, 3) for v in from_xyz], "to": [round(v, 3) for v in to_xyz], "faces": faces}
    if rot is not None:
        axis, angle, origin = rot
        elem["rotation"] = {
            "origin": [round(v, 3) for v in origin],
            "axis": axis,
            "angle": round(float(angle), 2),
        }
    return elem


def v2m(vx: float, vy: float, vz: float) -> list:
    """Convert vehicle-centered texels (vx, vy, vz) where (0,0,0) is ground under entity
    center (+X left, +Y up, +Z forward) into block-model texels (mx, my, mz) around (8, 0, 8)."""
    return [8.0 + vx, vy, 8.0 + vz]


def vbox(vx0, vy0, vz0, vx1, vy1, vz1, tex: str, tint: bool = False, vrot=None, full_uv_faces=()) -> dict:
    mrot = None
    if vrot is not None:
        axis, angle, (ox, oy, oz) = vrot
        mrot = (axis, angle, v2m(ox, oy, oz))
    return box(
        v2m(min(vx0, vx1), min(vy0, vy1), min(vz0, vz1)),
        v2m(max(vx0, vx1), max(vy0, vy1), max(vz0, vz1)),
        tex,
        tint=tint,
        rot=mrot,
        full_uv_faces=full_uv_faces,
    )


def generate_models() -> None:
    mdir = ASSETS / "models" / "block"
    mdir.mkdir(parents=True, exist_ok=True)

    # =========================================================================
    # 1. `go_kart_body.json` — Compact Low-Slung Go-Kart Spaceframe & Body (v0.4.0)
    # =========================================================================
    # Canonical Vehicle Frame (16 texels = 1.0 block):
    #   Origin (0, 0, 0) = ground plane directly under kart entity center
    #   +X = Driver's LEFT, -X = Driver's RIGHT, +Y = UP, +Z = FORWARD
    #   Front Axle Z = +9.0 tx (+0.5625 b), Front Track X = ±7.8 tx (±0.4875 b), R = 3.76 tx
    #   Rear Axle  Z = -8.6 tx (-0.5375 b), Rear Track  X = ±8.2 tx (±0.5125 b), R = 4.00 tx
    #   Driver Seat Cushion Top = +3.15 tx (+0.196875 b) at Z = -1.80 tx (-0.1125 b)
    #   Steering Wheel Hub Pivot = (0.0, 9.85, +4.30) tx, shaft angle +32.0 deg X
    #   Rear Engine Deck Top = +2.40 tx (+0.1500 b), Engine Pivot = (0.0, 6.20, -8.70) tx
    body_elements = [
        # --- A. Slammed Racing Floorpan & Low-Slung Tubular Frame (0.90 tx ground clearance!) ---
        vbox(-4.5, 0.90, -4.4,  4.5, 1.75, 11.8, "#frame"),
        # Primary left & right longitudinal chassis rails
        vbox( 3.9, 0.95, -13.4,  5.0, 2.30, 13.8, "#frame"),
        vbox(-5.0, 0.95, -13.4, -3.9, 2.30, 13.8, "#frame"),
        # Footwell raised side rails (keeps driver's boots framed cleanly inside cockpit)
        vbox( 3.9, 1.75,  4.2,  4.6, 3.70, 11.6, "#frame"),
        vbox(-4.6, 1.75,  4.2, -3.9, 3.70, 11.6, "#frame"),

        # --- B. Compact Front Axle Beam & Tucked Kingpin Yokes (Zero monster-truck spindle gap!) ---
        vbox(-5.4, 2.95,  8.3,  5.4, 4.05,  9.7, "#frame"),
        vbox( 4.5, 2.75,  8.1,  5.35, 4.35, 9.9, "#chrome"),
        vbox(-5.35, 2.75, 8.1, -4.5, 4.35,  9.9, "#chrome"),
        # Compact chrome steering tie-rod behind front beam
        vbox(-5.0, 3.25,  7.2,  5.0, 3.75,  7.8, "#chrome"),

        # --- C. Low Wrap-Around Front Bumper, Swept Front Fairing & Nassau Cowling ---
        # Front tire spans Z = +5.24..+12.76 tx -> bumper wraps closely right in front at Z = +13.4..+15.6!
        vbox(-5.8, 1.10, 14.5,  5.8, 2.40, 15.6, "#frame"),
        vbox( 5.0, 1.10, 13.3,  8.8, 2.30, 14.4, "#frame", vrot=("y",  16.0, (5.4, 1.7, 13.8))),
        vbox(-8.8, 1.10, 13.3, -5.0, 2.30, 14.4, "#frame", vrot=("y", -16.0, (-5.4, 1.7, 13.8))),
        # Painted low front spoiler & swept corner wings (`tint = True`, framing front slicks closely!)
        vbox(-4.8, 1.40, 13.1,  4.8, 3.55, 15.3, "#body", tint=True, vrot=("x", 12.0, (0.0, 2.5, 14.2))),
        vbox( 3.9, 1.35, 13.0,  8.6, 3.30, 14.8, "#body", tint=True, vrot=("y",  16.0, (4.4, 2.3, 13.9))),
        vbox(-8.6, 1.35, 13.0, -3.9, 3.30, 14.8, "#body", tint=True, vrot=("y", -16.0, (-4.4, 2.3, 13.9))),
        # Narrowed front nose cone (`±3.70 tx` between Z=+4.8..+13.2 -> full ±25 deg tire lock clearance!)
        vbox(-3.70, 2.10, 8.4,  3.70, 4.85, 13.5, "#body", tint=True, vrot=("x", 15.0, (0.0, 3.5, 11.0))),
        # Sloped Nassau steering cowling rising smoothly to steering column (`tint = True`)
        vbox(-3.75, 3.60, 4.2,  3.75, 7.00,  8.9, "#body", tint=True, vrot=("x", 25.0, (0.0, 5.3,  6.5))),
        # Front number-plate racing crest on nose
        vbox(-2.2, 4.75,  7.6,  2.2, 5.40, 11.5, "#chrome", vrot=("x", 18.0, (0.0, 5.1,  9.5))),

        # --- D. Tight, Low-Slung Sidepods Hugging Front & Rear Wheels (Z = -4.25..+3.75, X = ±4.5..±7.7) ---
        # Clean 1.15 tx clearance behind turned ±25 deg front tire & 0.35 tx arch in front of rear tire!
        vbox( 4.5, 1.00, -4.25,  7.7, 4.70,  3.75, "#body", tint=True),
        vbox(-7.7, 1.00, -4.25, -4.5, 4.70,  3.75, "#body", tint=True),
        # Sculpted front intake shoulders & dark radiator grilles behind front tires
        vbox( 4.6, 1.10,  2.55,  7.4, 4.55,  4.05, "#body", tint=True, vrot=("y", -16.0, (6.0, 2.8, 3.3))),
        vbox(-7.4, 1.10,  2.55, -4.6, 4.55,  4.05, "#body", tint=True, vrot=("y",  16.0, (-6.0, 2.8, 3.3))),
        vbox( 5.0, 1.50,  3.70,  7.0, 4.05,  4.15, "#seat", vrot=("y", -16.0, (6.0, 2.8, 3.3))),
        vbox(-7.0, 1.50,  3.70, -5.0, 4.05,  4.15, "#seat", vrot=("y",  16.0, (-6.0, 2.8, 3.3))),
        # Low-profile black side rub-skirts along outer edge of sidepods
        vbox( 7.55, 1.10, -4.05, 8.05, 2.45,  3.55, "#frame"),
        vbox(-8.05, 1.10, -4.05, -7.55, 2.45, 3.55, "#frame"),
        # Inner wheel-well splash guards hugging inside of rear slicks (`vx = ±4.85..±5.45`)
        vbox( 4.85, 1.60, -11.4, 5.45, 5.20, -5.0, "#frame"),
        vbox(-5.45, 1.60, -11.4, -4.85, 5.20, -5.0, "#frame"),

        # --- E. Deep Slammed Bucket Racing Seat (Cushion Top Y = 3.15 tx, Backrest Flush at Z = -3.68 tx) ---
        vbox(-4.3, 1.75, -5.1,  4.3, 3.15,  2.3, "#seat"),
        # Left & right deep lateral hip/thigh bolsters
        vbox( 3.8, 2.75, -4.9,  5.0, 7.35,  1.7, "#seat"),
        vbox(-5.0, 2.75, -4.9, -3.8, 7.35,  1.7, "#seat"),
        # Contoured bucket backrest (`-5 deg` X-recline, inner face at Z = -3.65 flush with driver back!)
        vbox(-4.2, 3.00, -5.1,  4.2, 13.30, -3.65, "#seat", vrot=("x", -5.0, (0.0, 3.15, -4.3))),
        # Integrated headrest pad & painted outer fiberglass shell (`tint = True`)
        vbox(-2.8, 12.90, -5.4, 2.8, 15.10, -3.85, "#seat", vrot=("x", -4.0, (0.0, 13.3, -4.6))),
        vbox(-3.9, 3.40, -5.65, 3.9, 12.90, -4.95, "#body", tint=True, vrot=("x", -5.0, (0.0, 3.15, -4.3))),

        # --- F. Coaxial +32.0 deg Steering Column & Chrome Shaft (Pivot (0.0, 9.85, +4.30)) + Pedals ---
        vbox(-1.5, 1.75,  5.6,  1.5, 6.20,  7.4, "#frame"),
        vbox(-0.55, 9.30, 4.30, 0.55, 10.40, 7.4, "#chrome", vrot=("x", 32.0, (0.0, 9.85, 4.30))),
        vbox(-0.95, 8.90, 4.85, 0.95, 10.80, 5.95, "#frame", vrot=("x", 32.0, (0.0, 9.85, 4.30))),
        # Chrome Throttle & Brake Pedals positioned right at driver's boots (`Z = +10.0 tx`)
        vbox( 1.5, 1.75,  9.8,  3.1, 5.30, 10.6, "#chrome", vrot=("x", -18.0, (2.3, 2.0, 10.2))),
        vbox(-3.1, 1.75,  9.8, -1.5, 5.30, 10.6, "#chrome", vrot=("x", -18.0, (-2.3, 2.0, 10.2))),
        vbox(-3.3, 1.75,  8.5,  3.3, 2.25,  9.2, "#frame"),

        # --- G. Low Rear Engine Deck (Top Y = 2.40 tx), Coaxial Live Rear Axle (Y=4.00, Z=-8.60) & Bumper ---
        vbox(-4.5, 1.25, -13.0,  4.5, 2.40, -4.6, "#frame"),
        # Axle bearing hangers at Z = -8.60
        vbox( 3.8, 1.90, -9.7,  5.1, 5.10, -7.5, "#frame"),
        vbox(-5.1, 1.90, -9.7, -3.8, 5.10, -7.5, "#frame"),
        # Full-width live chrome rear axle coaxial with R=4.00 rear slicks at (Y=4.00, Z=-8.60)!
        vbox(-6.4, 3.45, -9.15, 6.4, 4.55, -8.05, "#chrome"),
        # Tucked ventilated brake rotor + painted caliper (+X) and drive sprocket (-X, under engine clutch)
        vbox( 4.15, 2.25, -10.3, 4.70, 5.85, -6.9, "#chrome"),
        vbox( 4.00, 4.05, -7.4,  4.85, 6.05, -6.2, "#body", tint=True),
        vbox(-4.15, 2.35, -10.2, -3.45, 5.65, -7.0, "#frame"),
        # Integrated rear crash bumper & painted valence right behind rear slicks (`Z = -12.8..-14.0`)
        vbox(-7.6, 1.35, -14.0,  7.6, 2.70, -12.9, "#frame"),
        vbox(-5.2, 1.80, -13.6,  5.2, 3.65, -12.4, "#body", tint=True),
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

    # =========================================================================
    # 2. `go_kart_steering_wheel.json` — 8-Segment Round 3-Spoke Sport Wheel
    # =========================================================================
    # Authored symmetrically around (8.0, 8.0, 8.0) in XY plane:
    #   - Outer diameter = 6.2 tx (radius 3.1 tx), scaled 0.85 -> 0.33 b diameter
    #   - Hub center is EXACTLY (8.0, 8.0, 8.0) -> zero wobble when spinning around Z!
    sw_elements = [
        # Central machined aluminum boss + shaft collar
        box([6.9, 6.9, 7.2], [9.1, 9.1, 8.9], "#chrome"),
        box([7.4, 7.4, 6.95], [8.6, 8.6, 7.25], "#frame"),
        # 8-segment octagonal sport grip ring (4 cardinal + 4 rotated 45 deg around Z at [8,8,8])
        # Top segment includes racing 12-o'clock chrome/stripe marker!
        box([6.6, 10.2, 7.45], [9.4, 11.15, 8.55], "#seat"),
        box([7.65, 10.25, 7.40], [8.35, 11.20, 8.60], "#chrome"),
        box([6.6, 4.85, 7.45], [9.4, 5.8, 8.55], "#seat"),
        box([4.85, 6.6, 7.45], [5.8, 9.4, 8.55], "#seat"),
        box([10.2, 6.6, 7.45], [11.15, 9.4, 8.55], "#seat"),
        box([6.6, 10.2, 7.48], [9.4, 11.12, 8.52], "#seat", rot=("z", 45.0, [8.0, 8.0, 8.0])),
        box([6.6, 4.88, 7.48], [9.4, 5.8, 8.52], "#seat", rot=("z", 45.0, [8.0, 8.0, 8.0])),
        box([4.88, 6.6, 7.48], [5.8, 9.4, 8.52], "#seat", rot=("z", 45.0, [8.0, 8.0, 8.0])),
        box([10.2, 6.6, 7.48], [11.12, 9.4, 8.52], "#seat", rot=("z", 45.0, [8.0, 8.0, 8.0])),
        # 3-spoke brushed aluminum spider (left, right, bottom)
        box([5.6, 7.55, 7.65], [7.1, 8.45, 8.35], "#chrome", rot=("z",  12.0, [8.0, 8.0, 8.0])),
        box([8.9, 7.55, 7.65], [10.4, 8.45, 8.35], "#chrome", rot=("z", -12.0, [8.0, 8.0, 8.0])),
        box([7.55, 5.6, 7.65], [8.45, 7.1, 8.35], "#chrome"),
    ]
    (mdir / "go_kart_steering_wheel.json").write_text(
        json.dumps(
            {
                "textures": {
                    "seat": "gokart:block/kart_seat",
                    "chrome": "gokart:block/kart_chrome",
                    "frame": "gokart:block/kart_frame",
                },
                "elements": sw_elements,
            },
            indent=2,
        )
        + "\n"
    )

    # =========================================================================
    # 3. 16-Sided Cylindrical Kart Wheels (`wheel_standard`, `wheel_sports`, `wheel_racing`)
    # =========================================================================
    # Authored symmetrically around (8.0, 8.0, 8.0):
    #   - Chunky kart slick outer radius R = 4.00 tx (Y, Z in [4.00, 12.00], 0.50 b diameter!), half-chord = 0.80 tx
    #   - 4 boxes at 0, 22.5, 45, 67.5 deg around X -> smooth closed 16-gon slick cylinder!
    #   - Tire width X in [5.60, 10.40] (4.80 tx = ±2.40 tx from hub)
    #   - Recessed 8-sided alloy rim disc with centered [0,0,16,16] spoke UVs + chrome center-lock nut
    for wname, rim_tex in [
        ("wheel_standard", "gokart:block/wheel_standard"),
        ("wheel_sports", "gokart:block/wheel_sports"),
        ("wheel_racing", "gokart:block/wheel_racing"),
    ]:
        w_elements = []
        for idx, ang in enumerate((0.0, 22.5, 45.0, 67.5)):
            eps = 0.012 * idx
            r = None if ang == 0.0 else ("x", ang, [8.0, 8.0, 8.0])
            w_elements.append(
                box([5.60 + eps, 4.00, 7.20], [10.40 - eps, 12.00, 8.80], "#tire", rot=r)
            )
            w_elements.append(
                box([5.60 + eps, 7.20, 4.00], [10.40 - eps, 8.80, 12.00], "#tire", rot=r)
            )
        # Recessed dark tire sidewall ring (octagonal, R=2.95 tx, chord=1.22 tx -> true circle inside tire!)
        for r_ang in (0.0, 45.0):
            rr = None if r_ang == 0.0 else ("x", r_ang, [8.0, 8.0, 8.0])
            w_elements.append(box([5.52, 5.05, 6.78], [10.48, 10.95, 9.22], "#tire", rot=rr))
            w_elements.append(box([5.52, 6.78, 5.05], [10.48, 9.22, 10.95], "#tire", rot=rr))
        # True round 8-sided deep-dish alloy wheel rim (R=2.25 tx, chord=0.93 tx -> zero star spikes!)
        for idx_r, r_ang in enumerate((0.0, 45.0)):
            eps_r = 0.01 * idx_r
            rr = None if r_ang == 0.0 else ("x", r_ang, [8.0, 8.0, 8.0])
            w_elements.append(
                box(
                    [5.42 + eps_r, 5.75, 7.07],
                    [10.58 - eps_r, 10.25, 8.93],
                    "#rim",
                    rot=rr,
                    full_uv_faces=("west", "east"),
                )
            )
            w_elements.append(
                box(
                    [5.43 + eps_r, 7.07, 5.75],
                    [10.57 - eps_r, 8.93, 10.25],
                    "#rim",
                    rot=rr,
                    full_uv_faces=("west", "east"),
                )
            )
        # Center-lock chrome racing hub nut & inner spindle boss
        w_elements.append(box([5.22, 7.20, 7.20], [10.78, 8.80, 8.80], "#chrome"))
        (mdir / f"{wname}.json").write_text(
            json.dumps(
                {
                    "textures": {
                        "tire": "gokart:block/kart_tire",
                        "rim": rim_tex,
                        "chrome": "gokart:block/kart_chrome",
                    },
                    "elements": w_elements,
                },
                indent=2,
            )
            + "\n"
        )

    # =========================================================================
    # 4. Rear Racing Small Engines (`engine_iron`, `engine_gold`, `engine_diamond`)
    # =========================================================================
    # Authored around (8.0, 8.0, 8.0) with +Z forward (toward seat) and -Z rear (toward bumper):
    #   - Mounted at ENGINE_PIVOT = (0.0, 7.6, -11.4) tx with scale 0.95 (NO 180 flip!)
    #   - Crankcase bottom at my = 3.80 -> lands at vy = 7.6 - 4.2*0.95 = 3.61 tx (flush on 3.60 deck!)
    #   - Inclined finned cylinder head (-18 deg X), pull-starter shroud, top fuel tank & pod filter,
    #     and twin upswept chrome exhaust headers + mufflers pointing cleanly backward (-Z)!
    for ename, tex in [
        ("engine_iron", "gokart:block/engine_iron"),
        ("engine_gold", "gokart:block/engine_gold"),
        ("engine_diamond", "gokart:block/engine_diamond"),
    ]:
        e_elements = [
            # Lower bolted crankcase & sump block (rests flush on rear engine deck)
            box([4.9, 3.8, 5.2], [11.1, 7.6, 10.8], "#frame"),
            # Inclined finned racing cylinder barrel & tier-colored head
            box([5.2, 6.4, 5.6], [10.8, 11.4, 10.2], "#engine", rot=("x", -18.0, [8.0, 7.2, 8.0])),
            # Left-side (+X) recoil pull-starter housing & center hub (away from drive chain)
            box([11.0, 4.3, 5.8], [11.8, 8.5, 10.0], "#engine"),
            box([11.75, 5.6, 7.1], [12.05, 7.2, 8.7], "#chrome"),
            # Right-side (-X) centrifugal clutch & chain guard aligned directly over right axle sprocket!
            box([4.1, 3.8, 6.4], [5.0, 6.9, 9.9], "#chrome"),
            # Top auxiliary fuel tank + chrome filler cap
            box([5.5, 8.8, 8.6], [10.5, 11.2, 11.4], "#frame"),
            box([7.3, 11.2, 9.4], [8.7, 11.8, 10.8], "#chrome"),
            # High-flow conical pod air intake filter
            box([6.4, 9.6, 4.4], [9.6, 11.8, 7.2], "#chrome", rot=("x", 10.0, [8.0, 10.5, 5.8])),
            # Twin upswept chrome exhaust headers + dark racing mufflers + bright chrome tailpipe tips!
            box([5.5, 7.2, 1.6], [6.9, 8.6, 6.2], "#chrome", rot=("x", 12.0, [6.2, 7.9, 6.0])),
            box([9.1, 7.2, 1.6], [10.5, 8.6, 6.2], "#chrome", rot=("x", 12.0, [9.8, 7.9, 6.0])),
            box([5.35, 7.05, 0.5], [7.05, 8.75, 2.4], "#frame", rot=("x", 12.0, [6.2, 7.9, 6.0])),
            box([8.95, 7.05, 0.5], [10.65, 8.75, 2.4], "#frame", rot=("x", 12.0, [9.8, 7.9, 6.0])),
            box([5.65, 7.35, 0.0], [6.75, 8.45, 0.6], "#chrome", rot=("x", 12.0, [6.2, 7.9, 6.0])),
            box([9.25, 7.35, 0.0], [10.35, 8.45, 0.6], "#chrome", rot=("x", 12.0, [9.8, 7.9, 6.0])),
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

    # =========================================================================
    # 5. 4x4 Baja / Trail Off-Roader Body (`off_roader_body.json`)
    # =========================================================================
    # Authored around (8.0, 0.0, 8.0) in model texels (`mx = 8 + vx_m`, `my = vy_m`, `mz = 8 + vz_m`)
    # and rendered with `OFFROADER_BODY_SCALE = [1.40, 1.35, 1.40]`:
    #   - Every element stays strictly inside [-2.0, +26.0] ⊂ [-16.0, +32.0]!
    #   - Scaled in world to 2.15 blocks wide x 3.05 blocks long lifted 4x4!
    #   - Left-hand driver bucket seat at vx_m = +3.80 (VX = +5.32 tx) + right passenger seat at vx_m = -3.80!
    def obox(vfrom, vto, tex, tint=None, rot=None, full_uv_faces=()):
        f = [round(vfrom[0] + 8.0, 4), round(vfrom[1], 4), round(vfrom[2] + 8.0, 4)]
        t = [round(vto[0] + 8.0, 4), round(vto[1], 4), round(vto[2] + 8.0, 4)]
        r = None
        if rot is not None:
            ax, ang, orig = rot
            r = (ax, ang, [round(orig[0] + 8.0, 4), round(orig[1], 4), round(orig[2] + 8.0, 4)])
        return box(f, t, tex, tint=tint, rot=r, full_uv_faces=full_uv_faces)

    off_elements = [
        # --- Heavy Ladder Frame Rails, Skidplate & Solid 4x4 Axles ---
        obox([-4.6, 3.0, -15.4], [-3.2, 4.4, 15.6], "#frame"),
        obox([3.2, 3.0, -15.4], [4.6, 4.4, 15.6], "#frame"),
        obox([-4.6, 3.2, 13.8], [4.6, 4.6, 15.8], "#frame"),
        obox([-4.6, 3.2, -15.8], [4.6, 4.6, -13.8], "#frame"),
        # Angled front alloy skidplate
        obox([-4.4, 2.8, 12.2], [4.4, 4.2, 16.0], "#chrome", rot=("x", -18.0, [0.0, 3.5, 14.0])),
        # Front & Rear solid 4x4 axle tubes + differential pumpkins + coil-over shocks
        obox([-8.6, 2.35, 10.05], [8.6, 3.15, 10.95], "#chrome"),
        obox([-1.8, 1.85, 9.6], [1.8, 3.65, 11.4], "#frame"),
        obox([-8.6, 2.35, -10.95], [8.6, 3.15, -10.05], "#chrome"),
        obox([-1.8, 1.85, -11.4], [1.8, 3.65, -9.6], "#frame"),
        obox([5.6, 3.0, 10.0], [6.5, 8.2, 11.0], "#chrome"),
        obox([-6.5, 3.0, 10.0], [-5.6, 8.2, 11.0], "#chrome"),
        obox([5.6, 3.0, -11.0], [6.5, 8.2, -10.0], "#chrome"),
        obox([-6.5, 3.0, -11.0], [-5.6, 8.2, -10.0], "#chrome"),

        # --- Cabin Floorpan, Rock-Slider Side Steps & Center Console ---
        obox([-7.8, 3.5, -6.2], [7.8, 4.2, 5.8], "#seat"),
        obox([-9.4, 3.6, -5.4], [-8.0, 4.4, 5.2], "#frame"),
        obox([8.0, 3.6, -5.4], [9.4, 4.4, 5.2], "#frame"),
        # Center transmission tunnel + 4WD transfer shifter
        obox([-1.1, 4.2, -5.2], [1.1, 6.2, 4.8], "#frame"),
        obox([-0.35, 6.2, 0.8], [0.35, 8.8, 1.5], "#chrome", rot=("x", -12.0, [0.0, 6.2, 1.15])),
        obox([-0.65, 8.6, 0.5], [0.65, 9.5, 1.8], "#seat", rot=("x", -12.0, [0.0, 6.2, 1.15])),

        # --- Sculpted Paintable 4x4 Hood, 7-Slot Grille, Headlights & Bullbar ---
        obox([-5.5, 4.4, 5.4], [5.5, 9.6, 15.2], "#body", tint=0),
        obox([-5.2, 9.6, 5.4], [5.2, 10.6, 14.8], "#body", tint=0),
        # Dark charcoal raised V8 power-bulge hood scoop
        obox([-2.4, 10.5, 7.2], [2.4, 11.35, 13.4], "#frame"),
        obox([-1.8, 10.65, 13.3], [1.8, 11.2, 13.7], "#chrome"),
        # Front radiator grille plate + twin round LED headlights
        obox([-5.1, 5.0, 15.15], [5.1, 9.3, 15.55], "#frame"),
        obox([2.8, 6.6, 15.35], [4.7, 8.5, 15.85], "#chrome"),
        obox([-4.7, 6.6, 15.35], [-2.8, 8.5, 15.85], "#chrome"),
        # Heavy tubular front bullbar & winch bumper
        obox([-7.8, 4.0, 15.4], [7.8, 5.6, 16.8], "#frame"),
        obox([-4.8, 5.6, 15.9], [-4.0, 9.8, 16.7], "#frame"),
        obox([4.0, 5.6, 15.9], [4.8, 9.8, 16.7], "#frame"),
        obox([-4.8, 9.2, 15.9], [4.8, 10.0, 16.7], "#frame"),

        # --- Muscular Flared Off-Road Wheel Arches & Half-Doors (Tintable) ---
        # Front left/right high-clearance flared fenders (clear ±24 deg steered giant tires!)
        obox([5.5, 8.5, 5.6], [9.8, 10.0, 14.8], "#body", tint=0),
        obox([-9.8, 8.5, 5.6], [-5.5, 10.0, 14.8], "#body", tint=0),
        obox([5.5, 5.2, 5.2], [9.4, 8.6, 6.3], "#frame"),
        obox([-9.4, 5.2, 5.2], [-5.5, 8.6, 6.3], "#frame"),
        # Sculpted cut-out off-road half-doors
        obox([7.4, 4.2, -5.8], [8.5, 9.2, 5.6], "#body", tint=0),
        obox([-8.5, 4.2, -5.8], [-7.4, 9.2, 5.6], "#body", tint=0),
        # Rear body tub, flared rear fenders & tailgate
        obox([6.8, 8.5, -15.0], [9.8, 10.0, -5.6], "#body", tint=0),
        obox([-9.8, 8.5, -15.0], [-6.8, 10.0, -5.6], "#body", tint=0),
        obox([6.8, 4.4, -15.4], [8.5, 10.2, -5.6], "#body", tint=0),
        obox([-8.5, 4.4, -15.4], [-6.8, 10.2, -5.6], "#body", tint=0),
        obox([-6.8, 4.4, -15.2], [6.8, 5.6, -5.8], "#seat"),
        obox([-7.8, 4.4, -15.6], [7.8, 10.0, -14.6], "#body", tint=0),
        obox([-8.2, 3.6, -16.4], [8.2, 5.0, -15.2], "#frame"),
        # Twin rear chrome exhaust tailpipes under rear bumper
        obox([3.6, 3.0, -17.0], [4.7, 4.0, -15.0], "#chrome"),
        obox([-4.7, 3.0, -17.0], [-3.6, 4.0, -15.0], "#chrome"),

        # --- Dashboard, Left-Side Steering Column, Pedals & Slanted Windshield Frame ---
        obox([-7.6, 7.6, 4.0], [7.6, 10.8, 5.6], "#seat"),
        # Left driver gauge pod & chrome steering shaft terminating at vx_m=+3.80, vy_m=11.56, vz_m=+3.43
        obox([2.1, 10.4, 4.1], [5.5, 11.6, 5.5], "#frame"),
        obox([3.3, 11.05, 3.43], [4.3, 12.05, 5.4], "#chrome", rot=("x", 34.0, [3.80, 11.56, 3.43])),
        # Driver accelerator & brake pedals in left footwell
        obox([2.4, 4.2, 4.6], [3.3, 6.2, 5.2], "#chrome", rot=("x", -20.0, [2.85, 4.2, 4.9])),
        obox([4.2, 4.2, 4.6], [5.1, 6.2, 5.2], "#chrome", rot=("x", -20.0, [4.65, 4.2, 4.9])),
        # Slanted A-pillar windshield frame + top header bar
        obox([7.1, 10.2, 4.6], [8.1, 16.4, 5.5], "#body", tint=0, rot=("x", -20.0, [7.6, 10.4, 5.0])),
        obox([-8.1, 10.2, 4.6], [-7.1, 16.4, 5.5], "#body", tint=0, rot=("x", -20.0, [-7.6, 10.4, 5.0])),
        obox([-8.1, 15.6, 2.5], [8.1, 16.6, 3.6], "#body", tint=0),

        # --- Open-Top Tubular Roll Cage & Quad Roof Off-Road Light Bar ---
        obox([7.0, 9.8, -5.8], [7.9, 16.8, -4.9], "#frame"),
        obox([-7.9, 9.8, -5.8], [-7.0, 16.8, -4.9], "#frame"),
        obox([-7.9, 16.0, -5.8], [7.9, 16.9, -4.9], "#frame"),
        obox([7.0, 16.0, -5.8], [7.9, 16.8, 3.2], "#frame"),
        obox([-7.9, 16.0, -5.8], [-7.0, 16.8, 3.2], "#frame"),
        # Slanted rear roll-cage downbars into bed
        obox([7.0, 9.8, -14.2], [7.8, 16.4, -5.4], "#frame", rot=("x", 32.0, [7.4, 10.2, -13.8])),
        obox([-7.8, 9.8, -14.2], [-7.0, 16.4, -5.4], "#frame", rot=("x", 32.0, [-7.4, 10.2, -13.8])),
        # Quad roof spotlights on front header
        obox([4.2, 16.6, 2.4], [6.0, 18.2, 3.7], "#chrome"),
        obox([1.2, 16.6, 2.4], [3.0, 18.2, 3.7], "#chrome"),
        obox([-3.0, 16.6, 2.4], [-1.2, 18.2, 3.7], "#chrome"),
        obox([-6.0, 16.6, 2.4], [-4.2, 18.2, 3.7], "#chrome"),

        # --- Twin Front Racing Bucket Seats (Left Driver vx=+3.80, Right Passenger vx=-3.80) & Rear Bench ---
        # Left Driver Bucket Seat
        obox([1.6, 4.2, -3.8], [6.0, 5.4, 0.2], "#seat"),
        obox([1.6, 5.2, -4.6], [6.0, 11.8, -3.4], "#seat", rot=("x", -10.0, [3.8, 5.4, -3.8])),
        obox([2.4, 11.6, -4.8], [5.2, 13.4, -3.6], "#body", tint=0),
        # Right Passenger Bucket Seat
        obox([-6.0, 4.2, -3.8], [-1.6, 5.4, 0.2], "#seat"),
        obox([-6.0, 5.2, -4.6], [-1.6, 11.8, -3.4], "#seat", rot=("x", -10.0, [-3.8, 5.4, -3.8])),
        obox([-5.2, 11.6, -4.8], [-2.4, 13.4, -3.6], "#body", tint=0),
        # Elevated Rear Safari Bench in cargo bed
        obox([-6.2, 5.6, -11.8], [6.2, 7.2, -8.2], "#seat"),
        obox([-6.2, 7.2, -12.6], [6.2, 11.6, -11.4], "#seat"),
    ]
    (mdir / "off_roader_body.json").write_text(
        json.dumps(
            {
                "textures": {
                    "body": "gokart:block/kart_body",
                    "frame": "gokart:block/kart_frame",
                    "chrome": "gokart:block/kart_chrome",
                    "seat": "gokart:block/kart_seat",
                },
                "elements": off_elements,
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
    "off_roader",
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
        # 11. 4x4 Off-Roader (Iron Block + Twin Leather Seats + Gold/Iron Engine + Sports Wheels)
        "off_roader": {
            "type": "minecraft:crafting_shaped",
            "category": "transportation",
            "pattern": [
                "LGL",
                "IBI",
                "WEW",
            ],
            "key": {
                "L": "minecraft:leather",
                "G": "minecraft:glass_pane",
                "I": "minecraft:iron_ingot",
                "B": "minecraft:iron_block",
                "W": "gokart:sports_wheel",
                "E": "gokart:small_engine_gold",
            },
            "result": {"id": "gokart:off_roader", "count": 1},
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
        "gokart.mod.description": "Driveable 3D Go-Kart & 4x4 Off-Roader inspired by MrCrayfish's Vehicle Mod: Iron/Gold/Diamond engines, Standard/Sports/Racing wheels, 16-color dye painting, drift boost, fuel & tuning garage.",
        "item.gokart.go_kart": "Go-Kart",
        "item.gokart.off_roader": "4x4 Off-Roader",
        "gokart.vehicle.go_kart": "Go-Kart",
        "gokart.vehicle.off_roader": "4x4 Off-Roader",
        "gokart.tooltip.place_off_roader": "Right-click ground to deploy 4x4 Off-Roader (climbs 1-block terrain!)",
        "gokart.msg.placed_off_roader": "4x4 Off-Roader deployed! Right-click to drive, Wrench to tune.",
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
        "gokart.mod.description": "Go-Kart 3D & Off-Roader 4x4 conduse în timp real, inspirate din MrCrayfish's Vehicle Mod: motoare Fier/Aur/Diamant, roți Standard/Sport/Racing, vopsire în 16 culori, drift + boost, combustibil și garaj de tuning.",
        "item.gokart.go_kart": "Go-Kart",
        "item.gokart.off_roader": "Off-Roader 4x4",
        "gokart.vehicle.go_kart": "Go-Kart",
        "gokart.vehicle.off_roader": "Off-Roader 4x4",
        "gokart.tooltip.place_off_roader": "Click-dreapta pe sol pentru a plasa Off-Roader-ul 4x4 (urcă blocuri întregi!)",
        "gokart.msg.placed_off_roader": "Off-Roader 4x4 plasat! Click-dreapta pentru a conduce, Cheie Mecanică pentru tuning.",
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
