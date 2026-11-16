# Power BI report layout

I can't ship a `.pbix` file from here, so this is the build guide. 

## Setup

1. Get Data > Text/CSV > `data/raw/Sample-Superstore.csv`. Choose the 1252 Western European encoding if characters look odd.
2. In Power Query: Order Date to Date (the file uses month/day/year, so set the locale to English (United States)), Sales, Discount and Profit to Decimal Number, Quantity to Whole Number.
3. Add a Date table: `Date = CALENDAR ( MIN ( Orders[Order Date] ), MAX ( Orders[Order Date] ) )` and relate it to Orders[Order Date].
4. Add `Discount Band` as a calculated column (code at the bottom of `measures.dax`). Use a column, not a measure, so it can go on a chart axis.
5. Paste the measures from `measures.dax`.
6. The raw file has one duplicate row (order US-2014-150119, product FUR-CH-10002965). Remove duplicates in Power Query on Order ID, Product ID, Sales, Quantity, Discount and Profit so you land on 9,993 rows.

## Page 1: Executive view

- Cards: Revenue, Profit, Profit Margin %, Order Count
- Line chart: Revenue by month, Profit Margin % on a second axis
- Bar chart: Profit by region
- Title: "Profit has grown every year, but margin has stalled near 13%"

## Page 2: Product profitability

- Scatter: Revenue (x) against Profit Margin % (y), one dot per sub-category
- Bar chart: Profit by sub-category, lowest first
- Title: "Tables, Bookcases and Supplies lose money overall"

## Page 3: Discount impact

- Column chart: Profit Margin % by Discount Band
- Card: Loss Making Share
- Decomposition tree: Profit, split by Discount Band, then Category, then Region
- Title: "Anything discounted above 20% loses money"

## Check before publishing

These should match the SQL and the Excel workbook: Revenue 2,296,919, Profit 286,409, Profit Margin 12.5%, Loss Making Lines 1,870. 
