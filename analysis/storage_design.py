"""
STORAGE - two simple figures for the reports (same style as the put-to-light wall figures).
  storage_where.png : WHERE goods are stored - the whole warehouse (north up, as the floor plan) with every storage
                      area lettered, the south-east corner enlarged (pallets drawn in the bays) and a key.
  storage_how.png   : HOW storing works - side views of a rack (put away, store) and of the fast-pick area
                      (refill from the back, pick from the front), with 4 numbered steps.
Positions come from geometry.py; counts from phase1_metrics.json (layout, picking.fast_pick, small_parts, dock_mhe).
Run after warehouse_floorplan.py, picking_plan.py and dock_mhe_plan.py.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, ConnectionPatch, Circle, Polygon
from matplotlib.lines import Line2D
from _util import save_fig, update_metrics
import layout_draw as D
from layout_draw import M, FP, INK, SUB, COL, letter, flow
from geometry import (DEPTH, L, left_w, right_w, rax, cx0, cx1, la, ra, fwd_h, rack_y0, rack_y1, cross_y, mod_x, BLOCK,
                      n_mod, aisle_x, aisle_w, rvh, lzh, uh, R_DOORS, PK_Y0, SHELF_Y0, FP_X0, FP_X1, FP_WALL_Y0,
                      FP_FLOW_Y0, FP_FLOW_D, FP_REFILL_Y0, FP_AISLE_Y, lvl_h, LEVELS, PITCH_M, top_beam)

LAY, SP, DM = M["layout"], M["picking"]["small_parts"], M["dock_mhe"]
LC = DM["load_checks"]
HL = "#d40011"                                                       # zoom frame
C_PUT, C_REFILL, C_PICK = "#2b6cb0", "#139a6a", "#eb6834"            # put away / refill / pick (as the order-flow figure)
assert LAY["levels"] == LEVELS


def plan(ax, detail):
    D.building(ax); D.zone_fills(ax)
    D.racks(ax, pallets=detail)
    D.fast_pick(ax, detail=detail)
    D.packing(ax, only_shelving=True)
    D.doors(ax, labels=not detail)


# ============================================================ FIGURE 1: where are goods stored?
fig = plt.figure(figsize=(11, 13.6))
axA = fig.add_axes([0.02, 0.475, 0.96, 0.47]); axK = fig.add_axes([0.03, 0.01, 0.56, 0.44]); axB = fig.add_axes([0.61, 0.01, 0.37, 0.44])
for a in (axA, axB, axK):
    a.axis("off")
plan(axA, detail=False)
axA.set_xlim(-6, L + 9); axA.set_ylim(-7, DEPTH + 4); axA.set_aspect("equal")
for x, y, t in [(left_w / 2, rvh / 2, "Receiving"), (left_w / 2, rvh + lzh / 2, "Container\nzone"),
                (left_w / 2, DEPTH - 250 / left_w - 180 / left_w / 2, "Returns"), (left_w / 2, DEPTH - 250 / left_w / 2, "Offices"),
                (rax + right_w / 2, uh / 2, "Outbound\nstaging"), (rax + right_w / 2, PK_Y0 + 9.5, "Packing")]:
    axA.text(x, y, t, ha="center", va="center", fontsize=9, color=SUB, weight="bold", zorder=4)
axA.text(-4.0, rvh / 2 + 2, "Receiving docks", ha="center", va="center", fontsize=9, color=SUB, rotation=90)
axA.text(L + 4.8, uh / 2, "Shipping docks", ha="center", va="center", fontsize=9, color=SUB, rotation=90)
# flows: put away (receiving -> left aisle -> middle cross-aisle -> storage aisle), refill (rack -> front cross-aisle)
y_ft = (fwd_h + rack_y0) / 2
flow(axA, [(left_w - 1.0, R_DOORS["R2"]), (la, R_DOORS["R2"]), (la, cross_y), (aisle_x[2], cross_y), (aisle_x[2], cross_y + 9)], C_PUT)
flow(axA, [(aisle_x[5], rack_y0 + 12), (aisle_x[5], y_ft), (aisle_x[5] + 4, y_ft), (aisle_x[5] + 4, FP_REFILL_Y0 + 0.9)], C_REFILL)
flow(axA, [(cx0 + 46, FP_AISLE_Y), (cx1 - 1.0, FP_AISLE_Y), (ra, FP_AISLE_Y), (ra, PK_Y0 - 1.5)], C_PICK, lw=2.6)
places_a = {"A": (cx0 + 9.0, FP_FLOW_Y0 + FP_FLOW_D / 2), "B": (D.wall_row_parts()["shelving"][0] + 8, FP_WALL_Y0 + 0.75),
            "C": (mod_x[3] + BLOCK / 2, (cross_y + rack_y1) / 2), "D": (mod_x[n_mod - 2] + BLOCK / 2, (cross_y + rack_y1) / 2),
            "E": (mod_x[n_mod - 1] + BLOCK / 2, (cross_y + rack_y1) / 2), "F": (rax + right_w / 2, SHELF_Y0 + 18.5),
            "G": (cx0 + 24, y_ft), "H": (cx0 + 18, FP_AISLE_Y)}
for ch, (x, y) in places_a.items():
    letter(axA, x, y, ch, r=1.25, fs=11.5)
zx0, zx1, zy0, zy1 = mod_x[n_mod - 3] - 2.9, cx1 + 0.8, -1.3, rack_y0 + 19.0
axA.add_patch(Rectangle((zx0, zy0), zx1 - zx0, zy1 - zy0, facecolor="none", edgecolor=HL, lw=2.6, zorder=10))
axA.text(zx0 + (zx1 - zx0) / 2, zy1 + 1.0, "enlarged in (b)", ha="center", va="bottom", fontsize=12, weight="bold", color=HL, zorder=10,
         bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=HL, lw=1.0))
axA.annotate("", xy=(L / 2 + 30, DEPTH + 2.5), xytext=(L / 2 + 30, DEPTH - 3.5), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.8))
axA.text(L / 2 + 30, DEPTH + 3.2, "N", ha="center", fontsize=10, weight="bold", color=INK)
axA.plot([2, 12], [-4.5, -4.5], color=INK, lw=2.2); axA.text(7, -6.6, "10 m", ha="center", fontsize=9.5, color=INK)
axA.set_title("(a) The whole warehouse — north is up, as on the floor plan", fontsize=13.5, weight="bold", color=INK, loc="left")

# (b) enlarged: south-east corner, pallets drawn
plan(axB, detail=True)
axB.set_xlim(zx0, zx1); axB.set_ylim(zy0, zy1); axB.set_aspect("equal")
axB.add_patch(Rectangle((zx0, zy0), zx1 - zx0, zy1 - zy0, facecolor="none", edgecolor=HL, lw=2.6, zorder=10, clip_on=False))
D.truck_top(axB, aisle_x[n_mod - 3], rack_y0 + 13.0, heading="W")                       # putting away in a storage aisle
D.truck_top(axB, aisle_x[n_mod - 3] + 4.6, y_ft + 0.25, heading="S")                     # refilling the lanes from the back
D.picker_top(axB, mod_x[n_mod - 2] + 1.0, FP_AISLE_Y, side="E")
flow(axB, [(aisle_x[n_mod - 3] - 0.9, rack_y0 + 7.5), (aisle_x[n_mod - 3] - 0.9, y_ft - 0.4), (aisle_x[n_mod - 3] + 2.6, y_ft - 0.4)],
     C_REFILL, lw=3.0)
for k, w in [(n_mod - 3, aisle_w[n_mod - 3]), (n_mod - 2, aisle_w[n_mod - 2])]:
    axB.text(aisle_x[k], rack_y0 + 17.2, f"{w:.1f} m\naisle", ha="center", va="center", fontsize=9, color=INK, zorder=9,
             bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.9))
places_b = {"A": (mod_x[n_mod - 1] + 0.9, FP_FLOW_Y0 + FP_FLOW_D / 2), "B": (FP_X1 - 4.5, FP_WALL_Y0 + 0.6),
            "C": (mod_x[n_mod - 3] + BLOCK / 2, rack_y0 + 4.2), "D": (mod_x[n_mod - 2] + BLOCK / 2, rack_y0 + 4.2),
            "E": (mod_x[n_mod - 1] + BLOCK / 2, rack_y0 + 4.2), "G": (zx0 + 1.6, y_ft), "H": (zx0 + 1.6, FP_AISLE_Y)}
for ch, (x, y) in places_b.items():
    letter(axB, x, y, ch, r=0.95)
axB.set_title("(b) Enlarged: fast-pick area and racks", fontsize=13.5, weight="bold", color=INK, loc="left")
axB.plot([zx1 - 5.6, zx1 - 0.6], [zy0 - 0.9, zy0 - 0.9], color=INK, lw=2, clip_on=False)
axB.text(zx1 - 3.1, zy0 - 2.3, "5 m", ha="center", fontsize=9.5, color=INK)
for (xa, ya), (xb, yb) in [((zx0, zy0), (zx0, zy1)), ((zx1, zy0), (zx1, zy1))]:
    fig.add_artist(ConnectionPatch(xyA=(xa, ya), coordsA=axA.transData, xyB=(xb, yb), coordsB=axB.transData,
                                   color=HL, lw=1.2, ls="--", alpha=0.7))
# key
std_pos = LAY["positions_standard"]
key = [("A", "Carton-flow lanes (fast-pick)", f"{FP['flow_lanes']} lanes for the {FP['skus_in_lanes']} most-picked fast movers "
                                              "(the busiest get two)"),
       ("B", "Wall row (fast-pick)", f"{FP['shelf_bays']} shelving bays, {FP['long_bays']} long-item shelves, "
                                     f"{FP['pallet_faces']} floor pallets for heavy items"),
       ("C", "Pallet racks", f"9 modules, {std_pos:,} pallet places, {LEVELS} levels high"),
       ("D", "Odd-items module", f"{LAY['positions_odd']:,} places for loads that are not a standard pallet"),
       ("E", "Long-goods module", f"{LAY['positions_long']} places for pallets up to 2.05 m, 3.2 m aisle"),
       ("F", "Small-parts shelving", f"{SP['shelf_bays']} bays of bins in the packing area ({SP['skus']:,} slow small items)"),
       ("G", "Front cross-aisle", "reach trucks drive here and refill the lanes from the back"),
       ("H", "Pick aisle", "pickers with trolleys; no reach trucks")]
axK.set_xlim(0, 1); axK.set_ylim(0, 1)
axK.text(0.0, 0.985, "Key — what is stored where", ha="left", va="center", fontsize=13.5, weight="bold", color=INK, transform=axK.transAxes)
for i, (ch, head, txt) in enumerate(key):
    y = 0.905 - i * 0.094
    axK.add_patch(Circle((0.035, y), 0.028, facecolor="white", edgecolor=INK, lw=1.5, transform=axK.transAxes))
    axK.text(0.035, y, ch, ha="center", va="center", fontsize=12, weight="bold", color=INK, transform=axK.transAxes)
    axK.text(0.09, y + 0.019, head, ha="left", va="center", fontsize=12.5, weight="bold", color=INK, transform=axK.transAxes)
    axK.text(0.09, y - 0.021, txt, ha="left", va="center", fontsize=10.8, color=SUB, transform=axK.transAxes)
axK.legend(handles=[Line2D([0], [0], color=C_PUT, lw=3.5, label="put away (reach truck)"),
                    Line2D([0], [0], color=C_REFILL, lw=3.5, label="refill the fast-pick lanes"),
                    Line2D([0], [0], color=C_PICK, lw=3.5, label="pickers to packing"),
                    Line2D([0], [0], marker="s", ls="", markerfacecolor="#f2b134", markeredgecolor="#9a6b12", markersize=11, label="reach truck"),
                    Line2D([0], [0], marker="o", ls="", markerfacecolor=C_PICK, markeredgecolor="white", markersize=11, label="picker + trolley")],
           loc="lower left", bbox_to_anchor=(0.0, -0.02), fontsize=11, frameon=False, ncol=2)
fig.suptitle("Where are goods stored?", fontsize=18, weight="bold", color=INK, x=0.02, ha="left", y=0.995)
save_fig(fig, "storage_where.png")


# ============================================================ FIGURE 2: how does storing work? (side views)
fig = plt.figure(figsize=(11, 8.0))
axL = fig.add_axes([0.005, 0.02, 0.405, 0.90]); axR = fig.add_axes([0.43, 0.575, 0.565, 0.345]); axC = fig.add_axes([0.43, 0.02, 0.565, 0.53])
for a in (axL, axR, axC):
    a.axis("off")


def person(ax, x, color, facing=1, h=1.75, y0=0.0, arm=0.0):
    s = h / 1.75
    ax.add_patch(Circle((x, y0 + 1.62 * s), 0.12 * s, facecolor=color, edgecolor="none", zorder=6))
    ax.add_patch(FancyBboxPatch((x - 0.14 * s, y0 + 0.85 * s), 0.28 * s, 0.62 * s, boxstyle="round,pad=0,rounding_size=0.08",
                                facecolor=color, edgecolor="none", zorder=6))
    ax.plot([x - 0.06 * s, x - 0.08 * s], [y0 + 0.88 * s, y0], color=color, lw=5, solid_capstyle="round", zorder=6)
    ax.plot([x + 0.06 * s, x + 0.08 * s], [y0 + 0.88 * s, y0], color=color, lw=5, solid_capstyle="round", zorder=6)
    ax.plot([x + 0.08 * s * facing, x + 0.45 * s * facing], [y0 + 1.36 * s, y0 + (1.25 + arm) * s], color=color, lw=4.5,
            solid_capstyle="round", zorder=6)


def load(ax, x, y, w, h, fc="#e9cf9b", ec="#b08a4e", z=3):
    ax.add_patch(Rectangle((x, y), w, 0.14, facecolor="#a47a45", edgecolor="none", zorder=z))          # pallet
    ax.add_patch(Rectangle((x + 0.03, y + 0.14), w - 0.06, h, facecolor=fc, edgecolor=ec, lw=0.7, zorder=z))


def reach_truck(ax, x_back, facing, fork_y, reach=0.0, cargo=True, cargo_h=1.0, z=5):
    """ETV-style reach truck from the side: chassis x_back .. x_back+1.8 (facing=+1 -> forks to the right)."""
    f = facing; x0 = x_back if f > 0 else x_back - 1.8
    ax.add_patch(FancyBboxPatch((x0, 0.12), 1.8, 0.55, boxstyle="round,pad=0,rounding_size=0.08", facecolor="#f2b134", edgecolor="#9a6b12", lw=1, zorder=z))
    for wx in (x0 + 0.3, x0 + 1.5):
        ax.add_patch(Circle((wx, 0.13), 0.13, facecolor=INK, zorder=z + 0.1))
    cab = x0 + 0.15 if f > 0 else x0 + 0.95
    ax.plot([cab, cab], [0.67, 2.25], color="#9a6b12", lw=2.4, zorder=z); ax.plot([cab + 0.7, cab + 0.7], [0.67, 2.25], color="#9a6b12", lw=2.4, zorder=z)
    ax.plot([cab - 0.05, cab + 0.75], [2.25, 2.25], color="#9a6b12", lw=3, zorder=z)                              # overhead guard
    person(ax, cab + 0.35, "#475569", facing=f, h=1.35, y0=0.67)
    mx = (x0 + 1.8 + 0.08) if f > 0 else (x0 - 0.08)                                                                # mast
    top = max(2.5, fork_y + 1.4)
    for dx in (0.0, 0.12 * f):
        ax.plot([mx + dx, mx + dx], [0.12, top], color="#6b7280", lw=3.2, zorder=z)
    fx = mx + 0.15 * f + reach * f                                                                                 # forks
    if reach:
        ax.plot([mx, fx], [fork_y + 0.5, fork_y + 0.5], color="#6b7280", lw=2.2, zorder=z)                          # reach (pantograph)
    ax.plot([fx, fx], [fork_y, fork_y + 0.9], color="#374151", lw=3, zorder=z + 0.2)
    ax.plot([fx, fx + 1.15 * f], [fork_y + 0.05, fork_y + 0.05], color="#374151", lw=3, zorder=z + 0.2)
    if cargo:
        load(ax, fx + (0.0 if f > 0 else -1.2), fork_y + 0.08, 1.2, cargo_h, z=z + 0.1)


# ---- left panel: a rack cut across (looking along the aisles)
ax = axL
ax.set_xlim(-3.55, 6.1); ax.set_ylim(-1.05, 13.95); ax.set_aspect("equal")
ax.plot([-3.4, 6.0], [0, 0], color=INK, lw=2)
ax.plot([-3.4, 6.0], [12.2, 12.2], color="#94a3b8", lw=1.2, ls="--")
ax.text(6.0, 12.35, "roof 12.2 m", ha="right", va="bottom", fontsize=10, color=SUB)
for xp in (0.0, 1.22, 1.38, 2.6):                                                                                  # uprights
    ax.plot([xp, xp], [0, top_beam + 0.25], color="#475569", lw=2.0, zorder=2)
heavy, tall = {0}, {LEVELS - 1}
import numpy as np
rng = np.random.default_rng(3)
for i, yb in enumerate(lvl_h):
    ax.plot([0.0, 1.22], [yb, yb], color="#e46b2b", lw=3.2, zorder=2.5)                                           # beams
    ax.plot([1.38, 2.6], [yb, yb], color="#e46b2b", lw=3.2, zorder=2.5)
    for xs in (0.03, 1.41):
        if i == 5 and xs == 0.03:
            continue                                                                                            # the truck is putting this one away
        h = 1.5 if i in tall else (0.95 + 0.2 * rng.random())
        fc = "#c9a46a" if i in heavy else ("#e9cf9b" if i < 7 else "#f1dcb2")
        load(ax, xs, yb + 0.06, 1.16, min(h, PITCH_M - 0.3) if i not in tall else h, fc=fc)
ax.add_patch(Rectangle((1.38, -0.02), 1.22, lvl_h[2] - 0.08, facecolor="#fde2d4", edgecolor="none", zorder=1.5))  # pick levels, east face
reach_truck(ax, -2.95, +1, lvl_h[5] + 0.02, reach=0.9, cargo=True, cargo_h=1.0)
person(ax, 3.35, C_PICK, facing=-1, arm=0.25)
ax.add_patch(Rectangle((4.0, 0.12), 1.0, 0.05, facecolor="#64748b", zorder=4))
for yy in (0.25, 0.75):
    ax.add_patch(Rectangle((4.05, yy), 0.9, 0.3, facecolor="#93c5fd", edgecolor="#2563eb", lw=0.8, zorder=4))
ax.plot([4.0, 4.0], [0.1, 1.2], color="#64748b", lw=2); ax.plot([5.0, 5.0], [0.1, 1.2], color="#64748b", lw=2)
# brackets and notes (right side of the rack)
def bracket(ax, x, y0, y1, text, color, side=1, fs=10.5):
    ax.plot([x, x + 0.12 * side, x + 0.12 * side, x], [y0, y0, y1, y1], color=color, lw=1.6, zorder=6)
    ax.text(x + 0.2 * side, (y0 + y1) / 2, text, ha="left" if side > 0 else "right", va="center", fontsize=fs, color=color,
            weight="bold", zorder=6, linespacing=1.15)
bracket(ax, 2.72, lvl_h[2], top_beam + 1.45, f"Levels 3–{LEVELS}:\nfull pallets\nin reserve\n(reach truck\nonly)", "#2b6cb0")
ax.text(4.4, lvl_h[1] + 1.05, "Levels 1–2:\npick places\nfor slow items", ha="center", va="bottom", fontsize=10.5, color=C_PICK,
        weight="bold", zorder=6, bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.9))
ax.annotate("", xy=(-0.3, top_beam), xytext=(-0.3, lvl_h[LEVELS - 2]),
            arrowprops=dict(arrowstyle="<|-|>", color=SUB, lw=1.2))
ax.text(-0.42, (top_beam + lvl_h[LEVELS - 2]) / 2, f"{PITCH_M:.2f} m", ha="right", va="center", fontsize=9.5, color=SUB)
ax.text(-0.42, top_beam + 0.05, f"top beam {top_beam:.1f} m", ha="right", va="bottom", fontsize=9.5, color=SUB)
ax.text(-0.42, 11.35, "tall loads (≤ 1.68 m)\non the top level", ha="right", va="center", fontsize=9.5, color=INK, zorder=6)
ax.text(1.3, -0.25, "heavy pallets\non the lowest level", ha="center", va="top", fontsize=9.5, color=INK)
for x0_, x1_, t in [(-3.0, 0.0, "3.0 m aisle"), (2.6, 5.6, "3.0 m aisle")]:
    ax.text((x0_ + x1_) / 2, -0.75, t, ha="center", va="center", fontsize=10, color=SUB)
ax.text(1.3, 13.3, "Pallet rack (cut across)", ha="center", va="bottom", fontsize=12.5, weight="bold", color="#3b5bdb")
ax.text(1.3, 13.2, "one pallet each side, back to back", ha="center", va="top", fontsize=9.5, color=SUB)

# ---- right panel: fast-pick area cut north-south (north on the left, south wall on the right)
ax = axR
X = lambda y_plan: 7.4 - y_plan                                                      # plan y (m from the south wall) -> panel x
ax.set_xlim(-3.25, 7.75); ax.set_ylim(-0.55, 3.45); ax.set_aspect("equal")
ax.plot([-3.2, 7.45], [0, 0], color=INK, lw=2)
ax.add_patch(Rectangle((7.42, 0), 0.25, 3.0, facecolor="#cbd5e1", edgecolor="none"))                                # south wall
xr, xf = X(FP_REFILL_Y0), X(FP_FLOW_Y0)                                                                            # rear / front of the lanes
for xp in (xr, xf):
    ax.plot([xp, xp], [0, 2.15], color="#475569", lw=2, zorder=2)
for k in range(5):                                                                                                 # 5 sloping levels
    yf_, yr_ = 0.35 + k * 0.38, 0.5 + k * 0.38
    ax.plot([xr, xf], [yr_, yf_], color="#2f855a", lw=2.6, zorder=3)
    for j in range(4):
        t = (j + 0.5) / 4
        cx_ = xr + t * (xf - xr); cy_ = yr_ + t * (yf_ - yr_)
        ax.add_patch(Rectangle((cx_ - 0.17, cy_ + 0.02), 0.34, 0.22, facecolor="#d6a77a", edgecolor="#9a6b4f", lw=0.6, zorder=4))
# refill strip: pallet put down by the reach truck, the driver slides cases in at the back
load(ax, X(fwd_h) + 0.06, 0.0, 0.9, 0.85, z=3)
person(ax, xr - 0.3, C_REFILL, facing=1, arm=0.1)
reach_truck(ax, -3.1, +1, 0.12, cargo=False)
ax.annotate("", xy=(xr + 0.25, 1.62), xytext=(xr - 0.15, 1.62), arrowprops=dict(arrowstyle="-|>", color=C_REFILL, lw=2.2))
# pick aisle: picker + trolley; wall row: shelf
person(ax, xf + 0.45, C_PICK, facing=-1, arm=0.0)
ax.add_patch(Rectangle((xf + 1.0, 0.12), 1.0, 0.05, facecolor="#64748b", zorder=4))
for yy in (0.25, 0.75):
    ax.add_patch(Rectangle((xf + 1.05, yy), 0.9, 0.3, facecolor="#93c5fd", edgecolor="#2563eb", lw=0.8, zorder=4))
ax.plot([xf + 1.0, xf + 1.0], [0.1, 1.2], color="#64748b", lw=2); ax.plot([xf + 2.0, xf + 2.0], [0.1, 1.2], color="#64748b", lw=2)
xs0, xs1 = X(FP_WALL_Y0 + 0.6), X(FP_WALL_Y0)
for xp in (xs0, xs1):
    ax.plot([xp, xp], [0, 2.1], color="#475569", lw=2, zorder=2)
for k in range(7):
    yy = 0.12 + k * 0.3
    ax.plot([xs0, xs1], [yy, yy], color="#6b85d6", lw=2, zorder=3)
    if k < 6:
        ax.add_patch(Rectangle((xs0 + 0.08, yy + 0.02), 0.44, 0.18, facecolor="#c7d2fe", edgecolor="#6b85d6", lw=0.5, zorder=4))
for x0_, x1_, t, c in [(-3.2, X(fwd_h), "CROSS-AISLE\n(reach truck)", "#92400e"), (X(fwd_h), xr, "REFILL", C_REFILL),
                       (xr, xf, "CARTON\nFLOW", "#2f855a"), (xf, X(FP_WALL_Y0 + 1.2), "PICK AISLE", C_PICK),
                       (X(FP_WALL_Y0 + 1.2), 7.45, "WALL\nROW", "#3b5bdb")]:
    ax.text((x0_ + x1_) / 2, 2.95, t, ha="center", va="center", fontsize=10.5, weight="bold", color=c, linespacing=1.05)
    ax.plot([x1_, x1_], [0.02, 2.3], color="#e5e7eb", lw=0.8, ls=":", zorder=1)
ax.text((xr + xf) / 2, -0.32, "cases roll to the front", ha="center", va="center", fontsize=9.5, color="#2f855a")
ax.text(2.0, 3.45, "Fast-pick area (cut north–south)", ha="center", va="bottom", fontsize=12.5, weight="bold", color="#2f855a")

# ---- step cards
ax = axC
ax.set_xlim(0, 1); ax.set_ylim(0, 1)
cards = [(1, C_PUT, "Put away", "A pallet comes in and is scanned.\nThe system gives it a place: fast\nmovers' stock near the front, heavy\npallets low, tall loads on top. The\nreach truck drives it there."),
         (2, C_PUT, "Store", f"Full pallets wait on levels 3–{LEVELS}.\nThe two lowest levels are pick\nplaces for slow items, so pickers\nnever need a lift."),
         (3, C_REFILL, "Refill", "A lane runs low: the reach truck\nbrings a pallet of that item to the\nback of the lane. The driver slides\nthe cases in; they roll to the front."),
         (4, C_PICK, "Pick", "The picker walks the pick aisle\nwith a trolley: lanes on one side,\nshelves on the other. No reach\ntrucks in this aisle.")]
for i, (n, c, head, txt) in enumerate(cards):
    x0 = 0.0 + (i % 2) * 0.505; y0 = 0.51 - (i // 2) * 0.51
    ax.add_patch(FancyBboxPatch((x0, y0), 0.495, 0.48, boxstyle="round,pad=0,rounding_size=0.02", facecolor="#f8fafc",
                                edgecolor=c, lw=1.5, transform=ax.transAxes))
    ax.add_patch(Circle((x0 + 0.05, y0 + 0.40), 0.033, facecolor="white", edgecolor=c, lw=2.2, transform=ax.transAxes, zorder=3))
    ax.text(x0 + 0.05, y0 + 0.40, str(n), ha="center", va="center", fontsize=13, weight="bold", color=c, transform=ax.transAxes, zorder=4)
    ax.text(x0 + 0.105, y0 + 0.40, head, ha="left", va="center", fontsize=13.5, weight="bold", color=c, transform=ax.transAxes)
    ax.text(x0 + 0.025, y0 + 0.195, txt, ha="left", va="center", fontsize=10.6, color=INK, transform=ax.transAxes, linespacing=1.3)
fig.suptitle("How storing works", fontsize=17, weight="bold", color=INK, x=0.02, ha="left", y=0.985)
save_fig(fig, "storage_how.png")

update_metrics("storage_design", {"fast_pick": FP, "levels": LEVELS, "top_beam_m": round(float(top_beam), 2)})
print("Saved storage_where.png and storage_how.png")
