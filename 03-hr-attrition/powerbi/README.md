# Power BI report layout

Save your finished file here as `hr_attrition.pbix`. Screenshots go in `../screenshots/`.

## Setup

1. Get Data > Text/CSV > `WA_Fn-UseC_-HR-Employee-Attrition.csv`
2. Remove EmployeeCount, StandardHours, Over18 and EmployeeNumber in Power Query
3. Add calculated columns for Tenure Band and Income Band (same cut-offs as `sql/01_load_and_clean.sql`) so they can sit on chart axes
4. Paste the measures from `measures.dax`

## Page 1: Overview

- Cards: Headcount, Leavers, Attrition Rate, Avg Tenure of Leavers
- Bar chart: Attrition Rate by Department
- Slicers: Department, Job Role
- Title: "16% of employees have left, and overtime triples the odds"

## Page 2: Who is leaving

- Clustered column: Attrition Rate by Tenure Band
- Clustered column: Attrition Rate by OverTime (Yes / No)
- Bar chart: Attrition Rate by Job Role, with Headcount as a tooltip
- Column chart: Attrition Rate by Income Band
- Put the Sample Size Label on the chart labels where there is room
- Title: "The first year is the riskiest: 35% of new joiners have left"

## Page 3: What to test (use the findings from the README)

- A small table of three ideas, each with the pattern, the group, what you'd change, how you'd measure it and the trial length. Example row: overtime goes with 30.5% attrition against 10.4%, so cap overtime for people in their first two years in Sales and Lab Technician teams, compare with similar teams, and measure leavers after two quarters
- This is the page a hiring manager remembers, so keep it short and specific

## Check before publishing

- Headcount should read 1,470, Leavers 237 and Attrition Rate 16.1%
- No rate is shown for a group without its headcount next to it
