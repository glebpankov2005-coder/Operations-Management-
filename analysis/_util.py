"""Shared helpers for Phase 1 analysis modules."""
import os
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = os.path.join(os.path.dirname(__file__), "..")
TABLES = os.path.join(BASE, "outputs", "tables")
FIGS = os.path.join(BASE, "outputs", "figures")
REPORTS = os.path.join(BASE, "outputs", "reports")
for d in (TABLES, FIGS, REPORTS):
    os.makedirs(d, exist_ok=True)


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
