"""
PUT-TO-LIGHT WALL - two simple figures for the reports.
  putwall_where.png : WHERE it is - the whole warehouse (north up, same as the floor plan) with the spot marked,
                      and an enlarged view of that spot with lettered places (A-H) and a key.
  putwall_how.png   : HOW it works - a side view of the wall: pick side on the left, pack side on the right, 4 steps.
Positions come from geometry.py (same as the floor plan); sizes from picking_plan.py (slots, totes per order).
Run after picking_plan.py and warehouse_floorplan.py.
"""
import json, os
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, ConnectionPatch, Circle
from matplotlib.lines import Line2D
from _util import save_fig, update_metrics, REPORTS
from geometry import (DEPTH, L, left_w, right_w, rax, cx0, cx1, ra, fwd_h, rack_y0, rack_y1, cross_y, mod_x, BLOCK, n_mod,
                      OFF, RET, rvh, lzh, uh, PK_Y0, PW_X0, PW_DEPTH, PW_LEN, PW_Y0, BENCH_X0, BENCH_W,
                      N_BENCH, CAGE_X0, SHELF_Y0, R_DOORS, S_DOORS, FP_AISLE_Y)
import layout_draw as D

M = json.load(open(os.path.join(REPORTS, "phase1_metrics.json"), encoding="utf-8"))
PK = M["picking"]; PW = PK["putwall"]; SP = PK["small_parts"]
assert abs(PW["length_m"] - PW_LEN) < 0.01, "geometry.PW_LEN must match the wall sized in picking_plan.py"

INK, SUB, STEEL = "#1f2937", "#6b7280", "#33415a"
C_WALL, C_BENCH, C_CAGE, C_SHELF = "#1d4ed8", "#e59a7a", "#9fdcbf", "#b9cbf3"
C_PICK, C_PACK, C_LIGHT = "#eb6834", "#139a6a", "#eda100"
HL = "#d40011"                                                           # highlight (zoom frame)


def draw_plan(ax, detail):
    """Warehouse in metres, north up (same coordinates as the floor plan). detail=True adds people and trolleys."""
    ax.add_patch(Rectangle((0, 0), L, DEPTH, facecolor="white", edgecolor=STEEL, lw=1.6, zorder=0.5))
    oh, rh = OFF / left_w, RET / left_w
    zones = [(0, 0, left_w, rvh, "#f4c98c", "Receiving"), (0, rvh, left_w, lzh, "#f6dfb6", "Container\nzone"),
             (0, DEPTH - oh - rh, left_w, rh, "#e6bcd8", "Returns"), (0, DEPTH - oh, left_w, oh, "#cfd6e2", "Offices"),
             (cx0, 0, cx1 - cx0, fwd_h, "#dff3e6", ""),
             (rax, 0, right_w, uh, "#f4c98c", "Outbound\nstaging"), (rax, PK_Y0, right_w, DEPTH - PK_Y0, "#f7d4d4", "")]
    for x, y, w, h, c, name in zones:
        ax.add_patch(Rectangle((x + 0.3, y + 0.3), w - 0.6, h - 0.6, facecolor=c, edgecolor="none", zorder=1))
        if name and not detail:
            ax.text(x + w / 2, y + h / 2, name, ha="center", va="center", fontsize=10, weight="bold", color=INK, zorder=3)
    for m in range(n_mod):                                               # pallet racks: two runs per module
        for (y0, y1) in [(rack_y0, cross_y - 1.6), (cross_y + 1.6, rack_y1)]:
            ax.add_patch(Rectangle((mod_x[m], y0), BLOCK, y1 - y0, facecolor="#c3d0f7", edgecolor="#8aa4fb", lw=0.5, zorder=1))
    if not detail:
        ax.text((cx0 + cx1) / 2, (rack_y0 + rack_y1) / 2, "PALLET RACKS", ha="center", va="center", fontsize=12,
                weight="bold", color="#3b5bdb", zorder=3, bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.9))
    # packing internals (geometry.py)
    for r_ in range(12):
        ax.add_patch(Rectangle((rax + 0.9, SHELF_Y0 + r_ * 2.2), right_w - 1.8, 1.2, facecolor=C_SHELF, edgecolor="white", lw=0.4, zorder=2))
    ax.add_patch(Rectangle((PW_X0, PW_Y0), PW_DEPTH, PW_LEN, facecolor=C_WALL, edgecolor="none", zorder=3))
    for i in range(N_BENCH):
        ax.add_patch(Rectangle((BENCH_X0, PW_Y0 + i * PW_LEN / N_BENCH + 0.35), BENCH_W, PW_LEN / N_BENCH - 0.7,
                               facecolor=C_BENCH, edgecolor="white", lw=0.5, zorder=2))
    for i in range(7):
        for j in range(2):
            ax.add_patch(Rectangle((CAGE_X0 + j * 1.3, PW_Y0 + i * 1.5 + 0.2), 1.0, 1.1, facecolor=C_CAGE, edgecolor="white", lw=0.5, zorder=2))
    ax.add_patch(Rectangle((rax + 0.5, PK_Y0 + 0.6), 4.0, 3.8, facecolor="#fde7b0", edgecolor="none", zorder=2))   # large-order pallets
    ax.add_patch(Rectangle((rax + 5.2, PK_Y0 + 0.6), 2.2, 2.2, facecolor="#d1d5db", edgecolor="none", zorder=2))   # stretch wrapper
    D.fast_pick(ax, z=1.5)                                               # carton flow, pick aisle, wall row
    if not detail:
        ax.text((cx0 + cx1) / 2 - 12, FP_AISLE_Y, "Fast-pick area", ha="center", va="center", fontsize=10, weight="bold",
                color=INK, zorder=3, bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))
    D.doors(ax, labels=False)                                            # R1-R3 west, S1-S5 east (geometry.py)
    if detail:                                                           # people and trolleys in the enlarged view
        for yy in (PW_Y0 + 1.0, PW_Y0 + 2.6, PW_Y0 + 7.5):
            ax.add_patch(Rectangle((rax + 0.5, yy), 1.0, 0.6, facecolor="#fde2d4", edgecolor=C_PICK, lw=1.0, zorder=4))
        for (x, y, c) in [(PW_X0 - 0.45, PW_Y0 + 5.0, C_PICK), (PW_X0 + PW_DEPTH + 0.75, PW_Y0 + 2.0, C_PACK),
                          (PW_X0 + PW_DEPTH + 0.75, PW_Y0 + 6.6, C_PACK)]:
            ax.add_patch(Circle((x, y), 0.42, facecolor=c, edgecolor="white", lw=1.2, zorder=6))


def letter(ax, x, y, ch):
    ax.add_patch(Circle((x, y), 0.95, facecolor="white", edgecolor=INK, lw=1.5, zorder=8))
    ax.text(x, y, ch, ha="center", va="center", fontsize=12, weight="bold", color=INK, zorder=9)


def flow(ax, pts, color, lw=3.2):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=color, lw=lw, solid_capstyle="round", solid_joinstyle="round", zorder=7)
    ax.annotate("", xy=pts[-1], xytext=pts[-2], arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=16), zorder=7)


# ============================================================ FIGURE 1: where is it?
fig = plt.figure(figsize=(11, 13.2))
axA = fig.add_axes([0.02, 0.45, 0.96, 0.49]); axK = fig.add_axes([0.03, 0.01, 0.60, 0.40]); axB = fig.add_axes([0.64, 0.01, 0.34, 0.40])
for a in (axA, axB, axK):
    a.axis("off")
# (a) whole warehouse
draw_plan(axA, detail=False)
axA.set_xlim(-6, L + 9); axA.set_ylim(-7, DEPTH + 4); axA.set_aspect("equal")
axA.text(-4.0, rvh / 2 + 2, "Receiving\ndocks", ha="center", va="center", fontsize=9, color=SUB, rotation=90)
axA.text(L + 4.8, uh / 2, "Shipping\ndocks", ha="center", va="center", fontsize=9, color=SUB, rotation=90)
axA.text(rax + right_w / 2, SHELF_Y0 + 13, "Packing\narea", ha="center", va="center", fontsize=10, weight="bold", color=INK, zorder=4,
         bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.9))
zx0, zx1, zy0, zy1 = ra - 2.0, L + 0.8, PK_Y0 - 6.5, SHELF_Y0 + 5.5
axA.add_patch(Rectangle((zx0, zy0), zx1 - zx0, zy1 - zy0, facecolor="none", edgecolor=HL, lw=2.6, zorder=10))
axA.text(zx0 - 1.0, zy1 + 1.2, "put-to-light wall\nis here", ha="right", va="bottom", fontsize=13, weight="bold", color=HL, zorder=10,
         bbox=dict(boxstyle="round,pad=0.25", fc="white", ec=HL, lw=1.0))
flow(axA, [(cx1 - 14, FP_AISLE_Y), (ra, FP_AISLE_Y), (ra, PW_Y0 + 5.0), (PW_X0 - 0.4, PW_Y0 + 5.0)], C_PICK)
flow(axA, [(CAGE_X0 + 1.15, PW_Y0 - 0.2), (CAGE_X0 + 1.15, uh - 3.0)], C_PACK)
axA.annotate("", xy=(L / 2 + 30, DEPTH + 2.5), xytext=(L / 2 + 30, DEPTH - 3.5), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.8))
axA.text(L / 2 + 30, DEPTH + 3.2, "N", ha="center", fontsize=10, weight="bold", color=INK)
axA.plot([2, 12], [-4.5, -4.5], color=INK, lw=2.2); axA.text(7, -6.6, "10 m", ha="center", fontsize=9.5, color=INK)
axA.set_title("(a) The whole warehouse — north is up, as on the floor plan", fontsize=13.5, weight="bold", color=INK, loc="left")
# (b) enlarged view
draw_plan(axB, detail=True)
axB.set_xlim(zx0, zx1); axB.set_ylim(zy0, zy1); axB.set_aspect("equal")
axB.add_patch(Rectangle((zx0, zy0), zx1 - zx0, zy1 - zy0, facecolor="none", edgecolor=HL, lw=2.6, zorder=10, clip_on=False))
flow(axB, [(ra, zy0 + 0.6), (ra, PW_Y0 + 5.0), (PW_X0 - 0.95, PW_Y0 + 5.0)], C_PICK, lw=3.6)
flow(axB, [(CAGE_X0 + 1.15, PW_Y0 - 0.2), (CAGE_X0 + 1.15, zy0 + 0.8)], C_PACK, lw=3.6)
places = {"A": (PW_X0 + PW_DEPTH / 2, PW_Y0 + PW_LEN + 1.4), "B": (rax + 1.0, PW_Y0 + PW_LEN - 1.6),
          "C": (BENCH_X0 + BENCH_W / 2, PW_Y0 + PW_LEN + 1.4), "D": (CAGE_X0 + 1.15, PW_Y0 + PW_LEN + 1.4),
          "E": (rax + right_w / 2, SHELF_Y0 + 3.3), "F": (rax + 2.5, PK_Y0 + 2.5), "G": (rax + right_w / 2, zy0 + 3.0),
          "H": (ra, PW_Y0 + 9.0)}
for ch, (x, y) in places.items():
    letter(axB, x, y, ch)
axB.set_title("(b) Enlarged", fontsize=13.5, weight="bold", color=INK, loc="left")
axB.plot([zx1 - 5.6, zx1 - 0.6], [zy0 - 0.9, zy0 - 0.9], color=INK, lw=2, clip_on=False)
axB.text(zx1 - 3.1, zy0 - 2.3, "5 m", ha="center", fontsize=9.5, color=INK)
for (xa, ya), (xb, yb) in [((zx0, zy0), (zx0, zy1)), ((zx1, zy0), (zx1, zy1))]:     # box bottom corners -> enlarged view top corners
    fig.add_artist(ConnectionPatch(xyA=(xa, ya), coordsA=axA.transData, xyB=(xb, yb), coordsB=axB.transData,
                                   color=HL, lw=1.2, ls="--", alpha=0.7))
# key
key = [("A", "Put-to-light wall", f"{PW['columns']} × {PW['levels']} = {PW['slots']} slots, {PW['length_m']} m long, open on both sides"),
       ("B", "Pick side", "pickers park trolleys here; the putter fills the slots"),
       ("C", "Pack side + 4 pack stations", "packers take finished orders out of the wall and pack them"),
       ("D", "Roll cages", "one per carrier: each carton goes into its carrier's cage"),
       ("E", "Small-parts shelving", f"{SP['shelf_bays']} bays of small slow parts, right behind the wall"),
       ("F", "Large-order pallets", "big orders are picked onto a pallet and skip the wall"),
       ("G", "Outbound staging", "cages and pallets wait for their truck (doors S1–S5)"),
       ("H", "Right perimeter aisle", "pickers arrive here from the fast-pick area and the racks")]
axK.set_xlim(0, 1); axK.set_ylim(0, 1)
axK.text(0.0, 0.985, "Key to the enlarged view (b)", ha="left", va="center", fontsize=13.5, weight="bold", color=INK, transform=axK.transAxes)
for i, (ch, head, txt) in enumerate(key):
    y = 0.90 - i * 0.092
    axK.add_patch(Circle((0.035, y), 0.028, facecolor="white", edgecolor=INK, lw=1.5, transform=axK.transAxes))
    axK.text(0.035, y, ch, ha="center", va="center", fontsize=12, weight="bold", color=INK, transform=axK.transAxes)
    axK.text(0.09, y + 0.017, head, ha="left", va="center", fontsize=12.5, weight="bold", color=INK, transform=axK.transAxes)
    axK.text(0.09, y - 0.022, txt, ha="left", va="center", fontsize=11, color=SUB, transform=axK.transAxes)
axK.legend(handles=[Line2D([0], [0], color=C_PICK, lw=3.5, label="pickers bring full trolleys"),
                    Line2D([0], [0], color=C_PACK, lw=3.5, label="packed orders go to the trucks"),
                    Line2D([0], [0], marker="o", ls="", markerfacecolor=C_PICK, markeredgecolor="white", markersize=11, label="putter (1 per wave)"),
                    Line2D([0], [0], marker="o", ls="", markerfacecolor=C_PACK, markeredgecolor="white", markersize=11, label="packers (2–4)")],
           loc="lower left", bbox_to_anchor=(0.0, -0.01), fontsize=11.5, frameon=False, ncol=2)
fig.suptitle("Where is the put-to-light wall?", fontsize=18, weight="bold", color=INK, x=0.02, ha="left", y=0.995)
save_fig(fig, "putwall_where.png")

# ============================================================ FIGURE 2: how does it work? (side view)
fig, ax = plt.subplots(figsize=(11, 6.4))
fig.subplots_adjust(left=0.01, right=0.99, top=0.93, bottom=0.01)
ax.set_xlim(-4.6, 5.4); ax.set_ylim(-1.75, 3.05); ax.set_aspect("equal"); ax.axis("off")
ax.plot([-4.5, 5.3], [0, 0], color=INK, lw=2)
ax.add_patch(Rectangle((-4.5, -0.08), 9.8, 0.08, facecolor="#e5e7eb", edgecolor="none"))


def person(x, color, facing=1):
    ax.add_patch(Circle((x, 1.66), 0.13, facecolor=color, edgecolor="none", zorder=5))
    ax.add_patch(FancyBboxPatch((x - 0.15, 0.88), 0.30, 0.62, boxstyle="round,pad=0,rounding_size=0.1", facecolor=color, edgecolor="none", zorder=5))
    ax.plot([x - 0.07, x - 0.09], [0.9, 0.0], color=color, lw=6, solid_capstyle="round", zorder=5)
    ax.plot([x + 0.07, x + 0.09], [0.9, 0.0], color=color, lw=6, solid_capstyle="round", zorder=5)
    ax.plot([x + 0.1 * facing, x + 0.42 * facing], [1.38, 1.18], color=color, lw=5, solid_capstyle="round", zorder=5)   # arm


def tote(x, y, w=0.5, h=0.26, c="#93c5fd", ec="#2563eb"):
    ax.add_patch(Rectangle((x, y), w, h, facecolor=c, edgecolor=ec, lw=1.0, zorder=4))


# trolley (pick side)
tx0 = -3.9
for yy in (0.25, 0.75, 1.25):
    ax.add_patch(Rectangle((tx0, yy), 1.1, 0.05, facecolor="#64748b", zorder=3))
    tote(tx0 + 0.04, yy + 0.05); tote(tx0 + 0.56, yy + 0.05)
ax.plot([tx0, tx0], [0.12, 1.45], color="#64748b", lw=2.5); ax.plot([tx0 + 1.1, tx0 + 1.1], [0.12, 1.45], color="#64748b", lw=2.5)
ax.plot([tx0 + 1.1, tx0 + 1.35], [1.45, 1.55], color="#64748b", lw=2.5)
for wx in (tx0 + 0.12, tx0 + 0.98):
    ax.add_patch(Circle((wx, 0.08), 0.08, facecolor=INK, zorder=4))
# the wall: 5 slots, each with an order tote; lights on both faces
for i in range(5):
    y0 = 0.2 + i * 0.36
    ax.add_patch(Rectangle((0, y0), 0.6, 0.36, facecolor="#eef2ff", edgecolor=C_WALL, lw=1.6, zorder=3))
    if i != 4:
        tote(0.05, y0 + 0.03, w=0.5, h=0.27)
    put_c = C_LIGHT if i == 2 else "#cbd5e1"
    pack_c = C_PACK if i == 1 else "#cbd5e1"
    ax.add_patch(Rectangle((-0.11, y0 + 0.12), 0.1, 0.12, facecolor=put_c, edgecolor="none", zorder=5))
    ax.add_patch(Rectangle((0.61, y0 + 0.12), 0.1, 0.12, facecolor=pack_c, edgecolor="none", zorder=5))
ax.text(-0.06, 0.2 + 2 * 0.36 + 0.18, "2", ha="center", va="center", fontsize=8, weight="bold", color=INK, zorder=6)
ax.add_patch(Rectangle((0, 0), 0.6, 0.2, facecolor=C_WALL, zorder=3))
# people
person(-1.0, C_PICK, facing=1)
person(1.55, C_PACK, facing=1)
# pack bench + roll cage (pack side)
ax.add_patch(Rectangle((2.2, 0.88), 1.35, 0.08, facecolor="#9a6b4f", zorder=3))
ax.plot([2.28, 2.28], [0, 0.88], color="#9a6b4f", lw=3); ax.plot([3.47, 3.47], [0, 0.88], color="#9a6b4f", lw=3)
ax.add_patch(Rectangle((2.45, 0.96), 0.55, 0.36, facecolor="#d6a77a", edgecolor="#9a6b4f", lw=1, zorder=4))     # carton
ax.add_patch(Rectangle((3.1, 0.96), 0.3, 0.25, facecolor="#475569", zorder=4))                                   # label printer
ax.add_patch(Rectangle((3.95, 0.05), 1.05, 1.6, facecolor="none", edgecolor="#475569", lw=1.8, zorder=3))      # roll cage
for k in range(1, 5):
    ax.plot([3.95 + k * 0.21, 3.95 + k * 0.21], [0.05, 1.65], color="#94a3b8", lw=0.8, zorder=3)
for (cx_, cy_) in [(4.05, 0.1), (4.5, 0.1), (4.05, 0.5), (4.5, 0.5), (4.25, 0.9)]:
    ax.add_patch(Rectangle((cx_, cy_), 0.42, 0.38, facecolor="#d6a77a", edgecolor="#9a6b4f", lw=0.8, zorder=4))
# zone headings
for x, t, c in [(-2.35, "PICK SIDE\n(faces the aisle)", C_PICK), (0.3, "PUT-TO-LIGHT\nWALL", C_WALL), (3.2, "PACK SIDE", C_PACK)]:
    ax.text(x, 2.62, t, ha="center", va="center", fontsize=13, weight="bold", color=c)
ax.plot([-0.25, -0.25], [0.1, 2.35], color="#cbd5e1", lw=1, ls=":"); ax.plot([0.85, 0.85], [0.1, 2.35], color="#cbd5e1", lw=1, ls=":")


def step(x, y, n, color):
    ax.add_patch(Circle((x, y), 0.17, facecolor="white", edgecolor=color, lw=2.2, zorder=8))
    ax.text(x, y, str(n), ha="center", va="center", fontsize=13, weight="bold", color=color, zorder=9)


step(-3.35, 1.95, 1, C_PICK); step(-0.55, 2.1, 2, C_PICK); step(1.05, 2.1, 3, C_PACK); step(3.2, 1.95, 4, C_PACK)
ax.annotate("", xy=(-0.13, 0.2 + 2 * 0.36 + 0.18), xytext=(-0.62, 1.2), arrowprops=dict(arrowstyle="-|>", color=C_PICK, lw=2))
ax.annotate("", xy=(1.3, 1.2), xytext=(0.72, 0.2 + 0.36 + 0.18), arrowprops=dict(arrowstyle="-|>", color=C_PACK, lw=2))
ax.annotate("", xy=(3.95, 1.0), xytext=(3.45, 1.15), arrowprops=dict(arrowstyle="-|>", color=C_PACK, lw=2))
cards = [(1, C_PICK, "The picker brings a\ntrolley with items for\nmany small orders\n(one batch)."),
         (2, C_PICK, "The putter scans an\nitem: its order's slot\nlights up (here: put 2).\nPut in, press the light."),
         (3, C_PACK, "Order complete: the\nlight on the pack side\nturns green. The packer\ntakes the tote out."),
         (4, C_PACK, "Pack, print the label,\nput the carton in the\nroll cage of its\ncarrier.")]
for i, (n, c, t) in enumerate(cards):
    x0 = -4.5 + i * 2.48
    ax.add_patch(FancyBboxPatch((x0, -1.68), 2.34, 1.38, boxstyle="round,pad=0,rounding_size=0.08", facecolor="#f8fafc",
                                edgecolor=c, lw=1.4, zorder=2))
    step(x0 + 0.24, -0.53, n, c)
    ax.text(x0 + 0.14, -1.08, t, ha="left", va="center", fontsize=11.5, color=INK, zorder=3, linespacing=1.25)
ax.text(0.3, -0.12, "seen from the side", ha="center", va="top", fontsize=9.5, color=SUB)
fig.suptitle("How the put-to-light wall works", fontsize=17, weight="bold", color=INK, y=0.99)
save_fig(fig, "putwall_how.png")

old = os.path.join(os.path.dirname(__file__), "..", "outputs", "figures", "putwall_layout.png")
if os.path.exists(old):
    os.remove(old)                                                       # replaced by the two figures above
update_metrics("putwall_design", {"wall": PW, "wall_xy_m": [round(PW_X0, 1), round(PW_Y0, 1)], "pack_stations": N_BENCH})
print("Saved putwall_where.png and putwall_how.png")
