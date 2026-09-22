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

# ---- footprint / columns (content-derived widths; from volume-based areas) ----
DEPTH = 70.0
RECV, OFF, RET, PACK, OUTB, FWD = 262, 250, 180, 450, 216, 500
dd_area, sel_area = 3505, 728
CIRC = 450
left_w = (OFF + RET + RECV) / DEPTH
right_w = (PACK + OUTB) / DEPTH
core_w = (dd_area + sel_area + FWD) / DEPTH
aisle = CIRC / (2 * DEPTH)
L = left_w + aisle + core_w + aisle + right_w
cx0 = left_w + aisle
cx1 = cx0 + core_w
rax = cx1 + aisle                      # right block x0

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

def soft_zone(x0, y0, w, h, color, name, sub=None):
    ax.add_patch(FancyBboxPatch((x0, y0), w, h, boxstyle="round,pad=0,rounding_size=0.6",
                 facecolor=color, edgecolor="white", lw=1.4, alpha=0.9, zorder=2))
    ax.text(x0 + w/2, y0 + h/2 + (1.0 if sub else 0), "\n".join(name.split(" & ")) if w < 12 else name,
            ha="center", va="center", fontsize=8, weight="bold", color=INK, zorder=3)
    if sub:
        ax.text(x0 + w/2, y0 + h/2 - 1.8, sub, ha="center", va="center", fontsize=6.8, color=SUB, zorder=3)

# ---- left support column: offices (top), returns, receiving (bottom, dock side) ----
oh, rh, rvh = OFF/left_w, RET/left_w, RECV/left_w
soft_zone(0.4, DEPTH-oh, left_w-0.8, oh-0.4, "#cfd6e2", "Offices & amenities", f"{OFF} m²")
soft_zone(0.4, DEPTH-oh-rh, left_w-0.8, rh-0.2, "#e6bcd8", "Returns", f"{RET} m²")
soft_zone(0.4, 0.4, left_w-0.8, rvh-0.4, "#f4c98c", "Receiving & staging", f"{RECV} m²")
# ---- right column: packing (top), outbound (bottom, dock side) ----
ph, uh = PACK/right_w, OUTB/right_w
soft_zone(rax+0.4, DEPTH-ph+0.2, right_w-0.8, ph-0.6, "#f2a7a7", "Packing & consolidation", f"{PACK} m²")
soft_zone(rax+0.4, 0.4, right_w-0.8, uh-0.2, "#f4c98c", "Outbound & shipping", f"{OUTB} m²")

# ---- storage core: forward-pick band (bottom) + double-deep reserve racks ----
fwd_h = FWD / core_w
# forward-pick module (carton flow / shelving) - fine horizontal lanes
ax.add_patch(Rectangle((cx0, 0), core_w, fwd_h, facecolor="#dff3e6", edgecolor="#74cf9a", lw=1.2, zorder=1.5))
for yy in np.arange(0.8, fwd_h, 1.6):
    ax.plot([cx0+0.5, cx1-0.5], [yy, yy], color="#74cf9a", lw=0.7, alpha=0.7, zorder=1.6)
ax.text(cx0 + core_w/2, fwd_h/2, "FAST-PICK AREA  (best-sellers)  ·  500 m²",
        ha="center", va="center", fontsize=8, weight="bold", color="#2f855a", zorder=3,
        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.85))

# reserve racks: vertical double-deep blocks + aisles, with a central cross-aisle
rack_y0, rack_y1 = fwd_h + 1.5, DEPTH - 1.5
cross_y0, cross_y1 = (rack_y0+rack_y1)/2 - 1.6, (rack_y0+rack_y1)/2 + 1.6
runs = [(rack_y0, cross_y0), (cross_y1, rack_y1)]
BLOCK, AISLEW = 2.6, 3.0            # double-deep block (2 rows) + reach aisle
pitch = BLOCK + AISLEW
n_mod = int((core_w - AISLEW) // pitch)
start = cx0 + (core_w - (n_mod*pitch - AISLEW)) / 2
sel_from = n_mod - 2                 # last 2 modules = selective + cantilever
aisle_no = 1
for m in range(n_mod):
    bx = start + m*pitch
    is_sel = m >= sel_from
    fill = "#c3d2fb" if is_sel else "#8aa4fb"
    edge = "#6d8bfa"
    for (y0, y1) in runs:
        ax.add_patch(Rectangle((bx, y0), BLOCK, y1-y0, facecolor=fill, edgecolor=edge, lw=1.0, zorder=2))
        ax.plot([bx+BLOCK/2, bx+BLOCK/2], [y0, y1], color="white", lw=0.8, zorder=2.1)  # double-deep split
        for by in np.arange(y0+2.7, y1, 2.7):                                            # bay divisions
            ax.plot([bx, bx+BLOCK], [by, by], color="white", lw=0.5, alpha=0.8, zorder=2.1)
    # aisle number at top
    if m < n_mod:
        ax.text(bx + BLOCK + AISLEW/2, rack_y1 + 1.4, f"A{aisle_no}", ha="center", fontsize=6, color=SUB, zorder=3)
        aisle_no += 1
# cross aisle label
ax.text(cx0 + core_w/2, (cross_y0+cross_y1)/2, "cross-aisle", ha="center", va="center",
        fontsize=7, style="italic", color=SUB, zorder=3,
        bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.8))
# zone captions over racks
ax.text(cx0 + (sel_from*pitch)/2, rack_y1 - 3, "TWO-DEEP PALLET RACKS (main storage)  ·  3,505 m²",
        ha="center", fontsize=8.5, weight="bold", color="#3b5bdb", zorder=3,
        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.85))
ax.text(start + (sel_from+0.9)*pitch, rack_y0 + 8, "RACKS FOR\nODD / LONG\nITEMS · 728 m²", ha="center",
        fontsize=7, weight="bold", color="#3b5bdb", rotation=0, zorder=3,
        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.85))

# ---- dock doors (numbered) ----
def docks(x_start, x_end, n, label):
    xs = np.linspace(x_start, x_end, n)
    for i, dx in enumerate(xs, 1):
        ax.add_patch(FancyBboxPatch((dx-1.3, -2.2), 2.6, 1.7, boxstyle="round,pad=0,rounding_size=0.3",
                     facecolor=STEEL, edgecolor="none", zorder=4))
        ax.text(dx, -1.35, str(i), ha="center", va="center", fontsize=6, color="white", weight="bold", zorder=5)
    ax.text((x_start+x_end)/2, -4.2, label, ha="center", fontsize=8.5, color=STEEL, weight="bold")
docks(1.5, left_w-0.5, 3, "▲ RECEIVING docks")
docks(rax+0.5, L-1.5, 3, "SHIPPING docks ▲")

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
ax.plot([2, 12], [-9.5, -9.5], color=INK, lw=2.4)
for xx in (2, 12):
    ax.plot([xx, xx], [-10.1, -8.9], color=INK, lw=2.4)
ax.text(7, -11.3, "10 m", ha="center", fontsize=8, color=INK)
ax.annotate("", xy=(L+4, DEPTH-2), xytext=(L+4, DEPTH-8), arrowprops=dict(arrowstyle="-|>", color=INK, lw=2.2))
ax.text(L+4, DEPTH-0.5, "N", ha="center", fontsize=11, weight="bold", color=INK)

# ---- title block (bottom-right, text above the box via zorder) ----
tb_w, tb_h = 46, 7.6
tb_x, tb_y = L - tb_w, -13.2
ax.add_patch(Rectangle((tb_x, tb_y), tb_w, tb_h, facecolor="white", edgecolor=STEEL, lw=1.3, zorder=6))
ax.add_patch(Rectangle((tb_x, tb_y+tb_h-1.6), tb_w, 1.6, facecolor="#eef1f7", edgecolor=STEEL, lw=1.0, zorder=6.1))
ax.text(tb_x+tb_w/2, tb_y+tb_h-0.8, "Project OTM — Assa Abloy @ DHL Bemmel", ha="center", va="center",
        fontsize=7.6, weight="bold", color=INK, zorder=7)
rows = [("DRAWING", "Option B — warehouse floor plan (rack-level)"),
        ("POSITIONS", "target ~9,500 (peak 8,512 ÷ 0.90) · racking gives growth headroom"),
        ("SCALE / SIZE", f"~1:400  ·  {L:.0f} × {DEPTH:.0f} m = 6,541 m²  (93%)"),
        ("DATE / REV", "2026  ·  Draft A")]
for i, (k, v) in enumerate(rows):
    yy = tb_y + tb_h - 2.6 - i*1.25
    ax.text(tb_x+1.2, yy, k, fontsize=6.3, weight="bold", color=SUB, va="center", zorder=7)
    ax.text(tb_x+12, yy, v, fontsize=7, color=INK, va="center", zorder=7)

title_txt = ax.text(L/2, DEPTH + 8, "Option B — Warehouse Floor Plan (rack-level, to scale)",
                    ha="center", fontsize=15, weight="bold", color=INK)

fig.savefig(os.path.join(FIGS, "layout_floorplan.png"), dpi=130, bbox_inches="tight")
print(f"Saved layout_floorplan.png  ({n_mod} rack modules, building {L:.0f}x{DEPTH:.0f} m)")

# =================== Fig 8: SAME floor plan + order/returns/cross-dock flow overlay ===================
from matplotlib.lines import Line2D
BLUE, GREEN, REDD, PURPLE, GREY = "#2b6cb0", "#2f855a", "#d40011", "#7c3aed", "#64748b"
la = left_w + aisle/2; ra = cx1 + aisle/2
recv_cx, recv_cy = left_w/2, rvh/2
ret_cx = left_w/2
ret_cy = DEPTH - oh - rh/2
pack_cx, pack_cy = rax + right_w/2, DEPTH - ph/2
out_cx, out_cy = rax + right_w/2, uh/2
aisleA2 = start + pitch + BLOCK + AISLEW/2

def farrow(p0, p1, color, ls="-", rad=0.0, lw=2.6):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=16, color=color,
                 lw=lw, linestyle=ls, connectionstyle=f"arc3,rad={rad}", zorder=8))
def badge(x, y, n, color):
    ax.scatter([x], [y], s=190, color="white", edgecolor=color, lw=2.0, zorder=10)
    ax.text(x, y, str(n), ha="center", va="center", fontsize=8.5, weight="bold", color=color, zorder=11)

# forward flow 1-6
farrow((recv_cx, -0.6), (recv_cx, 6), BLUE); badge(recv_cx, 8.5, 1, BLUE)
farrow((left_w-0.5, recv_cy+3), (cx0+9, rack_y0+7), BLUE, rad=-0.18); badge(la, rack_y0+4, 2, BLUE)
farrow((aisleA2, rack_y0), (aisleA2, fwd_h+0.8), GREEN, ls=(0, (5, 3))); badge(aisleA2+3.2, (rack_y0+fwd_h)/2, 3, GREEN)
farrow((cx1, fwd_h*0.5), (rax, pack_cy-6), REDD, rad=-0.18); badge(ra, fwd_h+9, 4, REDD)
farrow((pack_cx, DEPTH-ph+2), (out_cx, uh+1), REDD); badge(ra, uh+7, 5, REDD)
farrow((out_cx, uh*0.4), (out_cx, -0.6), REDD); badge(ra, 5, 6, REDD)
# returns 7-9
farrow((recv_cx, rvh-1), (ret_cx, DEPTH-oh-rh+3), PURPLE); badge(recv_cx+3.2, rvh+1.5, 7, PURPLE)
farrow((left_w-0.5, ret_cy+1), (cx0+9, ret_cy+11), PURPLE, rad=-0.15); badge(la, ret_cy+9, 8, PURPLE)
farrow((0.7, ret_cy-5), (-3.0, ret_cy-5), PURPLE, ls=(0, (4, 3)), lw=1.9); badge(2.6, ret_cy-5, 9, PURPLE)
ax.text(-3.4, ret_cy-8, "scrap /\nRTV", ha="left", fontsize=7, color=PURPLE, style="italic")
# cross-dock via the main cross-aisle (open channel across the core)
cd_y = (cross_y0 + cross_y1)/2
farrow((left_w, cd_y), (rax, cd_y), GREY, ls=(0, (2, 2)), lw=1.7)

# flow legend (row along the bottom)
ax.set_ylim(-21, DEPTH + 10)
handles = [Line2D([0],[0], color=BLUE, lw=3, label="1–2  Goods in & put away"),
           Line2D([0],[0], color=GREEN, lw=3, ls="--", label="3  Refill the fast-pick area"),
           Line2D([0],[0], color=REDD, lw=3, label="4–6  Pick → pack → ship"),
           Line2D([0],[0], color=PURPLE, lw=3, label="7–9  Returns handling"),
           Line2D([0],[0], color=GREY, lw=2, ls=":", label="Straight-through goods (no storage)")]
ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.02), ncol=5,
          fontsize=8.2, frameon=False)
title_txt.set_text("Option B — Layout, Zoning & Order Flow (on the floor plan)")
fig.savefig(os.path.join(FIGS, "layout_orderflow.png"), dpi=130, bbox_inches="tight")
plt.close(fig)
print("Saved layout_orderflow.png")
