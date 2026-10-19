"""
Shared drawing of the Option B layout (metres, north up). The floor plan and the explanation figures (put-wall,
storage, zone guide, docks) all call these functions, so every picture shows the same places.
Positions come from geometry.py; counts (faces, bays, build spots) from phase1_metrics.json.
"""
import json, os
import numpy as np
from matplotlib.patches import Rectangle, Circle
from _util import REPORTS
from geometry import (DEPTH, L, left_w, right_w, cx0, cx1, rax, fwd_h, rack_y0, rack_y1, cross_y, mod_x, BLOCK, n_mod,
                      OFF, RET, rvh, lzh, uh, R_DOORS, S_DOORS, FP_X0, FP_X1, FP_WALL_Y0, FP_PAL_D, FP_SHELF_D,
                      FP_FLOW_Y0, FP_FLOW_D, FP_REFILL_Y0, FP_FLOW_BAY, FP_N_FLOW_BAYS, FP_FLOW_LANES,
                      FP_PAL_W, FP_SHELF_W, FP_LONG_W, LONG_BAY, CONV_Y, CONV_LEN, BUILD_W, WRAP_XY,
                      PK_Y0, PW_X0, PW_DEPTH, PW_LEN, PW_Y0, BENCH_X0, BENCH_W, N_BENCH, CAGE_X0, SHELF_Y0)

M = json.load(open(os.path.join(REPORTS, "phase1_metrics.json"), encoding="utf-8"))
FP = M["picking"]["fast_pick"]
LZ = M["dock_mhe"]["loose_zone"]

INK, SUB, STEEL = "#1f2937", "#6b7280", "#33415a"
COL = {   # zone backgrounds (as the floor plan) and the things inside them
    "recv": "#f4c98c", "cont": "#f6dfb6", "ret": "#e6bcd8", "off": "#cfd6e2", "fast": "#dff3e6", "pack": "#f7d4d4",
    "out": "#f4c98c", "rack": "#8aa4fb", "rack_odd": "#b7c6fb", "rack_long": "#a99cf0", "rack_edge": "#6d8bfa",
    "flow": "#4fb07c", "refill": "#c9ead6", "fp_pal": "#e8c36a", "shelf": "#b9cbf3", "long_shelf": "#8ea2e6",
    "pallet": "#e9cf9b", "pallet_edge": "#b08a4e", "conveyor": "#64748b", "build": "#fbe7c4", "wrap": "#d1d5db",
    "lane": "#fbe3bf", "bench": "#c08a6a", "cage": "#9fdcbf", "wall": "#1d4ed8", "pack_bench": "#e59a7a",
}
LEFT_X1 = left_w                                         # west column: x = 0 .. left_w
OFF_Y0 = DEPTH - OFF / left_w
RET_Y0 = OFF_Y0 - RET / left_w
LZ_Y1 = rvh + lzh


def rect(ax, x, y, w, h, fc, ec="none", lw=0.5, z=2.0, **kw):
    ax.add_patch(Rectangle((x, y), w, h, facecolor=fc, edgecolor=ec, lw=lw, zorder=z, **kw))


def pallet(ax, x, y, w=0.8, h=1.2, z=2.6, fc=None):
    rect(ax, x, y, w, h, fc or COL["pallet"], ec=COL["pallet_edge"], lw=0.35, z=z)


# ---------------------------------------------------------------- building, zone backgrounds, doors
def building(ax, z=0.5):
    rect(ax, 0, 0, L, DEPTH, "white", ec=STEEL, lw=1.6, z=z)


def zone_fills(ax, z=1.0, inset=0.3, fast=True):
    """Light background of every non-storage zone (the racks are drawn by racks())."""
    zones = [(0, 0, left_w, rvh, COL["recv"]), (0, rvh, left_w, lzh, COL["cont"]),
             (0, RET_Y0, left_w, RET / left_w, COL["ret"]), (0, OFF_Y0, left_w, OFF / left_w, COL["off"]),
             (rax, 0, right_w, uh, COL["out"]), (rax, PK_Y0, right_w, DEPTH - PK_Y0, COL["pack"])]
    if fast:
        zones.append((cx0, 0, cx1 - cx0, fwd_h, COL["fast"]))
    for x, y, w, h, c in zones:
        rect(ax, x + inset, y + inset, w - 2 * inset, h - 2 * inset, c, z=z)


def doors(ax, z=3.0, labels=True, fs=7.5):
    for name, yc in R_DOORS.items():
        rect(ax, -1.8, yc - 1.4, 1.6, 2.8, STEEL, z=z)
        if labels:
            ax.text(-1.0, yc, name, ha="center", va="center", fontsize=fs, color="white", weight="bold", rotation=90, zorder=z + 0.1,
                    clip_on=True)
    for name, yc in S_DOORS.items():
        rect(ax, L + 0.2, yc - 1.4, 1.6, 2.8, STEEL, z=z)
        if labels:
            ax.text(L + 1.0, yc, name, ha="center", va="center", fontsize=fs, color="white", weight="bold", rotation=90, zorder=z + 0.1,
                    clip_on=True)


# ---------------------------------------------------------------- storage
def racks(ax, z=2.0, pallets=False, x_range=None):
    """Single-deep back-to-back rack modules, two runs each (front and rear of the middle cross-aisle).
    pallets=True draws the pallets in every bay (top view): 3 EUR pallets per 2.7 m bay each side,
    2 long pallets (2.05 m) per 4.5 m bay in the long-goods module."""
    runs = [(rack_y0, cross_y - 1.6), (cross_y + 1.6, rack_y1)]
    for m in range(n_mod):
        x0 = mod_x[m]
        if x_range and not (x_range[0] - BLOCK <= x0 <= x_range[1]):
            continue
        fill = COL["rack_long"] if m == n_mod - 1 else (COL["rack_odd"] if m == n_mod - 2 else COL["rack"])
        for (y0, y1) in runs:
            rect(ax, x0, y0, BLOCK, y1 - y0, fill, ec=COL["rack_edge"], lw=0.6, z=z)
            if not pallets:
                continue
            bay = LONG_BAY if m == n_mod - 1 else 2.7
            nb = int((y1 - y0) // bay); off = ((y1 - y0) - nb * bay) / 2          # bays centred in the run
            for by in y0 + off + bay * np.arange(nb):
                ax.plot([x0, x0 + BLOCK], [by, by], color="white", lw=0.9, zorder=z + 0.2)
                if m == n_mod - 1:                                   # long goods: 2.05 m along the aisle, 0.8 m deep
                    for k in range(2):
                        yy = by + 0.15 + k * 2.15
                        pallet(ax, x0 + 0.1, yy, 0.8, 2.05, z + 0.3, fc="#d8cdfb")
                        pallet(ax, x0 + BLOCK - 0.9, yy, 0.8, 2.05, z + 0.3, fc="#d8cdfb")
                else:                                                # EUR: 800 mm to the aisle, 1.2 m deep
                    for k in range(3):
                        yy = by + 0.1 + k * 0.87
                        pallet(ax, x0 + 0.05, yy, 1.2, 0.8, z + 0.3)
                        pallet(ax, x0 + BLOCK - 1.25, yy, 1.2, 0.8, z + 0.3)
            ax.plot([x0 + BLOCK / 2, x0 + BLOCK / 2], [y0, y1], color="white", lw=0.8, zorder=z + 0.25)   # back-to-back


def fast_pick(ax, z=2.0, detail=False):
    """South band: refill strip | carton-flow row | pick aisle | wall row (floor pallets, shelving, long-item shelves)."""
    rect(ax, FP_X0, FP_REFILL_Y0 + 0.1, FP_X1 - FP_X0, fwd_h - FP_REFILL_Y0 - 0.3, COL["refill"], z=z)
    for i in range(FP_N_FLOW_BAYS):
        x = FP_X0 + i * FP_FLOW_BAY
        rect(ax, x + 0.04, FP_FLOW_Y0, FP_FLOW_BAY - 0.08, FP_FLOW_D, COL["flow"], ec="white", lw=0.3, z=z + 0.1)
        if detail:
            for k in range(1, FP_FLOW_LANES):
                xx = x + k * FP_FLOW_BAY / FP_FLOW_LANES
                ax.plot([xx, xx], [FP_FLOW_Y0 + 0.1, FP_FLOW_Y0 + FP_FLOW_D - 0.1], color="white", lw=0.5, alpha=0.8, zorder=z + 0.2)
    x = FP_X1                                                         # wall row, from the east end (next to packing)
    for _ in range(FP["pallet_faces"]):
        x -= FP_PAL_W
        rect(ax, x + 0.06, FP_WALL_Y0, FP_PAL_W - 0.12, FP_PAL_D, COL["fp_pal"], ec="#b98a2e", lw=0.3, z=z + 0.1)
    x -= 0.6
    for _ in range(FP["shelf_bays"]):
        x -= FP_SHELF_W
        rect(ax, x + 0.04, FP_WALL_Y0, FP_SHELF_W - 0.08, FP_SHELF_D, COL["shelf"], ec="white", lw=0.3, z=z + 0.1)
    x -= 0.6
    for _ in range(FP["long_bays"]):
        x -= FP_LONG_W
        rect(ax, x + 0.05, FP_WALL_Y0, FP_LONG_W - 0.1, FP_SHELF_D, COL["long_shelf"], ec="white", lw=0.3, z=z + 0.1)
    return x                                                          # west end of the wall row (spare beyond)


def wall_row_parts():
    """x-ranges of the wall-row parts (east to west) for labels."""
    x1 = FP_X1; x0 = x1 - FP["pallet_faces"] * FP_PAL_W; pal = (x0, x1)
    x1 = x0 - 0.6; x0 = x1 - FP["shelf_bays"] * FP_SHELF_W; shelf = (x0, x1)
    x1 = x0 - 0.6; x0 = x1 - FP["long_bays"] * FP_LONG_W; lng = (x0, x1)
    return {"pallets": pal, "shelving": shelf, "long": lng}


# ---------------------------------------------------------------- inbound side (west)
def receiving(ax, z=2.0, lent=True, detail=False):
    """Two unload lanes (R2 in the north half, R3 in the south half), check bench, pick-up points for the reach trucks."""
    for d in ("R2", "R3"):
        yc = R_DOORS[d]
        rect(ax, 0.5, yc - 0.75, 9.4, 1.5, COL["lane"], ec="#d9a35a", lw=0.4, z=z)
        for i in range(9):
            pallet(ax, 0.8 + i * 1.0, yc - 0.6, 0.8, 1.2, z + 0.2)
    rect(ax, 1.0, rvh * 0.5 - 2.6, 3.6, 1.4, COL["bench"], z=z + 0.2)          # check / QC bench (south half)
    for d in ("R2", "R3"):                                                       # pick-up points at the aisle side
        rect(ax, left_w - 2.3, R_DOORS[d] - 0.75, 1.9, 1.5, "white", ec="#b45309", lw=0.9, z=z + 0.1, ls="--")
    if lent:
        rect(ax, 0.35, rvh * 0.5 + 0.1, left_w - 0.7, rvh * 0.5 - 0.35, "none", ec="#c2410c", lw=1.3, z=z + 0.4, ls=(0, (4, 2)))


def container_zone(ax, z=2.0, detail=False):
    """Roller conveyor from R1, build spots each side of it, finished-pallet buffer, wrap/label station."""
    rect(ax, 0.2, CONV_Y - 1.0, CONV_LEN + 0.6, 2.0, "#fdf1dc", ec="#e2b77a", lw=0.4, z=z)   # unload lane (2 m)
    rect(ax, 0.2, CONV_Y - 0.3, CONV_LEN, 0.6, COL["conveyor"], z=z + 0.3)
    if detail:
        for xx in np.arange(0.5, CONV_LEN, 0.35):
            ax.plot([xx, xx], [CONV_Y - 0.25, CONV_Y + 0.25], color="#cbd5e1", lw=0.5, zorder=z + 0.35)
    n_side = int(np.ceil(LZ["build_spots"] / 2))
    for side in (1, -1):
        for i in range(n_side):
            x = 1.0 + i * 1.75
            y = CONV_Y + 1.1 if side > 0 else CONV_Y - 1.1 - BUILD_W
            rect(ax, x, y, BUILD_W, BUILD_W, COL["build"], ec="#d9a35a", lw=0.5, z=z + 0.1)
            pallet(ax, x + 0.4, y + 0.2, 0.8, 1.2, z + 0.2)
    rows = [(rvh + 7.1, 11), (rvh + 8.3, 11), (rvh + 10.8, 7), (rvh + 12.0, 7)]  # 2 double rows of finished pallets
    assert sum(n for _, n in rows) >= LZ["buffer_pallets"], "container-zone buffer smaller than sized"
    for y, n in rows:
        for i in range(n):
            pallet(ax, 0.6 + i * 1.0, y, 0.8, 1.2, z + 0.2, fc="#f2d9a6")
    rect(ax, WRAP_XY[0], WRAP_XY[1], 4.0, 4.0, COL["wrap"], ec="#94a3b8", lw=0.6, z=z + 0.1)
    ax.add_patch(Circle((WRAP_XY[0] + 2.0, WRAP_XY[1] + 2.0), 1.1, facecolor="white", edgecolor="#64748b", lw=0.8, zorder=z + 0.2))


def returns(ax, z=2.0):
    """Intake lane, two inspection benches, three grading places (restock / rework / scrap)."""
    y0 = RET_Y0
    for i in range(4):
        pallet(ax, 0.8 + i * 1.0, y0 + 0.8, 0.8, 1.2, z + 0.2)
    rect(ax, 1.0, y0 + 4.2, 3.0, 1.0, COL["bench"], z=z + 0.2)
    rect(ax, 1.0, y0 + 7.2, 3.0, 1.0, COL["bench"], z=z + 0.2)
    for i, c in enumerate(("#9fdcbf", "#fde68a", "#fca5a5")):
        rect(ax, 7.0 + i * 1.6, y0 + 5.5, 1.2, 1.2, c, ec="#64748b", lw=0.5, z=z + 0.2)


# ---------------------------------------------------------------- outbound side (east)
def packing(ax, z=2.0, only_shelving=False):
    for r_ in range(12):
        rect(ax, rax + 0.9, SHELF_Y0 + r_ * 2.2, right_w - 1.8, 1.2, COL["shelf"], ec="white", lw=0.4, z=z)
    if only_shelving:
        return
    rect(ax, PW_X0, PW_Y0, PW_DEPTH, PW_LEN, COL["wall"], z=z + 0.1)
    for i in range(N_BENCH):
        rect(ax, BENCH_X0, PW_Y0 + i * PW_LEN / N_BENCH + 0.35, BENCH_W, PW_LEN / N_BENCH - 0.7, COL["pack_bench"], ec="white", z=z)
    for i in range(7):
        for j in range(2):
            rect(ax, CAGE_X0 + j * 1.3, PW_Y0 + i * 1.5 + 0.2, 1.0, 1.1, COL["cage"], ec="white", z=z)
    rect(ax, rax + 0.5, PK_Y0 + 0.6, 4.0, 3.8, "#fde7b0", z=z)                 # large-order pallets waiting
    rect(ax, rax + 5.2, PK_Y0 + 0.6, 2.2, 2.2, COL["wrap"], z=z)               # stretch wrapper


def outbound(ax, z=2.0):
    """One staging lane per shipping door: roll cages and pallets wait for their trailer."""
    for name, yc in S_DOORS.items():
        rect(ax, rax + 0.9, yc - 1.1, right_w - 1.8, 2.2, "#fbe3bf", ec="#d9a35a", lw=0.4, z=z)
        for i in range(3):
            rect(ax, rax + 1.3 + i * 1.15, yc - 0.55, 0.85, 1.1, COL["cage"], ec="#4b8f72", lw=0.4, z=z + 0.2)
        for i in range(2):
            pallet(ax, rax + 4.9 + i * 1.1, yc - 0.6, 0.8, 1.2, z + 0.2)


# ---------------------------------------------------------------- labels, arrows and small top-view icons
def letter(ax, x, y, ch, r=0.95, fs=12, z=8):
    ax.add_patch(Circle((x, y), r, facecolor="white", edgecolor=INK, lw=1.5, zorder=z))
    ax.text(x, y, ch, ha="center", va="center", fontsize=fs, weight="bold", color=INK, zorder=z + 1)


def flow(ax, pts, color, lw=3.2, z=7, ms=16):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=color, lw=lw, solid_capstyle="round", solid_joinstyle="round", zorder=z)
    ax.annotate("", xy=pts[-1], xytext=pts[-2], arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=ms), zorder=z)


def truck_top(ax, x, y, heading="S", z=6, load=True):
    """Reach truck seen from above at (x, y) = centre of the chassis; forks (and pallet) point to `heading`."""
    d = {"N": (0, 1), "S": (0, -1), "E": (1, 0), "W": (-1, 0)}[heading]
    w, l = 1.27, 1.8                                                 # ETV 216i: 1,270 mm wide
    if d[0] == 0:
        rect(ax, x - w / 2, y - l / 2, w, l, "#f2b134", ec="#9a6b12", lw=0.8, z=z)
        fy = y + d[1] * (l / 2 + 0.6)
        if load:
            pallet(ax, x - 0.4, fy - 0.6, 0.8, 1.2, z + 0.1)
    else:
        rect(ax, x - l / 2, y - w / 2, l, w, "#f2b134", ec="#9a6b12", lw=0.8, z=z)
        fx = x + d[0] * (l / 2 + 0.6)
        if load:
            pallet(ax, fx - 0.6, y - 0.4, 1.2, 0.8, z + 0.1)
    ax.add_patch(Circle((x - 0.25 * d[0], y - 0.25 * d[1]), 0.28, facecolor="#1f2937", edgecolor="none", zorder=z + 0.2))


def picker_top(ax, x, y, color="#eb6834", trolley=True, z=6, side="E"):
    ax.add_patch(Circle((x, y), 0.38, facecolor=color, edgecolor="white", lw=1.0, zorder=z + 0.1))
    if trolley:
        dx = 1.0 if side == "E" else -1.6
        rect(ax, x + dx, y - 0.3, 1.0, 0.6, "#e5e7eb", ec="#64748b", lw=0.7, z=z)
        rect(ax, x + dx + 0.08, y - 0.22, 0.38, 0.44, "#93c5fd", ec="#2563eb", lw=0.5, z=z + 0.05)
        rect(ax, x + dx + 0.54, y - 0.22, 0.38, 0.44, "#93c5fd", ec="#2563eb", lw=0.5, z=z + 0.05)


def key_marker(ax, x, y, ch, color="white", text_color=INK, size=24, fs=12):
    """Round lettered/numbered marker in axes coordinates (stays a circle whatever the axes shape)."""
    ax.scatter([x], [y], s=size ** 2, facecolor=color, edgecolor=INK if color == "white" else "white", lw=1.5,
               transform=ax.transAxes, zorder=5, clip_on=False)
    ax.text(x, y, ch, ha="center", va="center", fontsize=fs, weight="bold", color=text_color, transform=ax.transAxes, zorder=6)
