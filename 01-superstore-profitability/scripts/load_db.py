"""Loads the Superstore CSV into a SQLite file (data/superstore.db) as orders_raw,
with snake_case column names so the SQL files run as written.
Run from the project root:  python scripts/load_db.py"""
import sqlite3
import pandas as pd

df = pd.read_csv("data/raw/Sample-Superstore.csv", encoding="latin-1")
df.columns = [c.strip().lower().replace("-", "_").replace(" ", "_") for c in df.columns]
# dates come as month/day/year text; store them as ISO so they sort and group properly
for c in ("order_date", "ship_date"):
    df[c] = pd.to_datetime(df[c], format="%m/%d/%Y").dt.strftime("%Y-%m-%d")
with sqlite3.connect("data/superstore.db") as con:
    df.to_sql("orders_raw", con, if_exists="replace", index=False)
print(len(df), "rows loaded;", list(df.columns))
