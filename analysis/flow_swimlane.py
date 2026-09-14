"""
End-to-end future-state process as a cross-functional SWIMLANE, rendered here
(matplotlib PNG) - no external app. Same model as the .drawio, drawn natively.
Output: outputs/figures/flow_swimlane.png
"""
import os, textwrap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon, FancyArrowPatch
import matplotlib.patheffects as pe
import matplotlib.font_manager as fm
from _util import FIGS

def _font():
    for f in ["Segoe UI", "Calibri", "Arial", "DejaVu Sans"]:
        if any(f.lower() == x.name.lower() for x in fm.fontManager.ttflist):
            return f
    return "DejaVu Sans"
plt.rcParams.update({"font.family": _font()})
INK, SUB = "#1f2937", "#6b7280"

lanes = ["Receiving", "Storage &\nPutaway", "Replenishment", "Picking",
         "Consolidation\n& Packing", "Shipping", "Returns\n(reverse)"]
lane_tint = ["#eef4ff", "#eefbf1", "#fff7e9", "#eef4ff", "#fdeef0", "#eefbf1", "#f5eefb"]

# id -> (label, lane, col, kind)
N = {
    "R1": ("Trailer arrives", 0, 0, "term"),
    "R2": ("Unload & RF scan", 0, 1, "proc"),
    "R3": ("Qty / quality OK?", 0, 2, "dec"),
    "R4": ("Register stock (LODNUM)", 0, 3, "proc"),
    "S1": ("System-directed putaway", 1, 3, "proc"),
    "S2": ("Reach truck to slot", 1, 4, "proc"),
    "S3": ("Stored & confirmed", 1, 5, "proc"),
    "P1": ("Forward face < min", 2, 4, "proc"),
    "P2": ("Pull reserve pallet", 2, 5, "proc"),
    "P3": ("Top-up pick face (FIFO)", 2, 6, "proc"),
    "K1": ("Wave release (cut-off)", 3, 0, "term"),
    "K2": ("Zone + batch pick", 3, 1, "proc"),
    "K3": ("Picked to consolidation", 3, 2, "proc"),
    "C1": ("Put-to-light sort", 4, 2, "proc"),
    "C2": ("Pack & label (P&A)", 4, 3, "proc"),
    "H1": ("Stage by carrier", 5, 4, "proc"),
    "H2": ("Load & dispatch", 5, 5, "proc"),
    "H3": ("Shipped (on-time)", 5, 6, "term"),
    "T1": ("Return arrives", 6, 0, "term"),
    "T2": ("Receive & grade", 6, 1, "proc"),
    "T3": ("Sellable /\nreworkable?", 6, 2, "dec"),
    "T4": ("Restock to storage", 6, 3, "proc"),
    "T5": ("Scrap / RTV", 6, 4, "term"),
}
E = [("R1","R2",""),("R2","R3",""),("R3","R4","yes"),("R4","S1",""),
     ("S1","S2",""),("S2","S3",""),("S3","P2","reserve"),
     ("P1","P2",""),("P2","P3",""),("P3","K2","faces"),
     ("K1","K2",""),("K2","K3",""),("K3","C1",""),("C1","C2",""),
     ("C2","H1",""),("H1","H2",""),("H2","H3",""),
     ("T1","T2",""),("T2","T3",""),("T3","T4","yes"),("T4","S1","putaway"),("T3","T5","no")]
DASHED = {("S3","P2"),("P3","K2"),("T4","S1")}

STYLE = {"proc": ("#dae8fc", "#6c8ebf"), "dec": ("#ffe6cc", "#d79b00"), "term": ("#d5e8d4", "#82b366")}
NL = len(lanes)
LANE_H, COL_W, X0, TITLE_W = 1.0, 1.55, 1.7, 1.35
BW, BH = 1.32, 0.5

def lane_base(i): return (NL - 1 - i) * LANE_H
def geom(nid):
    _, lane, col, kind = N[nid]
    w, h = (1.15, 0.62) if kind == "dec" else (BW, BH)
    x = X0 + col * COL_W
    y = lane_base(lane) + (LANE_H - h) / 2
    return x, y, w, h

POOL_W = X0 + 8 * COL_W
fig, ax = plt.subplots(figsize=(15, 8.2))
ax.set_xlim(-0.2, POOL_W + 0.3); ax.set_ylim(-0.9, NL * LANE_H + 0.9)
ax.set_aspect("equal"); ax.axis("off")
ax.text(POOL_W/2, NL*LANE_H + 0.55, "Option B — End-to-End Future-State Process (swimlane)",
        ha="center", fontsize=15, weight="bold", color=INK)

# lane bands + titles
for i, name in enumerate(lanes):
    b = lane_base(i)
    ax.add_patch(FancyBboxPatch((0, b + 0.03), POOL_W, LANE_H - 0.06, boxstyle="round,pad=0,rounding_size=0.05",
                 facecolor=lane_tint[i], edgecolor="#c7cede", lw=1.1, zorder=1))
    ax.add_patch(FancyBboxPatch((0, b + 0.03), TITLE_W, LANE_H - 0.06, boxstyle="round,pad=0,rounding_size=0.05",
                 facecolor="#eaeef6", edgecolor="#c7cede", lw=1.1, zorder=2))
    ax.text(TITLE_W/2, b + LANE_H/2, name, ha="center", va="center", fontsize=9, weight="bold", color=INK, zorder=3)

def draw_node(nid):
    x, y, w, h = geom(nid); label, _, _, kind = N[nid]
    fill, edge = STYLE[kind]
    # shadow
    if kind == "dec":
        cx, cy = x + w/2, y + h/2
        sh = Polygon([(cx+0.05, cy+h/2-0.05), (cx+w/2+0.05, cy-0.05), (cx+0.05, cy-h/2-0.05), (cx-w/2+0.05, cy-0.05)],
                     closed=True, facecolor="#8a94a6", alpha=0.18, zorder=3.8)
        ax.add_patch(sh)
        ax.add_patch(Polygon([(cx, cy+h/2), (cx+w/2, cy), (cx, cy-h/2), (cx-w/2, cy)], closed=True,
                     facecolor=fill, edgecolor=edge, lw=1.5, zorder=4))
    else:
        rs = 0.24 if kind == "term" else 0.09
        ax.add_patch(FancyBboxPatch((x+0.05, y-0.05), w, h, boxstyle=f"round,pad=0,rounding_size={rs}",
                     facecolor="#8a94a6", edgecolor="none", alpha=0.18, zorder=3.8))
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={rs}",
                     facecolor=fill, edgecolor=edge, lw=1.5, zorder=4))
    ax.text(x+w/2, y+h/2, "\n".join(textwrap.wrap(label, 16)) if "\n" not in label else label,
            ha="center", va="center", fontsize=7.6, color=INK, zorder=5, linespacing=1.0)

def center(g): return (g[0]+g[2]/2, g[1]+g[3]/2)
def edge_anchor(s, t):
    sg, tg = geom(s), geom(t)
    sl, tl = N[s][1], N[t][1]; scx = center(sg)[0]; tcx = center(tg)[0]
    if sl == tl:  # horizontal
        return ((sg[0]+sg[2], center(sg)[1]), (tg[0], center(tg)[1]))
    # tgt in a different lane
    a = (scx, sg[1]) if tl > sl else (scx, sg[1]+sg[3])          # leave bottom if target is lower-lane
    if abs(N[t][2]-N[s][2]) <= 0.1:                              # roughly same column -> vertical
        b = (tcx, tg[1]+tg[3]) if tl > sl else (tcx, tg[1])
    else:                                                       # enter tgt side nearest src
        b = (tg[0], center(tg)[1]) if tcx > scx else (tg[0]+tg[2], center(tg)[1])
    return (a, b)

for nid in N: draw_node(nid)

def poly(points, dashed, color="#5b6b7f"):
    xs = [p[0] for p in points]; ys = [p[1] for p in points]
    ln, = ax.plot(xs, ys, color=color, lw=1.8, zorder=6, solid_capstyle="round",
                  linestyle=(0, (5, 3)) if dashed else "-")
    ln.set_path_effects([pe.Stroke(linewidth=3.6, foreground="white"), pe.Normal()])
    ax.annotate("", xy=points[-1], xytext=points[-2], zorder=7,
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.8, mutation_scale=13))

GUTTER = TITLE_W + 0.22   # clear vertical channel between lane titles and col 0
BOTTOM = -0.55            # routing margin below all lanes
for s, t, lbl in E:
    dashed = (s, t) in DASHED
    sg, tg = geom(s), geom(t)
    lbl_pt = None
    if (s, t) == ("T4", "S1"):        # long feedback: down, along the bottom margin, up the left gutter
        a = (center(sg)[0], sg[1]); b = (tg[0], center(tg)[1])
        pts = [a, (a[0], BOTTOM), (GUTTER, BOTTOM), (GUTTER, b[1]), b]
        poly(pts, dashed); lbl_pt = (GUTTER, (BOTTOM + b[1]) / 2)
    elif (s, t) == ("T3", "T5"):      # 'no' branch: dip under the Restock box
        a = (center(sg)[0], sg[1]); b = (center(tg)[0], tg[1])
        yb = lane_base(6) + 0.12
        pts = [a, (a[0], yb), (b[0], yb), b]
        poly(pts, dashed); lbl_pt = (a[0] + 0.35, (a[1] + yb) / 2)
    else:
        a, b = edge_anchor(s, t)
        same = N[s][1] == N[t][1]
        if same:
            cs = "arc3,rad=0"
        else:
            leaving_bottom = a[1] <= center(sg)[1]
            cs = f"angle,angleA={-90 if leaving_bottom else 90},angleB=180,rad=6"
        p = FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=13, lw=1.8, color="#5b6b7f",
                            connectionstyle=cs, linestyle=(0, (5, 3)) if dashed else "-", zorder=6)
        p.set_path_effects([pe.Stroke(linewidth=3.6, foreground="white"), pe.Normal()])
        ax.add_patch(p)
        # label near the source so it never lands on the target box
        lbl_pt = (a[0]*0.62 + b[0]*0.38, a[1]*0.62 + b[1]*0.38 + 0.13)
    if lbl and lbl_pt:
        ax.text(lbl_pt[0], lbl_pt[1], lbl, ha="center", va="center", fontsize=7, color="#b45309",
                weight="bold", zorder=8, bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.9))

fig.savefig(os.path.join(FIGS, "flow_swimlane.png"), dpi=120, bbox_inches="tight")
plt.close(fig)
print("Saved flow_swimlane.png", f"({len(N)} nodes, {len(E)} edges, {NL} lanes)")
