/*
 Turns a presentation briefing written in Markdown into a Word document (same look as the deck: Arial, dark
 headings, DHL red accents, light tables), so the briefing can be printed or read in Word.

   node analysis/build_briefing_docx.js deliverables/presentation_prep/Storage_briefing_Gleb.md
   -> deliverables/presentation_prep/Storage_briefing_Gleb.docx

 Handles what the briefings use: # / ## / ### headings, paragraphs, - bullets, 1. numbered lists, > quotes,
 | tables |, --- separators, **bold** and `code`.
*/
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle,
  HeadingLevel, AlignmentType, LevelFormat, Footer, PageNumber, TableLayoutType,
} = require("docx");

const SRC = process.argv[2];
if (!SRC) { console.error("usage: node analysis/build_briefing_docx.js <briefing.md>"); process.exit(2); }
const OUT = SRC.replace(/\.md$/, ".docx");
const lines = fs.readFileSync(SRC, "utf8").split(/\r?\n/);

const INK = "1A1A1A", GREY = "595959", RED = "D40511", LIGHT = "F2F2F2", LINE = "D9D9D9", NOTE = "FFF5CC";
const PAGE_W = 11906, MARGIN = 1134, CONTENT_W = PAGE_W - 2 * MARGIN;           // A4, 2 cm margins (DXA)

// ---- inline formatting: **bold** and `code`
function runs(text, base = {}) {
  const out = [];
  const re = /(\*\*[^*]+\*\*|`[^`]+`)/g;
  let last = 0, m;
  while ((m = re.exec(text))) {
    if (m.index > last) out.push(new TextRun({ text: text.slice(last, m.index), ...base }));
    const tok = m[0];
    if (tok.startsWith("**")) out.push(new TextRun({ text: tok.slice(2, -2), ...base, bold: true }));
    else out.push(new TextRun({ text: tok.slice(1, -1), ...base, font: "Consolas", size: (base.size || 21) - 2 }));
    last = m.index + tok.length;
  }
  if (last < text.length) out.push(new TextRun({ text: text.slice(last), ...base }));
  return out;
}

// ---- tables: column widths from the length of their content
function table(rows) {
  const cells = rows.map((r) => r.replace(/^\||\|$/g, "").split("|").map((c) => c.trim())).filter((r) => r.some((c) => c));
  const hasHead = rows[0].replace(/[|\s]/g, "") !== "";
  const nCol = Math.max(...cells.map((r) => r.length));
  const weight = Array.from({ length: nCol }, (_, j) =>
    Math.min(60, Math.max(...cells.map((r) => (r[j] || "").replace(/\*\*|`/g, "").length))) + 6);
  const total = weight.reduce((a, b) => a + b, 0);
  const widths = weight.map((w) => Math.round(w / total * CONTENT_W));
  // every column at least as wide as its longest word, so no word is broken over two lines
  const minW = Array.from({ length: nCol }, (_, j) =>
    Math.max(...cells.map((r) => Math.max(0, ...(r[j] || "").replace(/\*\*|`/g, "").split(/\s+/).map((w) => w.length)))) * 105 + 220);
  const short = widths.reduce((a, w, j) => a + Math.max(0, minW[j] - w), 0);
  if (short > 0) {
    const slack = widths.map((w, j) => Math.max(0, w - minW[j]));
    const totalSlack = slack.reduce((a, b) => a + b, 0);
    if (totalSlack > short) widths.forEach((w, j) => { widths[j] = w < minW[j] ? minW[j] : w - Math.round(slack[j] / totalSlack * short); });
  }
  widths[nCol - 1] += CONTENT_W - widths.reduce((a, b) => a + b, 0);
  const border = { style: BorderStyle.SINGLE, size: 4, color: LINE };
  const borders = { top: border, bottom: border, left: border, right: border };
  return new Table({
    width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: widths, layout: TableLayoutType.FIXED,
    rows: cells.map((r, i) => new TableRow({
      tableHeader: hasHead && i === 0, cantSplit: true,
      children: Array.from({ length: nCol }, (_, j) => new TableCell({
        width: { size: widths[j], type: WidthType.DXA }, borders,
        shading: hasHead && i === 0 ? { type: ShadingType.CLEAR, color: "auto", fill: LIGHT } : undefined,
        margins: { top: 50, bottom: 50, left: 90, right: 90 },
        children: [new Paragraph({ spacing: { before: 0, after: 0 },
          children: runs(r[j] || "", { size: 18, bold: hasHead && i === 0 ? true : undefined, color: hasHead && i === 0 ? GREY : INK }) })],
      })),
    })),
  });
}

// ---- walk the Markdown
const body = [];
let numList = 0;                                  // each numbered list restarts at 1
for (let i = 0; i < lines.length; i++) {
  const line = lines[i];
  if (!line.trim()) continue;
  if (/^---+\s*$/.test(line)) continue;           // section separators: headings already separate sections
  let m;
  if ((m = line.match(/^# (.*)/))) {
    body.push(new Paragraph({ heading: HeadingLevel.TITLE, spacing: { after: 120 }, children: runs(m[1], { size: 40, bold: true, color: INK }) }));
  } else if ((m = line.match(/^## (.*)/))) {
    body.push(new Paragraph({ heading: HeadingLevel.HEADING_1, keepNext: true, spacing: { before: 320, after: 120 },
      border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: RED, space: 4 } },
      children: runs(m[1], { size: 28, bold: true, color: INK }) }));
  } else if ((m = line.match(/^### (.*)/))) {
    body.push(new Paragraph({ heading: HeadingLevel.HEADING_2, keepNext: true, spacing: { before: 220, after: 80 },
      children: runs(m[1], { size: 23, bold: true, color: RED }) }));
  } else if (line.startsWith("|")) {
    const rows = [];
    while (i < lines.length && lines[i].startsWith("|")) {
      if (!/^\|\s*:?-{2,}/.test(lines[i])) rows.push(lines[i]);
      i++;
    }
    i--;
    body.push(table(rows));
    body.push(new Paragraph({ spacing: { before: 0, after: 80 }, children: [] }));
  } else if (line.startsWith(">")) {
    const quote = [];
    while (i < lines.length && lines[i].startsWith(">")) { quote.push(lines[i].replace(/^>\s?/, "")); i++; }
    i--;
    body.push(new Paragraph({ spacing: { before: 80, after: 140 }, indent: { left: 240, right: 240 },
      shading: { type: ShadingType.CLEAR, color: "auto", fill: NOTE },
      border: { left: { style: BorderStyle.SINGLE, size: 18, color: "FFCC00", space: 8 } },
      children: runs(quote.join(" "), { size: 20, italics: true, color: INK }) }));
  } else if ((m = line.match(/^(\s*)- (.*)/))) {
    const level = m[1].length >= 2 ? 1 : 0;
    body.push(new Paragraph({ numbering: { reference: "bullets", level }, spacing: { after: 60 }, children: runs(m[2], { size: 21 }) }));
  } else if ((m = line.match(/^(\d+)\. (.*)/))) {
    if (m[1] === "1") numList++;
    body.push(new Paragraph({ numbering: { reference: "numbers", level: 0, instance: numList }, spacing: { after: 60 }, children: runs(m[2], { size: 21 }) }));
  } else {
    const next = lines.slice(i + 1).find((l) => l.trim()) || "";
    const keepNext = /^\*\*.*\*\*:?$/.test(line.trim()) || next.startsWith("|") || /^\s*-\s/.test(next);
    body.push(new Paragraph({ keepNext, spacing: { after: 120 }, children: runs(line, { size: 21 }) }));
  }
}

const doc = new Document({
  creator: "Group 3", title: path.basename(SRC, ".md").replace(/_/g, " "),
  styles: { default: { document: { run: { font: "Arial", size: 21, color: INK } } } },
  numbering: { config: [
    { reference: "bullets", levels: [
      { level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 360, hanging: 240 } } } },
      { level: 1, format: LevelFormat.BULLET, text: "–", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 240 } } } }] },
    { reference: "numbers", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 360, hanging: 300 } } } }] },
  ] },
  sections: [{
    properties: { page: { size: { width: PAGE_W, height: 16838 }, margin: { top: MARGIN, bottom: MARGIN, left: MARGIN, right: MARGIN } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [
      new TextRun({ text: "Project OTM · Group 3 · confidential   ", size: 16, color: GREY }),
      new TextRun({ children: ["page ", PageNumber.CURRENT, " of ", PageNumber.TOTAL_PAGES], size: 16, color: GREY }),
    ] })] }) },
    children: body,
  }],
});

Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(OUT, buf); console.log("Saved", OUT); });
