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

    # 1. `kart_body.png`: Smooth automotive metallic clear-coat (neutral silver-white so `tintindex: 0`
    # multiplies cleanly with all 16 Minecraft dye colors into rich lacquered bodywork!)
    pixels = []
    for y in range(16):
        for x in range(16):
            seam = x in (0, 15) or y in (0, 15)
            bevel_hi = y == 1 or x == 1
            spec_band = y in (2, 3) and 2 <= x <= 13
            bevel_lo = y == 14 or x == 14
            if seam:
                v = 194
            elif spec_band:
                v = 253
            elif bevel_hi:
                v = 246
            elif bevel_lo:
                v = 210
            else:
                # Subtle diagonal metallic flake gradient
                grad = int(6 * (1.0 - (y / 15.0)))
                flake = ((x * 5 + y * 3) % 3) - 1
                v = min(252, max(214, 228 + grad + flake))
            pixels.append((v, v, v, 255))
    write_png(bdir / "kart_body.png", 16, 16, pixels)

    # 2. `kart_frame.png`: Dark powder-coated tubular steel chassis & weld-shaded gunmetal
    pixels = []
    for y in range(16):
        for x in range(16):
            edge = x in (0, 15) or y in (0, 15)
            hi = y in (2, 3) and 2 <= x <= 13
            tread = (x % 4 == 1 and y % 4 == 1) or (x % 4 == 3 and y % 4 == 3)
            if edge:
                c = (30, 33, 39, 255)
            elif hi:
                c = (74, 80, 90, 255)
            elif tread:
                c = (64, 69, 78, 255)
            else:
                v = 46 + ((x * 3 + y * 5) % 6)
                c = (v, v + 3, v + 7, 255)
            pixels.append(c)
    write_png(bdir / "kart_frame.png", 16, 16, pixels)

    # 2b. `kart_carbon.png`: Woven 2x2 twill carbon-fiber composite (splitters, mufflers, aero trim)
    pixels = []
    for y in range(16):
        for x in range(16):
            border = x in (0, 15) or y in (0, 15)
            twill = (x + y) % 4
            if border:
                c = (20, 22, 26, 255)
            elif twill == 0:
                c = (66, 71, 80, 255)
            elif twill == 1:
                c = (48, 52, 60, 255)
            elif twill == 2:
                c = (28, 30, 36, 255)
            else:
                c = (36, 39, 46, 255)
            pixels.append(c)
    write_png(bdir / "kart_carbon.png", 16, 16, pixels)

    # 2c. `kart_grille.png`: Dark honeycomb radiator / air-intake mesh with metallic cell rims
    pixels = []
    for y in range(16):
        for x in range(16):
            frame = x in (0, 15) or y in (0, 15)
            row = y % 4
            shift = 2 if (y // 4) % 2 == 1 else 0
            col = (x + shift) % 4
            hole = row in (1, 2) and col in (1, 2)
            rim_hi = row == 0 and col in (1, 2)
            if frame:
                c = (38, 42, 48, 255)
            elif hole:
                c = (14, 16, 20, 255)
            elif rim_hi:
                c = (94, 102, 114, 255)
            else:
                c = (54, 59, 68, 255)
            pixels.append(c)
    write_png(bdir / "kart_grille.png", 16, 16, pixels)

    # 2d. `kart_glass.png`: Cutout automotive safety windshield glass (`alpha=0` clear window +
    # crisp weatherstrip seal + bright sky-cyan/white diagonal specular reflection streaks!)
    pixels = []
    for y in range(16):
        for x in range(16):
            gasket = x == 0 or x == 15 or y == 0 or y == 15
            inner_rim = x == 1 or x == 14 or y == 1 or y == 14
            streak1 = (x + y) in (6, 7) and 2 <= x <= 9 and 2 <= y <= 9
            streak2 = (x + y) == 11 and 3 <= x <= 10 and 3 <= y <= 10
            streak3 = (x + y) in (19, 20) and 6 <= x <= 13 and 6 <= y <= 13
            if gasket:
                c = (28, 32, 38, 255)
            elif inner_rim:
                c = (148, 206, 232, 255)
            elif streak1 or streak3:
                c = (236, 250, 255, 255)
            elif streak2:
                c = (172, 224, 246, 255)
            else:
                c = (0, 0, 0, 0)
            pixels.append(c)
    write_png(bdir / "kart_glass.png", 16, 16, pixels)

    # 2e. `kart_headlight.png`: Xenon/LED projector headlight lens with warm-white core & ice-blue halo
    pixels = []
    for y in range(16):
        for x in range(16):
            bezel = x in (0, 15) or y in (0, 15)
            dx = x - 7.5
            dy = y - 7.5
            dist = math.hypot(dx, dy)
            if bezel:
                c = (36, 40, 48, 255)
            elif dist < 3.2:
                c = (255, 252, 232, 255)
            elif dist < 5.1:
                c = (214, 242, 255, 255)
            elif dist < 6.6:
                c = (138, 184, 218, 255)
            else:
                c = (68, 76, 88, 255)
            pixels.append(c)
    write_png(bdir / "kart_headlight.png", 16, 16, pixels)

    # 2f. `kart_taillight.png`: Ruby-red LED brake/taillight lens with bright crimson light-bar
    pixels = []
    for y in range(16):
        for x in range(16):
            bezel = x in (0, 15) or y in (0, 15)
            led_bar = y in (6, 7, 8, 9) and 2 <= x <= 13
            inner = 2 <= x <= 13 and 3 <= y <= 12
            if bezel:
                c = (32, 24, 28, 255)
            elif led_bar:
                c = (255, 74, 68, 255)
            elif inner:
                v = 198 if (x + y) % 2 == 0 else 172
                c = (v, 22, 28, 255)
            else:
                c = (112, 14, 20, 255)
            pixels.append(c)
    write_png(bdir / "kart_taillight.png", 16, 16, pixels)

    # 2g. `kart_amber.png`: Crisp amber turn-signal / off-road marker lens
    pixels = []
    for y in range(16):
        for x in range(16):
            bezel = x in (0, 15) or y in (0, 15)
            core = 3 <= x <= 12 and 4 <= y <= 11
            if bezel:
                c = (38, 32, 24, 255)
            elif core:
                hi = (x + y) % 2 == 0
                c = (255, 196, 42, 255) if hi else (238, 156, 22, 255)
            else:
                c = (168, 96, 14, 255)
            pixels.append(c)
    write_png(bdir / "kart_amber.png", 16, 16, pixels)

    # 2h. `kart_dash.png`: Illuminated digital instrument cluster (RPM LED sweep + cyan speed readout)
    pixels = []
    for y in range(16):
        for x in range(16):
            bezel = x in (0, 1, 14, 15) or y in (0, 1, 14, 15)
            rpm_bar = y in (3, 4) and 2 <= x <= 13
            speed_digits = 7 <= y <= 11 and x in (4, 5, 7, 8, 10, 11)
            fuel_pips = y == 12 and 3 <= x <= 9
            if bezel:
                c = (28, 31, 38, 255)
            elif rpm_bar:
                if x <= 6:
                    c = (64, 238, 96, 255)
                elif x <= 10:
                    c = (252, 212, 52, 255)
                else:
                    c = (250, 62, 58, 255)
            elif speed_digits:
                c = (86, 228, 255, 255)
            elif fuel_pips:
                c = (248, 168, 44, 255)
            else:
                c = (16, 20, 26, 255)
            pixels.append(c)
    write_png(bdir / "kart_dash.png", 16, 16, pixels)

    # 2i. `kart_spring.png`: Helical coil-over suspension shock (crimson spring coils over chrome shaft)
    pixels = []
    for y in range(16):
        for x in range(16):
            cap = y in (0, 1, 14, 15)
            coil = (y + (x // 5)) % 3 == 0 and 2 <= x <= 13
            shaft = 5 <= x <= 10
            if cap:
                c = (186, 194, 206, 255)
            elif coil:
                c = (224, 48, 46, 255) if x < 11 else (168, 32, 32, 255)
            elif shaft:
                c = (212, 220, 230, 255) if x in (6, 7) else (126, 134, 146, 255)
            else:
                c = (32, 35, 42, 255)
            pixels.append(c)
    write_png(bdir / "kart_spring.png", 16, 16, pixels)

    # 2j. `police_side.png`: Poliția Română door livery (white top, blue/neon-lime Battenberg strip, navy band)
    pixels = []
    for y in range(16):
        for x in range(16):
            seam = x in (0, 15)
            if seam:
                c = (186, 194, 206, 255)
            elif y <= 3:
                c = (246, 249, 252, 255)
            elif y in (4, 5, 6, 7):
                # Iconic Romanian Police neon-yellow/lime & royal-blue Battenberg reflective checker!
                chk = ((x // 3) + (y // 2)) % 2 == 0
                c = (218, 248, 42, 255) if chk else (24, 78, 196, 255)
            elif y == 8:
                c = (248, 250, 252, 255)
            elif 9 <= y <= 13:
                c = (20, 58, 156, 255) if y < 12 else (15, 44, 124, 255)
            else:
                c = (32, 36, 44, 255)
            pixels.append(c)
    write_png(bdir / "police_side.png", 16, 16, pixels)

    # 2k. `police_hood.png`: Poliția Română cobalt-blue hood/trunk shield with neon-yellow chevrons
    pixels = []
    for y in range(16):
        for x in range(16):
            dx = abs(x - 7.5)
            chev = int(dx + y) % 4 in (0, 1) and y in (2, 3, 4, 11, 12)
            if dx > 5.8:
                c = (244, 247, 252, 255)
            elif chev:
                c = (226, 248, 46, 255)
            elif dx > 4.6:
                c = (250, 252, 255, 255)
            else:
                c = (22, 68, 178, 255) if y % 2 == 0 else (18, 56, 152, 255)
            pixels.append(c)
    write_png(bdir / "police_hood.png", 16, 16, pixels)

    # 2l. `plate_ro.png`: Authentic EU / Romanian license plate (`RO` blue strip + crisp black digits)
    pixels = []
    for y in range(16):
        for x in range(16):
            border = x == 0 or x == 15 or y in (0, 1, 14, 15)
            eu_strip = 1 <= x <= 3 and 2 <= y <= 13
            eu_star = x == 2 and y in (4, 5)
            ro_letters = y in (5, 6, 7, 8, 9, 10) and x in (5, 6, 8, 10, 12, 13) and not (y in (7, 8) and x == 10)
            if border:
                c = (26, 29, 36, 255)
            elif eu_star:
                c = (250, 214, 42, 255)
            elif eu_strip:
                c = (18, 68, 184, 255)
            elif ro_letters:
                c = (22, 24, 30, 255)
            else:
                c = (246, 248, 252, 255)
            pixels.append(c)
    write_png(bdir / "plate_ro.png", 16, 16, pixels)

    # 2m. `siren_red.png` & `siren_blue.png`: Intense glowing emergency LED girofar domes!
    for fname, core_col, mid_col, rim_col in [
        ("siren_red.png",  (255, 228, 224), (255, 42, 42),  (178, 14, 22)),
        ("siren_blue.png", (224, 246, 255), (36, 136, 255), (14, 62, 176)),
    ]:
        pixels = []
        for y in range(16):
            for x in range(16):
                dx = abs(x - 7.5)
                dy = abs(y - 7.5)
                if x in (0, 15) or y in (0, 15):
                    c = (*rim_col, 255)
                elif dy <= 2.5 and dx <= 4.5:
                    c = (*core_col, 255)
                elif dy <= 5.0 and dx <= 6.0:
                    c = (*mid_col, 255)
                else:
                    c = (*rim_col, 255)
                pixels.append(c)
        write_png(bdir / fname, 16, 16, pixels)

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

    # 1c. Quad Bike / ATV item icon (`quad_bike.png`)
    quad_pal = {
        ".": T,
        "K": (24, 26, 32, 255),
        "G": (64, 68, 76, 255),
        "S": (196, 204, 214, 255),
        "O": (236, 124, 34, 255),
        "H": (252, 172, 78, 255),
        "D": (168, 76, 18, 255),
        "C": (44, 48, 56, 255),
        "Y": (250, 224, 92, 255),
    }
    quad_art = [
        "................",
        "..........KK....",
        ".........KSSK...",
        ".........K..Y...",
        "...GGGG.CCCCCC..",
        "..HHHHHHHHHHHGY.",
        ".HOOOOOOOOOOOOH.",
        ".DOOOGGGGGOOOOD.",
        "..GGGGGGGGGGGG..",
        "..KKKK....KKKK..",
        ".KGGGGK..KGGGGK.",
        ".KGSSGK..KGSSGK.",
        ".KGGGGK..KGGGGK.",
        "..KKKK....KKKK..",
        "................",
        "................",
    ]
    grid_to_png(idir / "quad_bike.png", quad_art, quad_pal)

    # 1d. Romanian Police Car (`Poliția Română`) item icon (`police_car.png`)
    pol_pal = {
        ".": T,
        "K": (24, 26, 32, 255),
        "G": (64, 68, 76, 255),
        "S": (196, 204, 214, 255),
        "W": (246, 249, 252, 255),
        "B": (24, 72, 188, 255),
        "L": (218, 248, 42, 255),
        "R": (252, 46, 46, 255),
        "C": (42, 148, 255, 255),
        "A": (152, 214, 246, 255),
        "Y": (255, 236, 128, 255),
    }
    pol_art = [
        "................",
        "......CCRR......",
        "....WWWWWWWW....",
        "...WWAAWWAAWW...",
        "..WWWWWWWWWWWW..",
        ".RWWWWWWWWWWWWY.",
        ".WLBLBLBLBLBLBY.",
        ".BBBBBBBBBBBBBB.",
        ".GGGGGGGGGGGGGG.",
        "..KKKK....KKKK..",
        ".KGGGGK..KGGGGK.",
        ".KGSSGK..KGSSGK.",
        ".KGGGGK..KGGGGK.",
        "..KKKK....KKKK..",
        "................",
        "................",
    ]
    grid_to_png(idir / "police_car.png", pol_art, pol_pal)

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
    # 1. `go_kart_body.json` — Realistic Mechanical Racing Go-Kart (v0.7.0)
    # =========================================================================
    body_elements = [
        # --- A. Carbon-Fiber Floorpan & Tubular Chromoly Spaceframe ---
        vbox(-6.2, 0.95, -6.38, 6.2, 1.84, 13.0, "#carbon"),
        vbox( 5.2, 1.00, -17.55, 6.4, 2.40, 17.8, "#frame"),
        vbox(-6.4, 1.00, -17.55,-5.2, 2.40, 17.8, "#frame"),
        # Tall protective footwell side tubs (keeps Steve's thighs & boots 100% inside the chassis!)
        vbox( 5.3, 2.42,  4.8,  6.38, 5.10, 12.18, "#body", tint=True),
        vbox(-6.38,2.42,  4.8, -5.3,  5.10, 12.18, "#body", tint=True),
        vbox(-5.6, 1.86, 12.2,  5.6,  5.40, 13.4, "#frame"),

        # --- B. Front Axle Beam, Kingpin Yokes, Steering Tie-Rods & Front Disc Brakes ---
        vbox(-7.8, 2.15, 10.6,  7.8, 3.25, 11.9, "#frame"),
        vbox( 6.8, 1.95, 10.2,  8.2, 3.75, 12.2, "#chrome"),
        vbox(-8.2, 1.95, 10.2, -6.8, 3.75, 12.2, "#chrome"),
        # Articulated chrome steering tie-rods from central pitman arm out to left/right spindles!
        vbox( 0.4, 2.55,  9.2,  7.2, 3.00,  9.8, "#chrome", vrot=("y", -8.0, (0.4, 2.75, 9.5))),
        vbox(-7.2, 2.55,  9.2, -0.4, 3.00,  9.8, "#chrome", vrot=("y",  8.0, (-0.4, 2.75, 9.5))),
        # Front ventilated brake discs + crimson racing brake calipers inside wheel hubs
        vbox( 8.2, 1.90,  9.8,  8.75, 4.90, 12.6, "#chrome"),
        vbox(-8.75, 1.90, 9.8, -8.2,  4.90, 12.6, "#chrome"),
        vbox( 8.05, 3.10, 9.4,  8.85, 4.55, 10.5, "#taillight"),
        vbox(-8.85, 3.10, 9.4, -8.05, 4.55, 10.5, "#taillight"),

        # --- C. Carbon Front Aero Splitter, Swept Wheel Fairings & Sculpted Nassau Nosecone ---
        vbox(-8.4, 0.95, 19.2,  8.4, 1.55, 23.2, "#carbon"),
        vbox(-8.2, 1.35, 21.0,  8.2, 2.55, 22.8, "#frame"),
        vbox( 6.8, 1.15, 17.0, 12.2, 2.50, 18.8, "#carbon", vrot=("y",  20.0, (7.4, 1.8, 17.9))),
        vbox(-12.2, 1.15, 17.0, -6.8, 2.50, 18.8, "#carbon", vrot=("y", -20.0, (-7.4, 1.8, 17.9))),
        vbox(-7.2, 1.45, 18.6,  7.2, 4.10, 22.4, "#body", tint=True, vrot=("x", 12.0, (0.0, 2.7, 20.5))),
        vbox( 5.8, 1.40, 16.6, 12.2, 3.85, 19.6, "#body", tint=True, vrot=("y",  18.0, (6.4, 2.6, 18.0))),
        vbox(-12.2, 1.40, 16.6, -5.8, 3.85, 19.6, "#body", tint=True, vrot=("y", -18.0, (-6.4, 2.6, 18.0))),
        vbox(-5.3, 2.40, 11.8,  5.3, 5.85, 19.4, "#body", tint=True, vrot=("x", 14.0, (0.0, 4.1, 15.6))),
        vbox(-5.5, 4.50,  4.4,  5.5, 8.35, 12.4, "#body", tint=True, vrot=("x", 22.0, (0.0, 6.4,  8.4))),
        # Front radiator / brake-cooling intake grille + under-cowl fuel tank filler cap
        vbox(-3.4, 3.00, 18.9,  3.4, 4.35, 22.55, "#grille", vrot=("x", 12.0, (0.0, 2.7, 20.5))),
        vbox(-1.1, 7.60,  8.4,  1.1, 8.55, 10.6, "#chrome", vrot=("x", 22.0, (0.0, 6.4, 8.4))),

        # --- D. Sculpted Sidepods with Honeycomb Radiator Intakes (`#grille`) & Chrome Nerf Bars ---
        vbox( 6.0, 1.05, -5.8, 12.2, 5.85,  5.6, "#body", tint=True),
        vbox(-12.2, 1.05, -5.8, -6.0, 5.85, 5.6, "#body", tint=True),
        vbox( 6.2, 1.20,  3.8, 11.8, 5.60,  6.0, "#body", tint=True, vrot=("y", -16.0, (9.0, 3.4, 4.9))),
        vbox(-11.8, 1.20, 3.8, -6.2, 5.60,  6.0, "#body", tint=True, vrot=("y",  16.0, (-9.0, 3.4, 4.9))),
        # Realistic honeycomb cooling duct intakes on the leading edge of both sidepods!
        vbox( 6.8, 1.75,  5.45, 11.2, 5.05, 6.10, "#grille", vrot=("y", -16.0, (9.0, 3.4, 4.9))),
        vbox(-11.2, 1.75, 5.45, -6.8, 5.05, 6.10, "#grille", vrot=("y",  16.0, (-9.0, 3.4, 4.9))),
        # Carbon lower aero skirts + tubular chrome side nerf bars
        vbox( 12.22, 1.00, -5.8, 12.58, 1.95, 5.2, "#carbon"),
        vbox(-12.58, 1.00, -5.8, -12.22, 1.95, 5.2, "#carbon"),
        vbox( 12.05, 2.35, -6.2, 12.60, 3.05, 5.4, "#chrome"),
        vbox(-12.60, 2.35, -6.2, -12.05, 3.05, 5.4, "#chrome"),
        vbox( 6.2, 1.70, -15.6,  6.9, 6.20, -6.0, "#frame"),
        vbox(-6.9, 1.70, -15.6, -6.2, 6.20, -6.0, "#frame"),

        # --- E. Molded Fiberglass/Carbon Racing Bucket Seat & Tubular Seat Struts ---
        vbox(-5.6, 1.85, -6.6,  5.6, 3.30,  2.4, "#seat"),
        vbox( 4.8, 2.90, -6.4,  6.3, 8.80,  1.8, "#seat"),
        vbox(-6.3, 2.90, -6.4, -4.8, 8.80,  1.8, "#seat"),
        vbox(-5.5, 3.15, -6.8,  5.5, 14.20, -5.35, "#seat", vrot=("x", -6.0, (0.0, 3.30, -6.0))),
        vbox(-3.6, 13.80, -7.1, 3.6, 15.80, -5.55, "#seat", vrot=("x", -5.0, (0.0, 14.0, -6.2))),
        vbox(-5.2, 3.60, -7.45, 5.2, 13.60, -6.65, "#carbon", vrot=("x", -6.0, (0.0, 3.30, -6.0))),

        # --- F. Coaxial +30.0 deg Steering Column, Digital Lap/RPM Dash (`#dash`) & Pedals ---
        vbox(-1.9, 1.85,  5.2,  1.9, 7.80,  7.6, "#frame"),
        vbox(-2.1, 7.60,  4.55, 2.1, 10.15, 6.15, "#carbon", vrot=("x", 26.0, (0.0, 8.8, 5.3))),
        vbox(-1.75, 7.90, 4.40, 1.75, 9.85, 4.65, "#dash", vrot=("x", 26.0, (0.0, 8.8, 5.3)), full_uv_faces=("north", "south")),
        vbox(-0.65, 9.90, 2.95, 0.65, 11.10, 7.2, "#chrome", vrot=("x", 30.0, (0.0, 10.50, 2.95))),
        vbox(-1.15, 9.45, 3.65, 1.15, 11.55, 5.05, "#frame", vrot=("x", 30.0, (0.0, 10.50, 2.95))),
        # Master brake cylinder + alloy throttle/brake pedals with heel stop
        vbox(-1.1, 1.90,  8.6,  1.1, 3.90, 10.6, "#chrome"),
        vbox( 1.8, 1.85,  7.6,  3.8, 5.60,  8.5, "#chrome", vrot=("x", -18.0, (2.8, 2.0, 8.0))),
        vbox(-3.8, 1.85,  7.6, -1.8, 5.60,  8.5, "#chrome", vrot=("x", -18.0, (-2.8, 2.0, 8.0))),
        vbox(-4.4, 1.86,  7.65, 4.4, 2.35,  8.35, "#frame"),

        # --- G. Rear Drivetrain (Live Axle, Ventilated Brake Rotor, Chain Sprocket & FIA Rain Light!) ---
        vbox(-5.18, 1.30, -17.6,  5.18, 2.45, -6.4, "#frame"),
        vbox( 5.8, 2.42, -17.4,  7.8, 5.20, -14.8, "#body", tint=True),
        vbox(-7.8, 2.42, -17.4, -5.8, 5.20, -14.8, "#body", tint=True),
        vbox( 5.0, 2.46, -12.6,  6.36, 5.20, -10.2, "#frame"),
        vbox(-6.36,2.46, -12.6, -5.0,  5.20, -10.2, "#frame"),
        vbox(-8.8, 2.30, -12.0,  8.8, 3.40, -10.8, "#chrome"),
        # Left rear ventilated brake disc + red caliper; Right rear drive sprocket + carbon chain guard!
        vbox( 6.55, 1.35, -13.3, 7.15, 5.25, -9.5, "#chrome"),
        vbox( 6.35, 3.55, -10.3, 7.35, 5.45, -8.8, "#taillight"),
        vbox(-5.95, 1.45, -13.2, -5.15, 5.25, -9.6, "#chrome"),
        vbox(-6.15, 3.40, -13.4, -4.95, 5.60, -8.8, "#carbon"),
        # Full-width FIA Kart Rear Bumper, Carbon End-Pods & Center Glowing Ruby Rain Light!
        vbox(-12.4, 1.45, -19.8, 12.4, 2.95, -18.2, "#frame"),
        vbox( 8.2,  1.35, -20.0, 12.5, 3.35, -17.8, "#carbon"),
        vbox(-12.5, 1.35, -20.0, -8.2, 3.35, -17.8, "#carbon"),
        vbox(-7.6,  2.00, -19.2,  7.6, 4.30, -17.6, "#body", tint=True),
        vbox(-1.5,  2.25, -20.05, 1.5, 3.85, -19.15, "#taillight", full_uv_faces=("north", "south")),
    ]
    (mdir / "go_kart_body.json").write_text(
        json.dumps(
            {
                "textures": {
                    "body": "gokart:block/kart_body",
                    "frame": "gokart:block/kart_frame",
                    "carbon": "gokart:block/kart_carbon",
                    "grille": "gokart:block/kart_grille",
                    "dash": "gokart:block/kart_dash",
                    "taillight": "gokart:block/kart_taillight",
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
    # 2b. `quad_handlebars.json` — Dedicated ATV Trail T-Handlebars + Handguards!
    # =========================================================================
    # Authored symmetrically around (8.0, 8.0, 8.0) so yawing around Y at `steer_pivot`
    # turns the bars, grips, brake levers, digital pod & paint-matched rally handguards!
    qh_elements = [
        # Billet aluminum riser clamp & central steering stem collar
        box([6.7, 6.8, 7.2], [9.3, 8.3, 8.8], "#chrome"),
        box([7.3, 5.9, 7.4], [8.7, 7.0, 8.6], "#frame"),
        # Central carbon crossbar pad + illuminated ATV digital trail gauge (`#dash`)!
        box([5.8, 8.9, 7.55], [10.2, 9.85, 8.45], "#carbon"),
        box([6.4, 9.45, 8.15], [9.6, 10.65, 9.25], "#frame", rot=("x", 28.0, [8.0, 9.8, 8.6])),
        box([6.7, 9.60, 8.02], [9.3, 10.50, 8.28], "#dash", rot=("x", 28.0, [8.0, 9.8, 8.6]), full_uv_faces=("north", "south")),
        # Swept chromoly steel riser tubes (left +X and right -X)
        box([8.8, 7.7, 7.65], [11.8, 8.45, 8.35], "#chrome", rot=("z",  28.0, [9.0, 8.0, 8.0])),
        box([4.2, 7.7, 7.65], [ 7.2, 8.45, 8.35], "#chrome", rot=("z", -28.0, [7.0, 8.0, 8.0])),
        # Horizontal handlebar ends + ribbed vulcanized rubber grips (`mx = 1.6..4.5` & `11.5..14.4`, `my = 9.2..10.1`)
        box([11.2, 9.25, 7.65], [14.5, 9.95, 8.35], "#chrome"),
        box([ 1.5, 9.25, 7.65], [ 4.8, 9.95, 8.35], "#chrome"),
        box([11.6, 9.12, 7.48], [14.4, 10.08, 8.52], "#tire"),
        box([ 1.6, 9.12, 7.48], [ 4.4, 10.08, 8.52], "#tire"),
        # Master brake fluid reservoirs, alloy front/rear brake levers & right-thumb throttle!
        box([11.0, 9.35, 8.25], [11.9, 10.25, 9.05], "#frame"),
        box([ 4.1, 9.35, 8.25], [ 5.0, 10.25, 9.05], "#frame"),
        box([11.6, 9.38, 8.75], [14.0,  9.78, 9.18], "#chrome", rot=("y", -8.0, [11.6, 9.6, 8.9])),
        box([ 2.0, 9.38, 8.75], [ 4.4,  9.78, 9.18], "#chrome", rot=("y",  8.0, [ 4.4, 9.6, 8.9])),
        box([ 4.2, 8.85, 6.95], [ 5.3,  9.35, 7.65], "#chrome"),
        # Wraparound paint-tinted ATV rally handguards protecting the rider's knuckles!
        box([11.4, 8.85, 9.25], [14.6, 10.35, 9.85], "#body", tint=0),
        box([14.1, 9.10, 7.85], [14.65, 10.10, 9.55], "#frame"),
        box([ 1.4, 8.85, 9.25], [ 4.6, 10.35, 9.85], "#body", tint=0),
        box([ 1.35, 9.10, 7.85], [1.9, 10.10, 9.55], "#frame"),
    ]
    (mdir / "quad_handlebars.json").write_text(
        json.dumps(
            {
                "textures": {
                    "body": "gokart:block/kart_body",
                    "tire": "gokart:block/kart_tire",
                    "carbon": "gokart:block/kart_carbon",
                    "dash": "gokart:block/kart_dash",
                    "chrome": "gokart:block/kart_chrome",
                    "frame": "gokart:block/kart_frame",
                },
                "elements": qh_elements,
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
            eps = 0.014 * idx
            r = None if ang == 0.0 else ("x", ang, [8.0, 8.0, 8.0])
            w_elements.append(
                box([5.60 + eps, 4.00, 7.20], [10.40 - eps, 12.00, 8.80], "#tire", rot=r)
            )
            w_elements.append(
                box([5.607 + eps, 7.20, 4.00], [10.393 - eps, 8.80, 12.00], "#tire", rot=r)
            )
        # Recessed dark tire sidewall ring (octagonal, R=2.95 tx, chord=1.22 tx -> true circle inside tire!)
        for idx_s, r_ang in enumerate((0.0, 45.0)):
            eps_s = 0.010 * idx_s
            rr = None if r_ang == 0.0 else ("x", r_ang, [8.0, 8.0, 8.0])
            w_elements.append(box([5.52 + eps_s, 5.05, 6.78], [10.48 - eps_s, 10.95, 9.22], "#tire", rot=rr))
            w_elements.append(box([5.526 + eps_s, 6.78, 5.05], [10.474 - eps_s, 9.22, 10.95], "#tire", rot=rr))
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
        # Center-lock chrome racing hub nut & inner spindle boss (strictly disjoint from 7.20..8.80 tire planes!)
        w_elements.append(box([5.22, 7.24, 7.24], [10.78, 8.76, 8.76], "#chrome"))
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
            box([4.1, 3.85, 6.4], [4.88, 6.9, 9.9], "#chrome"),
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
        # --- Heavy 4x4 Ladder Chassis, Alloy Skidplate, Live Axles & Coil-Over Shocks (`#spring`) ---
        obox([-6.6, 3.6, -21.8], [-4.8, 5.35, 21.8], "#frame"),
        obox([ 4.8, 3.6, -21.8], [ 6.6, 5.35, 21.8], "#frame"),
        obox([-4.75, 3.8,  20.0], [ 4.75, 5.35, 21.8], "#frame"),
        obox([-4.75, 3.8, -21.8], [ 4.75, 5.35, -20.0], "#frame"),
        obox([-6.2, 3.0,  18.2], [ 6.2, 4.7, 22.8], "#chrome", rot=("x", -18.0, [0.0, 3.9, 20.5])),
        # Front & rear live axle tubes + differential pumpkins + Panhard track bars
        obox([-10.4, 2.35,  13.95], [-2.35, 3.30,  15.05], "#chrome"),
        obox([  2.35, 2.35, 13.95], [10.4,  3.30,  15.05], "#chrome"),
        obox([ -2.3, 1.80,  13.30], [ 2.3,  4.10,  15.70], "#frame"),
        obox([-10.4, 2.35, -15.05], [-2.35, 3.30, -13.95], "#chrome"),
        obox([  2.35, 2.35,-15.05], [10.4,  3.30, -13.95], "#chrome"),
        obox([ -2.3, 1.80, -15.70], [ 2.3,  4.10, -13.30], "#frame"),
        # Four long-travel helical coil-over shock absorbers (`#spring`)!
        obox([ 7.15, 3.35,  13.85], [ 8.45, 9.9,  15.15], "#spring"),
        obox([-8.45, 3.35,  13.85], [-7.15, 9.9,  15.15], "#spring"),
        obox([ 7.15, 3.35, -15.15], [ 8.45, 9.9, -13.85], "#spring"),
        obox([-8.45, 3.35, -15.15], [-7.15, 9.9, -13.85], "#spring"),

        # --- Wide Dual-Seat Cabin Floorpan, Rock-Slider Side Steps, Firewall & Center Console ---
        obox([-10.55, 4.4, -8.8], [10.55, 5.4,  8.15], "#carbon"),
        obox([-13.0, 4.1, -8.4], [-11.0, 5.2, 8.2], "#frame"),
        obox([ 11.0, 4.1, -8.4], [ 13.0, 5.2, 8.2], "#frame"),
        obox([-10.55, 5.4,  8.2], [10.55, 9.75, 9.15], "#frame"),
        obox([-1.45, 5.45, -6.8], [1.45, 8.2,  6.15], "#carbon"),
        obox([-0.4, 8.25,  1.2], [0.4, 11.0, 2.0], "#chrome", rot=("x", -12.0, [0.0, 8.25, 1.6])),
        obox([-0.85, 10.85, 0.85], [0.85, 11.85, 2.35], "#seat", rot=("x", -12.0, [0.0, 8.25, 1.6])),
        obox([-1.25, 8.25, 2.6], [-0.75, 10.2, 3.1], "#chrome", rot=("x", -8.0, [-1.0, 8.25, 2.85])),

        # --- Sculpted 4x4 Hood, 7-Slot Grille, Unobstructed Headlights & Narrow Center Winch Bullbar! ---
        obox([-8.2,  5.6,  9.2], [ 8.2, 12.2, 21.8], "#body", tint=0),
        obox([-7.8, 12.25, 9.2], [ 7.8, 13.35, 21.4], "#body", tint=0),
        obox([-3.6, 13.4, 11.2], [ 3.6, 14.25, 19.0], "#carbon"),
        obox([-3.0, 13.45, 19.05], [3.0, 14.15, 19.65], "#grille"),
        # Honeycomb radiator backing + 6 painted vertical slats = authentic 7-slot off-road fascia!
        obox([-7.9,  6.95, 21.85], [ 7.9, 12.15, 22.35], "#grille"),
        obox([ -3.75, 7.0, 22.36], [-3.15, 11.9, 22.62], "#body", tint=0),
        obox([ -2.35, 7.0, 22.36], [-1.75, 11.9, 22.62], "#body", tint=0),
        obox([ -0.95, 7.0, 22.36], [-0.35, 11.9, 22.62], "#body", tint=0),
        obox([  0.35, 7.0, 22.36], [ 0.95, 11.9, 22.62], "#body", tint=0),
        obox([  1.75, 7.0, 22.36], [ 2.35, 11.9, 22.62], "#body", tint=0),
        obox([  3.15, 7.0, 22.36], [ 3.75, 11.9, 22.62], "#body", tint=0),
        # 100% Unobstructed Projector Xenon/LED Headlights (`vx = ±4.5..±7.4`) + Amber Signals!
        obox([ 4.5,  8.4, 22.36], [ 7.4, 11.2, 22.78], "#headlight", full_uv_faces=("south", "north")),
        obox([-7.4,  8.4, 22.36], [-4.5, 11.2, 22.78], "#headlight", full_uv_faces=("south", "north")),
        obox([ 8.4,  8.6, 21.65], [10.8, 10.2, 22.05], "#amber", full_uv_faces=("south", "north")),
        obox([-10.8, 8.6, 21.65], [-8.4, 10.2, 22.05], "#amber", full_uv_faces=("south", "north")),
        # Heavy steel front bumper + Romanian front plate + NARROW center winch hoop (`vx = ±3.0..±3.85`, NEVER over headlights!)
        obox([-11.8, 4.8, 22.0], [11.8,  6.9, 23.6], "#frame"),
        obox([ -2.6, 5.2, 23.62], [ 2.6,  7.3, 23.85], "#carbon"),
        obox([ -1.8, 5.55, 23.86], [ 1.8, 6.95, 24.00], "#chrome"),
        obox([  6.4, 5.0, 23.62], [ 7.4,  6.5, 24.00], "#taillight"),
        obox([ -7.4, 5.0, 23.62], [-6.4,  6.5, 24.00], "#taillight"),
        obox([ -3.85, 6.95, 22.85], [-3.00, 11.8, 23.55], "#frame"),
        obox([  3.00, 6.95, 22.85], [ 3.85, 11.8, 23.55], "#frame"),
        obox([ -3.85, 11.82, 22.85], [3.85, 12.6, 23.55], "#frame"),

        # --- Disjoint Sculpted Front Fenders, Half-Doors & Redesigned Rear Bodywork (Zero Z-Fighting!) ---
        obox([ 8.25, 10.8,  9.4], [13.0, 12.6, 20.0], "#body", tint=0),
        obox([-13.0, 10.8,  9.4], [-8.25, 12.6, 20.0], "#body", tint=0),
        obox([ 8.25,  5.6,  8.45], [12.6, 10.75, 9.38], "#body", tint=0),
        obox([-12.6,  5.6,  8.45], [-8.25, 10.75, 9.38], "#body", tint=0),
        obox([ 8.25,  6.4, 20.02], [12.2, 11.4, 21.6], "#body", tint=0),
        obox([-12.2,  6.4, 20.02], [-8.25, 11.4, 21.6], "#body", tint=0),
        # Half-doors with exterior chrome handles & carbon rub-strips
        obox([ 10.6, 5.45, -8.8], [12.0, 11.8,  8.4], "#body", tint=0),
        obox([-12.0, 5.45, -8.8], [-10.6, 11.8, 8.4], "#body", tint=0),
        obox([ 12.02, 9.8, -5.8], [12.42, 10.6, -2.8], "#chrome"),
        obox([-12.42, 9.8, -5.8], [-12.02, 10.6, -2.8], "#chrome"),
        obox([ 12.02, 6.4, -8.2], [12.28,  7.4,  7.8], "#carbon"),
        obox([-12.28, 6.4, -8.2], [-12.02, 7.4,  7.8], "#carbon"),

        # --- REDESIGNED Clean 4x4 Rear Quarter Panels, Tailgate, 3-Tier LED Lamps & Spare Carrier! ---
        obox([ 10.6,  5.6, -21.0], [12.0, 12.8, -8.85], "#body", tint=0),
        obox([-12.0,  5.6, -21.0], [-10.6, 12.8, -8.85], "#body", tint=0),
        obox([ 12.02, 10.6, -20.0], [13.0, 12.6, -9.0], "#body", tint=0),
        obox([-13.0,  10.6, -20.0], [-12.02, 12.6, -9.0], "#body", tint=0),
        obox([ 12.02, 5.6, -21.0], [12.75, 10.55, -19.8], "#body", tint=0),
        obox([-12.75, 5.6, -21.0], [-12.02, 10.55, -19.8], "#body", tint=0),
        obox([-10.55, 5.4, -21.0], [10.55,  6.75, -8.85], "#carbon"),
        # Sculpted Swing-Out Tailgate (`vx = -8.15..+8.15`) + Corner D-Pillar Lamp Pods (`±8.20..±10.55`)!
        obox([-8.15,  5.8, -22.1], [ 8.15, 12.6, -21.05], "#body", tint=0),
        obox([-3.8,   8.1, -22.25], [ 3.8, 12.1, -22.12], "#carbon"),
        # Heavy chrome right-side tailgate hinges + left latch handle + Romanian License Plate (`#plate_ro`)!
        obox([-8.0,  10.6, -22.35], [-6.2, 11.6, -22.12], "#chrome"),
        obox([-8.0,   7.0, -22.35], [-6.2,  8.0, -22.12], "#chrome"),
        obox([ 5.6,  10.4, -22.38], [ 7.7, 11.2, -22.12], "#chrome"),
        obox([ 3.9,   6.2, -22.34], [ 7.9,  8.0, -22.12], "#plate_ro", full_uv_faces=("north", "south")),
        # Heavy-Duty Steel A-Frame Spare-Tire Carrier bolted straight to center of tailgate!
        obox([-2.4,   8.8, -23.15], [ 2.4, 11.8, -22.26], "#frame"),
        obox([-1.1,   9.6, -23.85], [ 1.1, 11.2, -23.16], "#chrome"),
        # Corner Vertical 3-Chamber LED Tail-Lamp Pillars (Top Ruby Brake, Mid Amber Turn, Bot White Reverse)!
        obox([ 8.20,  5.8, -22.1], [10.58, 12.8, -21.05], "#body", tint=0),
        obox([-10.58, 5.8, -22.1], [-8.20, 12.8, -21.05], "#body", tint=0),
        obox([ 8.45, 10.0, -22.32], [10.35, 12.3, -22.12], "#taillight", full_uv_faces=("north", "south")),
        obox([-10.35,10.0, -22.32], [-8.45, 12.3, -22.12], "#taillight", full_uv_faces=("north", "south")),
        obox([ 8.45,  8.2, -22.32], [10.35,  9.9, -22.12], "#amber", full_uv_faces=("north", "south")),
        obox([-10.35, 8.2, -22.32], [-8.45,  9.9, -22.12], "#amber", full_uv_faces=("north", "south")),
        obox([ 8.45,  6.5, -22.32], [10.35,  8.1, -22.12], "#headlight", full_uv_faces=("north", "south")),
        obox([-10.35, 6.5, -22.32], [-8.45,  8.1, -22.12], "#headlight", full_uv_faces=("north", "south")),
        # Stepped Off-Road Rear Steel Bumper, Corner End-Caps, Tow Hitch, Red Shackles & Dual Exhaust!
        obox([-10.6,  4.2, -23.3], [10.6,  5.75, -21.9], "#frame"),
        obox([ 10.62, 4.3, -23.0], [12.3,  5.75, -21.4], "#frame"),
        obox([-12.3,  4.3, -23.0], [-10.62, 5.75, -21.4], "#frame"),
        obox([ -1.3,  3.3, -23.6], [ 1.3,  4.18, -22.2], "#carbon"),
        obox([  5.8,  4.4, -23.65], [ 6.7, 5.55, -23.32], "#taillight"),
        obox([ -6.7,  4.4, -23.65], [-5.8, 5.55, -23.32], "#taillight"),
        obox([  7.4,  3.3, -23.5], [ 8.7,  4.18, -21.2], "#chrome"),
        obox([ -8.7,  3.3, -23.5], [-7.4,  4.18, -21.2], "#chrome"),

        # --- Dashboard (`#dash`), Steering Pod & CRYSTAL-CLEAR Open-View Windshield Frame! ---
        obox([-10.55, 9.8,  6.35], [10.55, 13.5, 8.4], "#seat"),
        obox([ 2.4, 13.52,  6.35], [ 7.2, 14.7, 8.3], "#carbon"),
        obox([ 2.8, 13.55,  6.02], [ 6.8, 14.55, 6.33], "#dash", full_uv_faces=("north", "south")),
        obox([-2.0, 10.6,  6.02], [ 2.0, 13.1, 6.33], "#grille"),
        obox([-8.4, 12.0,  5.75], [-3.8, 12.6, 6.33], "#chrome"),
        obox([ 4.2, 11.95, 3.13], [5.4, 13.15, 6.3], "#chrome", rot=("x", 32.0, [4.80, 12.54, 3.13])),
        obox([ 3.1, 5.45,  6.8], [ 4.3, 7.9,  7.6], "#chrome", rot=("x", -20.0, [3.7, 5.45, 7.2])),
        obox([ 5.3, 5.45,  6.8], [ 6.5, 7.9,  7.6], "#chrome", rot=("x", -20.0, [5.9, 5.45, 7.2])),
        # 100% Clear Open-View Windshield Frame (-18 deg slanted A-pillars + top visor + thin chrome seal, ZERO center obstruction!)
        obox([ 10.2, 13.5, 6.8], [11.6, 22.2, 8.0], "#body", tint=0, rot=("x", -18.0, [0.0, 13.5, 7.4])),
        obox([-11.6, 13.5, 6.8], [-10.2, 22.2, 8.0], "#body", tint=0, rot=("x", -18.0, [0.0, 13.5, 7.4])),
        obox([-11.6, 22.22, 6.8], [11.6, 23.5, 8.0], "#body", tint=0, rot=("x", -18.0, [0.0, 13.5, 7.4])),
        obox([-10.18, 21.75, 7.15], [10.18, 22.20, 7.65], "#carbon", rot=("x", -18.0, [0.0, 13.5, 7.4])),
        obox([-10.18, 13.52, 7.20], [10.18, 13.84, 7.60], "#chrome", rot=("x", -18.0, [0.0, 13.5, 7.4])),
        # Low-profile parked wipers at cowl base + high-mounted interior mirror + exterior wing mirrors!
        obox([ 1.2, 13.55, 8.05], [ 7.8, 13.95, 8.32], "#frame", rot=("z",  4.0, [1.2, 13.7, 8.18])),
        obox([-7.8, 13.55, 8.05], [-1.2, 13.95, 8.32], "#frame", rot=("z",  4.0, [-7.8, 13.7, 8.18])),
        obox([-1.8, 21.1, 4.35], [ 1.8, 21.9, 4.85], "#frame"),
        obox([-1.6, 21.2, 4.20], [ 1.6, 21.8, 4.34], "#chrome"),
        obox([ 11.62, 14.0, 6.4], [12.78, 14.7, 7.1], "#frame"),
        obox([ 12.80, 13.4, 6.0], [14.6, 16.2, 7.2], "#body", tint=0),
        obox([ 12.90, 13.6, 5.86], [14.4, 16.0, 5.99], "#chrome"),
        obox([-12.78, 14.0, 6.4], [-11.62, 14.7, 7.1], "#frame"),
        obox([-14.6,  13.4, 6.0], [-12.80, 16.2, 7.2], "#body", tint=0),
        obox([-14.4,  13.6, 5.86], [-12.90, 16.0, 5.99], "#chrome"),

        # --- Full-Height Overhead Safari Roll Cage (`vy_m = 23.4`) & 4 Halogen Roof Lamps ---
        obox([ 10.2, 12.85, -8.8], [11.4, 22.18, -7.6], "#frame"),
        obox([-11.4, 12.85, -8.8], [-10.2, 22.18, -7.6], "#frame"),
        obox([-11.4, 22.2, -8.8], [11.4, 23.4, -7.6], "#frame"),
        obox([ 10.2, 22.2, -7.58], [11.4, 23.3,  3.8], "#frame"),
        obox([-11.4, 22.2, -7.58], [-10.2, 23.3, 3.8], "#frame"),
        obox([ 10.2, 12.85, -20.6], [11.3, 22.15, -8.85], "#frame", rot=("x", 32.0, [10.7, 13.0, -20.0])),
        obox([-11.3, 12.85, -20.6], [-10.2, 22.15, -8.85], "#frame", rot=("x", 32.0, [-10.7, 13.0, -20.0])),
        obox([ 6.1, 23.42, 3.2], [ 8.7, 24.6, 4.85], "#frame"),
        obox([ 6.3, 23.50, 4.86], [8.5, 24.5, 5.18], "#headlight", full_uv_faces=("south", "north")),
        obox([ 1.7, 23.42, 3.2], [ 4.3, 24.6, 4.85], "#frame"),
        obox([ 1.9, 23.50, 4.86], [4.1, 24.5, 5.18], "#headlight", full_uv_faces=("south", "north")),
        obox([-4.3, 23.42, 3.2], [-1.7, 24.6, 4.85], "#frame"),
        obox([-4.1, 23.50, 4.86], [-1.9, 24.5, 5.18], "#headlight", full_uv_faces=("south", "north")),
        obox([-8.7, 23.42, 3.2], [-6.1, 24.6, 4.85], "#frame"),
        obox([-8.5, 23.50, 4.86], [-6.3, 24.5, 5.18], "#headlight", full_uv_faces=("south", "north")),

        # --- Full-Width Twin Front Bucket Seats (`vx_m = ±4.80`, 9.4 tx world wide each!) & Rear Bench ---
        obox([ 1.55, 5.45, -5.6], [ 8.1,  6.7,  0.8], "#seat"),
        obox([ 1.55, 6.72, -6.8], [ 8.1, 15.8, -5.2], "#seat", rot=("x", -8.0, [4.8, 6.72, -5.6])),
        obox([ 2.7, 15.85, -7.0], [6.9, 18.4, -5.4], "#body", tint=0),
        obox([-8.1, 5.45, -5.6], [-1.55,  6.7,  0.8], "#seat"),
        obox([-8.1, 6.72, -6.8], [-1.55, 15.8, -5.2], "#seat", rot=("x", -8.0, [-4.8, 6.72, -5.6])),
        obox([-6.9, 15.85, -7.0], [-2.7, 18.4, -5.4], "#body", tint=0),
        obox([-9.0, 6.8, -17.1], [9.0,  8.8, -12.0], "#seat"),
        obox([-9.0, 8.82, -19.0], [9.0, 15.6, -17.2], "#seat"),
    ]
    (mdir / "off_roader_body.json").write_text(
        json.dumps(
            {
                "textures": {
                    "body": "gokart:block/kart_body",
                    "frame": "gokart:block/kart_frame",
                    "carbon": "gokart:block/kart_carbon",
                    "grille": "gokart:block/kart_grille",
                    "headlight": "gokart:block/kart_headlight",
                    "taillight": "gokart:block/kart_taillight",
                    "amber": "gokart:block/kart_amber",
                    "dash": "gokart:block/kart_dash",
                    "spring": "gokart:block/kart_spring",
                    "plate_ro": "gokart:block/plate_ro",
                    "chrome": "gokart:block/kart_chrome",
                    "seat": "gokart:block/kart_seat",
                },
                "elements": off_elements,
            },
            indent=2,
        )
        + "\n"
    )

    # =========================================================================
    # 6. Trail Quad Bike / ATV Body (`quad_bike_body.json`) — Clean Headlights & Zero Overlap!
    # =========================================================================
    quad_elements = [
        # --- Tubular Cradle Frame, Front Skidplate, Double-Wishbone A-Arms & Coilover Shocks! ---
        obox([-4.2, 3.2, -16.8], [ 4.2, 4.8, 17.2], "#frame"),
        obox([-3.6, 2.75, 13.4], [ 3.6, 4.2, 18.6], "#chrome", rot=("x", -22.0, [0.0, 3.5, 16.0])),
        obox([ 4.22, 2.55, 10.8], [ 9.2, 3.25, 12.2], "#frame"),
        obox([-9.2,  2.55, 10.8], [-4.22, 3.25, 12.2], "#frame"),
        obox([ 4.22, 4.35, 10.9], [ 8.8, 5.00, 12.1], "#frame", rot=("z", -8.0, [4.22, 4.7, 11.5])),
        obox([-8.8,  4.35, 10.9], [-4.22, 5.00, 12.1], "#frame", rot=("z",  8.0, [-4.22, 4.7, 11.5])),
        obox([-8.6, 2.95,  9.95], [ 8.6, 3.45, 10.45], "#chrome"),
        obox([ 6.0, 3.3, 10.95], [ 7.2, 9.55, 12.05], "#spring", rot=("z",  22.0, [6.6, 3.3, 11.5])),
        obox([-7.2, 3.3, 10.95], [-6.0, 9.55, 12.05], "#spring", rot=("z", -22.0, [-6.6, 3.3, 11.5])),
        obox([-8.6, 2.35, -12.05], [8.6, 3.16, -10.95], "#chrome"),
        obox([ 2.4, 2.65, -12.6], [ 3.6, 3.22, -5.2], "#frame"),
        obox([-3.6, 2.65, -12.6], [-2.4, 3.22, -5.2], "#frame"),
        obox([-0.85, 3.25, -11.6], [0.85, 6.75, -10.3], "#spring", rot=("x", 22.0, [0.0, 3.4, -11.0])),

        # --- Exposed Single/V-Twin Trail Engine, Clutch Cover & Twin Carbon-Tipped Exhausts ---
        obox([-3.7, 4.82, -4.6], [ 3.7, 6.75,  3.15], "#frame"),
        obox([-3.2, 6.78, -2.4], [ 3.2, 9.2,   2.8], "#chrome", rot=("x", 10.0, [0.0, 6.8, 0.2])),
        obox([ 3.72, 4.85, -2.8], [ 4.25, 6.6, 1.8], "#carbon"),
        obox([-4.25, 4.85, -2.8], [-3.72, 6.6, 1.8], "#chrome"),
        obox([ 2.1, 5.1, -18.3], [ 3.8, 6.75, -12.0], "#carbon"),
        obox([-3.8, 5.1, -18.3], [-2.1, 6.75, -12.0], "#carbon"),
        obox([ 2.35, 5.35, -19.0], [ 3.55, 6.55, -18.32], "#chrome"),
        obox([-3.55, 5.35, -19.0], [-2.35, 6.55, -18.32], "#chrome"),

        # --- Anti-Slip Footwells, Heel Guards, Sculpted Cowling & Billet Fuel Cap ---
        obox([ 4.25, 3.6, -4.95], [10.18, 4.5,  4.75], "#carbon"),
        obox([-10.18, 3.6, -4.95], [-4.25, 4.5, 4.75], "#carbon"),
        obox([ 10.2, 3.6, -4.95], [11.2, 5.8, 4.75], "#frame"),
        obox([-11.2, 3.6, -4.95], [-10.2, 5.8, 4.75], "#frame"),
        obox([-4.8, 6.8,  3.2], [ 4.8, 12.2, 16.4], "#body", tint=0),
        obox([-3.6, 12.22, 3.6], [ 3.6, 12.85, 9.8], "#body", tint=0),
        obox([-1.0, 12.87, 3.6], [1.0, 13.40, 5.2], "#chrome"),
        # Front Honeycomb Radiator Grille + 100% Unobstructed Projector Headlights (`±1.85..±4.35`) & Narrow Center Hoop!
        obox([-4.4, 6.2, 16.42], [ 4.4, 11.4, 17.8], "#grille"),
        obox([ 1.85, 8.4, 17.82], [ 4.35, 10.8, 18.45], "#headlight", full_uv_faces=("south", "north")),
        obox([-4.35, 8.4, 17.82], [-1.85, 10.8, 18.45], "#headlight", full_uv_faces=("south", "north")),
        obox([ 4.85, 8.8, 16.82], [ 6.55, 10.1, 17.35], "#amber", full_uv_faces=("south", "north")),
        obox([-6.55, 8.8, 16.82], [-4.85, 10.1, 17.35], "#amber", full_uv_faces=("south", "north")),
        obox([-6.8, 4.2, 17.6], [ 6.8,  6.15, 19.3], "#frame"),
        obox([-1.8, 4.55, 19.32], [ 1.8, 6.15, 19.90], "#chrome"),
        obox([-1.55, 6.18, 18.45], [-1.00, 10.4, 19.15], "#frame"),
        obox([ 1.00, 6.18, 18.45], [ 1.55, 10.4, 19.15], "#frame"),
        obox([-1.55, 10.42, 18.45], [1.55, 11.0, 19.15], "#frame"),

        # --- Disjoint Flared Front & Rear Mudguards, Cargo Racks, Saddle & Ruby Taillights! ---
        obox([ 4.82, 9.6,  6.22], [11.5, 11.4, 16.8], "#body", tint=0),
        obox([-11.5, 9.6,  6.22], [-4.82, 11.4, 16.8], "#body", tint=0),
        obox([ 4.82, 5.2,  4.8], [11.2, 11.4,  6.2], "#body", tint=0),
        obox([-11.2, 5.2,  4.8], [-4.82, 11.4, 6.2], "#body", tint=0),
        obox([ 4.82, 9.6, -16.8], [11.5, 11.4, -6.42], "#body", tint=0),
        obox([-11.5, 9.6, -16.8], [-4.82, 11.4, -6.42], "#body", tint=0),
        obox([ 4.82, 5.2, -6.4], [11.2, 11.4, -5.0], "#body", tint=0),
        obox([-11.2, 5.2, -6.4], [-4.82, 11.4, -5.0], "#body", tint=0),
        obox([-4.8, 6.8, -16.8], [ 4.8, 11.2, -10.42], "#body", tint=0),
        obox([ 1.8, 8.2, -17.30], [ 4.5, 10.4, -16.82], "#taillight", full_uv_faces=("north", "south")),
        obox([-4.5, 8.2, -17.30], [-1.8, 10.4, -16.82], "#taillight", full_uv_faces=("north", "south")),
        obox([-8.6, 12.25, 10.4], [ 8.6, 12.95, 16.6], "#frame"),
        obox([-8.6, 12.97, 15.6], [ 8.6, 13.65, 16.6], "#frame"),
        obox([-8.6, 11.6, -16.8], [8.6, 12.45, -10.45], "#frame"),
        obox([-8.6, 12.47, -16.8], [8.6, 13.65, -15.8], "#frame"),
        obox([-3.8, 6.8, -10.4], [ 3.8,  7.85, 3.18], "#seat"),
        obox([-3.4, 7.87, -10.4], [ 3.4, 10.2, -7.8], "#seat"),
        obox([-1.4, 12.87, 5.5], [ 1.4, 13.7, 7.5], "#frame"),
        obox([-0.6, 13.85, 3.95], [0.6, 15.0, 6.8], "#chrome", rot=("x", 38.0, [0.0, 14.43, 3.95])),
    ]
    (mdir / "quad_bike_body.json").write_text(
        json.dumps(
            {
                "textures": {
                    "body": "gokart:block/kart_body",
                    "frame": "gokart:block/kart_frame",
                    "carbon": "gokart:block/kart_carbon",
                    "grille": "gokart:block/kart_grille",
                    "headlight": "gokart:block/kart_headlight",
                    "taillight": "gokart:block/kart_taillight",
                    "amber": "gokart:block/kart_amber",
                    "spring": "gokart:block/kart_spring",
                    "chrome": "gokart:block/kart_chrome",
                    "seat": "gokart:block/kart_seat",
                },
                "elements": quad_elements,
            },
            indent=2,
        )
        + "\n"
    )

    # =========================================================================
    # 7. Romanian Police Sedan (`police_car_body.json`) — Poliția Română FiveM!
    # =========================================================================
    # Authored with strictly non-overlapping intervals (zero z-fighting!), open-view
    # windshields for 1st-person patrol driving, Battenberg blue/lime door livery,
    # Romanian `RO` license plates, MDT police laptop, and Red/Blue roof Girofar!
    police_elements = [
        # --- A. Underbody Chassis Rails, Floorpan, Axles & Dual Exhaust ---
        obox([-10.2, 2.8, -8.6], [10.2, 3.9,  8.6], "#carbon"),
        obox([-6.4,  2.8,  8.62], [ 6.4, 3.9, 21.8], "#frame"),
        obox([-6.4,  2.8, -21.8], [ 6.4, 3.9, -8.62], "#frame"),
        obox([-9.8,  2.15,  13.25], [9.8, 3.05,  14.35], "#chrome"),
        obox([-9.8,  2.15, -14.35], [9.8, 3.05, -13.25], "#chrome"),
        obox([ 5.6,  2.3, -23.6], [ 7.2, 3.3, -21.4], "#chrome"),
        obox([-7.2,  2.3, -23.6], [-5.6, 3.3, -21.4], "#chrome"),

        # --- B. Sleek Front Bumper, Splitter, Romanian Plate, Sedan Grille & Xenon Headlights ---
        obox([-12.2, 2.9, 22.0], [12.2, 6.2, 23.5], "#body", tint=0),
        obox([-12.4, 2.4, 21.8], [12.4, 2.88, 23.8], "#carbon"),
        obox([ -3.8, 3.3, 23.52], [ 3.8, 5.1, 23.82], "#plate_ro", full_uv_faces=("south", "north")),
        obox([ -7.6, 3.3, 23.52], [-4.4, 4.9, 23.72], "#grille"),
        obox([  4.4, 3.3, 23.52], [ 7.6, 4.9, 23.72], "#grille"),
        # Wide honeycomb sedan grille + chrome emblem bar + swept LED headlights & amber corners!
        obox([ -5.8, 6.22, 22.1], [ 5.8,  9.8, 22.95], "#grille"),
        obox([ -5.8, 7.85, 22.97], [5.8,  8.35, 23.18], "#chrome"),
        obox([  5.85, 6.8, 22.05], [10.4, 9.5, 22.85], "#headlight", full_uv_faces=("south", "north")),
        obox([-10.4,  6.8, 22.05], [-5.85, 9.5, 22.85], "#headlight", full_uv_faces=("south", "north")),
        obox([ 10.42, 6.8, 21.6], [12.1,  9.3, 22.45], "#amber", full_uv_faces=("south", "north")),
        obox([-12.1,  6.8, 21.6], [-10.42, 9.3, 22.45], "#amber", full_uv_faces=("south", "north")),

        # --- C. Sculpted Poliția Română Hood (`#police_hood`) & Front Wheel Arches ---
        obox([ -8.2,  6.22,  8.8], [ 8.2, 10.35, 22.0], "#body", tint=0),
        obox([ -5.6, 10.37,  8.8], [ 5.6, 10.95, 21.8], "#police_hood", full_uv_faces=("up", "south")),
        obox([  5.62, 10.37, 8.8], [ 8.2, 10.85, 21.8], "#body", tint=0),
        obox([ -8.2, 10.37,  8.8], [-5.62, 10.85, 21.8], "#body", tint=0),
        obox([  8.22, 9.4,   8.8], [12.6, 10.85, 19.0], "#body", tint=0),
        obox([-12.6,  9.4,   8.8], [-8.22, 10.85, 19.0], "#body", tint=0),
        obox([  8.22, 3.9,  19.02], [12.2, 10.6, 21.98], "#body", tint=0),
        obox([-12.2,  3.9,  19.02], [-8.22, 10.6, 21.98], "#body", tint=0),

        # --- D. 4-Door Poliția Română Battenberg Livery (`#police_side`), Sills & Chrome Handles ---
        obox([ 10.22, 3.1, -8.75], [12.3,  3.95,  8.75], "#carbon"),
        obox([-12.3,  3.1, -8.75], [-10.22, 3.95, 8.75], "#carbon"),
        obox([ 10.22, 3.97, -8.75], [12.1, 10.9,  8.75], "#police_side", full_uv_faces=("east", "west")),
        obox([-12.1,  3.97, -8.75], [-10.22, 10.9, 8.75], "#police_side", full_uv_faces=("east", "west")),
        # Front & rear chrome door handles on both sides
        obox([ 12.12, 9.2,  0.8], [12.45, 9.85,  3.2], "#chrome"),
        obox([ 12.12, 9.2, -6.8], [12.45, 9.85, -4.4], "#chrome"),
        obox([-12.45, 9.2,  0.8], [-12.12, 9.85, 3.2], "#chrome"),
        obox([-12.45, 9.2, -6.8], [-12.12, 9.85, -4.4], "#chrome"),

        # --- E. Open-View Sedan Greenhouse (Clear Front/Rear/Side Windows!) & Wing Mirrors ---
        # Front slanted A-pillars (-24 deg) + thin lower chrome seal -> 100% CLEAR center windshield!
        obox([ 10.0, 10.9, 6.8], [11.4, 19.2, 8.0], "#body", tint=0, rot=("x", -24.0, [0.0, 10.9, 7.4])),
        obox([-11.4, 10.9, 6.8], [-10.0, 19.2, 8.0], "#body", tint=0, rot=("x", -24.0, [0.0, 10.9, 7.4])),
        obox([ -9.98, 10.92, 7.2], [9.98, 11.25, 7.6], "#chrome", rot=("x", -24.0, [0.0, 10.9, 7.4])),
        # Center B-pillars between front and rear side windows
        obox([ 10.4, 10.92, -1.6], [11.5, 18.6, -0.4], "#carbon"),
        obox([-11.5, 10.92, -1.6], [-10.4, 18.6, -0.4], "#carbon"),
        # Rear slanted C-pillars (+26 deg) -> 100% CLEAR rear window!
        obox([ 10.0, 10.9, -10.2], [11.4, 19.1, -9.0], "#body", tint=0, rot=("x", 26.0, [0.0, 10.9, -9.6])),
        obox([-11.4, 10.9, -10.2], [-10.0, 19.1, -9.0], "#body", tint=0, rot=("x", 26.0, [0.0, 10.9, -9.6])),
        # Sleek Sedan Roof Panel (`vy_m = 18.6..19.8`) + Interior Mirror + Exterior Wing Mirrors!
        obox([-11.2, 18.62, -6.6], [11.2, 19.8,  4.2], "#body", tint=0),
        obox([ -1.8, 17.8,  3.2], [ 1.8, 18.55, 3.8], "#frame"),
        obox([ 11.45, 11.4, 5.6], [12.55, 12.0, 6.3], "#frame"),
        obox([ 12.57, 11.0, 5.2], [14.2, 13.1, 6.4], "#body", tint=0),
        obox([ 12.68, 11.15, 5.06], [14.0, 12.95, 5.19], "#chrome"),
        obox([-12.55, 11.4, 5.6], [-11.45, 12.0, 6.3], "#frame"),
        obox([-14.2,  11.0, 5.2], [-12.57, 13.1, 6.4], "#body", tint=0),
        obox([-14.0,  11.15, 5.06], [-12.68, 12.95, 5.19], "#chrome"),

        # --- F. Roof Emergency Girofar Lightbar (Blue Left + Speaker Center + Red Right!) ---
        obox([ -8.4, 19.82, -2.5], [ 8.4, 20.35, -0.5], "#frame"),
        obox([ -1.4, 20.37, -2.6], [ 1.4, 21.65, -0.4], "#grille"),
        obox([  1.42, 20.37, -2.55], [ 8.2, 21.65, -0.45], "#siren_blue", full_uv_faces=("south", "north", "up")),
        obox([ -8.2,  20.37, -2.55], [-1.42, 21.65, -0.45], "#siren_red", full_uv_faces=("south", "north", "up")),

        # --- G. Police Cockpit: Digital Dash, MDT Police Laptop, Partition & Seats ---
        obox([-10.18, 7.6,  6.2], [10.18, 10.9, 8.55], "#seat"),
        obox([  2.4, 10.92, 6.2], [ 7.0, 12.1, 8.2], "#carbon"),
        obox([  2.8, 10.95, 5.90], [ 6.6, 11.95, 6.18], "#dash", full_uv_faces=("north", "south")),
        # Center Console + Angled Police MDT Laptop Screen (`#dash`)!
        obox([ -1.5,  3.92, -5.8], [ 1.5,  7.58, 6.18], "#carbon"),
        obox([ -1.8,  8.2,   4.0], [ 1.4, 10.8,  4.6], "#dash", rot=("y", 18.0, [0.0, 9.5, 4.3]), full_uv_faces=("north", "south")),
        obox([  4.15, 10.9,  3.46], [5.35, 12.0, 6.18], "#chrome", rot=("x", 28.0, [4.75, 11.45, 3.46])),
        # Front Patrol Bucket Seats + Protective Mesh Prisoner Partition + Rear Bench
        obox([  1.6,  3.92, -5.2], [ 8.0,  5.4,  1.0], "#seat"),
        obox([  1.6,  5.42, -6.4], [ 8.0, 13.8, -4.9], "#seat", rot=("x", -8.0, [4.8, 5.42, -5.2])),
        obox([ -8.0,  3.92, -5.2], [-1.6,  5.4,  1.0], "#seat"),
        obox([ -8.0,  5.42, -6.4], [-1.6, 13.8, -4.9], "#seat", rot=("x", -8.0, [-4.8, 5.42, -5.2])),
        obox([ -9.8, 10.8, -7.2], [ 9.8, 17.8, -6.65], "#grille"),
        obox([ -9.2,  4.2, -16.8], [ 9.2,  6.2, -11.2], "#seat"),
        obox([ -9.2,  6.22, -18.2], [9.2, 12.8, -16.6], "#seat"),

        # --- H. Sculpted Sedan Rear Quarters, Trunk Lid (`#police_hood`), RO Plate & LED Tail Lamps ---
        obox([  8.22, 9.4, -19.0], [12.6, 10.9, -8.8], "#body", tint=0),
        obox([-12.6,  9.4, -19.0], [-8.22, 10.9, -8.8], "#body", tint=0),
        obox([  8.22, 3.9, -22.2], [12.1, 10.9, -19.02], "#body", tint=0),
        obox([-12.1,  3.9, -22.2], [-8.22, 10.9, -19.02], "#body", tint=0),
        obox([ -8.2,  5.8, -22.2], [ 8.2, 10.8, -8.8], "#body", tint=0),
        obox([ -5.4, 10.82, -21.05], [5.4, 11.25, -10.4], "#police_hood", full_uv_faces=("up", "north")),
        obox([-10.8, 10.84, -22.3], [10.8, 11.55, -21.1], "#carbon"),
        # Wide Sedan LED Tail-Lamps, Amber Signals, Romanian Rear Plate & Rear Bumper!
        obox([  4.8,  7.8, -22.48], [11.6, 10.3, -22.22], "#taillight", full_uv_faces=("north", "south")),
        obox([-11.6,  7.8, -22.48], [-4.8, 10.3, -22.22], "#taillight", full_uv_faces=("north", "south")),
        obox([  6.8,  6.4, -22.48], [11.6,  7.75, -22.22], "#amber", full_uv_faces=("north", "south")),
        obox([-11.6,  6.4, -22.48], [-6.8,  7.75, -22.22], "#amber", full_uv_faces=("north", "south")),
        obox([ -3.8,  6.6, -22.48], [ 3.8,  8.5, -22.22], "#plate_ro", full_uv_faces=("north", "south")),
        obox([-12.2,  3.1, -23.4], [12.2,  5.78, -21.9], "#body", tint=0),
        obox([-11.8,  2.5, -23.5], [11.8,  3.08, -22.0], "#carbon"),
    ]
    (mdir / "police_car_body.json").write_text(
        json.dumps(
            {
                "textures": {
                    "body": "gokart:block/kart_body",
                    "frame": "gokart:block/kart_frame",
                    "carbon": "gokart:block/kart_carbon",
                    "grille": "gokart:block/kart_grille",
                    "headlight": "gokart:block/kart_headlight",
                    "taillight": "gokart:block/kart_taillight",
                    "amber": "gokart:block/kart_amber",
                    "dash": "gokart:block/kart_dash",
                    "police_side": "gokart:block/police_side",
                    "police_hood": "gokart:block/police_hood",
                    "plate_ro": "gokart:block/plate_ro",
                    "siren_red": "gokart:block/siren_red",
                    "siren_blue": "gokart:block/siren_blue",
                    "chrome": "gokart:block/kart_chrome",
                    "seat": "gokart:block/kart_seat",
                },
                "elements": police_elements,
            },
            indent=2,
        )
        + "\n"
    )

    # =========================================================================
    # 7b. Dynamic FiveM Girofar Strobe Pods (`siren_red.json`, `siren_blue.json`)
    # =========================================================================
    for sname, stex in [
        ("siren_red", "gokart:block/siren_red"),
        ("siren_blue", "gokart:block/siren_blue"),
    ]:
        (mdir / f"{sname}.json").write_text(
            json.dumps(
                {
                    "textures": {"siren": stex},
                    "elements": [
                        box(
                            [5.5, 6.8, 6.8],
                            [10.5, 9.2, 9.2],
                            "#siren",
                            full_uv_faces=("north", "south", "east", "west", "up", "down"),
                        )
                    ],
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
    "quad_bike",
    "police_car",
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
        # 12. Quad Bike / ATV (Iron Bars + Leather Saddle + Iron Engine + Sports Wheels)
        "quad_bike": {
            "type": "minecraft:crafting_shaped",
            "category": "transportation",
            "pattern": [
                "BLB",
                "IEI",
                "W W",
            ],
            "key": {
                "B": "minecraft:iron_bars",
                "L": "minecraft:leather",
                "I": "minecraft:iron_ingot",
                "E": "gokart:small_engine_iron",
                "W": "gokart:sports_wheel",
            },
            "result": {"id": "gokart:quad_bike", "count": 1},
        },
        # 13. Romanian Police Car (`Poliția Română` — Redstone + Lapis Girofar, Iron Sedan, Diamond/Gold Engine, Racing/Sports Wheels)
        "police_car": {
            "type": "minecraft:crafting_shaped",
            "category": "transportation",
            "pattern": [
                "RLB",
                "III",
                "WEW",
            ],
            "key": {
                "R": "minecraft:redstone",
                "L": "minecraft:leather",
                "B": "minecraft:lapis_lazuli",
                "I": "minecraft:iron_ingot",
                "W": "gokart:racing_wheel",
                "E": "gokart:small_engine_diamond",
            },
            "result": {"id": "gokart:police_car", "count": 1},
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
        "siren": {
            "subtitle": "subtitles.gokart.siren",
            "sounds": [{"name": "gokart:siren", "attenuation_distance": 56, "stream": False}],
        },
    }
    (ASSETS / "sounds.json").write_text(json.dumps(sounds_json, indent=2) + "\n")

    # Skip re-encoding if all OGG files already exist unless `--force-sounds` is passed
    ogg_names = ["engine_pulse", "horn", "drift", "boost", "wrench", "refuel", "siren"]
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

    # 7. `siren.ogg` — Authentic European / Romanian Police Electronic Wail-Yelp Siren cycle (1.32s)
    n = int(rate * 1.32)
    t = np.linspace(0, 1.32, n, endpoint=False)
    # Smooth rising-and-falling electronic police wail sweep (640 Hz -> 1280 Hz -> 640 Hz)
    sweep = 640.0 + 640.0 * (0.5 - 0.5 * np.cos(2 * np.pi * t / 1.30))
    phase = 2 * np.pi * np.cumsum(sweep) / rate
    siren_wave = (
        0.64 * np.sin(phase)
        + 0.24 * np.sin(2.0 * phase)
        + 0.12 * np.sin(3.0 * phase)
    )
    env = np.minimum(t / 0.03, 1.0) * np.minimum((1.32 - t) / 0.04, 1.0)
    save_ogg("siren", np.tanh(siren_wave * 1.35) * env)


# ---------------------------------------------------------------------------
# Bilingual Localization (`en_us.json` + `ro_ro.json`)
# ---------------------------------------------------------------------------

def generate_lang() -> None:
    ldir = ASSETS / "lang"
    ldir.mkdir(parents=True, exist_ok=True)

    en_us = {
        "gokart.mod.description": "FiveM-style 3D Go-Kart, Quad Bike ATV, 4x4 Off-Roader & Romanian Police Car (Poliția Română): nighttime headlights, siren & girofar, engines, wheels, 16-color paint & tuning garage.",
        "item.gokart.go_kart": "Go-Kart",
        "item.gokart.off_roader": "4x4 Off-Roader",
        "item.gokart.quad_bike": "Quad Bike (ATV)",
        "item.gokart.police_car": "Romanian Police Car (Poliția Română)",
        "gokart.vehicle.go_kart": "Go-Kart",
        "gokart.vehicle.off_roader": "4x4 Off-Roader",
        "gokart.vehicle.quad_bike": "Quad Bike (ATV)",
        "gokart.vehicle.police_car": "Romanian Police Car (Poliția)",
        "gokart.tooltip.place_off_roader": "Right-click ground to deploy 4x4 Off-Roader (climbs 1-block terrain!)",
        "gokart.tooltip.place_quad_bike": "Right-click ground to deploy Quad Bike ATV (nimble 1-block trail climber!)",
        "gokart.tooltip.place_police_car": "Right-click ground to deploy Poliția Română Patrol Car (press [H] for Siren & Girofar!)",
        "gokart.msg.placed_off_roader": "4x4 Off-Roader deployed! Right-click to drive, Wrench to tune.",
        "gokart.msg.placed_quad_bike": "Quad Bike ATV deployed! Right-click to ride, Wrench to tune.",
        "gokart.msg.placed_police_car": "Poliția Română Patrol Car deployed! Press [H] while driving to toggle Siren & Girofar.",
        "gokart.msg.siren_on": "POLIȚIA ROMÂNĂ — Emergency Siren & Girofar: ON",
        "gokart.msg.siren_off": "POLIȚIA ROMÂNĂ — Emergency Siren & Girofar: OFF",
        "gokart.ui.paint_shop": "Quick Paint Shop (click swatch):",
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
        "subtitles.gokart.refuel": "Vehicle refuels",
        "subtitles.gokart.siren": "Poliția Română siren wails",
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
        "gokart.msg.fuel_mode_on": "Vehicle fuel consumption: ENABLED",
        "gokart.msg.fuel_mode_off": "Vehicle fuel consumption: INFINITE FUEL",
        "gokart.msg.kit_given": "Delivered complete Go-Kart, Quad Bike ATV, 4x4 Off-Roader & Poliția Română Kit!",
        "gokart.msg.removed_one": "Removed %1$s!",
        "gokart.msg.removed_many": "Removed %1$s vehicle(s) from the world.",
        "gokart.msg.remove_none": "No vehicle nearby to remove (use /vehicle remove all to clear all).",
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
        "gokart.mod.description": "Vehicule 3D stil FiveM (Go-Kart, ATV Quad Bike, Off-Roader 4x4 & Mașină Poliția Română): faruri automate noaptea, girofar & sirenă, motoare, roți, vopsire în 16 culori și garaj tuning.",
        "item.gokart.go_kart": "Go-Kart",
        "item.gokart.off_roader": "Off-Roader 4x4",
        "item.gokart.quad_bike": "ATV Quad Bike",
        "item.gokart.police_car": "Autospecială Poliția Română",
        "gokart.vehicle.go_kart": "Go-Kart",
        "gokart.vehicle.off_roader": "Off-Roader 4x4",
        "gokart.vehicle.quad_bike": "ATV Quad Bike",
        "gokart.vehicle.police_car": "Autospecială Poliția Română",
        "gokart.tooltip.place_off_roader": "Click-dreapta pe sol pentru a plasa Off-Roader-ul 4x4 (urcă blocuri întregi!)",
        "gokart.tooltip.place_quad_bike": "Click-dreapta pe sol pentru a plasa ATV-ul Quad Bike (agil pe teren accidentat!)",
        "gokart.tooltip.place_police_car": "Click-dreapta pe sol pentru a plasa Autospeciala Poliției Române (apasă [H] pentru Sirenă & Girofar!)",
        "gokart.msg.placed_off_roader": "Off-Roader 4x4 plasat! Click-dreapta pentru a conduce, Cheie Mecanică pentru tuning.",
        "gokart.msg.placed_quad_bike": "ATV Quad Bike plasat! Click-dreapta pentru a conduce, Cheie Mecanică pentru tuning.",
        "gokart.msg.placed_police_car": "Autospecială Poliția Română plasată! Apasă [H] la volan pentru Sirenă & Girofar.",
        "gokart.msg.siren_on": "POLIȚIA ROMÂNĂ — Sirenă & Girofar: PORNITE",
        "gokart.msg.siren_off": "POLIȚIA ROMÂNĂ — Sirenă & Girofar: OPRITE",
        "gokart.ui.paint_shop": "Vopsitorie Rapidă (click pe culoare):",
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
        "subtitles.gokart.refuel": "Alimentare vehicul",
        "subtitles.gokart.siren": "Sirenă Poliția Română",
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
        "gokart.msg.fuel_mode_on": "Consum combustibil vehicule: ACTIVAT",
        "gokart.msg.fuel_mode_off": "Consum combustibil vehicule: COMBUSTIBIL INFINIT",
        "gokart.msg.kit_given": "Ai primit pachetul complet Go-Kart, ATV Quad Bike, Off-Roader 4x4 & Poliția Română!",
        "gokart.msg.removed_one": "Ai șters %1$s!",
        "gokart.msg.removed_many": "Au fost șterse %1$s vehicule din lume.",
        "gokart.msg.remove_none": "Niciun vehicul în apropiere de șters (folosește /vehicle remove all pentru toate).",
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


def generate_creative_tab() -> None:
    """Writes Horizon Creative Inventory category tab (`data/gokart/horizon/creative_tab/vehicles.json`)."""
    tdir = DATA / "horizon" / "creative_tab"
    tdir.mkdir(parents=True, exist_ok=True)
    tab = {
        "title": "Horizon Vehicles",
        "icon": "gokart:police_car",
        "items": [
            "gokart:go_kart",
            "gokart:quad_bike",
            "gokart:off_roader",
            "gokart:police_car",
            "gokart:small_engine_iron",
            "gokart:small_engine_gold",
            "gokart:small_engine_diamond",
            "gokart:standard_wheel",
            "gokart:sports_wheel",
            "gokart:racing_wheel",
            "gokart:wrench",
            "gokart:jerry_can",
        ],
    }
    (tdir / "vehicles.json").write_text(json.dumps(tab, indent=2) + "\n", encoding="utf-8")


def validate_models_no_zfighting() -> None:
    """Verifies [-16..32] element bounds AND zero coplanar overlapping faces across all 3D models."""
    mdir = ASSETS / "models" / "block"
    eps = 1e-3
    face_defs = [
        ("west",  0, 0, 1, 2),
        ("east",  0, 1, 1, 2),
        ("down",  1, 0, 0, 2),
        ("up",    1, 1, 0, 2),
        ("north", 2, 0, 0, 1),
        ("south", 2, 1, 0, 1),
    ]
    for mpath in sorted(mdir.glob("*.json")):
        data = json.loads(mpath.read_text(encoding="utf-8"))
        elems = data.get("elements", [])
        for idx, el in enumerate(elems):
            for k in ("from", "to"):
                for c in el[k]:
                    if c < -16.0 - 1e-5 or c > 32.0 + 1e-5:
                        raise ValueError(f"{mpath.name} element #{idx} {k}={el[k]} exceeds [-16, 32]!")
        # Check coplanar faces within identical rotation transform groups
        for i in range(len(elems)):
            for j in range(i + 1, len(elems)):
                ei, ej = elems[i], elems[j]
                if ei.get("rotation") != ej.get("rotation"):
                    continue
                for fname, axis, side, u_ax, v_ax in face_defs:
                    fi = ei["faces"].get(fname)
                    fj = ej["faces"].get(fname)
                    if not fi or not fj:
                        continue
                    pi = ei["to" if side else "from"][axis]
                    pj = ej["to" if side else "from"][axis]
                    if abs(pi - pj) < eps:
                        u0 = max(ei["from"][u_ax], ej["from"][u_ax])
                        u1 = min(ei["to"][u_ax], ej["to"][u_ax])
                        v0 = max(ei["from"][v_ax], ej["from"][v_ax])
                        v1 = min(ei["to"][v_ax], ej["to"][v_ax])
                        if (u1 - u0) > 0.02 and (v1 - v0) > 0.02:
                            raise ValueError(
                                f"Z-FIGHTING in {mpath.name}: elem #{i} ({fi['texture']}) & #{j} ({fj['texture']}) "
                                f"coplanar on {fname}={pi:.3f} overlap=({u1-u0:.2f}x{v1-v0:.2f})"
                            )


def main() -> None:
    generate_vehicle_textures()
    generate_item_textures()
    generate_models()
    validate_models_no_zfighting()
    generate_item_jsons()
    generate_recipes()
    generate_creative_tab()
    generate_sounds()
    generate_lang()
    generate_mod_icon()
    print("Generated & verified all Horizon Vehicles v0.8.0 assets, zero-zfight 3D models, Poliția Română, sounds & EN/RO locales.")


if __name__ == "__main__":
    main()
