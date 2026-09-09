"""
PHASE 3 - DECISION MATRIX.
Weighted scoring of the three design options against the criteria in the brief.
Scores are documented ASSESSMENTS (1=worst .. 5=best), not measured values;
capacity/space scores are anchored to the capacity model. Weights are tunable.
Outputs a scored table + weight-sensitivity check.
"""
import pandas as pd
from _util import save_table, save_fig, update_metrics
import matplotlib.pyplot as plt

# criterion: (weight, higher-is-better)
weights = {
    "Space fit (7,000 m2)": 0.20,
    "Labour efficiency":    0.20,
    "CAPEX (lower=better)": 0.15,
    "Travel / throughput":  0.15,
    "Flexibility":          0.10,
    "Simplicity / low risk":0.10,
    "Peak resilience":      0.10,
}
# scores 1..5
scores = {
    "A - Conventional+":     [2, 2, 5, 2, 5, 5, 2],
    "B - Hybrid density":    [4, 4, 3, 4, 4, 3, 4],
    "C - Semi-automated":    [5, 5, 1, 5, 2, 2, 4],
}
rationale = {
    "A - Conventional+":  "cheapest & simplest, but borderline on space and high travel/labour",
    "B - Hybrid density": "fits with buffer; batching+slotting cut labour; moderate cost/risk",
    "C - Semi-automated": "densest & lowest labour, but high CAPEX, complex, less flexible",
}

crit = list(weights.keys())
w = pd.Series(weights)
df = pd.DataFrame(scores, index=crit).T
df_weighted = (df * w).sum(axis=1).round(2)
out = df.copy()
out["WEIGHTED TOTAL"] = df_weighted
out["rationale"] = pd.Series(rationale)
out = out.sort_values("WEIGHTED TOTAL", ascending=False)
save_table(out, "decision_matrix.csv")

# weight-sensitivity: if labour+CAPEX dominate (cost-driven org) vs space-driven
def weighted(scores_row, wt):
    return round(sum(s * wt[c] for s, c in zip(scores_row, crit)), 2)

alt_cost = dict(weights); alt_cost.update({"Labour efficiency": 0.30, "CAPEX (lower=better)": 0.25,
                                           "Space fit (7,000 m2)": 0.10, "Travel / throughput": 0.10,
                                           "Flexibility": 0.10, "Simplicity / low risk": 0.10, "Peak resilience": 0.05})
alt_space = dict(weights); alt_space.update({"Space fit (7,000 m2)": 0.35, "Peak resilience": 0.20})

sens = {}
for name, row in scores.items():
    sens[name] = {
        "base": weighted(row, weights),
        "cost_driven": weighted(row, alt_cost),
        "space_driven": weighted(row, alt_space),
    }
sens_df = pd.DataFrame(sens).T
save_table(sens_df, "decision_matrix_sensitivity.csv")

update_metrics("decision", {
    "weights": weights,
    "scores": scores,
    "weighted_totals": df_weighted.to_dict(),
    "ranking": list(out.index),
    "winner": out.index[0],
    "sensitivity": sens,
})

# figure
fig, ax = plt.subplots(figsize=(7, 4))
order = out.index.tolist()
ax.barh(order[::-1], [df_weighted[o] for o in order[::-1]], color=["#6c8eef", "#8fa9f2", "#c2cff8"][::-1])
ax.set_xlim(0, 5); ax.set_xlabel("weighted score (max 5)")
ax.set_title("Design-option decision matrix (weighted)")
for i, o in enumerate(order[::-1]):
    ax.text(df_weighted[o], i, f" {df_weighted[o]}", va="center", fontsize=9)
save_fig(fig, "decision_matrix.png")

print("WEIGHTED SCORING:"); print(out.to_string())
print("\nWEIGHT SENSITIVITY (base / cost-driven / space-driven):"); print(sens_df.round(2).to_string())
print("\nWINNER (base weights):", out.index[0])
