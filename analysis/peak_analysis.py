"""
PHASE 1 - PEAK ANALYSIS.
Daily/weekly throughput (lines, units, orders, shipments), peak day/week,
peak hour from PICK DATE, peak vs average ratios. Distinguishes AVERAGE vs PEAK.
Writes daily series table + metrics + figure.
"""
import numpy as np
import pandas as pd
from load_data import combined_outbound
from _util import save_table, save_fig, update_metrics
import matplotlib.pyplot as plt

ob = combined_outbound()
ob["PICKED QTY"] = pd.to_numeric(ob["PICKED QTY"], errors="coerce")
ob["DATE"] = pd.to_datetime(ob["DATE"], errors="coerce")
ob["PICK DATE"] = pd.to_datetime(ob["PICK DATE"], errors="coerce")

# daily throughput on ship DATE
daily = ob.groupby(ob["DATE"].dt.date).agg(
    lines=("ORDER NO", "size"),
    units=("PICKED QTY", "sum"),
    orders=("ORDER NO", "nunique"),
    shipments=("SHIPMENT ID", "nunique"),
)
daily.index = pd.to_datetime(daily.index)
daily["weekday"] = daily.index.day_name()
# restrict to actual operating days (lines>0)
op = daily[daily["lines"] > 0]
save_table(daily, "throughput_daily.csv")

def stats(s):
    return {"mean": round(float(s.mean()), 0), "median": float(s.median()),
            "peak": float(s.max()), "peak_date": str(s.idxmax().date()),
            "peak_over_avg": round(float(s.max() / s.mean()), 2)}

# weekly
wk = op.resample("W").agg({"lines": "sum", "units": "sum", "orders": "sum"})
wk_lines = wk["lines"][wk["lines"] > 0]

# peak hour from pick timestamps
ph = ob.dropna(subset=["PICK DATE"]).copy()
ph["hour"] = ph["PICK DATE"].dt.hour
hourly = ph.groupby("hour").size()
# average picks per operating day in each hour
n_days = ph["PICK DATE"].dt.date.nunique()
hourly_avg = (hourly / n_days).round(0)

# weekday seasonality
wd = op.groupby("weekday")["lines"].mean().reindex(
    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])

metrics = {
    "operating_days": int(len(op)),
    "lines": stats(op["lines"]),
    "units": stats(op["units"]),
    "orders": stats(op["orders"]),
    "shipments": stats(op["shipments"]),
    "weekly_lines": {"mean": round(float(wk_lines.mean()), 0), "peak": float(wk_lines.max()),
                      "peak_week": str(wk_lines.idxmax().date())},
    "peak_hour": int(hourly_avg.idxmax()),
    "peak_hour_avg_picks": float(hourly_avg.max()),
    "hourly_avg_picks": {int(h): float(v) for h, v in hourly_avg.items()},
    "weekday_avg_lines": {k: round(float(v), 0) for k, v in wd.dropna().items()},
    "design_note": "Design to PEAK day, not average.",
}
update_metrics("peak", metrics)

# figure: daily lines with peak
fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(op.index, op["lines"], color="#6c8eef", lw=1)
ax.axhline(op["lines"].mean(), color="#999", ls="--", lw=1, label=f"avg {op['lines'].mean():.0f}")
pk = op["lines"].idxmax()
ax.scatter([pk], [op['lines'].max()], color="#e08a5b", zorder=5, label=f"peak {op['lines'].max():.0f}")
ax.set_title("Daily shipped order-lines (Q2 2025)"); ax.set_ylabel("order lines")
ax.legend(); ax.grid(alpha=0.3)
save_fig(fig, "throughput_daily.png")

# figure: hourly pick profile
fig2, ax2 = plt.subplots(figsize=(8, 4))
ax2.bar(hourly_avg.index, hourly_avg.values, color="#6c8eef")
ax2.set_title("Average picks per hour of day"); ax2.set_xlabel("hour"); ax2.set_ylabel("avg picks")
save_fig(fig2, "pick_hourly_profile.png")

print(f"Operating days={len(op)}")
print(f"Lines/day: {metrics['lines']}")
print(f"Units/day: {metrics['units']}")
print(f"Orders/day: {metrics['orders']}")
print(f"Weekly lines: {metrics['weekly_lines']}")
print(f"Peak hour={metrics['peak_hour']}:00 (~{metrics['peak_hour_avg_picks']:.0f} picks) ")
print(f"Weekday avg lines: {metrics['weekday_avg_lines']}")
