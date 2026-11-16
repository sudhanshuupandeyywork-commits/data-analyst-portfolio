# HR Attrition: who leaves, and what should we test first?

**Tools:** SQL (SQLite), Excel, Power BI
**Data:** IBM HR Analytics Employee Attrition, 1,470 employees. IBM data scientists made it up, so it's fictional.

## The problem

HR sees turnover rising. Which departments, roles and groups of employees have the highest attrition, what goes along with leaving, and which retention ideas are worth a small trial?

## What I found

1. **16.1% of employees have left** (237 of 1,470).
2. **Overtime is the strongest signal.** 30.5% of people working overtime left (127 of 416), against 10.4% of those who didn't (110 of 1,054). That is 2.9 times as often, and the 95% intervals (26% to 35% against 9% to 12%) don't overlap. The gap shows up in every income band and every tenure band, so it isn't just a side effect of pay or seniority. For example, among people earning under 3,000 a month, 56% of those on overtime left versus 17% of those who weren't.
3. **The first year is the riskiest.** 34.9% of people with up to 1 year at the company left (75 of 215), falling steadily to 8.1% for those with 11 or more years. Leavers had an average of 5.1 years at the company; stayers, 7.4.
4. **Overtime in the first year is the worst combination:** 55% of new joiners on overtime left (38 of 69).
5. **Sales Representatives have the highest attrition by role, 39.8%** (33 of 83), followed by Laboratory Technicians (23.9%, 62 of 259) and HR (23.1%, 12 of 52). Research Directors (2.5%) and Managers (4.9%) rarely leave.
6. **Pay and travel also line up with leaving.** Employees earning under 3,000 a month left at 28.6%, against 8.9% for those earning 10,000 or more. Frequent travellers left at 24.9%, against 8.0% for those who don't travel.

## What I'd recommend

These are things to test, not roll out.

- **Pilot a cap on overtime for people in their first two years,** starting in Sales and Laboratory Technician teams. Compare against similar teams that keep working as now, and look at leavers after two quarters.
- **Look at how new Sales Representatives are onboarded and paid.** They have the highest attrition, the lowest median pay of any role (2,579 a month, against 4,919 for the whole company) and a median of 2 years at the company, against 5 overall.
- **Ask people who leave why.** This data has no exit reasons, so everything above is a pattern, not an explanation.

## Data and cleaning

- Source: IBM HR Analytics Employee Attrition (Kaggle), 1,470 rows, 35 columns.
- I dropped `EmployeeCount`, `StandardHours` and `Over18` (the same value on every row) and the `EmployeeNumber` ID. No rows were removed or filled in.
- This is a single snapshot, so "attrition rate" here means leavers divided by employees in the file. A proper annual rate uses average headcount over a year.

## How I did it

1. Loaded the CSV into SQLite with `scripts/load_db.py`, dropped the constant columns and built tenure and income bands (`sql/01_load_and_clean.sql`)
2. Attrition by department, role, overtime, tenure and income (`sql/02_analysis.sql`)
3. Split overtime by tenure, and separately by income, to check whether pay or tenure explained the overtime gap
4. Added confidence intervals and a chi-square test in Excel (`excel/hr_attrition.xlsx`, sheet "Overtime Test")
5. Power BI report: measures and page layout in `powerbi/`

## Reading the numbers carefully

- **Small groups mislead.** Sales Representatives (83 people) have a 95% interval of 30% to 51%. That is high, but not precise. Among Sales Representatives on overtime, 67% left, but that is 16 of 24 people, so treat it as a hint.
- **Everything here is an association.** Overtime going with leaving doesn't mean overtime causes it. Employees who were already unhappy may also pick up more overtime, or the reverse.
- **Department and role differences are real but smaller** than the overtime gap. The tests say the department gap (Sales 20.6%, HR 19.0%, R&D 13.8%) is unlikely to be chance, but with 1,470 people it doesn't say much about why.
- Age, gender and marital status are in the data, but I haven't used them to point at anyone. The point is to find process and policy problems like workload and promotion gaps.

## Limits

- Fictional, single-snapshot data.
- No exit reasons, so I can't separate voluntary from involuntary leavers.
- No hiring data, so this project covers attrition only.

## Files

```
03-hr-attrition/
  data/raw/                  HR CSV (not committed, see the note in that folder)
  sql/                       load and clean, then analysis
  scripts/                   load_db.py, build_workbook.py
  excel/hr_attrition.xlsx
  powerbi/                   measures.dax and page layout
```
