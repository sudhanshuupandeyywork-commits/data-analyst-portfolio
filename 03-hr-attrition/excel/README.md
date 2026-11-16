# Excel workbook

`hr_attrition.xlsx` is built from the cleaned data by `scripts/build_workbook.py`. The summary sheets are formulas that read the Employees sheet.

| Sheet | What it shows |
|---|---|
| Summary | Headcount, leavers, attrition rate, average tenure of leavers and stayers |
| Employees | The 1,470 employees (constant columns dropped), plus a Left (1/0) column |
| By Department / By Job Role / By Tenure / By Income / By Travel | Headcount, leavers, rate and how many times the company rate (charts on most) |
| Overtime Test | Rates for overtime Yes and No, 95% confidence intervals, a chi-square statistic and p-value |
| Overtime x Tenure | Attrition by tenure band, split by overtime, with a chart |

The numbers match the SQL output: 237 leavers out of 1,470 (16.1%), and 30.5% against 10.4% for overtime.

To rebuild: run `scripts/load_db.py`, run `sql/01_load_and_clean.sql` against `data/hr.db`, then run `scripts/build_workbook.py` from the project folder.
