"""
Builds excel/superstore_analysis.xlsx from the cleaned `orders` table.

Steps before this:
    python scripts/load_db.py
    run sql/01_load_and_clean.sql against data/superstore.db  (creates `orders`)

Every summary number in the workbook is a formula pointing at the Orders sheet.
Run from the project root:  python scripts/build_workbook.py
"""
import sqlite3
import pandas as pd
from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Font, PatternFill

with sqlite3.connect("data/superstore.db") as con:
    df = pd.read_sql_query("SELECT * FROM orders", con, parse_dates=["order_date"])

n = len(df)
last = n + 1
cols = ["order_id", "order_date", "region", "state", "category", "sub_category",
        "product_name", "sales", "quantity", "discount", "profit"]

HEAD_FILL = PatternFill("solid", fgColor="1F3864")
HEAD_FONT = Font(bold=True, color="FFFFFF")
RED_FILL = PatternFill("solid", bgColor="F8CBAD")
MONEY = '#,##0;[Red]-#,##0'
PCT = '0.0%;[Red]-0.0%'


def header(ws, row, ncols):
    for c in range(1, ncols + 1):
        cell = ws.cell(row=row, column=c)
        cell.fill, cell.font = HEAD_FILL, HEAD_FONT
        cell.alignment = Alignment(horizontal="center", wrap_text=True)


def widths(ws, ws_widths):
    for i, w in enumerate(ws_widths, start=1):
        ws.column_dimensions[chr(64 + i)].width = w


wb = Workbook()

# ------------------------------------------------------------------ Orders
od = wb.active
od.title = "Orders"
od.append(["Order ID", "Order Date", "Region", "State", "Category", "Sub-Category",
           "Product Name", "Sales", "Quantity", "Discount", "Profit",
           "Year", "Discount Band", "Loss line?"])
header(od, 1, 14)
for i, r in enumerate(df[cols].itertuples(index=False), start=2):
    od.append([r.order_id, r.order_date.date(), r.region, r.state, r.category,
               r.sub_category, r.product_name, float(r.sales), int(r.quantity),
               float(r.discount), float(r.profit),
               f"=YEAR(B{i})",
               f'=IF(J{i}=0,"a. No discount",IF(J{i}<=0.2,"b. Up to 20%",IF(J{i}<=0.4,"c. 20 to 40%","d. Above 40%")))',
               f"=IF(K{i}<0,1,0)"])
    od[f"B{i}"].number_format = "yyyy-mm-dd"
    od[f"H{i}"].number_format = "#,##0.00"
    od[f"J{i}"].number_format = "0%"
    od[f"K{i}"].number_format = "#,##0.00;[Red]-#,##0.00"
widths(od, [16, 12, 10, 16, 16, 14, 40, 10, 9, 9, 11, 7, 15, 9])
od.freeze_panes = "A2"
od.auto_filter.ref = f"A1:N{last}"

R = lambda col: f"Orders!${col}$2:${col}${last}"  # noqa: E731


def summary_block(ws, title, key_col, keys, first_row=1):
    """Writes a Revenue / Profit / Margin table grouped by one Orders column."""
    ws.append([title, "Revenue", "Profit", "Margin", "Loss lines", "Lines"])
    header(ws, first_row, 6)
    for i, k in enumerate(keys, start=first_row + 1):
        ws.append([k,
                   f"=SUMIFS({R('H')},{R(key_col)},A{i})",
                   f"=SUMIFS({R('K')},{R(key_col)},A{i})",
                   f"=IFERROR(C{i}/B{i},0)",
                   f"=SUMIFS({R('N')},{R(key_col)},A{i})",
                   f"=COUNTIFS({R(key_col)},A{i})"])
        for c in "BC":
            ws[f"{c}{i}"].number_format = MONEY
        ws[f"D{i}"].number_format = PCT
    return first_row + len(keys)


# ------------------------------------------------------------------ Summary
sm = wb.create_sheet("Summary", 0)
sm["A1"] = "Superstore profitability: headline numbers"
sm["A1"].font = Font(bold=True, size=13)
rows = [
    ("Order lines", f"=COUNTA({R('A')})", "#,##0"),
    ("Total sales", f"=SUM({R('H')})", MONEY),
    ("Total profit", f"=SUM({R('K')})", MONEY),
    ("Profit margin", "=B5/B4", PCT),
    ("Lines that lost money", f"=SUM({R('N')})", "#,##0"),
    ("Share of lines that lost money", "=B7/B3", PCT),
]
for i, (label, formula, fmt) in enumerate(rows, start=3):
    sm[f"A{i}"], sm[f"B{i}"] = label, formula
    sm[f"B{i}"].number_format = fmt
    sm[f"A{i}"].font = Font(bold=True)
sm["A10"] = "Margin is total profit divided by total sales, never an average of line margins."
sm["A10"].font = Font(italic=True)
widths(sm, [34, 16])

# ------------------------------------------------------------------ By Category / Sub-Category
cat_order = df.groupby("category")["profit"].sum().sort_values(ascending=False).index.tolist()
sub_order = df.groupby("sub_category")["profit"].sum().sort_values().index.tolist()

ct = wb.create_sheet("By Category")
summary_block(ct, "Category", "E", cat_order)
widths(ct, [22, 14, 14, 10, 11, 9])

sb = wb.create_sheet("By Sub-Category")
end = summary_block(sb, "Sub-Category", "F", sub_order)
widths(sb, [22, 14, 14, 10, 11, 9])
sb.conditional_formatting.add(f"C2:C{end}", CellIsRule(operator="lessThan", formula=["0"], fill=RED_FILL))
ch = BarChart()
ch.type = "bar"
ch.title = "Profit by sub-category (worst at the bottom of the list = top of chart)"
ch.add_data(Reference(sb, min_col=3, min_row=1, max_row=end), titles_from_data=True)
ch.set_categories(Reference(sb, min_col=1, min_row=2, max_row=end))
ch.legend = None
ch.height, ch.width = 11, 18
sb.add_chart(ch, "H2")

# ------------------------------------------------------------------ By Region
rg = wb.create_sheet("By Region")
region_order = df.groupby("region")["profit"].sum().sort_values(ascending=False).index.tolist()
summary_block(rg, "Region", "C", region_order)
widths(rg, [16, 14, 14, 10, 11, 9])

# ------------------------------------------------------------------ Discount bands
dbn = wb.create_sheet("Discount Bands")
bands = ["a. No discount", "b. Up to 20%", "c. 20 to 40%", "d. Above 40%"]
dend = summary_block(dbn, "Discount band", "M", bands)
dbn["G1"], dbn["G1"].font = "Share of lines losing money", HEAD_FONT
dbn["G1"].fill = HEAD_FILL
for i in range(2, dend + 1):
    dbn[f"G{i}"] = f"=E{i}/F{i}"
    dbn[f"G{i}"].number_format = "0.0%"
widths(dbn, [18, 14, 14, 10, 11, 9, 24])
ch = BarChart()
ch.title = "Profit margin by discount band"
ch.add_data(Reference(dbn, min_col=4, min_row=1, max_row=dend), titles_from_data=True)
ch.set_categories(Reference(dbn, min_col=1, min_row=2, max_row=dend))
ch.legend = None
ch.height, ch.width = 8, 14
dbn.add_chart(ch, "A9")

# ------------------------------------------------------------------ Year trend
yr = wb.create_sheet("By Year")
yend = summary_block(yr, "Year", "L", sorted(df["order_date"].dt.year.unique().tolist()))
widths(yr, [10, 14, 14, 10, 11, 9])
lc = LineChart()
lc.title = "Revenue and profit by year"
lc.add_data(Reference(yr, min_col=2, max_col=3, min_row=1, max_row=yend), titles_from_data=True)
lc.set_categories(Reference(yr, min_col=1, min_row=2, max_row=yend))
lc.height, lc.width = 8, 14
yr.add_chart(lc, "A8")

# ------------------------------------------------------------------ Profit leak
lk = wb.create_sheet("Profit Leak")
lk["A1"] = "How much profit did heavy discounting cost?"
lk["A1"].font = Font(bold=True, size=12)
lk["A3"], lk["B3"] = "Heavy discount threshold", 0.3
lk["A4"], lk["B4"] = "Light discount threshold", 0.2
lk["B3"].number_format = lk["B4"].number_format = "0%"
lk["A6"], lk["B6"] = "Heavy-discount lines", f'=COUNTIFS({R("J")},">"&B3)'
lk["A7"], lk["B7"] = "Their sales", f'=SUMIFS({R("H")},{R("J")},">"&B3)'
lk["A8"], lk["B8"] = "Their actual profit", f'=SUMIFS({R("K")},{R("J")},">"&B3)'
lk["A9"], lk["B9"] = "Margin of light-discount lines", (
    f'=SUMIFS({R("K")},{R("J")},"<="&B4)/SUMIFS({R("H")},{R("J")},"<="&B4)')
lk["A10"], lk["B10"] = "Profit if they had earned that margin", "=B7*B9"
lk["A11"], lk["B11"] = "Estimated leak (company-wide margin)", "=B10-B8"
lk["A12"], lk["B12"] = "Company profit without heavy-discount lines", f"=SUM({R('K')})-B8"
for r in (6,):
    lk[f"B{r}"].number_format = "#,##0"
for r in (7, 8, 10, 11, 12):
    lk[f"B{r}"].number_format = MONEY
lk["B9"].number_format = PCT
lk["A11"].font = lk["B11"].font = Font(bold=True)
lk["A14"] = ("The second estimate (comparing within each sub-category) is in sql/02_analysis.sql, "
             "query 6. It lands within about 2% of this one.")
lk["A14"].font = Font(italic=True)
widths(lk, [46, 16])

wb.save("excel/superstore_analysis.xlsx")
print("saved", n, "rows")
