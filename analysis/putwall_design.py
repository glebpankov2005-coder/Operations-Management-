"""
PUT-TO-LIGHT WALL - how small orders are sorted, where things stand and who walks where.
Draws (a) a plan view of the packing area (put-wall, small-parts shelving, pack stations, carrier cages) with the
numbered worker steps, and (b) a front view of the wall with its tote slots and lights.
Sizes come from picking_plan.py (slots, totes per order) and the layout (packing area 450 m2).
Output: outputs/figures/putwall_layout.png (+ metrics section "putwall_design"). Run after picking_plan.py.
"""
import json, os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, FancyArrowPatch
from _util import save_fig, update_metrics, REPORTS
from geometry import right_w, PACK

M = json.load(open(os.path.join(REPORTS, "phase1_metrics.json"), encoding="utf-8"))
PK = M["picking"]; PW = PK["putwall"]; SP = PK["small_parts"]
INK, SUB = "#1f2937", "#6b7280"
BLUE, ORANGE, AQUA, YELLOW, GREY = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#a3abb8"
W, H = right_w, PACK / right_w                        # packing area: ~9.5 m wide x ~47 m long (east column)

fig = plt.figure(figsize=(16, 9.6))
ax = fig.add_axes([0.02, 0.47, 0.96, 0.47]); bx = fig.add_axes([0.02, 0.03, 0.48, 0.40]); tx = fig.add_axes([0.53, 0.03, 0.46, 0.40])
for a in (ax, bx, tx):
    a.axis("off")

# ------------------------------------------------ (a) plan view, turned sideways: length of the column runs left -> right
# local coordinates: x = west -> east across the column (0..W), y = south -> north along it (0..H); drawn as (y, x)
ax.set_xlim(-6.0, H + 1.0); ax.set_ylim(-4.2, W + 1.6); ax.set_aspect("equal")
def R(x, y, w, h, **kw):
    ax.add_patch(Rectangle((y, x), h, w, **kw))
def T(x, y, t, **kw):
    ax.text(y, x, t, **kw)
R(0, 0, W, H, fc="#fbf3f3", ec="#c7cede", lw=1.4)
R(-3.2, -6.0, 3.2, H + 6.0, fc="#eef1f6", ec="none")
T(-1.6, H * 0.55, "right perimeter aisle — pickers arrive from the fast-pick and reserve zones", ha="center", va="center", fontsize=8, color=SUB)
R(0, -6.0, W, 5.8, fc="#fff4dc", ec="none")
T(W / 2, -3.1, "outbound\nstaging →\nshipping\ndoors", ha="center", va="center", fontsize=7.6, color=SUB)

def box(x, y, w, h, fc, ec="white", lw=1.0, z=2):
    R(x, y, w, h, fc=fc, ec=ec, lw=lw, zorder=z)

# small-parts bin shelving (north): rows of 1.2 m double-sided shelving with 1.0 m picking aisles
rows = int(np.ceil(SP["shelf_bays"] / (2 * int(W - 1.0))))
y_top = H - 0.6
for r in range(rows):
    y0 = y_top - (r + 1) * 1.2 - r * 1.0
    box(0.5, y0, W - 1.0, 1.2, "#c9d8f5", "#7d9be0", 0.6)
y_shelf = y_top - rows * 1.2 - (rows - 1) * 1.0
T(W / 2, (y_shelf + y_top) / 2, f"SMALL-PARTS BIN SHELVING · {SP['shelf_bays']} bays · {SP['skus']:,} slow small SKUs · "
  f"half-bins 300×400 mm, 7 levels", ha="center", va="center", fontsize=8, weight="bold", color="#1e4fa8", zorder=5,
  bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.92))

# put-wall (double-sided) along the column: put side faces the perimeter aisle, pack side faces the pack stations
wall_x, wall_y0 = 2.4, 7.0
wall_len = PW["length_m"]
box(wall_x, wall_y0, PW["depth_m"], wall_len, BLUE, "white", 0.8, z=3)
for k in range(PW["columns"] + 1):
    ax.plot([wall_y0 + k * 0.45] * 2, [wall_x, wall_x + PW["depth_m"]], color="white", lw=0.5, zorder=4)
T(wall_x + 0.3, wall_y0 + wall_len + 1.6, f"PUT-WALL\n{PW['slots']} slots", ha="center", va="center", fontsize=8, weight="bold", color=BLUE)
box(0.2, wall_y0, 2.0, wall_len, "#e6eefb", "#9db4fb", 0.6)
T(1.2, wall_y0 + wall_len * 0.55, "PUT SIDE: trolleys park, the putter scans and puts", ha="center", va="center", fontsize=7.6, color=INK)
nst = int(np.ceil([r for r in M["capacity_plan"]["labour_table"] if r["Process"].startswith("Packing")][0]["FTE peak"]))
st_h = wall_len / nst
for i in range(nst):
    box(4.6, wall_y0 + i * st_h + 0.3, 1.6, st_h - 0.6, "#f2c9b4", "white", 0.8)
    T(5.4, wall_y0 + (i + 0.5) * st_h, f"pack station {i + 1}", ha="center", va="center", fontsize=7, color=INK)
T(3.8, wall_y0 + wall_len * 0.45, "PACK SIDE: packers take complete orders", ha="center", va="center", fontsize=7.6, color=INK)
for i in range(7):
    box(6.8, wall_y0 + i * 1.5 + 0.2, 1.0, 1.1, "#d8f1e4", "#1baf7a", 0.6)
    box(8.1, wall_y0 + i * 1.5 + 0.2, 1.0, 1.1, "#d8f1e4", "#1baf7a", 0.6)
T(7.95, wall_y0 + 12.4, "ROLL CAGES\nper carrier", ha="center", va="center", fontsize=7.4, weight="bold", color="#167a55")
box(0.4, 0.6, 4.0, 5.6, "#fff0c9", "#eda100", 0.6); T(2.4, 3.4, "large-order\npallets waiting\n(EJE 120i)", ha="center", va="center", fontsize=7.2)
box(5.0, 0.6, 2.0, 2.6, "#e5e7eb", "#9ca3af", 0.6); T(6.0, 1.9, "stretch\nwrapper", ha="center", va="center", fontsize=7)
box(5.0, 3.6, 2.0, 2.6, "#e6eefb", "#9db4fb", 0.6); T(6.0, 4.9, "empty\ntotes", ha="center", va="center", fontsize=7)
box(7.3, 0.6, 1.6, 5.6, "#ede9fe", "#a78bfa", 0.6); T(8.1, 3.4, "cartons,\nfilm,\nlabels", ha="center", va="center", fontsize=7)

def arrow(p0, p1, color, rad=0.0, lw=2.2):
    ax.add_patch(FancyArrowPatch((p0[1], p0[0]), (p1[1], p1[0]), arrowstyle="-|>", mutation_scale=13, color=color, lw=lw,
                                 connectionstyle=f"arc3,rad={rad}", zorder=7))
def badge(x, y, n, color):
    ax.scatter([y], [x], s=200, color="white", edgecolor=color, lw=2, zorder=8)
    ax.text(y, x, str(n), ha="center", va="center", fontsize=8.5, weight="bold", color=color, zorder=9)
arrow((-0.8, wall_y0 + 3.0), (-0.8, -5.5), ORANGE); badge(-0.8, -1.0, 1, ORANGE)                       # picker leaves (to the zones)
arrow((-2.4, -5.5), (0.9, wall_y0 + 1.0), ORANGE, rad=0.25); badge(-2.4, -3.4, 2, ORANGE)              # comes back with a full trolley
arrow((1.4, y_shelf - 0.3), (1.4, wall_y0 + wall_len + 0.2), AQUA); badge(1.4, (y_shelf + wall_y0 + wall_len) / 2, 3, AQUA)
badge(1.2, wall_y0 + 0.9, 4, BLUE)
badge(3.8, wall_y0 + wall_len * 0.88, 5, "#b45309")
arrow((6.2, wall_y0 + st_h * 0.5), (6.8, wall_y0 + st_h * 0.5), "#167a55"); badge(6.5, wall_y0 + st_h * 1.2, 6, "#167a55")
arrow((9.3, wall_y0 + 0.6), (9.3, -1.0), "#167a55"); badge(9.3, wall_y0 - 0.6, 7, "#167a55")
arrow((5.0, 4.9), (2.0, wall_y0 + 0.4), GREY, rad=-0.2, lw=1.6); badge(3.6, 6.0, 8, "#6b7280")
ax.text(H / 2 - 2, W + 1.1, "(a) Packing area seen from above — north is to the right; shipping doors are to the left (south)",
        ha="center", fontsize=10.5, weight="bold", color=INK)
ax.plot([H - 9.5, H - 4.5], [-3.9, -3.9], color=INK, lw=2); ax.text(H - 7, -3.7, "5 m", ha="center", va="bottom", fontsize=7.5)

# ------------------------------------------------ (b) front view of the wall (put side)
cols, lev = PW["columns"], PW["levels"]
bx.set_xlim(-0.6, cols * 0.45 + 0.6); bx.set_ylim(-0.35, 2.55); bx.set_aspect("equal")
rng = np.random.default_rng(3)
lit_put = set(rng.choice(cols * lev, 3, replace=False)); full = set(rng.choice(cols * lev, 5, replace=False)) - lit_put
two = [(5, 1), (14, 2)]                                                           # examples of 2-tote orders (adjacent slots)
for c in range(cols):
    for l in range(lev):
        x0, y0 = c * 0.45, 0.2 + l * 0.36
        idx = c * lev + l
        used = rng.random() < 0.55
        bx.add_patch(Rectangle((x0, y0), 0.45, 0.36, fc="#f8fafc", ec="#94a3b8", lw=0.6))
        if used:
            bx.add_patch(Rectangle((x0 + 0.04, y0 + 0.03), 0.37, 0.27, fc="#93c5fd", ec="#2563eb", lw=0.5))    # order tote
        col = YELLOW if idx in lit_put else (AQUA if idx in full else "#cbd5e1")
        bx.add_patch(Rectangle((x0 + 0.1, y0 + 0.315), 0.25, 0.035, fc=col, ec="none"))                    # light + button
        if idx in lit_put:
            bx.text(x0 + 0.225, y0 + 0.15, "2", ha="center", va="center", fontsize=8, weight="bold", color=INK)
for c, l in two:
    bx.add_patch(Rectangle((c * 0.45, 0.2 + l * 0.36), 0.9, 0.36, fc="none", ec=ORANGE, lw=1.8, ls="--"))
bx.plot([-0.4, cols * 0.45 + 0.4], [0, 0], color=INK, lw=1.5)
for hh in (0.2, 1.0, 2.0):
    bx.plot([-0.45, -0.35], [hh, hh], color=INK, lw=1); bx.text(-0.48, hh, f"{hh:.1f} m", ha="right", va="center", fontsize=7)
bx.text(cols * 0.45 / 2, 2.4, f"(b) Front of the wall (put side): {cols} columns × {lev} levels = {PW['slots']} tote slots, "
        f"{PW['length_m']} m long, open on both sides", ha="center", fontsize=10, weight="bold", color=INK)
from matplotlib.patches import Patch
bx.legend(handles=[Patch(fc="#93c5fd", ec="#2563eb", label="order tote in its slot"),
                   Patch(fc=YELLOW, label="put light: 'put 2 here' (press to confirm)"),
                   Patch(fc=AQUA, label="order complete: packer takes it"),
                   Patch(fc="none", ec=ORANGE, ls="--", label="bigger order: 2 slots side by side")],
          loc="upper center", bbox_to_anchor=(0.5, -0.02), ncol=2, fontsize=8, frameon=False)

# ------------------------------------------------ steps text
steps = [
    (ORANGE, "1", "Wave starts: the WMS gives every small order a slot and fills each trolley batch to 80% (volume/weight)."),
    (ORANGE, "2", f"Picker takes a trolley with 6 empty totes, picks the batch in their zone (~{PK['small_orders'][0]['Lines per tour']:.0f} lines), "
                  "returns to the put side and takes an empty trolley."),
    (AQUA, "3", f"Small slow parts: picked from the bin shelving right behind the wall (~{SP['lines_day']:.0f} lines/day)."),
    (BLUE, "4", "Putter scans an item → one slot lights up with the quantity → item into that order's tote → press the light."),
    ("#b45309", "5", "When all items of an order are in, its light on the pack side turns on; the packer takes the tote out."),
    ("#167a55", "6", "Packer scans, packs in a carton, prints the carrier label and puts the carton in that carrier's roll cage."),
    ("#167a55", "7", "Roll cages go to the outbound lane of their trailer before its departure slot."),
    ("#6b7280", "8", "Empty totes go back to the tote rack; the slot is free for the next order."),
]
for i, (c, n, t) in enumerate(steps):
    y = 0.95 - i * 0.12
    tx.scatter([0.015], [y], s=150, color="white", edgecolor=c, lw=2, transform=tx.transAxes)
    tx.text(0.015, y, n, ha="center", va="center", fontsize=8, weight="bold", color=c, transform=tx.transAxes)
    tx.text(0.04, y, t, ha="left", va="center", fontsize=8.8, color=INK, transform=tx.transAxes)
fig.suptitle("Put-to-light wall: how small orders are sorted, and who works where", fontsize=15, weight="bold", color=INK, y=0.995)
save_fig(fig, "putwall_layout.png")

update_metrics("putwall_design", {"wall": PW, "packing_area_m": [round(W, 1), round(H, 1)], "shelf_rows": rows,
                                  "pack_stations": nst})
print("Saved putwall_layout.png", PW, "shelf rows", rows)
