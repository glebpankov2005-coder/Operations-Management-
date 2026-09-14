"""Shared helpers for Phase 1 analysis modules."""
import os
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from cycler import cycler

BASE = os.path.join(os.path.dirname(__file__), "..")
TABLES = os.path.join(BASE, "outputs", "tables")
FIGS = os.path.join(BASE, "outputs", "figures")
REPORTS = os.path.join(BASE, "outputs", "reports")
for d in (TABLES, FIGS, REPORTS):
    os.makedirs(d, exist_ok=True)

# ---- one cohesive chart style across every figure (premium, matches the maps) ----
PALETTE = ["#6c8eef", "#e08a5b", "#74cf9a", "#9db4fb", "#f2a6a6", "#c9a9e0", "#f4c58a", "#7fc8c0"]
def _pick_font():
    for f in ["Segoe UI", "Calibri", "Helvetica Neue", "Arial", "DejaVu Sans"]:
        if any(f.lower() == x.name.lower() for x in fm.fontManager.ttflist):
            return f
    return "DejaVu Sans"
def apply_style():
    plt.rcParams.update({
        "font.family": _pick_font(), "font.size": 10.5,
        "figure.facecolor": "white", "savefig.facecolor": "white", "savefig.dpi": 130,
        "axes.facecolor": "white", "axes.edgecolor": "#c7cede", "axes.linewidth": 0.9,
        "axes.grid": True, "axes.grid.axis": "y", "grid.color": "#e8ecf5", "grid.linewidth": 0.8,
        "axes.axisbelow": True, "axes.spines.top": False, "axes.spines.right": False,
        "axes.titlesize": 12.5, "axes.titleweight": "bold", "axes.titlecolor": "#1f2937",
        "axes.labelcolor": "#374151", "axes.labelsize": 10,
        "xtick.color": "#4b5563", "ytick.color": "#4b5563", "text.color": "#1f2937",
        "xtick.labelsize": 9, "ytick.labelsize": 9, "legend.frameon": False, "legend.fontsize": 9,
        "axes.prop_cycle": cycler(color=PALETTE),
    })
apply_style()


def save_table(df, name):
    path = os.path.join(TABLES, name)
    df.to_csv(path, index=True)
    return path


def save_fig(fig, name):
    path = os.path.join(FIGS, name)
    fig.savefig(path, dpi=110, bbox_inches="tight")
    plt.close(fig)
    return path


def update_metrics(section, data):
    """Merge a section into outputs/reports/phase1_metrics.json."""
    path = os.path.join(REPORTS, "phase1_metrics.json")
    cur = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            cur = json.load(f)
    cur[section] = data
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cur, f, indent=2, default=str)
