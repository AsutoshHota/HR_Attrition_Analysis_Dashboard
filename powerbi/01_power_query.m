// =====================================================================
// HR ATTRITION DASHBOARD - POWER QUERY (M) SCRIPT
// =====================================================================
// HOW TO USE
//  1. Power BI Desktop > Home > Transform data > Power Query Editor
//  2. Home > New Source > Blank Query > Advanced Editor
//     Paste QUERY 1 (FilePath) and name the query:  FilePath
//  3. Create another Blank Query, paste QUERY 2 and name it:  HR
//  4. Edit the path in FilePath to where the CSV is saved on your PC
//  5. Close & Apply
//
// The bands below are IDENTICAL to python/analysis.py, so both
// give the same numbers (overall attrition = 16.1%).
// =====================================================================


// ---------------------------------------------------------------------
// QUERY 1  ->  name it:  FilePath
// ---------------------------------------------------------------------
"C:\HR_Attrition\data\WA_Fn-UseC_-HR-Employee-Attrition.csv" meta [IsParameterQuery = true, Type = "Text", IsParameterQueryRequired = true]


// ---------------------------------------------------------------------
// QUERY 2  ->  name it:  HR
// ---------------------------------------------------------------------
let
    Source = Csv.Document(
        File.Contents(FilePath),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.None]
    ),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),

    // ---- 1. Data types -------------------------------------------------
    Typed = Table.TransformColumnTypes(
        Promoted,
        {
            {"Age", Int64.Type}, {"Attrition", type text}, {"BusinessTravel", type text},
            {"DailyRate", Int64.Type}, {"Department", type text}, {"DistanceFromHome", Int64.Type},
            {"Education", Int64.Type}, {"EducationField", type text}, {"EmployeeNumber", Int64.Type},
            {"EnvironmentSatisfaction", Int64.Type}, {"Gender", type text}, {"HourlyRate", Int64.Type},
            {"JobInvolvement", Int64.Type}, {"JobLevel", Int64.Type}, {"JobRole", type text},
            {"JobSatisfaction", Int64.Type}, {"MaritalStatus", type text}, {"MonthlyIncome", Int64.Type},
            {"MonthlyRate", Int64.Type}, {"NumCompaniesWorked", Int64.Type}, {"OverTime", type text},
            {"PercentSalaryHike", Int64.Type}, {"PerformanceRating", Int64.Type},
            {"RelationshipSatisfaction", Int64.Type}, {"StockOptionLevel", Int64.Type},
            {"TotalWorkingYears", Int64.Type}, {"TrainingTimesLastYear", Int64.Type},
            {"WorkLifeBalance", Int64.Type}, {"YearsAtCompany", Int64.Type},
            {"YearsInCurrentRole", Int64.Type}, {"YearsSinceLastPromotion", Int64.Type},
            {"YearsWithCurrManager", Int64.Type}
        }
    ),

    // ---- 2. Drop constant columns (no information) ---------------------
    Removed = Table.RemoveColumns(Typed, {"EmployeeCount", "Over18", "StandardHours"}),

    // ---- 3. Attrited flag (1 = left, 0 = stayed) -----------------------
    AddAttrited = Table.AddColumn(
        Removed, "Attrited", each if [Attrition] = "Yes" then 1 else 0, Int64.Type
    ),

    // ---- 4. Tenure band -------------------------------------------------
    AddTenure = Table.AddColumn(
        AddAttrited, "TenureBand",
        each if [YearsAtCompany] <= 1 then "0-1 yrs"
             else if [YearsAtCompany] <= 5 then "2-5 yrs"
             else if [YearsAtCompany] <= 10 then "6-10 yrs"
             else "11+ yrs",
        type text
    ),
    AddTenureSort = Table.AddColumn(
        AddTenure, "TenureBandSort",
        each if [YearsAtCompany] <= 1 then 1
             else if [YearsAtCompany] <= 5 then 2
             else if [YearsAtCompany] <= 10 then 3
             else 4,
        Int64.Type
    ),

    // ---- 5. Salary band (monthly income) --------------------------------
    AddSalary = Table.AddColumn(
        AddTenureSort, "SalaryBand",
        each if [MonthlyIncome] < 3000 then "Low (<3K)"
             else if [MonthlyIncome] < 6000 then "Mid (3K-6K)"
             else if [MonthlyIncome] < 10000 then "High (6K-10K)"
             else "Very High (10K+)",
        type text
    ),
    AddSalarySort = Table.AddColumn(
        AddSalary, "SalaryBandSort",
        each if [MonthlyIncome] < 3000 then 1
             else if [MonthlyIncome] < 6000 then 2
             else if [MonthlyIncome] < 10000 then 3
             else 4,
        Int64.Type
    ),

    // ---- 6. Age band ------------------------------------------------------
    AddAge = Table.AddColumn(
        AddSalarySort, "AgeBand",
        each if [Age] < 25 then "<25"
             else if [Age] < 35 then "25-34"
             else if [Age] < 45 then "35-44"
             else if [Age] < 55 then "45-54"
             else "55+",
        type text
    ),
    AddAgeSort = Table.AddColumn(
        AddAge, "AgeBandSort",
        each if [Age] < 25 then 1
             else if [Age] < 35 then 2
             else if [Age] < 45 then 3
             else if [Age] < 55 then 4
             else 5,
        Int64.Type
    ),

    // ---- 7. Readable labels for coded columns ----------------------------
    AddJobSat = Table.AddColumn(
        AddAgeSort, "JobSatisfactionLabel",
        each if [JobSatisfaction] = 1 then "Low"
             else if [JobSatisfaction] = 2 then "Medium"
             else if [JobSatisfaction] = 3 then "High"
             else "Very High",
        type text
    ),
    AddWLB = Table.AddColumn(
        AddJobSat, "WorkLifeBalanceLabel",
        each if [WorkLifeBalance] = 1 then "Bad"
             else if [WorkLifeBalance] = 2 then "Good"
             else if [WorkLifeBalance] = 3 then "Better"
             else "Best",
        type text
    )
in
    AddWLB
