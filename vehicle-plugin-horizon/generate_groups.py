#!/usr/bin/env python3
"""Regenerate constant group data from the audited transfer descriptor."""
import json
from pathlib import Path
root = Path(__file__).resolve().parent
base = root / 'paper-plugin/src/main'
data = json.loads((base / 'resources/horizon/off_roader_parts.json').read_text())['parts']
out = ['''package com.mrcrayfish.vehicle.paper.render;

import org.joml.Quaternionf;
import org.joml.Vector3f;
import java.util.List;

/** Generated from resources/horizon/off_roader_parts.json; do not edit manually. */
final class HorizonGroups {
    record Group(String name, float x, float y, float z, char axis, float degrees) {
        Vector3f origin() { return new Vector3f(x, y, z); }
        Quaternionf rotation() {
            float r = (float)Math.toRadians(degrees);
            return switch (axis) {
                case 'x' -> new Quaternionf().rotateX(r);
                case 'y' -> new Quaternionf().rotateY(r);
                case 'z' -> new Quaternionf().rotateZ(r);
                default -> new Quaternionf();
            };
        }
    }
''']
for name, groups in data.items():
    out.append(f'    static final List<Group> {name.upper()} = List.of(\n')
    rows=[]
    for g in groups:
        r=g['rotation'] or {'axis':'n','angle':0,'origin':[8,8,8]}
        x,y,z=r['origin']
        def f(v): return str(float(v))+'F'
        rows.append(f'        new Group("{g["item_model"].split(":")[1]}", {f(x)}, {f(y)}, {f(z)}, \'{r["axis"]}\', {f(r["angle"])})')
    out.append(',\n'.join(rows)+ '\n    );\n')
out.append('    private HorizonGroups() {}\n}\n')
(base / 'java/com/mrcrayfish/vehicle/paper/render/HorizonGroups.java').write_text(''.join(out))
