"""
ZONES - two figures that explain the zones around the storage (same style as the put-wall and storage figures).
  zone_guide.png    : the whole warehouse (north up) with every zone numbered in the order the goods pass through it,
                      and a list: name, size and what happens there.
  inbound_zones.png : the west side enlarged - receiving, the container zone and returns - with lettered places and a
                      key; it also shows the half of receiving that is lent to unpacking on big-container days.
Positions from geometry.py (drawn by layout_draw.py); sizes and counts from phase1_metrics.json.
Run after warehouse_floorplan.py, picking_plan.py and dock_mhe_plan.py.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, ConnectionPatch
from matplotlib.lines import Line2D
from _util import save_fig, update_metrics
import layout_draw as D
from layout_draw import M, FP, LZ, INK, SUB, COL, letter, flow, RET_Y0, OFF_Y0
from geometry import (DEPTH, L, left_w, right_w, rax, cx0, cx1, la, ra, fwd_h, rack_y0, rack_y1, cross_y, rvh, lzh, uh,
                      PK_Y0, R_DOORS, S_DOORS, CONV_Y, CONV_LEN, BUILD_W, WRAP_XY, RECV, LOOSE, RET, OFF, PACK, OUTB, FWD,
                      CIRC, dd_area, sel_area)

LAY, SP, DM = M["layout"], M["picking"]["small_parts"], M["dock_mhe"]
PW = M["picking"]["putwall"]
HL = "#d40011"
C_IN, C_CONT = "#2b6cb0", "#d97706"


def whole(ax, labels_doors=True, pallets=False):
    D.building(ax); D.zone_fills(ax)
    D.racks(ax, pallets=pallets); D.fast_pick(ax)
    D.receiving(ax, lent=False); D.container_zone(ax); D.returns(ax); D.packing(ax); D.outbound(ax)
    D.doors(ax, labels=labels_doors, fs=7)


def badge(ax, x, y, n, color, r=2.7, fs=15):
    ax.add_patch(Circle((x, y), r, facecolor=color, edgecolor="white", lw=2.2, zorder=9))
    ax.text(x, y, str(n), ha="center", va="center", fontsize=fs, weight="bold", color="white", zorder=10)


# ============================================================ FIGURE 1: zone guide
ZC = {1: "#c2410c", 2: "#d97706", 3: "#3b5bdb", 4: "#2f855a", 5: "#be185d", 6: "#b45309", 7: "#9d174d", 8: "#475569", 9: "#64748b"}
zones = [
    (1, "Receiving", RECV, "trailers unloaded at R2 / R3; pallets\ncounted, checked and scanned", (left_w / 2, rvh * 0.5)),
    (2, "Container zone", LOOSE, f"containers at R1 unpacked; cartons\nsorted onto {LZ['build_spots']} pallets at a time",
     (left_w / 2 + 1.5, rvh + lzh * 0.62)),
    (3, "Pallet racks", dd_area + sel_area, f"{LAY['positions_total']:,} pallet places: stock in\nreserve and slow items",
     ((cx0 + cx1) / 2, (cross_y + rack_y1) / 2)),
    (4, "Fast-pick area", FWD, f"pick faces for the {FP['skus']:,}\nbest-selling items", ((cx0 + cx1) / 2 - 12, fwd_h / 2)),
    (5, "Packing", PACK, f"put-to-light wall, {M['putwall_design']['pack_stations']} pack stations,\nsmall-parts shelving",
     (rax + right_w / 2, PK_Y0 + 11.5)),
    (6, "Outbound staging", OUTB, "a lane per shipping door S1–S5:\ngoods wait for their truck", (rax + right_w / 2 - 2.6, uh / 2 + 2.15)),
    (7, "Returns", RET, "returned goods checked and sorted:\nrestock, rework or scrap", (left_w / 2 + 3.2, RET_Y0 + RET / left_w * 0.72)),
    (8, "Offices & amenities", OFF, "office, canteen, toilets and lockers", (left_w / 2, OFF_Y0 + OFF / left_w / 2)),
    (9, "Aisles", CIRC, "perimeter and cross-aisles: where\ntrucks and people move", (la, (rack_y0 + cross_y) / 2)),
]
assert sum(z[2] for z in zones) == LAY["total_area_m2"], "zone list must add up to the layout area"
fig = plt.figure(figsize=(11, 6.6))
axP = fig.add_axes([0.005, 0.02, 0.625, 0.90]); axL = fig.add_axes([0.64, 0.02, 0.355, 0.90])
for a in (axP, axL):
    a.axis("off")
whole(axP)
axP.set_xlim(-4, L + 4); axP.set_ylim(-5.5, DEPTH + 1.5); axP.set_aspect("equal")
for n, name, a_, txt, (x, y) in zones:
    badge(axP, x, y, n, ZC[n])
axP.plot([2, 12], [-3.2, -3.2], color=INK, lw=2.2); axP.text(7, -5.2, "10 m", ha="center", fontsize=9, color=INK)
axP.annotate("", xy=(L - 3, -1.0), xytext=(L - 3, -5.0), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.6))
axP.text(L - 1.6, -3.2, "N", ha="left", va="center", fontsize=10, weight="bold", color=INK)
axL.set_xlim(0, 1); axL.set_ylim(0, 1)
for i, (n, name, a_, txt, _) in enumerate(zones):
    y = 0.955 - i * 0.107
    D.key_marker(axL, 0.06, y - 0.012, str(n), color=ZC[n], text_color="white", size=25, fs=12.5)
    axL.text(0.14, y + 0.012, f"{name}  ·  {a_:,} m²", ha="left", va="center", fontsize=11.5, weight="bold", color=INK, transform=axL.transAxes)
    axL.text(0.14, y - 0.008, txt, ha="left", va="top", fontsize=9.6, color=SUB, transform=axL.transAxes, linespacing=1.15)
fig.suptitle("The zones at a glance — numbered in the order goods pass through", fontsize=15.5, weight="bold", color=INK,
             x=0.01, ha="left", y=0.985)
save_fig(fig, "zone_guide.png")


# ============================================================ FIGURE 2: inbound side enlarged
fig = plt.figure(figsize=(11, 12.6))
axZ = fig.add_axes([0.01, 0.01, 0.47, 0.93]); axLoc = fig.add_axes([0.52, 0.70, 0.46, 0.25]); axK = fig.add_axes([0.52, 0.01, 0.46, 0.66])
for a in (axZ, axLoc, axK):
    a.axis("off")
# locator
whole(axLoc, labels_doors=False)
axLoc.set_xlim(-3, L + 3); axLoc.set_ylim(-2, DEPTH + 2); axLoc.set_aspect("equal")
zx0, zx1, zy0, zy1 = -3.4, cx0 + 0.4, -1.6, RET_Y0 + RET / left_w + 0.6
axLoc.add_patch(Rectangle((zx0, zy0), zx1 - zx0, zy1 - zy0, facecolor="none", edgecolor=HL, lw=2.4, zorder=10))
axLoc.text(zx1 + 1.5, zy1 - 2, "enlarged on the left", ha="left", va="top", fontsize=11, weight="bold", color=HL, zorder=10,
           bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=HL, lw=1.0))
axLoc.set_title("Where: the west side of the building", fontsize=12.5, weight="bold", color=INK, loc="left")
# enlarged west side
D.building(axZ); D.zone_fills(axZ, fast=False)
D.receiving(axZ, lent=True, detail=True); D.container_zone(axZ, detail=True); D.returns(axZ); D.doors(axZ, fs=9)
axZ.set_xlim(zx0, zx1 + 0.2); axZ.set_ylim(zy0, zy1); axZ.set_aspect("equal")
axZ.add_patch(Rectangle((zx0, zy0), zx1 - zx0, zy1 - zy0, facecolor="none", edgecolor=HL, lw=2.4, zorder=10, clip_on=False))
for y, t in [(rvh * 0.5 - 0.75, "1  RECEIVING"), (rvh + lzh - 1.0, "2  CONTAINER ZONE"), (RET_Y0 + RET / left_w - 1.1, "7  RETURNS")]:
    axZ.text(0.5, y, t, ha="left", va="center", fontsize=10.5, weight="bold", color=INK, zorder=9,
             bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.85))
axZ.text(left_w + (cx0 - left_w) / 2, 30, "left perimeter aisle", ha="center", va="center", fontsize=10, color=SUB, rotation=90)
# flows
for d in ("R3", "R2"):
    flow(axZ, [(-0.4, R_DOORS[d] + 1.15), (left_w - 1.2, R_DOORS[d] + 1.15)], C_IN, lw=2.6, ms=14)
flow(axZ, [(left_w - 1.3, R_DOORS["R2"]), (la, R_DOORS["R2"]), (la, cross_y), (cx0 + 0.3, cross_y)], C_IN, lw=2.6, ms=14)
axZ.text(la - 0.5, cross_y + 0.5, "to the racks", ha="right", va="bottom", fontsize=10, color=C_IN, weight="bold", zorder=9,
         bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.9))
flow(axZ, [(-0.4, CONV_Y + 0.0), (CONV_LEN - 0.4, CONV_Y)], C_CONT, lw=2.6, ms=14)
flow(axZ, [(WRAP_XY[0] + 2.0, WRAP_XY[1] - 0.3), (WRAP_XY[0] + 2.0, rvh + 8.9 + 1.4), (la - 0.4, rvh + 8.9 + 1.4)], C_CONT, lw=2.6, ms=14)
places = {"A": (-1.0, R_DOORS["R3"] - 2.6), "B": (5.0, R_DOORS["R3"] - 1.75), "C": (2.8, rvh * 0.5 - 3.6), "D": (left_w - 1.35, R_DOORS["R3"] - 1.75),
          "E": (6.3, rvh * 0.5 + 2.4), "F": (CONV_LEN + 1.0, CONV_Y), "G": (4.5, CONV_Y + 1.1 + BUILD_W / 2),
          "H": (6.0, rvh + 8.3), "I": (WRAP_XY[0] + 2.0, WRAP_XY[1] + 2.0), "J": (5.4, RET_Y0 + 1.4), "K": (5.2, RET_Y0 + 5.7),
          "L": (8.6, RET_Y0 + 8.0)}
for ch, (x, y) in places.items():
    letter(axZ, x, y, ch, r=0.75, fs=11)
axZ.plot([zx0 + 1.0, zx0 + 6.0], [zy0 - 0.5, zy0 - 0.5], color=INK, lw=2, zorder=9, clip_on=False)
axZ.text(zx0 + 3.5, zy0 - 0.8, "5 m", ha="center", va="top", fontsize=9.5, color=INK, zorder=9)
for (xa, ya), (xb, yb) in [((zx1, zy1), (zx1, zy1))]:
    fig.add_artist(ConnectionPatch(xyA=(xa, ya), coordsA=axLoc.transData, xyB=(xb, yb), coordsB=axZ.transData,
                                   color=HL, lw=1.2, ls="--", alpha=0.7))
key = [("A", "Doors R2 and R3", "trailers dock here: R2 in the north half, R3 in the south half"),
       ("B", "Unload lanes", f"pallets come off the trailer with the ERE 225 (9 places per lane;\npeak ~{LZ['recv_staged_pallets_peak']:.0f} waiting)"),
       ("C", "Check bench", "count, check quality, scan each pallet against the delivery note"),
       ("D", "Pick-up points", "the reach truck collects checked pallets here (put away)"),
       ("E", "R2 half — lent on big-container days", f"R2 is closed and this half ({LZ['r2_lend_m2']:.0f} m²) joins the\ncontainer zone: {LZ['area_with_r2_m2']:.0f} m² for unpacking"),
       ("F", "Door R1 + roller conveyor", "cartons roll out of the container into the zone"),
       ("G", "Build spots", f"{LZ['build_spots']} pallets built at once — one per item (SKU)"),
       ("H", "Finished pallets", f"room for {LZ['buffer_pallets']} built pallets waiting for the reach truck"),
       ("I", "Wrap and label station", "stretch-wrap, print the pallet label, scan"),
       ("J", "Returns intake", "returned goods arrive (through R2 / R3)"),
       ("K", "Inspection benches", "check each return and decide what happens"),
       ("L", "Grading places", "restock (green) · rework (yellow) · scrap (red)")]
axK.set_xlim(0, 1); axK.set_ylim(0, 1)
axK.text(0.0, 0.99, "Key", ha="left", va="center", fontsize=13.5, weight="bold", color=INK, transform=axK.transAxes)
for i, (ch, head, txt) in enumerate(key):
    y = 0.935 - i * 0.0745
    D.key_marker(axK, 0.04, y - 0.004, ch, size=22, fs=11.5)
    axK.text(0.10, y + 0.009, head, ha="left", va="center", fontsize=11.5, weight="bold", color=INK, transform=axK.transAxes)
    axK.text(0.10, y - 0.008, txt, ha="left", va="top", fontsize=9.8, color=SUB, transform=axK.transAxes, linespacing=1.15)
axK.legend(handles=[Line2D([0], [0], color=C_IN, lw=3.2, label="pallets from trailers"),
                    Line2D([0], [0], color=C_CONT, lw=3.2, label="cartons from containers")],
           loc="lower left", bbox_to_anchor=(0.0, -0.015), fontsize=11, frameon=False, ncol=2)
fig.suptitle("Receiving, container zone and returns — enlarged", fontsize=17, weight="bold", color=INK, x=0.01, ha="left", y=0.995)
save_fig(fig, "inbound_zones.png")

update_metrics("zones_design", {"zones": [{"No": n, "Zone": name, "m2": int(a_), "What happens": txt} for n, name, a_, txt, _ in zones]})
print("Saved zone_guide.png and inbound_zones.png")
