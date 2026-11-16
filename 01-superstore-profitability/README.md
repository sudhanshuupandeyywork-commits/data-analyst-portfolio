# Superstore Profitability: where is the money leaking?

**Tools:** SQL (SQLite), Excel, Power BI
**Data:** Sample Superstore, 9,994 order lines from January 2014 to December 2017

## The problem

A merchandising team wants to know which products, regions and discount levels are costing the business margin, and what to change next quarter. I expected to find "revenue up, profit flat". The data doesn't say that (see finding 1), so the real question became: profit is growing, but how much is being thrown away?

## What I found

1. **Revenue and profit both grew, but margin stalled.** Sales went from 484K in 2014 to 733K in 2017, and profit from 50K to 93K. Margin rose from 10.2% to about 13% in 2015 and 2016, then slipped to 12.7% in 2017.
2. **Discounts above 20% are where it goes wrong.** Lines with no discount earn a 29.5% margin. Lines discounted 20 to 40% lose money overall (-15.3%), and every one of the 933 lines discounted over 40% lost money (-77.4% margin). At exactly 20% off, the 3,657 lines still made 90K of profit. At 30% off they started losing.
3. **Heavy discounting cost real money.** The 1,166 lines discounted more than 30% brought in 260K of sales (11% of the total) and lost 125K. Without them, total profit would have been 411K instead of 286K, about 44% higher.
4. **Furniture is the weak category.** Its margin is 2.5%, against 17% to 17.4% for Technology and Office Supplies. Tables lost 17.7K, Bookcases 3.5K and Supplies 1.2K.
5. **The Central region is weakest (7.9% margin, against 14.9% in the West).** It also discounts the most: an average discount of 24%, with 21% of lines above 30% off, compared with 3.7% in the West.
6. **A few big products lose money on every sale.** The worst are the Cubify CubeX 3D Printer Double Head (11.1K revenue, 8.9K lost), a Lexmark laser printer (16.8K revenue, 4.6K lost) and the Cubify Triple Head (8K revenue, 3.8K lost).

## What I'd recommend

- **Cap discounts at 20%.** The data shows a clear break between 20% and 30%. Start with Binders, which account for 613 of the 1,166 heavy-discount lines and lost 38.5K on them, then Machines (29.9K lost on just 48 lines) and Tables (27.3K lost on 122 lines).
- **Re-price or drop the loss-making products,** starting with the two Cubify printers and the Lexmark printer.
- **Look at the Central region's discounting habits** before blaming its product mix.

How much would this recover? Between 125K and about 185K over the four years. The low end assumes the heavy-discount sales simply don't happen (profit rises by the 125K they lost). The high end assumes the same volume sells at normal margin, which is unlikely, since some customers only buy at a steep discount. Two ways of calculating the high end land within 2% of each other (182K and 186K). The real figure is probably nearer the low end, and a small trial would tell.

## Data and cleaning

- Source: Sample Superstore, 9,994 rows. All order lines are US, from 5,009 orders.
- One duplicated row (order US-2014-150119, a Hon chair) was removed, leaving 9,993 lines. Totals after cleaning: sales 2,296,919, profit 286,409, margin 12.5%.
- Dates were stored as month/day/year text and were converted to proper dates.
- I kept the 1,870 loss-making lines (18.7% of all lines). They are the story, so deleting them would hide the problem.

## How I did it

1. Loaded the CSV into SQLite with `scripts/load_db.py` and cleaned it (`sql/01_load_and_clean.sql`)
2. Profit and margin by category, sub-category, region, year and discount band (`sql/02_analysis.sql`, queries 1 to 4 and 7)
3. Found high-revenue, low-margin products with `NTILE` (query 5)
4. Estimated the profit lost to heavy discounting two ways (queries 6 and 8)
5. Rebuilt the same numbers in Excel with live formulas (`excel/superstore_analysis.xlsx`, built by `scripts/build_workbook.py`) and checked they match the SQL
6. Power BI report: measures and page layout in `powerbi/`

## Limits

- This is observational data. Discounts and losses go together, but I can't prove the discount caused every loss. Shipping cost, returns and product mix could also play a part, which is why the estimate is a range.
- A discount cap changes customer behaviour, and this data can't tell me how. A trial in one region would.
- Superstore is a well-known practice dataset (a fictional retailer), so none of this describes a real company.
- There is no cost column, so margin is only as reliable as the profit column.

## Files

```
01-superstore-profitability/
  data/raw/                 Superstore CSV (not committed, see the note in that folder)
  sql/                      load and clean, then analysis
  scripts/                  load_db.py, build_workbook.py
  excel/superstore_analysis.xlsx
  powerbi/                  measures.dax and page layout
  screenshots/              dashboard images
```
