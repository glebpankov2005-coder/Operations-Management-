"""
Numbers for the 15-minute presentation (build_presentation.js reads outputs/reports/presentation_data.json).
Everything comes from phase1_metrics.json, except the hourly order profile, which is recomputed from the outbound data
exactly as dock_mhe_plan.py does for its figure.
"""
import json, os
import pandas as pd
from load_data import combined_outbound
from _util import REPORTS

M = json.load(open(os.path.join(REPORTS, "phase1_metrics.json"), encoding="utf-8"))
ob = combined_outbound()
for c in ["ORDER ARRIVE DATE", "ALOCATE DATE", "PICK DATE"]:
    ob[c] = pd.to_datetime(ob[c], errors="coerce")
orders = ob.drop_duplicates("ORDER NO")
hours = list(range(6, 19))
def share(s):
    v = s.dt.hour.value_counts(normalize=True) * 100
    return [round(float(v.get(h, 0.0)), 1) for h in hours]
profile = {"hours": [f"{h:02d}" for h in hours], "orders_arrive": share(orders["ORDER ARRIVE DATE"]),
           "lines_picked": share(ob["PICK DATE"])}
# share of stored loads older than one year (dead-stock signal), same calculation as warehouse_reports.py (D1 Fig 2b)
from load_data import all_storage
st = all_storage(); latest = st[sorted(st)[-1]]
age = (pd.to_datetime(latest["DATE"], errors="coerce").max() - pd.to_datetime(latest["ADD DATE"], errors="coerce")).dt.days
loads = pd.DataFrame({"LODNUM": latest["LODNUM"], "age": age}).dropna().drop_duplicates("LODNUM")
stock_age = {"loads": int(len(loads)), "over_1y_pct": round(float((loads["age"] > 365).mean() * 100), 1)}

# APA citations for the slide source lines, and the reference list for the 'Sources' slide
from references import cite_text, reference_list
DECK_SOURCES = ["S001", "S002", "S031", "S017", "S014", "S023", "S020", "S026", "S006", "S008", "S010"]
used = set()
cites = {s: cite_text(s, used) for s in DECK_SOURCES}
out = {"metrics": M, "hourly": profile, "stock_age": stock_age, "cites": cites, "references": reference_list(used)}
def no_nan(v):   # JSON has no NaN (JavaScript cannot read it): write null instead
    if isinstance(v, float) and v != v:
        return None
    if isinstance(v, dict):
        return {k: no_nan(x) for k, x in v.items()}
    if isinstance(v, list):
        return [no_nan(x) for x in v]
    return v
path = os.path.join(REPORTS, "presentation_data.json")
json.dump(no_nan(out), open(path, "w", encoding="utf-8"), ensure_ascii=False, default=str, allow_nan=False)
print("Saved", path, profile)

# ---- figure crops for the slides (the report figures carry their own titles and keys; the slides use their own)
from PIL import Image
FIGS = os.path.join(os.path.dirname(__file__), "..", "outputs", "figures"); DECK = os.path.join(FIGS, "deck")
os.makedirs(DECK, exist_ok=True)
for src, box, dst in [("layout_orderflow.png", (40, 39, 1085, 765), "layout_flow.png"),
                      ("inbound_zones.png", (58, 452, 527, 1340), "receiving_zoom.png"),
                      ("storage_how.png", (520, 108, 1219, 345), "fastpick_cut.png")]:
    Image.open(os.path.join(FIGS, src)).crop(box).save(os.path.join(DECK, dst))
# DHL logo for the cover (the client): the same file the group used in its Milestone 1 deck, cropped to the yellow field
import io, zipfile
M1 = os.path.join(os.path.dirname(__file__), "..", "deliverables", "DHL Group 3 Milestone 1 (v2).pptx")
with zipfile.ZipFile(M1) as z:
    logo = Image.open(io.BytesIO(z.read("ppt/media/image2.png"))).convert("RGB").crop((83, 91, 555, 390))
# keep only the red wordmark (yellow field -> transparent), so no box edge shows on the yellow cover in any renderer
g = logo.getchannel("G").point(lambda v: max(0, min(255, round((204 - v) / 199 * 255))))
mark = Image.new("RGBA", logo.size, (0xD4, 0x05, 0x11, 0)); mark.putalpha(g)
mark.save(os.path.join(DECK, "dhl_logo.png"))
print("Saved deck crops in", DECK)
