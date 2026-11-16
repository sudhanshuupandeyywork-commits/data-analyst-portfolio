"""Loads the IBM HR CSV into SQLite (data/hr.db) as hr_raw.
Run from the project root:  python scripts/load_db.py"""
import sqlite3
import pandas as pd

df = pd.read_csv("data/raw/WA_Fn-UseC_-HR-Employee-Attrition.csv", encoding="utf-8-sig")
with sqlite3.connect("data/hr.db") as con:
    df.to_sql("hr_raw", con, if_exists="replace", index=False)
print(len(df), "rows loaded")
