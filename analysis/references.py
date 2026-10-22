"""
APA 7 referencing for the generated reports.
The analysis keeps short source IDs (S001-S030, see documentation/sources.md). This module turns them into APA
author-date citations in the text and builds the APA reference list of every work actually cited in a document.

  cite_text(text, used)  -> text with every S0xx replaced by its APA in-text citation; cited keys are added to `used`
  reference_list(used)   -> list of APA references (strings, '*...*' = italics), sorted as APA requires
Personal communications (teacher / DHL sessions) are cited in the text only, as APA prescribes - not in the list.
"""
import re

ACC = "Retrieved {d}, from "
# key: (author as in the list, author for in-text, year, rest of the reference after "(year). ")
REFS = {
    "brief":    ("HAN University of Applied Sciences.", "HAN University of Applied Sciences", "2026",
                 "*Project DHL on the move: Project OTM* [Unpublished project brief]. OPERMB04 Operations Management."),
    "lecture":  ("HAN University of Applied Sciences.", "HAN University of Applied Sciences", "2026",
                 "[Lecture slides on warehouse design, layouts, storage and order-picking systems, week 3]. OPERMB04 Operations "
                 "Management. Unpublished course material."),
    "data":     ("Assa Abloy, & DHL Supply Chain.", "Assa Abloy & DHL Supply Chain", "2025",
                 "*Assa Abloy storage details (1 April, 1 May and 1 June 2025) and outbound details (April–June 2025)* "
                 "[Unpublished raw data]. DHL Supply Chain, Bemmel."),
    "slack":    ("Slack, N., Brandon-Jones, A., & Burgess, N.", "Slack et al.", "2022",
                 "*Operations management* (10th ed.). Pearson."),
    "baker":    ("Baker, P., & Canessa, M.", "Baker & Canessa", "2009",
                 "Warehouse design: A structured approach. *European Journal of Operational Research, 193*(2), 425–436. "
                 "https://doi.org/10.1016/j.ejor.2007.11.045"),
    "huertas":  ("Huertas, J. I., Díaz Ramírez, J., & Trigos Salazar, F.", "Huertas et al.", "2007",
                 "Layout evaluation of large capacity warehouses. *Facilities, 25*(7/8), 259–270. "
                 "https://www.emerald.com/f/article/25/7-8/259/106959/Layout-evaluation-of-large-capacity-warehouses"),
    "dekoster": ("de Koster, R., Le-Duc, T., & Roodbergen, K. J.", "de Koster et al.", "2007",
                 "Design and control of warehouse order picking: A literature review. *European Journal of Operational "
                 "Research, 182*(2), 481–501. https://doi.org/10.1016/j.ejor.2006.07.009"),
    "gadeyne":  ("Gadeyne, B.", "Gadeyne", "n.d.",
                 "*How to slot a warehouse during peak season (and avoid congestion)*. LinkedIn. " + ACC.format(d="September 14, 2026") +
                 "https://www.linkedin.com/pulse/how-slot-warehouse-during-peak-season-avoid-bart-gadeyne-yhude/"),
    "jh_etv":   ("Jungheinrich.", "Jungheinrich", "2019",
                 "*ETV 216i: Technical data* [Data sheet]. " + ACC.format(d="October 7, 2026") +
                 "https://www.fallsway.com/hubfs/Fallsway_January2022/Pdf/jungheinrich-ii-etv-216i-spec-sheet-english.pdf"),
    "jh_ere":   ("Jungheinrich.", "Jungheinrich", "n.d.",
                 "*ERE 225 rider pallet truck* [Product listing]. " + ACC.format(d="October 7, 2026") +
                 "https://www.shop.jungheinrich.co.uk/en/ere-225---98280668"),
    "jh_risk":  ("Jungheinrich.", "Jungheinrich", "n.d.",
                 "*Warehouse risks: Identifying and reducing operational risks*. " + ACC.format(d="October 7, 2026") +
                 "https://www.jungheinrich.co.uk/jungheinrich-blog-material-handling-insights-trends/warehouse-risks-identifying-"
                 "and-reducing-operational-risks-2496552"),
    "jh_eje":   ("Jungheinrich.", "Jungheinrich", "n.d.",
                 "*EJE 120i: Technical data (JEHN0398)* [Data sheet]. Logisnext Americas. " + ACC.format(d="October 14, 2026") +
                 "https://www.logisnextamericas.com/globalassets/migration-blocks/jungheinrich/product-listing/pallet-trucks/"
                 "eje-120-225/jehn0398---eje-120i-spec-sheet.pdf"),
    "jh_ezs":   ("Jungheinrich.", "Jungheinrich", "n.d.",
                 "*EZS 130 tow tractor*. " + ACC.format(d="October 14, 2026") +
                 "https://www.jungheinrich.co.uk/products/new-forklifts/tow-tractors/ezs-130-108322"),
    "tbsg":     ("TBSG.", "TBSG", "n.d.",
                 "*Order picking and display trolley with adjustable shelves* [Product listing]. " + ACC.format(d="October 14, 2026") +
                 "https://www.tbsg.co.uk/order-picking-and-display-trolley-with-adjustable-shelves--2"),
    "ssi":      ("SSI Schäfer.", "SSI Schäfer", "n.d.",
                 "*What does the rack inspection check?* " + ACC.format(d="October 14, 2026") +
                 "https://ssi-schaefer.com/en-de/what-does-the-rack-inspection-check--1580504"),
    "stow":     ("STOW.", "STOW", "n.d.",
                 "*DIN EN 15635 and other safety standards for racking*. " + ACC.format(d="October 14, 2026") +
                 "https://www.stow-group.com/en/racking/blog/warehouse-safety-standards/"),
    "iplo":     ("Informatiepunt Leefomgeving.", "Informatiepunt Leefomgeving", "n.d.",
                 "*Publicatiereeks Gevaarlijke Stoffen (PGS) 15: Systematiek*. " + ACC.format(d="October 14, 2026") +
                 "https://iplo.nl/thema/externe-veiligheid/handleiding-publicatiereeks-gevaarlijke-stoffen/pgs-15-systematiek"),
    "cbs_news": ("Centraal Bureau voor de Statistiek.", "Centraal Bureau voor de Statistiek", "2025",
                 "*Loonkosten per gewerkt uur 6 procent hoger in 2024*. " + ACC.format(d="October 18, 2026") +
                 "https://www.cbs.nl/nl-nl/nieuws/2025/42/loonkosten-per-gewerkt-uur-6-procent-hoger-in-2024"),
    "cbs_long": ("Centraal Bureau voor de Statistiek.", "Centraal Bureau voor de Statistiek", "2025",
                 "*De arbeidsmarkt in cijfers 2025: Lonen en loonkosten*. " + ACC.format(d="October 18, 2026") +
                 "https://longreads.cbs.nl/dearbeidsmarktincijfers-2025/lonen-en-loonkosten/"),
    "cao":      ("Cao Beroepsgoederenvervoer.", "Cao Beroepsgoederenvervoer", "n.d.",
                 "*TLN functieloonschalen per 1 januari 2025*. " + ACC.format(d="October 18, 2026") +
                 "https://www.caoberoepsgoederenvervoer.nl/tln-functieloonschalen-per-1-januari-2025/"),
    "cpeople":  ("Connecting People.", "Connecting People", "n.d.",
                 "*Salaris orderpicker*. " + ACC.format(d="October 18, 2026") + "https://www.connectingpeople.nl/salaris/orderpicker/"),
    "indexbox": ("IndexBox.", "IndexBox", "n.d.",
                 "*European Union: Metal racks market analysis, forecast, size, trends and insights*. " + ACC.format(d="October 18, 2026") +
                 "https://www.indexbox.io/store/european-union-metal-racks-market-analysis-forecast-size-trends-and-insights/"),
    "tracking": ("T-Racking.", "T-Racking", "n.d.",
                 "*How much does pallet racking cost?* " + ACC.format(d="October 18, 2026") + "https://t-racking.com/how-much-does-pallet-racking-cost"),
    "liftlease": ("Liftlease.", "Liftlease", "n.d.", "*Reachtruck leasen*. " + ACC.format(d="October 18, 2026") +
                  "https://liftlease.nl/lease/reachtruck-leasen"),
    "beekmans": ("Beekmans Heftrucks.", "Beekmans Heftrucks", "n.d.", "*Reachtrucks*. " + ACC.format(d="October 18, 2026") +
                 "https://www.beekmansheftrucks.nl/product-categorie/reachtrucks/"),
    "itolang":  ("Itolang.", "Itolang", "n.d.", "*Lease*. " + ACC.format(d="October 18, 2026") + "https://itolang.nl/lease"),
    "solidlift": ("Solid Lift.", "Solid Lift", "n.d.", "*Reachtrucks*. " + ACC.format(d="October 18, 2026") +
                  "https://www.solidlift.nl/reachtrucks"),
    "statista": ("Statista.", "Statista", "n.d.",
                 "[Electricity prices for non-household consumers in the Netherlands, Eurostat nrg_pc_205]. " +
                 ACC.format(d="October 18, 2026") + "https://www.statista.com/statistics/596254/electricity-non-household-price-netherlands"),
    "extensiv": ("Extensiv.", "Extensiv", "n.d.",
                 "*3PL fulfillment KPIs: Formulas & benchmarks*. " + ACC.format(d="October 18, 2026") +
                 "https://www.extensiv.com/blog/3pl-fulfillment-kpis-formulas-benchmarks"),
    "prest_hand": ("Prestatie Personeelsdiensten.", "Prestatie Personeelsdiensten", "n.d.",
                   "*Handmatig containers lossen*. " + ACC.format(d="October 18, 2026") +
                   "https://prestatie.eu/containers-lossen-en-laden/handmatig-containers-lossen/"),
    "prest_loose": ("Prestatie Personeelsdiensten.", "Prestatie Personeelsdiensten", "n.d.",
                    "*Looseloaded containers lossen*. " + ACC.format(d="October 18, 2026") +
                    "https://prestatie.eu/containers-lossen-en-laden/looseloaded-containers-lossen/"),
    "boxic":    ("boxic24.", "boxic24", "n.d.", "*Fetra 28301* [Product listing]. " + ACC.format(d="October 18, 2026") +
                 "https://boxic24.com/english/fetra-28301.html"),
    "ldirect":  ("Logistiekdirect.", "Logistiekdirect", "n.d.",
                 "*Magazijnbak Eco Euronorm 64 liter, 600x400x320 mm* [Product listing]. " + ACC.format(d="October 18, 2026") +
                 "https://www.logistiekdirect.be/magazijnbak-eco-euronorm-64-liter-donkergrijs-600x400x320mm"),
    "mseeker":  ("Machineseeker.", "Machineseeker", "n.d.", "*Vogel Verpackungen Starter* [Product listing]. " +
                 ACC.format(d="October 18, 2026") + "https://www.machineseeker.com/vogel+verpackungen-starter/i-22833460"),
    "cromwell": ("Cromwell.", "Cromwell", "n.d.", "[Extendable roller conveyor, product listing]. " + ACC.format(d="October 18, 2026") +
                 "https://cromwell.co.uk/"),
    "shelving": ("Shelving.com.", "Shelving.com", "n.d.", "*Gravity flow rack prices* [Price list]. " + ACC.format(d="October 18, 2026") +
                 "https://www.shelving.com/v/gravityflowrackprices.pdf"),
    "latestcost": ("LatestCost.", "LatestCost", "n.d.", "*Put-to-light system cost*. " + ACC.format(d="October 18, 2026") +
                   "https://latestcost.com/put-light-system-cost/"),
    "bechtle":  ("Bechtle.", "Bechtle", "n.d.", "*Zebra MC3300 charging cradle base* [Product listing]. " +
                 ACC.format(d="October 18, 2026") + "https://www.bechtle.com/de-en/shop/zebra-mc3300-charging-cradle-base--4258458--p"),
    "relevator": ("Relevator Group.", "Relevator Group", "n.d.", "*Vertical lift modules* [Product category]. " +
                  ACC.format(d="October 18, 2026") + "https://www.relevatorgroup.com/product-category/vertical-storage-systems/vertical-lift-modules/"),
    "ciscoeagle": ("Cisco-Eagle.", "Cisco-Eagle", "n.d.", "*Vertical lift modules vs. horizontal carousels*. " +
                   ACC.format(d="October 18, 2026") + "https://www.cisco-eagle.com/blog/?p=2003"),
    "commander": ("Commander.", "Commander", "n.d.", "*LogiMat vertical lift module* [Product page]. " + ACC.format(d="October 18, 2026") +
                  "https://www.commander.ca/product-logimat-vertical-lift-module/"),
    "mmh":      ("Modern Materials Handling.", "Modern Materials Handling", "n.d.", "*Van Meter optimizes with vertical lift modules*. " +
                 ACC.format(d="October 18, 2026") + "https://www.mmh.com/article/van_meter_optimizes_with_vertical_lift_modules_vlms"),
    "evofenedex": ("Evofenedex.", "Evofenedex", "n.d.", "*PGS 37: Opslag lithiumbatterijen*. " + ACC.format(d="October 18, 2026") +
                   "https://www.evofenedex.nl/kennis/gevaarlijke-stoffen/pgs-37-opslag-lithiumbatterijen"),
    "specialcargo": ("Special Cargo.", "Special Cargo", "n.d.", "*PGS 37-2 onder de loep*. " + ACC.format(d="October 18, 2026") +
                     "https://services.specialcargo.com/nl-nl/blog/kennisbank/pgs-372/"),
    "bovag":    ("BOVAG.", "BOVAG", "n.d.", "*Veelgestelde vragen over PGS 37-2*. " + ACC.format(d="October 18, 2026") +
                 "https://mijn.bovag.nl/dossiers/veelgestelde-vragen-over-pgs-37-2"),
    "manutan":  ("Manutan.", "Manutan", "n.d.",
                 "*Open stelling van plaatstaal Quick-Fix Plus, hoogte 2000 mm, breedte 1000 mm* [Product listing]. " +
                 ACC.format(d="October 18, 2026") + "https://www.manutan.be/nl/mab/open-stelling-van-plaatstaal-quick-fix-plus-hoogte-2000-mm-breedte-1000-mm"),
}
PC = {   # personal communications: in-text only (APA 7, section 8.9)
    "S004": "Rogier, course teacher, personal communication, October 7, 2026",
    "S013": "Rogier, course teacher, personal communication, October 7, 2026",
    "S026": "Rogier, course teacher, personal communication, October 2026",
}
SID = {   # source register ID -> works it stands for (documentation/sources.md)
    "S001": ["brief"], "S002": ["data"], "S003": ["gadeyne"], "S006": ["jh_etv"], "S008": ["jh_ere"], "S009": ["jh_risk"],
    "S010": ["jh_eje"], "S011": ["tbsg"], "S012": ["jh_ezs"], "S014": ["dekoster"], "S015": ["ssi", "stow"], "S016": ["iplo"],
    "S017": ["lecture"], "S018": ["cbs_news", "cbs_long"], "S019": ["cao", "cpeople"], "S020": ["indexbox", "tracking"],
    "S021": ["liftlease", "beekmans", "itolang", "solidlift"], "S022": ["statista"], "S023": ["extensiv"],
    "S024": ["prest_hand", "prest_loose"], "S025a": ["boxic"], "S025b": ["ldirect"], "S025d": ["mseeker"], "S025e": ["cromwell"],
    "S025f": ["shelving"], "S025g": ["latestcost"], "S025h": ["bechtle"], "S027": ["relevator"],
    "S028": ["ciscoeagle", "commander", "mmh"], "S029": ["evofenedex", "specialcargo", "bovag"], "S030": ["manutan"],
    "S031": ["slack"], "S032": ["baker"], "S033": ["huertas"],
}


def _plain(s):
    return re.sub(r"[*\[\]]", "", s).lower()


def _years():
    """APA a/b suffixes for the same author and year (ordered by title)."""
    groups = {}
    for k, (a, _, y, rest) in REFS.items():
        groups.setdefault((a, y), []).append(k)
    out = {}
    for (a, y), keys in groups.items():
        keys = sorted(keys, key=lambda k: _plain(REFS[k][3]))
        for i, k in enumerate(keys):
            suf = "abcdefghij"[i] if len(keys) > 1 else ""
            out[k] = (f"{y}-{suf}" if y == "n.d." and suf else f"{y}{suf}")
    return out


YEAR = _years()


def in_text(key):
    return f"{REFS[key][1]}, {YEAR[key]}"


def _cite_id(sid, used):
    if sid in PC:
        return PC[sid]
    keys = SID[sid]
    used.update(keys)
    groups = {}                                         # same author: "(Author, n.d.-a, n.d.-b)"
    for k in keys:
        groups.setdefault(REFS[k][1], []).append(YEAR[k])
    return "; ".join(f"{au}, {', '.join(ys)}" for au, ys in groups.items())


TOKEN = re.compile(r"\b(S0\d\d[a-h]?)\b")


def cite_text(text, used):
    """Replace every source ID in `text` by its APA in-text citation (parentheses are kept from the text)."""
    if not isinstance(text, str) or not TOKEN.search(text):
        return text
    text = re.sub(r",\s*(?=S0\d\d[a-h]?\b)", "; ", text)    # "(2.6 m, S006)" -> "(2.6 m; Jungheinrich, 2019)"
    text = re.sub(r"(?<=\))\s*\+\s*(?=S0)", "; ", text)
    return TOKEN.sub(lambda m: _cite_id(m.group(1), used), text)


def reference_list(used):
    """APA reference list (alphabetical by author, then year, then title) of the cited works."""
    keys = sorted(used, key=lambda k: (_plain(REFS[k][0]), YEAR[k].replace("n.d.", "0000"), _plain(REFS[k][3])))
    return [f"{REFS[k][0]} ({YEAR[k]}). {REFS[k][3]}" for k in keys]


def add_reference_list(doc, used, heading="References", level=1, size=10):
    """Write the APA reference list into a python-docx Document (hanging indent, '*...*' in italics)."""
    from docx.shared import Pt, Cm
    doc.add_heading(heading, level=level)
    note = doc.add_paragraph()
    r = note.add_run("APA 7th edition. Conversations with the course teacher and DHL are personal communications and are cited "
                     "in the text only.")
    r.italic = True; r.font.size = Pt(8.5)
    for ref in reference_list(used):
        p = doc.add_paragraph()
        pf = p.paragraph_format
        pf.left_indent = Cm(1.27); pf.first_line_indent = Cm(-1.27); pf.space_after = Pt(4)
        for i, seg in enumerate(ref.split("*")):
            if seg:
                run = p.add_run(seg); run.italic = (i % 2 == 1); run.font.size = Pt(size)
