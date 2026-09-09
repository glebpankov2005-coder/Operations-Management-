"""
PHASE 4 - FUTURE-STATE PROCESS FLOWCHARTS (Option B).
Draws clean vertical flowcharts (matplotlib, no external binary) for the
in-scope processes, annotating where the Deliverable-1 design choices apply.
Saves PNGs to outputs/figures/.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon
from _util import FIGS
import os

BLUE = "#6c8eef"; DARK = "#22303f"; NOTE = "#b45309"; GREEN = "#2f855a"; GREY = "#e8edf7"


def draw_flow(title, steps, filename):
    """steps: list of dict(kind, text, note). kind in start|process|decision|end."""
    n = len(steps)
    fig_h = 0.95 * n + 1.1
    fig, ax = plt.subplots(figsize=(8.2, fig_h))
    ax.set_xlim(0, 10); ax.set_ylim(0, n + 0.5); ax.axis("off")
    ax.set_title(title, fontsize=13, weight="bold", color=DARK, pad=12)
    cx = 4.2; bw = 4.6; bh = 0.62
    for i, s in enumerate(steps):
        y = n - i - 0.2
        kind = s.get("kind", "process")
        if kind == "decision":
            d = 0.42
            poly = Polygon([(cx, y + bh/2 + d), (cx + bw/2, y + bh/2),
                            (cx, y + bh/2 - d), (cx - bw/2, y + bh/2)],
                           closed=True, facecolor="#fff4e0", edgecolor=NOTE, lw=1.6)
            ax.add_patch(poly)
            ax.text(cx, y + bh/2, s["text"], ha="center", va="center", fontsize=8.5, color=DARK, wrap=True)
        else:
            face = BLUE if kind in ("start", "end") else GREY
            edge = BLUE if kind in ("start", "end") else "#9db4e8"
            tcol = "white" if kind in ("start", "end") else DARK
            box = FancyBboxPatch((cx - bw/2, y), bw, bh, boxstyle="round,pad=0.02,rounding_size=0.12",
                                 facecolor=face, edgecolor=edge, lw=1.4)
            ax.add_patch(box)
            ax.text(cx, y + bh/2, s["text"], ha="center", va="center", fontsize=9,
                    color=tcol, weight="bold" if kind in ("start", "end") else "normal")
        # side note (design choice)
        if s.get("note"):
            ax.annotate(s["note"], xy=(cx + bw/2, y + bh/2), xytext=(cx + bw/2 + 0.35, y + bh/2),
                        ha="left", va="center", fontsize=7.6, color=NOTE, style="italic",
                        arrowprops=dict(arrowstyle="-", color=NOTE, lw=0.7))
        # arrow to next
        if i < n - 1:
            ax.annotate("", xy=(cx, y - 0.18), xytext=(cx, y),
                        arrowprops=dict(arrowstyle="-|>", color=DARK, lw=1.4))
    fig.savefig(os.path.join(FIGS, filename), dpi=115, bbox_inches="tight")
    plt.close(fig)
    print("saved", filename)


# 1) RECEIVING & PUTAWAY
draw_flow("Receiving & Putaway", [
    {"kind": "start", "text": "Inbound trailer arrives"},
    {"kind": "process", "text": "Unload & scan pallets (ASN check)", "note": "RF scan; ~25 pallets/h"},
    {"kind": "decision", "text": "Qty / quality OK?", "note": "discrepancy -> hold & report"},
    {"kind": "process", "text": "Register stock in WMS (LODNUM)"},
    {"kind": "process", "text": "System-directed putaway location", "note": "velocity-based: A/B->double-deep reserve near pick; C->deep/upper"},
    {"kind": "process", "text": "Reach truck moves pallet to slot", "note": "cantilever for XLONG goods (>240cm)"},
    {"kind": "end", "text": "Pallet stored & confirmed"},
], "flow_receiving_putaway.png")

# 2) REPLENISHMENT
draw_flow("Replenishment (reserve -> forward pick)", [
    {"kind": "start", "text": "Forward-pick face below min"},
    {"kind": "process", "text": "WMS raises replen task", "note": "min/max triggered"},
    {"kind": "decision", "text": "Reserve pallet available?", "note": "no -> flag for inbound/putaway"},
    {"kind": "process", "text": "Reach truck pulls reserve pallet"},
    {"kind": "process", "text": "Top up carton-flow / pick face", "note": "FIFO via FIF DATE where relevant"},
    {"kind": "end", "text": "Forward face replenished"},
], "flow_replenishment.png")

# 3) PICKING (zone + batch/wave)
draw_flow("Picking  (zone + batch / wave)", [
    {"kind": "start", "text": "Orders received & allocated"},
    {"kind": "process", "text": "Wave release by carrier cut-off", "note": "wave = carrier/route deadline"},
    {"kind": "decision", "text": "Order profile?", "note": "routes line to the right method"},
    {"kind": "process", "text": "Full-pallet pick from reserve (2.6%)"},
    {"kind": "process", "text": "Case pick - batch multi-order (63%)", "note": "batch single-line orders; voice/RF; A in golden zone"},
    {"kind": "process", "text": "Each pick - pick-to-cart (16%)"},
    {"kind": "end", "text": "Picked stock to consolidation"},
], "flow_picking.png")

# 4) PACK, CONSOLIDATION & SHIPPING
draw_flow("Consolidation, Packing & Shipping", [
    {"kind": "start", "text": "Picked totes / pallets arrive"},
    {"kind": "process", "text": "Put-to-light sort by order", "note": "consolidate multi-zone picks"},
    {"kind": "process", "text": "Pack & print-and-apply label", "note": "labour bottleneck - size to peak"},
    {"kind": "decision", "text": "Parcel or pallet?", "note": "~18 pallets/day; rest = DHL Parcel cartons"},
    {"kind": "process", "text": "Stage by carrier / dock"},
    {"kind": "process", "text": "Load & dispatch trailer", "note": "confirm ship in WMS"},
    {"kind": "end", "text": "Order shipped (on-time)"},
], "flow_pack_ship.png")

# 5) RETURNS (reverse logistics)
draw_flow("Returns  (reverse logistics)", [
    {"kind": "start", "text": "Customer return arrives (carrier)"},
    {"kind": "process", "text": "Receive & scan return (RMA)", "note": "at receiving docks; log in WMS"},
    {"kind": "process", "text": "Inspect & grade at Returns/VAS"},
    {"kind": "decision", "text": "Sellable as-is?", "note": "yes -> restock"},
    {"kind": "decision", "text": "Reworkable (VAS)?", "note": "no -> scrap / return-to-vendor"},
    {"kind": "process", "text": "Rework / repack (VAS)"},
    {"kind": "process", "text": "Putaway back to stock", "note": "velocity-based, same as inbound"},
    {"kind": "end", "text": "Inventory & credit updated"},
], "flow_returns.png")

print("all flowcharts done")
