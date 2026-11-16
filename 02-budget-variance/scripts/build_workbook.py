"""
Builds the Excel workbook for the budget variance project.
Every number on the summary sheets is a live formula pointing at the Ledger
sheet, so you can change a value and watch the totals move.

Run from the project root:  python scripts/build_workbook.py
"""
import pandas as pd
from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

df = pd.read_csv("data/raw/ledger.csv", parse_dates=["month"])
n = len(df)
last = n + 1  # last data row on the Ledger sheet

head_fill = PatternFill("solid", fgColor="1F3864")
head_font = Font(bold=True, color="FFFFFF")
money = '#,##0;[Red]-#,##0'
pct = '0.0%;[Red]-0.0%'


def style_header(ws, row, ncols):
    for c in range(1, ncols + 1):
        cell = ws.cell(row=row, column=c)
        cell.fill, cell.font = head_fill, head_font
        cell.alignment = Alignment(horizontal="center")


wb = Workbook()

# ---------- Ledger ----------
ws = wb.active
ws.title = "Ledger"
ws.append(["Month", "Department", "Account", "Budget", "Actual",
           "Variance", "Variance %", "Over 5%?"])
style_header(ws, 1, 8)
for i, r in enumerate(df.itertuples(index=False), start=2):
    ws.append([r.month.date(), r.department, r.account, r.budget, r.actual,
               f"=E{i}-D{i}", f"=IFERROR(F{i}/D{i},0)", f'=IF(G{i}>0.05,"Over","OK")'])
for i in range(2, last + 1):
    ws[f"A{i}"].number_format = "yyyy-mm"
    for col in "DEF":
        ws[f"{col}{i}"].number_format = money
    ws[f"G{i}"].number_format = pct
ws.conditional_formatting.add(f"H2:H{last}", CellIsRule(
    operator="equal", formula=['"Over"'], fill=PatternFill("solid", bgColor="F8CBAD")))
for col, w in zip("ABCDEFGH", [12, 14, 17, 11, 11, 11, 11, 10]):
    ws.column_dimensions[col].width = w
ws.freeze_panes = "A2"
ws.auto_filter.ref = f"A1:H{last}"

# ---------- By department ----------
dp = wb.create_sheet("By Department")
dp.append(["Department", "Budget", "Actual", "Variance", "Variance %"])
style_header(dp, 1, 5)
depts = sorted(df["department"].unique())
for i, d in enumerate(depts, start=2):
    dp.append([d,
               f"=SUMIFS(Ledger!$D$2:$D${last},Ledger!$B$2:$B${last},A{i})",
               f"=SUMIFS(Ledger!$E$2:$E${last},Ledger!$B$2:$B${last},A{i})",
               f"=C{i}-B{i}", f"=IFERROR(D{i}/B{i},0)"])
tot = len(depts) + 2
dp.append(["Total", f"=SUM(B2:B{tot-1})", f"=SUM(C2:C{tot-1})",
           f"=C{tot}-B{tot}", f"=IFERROR(D{tot}/B{tot},0)"])
for c in range(1, 6):
    dp.cell(row=tot, column=c).font = Font(bold=True)
for i in range(2, tot + 1):
    for col in "BCD":
        dp[f"{col}{i}"].number_format = money
    dp[f"E{i}"].number_format = pct
for col, w in zip("ABCDE", [16, 13, 13, 12, 12]):
    dp.column_dimensions[col].width = w

chart = BarChart()
chart.type = "bar"
chart.title = "Variance by department (actual minus budget)"
chart.add_data(Reference(dp, min_col=4, min_row=1, max_row=tot - 1), titles_from_data=True)
chart.set_categories(Reference(dp, min_col=1, min_row=2, max_row=tot - 1))
chart.legend = None
chart.height, chart.width = 8, 16
dp.add_chart(chart, "G2")

# ---------- By account ----------
ac = wb.create_sheet("By Account")
ac.append(["Account", "Budget", "Actual", "Variance", "Variance %"])
style_header(ac, 1, 5)
accounts = sorted(df["account"].unique())
for i, a in enumerate(accounts, start=2):
    ac.append([a,
               f"=SUMIFS(Ledger!$D$2:$D${last},Ledger!$C$2:$C${last},A{i})",
               f"=SUMIFS(Ledger!$E$2:$E${last},Ledger!$C$2:$C${last},A{i})",
               f"=C{i}-B{i}", f"=IFERROR(D{i}/B{i},0)"])
for i in range(2, len(accounts) + 2):
    for col in "BCD":
        ac[f"{col}{i}"].number_format = money
    ac[f"E{i}"].number_format = pct
for col, w in zip("ABCDE", [18, 13, 13, 12, 12]):
    ac.column_dimensions[col].width = w

# ---------- Forecast ----------
fc = wb.create_sheet("Forecast")
fc["A1"] = "Full-year forecast made from January to June actuals"
fc["A1"].font = Font(bold=True, size=12)
fc["A3"], fc["B3"] = "Months elapsed", 6
fc["A4"], fc["B4"] = "H1 actual", f'=SUMIFS(Ledger!$E$2:$E${last},Ledger!$A$2:$A${last},"<="&DATE(2026,6,1))'
fc["A5"], fc["B5"] = "H1 budget", f'=SUMIFS(Ledger!$D$2:$D${last},Ledger!$A$2:$A${last},"<="&DATE(2026,6,1))'
fc["A6"], fc["B6"] = "Full-year budget", f"=SUM(Ledger!$D$2:$D${last})"
fc["A7"], fc["B7"] = "Saving rate on cost action", 0.05
fc["B7"].number_format = "0%"
fc.append([])
fc["A9"], fc["B9"], fc["C9"], fc["D9"] = "Scenario", "Full-year forecast", "vs budget", "vs budget %"
style_header(fc, 9, 4)
fc["A10"], fc["B10"] = "Rest of year goes to budget", "=B4+(B6-B5)"
fc["A11"], fc["B11"] = "Run rate continues", "=B4/B3*12"
fc["A12"], fc["B12"] = "Cost action (rest of year 5% under budget)", "=B4+(B6-B5)*(1-B7)"
for r in (10, 11, 12):
    fc[f"C{r}"] = f"=B{r}-$B$6"
    fc[f"D{r}"] = f"=C{r}/$B$6"
fc["A14"] = "What actually happened (simulated full year)"
fc["B14"] = f"=SUM(Ledger!$E$2:$E${last})"
fc["C14"], fc["D14"] = "=B14-B6", "=C14/B6"
fc["A14"].font = Font(bold=True)
for r in range(4, 15):
    for col in "BC":
        if fc[f"{col}{r}"].value is not None and r != 7:
            fc[f"{col}{r}"].number_format = money
for r in (10, 11, 12, 14):
    fc[f"D{r}"].number_format = pct
fc["A16"] = ("Note: the run rate forecast ignores that this ledger has a planted drift in "
             "Engineering contractors and travel spikes in March and September.")
fc.column_dimensions["A"].width = 44
for col in "BCD":
    fc.column_dimensions[col].width = 18

wb.move_sheet("Ledger", offset=3)
wb.save("excel/budget_variance.xlsx")
print("Saved excel/budget_variance.xlsx")
