"""Add a title + zone-colour legend to the Blender render -> layout_3d_render.png"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.patches import Patch
import matplotlib.font_manager as fm

def _font():
    for f in ["Segoe UI", "Calibri", "Arial", "DejaVu Sans"]:
        if any(f.lower() == x.name.lower() for x in fm.fontManager.ttflist):
            return f
    return "DejaVu Sans"
plt.rcParams.update({"font.family": _font()})

FIGS = os.path.join(os.path.dirname(__file__), "..", "outputs", "figures")
img = mpimg.imread(os.path.join(FIGS, "warehouse_blender.png"))
h, w = img.shape[0], img.shape[1]
fig_w = 14
fig, ax = plt.subplots(figsize=(fig_w, fig_w * h / w + 1.4))
ax.imshow(img); ax.axis("off")
ax.set_title("Option B — Warehouse 3D (Blender render)", fontsize=16, weight="bold", color="#1f2937", pad=12)
handles = [
    Patch(fc=(0.30, 0.42, 0.85), label="Single-deep pallet racks (back-to-back)"),
    Patch(fc=(0.55, 0.66, 0.95), label="Odd-items + long-goods modules"),
    Patch(fc=(0.35, 0.74, 0.52), label="Fast-pick area"),
    Patch(fc=(0.95, 0.78, 0.45), label="Receiving / Outbound (staging)"),
    Patch(fc=(0.93, 0.62, 0.42), label="Loose-container zone (door R1)"),
    Patch(fc=(0.94, 0.62, 0.62), label="Packing & consolidation"),
    Patch(fc=(0.78, 0.80, 0.86), label="Offices & amenities"),
]
ax.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, -0.09), ncol=4,
          fontsize=9.5, frameon=False)
fig.savefig(os.path.join(FIGS, "layout_3d_render.png"), dpi=140, bbox_inches="tight")
plt.close(fig)
print("Saved layout_3d_render.png")

# ---- worker-movement render ----
wimg = mpimg.imread(os.path.join(FIGS, "warehouse_workers.png"))
h2, w2 = wimg.shape[0], wimg.shape[1]
fig, ax = plt.subplots(figsize=(fig_w, fig_w * h2 / w2 + 1.4))
ax.imshow(wimg); ax.axis("off")
ax.set_title("Option B — Worker Movement (Blender, top-down): zone batch picking with trolleys, aisles open at both ends",
             fontsize=15, weight="bold", color="#1f2937", pad=12)
wh = [
    Patch(fc=(0.85, 0.55, 0.10), label="Picker + trolley · Zone 1 (fast-pick area)"),
    Patch(fc=(0.49, 0.20, 0.66), label="Picker + trolley · Zone 2 (reserve low levels, left)"),
    Patch(fc=(0.03, 0.57, 0.70), label="Picker + trolley · Zone 3 (reserve low levels, right)"),
    Patch(fc=(0.10, 0.60, 0.30), label="Reach truck ETV 216i · putaway & replenishment"),
    Patch(fc=(0.86, 0.15, 0.15), label="Pallet truck ERE 225 · pack → east shipping docks"),
    Patch(fc=(0.93, 0.62, 0.42), label="Loose-container zone (door R1)"),
]
ax.legend(handles=wh, loc="lower center", bbox_to_anchor=(0.5, -0.09), ncol=3, fontsize=9.5, frameon=False)
fig.savefig(os.path.join(FIGS, "layout_worker_render.png"), dpi=140, bbox_inches="tight")
plt.close(fig)
print("Saved layout_worker_render.png")
