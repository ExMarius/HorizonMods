#!/usr/bin/env python3
"""Inspect the first bus mesh before a vanilla resource-pack conversion.

Vanilla 1.21.4 does not load OBJ meshes. This tool intentionally emits no pack:
it reports geometry that needs a conversion strategy, rather than silently
rounding rotations or dropping polygons. Counts are not a visual quality test.
"""
import json
import math
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def analyze(path):
    vertices = []
    counts = Counter()
    objects = set()
    for line in path.read_text(encoding='utf-8').splitlines():
        tokens = line.split()
        if not tokens or tokens[0].startswith('#'):
            continue
        if tokens[0] == 'v':
            vertex = tuple(float(v) for v in tokens[1:4])
            if len(vertex) != 3 or not all(math.isfinite(v) for v in vertex):
                raise ValueError('Invalid OBJ vertex')
            vertices.append(vertex)
        elif tokens[0] == 'o':
            objects.add(' '.join(tokens[1:]))
        elif tokens[0] == 'f':
            indices = [int(v.split('/')[0]) for v in tokens[1:]]
            if any(i <= 0 or i > len(vertices) for i in indices):
                raise ValueError('Unsupported or invalid OBJ vertex index')
            points = [vertices[i - 1] for i in indices]
            counts['faces'] += 1
            if len(points) != 4:
                counts['non_quads'] += 1
                continue
            edges = [tuple(points[(i + 1) % 4][j] - points[i][j] for j in range(3))
                     for i in range(4)]
            lengths = [math.sqrt(sum(v * v for v in edge)) for edge in edges]
            if min(lengths) < 1e-8:
                counts['degenerate_quads'] += 1
                continue
            orthogonal = all(abs(sum(a * b for a, b in zip(edges[i], edges[(i + 1) % 4])))
                             <= 1e-6 * lengths[i] * lengths[(i + 1) % 4] for i in range(4))
            if orthogonal:
                counts['rectangular_quads'] += 1
            else:
                counts['other_quads'] += 1
    return {'vertices': len(vertices), 'objects': len(objects),
            **{k: counts[k] for k in ('faces', 'rectangular_quads', 'other_quads',
                                       'degenerate_quads', 'non_quads')}}


if __name__ == '__main__':
    for name in ('bus.obj', 'bus_wheel.obj'):
        print(name, json.dumps(analyze(ROOT / 'asset-src/city_bus' / name), sort_keys=True))
