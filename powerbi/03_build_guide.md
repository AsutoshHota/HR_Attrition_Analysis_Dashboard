# Power BI Build Guide (about 30-45 minutes)

Follow these steps in **Power BI Desktop** (free, Windows). Numbers you should see are listed so you can check your work.

## Step 1 - Load the data
1. Save `data/WA_Fn-UseC_-HR-Employee-Attrition.csv` somewhere on your PC.
2. **Home > Transform data**. Create the two queries from `01_power_query.m` (`FilePath`, then `HR`). Edit the path in `FilePath`.
3. **Close & Apply**.

**Check:** table `HR` has **1,470 rows**.

## Step 2 - Sort the bands (important)
Without this, bands appear alphabetically ("11+ yrs" before "2-5 yrs").
Select the column in the Data pane > **Column tools > Sort by column**:

| Column | Sort by |
|---|---|
| TenureBand | TenureBandSort |
| SalaryBand | SalaryBandSort |
| AgeBand | AgeBandSort |

## Step 3 - Add measures
1. **Home > Enter data**, leave it empty, name the table `_Measures`, Load.
2. Add every measure from `02_dax_measures.dax` (right-click `_Measures > New measure`).
3. **Modeling > New table** and paste the `High Risk Groups` calculated table.
4. Format: `Attrition Rate`, `Company Attrition Rate`, `Share of All Leavers`, `AttritionRate` (in High Risk Groups) as **Percentage, 1 decimal**.

**Check:** `Total Employees` = 1470, `Leavers` = 237, `Attrition Rate` = 16.1%. The `High Risk Groups` table has 25 rows.

## Step 4 - Apply theme
**View > Themes > Browse for themes** > select `theme.json`.

## Step 5 - Page 1: "Attrition Overview"
Canvas 16:9. Layout (top to bottom):

| Area | Visual | Fields |
|---|---|---|
| Top row, 4 cards | Card | `Total Employees`, `Leavers`, `Attrition Rate`, `Avg Monthly Income` |
| Left | Clustered column | X: `Department` / Y: `Attrition Rate` |
| Centre | Clustered column | X: `TenureBand` / Y: `Attrition Rate` |
| Right | Clustered column | X: `SalaryBand` / Y: `Attrition Rate` |
| Bottom left | Bar | Y: `JobRole` / X: `Attrition Rate` (sort descending) |
| Bottom right | Column | X: `OverTime` / Y: `Attrition Rate` |
| Left edge | Slicers | `Department`, `Gender`, `AgeBand` |

For each column chart: **Format > Data labels ON**, add a **Constant line** (Analytics pane) using `Company Attrition Rate` as the average line, and colour bars with **Format > Columns > Colors > fx > Field value > `Risk Colour`**.

**Values you should see**

| Department | Rate | Tenure | Rate | Salary | Rate |
|---|---|---|---|---|---|
| Sales | 20.6% | 0-1 yrs | 34.9% | Low (<3K) | 28.6% |
| Human Resources | 19.1% | 2-5 yrs | 15.5% | Mid (3K-6K) | 12.7% |
| R&D | 13.8% | 6-10 yrs | 12.3% | High (6K-10K) | 12.0% |
| | | 11+ yrs | 8.1% | Very High (10K+) | 8.9% |

## Step 6 - Page 2: "High-Risk Groups"
1. **Table** visual using the `High Risk Groups` table: `Department`, `TenureBand`, `SalaryBand`, `OverTime`, `Employees`, `Leavers`, `AttritionRate`, `RiskMultiple`.
2. Sort by `AttritionRate` descending.
3. On `AttritionRate`: **Conditional formatting > Data bars** (red). On `RiskMultiple`: **Background colour > Rules** (>= 2 dark red, >= 1.25 light red).
4. Add a card using the `Headline` measure as a dynamic subtitle.

**Check:** top row is *R&D | 0-1 yrs | Low (<3K) | OverTime Yes | 28 employees | 71.4%* (4.43x average).

## Step 7 - Page 3 (optional): "Why people leave"
- Matrix: rows `JobRole`, columns `TenureBand`, values `Attrition Rate` (colour scale: white to red).
- Column chart: `JobSatisfactionLabel` vs `Attrition Rate`.
- Column chart: `WorkLifeBalanceLabel` vs `Attrition Rate`.
- Two cards: `Overtime Attrition Rate` (30.5%) and `Non-Overtime Attrition Rate` (10.4%).

## Step 8 - Publish / share
Save as `HR_Attrition_Dashboard.pbix`. Export screenshots (File > Export > PDF) for your portfolio/GitHub README. Put the `.pbix` and screenshots in the repo.
