"""Build the hand-designed cuboid harpy, its pixel atlas and Blockbench project.

Coordinates: Blockbench pixels, Y up, front = -Z. No animation is generated.
Requires Python 3.10+ and Pillow. All authored surfaces are six-faced cuboids.
"""
from __future__ import annotations

import base64
import hashlib
import io
import json
import math
from pathlib import Path
import random
import uuid

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dead_harpy"
OUT.mkdir(exist_ok=True)
NAMESPACE = uuid.UUID("afc18e3e-1e82-4a5a-aed2-5acdb9943eb0")
TEX = 256
TEXELS_PER_UNIT = 1.5
ELEMENTS: list[dict] = []
GROUPS: list[dict] = []
MATERIALS: dict[str, str] = {}
FACE_NAMES = ("north", "east", "south", "west", "up", "down")
PALETTES = {
    "skin": [(98, 88, 75), (124, 111, 94), (153, 141, 121), (173, 159, 138), (185, 171, 149)],
    "bone": [(112, 96, 80), (140, 123, 103), (165, 148, 124), (185, 167, 143), (200, 180, 155)],
    "hollow": [(45, 34, 32), (59, 43, 37), (76, 54, 43), (98, 73, 55), (123, 94, 70)],
    "hair": [(24, 20, 23), (32, 26, 28), (41, 32, 34), (51, 39, 39), (63, 47, 44)],
    "brown": [(35, 28, 29), (46, 35, 33), (59, 44, 39), (72, 52, 44), (89, 64, 51)],
    "umber": [(43, 32, 30), (58, 40, 34), (74, 50, 40), (91, 60, 46), (107, 74, 56)],
    "rust": [(59, 35, 33), (79, 42, 35), (102, 54, 42), (121, 66, 49), (140, 81, 59)],
    "ash": [(46, 43, 43), (60, 55, 53), (76, 69, 65), (91, 82, 74), (108, 97, 85)],
    "claw": [(22, 22, 24), (31, 30, 31), (43, 41, 41), (57, 53, 50), (75, 67, 59)],
    "beak": [(64, 31, 29), (91, 42, 33), (119, 59, 42), (146, 85, 59), (172, 118, 83)],
    "eye": [(15, 11, 12), (19, 13, 14), (25, 16, 17), (36, 21, 21), (57, 30, 26)],
    "eye_ember": [(39, 15, 15), (52, 21, 20), (71, 31, 26), (88, 40, 30), (100, 49, 35)],
}


def uid(name: str) -> str:
    return str(uuid.uuid5(NAMESPACE, name))


def vec(values):
    return [round(float(x), 5) for x in values]


def group(name, origin, parent=None):
    g = dict(name=name, origin=vec(origin), rotation=[0, 0, 0], color=0,
             uuid=uid("bone/" + name), export=True, isOpen=False,
             visibility=True, autouv=0, children=[])
    GROUPS.append(g)
    if parent is not None:
        parent["children"].append(g)
    return g


def cube(name, center, size, material, parent, rotation=(0, 0, 0), pivot=None):
    assert all(x > 0 for x in size), name
    e = dict(name=name, type="cube", uuid=uid("cube/" + name),
             from_=vec(c - s / 2 for c, s in zip(center, size)),
             to=vec(c + s / 2 for c, s in zip(center, size)),
             origin=vec(pivot or center), rotation=vec(rotation),
             autouv=0, box_uv=False, rescale=False, locked=False,
             visibility=True, export=True, shade=True, color=0, faces={})
    e["from"] = e.pop("from_")
    ELEMENTS.append(e)
    MATERIALS[e["uuid"]] = material
    parent["children"].append(e["uuid"])
    return e


def beam(name, a, b, width, depth, material, parent):
    """A cuboid aligned from endpoint a to b; its local long axis is +Y."""
    d = [b[i] - a[i] for i in range(3)]
    length = math.sqrt(sum(x * x for x in d))
    # Rz(z) Rx(x) (0,1,0) = (-sin(z)cos(x), cos(z)cos(x), sin(x)).
    rx = math.degrees(math.asin(d[2] / length))
    rz = math.degrees(math.atan2(-d[0], d[1]))
    return cube(name, [(a[i] + b[i]) / 2 for i in range(3)],
                [width, length, depth], material, parent, [rx, 0, rz])


from harpy_minecraft_style import build_geometry, paint_face as paint_minecraft_face

root = build_geometry(cube, beam, group, GROUPS)

def paint_face(w, h, mat, name, face):
    return paint_minecraft_face(w, h, mat, name, face, PALETTES)


# Unique per-face islands, integral UV boundaries and a one-texel dilated gutter.
rects = []
for e in ELEMENTS:
    w, h, d = [max(1, math.ceil((e["to"][k] - e["from"][k]) * TEXELS_PER_UNIT - 1e-4)) for k in range(3)]
    sizes = {"north": (w, h), "south": (w, h), "east": (d, h), "west": (d, h), "up": (w, d), "down": (w, d)}
    for face, (fw, fh) in sizes.items():
        rects.append((fw, fh, e, face))
rects.sort(key=lambda r: (-r[1], -r[0], r[2]["name"], r[3]))
atlas = Image.new("RGBA", (TEX, TEX), (0, 0, 0, 0))
layout = Image.new("RGBA", (TEX, TEX), (20, 23, 27, 255))
ld = ImageDraw.Draw(layout)
x = y = row_h = 0
uv_records = []
for w, h, e, face in rects:
    if x + w + 2 > TEX:
        x, y, row_h = 0, y + row_h, 0
    if y + h + 2 > TEX:
        raise RuntimeError("UV atlas overflow")
    u, v = x + 1, y + 1
    mat = MATERIALS[e["uuid"]]
    patch = paint_face(w, h, mat, e["name"], face)
    atlas.paste(patch, (u, v))
    atlas.paste(patch.crop((0,0,w,1)), (u, v-1))
    atlas.paste(patch.crop((0,h-1,w,h)), (u, v+h))
    atlas.paste(patch.crop((0,0,1,h)), (u-1, v))
    atlas.paste(patch.crop((w-1,0,w,h)), (u+w, v))
    for a,b,px,py in [(u-1,v-1,0,0),(u+w,v-1,w-1,0),(u-1,v+h,0,h-1),(u+w,v+h,w-1,h-1)]:
        atlas.putpixel((a,b), patch.getpixel((px,py)))
    e["faces"][face] = {"uv": [u, v, u+w, v+h], "texture": 0, "rotation": 0}
    ld.rectangle((u,v,u+w-1,v+h-1), fill=PALETTES[mat][2]+(255,))
    uv_records.append(dict(cube=e["name"], face=face, material=mat, uv=[u,v,u+w,v+h]))
    x += w + 2
    row_h = max(row_h, h + 2)
atlas.save(OUT / "dead_harpy.png", optimize=True)
(OUT / "previews").mkdir(exist_ok=True)
layout.resize((2048,2048), Image.Resampling.NEAREST).save(OUT / "previews/uv_layout.png")
buf = io.BytesIO()
atlas.save(buf, format="PNG")
texture = dict(path="", name="dead_harpy.png", folder="entity", namespace="fallofherovgadia",
               id="0", particle=False, render_mode="default", render_sides="auto", frame_time=1,
               frame_order_type="loop", frame_order="", frame_interpolate=False,
               visible=True, internal=True, saved=True, uuid=uid("texture"),
               source="data:image/png;base64,"+base64.b64encode(buf.getvalue()).decode(),
               width=TEX, height=TEX, uv_width=TEX, uv_height=TEX)
model = dict(meta=dict(format_version="4.10", model_format="bedrock", box_uv=False),
             name="Dead Harpy — Minecraft style — Fall of Herovgadia", model_identifier="dead_harpy",
             visible_box=[6, 4, 1.45], variable_placeholders="", variable_placeholder_buttons=[],
             unhandled_root_fields={}, resolution=dict(width=TEX, height=TEX),
             elements=ELEMENTS, outliner=[root], textures=[texture], animations=[],
             animation_controllers=[], display={}, overrides=[])
(OUT / "dead_harpy.bbmodel").write_text(json.dumps(model, ensure_ascii=False, indent=2)+"\n")

# Bedrock geometry is the geometry interchange used by GeckoLib on Java.
# Apply the same X reflection and Euler conversion as Blockbench's Bedrock codec.
by_id = {e["uuid"]: e for e in ELEMENTS}
bones = []
def export_group(g, parent=None):
    b = dict(name=g["name"], pivot=[-g["origin"][0], *g["origin"][1:]])
    if parent:
        b["parent"] = parent
    if any(g["rotation"]):
        b["rotation"] = [-g["rotation"][0], -g["rotation"][1], g["rotation"][2]]
    cubes = []
    for ch in g["children"]:
        if isinstance(ch, dict):
            continue
        e = by_id[ch]
        size = vec(e["to"][k] - e["from"][k] for k in range(3))
        c = dict(origin=[-e["to"][0], *e["from"][1:]], size=size, uv={})
        if any(e["rotation"]):
            c["pivot"] = [-e["origin"][0], *e["origin"][1:]]
            c["rotation"] = [-e["rotation"][0], -e["rotation"][1], e["rotation"][2]]
        for f, data in e["faces"].items():
            a, b0, a1, b1 = data["uv"]
            c["uv"][f] = dict(uv=[a1,b1] if f in ("up","down") else [a,b0],
                               uv_size=[a-a1,b0-b1] if f in ("up","down") else [a1-a,b1-b0])
        cubes.append(c)
    if cubes:
        b["cubes"] = cubes
    bones.append(b)
    for ch in g["children"]:
        if isinstance(ch, dict):
            export_group(ch, g["name"])
export_group(root)
geo = {"format_version":"1.12.0", "minecraft:geometry":[{
    "description": {"identifier":"geometry.dead_harpy", "texture_width":TEX, "texture_height":TEX,
                    "visible_bounds_width":6, "visible_bounds_height":4, "visible_bounds_offset":[0,1.45,0]},
    "bones":bones}]}
(OUT / "dead_harpy.geo.json").write_text(json.dumps(geo, indent=2)+"\n")
(OUT / "uv_manifest.json").write_text(json.dumps(uv_records, indent=2)+"\n")
(OUT / "material_manifest.json").write_text(json.dumps(MATERIALS, indent=2)+"\n")
stats = dict(cuboids=len(ELEMENTS), bones=len(GROUPS), faces=6*len(ELEMENTS),
             triangles=12*len(ELEMENTS), texture_size=[TEX,TEX], atlas_rows_used=y+row_h,
             animations=0)
(OUT / "build_stats.json").write_text(json.dumps(stats, indent=2)+"\n")
print(json.dumps(stats, indent=2))
