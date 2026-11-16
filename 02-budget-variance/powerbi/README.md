# Power BI report: Budget Variance

I can't ship a `.pbix` file from here
## Load the data

1. Get Data > Text/CSV > `data/raw/ledger.csv`
2. In Power Query, set `month` to Date, and `budget` and `actual` to Whole Number
3. Close and apply

Add a Date table (Modeling > New table):

```
Date = CALENDAR ( DATE ( 2026, 1, 1 ), DATE ( 2026, 12, 31 ) )
```

Relate `Date[Date]` to `ledger[month]` (many to one from ledger).

## Measures

```
Budget = SUM ( ledger[budget] )

Actual = SUM ( ledger[actual] )

Variance = [Actual] - [Budget]

Variance % = DIVIDE ( [Variance], [Budget] )

Over Budget Lines =
CALCULATE (
    COUNTROWS ( ledger ),
    FILTER ( ledger, ledger[actual] > ledger[budget] * 1.05 )
)

YTD Actual = TOTALYTD ( [Actual], 'Date'[Date] )

YTD Budget = TOTALYTD ( [Budget], 'Date'[Date] )
```

## Pages

**Page 1: Overview**
- Cards: Budget, Actual, Variance, Variance %
- Line chart: Budget and Actual by month
- Title to use: "We finished 1.1% over budget, but one line drives half of it"

**Page 2: Where the overspend is**
- Bar chart: Variance by department
- Bar chart: Variance by account
- Matrix: department (rows) by account (columns), Variance % as values, with conditional formatting (red above 5%)
- Title to use: "Engineering contractors are 13% over budget"

**Page 3: Is it persistent?**
- Line chart: Variance % by month for Engineering / Contractors, with a constant line at 5%
- Table: lines from `sql/03_persistent_overspend.sql`
- Slicer: department

## Check before you publish

- Total Variance on page 1 should read 49,648
- Engineering / Contractors variance should read 23,165
- If either is off, check that the month relationship is active
