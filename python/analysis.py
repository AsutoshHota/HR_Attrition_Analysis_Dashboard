"""
HR Attrition Analysis - data preparation + analysis
----------------------------------------------------
Dataset : IBM HR Analytics Employee Attrition & Performance (Kaggle)
Input   : data/WA_Fn-UseC_-HR-Employee-Attrition.csv
Output  : data/processed/hr_clean.csv            <- load this into Power BI
          data/processed/attrition_by_*.csv      <- summary tables
          data/processed/high_risk_groups.csv    <- highest-risk employee groups
          output/dashboard_preview.png           <- static preview of the dashboard

Run:  python python/analysis.py
"""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "WA_Fn-UseC_-HR-Employee-Attrition.csv"
OUT = ROOT / "data" / "processed"
FIG = ROOT / "output"
OUT.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- 1. LOAD
df = pd.read_csv(RAW, encoding="utf-8-sig")
print(f"Loaded {len(df):,} rows x {df.shape[1]} columns")

# ---------------------------------------------------------------- 2. CLEAN
# Constant columns carry no information
df = df.drop(columns=["EmployeeCount", "Over18", "StandardHours"])
assert df["EmployeeNumber"].is_unique, "EmployeeNumber must be unique"
assert df.isna().sum().sum() == 0, "Unexpected missing values"

df["Attrited"] = (df["Attrition"] == "Yes").astype(int)   # 1 = left, 0 = stayed

# ---------------------------------------------------------------- 3. BANDS
# Tenure band (years at company)
tenure_bins = [-1, 1, 5, 10, 100]
tenure_labels = ["0-1 yrs", "2-5 yrs", "6-10 yrs", "11+ yrs"]
df["TenureBand"] = pd.cut(df["YearsAtCompany"], bins=tenure_bins, labels=tenure_labels)

# Salary band (monthly income, USD)
sal_bins = [0, 2999, 5999, 9999, 10**9]
sal_labels = ["Low (<3K)", "Mid (3K-6K)", "High (6K-10K)", "Very High (10K+)"]
df["SalaryBand"] = pd.cut(df["MonthlyIncome"], bins=sal_bins, labels=sal_labels)

# Age band
df["AgeBand"] = pd.cut(df["Age"], bins=[0, 24, 34, 44, 54, 100],
                       labels=["<25", "25-34", "35-44", "45-54", "55+"])

# Readable labels for coded columns
df["EducationLevel"] = df["Education"].map(
    {1: "Below College", 2: "College", 3: "Bachelor", 4: "Master", 5: "Doctor"})
df["JobSatisfactionLabel"] = df["JobSatisfaction"].map(
    {1: "Low", 2: "Medium", 3: "High", 4: "Very High"})
df["WorkLifeBalanceLabel"] = df["WorkLifeBalance"].map(
    {1: "Bad", 2: "Good", 3: "Better", 4: "Best"})

# Sort helpers for Power BI (Sort by column)
df["TenureBandSort"] = df["TenureBand"].cat.codes + 1
df["SalaryBandSort"] = df["SalaryBand"].cat.codes + 1
df["AgeBandSort"] = df["AgeBand"].cat.codes + 1

df.to_csv(OUT / "hr_clean.csv", index=False)

# ---------------------------------------------------------------- 4. SUMMARIES
overall = df["Attrited"].mean()
print(f"\nOverall: {df['Attrited'].sum()} of {len(df):,} left  ->  {overall:.1%} attrition")


def summarise(col):
    t = (df.groupby(col, observed=True)
           .agg(Employees=("Attrited", "size"), Leavers=("Attrited", "sum"))
           .reset_index())
    t["AttritionRate"] = (t["Leavers"] / t["Employees"]).round(4)
    return t


for col, name in [("Department", "department"), ("TenureBand", "tenure"),
                  ("SalaryBand", "salary"), ("OverTime", "overtime"),
                  ("JobRole", "jobrole"), ("AgeBand", "age")]:
    t = summarise(col)
    t.to_csv(OUT / f"attrition_by_{name}.csv", index=False)
    print(f"\n-- Attrition by {col}")
    print(t.to_string(index=False, formatters={"AttritionRate": "{:.1%}".format}))

# ---------------------------------------------------------------- 5. HIGH-RISK GROUPS
# Combine the three dashboard dimensions (+ overtime) and rank segments by attrition.
MIN_SIZE = 20   # ignore tiny segments - their rates are unreliable
seg = (df.groupby(["Department", "TenureBand", "SalaryBand", "OverTime"], observed=True)
         .agg(Employees=("Attrited", "size"), Leavers=("Attrited", "sum"))
         .reset_index())
seg["AttritionRate"] = (seg["Leavers"] / seg["Employees"]).round(4)
seg["RiskMultiple"] = (seg["AttritionRate"] / overall).round(2)   # x times company average
risk = (seg[seg["Employees"] >= MIN_SIZE]
        .sort_values(["AttritionRate", "Employees"], ascending=False)
        .reset_index(drop=True))
risk.insert(0, "Rank", risk.index + 1)
risk.to_csv(OUT / "high_risk_groups.csv", index=False)
print(f"\n-- Top 8 highest-risk groups (min {MIN_SIZE} employees, company avg {overall:.1%})")
print(risk.head(8).to_string(index=False, formatters={"AttritionRate": "{:.1%}".format}))

# ---------------------------------------------------------------- 6. PREVIEW CHART
NAVY, RED, GREY = "#1F3A5F", "#D64550", "#B8C2CC"


SHORT = {"Research & Development": "R&D", "Human Resources": "HR",
         "Low (<3K)": "Low\n(<3K)", "Mid (3K-6K)": "Mid\n(3K-6K)",
         "High (6K-10K)": "High\n(6K-10K)", "Very High (10K+)": "Very High\n(10K+)"}


def bar(ax, tbl, col, title):
    colors = [RED if r > overall else GREY for r in tbl["AttritionRate"]]
    ax.bar([SHORT.get(str(v), str(v)) for v in tbl[col]], tbl["AttritionRate"] * 100, color=colors)
    ax.axhline(overall * 100, color=NAVY, ls="--", lw=1)
    ax.set_title(title, fontsize=11, fontweight="bold", color=NAVY, loc="left")
    ax.set_ylabel("Attrition %")
    for i, (r, n) in enumerate(zip(tbl["AttritionRate"], tbl["Employees"])):
        ax.text(i, r * 100 + 0.4, f"{r:.1%}\n(n={n})", ha="center", fontsize=8)
    ax.set_ylim(0, max(tbl["AttritionRate"]) * 100 * 1.3)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(axis="x", labelsize=8)


fig = plt.figure(figsize=(15, 9.5))
fig.suptitle("HR Attrition Analysis Dashboard (preview)", fontsize=16,
             fontweight="bold", color=NAVY, x=0.06, ha="left")
fig.text(0.06, 0.925,
         f"{len(df):,} employees  |  {df['Attrited'].sum()} leavers  |  "
         f"{overall:.1%} overall attrition  |  dashed line = company average",
         fontsize=10, color="#555")

gs = fig.add_gridspec(1, 3, left=0.06, right=0.97, top=0.86, bottom=0.52, wspace=0.22)
gs2 = fig.add_gridspec(1, 1, left=0.26, right=0.97, top=0.42, bottom=0.07)
ax1 = fig.add_subplot(gs[0, 0])
bar(ax1, summarise("Department"), "Department", "By Department")
ax2 = fig.add_subplot(gs[0, 1])
bar(ax2, summarise("TenureBand"), "TenureBand", "By Tenure Band")
ax3 = fig.add_subplot(gs[0, 2])
bar(ax3, summarise("SalaryBand"), "SalaryBand", "By Salary Level")

ax4 = fig.add_subplot(gs2[0, 0])
top = risk.head(8).iloc[::-1]
labels = [f"{SHORT.get(r.Department, r.Department)} | {r.TenureBand} | "
          f"{str(r.SalaryBand).split(chr(10))[0].split(' ')[0]} pay | OT:{r.OverTime}"
          for r in top.itertuples()]
ax4.barh(labels, top["AttritionRate"] * 100, color=RED)
ax4.axvline(overall * 100, color=NAVY, ls="--", lw=1)
for i, (r, n) in enumerate(zip(top["AttritionRate"], top["Employees"])):
    ax4.text(r * 100 + 0.5, i, f"{r:.0%}  (n={n})", va="center", fontsize=8)
ax4.set_title("Highest-risk employee groups (segments with 20+ employees)",
              fontsize=11, fontweight="bold", color=NAVY, loc="left")
ax4.set_xlabel("Attrition %")
ax4.set_xlim(0, 85)
ax4.tick_params(axis="y", labelsize=8)
ax4.spines[["top", "right"]].set_visible(False)

plt.savefig(FIG / "dashboard_preview.png", dpi=130)
print(f"\nSaved: {OUT / 'hr_clean.csv'}  and  {FIG / 'dashboard_preview.png'}")
