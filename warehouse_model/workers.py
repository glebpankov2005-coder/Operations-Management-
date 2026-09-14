"""
Blender render of WORKER MOVEMENT (zone picking) over the Option B warehouse.
Same building as main.py, with glowing colored travel routes on the floor and a
higher camera so aisles/routes are visible.
Run: blender --background --python warehouse_model/workers.py
Output: outputs/figures/warehouse_workers.png
"""
import bpy, math, os, random
from mathutils import Vector
random.seed(7)
OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "outputs", "figures", "warehouse_workers.png"))

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

DEPTH = 70.0
left_w, right_w, aisle, core_w = 9.9, 9.5, 3.2, 67.6
L = left_w + aisle + core_w + aisle + right_w
cx0 = left_w + aisle; cx1 = cx0 + core_w; cmid = (cx0 + cx1) / 2; rax = cx1 + aisle
FWD_H = 7.4
BLOCK, AISLEW = 2.6, 3.0; pitch = BLOCK + AISLEW
n_mod = int((core_w - AISLEW) // pitch)
startx = cx0 + (core_w - (n_mod * pitch - AISLEW)) / 2
ry0, ry1 = FWD_H + 1.5, DEPTH - 1.5
ymid = (ry0 + ry1) / 2
runs = [(ry0, ymid - 1.6), (ymid + 1.6, ry1)]
sel_from = n_mod - 2
RES_H, SEL_H, LEVELS = 11.5, 10.5, 6

def mat(name, rgba, rough=0.6, metal=0.0, alpha=1.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rgba
    b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    if alpha < 1.0:
        b.inputs["Alpha"].default_value = alpha
        try: m.surface_render_method = 'BLENDED'
        except Exception:
            try: m.blend_method = 'BLEND'
            except Exception: pass
    return m
def emit(name, rgb):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Emission Color"].default_value = (*rgb, 1)
    b.inputs["Emission Strength"].default_value = 3.0
    return m

M_FLOOR = mat("floor", (0.90, 0.91, 0.94, 1), 0.9)
M_RES = mat("res", (0.42, 0.53, 0.85, 1), 0.6, alpha=0.38); M_SEL = mat("sel", (0.60, 0.70, 0.93, 1), 0.6, alpha=0.38)
M_BEAM = mat("beam", (0.30, 0.38, 0.62, 1), 0.5, alpha=0.5); M_FWD = mat("fwd", (0.40, 0.78, 0.58, 1), 0.6)
M_WALL = mat("wall", (0.93, 0.94, 0.97, 1), 0.85); M_DOCK = mat("dock", (0.30, 0.34, 0.42, 1), 0.5)
M_OFF = mat("off", (0.82, 0.84, 0.89, 1), 0.6)

def box(x, y, z0, sx, sy, sz, m, name="b"):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x+sx/2, y+sy/2, z0+sz/2))
    o = bpy.context.active_object; o.scale = (sx, sy, sz); o.name = name
    o.data.materials.append(m); return o

# floor + building
box(0, 0, -0.2, L, DEPTH, 0.2, M_FLOOR, "floor")
box(0.5, DEPTH-250/left_w+0.5, 0, left_w-1, 250/left_w-1, 5.5, M_OFF, "office")
for wx, wy, wsx, wsy, wsz in [(0,0,L,0.3,2.0),(0,DEPTH-0.3,L,0.3,7),(0,0,0.3,DEPTH,7),(L-0.3,0,0.3,DEPTH,7)]:
    box(wx, wy, 0, wsx, wsy, wsz, M_WALL, "wall")
for i in range(3):
    box(2+i*3.2, -0.35, 0, 2.4, 0.5, 3.0, M_DOCK); box(rax+1+i*2.6, -0.35, 0, 2.2, 0.5, 3.0, M_DOCK)

# forward-pick + racks (kept lighter so routes read)
box(cx0, 0.5, 0, core_w, FWD_H-1, 3.2, M_FWD, "forward")
for mnum in range(n_mod):
    bx = startx + mnum*pitch; is_sel = mnum >= sel_from
    rmat = M_SEL if is_sel else M_RES; H = SEL_H if is_sel else RES_H
    for (y0, y1) in runs:
        ln = y1-y0
        for dxp in (0.0, BLOCK-0.18): box(bx+dxp, y0, 0, 0.18, ln, H, M_BEAM, "up")
        for k in range(LEVELS):
            zz = 0.4 + k*(H-0.6)/(LEVELS-1); box(bx, y0, zz, BLOCK, ln, 0.10, rmat, "beam")

# ---------------- worker routes (glowing tubes on the floor) ----------------
def tube(points, rgb, rad=0.45, z=0.3):
    cu = bpy.data.curves.new("r", 'CURVE'); cu.dimensions = '3D'
    sp = cu.splines.new('POLY'); sp.points.add(len(points)-1)
    for i, (px, py) in enumerate(points):
        sp.points[i].co = (px, py, z, 1)
    cu.bevel_depth = rad; cu.bevel_resolution = 3
    ob = bpy.data.objects.new("route", cu); scene.collection.objects.link(ob)
    ob.data.materials.append(emit("e", rgb))
    # start marker
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.9, location=(points[0][0], points[0][1], z))
    s = bpy.context.active_object; s.data.materials.append(emit("es", rgb))

def serp(lanes, lo, hi, axis):
    pts = []
    for i, c in enumerate(lanes):
        a, b = (lo, hi) if i % 2 == 0 else (hi, lo)
        pts += [(c, a), (c, b)] if axis == "v" else [(a, c), (b, c)]
    return pts

AMBER, VIOLET, CYAN, GREEN, RED = (0.85,0.55,0.10),(0.49,0.20,0.66),(0.03,0.57,0.70),(0.10,0.60,0.30),(0.86,0.15,0.15)
tube(serp([1.6, 3.7, 5.8], cx0+2, cx1-2, "h"), AMBER)                       # zone1 fast
tube(serp([cx0+8, (cx0+cmid)/2, cmid-8], ry0+2, ry1-2, "v"), VIOLET)        # zone2 reserve-left
tube(serp([cmid+8, (cmid+cx1)/2, cx1-8], ry0+2, ry1-2, "v"), CYAN)          # zone3 reserve-right
tube([(6, 11), (cx0+2, 20), (cx0+7, 40)], GREEN)                           # reach-truck putaway
for xr in (cx0+core_w*0.34, cx0+core_w*0.64):                               # replenishment shuttles
    tube([(xr, FWD_H+7), (xr, FWD_H-2)], GREEN, rad=0.28)
tube([(rax+right_w/2, 55), (rax+right_w/2, 6), (rax+right_w/2, 0.5)], RED)   # handler pack->ship

# ---------------- lighting ----------------
scene.world = bpy.data.worlds.new("W"); scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (0.96, 0.97, 0.99, 1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value = 0.9
sd = bpy.data.lights.new("Sun", 'SUN'); sd.energy = 3.0
su = bpy.data.objects.new("Sun", sd); scene.collection.objects.link(su); su.rotation_euler = (math.radians(50), math.radians(15), math.radians(40))

# ---------------- camera (higher angle so aisles & routes are visible) ----------------
cam_d = bpy.data.cameras.new("Cam"); cam_d.type = 'ORTHO'; cam_d.ortho_scale = 128
cam = bpy.data.objects.new("Cam", cam_d); scene.collection.objects.link(cam)
cam.location = (L/2 - 12, -46, 165)
tgt = bpy.data.objects.new("T", None); scene.collection.objects.link(tgt); tgt.location = Vector((L/2, DEPTH/2, 2))
cc = cam.constraints.new('TRACK_TO'); cc.target = tgt; cc.track_axis = 'TRACK_NEGATIVE_Z'; cc.up_axis = 'UP_Y'
scene.camera = cam

try: scene.render.engine = 'BLENDER_EEVEE_NEXT'
except Exception: scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1700; scene.render.resolution_y = 1100
scene.view_settings.view_transform = 'Standard'
scene.render.filepath = OUT
bpy.ops.render.render(write_still=True)
print("RENDERED:", OUT)
