"""
PHASE 6 - LAYOUT & ZONING (Option B), 3-dimensional.
Sizes each functional zone from the capacity analysis, lays them out to scale in
a flow-through block plan, and renders a 3D massing. Verifies total floor area
and pallet-position capacity against the 7,000 m2 / 12.2 m envelope.
Outputs: outputs/figures/layout_plan.png, layout_3d.png (+ metrics, table).
"""
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from _util import FIGS, save_table, update_metrics
import pandas as pd

M = json.load(open(os.path.join(os.path.dirname(__file__), "..", "outputs", "reports", "phase1_metrics.json"), encoding="utf-8"))
cap = M["capacity"]
target_pos = cap["design_positions_target"]           # ~14,074
DD_DENS, SEL_DENS = 0.293, 0.345                        # m2/position (double-deep, selective)
DD_SHARE = 0.85
dd_pos = target_pos * DD_SHARE
sel_pos = target_pos * (1 - DD_SHARE)
dd_area = dd_pos * DD_DENS
sel_area = sel_pos * SEL_DENS

# ---- functional zones: (name, area m2, 3D height m, colour) ----
zones = [
    ("Receiving &\ninbound staging", 700, 8.0,  "#f4c58a"),
    ("Offices &\namenities",         300, 4.0,  "#c9c9c9"),
    ("Returns / VAS",                300, 4.0,  "#e3b7d6"),
    ("Double-deep reserve\n(A/B)",   round(dd_area), 11.5, "#6c8eef"),
    ("Selective + cantilever\n(irregular/XLONG/C)", round(sel_area), 11.5, "#8fa9f2"),
    ("Forward-pick module\n(carton-flow/shelving)", 400, 4.5, "#9ad0a0"),
    ("Packing &\nconsolidation",     700, 4.5,  "#f2a6a6"),
    ("Outbound staging\n& shipping",  300, 8.0,  "#f4c58a"),
    ("Circulation / aisles",         560, 0.2,  "#eef2fb"),
]
total_area = sum(z[1] for z in zones)
pct_env = total_area / 7000 * 100
positions_capacity = int(dd_area / DD_DENS + sel_area / SEL_DENS)

tbl = pd.DataFrame([(n.replace("\n", " "), a, f"{a/total_area*100:.0f}%") for n, a, _, _ in zones],
                   columns=["Zone", "Area m2", "% of building"]).set_index("Zone")
save_table(tbl, "layout_zones.csv")

# ============================ 2D PLAN (to scale) ============================
DEPTH = 70.0  # building depth (m)
# three columns: left support | storage core | right pack-ship, with 4 m aisles
left = [("Receiving &\ninbound staging", 700, "#f4c58a"),
        ("Offices &\namenities", 300, "#c9c9c9"),
        ("Returns / VAS", 300, "#e3b7d6")]
core = [("Double-deep reserve (A/B)", round(dd_area), "#6c8eef"),
        ("Selective + cantilever", round(sel_area), "#8fa9f2"),
        ("Forward-pick module", 400, "#9ad0a0")]
right = [("Packing &\nconsolidation", 700, "#f2a6a6"),
         ("Outbound staging\n& shipping", 300, "#f4c58a")]

left_w, right_w, aisle = 20.0, 14.0, 4.0
core_area = sum(a for _, a, _ in core)
core_w = core_area / DEPTH
L = left_w + aisle + core_w + aisle + right_w

fig, ax = plt.subplots(figsize=(12, 7.2))
ax.set_xlim(-2, L + 2); ax.set_ylim(-6, DEPTH + 4); ax.set_aspect("equal"); ax.axis("off")
ax.set_title(f"Option B — warehouse layout & zoning (to scale)\n"
             f"Total {total_area:,} m² ({pct_env:.0f}% of 7,000 m² envelope) · "
             f"~{positions_capacity:,} pallet positions · building ≈ {L:.0f} m × {DEPTH:.0f} m",
             fontsize=12, weight="bold")

def stack_col(x0, w, items, top=DEPTH):
    y = top
    for name, area, col in items:
        h = area / w
        ax.add_patch(Rectangle((x0, y - h), w, h, facecolor=col, edgecolor="white", lw=1.5))
        ax.text(x0 + w/2, y - h/2, f"{name}\n{area:,} m²", ha="center", va="center",
                fontsize=8, weight="bold", color="#12203a")
        y -= h

stack_col(0, left_w, left)
stack_col(left_w + aisle, core_w, core)
stack_col(left_w + aisle + core_w + aisle, right_w, right)
# aisles
for ax0 in (left_w, left_w + aisle + core_w):
    ax.add_patch(Rectangle((ax0, 0), aisle, DEPTH, facecolor="#eef2fb", edgecolor="none", hatch="//", alpha=0.6))
# dock doors (bottom)
for dx in np.arange(2, L, 8):
    ax.add_patch(Rectangle((dx, -1.2), 2.4, 1.2, facecolor="#33415a", edgecolor="none"))
ax.text(left_w/2, -3.2, "▲ RECEIVING docks", ha="center", fontsize=8, color="#33415a", weight="bold")
ax.text(L - right_w/2, -3.2, "SHIPPING docks ▲", ha="center", fontsize=8, color="#33415a", weight="bold")
# material-flow arrows
flow = [(left_w/2, 52, left_w + aisle + core_w/2, 52),
        (left_w + aisle + core_w/2, 20, left_w + aisle + core_w/2, 10),
        (left_w + aisle + core_w, 8, L - right_w, 8),
        (L - right_w/2, 40, L - right_w/2, 18)]
for x0, y0, x1, y1 in flow:
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="-|>", color="#d40011", lw=2.2, alpha=0.8))
ax.text(L/2, DEPTH + 2, "Material flow: Receive → Store → Forward-pick → Pack → Ship",
        ha="center", fontsize=9, color="#d40011", style="italic")
fig.savefig(os.path.join(FIGS, "layout_plan.png"), dpi=115, bbox_inches="tight")
plt.close(fig)

# ============================ 3D MASSING ============================
fig = plt.figure(figsize=(11, 7))
ax = fig.add_subplot(111, projection="3d")
def box(x, y, dx, dy, dz, color):
    xx = [x, x+dx]; yy = [y, y+dy]; zz = [0, dz]
    verts = [
        [(xx[0],yy[0],zz[0]),(xx[1],yy[0],zz[0]),(xx[1],yy[1],zz[0]),(xx[0],yy[1],zz[0])],
        [(xx[0],yy[0],zz[1]),(xx[1],yy[0],zz[1]),(xx[1],yy[1],zz[1]),(xx[0],yy[1],zz[1])],
        [(xx[0],yy[0],zz[0]),(xx[1],yy[0],zz[0]),(xx[1],yy[0],zz[1]),(xx[0],yy[0],zz[1])],
        [(xx[0],yy[1],zz[0]),(xx[1],yy[1],zz[0]),(xx[1],yy[1],zz[1]),(xx[0],yy[1],zz[1])],
        [(xx[0],yy[0],zz[0]),(xx[0],yy[1],zz[0]),(xx[0],yy[1],zz[1]),(xx[0],yy[0],zz[1])],
        [(xx[1],yy[0],zz[0]),(xx[1],yy[1],zz[0]),(xx[1],yy[1],zz[1]),(xx[1],yy[0],zz[1])],
    ]
    pc = Poly3DCollection(verts, facecolor=color, edgecolor="#33415a", linewidths=0.5, alpha=1.0)
    pc.set_sort_zpos(y + dy / 2)   # hint depth-sort by the block's own position
    ax.add_collection3d(pc)

# place same columns in 3D with heights; GAP separates blocks so tall/short zones read cleanly
GAP = 2.0
def place(x0, w, items, heights):
    y = DEPTH
    for (name, area, col), h in zip(items, heights):
        dy = area / w
        box(x0, y - dy + GAP / 2, w, max(dy - GAP, 1.0), h, col)
        y -= dy

place(0, left_w, left, [8.0, 4.0, 4.0])
place(left_w + aisle, core_w, core, [11.5, 11.5, 4.5])
place(left_w + aisle + core_w + aisle, right_w, right, [4.5, 8.0])
ax.set_xlim(0, L); ax.set_ylim(0, DEPTH); ax.set_zlim(0, 12.2)
ax.set_box_aspect((L, DEPTH, 26))
ax.set_xlabel("length (m)"); ax.set_ylabel("depth (m)"); ax.set_zlabel("height (m)")
ax.set_title("Option B — 3D massing (max height 12.2 m; reserve racks ≈ 11.5 m)", fontsize=12, weight="bold")
ax.view_init(elev=32, azim=-72)
fig.savefig(os.path.join(FIGS, "layout_3d.png"), dpi=115, bbox_inches="tight")
plt.close(fig)

update_metrics("layout", {
    "building_L_m": round(L, 1), "building_depth_m": DEPTH,
    "total_area_m2": total_area, "pct_of_7000": round(pct_env, 0),
    "positions_capacity": positions_capacity, "positions_target": target_pos,
    "fits_7000": total_area <= 7000, "zones": tbl.reset_index().to_dict("records"),
    "dd_area_m2": round(dd_area), "sel_area_m2": round(sel_area),
})

print(f"Total floor {total_area:,} m2 = {pct_env:.0f}% of 7,000 | building {L:.0f} x {DEPTH:.0f} m")
print(f"Pallet positions provided ~{positions_capacity:,} vs target {target_pos:,} "
      f"({'OK' if positions_capacity>=target_pos else 'SHORT'})")
print(tbl.to_string())
