"""
Generate an EDITABLE draw.io swimlane process map of the Option B future-state
operation (open/edit in free draw.io - no third-party skill, no CLI needed).
Output: outputs/diagrams/warehouse_process.drawio
"""
import os
from xml.sax.saxutils import escape

OUT = os.path.join(os.path.dirname(__file__), "..", "outputs", "diagrams")
os.makedirs(OUT, exist_ok=True)

# geometry
TITLE_X, TITLE_W = 20, 150
CONTENT_X0, COL_W = 190, 172
LANE_TOP0, LANE_H = 20, 112
BW, BH = 148, 50            # process box
POOL_W = CONTENT_X0 + 8 * COL_W

lanes = [
    ("Receiving",              "#eef4ff"),
    ("Storage & Putaway",      "#eefbf1"),
    ("Replenishment",          "#fff7e9"),
    ("Picking",                "#eef4ff"),
    ("Consolidation & Packing","#fdeef0"),
    ("Shipping",               "#eefbf1"),
    ("Returns (reverse)",      "#f5eefb"),
]

# node: id -> (label, lane, col, kind)   kind: proc|dec|term
N = {
    "R1": ("Trailer arrives", 0, 0, "term"),
    "R2": ("Unload & RF scan (ASN check)", 0, 1, "proc"),
    "R3": ("Qty / quality OK?", 0, 2, "dec"),
    "R4": ("Register stock (LODNUM)", 0, 3, "proc"),
    "S1": ("System-directed putaway (velocity-based)", 1, 3, "proc"),
    "S2": ("Reach truck to rack slot", 1, 4, "proc"),
    "S3": ("Stored & confirmed", 1, 5, "proc"),
    "P1": ("Forward face below min", 2, 4, "proc"),
    "P2": ("Pull reserve pallet", 2, 5, "proc"),
    "P3": ("Top-up pick face (FIFO)", 2, 6, "proc"),
    "K1": ("Orders: wave release (carrier cut-off)", 3, 0, "term"),
    "K2": ("Zone + batch pick (voice/RF)", 3, 1, "proc"),
    "K3": ("Picked to consolidation", 3, 2, "proc"),
    "C1": ("Put-to-light sort by order", 4, 2, "proc"),
    "C2": ("Pack & print-and-apply label", 4, 3, "proc"),
    "H1": ("Stage by carrier / dock", 5, 4, "proc"),
    "H2": ("Load & dispatch trailer", 5, 5, "proc"),
    "H3": ("Shipped (on-time)", 5, 6, "term"),
    "T1": ("Customer return arrives", 6, 0, "term"),
    "T2": ("Receive & grade at Returns/VAS", 6, 1, "proc"),
    "T3": ("Sellable / reworkable?", 6, 2, "dec"),
    "T4": ("Restock to storage", 6, 3, "proc"),
    "T5": ("Scrap / return-to-vendor", 6, 4, "term"),
}

# edges: (src, tgt, label, dashed)
E = [
    ("R1", "R2", "", 0), ("R2", "R3", "", 0), ("R3", "R4", "yes", 0),
    ("R4", "S1", "", 0), ("S1", "S2", "", 0), ("S2", "S3", "", 0),
    ("S3", "P2", "reserve", 1),
    ("P1", "P2", "", 0), ("P2", "P3", "", 0), ("P3", "K2", "faces ready", 1),
    ("K1", "K2", "", 0), ("K2", "K3", "", 0),
    ("K3", "C1", "", 0), ("C1", "C2", "", 0), ("C2", "H1", "", 0),
    ("H1", "H2", "", 0), ("H2", "H3", "", 0),
    ("T1", "T2", "", 0), ("T2", "T3", "", 0), ("T3", "T4", "yes", 0),
    ("T4", "S1", "putaway", 1), ("T3", "T5", "no", 0),
]

STYLE = {
    "proc": "rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=11;",
    "dec":  "rhombus;whiteSpace=wrap;html=1;fillColor=#ffe6cc;strokeColor=#d79b00;fontSize=11;",
    "term": "rounded=1;arcSize=50;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=11;",
}

def geom(node):
    _, lane, col, kind = node
    lane_top = LANE_TOP0 + lane * LANE_H
    x = CONTENT_X0 + col * COL_W
    if kind == "dec":
        w, h = 128, 62
    else:
        w, h = BW, BH
    y = lane_top + (LANE_H - h) / 2
    return x, y, w, h

cells = []
# pool title
cells.append(f'<mxCell id="pool" value="Assa Abloy @ DHL Bemmel — Future-state process (Option B)" '
             f'style="text;html=1;fontStyle=1;fontSize=15;align=left;verticalAlign=middle;" vertex="1" parent="1">'
             f'<mxGeometry x="{TITLE_X}" y="-30" width="900" height="26" as="geometry"/></mxCell>')
# lane bands + titles
for i, (name, col) in enumerate(lanes):
    top = LANE_TOP0 + i * LANE_H
    cells.append(f'<mxCell id="lane{i}" value="" style="rounded=0;fillColor={col};strokeColor=#c7cede;" '
                 f'vertex="1" parent="1"><mxGeometry x="{TITLE_X}" y="{top}" width="{POOL_W}" height="{LANE_H}" as="geometry"/></mxCell>')
    cells.append(f'<mxCell id="lt{i}" value="{escape(name)}" '
                 f'style="text;html=1;horizontal=0;fontStyle=1;fontSize=11;align=center;verticalAlign=middle;'
                 f'fillColor=#eaeef6;strokeColor=#c7cede;" vertex="1" parent="1">'
                 f'<mxGeometry x="{TITLE_X}" y="{top}" width="{TITLE_W}" height="{LANE_H}" as="geometry"/></mxCell>')
# nodes
for nid, node in N.items():
    x, y, w, h = geom(node)
    cells.append(f'<mxCell id="{nid}" value="{escape(node[0])}" style="{STYLE[node[3]]}" vertex="1" parent="1">'
                 f'<mxGeometry x="{x:.0f}" y="{y:.0f}" width="{w}" height="{h}" as="geometry"/></mxCell>')
# edges
for k, (s, t, lbl, dashed) in enumerate(E):
    st = ("edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;endArrow=block;strokeColor=#5b6b7f;"
          + ("dashed=1;" if dashed else ""))
    cells.append(f'<mxCell id="e{k}" value="{escape(lbl)}" style="{st}" edge="1" parent="1" source="{s}" target="{t}">'
                 f'<mxGeometry relative="1" as="geometry"/></mxCell>')

xml = ('<mxfile host="app.diagrams.net">\n'
       '  <diagram name="Future-state process (Option B)">\n'
       f'    <mxGraphModel dx="1400" dy="900" grid="1" gridSize="10" guides="1" tooltips="1" '
       f'connect="1" arrows="1" fold="1" page="1" pageWidth="1700" pageHeight="900" background="#ffffff" math="0" shadow="1">\n'
       '      <root>\n        <mxCell id="0"/>\n        <mxCell id="1" parent="0"/>\n'
       + "\n".join("        " + c for c in cells) +
       '\n      </root>\n    </mxGraphModel>\n  </diagram>\n</mxfile>\n')

path = os.path.join(OUT, "warehouse_process.drawio")
with open(path, "w", encoding="utf-8") as f:
    f.write(xml)
print("Saved:", path, f"({len(N)} nodes, {len(E)} edges, {len(lanes)} lanes)")
