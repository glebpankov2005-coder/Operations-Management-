"""
Parametric Blender model of the Option B warehouse (run headless):
  blender --background --python warehouse_model/main.py
Builds floor + zones + double-deep rack rows (with shelf levels & pallets) +
forward-pick + offices + dock doors, lights it, and renders a 3/4 view to
outputs/figures/warehouse_blender.png.  Geometry mirrors the 2D floor plan.
"""
import bpy, math, os, random
from mathutils import Vector

random.seed(7)
OUT = os.path.join(os.path.dirname(__file__), "..", "outputs", "figures", "warehouse_blender.png")
OUT = os.path.abspath(OUT)

# ---------------- reset scene ----------------
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# ---------------- parameters (from the layout) ----------------
DEPTH = 70.0
left_w, right_w, aisle, core_w = 9.9, 9.5, 3.2, 67.6
L = left_w + aisle + core_w + aisle + right_w
cx0 = left_w + aisle
cx1 = cx0 + core_w
rax = cx1 + aisle
FWD_H = 7.4
BLOCK, AISLEW = 2.6, 3.0
pitch = BLOCK + AISLEW
n_mod = int((core_w - AISLEW) // pitch)
startx = cx0 + (core_w - (n_mod * pitch - AISLEW)) / 2
ry0, ry1 = FWD_H + 1.5, DEPTH - 1.5
ymid = (ry0 + ry1) / 2
runs = [(ry0, ymid - 1.6), (ymid + 1.6, ry1)]
sel_from = n_mod - 2
RES_H, SEL_H = 11.5, 10.5
LEVELS = 6

# ---------------- helpers ----------------
def mat(name, rgba, rough=0.6, metal=0.0, emit=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = rgba
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit and "Emission Strength" in b.inputs:
        b.inputs["Emission Color"].default_value = rgba
        b.inputs["Emission Strength"].default_value = emit
    return m

M_FLOOR = mat("floor", (0.86, 0.87, 0.90, 1), 0.9)
M_RES   = mat("reserve", (0.30, 0.42, 0.85, 1), 0.5, 0.2)
M_SEL   = mat("selective", (0.55, 0.66, 0.95, 1), 0.5, 0.2)
M_BEAM  = mat("beam", (0.16, 0.22, 0.45, 1), 0.4, 0.4)
M_PAL   = mat("pallet", (0.80, 0.62, 0.34, 1), 0.8)
M_FWD   = mat("forward", (0.35, 0.74, 0.52, 1), 0.6)
M_RECV  = mat("recv", (0.95, 0.78, 0.45, 1), 0.7)
M_OFF   = mat("off", (0.78, 0.80, 0.86, 1), 0.6)
M_RET   = mat("ret", (0.88, 0.72, 0.84, 1), 0.7)
M_PACK  = mat("pack", (0.94, 0.62, 0.62, 1), 0.7)
M_WALL  = mat("wall", (0.92, 0.93, 0.96, 1), 0.8)
M_DOCK  = mat("dock", (0.22, 0.26, 0.34, 1), 0.5)

def box(x, y, z0, sx, sy, sz, m, name="box"):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x + sx/2, y + sy/2, z0 + sz/2))
    o = bpy.context.active_object
    o.scale = (sx, sy, sz); o.name = name
    o.data.materials.append(m)
    return o

def plane(x, y, sx, sy, z, m, name="zone"):
    bpy.ops.mesh.primitive_plane_add(size=1, location=(x + sx/2, y + sy/2, z))
    o = bpy.context.active_object; o.scale = (sx, sy, 1); o.name = name
    o.data.materials.append(m); return o

# ---------------- floor + zone decals ----------------
box(0, 0, -0.2, L, DEPTH, 0.2, M_FLOOR, "floor")
plane(0.3, 0.3, left_w-0.6, (250/left_w)-0.6, 0.02, M_OFF, "z_off")             # offices (back-left)
# left column zones by area (offices top, returns mid, receiving bottom)
oh, rh, vh = 250/left_w, 180/left_w, 262/left_w
plane(0.3, DEPTH-oh, left_w-0.6, oh-0.6, 0.02, M_OFF, "z_off")
plane(0.3, DEPTH-oh-rh, left_w-0.6, rh-0.4, 0.02, M_RET, "z_ret")
plane(0.3, 0.3, left_w-0.6, vh-0.6, 0.02, M_RECV, "z_recv")
ph, uh = 450/right_w, 216/right_w
plane(rax+0.3, DEPTH-ph, right_w-0.6, ph-0.6, 0.02, M_PACK, "z_pack")
plane(rax+0.3, 0.3, right_w-0.6, uh-0.4, 0.02, M_RECV, "z_out")

# ---------------- forward-pick module (low carton-flow rows) ----------------
box(cx0, 0.5, 0, core_w, FWD_H-1.0, 3.4, M_FWD, "forward")

# ---------------- reserve / selective rack rows ----------------
for mnum in range(n_mod):
    bx = startx + mnum * pitch
    is_sel = mnum >= sel_from
    rmat = M_SEL if is_sel else M_RES
    H = SEL_H if is_sel else RES_H
    for (y0, y1) in runs:
        ln = y1 - y0
        # two upright panels (double-deep) - thin
        for dxp in (0.0, BLOCK-0.18):
            box(bx+dxp, y0, 0, 0.18, ln, H, M_BEAM, "upright")
        # shelf/beam levels spanning the block
        for k in range(LEVELS):
            zz = 0.4 + k * (H-0.6) / (LEVELS-1)
            box(bx, y0, zz, BLOCK, ln, 0.12, rmat, "beam")
        # a few pallets on random levels for realism
        for _ in range(5):
            lv = random.randint(0, LEVELS-2)
            zz = 0.4 + lv * (H-0.6)/(LEVELS-1) + 0.12
            py = y0 + random.uniform(0.4, max(0.5, ln-1.4))
            box(bx+0.25, py, zz, BLOCK-0.5, 1.1, 0.9, M_PAL, "pallet")

# staged pallets in receiving & outbound
for _ in range(14):
    box(random.uniform(1, left_w-2.2), random.uniform(1, 18), 0, 1.2, 1.0, 0.9, M_PAL, "spal")
for _ in range(10):
    box(random.uniform(rax+1, L-2.2), random.uniform(1, 16), 0, 1.2, 1.0, 0.9, M_PAL, "spal")

# ---------------- offices block (2-storey) + perimeter low walls + dock doors ----------------
box(0.5, DEPTH-oh+0.5, 0, left_w-1.0, oh-1.0, 6.0, M_OFF, "office_bldg")
WALL_H, WT = 2.2, 0.3
box(0, 0, 0, L, WT, WALL_H, M_WALL, "wall_front")
box(0, DEPTH-WT, 0, L, WT, 8.0, M_WALL, "wall_back")
box(0, 0, 0, WT, DEPTH, 8.0, M_WALL, "wall_left")
box(L-WT, 0, 0, WT, DEPTH, 8.0, M_WALL, "wall_right")
for i in range(3):
    box(2 + i*3.2, -0.35, 0, 2.4, 0.5, 3.2, M_DOCK, "recv_dock")
    box(rax + 1 + i*2.6, -0.35, 0, 2.2, 0.5, 3.2, M_DOCK, "ship_dock")

# ---------------- lighting ----------------
world = bpy.data.worlds.new("W"); scene.world = world; world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.95, 0.96, 0.98, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.8
sun_d = bpy.data.lights.new("Sun", 'SUN'); sun_d.energy = 3.2; sun_d.angle = 0.15
sun = bpy.data.objects.new("Sun", sun_d); scene.collection.objects.link(sun)
sun.rotation_euler = (math.radians(52), math.radians(18), math.radians(35))
area_d = bpy.data.lights.new("Fill", 'AREA'); area_d.energy = 12000; area_d.size = 60
fill = bpy.data.objects.new("Fill", area_d); scene.collection.objects.link(fill)
fill.location = (L*0.3, -40, 55)

# ---------------- camera (orthographic 3/4 view from front-left) ----------------
center = Vector((L/2, DEPTH/2, 5))
cam_d = bpy.data.cameras.new("Cam"); cam_d.type = 'ORTHO'; cam_d.ortho_scale = 118
cam = bpy.data.objects.new("Cam", cam_d); scene.collection.objects.link(cam)
cam.location = (L/2 - 78, -70, 82)
tgt = bpy.data.objects.new("T", None); scene.collection.objects.link(tgt); tgt.location = center
c = cam.constraints.new('TRACK_TO'); c.target = tgt; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
scene.camera = cam

# ---------------- render ----------------
try:
    scene.render.engine = 'BLENDER_EEVEE_NEXT'
except Exception:
    scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1700
scene.render.resolution_y = 1050
scene.render.film_transparent = False
scene.view_settings.view_transform = 'Standard'
scene.render.filepath = OUT
bpy.ops.render.render(write_still=True)
print("RENDERED:", OUT)
