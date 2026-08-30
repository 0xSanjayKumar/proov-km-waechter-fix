# analyze.py
# KEY FINDING: km_since_service is by far the strongest predictor (Cohen's d = 1.06, 61% higher
# in breakdown cars); avg_daily_km and load_factor add medium signal (d ≈ 0.6 and 0.5). Total
# mileage (odometer_km) and age_years show virtually zero separation (d < 0.01 each) — the
# obvious guesses are wrong. The risk score is built from the three real separators only.

import math
import pandas as pd


# -- 1. Load ------------------------------------------------------------------
df = pd.read_csv("fleet_history.csv")
yes = df[df.broke_down == 1]    # 26 cars that broke down
no  = df[df.broke_down == 0]    # 94 cars that did not


# -- 2. Column-by-column group comparison -------------------------------------
# For each numeric column we compute:
#   • mean for each group and the percentage difference
#   • Cohen's d — a standard measure of how far apart two distributions are
#     (< 0.2 = negligible, 0.2–0.5 = small, 0.5–0.8 = medium, > 0.8 = large)
#   • Pearson r with the broke_down flag
#
# This lets the data answer the question instead of assuming "mileage must matter".

features = ["odometer_km", "km_since_service", "avg_daily_km", "load_factor", "age_years"]


def cohens_d(a: pd.Series, b: pd.Series) -> float:
    """Pooled-std Cohen's d between two samples."""
    n1, n2 = len(a), len(b)
    pooled = math.sqrt(((n1 - 1) * a.std() ** 2 + (n2 - 1) * b.std() ** 2) / (n1 + n2 - 2))
    return (a.mean() - b.mean()) / pooled if pooled else 0.0


print("=" * 70)
print("STEP 2 — Which columns separate the two groups?")
print(f"  Broke down: {len(yes)} cars    Did not: {len(no)} cars")
print()
print(f"  {'column':<22} {'mean_broke':>11} {'mean_ok':>9} {'diff%':>7}  {'cohen_d':>8}  {'r':>6}  verdict")
print("  " + "-" * 68)

SIGNAL_COLS = []
for col in features:
    mb = yes[col].mean()
    mo = no[col].mean()
    diff = (mb - mo) / mo * 100 if mo != 0 else float("nan")
    d = cohens_d(yes[col], no[col])
    r = df[col].corr(df["broke_down"])
    if abs(d) >= 0.5:
        verdict = "SEPARATES (strong)" if abs(d) >= 0.8 else "SEPARATES (medium)"
        SIGNAL_COLS.append(col)
    elif abs(d) >= 0.2:
        verdict = "weak signal"
    else:
        verdict = "no signal"
    print(f"  {col:<22} {mb:>11.1f} {mo:>9.1f} {diff:>+7.1f}%  {d:>+8.3f}  {r:>+6.3f}  {verdict}")

print()
print(f"  Columns that genuinely separate: {SIGNAL_COLS}")
print(f"  Columns that do NOT separate:    odometer_km, age_years")
print()


# -- 3. Risk score 0–100 -------------------------------------------------------
# Method: for each of the three signal columns, rank every car from 0 (safest value
# seen in the fleet) to 1 (riskiest value seen), using min-max scaling.  Then
# combine those three 0-1 scores with weights that reflect how strongly each column
# separates the groups (Cohen's d drives the weights).
#
# No black-box ML: every number in the score can be traced back to a single
# observable measurement on the car.

weights = {col: abs(cohens_d(yes[col], no[col])) for col in SIGNAL_COLS}
total_w = sum(weights.values())

# Min-max scale each signal column to [0, 1]
scaled = pd.DataFrame({"car_id": df["car_id"]})
for col in SIGNAL_COLS:
    col_min = df[col].min()
    col_max = df[col].max()
    scaled[col + "_s"] = (df[col] - col_min) / (col_max - col_min)

# Weighted average → stretch to 0–100
scaled["risk_score"] = sum(
    scaled[col + "_s"] * (weights[col] / total_w) for col in SIGNAL_COLS
) * 100

df = df.merge(scaled[["car_id", "risk_score"]], on="car_id")


# -- 4. Rank by risk, highest first --------------------------------------------
ranked = df.sort_values("risk_score", ascending=False).reset_index(drop=True)

print("=" * 70)
print("STEP 4 -- Top 10 cars by risk score")
print()
print(f"  {'rank':<5} {'car_id':<12} {'risk':>6}  {'km_since_svc':>13}  {'avg_daily':>10}  {'load':>6}  broke?")
print("  " + "-" * 63)
for i, row in ranked.head(10).iterrows():
    flag = " <<< already broke" if row["broke_down"] == 1 else ""
    print(
        f"  {i+1:<5} {row['car_id']:<12} {row['risk_score']:>6.1f}"
        f"  {row['km_since_service']:>13,.0f}"
        f"  {row['avg_daily_km']:>10,.0f}"
        f"  {row['load_factor']:>6.2f}"
        f"  {int(row['broke_down'])}{flag}"
    )

print()
print("=" * 70)
print("Done.")
