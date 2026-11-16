# Budget Variance Analysis: where did the overspend come from?

**Tools:** SQL (SQLite), Excel, Power BI
**Data:** simulated company ledger, 432 rows (12 months x 6 departments x 6 accounts)

## The problem

The CFO's monthly review keeps saying "we're over budget" without saying where. The question I set out to answer: which departments and cost lines drive the overspend, is it a one-off or does it keep happening, and what does the year end up looking like?

## What I found

1. **The company finished 1.14% over budget** (4,399,648 actual against 4,350,000 budget, a gap of 49,648).
2. **One line explains almost half of it.** Engineering / Contractors came in 23,165 over, 12.9% above its budget. That is about 47% of the whole company overspend from a single line.
3. **It is a pattern, not a bad month.** Engineering / Contractors was more than 5% over budget in all 12 months, and the gap widens late in the year (about 8% over in January, 26% over in December).
4. **Travel is over everywhere.** 6.3% over budget company-wide, and most of that comes from spikes in March and September.
5. Two departments came in *under* budget (Finance -1.55%, HR -1.12%), so the headline number hides movement in both directions.

## What I'd recommend

- Open a review of Engineering contractor spend and either re-baseline the budget or cap it. If that line had stayed on budget, the company overspend would have dropped from 49,648 to roughly 26,500.
- Ask why travel spikes in March and September. If it is a conference or planning cycle, budget for it in those months instead of spreading it evenly.
- Do not chase Salaries. It is the biggest line but only 0.3% over.

## Data

The ledger is **simulated**. Real company ledgers are confidential, so I generated one with a fixed random seed (`scripts/make_ledger.py`). Two things are planted on purpose so there is something to find: a steady upward drift in Engineering contractors, and a 35% travel spike in March and September. That means the findings above are about how I built the data, not about a real company. What the project shows is the method: how to find the drivers and how to tell a one-off from a pattern.

The dataset covers a full simulated year (Jan to Dec 2026).

## How I did it

1. Generated the ledger and checked totals tie out to the CSV (`scripts/make_ledger.py`, `sql/01_load.sql`)
2. Variance by department, account, month and line (`sql/02_analysis.sql`)
3. Flagged lines that were over budget by more than 5% three months in a row, using a window function (`sql/03_persistent_overspend.sql`)
4. Built an Excel workbook with live formulas and three full-year forecast scenarios (`excel/budget_variance.xlsx`)
5. Built the Power BI report (see `powerbi/README.md` for the measures and page layout)

Sign convention: variance = actual minus budget. For costs, a positive number is an overspend.

## Forecast scenarios

Made at the halfway point using January to June actuals:

| Scenario | Full-year forecast | vs budget |
|---|---|---|
| Rest of year goes to budget | 4,367,457 | +0.40% |
| Current run rate continues | 4,384,914 | +0.80% |
| Cost action (rest of year 5% under) | 4,258,707 | -2.10% |
| What actually happened | 4,399,648 | +1.14% |

Both "no action" forecasts came in low, because the Engineering drift and the September travel spike hadn't happened yet at the halfway point. A flat run rate can't see a trend that is still building.

## Limits

- Simulated data, so none of this describes a real business.
- I compare actual to budget only. I can't say whether the budget itself was reasonable.
- A line over budget is not automatically bad. Contractors may have been over because of extra work that earned revenue, and this dataset has no revenue side.
- The streak query reports the month a line *completed* its third straight month over 5%, not the month the overspend began. For Engineering contractors that shows March, but the overspend actually started in January.

## Files

```
02-budget-variance/
  data/raw/ledger.csv           simulated ledger
  sql/                          load, analysis and streak queries
  scripts/                      python that builds the data and the workbook
  excel/budget_variance.xlsx    pivot-style summaries and forecast
  powerbi/README.md             measures and report layout
```
