# Excel workbook

`superstore_analysis.xlsx` is built from the cleaned data by `scripts/build_workbook.py`. Every number on the summary sheets is a formula that reads the Orders sheet, so if you change a value there, the totals move.

| Sheet | What it shows |
|---|---|
| Summary | Order lines, sales, profit, margin, and how many lines lost money |
| Orders | The 9,993 cleaned order lines, plus formula columns for year, discount band and loss flag |
| By Category / By Sub-Category / By Region | Revenue, profit, margin and loss lines (sub-category sheet has a chart and red highlights for losses) |
| Discount Bands | Margin by discount band, with a chart |
| By Year | Revenue and profit by year, with a line chart |
| Profit Leak | Change the thresholds (30% and 20%) in the two cells at the top and the estimate recalculates |

The totals match the SQL results (sales 2,296,919, profit 286,409, margin 12.5%).

To rebuild it from scratch: run `scripts/load_db.py`, run `sql/01_load_and_clean.sql` against `data/superstore.db`, then run `scripts/build_workbook.py` from the project folder.

Excel calculates the formulas when you open the file. If numbers look empty in a preview tool, open it in Excel and save once.
