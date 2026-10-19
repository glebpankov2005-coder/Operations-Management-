"""
CAD-style detailed warehouse FLOOR PLAN for Option B — actual rack rows & aisles
drawn to scale, numbered dock doors, dimension lines, title block, scale bar and
north arrow. Rendered natively (matplotlib). Output: outputs/figures/layout_floorplan.png
"""
import os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch
import matplotlib.font_manager as fm
from _util import FIGS, REPORTS

def _font():
    for f in ["Segoe UI", "Calibri", "Arial", "DejaVu Sans"]:
        if any(f.lower() == x.name.lower() for x in fm.fontManager.ttflist):
            return f
    return "DejaVu Sans"
plt.rcParams.update({"font.family": _font()})
INK, SUB, STEEL = "#1f2937", "#6b7280", "#33415a"
M = json.load(open(os.path.join(REPORTS, "phase1_metrics.json"), encoding="utf-8"))
POS = M["capacity"]["design_positions_target"]

# ---- footprint / columns: single source = geometry.py (content-derived widths from volume-based areas) ----
from geometry import (DEPTH, RECV, OFF, RET, PACK, OUTB, FWD, LOOSE, dd_area, sel_area, CIRC,
                      left_w, right_w, core_w, aisle, L, cx0, cx1, rax, LEVELS,
                      PK_Y0, PW_X0, PW_DEPTH, PW_LEN, PW_Y0, BENCH_X0, BENCH_W, N_BENCH, CAGE_X0, SHELF_Y0,
                      R_DOORS, FP_AISLE_Y, FP_REFILL_Y0)
import layout_draw as D
TOTAL_AREA = RECV + OFF + RET + LOOSE + PACK + OUTB + FWD + dd_area + sel_area + CIRC

fig, ax = plt.subplots(figsize=(15.5, 9))
ax.set_facecolor("#f7f9fc")
ax.set_xlim(-9, L + 9); ax.set_ylim(-15.5, DEPTH + 10); ax.set_aspect("equal"); ax.axis("off")

# building slab
ax.add_patch(FancyBboxPatch((1, -1), L, DEPTH, boxstyle="round,pad=0,rounding_size=1.5",
             facecolor="#8a94a6", edgecolor="none", alpha=0.15, zorder=0.4))
ax.add_patch(Rectangle((0, 0), L, DEPTH, facecolor="#ffffff", edgecolor=STEEL, lw=2.2, zorder=0.6))
# structural grid columns (subtle)
for gx in np.arange(0, L + 1, L / 6):
    for gy in np.arange(0, DEPTH + 1, DEPTH / 3):
        ax.add_patch(Rectangle((gx - 0.35, gy - 0.35), 0.7, 0.7, facecolor="#cbd5e1", edgecolor="none", zorder=0.7))

def soft_zone(x0, y0, w, h, color, name, sub=None, label_y=None):
    """Zone background; the label sits at label_y (default: centre) on a white tag so the zone's inside stays visible."""
    ax.add_patch(FancyBboxPatch((x0, y0), w, h, boxstyle="round,pad=0,rounding_size=0.6",
                 facecolor=color, edgecolor="white", lw=1.4, alpha=0.9, zorder=1.2))
    if not name:
        return
    ly = y0 + h / 2 if label_y is None else label_y
    ax.text(x0 + w / 2, ly, f"{name}\n{sub}" if sub else name, ha="center", va="center", fontsize=7, weight="bold",
            color=INK, zorder=3.5, linespacing=1.1, bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.88))

# ---- left support column: offices (top), returns, loose-container zone, receiving (bottom, dock side) ----
oh, rh, rvh, lzh = OFF/left_w, RET/left_w, RECV/left_w, LOOSE/left_w
soft_zone(0.4, DEPTH-oh, left_w-0.8, oh-0.4, "#cfd6e2", "Offices\n& amenities", f"{OFF} m²")
soft_zone(0.4, DEPTH-oh-rh, left_w-0.8, rh-0.2, "#e6bcd8", "Returns", f"{RET} m²", label_y=DEPTH-oh-2.6)
soft_zone(0.4, rvh+0.2, left_w-0.8, lzh-0.4, "#f6dfb6", "Container zone", f"{LOOSE} m²", label_y=rvh+10.15)
soft_zone(0.4, 0.4, left_w-0.8, rvh-0.4, "#f4c98c", "Receiving", f"{RECV} m²", label_y=rvh-2.1)
D.receiving(ax, z=2.2, lent=True); D.container_zone(ax, z=2.2); D.returns(ax, z=2.2)
# ---- right column: packing (top), outbound (bottom, dock side) ----
ph, uh = PACK/right_w, OUTB/right_w
soft_zone(rax+0.4, DEPTH-ph+0.2, right_w-0.8, ph-0.6, "#f7d4d4", "")
# packing internals (geometry.py): put-to-light wall, pack stations, roll cages, small-parts shelving
C_WALL, C_BENCH, C_CAGE, C_SHELF = "#1d4ed8", "#e59a7a", "#9fdcbf", "#b9cbf3"
n_rows = 12
for r_ in range(n_rows):
    y_ = SHELF_Y0 + r_ * 2.2
    ax.add_patch(Rectangle((rax + 0.9, y_), right_w - 1.8, 1.2, facecolor=C_SHELF, edgecolor="white", lw=0.4, zorder=2.5))
ax.add_patch(Rectangle((PW_X0, PW_Y0), PW_DEPTH, PW_LEN, facecolor=C_WALL, edgecolor="none", zorder=2.6))
for i_ in range(N_BENCH):
    ax.add_patch(Rectangle((BENCH_X0, PW_Y0 + i_ * PW_LEN / N_BENCH + 0.35), BENCH_W, PW_LEN / N_BENCH - 0.7,
                           facecolor=C_BENCH, edgecolor="white", lw=0.4, zorder=2.6))
for i_ in range(7):
    for j_ in range(2):
        ax.add_patch(Rectangle((CAGE_X0 + j_ * 1.3, PW_Y0 + i_ * 1.5 + 0.2), 1.0, 1.1, facecolor=C_CAGE,
                               edgecolor="white", lw=0.4, zorder=2.6))
ax.text(rax + right_w / 2, (PW_Y0 + PW_LEN + SHELF_Y0) / 2, f"Packing · {PACK} m²", ha="center", va="center",
        fontsize=7.2, weight="bold", color=INK, zorder=3, bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.9))
soft_zone(rax+0.4, 0.4, right_w-0.8, uh-0.2, "#f4c98c", "Outbound", f"{OUTB} m²", label_y=uh/2 + 2.15)   # between lanes S3 / S4
D.outbound(ax, z=2.2)
from matplotlib.patches import Patch
pack_handles = [Patch(facecolor=D.COL["flow"], label="Carton-flow lanes (fast-pick)"),
                Patch(facecolor=D.COL["shelf"], label="Shelving (fast-pick, small parts)"),
                Patch(facecolor=D.COL["fp_pal"], label="Floor pallets, heavy fast movers"),
                Patch(facecolor=C_WALL, label=f"Put-to-light wall ({M['picking']['putwall']['slots']} slots)"),
                Patch(facecolor=C_BENCH, label="Pack stations"), Patch(facecolor=C_CAGE, label="Roll cages per carrier"),
                Patch(facecolor=D.COL["conveyor"], label="Roller conveyor (containers)"),
                Patch(facecolor=D.COL["pallet"], edgecolor=D.COL["pallet_edge"], label="Pallet places (lanes, build spots)")]

# ---- storage core: forward-pick band (bottom) + double-deep reserve racks ----
fwd_h = FWD / core_w
# forward-pick module (carton flow / shelving) - fine horizontal lanes
ax.add_patch(Rectangle((cx0, 0), core_w, fwd_h, facecolor="#dff3e6", edgecolor="#74cf9a", lw=1.2, zorder=1.5))
D.fast_pick(ax, z=1.7)                     # refill strip | carton-flow lanes | pick aisle | wall row (geometry.py)
ax.text(cx0 + core_w * 0.36, FP_AISLE_Y, f"FAST-PICK AREA  (best-sellers)  ·  {FWD} m²",
        ha="center", va="center", fontsize=7.5, weight="bold", color="#2f855a", zorder=3,
        bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.9))

# reserve racks: single-deep back-to-back blocks (one pallet each side) + aisles, with a central cross-aisle
END_AISLE = 3.2                        # front + rear cross-aisles: every storage aisle open at BOTH ends (no U-turns)
rack_y0, rack_y1 = fwd_h + END_AISLE, DEPTH - END_AISLE
cross_y0, cross_y1 = (rack_y0+rack_y1)/2 - 1.6, (rack_y0+rack_y1)/2 + 1.6
runs = [(rack_y0, cross_y0), (cross_y1, rack_y1)]
from geometry import BLOCK, AISLEW, pitch, n_mod, start, mod_x, aisle_w, LONG_BAY, LONG_PER_BAY, LONG_AISLE
sel_from = n_mod - 2                 # module 10 = odd / irregular items, module 11 = long goods (4.5 m bays)
aisle_no = 1
BAY, PAL_PER_BAY = 2.7, 3            # 2.7 m bay holds 3 EUR pallets (800 mm side to the aisle)
bays_per_row = sum(int((y1 - y0) // BAY) for (y0, y1) in runs)
long_bays_per_row = sum(int((y1 - y0) // LONG_BAY) for (y0, y1) in runs)
positions_per_module = 2 * bays_per_row * PAL_PER_BAY * LEVELS
positions_long = 2 * long_bays_per_row * LONG_PER_BAY * LEVELS
positions_odd = positions_per_module
positions_total = (n_mod - 1) * positions_per_module + positions_long
for m in range(n_mod):
    bx = mod_x[m]
    is_sel = m >= sel_from
    fill = "#c3d2fb" if is_sel else "#8aa4fb"
    edge = "#6d8bfa"
    for (y0, y1) in runs:
        ax.add_patch(Rectangle((bx, y0), BLOCK, y1-y0, facecolor=fill, edgecolor=edge, lw=1.0, zorder=2))
        ax.plot([bx+BLOCK/2, bx+BLOCK/2], [y0, y1], color="white", lw=0.8, zorder=2.1)  # back-to-back split
        bay_ = LONG_BAY if m == n_mod - 1 else BAY
        for by in np.arange(y0+bay_, y1, bay_):                                          # bay divisions
            ax.plot([bx, bx+BLOCK], [by, by], color="white", lw=0.5, alpha=0.8, zorder=2.1)
    # aisle number at top
    if m < n_mod - 1:                                                                   # 10 storage aisles
        ax.text(bx + BLOCK + aisle_w[m] / 2, rack_y1 + 0.7, f"A{aisle_no}", ha="center", fontsize=6, color=SUB, zorder=3)
        aisle_no += 1
# cross aisle label
ax.text(cx0 + core_w/2, (cross_y0+cross_y1)/2, "middle cross-aisle", ha="center", va="center",
        fontsize=7, style="italic", color=SUB, zorder=3,
        bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.8))
for yy_, lab in [((fwd_h + rack_y0) / 2, "front cross-aisle (3.2 m)"), (DEPTH - 1.0, "rear cross-aisle (3.2 m)")]:
    ax.text(cx0 + core_w * 0.72, yy_, lab, ha="center", va="center", fontsize=6.5, style="italic", color=SUB,
            zorder=3, bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.8))
# zone captions over racks
ax.text(cx0 + (sel_from*pitch)/2, rack_y1 - 3, "SINGLE-DEEP PALLET RACKS, BACK-TO-BACK (main storage)  ·  3,505 m²",
        ha="center", fontsize=8.5, weight="bold", color="#3b5bdb", zorder=3,
        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.85))
ax.text(mod_x[sel_from] + pitch * 0.95, rack_y0 + 8, "ODD ITEMS +\nLONG GOODS\n(4.5 m bays)", ha="center",
        fontsize=7, weight="bold", color="#3b5bdb", rotation=0, zorder=3,
        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.85))

# ---- dock doors on the side walls (sized in dock_mhe_plan.py: 3 inbound, 5 outbound) ----
# A trailer door needs ~4.3 m of wall: the 9.9 m receiving / 9.5 m outbound columns are too narrow on the
# south wall, so receiving docks sit on the WEST wall and shipping docks on the EAST wall (straight-through flow).
DOOR_PITCH = 4.3
def docks_side(x_wall, y_centre, n, prefix, outside):
    ys_ = y_centre + (np.arange(n) - (n - 1) / 2) * DOOR_PITCH
    x0 = x_wall - 2.3 if outside == "left" else x_wall + 0.6
    for i, dy in enumerate(ys_, 1):
        ax.add_patch(FancyBboxPatch((x0, dy - 1.5), 1.7, 3.0, boxstyle="round,pad=0,rounding_size=0.3",
                     facecolor=STEEL, edgecolor="white", lw=0.8, zorder=12))      # above flow arrows
        ax.text(x0 + 0.85, dy, f"{prefix}{i}", ha="center", va="center", fontsize=5.6, color="white",
                weight="bold", zorder=13, rotation=90)
    return ys_
# R1 = container dock beside the loose-container zone; R2-R3 = palletised trailers beside receiving
in_doors = np.concatenate([docks_side(0, R_DOORS["R1"], 1, "R", "left"), np.array([R_DOORS["R2"], R_DOORS["R3"]])])
for i, dy in enumerate(in_doors[1:], 2):
    ax.add_patch(FancyBboxPatch((-2.3, dy - 1.5), 1.7, 3.0, boxstyle="round,pad=0,rounding_size=0.3",
                 facecolor=STEEL, edgecolor="white", lw=0.8, zorder=12))
    ax.text(-1.45, dy, f"R{i}", ha="center", va="center", fontsize=5.6, color="white", weight="bold", zorder=13, rotation=90)
out_doors = docks_side(L, uh / 2, 5, "S", "right")
ax.text(-4.9, (rvh + lzh) / 2, "RECEIVING docks  (R1 = container)", ha="center", va="center", rotation=90,
        fontsize=7.2, color=STEEL, weight="bold")
ax.text(L + 5.4, out_doors[3], "SHIPPING docks", ha="center", va="center", rotation=90,
        fontsize=7.6, color=STEEL, weight="bold")

# ---- dimension lines ----
def dim_h(x0, x1, y, text):
    ax.annotate("", xy=(x1, y), xytext=(x0, y), arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=1.2))
    for xx in (x0, x1):
        ax.plot([xx, xx], [y-0.8, y+0.8], color=INK, lw=1.0)
    ax.text((x0+x1)/2, y+1.2, text, ha="center", va="bottom", fontsize=8, color=INK)
def dim_v(y0, y1, x, text):
    ax.annotate("", xy=(x, y1), xytext=(x, y0), arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=1.2))
    for yy in (y0, y1):
        ax.plot([x-0.8, x+0.8], [yy, yy], color=INK, lw=1.0)
    ax.text(x-1.4, (y0+y1)/2, text, ha="right", va="center", fontsize=8, color=INK, rotation=90)
dim_h(0, L, DEPTH + 4.5, f"{L:.0f} m")
dim_v(0, DEPTH, -6.5, f"{DEPTH:.0f} m")

# ---- scale bar + north arrow ----
ax.plot([L - 44, L - 34], [-2.6, -2.6], color=INK, lw=2.4)                 # scale bar above the title block
for xx in (L - 44, L - 34):
    ax.plot([xx, xx], [-3.2, -2.0], color=INK, lw=2.4)
ax.text(L - 32.5, -2.6, "10 m", ha="left", va="center", fontsize=8, color=INK)
ax.annotate("", xy=(L+4, DEPTH-2), xytext=(L+4, DEPTH-8), arrowprops=dict(arrowstyle="-|>", color=INK, lw=2.2))
ax.text(L+4, DEPTH-0.5, "N", ha="center", fontsize=11, weight="bold", color=INK)

# ---- title block (bottom-right, text above the box via zorder) ----
tb_w, tb_h = 46, 8.85
tb_x, tb_y = L - tb_w, -14.4
ax.add_patch(Rectangle((tb_x, tb_y), tb_w, tb_h, facecolor="white", edgecolor=STEEL, lw=1.3, zorder=6))
ax.add_patch(Rectangle((tb_x, tb_y+tb_h-1.6), tb_w, 1.6, facecolor="#eef1f7", edgecolor=STEEL, lw=1.0, zorder=6.1))
ax.text(tb_x+tb_w/2, tb_y+tb_h-0.8, "Project OTM — Assa Abloy @ DHL Bemmel", ha="center", va="center",
        fontsize=7.6, weight="bold", color=INK, zorder=7)
rows = [("DRAWING", "Option B — warehouse floor plan (rack-level)"),
        ("POSITIONS", f"{positions_total:,} single-deep  ·  target ~9,500"),
        ("DOCKS / MHE", "3 in (W) · 5 out (E) · ETV 216i, EJE 120i, ERE 225"),
        ("SCALE / SIZE", f"~1:400  ·  {L:.0f} × {DEPTH:.0f} m = {TOTAL_AREA:,} m²  ({TOTAL_AREA / 7000:.0%})"),
        ("DATE / REV", "2026  ·  Rev C (zone insides, fast-pick faces)")]
for i, (k, v) in enumerate(rows):
    yy = tb_y + tb_h - 2.6 - i*1.25
    ax.text(tb_x+1.2, yy, k, fontsize=6.3, weight="bold", color=SUB, va="center", zorder=7)
    ax.text(tb_x+12, yy, v, fontsize=7, color=INK, va="center", zorder=7)

title_txt = ax.text(L/2, DEPTH + 8, "Option B — Warehouse Floor Plan (rack-level, to scale)",
                    ha="center", fontsize=15, weight="bold", color=INK)

ax.legend(handles=pack_handles, loc="lower left", bbox_to_anchor=(0.0, 0.0), ncol=2, fontsize=7.5, frameon=False,
          title="Inside the zones", title_fontsize=8, alignment="left")
fig.savefig(os.path.join(FIGS, "layout_floorplan.png"), dpi=130, bbox_inches="tight")
print(f"Saved layout_floorplan.png  ({n_mod} rack modules, {positions_total:,} positions, building {L:.0f}x{DEPTH:.0f} m)")

# =================== Fig 8: SAME floor plan + order/returns/cross-dock flow overlay ===================
from matplotlib.lines import Line2D
BLUE, GREEN, REDD, PURPLE, GREY = "#2b6cb0", "#2f855a", "#d40011", "#7c3aed", "#64748b"
la = left_w + aisle/2; ra = cx1 + aisle/2
recv_cx, recv_cy = left_w/2, rvh/2
ret_cx = left_w/2
ret_cy = DEPTH - oh - rh/2
pack_cx, pack_cy = rax + right_w/2, DEPTH - ph/2
out_cx, out_cy = rax + right_w/2, uh/2
aisleA2 = mod_x[1] + BLOCK + AISLEW/2

import matplotlib.patheffects as pe
from matplotlib.path import Path
LW = 5.0
def route(pts, color):
    """Bold flow arrow along a polyline routed through OPEN space (doors, perimeter aisles,
    cross-aisle, storage aisles) - never across a rack. One patch: rounded corners, crisp head."""
    path = Path(pts, [Path.MOVETO] + [Path.LINETO] * (len(pts) - 1))
    a = FancyArrowPatch(path=path, arrowstyle="-|>,head_length=0.55,head_width=0.24", mutation_scale=26,
                        color=color, lw=LW, joinstyle="round", capstyle="round", zorder=8)
    a.set_path_effects([pe.Stroke(linewidth=LW + 2.6, foreground="white"), pe.Normal()])
    ax.add_patch(a)
def badge(x, y, n, color):
    ax.scatter([x], [y], s=330, color="white", edgecolor=color, lw=2.6, zorder=10)
    ax.text(x, y, str(n), ha="center", va="center", fontsize=10, weight="bold", color=color, zorder=11)

cd_y = (cross_y0 + cross_y1) / 2
aisle_c = [mod_x[k] + BLOCK + aisle_w[k] / 2 for k in range(n_mod - 1)]
x_ref = aisle_c[3]                                     # storage aisle A4 (open channel) for the refill run
pk_y = PW_Y0 + PW_LEN / 2                              # pickers arrive at the PICK side of the put-to-light wall
x5 = CAGE_X0 + 1.15                                    # packed orders leave the roll cages for outbound staging

# ---- main flow 1-6 : In -> put away -> refill -> pick -> pack -> out ----
route([(-1.45, in_doors[1]), (left_w * 0.62, in_doors[1])], BLUE)                      # 1 in through R2 (pallets)
badge(left_w * 0.18, in_doors[1], 1, BLUE)
ORANGE = "#d97706"                                                                     # loose container: R1 -> zone -> receiving
route([(-1.45, in_doors[0]), (left_w * 0.72, in_doors[0])], ORANGE)                      # C: container -> conveyor
badge(left_w * 0.18, in_doors[0], "C", ORANGE)
route([(left_w - 0.6, in_doors[1]), (la, in_doors[1]), (la, cd_y), (start + 7.0, cd_y)], BLUE)   # 2 up left aisle, into cross-aisle
badge(la, cd_y - 4.0, 2, BLUE)
route([(x_ref, cd_y + 10), (x_ref, FP_REFILL_Y0 + 0.9)], GREEN)                        # 3 reserve -> back of the fast-pick lanes
badge(x_ref, cd_y - 8, 3, GREEN)
route([(cx1 - 11, FP_AISLE_Y), (ra, FP_AISLE_Y), (ra, pk_y), (PW_X0 - 0.3, pk_y)], REDD)  # 4 pick aisle -> right aisle -> put-wall
badge(ra, (fwd_h + pk_y) / 2, 4, REDD)
route([(x5, PW_Y0 + 0.4), (x5, uh - 4.2)], REDD)                                       # 5 pack -> outbound
badge(x5, PK_Y0 + 2.4, 5, REDD)
route([(rax + 1.2, out_doors[1]), (L + 4.5, out_doors[1])], REDD)                      # 6 out through S2
badge(out_cx, out_doors[1], 6, REDD)

# flow legend (boxed, below the plan)
ax.set_ylim(-21, DEPTH + 10)
handles = [Line2D([0], [0], color=ORANGE, lw=5, label="C  Loose container: unpack, build pallets"),
           Line2D([0], [0], color=BLUE, lw=5, label="1–2  In & put away"),
           Line2D([0], [0], color=GREEN, lw=5, label="3  Refill the fast-pick area"),
           Line2D([0], [0], color=REDD, lw=5, label="4–6  Pick → put-wall & pack → out")] + pack_handles
leg = ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 0.02), ncol=3, fontsize=9,
                frameon=True, fancybox=True, borderpad=0.8, columnspacing=1.6, handlelength=2.6)
leg.get_frame().set_edgecolor("#9db4fb"); leg.get_frame().set_linewidth(1.2)
title_txt.set_text("Option B — Layout, Zoning & Order Flow (on the floor plan)")
fig.savefig(os.path.join(FIGS, "layout_orderflow.png"), dpi=130, bbox_inches="tight")
plt.close(fig)
print("Saved layout_orderflow.png")

# ---- layout metrics (single source for the reports) ----
from _util import update_metrics
zones = [("Receiving & inbound staging", RECV), ("Loose-container zone (unpack & palletise)", LOOSE),
         ("Offices & amenities", OFF), ("Returns / VAS", RET),
         ("Single-deep pallet racks (A/B/C reserve)", dd_area), ("Odd-item + long-goods modules", sel_area),
         ("Fast-pick area (carton-flow / shelving)", FWD), ("Packing & consolidation", PACK),
         ("Outbound staging & shipping", OUTB), ("Circulation / aisles", CIRC)]
update_metrics("layout", {
    "building_L_m": round(L, 1), "building_depth_m": DEPTH, "total_area_m2": int(TOTAL_AREA),
    "pct_of_7000": round(TOTAL_AREA / 7000 * 100, 0), "fits_7000": bool(TOTAL_AREA <= 7000),
    "zones": [{"Zone": z, "Area m2": int(a), "% of building": f"{a / TOTAL_AREA:.0%}"} for z, a in zones],
    "rack_modules": int(n_mod), "storage_aisles": int(n_mod - 1), "levels": int(LEVELS),
    "bays_per_row": int(bays_per_row), "long_bays_per_row": int(long_bays_per_row), "positions_total": int(positions_total),
    "positions_standard": int(positions_total - positions_odd - positions_long), "positions_odd": int(positions_odd),
    "positions_long": int(positions_long), "positions_odd_long": int(positions_odd + positions_long),
    "long_aisle_m": LONG_AISLE, "positions_12th_module": int(positions_per_module),
    "positions_target": 9500, "rack_type": "single-deep, back-to-back", "loose_zone_m2": int(LOOSE),
    "dd_area_m2": int(dd_area), "sel_area_m2": int(sel_area),
})
