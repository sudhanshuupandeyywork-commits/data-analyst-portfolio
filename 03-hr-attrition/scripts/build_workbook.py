"""
Builds excel/hr_attrition.xlsx from the cleaned `employees` table.

Steps before this:
    python scripts/load_db.py
    run sql/01_load_and_clean.sql against data/hr.db   (creates `employees`)

Summary sheets are formulas that point at the Employees sheet.
Run from the project root:  python scripts/build_workbook.py
"""
import sqlite3
import pandas as pd
from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.styles import Alignment, Font, PatternFill

with sqlite3.connect("data/hr.db") as con:
    df = pd.read_sql_query("SELECT * FROM employees", con)

n = len(df)
last = n + 1
HEAD_FILL = PatternFill("solid", fgColor="1F3864")
HEAD_FONT = Font(bold=True, color="FFFFFF")
PCT = "0.0%"

# column letters on the Employees sheet
COLS = ["age", "attrition", "business_travel", "department", "job_role", "job_level",
        "job_satisfaction", "monthly_income", "overtime", "work_life_balance",
        "years_at_company", "years_since_promotion", "tenure_band", "income_band"]
# A..N from the table, then O = Left (1/0)
L = {name: chr(65 + i) for i, name in enumerate(COLS)}
L["left"] = "O"
R = lambda key: f"Employees!${L[key]}$2:${L[key]}${last}"  # noqa: E731


def header(ws, row, ncols):
    for c in range(1, ncols + 1):
        cell = ws.cell(row=row, column=c)
        cell.fill, cell.font = HEAD_FILL, HEAD_FONT
        cell.alignment = Alignment(horizontal="center", wrap_text=True)


def widths(ws, ws_widths):
    for i, w in enumerate(ws_widths, start=1):
        ws.column_dimensions[chr(64 + i)].width = w


wb = Workbook()

# ------------------------------------------------------------ Employees
em = wb.active
em.title = "Employees"
em.append(["Age", "Attrition", "Business Travel", "Department", "Job Role", "Job Level",
           "Job Satisfaction", "Monthly Income", "OverTime", "Work-Life Balance",
           "Years At Company", "Years Since Promotion", "Tenure Band", "Income Band", "Left (1/0)"])
header(em, 1, 15)
for i, r in enumerate(df[COLS].itertuples(index=False), start=2):
    em.append(list(r) + [f'=IF(B{i}="Yes",1,0)'])
widths(em, [6, 10, 18, 22, 24, 9, 12, 12, 10, 12, 12, 12, 12, 14, 10])
em.freeze_panes = "A2"
em.auto_filter.ref = f"A1:O{last}"


def rate_table(ws, title, key, keys, min_row=1):
    ws.append([title, "Employees", "Leavers", "Attrition rate", "Times company rate"])
    header(ws, min_row, 5)
    for i, k in enumerate(keys, start=min_row + 1):
        ws.append([k,
                   f"=COUNTIFS({R(key)},A{i})",
                   f"=SUMIFS({R('left')},{R(key)},A{i})",
                   f"=IFERROR(C{i}/B{i},0)",
                   f"=D{i}/Summary!$B$6"])
        ws[f"D{i}"].number_format = PCT
        ws[f"E{i}"].number_format = "0.00"
    return min_row + len(keys)


def bar(ws, title, end, anchor, col=4, horizontal=False):
    ch = BarChart()
    if horizontal:
        ch.type = "bar"
    ch.title = title
    ch.add_data(Reference(ws, min_col=col, min_row=1, max_row=end), titles_from_data=True)
    ch.set_categories(Reference(ws, min_col=1, min_row=2, max_row=end))
    ch.legend = None
    ch.y_axis.numFmt = "0%"
    ch.height, ch.width = 8, 15
    ws.add_chart(ch, anchor)


def order_by_rate(col):
    g = df.groupby(col)["attrition"].apply(lambda s: (s == "Yes").mean())
    return g.sort_values(ascending=False).index.tolist()


# ------------------------------------------------------------ Summary
sm = wb.create_sheet("Summary", 0)
sm["A1"] = "HR attrition: headline numbers"
sm["A1"].font = Font(bold=True, size=13)
sm["A3"], sm["B3"] = "Employees", f"=COUNTA({R('attrition')})"
sm["A4"], sm["B4"] = "Leavers", f"=SUM({R('left')})"
sm["A5"], sm["B5"] = "", ""
sm["A6"], sm["B6"] = "Attrition rate", "=B4/B3"
sm["A7"], sm["B7"] = "Avg years at company, leavers", f'=AVERAGEIFS({R("years_at_company")},{R("attrition")},"Yes")'
sm["A8"], sm["B8"] = "Avg years at company, stayers", f'=AVERAGEIFS({R("years_at_company")},{R("attrition")},"No")'
sm["B6"].number_format = PCT
sm["B7"].number_format = sm["B8"].number_format = "0.0"
for r in (3, 4, 6, 7, 8):
    sm[f"A{r}"].font = Font(bold=True)
sm["A10"] = ("Attrition rate here is leavers divided by employees in a single snapshot, "
             "not an annual rate over average headcount.")
sm["A10"].font = Font(italic=True)
widths(sm, [34, 14])

# ------------------------------------------------------------ By Department
dp = wb.create_sheet("By Department")
end = rate_table(dp, "Department", "department", order_by_rate("department"))
widths(dp, [26, 11, 10, 14, 18])
bar(dp, "Attrition rate by department", end, "G2")

# ------------------------------------------------------------ By Job Role
jr = wb.create_sheet("By Job Role")
end = rate_table(jr, "Job role", "job_role", order_by_rate("job_role"))
widths(jr, [28, 11, 10, 14, 18])
bar(jr, "Attrition rate by job role", end, "G2", horizontal=True)

# ------------------------------------------------------------ Tenure / Income / Travel
tn = wb.create_sheet("By Tenure")
end = rate_table(tn, "Tenure band (years)", "tenure_band", ["0 to 1", "2 to 3", "4 to 5", "6 to 10", "11 plus"])
widths(tn, [20, 11, 10, 14, 18])
bar(tn, "Attrition rate by years at company", end, "G2")

ic = wb.create_sheet("By Income")
end = rate_table(ic, "Monthly income band", "income_band",
                 ["a. Under 3k", "b. 3k to 6k", "c. 6k to 10k", "d. 10k plus"])
widths(ic, [20, 11, 10, 14, 18])
bar(ic, "Attrition rate by monthly income", end, "G2")

tv = wb.create_sheet("By Travel")
rate_table(tv, "Business travel", "business_travel", ["Non-Travel", "Travel_Rarely", "Travel_Frequently"])
widths(tv, [22, 11, 10, 14, 18])

# ------------------------------------------------------------ Overtime test
ot = wb.create_sheet("Overtime Test")
ot["A1"] = "Is overtime linked to leaving? (rates, 95% confidence intervals and a chi-square test)"
ot["A1"].font = Font(bold=True, size=12)
ot.append([])
ot.append(["OverTime", "Employees", "Leavers", "Attrition rate", "CI low", "CI high"])
header(ot, 3, 6)
for i, k in enumerate(["No", "Yes"], start=4):
    ot[f"A{i}"] = k
    ot[f"B{i}"] = f"=COUNTIFS({R('overtime')},A{i})"
    ot[f"C{i}"] = f"=SUMIFS({R('left')},{R('overtime')},A{i})"
    ot[f"D{i}"] = f"=C{i}/B{i}"
    # Wilson score interval, z = 1.96
    ot[f"E{i}"] = (f"=(D{i}+1.96^2/(2*B{i})-1.96*SQRT(D{i}*(1-D{i})/B{i}+1.96^2/(4*B{i}^2)))"
                   f"/(1+1.96^2/B{i})")
    ot[f"F{i}"] = (f"=(D{i}+1.96^2/(2*B{i})+1.96*SQRT(D{i}*(1-D{i})/B{i}+1.96^2/(4*B{i}^2)))"
                   f"/(1+1.96^2/B{i})")
    for c in "DEF":
        ot[f"{c}{i}"].number_format = PCT
ot["A7"], ot["B7"] = "Rate ratio (Yes / No)", "=D5/D4"
ot["B7"].number_format = "0.00"
ot["A9"] = "Expected leavers if overtime made no difference"
ot["A9"].font = Font(bold=True)
ot["A10"], ot["B10"] = "No", "=B4*SUM(C4:C5)/SUM(B4:B5)"
ot["A11"], ot["B11"] = "Yes", "=B5*SUM(C4:C5)/SUM(B4:B5)"
ot["A12"], ot["B12"] = "Expected stayers, No", "=B4-B10"
ot["A13"], ot["B13"] = "Expected stayers, Yes", "=B5-B11"
ot["A15"], ot["B15"] = "Chi-square statistic", (
    "=(C4-B10)^2/B10+(C5-B11)^2/B11+((B4-C4)-B12)^2/B12+((B5-C5)-B13)^2/B13")
ot["A16"], ot["B16"] = "p-value (1 degree of freedom)", "=CHIDIST(B15,1)"
ot["A15"].font = ot["A16"].font = Font(bold=True)
ot["B15"].number_format = "0.0"
ot["B16"].number_format = "0.00E+00"
ot["A18"] = ("A tiny p-value says the gap is unlikely to be chance. It does not say overtime causes "
             "leaving. See the README for why.")
ot["A18"].font = Font(italic=True)
widths(ot, [44, 12, 10, 14, 10, 10])

# ------------------------------------------------------------ Overtime x Tenure
ox = wb.create_sheet("Overtime x Tenure")
ox["A1"] = "Attrition rate by tenure band, split by overtime"
ox["A1"].font = Font(bold=True, size=12)
ox.append([])
ox.append(["Tenure band", "No overtime", "Overtime", "Employees (No)", "Employees (Yes)"])
header(ox, 3, 5)
for i, t in enumerate(["0 to 1", "2 to 3", "4 to 5", "6 to 10", "11 plus"], start=4):
    ox[f"A{i}"] = t
    ox[f"B{i}"] = (f'=SUMIFS({R("left")},{R("tenure_band")},A{i},{R("overtime")},"No")'
                   f'/COUNTIFS({R("tenure_band")},A{i},{R("overtime")},"No")')
    ox[f"C{i}"] = (f'=SUMIFS({R("left")},{R("tenure_band")},A{i},{R("overtime")},"Yes")'
                   f'/COUNTIFS({R("tenure_band")},A{i},{R("overtime")},"Yes")')
    ox[f"D{i}"] = f'=COUNTIFS({R("tenure_band")},A{i},{R("overtime")},"No")'
    ox[f"E{i}"] = f'=COUNTIFS({R("tenure_band")},A{i},{R("overtime")},"Yes")'
    ox[f"B{i}"].number_format = ox[f"C{i}"].number_format = PCT
ch = BarChart()
ch.title = "Attrition by tenure, with and without overtime"
ch.add_data(Reference(ox, min_col=2, max_col=3, min_row=3, max_row=8), titles_from_data=True)
ch.set_categories(Reference(ox, min_col=1, min_row=4, max_row=8))
ch.y_axis.numFmt = "0%"
ch.height, ch.width = 8, 15
ox.add_chart(ch, "G2")
widths(ox, [16, 14, 12, 16, 16])

wb.save("excel/hr_attrition.xlsx")
print("saved", n, "rows")
