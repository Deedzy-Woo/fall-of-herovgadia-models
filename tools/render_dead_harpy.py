"""Render actual geometry read back from Blockbench. Run with Blender --background.

This is an inspection render, not an alternative smoothed model.
"""
import bpy
from mathutils import Vector, Matrix
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dead_harpy"
DATA = json.loads((OUT / "render_geometry.json").read_text())
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.samples = 32
scene.cycles.use_denoising = False
scene.render.threads_mode = "FIXED"
scene.render.threads = 5
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.film_transparent = False
scene.world.color = (.16, .16, .16)
scene.world.use_nodes = True
world = scene.world.node_tree.nodes.get("Background")
world.inputs[0].default_value = (.24, .29, .32, 1)
world.inputs[1].default_value = .32
scene.view_settings.view_transform = "Standard"
scene.view_settings.look = "Medium High Contrast"
scene.view_settings.exposure = 0
scene.view_settings.gamma = 1

mat = bpy.data.materials.new("dead_harpy • single pixel atlas")
mat.use_nodes = True
nodes = mat.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs["Roughness"].default_value = 1
image_node = nodes.new("ShaderNodeTexImage")
image_node.image = bpy.data.images.load(str(OUT / "dead_harpy.png"))
image_node.interpolation = "Closest"
mat.node_tree.links.new(image_node.outputs["Color"], bsdf.inputs["Base Color"])

objects=[]
for c in DATA:
    # Three.js stores matrices column-major; Blender uses row-major constructors.
    mw = Matrix([c["matrix"][i:i+4] for i in range(0,16,4)]).transposed()
    verts=[]
    for i in range(0,len(c["position"]),3):
        v=mw @ Vector(c["position"][i:i+3])
        # Y-up Blockbench -> Z-up Blender; -Z front -> +Y front.
        verts.append((v.x/16, -v.z/16, v.y/16))
    faces=[c["index"][i:i+3] for i in range(0,len(c["index"]),3)]
    mesh=bpy.data.meshes.new(c["name"])
    mesh.from_pydata(verts,[],faces)
    mesh.materials.append(mat)
    mesh.uv_layers.new(name="Blockbench per-face UV")
    for p in mesh.polygons:
        for li in p.loop_indices:
            vi=mesh.loops[li].vertex_index
            mesh.uv_layers[0].data[li].uv=c["uv"][2*vi:2*vi+2]
    obj=bpy.data.objects.new(c["name"],mesh)
    bpy.context.collection.objects.link(obj)
    objects.append(obj)

def light(name, location, power, color, size):
    data=bpy.data.lights.new(name,"AREA")
    data.energy=power
    data.shape="DISK"
    data.size=size
    data.color=color
    obj=bpy.data.objects.new(name,data)
    bpy.context.collection.objects.link(obj)
    obj.location=location
    obj.rotation_euler=(Vector((0,0,1.5))-obj.location).to_track_quat('-Z','Y').to_euler()

light("warm broad key", (2.3,4.8,7), 330, (1,.87,.75), 5)
light("cool soft fill", (-4,2.7,3.9), 180, (.69,.81,1), 5)
light("feather edge", (1,-4,5.4), 320, (.85,.89,1), 4)

# Matte charcoal studio floor; all model geometry above is untouched.
bpy.ops.mesh.primitive_plane_add(size=200, location=(0,0,-.16))
floor=bpy.context.object
floor.name="STUDIO • not exported"
fm=bpy.data.materials.new("Studio charcoal")
fm.use_nodes=True
fbs=fm.node_tree.nodes.get('Principled BSDF')
fbs.inputs['Base Color'].default_value=(.025,.037,.044,1)
fbs.inputs['Roughness'].default_value=1
floor.data.materials.append(fm)
camera_data=bpy.data.cameras.new("Inspection camera")
camera=bpy.data.objects.new("Inspection camera",camera_data)
bpy.context.collection.objects.link(camera)
scene.camera=camera
camera_data.type='ORTHO'
def render(name, pos, target, scale, width, height):
    camera.location=pos
    camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    camera_data.ortho_scale=scale
    scene.render.resolution_x=width
    scene.render.resolution_y=height
    scene.render.filepath=str(OUT/'previews'/name)
    bpy.ops.render.render(write_still=True)

render('hero.png',(4.1,8,4.3),(0,0,1.45),5.65,1800,1350)
render('front.png',(0,9,2.8),(0,0,1.42),5.65,1600,1200)
render('back.png',(0,-9,3.2),(0,0,1.45),5.65,1600,1200)
render('side.png',(9,1,3.5),(0,0,1.4),3.95,1200,1400)
render('face_detail.png',(3.7,6.6,3.55),(0,.25,1.96),1.45,1200,1200)
