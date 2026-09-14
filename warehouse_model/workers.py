"""
Blender render of WORKER MOVEMENT (zone picking) - solid, well-lit warehouse
viewed down the aisles from the front, with bold painted floor-lane routes and
worker figures. Run: blender --background --python warehouse_model/workers.py
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

def mat(name, rgba, rough=0.6, metal=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rgba
    b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    return m
def emit(rgb, strength=2.6):
    m = bpy.data.materials.new("e"); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = strength
    return m

M_FLOOR = mat("floor", (0.88, 0.89, 0.92, 1), 0.9)
M_RES = mat("res", (0.30, 0.42, 0.85, 1), 0.5, 0.2); M_SEL = mat("sel", (0.55, 0.66, 0.95, 1), 0.5, 0.2)
M_BEAM = mat("beam", (0.16, 0.22, 0.45, 1), 0.4, 0.4); M_PAL = mat("pal", (0.80, 0.62, 0.34, 1), 0.8)
M_FWD = mat("fwd", (0.35, 0.74, 0.52, 1), 0.6); M_OFF = mat("off", (0.78, 0.80, 0.86, 1), 0.6)
M_PACK = mat("pack", (0.94, 0.62, 0.62, 1), 0.7); M_RECV = mat("recv", (0.95, 0.78, 0.45, 1), 0.7)
M_WALL = mat("wall", (0.93, 0.94, 0.97, 1), 0.85); M_DOCK = mat("dock", (0.22, 0.26, 0.34, 1), 0.5)
M_BODY = mat("body", (0.12, 0.14, 0.20, 1), 0.6)

def box(x, y, z0, sx, sy, sz, m, name="b"):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x+sx/2, y+sy/2, z0+sz/2))
    o = bpy.context.active_object; o.scale = (sx, sy, sz); o.name = name
    o.data.materials.append(m); return o
def plane(x, y, sx, sy, z, m):
    bpy.ops.mesh.primitive_plane_add(size=1, location=(x+sx/2, y+sy/2, z))
    o = bpy.context.active_object; o.scale = (sx, sy, 1); o.data.materials.append(m); return o

# floor + zone decals + building
box(0, 0, -0.2, L, DEPTH, 0.2, M_FLOOR, "floor")
oh, rh, vh = 250/left_w, 180/left_w, 262/left_w
plane(0.3, DEPTH-oh, left_w-0.6, oh-0.6, 0.02, M_OFF); plane(0.3, DEPTH-oh-rh, left_w-0.6, rh-0.4, 0.02, M_PACK)
plane(0.3, 0.3, left_w-0.6, vh-0.6, 0.02, M_RECV)
ph, uh = 450/right_w, 216/right_w
plane(rax+0.3, DEPTH-ph, right_w-0.6, ph-0.6, 0.02, M_PACK); plane(rax+0.3, 0.3, right_w-0.6, uh-0.4, 0.02, M_RECV)
box(0.5, DEPTH-oh+0.5, 0, left_w-1, oh-1, 6, M_OFF, "office")
for wx, wy, wsx, wsy, wsz in [(0,0,L,0.3,2),(0,DEPTH-0.3,L,0.3,8),(0,0,0.3,DEPTH,8),(L-0.3,0,0.3,DEPTH,8)]:
    box(wx, wy, 0, wsx, wsy, wsz, M_WALL, "wall")
for i in range(3):
    box(2+i*3.2, -0.35, 0, 2.4, 0.5, 3, M_DOCK); box(rax+1+i*2.6, -0.35, 0, 2.2, 0.5, 3, M_DOCK)

box(cx0, 0.5, 0, core_w, FWD_H-1, 3.2, M_FWD, "forward")
for mnum in range(n_mod):
    bx = startx + mnum*pitch; is_sel = mnum >= sel_from
    rmat = M_SEL if is_sel else M_RES; H = SEL_H if is_sel else RES_H
    for (y0, y1) in runs:
        ln = y1-y0
        for dxp in (0.0, BLOCK-0.18): box(bx+dxp, y0, 0, 0.18, ln, H, M_BEAM, "up")
        for k in range(LEVELS): box(bx, y0, 0.4+k*(H-0.6)/(LEVELS-1), BLOCK, ln, 0.1, rmat, "beam")
        for _ in range(3):
            lv = random.randint(0, LEVELS-2); zz = 0.4+lv*(H-0.6)/(LEVELS-1)+0.1
            box(bx+0.25, y0+random.uniform(0.5, ln-1.4), zz, BLOCK-0.5, 1.1, 0.9, M_PAL, "pal")

# ---------------- worker routes as bold painted floor-lanes + worker figures ----------------
def strip(p0, p1, rgb, w=0.75, z=0.10):
    x0, y0 = p0; x1, y1 = p1; dx, dy = x1-x0, y1-y0; ln = math.hypot(dx, dy)
    if ln < 0.05: return
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x0+x1)/2, (y0+y1)/2, z))
    o = bpy.context.active_object; o.scale = (ln, w, 0.08); o.rotation_euler = (0, 0, math.atan2(dy, dx))
    o.data.materials.append(emit(rgb))
def worker(x, y, rgb):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.32, depth=1.2, location=(x, y, 0.6))
    bpy.context.active_object.data.materials.append(mat("v", (*rgb, 1), 0.5))
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.34, location=(x, y, 1.4))
    bpy.context.active_object.data.materials.append(M_BODY)
def route(points, rgb, put_workers=True):
    for a, b in zip(points[:-1], points[1:]):
        strip(a, b, rgb)
    if put_workers:
        worker(points[0][0], points[0][1], rgb)
        mid = points[len(points)//2]; worker(mid[0], mid[1], rgb)

def serp(lanes, lo, hi, axis):
    pts = []
    for i, c in enumerate(lanes):
        a, b = (lo, hi) if i % 2 == 0 else (hi, lo)
        pts += [(c, a), (c, b)] if axis == "v" else [(a, c), (b, c)]
    return pts

AMBER, VIOLET, CYAN, GREEN, RED = (0.90,0.55,0.05),(0.55,0.20,0.75),(0.05,0.62,0.78),(0.10,0.62,0.30),(0.90,0.12,0.12)
# actual aisle centres (between rack blocks) so routes never cross racks
aisle_xs = [startx + m*pitch + BLOCK + AISLEW/2 for m in range(n_mod - 1)]
left_ais = [x for x in aisle_xs if x < cmid]
right_ais = [x for x in aisle_xs if x >= cmid]
def serp_aisles(xs, y0, y1):
    pts = []
    for i, x in enumerate(xs):
        a, b = (y0, y1) if i % 2 == 0 else (y1, y0)
        pts += [(x, a), (x, b)]
    return pts
# Zone 1 (fast) - along the forward-pick face (open zone)
route(serp([1.8, 4.0, 6.0], cx0+2, cx1-2, "h"), AMBER)
# Zone 2 & 3 pickers - serpentine strictly along reserve aisles
route(serp_aisles(left_ais[::2][:3], ry0+2, ry1-2), VIOLET)
route(serp_aisles(right_ais[::2][:3], ry0+2, ry1-2), CYAN)
# Reach truck putaway: receiving -> perimeter aisle -> up an aisle
la_x = cx0 - aisle/2
route([(5, 10), (la_x, 22), (aisle_xs[1], 30), (aisle_xs[1], ry1-4)], GREEN)
# replenishment: two aisles, reserve -> forward
for xr in (aisle_xs[2], aisle_xs[len(aisle_xs)//2]):
    strip((xr, ry0+3), (xr, FWD_H-1), GREEN, w=0.7)
# handler: right perimeter aisle, pack -> ship
ha_x = cx1 + aisle/2
route([(ha_x, 55), (ha_x, 6)], RED)

# ---------------- lighting (with shadows for depth) ----------------
scene.world = bpy.data.worlds.new("W"); scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (0.90, 0.92, 0.96, 1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value = 0.55
sd = bpy.data.lights.new("Sun", 'SUN'); sd.energy = 4.0; sd.angle = 0.1
su = bpy.data.objects.new("Sun", sd); scene.collection.objects.link(su)
su.rotation_euler = (math.radians(48), math.radians(12), math.radians(150))
ad = bpy.data.lights.new("Fill", 'AREA'); ad.energy = 9000; ad.size = 70
af = bpy.data.objects.new("Fill", ad); scene.collection.objects.link(af); af.location = (L/2, -45, 50)

# ---------------- camera: near top-down (bird's-eye) so all routes are visible, no occlusion ----------------
cam_d = bpy.data.cameras.new("Cam"); cam_d.type = 'ORTHO'; cam_d.ortho_scale = 124
cam = bpy.data.objects.new("Cam", cam_d); scene.collection.objects.link(cam)
cam.location = (L/2, DEPTH/2 - 14, 175)
tgt = bpy.data.objects.new("T", None); scene.collection.objects.link(tgt); tgt.location = Vector((L/2, DEPTH/2, 0))
cc = cam.constraints.new('TRACK_TO'); cc.target = tgt; cc.track_axis = 'TRACK_NEGATIVE_Z'; cc.up_axis = 'UP_Y'
scene.camera = cam

try: scene.render.engine = 'BLENDER_EEVEE_NEXT'
except Exception: scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1700; scene.render.resolution_y = 1150
scene.view_settings.view_transform = 'Standard'
scene.render.filepath = OUT
bpy.ops.render.render(write_still=True)
print("RENDERED:", OUT)
