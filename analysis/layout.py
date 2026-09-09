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
# left column ordered top->bottom so Receiving sits at the BOTTOM, next to its docks
left = [("Offices &\namenities", 300, "#c9c9c9"),
        ("Returns / VAS", 300, "#e3b7d6"),
        ("Receiving &\ninbound staging", 700, "#f4c58a")]
core = [("Double-deep reserve (A/B)", round(dd_area), "#6c8eef"),
        ("Selective + cantilever", round(sel_area), "#8fa9f2"),
        ("Forward-pick module", 400, "#9ad0a0")]
right = [("Packing &\nconsolidation", 700, "#f2a6a6"),
         ("Outbound staging\n& shipping", 300, "#f4c58a")]

left_w, right_w, aisle = 20.0, 14.0, 4.0
core_area = sum(a for _, a, _ in core)
core_w = core_area / DEPTH
L = left_w + aisle + core_w + aisle + right_w

from matplotlib.patches import Polygon as MplPolygon, FancyArrowPatch
from matplotlib.lines import Line2D
import math

# ============================ 2D PLAN + ORDER FLOW ============================
fig, ax = plt.subplots(figsize=(12.5, 7.6))
ax.set_xlim(-3, L + 3); ax.set_ylim(-8, DEPTH + 6); ax.set_aspect("equal"); ax.axis("off")
ax.set_title(f"Option B — warehouse layout, zoning & order flow (to scale)\n"
             f"Total {total_area:,} m² ({pct_env:.0f}% of 7,000 m² envelope) · "
             f"~{positions_capacity:,} pallet positions · building ≈ {L:.0f} m × {DEPTH:.0f} m",
             fontsize=12, weight="bold")

C = {}  # zone name -> (cx, cy, x0, x1, y0, y1)
def stack_col(x0, w, items, top=DEPTH):
    y = top
    for name, area, col in items:
        h = area / w
        ax.add_patch(Rectangle((x0, y - h), w, h, facecolor=col, edgecolor="white", lw=1.5))
        ax.text(x0 + w/2, y - h/2, f"{name}\n{area:,} m²", ha="center", va="center",
                fontsize=8, weight="bold", color="#12203a")
        C[name] = (x0 + w/2, y - h/2, x0, x0 + w, y - h, y)
        y -= h

stack_col(0, left_w, left)
stack_col(left_w + aisle, core_w, core)
stack_col(left_w + aisle + core_w + aisle, right_w, right)
for ax0 in (left_w, left_w + aisle + core_w):
    ax.add_patch(Rectangle((ax0, 0), aisle, DEPTH, facecolor="#eef2fb", edgecolor="none", hatch="//", alpha=0.6))
for dx in np.arange(2, L, 8):
    ax.add_patch(Rectangle((dx, -1.4), 2.4, 1.4, facecolor="#33415a", edgecolor="none"))
ax.text(left_w/2, -3.6, "▲ RECEIVING docks", ha="center", fontsize=8, color="#33415a", weight="bold")
ax.text(L - right_w/2, -3.6, "SHIPPING docks ▲", ha="center", fontsize=8, color="#33415a", weight="bold")

recv, off, ret = C["Receiving &\ninbound staging"], C["Offices &\namenities"], C["Returns / VAS"]
dd, sel, fp = C["Double-deep reserve (A/B)"], C["Selective + cantilever"], C["Forward-pick module"]
pack, ship = C["Packing &\nconsolidation"], C["Outbound staging\n& shipping"]

def arrow(p0, p1, color, ls="-", rad=0.0, lw=2.6):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=18, color=color,
                                 lw=lw, linestyle=ls, connectionstyle=f"arc3,rad={rad}", zorder=6))

def step(p, n):
    ax.text(p[0], p[1], str(n), ha="center", va="center", fontsize=8.5, weight="bold",
            color="white", zorder=7,
            bbox=dict(boxstyle="circle,pad=0.25", fc="#12203a", ec="white", lw=1))

BLUE, GREEN, REDD = "#2b6cb0", "#2f855a", "#d40011"
# 1 inbound at dock -> receiving
arrow((recv[0], -1.2), (recv[0], recv[4] + 3), BLUE); step((recv[0], recv[4] - 2), 1)
# 2 putaway: receiving -> double-deep reserve
arrow((recv[3], recv[1]), (dd[2] + 6, dd[1]), BLUE, rad=-0.15); step(((recv[3]+dd[2])/2, dd[1] + 4), 2)
# 3 replenishment: reserve -> forward pick (dashed green)
arrow((dd[0], dd[4]), (fp[0], fp[1] + 1.2), GREEN, ls=(0, (5, 3)), rad=0.0); step((dd[0] + 8, (dd[4]+fp[5])/2), 3)
# 4 order pick: forward-pick -> packing  (+ full-pallet from reserve, thin)
arrow((fp[3], fp[1]), (pack[0], pack[1] - 6), REDD, rad=-0.2); step(((fp[3]+pack[0])/2, fp[1] + 2), 4)
arrow((dd[3], dd[1] - 8), (pack[2] - 1, pack[1] + 4), REDD, ls=(0, (2, 2)), rad=-0.25, lw=1.6)
# 5 pack -> outbound staging -> ship out
arrow((pack[0], pack[4]), (ship[0], ship[5] - 1), REDD); step((pack[0], (pack[4]+ship[5])/2), 5)
arrow((ship[0], ship[4] + 2), (ship[0], -1.4), REDD); step((ship[0], ship[4] - 1), 6)

# ---- reverse logistics (returns) ----
PURPLE, GREY = "#7c3aed", "#64748b"
# 7 returns arrive at receiving docks -> Returns/VAS (inspect & grade)
arrow((recv[0] - 5, recv[1] + 4), (ret[0] - 5, ret[4] + 2), PURPLE); step((ret[0] - 5, ret[4] - 3), 7)
# 8 restock good returns -> reserve storage
arrow((ret[3], ret[1] + 2), (dd[2] + 6, dd[1] + 10), PURPLE, rad=-0.15); step(((ret[3]+dd[2])/2, dd[1] + 13), 8)
# 9 scrap / return-to-vendor -> out
arrow((ret[2], ret[1] - 4), (-1.8, ret[1] - 4), PURPLE, ls=(0, (4, 3)), lw=1.8); step((ret[2] - 6, ret[1] - 4), 9)
ax.text(-1.8, ret[1] - 7, "scrap / RTV", ha="left", fontsize=7, color=PURPLE, style="italic")
# cross-dock: receiving -> outbound staging direct, routed near the top (855 SKUs shipped, never stocked)
arrow((recv[3], 64), (ship[2], 64), GREY, ls=(0, (2, 2)), rad=-0.10, lw=1.6)
ax.text((recv[3]+ship[2])/2, 67, "cross-dock (855 SKUs shipped, never stocked)",
        ha="center", fontsize=7, color=GREY, style="italic")

handles = [
    Line2D([0], [0], color=BLUE, lw=3, label="1–2  Inbound & putaway"),
    Line2D([0], [0], color=GREEN, lw=3, ls="--", label="3  Replenishment (reserve→forward)"),
    Line2D([0], [0], color=REDD, lw=3, label="4–6  Order flow: pick → pack → ship"),
    Line2D([0], [0], color=PURPLE, lw=3, label="7–9  Returns: in → grade → restock / scrap"),
    Line2D([0], [0], color=GREY, lw=2, ls=":", label="Cross-dock (bypasses storage)"),
]
ax.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, -0.12), ncol=3,
          fontsize=8.3, frameon=False)
fig.savefig(os.path.join(FIGS, "layout_plan.png"), dpi=115, bbox_inches="tight")
plt.close(fig)

# ============================ 3D MASSING (manual isometric, painter-ordered) ============================
EZ = 3.6  # vertical exaggeration so heights are legible next to the 100 m footprint
def iso(x, y, z):
    a = math.radians(30)
    return (x - y) * math.cos(a), (x + y) * math.sin(a) + z * EZ

def shade(hexcol, f):
    h = hexcol.lstrip("#"); r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(c * f))) for c in (r, g, b))

GAP = 2.0
boxes = []  # (x0, y0, dx, dy, dz, color, name)
def add_col(x0, w, items, heights):
    y = DEPTH
    for (name, area, col), h in zip(items, heights):
        dy = area / w
        boxes.append((x0, y - dy + GAP/2, w, max(dy - GAP, 1.0), h, col, name.replace("\n", " ")))
        y -= dy
add_col(0, left_w, left, [5.0, 2.5, 1.8])   # offices, returns, receiving(low, dock-adjacent)
add_col(left_w + aisle, core_w, core, [11.5, 10.5, 3.5])
add_col(left_w + aisle + core_w + aisle, right_w, right, [2.8, 1.8])

fig, ax = plt.subplots(figsize=(13, 7.6)); ax.set_aspect("equal"); ax.axis("off")
ax.set_title("Option B — 3D massing (isometric; max height 12.2 m, reserve racks ≈ 11.5 m)",
             fontsize=12, weight="bold")
pts = []
# floor slab (drawn first, farthest)
floor = [iso(0, 0, 0), iso(L, 0, 0), iso(L, DEPTH, 0), iso(0, DEPTH, 0)]
ax.add_patch(MplPolygon(floor, closed=True, facecolor="#f3f5fa", edgecolor="#cdd6ea", lw=1)); pts += floor

def draw_box(b):
    x0, y0, dx, dy, dz, col, name = b
    x1, y1 = x0 + dx, y0 + dy
    A, B, D_, Ap, Bp, Cp, Dp = iso(x0,y0,0), iso(x1,y0,0), iso(x0,y1,0), \
        iso(x0,y0,dz), iso(x1,y0,dz), iso(x1,y1,dz), iso(x0,y1,dz)
    left_face  = [A, D_, Dp, Ap]           # x = x0
    front_face = [A, B, Bp, Ap]            # y = y0
    top_face   = [Ap, Bp, Cp, Dp]
    ax.add_patch(MplPolygon(left_face,  closed=True, facecolor=shade(col, 0.72), edgecolor="#33415a", lw=0.6))
    ax.add_patch(MplPolygon(front_face, closed=True, facecolor=shade(col, 0.88), edgecolor="#33415a", lw=0.6))
    ax.add_patch(MplPolygon(top_face,   closed=True, facecolor=col,               edgecolor="#33415a", lw=0.6))
    for p in (A, B, D_, Ap, Bp, Cp, Dp): pts.append(p)
    tc = iso(x0 + dx/2, y0 + dy/2, dz)
    if dz >= 3:   # label only blocks tall enough to read
        ax.text(tc[0], tc[1], name, ha="center", va="center", fontsize=7, weight="bold", color="#12203a")

# paint far -> near (largest x+y first)
for b in sorted(boxes, key=lambda bb: (bb[0]+bb[2]/2) + (bb[1]+bb[3]/2), reverse=True):
    draw_box(b)

xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
ax.set_xlim(min(xs) - 5, max(xs) + 5); ax.set_ylim(min(ys) - 5, max(ys) + 8)
# height reference
ax.text(min(xs), max(ys) + 4, "Reserve racking uses ≈ 11.5 m of the 12.2 m clear height; "
        "floor operations (receiving, pack, ship) are low.", fontsize=8, color="#555", style="italic")
fig.savefig(os.path.join(FIGS, "layout_3d.png"), dpi=115, bbox_inches="tight")
plt.close(fig)

# ============================ 2D WORKER-MOVEMENT MODEL ============================
import matplotlib.patheffects as pe

fig, ax = plt.subplots(figsize=(13, 7.8))
ax.set_xlim(-3, L + 3); ax.set_ylim(-9, DEPTH + 7); ax.set_aspect("equal"); ax.axis("off")
ax.set_title("Option B — worker movement (zone picking)", fontsize=13, weight="bold")
ax.text(L/2, DEPTH + 3.2, "Each picker is confined to one zone → short, non-crossing travel; "
        "reach trucks handle putaway & replenishment; a handler runs pack → ship.",
        ha="center", fontsize=8.5, color="#555", style="italic")

# ---- context: all zones drawn faintly (no centre text), building outline + docks ----
Z = {}
def stack_bg(x0, w, items, top=DEPTH):
    y = top
    for name, area, col in items:
        h = area / w
        ax.add_patch(Rectangle((x0, y - h), w, h, facecolor=col, edgecolor="white", lw=1.2, alpha=0.28))
        Z[name] = (x0, x0 + w, y - h, y)
        y -= h
stack_bg(0, left_w, left)
stack_bg(left_w + aisle, core_w, core)
stack_bg(left_w + aisle + core_w + aisle, right_w, right)
ax.add_patch(Rectangle((0, 0), L, DEPTH, fill=False, edgecolor="#33415a", lw=1.6))
for ax0 in (left_w, left_w + aisle + core_w):
    ax.add_patch(Rectangle((ax0, 0), aisle, DEPTH, facecolor="#eef2fb", edgecolor="none", hatch="//", alpha=0.5))
for dx in np.arange(2, L, 8):
    ax.add_patch(Rectangle((dx, -1.6), 2.6, 1.6, facecolor="#33415a", edgecolor="none"))
ax.text(left_w/2, -3.9, "▲ RECEIVING docks", ha="center", fontsize=8, color="#33415a", weight="bold")
ax.text(L - right_w/2, -3.9, "SHIPPING docks ▲", ha="center", fontsize=8, color="#33415a", weight="bold")

cx0 = left_w + aisle; cx1 = cx0 + core_w; cmid = (cx0 + cx1) / 2
fast_top = Z["Selective + cantilever"][3]          # top of fast band (= bottom of reserve)
res_top = Z["Double-deep reserve (A/B)"][3]        # 70
recv, pack, shipz = Z["Receiving &\ninbound staging"], Z["Packing &\nconsolidation"], Z["Outbound staging\n& shipping"]

# ---- pick-zone tints + dashed boundaries (clearly separated, non-overlapping) ----
ax.add_patch(Rectangle((cx0, 0), core_w, fast_top, facecolor="#d97706", alpha=0.10, zorder=1))
ax.add_patch(Rectangle((cx0, fast_top), core_w/2, res_top - fast_top, facecolor="#7c3aed", alpha=0.10, zorder=1))
ax.add_patch(Rectangle((cmid, fast_top), core_w/2, res_top - fast_top, facecolor="#0891b2", alpha=0.10, zorder=1))
ax.plot([cx0, cx1], [fast_top, fast_top], ls=(0, (6, 4)), color="#94a3b8", lw=1.1, zorder=2)
ax.plot([cmid, cmid], [fast_top, res_top], ls=(0, (6, 4)), color="#94a3b8", lw=1.1, zorder=2)

def serp(lanes, lo, hi, axis="v", m=2.6):
    pts = []
    for i, c in enumerate(lanes):
        a, b = (lo + m, hi - m) if i % 2 == 0 else (hi - m, lo + m)
        pts += [(c, a), (c, b)] if axis == "v" else [(a, c), (b, c)]
    return pts

def wpath(pts, color, lw=2.6, min_seg=20):
    """Draw a route; arrowheads are centred on LONG travel segments only (never on connectors)."""
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    ln, = ax.plot(xs, ys, color=color, lw=lw, zorder=6, solid_capstyle="round", solid_joinstyle="round")
    ln.set_path_effects([pe.Stroke(linewidth=lw + 2.6, foreground="white"), pe.Normal()])
    ax.scatter([xs[0]], [ys[0]], s=48, color=color, edgecolor="white", lw=1.5, zorder=8)  # start ●
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        seg = math.hypot(x1 - x0, y1 - y0)
        if seg >= min_seg:
            mx, my = (x0 + x1)/2, (y0 + y1)/2; ux, uy = (x1 - x0)/seg, (y1 - y0)/seg
            ax.annotate("", xy=(mx + ux*1.6, my + uy*1.6), xytext=(mx - ux*1.6, my - uy*1.6),
                        zorder=8, arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=16))

def repl_arrow(x, y_from, y_to, color):
    """A single clearly-dashed replenishment shuttle with one arrowhead at the end."""
    ln, = ax.plot([x, x], [y_from, y_to], color=color, lw=2.2, zorder=6,
                  linestyle=(0, (6, 4)), solid_capstyle="round")
    ln.set_path_effects([pe.Stroke(linewidth=4.6, foreground="white"), pe.Normal()])
    ax.annotate("", xy=(x, y_to), xytext=(x, y_to + 3.2), zorder=8,
                arrowprops=dict(arrowstyle="-|>", color=color, lw=2.2, mutation_scale=15))

Z1, Z2, Z3, RT, DP = "#d97706", "#7c3aed", "#0891b2", "#16a34a", "#dc2626"
# pickers - each contained in its own zone (arrowheads only on the long travel lanes)
wpath(serp(np.linspace(3.5, 12.5, 3), cx0, cx1, axis="h"), Z1)                    # zone 1 fast/forward
wpath(serp(np.linspace(cx0 + 6, cmid - 6, 3), fast_top, res_top, axis="v"), Z2)  # zone 2 reserve-left
wpath(serp(np.linspace(cmid + 6, cx1 - 6, 3), fast_top, res_top, axis="v"), Z3)  # zone 3 reserve-right
# reach truck putaway: receiving -> reserve (single clean diagonal, one arrowhead)
wpath([((recv[0]+recv[1])/2, (recv[2]+recv[3])/2), (cx0 + 8, 52)], RT, min_seg=10)
# replenishment: two clearly-dashed shuttles reserve -> forward pick
repl_arrow(cx0 + core_w*0.36, fast_top + 7, fast_top - 6, RT)
repl_arrow(cx0 + core_w*0.64, fast_top + 7, fast_top - 6, RT)
# dispatch handler: pack -> shipping -> dock (single vertical, one arrowhead)
dcx = (shipz[0] + shipz[1]) / 2
wpath([(dcx, pack[3] - 4), (dcx, -1.4)], DP, min_seg=10)

# ---- labels (white boxes so they read over tints/lines) ----
def lbl(x, y, t, fs=8):
    ax.text(x, y, t, ha="center", va="center", fontsize=fs, weight="bold", color="#12203a",
            bbox=dict(boxstyle="round,pad=0.28", fc="white", ec="#cbd5e1", lw=0.8), zorder=9)
lbl(cx0 + core_w*0.5, fast_top - 1.5, "ZONE 1 · fast / forward pick")
lbl(cx0 + (cmid-cx0)*0.5, res_top - 3, "ZONE 2 · reserve (left)")
lbl(cmid + (cx1-cmid)*0.5, res_top - 3, "ZONE 3 · reserve (right)")
lbl((recv[0]+recv[1])/2, (recv[2]+recv[3])/2, "Receiving", 7.5)
lbl((Z["Offices &\namenities"][0]+Z["Offices &\namenities"][1])/2, (Z["Offices &\namenities"][2]+Z["Offices &\namenities"][3])/2, "Offices", 7.5)
lbl((Z["Returns / VAS"][0]+Z["Returns / VAS"][1])/2, (Z["Returns / VAS"][2]+Z["Returns / VAS"][3])/2, "Returns / VAS", 7)
lbl((pack[0]+pack[1])/2, pack[3] - 2.5, "Packing", 7.5)
lbl((shipz[0]+shipz[1])/2, shipz[2] + 3.5, "Shipping", 7.5)

handles = [
    Line2D([0], [0], color=Z1, lw=3, label="Picker · Zone 1 (fast / forward)"),
    Line2D([0], [0], color=Z2, lw=3, label="Picker · Zone 2 (reserve left)"),
    Line2D([0], [0], color=Z3, lw=3, label="Picker · Zone 3 (reserve right)"),
    Line2D([0], [0], color=RT, lw=3, label="Reach truck · putaway"),
    Line2D([0], [0], color=RT, lw=3, ls="--", label="Reach truck · replenishment"),
    Line2D([0], [0], color=DP, lw=3, label="Handler · pack → ship"),
    Line2D([0], [0], marker="o", color="w", markerfacecolor="#333", markeredgecolor="white",
           markersize=9, label="● start of route", lw=0),
]
ax.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, -0.145), ncol=4,
          fontsize=8, frameon=False, handlelength=2.4, columnspacing=1.6)
fig.savefig(os.path.join(FIGS, "layout_worker_flow.png"), dpi=120, bbox_inches="tight")
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
