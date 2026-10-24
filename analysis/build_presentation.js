/*
 Final presentation (15 minutes) for the client, DHL Supply Chain - Project OTM, Group 3.

 Ten main slides (~13 minutes, leaving time for the hand-overs) plus an appendix for questions. Built for the client:
 DHL's own colours (yellow FFCC00, red D40511), the answer first, and every process told in DHL's terms - service to
 Assa Abloy, cost per order line, safety, growth and a step-by-step roadmap with the decisions DHL has to take.
 Consulting conventions: a full-sentence takeaway as every title, native (editable) charts, a source line on every
 slide, and speaker notes with the presenter and the timing.

 Every number comes from outputs/reports/presentation_data.json, which analysis/presentation_data.py builds from the
 project's metrics, so no figure is typed in by hand.

   npm install        (once: installs pptxgenjs from package.json)
   npm run deck       (= python analysis/presentation_data.py && node analysis/build_presentation.js)

 Output: deliverables/Presentation_Group3_Project_OTM.pptx
*/
const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");
const JSZip = require(require.resolve("jszip", { paths: [require.resolve("pptxgenjs")] }));

const ROOT = path.join(__dirname, "..");
const D = JSON.parse(fs.readFileSync(path.join(ROOT, "outputs/reports/presentation_data.json"), "utf8"));
const FIG = (f) => path.join(ROOT, "outputs/figures/deck", f);
const OUT = path.join(ROOT, "deliverables/Presentation_Group3_Project_OTM.pptx");

// ---------------------------------------------------------------- numbers (all from the metrics file)
const M = D.metrics, PC = M.performance_cost, CITE = D.cites;
const LT = PC.leadtime, ST = PC.storage, UC = PC.unit_cost, SORT = PC.sorting;
const P = M.peak, O = M.orders, A = M.abc, S = M.sku, LAY = M.layout;
const CPM = M.capacity_plan.measured;
const DM = M.dock_mhe, OD = DM.outbound_doors, REL = DM.order_release, DEP = DM.departure_plan, LZ = DM.loose_zone, IND = DM.inbound_doors;
const FP = M.picking.fast_pick, SP = M.picking.small_parts;
const SEG = Object.fromEntries(M.picking.segments.map((s) => [s.segment, s]));
const KPI = Object.fromEntries(PC.kpis.map((k) => [k.KPI, k]));
const DEC = M.decision, HAZ = M.design_evaluation.hazmat, FLEET = DM.fleet, STRESS = PC.stress;

// round half to even, like Python's round() and f"{x:.0f}" in the reports, so a slide never says 71 h where a report says 70 h
const r0 = (v) => { const f = Math.floor(v); return Math.abs(v - f - 0.5) < 1e-9 ? (f % 2 === 0 ? f : f + 1) : Math.round(v); };
const n0 = (v) => r0(v).toLocaleString("en-US");
const n1 = (v) => (r0(v * 10) / 10).toFixed(1);
const eurM = (v) => `€${(v / 1e6).toFixed(2)}M`;
const eurK = (v) => `€${r0(v / 1000)}k`;
const num = (s) => parseFloat(String(s).replace(/[^0-9.]/g, " ").trim().split(/\s+/)[0]);   // first number in a KPI text
const src = (sid) => `(${CITE[sid]})`;

const N_DAYS = r0(O.n_order_lines / P.lines.mean);
const ORDERS_DAY = O.n_orders / N_DAYS;
const WEB_PCT = Object.entries(O.order_type_mix).filter(([k]) => k.startsWith("WEB")).reduce((a, [, v]) => a + v, 0) / O.n_order_lines * 100;
const ON_TIME_TODAY = num(KPI["On-time shipment"]["Today (data)"]);
const PICK_TODAY = PC.pick_today_staffed_h, PICK_WORK = PC.pick_today_h, PICK_PEAK = PC.pick_today_staffed_h - PC.pick_today_h, PICK_NEW = PC.pick_future_h;
const PICK_CUT = r0((1 - PICK_NEW / PICK_TODAY) * 100);
const RACK_FILL = r0(ST.rack_need_peak / LAY.positions_total * 100);
const DOCK_TO_STOCK = num(KPI["Dock-to-stock time"]["Future (design)"]);
const STAGING_FILL = num(KPI["Outbound staging fill"]["Future (design)"]);
const SAFE_PCT = num(KPI["Trucks and pickers separated"]["Future (design)"]);
const LEVER = Object.fromEntries(PC.levers.map((l) => [l.Lever.startsWith("Batch") ? "batch" : "waves", { eur: l["Saved EUR/yr"], h: l["Saved h/day"] }]));
const LABOUR_SHARE = r0(PC.opex_by_group.Labour / PC.opex_total * 100);
const CONTINGENCY = r0(PC.capex_by_group.Contingency / (PC.capex_total - PC.capex_by_group.Contingency) * 100);
const OLD_LOADS = r0(D.stock_age.over_1y_pct);
const WT = DEC.weighted_totals, SENS = DEC.sensitivity;
const OPT = { A: "A - Conventional+", B: "B - Hybrid density", C: "C - Semi-automated" };
const FLEET_UNITS = Object.fromEntries(FLEET.map((f) => [f.Model.replace("Jungheinrich ", ""), f["Units recommended"]]));
const GROW = STRESS.find((r) => r.Volume === "150%");
const DOORS_OUT = 5;

// ---------------------------------------------------------------- theme (DHL colours), owners, canvas
const THEME = {
  name: "Project OTM for DHL", headFontFace: "Arial", bodyFontFace: "Arial",
  colors: { dk1: "1A1A1A", lt1: "FFFFFF", dk2: "262626", lt2: "F2F2F2", accent1: "D40511", accent2: "595959",
            accent3: "A6A6A6", accent4: "D9D9D9", accent5: "FFF0B3", accent6: "FFCC00", hlink: "D40511", folHlink: "595959" },
};
const HEX = THEME.colors;                 // hex values for the options that take hex only (charts, table borders)
// process owners: same names and colours as the reports (analysis/team.py)
const OWN = {
  Receiving: { name: "Vidhi", hex: "C2410C", scope: "unloading, checking, container unpacking, returns intake" },
  Storage:   { name: "Gleb", hex: "1D4ED8", scope: "putaway, racks, slotting, refills, stock control" },
  Picking:   { name: "Arnau", hex: "15803D", scope: "waves, picking, sorting at the put-to-light wall" },
  Shipping:  { name: "Rachel", hex: "7C3AED", scope: "packing, staging, dock doors, departure plan, loading" },
};
const FULL = (o) => (o.name === "Rachel" ? "Rachel Selvarathnam" : o.name);
const FLOW = { blue: "2B6CB0", green: "2F855A", red: "D40011", orange: "D97706" };   // flow colours of the layout drawing

const L = 0.6, CW = 12.133, XR = L + CW, Y0 = 1.9;

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "Project OTM - final presentation for DHL Supply Chain, Group 3";
pres.subject = "Redesign of the Assa Abloy warehouse operated by DHL Supply Chain in Bemmel";
pres.author = "Group 3: Vidhi, Gleb, Arnau, Rachel Selvarathnam";
pres.company = "HAN University of Applied Sciences";
const C = pres.SchemeColor;

// ---------------------------------------------------------------- layouts
pres.defineSlideMaster({
  title: "COVER", background: { color: C.accent6 },
  objects: [
    { image: { path: FIG("dhl_logo.png"), x: 0.8, y: 0.55, w: 2.0, h: 2.0 * 299 / 472 } },
    { placeholder: { options: { name: "kicker", type: "body", x: 0.8, y: 2.05, w: 11, h: 0.4, fontSize: 12, bold: true, color: C.accent1, charSpacing: 2, margin: 0, valign: "middle" }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 2.55, w: 11.4, h: 1.75, fontSize: 38, bold: true, color: C.text1, margin: 0, valign: "top", align: "left" }, text: "" } },
    { placeholder: { options: { name: "subtitle", type: "body", x: 0.8, y: 4.35, w: 10.6, h: 0.85, fontSize: 18, color: C.text2, margin: 0, valign: "top" }, text: "" } },
    { placeholder: { options: { name: "meta", type: "body", x: 0.8, y: 6.0, w: 11.7, h: 0.8, fontSize: 12, color: C.text2, margin: 0, valign: "top" }, text: "" } },
  ],
});
const contentObjects = (extra = []) => [
  { placeholder: { options: { name: "tracker", type: "body", x: L, y: 0.3, w: 8.9, h: 0.28, fontSize: 9, color: C.accent3, charSpacing: 1, margin: 0, valign: "middle" }, text: "" } },
  { placeholder: { options: { name: "title", type: "title", x: L, y: 0.66, w: CW, h: 1.05, fontSize: 20, bold: true, color: C.text2, margin: 0, valign: "top", align: "left" }, text: "" } },
  { placeholder: { options: { name: "source", type: "body", x: L, y: 7.0, w: 8.3, h: 0.4, fontSize: 9, color: C.accent2, margin: 0, valign: "top" }, text: "" } },
  { text: { text: "Group 3 · prepared for DHL Supply Chain · confidential", options: { x: 9.0, y: 7.0, w: 3.3, h: 0.2, fontSize: 9, color: C.accent3, align: "right", margin: 0, valign: "top" } } },
  ...extra,
];
const SLIDE_NO = { x: 12.38, y: 7.0, w: 0.35, h: 0.2, fontSize: 9, color: HEX.accent2, align: "right", margin: 0 };
pres.defineSlideMaster({ title: "CONTENT", background: { color: C.background1 }, objects: contentObjects(), slideNumber: SLIDE_NO });
pres.defineSlideMaster({
  title: "APPENDIX", background: { color: C.background1 }, slideNumber: SLIDE_NO,
  objects: contentObjects([{ text: { text: "APPENDIX", options: { x: 11.48, y: 0.28, w: 1.25, h: 0.3, fontSize: 9, bold: true, charSpacing: 2, color: C.text2, align: "center", valign: "middle", margin: 0, fill: { color: C.accent6 } } } }]),
});
pres.defineSlideMaster({
  title: "CLOSE", background: { color: C.accent6 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 2.2, w: 11.5, h: 0.9, fontSize: 40, bold: true, color: C.text1, margin: 0, valign: "middle", align: "left" }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.8, y: 3.35, w: 11.5, h: 2.8, fontSize: 16, color: C.text2, margin: 0, valign: "top" }, text: "" } },
  ],
});

// ---------------------------------------------------------------- helpers
const TRACK = ["Today", "Our solution", "Processes", "Value for DHL", "Roadmap"];
function trackerRuns(cur) {
  if (!TRACK.includes(cur)) return [{ text: cur.toUpperCase(), options: { bold: true, color: C.accent1 } }];
  const runs = [];
  TRACK.forEach((t, i) => {
    if (i) runs.push({ text: "   ·   " });
    runs.push({ text: t.toUpperCase(), options: t === cur ? { bold: true, color: C.accent1 } : {} });
  });
  return runs;
}
function ownerTag(s, proc, label) {
  const o = OWN[proc];
  s.addShape(pres.shapes.RECTANGLE, { x: 9.95, y: 0.37, w: 0.13, h: 0.13, fill: { color: o.hex }, line: { type: "none" }, objectName: "Owner marker" });
  s.addText([{ text: o.name, options: { bold: true, color: C.text1 } }, { text: ` · ${label || proc + " owner"}` }],
    { x: 10.16, y: 0.3, w: 2.57, h: 0.28, fontSize: 10, color: C.accent2, margin: 0, valign: "middle", isTextBox: true, objectName: "Presenter" });
}
function slide(section, title, source, opt = {}) {
  const s = pres.addSlide({ masterName: opt.appendix ? "APPENDIX" : "CONTENT", sectionTitle: section });
  s.addText(trackerRuns(opt.tracker || section), { placeholder: "tracker" });
  s.addText(title, { placeholder: "title" });
  s.addText(source, { placeholder: "source" });
  if (opt.owner) ownerTag(s, opt.owner, opt.ownerLabel);
  return s;
}
function txt(s, text, o) {
  s.addText(text, Object.assign({ isTextBox: true, margin: 0, fontSize: 14, color: C.text1, valign: "top" }, o));
}
function box(s, x, y, w, h, fill, o = {}) {
  s.addShape(pres.shapes.RECTANGLE, Object.assign({ x, y, w, h, fill: { color: fill }, line: { type: "none" } }, o));
}
function hline(s, x, y, w, color = C.accent4, width = 0.75) {
  s.addShape(pres.shapes.LINE, { x, y, w, h: 0, line: { color, width } });
}
function dots(s, x, y, n, of = 3) {     // gap / impact rating: filled dots out of three
  for (let i = 0; i < of; i++)
    s.addShape(pres.shapes.OVAL, { x: x + i * 0.2, y, w: 0.13, h: 0.13, fill: { color: i < n ? C.accent1 : C.accent4 }, line: { type: "none" } });
}
function badge(s, x, y, label, color, d = 0.32) {   // numbered circle like the badges in the layout drawing
  s.addText(label, { shape: pres.shapes.OVAL, x, y, w: d, h: d, fill: { color: C.background1 }, line: { color, width: 2 },
    fontSize: 11, bold: true, color, align: "center", valign: "middle", margin: 0 });
}
function numberRows(s, x, y, w, rowH, rows, o = {}) {   // "1  Lead. text" rows used for how-it-works lists
  rows.forEach(([lead, body], i) => {
    const yy = y + i * rowH;
    txt(s, String(i + 1), { x, y: yy - 0.04, w: 0.35, h: 0.4, fontSize: 18, bold: true, color: C.accent1 });
    txt(s, [{ text: lead + " ", options: { bold: true, color: C.text2 } }, { text: body }], { x: x + 0.42, y: yy, w: w - 0.42, h: rowH - 0.08, fontSize: o.size || 13 });
  });
}
function stat(s, x, y, w, big, label, o = {}) {      // big number with a label underneath
  txt(s, big, { x, y, w, h: o.bh || 0.55, fontSize: o.size || 30, bold: true, color: o.color || C.accent1 });
  txt(s, label, { x, y: y + (o.bh || 0.55), w, h: o.lh || 0.5, fontSize: o.lsize || 12, color: C.text1 });
}
function chevrons(s, labels, y, h, o = {}) {   // a row of chevrons that fills the content width exactly
  const cw = (CW + (labels.length - 1) * 0.12) / labels.length, step = cw - 0.12;
  labels.forEach((t, i) => s.addText(t, { shape: i ? pres.shapes.CHEVRON : pres.shapes.PENTAGON, x: L + i * step, y, w: cw, h,
    fill: { color: o.fill || C.text2 }, line: { type: "none" }, fontSize: o.size || 14, bold: true, color: o.color || C.background1,
    align: "center", valign: "middle", margin: [18, 18, 0, 0] }));
  return step;
}
function chartBase(extra) {
  return Object.assign({
    catAxisLabelColor: HEX.accent2, valAxisLabelColor: HEX.accent2, catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt",
    catAxisLabelFontSize: 12, valAxisLabelFontSize: 11, catAxisLineShow: true, catAxisLineColor: HEX.accent3, valAxisLineShow: false,
    valGridLine: { color: "E6E6E6", size: 0.75 }, catGridLine: { style: "none" },
    showLegend: false, legendFontFace: "+mn-lt", legendFontSize: 12, legendColor: HEX.accent2,
    dataLabelFontFace: "+mn-lt", dataLabelFontSize: 12, dataLabelColor: HEX.dk1, showTitle: false,
  }, extra);
}
function chartHead(s, x, y, w, title, sub) {
  txt(s, title, { x, y, w, h: 0.3, fontSize: 13, bold: true, color: C.text2 });
  if (sub) txt(s, sub, { x, y: y + 0.29, w, h: 0.26, fontSize: 11, color: C.accent2 });
}
function notes(s, who, time, say) {
  s.addNotes(`PRESENTER: ${who}  ·  about ${time}\n\n${say}`);
}
const thB = { type: "solid", pt: 1, color: HEX.dk1 }, rowB = { type: "solid", pt: 0.75, color: HEX.accent4 }, noB = { type: "none" };
const th = (t, a = "left") => ({ text: t, options: { bold: true, fontSize: 11, color: C.accent2, align: a, valign: "bottom", border: [noB, noB, thB, noB] } });
const td = (t, o = {}) => ({ text: t, options: Object.assign({ valign: "middle", border: [noB, noB, rowB, noB] }, o) });

// ================================================================ 1. COVER
pres.addSection({ title: "Summary" });
let s = pres.addSlide({ masterName: "COVER", sectionTitle: "Summary" });
s.addText("PROJECT OTM  ·  PREPARED FOR DHL SUPPLY CHAIN, BEMMEL", { placeholder: "kicker" });
s.addText("A faster, leaner Assa Abloy warehouse in the same building", { placeholder: "title" });
s.addText("Our redesign of receiving, storage, picking and shipping — and what it means for service, cost and growth", { placeholder: "subtitle" });
s.addText([
  { text: `Group 3  ·  ${Object.entries(OWN).map(([p, o]) => `${FULL(o)} (${p})`).join("  ·  ")}`, options: { breakLine: true } },
  { text: "HAN University of Applied Sciences, OPERMB04  ·  based on Assa Abloy warehouse data, April–June 2025" },
], { placeholder: "meta" });
notes(s, "Gleb (Storage)", "0:15",
  "Good morning. We are Group 3. Over the last weeks we redesigned the Assa Abloy warehouse that DHL runs in Bemmel. " +
  "Each of us owns one process — Vidhi receiving, me storage, Arnau picking and Rachel shipping — and each of us presents their own part.");

// ================================================================ 2. EXECUTIVE SUMMARY
s = slide("Summary",
  `Our design lets DHL keep its promise to Assa Abloy at a lower cost: ${LT.future_within_24h_pct}% of orders out within 24 hours, ${PICK_CUT}% fewer picker-hours, in the same building`,
  `Source: WMS data April–June 2025 ${src("S002")}; design values modelled in Deliverables 2 and 3`,
  { tracker: "Executive summary", owner: "Storage", ownerLabel: "presenter" });
[
  ["Today", `DHL ships ~${n0(P.lines.mean)} order lines a day for Assa Abloy from ${n0(A.n_skus_shipped)} different items. All orders are released at once in the evening: picking peaks at 08:00, only ${n1(ON_TIME_TODAY)}% of lines are staged on time and ${LT.today_within_24h_pct}% of orders leave within 24 hours.`],
  ["Our answer", `A one-way flow from dock to trailer: a fast-pick area for the ${n0(FP.skus)} best-sellers, batch picking with a put-to-light wall, and three waves planned back from fixed trailer departures. It fits in ${n0(LAY.total_area_m2)} of the 7,000 m².`],
  ["What DHL gets", `${LT.future_within_24h_pct}% of orders out within 24 h and ≥ 98% on time; ~${r0(PICK_NEW)} instead of ~${r0(PICK_TODAY)} picker-hours a day (${eurK(PC.saving_year)} a year); €${UC.per_order_line.toFixed(2)} per order line; trucks and pickers fully separated.`],
  ["How to start", `With the low-cost process changes (${eurM(PC.capex_process)}, payback ~${PC.payback_process_years.toFixed(1)} years). The racking decision comes last. Main risk: stock growth fills the racks in ~${r0(ST.months_headroom)} months.`],
].forEach(([lab, body], i) => {
  const y = Y0 + 0.05 + i * 1.2;
  hline(s, L, y, 7.85);
  txt(s, lab, { x: L, y: y + 0.14, w: 1.7, h: 0.4, fontSize: 14, bold: true, color: C.accent1 });
  txt(s, body, { x: L + 1.85, y: y + 0.14, w: 6.0, h: 1.0, fontSize: 13 });
});
hline(s, L, Y0 + 0.05 + 4 * 1.2, 7.85);
box(s, 8.85, Y0 + 0.05, 3.88, 4.8, C.accent6, { objectName: "What DHL gets panel" });
txt(s, "WHAT DHL GETS", { x: 9.1, y: Y0 + 0.22, w: 3.4, h: 0.25, fontSize: 10, bold: true, charSpacing: 1, color: C.text1 });
[
  [`${LT.future_within_24h_pct}%`, `of orders out within 24 h (today ${LT.today_within_24h_pct}%)`],
  ["≥ 98%", `of lines staged on time (today ${r0(ON_TIME_TODAY)}%)`],
  [`−${PICK_CUT}%`, `picker-hours a day: ~${r0(PICK_TODAY)} → ~${r0(PICK_NEW)}`],
  [`${PC.payback_process_years.toFixed(1)} yrs`, `payback of the ${eurM(PC.capex_process)} process changes`],
].forEach(([big, lab], i) => stat(s, 9.1, Y0 + 0.6 + i * 1.05, 3.4, big, lab, { lh: 0.42 }));
notes(s, "Gleb (Storage)", "1:00",
  `Our answer first. Today about ${n0(P.lines.mean)} order lines a day go out, but all orders are released at once in the evening, so the floor is overloaded at eight in the morning and only half of the lines are staged on time. ` +
  "We redesigned the warehouse around the flow: a fast-pick area for the best-sellers, batch picking, a put-to-light wall and three waves planned backwards from fixed trailer departures. " +
  `For DHL that means ${LT.future_within_24h_pct}% of orders out within 24 hours instead of ${LT.today_within_24h_pct}%, about ${r0(PICK_NEW)} instead of ${r0(PICK_TODAY)} picker-hours a day, and it all fits in the current building. ` +
  "We propose to start with the cheap process changes and take the racking decision last.");

// ================================================================ 3. TODAY - THE PROBLEM
pres.addSection({ title: "Today" });
s = slide("Today",
  `Today all orders are released at once: picking peaks at 08:00, half the lines ship late and the racks are almost full`,
  `Source: WMS data April–June 2025 ${src("S002")}; picker-hours modelled (Deliverable 3 §2.2)`,
  { owner: "Picking", ownerLabel: "presenter" });
chartHead(s, L, Y0, 6.7, "When orders arrive vs when lines are picked", "share of the day's total per hour of the day, % (April–June 2025)");
s.addChart([
  { type: pres.charts.BAR, data: [{ name: "Orders arriving", labels: D.hourly.hours, values: D.hourly.orders_arrive }], options: { barDir: "col", chartColors: [HEX.accent3], barGapWidthPct: 35 } },
  { type: pres.charts.LINE, data: [{ name: "Lines picked", labels: D.hourly.hours, values: D.hourly.lines_picked }], options: { chartColors: [HEX.accent1], lineSize: 3, lineDataSymbol: "circle", lineDataSymbolSize: 7 } },
], chartBase({ x: 0.45, y: 2.5, w: 6.9, h: 4.15, showLegend: true, legendPos: "b", valAxisMaxVal: 40, valAxisMinVal: 0, valAxisMajorUnit: 10,
  valAxisLabelFormatCode: '0"%"', showCatAxisTitle: true, catAxisTitle: "hour of the day", catAxisTitleFontSize: 11, catAxisTitleColor: HEX.accent2, catAxisTitleFontFace: "+mn-lt" }));
txt(s, `Picking peaks at 08:00: ${REL.pick_peak_over_mean_active_hour}× the average hour`, { x: 1.3, y: 2.62, w: 2.6, h: 0.5, fontSize: 11, bold: true, color: C.accent1 });
txt(s, `${REL.orders_arrive_15_17_pct}% of orders arrive 15:00–17:00, released together in the evening`, { x: 3.9, y: 2.62, w: 2.6, h: 0.5, fontSize: 11, bold: true, color: C.accent2, align: "right" });
const GX = 7.75, GW = XR - GX;
txt(s, "What it costs DHL today", { x: GX, y: Y0, w: GW, h: 0.3, fontSize: 13, bold: true, color: C.text2 });
[
  ["Service", `${n1(ON_TIME_TODAY)}% of lines staged on time; ${LT.today_within_24h_pct}% of orders out within 24 h, the slowest 10% take over ${r0(LT.today_p90_h)} h`, 3],
  ["Cost", `~${r0(PICK_TODAY)} picker-hours a day: every tour picks one order, and staff is planned for the 08:00 peak`, 3],
  ["Space", `racks full in ~${r0(ST.months_headroom)} months at the current growth; slotting matches demand for only ${r0(A.agreement_with_wms_pct)}% of items`, 2],
].forEach(([obj, today, gap], i) => {
  const y = Y0 + 0.45 + i * 1.12;
  hline(s, GX, y, GW);
  txt(s, obj, { x: GX, y: y + 0.13, w: 1.2, h: 0.3, fontSize: 14, bold: true, color: C.text2 });
  txt(s, today, { x: GX + 1.25, y: y + 0.13, w: 3.05, h: 0.95, fontSize: 12.5 });
  dots(s, XR - 0.55, y + 0.2, gap);
});
hline(s, GX, Y0 + 0.45 + 3 * 1.12, GW);
s.addText([{ text: "The cause: ", options: { bold: true } }, { text: "how work is released and picked — not a lack of space." }],
  { x: GX, y: 5.85, w: GW, h: 0.8, fontSize: 13, color: C.text1, fill: { color: C.accent6 }, margin: [10, 10, 4, 4], valign: "middle", isTextBox: true });
notes(s, "Arnau (Picking)", "1:30",
  `This chart is the core of the problem. The grey bars show when orders arrive: ${REL.orders_arrive_15_17_pct}% come in between three and five in the afternoon. ` +
  "They are all released in one go in the evening, so the red line — picking — peaks at eight the next morning. " +
  `For DHL this costs on three fronts. Service: only ${n1(ON_TIME_TODAY)}% of lines are staged on time and ${LT.today_within_24h_pct}% of orders leave within 24 hours. ` +
  `Cost: about ${r0(PICK_TODAY)} picker-hours a day, because staff is planned for the peak and every tour picks one order. Space: the racks are almost full. ` +
  "The cause is the way work is released and picked, so that is what our design changes. Vidhi shows the solution.");

// ================================================================ 4. OUR SOLUTION - LAYOUT
pres.addSection({ title: "Our solution" });
s = slide("Our solution", `One-way flow from dock to trailer in ${n0(LAY.total_area_m2)} m² — the design fits the current 7,000 m² building`,
  `Source: team layout drawing, to scale (Deliverable 2 §2); option choice: team decision matrix (Deliverable 1 §15)`,
  { owner: "Receiving", ownerLabel: "presenter" });
const imgH = 4.85, imgW = imgH * 1045 / 726;
s.addImage({ path: FIG("layout_flow.png"), x: L, y: Y0, w: imgW, h: imgH, altText: "Warehouse layout with the numbered route of an order line" });
const SX = 8.05, SW = XR - SX;
txt(s, "The route of an order line", { x: SX, y: Y0, w: SW, h: 0.3, fontSize: 13, bold: true, color: C.text2 });
[
  ["1", FLOW.blue, "Trailers unloaded and checked at R2 / R3"],
  ["C", FLOW.orange, "Containers unpacked at R1, built onto pallets"],
  ["2", FLOW.blue, "Reach truck puts the pallets away"],
  ["3", FLOW.green, "Refills drop cases into the fast-pick area"],
  ["4", FLOW.red, "Orders picked in waves, taken to packing"],
  ["5", FLOW.red, "Sorted at the put-to-light wall and packed"],
  ["6", FLOW.red, "Staged in the lane of its door and loaded"],
].forEach(([b, col, t], i) => {
  const y = Y0 + 0.4 + i * 0.43;
  badge(s, SX, y, b, col, 0.3);
  txt(s, t, { x: SX + 0.44, y: y + 0.03, w: SW - 0.44, h: 0.3, fontSize: 12.5 });
});
hline(s, SX, 5.5, SW);
[[`${LAY.pct_of_7000}%`, "of the 7,000 m² used"], [n0(LAY.positions_total), "pallet places"], ["3 + 5", "doors in / out"]].forEach(([big, lab], i) =>
  stat(s, SX + i * (SW / 3), 5.6, SW / 3 - 0.1, big, lab, { size: 22, bh: 0.42, lh: 0.3, lsize: 11, color: C.text2 }));
txt(s, [{ text: "Why this option: ", options: { bold: true } }, { text: `best of three on seven criteria (${WT[OPT.B].toFixed(2)} of 5). Full automation scored ${WT[OPT.C].toFixed(2)} but costs more and is less flexible (appendix).` }],
  { x: SX, y: 6.35, w: SW, h: 0.5, fontSize: 10.5, color: C.accent2 });
notes(s, "Vidhi (Receiving)", "1:30",
  "This is our layout, drawn to scale, with the route of one order line. Goods come in on the west wall: pallet trailers at doors R2 and R3, and loose containers at R1. " +
  "The reach truck puts the pallets away in single-deep racks and refills the fast-pick row along the south wall from behind. " +
  "Pickers work that row and bring the goods to packing, and orders wait in the lane of their shipping door on the east wall. Everything moves one way. " +
  `It uses ${LAY.pct_of_7000}% of the 7,000 square metres, so no extra building is needed. We chose this from three options; full automation scored almost as high but costs more and copes less well with two-metre items.`);

// ================================================================ 5. RECEIVING
pres.addSection({ title: "Processes" });
s = slide("Processes", `Receiving keeps pallet trailers and loose containers apart, so a 40 ft container is unloaded and palletised in ~${IND.container_door_h.toFixed(1)} hours`,
  `Source: inbound receipts April–June 2025 ${src("S002")}; dock-to-stock benchmark ${src("S023")}; Deliverable 2 §4.1 and §4.6`,
  { owner: "Receiving" });
const rH = 4.85, rW = rH * 469 / 888;
s.addImage({ path: FIG("receiving_zoom.png"), x: L, y: Y0, w: rW, h: rH, altText: "Receiving and the container zone, enlarged, with letters A to I" });
const KX = L + rW + 0.4, KW = 8.5 - KX;
txt(s, "How it works", { x: KX, y: Y0, w: KW, h: 0.3, fontSize: 13, bold: true, color: C.text2 });
numberRows(s, KX, Y0 + 0.45, KW, 1.3, [
  ["Pallet trailers at R2 / R3.", "Unloaded into a lane (A–B), counted, checked and scanned at the bench (C), then collected by the reach truck at the pick-up point (D)."],
  ["Loose containers at R1.", `Cartons roll out on a conveyor (F); two people build ${LZ.build_spots} pallets at once, one per item (G), with room for ${LZ.buffer_pallets} finished pallets (H) and a wrap-and-label station (I).`],
  ["Flexible space.", `On big-container days half of the R2 area (E) joins the container zone: +${n0(LZ.r2_lend_m2)} m².`],
], { size: 13 });
const PX = 8.85, PW = XR - PX;
box(s, PX, Y0, PW, 4.85, C.background2, { objectName: "Receiving numbers" });
[
  [n0(CPM.inbound_loads_day), `inbound loads a day (busiest day ${n0(CPM.inbound_max_day)})`],
  [`${r0(CPM.inbound_asia_origin_pct)}%`, "of loads come from Asia, loose in containers"],
  [`${LZ.share_fit_with_r2_pct}%`, `of containers fit the zone (${LZ.share_fit_zone_pct}% without R2's half)`],
  [`~${n1(DOCK_TO_STOCK)} h`, "dock-to-stock per pallet trailer (benchmark < 3.5 h)"],
].forEach(([big, lab], i) => stat(s, PX + 0.25, Y0 + 0.2 + i * 1.15, PW - 0.5, big, lab, { size: 28 }));
notes(s, "Vidhi (Receiving)", "1:30",
  `Receiving handles about ${n0(CPM.inbound_loads_day)} loads a day, and ${r0(CPM.inbound_asia_origin_pct)}% come loose in containers from Asia. The key idea is to keep the two apart. ` +
  "Pallet trailers dock at R2 and R3: pallets go into a lane, are checked and scanned at the bench, and the reach truck collects them — letters A to D. " +
  `Containers dock at R1: cartons roll out on a conveyor and two people build ${LZ.build_spots} pallets at once, one per item — F to I. ` +
  `On the few big-container days we lend half of the R2 area, so ${LZ.share_fit_with_r2_pct}% of containers fit. A pallet trailer is in stock in about ${n1(DOCK_TO_STOCK)} hours, well inside the 3.5-hour benchmark. Gleb takes over from the pick-up point.`);

// ================================================================ 6. STORAGE
s = slide("Processes", `${n0(LAY.positions_total)} rack places hold today's peak at ${RACK_FILL}% full — but at the current stock growth they are full in about ${r0(ST.months_headroom)} months`,
  `Source: stock snapshots 1 April, 1 May and 1 June 2025 ${src("S002")}; Deliverable 2 §2–3 and Deliverable 3 §4`,
  { owner: "Storage" });
chartHead(s, L, Y0, 5.6, "Pallet places at the peak (June 2025)");
s.addChart(pres.charts.BAR, [{ name: "Pallet places", labels: ["Occupied today", "Needed in our design", "Rack places in our design"], values: [ST.occupied_peak, ST.rack_need_peak, LAY.positions_total] }],
  chartBase({ x: 0.45, y: 2.25, w: 5.75, h: 3.15, barDir: "col", chartColors: [HEX.accent3, HEX.accent1, HEX.dk2], barGapWidthPct: 55,
    valAxisHidden: true, valGridLine: { style: "none" }, valAxisMinVal: 0, valAxisMaxVal: 10500,
    showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "#,##0", dataLabelFontSize: 14, dataLabelFontBold: true, catAxisLabelFontSize: 11 }));
txt(s, `−${n0(SP.freed_rack_locations)} places: ${n0(SP.skus)} small, slow items move to bin shelving next to packing.`,
  { x: L, y: 5.42, w: 5.6, h: 0.45, fontSize: 11, color: C.accent2 });
s.addText([{ text: "Risk: ", options: { bold: true } },
  { text: `stock grows ~${r0(ST.growth_per_quarter_pct)}% per quarter: racks full in ~${r0(ST.months_headroom)} months (~${r0(ST.months_headroom_12)} with the reserved 12th module). ${OLD_LOADS}% of loads are over a year old — clearing dead stock is the main lever.` }],
  { x: L, y: 5.92, w: 5.6, h: 0.85, fontSize: 12, color: C.text1, fill: { color: C.accent6 }, margin: [10, 10, 4, 4], valign: "middle", isTextBox: true });
const HX = 6.75, HW = XR - HX;
txt(s, "How storage works", { x: HX, y: Y0, w: HW, h: 0.3, fontSize: 13, bold: true, color: C.text2 });
numberRows(s, HX, Y0 + 0.42, HW, 0.8, [
  ["Every pallet reachable.", `Single-deep racks back-to-back, ${LAY.levels} levels, ${LAY.storage_aisles} aisles; one reach-truck type (ETV 216i) for putaway and refills.`],
  ["A place by demand.", "Fast movers' reserve close to the fast-pick area, slow movers further away; heavy pallets low; long goods in their own module."],
  ["Safe refills from behind.", `${FP.flow_bays} carton-flow bays (${n0(FP.flow_lanes)} lanes): the reach truck refills from the back, pickers take from the front — they never share an aisle.`],
], { size: 12.5 });
const fcW = HW - 0.2, fcH = fcW * 237 / 699;
s.addImage({ path: FIG("fastpick_cut.png"), x: HX + 0.1, y: 6.78 - fcH, w: fcW, h: fcH, altText: "Cross-section of the fast-pick area: refill side, carton flow, pick aisle" });
notes(s, "Gleb (Storage)", "1:30",
  `Storage keeps every pallet and keeps the pick faces full. At the June peak ${n0(ST.occupied_peak)} pallet places were in use. ` +
  `We move ${n0(SP.skus)} small, slow items to bin shelving, which frees ${n0(SP.freed_rack_locations)} places, so the design needs ${n0(ST.rack_need_peak)} of its ${n0(LAY.positions_total)} places — ${RACK_FILL}% full. ` +
  "All racks are single-deep, so every pallet can be reached without moving another. The fast-pick area is refilled from behind, so reach trucks and pickers never share an aisle — good for safety. " +
  `The risk for DHL: stock grew about ${r0(ST.growth_per_quarter_pct)}% in one quarter, so at that rate the racks are full in about ${r0(ST.months_headroom)} months. Clearing dead stock with Assa Abloy is the first lever; a 12th rack module is kept in reserve.`);

// ================================================================ 7. PICKING
s = slide("Processes", `Batch picking from a fast-pick area cuts picking from ~${r0(PICK_TODAY)} to ~${r0(PICK_NEW)} picker-hours a day`,
  `Source: model on WMS order lines April–June 2025 ${src("S002")} (Deliverable 3 §2.2); today = one order per tour, staffed for the 08:00 peak; batching ${src("S014")}`,
  { owner: "Picking" });
chartHead(s, L, Y0, 5.4, "Picker-hours on an average day", "modelled on the same order lines");
s.addChart(pres.charts.BAR, [
  { name: "Picking work", labels: [`Today: ${n1(PICK_TODAY)} h`, `Our design: ${n1(PICK_NEW)} h`], values: [PICK_WORK, PICK_NEW] },
  { name: "Extra staff for the 08:00 peak", labels: [`Today: ${n1(PICK_TODAY)} h`, `Our design: ${n1(PICK_NEW)} h`], values: [PICK_PEAK, 0] },
], chartBase({ x: 0.45, y: 2.5, w: 5.4, h: 4.25, barDir: "col", barGrouping: "stacked", chartColors: [HEX.dk2, HEX.accent1], barGapWidthPct: 70,
  valAxisMinVal: 0, valAxisMaxVal: 35, valAxisMajorUnit: 10, showLegend: true, legendPos: "b", catAxisLabelFontSize: 13,
  showValue: true, dataLabelPosition: "ctr", dataLabelFormatCode: "0.0;;;", dataLabelColor: "FFFFFF", dataLabelFontSize: 13, dataLabelFontBold: true }));
const KX2 = 6.35, KW2 = XR - KX2;
txt(s, "How it works", { x: KX2, y: Y0, w: KW2, h: 0.3, fontSize: 13, bold: true, color: C.text2 });
numberRows(s, KX2, Y0 + 0.42, KW2, 1.08, [
  ["Split orders by size.", `${r0(SEG.small.pct_orders)}% of orders are small and go on a trolley with 6 totes; the other ${r0(SEG.large.pct_orders)}% carry ${r0(SEG.large.pct_volume)}% of the volume and are picked straight onto a pallet.`],
  ["Best-sellers close by.", `The ${n0(FP.skus)} best-sellers sit in the fast-pick area: ${r0(ST.fast_hit_pct)}% of lines are picked there, with ~${r0(ST.walk_per_line_m)} m of walking per line.`],
  ["Batch, then sort.", `One trolley tour picks ~${SORT.lines_per_tour} lines for many orders; the put-to-light wall (${M.putwall_design.wall.slots} slots) sorts them into orders and checks every item.`],
  ["Three waves a day.", "Instead of one evening release — no 08:00 rush; the first wave starts at 06:00."],
], { size: 12.5 });
notes(s, "Arnau (Picking)", "1:30",
  `Today picking is the biggest block of labour. In our model it takes about ${n1(PICK_TODAY)} picker-hours a day: ${n1(PICK_WORK)} hours of work, because every tour picks one order across the whole building, plus ${n1(PICK_PEAK)} hours of extra staff for the eight o'clock peak. ` +
  `Our design needs ${n1(PICK_NEW)} hours. Orders are split by size: ${r0(SEG.small.pct_orders)}% are small and go on a trolley, large ones go straight onto a pallet. ` +
  `The ${n0(FP.skus)} best-sellers sit in the fast-pick area, where ${r0(ST.fast_hit_pct)}% of lines are picked. One tour picks for many orders, and the put-to-light wall sorts them and checks every item, which protects accuracy. ` +
  "And work is released in three waves, so the morning peak disappears. These times are modelled, so we propose a time study before go-live.");

// ================================================================ 8. SHIPPING
s = slide("Processes", `A fixed trailer departure plan gets ${LT.future_within_24h_pct}% of orders out within 24 hours and every wave staged before its trailer leaves`,
  `Source: shipments April–June 2025 ${src("S002")}; departure plan and lead times modelled (Deliverable 2 §4.5, Deliverable 3 §2.1)`,
  { owner: "Shipping" });
chartHead(s, L, Y0, 5.7, "Service today vs our design, %");
s.addChart(pres.charts.BAR, [
  { name: "Today", labels: ["Orders out within 24 h", "Lines staged on time"], values: [LT.today_within_24h_pct, ON_TIME_TODAY] },
  { name: "Our design", labels: ["Orders out within 24 h", "Lines staged on time"], values: [LT.future_within_24h_pct, 98] },
], chartBase({ x: 0.45, y: 2.2, w: 5.85, h: 2.75, barDir: "col", barGrouping: "clustered", chartColors: [HEX.accent3, HEX.accent1], barGapWidthPct: 60,
  valAxisHidden: true, valGridLine: { style: "none" }, valAxisMinVal: 0, valAxisMaxVal: 115, showLegend: true, legendPos: "r",
  showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: '0"%"', dataLabelFontSize: 13, dataLabelFontBold: true }));
const hx = (t) => { const [h, m] = t.split(":").map(Number); return 1.5 + (h + m / 60 - 6) * (4.75 / 11); };
txt(s, `The day plan: three waves feed ${DEP.trailers_planned} trailer departures`, { x: L, y: 5.1, w: 5.8, h: 0.28, fontSize: 12, bold: true, color: C.text2 });
txt(s, "Waves", { x: L, y: 5.5, w: 0.85, h: 0.3, fontSize: 10, color: C.accent2, valign: "middle" });
txt(s, "Trailers", { x: L, y: 5.95, w: 0.85, h: 0.3, fontSize: 10, color: C.accent2, valign: "middle" });
const waveFill = [C.text2, C.accent1, C.accent6], waveText = [C.background1, C.background1, C.text1];
DEP.waves.forEach((w, i) => s.addText(w.wave, { shape: pres.shapes.RECTANGLE, x: hx(w.start), y: 5.5, w: hx(w.end) - hx(w.start) - 0.03, h: 0.3,
  fill: { color: waveFill[i] }, line: { type: "none" }, fontSize: 10, bold: true, color: waveText[i], align: "center", valign: "middle", margin: 0 }));
const seen = {};
DEP.departures.forEach((d) => {
  for (let k = 0; k < d.Trailers; k++) {
    const stack = seen[d.Departure] = (seen[d.Departure] || 0) + 1;
    s.addShape(pres.shapes.ISOSCELES_TRIANGLE, { x: hx(d.Departure) - 0.065, y: 6.13 - (stack - 1) * 0.16, w: 0.13, h: 0.13, fill: { color: C.text2 }, line: { type: "none" } });
  }
});
hline(s, hx("06:00"), 6.33, hx("17:00") - hx("06:00"), C.accent3);
["06:00", "08:00", "10:00", "12:00", "14:00", "16:00"].forEach((t) => txt(s, t, { x: hx(t) - 0.3, y: 6.38, w: 0.6, h: 0.22, fontSize: 9, color: C.accent2, align: "center" }));
const SX2 = 6.75, SW2 = XR - SX2;
[[`${OD.current_drop_trailer_concurrent_p90} → ${DEP.plan_max_doors_busy}`, `trailers at the doors at once on a busy day: parked all day today, max ${DEP.plan_max_doors_busy} of ${DOORS_OUT} doors with time slots`],
 [`${r0(LT.today_p90_h)} → ${r0(LT.future_p90_h)} h`, "order to trailer for the slowest 10% of orders"],
].forEach(([big, lab], i) => stat(s, SX2 + i * (SW2 / 2 + 0.1), Y0, SW2 / 2 - 0.15, big, lab, { bh: 0.6, lh: 0.75 }));
hline(s, SX2, 3.45, SW2);
txt(s, "How it works", { x: SX2, y: 3.6, w: SW2, h: 0.3, fontSize: 13, bold: true, color: C.text2 });
numberRows(s, SX2, 4.02, SW2, 0.9, [
  ["Fixed slots.", `${DEP.trailers_planned} trailer slots a day, each with a time and a door (S1–S5); every wave ends at least 45 minutes before its trailers leave.`],
  ["Same-day lane.", `Orders received before 12:00 (${DEP.orders_before_noon_pct}%) go in wave 3 and leave the same day.`],
  ["Pack and stage by departure.", `${M.putwall_design.pack_stations} pack stations at the put-to-light wall; one staging lane per door, ${STAGING_FILL}% full on the busiest afternoon.`],
], { size: 12.5 });
notes(s, "Rachel (Shipping)", "1:30",
  `Shipping turns the whole day into one plan. Each carrier gets fixed departure slots and a door — ${DEP.trailers_planned} trailers a day — and the waves are planned backwards from those times, so every wave ends at least 45 minutes before its trailers leave. ` +
  `Orders that arrive before noon go in the third wave and leave the same day. The effect: ${LT.future_within_24h_pct}% of orders leave within 24 hours instead of ${LT.today_within_24h_pct}%, and the slowest ten percent drop from ${r0(LT.today_p90_h)} to ${r0(LT.future_p90_h)} hours. ` +
  `The yard calms down too: today up to ${OD.current_drop_trailer_concurrent_p90} trailers stand parked; with time slots at most ${DEP.plan_max_doors_busy} of the ${DOORS_OUT} doors are busy at once.`);

// ================================================================ 9. VALUE FOR DHL
pres.addSection({ title: "Value for DHL" });
s = slide("Value for DHL", `For DHL: a kept service promise, ${eurK(PC.saving_year)} lower labour cost a year, and process changes that pay back in ~${PC.payback_process_years.toFixed(1)} years`,
  `Source: KPI and cost model (Deliverable 3 §2–3); racking prices ${src("S020")}; labour €20 per hour ${src("S026")}; benchmark prices, not supplier quotes`,
  { owner: "Shipping", ownerLabel: "presenter" });
txt(s, "What changes for DHL", { x: L, y: Y0, w: 6.6, h: 0.3, fontSize: 13, bold: true, color: C.text2 });
const VR = [
  ["Service", "Lines staged on time", `${n1(ON_TIME_TODAY)}%`, "≥ 98%"],
  ["", "Orders out within 24 hours", `${LT.today_within_24h_pct}%`, `${LT.future_within_24h_pct}%`],
  ["Cost", "Picker-hours a day", `~${r0(PICK_TODAY)}`, `~${r0(PICK_NEW)}`],
  ["", "Cost per order line (incl. depreciation)", "—", `€${UC.per_order_line.toFixed(2)}`],
  ["Docks", "Trailers at the doors at once", `${OD.current_drop_trailer_concurrent_p90}`, `max ${DEP.plan_max_doors_busy}`],
  ["Safety", "Pick faces with reach-truck traffic", "—", `none (${SAFE_PCT}% separated)`],
  ["Growth", "+50% volume needs", "—", `+${GROW["ETV 216i needed"] - FLEET_UNITS["ETV 216i"]} reach truck, +${GROW["EJE 120i needed"] - FLEET_UNITS["EJE 120i"]} pallet truck, same ${DOORS_OUT} doors`],
];
s.addTable([[th(""), th("KPI"), th("Today"), th("Our design")], ...VR.map(([a, k, t, d]) => [
  td(a, { bold: true, color: C.text2, border: [a ? { type: "solid", pt: 0.75, color: HEX.accent3 } : noB, noB, rowB, noB] }),
  td(k, { border: [a ? { type: "solid", pt: 0.75, color: HEX.accent3 } : noB, noB, rowB, noB] }),
  td(t, { color: C.accent2, border: [a ? { type: "solid", pt: 0.75, color: HEX.accent3 } : noB, noB, rowB, noB] }),
  td(d, { bold: true, color: C.accent1, border: [a ? { type: "solid", pt: 0.75, color: HEX.accent3 } : noB, noB, rowB, noB] })])],
  { x: L, y: Y0 + 0.4, w: 6.6, colW: [0.95, 2.75, 0.85, 2.05], rowH: [0.32, ...VR.map(() => 0.5)], fontSize: 12, color: C.text1, margin: [0.02, 0.06, 0.02, 0.06] });
const BX = 7.6, BW = XR - BX;
chartHead(s, BX, Y0, BW, "Three ways to invest, € million", "payback from the labour saved");
const INV = [
  ["Process changes only", PC.capex_process, PC.payback_process_years],
  ["Full design, re-using racks", PC.capex_reuse_racking, PC.payback_reuse_years],
  ["Full design, new racks", PC.capex_total, PC.payback_years],
];
s.addChart(pres.charts.BAR, [{ name: "Investment", labels: INV.map(([k, , p]) => `${k} · ${p < 3 ? p.toFixed(1) : r0(p)} yrs`), values: INV.map(([, v]) => Math.round(v / 1e4) / 100) }],
  chartBase({ x: BX - 0.15, y: 2.5, w: BW + 0.15, h: 2.85, barDir: "bar", catAxisOrientation: "maxMin", chartColors: [HEX.accent1, HEX.accent3, HEX.accent3],
    barGapWidthPct: 45, valAxisHidden: true, valGridLine: { style: "none" }, valAxisMinVal: 0, valAxisMaxVal: 2.1, catAxisLabelFontSize: 11,
    showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: '"€"0.00"M"', dataLabelFontBold: true }));
box(s, BX, 5.5, BW, 1.25, C.accent6, { objectName: "Yearly numbers" });
[[eurK(PC.saving_year), "labour saved a year"], [eurK(PC.opex_total), `running cost a year (${LABOUR_SHARE}% labour)`]].forEach(([big, lab], i) =>
  stat(s, BX + 0.25 + i * (BW / 2), 5.6, BW / 2 - 0.35, big, lab, { size: 26, bh: 0.5, lh: 0.5, lsize: 11.5, color: C.text1 }));
notes(s, "Rachel (Shipping)", "1:30",
  `What does DHL get? On service, the promise to Assa Abloy is kept: at least 98% of lines on time and ${LT.future_within_24h_pct}% of orders out within 24 hours. ` +
  `On cost, about ${r0(PICK_NEW)} picker-hours a day instead of ${r0(PICK_TODAY)}, which saves about ${eurK(PC.saving_year)} a year, and a cost of €${UC.per_order_line.toFixed(2)} per order line that DHL can use in pricing. ` +
  "Reach trucks and pickers never share an aisle, and volume can grow by half with one extra reach truck and one extra pallet truck, through the same doors. " +
  `On the right, three ways to invest. The process changes alone cost ${eurM(PC.capex_process)} and pay back in about ${PC.payback_process_years.toFixed(1)} years. ` +
  `The full design costs ${eurM(PC.capex_reuse_racking)} if today's racks can be re-used, or ${eurM(PC.capex_total)} with new racks, which pays back much more slowly. These are benchmark prices, not quotes.`);

// ================================================================ 10. ROADMAP
pres.addSection({ title: "Roadmap" });
s = slide("Roadmap", "Start with the low-cost process changes, then build the fast-pick area — the racking decision comes last",
  `Source: proposed sequence based on the cost model (Deliverable 3 §3) and the savings per lever; open points in the appendix`,
  { owner: "Storage", ownerLabel: "presenter" });
chevrons(s, ["Step 1  Change how work flows", "Step 2  Build the fast-pick area", "Step 3  Decide the racking"], Y0, 0.6, { size: 14 });
const COLW = (CW - 2 * 0.3) / 3;
[
  [`Three waves a day, fixed trailer slots, slotting by demand, and dead stock cleared (${OLD_LOADS}% of loads are over a year old).`,
   `No 08:00 peak staffing: −${n1(LEVER.waves.h)} picker-hours a day (~${eurK(LEVER.waves.eur)} a year), and the wave plan behind ${LT.future_within_24h_pct}% within 24 h.`,
   "WMS wave set-up; carriers agree to fixed slots."],
  [`Carton flow for the ${n0(FP.skus)} best-sellers, the put-to-light wall, trolleys and scanners; small parts to bin shelving.`,
   `Batch picking: −${n1(LEVER.batch.h)} picker-hours a day (~${eurK(LEVER.batch.eur)} a year); ${n0(SP.freed_rack_locations)} rack places freed.`,
   `Steps 1 + 2: ${eurM(PC.capex_process)}, payback ~${PC.payback_process_years.toFixed(1)} years; small-parts shelving ${eurK(PC.capex_by_group["Small-item storage"])}.`],
  ["Re-use today's racking or install new single-deep racks; keep the 12th module in reserve for growth.",
   `${n0(LAY.positions_total)} places, every pallet reachable without moving another.`,
   `Re-use: ${eurM(PC.capex_reuse_racking)} in total (payback ~${r0(PC.payback_reuse_years)} years). New: ${eurM(PC.capex_total)} (~${r0(PC.payback_years)} years).`],
].forEach((rows, i) => {
  const x = L + i * (COLW + 0.3);
  ["What", "Delivers", "Needs"].forEach((lab, j) => {
    const y = 2.72 + j * 1.07;
    if (j) hline(s, x, y - 0.08, COLW);
    txt(s, lab.toUpperCase(), { x, y, w: COLW, h: 0.22, fontSize: 9, bold: true, charSpacing: 1, color: C.accent1 });
    txt(s, rows[j], { x, y: y + 0.24, w: COLW, h: 0.78, fontSize: 12.5 });
  });
});
s.addText([{ text: "Decisions we need from DHL:  ", options: { bold: true } },
  { text: "the 7,000 m² scope  ·  carriers accepting fixed slots  ·  re-use or replace the racking" }],
  { x: L, y: 6.1, w: CW, h: 0.65, fontSize: 14, color: C.text1, fill: { color: C.accent6 }, margin: [14, 14, 4, 4], valign: "middle", isTextBox: true });
notes(s, "Gleb (Storage)", "1:15",
  "How to get there? We propose three steps. Step one changes how work flows: three waves, fixed trailer slots, slotting by demand and clearing dead stock. That needs little more than WMS settings and an agreement with the carriers, and it already removes the morning peak. " +
  `Step two builds the fast-pick area and the put-to-light wall; together with step one that costs ${eurM(PC.capex_process)} and pays back in about ${PC.payback_process_years.toFixed(1)} years. ` +
  "Step three is the racking decision, which is the big investment, so it comes last and depends on whether today's racks can be re-used. " +
  "To start, we need three decisions from DHL: the 7,000 square metre scope, the carriers' acceptance of fixed slots, and the racking. Before go-live each of us closes one open point — they are in the appendix. Thank you, we are happy to take your questions.");

// ================================================================ 11. QUESTIONS
s = pres.addSlide({ masterName: "CLOSE", sectionTitle: "Roadmap" });
s.addText("Thank you — questions?", { placeholder: "title" });
s.addText(Object.entries(OWN).map(([p, o], i, arr) => ({ text: `${FULL(o)} — ${p}`, options: { breakLine: i < arr.length - 1 } })), { placeholder: "body" });
notes(s, "All", "Q&A", "Each owner answers questions about their own process. The appendix has the details: the four V's, the option choice, all KPIs, costs, open points, planning and control, equipment and sources.");

// ================================================================ APPENDIX
pres.addSection({ title: "Appendix" });

// A1 - the four V's
s = slide("Appendix", "Assa Abloy is a high-variety, medium-volume operation: many small, different orders with sharp peaks",
  `Source: WMS data April–June 2025 ${src("S002")}; four V's and process types ${src("S031")}; Deliverable 1 §11`, { appendix: true, tracker: "Operation profile" });
const VS = [
  ["VOLUME", "MEDIUM", n0(P.lines.mean), `order lines a day (~${n0(ORDERS_DAY)} orders)`,
    `${n0(CPM.inbound_loads_day)} inbound loads and ~${n0(OD.trailers_per_day_mean)} outbound trailers a day`, "standard methods, scanning and batching pay off"],
  ["VARIETY", "HIGH", n0(A.n_skus_shipped), "different items shipped in three months",
    `${n0(S.n_skus)} items in stock; each, case and pallet picks; ${S.hazmat_skus} hazardous items`, "several storage types; pick by order size"],
  ["VARIATION", "HIGH", `${P.lines.peak_over_avg.toFixed(1)}×`, "busiest day vs an average day (order lines)",
    `08:00 pick peak ${REL.pick_peak_over_mean_active_hour}× the average hour; stock +${r0(ST.growth_per_quarter_pct)}% per quarter`, "level the self-made peak with waves; keep storage headroom"],
  ["VISIBILITY", "LOW", "Low", "customers see only the result",
    `business customers and web shops (${r0(WEB_PCT)}% of lines) want complete, on-time orders`, "efficiency is designed in the back office, but the dispatch promise must be kept"],
];
const TW = (CW - 3 * 0.25) / 4;
VS.forEach(([lab, lvl, big, unit, facts, impl], i) => {
  const x = L + i * (TW + 0.25), y = Y0 + 0.05, pad = 0.22, iw = TW - 2 * pad;
  box(s, x, y, TW, 4.05, C.background2, { objectName: `${lab} tile` });
  txt(s, lab, { x: x + pad, y: y + 0.2, w: iw, h: 0.26, fontSize: 11, bold: true, charSpacing: 1, color: C.accent1 });
  txt(s, lvl, { x: x + pad, y: y + 0.2, w: iw, h: 0.26, fontSize: 9, bold: true, charSpacing: 1, color: C.accent2, align: "right" });
  txt(s, big, { x: x + pad, y: y + 0.55, w: iw, h: 0.72, fontSize: 38, bold: true, color: C.text2 });
  txt(s, unit, { x: x + pad, y: y + 1.3, w: iw, h: 0.5, fontSize: 12 });
  hline(s, x + pad, y + 1.9, iw, C.accent3);
  txt(s, facts, { x: x + pad, y: y + 2.02, w: iw, h: 0.85, fontSize: 12, color: C.accent2 });
  txt(s, [{ text: "For the design: ", options: { bold: true, color: C.text2 } }, { text: impl }], { x: x + pad, y: y + 2.95, w: iw, h: 0.95, fontSize: 12 });
});
s.addText([{ text: "So what: ", options: { bold: true } },
  { text: "high variety at medium volume sits between a batch and a mass process — people supported by scanners, carton flow and a put-to-light wall fit better than full automation." }],
  { x: L, y: 6.15, w: CW, h: 0.6, fontSize: 13, color: C.text1, fill: { color: C.accent6 }, margin: [12, 12, 4, 4], valign: "middle", isTextBox: true });
notes(s, "Appendix", "-", "Use if asked what kind of operation this is (four V's, Slack et al.).");

// A2 - option choice
s = slide("Appendix", `We chose Option B, 'hybrid density': it scores highest (${WT[OPT.B].toFixed(2)} of 5) and stays ahead when cost counts most`,
  `Source: team decision matrix (Deliverable 1 §14–15); storage and picking systems ${src("S017")}; batch picking ${src("S014")}`, { appendix: true, tracker: "Option choice" });
const crit = Object.keys(DEC.weights);
const hdr = (t, sub, hi) => ({ text: [{ text: t, options: { bold: true, breakLine: true } }, { text: sub, options: { fontSize: 10, color: C.accent2 } }],
  options: { fill: { color: hi ? C.accent5 : C.background1 }, align: "center", valign: "bottom", border: [noB, noB, thB, noB] } });
const rowsM = [[
  { text: "Criterion", options: { bold: true, valign: "bottom", border: [noB, noB, thB, noB] } },
  { text: "Weight", options: { bold: true, align: "center", valign: "bottom", border: [noB, noB, thB, noB] } },
  hdr("A", "Conventional+"), hdr("B", "Hybrid density", true), hdr("C", "Semi-automated"),
]];
crit.forEach((c, i) => rowsM.push([
  td(c.replace("m2", "m²").replace("(lower=better)", "(lower is better)")), td(`${r0(DEC.weights[c] * 100)}%`, { align: "center", color: C.accent2 }),
  td(String(DEC.scores[OPT.A][i]), { align: "center" }), td(String(DEC.scores[OPT.B][i]), { align: "center", fill: { color: C.accent5 } }),
  td(String(DEC.scores[OPT.C][i]), { align: "center" }),
]));
rowsM.push([td("Weighted score (max 5)", { bold: true }), td("100%", { align: "center", color: C.accent2 }),
  td(WT[OPT.A].toFixed(2), { align: "center", bold: true }), td(WT[OPT.B].toFixed(2), { align: "center", bold: true, color: C.accent1, fill: { color: C.accent5 } }),
  td(WT[OPT.C].toFixed(2), { align: "center", bold: true })]);
s.addTable(rowsM, { x: L, y: Y0, w: 7.6, colW: [3.05, 0.95, 1.2, 1.2, 1.2], rowH: [0.62, ...crit.map(() => 0.42), 0.46], fontSize: 13, color: C.text1, margin: [0.03, 0.08, 0.03, 0.08] });
txt(s, "Scores 1 (poor) to 5 (best), agreed in the team; weighted score = sum of weight × score.", { x: L, y: 6.2, w: 7.6, h: 0.3, fontSize: 11, color: C.accent2 });
const RX = 8.6, RW = XR - RX;
txt(s, "Why B", { x: RX, y: Y0, w: RW, h: 0.3, fontSize: 13, bold: true, color: C.text2 });
numberRows(s, RX, Y0 + 0.42, RW, 0.66, [
  ["Fits the site", `with all working areas: ${n0(LAY.total_area_m2)} m² of 7,000 m².`],
  ["Cuts labour", "through slotting and batch picking, without betting on automation."],
  ["Proven kit", "at moderate cost: reach trucks, carton flow, a put-to-light wall."],
], { size: 13 });
txt(s, "Robustness: scores with other weights", { x: RX, y: 4.45, w: RW, h: 0.3, fontSize: 12, bold: true, color: C.text2 });
const sensRow = (lab, key) => [td(lab), ...["A", "B", "C"].map((k) => td(SENS[OPT[k]][key].toFixed(2), { align: "center", bold: k === "B", fill: { color: k === "B" ? C.accent5 : C.background1 } }))];
s.addTable([
  [td("Weights", { bold: true, color: C.accent2 }), ...["A", "B", "C"].map((k) => td(k, { bold: true, align: "center", color: C.accent2, fill: { color: k === "B" ? C.accent5 : C.background1 } }))],
  sensRow("Base case", "base"), sensRow("Cost-driven", "cost_driven"), sensRow("Space-driven", "space_driven"),
], { x: RX, y: 4.8, w: RW, colW: [RW - 2.4, 0.8, 0.8, 0.8], rowH: 0.36, fontSize: 12, color: C.text1, margin: [0.02, 0.08, 0.02, 0.08] });
txt(s, `Only when space is all that counts does C edge ahead (${SENS[OPT.C].space_driven.toFixed(2)} vs ${SENS[OPT.B].space_driven.toFixed(2)}).`,
  { x: RX, y: 6.33, w: RW, h: 0.45, fontSize: 11, color: C.accent2 });
notes(s, "Appendix", "-", "Use if asked why not more automation, or how the option was chosen.");

// A3 - KPI scorecard
s = slide("Appendix", "Nine KPIs, each with an owner, track the five performance objectives — all but storage headroom meet their target",
  `Source: KPI overview (Deliverable 3 §2); today = WMS data April–June 2025 ${src("S002")}; benchmarks ${src("S023")}; design values modelled`, { appendix: true, tracker: "KPI scorecard" });
const KR = [
  ["Dependability", "On-time shipment (lines staged before departure)", `${n1(ON_TIME_TODAY)}%`, "≥ 98%", "≥ 98%", "Rachel", true],
  ["", "Trailers at the doors at once (busy day)", `${OD.current_drop_trailer_concurrent_p90}, parked`, `max ${DEP.plan_max_doors_busy}`, `≤ ${DOORS_OUT}`, "Rachel", true],
  ["Speed", "Orders out within 24 hours", `${LT.today_within_24h_pct}%`, `${LT.future_within_24h_pct}%`, "≥ 60%", "Rachel", true],
  ["", "Dock-to-stock, pallet trailer", "1–3 days (big receipts)", `~${n1(DOCK_TO_STOCK)} h`, "< 3.5 h", "Vidhi", true],
  ["Quality", "Pick accuracy (orders without error)", "not in the data", "≥ 99.7%", "≥ 99.3%", "Arnau", true],
  ["Cost", "Fast-pick hit rate (lines from the fast-pick area)", "—", `${r0(ST.fast_hit_pct)}%`, "≥ 60%", "Arnau", true],
  ["", "Rack fill at the peak", `${n0(ST.occupied_peak)} places used`, `${RACK_FILL}%`, "≤ 90%", "Gleb", true],
  ["Flexibility", "Containers unpacked inside their zone", "—", `${LZ.share_fit_zone_pct}%`, "≥ 90%", "Vidhi", true],
  ["", "Storage headroom", "—", `~${r0(ST.months_headroom)} months`, "≥ 12 months", "Gleb", false],
];
const kRows = [[th("Objective"), th("KPI"), th("Today"), th("Our design"), th("Target"), th("Owner"), th("Status")]];
KR.forEach(([obj, k, today, des, tgt, own, ok], i) => {
  const topB = obj && i ? { type: "solid", pt: 0.75, color: HEX.accent3 } : noB;
  const c = (t, o = {}) => ({ text: t, options: Object.assign({ valign: "middle", border: [topB, noB, { type: "solid", pt: 0.5, color: HEX.accent4 }, noB] }, o) });
  kRows.push([c(obj, { bold: true, color: C.text2 }), c(k), c(today, { color: C.accent2 }), c(des, { bold: true }), c(tgt), c(own),
    c([{ text: "● ", options: { color: ok ? C.text2 : C.accent1 } }, { text: ok ? "meets" : "gap", options: { color: ok ? C.text1 : C.accent1, bold: !ok } }])]);
});
s.addTable(kRows, { x: L, y: Y0, w: CW, colW: [1.65, 3.85, 2.05, 1.5, 1.25, 0.88, 0.95], rowH: [0.36, ...KR.map(() => 0.44)], fontSize: 12, color: C.text1, margin: [0.02, 0.08, 0.02, 0.08] });
txt(s, "Checked every day in the start-of-day meeting of the four owners and weekly with the DHL operations manager (Deliverable 2 §7.5).",
  { x: L, y: 6.42, w: CW, h: 0.3, fontSize: 11, color: C.accent2 });
notes(s, "Appendix", "-", "Use if asked how the design is measured, or who owns which KPI.");

// A4 - cost detail
s = slide("Appendix", `The full fit-out costs ${eurM(PC.capex_total)}, mostly new racking; running the warehouse costs ${eurK(PC.opex_total)} a year`,
  `Source: cost model (Deliverable 3 §3): racking prices ${src("S020")}; labour €20 per hour ${src("S026")}; benchmark prices, not supplier quotes`, { appendix: true, tracker: "Cost detail" });
chartHead(s, L, Y0, 6.4, "Investment (CAPEX) by group, € thousand");
const CAP = Object.entries(PC.capex_by_group).sort((a, b) => b[1] - a[1]);
const CAP_LAB = { "Storage": "Storage racks", "Loose-container zone": "Container zone", "One-off": "One-off (moving, training)" };
s.addChart(pres.charts.BAR, [{ name: "CAPEX", labels: CAP.map(([k]) => CAP_LAB[k] || k), values: CAP.map(([, v]) => r0(v / 1000)) }],
  chartBase({ x: 0.45, y: 2.25, w: 6.4, h: 3.95, barDir: "bar", catAxisOrientation: "maxMin", chartColors: CAP.map(([k]) => k === "Storage" ? HEX.dk2 : HEX.accent3),
    barGapWidthPct: 45, valAxisHidden: true, valGridLine: { style: "none" }, valAxisMinVal: 0, valAxisMaxVal: 1500,
    showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: '"€"#,##0"k"', catAxisLabelFontSize: 12 }));
txt(s, `Contingency = ${CONTINGENCY}% of all items.`, { x: L, y: 6.3, w: 6.3, h: 0.4, fontSize: 11, color: C.accent2 });
const TX = 7.2, TWd = (XR - TX - 0.2) / 2;
[
  [eurK(PC.opex_by_group.Labour), "labour a year (direct and indirect staff)"],
  [eurK(PC.opex_by_group.Machinery), "machinery a year (truck lease and energy)"],
  [`€${UC.per_order_line.toFixed(2)}`, `per order line (€${UC.per_order.toFixed(2)} per order), depreciation included`],
  [`€${UC.per_inbound_pallet.toFixed(2)}`, "per inbound pallet received and put away"],
].forEach(([big, lab], i) => {
  const x = TX + (i % 2) * (TWd + 0.2), y = Y0 + Math.floor(i / 2) * 2.45;
  box(s, x, y, TWd, 2.25, C.background2, { objectName: `Cost tile ${i + 1}` });
  stat(s, x + 0.22, y + 0.22, TWd - 0.44, big, lab, { bh: 0.62, lh: 1.2 });
});
notes(s, "Appendix", "-", "Use if asked for the cost breakdown.");

// A5 - open points and owners
s = slide("Appendix", "Four open points to close before go-live — each has an owner and a next step",
  "Source: assumption register (Deliverable 2 §8) and risks in Deliverable 3", { appendix: true, tracker: "Open points" });
const RK = [
  ["Storage", "Stock growth", `racks full in ~${r0(ST.months_headroom)} months at +${r0(ST.growth_per_quarter_pct)}% per quarter`, 3,
    `Clear dead stock (${OLD_LOADS}% of loads over a year old); order the reserved 12th module at 90% fill (+${n0(LAY.positions_12th_module)} places)`],
  ["Picking", "Pick times are modelled", `they set the staff per wave; labour is ${LABOUR_SHARE}% of the running cost`, 3,
    "Time study on the current floor; recalculate pickers per wave"],
  ["Shipping", "Costs are benchmarks", `racking alone ranges €${PC.cost_register.rack_pp.low}–${PC.cost_register.rack_pp.high} per place`, 2,
    "Quotes for racking, carton flow and the put-to-light wall; lease quote from Jungheinrich"],
  ["Receiving", "Hazard class unconfirmed", `${HAZ.skus} items, ${n0(HAZ.loads)} loads, ${n0(HAZ.kg_in_stock / 1000)} t in stock`, 2,
    "Ask Assa Abloy for UN numbers and safety data sheets; size the hazmat section"],
];
[["OPEN POINT", L + 0.5], ["IMPACT", 5.55], ["NEXT STEP", 6.75], ["OWNER", 11.35]].forEach(([t, x]) =>
  txt(s, t, { x, y: Y0, w: 2.5, h: 0.25, fontSize: 10, bold: true, charSpacing: 1, color: C.accent2 }));
RK.forEach(([proc, head, why, imp, step], i) => {
  const y = Y0 + 0.32 + i * 0.95;
  hline(s, L, y, CW);
  txt(s, String(i + 1), { x: L, y: y + 0.12, w: 0.4, h: 0.4, fontSize: 18, bold: true, color: C.accent1 });
  txt(s, [{ text: head, options: { bold: true, color: C.text2, breakLine: true } }, { text: why, options: { color: C.accent2, fontSize: 12 } }], { x: L + 0.5, y: y + 0.12, w: 4.35, h: 0.78, fontSize: 13 });
  dots(s, 5.6, y + 0.22, imp);
  txt(s, step, { x: 6.75, y: y + 0.12, w: 4.45, h: 0.78, fontSize: 13 });
  s.addShape(pres.shapes.RECTANGLE, { x: 11.35, y: y + 0.19, w: 0.13, h: 0.13, fill: { color: OWN[proc].hex }, line: { type: "none" } });
  txt(s, [{ text: OWN[proc].name, options: { bold: true, breakLine: true } }, { text: proc, options: { color: C.accent2, fontSize: 11 } }], { x: 11.56, y: y + 0.12, w: 1.17, h: 0.6, fontSize: 13 });
});
hline(s, L, Y0 + 0.32 + 4 * 0.95, CW);
notes(s, "Appendix", "-", "Use if asked about risks or what happens before go-live.");

// A6 - planning and control
s = slide("Appendix", "Planning and control: one day plan links the four processes, and each owner checks their KPIs every day",
  "Source: Deliverable 2 §7 (planning and control per process)", { appendix: true, tracker: "Planning and control" });
const pc = (t, o = {}) => ({ text: t, options: Object.assign({ valign: "top", border: [noB, noB, rowB, noB] }, o) });
const pcRows = [[th("Process (owner)"), th("Planned ahead"), th("Controlled during the day"), th("KPIs")]];
[
  ["Receiving", "a time slot for every delivery from the advance shipping notice; containers booked on R1 in the morning", "late or early arrivals re-booked into the next free slot", "dock-to-stock, container door time"],
  ["Storage", "system-directed putaway; min/max refills between the waves; re-slotting every month", "cycle counts (A monthly, B quarterly, C yearly); occupancy each month, 12th module ordered at 90%", "rack fill, storage headroom"],
  ["Picking", "three waves planned back from the departures; pickers per wave = lines ÷ pick rate", "lines picked against plan per hour; the wall releases only complete, correct orders", "pick rate, accuracy, picker-hours"],
  ["Shipping", `${DEP.trailers_planned} fixed trailer slots; pack and stage in departure order`, "checked after each departure; a missed slot moves to the carrier's next slot", "on-time shipment, orders within 24 h"],
].forEach(([p, plan, ctrl, k]) => pcRows.push([
  pc([{ text: p, options: { bold: true, color: C.text2, breakLine: true } }, { text: OWN[p].name, options: { color: C.accent2 } }]), pc(plan), pc(ctrl), pc(k, { color: C.accent2 })]));
s.addTable(pcRows, { x: L, y: Y0, w: CW, colW: [1.9, 4.2, 4.2, 1.833], rowH: [0.36, 0.78, 0.78, 0.78, 0.78], fontSize: 12, color: C.text1, margin: [0.05, 0.08, 0.05, 0.08] });
txt(s, "THE CONTROL LOOP", { x: L, y: 5.45, w: 5, h: 0.25, fontSize: 10, bold: true, charSpacing: 1, color: C.accent2 });
chevrons(s, ["Measure: scans in the WMS", "Compare with the target", "Act: re-plan or re-slot", "Check: KPI back on target"], 5.75, 0.55,
  { fill: C.accent6, color: C.text1, size: 12 });
txt(s, "Every day: start-of-day meeting of the four owners  ·  every week: KPI review with DHL  ·  every month: review with Assa Abloy",
  { x: L, y: 6.42, w: CW, h: 0.3, fontSize: 11, color: C.accent2 });
notes(s, "Appendix", "-", "Use if asked how the design is planned and controlled day to day.");

// A7 - equipment and stress test
s = slide("Appendix", `Equipment: the fleet covers the peak day; at double volume the ${DOORS_OUT} outbound doors, not the trucks, become the limit`,
  `Source: Deliverable 2 §5 and Deliverable 3 stress test; equipment data (Jungheinrich, ${[CITE.S010, CITE.S008, CITE.S006].map((c) => c.replace("Jungheinrich, ", "")).join(", ")})`,
  { appendix: true, tracker: "Equipment" });
txt(s, "Equipment plan", { x: L, y: Y0, w: 6, h: 0.3, fontSize: 13, bold: true, color: C.text2 });
const fr = [[th("Equipment"), th("Task"), th("Units", "center"), th("Busy, avg day", "center")]];
FLEET.forEach((f) => fr.push([pc(f.Model.replace("Jungheinrich ", ""), { bold: true }), pc(f.Task), pc(String(f["Units recommended"]), { align: "center" }),
  pc(f["Utilisation avg %"] == null ? "—" : `${r0(f["Utilisation avg %"])}%`, { align: "center" })]));
s.addTable(fr, { x: L, y: Y0 + 0.4, w: 6.6, colW: [1.95, 2.95, 0.7, 1.0], fontSize: 12, color: C.text1, margin: [0.05, 0.08, 0.05, 0.08] });
txt(s, "Units = recommended fleet, sized for the peak day. Busy = equipment-hours ÷ available hours on an average day; the spare time absorbs peaks and growth.",
  { x: L, y: 4.75, w: 6.6, h: 0.6, fontSize: 11, color: C.accent2 });
const ZX = 7.6, ZW = XR - ZX;
txt(s, "Stress test: what more volume needs", { x: ZX, y: Y0, w: ZW, h: 0.3, fontSize: 13, bold: true, color: C.text2 });
const sr = [[th("Volume"), th("Staff (peak FTE)", "center"), th("Reach trucks", "center"), th("Pallet trucks", "center"), th("Out doors", "center")]];
STRESS.forEach((r) => {
  const over = r["Outbound doors (busiest hour)"] > DOORS_OUT;
  sr.push([pc(r.Volume, { bold: true }), pc(n1(r["Direct FTE (peak day)"]), { align: "center" }), pc(String(r["ETV 216i needed"]), { align: "center" }),
    pc(String(r["EJE 120i needed"]), { align: "center" }), pc(String(r["Outbound doors (busiest hour)"]), { align: "center", bold: over, color: over ? C.accent1 : C.text1 })]);
});
s.addTable(sr, { x: ZX, y: Y0 + 0.4, w: ZW, colW: [0.95, 1.15, 1.0, 1.0, ZW - 4.1], fontSize: 12, color: C.text1, margin: [0.05, 0.06, 0.05, 0.06] });
txt(s, `Doors needed in the busiest hour; the design has ${DOORS_OUT} outbound doors. Above that, more time slots spread the trailers over the day.`,
  { x: ZX, y: 4.35, w: ZW, h: 0.6, fontSize: 11, color: C.accent2 });
notes(s, "Appendix", "-", "Use if asked about equipment, utilisation or growth.");

// A8 - sources
s = slide("Appendix", "Sources", "References in APA 7th edition. Personal communications are cited in the text only.", { appendix: true, tracker: "Sources" });
const italicRuns = (ref, last) => ref.split("*").map((part, i, arr) => ({ text: part, options: Object.assign({ italic: i % 2 === 1 },
  i === arr.length - 1 && !last ? { breakLine: true } : {}) })).filter((r) => r.text.length);
const refRuns = [];
D.references.forEach((r, i) => refRuns.push(...italicRuns(r, i === D.references.length - 1)));
txt(s, refRuns, { x: L, y: Y0 - 0.1, w: CW, h: 4.95, fontSize: 11, paraSpaceAfter: 5, color: C.text1 });
notes(s, "Appendix", "-", "All sources used on the slides; the full list is in the portfolio.");

// ---------------------------------------------------------------- write, then put the theme colours into the file
function themeXml(xml) {
  const slots = ["dk1", "lt1", "dk2", "lt2", "accent1", "accent2", "accent3", "accent4", "accent5", "accent6", "hlink", "folHlink"];
  const scheme = `<a:clrScheme name="${THEME.name}">` + slots.map((k) => `<a:${k}><a:srgbClr val="${THEME.colors[k]}"/></a:${k}>`).join("") + "</a:clrScheme>";
  return xml.replace(/<a:clrScheme\b[\s\S]*?<\/a:clrScheme>/, () => scheme).replace(/(<a:(?:theme|fontScheme)\b[^>]*?\bname=")[^"]*"/g, (_, h) => `${h}${THEME.name}"`);
}
async function applyTheme(file) {
  // pptxgenjs writes Office's colours into the theme; scheme colours on the slides only show ours after this step
  const zip = await JSZip.loadAsync(fs.readFileSync(file));
  const part = "ppt/theme/theme1.xml";
  zip.file(part, themeXml(await zip.file(part).async("string")));
  for (const name of Object.keys(zip.files)) {
    if (!name.endsWith(".xml")) continue;
    const bad = (await zip.file(name).async("string")).match(/<a:srgbClr val="((?![0-9A-Fa-f]{6}")[^"]*)"/);
    if (bad) throw new Error(`${name}: colour "${bad[1]}" is not hex (a scheme colour in a hex-only option)`);
  }
  fs.writeFileSync(file, await zip.generateAsync({ type: "nodebuffer", compression: "DEFLATE" }));
}

pres.writeFile({ fileName: OUT }).then(async () => {
  await applyTheme(OUT);
  console.log("Saved", OUT);
});
